from __future__ import annotations

import threading
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from openspec_py.launch_execution import execute_launch_item
from openspec_py.legacy_results import legacy_session_dir
from openspec_py.orchestrator import OrchestrationItem, OrchestrationSession
from openspec_py.preparation import PreparationSession
from openspec_py.runtime_logging import append_event
from openspec_py.session_store import SessionWriteResult, write_session_payload

PLACEHOLDER_MAP = {
    "__CHANGE_ID__": "change_id",
    "__CHANGE_PATH__": "change_path",
    "__WORKTREE_PATH__": "execution_path",
    "__EXECUTION_PATH__": "execution_path",
    "__WORKTREE_CHANGE_PATH__": "worktree_change_path",
    "__SERIES__": "series",
    "__STEP__": "step",
    "__NEXT_TASK__": "next_task",
    "__PORT_PROFILE__": "port_profile_path",
    "__IMPL_BRANCH__": "implementation_branch",
    "__INTEGRATION_BRANCH__": "integration_branch",
    "__ATTEMPT__": "attempt",
    "__TASKS_COMPLETED__": "tasks_completed",
    "__TASKS_TOTAL__": "tasks_total",
    "__MANUAL_COMPLETED__": "manual_completed",
    "__MANUAL_TOTAL__": "manual_total",
    "__TRANSCRIPT_FILE__": "transcript_file",
    "__TASK_SYNC_LOG__": "task_sync_log",
    "__ASSESSMENT_LOG__": "assessment_log",
    "__RETRY_GUIDANCE_FILE__": "retry_guidance_file",
}


@dataclass(slots=True)
class LaunchItem:
    change_id: str
    series: str
    step: int | None
    action: str
    plan_state: str
    current_status: str
    command: str | None
    change_path: Path
    tasks_path: Path | None
    execution_path: Path
    worktree_change_path: Path
    next_task: str | None
    run_state: str
    reason: str
    max_attempts: int
    preparation_state: str | None = None
    port_profile_path: Path | None = None
    implementation_branch: str | None = None
    integration_branch: str | None = None
    log_path: Path | None = None
    task_sync_log_path: Path | None = None
    assessment_log_path: Path | None = None
    retry_guidance_path: Path | None = None
    result_path: Path | None = None
    attempt: int = 0
    exit_code: int | None = None
    manual_completed: int = 0
    manual_total: int = 0
    full_completed: int = 0
    full_total: int = 0
    assessment_state: str | None = None
    assessment_reason: str | None = None
    assessment_next_action: str | None = None
    notes: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["change_path"] = str(self.change_path)
        payload["tasks_path"] = str(self.tasks_path) if self.tasks_path else None
        payload["execution_path"] = str(self.execution_path)
        payload["worktree_change_path"] = str(self.worktree_change_path)
        payload["port_profile_path"] = (
            str(self.port_profile_path) if self.port_profile_path else None
        )
        payload["log_path"] = str(self.log_path) if self.log_path else None
        payload["task_sync_log_path"] = (
            str(self.task_sync_log_path) if self.task_sync_log_path else None
        )
        payload["assessment_log_path"] = (
            str(self.assessment_log_path) if self.assessment_log_path else None
        )
        payload["retry_guidance_path"] = (
            str(self.retry_guidance_path) if self.retry_guidance_path else None
        )
        payload["result_path"] = str(self.result_path) if self.result_path else None
        payload["started_at"] = self.started_at.isoformat() if self.started_at else None
        payload["finished_at"] = self.finished_at.isoformat() if self.finished_at else None
        return payload


