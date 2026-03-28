from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from openspec_py.git_ops import (
    GitCommandError,
    current_branch,
    is_registered_worktree,
    ref_exists,
    run_git,
    worktree_path_is_reusable,
)
from openspec_py.legacy_session_state import ensure_legacy_session_dir
from openspec_py.git_tasks import inspect_managed_git_tasks, mark_start_tasks
from openspec_py.legacy_results import write_legacy_result
from openspec_py.orchestrator import OrchestrationSession
from openspec_py.parsers import parse_shell_kv_file
from openspec_py.runtime_logging import append_event
from openspec_py.session_store import SessionWriteResult, write_session_payload


class PreparationError(RuntimeError):
    """Raised when a preparation step fails."""


@dataclass(frozen=True, slots=True)
class PortAssignment:
    slot: int
    api_port: int
    worker_port: int
    agent_runtime_mock_port: int
    agent_runtime_grpc_port: int
    agent_runtime_base_url: str
    agent_runtime_grpc_target: str
    source_path: Path

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["source_path"] = str(self.source_path)
        return payload


@dataclass(slots=True)
class PreparationItem:
    change_id: str
    series: str
    step: int | None
    action: str
    plan_state: str
    current_status: str
    change_path: Path
    tasks_path: Path | None
    worktree_path: Path | None
    base_ref: str | None
    implementation_branch: str | None
    integration_branch: str | None
    managed_git: bool
    prep_state: str
    reason: str
    notes: list[str] = field(default_factory=list)
    port_profile: PortAssignment | None = None
    port_profile_path: Path | None = None
    env_status: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["change_path"] = str(self.change_path)
        payload["tasks_path"] = str(self.tasks_path) if self.tasks_path else None
        payload["worktree_path"] = str(self.worktree_path) if self.worktree_path else None
        payload["port_profile"] = (
            self.port_profile.to_dict() if self.port_profile else None
        )
        payload["port_profile_path"] = (
            str(self.port_profile_path) if self.port_profile_path else None
        )
        payload["started_at"] = self.started_at.isoformat() if self.started_at else None
        payload["finished_at"] = self.finished_at.isoformat() if self.finished_at else None
        return payload


@dataclass(slots=True)
class PreparationSession:
    workspace_root: Path
    repo_root: Path
    generated_at: datetime
    session_key: str
    execute: bool
    max_parallel: int
    worktree_root: Path
    legacy_session_dir: Path
    port_block_base: int
    port_block_size: int
    items: list[PreparationItem] = field(default_factory=list)

    @property
    def state_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.prep_state] = counts.get(item.prep_state, 0) + 1
        return dict(sorted(counts.items()))

    @property
    def prepared_paths(self) -> dict[str, Path]:
        return {
            item.change_id: item.worktree_path
            for item in self.items
            if item.worktree_path is not None and item.prep_state == "prepared"
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_root": str(self.workspace_root),
            "repo_root": str(self.repo_root),
            "generated_at": self.generated_at.isoformat(),
            "session_key": self.session_key,
            "execute": self.execute,
            "max_parallel": self.max_parallel,
            "worktree_root": str(self.worktree_root),
            "legacy_session_dir": str(self.legacy_session_dir),
            "port_block_base": self.port_block_base,
            "port_block_size": self.port_block_size,
            "state_counts": self.state_counts,
            "items": [item.to_dict() for item in self.items],
        }


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as error:
        raise PreparationError(f"Environment variable {name} must be an integer") from error


def default_worktree_root(workspace_root: Path) -> Path:
    override = os.environ.get("OPENSPEC_AUTO_WORKTREE_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (
        workspace_root.parent / ".openspec-auto-worktrees" / workspace_root.name
    ).resolve()


def default_session_dir(workspace_root: Path, session_key: str) -> Path:
    return (
        workspace_root
        / "openspec"
        / "auto"
        / "logs"
        / f".auto-apply-run.{session_key}"
    ).resolve()


def _candidate_base_refs(repo_root: Path, series: str, step: int | None) -> list[str]:
    refs: list[str] = []
    if step is not None:
        refs.extend([f"series/{series}", f"origin/series/{series}"])
    refs.extend(["dev", "origin/dev", "master", "origin/master"])
    branch = current_branch(repo_root)
    if branch:
        refs.append(branch)
    refs.append("HEAD")
    unique: list[str] = []
    for ref in refs:
        if ref not in unique:
            unique.append(ref)
    return unique


def base_ref_for_change(repo_root: Path, series: str, step: int | None) -> str:
    for ref in _candidate_base_refs(repo_root, series, step):
        if ref == "HEAD":
            return ref
        if ref.startswith("origin/"):
            if ref_exists(repo_root, f"refs/remotes/{ref}"):
                return ref
            continue
        if ref_exists(repo_root, f"refs/heads/{ref}"):
            return ref
    return "HEAD"


