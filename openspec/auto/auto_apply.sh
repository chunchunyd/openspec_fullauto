#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENSPEC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AUTO_DEPS_DIR="${OPENSPEC_AUTO_DEPS_DIR:-${SCRIPT_DIR}/deps}"
AUTO_LOGS_DIR="${OPENSPEC_AUTO_LOGS_DIR:-${SCRIPT_DIR}/logs}"
TASKS_GIT_HELPER="${SCRIPT_DIR}/managed_git_tasks.py"
WORKTREE_ROOT="${OPENSPEC_AUTO_WORKTREE_ROOT:-$(cd "${PROJECT_ROOT}/.." && pwd)/.openspec-auto-worktrees/$(basename "${PROJECT_ROOT}")}"
PORT_BLOCK_BASE="${OPENSPEC_AUTO_PORT_BASE:-3000}"
PORT_BLOCK_SIZE="${OPENSPEC_AUTO_PORT_BLOCK_SIZE:-10}"

CLAUDE_CMD_STRING="${CLAUDE_CMD:-claude -p --dangerously-skip-permissions}"
OPENSPEC_CMD_STRING="${OPENSPEC_CMD:-npx -y @fission-ai/openspec}"
read -r -a CLAUDE_CMD <<<"${CLAUDE_CMD_STRING}"
read -r -a OPENSPEC_CMD <<<"${OPENSPEC_CMD_STRING}"

DRY_RUN=0
RUN_ALL=0
AUTO_ARCHIVE=1
CLEANUP_WORKTREES=0
STRICT_VALIDATE=0
SKIP_VALIDATE=0
STOP_ON_ERROR=0
MAX_PARALLEL=0
MAX_PARALLEL_SET=0
ALLOW_LOCAL_DB_RESET="${OPENSPEC_AUTO_ALLOW_LOCAL_DB_RESET:-0}"
INCOMPLETE_RETRY_LIMIT="${OPENSPEC_AUTO_INCOMPLETE_RETRY_LIMIT:-1}"
CLAUDE_RATE_LIMIT_RETRY_LIMIT="${OPENSPEC_AUTO_CLAUDE_RATE_LIMIT_RETRY_LIMIT:-3}"
CLAUDE_RATE_LIMIT_BASE_DELAY_SECONDS="${OPENSPEC_AUTO_CLAUDE_RATE_LIMIT_BASE_DELAY_SECONDS:-30}"
CLAUDE_RATE_LIMIT_MAX_DELAY_SECONDS="${OPENSPEC_AUTO_CLAUDE_RATE_LIMIT_MAX_DELAY_SECONDS:-300}"

declare -a TARGET_CHANGES=()
declare -a PREFIX_FILTERS=()
declare -a DEPENDENCY_FILES=()
declare -a AUTO_DEPENDENCY_FILES=()
declare -a COMPLETED_CHANGES=()
declare -a ARCHIVED_CHANGES=()
declare -a FAILED_CHANGES=()
declare -a INCOMPLETE_CHANGES=()
declare -a BLOCKED_CHANGES=()
declare -a RESTORED_CHANGES=()
declare -a CLEANUP_FAILED_CHANGES=()
declare -a BRANCH_CLEANED_CHANGES=()
declare -a BRANCH_CLEANUP_FAILED_CHANGES=()
declare -a HUMAN_REVIEW_CHANGES=()
declare -a MERGE_READY_QUEUE=()
declare -A CHANGE_DEPS=()
declare -A CHANGE_STATE=()
declare -A CHANGE_RESULT_FILE=()
declare -A CHANGE_WORKTREE=()
declare -A CHANGE_HUMAN_REASON=()
declare -A CHANGE_HUMAN_ACTION=()
declare -A CHANGE_RESULT_TRANSITION_AT=()
declare -A PID_TO_CHANGE=()
declare -A CHANGE_TASKS_FILE=()
declare -A CHANGE_IMPL_BRANCH=()
declare -A CHANGE_INTEGRATION_BRANCH=()
declare -A CHANGE_PARENT_MANAGED_GIT=()

SESSION_KEY=""
SESSION_DIR=""
STOP_REQUESTED=0
INTERRUPT_HANDLED=0

if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
  C_RESET=$'\033[0m'; C_DIM=$'\033[2m'; C_BOLD=$'\033[1m'
  C_INFO=$'\033[36m'; C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_ERR=$'\033[31m'; C_CHANGE=$'\033[35m'
else
  C_RESET=""; C_DIM=""; C_BOLD=""; C_INFO=""; C_OK=""; C_WARN=""; C_ERR=""; C_CHANGE=""
fi

usage() {
  cat <<'EOU'
Usage:
  ./auto_apply.sh <change-id> [<change-id> ...]
  ./auto_apply.sh --all [--prefix mobile-foundation-] [--prefix mobile-auth-]
  ./auto_apply.sh --deps deps/deps.mobile-auth.json [--deps deps/deps.feed-home.json]

Options:
  --all
  --prefix <prefix>   Repeatable; matches active changes whose names start with any provided prefix
                      Multiple prefixes only support independent series. If series depend on each other,
                      merge them under one target-named series prefix instead.
  --deps <file>       Repeatable; merges multiple dependency graphs
  --max-parallel <n>
  --no-archive
  --cleanup-worktrees
  --allow-local-db-reset
                      Allow the child agent to reset / rebuild only the disposable local dev/test DB for the current worktree
  --skip-validate
  --strict
  --stop-on-error
  --dry-run
  -h, --help
EOU
}