@dataclass(slots=True)
class LaunchSession:
    workspace_root: Path
    generated_at: datetime
    session_key: str
    dry_run: bool
    execute: bool
    max_parallel: int
    command_template: str
    task_sync_command_template: str | None
    assessment_command_template: str | None
    retry_limit: int
    used_preparation: bool
    legacy_session_dir: Path
    items: list[LaunchItem] = field(default_factory=list)

    @property
    def state_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.run_state] = counts.get(item.run_state, 0) + 1
        return dict(sorted(counts.items()))

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_root": str(self.workspace_root),
            "generated_at": self.generated_at.isoformat(),
            "session_key": self.session_key,
            "dry_run": self.dry_run,
            "execute": self.execute,
            "max_parallel": self.max_parallel,
            "command_template": self.command_template,
            "task_sync_command_template": self.task_sync_command_template,
            "assessment_command_template": self.assessment_command_template,
            "retry_limit": self.retry_limit,
            "used_preparation": self.used_preparation,
            "legacy_session_dir": str(self.legacy_session_dir),
            "state_counts": self.state_counts,
            "items": [item.to_dict() for item in self.items],
        }


def _render_command(template: str, values: dict[str, str]) -> str:
    rendered = template
    for placeholder, key in PLACEHOLDER_MAP.items():
        rendered = rendered.replace(placeholder, values[key])
    return rendered


def _prepared_lookup(
    preparation_session: PreparationSession | None,
) -> dict[str, object]:
    if preparation_session is None:
        return {}
    return {item.change_id: item for item in preparation_session.items}


def _worktree_change_path(
    execution_path: Path,
    change_id: str,
    fallback_change_path: Path,
) -> Path:
    candidate = execution_path / "openspec" / "changes" / change_id
    return candidate if candidate.exists() else fallback_change_path


def _tasks_path_for_launch_item(worktree_change_path: Path, change_path: Path) -> Path | None:
    candidate = worktree_change_path / "tasks.md"
    if candidate.exists():
        return candidate
    fallback = change_path / "tasks.md"
    return fallback if fallback.exists() else None


def _run_state_for_launch_item(
    item: OrchestrationItem,
    *,
    execute: bool,
    preparation_state: str | None,
) -> str:
    if item.action == "launch_now":
        if preparation_state == "failed_preparation":
            return "failed_preparation"
        if preparation_state == "prepared":
            return "pending_execution" if execute else "dry_run"
        if preparation_state == "dry_run":
            return "dry_run"
        return "pending_execution" if execute else "dry_run"
    if item.action == "keep_running":
        return "already_running"
    if item.action == "wait_capacity":
        return "waiting_capacity"
    if item.action == "wait_dependencies":
        return "waiting_dependencies"
    if item.action == "halted":
        return "halted"
    if item.action == "completed":
        return "completed"
    return "blocked"