def _default_integration_branch(series: str, step: int | None) -> str:
    return f"series/{series}" if step is not None else "dev"


def _default_implementation_branch(change_id: str) -> str:
    return f"feat/{change_id}"


def build_preparation_session(
    orchestration: OrchestrationSession,
    *,
    execute: bool,
) -> PreparationSession:
    workspace_root = orchestration.workspace_root.resolve()
    worktree_root = default_worktree_root(workspace_root)
    session_dir = default_session_dir(workspace_root, orchestration.session_key)
    items: list[PreparationItem] = []

    for orchestration_item in orchestration.items:
        tasks_path = orchestration_item.path / "tasks.md"
        default_impl = _default_implementation_branch(orchestration_item.change_id)
        default_integ = _default_integration_branch(
            orchestration_item.series, orchestration_item.step
        )
        implementation_branch = default_impl
        integration_branch = default_integ
        managed_git = False
        if tasks_path.exists():
            metadata = inspect_managed_git_tasks(
                tasks_path,
                orchestration_item.change_id,
                default_impl,
                default_integ,
            )
            implementation_branch = metadata.implementation_branch
            integration_branch = metadata.integration_branch
            managed_git = metadata.managed

        if orchestration_item.action == "launch_now":
            prep_state = "pending_preparation" if execute else "dry_run"
        elif orchestration_item.action == "keep_running":
            prep_state = "already_running"
        elif orchestration_item.action == "wait_capacity":
            prep_state = "waiting_capacity"
        elif orchestration_item.action == "wait_dependencies":
            prep_state = "waiting_dependencies"
        elif orchestration_item.action == "halted":
            prep_state = "halted"
        elif orchestration_item.action == "completed":
            prep_state = "completed"
        else:
            prep_state = "blocked"

        worktree_path = (
            worktree_root / orchestration_item.change_id
            if orchestration_item.action in {"launch_now", "keep_running"}
            else None
        )
        base_ref = (
            base_ref_for_change(
                workspace_root,
                orchestration_item.series,
                orchestration_item.step,
            )
            if orchestration_item.action in {"launch_now", "keep_running"}
            else None
        )

        items.append(
            PreparationItem(
                change_id=orchestration_item.change_id,
                series=orchestration_item.series,
                step=orchestration_item.step,
                action=orchestration_item.action,
                plan_state=orchestration_item.plan_state,
                current_status=orchestration_item.current_status,
                change_path=orchestration_item.path,
                tasks_path=tasks_path if tasks_path.exists() else None,
                worktree_path=worktree_path,
                base_ref=base_ref,
                implementation_branch=implementation_branch,
                integration_branch=integration_branch,
                managed_git=managed_git,
                prep_state=prep_state,
                reason=orchestration_item.reason,
            )
        )

    return PreparationSession(
        workspace_root=workspace_root,
        repo_root=workspace_root,
        generated_at=datetime.now(),
        session_key=orchestration.session_key,
        execute=execute,
        max_parallel=orchestration.max_parallel,
        worktree_root=worktree_root,
        legacy_session_dir=session_dir,
        port_block_base=_env_int("OPENSPEC_AUTO_PORT_BASE", 3000),
        port_block_size=_env_int("OPENSPEC_AUTO_PORT_BLOCK_SIZE", 10),
        items=items,
    )


def write_preparation_session(
    session: PreparationSession,
    output_path: Path,
    runtime_root: Path,
    *,
    event_name: str = "preparation_written",
) -> SessionWriteResult:
    return write_session_payload(
        session.to_dict(),
        output_path,
        runtime_root,
        event_name,
        {
            "session_key": session.session_key,
            "item_count": len(session.items),
            "state_counts": session.state_counts,
            "execute": session.execute,
            "max_parallel": session.max_parallel,
            "legacy_session_dir": str(session.legacy_session_dir),
            "worktree_root": str(session.worktree_root),
        },
    )


def _ensure_worktree(
    repo_root: Path,
    worktree_root: Path,
    worktree_path: Path,
    base_ref: str,
) -> str:
    worktree_root.mkdir(parents=True, exist_ok=True)
    if is_registered_worktree(repo_root, worktree_path):
        return "reused_registered"
    if worktree_path_is_reusable(repo_root, worktree_path):
        run_git(repo_root, "worktree", "repair", str(worktree_path), check=False)
        return "reused_existing"
    if worktree_path.exists():
        raise PreparationError(
            f"Worktree path already exists but does not belong to this repository: {worktree_path}"
        )
    run_git(repo_root, "worktree", "add", "--detach", str(worktree_path), base_ref)
    return "created"


