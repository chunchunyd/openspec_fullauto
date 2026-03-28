#!/usr/bin/env bash

set -u
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENSPEC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AUTO_LOGS_DIR="${OPENSPEC_AUTO_LOGS_DIR:-${SCRIPT_DIR}/logs}"
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
AUTO_MERGE_BRANCHES=0
STRICT_VALIDATE=0
SKIP_VALIDATE=0
STOP_ON_ERROR=0
PREFIX=""
DEPENDENCY_FILE=""
MAX_PARALLEL=0
MAX_PARALLEL_SET=0

declare -a TARGET_CHANGES=()
declare -a FAILED_CHANGES=()
declare -a ARCHIVED_CHANGES=()
declare -a COMPLETED_CHANGES=()
declare -a INCOMPLETE_CHANGES=()
declare -a BLOCKED_CHANGES=()
declare -a CLEANUP_FAILED_CHANGES=()
declare -a RESTORED_CHANGES=()
declare -A CHANGE_DEPS=()
declare -A CHANGE_STATE=()
declare -A CHANGE_RESULT_FILE=()
declare -A CHANGE_WORKTREE=()
declare -A CHANGE_CLEANUP_RESULT=()
declare -A PID_TO_CHANGE=()
SESSION_KEY=""
SESSION_DIR=""
STOP_REQUESTED=0

usage() {
  cat <<'EOF'
Usage:
  ./auto_apply.sh <change-id> [<change-id> ...]
  ./auto_apply.sh --all [--prefix mobile-foundation-]
  ./auto_apply.sh --deps deps/deps.mobile-foundation.json

What it does:
  0. Restores previously completed changes from the matching session archive
  1. Calls `openspec instructions apply --change <id> --json`
  2. Creates an isolated git worktree for the change from its base ref
  3. Sends the resulting instructions to Claude in that worktree
  4. Optionally auto-commits and squash-merges series step branches
  5. Optionally validates the change
  6. Archives the change only if all tasks are complete and validation passed

Options:
  --all               Apply all active changes
  --prefix <prefix>   Filter changes by prefix when used with --all
  --deps <file>       Dependency graph JSON file
  --max-parallel <n>  Max number of concurrent Claude runs (0 = unlimited)
  --no-archive        Do not archive even if the change is complete
  --cleanup-worktrees Remove per-change worktrees after a successful archive,
                      but only when the worktree is clean
  --merge-branches    Auto-commit and merge step branches back to the
                      series integration branch after Claude completes
  --skip-validate     Skip `openspec validate`
  --strict            Use `openspec validate --strict`
  --stop-on-error     Stop immediately when one change fails
  --dry-run           Print planned actions without invoking Claude
  -h, --help          Show this help message

Environment:
  CLAUDE_CMD          Override Claude invocation
                      default: claude -p --dangerously-skip-permissions
  OPENSPEC_CMD        Override OpenSpec invocation
                      default: npx -y @fission-ai/openspec
  OPENSPEC_AUTO_WORKTREE_ROOT
                      Root directory used to store per-change git worktrees
                      default: ../.openspec-auto-worktrees/<repo-name>
  OPENSPEC_AUTO_PORT_BASE
                      Base port used for per-worktree listener port blocks
                      default: 3000
  OPENSPEC_AUTO_PORT_BLOCK_SIZE
                      Port block size allocated to each change
                      default: 10

Examples:
  ./auto_apply.sh mobile-foundation-step-01-bootstrap-shell-and-routing-baseline
  ./auto_apply.sh --all --prefix mobile-foundation-
  ./auto_apply.sh --all --prefix mobile-foundation- --deps ./deps/deps.mobile-foundation.json --max-parallel 3
  ./auto_apply.sh --deps ./deps/deps.mobile-foundation.json
  CLAUDE_CMD="claude -p --dangerously-skip-permissions" ./auto_apply.sh --all --prefix mobile-foundation-

Session archive:
  Result files are persisted under:
    openspec/auto/logs/.auto-apply-run.<session-key>/
  The session key defaults to the series prefix when possible, for example:
    logs/.auto-apply-run.mobile-foundation

Dependency JSON formats:
  1. Object map
     {
       "step08": ["step01", "step05"],
       "step09": ["step03", "step08"]
     }

  2. Explicit list
     {
       "changes": [
         { "name": "step08", "dependsOn": ["step01", "step05"] },
         { "name": "step09", "dependsOn": ["step03", "step08"] }
       ]
     }
EOF
}

log() {
  printf '[auto-apply] %s\n' "$*"
}

change_log() {
  local change="$1"
  shift
  printf '[auto-apply][%s] %s\n' "${change}" "$*"
}

fail() {
  printf '[auto-apply] ERROR: %s\n' "$*" >&2
  exit 1
}

require_command() {
  local cmd="$1"
  command -v "${cmd}" >/dev/null 2>&1 || fail "Missing required command: ${cmd}"
}

run_openspec() {
  (
    # This repo keeps OpenSpec as a nested `./openspec` workspace, so the CLI
    # must run from the main project root for discovery to work correctly.
    cd "${PROJECT_ROOT}" || exit 1
    "${OPENSPEC_CMD[@]}" "$@"
  )
}

git_ref_exists() {
  local ref="$1"
  git -C "${PROJECT_ROOT}" rev-parse --verify --quiet "${ref}" >/dev/null 2>&1
}