def build_launch_session(
    orchestration: OrchestrationSession,
    *,
    command_template: str,
    execute: bool,
    retry_limit: int = 0,
    task_sync_command_template: str | None = None,
    assessment_command_template: str | None = None,
    preparation_session: PreparationSession | None = None,
) -> LaunchSession:
    items: list[LaunchItem] = []
    preparation_lookup = _prepared_lookup(preparation_session)
    legacy_dir = legacy_session_dir(orchestration.workspace_root, orchestration.session_key)

    for orchestration_item in orchestration.items:
        prepared_item = preparation_lookup.get(orchestration_item.change_id)
        change_path = orchestration_item.path
        execution_path = (
            prepared_item.worktree_path
            if prepared_item and prepared_item.worktree_path
            else change_path
        )
        worktree_change_path = _worktree_change_path(
            execution_path,
            orchestration_item.change_id,
            change_path,
        )
        tasks_path = _tasks_path_for_launch_item(worktree_change_path, change_path)
        preparation_state = prepared_item.prep_state if prepared_item else None
        run_state = _run_state_for_launch_item(
            orchestration_item,
            execute=execute,
            preparation_state=preparation_state,
        )
        values = {
            "change_id": orchestration_item.change_id,
            "change_path": str(change_path),
            "execution_path": str(execution_path),
            "worktree_change_path": str(worktree_change_path),
            "series": orchestration_item.series,
            "step": "" if orchestration_item.step is None else str(orchestration_item.step),
            "next_task": orchestration_item.next_task or "",
            "port_profile_path": (
                str(prepared_item.port_profile_path)
                if prepared_item and prepared_item.port_profile_path
                else ""
            ),
            "implementation_branch": (
                prepared_item.implementation_branch if prepared_item else ""
            )
            or "",
            "integration_branch": (
                prepared_item.integration_branch if prepared_item else ""
            )
            or "",
            "attempt": "1",
            "tasks_completed": "0",
            "tasks_total": "0",
            "manual_completed": "0",
            "manual_total": "0",
            "transcript_file": "",
            "task_sync_log": "",
            "assessment_log": "",
            "retry_guidance_file": "",
        }
        command = (
            _render_command(command_template, values)
            if orchestration_item.action == "launch_now"
            else None
        )

        items.append(
            LaunchItem(
                change_id=orchestration_item.change_id,
                series=orchestration_item.series,
                step=orchestration_item.step,
                action=orchestration_item.action,
                plan_state=orchestration_item.plan_state,
                current_status=orchestration_item.current_status,
                command=command,
                change_path=change_path,
                tasks_path=tasks_path,
                execution_path=execution_path,
                worktree_change_path=worktree_change_path,
                next_task=orchestration_item.next_task,
                run_state=run_state,
                reason=orchestration_item.reason,
                max_attempts=max(retry_limit, 0) + 1,
                preparation_state=preparation_state,
                port_profile_path=(
                    prepared_item.port_profile_path if prepared_item else None
                ),
                implementation_branch=(
                    prepared_item.implementation_branch if prepared_item else None
                ),
                integration_branch=(
                    prepared_item.integration_branch if prepared_item else None
                ),
            )
        )

    return LaunchSession(
        workspace_root=orchestration.workspace_root,
        generated_at=datetime.now(),
        session_key=orchestration.session_key,
        dry_run=not execute,
        execute=execute,
        max_parallel=orchestration.max_parallel,
        command_template=command_template,
        task_sync_command_template=task_sync_command_template,
        assessment_command_template=assessment_command_template,
        retry_limit=max(retry_limit, 0),
        used_preparation=preparation_session is not None,
        legacy_session_dir=legacy_dir,
        items=items,
    )


def write_launch_session(
    session: LaunchSession,
    output_path: Path,
    runtime_root: Path,
    *,
    event_name: str = "launch_session_written",
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
            "retry_limit": session.retry_limit,
            "used_preparation": session.used_preparation,
            "legacy_session_dir": str(session.legacy_session_dir),
        },
    )


def execute_launch_session(
    session: LaunchSession,
    runtime_root: Path,
) -> None:
    launch_logs_root = runtime_root / "launch-logs"
    launch_logs_root.mkdir(parents=True, exist_ok=True)
    pending_items = [item for item in session.items if item.run_state == "pending_execution"]
    if not pending_items:
        return

    max_workers = session.max_parallel if session.max_parallel > 0 else len(pending_items)
    max_workers = max(max_workers, 1)
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map: dict[Future[LaunchItem], LaunchItem] = {
            executor.submit(
                execute_launch_item,
                session,
                item,
                runtime_root,
                launch_logs_root,
                lock,
                _render_command,
            ): item
            for item in pending_items
        }
        for future in as_completed(future_map):
            item = future.result()
            append_event(
                runtime_root,
                "launch_finished",
                {
                    "change_id": item.change_id,
                    "series": item.series,
                    "attempt": item.attempt,
                    "exit_code": item.exit_code,
                    "run_state": item.run_state,
                    "execution_path": str(item.execution_path),
                    "log_path": str(item.log_path) if item.log_path else None,
                    "assessment_state": item.assessment_state,
                    "result_path": str(item.result_path) if item.result_path else None,
                },
            )