def _parse_port_assignment(path: Path) -> PortAssignment:
    payload = parse_shell_kv_file(path)
    return PortAssignment(
        slot=int(payload["PORT_SLOT"]),
        api_port=int(payload["API_PORT"]),
        worker_port=int(payload["WORKER_PORT"]),
        agent_runtime_mock_port=int(payload["AGENT_RUNTIME_MOCK_PORT"]),
        agent_runtime_grpc_port=int(payload["AGENT_RUNTIME_GRPC_PORT"]),
        agent_runtime_base_url=payload["AGENT_RUNTIME_BASE_URL"],
        agent_runtime_grpc_target=payload["AGENT_RUNTIME_GRPC_TARGET"],
        source_path=path,
    )


def _ensure_port_profile(
    session_dir: Path,
    change_id: str,
    *,
    block_base: int,
    block_size: int,
) -> PortAssignment:
    session_dir.mkdir(parents=True, exist_ok=True)
    target = session_dir / f"{change_id}.ports.env"
    if target.exists():
        return _parse_port_assignment(target)

    max_slot = -1
    for profile in session_dir.glob("*.ports.env"):
        try:
            payload = parse_shell_kv_file(profile)
            max_slot = max(max_slot, int(payload.get("PORT_SLOT", "-1")))
        except ValueError:
            continue

    slot = max_slot + 1
    api_port = block_base + slot * block_size
    worker_port = api_port + 1
    mock_port = api_port + 2
    grpc_port = api_port + 3
    body = "\n".join(
        [
            f"PORT_SLOT={slot}",
            f"API_PORT={api_port}",
            f"WORKER_PORT={worker_port}",
            f"AGENT_RUNTIME_MOCK_PORT={mock_port}",
            f"AGENT_RUNTIME_GRPC_PORT={grpc_port}",
            f"AGENT_RUNTIME_BASE_URL=http://localhost:{mock_port}",
            f"AGENT_RUNTIME_GRPC_TARGET=127.0.0.1:{grpc_port}",
            "",
        ]
    )
    target.write_text(body, encoding="utf-8")
    return _parse_port_assignment(target)


def _seed_worktree_env_if_needed(
    worktree_path: Path,
    change_id: str,
    port_profile: PortAssignment,
) -> str:
    env_path = worktree_path / ".env"
    if env_path.exists():
        return "existing"

    example_path = worktree_path / ".env.example"
    if not example_path.exists():
        return "missing_example"

    updates = {
        "API_PORT": str(port_profile.api_port),
        "WORKER_PORT": str(port_profile.worker_port),
        "AGENT_RUNTIME_MOCK_PORT": str(port_profile.agent_runtime_mock_port),
        "AGENT_RUNTIME_GRPC_PORT": str(port_profile.agent_runtime_grpc_port),
        "AGENT_RUNTIME_BASE_URL": port_profile.agent_runtime_base_url,
        "AGENT_RUNTIME_GRPC_TARGET": port_profile.agent_runtime_grpc_target,
    }

    lines = example_path.read_text(encoding="utf-8", errors="replace").splitlines()
    output = [
        f"# Auto-generated for worktree change {change_id} (port slot {port_profile.slot})",
        "# Shared infrastructure ports stay unchanged; local listener ports are isolated per worktree.",
    ]
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            output.append(line)
            continue
        key, _ = line.split("=", 1)
        key = key.strip()
        output.append(f"{key}={updates[key]}" if key in updates else line)

    env_path.write_text("\n".join(output) + "\n", encoding="utf-8")
    return "created"


def ensure_local_integration_branch(repo_root: Path, integration_branch: str) -> str:
    if ref_exists(repo_root, f"refs/heads/{integration_branch}"):
        return integration_branch

    remote_ref = f"origin/{integration_branch}"
    if ref_exists(repo_root, f"refs/remotes/{remote_ref}"):
        run_git(repo_root, "branch", "--track", integration_branch, remote_ref)
        return remote_ref

    for candidate in ("dev", "origin/dev", "master", "origin/master"):
        if candidate.startswith("origin/"):
            if ref_exists(repo_root, f"refs/remotes/{candidate}"):
                run_git(repo_root, "branch", integration_branch, candidate)
                return candidate
        elif ref_exists(repo_root, f"refs/heads/{candidate}"):
            run_git(repo_root, "branch", integration_branch, candidate)
            return candidate

    branch = current_branch(repo_root)
    base_ref = branch or "HEAD"
    run_git(repo_root, "branch", integration_branch, base_ref)
    return base_ref