series_prefix_for_change() {
  local change="$1"

  if [[ "${change}" =~ ^(.+)-step-[0-9]+($|-) ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
  fi
}

sanitize_session_key() {
  local raw="$1"
  local sanitized

  sanitized="$(printf '%s' "${raw}" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9._-]+/-/g; s/^-+//; s/-+$//; s/-{2,}/-/g')"
  if [[ -z "${sanitized}" ]]; then
    sanitized="batch"
  fi
  printf '%s\n' "${sanitized}"
}

common_series_prefix_for_targets() {
  local change prefix common=""

  for change in "${TARGET_CHANGES[@]}"; do
    prefix="$(series_prefix_for_change "${change}")"
    if [[ -z "${prefix}" ]]; then
      printf '\n'
      return 0
    fi
    if [[ -z "${common}" ]]; then
      common="${prefix}"
    elif [[ "${common}" != "${prefix}" ]]; then
      printf '\n'
      return 0
    fi
  done

  printf '%s\n' "${common}"
}

derive_session_key() {
  local candidate=""
  local dep_name=""
  local common_series=""

  if [[ -n "${PREFIX}" ]]; then
    candidate="${PREFIX%-}"
  fi

  if [[ -z "${candidate}" && -n "${DEPENDENCY_FILE}" ]]; then
    dep_name="$(basename "${DEPENDENCY_FILE}")"
    if [[ "${dep_name}" =~ ^deps[._-](.+)\.json$ ]]; then
      candidate="${BASH_REMATCH[1]}"
    fi
  fi

  if [[ -z "${candidate}" ]]; then
    common_series="$(common_series_prefix_for_targets)"
    if [[ -n "${common_series}" ]]; then
      candidate="${common_series}"
    fi
  fi

  if [[ -z "${candidate}" ]]; then
    if [[ "${#TARGET_CHANGES[@]}" -eq 1 ]]; then
      candidate="${TARGET_CHANGES[0]}"
    else
      candidate="batch"
    fi
  fi

  sanitize_session_key "${candidate}"
}

select_legacy_session_dir() {
  local best_dir=""
  local best_score=0
  local best_mtime=0
  local dir score mtime change result_file

  shopt -s nullglob
  for dir in "${AUTO_LOGS_DIR}"/.auto-apply-run.* "${SCRIPT_DIR}"/.auto-apply-run.*; do
    [[ -d "${dir}" ]] || continue
    [[ "${dir}" == "${SESSION_DIR}" ]] && continue

    score=0
    for change in "${TARGET_CHANGES[@]}"; do
      result_file="${dir}/${change}.result"
      if [[ -f "${result_file}" ]]; then
        score=$((score + 1))
      fi
    done

    if [[ "${score}" -le 0 ]]; then
      continue
    fi

    mtime=$(stat -c %Y "${dir}" 2>/dev/null || echo 0)
    if [[ "${score}" -gt "${best_score}" || ( "${score}" -eq "${best_score}" && "${mtime}" -gt "${best_mtime}" ) ]]; then
      best_dir="${dir}"
      best_score="${score}"
      best_mtime="${mtime}"
    fi
  done
  shopt -u nullglob

  printf '%s\n' "${best_dir}"
}

ensure_session_dir() {
  local legacy_dir=""

  SESSION_KEY="$(derive_session_key)"
  mkdir -p "${AUTO_LOGS_DIR}" || fail "Failed to create ${AUTO_LOGS_DIR}"
  SESSION_DIR="${AUTO_LOGS_DIR}/.auto-apply-run.${SESSION_KEY}"

  if [[ -e "${SESSION_DIR}" && ! -d "${SESSION_DIR}" ]]; then
    fail "Session archive path exists and is not a directory: ${SESSION_DIR}"
  fi

  if [[ -d "${SESSION_DIR}" ]]; then
    return 0
  fi

  legacy_dir="$(select_legacy_session_dir)"
  if [[ -n "${legacy_dir}" ]]; then
    cp -a "${legacy_dir}" "${SESSION_DIR}" || fail "Failed to copy legacy session dir ${legacy_dir} -> ${SESSION_DIR}"
    log "Copied legacy session archive ${legacy_dir} -> ${SESSION_DIR}"
    return 0
  fi

  mkdir -p "${SESSION_DIR}" || fail "Failed to create session archive ${SESSION_DIR}"
}

change_port_profile_file() {
  local change="$1"
  printf '%s/%s.ports.env\n' "${SESSION_DIR}" "${change}"
}

implementation_branch_for_change() {
  local change="$1"
  local candidate

  for candidate in "feat/${change}" "fix/${change}" "chore/${change}"; do
    if git_ref_exists "refs/heads/${candidate}"; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done

  printf 'feat/%s\n' "${change}"
}

integration_branch_for_change() {
  local change="$1"
  local series_prefix

  series_prefix="$(series_prefix_for_change "${change}")"
  if [[ -n "${series_prefix}" ]]; then
    printf 'dev/%s\n' "${series_prefix}"
    return 0
  fi

  printf 'dev\n'
}

integration_seed_ref_for_change() {
  local change="$1"
  local integration_branch

  integration_branch="$(integration_branch_for_change "${change}")"
  if git_ref_exists "refs/heads/${integration_branch}"; then
    printf '%s\n' "${integration_branch}"
    return 0
  fi
  if git_ref_exists "refs/remotes/origin/${integration_branch}"; then
    printf 'origin/%s\n' "${integration_branch}"
    return 0
  fi
  if git_ref_exists "refs/heads/dev"; then
    printf 'dev\n'
    return 0
  fi
  if git_ref_exists "refs/remotes/origin/dev"; then
    printf 'origin/dev\n'
    return 0
  fi

  printf 'HEAD\n'
}

ensure_local_integration_branch() {
  local change="$1"
  local integration_branch
  local seed_ref

  integration_branch="$(integration_branch_for_change "${change}")"
  if git_ref_exists "refs/heads/${integration_branch}"; then
    return 0
  fi

  seed_ref="$(integration_seed_ref_for_change "${change}")"
  git -C "${PROJECT_ROOT}" branch "${integration_branch}" "${seed_ref}" >/dev/null 2>&1 \
    || {
      change_log "${change}" "Failed to create integration branch ${integration_branch} from ${seed_ref}" >&2
      return 1
    }
  change_log "${change}" "Created integration branch ${integration_branch} from ${seed_ref}" >&2
}

branch_checked_out_worktree() {
  local branch="$1"
  python3 - "${PROJECT_ROOT}" "${branch}" <<'PY'
import subprocess
import sys

repo = sys.argv[1]
branch = sys.argv[2]
current_worktree = ""

result = subprocess.run(
    ["git", "-C", repo, "worktree", "list", "--porcelain"],
    check=True,
    capture_output=True,
    text=True,
)

for line in result.stdout.splitlines():
    if line.startswith("worktree "):
        current_worktree = line[len("worktree "):]
    elif line == f"branch refs/heads/{branch}":
        print(current_worktree)
        break
PY
}

change_tasks_file() {
  local change="$1"
  printf '%s/changes/%s/tasks.md\n' "${OPENSPEC_ROOT}" "${change}"
}

mark_branch_tasks() {
  local change="$1"
  local integration_branch="$2"
  local implementation_branch="$3"
  local mode="$4"
  local tasks_file

  tasks_file="$(change_tasks_file "${change}")"
  [[ -f "${tasks_file}" ]] || return 0

  python3 - "${tasks_file}" "${integration_branch}" "${implementation_branch}" "${mode}" <<'PY'
from pathlib import Path
import sys

tasks_file = Path(sys.argv[1])
integration_branch = sys.argv[2]
implementation_branch = sys.argv[3]
mode = sys.argv[4]

lines = tasks_file.read_text(encoding="utf-8").splitlines()
updated = []

for line in lines:
    new_line = line
    if line.startswith("- [ ]"):
        if mode == "prepare":
            if implementation_branch in line and "切出" in line and "squash merge" not in line:
                new_line = line.replace("- [ ]", "- [x]", 1)
            elif integration_branch in line and ("同步最新" in line or "从最新" in line):
                new_line = line.replace("- [ ]", "- [x]", 1)
        elif mode == "merge":
            if implementation_branch in line and integration_branch in line and "squash merge" in line:
                new_line = line.replace("- [ ]", "- [x]", 1)
    updated.append(new_line)

tasks_file.write_text("\n".join(updated) + "\n", encoding="utf-8")
PY
}

ensure_change_port_profile() {
  local change="$1"
  local profile_file
  local profile PORT_SLOT=0
  local max_slot=0
  local slot=0
  local api_port=0
  local worker_port=0
  local mock_port=0
  local grpc_port=0

  profile_file="$(change_port_profile_file "${change}")"
  if [[ -f "${profile_file}" ]]; then
    printf '%s\n' "${profile_file}"
    return 0
  fi

  shopt -s nullglob
  for profile in "${SESSION_DIR}"/*.ports.env; do
    PORT_SLOT=0
    # shellcheck disable=SC1090
    source "${profile}"
    if [[ "${PORT_SLOT}" =~ ^[0-9]+$ ]] && [[ "${PORT_SLOT}" -gt "${max_slot}" ]]; then
      max_slot="${PORT_SLOT}"
    fi
  done
  shopt -u nullglob

  slot=$((max_slot + 1))
  api_port=$((PORT_BLOCK_BASE + slot * PORT_BLOCK_SIZE))
  worker_port=$((api_port + 1))
  mock_port=$((api_port + 2))
  grpc_port=$((api_port + 3))

  cat >"${profile_file}" <<EOF
PORT_SLOT=${slot}
API_PORT=${api_port}
WORKER_PORT=${worker_port}
AGENT_RUNTIME_MOCK_PORT=${mock_port}
AGENT_RUNTIME_GRPC_PORT=${grpc_port}
AGENT_RUNTIME_BASE_URL=http://localhost:${mock_port}
AGENT_RUNTIME_GRPC_TARGET=127.0.0.1:${grpc_port}
EOF

  change_log "${change}" "Allocated isolated listener ports: API=${api_port}, WORKER=${worker_port}, MOCK=${mock_port}, GRPC=${grpc_port}" >&2
  printf '%s\n' "${profile_file}"
}

seed_worktree_env_if_needed() {
  local change="$1"
  local worktree_dir="$2"
  local env_example="${worktree_dir}/.env.example"
  local env_file="${worktree_dir}/.env"
  local profile_file=""
  local PORT_SLOT=0
  local API_PORT=0
  local WORKER_PORT=0
  local AGENT_RUNTIME_MOCK_PORT=0
  local AGENT_RUNTIME_GRPC_PORT=0
  local AGENT_RUNTIME_BASE_URL=""
  local AGENT_RUNTIME_GRPC_TARGET=""

  if [[ -f "${env_file}" ]]; then
    return 0
  fi

  [[ -f "${env_example}" ]] || fail "Missing .env.example in worktree: ${env_example}"

  profile_file="$(ensure_change_port_profile "${change}")" || return 1
  # shellcheck disable=SC1090
  source "${profile_file}"

  python3 - "${env_example}" "${env_file}" "${change}" "${PORT_SLOT}" "${API_PORT}" "${WORKER_PORT}" "${AGENT_RUNTIME_MOCK_PORT}" "${AGENT_RUNTIME_GRPC_PORT}" "${AGENT_RUNTIME_BASE_URL}" "${AGENT_RUNTIME_GRPC_TARGET}" <<'PY'
from pathlib import Path
import sys

env_example = Path(sys.argv[1])
env_file = Path(sys.argv[2])
change = sys.argv[3]
port_slot = sys.argv[4]
api_port = sys.argv[5]
worker_port = sys.argv[6]
mock_port = sys.argv[7]
grpc_port = sys.argv[8]
mock_url = sys.argv[9]
grpc_target = sys.argv[10]

updates = {
    "API_PORT": api_port,
    "WORKER_PORT": worker_port,
    "AGENT_RUNTIME_MOCK_PORT": mock_port,
    "AGENT_RUNTIME_GRPC_PORT": grpc_port,
    "AGENT_RUNTIME_BASE_URL": mock_url,
    "AGENT_RUNTIME_GRPC_TARGET": grpc_target,
}

lines = env_example.read_text(encoding="utf-8").splitlines()
rendered = [
    f"# Auto-generated for worktree change {change} (port slot {port_slot})",
    "# Shared infrastructure ports stay unchanged; local listener ports are isolated per worktree.",
]

for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in line:
        rendered.append(line)
        continue

    key, _ = line.split("=", 1)
    key = key.strip()
    if key in updates:
        rendered.append(f"{key}={updates[key]}")
    else:
        rendered.append(line)

env_file.write_text("\n".join(rendered) + "\n", encoding="utf-8")
PY

  change_log "${change}" "Created worktree .env from .env.example with isolated listener ports" >&2
}

commit_worktree_changes_if_needed() {
  local change="$1"
  local worktree_dir="$2"
  local implementation_branch="$3"

  if [[ -n "$(git -C "${worktree_dir}" status --porcelain --untracked-files=normal 2>/dev/null)" ]]; then
    git -C "${worktree_dir}" add -A >/dev/null 2>&1 \
      || {
        change_log "${change}" "Failed to stage changes for ${implementation_branch}" >&2
        return 1
      }
    git -C "${worktree_dir}" commit -m "${change}" >/dev/null 2>&1 \
      || {
        change_log "${change}" "Failed to commit changes for ${implementation_branch}" >&2
        return 1
      }
    change_log "${change}" "Committed implementation branch ${implementation_branch}" >&2
  fi
}

auto_merge_change_branch() {
  local change="$1"
  local worktree_dir="$2"
  local implementation_branch
  local integration_branch
  local branch_holder=""

  implementation_branch="$(implementation_branch_for_change "${change}")"
  integration_branch="$(integration_branch_for_change "${change}")"

  if [[ "${AUTO_MERGE_BRANCHES}" -ne 1 ]]; then
    return 0
  fi

  if [[ -z "$(series_prefix_for_change "${change}")" ]]; then
    return 0
  fi

  git -C "${worktree_dir}" switch "${implementation_branch}" >/dev/null 2>&1 \
    || {
      change_log "${change}" "Failed to switch ${worktree_dir} to ${implementation_branch} before merge" >&2
      return 1
    }

  commit_worktree_changes_if_needed "${change}" "${worktree_dir}" "${implementation_branch}" || return 1

  branch_holder="$(branch_checked_out_worktree "${integration_branch}")"
  if [[ -n "${branch_holder}" && "${branch_holder}" != "${worktree_dir}" ]]; then
    change_log "${change}" "Integration branch ${integration_branch} is already checked out in ${branch_holder}; cannot auto-merge" >&2
    return 1
  fi

  if ! git_ref_exists "refs/heads/${integration_branch}"; then
    ensure_local_integration_branch "${change}" || return 1
  fi

  if git -C "${PROJECT_ROOT}" diff --quiet "${integration_branch}" "${implementation_branch}" >/dev/null 2>&1; then
    change_log "${change}" "Integration branch ${integration_branch} already matches ${implementation_branch}" >&2
    mark_branch_tasks "${change}" "${integration_branch}" "${implementation_branch}" "merge"
    return 0
  fi

  git -C "${worktree_dir}" switch "${integration_branch}" >/dev/null 2>&1 \
    || {
      change_log "${change}" "Failed to switch ${worktree_dir} to ${integration_branch} for auto-merge" >&2
      return 1
    }
  git -C "${worktree_dir}" merge --squash "${implementation_branch}" >/dev/null 2>&1 \
    || {
      change_log "${change}" "Squash merge ${implementation_branch} -> ${integration_branch} failed" >&2
      return 1
    }

  if [[ -n "$(git -C "${worktree_dir}" status --porcelain --untracked-files=normal 2>/dev/null)" ]]; then
    git -C "${worktree_dir}" commit -m "${change}" >/dev/null 2>&1 \
      || {
        change_log "${change}" "Failed to commit squash merge into ${integration_branch}" >&2
        return 1
      }
    change_log "${change}" "Squash merged ${implementation_branch} into ${integration_branch}" >&2
  fi

  mark_branch_tasks "${change}" "${integration_branch}" "${implementation_branch}" "merge"
}

base_ref_for_change() {
  local change="$1"
  local series_prefix

  series_prefix="$(series_prefix_for_change "${change}")"
  if [[ -n "${series_prefix}" ]]; then
    if git_ref_exists "refs/heads/dev/${series_prefix}"; then
      printf 'dev/%s\n' "${series_prefix}"
      return 0
    fi
    if git_ref_exists "refs/remotes/origin/dev/${series_prefix}"; then
      printf 'origin/dev/%s\n' "${series_prefix}"
      return 0
    fi
  fi

  if git_ref_exists "refs/heads/dev"; then
    printf 'dev\n'
    return 0
  fi
  if git_ref_exists "refs/remotes/origin/dev"; then
    printf 'origin/dev\n'
    return 0
  fi

  printf 'HEAD\n'
}

prepare_worktree_for_change() {
  local change="$1"
  local worktree_dir="${WORKTREE_ROOT}/${change}"
  local base_ref
  local worktree_registered=0

  mkdir -p "${WORKTREE_ROOT}"
  base_ref="$(base_ref_for_change "${change}")"

  if git -C "${PROJECT_ROOT}" worktree list --porcelain | grep -F "worktree ${worktree_dir}" >/dev/null 2>&1; then
    worktree_registered=1
  fi

  if [[ "${worktree_registered}" -eq 1 ]]; then
    change_log "${change}" "Reusing isolated worktree at ${worktree_dir}" >&2
  elif [[ -e "${worktree_dir}" ]]; then
    fail "Worktree path already exists but is not registered: ${worktree_dir}"
  else
    if ! git -C "${PROJECT_ROOT}" worktree add --detach "${worktree_dir}" "${base_ref}" >/dev/null 2>&1; then
      fail "Failed to create worktree for ${change} from ${base_ref}"
    fi
    change_log "${change}" "Created isolated worktree at ${worktree_dir} from ${base_ref}" >&2
  fi

  [[ -e "${worktree_dir}/openspec" ]] || fail "Missing openspec entry in ${worktree_dir}. The main repository must track the openspec symlink before running auto_apply_old."
  seed_worktree_env_if_needed "${change}" "${worktree_dir}" || fail "Failed to initialize .env for ${change}"
  printf '%s\n' "${worktree_dir}"
}

cleanup_change_worktree() {
  local change="$1"
  local worktree_dir="${CHANGE_WORKTREE["${change}"]:-}"

  if [[ -z "${worktree_dir}" ]]; then
    return 0
  fi

  if [[ ! -d "${worktree_dir}" ]]; then
    CHANGE_CLEANUP_RESULT["${change}"]="removed"
    return 0
  fi

  if [[ -n "$(git -C "${worktree_dir}" status --porcelain --untracked-files=normal 2>/dev/null)" ]]; then
    CHANGE_CLEANUP_RESULT["${change}"]="skipped-dirty"
    change_log "${change}" "Skipped worktree cleanup because ${worktree_dir} still has uncommitted changes"
    return 0
  fi

  if git -C "${PROJECT_ROOT}" worktree remove "${worktree_dir}" >/dev/null 2>&1; then
    CHANGE_CLEANUP_RESULT["${change}"]="removed"
    change_log "${change}" "Removed isolated worktree ${worktree_dir}"
    return 0
  fi

  CHANGE_CLEANUP_RESULT["${change}"]="failed"
  CLEANUP_FAILED_CHANGES+=("${change}")
  change_log "${change}" "Failed to remove isolated worktree ${worktree_dir}"
  return 1
}

cleanup() {
  :
}

trap cleanup EXIT

print_worktree_summary() {
  local change

  if [[ "${#CHANGE_WORKTREE[@]}" -eq 0 ]]; then
    printf '  worktrees: none\n'
    return
  fi

  printf '  worktrees:\n'
  for change in "${TARGET_CHANGES[@]}"; do
    [[ -n "${CHANGE_WORKTREE["${change}"]:-}" ]] || continue
    printf '    %s -> %s\n' "${change}" "${CHANGE_WORKTREE["${change}"]}"
  done
}

print_cleanup_summary() {
  local change result printed=0

  if [[ "${CLEANUP_WORKTREES}" -eq 0 ]]; then
    printf '  cleanup: disabled\n'
    return
  fi

  printf '  cleanup:\n'
  for change in "${TARGET_CHANGES[@]}"; do
    result="${CHANGE_CLEANUP_RESULT["${change}"]:-not-requested}"
    case "${result}" in
      removed)
        printf '    %s -> removed\n' "${change}"
        printed=1
        ;;
      skipped-dirty)
        printf '    %s -> skipped (dirty worktree)\n' "${change}"
        printed=1
        ;;
      skipped-not-archived)
        printf '    %s -> skipped (not archived)\n' "${change}"
        printed=1
        ;;
      failed)
        printf '    %s -> failed\n' "${change}"
        printed=1
        ;;
      *)
        ;;
    esac
  done

  if [[ "${printed}" -eq 0 ]]; then
    printf '    none\n'
  fi
}

append_unique_change() {
  local value="$1"
  shift
  local -n array_ref="$1"
  local existing

  for existing in "${array_ref[@]}"; do
    if [[ "${existing}" == "${value}" ]]; then
      return 0
    fi
  done

  array_ref+=("${value}")
}

print_restored_summary() {
  if [[ "${#RESTORED_CHANGES[@]}" -gt 0 ]]; then
    printf '  restored: %s\n' "${RESTORED_CHANGES[*]}"
  else
    printf '  restored: none\n'
  fi
}

json_get_change_names() {
  local prefix="$1"
  local payload="$2"
  python3 - "$prefix" "$payload" <<'PY'
import json
import sys

prefix = sys.argv[1]
payload = json.loads(sys.argv[2])
changes = payload.get("changes", [])
names = []
for item in changes:
    name = item.get("name")
    if not name:
        continue
    if prefix and not name.startswith(prefix):
        continue
    names.append(name)

for name in sorted(names):
    print(name)
PY
}

json_change_progress() {
  local change="$1"
  local payload="$2"
  python3 - "$change" "$payload" <<'PY'
import json
import sys

target = sys.argv[1]
payload = json.loads(sys.argv[2])
for item in payload.get("changes", []):
    if item.get("name") == target:
        print(item.get("completedTasks", 0))
        print(item.get("totalTasks", 0))
        sys.exit(0)

print("0")
print("0")
PY
}

json_validate_result() {
  local payload="$1"
  python3 - "$payload" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
items = payload.get("items", [])
if not items:
    print("false")
    sys.exit(0)

print("true" if items[0].get("valid") else "false")
PY
}

json_missing_changes() {
  local payload="$1"
  shift
  python3 - "$payload" "$@" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
requested = sys.argv[2:]
known = {item.get("name") for item in payload.get("changes", []) if item.get("name")}

missing = [name for name in requested if name not in known]
for name in missing:
    print(name)
PY
}

normalize_dependency_graph() {
  local dep_file="$1"
  shift
  python3 - "${dep_file}" "$@" <<'PY'
import json
import sys
from pathlib import Path

dep_file = Path(sys.argv[1])
roots = list(sys.argv[2:])

payload = json.loads(dep_file.read_text(encoding="utf-8"))
graph = {}

def ensure_node(name: str):
    if name not in graph:
        graph[name] = []

def normalize_deps(raw):
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        out = []
        for item in raw:
            if not isinstance(item, str):
                raise SystemExit(f"Dependency names must be strings: {item!r}")
            out.append(item)
        return out
    raise SystemExit(f"Unsupported dependency value: {raw!r}")

if isinstance(payload, dict) and isinstance(payload.get("changes"), list):
    for item in payload["changes"]:
        if not isinstance(item, dict):
            raise SystemExit("Each item in changes[] must be an object")
        name = item.get("name") or item.get("id")
        if not isinstance(name, str) or not name:
            raise SystemExit("Each changes[] item must include a non-empty name or id")
        deps = normalize_deps(item.get("dependsOn", item.get("depends_on", item.get("deps"))))
        graph[name] = deps
elif isinstance(payload, dict):
    for name, deps in payload.items():
        if not isinstance(name, str) or not name:
            raise SystemExit("Dependency graph keys must be non-empty strings")
        graph[name] = normalize_deps(deps)
else:
    raise SystemExit("Dependency file must be an object or a {\"changes\": [...]} wrapper")

for name, deps in list(graph.items()):
    ensure_node(name)
    for dep in deps:
        ensure_node(dep)

selected = set()

def visit(name: str):
    ensure_node(name)
    if name in selected:
        return
    selected.add(name)
    for dep in graph.get(name, []):
        visit(dep)

if roots:
    for root in roots:
        visit(root)
else:
    for name in graph.keys():
        selected.add(name)

temp = set()
perm = set()

def dfs(name: str, stack: list[str]):
    if name in perm or name not in selected:
        return
    if name in temp:
        cycle = " -> ".join(stack + [name])
        raise SystemExit(f"Dependency cycle detected: {cycle}")
    temp.add(name)
    stack.append(name)
    for dep in graph.get(name, []):
        dfs(dep, stack)
    stack.pop()
    temp.remove(name)
    perm.add(name)

for name in sorted(selected):
    dfs(name, [])

for name in sorted(selected):
    deps = [dep for dep in graph.get(name, []) if dep in selected]
    print(f"{name}\t{' '.join(deps)}")
PY
}

build_prompt() {
  local change="$1"
  local worktree_dir="$2"
  local instructions_json="$3"
  local merge_guidance=""
  local series_prefix=""
  local implementation_branch=""
  local integration_branch=""

  series_prefix="$(series_prefix_for_change "${change}")"
  if [[ -n "${series_prefix}" ]]; then
    implementation_branch="$(implementation_branch_for_change "${change}")"
    integration_branch="$(integration_branch_for_change "${change}")"
    merge_guidance="$(cat <<EOF
- For the final series merge step, rely on Git's own branch checkout exclusivity instead of creating your own lock file.
- Once \`${implementation_branch}\` is committed and clean, try switching to \`${integration_branch}\` inside this isolated worktree.
- If Git reports that \`${integration_branch}\` is already checked out in another worktree, wait briefly and retry until the checkout succeeds.
- After the checkout succeeds, squash-merge \`${implementation_branch}\` into \`${integration_branch}\`, commit the merge result, then switch back to \`${implementation_branch}\` so the integration branch is not left checked out.
EOF
)"
  fi
  cat <<EOF
You are implementing the OpenSpec change \`${change}\` in the project at:
\`${worktree_dir}\`

The canonical main repository is:
\`${PROJECT_ROOT}\`

The OpenSpec repository is available inside the worktree at:
\`${worktree_dir}/openspec\`

Follow the OpenSpec apply instructions below exactly.

Important requirements:
- Work only from the isolated worktree above.
- Do not switch branches or edit files in the canonical main repository path directly.
- The isolated worktree may start from a detached base ref. If the change tasks require branch checkout or merge steps, perform them inside the isolated worktree only.
- Implement code and documentation changes needed for the change.
- Update the change's \`tasks.md\` checkboxes via the \`openspec/\` path inside the worktree as tasks are completed.
- Run relevant tests or validation when appropriate.
- Do not archive the change yourself; the wrapper script will decide that.
- If you hit a blocker, explain it clearly and stop rather than pretending the change is complete.
${merge_guidance}

OpenSpec apply instructions:
\`\`\`json
${instructions_json}
\`\`\`
EOF
}

run_claude_for_change() {
  local change="$1"
  local worktree_dir="$2"
  local instructions_json="$3"
  local prompt

  prompt="$(build_prompt "${change}" "${worktree_dir}" "${instructions_json}")"

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    change_log "${change}" "Dry run: would invoke Claude in ${worktree_dir}"
    return 0
  fi

  (
    cd "${worktree_dir}" || exit 1
    "${CLAUDE_CMD[@]}" "${prompt}" 2>&1 | sed "s/^/[claude][${change}] /"
  )
}

mark_failure() {
  local change="$1"
  FAILED_CHANGES+=("${change}")
  if [[ "${STOP_ON_ERROR}" -eq 1 ]]; then
    summarize_and_exit 1
  fi
}

summarize_and_exit() {
  local exit_code="$1"

  echo
  log "Summary"
  if [[ -n "${SESSION_DIR}" ]]; then
    printf '  session: %s\n' "${SESSION_DIR}"
  else
    printf '  session: none\n'
  fi
  print_restored_summary
  print_worktree_summary
  print_cleanup_summary
  if [[ "${#COMPLETED_CHANGES[@]}" -gt 0 ]]; then
    printf '  completed: %s\n' "${COMPLETED_CHANGES[*]}"
  else
    printf '  completed: none\n'
  fi
  if [[ "${#ARCHIVED_CHANGES[@]}" -gt 0 ]]; then
    printf '  archived: %s\n' "${ARCHIVED_CHANGES[*]}"
  else
    printf '  archived: none\n'
  fi

  if [[ "${#INCOMPLETE_CHANGES[@]}" -gt 0 ]]; then
    printf '  incomplete: %s\n' "${INCOMPLETE_CHANGES[*]}" >&2
  else
    printf '  incomplete: none\n'
  fi

  if [[ "${#BLOCKED_CHANGES[@]}" -gt 0 ]]; then
    printf '  blocked: %s\n' "${BLOCKED_CHANGES[*]}" >&2
  else
    printf '  blocked: none\n'
  fi

  if [[ "${#FAILED_CHANGES[@]}" -gt 0 ]]; then
    printf '  failed: %s\n' "${FAILED_CHANGES[*]}" >&2
  else
    printf '  failed: none\n'
  fi
  if [[ "${#CLEANUP_FAILED_CHANGES[@]}" -gt 0 ]]; then
    printf '  cleanup-failed: %s\n' "${CLEANUP_FAILED_CHANGES[*]}" >&2
  else
    printf '  cleanup-failed: none\n'
  fi

  exit "${exit_code}"
}

write_result_file() {
  local result_file="$1"
  local status="$2"
  local completed_tasks="$3"
  local total_tasks="$4"
  local archived="$5"

  cat >"${result_file}" <<EOF
status=${status}
completed_tasks=${completed_tasks}
total_tasks=${total_tasks}
archived=${archived}
EOF
}

restore_completed_changes_from_session() {
  local change result_file
  local status completed_tasks total_tasks archived

  RESTORED_CHANGES=()

  for change in "${TARGET_CHANGES[@]}"; do
    result_file="${SESSION_DIR}/${change}.result"
    CHANGE_RESULT_FILE["${change}"]="${result_file}"

    if [[ ! -f "${result_file}" ]]; then
      continue
    fi

    status=""
    completed_tasks=0
    total_tasks=0
    archived=0
    # shellcheck disable=SC1090
    source "${result_file}"

    if [[ "${status:-}" != "success" || "${archived:-0}" -ne 1 ]]; then
      continue
    fi

    CHANGE_STATE["${change}"]="success"
    append_unique_change "${change}" COMPLETED_CHANGES
    append_unique_change "${change}" RESTORED_CHANGES

    append_unique_change "${change}" ARCHIVED_CHANGES

    change_log "${change}" "Restored completed state from ${SESSION_DIR}"
  done
}

process_change() {
  local change="$1"
  local result_file="$2"
  local worktree_dir="$3"
  local archived=0
  local completed_tasks=0
  local total_tasks=0
  local validation_ok=1

  change_log "${change}" "Starting"

  if ! run_openspec status --change "${change}" --json >/dev/null 2>&1; then
    change_log "${change}" "Failed to read change status"
    write_result_file "${result_file}" "failed" 0 0 0
    return 1
  fi

  local instructions_json
  if ! instructions_json="$(run_openspec instructions apply --change "${change}" --json 2>/dev/null)"; then
    change_log "${change}" "Failed to generate apply instructions"
    write_result_file "${result_file}" "failed" 0 0 0
    return 1
  fi

  if ! run_claude_for_change "${change}" "${worktree_dir}" "${instructions_json}"; then
    change_log "${change}" "Claude execution failed"
    write_result_file "${result_file}" "failed" 0 0 0
    return 1
  fi

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    write_result_file "${result_file}" "success" 1 1 0
    change_log "${change}" "Dry run completed"
    return 0
  fi

  if ! auto_merge_change_branch "${change}" "${worktree_dir}"; then
    change_log "${change}" "Auto-merge failed"
    write_result_file "${result_file}" "failed" 0 0 0
    return 1
  fi

  local list_json_after_apply
  if ! list_json_after_apply="$(run_openspec list --changes --json 2>/dev/null)"; then
    change_log "${change}" "Failed to re-read change list after apply"
    write_result_file "${result_file}" "failed" 0 0 0
    return 1
  fi

  mapfile -t progress < <(json_change_progress "${change}" "${list_json_after_apply}")
  completed_tasks="${progress[0]:-0}"
  total_tasks="${progress[1]:-0}"
  change_log "${change}" "Task progress: ${completed_tasks}/${total_tasks}"

  if [[ "${SKIP_VALIDATE}" -eq 0 ]]; then
    local -a validate_args=(validate "${change}" --type change --json)
    if [[ "${STRICT_VALIDATE}" -eq 1 ]]; then
      validate_args+=(--strict)
    fi

    local validate_json
    if ! validate_json="$(run_openspec "${validate_args[@]}" 2>/dev/null)"; then
      change_log "${change}" "Validation command failed"
      write_result_file "${result_file}" "failed" "${completed_tasks}" "${total_tasks}" 0
      return 1
    fi

    local validate_ok_str
    validate_ok_str="$(json_validate_result "${validate_json}")"
    if [[ "${validate_ok_str}" != "true" ]]; then
      validation_ok=0
      change_log "${change}" "Validation failed"
      write_result_file "${result_file}" "failed" "${completed_tasks}" "${total_tasks}" 0
      return 1
    fi
  fi

  if [[ "${completed_tasks}" -ne "${total_tasks}" || "${total_tasks}" -le 0 ]]; then
    change_log "${change}" "Tasks are not complete; dependency dependents will not be unblocked"
    write_result_file "${result_file}" "incomplete" "${completed_tasks}" "${total_tasks}" 0
    return 0
  fi

  if [[ "${AUTO_ARCHIVE}" -eq 1 && "${validation_ok}" -eq 1 ]]; then
    if run_openspec archive "${change}" -y >/dev/null 2>&1; then
      archived=1
      change_log "${change}" "Archived"
    else
      change_log "${change}" "Archive failed"
      write_result_file "${result_file}" "failed" "${completed_tasks}" "${total_tasks}" 0
      return 1
    fi
  fi

  write_result_file "${result_file}" "success" "${completed_tasks}" "${total_tasks}" "${archived}"
  change_log "${change}" "Completed"
  return 0
}

initialize_dependency_map() {
  local dep_file="$1"

  CHANGE_DEPS=()
  if [[ -n "${dep_file}" ]]; then
    local normalized_graph_text
    normalized_graph_text="$(normalize_dependency_graph "${dep_file}" "${TARGET_CHANGES[@]}")" \
      || fail "Failed to parse dependency graph from ${dep_file}"
    mapfile -t normalized_graph <<< "${normalized_graph_text}"

    TARGET_CHANGES=()
    local line change deps
    for line in "${normalized_graph[@]}"; do
      change="${line%%$'\t'*}"
      deps="${line#*$'\t'}"
      if [[ "${line}" != *$'\t'* ]]; then
        deps=""
      fi
      TARGET_CHANGES+=("${change}")
      CHANGE_DEPS["${change}"]="${deps}"
    done
  else
    local change
    for change in "${TARGET_CHANGES[@]}"; do
      CHANGE_DEPS["${change}"]=""
    done
  fi
}

assert_target_changes_exist() {
  local list_json
  local -a missing_changes=()
  local -a unresolved_missing_changes=()
  local change

  list_json="$(run_openspec list --changes --json)" || fail "Failed to list changes for preflight validation"
  mapfile -t missing_changes < <(json_missing_changes "${list_json}" "${TARGET_CHANGES[@]}")

  for change in "${missing_changes[@]}"; do
    if [[ "${CHANGE_STATE["${change}"]:-pending}" == "success" ]]; then
      continue
    fi
    unresolved_missing_changes+=("${change}")
  done

  if [[ "${#unresolved_missing_changes[@]}" -gt 0 ]]; then
    fail "Missing change directories for: ${unresolved_missing_changes[*]}. Check openspec/changes/, dependency JSON, or session archive ${SESSION_DIR}."
  fi
}

active_job_count() {
  echo "${#PID_TO_CHANGE[@]}"
}

is_capacity_available() {
  local active
  active="$(active_job_count)"
  if [[ "${MAX_PARALLEL}" -eq 0 ]]; then
    return 0
  fi

  [[ "${active}" -lt "${MAX_PARALLEL}" ]]
}

dependency_state_for_change() {
  local change="$1"
  local dep dep_state

  for dep in ${CHANGE_DEPS["${change}"]}; do
    dep_state="${CHANGE_STATE["${dep}"]:-pending}"
    case "${dep_state}" in
      success)
        ;;
      failed|blocked)
        return 2
        ;;
      *)
        return 1
        ;;
    esac
  done

  return 0
}

mark_blocked_changes() {
  local change dep dep_state

  for change in "${TARGET_CHANGES[@]}"; do
    [[ "${CHANGE_STATE["${change}"]:-pending}" == "pending" ]] || continue
    for dep in ${CHANGE_DEPS["${change}"]}; do
      dep_state="${CHANGE_STATE["${dep}"]:-pending}"
      if [[ "${dep_state}" == "failed" || "${dep_state}" == "blocked" ]]; then
        CHANGE_STATE["${change}"]="blocked"
        BLOCKED_CHANGES+=("${change}")
        log "Blocking ${change}; dependency ${dep} ended as ${dep_state}"
        break
      fi
    done
  done
}

start_change_job() {
  local change="$1"
  local result_file="${SESSION_DIR}/${change}.result"
  local worktree_dir=""

  CHANGE_STATE["${change}"]="running"
  CHANGE_RESULT_FILE["${change}"]="${result_file}"
  CHANGE_CLEANUP_RESULT["${change}"]="not-requested"

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    worktree_dir="${WORKTREE_ROOT}/${change}"
  else
    worktree_dir="$(prepare_worktree_for_change "${change}")" || {
      CHANGE_STATE["${change}"]="failed"
      FAILED_CHANGES+=("${change}")
      STOP_REQUESTED=$(( STOP_ON_ERROR == 1 ? 1 : STOP_REQUESTED ))
      return 1
    }
  fi
  CHANGE_WORKTREE["${change}"]="${worktree_dir}"

  (
    process_change "${change}" "${result_file}" "${worktree_dir}"
  ) &

  local pid=$!
  PID_TO_CHANGE["${pid}"]="${change}"
  log "Started ${change} (pid=${pid}, worktree=${worktree_dir})"
}

cancel_running_jobs() {
  local pid
  for pid in "${!PID_TO_CHANGE[@]}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
}

handle_finished_job() {
  local pid="$1"
  local wait_rc="$2"
  local change="${PID_TO_CHANGE["${pid}"]}"
  local result_file="${CHANGE_RESULT_FILE["${change}"]}"

  unset 'PID_TO_CHANGE['"${pid}"']'

  if [[ ! -f "${result_file}" ]]; then
    CHANGE_STATE["${change}"]="failed"
    FAILED_CHANGES+=("${change}")
    log "Change ${change} exited without a result file"
    STOP_REQUESTED=$(( STOP_ON_ERROR == 1 ? 1 : STOP_REQUESTED ))
    return
  fi

  local status completed_tasks total_tasks archived
  # shellcheck disable=SC1090
  source "${result_file}"

  case "${status}" in
    success)
      CHANGE_STATE["${change}"]="success"
      COMPLETED_CHANGES+=("${change}")
      if [[ "${archived:-0}" -eq 1 ]]; then
        ARCHIVED_CHANGES+=("${change}")
        if [[ "${CLEANUP_WORKTREES}" -eq 1 ]]; then
          cleanup_change_worktree "${change}" || true
        fi
      elif [[ "${CLEANUP_WORKTREES}" -eq 1 ]]; then
        CHANGE_CLEANUP_RESULT["${change}"]="skipped-not-archived"
      fi
      ;;
    incomplete)
      CHANGE_STATE["${change}"]="failed"
      INCOMPLETE_CHANGES+=("${change}")
      STOP_REQUESTED=$(( STOP_ON_ERROR == 1 ? 1 : STOP_REQUESTED ))
      ;;
    *)
      CHANGE_STATE["${change}"]="failed"
      FAILED_CHANGES+=("${change}")
      STOP_REQUESTED=$(( STOP_ON_ERROR == 1 ? 1 : STOP_REQUESTED ))
      ;;
  esac

  if [[ "${wait_rc}" -ne 0 && "${status}" == "success" ]]; then
    CHANGE_STATE["${change}"]="failed"
    COMPLETED_CHANGES=("${COMPLETED_CHANGES[@]/${change}}")
    FAILED_CHANGES+=("${change}")
    STOP_REQUESTED=$(( STOP_ON_ERROR == 1 ? 1 : STOP_REQUESTED ))
  fi
}

wait_for_any_job() {
  local pid change rc

  while true; do
    for pid in "${!PID_TO_CHANGE[@]}"; do
      if ! kill -0 "${pid}" 2>/dev/null; then
        wait "${pid}"
        rc=$?
        change="${PID_TO_CHANGE["${pid}"]}"
        log "Finished ${change} (exit=${rc})"
        handle_finished_job "${pid}" "${rc}"
        return 0
      fi
    done
    sleep 1
  done
}

has_pending_changes() {
  local change
  for change in "${TARGET_CHANGES[@]}"; do
    if [[ "${CHANGE_STATE["${change}"]:-pending}" == "pending" ]]; then
      return 0
    fi
  done
  return 1
}

start_ready_jobs() {
  local change dep_status started=0

  for change in "${TARGET_CHANGES[@]}"; do
    [[ "${CHANGE_STATE["${change}"]:-pending}" == "pending" ]] || continue
    is_capacity_available || break
    dependency_state_for_change "${change}"
    dep_status=$?
    if [[ "${dep_status}" -eq 0 ]]; then
      if start_change_job "${change}"; then
        started=1
      fi
    fi
  done

  return "${started}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      RUN_ALL=1
      shift
      ;;
    --prefix)
      [[ $# -ge 2 ]] || fail "--prefix requires a value"
      PREFIX="$2"
      shift 2
      ;;
    --deps)
      [[ $# -ge 2 ]] || fail "--deps requires a file path"
      DEPENDENCY_FILE="$2"
      shift 2
      ;;
    --max-parallel)
      [[ $# -ge 2 ]] || fail "--max-parallel requires a value"
      MAX_PARALLEL="$2"
      MAX_PARALLEL_SET=1
      shift 2
      ;;
    --no-archive)
      AUTO_ARCHIVE=0
      shift
      ;;
    --cleanup-worktrees)
      CLEANUP_WORKTREES=1
      shift
      ;;
    --merge-branches)
      AUTO_MERGE_BRANCHES=1
      shift
      ;;
    --skip-validate)
      SKIP_VALIDATE=1
      shift
      ;;
    --strict)
      STRICT_VALIDATE=1
      shift
      ;;
    --stop-on-error)
      STOP_ON_ERROR=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        TARGET_CHANGES+=("$1")
        shift
      done
      ;;
    -*)
      fail "Unknown option: $1"
      ;;
    *)
      TARGET_CHANGES+=("$1")
      shift
      ;;
  esac
done

require_command "${CLAUDE_CMD[0]}"
require_command "${OPENSPEC_CMD[0]}"
require_command "git"
require_command "python3"

git -C "${PROJECT_ROOT}" worktree prune >/dev/null 2>&1 || true

if [[ -n "${DEPENDENCY_FILE}" && ! -f "${DEPENDENCY_FILE}" ]]; then
  fail "Dependency file not found: ${DEPENDENCY_FILE}"
fi

if ! [[ "${MAX_PARALLEL}" =~ ^[0-9]+$ ]]; then
  fail "--max-parallel must be a non-negative integer"
fi

if ! [[ "${PORT_BLOCK_BASE}" =~ ^[0-9]+$ ]]; then
  fail "OPENSPEC_AUTO_PORT_BASE must be a non-negative integer"
fi

if ! [[ "${PORT_BLOCK_SIZE}" =~ ^[0-9]+$ ]] || [[ "${PORT_BLOCK_SIZE}" -lt 4 ]]; then
  fail "OPENSPEC_AUTO_PORT_BLOCK_SIZE must be an integer >= 4"
fi

if [[ "${MAX_PARALLEL_SET}" -eq 0 ]]; then
  if [[ -n "${DEPENDENCY_FILE}" ]]; then
    MAX_PARALLEL=0
  else
    MAX_PARALLEL=1
  fi
fi

if [[ "${RUN_ALL}" -eq 1 && "${#TARGET_CHANGES[@]}" -gt 0 ]]; then
  fail "Use either explicit change ids or --all, not both"
fi

if [[ "${CLEANUP_WORKTREES}" -eq 1 && "${AUTO_ARCHIVE}" -eq 0 ]]; then
  log "Cleanup is enabled, but --no-archive was also set; worktrees will be kept because cleanup only runs after successful archive"
fi

if [[ "${RUN_ALL}" -eq 0 && "${#TARGET_CHANGES[@]}" -eq 0 && -z "${DEPENDENCY_FILE}" ]]; then
  usage
  exit 1
fi

if [[ "${RUN_ALL}" -eq 1 ]]; then
  log "Resolving active changes from OpenSpec"
  list_json="$(run_openspec list --changes --json)" || fail "Failed to list changes"
  mapfile -t TARGET_CHANGES < <(json_get_change_names "${PREFIX}" "${list_json}")

  if [[ "${#TARGET_CHANGES[@]}" -eq 0 ]]; then
    fail "No matching active changes found"
  fi
fi

initialize_dependency_map "${DEPENDENCY_FILE}"

if [[ "${#TARGET_CHANGES[@]}" -eq 0 ]]; then
  fail "No changes resolved for execution"
fi

ensure_session_dir

for change in "${TARGET_CHANGES[@]}"; do
  CHANGE_STATE["${change}"]="pending"
done

restore_completed_changes_from_session

assert_target_changes_exist

log "Project root: ${PROJECT_ROOT}"
log "Nested OpenSpec repo: ${OPENSPEC_ROOT}"
log "Worktree root: ${WORKTREE_ROOT}"
log "Port block: base=${PORT_BLOCK_BASE}, size=${PORT_BLOCK_SIZE}"
log "Session key: ${SESSION_KEY}"
log "Session dir: ${SESSION_DIR}"
log "OpenSpec command: ${OPENSPEC_CMD_STRING}"
log "Claude command: ${CLAUDE_CMD_STRING}"
log "Auto archive: ${AUTO_ARCHIVE}"
log "Auto merge branches: ${AUTO_MERGE_BRANCHES}"
log "Cleanup worktrees: ${CLEANUP_WORKTREES}"
if [[ -n "${DEPENDENCY_FILE}" ]]; then
  log "Dependency file: ${DEPENDENCY_FILE}"
fi
log "Max parallel: ${MAX_PARALLEL}"
log "Target changes: ${TARGET_CHANGES[*]}"

overall_failed=0

while true; do
  mark_blocked_changes

  if [[ "${STOP_REQUESTED}" -eq 0 ]]; then
    start_ready_jobs || true
  fi

  if [[ "${STOP_REQUESTED}" -eq 1 ]]; then
    cancel_running_jobs
  fi

  if [[ "$(active_job_count)" -gt 0 ]]; then
    wait_for_any_job
    continue
  fi

  if has_pending_changes; then
    mark_blocked_changes
    if has_pending_changes; then
      log "No runnable changes remain; unresolved pending changes detected"
      overall_failed=1
      break
    fi
  fi

  break
done

if [[ "${#FAILED_CHANGES[@]}" -gt 0 || "${#INCOMPLETE_CHANGES[@]}" -gt 0 || "${#BLOCKED_CHANGES[@]}" -gt 0 ]]; then
  overall_failed=1
fi
if [[ "${#CLEANUP_FAILED_CHANGES[@]}" -gt 0 ]]; then
  overall_failed=1
fi

if [[ "${overall_failed}" -eq 1 ]]; then
  summarize_and_exit 1
fi

summarize_and_exit 0