tag() { printf '%s[%s]%s' "$1" "$2" "${C_RESET}"; }
log() { printf '%s %s\n' "$(tag "${C_INFO}" "auto-apply")" "$*"; }
warn() { printf '%s %s\n' "$(tag "${C_WARN}" "auto-apply")" "$*" >&2; }
ok() { printf '%s %s\n' "$(tag "${C_OK}" "auto-apply")" "$*"; }
change_log() { local c="$1"; shift; printf '%s %s\n' "$(tag "${C_CHANGE}" "auto-apply:${c}")" "$*"; }
fail() { printf '%s %s\n' "$(tag "${C_ERR}" "auto-apply")" "$*" >&2; exit 1; }
attention() { printf '%s %s\n' "$(tag "${C_ERR}${C_BOLD}" "auto-apply")" "$*" >&2; }
require_command() { command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"; }

append_unique() {
  local value="$1" name="$2" existing
  local -n arr="${name}"
  for existing in "${arr[@]}"; do [[ "${existing}" == "${value}" ]] && return 0; done
  arr+=("${value}")
}

child_pids_of() {
  local pid="$1"
  ps -o pid= --ppid "${pid}" 2>/dev/null | awk '{print $1}'
}

kill_process_tree() {
  local pid="$1" signal="${2:-TERM}" child
  [[ -n "${pid}" ]] || return 0
  for child in $(child_pids_of "${pid}"); do
    kill_process_tree "${child}" "${signal}"
  done
  kill "-${signal}" "${pid}" >/dev/null 2>&1 || true
}

handle_interrupt() {
  local signal_name="$1"
  [[ "${INTERRUPT_HANDLED}" -eq 0 ]] || exit 130
  INTERRUPT_HANDLED=1
  STOP_REQUESTED=1
  warn "Received ${signal_name}; terminating running child processes"
  cancel_running_jobs
  summarize_and_exit 130
}

run_openspec() { (cd "${PROJECT_ROOT}" || exit 1; "${OPENSPEC_CMD[@]}" "$@"); }
git_ref_exists() { git -C "${PROJECT_ROOT}" rev-parse --verify --quiet "$1" >/dev/null 2>&1; }

build_local_db_reset_guidance() {
  [[ "${ALLOW_LOCAL_DB_RESET}" -eq 1 ]] || return 0
  cat <<'EOF2'

Local database permission for this run:
- If a disposable local development or test database used only by this worktree blocks implementation or validation, you may directly drop, recreate, reset, migrate from scratch, or reseed it without asking for approval first.
- Limit this permission to databases reached through this worktree's local env files, local compose services, or local project scripts.
- Never apply this permission to any shared database, remote database, staging environment, or production environment.
- Prefer the project's standard reset / rebuild commands over ad-hoc manual steps whenever possible.
- If you cannot confirm that the target database is local and disposable, stop and explain the blocker instead of guessing.
- Whenever you use this permission, report the exact command(s) and the reason in your final handoff note or transcript.
EOF2
}

series_prefix_for_change() {
  local change="$1"
  [[ "${change}" =~ ^(.+)-step-[0-9]+($|-) ]] && printf '%s\n' "${BASH_REMATCH[1]}"
}

implementation_branch_for_change() { printf 'feat/%s\n' "$1"; }
integration_branch_for_change() {
  local prefix
  prefix="$(series_prefix_for_change "$1")"
  [[ -n "${prefix}" ]] && printf 'series/%s\n' "${prefix}" || printf 'dev\n'
}

current_main_branch() {
  git -C "${PROJECT_ROOT}" symbolic-ref --quiet --short HEAD 2>/dev/null || true
}

warn_if_main_worktree_holds_series_branch() {
  local current_branch="" change prefix candidate dirty_note=""
  local -a series_prefixes=()

  current_branch="$(current_main_branch)"
  [[ -n "${current_branch}" ]] || return 0

  for change in "${TARGET_CHANGES[@]}"; do
    prefix="$(series_prefix_for_change "${change}")"
    [[ -n "${prefix}" ]] || continue
    append_unique "${prefix}" series_prefixes
  done

  for prefix in "${series_prefixes[@]}"; do
    for candidate in "series/${prefix}"; do
      if [[ "${current_branch}" == "${candidate}" ]]; then
        if [[ -n "$(git -C "${PROJECT_ROOT}" status --porcelain --untracked-files=normal 2>/dev/null)" ]]; then
          dirty_note=" Main worktree also has uncommitted changes."
        fi
        warn "Main worktree is currently on ${current_branch}. This can block sub-worktrees from checking out the same series integration branch for the final merge.${dirty_note}"
        warn "Recommendation: keep the main worktree on dev, a personal feature branch, or detached HEAD during parallel auto-apply runs."
        return 0
      fi
    done
  done
}

add_prefix_filter() {
  local raw="$1" part
  local -a parts=()
  IFS=',' read -r -a parts <<< "${raw}"
  for part in "${parts[@]}"; do
    [[ -n "${part}" ]] || continue
    append_unique "${part}" PREFIX_FILTERS
  done
}

add_dependency_file() {
  local raw="$1" part
  local -a parts=()
  IFS=',' read -r -a parts <<< "${raw}"
  for part in "${parts[@]}"; do
    [[ -n "${part}" ]] || continue
    append_unique "${part}" DEPENDENCY_FILES
  done
}

resolve_dependency_file_path() {
  local raw="$1" candidate base
  [[ -f "${raw}" ]] && { printf '%s\n' "${raw}"; return 0; }

  base="$(basename "${raw}")"
  candidate="${AUTO_DEPS_DIR}/${base}"
  [[ -f "${candidate}" ]] && { printf '%s\n' "${candidate}"; return 0; }

  candidate="${SCRIPT_DIR}/${base}"
  [[ -f "${candidate}" ]] && { printf '%s\n' "${candidate}"; return 0; }

  return 1
}

infer_dependency_files_from_prefixes() {
  local prefix trimmed candidate legacy_candidate
  AUTO_DEPENDENCY_FILES=()
  [[ "${#DEPENDENCY_FILES[@]}" -eq 0 ]] || return 0
  [[ "${#PREFIX_FILTERS[@]}" -gt 0 ]] || return 0
  for prefix in "${PREFIX_FILTERS[@]}"; do
    trimmed="${prefix%-}"
    [[ -n "${trimmed}" ]] || continue
    candidate="${AUTO_DEPS_DIR}/deps.${trimmed}.json"
    if [[ -f "${candidate}" ]]; then
      append_unique "${candidate}" DEPENDENCY_FILES
      append_unique "${candidate}" AUTO_DEPENDENCY_FILES
      continue
    fi
    legacy_candidate="${SCRIPT_DIR}/deps.${trimmed}.json"
    if [[ -f "${legacy_candidate}" ]]; then
      warn "Using legacy dependency graph path for prefix ${prefix}: ${legacy_candidate}"
      append_unique "${legacy_candidate}" DEPENDENCY_FILES
      append_unique "${legacy_candidate}" AUTO_DEPENDENCY_FILES
    else
      attention "No inferred dependency graph found for prefix ${prefix}: ${candidate}"
    fi
  done
}

resolve_dependency_files() {
  local file resolved
  local -a resolved_files=()
  mkdir -p "${AUTO_DEPS_DIR}" "${AUTO_LOGS_DIR}"
  for file in "${DEPENDENCY_FILES[@]}"; do
    resolved="$(resolve_dependency_file_path "${file}")" || fail "Dependency file not found: ${file}"
    append_unique "${resolved}" resolved_files
  done
  DEPENDENCY_FILES=("${resolved_files[@]}")
  infer_dependency_files_from_prefixes
}

sanitize_session_key() {
  local raw="$1" out
  out="$(printf '%s' "${raw}" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9._-]+/-/g; s/^-+//; s/-+$//; s/-{2,}/-/g')"
  [[ -n "${out}" ]] && printf '%s\n' "${out}" || printf 'batch\n'
}

common_series_prefix_for_targets() {
  local change prefix common=""
  for change in "${TARGET_CHANGES[@]}"; do
    prefix="$(series_prefix_for_change "${change}")"
    [[ -n "${prefix}" ]] || { printf '\n'; return 0; }
    [[ -z "${common}" ]] && common="${prefix}" || [[ "${common}" == "${prefix}" ]] || { printf '\n'; return 0; }
  done
  printf '%s\n' "${common}"
}

derive_session_key() {
  local candidate="" dep_name="" common="" joined="" file stem prefix
  if [[ "${#PREFIX_FILTERS[@]}" -eq 1 ]]; then
    candidate="${PREFIX_FILTERS[0]%-}"
  elif [[ "${#PREFIX_FILTERS[@]}" -gt 1 ]]; then
    joined=""
    for prefix in "${PREFIX_FILTERS[@]}"; do
      joined+="${prefix%-}__"
    done
    candidate="${joined%__}"
  fi
  if [[ -z "${candidate}" && "${#DEPENDENCY_FILES[@]}" -gt 0 ]]; then
    if [[ "${#DEPENDENCY_FILES[@]}" -eq 1 ]]; then
      dep_name="$(basename "${DEPENDENCY_FILES[0]}")"
      [[ "${dep_name}" =~ ^deps[._-](.+)\.json$ ]] && candidate="${BASH_REMATCH[1]}"
    else
      joined=""
      for file in "${DEPENDENCY_FILES[@]}"; do
        dep_name="$(basename "${file}")"
        stem="${dep_name%.json}"
        stem="${stem#deps.}"
        stem="${stem#deps_}"
        stem="${stem#deps-}"
        [[ -n "${stem}" ]] || stem="${dep_name}"
        joined+="${stem}__"
      done
      candidate="${joined%__}"
    fi
  fi
  if [[ -z "${candidate}" ]]; then
    common="$(common_series_prefix_for_targets)"
    [[ -n "${common}" ]] && candidate="${common}"
  fi
  if [[ -z "${candidate}" ]]; then
    [[ "${#TARGET_CHANGES[@]}" -eq 1 ]] && candidate="${TARGET_CHANGES[0]}" || candidate="batch"
  fi
  sanitize_session_key "${candidate}"
}

select_legacy_session_dir() {
  local best="" best_score=0 best_mtime=0 dir score mtime change file
  shopt -s nullglob
  for dir in "${AUTO_LOGS_DIR}"/.auto-apply-run.* "${SCRIPT_DIR}"/.auto-apply-run.*; do
    [[ -d "${dir}" && "${dir}" != "${SESSION_DIR}" ]] || continue
    score=0
    for change in "${TARGET_CHANGES[@]}"; do
      file="${dir}/${change}.result"
      [[ -f "${file}" ]] && score=$((score + 1))
    done
    [[ "${score}" -gt 0 ]] || continue
    mtime=$(stat -c %Y "${dir}" 2>/dev/null || echo 0)
    if [[ "${score}" -gt "${best_score}" || ( "${score}" -eq "${best_score}" && "${mtime}" -gt "${best_mtime}" ) ]]; then
      best="${dir}"; best_score="${score}"; best_mtime="${mtime}"
    fi
  done
  shopt -u nullglob
  printf '%s\n' "${best}"
}

ensure_session_dir() {
  local legacy=""
  SESSION_KEY="$(derive_session_key)"
  mkdir -p "${AUTO_LOGS_DIR}" || fail "Failed to create ${AUTO_LOGS_DIR}"
  SESSION_DIR="${AUTO_LOGS_DIR}/.auto-apply-run.${SESSION_KEY}"
  [[ ! -e "${SESSION_DIR}" || -d "${SESSION_DIR}" ]] || fail "Session archive path is not a directory: ${SESSION_DIR}"
  [[ -d "${SESSION_DIR}" ]] && return 0
  legacy="$(select_legacy_session_dir)"
  if [[ -n "${legacy}" ]]; then
    cp -a "${legacy}" "${SESSION_DIR}" || fail "Failed to copy ${legacy} -> ${SESSION_DIR}"
    ok "Copied legacy session archive ${legacy} -> ${SESSION_DIR}"
    return 0
  fi
  mkdir -p "${SESSION_DIR}" || fail "Failed to create ${SESSION_DIR}"
}

change_port_profile_file() { printf '%s/%s.ports.env\n' "${SESSION_DIR}" "$1"; }
change_attempt_log_file() { printf '%s/%s.attempt-%s.claude.log\n' "${SESSION_DIR}" "$1" "$2"; }
change_task_sync_log_file() { printf '%s/%s.attempt-%s.tasks-sync.log\n' "${SESSION_DIR}" "$1" "$2"; }
change_handoff_log_file() { printf '%s/%s.attempt-%s.handoff.claude.log\n' "${SESSION_DIR}" "$1" "$2"; }
change_assessment_log_file() { printf '%s/%s.incomplete-assessment.log\n' "${SESSION_DIR}" "$1"; }
change_cleanup_log_file() { printf '%s/%s.cleanup.claude.log\n' "${SESSION_DIR}" "$1"; }
change_merge_log_file() { printf '%s/%s.merge-fallback.claude.log\n' "${SESSION_DIR}" "$1"; }
change_branch_cleanup_log_file() { printf '%s/%s.branch-cleanup.log\n' "${SESSION_DIR}" "$1"; }

append_log_note() {
  local file="$1" note="$2"
  mkdir -p "$(dirname "${file}")"
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "${note}" >> "${file}"
}

claude_output_has_rate_limit_error() {
  local file="$1"
  [[ -f "${file}" ]] || return 1
  grep -Eq 'API Error: 429|"code":"1302"|速率限制|rate limit' "${file}"
}

claude_rate_limit_delay_seconds() {
  local retry_number="$1" delay="${CLAUDE_RATE_LIMIT_BASE_DELAY_SECONDS:-30}" i
  [[ "${retry_number}" =~ ^[0-9]+$ ]] || retry_number=1
  [[ "${delay}" =~ ^[0-9]+$ && "${delay}" -ge 1 ]] || delay=30
  for ((i=1; i<retry_number; i+=1)); do
    delay=$((delay * 2))
    if [[ "${CLAUDE_RATE_LIMIT_MAX_DELAY_SECONDS}" =~ ^[0-9]+$ && "${CLAUDE_RATE_LIMIT_MAX_DELAY_SECONDS}" -ge 1 && "${delay}" -gt "${CLAUDE_RATE_LIMIT_MAX_DELAY_SECONDS}" ]]; then
      delay="${CLAUDE_RATE_LIMIT_MAX_DELAY_SECONDS}"
      break
    fi
  done
  printf '%s\n' "${delay}"
}

run_claude_command_with_retry() {
  local workdir="$1" prompt="$2" prefix="$3" output_file="${4:-}" context_label="${5:-Claude command}"
  local attempt=1 retry_number=0 max_attempts=1 delay=0 rc=0 tmp_file=""

  [[ "${CLAUDE_RATE_LIMIT_RETRY_LIMIT}" =~ ^[0-9]+$ && "${CLAUDE_RATE_LIMIT_RETRY_LIMIT}" -ge 0 ]] || CLAUDE_RATE_LIMIT_RETRY_LIMIT=3
  max_attempts=$((CLAUDE_RATE_LIMIT_RETRY_LIMIT + 1))

  while (( attempt <= max_attempts )); do
    tmp_file="$(mktemp)"
    if (( attempt > 1 )); then
      retry_number=$((attempt - 1))
      [[ -n "${output_file}" ]] && append_log_note "${output_file}" "${context_label}: retry attempt ${retry_number}/${CLAUDE_RATE_LIMIT_RETRY_LIMIT}"
    fi

    (
      cd "${workdir}" || exit 1
      "${CLAUDE_CMD[@]}" "${prompt}" 2>&1
    ) | while IFS= read -r line || [[ -n "${line}" ]]; do
      printf '%s %s\n' "${prefix}" "${line}"
      printf '%s\n' "${line}" >> "${tmp_file}"
      [[ -n "${output_file}" ]] && printf '%s\n' "${line}" >> "${output_file}"
    done
    rc="${PIPESTATUS[0]}"

    if [[ "${rc}" -eq 0 ]]; then
      if (( attempt > 1 )); then
        retry_number=$((attempt - 1))
        [[ -n "${output_file}" ]] && append_log_note "${output_file}" "${context_label}: recovered after rate-limit retry ${retry_number}/${CLAUDE_RATE_LIMIT_RETRY_LIMIT}"
      fi
      rm -f "${tmp_file}"
      return 0
    fi

    if ! claude_output_has_rate_limit_error "${tmp_file}"; then
      rm -f "${tmp_file}"
      return "${rc}"
    fi

    if (( attempt >= max_attempts )); then
      [[ -n "${output_file}" ]] && append_log_note "${output_file}" "${context_label}: exhausted Claude rate-limit retries after ${attempt} attempts"
      warn "${context_label} hit Claude API rate limits repeatedly; exhausted ${CLAUDE_RATE_LIMIT_RETRY_LIMIT} retries"
      rm -f "${tmp_file}"
      return "${rc}"
    fi

    retry_number="${attempt}"
    delay="$(claude_rate_limit_delay_seconds "${retry_number}")"
    [[ -n "${output_file}" ]] && append_log_note "${output_file}" "${context_label}: Claude returned API Error 429/code 1302, sleeping ${delay}s before retry ${retry_number}/${CLAUDE_RATE_LIMIT_RETRY_LIMIT}"
    warn "${context_label} hit Claude API rate limits (429/1302); sleeping ${delay}s before retry ${retry_number}/${CLAUDE_RATE_LIMIT_RETRY_LIMIT}"
    rm -f "${tmp_file}"
    sleep "${delay}"
    attempt=$((attempt + 1))
  done

  return "${rc}"
}

worktree_current_branch() {
  git -C "$1" branch --show-current 2>/dev/null || true
}

worktree_has_local_changes() {
  [[ -n "$(git -C "$1" status --porcelain --untracked-files=normal 2>/dev/null)" ]]
}

canonical_repo_common_dir() {
  local dir="$1" common=""
  common="$(git -C "${dir}" rev-parse --git-common-dir 2>/dev/null || true)"
  [[ -n "${common}" ]] || return 1
  (
    cd "${dir}" >/dev/null 2>&1 || exit 1
    cd "${common}" >/dev/null 2>&1 || exit 1
    pwd -P
  )
}

worktree_dir_is_reusable_for_project() {
  local dir="$1" project_common="" dir_common="" dir_top="" dir_phys=""
  [[ -d "${dir}" ]] || return 1
  git -C "${dir}" rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 1
  dir_phys="$(cd "${dir}" >/dev/null 2>&1 && pwd -P)" || return 1
  dir_top="$(git -C "${dir}" rev-parse --show-toplevel 2>/dev/null || true)"
  [[ -n "${dir_top}" ]] || return 1
  dir_top="$(cd "${dir_top}" >/dev/null 2>&1 && pwd -P)" || return 1
  [[ "${dir_top}" == "${dir_phys}" ]] || return 1
  project_common="$(canonical_repo_common_dir "${PROJECT_ROOT}")" || return 1
  dir_common="$(canonical_repo_common_dir "${dir}")" || return 1
  [[ "${dir_common}" == "${project_common}" ]]
}

worktree_git_path_exists() {
  local dir="$1" name="$2" path=""
  path="$(git -C "${dir}" rev-parse --git-path "${name}" 2>/dev/null || true)"
  [[ -n "${path}" && -e "${path}" ]]
}

worktree_has_pending_parent_managed_merge_state() {
  local dir="$1" integ="$2" current_branch=""
  current_branch="$(worktree_current_branch "${dir}")"
  [[ "${current_branch}" == "${integ}" ]] || return 1
  [[ -n "$(git -C "${dir}" diff --name-only --diff-filter=U 2>/dev/null)" ]] && return 0
  worktree_git_path_exists "${dir}" "SQUASH_MSG" && return 0
  worktree_git_path_exists "${dir}" "MERGE_MSG" && return 0
  worktree_git_path_exists "${dir}" "AUTO_MERGE" && return 0
  return 1
}

switch_worktree_branch() {
  local change="$1" dir="$2" branch="$3" holders=""
  git -C "${dir}" switch "${branch}" >/dev/null 2>&1 && return 0
  holders="$(find_worktree_holders_for_branch "${branch}" | grep -Fxv "${dir}" | tr '\n' ',' | sed 's/,$//')"
  if [[ -n "${holders}" ]]; then
    warn "Failed to switch ${change} worktree to ${branch}; it is currently checked out by: ${holders}"
  else
    warn "Failed to switch ${change} worktree to ${branch}"
  fi
  return 1
}

ensure_change_port_profile() {
  local change="$1" file profile PORT_SLOT=0 max_slot=0 slot api worker mock grpc
  file="$(change_port_profile_file "${change}")"
  [[ -f "${file}" ]] && { printf '%s\n' "${file}"; return 0; }
  shopt -s nullglob
  for profile in "${SESSION_DIR}"/*.ports.env; do
    PORT_SLOT=0
    source "${profile}"
    [[ "${PORT_SLOT}" =~ ^[0-9]+$ && "${PORT_SLOT}" -gt "${max_slot}" ]] && max_slot="${PORT_SLOT}"
  done
  shopt -u nullglob
  slot=$((max_slot + 1)); api=$((PORT_BLOCK_BASE + slot * PORT_BLOCK_SIZE)); worker=$((api + 1)); mock=$((api + 2)); grpc=$((api + 3))
  cat >"${file}" <<EOF2
PORT_SLOT=${slot}
API_PORT=${api}
WORKER_PORT=${worker}
AGENT_RUNTIME_MOCK_PORT=${mock}
AGENT_RUNTIME_GRPC_PORT=${grpc}
AGENT_RUNTIME_BASE_URL=http://localhost:${mock}
AGENT_RUNTIME_GRPC_TARGET=127.0.0.1:${grpc}
EOF2
  change_log "${change}" "Allocated ports: API=${api}, WORKER=${worker}, MOCK=${mock}, GRPC=${grpc}" >&2
  printf '%s\n' "${file}"
}

seed_worktree_env_if_needed() {
  local change="$1" dir="$2" example="${dir}/.env.example" env="${dir}/.env" profile=""
  local PORT_SLOT=0 API_PORT=0 WORKER_PORT=0 AGENT_RUNTIME_MOCK_PORT=0 AGENT_RUNTIME_GRPC_PORT=0 AGENT_RUNTIME_BASE_URL="" AGENT_RUNTIME_GRPC_TARGET=""
  [[ -f "${env}" ]] && return 0
  [[ -f "${example}" ]] || fail "Missing .env.example in ${dir}"
  profile="$(ensure_change_port_profile "${change}")" || return 1
  source "${profile}"
  python3 - "${example}" "${env}" "${change}" "${PORT_SLOT}" "${API_PORT}" "${WORKER_PORT}" "${AGENT_RUNTIME_MOCK_PORT}" "${AGENT_RUNTIME_GRPC_PORT}" "${AGENT_RUNTIME_BASE_URL}" "${AGENT_RUNTIME_GRPC_TARGET}" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]); dst = Path(sys.argv[2]); change = sys.argv[3]; slot = sys.argv[4]
updates = {
    "API_PORT": sys.argv[5], "WORKER_PORT": sys.argv[6],
    "AGENT_RUNTIME_MOCK_PORT": sys.argv[7], "AGENT_RUNTIME_GRPC_PORT": sys.argv[8],
    "AGENT_RUNTIME_BASE_URL": sys.argv[9], "AGENT_RUNTIME_GRPC_TARGET": sys.argv[10],
}
lines = src.read_text(encoding="utf-8").splitlines()
out = [f"# Auto-generated for worktree change {change} (port slot {slot})", "# Shared infrastructure ports stay unchanged; local listener ports are isolated per worktree."]
for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in line:
        out.append(line)
        continue
    key, _ = line.split("=", 1)
    key = key.strip()
    out.append(f"{key}={updates[key]}" if key in updates else line)
dst.write_text("\n".join(out) + "\n", encoding="utf-8")
PY
  change_log "${change}" "Created .env with isolated listener ports" >&2
}

base_ref_for_change() {
  local change="$1" prefix
  prefix="$(series_prefix_for_change "${change}")"
  if [[ -n "${prefix}" ]]; then
    git_ref_exists "refs/heads/series/${prefix}" && { printf 'series/%s\n' "${prefix}"; return 0; }
    git_ref_exists "refs/remotes/origin/series/${prefix}" && { printf 'origin/series/%s\n' "${prefix}"; return 0; }
  fi
  git_ref_exists "refs/heads/dev" && { printf 'dev\n'; return 0; }
  git_ref_exists "refs/remotes/origin/dev" && { printf 'origin/dev\n'; return 0; }
  printf 'HEAD\n'
}

prepare_worktree_for_change() {
  local change="$1" dir="${WORKTREE_ROOT}/${change}" ref registered=0 reusable_existing=0
  mkdir -p "${WORKTREE_ROOT}"
  ref="$(base_ref_for_change "${change}")"
  git -C "${PROJECT_ROOT}" worktree list --porcelain | grep -F "worktree ${dir}" >/dev/null 2>&1 && registered=1
  worktree_dir_is_reusable_for_project "${dir}" && reusable_existing=1
  if [[ "${registered}" -eq 1 ]]; then
    change_log "${change}" "Reusing isolated worktree at ${dir}" >&2
  elif [[ "${reusable_existing}" -eq 1 ]]; then
    git -C "${PROJECT_ROOT}" worktree repair "${dir}" >/dev/null 2>&1 || true
    change_log "${change}" "Reusing existing isolated worktree at ${dir} even though it was not listed in worktree metadata" >&2
  elif [[ -e "${dir}" ]]; then
    fail "Worktree path exists but is not registered: ${dir}"
  else
    if git -C "${PROJECT_ROOT}" worktree add --detach "${dir}" "${ref}" >/dev/null 2>&1; then
      change_log "${change}" "Created isolated worktree at ${dir} from ${ref}" >&2
    elif worktree_dir_is_reusable_for_project "${dir}"; then
      git -C "${PROJECT_ROOT}" worktree repair "${dir}" >/dev/null 2>&1 || true
      change_log "${change}" "Reusing isolated worktree at ${dir} after worktree add reported a recoverable failure" >&2
    else
      fail "Failed to create worktree for ${change} from ${ref}"
    fi
  fi
  [[ -e "${dir}/openspec" ]] || fail "Missing openspec entry in ${dir}. The main repository must track the openspec symlink before running auto_apply."
  seed_worktree_env_if_needed "${change}" "${dir}" || fail "Failed to initialize .env for ${change}"
  printf '%s\n' "${dir}"
}

ensure_local_integration_branch() {
  local change="$1" integ="$2" base_ref=""
  git_ref_exists "refs/heads/${integ}" && return 0
  if git_ref_exists "refs/remotes/origin/${integ}"; then
    git -C "${PROJECT_ROOT}" branch --track "${integ}" "origin/${integ}" >/dev/null 2>&1 || {
      warn "Failed to create local integration branch ${integ} for ${change}"
      return 1
    }
    change_log "${change}" "Created local integration branch ${integ} from origin/${integ}" >&2
    return 0
  fi
  if git_ref_exists "refs/heads/dev"; then
    base_ref="dev"
  elif git_ref_exists "refs/remotes/origin/dev"; then
    base_ref="origin/dev"
  else
    base_ref="HEAD"
  fi
  git -C "${PROJECT_ROOT}" branch "${integ}" "${base_ref}" >/dev/null 2>&1 || {
    warn "Failed to create local integration branch ${integ} from ${base_ref} for ${change}"
    return 1
  }
  change_log "${change}" "Created local integration branch ${integ} from ${base_ref}" >&2
}

prepare_parent_managed_series_branching() {
  local change="$1" dir="$2" tasks_file="" default_impl="" default_integ="" impl="" integ="" managed=0
  local is_series=0 start_matches=0 merge_matches=0 full_total=0 full_completed=0 apply_total=0 apply_completed=0
  tasks_file="$(resolve_change_tasks_file "${change}")" || {
    warn "Missing tasks.md for ${change}"
    return 1
  }
  default_impl="$(implementation_branch_for_change "${change}")"
  default_integ="$(integration_branch_for_change "${change}")"
  load_change_git_task_metadata "${change}" "${tasks_file}" "${default_impl}" "${default_integ}" || {
    warn "Failed to inspect standardized git tasks for ${change}"
    return 1
  }
  impl="${CHANGE_IMPL_BRANCH["${change}"]}"
  integ="${CHANGE_INTEGRATION_BRANCH["${change}"]}"
  managed="${CHANGE_PARENT_MANAGED_GIT["${change}"]:-0}"

  [[ "${integ}" != "dev" ]] || return 0
  if [[ "${managed}" -ne 1 ]]; then
    warn "Series change ${change} does not use the standardized auto-managed branch tasks. Regenerate or normalize ${tasks_file} before running auto_apply."
    return 1
  fi

  ensure_local_integration_branch "${change}" "${integ}" || return 1

  if worktree_has_pending_parent_managed_merge_state "${dir}" "${integ}"; then
    change_log "${change}" "Detected existing unresolved parent-managed merge state in ${dir} on ${integ}; will resume merge handling in place" >&2
    return 0
  fi

  if git_ref_exists "refs/heads/${impl}"; then
    switch_worktree_branch "${change}" "${dir}" "${impl}" || return 1
    change_log "${change}" "Switched worktree to existing implementation branch ${impl}" >&2
  else
    git -C "${dir}" switch -c "${impl}" "${integ}" >/dev/null 2>&1 || {
      warn "Failed to create implementation branch ${impl} from ${integ} for ${change}"
      return 1
    }
    change_log "${change}" "Created implementation branch ${impl} from ${integ}" >&2
  fi

  mark_managed_git_tasks_complete "${tasks_file}" "${change}" "${impl}" "${integ}" mark-start
  change_log "${change}" "Marked auto-managed branch preparation tasks complete in ${tasks_file}" >&2
}

find_worktree_holders_for_branch() {
  local branch="$1"
  python3 - "${PROJECT_ROOT}" "${branch}" <<'PY'
from pathlib import Path
import subprocess
import sys

repo = Path(sys.argv[1])
branch = sys.argv[2]
result = subprocess.run(
    ["git", "-C", str(repo), "worktree", "list", "--porcelain"],
    check=True,
    capture_output=True,
    text=True,
)
holders = []
current_worktree = None
current_branch = None
for line in result.stdout.splitlines() + [""]:
    if not line:
        if current_worktree and current_branch == branch:
            holders.append(current_worktree)
        current_worktree = None
        current_branch = None
        continue
    if line.startswith("worktree "):
        current_worktree = line.removeprefix("worktree ").strip()
    elif line.startswith("branch "):
        current_branch = line.removeprefix("branch ").strip()
        if current_branch.startswith("refs/heads/"):
            current_branch = current_branch[len("refs/heads/") :]
for holder in holders:
    print(holder)
PY
}

merge_fallback_completed() {
  local merge_dir="$1" integ="$2" initial_head="$3" current_branch="" current_head=""
  current_branch="$(git -C "${merge_dir}" branch --show-current 2>/dev/null || true)"
  [[ "${current_branch}" == "${integ}" ]] || return 1
  [[ -z "$(git -C "${merge_dir}" diff --name-only --diff-filter=U 2>/dev/null)" ]] || return 1
  [[ -z "$(git -C "${merge_dir}" status --porcelain --untracked-files=normal 2>/dev/null)" ]] || return 1
  current_head="$(git -C "${merge_dir}" rev-parse HEAD 2>/dev/null || true)"
  [[ -n "${current_head}" && "${current_head}" != "${initial_head}" ]] || return 1
}

detach_worktree_at_current_head() {
  local change="$1" dir="$2" current_head=""
  current_head="$(git -C "${dir}" rev-parse --short HEAD 2>/dev/null || true)"
  git -C "${dir}" switch --detach HEAD >/dev/null 2>&1 || git -C "${dir}" checkout --detach HEAD >/dev/null 2>&1 || {
    warn "Failed to detach ${change} worktree at the merged integration commit"
    return 1
  }
  change_log "${change}" "Detached worktree at merged integration commit ${current_head:-unknown}"
}

parent_managed_series_merge() {
  local change="$1" dir="$2" impl="$3" integ="$4" tasks_file="$5"
  local merge_commit_message="${change}" merge_log_file="" initial_head="" merge_fallback_succeeded=0 resume_existing_merge=0 current_head=""

  merge_log_file="$(change_merge_log_file "${change}")"
  : > "${merge_log_file}"

  if worktree_has_pending_parent_managed_merge_state "${dir}" "${integ}"; then
    resume_existing_merge=1
    append_log_note "${merge_log_file}" "Detected existing unresolved merge state in original worktree ${dir} on ${integ}; resuming merge fallback in place"
    change_log "${change}" "Resuming unresolved parent-managed merge in ${dir} on ${integ}"
  else
    switch_worktree_branch "${change}" "${dir}" "${impl}" || return 1
    if ! switch_worktree_branch "${change}" "${dir}" "${integ}"; then
      append_log_note "${merge_log_file}" "Failed to switch original worktree ${dir} to ${integ} before merge"
      return 1
    fi
    append_log_note "${merge_log_file}" "Switched original worktree ${dir} to ${integ} for --no-ff merge of ${impl}"
  fi

  initial_head="$(git -C "${dir}" rev-parse HEAD 2>/dev/null || true)"

  if [[ "${resume_existing_merge}" -eq 0 ]]; then
    if ! git -C "${dir}" merge --no-ff -m "${merge_commit_message}" "${impl}" >> "${merge_log_file}" 2>&1; then
      append_log_note "${merge_log_file}" "Direct parent-managed --no-ff merge failed in original worktree; launching Claude merge fallback"
      warn "Direct parent-managed merge failed for ${change}; launching Claude merge fallback"
      if run_merge_fallback "${change}" "${dir}" "${impl}" "${integ}" "${tasks_file}" "${merge_log_file}" "${merge_commit_message}" \
        && merge_fallback_completed "${dir}" "${integ}" "${initial_head}"; then
        merge_fallback_succeeded=1
        append_log_note "${merge_log_file}" "Claude merge fallback completed the merge successfully"
        change_log "${change}" "Claude merge fallback completed the merge in ${dir}"
      else
        append_log_note "${merge_log_file}" "Claude merge fallback did not complete successfully in original worktree"
        warn "Parent-managed merge failed for ${change}; leaving ${dir} for manual inspection"
        return 1
      fi
    fi
  else
    append_log_note "${merge_log_file}" "Launching Claude merge fallback to continue the existing in-place merge state"
    if run_merge_fallback "${change}" "${dir}" "${impl}" "${integ}" "${tasks_file}" "${merge_log_file}" "${merge_commit_message}" \
      && merge_fallback_completed "${dir}" "${integ}" "${initial_head}"; then
      merge_fallback_succeeded=1
      append_log_note "${merge_log_file}" "Claude merge fallback completed the in-place merge successfully"
      change_log "${change}" "Claude merge fallback completed the in-place merge in ${dir}"
    else
      append_log_note "${merge_log_file}" "Claude merge fallback could not complete the existing in-place merge"
      warn "Parent-managed in-place merge could not be completed for ${change}; leaving ${dir} for manual inspection"
      return 1
    fi
  fi

  current_head="$(git -C "${dir}" rev-parse HEAD 2>/dev/null || true)"
  if [[ "${merge_fallback_succeeded}" -eq 0 ]]; then
    if [[ -n "${current_head}" && "${current_head}" != "${initial_head}" ]]; then
      change_log "${change}" "Merged ${impl} into ${integ} with --no-ff history preservation in the original worktree"
    else
      change_log "${change}" "No new merge commit was needed for ${impl} -> ${integ}; treating merge as already integrated"
    fi
  fi

  mark_managed_git_tasks_complete "${tasks_file}" "${change}" "${impl}" "${integ}" mark-merge

  if ! detach_worktree_at_current_head "${change}" "${dir}"; then
    append_log_note "${merge_log_file}" "Merge completed, but failed to detach the original worktree from ${integ}"
    warn "Parent-managed merge completed for ${change}, but ${dir} is still holding ${integ}"
    return 1
  fi
  append_log_note "${merge_log_file}" "Detached original worktree ${dir} at the merged integration commit after parent-managed merge"
  return 0
}

cleanup_change_branch() {
  local change="$1" impl="${CHANGE_IMPL_BRANCH["${change}"]:-}" integ="${CHANGE_INTEGRATION_BRANCH["${change}"]:-}" branch_cleanup_log_file="" holders=""
  [[ -n "${impl}" && -n "${integ}" ]] || return 0
  git_ref_exists "refs/heads/${impl}" || return 0

  branch_cleanup_log_file="$(change_branch_cleanup_log_file "${change}")"
  : > "${branch_cleanup_log_file}"
  append_log_note "${branch_cleanup_log_file}" "Attempting implementation branch cleanup for ${impl} after successful archive"

  if ! git_ref_exists "refs/heads/${integ}"; then
    append_log_note "${branch_cleanup_log_file}" "Integration branch ${integ} is missing; cannot verify branch ancestry for ${impl}"
    append_unique "${change}" BRANCH_CLEANUP_FAILED_CHANGES
    warn "Skipping deletion of ${impl} for ${change} because ${integ} is missing"
    return 1
  fi

  holders="$(find_worktree_holders_for_branch "${impl}" | tr '\n' ',' | sed 's/,$//')"
  if [[ -n "${holders}" ]]; then
    append_log_note "${branch_cleanup_log_file}" "Implementation branch ${impl} is still checked out by: ${holders}"
    append_unique "${change}" BRANCH_CLEANUP_FAILED_CHANGES
    warn "Skipping deletion of ${impl} for ${change}; branch is still checked out by: ${holders}"
    return 1
  fi

  if ! git -C "${PROJECT_ROOT}" merge-base --is-ancestor "${impl}" "${integ}" >/dev/null 2>&1; then
    append_log_note "${branch_cleanup_log_file}" "Implementation branch ${impl} is not an ancestor of ${integ}; refusing to delete it"
    append_unique "${change}" BRANCH_CLEANUP_FAILED_CHANGES
    warn "Skipping deletion of ${impl} for ${change}; it is not merged into ${integ}"
    return 1
  fi

  if ! git -C "${PROJECT_ROOT}" branch -D "${impl}" >> "${branch_cleanup_log_file}" 2>&1; then
    append_log_note "${branch_cleanup_log_file}" "git branch -D ${impl} failed"
    append_unique "${change}" BRANCH_CLEANUP_FAILED_CHANGES
    warn "Failed to delete implementation branch ${impl} for ${change}"
    return 1
  fi

  append_unique "${change}" BRANCH_CLEANED_CHANGES
  change_log "${change}" "Deleted merged implementation branch ${impl}"
  return 0
}

cleanup_change_worktree() {
  local change="$1" dir="${CHANGE_WORKTREE["${change}"]:-}"
  local cleanup_log_file=""
  [[ -n "${dir}" ]] || return 0
  [[ -d "${dir}" ]] || return 0
  if [[ -n "$(git -C "${dir}" status --porcelain --untracked-files=normal 2>/dev/null)" ]]; then
    change_log "${change}" "Direct cleanup skipped because ${dir} still has uncommitted changes; launching Claude fallback"
    cleanup_log_file="$(change_cleanup_log_file "${change}")"
    : > "${cleanup_log_file}"
    append_log_note "${cleanup_log_file}" "Direct cleanup skipped because ${dir} still has uncommitted changes"
    git -C "${dir}" status --short >> "${cleanup_log_file}" 2>&1 || true
    if run_cleanup_fallback "${change}" "${dir}" "${cleanup_log_file}" && ! [[ -d "${dir}" ]]; then
      change_log "${change}" "Removed isolated worktree ${dir} via Claude cleanup fallback"
      return 0
    fi
    append_unique "${change}" CLEANUP_FAILED_CHANGES
    change_log "${change}" "Cleanup fallback did not remove ${dir}"
    return 1
  fi
  cleanup_log_file="$(change_cleanup_log_file "${change}")"
  : > "${cleanup_log_file}"
  append_log_note "${cleanup_log_file}" "Attempting direct git worktree remove for ${dir}"
  if ! git -C "${PROJECT_ROOT}" worktree remove "${dir}" >> "${cleanup_log_file}" 2>&1; then
    append_log_note "${cleanup_log_file}" "Direct git worktree remove failed; launching Claude cleanup fallback"
    change_log "${change}" "Direct cleanup failed for ${dir}; launching Claude fallback"
    if run_cleanup_fallback "${change}" "${dir}" "${cleanup_log_file}" && ! [[ -d "${dir}" ]]; then
      change_log "${change}" "Removed isolated worktree ${dir} via Claude cleanup fallback"
      return 0
    fi
    append_unique "${change}" CLEANUP_FAILED_CHANGES
    change_log "${change}" "Failed to remove isolated worktree ${dir}"
    return 1
  fi
  change_log "${change}" "Removed isolated worktree ${dir}"
}

json_get_change_names() {
  local payload="$1"
  shift
  python3 - "$payload" "$@" <<'PY'
import json, sys
payload = json.loads(sys.argv[1])
prefixes = [item for item in sys.argv[2:] if item]
names = []
for item in payload.get("changes", []):
    name = item.get("name")
    if not name:
        continue
    if prefixes and not any(name.startswith(prefix) for prefix in prefixes):
        continue
    names.append(name)
for name in sorted(names):
    print(name)
PY
}

json_change_progress() {
  local change="$1" payload="$2"
  python3 - "$change" "$payload" <<'PY'
import json, sys
target = sys.argv[1]
payload = json.loads(sys.argv[2])
for item in payload.get("changes", []):
    if item.get("name") == target:
        print(item.get("completedTasks", 0))
        print(item.get("totalTasks", 0))
        raise SystemExit(0)
print("0")
print("0")
PY
}

json_validate_result() {
  local payload="$1"
  python3 - "$payload" <<'PY'
import json, sys
payload = json.loads(sys.argv[1])
items = payload.get("items", [])
print("true" if items and items[0].get("valid") else "false")
PY
}

json_validate_issue_lines() {
  local payload="$1"
  python3 - "$payload" <<'PY'
import json, sys
payload = json.loads(sys.argv[1])
for item in payload.get("items", []):
    item_id = item.get("id") or "<unknown>"
    item_type = item.get("type") or "item"
    issues = item.get("issues") or []
    if not issues and item.get("valid") is False:
        print(f"{item_type} {item_id}: validation failed without detailed issues")
        continue
    for issue in issues:
        level = issue.get("level") or "ERROR"
        path = issue.get("path") or "unknown-path"
        message = issue.get("message") or "unknown validation issue"
        print(f"{item_type} {item_id} [{level}] {path}: {message}")
PY
}

parse_incomplete_assessment_output() {
  local file="$1"
  python3 - "${file}" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()
data = {}
for raw in text:
    line = raw.strip()
    for key in ("NEEDS_HUMAN", "REASON", "NEXT_ACTION"):
        prefix = key + "="
        if line.startswith(prefix) and key not in data:
            data[key] = line[len(prefix):].strip()
            break

needs_human = data.get("NEEDS_HUMAN", "").lower()
reason = data.get("REASON", "")
next_action = data.get("NEXT_ACTION", "")

if needs_human not in {"yes", "no"} or not reason or not next_action:
    raise SystemExit(1)

print(needs_human)
print(reason)
print(next_action)
PY
}

resolve_active_change_dir() {
  local change="$1" dir="${OPENSPEC_ROOT}/changes/${change}"
  [[ -d "${dir}" ]] && printf '%s\n' "${dir}"
}

resolve_archived_change_dir() {
  local change="$1"
  python3 - "${OPENSPEC_ROOT}" "${change}" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
change = sys.argv[2]
archive_root = root / "changes" / "archive"
matches = []

direct = archive_root / change
if direct.is_dir():
    matches.append(direct)

if archive_root.is_dir():
    matches.extend(sorted(p for p in archive_root.glob(f"*-{change}") if p.is_dir()))

if matches:
    print(matches[-1])
PY
}

resolve_change_tasks_file() {
  local change="$1" active_dir="" archived_dir=""
  active_dir="$(resolve_active_change_dir "${change}")"
  if [[ -n "${active_dir}" && -f "${active_dir}/tasks.md" ]]; then
    printf '%s\n' "${active_dir}/tasks.md"
    return 0
  fi

  archived_dir="$(resolve_archived_change_dir "${change}")"
  if [[ -n "${archived_dir}" && -f "${archived_dir}/tasks.md" ]]; then
    printf '%s\n' "${archived_dir}/tasks.md"
    return 0
  fi

  return 1
}

collect_change_artifact_paths() {
  local change="$1" change_dir="" path=""
  change_dir="$(resolve_active_change_dir "${change}" 2>/dev/null || true)"
  [[ -n "${change_dir}" ]] || change_dir="$(resolve_archived_change_dir "${change}" 2>/dev/null || true)"
  [[ -n "${change_dir}" ]] || return 0

  for path in "${change_dir}/proposal.md" "${change_dir}/design.md" "${change_dir}/tasks.md"; do
    [[ -f "${path}" ]] && printf '%s\n' "${path}"
  done

  [[ -d "${change_dir}/specs" ]] || return 0
  find "${change_dir}/specs" -type f -name 'spec.md' | sort
}

inspect_managed_git_tasks() {
  local tasks_file="$1" change="$2" default_impl="$3" default_integ="$4"
  python3 "${TASKS_GIT_HELPER}" inspect \
    --tasks "${tasks_file}" \
    --change "${change}" \
    --default-impl "${default_impl}" \
    --default-integ "${default_integ}"
}

mark_managed_git_tasks_complete() {
  local tasks_file="$1" change="$2" default_impl="$3" default_integ="$4" mode="$5"
  python3 "${TASKS_GIT_HELPER}" "${mode}" \
    --tasks "${tasks_file}" \
    --change "${change}" \
    --default-impl "${default_impl}" \
    --default-integ "${default_integ}" >/dev/null
}

load_change_git_task_metadata() {
  local change="$1" tasks_file="$2" default_impl="$3" default_integ="$4"
  local impl="" integ="" is_series=0 start_matches=0 merge_matches=0 full_total=0 full_completed=0 apply_total=0 apply_completed=0
  local metadata=""
  metadata="$(inspect_managed_git_tasks "${tasks_file}" "${change}" "${default_impl}" "${default_integ}")" || return 1
  eval "${metadata}"
  CHANGE_TASKS_FILE["${change}"]="${tasks_file}"
  CHANGE_IMPL_BRANCH["${change}"]="${impl:-${default_impl}}"
  CHANGE_INTEGRATION_BRANCH["${change}"]="${integ:-${default_integ}}"
  if [[ "${is_series:-0}" -eq 1 && "${start_matches:-0}" -gt 0 && "${merge_matches:-0}" -gt 0 ]]; then
    CHANGE_PARENT_MANAGED_GIT["${change}"]=1
  else
    CHANGE_PARENT_MANAGED_GIT["${change}"]=0
  fi
}

read_change_task_progress() {
  local change="$1" mode="${2:-full}" tasks_file="" default_impl="" default_integ=""
  local impl="" integ="" is_series=0 start_matches=0 merge_matches=0 full_total=0 full_completed=0 apply_total=0 apply_completed=0
  local metadata=""
  tasks_file="$(resolve_change_tasks_file "${change}")" || return 1
  default_impl="${CHANGE_IMPL_BRANCH["${change}"]:-$(implementation_branch_for_change "${change}")}"
  default_integ="${CHANGE_INTEGRATION_BRANCH["${change}"]:-$(integration_branch_for_change "${change}")}"
  metadata="$(inspect_managed_git_tasks "${tasks_file}" "${change}" "${default_impl}" "${default_integ}")" || return 1
  eval "${metadata}"
  if [[ "${mode}" == "apply" ]]; then
    printf '%s\n%s\n' "${apply_completed:-0}" "${apply_total:-0}"
  else
    printf '%s\n%s\n' "${full_completed:-0}" "${full_total:-0}"
  fi
}

change_is_archived() {
  local change="$1"
  if [[ -n "$(resolve_active_change_dir "${change}")" ]]; then
    return 1
  fi
  [[ -n "$(resolve_archived_change_dir "${change}")" ]]
}

restore_change_state_from_tasks_truth() {
  local change="$1" result_file="$2" tasks_file="" archived=0 completed=0 total=0
  local human_reason="" human_next_action=""
  local -a progress_lines=()

  tasks_file="$(resolve_change_tasks_file "${change}")" || return 1
  change_is_archived "${change}" && archived=1 || archived=0
  [[ "${archived}" -eq 1 ]] || return 1

  if ! mapfile -t progress_lines < <(read_change_task_progress "${change}" full); then
    return 1
  fi

  completed="${progress_lines[0]:-0}"
  total="${progress_lines[1]:-0}"

  if [[ "${total}" -gt 0 && "${completed}" -eq "${total}" ]]; then
    write_result_file "${result_file}" success "${completed}" "${total}" 1
    CHANGE_STATE["${change}"]="success"
    append_unique "${change}" COMPLETED_CHANGES
    append_unique "${change}" ARCHIVED_CHANGES
    append_unique "${change}" RESTORED_CHANGES
    change_log "${change}" "Restored archived completed state from ${tasks_file}"
    return 0
  fi

  human_reason="Archived change ${change} exists, but tasks.md shows incomplete progress (${completed}/${total})."
  human_next_action="Inspect ${tasks_file} and reconcile the archived change manually before rerunning auto_apply."
  write_result_file "${result_file}" needs_human "${completed}" "${total}" 1 1 "${human_reason}" "${human_next_action}"
  CHANGE_STATE["${change}"]="failed"
  append_unique "${change}" FAILED_CHANGES
  append_unique "${change}" HUMAN_REVIEW_CHANGES
  CHANGE_HUMAN_REASON["${change}"]="${human_reason}"
  CHANGE_HUMAN_ACTION["${change}"]="${human_next_action}"
  change_log "${change}" "Archived change exists but cannot be treated as completed because tasks.md is ${completed}/${total}"
  return 0
}

json_missing_changes() {
  local payload="$1"; shift
  python3 - "$payload" "$@" <<'PY'
import json, sys
payload = json.loads(sys.argv[1])
known = {item.get("name") for item in payload.get("changes", []) if item.get("name")}
for name in sys.argv[2:]:
    if name not in known:
        print(name)
PY
}

normalize_dependency_graphs() {
  python3 - "$@" <<'PY'
import json, sys
from pathlib import Path
graph = {}
args = sys.argv[1:]
if "--" in args:
    idx = args.index("--")
    file_args = args[:idx]
    roots = args[idx + 1:]
else:
    file_args = args
    roots = []
def norm(raw):
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        if not all(isinstance(x, str) for x in raw):
            raise SystemExit("Dependency names must be strings")
        return list(raw)
    raise SystemExit("Unsupported dependency value")
def merge_entry(name, deps):
    graph.setdefault(name, [])
    for dep in deps:
        if dep not in graph[name]:
            graph[name].append(dep)

for file_arg in file_args:
    payload = json.loads(Path(file_arg).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("changes"), list):
        for item in payload["changes"]:
            if not isinstance(item, dict):
                raise SystemExit("Each changes[] item must be an object")
            name = item.get("name") or item.get("id")
            if not isinstance(name, str) or not name:
                raise SystemExit("Each changes[] item must include a non-empty name or id")
            merge_entry(name, norm(item.get("dependsOn", item.get("depends_on", item.get("deps")))))
    elif isinstance(payload, dict):
        for name, deps in payload.items():
            if not isinstance(name, str) or not name:
                raise SystemExit("Dependency graph keys must be non-empty strings")
            merge_entry(name, norm(deps))
    else:
        raise SystemExit("Dependency file must be an object or a {\"changes\": [...]} wrapper")
for name, deps in list(graph.items()):
    graph.setdefault(name, [])
    for dep in deps:
        graph.setdefault(dep, [])
selected = set()
def visit(name):
    graph.setdefault(name, [])
    if name in selected:
        return
    selected.add(name)
    for dep in graph.get(name, []):
        visit(dep)
if roots:
    for root in roots:
        visit(root)
else:
    selected.update(graph.keys())
temp, perm = set(), set()
def dfs(name, stack):
    if name in perm or name not in selected:
        return
    if name in temp:
        raise SystemExit("Dependency cycle detected: " + " -> ".join(stack + [name]))
    temp.add(name); stack.append(name)
    for dep in graph.get(name, []):
        dfs(dep, stack)
    stack.pop(); temp.remove(name); perm.add(name)
for name in sorted(selected):
    dfs(name, [])
for name in sorted(selected):
    print(f"{name}\t{' '.join(dep for dep in graph.get(name, []) if dep in selected)}")
PY
}

build_prompt() {
  local change="$1" dir="$2" instructions_json="$3" extra_guidance="${4:-}" series="" impl="" integ="" guidance="" extra_section="" managed=0 current_branch="" existing_state_block="" local_db_reset_block="" line=""
  local -a status_lines=()
  series="$(series_prefix_for_change "${change}")"
  current_branch="$(worktree_current_branch "${dir}")"
  local_db_reset_block="$(build_local_db_reset_guidance)"
  mapfile -t status_lines < <(git -C "${dir}" status --short --untracked-files=normal 2>/dev/null || true)
  if [[ "${#status_lines[@]}" -gt 0 ]]; then
    existing_state_block=$'Current worktree state before you begin:\n'
    existing_state_block+="- Current branch: \`${current_branch:-detached HEAD}\`"$'\n'
    existing_state_block+="- Existing \`git status --short\` entries:\n"
    for line in "${status_lines[@]}"; do
      existing_state_block+="  - \`${line}\`"$'\n'
    done
    existing_state_block+=$'Treat these staged, unstaged, or untracked files as inherited in-progress state for this same change unless you verify they are obsolete residue. Reconcile this state before adding more edits.\n'
  else
    existing_state_block=$'Current worktree state before you begin:\n'
    existing_state_block+="- Current branch: \`${current_branch:-detached HEAD}\`"$'\n'
    existing_state_block+="- `git status --short` is currently clean.\n"
  fi
  if [[ -n "${series}" ]]; then
    impl="${CHANGE_IMPL_BRANCH["${change}"]:-$(implementation_branch_for_change "${change}")}"
    integ="${CHANGE_INTEGRATION_BRANCH["${change}"]:-$(integration_branch_for_change "${change}")}"
    managed="${CHANGE_PARENT_MANAGED_GIT["${change}"]:-0}"
    guidance="$(cat <<EOF2
- For this series change, the wrapper script has already prepared the isolated worktree on the implementation branch \`${impl}\`.
- The wrapper script, not the child agent, owns the standardized branch preparation checkbox tasks and the final merge back to \`${integ}\`.
- Do not create or switch to another implementation or integration branch unless \`tasks.md\` explicitly requires a different branch name and the wrapper-prepared branch is clearly wrong.
- Do not perform the final merge back to \`${integ}\` yourself. Focus on implementation, validation, and keeping non-wrapper tasks in \`tasks.md\` synchronized with reality.
- Commit meaningful implementation changes yourself on \`${impl}\` before you finish. Leave the worktree clean for handoff; do not leave staged, unstaged, or untracked files behind unless you are explicitly stopping because of a blocker and you explain it.
EOF2
)"
  fi
  if [[ -n "${extra_guidance}" ]]; then
    extra_section="$(cat <<EOF2

Additional focus for this run:
${extra_guidance}
EOF2
)"
  fi
  cat <<EOF2
You are implementing the OpenSpec change \`${change}\` in the project at:
\`${dir}\`

The canonical main repository is:
\`${PROJECT_ROOT}\`

The OpenSpec repository is available inside the worktree at:
\`${dir}/openspec\`

Follow the OpenSpec apply instructions below exactly.

Important requirements:
- Work only from the isolated worktree above.
- Do not switch branches or edit files in the canonical main repository path directly.
- The isolated worktree may start from a detached base ref.
- Begin by checking \`git status --short\` in this worktree. If existing local changes are present, treat them as inherited state from the current change unless you verify they are safe residue to remove.
- Keep \`openspec/changes/${change}/tasks.md\` synchronized with the real completion status of this change as you work.
- Run relevant tests or validation when appropriate.
- Before finishing a successful pass, leave this worktree clean on the implementation branch. Commit meaningful changes yourself with clear commit messages; only remove leftover files after verifying they are safe to drop.
- Do not archive the change yourself; the wrapper script will decide that.
- If you hit a blocker, explain it clearly and stop rather than pretending the change is complete.

${existing_state_block}
${guidance}
${local_db_reset_block}
${extra_section}

OpenSpec apply instructions:
\`\`\`json
${instructions_json}
\`\`\`
EOF2
}
run_claude_for_change() {
  local change="$1" dir="$2" instructions_json="$3" transcript_file="${4:-}" extra_guidance="${5:-}" prompt prefix rc
  prompt="$(build_prompt "${change}" "${dir}" "${instructions_json}" "${extra_guidance}")"
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    change_log "${change}" "Dry run: would invoke Claude in ${dir}"
    return 0
  fi
  [[ -n "${transcript_file}" ]] && : > "${transcript_file}"
  prefix="$(tag "${C_DIM}" "claude:${change}")"
  rc=0
  run_claude_command_with_retry "${dir}" "${prompt}" "${prefix}" "${transcript_file}" "Claude apply for ${change}" || rc=$?
  return "${rc}"
}

build_task_sync_prompt() {
  local change="$1" dir="$2" transcript_file="$3" completed="$4" total="$5"
  cat <<EOF2
You are doing a focused tasks synchronization pass for OpenSpec change \`${change}\`.

Worktree:
\`${dir}\`

OpenSpec repository inside the worktree:
\`${dir}/openspec\`

Previous apply transcript:
\`${transcript_file}\`

Current recorded task progress before this sync pass: ${completed}/${total}

Your job is only to reconcile \`openspec/changes/${change}/tasks.md\` with the real current state of the worktree.

Rules:
- Do not implement new product scope in this pass.
- Inspect the actual worktree state and the current \`tasks.md\`.
- If a checkbox task is already fully done, mark it complete.
- Leave wrapper-managed branch preparation and final merge-back tasks alone; the parent script will synchronize those itself.
- If a checkbox line is only descriptive, manual-only, or out of scope for this change, rewrite it as a plain note instead of leaving it as an unchecked checkbox.
- If a task is not actually done yet, leave it unchecked.
- Do not archive the change.
- Do not touch the canonical main repository path.

When this pass ends, \`tasks.md\` should reflect the real completion status as accurately as possible.
EOF2
}

run_task_sync() {
  local change="$1" dir="$2" transcript_file="$3" completed="$4" total="$5" output_file="$6"
  local prompt prefix rc
  prompt="$(build_task_sync_prompt "${change}" "${dir}" "${transcript_file}" "${completed}" "${total}")"
  : > "${output_file}"
  prefix="$(tag "${C_DIM}" "tasks-sync:${change}")"
  rc=0
  run_claude_command_with_retry "${dir}" "${prompt}" "${prefix}" "${output_file}" "Claude tasks sync for ${change}" || rc=$?
  return "${rc}"
}

build_incomplete_assessment_prompt() {
  local change="$1" dir="$2" transcript_file="$3" completed="$4" total="$5"
  cat <<EOF2
You are reviewing an incomplete OpenSpec auto-apply run for change \`${change}\`.

Worktree:
\`${dir}\`

Canonical main repository:
\`${PROJECT_ROOT}\`

OpenSpec repository inside the worktree:
\`${dir}/openspec\`

Previous Claude transcript:
\`${transcript_file}\`

Current recorded task progress: ${completed}/${total}

Please inspect the current worktree state, the remaining checkbox tasks in \`openspec/changes/${change}/tasks.md\`, and the previous transcript. Decide whether a human must intervene before another apply attempt.

Rules:
- Use \`NEEDS_HUMAN=no\` only when the remaining work is still clearly within the current change scope and can be finished autonomously without product clarification, architecture clarification, missing credentials, external service setup, or manual approval.
- Small documentation, README, comment, cleanup, and test tasks are not optional if they remain as unchecked checkbox tasks.
- Ignore the wrapper-managed branch preparation and final merge-back checkbox tasks when deciding whether human intervention is needed.
- If the remaining work is straightforward and should simply be finished by a fresh apply attempt, choose \`NEEDS_HUMAN=no\`.
- Use \`NEEDS_HUMAN=yes\` only when a real human decision or external unblock is required.

Return exactly three lines and nothing else:
NEEDS_HUMAN=yes|no
REASON=<one concise sentence>
NEXT_ACTION=<one concise sentence telling the next concrete step>
EOF2
}

run_incomplete_assessment() {
  local change="$1" dir="$2" transcript_file="$3" completed="$4" total="$5" output_file="$6"
  local prompt prefix rc
  prompt="$(build_incomplete_assessment_prompt "${change}" "${dir}" "${transcript_file}" "${completed}" "${total}")"
  : > "${output_file}"
  prefix="$(tag "${C_DIM}" "assess:${change}")"
  rc=0
  run_claude_command_with_retry "${dir}" "${prompt}" "${prefix}" "${output_file}" "Claude incomplete assessment for ${change}" || rc=$?
  return "${rc}"
}

build_implementation_handoff_prompt() {
  local change="$1" dir="$2" impl="$3" integ="$4" tasks_file="$5" transcript_file="$6"
  local docs_block="" status_block="" path=""
  local -a doc_paths=() status_lines=()

  mapfile -t doc_paths < <(collect_change_artifact_paths "${change}")
  if [[ "${#doc_paths[@]}" -gt 0 ]]; then
    docs_block=$'Read these change artifacts before deciding whether any local files should be committed, kept, or removed:\n'
    for path in "${doc_paths[@]}"; do
      docs_block+="- \`${path}\`"$'\n'
    done
  else
    docs_block=$'No additional change artifact files were found beyond the tasks path listed below.\n'
  fi

  mapfile -t status_lines < <(git -C "${dir}" status --short --untracked-files=normal 2>/dev/null || true)
  if [[ "${#status_lines[@]}" -gt 0 ]]; then
    status_block=$'Current `git status --short` snapshot:\n'
    for path in "${status_lines[@]}"; do
      status_block+="- \`${path}\`"$'\n'
    done
  else
    status_block=$'Current `git status --short` snapshot: clean.\n'
  fi

  cat <<EOF2
You are doing an implementation handoff cleanup pass for OpenSpec change \`${change}\`.

Canonical main repository:
\`${PROJECT_ROOT}\`

Original change worktree:
\`${dir}\`

Implementation branch that must remain ready for parent-managed merge:
\`${impl}\`

Integration branch owned by the wrapper:
\`${integ}\`

OpenSpec tasks truth file:
\`${tasks_file:-unavailable}\`

Previous apply transcript:
\`${transcript_file:-unavailable}\`

${docs_block}
${status_block}

The wrapper script no longer auto-creates checkpoint commits. The implementation side of this change must be handed off cleanly on \`${impl}\`.

Your job is to inspect the current implementation worktree state, preserve or finish any meaningful work for this change, and leave the worktree clean on \`${impl}\`.

Rules:
- Work only inside \`${dir}\`.
- Keep the current branch on \`${impl}\`.
- Treat existing staged, unstaged, and untracked files as inherited state for this change unless you verify they are obsolete residue.
- Do not discard meaningful work just to make the tree clean.
- If the remaining files belong to this change, stage and commit them yourself with one or more clear commit messages.
- If any files are only transient residue or clearly wrong-path leftovers, remove them only after verifying they are safe to drop.
- Do not switch to \`${integ}\` and do not perform the final merge yourself.
- Leave \`git status --short\` clean on \`${impl}\` when you are done so the wrapper can continue.
- If you cannot safely reach a clean implementation handoff without human judgment, stop and explain the blocker clearly.
EOF2
}

run_implementation_handoff_cleanup() {
  local change="$1" dir="$2" impl="$3" integ="$4" tasks_file="$5" transcript_file="$6" output_file="$7"
  local prompt prefix rc
  prompt="$(build_implementation_handoff_prompt "${change}" "${dir}" "${impl}" "${integ}" "${tasks_file}" "${transcript_file}")"
  [[ "${DRY_RUN}" -eq 1 ]] && return 0
  : >> "${output_file}"
  append_log_note "${output_file}" "Launching Claude implementation handoff cleanup in ${dir}"
  prefix="$(tag "${C_DIM}" "handoff:${change}")"
  rc=0
  run_claude_command_with_retry "${dir}" "${prompt}" "${prefix}" "${output_file}" "Claude implementation handoff cleanup for ${change}" || rc=$?
  return "${rc}"
}

implementation_handoff_completed() {
  local dir="$1" impl="$2" current_branch=""
  current_branch="$(worktree_current_branch "${dir}")"
  [[ "${current_branch}" == "${impl}" ]] || return 1
  ! worktree_has_local_changes "${dir}"
}

ensure_clean_implementation_handoff() {
  local change="$1" dir="$2" impl="$3" integ="$4" tasks_file="$5" transcript_file="$6" attempt="$7"
  local handoff_log_file=""

  switch_worktree_branch "${change}" "${dir}" "${impl}" || {
    warn "Failed to return ${change} worktree to ${impl} before implementation handoff cleanup"
    return 1
  }
  if ! worktree_has_local_changes "${dir}"; then
    change_log "${change}" "Implementation branch ${impl} is already clean for parent-managed merge"
    return 0
  fi

  handoff_log_file="$(change_handoff_log_file "${change}" "${attempt}")"
  : > "${handoff_log_file}"
  append_log_note "${handoff_log_file}" "Implementation branch ${impl} still has local changes before parent-managed merge"
  git -C "${dir}" status --short --untracked-files=normal >> "${handoff_log_file}" 2>&1 || true

  change_log "${change}" "Implementation branch ${impl} is still dirty; launching Claude handoff cleanup"
  if run_implementation_handoff_cleanup "${change}" "${dir}" "${impl}" "${integ}" "${tasks_file}" "${transcript_file}" "${handoff_log_file}" \
    && implementation_handoff_completed "${dir}" "${impl}"; then
    change_log "${change}" "Claude handoff cleanup left ${impl} clean for parent-managed merge"
    append_log_note "${handoff_log_file}" "Claude handoff cleanup completed successfully"
    return 0
  fi

  append_log_note "${handoff_log_file}" "Implementation handoff cleanup did not leave ${impl} clean"
  warn "Implementation handoff cleanup did not leave ${change} clean on ${impl}"
  return 1
}

build_cleanup_prompt() {
  local change="$1" dir="$2" tasks_file=""
  tasks_file="$(resolve_change_tasks_file "${change}" 2>/dev/null || true)"
  cat <<EOF2
You are doing a cleanup fallback pass for OpenSpec change \`${change}\`.

Canonical main repository:
\`${PROJECT_ROOT}\`

Target isolated worktree:
\`${dir}\`

OpenSpec tasks truth file:
\`${tasks_file:-unavailable}\`

The wrapper script already attempted a direct \`git worktree remove\` for this worktree and it did not succeed.

Your job is to inspect whether this worktree can now be safely removed, and if so, remove it.

Rules:
- Do not implement new product scope.
- Do not modify unrelated branches or unrelated worktrees.
- Use \`${PROJECT_ROOT}\` as the git control point when running \`git worktree\` commands.
- If the worktree only has harmless transient files or generated residue blocking removal, you may clean those up and then remove the worktree.
- If meaningful uncommitted implementation work remains, do not remove the worktree; explain why it is unsafe.
- Prefer \`git -C ${PROJECT_ROOT} worktree remove ${dir}\`.
- If the worktree is already gone, report that clearly.
EOF2
}

run_cleanup_fallback() {
  local change="$1" dir="$2" output_file="$3"
  local prompt prefix rc
  prompt="$(build_cleanup_prompt "${change}" "${dir}")"
  [[ "${DRY_RUN}" -eq 1 ]] && return 0
  : >> "${output_file}"
  append_log_note "${output_file}" "Launching Claude cleanup fallback for ${dir}"
  prefix="$(tag "${C_DIM}" "cleanup:${change}")"
  rc=0
  run_claude_command_with_retry "${PROJECT_ROOT}" "${prompt}" "${prefix}" "${output_file}" "Claude cleanup fallback for ${change}" || rc=$?
  return "${rc}"
}

build_merge_fallback_prompt() {
  local change="$1" merge_dir="$2" impl="$3" integ="$4" tasks_file="$5" commit_message="$6"
  local docs_block="" conflicts_block="" status_block="" path=""
  local -a doc_paths=() conflict_files=() status_lines=()

  mapfile -t doc_paths < <(collect_change_artifact_paths "${change}")
  if [[ "${#doc_paths[@]}" -gt 0 ]]; then
    docs_block=$'Before resolving conflicts, read these change artifacts as the source of truth for intended behavior and scope:\n'
    for path in "${doc_paths[@]}"; do
      docs_block+="- \`${path}\`"$'\n'
    done
  else
    docs_block=$'No additional change artifact files were found beyond the tasks path listed below.\n'
  fi

  mapfile -t conflict_files < <(git -C "${merge_dir}" diff --name-only --diff-filter=U 2>/dev/null || true)
  if [[ "${#conflict_files[@]}" -gt 0 ]]; then
    conflicts_block=$'Current unmerged files:\n'
    for path in "${conflict_files[@]}"; do
      conflicts_block+="- \`${path}\`"$'\n'
    done
  else
    conflicts_block=$'Current unmerged files: none reported by `git diff --name-only --diff-filter=U`.\n'
  fi

  mapfile -t status_lines < <(git -C "${merge_dir}" status --short 2>/dev/null || true)
  if [[ "${#status_lines[@]}" -gt 0 ]]; then
    status_block=$'Current `git status --short` snapshot:\n'
    for path in "${status_lines[@]}"; do
      status_block+="- \`${path}\`"$'\n'
    done
  else
    status_block=$'Current `git status --short` snapshot: clean.\n'
  fi
  cat <<EOF2
You are doing a merge fallback pass for OpenSpec change \`${change}\`.

Canonical main repository:
\`${PROJECT_ROOT}\`

Original change worktree currently holding the integration branch:
\`${merge_dir}\`

Implementation branch that must be merged:
\`${impl}\`

Integration branch:
\`${integ}\`

OpenSpec tasks truth file:
\`${tasks_file:-unavailable}\`

${docs_block}
${conflicts_block}
${status_block}

The wrapper script is doing the parent-managed \`git merge --no-ff -m "${commit_message}" ${impl}\` directly inside this original change worktree. A direct merge or a follow-up merge commit did not complete cleanly.

Your job is to inspect the current state of this worktree, resolve only the conflicts needed for this change, finish the merge, and create the integration commit if it is safe.

Rules:
- Work only inside \`${merge_dir}\`.
- Do not modify unrelated branches, unrelated worktrees, or the canonical main worktree directly.
- Keep the current branch on \`${integ}\`.
- When deciding between conflict sides, prefer the intended behavior described by the change artifacts above over accidental branch drift.
- Preserve changes that belong to this merge; do not discard conflict context unless you are intentionally resolving it.
- If you can complete the merge safely, resolve conflicts, stage the result, and create the final commit with message \`${commit_message}\`.
- Leave the worktree clean on \`${integ}\` when you are done so the wrapper can switch it back to \`${impl}\`.
- Do not archive the change.
- Do not switch back to \`${impl}\`; the wrapper script will handle that after verification.
- If the conflicts cannot be resolved safely without human product or code decisions, stop and explain the blocker clearly.
EOF2
}

run_merge_fallback() {
  local change="$1" merge_dir="$2" impl="$3" integ="$4" tasks_file="$5" output_file="$6" commit_message="$7"
  local prompt prefix rc
  prompt="$(build_merge_fallback_prompt "${change}" "${merge_dir}" "${impl}" "${integ}" "${tasks_file}" "${commit_message}")"
  [[ "${DRY_RUN}" -eq 1 ]] && return 0
  : >> "${output_file}"
  append_log_note "${output_file}" "Launching Claude merge fallback in ${merge_dir}"
  prefix="$(tag "${C_DIM}" "merge-fallback:${change}")"
  rc=0
  run_claude_command_with_retry "${merge_dir}" "${prompt}" "${prefix}" "${output_file}" "Claude merge fallback for ${change}" || rc=$?
  return "${rc}"
}

write_result_file() {
  local file="$1" status="$2" completed="$3" total="$4" archived="$5" requires_human="${6:-0}" human_reason="${7:-}" human_next_action="${8:-}" transition_at="${9:-}"
  if [[ -z "${transition_at}" ]]; then
    transition_at="$(date +%s%N 2>/dev/null || true)"
    [[ -n "${transition_at}" ]] || transition_at="$(date +%s)000000000"
  fi
  {
    printf 'status=%q\n' "${status}"
    printf 'completed_tasks=%q\n' "${completed}"
    printf 'total_tasks=%q\n' "${total}"
    printf 'archived=%q\n' "${archived}"
    printf 'requires_human=%q\n' "${requires_human}"
    printf 'human_reason=%q\n' "${human_reason}"
    printf 'human_next_action=%q\n' "${human_next_action}"
    printf 'transition_at=%q\n' "${transition_at}"
  } >"${file}"
}

restore_completed_changes_from_session() {
  local change file status completed_tasks total_tasks archived
  RESTORED_CHANGES=()
  for change in "${TARGET_CHANGES[@]}"; do
    file="${SESSION_DIR}/${change}.result"
    CHANGE_RESULT_FILE["${change}"]="${file}"
    [[ -f "${file}" ]] || continue
    status=""; completed_tasks=0; total_tasks=0; archived=0
    source "${file}"
    [[ "${status:-}" == "success" && "${archived:-0}" -eq 1 ]] || continue
    CHANGE_STATE["${change}"]="success"
    append_unique "${change}" COMPLETED_CHANGES
    append_unique "${change}" ARCHIVED_CHANGES
    append_unique "${change}" RESTORED_CHANGES
    change_log "${change}" "Restored completed state from ${SESSION_DIR}"
  done
}

process_change() {
  local change="$1" result_file="$2" dir="$3" archived=0 completed=0 total=0 full_completed=0 full_total=0
  local instructions_json="" validate_json="" validate_ok="" retry_guidance="" tasks_file=""
  local transcript_file="" task_sync_log_file="" assessment_log_file="" human_reason="" human_next_action="" needs_human=""
  local impl="" integ="" managed_git=0 resume_merge_only=0
  local attempt=1 max_attempts=$((INCOMPLETE_RETRY_LIMIT + 1))
  local -a validate_args=() progress_lines=() assessment_lines=()
  change_log "${change}" "Starting"
  impl="${CHANGE_IMPL_BRANCH["${change}"]:-$(implementation_branch_for_change "${change}")}"
  integ="${CHANGE_INTEGRATION_BRANCH["${change}"]:-$(integration_branch_for_change "${change}")}"
  managed_git="${CHANGE_PARENT_MANAGED_GIT["${change}"]:-0}"
  while [[ "${attempt}" -le "${max_attempts}" ]]; do
    change_log "${change}" "Apply attempt ${attempt}/${max_attempts}"
    resume_merge_only=0
    if [[ "${managed_git}" -eq 1 ]] && worktree_has_pending_parent_managed_merge_state "${dir}" "${integ}"; then
      resume_merge_only=1
      change_log "${change}" "Detected unresolved parent-managed merge state in ${dir}; skipping implementation apply and resuming merge handling"
    fi

    if [[ "${resume_merge_only}" -eq 0 ]]; then
      if ! run_openspec status --change "${change}" --json >/dev/null 2>&1; then
        change_log "${change}" "Failed to read change status"
        write_result_file "${result_file}" failed 0 0 0
        return 1
      fi
      if ! instructions_json="$(run_openspec instructions apply --change "${change}" --json 2>/dev/null)"; then
        change_log "${change}" "Failed to generate apply instructions"
        write_result_file "${result_file}" failed 0 0 0
        return 1
      fi
      transcript_file="$(change_attempt_log_file "${change}" "${attempt}")"
      if ! run_claude_for_change "${change}" "${dir}" "${instructions_json}" "${transcript_file}" "${retry_guidance}"; then
        change_log "${change}" "Claude execution failed"
        write_result_file "${result_file}" failed 0 0 0
        return 1
      fi
      if [[ "${DRY_RUN}" -eq 1 ]]; then
        write_result_file "${result_file}" success 1 1 0
        change_log "${change}" "Dry run completed"
        return 0
      fi
      if ! mapfile -t progress_lines < <(read_change_task_progress "${change}" apply); then
        change_log "${change}" "Failed to read tasks.md progress after apply"
        write_result_file "${result_file}" failed 0 0 0
        return 1
      fi
      completed="${progress_lines[0]:-0}"
      total="${progress_lines[1]:-0}"
      change_log "${change}" "Task progress: ${completed}/${total}"
      if [[ "${completed}" -ne "${total}" || "${total}" -le 0 ]]; then
        task_sync_log_file="$(change_task_sync_log_file "${change}" "${attempt}")"
        change_log "${change}" "Tasks remain incomplete; launching tasks sync"
        if run_task_sync "${change}" "${dir}" "${transcript_file}" "${completed}" "${total}" "${task_sync_log_file}"; then
          if ! mapfile -t progress_lines < <(read_change_task_progress "${change}" apply); then
            change_log "${change}" "Failed to read tasks.md progress after tasks sync"
            write_result_file "${result_file}" failed 0 0 0
            return 1
          fi
          completed="${progress_lines[0]:-0}"
          total="${progress_lines[1]:-0}"
          change_log "${change}" "Task progress after tasks sync: ${completed}/${total}"
        else
          change_log "${change}" "Tasks sync failed; continuing with incomplete-task handling"
        fi
      fi
    else
      if ! mapfile -t progress_lines < <(read_change_task_progress "${change}" apply); then
        change_log "${change}" "Failed to read tasks.md progress before resuming merge handling"
        write_result_file "${result_file}" failed 0 0 0
        return 1
      fi
      completed="${progress_lines[0]:-0}"
      total="${progress_lines[1]:-0}"
      change_log "${change}" "Task progress before resumed merge handling: ${completed}/${total}"
    fi
    if [[ "${completed}" -eq "${total}" && "${total}" -gt 0 ]]; then
      tasks_file="$(resolve_change_tasks_file "${change}" 2>/dev/null || true)"
      if change_is_archived "${change}"; then
        archived=1
        change_log "${change}" "Change is already archived; using ${tasks_file:-archive tasks.md} as the source of truth"
      fi
      if [[ "${SKIP_VALIDATE}" -eq 0 && "${archived}" -eq 0 ]]; then
        validate_args=(validate "${change}" --type change --json)
        [[ "${STRICT_VALIDATE}" -eq 1 ]] && validate_args+=(--strict)
        if ! validate_json="$(run_openspec "${validate_args[@]}" 2>/dev/null)"; then
          change_log "${change}" "Validation command failed"
          write_result_file "${result_file}" failed "${completed}" "${total}" 0
          return 1
        fi
        validate_ok="$(json_validate_result "${validate_json}")"
        if [[ "${validate_ok}" != "true" ]]; then
          change_log "${change}" "Validation failed"
          write_result_file "${result_file}" failed "${completed}" "${total}" 0
          return 1
        fi
      fi
      if [[ "${managed_git}" -eq 1 && "${archived}" -eq 0 ]]; then
        if [[ "${resume_merge_only}" -eq 1 ]]; then
          change_log "${change}" "Queued for parent-managed merge resume on ${integ}"
        else
          change_log "${change}" "Ready for parent-managed merge queue finalization"
        fi
        write_result_file "${result_file}" ready_for_merge "${completed}" "${total}" 0
        return 0
      fi
      if ! mapfile -t progress_lines < <(read_change_task_progress "${change}" full); then
        change_log "${change}" "Failed to read final tasks.md progress after wrapper-managed git steps"
        write_result_file "${result_file}" failed "${completed}" "${total}" 0
        return 1
      fi
      full_completed="${progress_lines[0]:-0}"
      full_total="${progress_lines[1]:-0}"
      if [[ "${full_completed}" -ne "${full_total}" || "${full_total}" -le 0 ]]; then
        human_reason="The non-git tasks completed, but tasks.md still has unchecked items after wrapper-managed branch synchronization."
        human_next_action="Inspect ${tasks_file:-openspec/changes/${change}/tasks.md} and reconcile the remaining checkbox items before rerunning auto_apply."
        write_result_file "${result_file}" needs_human "${full_completed}" "${full_total}" 0 1 "${human_reason}" "${human_next_action}"
        return 0
      fi
      if [[ "${AUTO_ARCHIVE}" -eq 1 && "${archived}" -eq 0 ]]; then
        if run_openspec archive "${change}" -y >/dev/null 2>&1; then
          archived=1
          change_log "${change}" "Archived"
        elif change_is_archived "${change}"; then
          archived=1
          change_log "${change}" "Change was already archived during apply"
        else
          change_log "${change}" "Archive failed"
          write_result_file "${result_file}" failed "${completed}" "${total}" 0
          return 1
        fi
      fi
      write_result_file "${result_file}" success "${full_completed}" "${full_total}" "${archived}"
      change_log "${change}" "Completed"
      return 0
    fi

    if [[ "${attempt}" -lt "${max_attempts}" ]]; then
      assessment_log_file="$(change_assessment_log_file "${change}")"
      change_log "${change}" "Tasks remain incomplete after tasks sync; launching assessment before retry"
      if ! run_incomplete_assessment "${change}" "${dir}" "${transcript_file}" "${completed}" "${total}" "${assessment_log_file}"; then
        human_reason="The follow-up assessment process failed after the first incomplete apply/tasks-sync cycle."
        human_next_action="Inspect ${assessment_log_file} and the remaining checkbox tasks manually before rerunning this change."
        write_result_file "${result_file}" needs_human "${completed}" "${total}" 0 1 "${human_reason}" "${human_next_action}"
        return 0
      fi
      if ! mapfile -t assessment_lines < <(parse_incomplete_assessment_output "${assessment_log_file}"); then
        human_reason="The follow-up assessment returned an invalid format after the first incomplete apply/tasks-sync cycle."
        human_next_action="Inspect ${assessment_log_file} and the remaining checkbox tasks manually before rerunning this change."
        write_result_file "${result_file}" needs_human "${completed}" "${total}" 0 1 "${human_reason}" "${human_next_action}"
        return 0
      fi
      needs_human="${assessment_lines[0]:-yes}"
      human_reason="${assessment_lines[1]:-The assessment did not provide a reason.}"
      human_next_action="${assessment_lines[2]:-Review the remaining checkbox tasks manually.}"
      if [[ "${needs_human}" == "no" ]]; then
        retry_guidance="$(cat <<EOF2
- A follow-up review decided this change should still be finishable without human intervention.
- Focus specifically on this next action: ${human_next_action}
- Before stopping, make sure \`tasks.md\` matches the real completion state of the change.
EOF2
)"
        change_log "${change}" "Assessment says no human intervention is needed; retrying apply once"
        attempt=$((attempt + 1))
        continue
      fi
      change_log "${change}" "Assessment requires human intervention: ${human_reason}"
      write_result_file "${result_file}" needs_human "${completed}" "${total}" 0 1 "${human_reason}" "${human_next_action}"
      return 0
    fi

    human_reason="The change remained incomplete after the retry attempt and the final tasks sync pass."
    human_next_action="Review the remaining checkbox tasks in openspec/changes/${change}/tasks.md and continue this change manually or rerun auto_apply for this single change."
    change_log "${change}" "Tasks are still incomplete after the automatic retry and final tasks sync"
    write_result_file "${result_file}" needs_human "${completed}" "${total}" 0 1 "${human_reason}" "${human_next_action}"
    return 0
  done
}
initialize_dependency_map() {
  local normalized="" line change deps
  local -a lines=()
  CHANGE_DEPS=()
  if [[ "${#DEPENDENCY_FILES[@]}" -gt 0 ]]; then
    normalized="$(normalize_dependency_graphs "${DEPENDENCY_FILES[@]}" -- "${TARGET_CHANGES[@]}")" || fail "Failed to parse dependency graph from: ${DEPENDENCY_FILES[*]}"
    mapfile -t lines <<< "${normalized}"
    TARGET_CHANGES=()
    for line in "${lines[@]}"; do
      change="${line%%$'\t'*}"
      deps="${line#*$'\t'}"
      [[ "${line}" == *$'\t'* ]] || deps=""
      TARGET_CHANGES+=("${change}")
      CHANGE_DEPS["${change}"]="${deps}"
    done
  else
    for change in "${TARGET_CHANGES[@]}"; do
      CHANGE_DEPS["${change}"]=""
    done
  fi
}

assert_no_cross_series_dependencies() {
  local change dep change_scope dep_scope
  for change in "${TARGET_CHANGES[@]}"; do
    change_scope="$(series_prefix_for_change "${change}")"
    [[ -n "${change_scope}" ]] || change_scope="dev"
    for dep in ${CHANGE_DEPS["${change}"]}; do
      dep_scope="$(series_prefix_for_change "${dep}")"
      [[ -n "${dep_scope}" ]] || dep_scope="dev"
      if [[ "${change_scope}" != "${dep_scope}" ]]; then
        fail "Cross-series dependency detected: ${change} (${change_scope}) depends on ${dep} (${dep_scope}). Multiple prefixes only support independent series. If these changes depend on each other, merge them under a single target-named series prefix."
      fi
    done
  done
}

assert_target_changes_exist() {
  local payload="" change
  local -a missing=() unresolved=()
  payload="$(run_openspec list --changes --json)" || fail "Failed to list changes for preflight validation"
  mapfile -t missing < <(json_missing_changes "${payload}" "${TARGET_CHANGES[@]}")
  for change in "${missing[@]}"; do
    if [[ "${CHANGE_STATE["${change}"]:-pending}" == "success" ]]; then
      continue
    fi
    if restore_change_state_from_tasks_truth "${change}" "${CHANGE_RESULT_FILE["${change}"]}"; then
      continue
    fi
    unresolved+=("${change}")
  done
  [[ "${#unresolved[@]}" -eq 0 ]] || fail "Missing change directories for: ${unresolved[*]}. Check openspec/changes/, dependency JSON, or session archive ${SESSION_DIR}."
}

preflight_validate_target_changes() {
  local change validate_json="" validate_ok="" issue
  local -a invalid_changes=() validation_lines=()

  for change in "${TARGET_CHANGES[@]}"; do
    [[ "${CHANGE_STATE["${change}"]:-pending}" == "success" ]] && continue
    [[ -n "$(resolve_active_change_dir "${change}" 2>/dev/null || true)" ]] || continue

    validate_json="$(run_openspec validate "${change}" --type change --json 2>/dev/null || true)"
    if [[ -z "${validate_json}" ]]; then
      validation_lines+=("${change}: preflight validation produced no JSON output")
      invalid_changes+=("${change}")
      continue
    fi

    if ! validate_ok="$(json_validate_result "${validate_json}" 2>/dev/null)"; then
      validation_lines+=("${change}: preflight validation returned unreadable JSON")
      invalid_changes+=("${change}")
      continue
    fi

    [[ "${validate_ok}" == "true" ]] && continue

    invalid_changes+=("${change}")
    mapfile -t validation_lines < <(
      {
        printf '%s\n' "${validation_lines[@]}"
        json_validate_issue_lines "${validate_json}"
      } | sed '/^$/d'
    )
  done

  if [[ "${#invalid_changes[@]}" -gt 0 ]]; then
    attention "Preflight change validation failed before execution. Fix the OpenSpec change artifacts first."
    for issue in "${validation_lines[@]}"; do
      warn "${issue}"
    done
    fail "Invalid change artifacts detected for: ${invalid_changes[*]}"
  fi
}

active_job_count() { echo "${#PID_TO_CHANGE[@]}"; }
is_capacity_available() { [[ "${MAX_PARALLEL}" -eq 0 || "$(active_job_count)" -lt "${MAX_PARALLEL}" ]]; }

dependency_state_for_change() {
  local change="$1" dep state
  for dep in ${CHANGE_DEPS["${change}"]}; do
    state="${CHANGE_STATE["${dep}"]:-pending}"
    case "${state}" in
      success) ;;
      failed|blocked) return 2 ;;
      *) return 1 ;;
    esac
  done
  return 0
}

mark_blocked_changes() {
  local change dep state
  for change in "${TARGET_CHANGES[@]}"; do
    [[ "${CHANGE_STATE["${change}"]:-pending}" == "pending" ]] || continue
    for dep in ${CHANGE_DEPS["${change}"]}; do
      state="${CHANGE_STATE["${dep}"]:-pending}"
      if [[ "${state}" == "failed" || "${state}" == "blocked" ]]; then
        CHANGE_STATE["${change}"]="blocked"
        append_unique "${change}" BLOCKED_CHANGES
        warn "Blocking ${change}; dependency ${dep} ended as ${state}"
        break
      fi
    done
  done
}

start_change_job() {
  local change="$1" file="${SESSION_DIR}/${change}.result" dir=""
  CHANGE_STATE["${change}"]="running"
  CHANGE_RESULT_FILE["${change}"]="${file}"
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    dir="${WORKTREE_ROOT}/${change}"
  else
    dir="$(prepare_worktree_for_change "${change}")" || {
      CHANGE_STATE["${change}"]="failed"
      append_unique "${change}" FAILED_CHANGES
      [[ "${STOP_ON_ERROR}" -eq 1 ]] && STOP_REQUESTED=1
      return 1
    }
    prepare_parent_managed_series_branching "${change}" "${dir}" || {
      CHANGE_STATE["${change}"]="failed"
      append_unique "${change}" FAILED_CHANGES
      [[ "${STOP_ON_ERROR}" -eq 1 ]] && STOP_REQUESTED=1
      return 1
    }
  fi
  CHANGE_WORKTREE["${change}"]="${dir}"
  (process_change "${change}" "${file}" "${dir}") &
  PID_TO_CHANGE["$!"]="${change}"
  log "Started ${change} (pid=$!, worktree=${dir})"
}

enqueue_merge_ready_change() {
  local change="$1" ready_at="$2" other other_time inserted=0
  local -a next_queue=()

  [[ -n "${ready_at}" ]] || ready_at="$(date +%s%N 2>/dev/null || date +%s)000000000"
  CHANGE_RESULT_TRANSITION_AT["${change}"]="${ready_at}"

  for other in "${MERGE_READY_QUEUE[@]}"; do
    [[ "${other}" == "${change}" ]] && return 0
  done

  for other in "${MERGE_READY_QUEUE[@]}"; do
    other_time="${CHANGE_RESULT_TRANSITION_AT["${other}"]:-9999999999999999999}"
    if [[ "${inserted}" -eq 0 && "${ready_at}" < "${other_time}" ]]; then
      next_queue+=("${change}")
      inserted=1
    fi
    next_queue+=("${other}")
  done

  if [[ "${inserted}" -eq 0 ]]; then
    next_queue+=("${change}")
  fi

  MERGE_READY_QUEUE=("${next_queue[@]}")
}

has_merge_ready_changes() {
  [[ "${#MERGE_READY_QUEUE[@]}" -gt 0 ]]
}

cancel_running_jobs() {
  local pid
  for pid in "${!PID_TO_CHANGE[@]}"; do
    kill_process_tree "${pid}" TERM
  done
  sleep 1
  for pid in "${!PID_TO_CHANGE[@]}"; do
    kill -0 "${pid}" >/dev/null 2>&1 || continue
    kill_process_tree "${pid}" KILL
  done
}

apply_result_state_from_file() {
  local change="$1" wait_rc="${2:-0}" file="${CHANGE_RESULT_FILE["${change}"]}"
  local status="" completed_tasks=0 total_tasks=0 archived=0 requires_human=0 human_reason="" human_next_action="" transition_at=""
  if [[ ! -f "${file}" ]]; then
    CHANGE_STATE["${change}"]="failed"
    append_unique "${change}" FAILED_CHANGES
    warn "Change ${change} exited without a result file"
    [[ "${STOP_ON_ERROR}" -eq 1 ]] && STOP_REQUESTED=1
    return 1
  fi
  source "${file}"
  CHANGE_RESULT_TRANSITION_AT["${change}"]="${transition_at:-}"
  if [[ "${wait_rc}" -ne 0 && ( "${status}" == "success" || "${status}" == "ready_for_merge" ) ]]; then
    CHANGE_STATE["${change}"]="failed"
    append_unique "${change}" FAILED_CHANGES
    warn "Change ${change} returned a non-zero exit code despite a ${status} result"
    [[ "${STOP_ON_ERROR}" -eq 1 ]] && STOP_REQUESTED=1
    return 1
  fi
  case "${status}" in
    success)
      CHANGE_STATE["${change}"]="success"
      append_unique "${change}" COMPLETED_CHANGES
      if [[ "${archived:-0}" -eq 1 ]]; then
        append_unique "${change}" ARCHIVED_CHANGES
        cleanup_change_branch "${change}" || true
        [[ "${CLEANUP_WORKTREES}" -eq 1 ]] && cleanup_change_worktree "${change}" || true
      fi
      ok "Finished ${change}"
      ;;
    ready_for_merge)
      CHANGE_STATE["${change}"]="merge_pending"
      enqueue_merge_ready_change "${change}" "${transition_at:-}"
      ok "Queued ${change} for parent-managed merge finalization"
      ;;
    incomplete)
      CHANGE_STATE["${change}"]="failed"
      append_unique "${change}" INCOMPLETE_CHANGES
      warn "Change ${change} is incomplete (${completed_tasks}/${total_tasks})"
      [[ "${STOP_ON_ERROR}" -eq 1 ]] && STOP_REQUESTED=1
      ;;
    needs_human)
      CHANGE_STATE["${change}"]="failed"
      append_unique "${change}" FAILED_CHANGES
      append_unique "${change}" HUMAN_REVIEW_CHANGES
      CHANGE_HUMAN_REASON["${change}"]="${human_reason}"
      CHANGE_HUMAN_ACTION["${change}"]="${human_next_action}"
      warn "Change ${change} requires human intervention: ${human_reason}"
      [[ -n "${human_next_action}" ]] && warn "Suggested next action for ${change}: ${human_next_action}"
      STOP_REQUESTED=1
      ;;
    *)
      CHANGE_STATE["${change}"]="failed"
      append_unique "${change}" FAILED_CHANGES
      warn "Change ${change} failed"
      [[ "${STOP_ON_ERROR}" -eq 1 ]] && STOP_REQUESTED=1
      ;;
  esac
  return 0
}

handle_finished_job() {
  local pid="$1" wait_rc="$2" change="${PID_TO_CHANGE["${pid}"]}"
  unset 'PID_TO_CHANGE['"${pid}"']'
  apply_result_state_from_file "${change}" "${wait_rc}"
}

wait_for_any_job() {
  local pid change rc
  while true; do
    for pid in "${!PID_TO_CHANGE[@]}"; do
      if ! kill -0 "${pid}" 2>/dev/null; then
        wait "${pid}"; rc=$?
        change="${PID_TO_CHANGE["${pid}"]}"
        log "Collected ${change} (exit=${rc})"
        handle_finished_job "${pid}" "${rc}"
        return 0
      fi
    done
    sleep 1
  done
}

collect_finished_jobs_nonblocking() {
  local pid change rc collected=0
  for pid in "${!PID_TO_CHANGE[@]}"; do
    if ! kill -0 "${pid}" 2>/dev/null; then
      wait "${pid}"; rc=$?
      change="${PID_TO_CHANGE["${pid}"]}"
      log "Collected ${change} (exit=${rc})"
      handle_finished_job "${pid}" "${rc}"
      collected=1
    fi
  done
  return "${collected}"
}

has_pending_changes() {
  local change
  for change in "${TARGET_CHANGES[@]}"; do
    [[ "${CHANGE_STATE["${change}"]:-pending}" == "pending" ]] && return 0
  done
  return 1
}

start_ready_jobs() {
  local change dep_status started=0
  for change in "${TARGET_CHANGES[@]}"; do
    [[ "${CHANGE_STATE["${change}"]:-pending}" == "pending" ]] || continue
    is_capacity_available || break
    dependency_state_for_change "${change}"; dep_status=$?
    if [[ "${dep_status}" -eq 0 ]]; then
      start_change_job "${change}" && started=1
    fi
  done
  return "${started}"
}

finalize_merge_ready_change() {
  local change="$1" result_file="${CHANGE_RESULT_FILE["${change}"]}" dir="${CHANGE_WORKTREE["${change}"]:-}"
  local tasks_file="" impl="" integ="" archived=0 full_completed=0 full_total=0 managed_git=0
  local human_reason="" human_next_action=""
  local -a progress_lines=()

  change_log "${change}" "Starting parent-managed merge queue finalization"
  CHANGE_STATE["${change}"]="merging"

  [[ -n "${dir}" && -d "${dir}" ]] || {
    write_result_file "${result_file}" failed 0 0 0
    apply_result_state_from_file "${change}" 0
    return 1
  }

  tasks_file="$(resolve_change_tasks_file "${change}" 2>/dev/null || true)"
  impl="${CHANGE_IMPL_BRANCH["${change}"]:-$(implementation_branch_for_change "${change}")}"
  integ="${CHANGE_INTEGRATION_BRANCH["${change}"]:-$(integration_branch_for_change "${change}")}"
  managed_git="${CHANGE_PARENT_MANAGED_GIT["${change}"]:-0}"

  if change_is_archived "${change}"; then
    archived=1
    change_log "${change}" "Change is already archived before queued finalization; using archived tasks truth"
  fi

  if [[ "${managed_git}" -eq 1 && "${archived}" -eq 0 ]]; then
    if ! worktree_has_pending_parent_managed_merge_state "${dir}" "${integ}"; then
      if ! ensure_clean_implementation_handoff "${change}" "${dir}" "${impl}" "${integ}" "${tasks_file}" "" "queue"; then
        human_reason="The implementation branch ${impl} was not handed off cleanly before the parent-managed merge."
        human_next_action="Inspect ${dir} and ${SESSION_DIR}/${change}.attempt-queue.handoff.claude.log, clean up or commit the remaining implementation work on ${impl}, and rerun auto_apply for ${change}."
        write_result_file "${result_file}" needs_human 0 0 0 1 "${human_reason}" "${human_next_action}"
        apply_result_state_from_file "${change}" 0
        return 0
      fi
    else
      change_log "${change}" "Queued finalization detected existing unresolved merge state in ${dir}; resuming merge handling"
    fi

    if ! parent_managed_series_merge "${change}" "${dir}" "${impl}" "${integ}" "${tasks_file}"; then
      human_reason="The parent-managed merge from ${impl} back to ${integ} did not complete cleanly."
      human_next_action="Inspect the original worktree ${dir} and the merge fallback log ${SESSION_DIR}/${change}.merge-fallback.claude.log, or release ${integ} if it is occupied elsewhere, then rerun auto_apply for ${change}."
      write_result_file "${result_file}" needs_human 0 0 0 1 "${human_reason}" "${human_next_action}"
      apply_result_state_from_file "${change}" 0
      return 0
    fi
  fi

  if ! mapfile -t progress_lines < <(read_change_task_progress "${change}" full); then
    change_log "${change}" "Failed to read final tasks.md progress after parent-managed merge queue finalization"
    write_result_file "${result_file}" failed 0 0 "${archived}"
    apply_result_state_from_file "${change}" 0
    return 1
  fi
  full_completed="${progress_lines[0]:-0}"
  full_total="${progress_lines[1]:-0}"
  if [[ "${full_completed}" -ne "${full_total}" || "${full_total}" -le 0 ]]; then
    human_reason="The non-git tasks completed, but tasks.md still has unchecked items after wrapper-managed branch synchronization."
    human_next_action="Inspect ${tasks_file:-openspec/changes/${change}/tasks.md} and reconcile the remaining checkbox items before rerunning auto_apply."
    write_result_file "${result_file}" needs_human "${full_completed}" "${full_total}" "${archived}" 1 "${human_reason}" "${human_next_action}"
    apply_result_state_from_file "${change}" 0
    return 0
  fi

  if [[ "${AUTO_ARCHIVE}" -eq 1 && "${archived}" -eq 0 ]]; then
    if run_openspec archive "${change}" -y >/dev/null 2>&1; then
      archived=1
      change_log "${change}" "Archived"
    elif change_is_archived "${change}"; then
      archived=1
      change_log "${change}" "Change was already archived during queued finalization"
    else
      change_log "${change}" "Archive failed during queued finalization"
      write_result_file "${result_file}" failed "${full_completed}" "${full_total}" 0
      apply_result_state_from_file "${change}" 0
      return 1
    fi
  fi

  write_result_file "${result_file}" success "${full_completed}" "${full_total}" "${archived}"
  apply_result_state_from_file "${change}" 0
  return 0
}

process_next_merge_ready_change() {
  local change=""
  [[ "${#MERGE_READY_QUEUE[@]}" -gt 0 ]] || return 1
  change="${MERGE_READY_QUEUE[0]}"
  if [[ "${#MERGE_READY_QUEUE[@]}" -gt 1 ]]; then
    MERGE_READY_QUEUE=("${MERGE_READY_QUEUE[@]:1}")
  else
    MERGE_READY_QUEUE=()
  fi
  finalize_merge_ready_change "${change}"
}

summarize_and_exit() {
  local code="$1" change
  echo
  printf '%s %sSummary%s\n' "$(tag "${C_BOLD}${C_INFO}" "auto-apply")" "${C_BOLD}" "${C_RESET}"
  printf '%s  session:%s %s\n' "${C_DIM}" "${C_RESET}" "${SESSION_DIR:-none}"
  [[ "${#RESTORED_CHANGES[@]}" -gt 0 ]] && printf '%s  restored:%s %s\n' "${C_DIM}" "${C_RESET}" "${RESTORED_CHANGES[*]}" || printf '%s  restored:%s none\n' "${C_DIM}" "${C_RESET}"
  [[ "${#COMPLETED_CHANGES[@]}" -gt 0 ]] && printf '%s  completed:%s %s\n' "${C_OK}" "${C_RESET}" "${COMPLETED_CHANGES[*]}" || printf '%s  completed:%s none\n' "${C_OK}" "${C_RESET}"
  [[ "${#ARCHIVED_CHANGES[@]}" -gt 0 ]] && printf '%s  archived:%s %s\n' "${C_OK}" "${C_RESET}" "${ARCHIVED_CHANGES[*]}" || printf '%s  archived:%s none\n' "${C_OK}" "${C_RESET}"
  [[ "${#MERGE_READY_QUEUE[@]}" -gt 0 ]] && printf '%s  merge-pending:%s %s\n' "${C_WARN}" "${C_RESET}" "${MERGE_READY_QUEUE[*]}" >&2 || printf '%s  merge-pending:%s none\n' "${C_WARN}" "${C_RESET}"
  [[ "${#INCOMPLETE_CHANGES[@]}" -gt 0 ]] && printf '%s  incomplete:%s %s\n' "${C_WARN}" "${C_RESET}" "${INCOMPLETE_CHANGES[*]}" >&2 || printf '%s  incomplete:%s none\n' "${C_WARN}" "${C_RESET}"
  [[ "${#BLOCKED_CHANGES[@]}" -gt 0 ]] && printf '%s  blocked:%s %s\n' "${C_WARN}" "${C_RESET}" "${BLOCKED_CHANGES[*]}" >&2 || printf '%s  blocked:%s none\n' "${C_WARN}" "${C_RESET}"
  [[ "${#FAILED_CHANGES[@]}" -gt 0 ]] && printf '%s  failed:%s %s\n' "${C_ERR}" "${C_RESET}" "${FAILED_CHANGES[*]}" >&2 || printf '%s  failed:%s none\n' "${C_ERR}" "${C_RESET}"
  [[ "${#BRANCH_CLEANED_CHANGES[@]}" -gt 0 ]] && printf '%s  branch-cleaned:%s %s\n' "${C_OK}" "${C_RESET}" "${BRANCH_CLEANED_CHANGES[*]}" || printf '%s  branch-cleaned:%s none\n' "${C_OK}" "${C_RESET}"
  if [[ "${#HUMAN_REVIEW_CHANGES[@]}" -gt 0 ]]; then
    printf '%s  human-review:%s\n' "${C_WARN}" "${C_RESET}" >&2
    for change in "${HUMAN_REVIEW_CHANGES[@]}"; do
      printf '%s    %s%s%s: %s\n' "${C_WARN}" "${C_CHANGE}" "${change}" "${C_RESET}" "${CHANGE_HUMAN_REASON["${change}"]:-needs manual review}" >&2
      [[ -n "${CHANGE_HUMAN_ACTION["${change}"]:-}" ]] && printf '%s      next: %s\n' "${C_DIM}" "${CHANGE_HUMAN_ACTION["${change}"]}" >&2
    done
  else
    printf '%s  human-review:%s none\n' "${C_WARN}" "${C_RESET}"
  fi
  [[ "${#BRANCH_CLEANUP_FAILED_CHANGES[@]}" -gt 0 ]] && printf '%s  branch-cleanup-failed:%s %s\n' "${C_ERR}" "${C_RESET}" "${BRANCH_CLEANUP_FAILED_CHANGES[*]}" >&2 || printf '%s  branch-cleanup-failed:%s none\n' "${C_ERR}" "${C_RESET}"
  [[ "${#CLEANUP_FAILED_CHANGES[@]}" -gt 0 ]] && printf '%s  cleanup-failed:%s %s\n' "${C_ERR}" "${C_RESET}" "${CLEANUP_FAILED_CHANGES[*]}" >&2 || printf '%s  cleanup-failed:%s none\n' "${C_ERR}" "${C_RESET}"
  if [[ "${#CHANGE_WORKTREE[@]}" -gt 0 ]]; then
    printf '%s  worktrees:%s\n' "${C_DIM}" "${C_RESET}"
    for change in "${TARGET_CHANGES[@]}"; do
      [[ -n "${CHANGE_WORKTREE["${change}"]:-}" ]] || continue
      printf '%s    %s%s%s -> %s\n' "${C_DIM}" "${C_CHANGE}" "${change}" "${C_RESET}" "${CHANGE_WORKTREE["${change}"]}"
    done
  fi
  exit "${code}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) RUN_ALL=1; shift ;;
    --prefix) [[ $# -ge 2 ]] || fail "--prefix requires a value"; add_prefix_filter "$2"; shift 2 ;;
    --deps) [[ $# -ge 2 ]] || fail "--deps requires a file path"; add_dependency_file "$2"; shift 2 ;;
    --max-parallel) [[ $# -ge 2 ]] || fail "--max-parallel requires a value"; MAX_PARALLEL="$2"; MAX_PARALLEL_SET=1; shift 2 ;;
    --no-archive) AUTO_ARCHIVE=0; shift ;;
    --cleanup-worktrees) CLEANUP_WORKTREES=1; shift ;;
    --allow-local-db-reset) ALLOW_LOCAL_DB_RESET=1; shift ;;
    --skip-validate) SKIP_VALIDATE=1; shift ;;
    --strict) STRICT_VALIDATE=1; shift ;;
    --stop-on-error) STOP_ON_ERROR=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; while [[ $# -gt 0 ]]; do TARGET_CHANGES+=("$1"); shift; done ;;
    -*) fail "Unknown option: $1" ;;
    *) TARGET_CHANGES+=("$1"); shift ;;
  esac
done

require_command "${CLAUDE_CMD[0]}"
require_command "${OPENSPEC_CMD[0]}"
require_command git
require_command python3
[[ -f "${TASKS_GIT_HELPER}" ]] || fail "Missing managed git task helper: ${TASKS_GIT_HELPER}"

trap 'handle_interrupt INT' INT
trap 'handle_interrupt TERM' TERM

git -C "${PROJECT_ROOT}" worktree prune >/dev/null 2>&1 || true
resolve_dependency_files
[[ "${MAX_PARALLEL}" =~ ^[0-9]+$ ]] || fail "--max-parallel must be a non-negative integer"
[[ "${PORT_BLOCK_BASE}" =~ ^[0-9]+$ ]] || fail "OPENSPEC_AUTO_PORT_BASE must be a non-negative integer"
[[ "${PORT_BLOCK_SIZE}" =~ ^[0-9]+$ && "${PORT_BLOCK_SIZE}" -ge 4 ]] || fail "OPENSPEC_AUTO_PORT_BLOCK_SIZE must be an integer >= 4"
[[ "${ALLOW_LOCAL_DB_RESET}" =~ ^[01]$ ]] || fail "OPENSPEC_AUTO_ALLOW_LOCAL_DB_RESET must be 0 or 1"

if [[ "${MAX_PARALLEL_SET}" -eq 0 ]]; then
  [[ "${#DEPENDENCY_FILES[@]}" -gt 0 ]] && MAX_PARALLEL=0 || MAX_PARALLEL=1
fi

[[ "${RUN_ALL}" -eq 0 || "${#TARGET_CHANGES[@]}" -eq 0 ]] || fail "Use either explicit change ids or --all, not both"
[[ "${CLEANUP_WORKTREES}" -eq 0 || "${AUTO_ARCHIVE}" -eq 1 ]] || warn "Cleanup only runs after successful archive; worktrees will be kept because --no-archive is set"

if [[ "${RUN_ALL}" -eq 0 && "${#TARGET_CHANGES[@]}" -eq 0 && "${#DEPENDENCY_FILES[@]}" -eq 0 ]]; then
  usage
  exit 1
fi

if [[ "${RUN_ALL}" -eq 1 ]]; then
  log "Resolving active changes from OpenSpec"
  LIST_JSON="$(run_openspec list --changes --json)" || fail "Failed to list changes"
  mapfile -t TARGET_CHANGES < <(json_get_change_names "${LIST_JSON}" "${PREFIX_FILTERS[@]}")
  [[ "${#TARGET_CHANGES[@]}" -gt 0 ]] || fail "No matching active changes found"
fi

initialize_dependency_map
[[ "${#TARGET_CHANGES[@]}" -gt 0 ]] || fail "No changes resolved for execution"
assert_no_cross_series_dependencies

ensure_session_dir
for change in "${TARGET_CHANGES[@]}"; do CHANGE_STATE["${change}"]="pending"; done
restore_completed_changes_from_session
assert_target_changes_exist
preflight_validate_target_changes
warn_if_main_worktree_holds_series_branch

log "Project root: ${PROJECT_ROOT}"
log "Nested OpenSpec repo: ${OPENSPEC_ROOT}"
log "Auto deps dir: ${AUTO_DEPS_DIR}"
log "Auto logs dir: ${AUTO_LOGS_DIR}"
log "Worktree root: ${WORKTREE_ROOT}"
log "Port block: base=${PORT_BLOCK_BASE}, size=${PORT_BLOCK_SIZE}"
log "Session key: ${SESSION_KEY}"
log "Session dir: ${SESSION_DIR}"
log "OpenSpec command: ${OPENSPEC_CMD_STRING}"
log "Claude command: ${CLAUDE_CMD_STRING}"
log "Auto archive: ${AUTO_ARCHIVE}"
log "Cleanup worktrees: ${CLEANUP_WORKTREES}"
log "Allow local DB reset: ${ALLOW_LOCAL_DB_RESET}"
log "Incomplete retry limit: ${INCOMPLETE_RETRY_LIMIT}"
[[ "${#DEPENDENCY_FILES[@]}" -gt 0 ]] && log "Dependency files: ${DEPENDENCY_FILES[*]}"
[[ "${#AUTO_DEPENDENCY_FILES[@]}" -gt 0 ]] && log "Auto-discovered dependency files: ${AUTO_DEPENDENCY_FILES[*]}"
[[ "${#PREFIX_FILTERS[@]}" -gt 0 ]] && log "Prefix filters: ${PREFIX_FILTERS[*]}"
log "Max parallel: ${MAX_PARALLEL}"
log "Target changes: ${TARGET_CHANGES[*]}"

overall_failed=0
while true; do
  collect_finished_jobs_nonblocking || true
  if [[ "${STOP_REQUESTED}" -eq 0 ]] && has_merge_ready_changes; then
    process_next_merge_ready_change || overall_failed=1
    continue
  fi
  mark_blocked_changes
  [[ "${STOP_REQUESTED}" -eq 0 ]] && start_ready_jobs || true
  [[ "${STOP_REQUESTED}" -eq 1 ]] && cancel_running_jobs
  collect_finished_jobs_nonblocking || true
  if [[ "${STOP_REQUESTED}" -eq 0 ]] && has_merge_ready_changes; then
    process_next_merge_ready_change || overall_failed=1
    continue
  fi
  if [[ "$(active_job_count)" -gt 0 ]]; then
    wait_for_any_job
    continue
  fi
  if [[ "${STOP_REQUESTED}" -eq 0 ]] && has_merge_ready_changes; then
    process_next_merge_ready_change || overall_failed=1
    continue
  fi
  if has_pending_changes; then
    mark_blocked_changes
    if has_pending_changes; then
      warn "No runnable changes remain; unresolved pending changes detected"
      overall_failed=1
      break
    fi
  fi
  break
done

if [[ "${#FAILED_CHANGES[@]}" -gt 0 || "${#INCOMPLETE_CHANGES[@]}" -gt 0 || "${#BLOCKED_CHANGES[@]}" -gt 0 || "${#CLEANUP_FAILED_CHANGES[@]}" -gt 0 || "${#BRANCH_CLEANUP_FAILED_CHANGES[@]}" -gt 0 ]]; then
  overall_failed=1
fi

[[ "${overall_failed}" -eq 0 ]] && summarize_and_exit 0 || summarize_and_exit 1