def _prepare_series_branching(item: PreparationItem, repo_root: Path) -> None:
    if item.integration_branch in {None, "dev"}:
        return
    if item.tasks_path is None:
        raise PreparationError(f"Missing tasks.md for {item.change_id}")

    metadata = inspect_managed_git_tasks(
        item.tasks_path,
        item.change_id,
        item.implementation_branch or _default_implementation_branch(item.change_id),
        item.integration_branch,
    )
    item.implementation_branch = metadata.implementation_branch
    item.integration_branch = metadata.integration_branch
    item.managed_git = metadata.managed

    if not metadata.managed:
        raise PreparationError(
            f"{item.change_id} does not use the standardized auto-managed branch tasks"
        )

    created_from = ensure_local_integration_branch(repo_root, metadata.integration_branch)
    if created_from != metadata.integration_branch:
        item.notes.append(
            f"integration branch {metadata.integration_branch} prepared from {created_from}"
        )

    if ref_exists(repo_root, f"refs/heads/{metadata.implementation_branch}"):
        run_git(item.worktree_path or repo_root, "switch", metadata.implementation_branch)
        item.notes.append(f"switched worktree to {metadata.implementation_branch}")
    else:
        run_git(
            item.worktree_path or repo_root,
            "switch",
            "-c",
            metadata.implementation_branch,
            metadata.integration_branch,
        )
        item.notes.append(
            f"created implementation branch {metadata.implementation_branch}"
        )

    marked = mark_start_tasks(item.tasks_path, metadata)
    if marked:
        item.notes.append(f"marked {marked} auto-managed start task(s) complete")


def execute_preparation_session(
    session: PreparationSession,
    runtime_root: Path,
) -> None:
    pending_items = [
        item for item in session.items if item.prep_state == "pending_preparation"
    ]
    if not pending_items:
        return

    ensure_legacy_session_dir(
        session.workspace_root / "openspec" / "auto" / "logs",
        session_dir=session.legacy_session_dir,
        target_change_ids=[item.change_id for item in session.items],
        runtime_root=runtime_root,
    )

    for item in pending_items:
        item.prep_state = "preparing"
        item.started_at = datetime.now()
        append_event(
            runtime_root,
            "preparation_started",
            {
                "change_id": item.change_id,
                "series": item.series,
                "worktree_path": str(item.worktree_path) if item.worktree_path else None,
                "session_dir": str(session.legacy_session_dir),
            },
        )

        try:
            if item.worktree_path is None or item.base_ref is None:
                raise PreparationError(
                    f"Preparation target is incomplete for {item.change_id}"
                )

            outcome = _ensure_worktree(
                session.repo_root,
                session.worktree_root,
                item.worktree_path,
                item.base_ref,
            )
            item.notes.append(
                (
                    f"created worktree from {item.base_ref}"
                    if outcome == "created"
                    else f"reused worktree from {item.base_ref}"
                )
            )

            if not (item.worktree_path / "openspec").exists():
                raise PreparationError(
                    f"Missing openspec entry inside worktree {item.worktree_path}"
                )
            worktree_tasks_path = (
                item.worktree_path / "openspec" / "changes" / item.change_id / "tasks.md"
            )
            if worktree_tasks_path.exists():
                item.tasks_path = worktree_tasks_path
            elif item.tasks_path is not None:
                item.notes.append(
                    "worktree-local openspec change path is missing; using main workspace tasks.md"
                )

            port_profile = _ensure_port_profile(
                session.legacy_session_dir,
                item.change_id,
                block_base=session.port_block_base,
                block_size=session.port_block_size,
            )
            item.port_profile = port_profile
            item.port_profile_path = port_profile.source_path
            item.notes.append(
                "allocated ports "
                f"api={port_profile.api_port}, worker={port_profile.worker_port}, "
                f"mock={port_profile.agent_runtime_mock_port}, grpc={port_profile.agent_runtime_grpc_port}"
            )

            item.env_status = _seed_worktree_env_if_needed(
                item.worktree_path,
                item.change_id,
                port_profile,
            )
            if item.env_status == "created":
                item.notes.append("created .env from .env.example with isolated ports")
            elif item.env_status == "existing":
                item.notes.append("kept existing .env")
            else:
                item.notes.append("skipped .env creation because .env.example is missing")

            _prepare_series_branching(item, session.repo_root)

            item.prep_state = "prepared"
            item.reason = "worktree, ports, and branch context are ready"
        except (GitCommandError, PreparationError, ValueError) as error:
            item.prep_state = "failed_preparation"
            item.reason = str(error)
            write_legacy_result(
                workspace_root=session.workspace_root,
                session_key=session.session_key,
                change_id=item.change_id,
                status="failed",
                tasks_path=item.tasks_path,
                human_reason=item.reason,
                runtime_root=runtime_root,
            )
        finally:
            item.finished_at = datetime.now()
            append_event(
                runtime_root,
                "preparation_finished",
                {
                    "change_id": item.change_id,
                    "series": item.series,
                    "prep_state": item.prep_state,
                    "reason": item.reason,
                    "worktree_path": str(item.worktree_path)
                    if item.worktree_path
                    else None,
                    "port_profile_path": str(item.port_profile_path)
                    if item.port_profile_path
                    else None,
                },
            )
