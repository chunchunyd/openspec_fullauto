from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from openspec_py.git_tasks import inspect_managed_git_tasks
from openspec_py.legacy_results import write_legacy_result
from openspec_py.models import ChangeSnapshot, WorkspaceSnapshot
from openspec_py.openspec_cli import OpenSpecCommandError, archive_change, validate_change
from openspec_py.runtime_logging import append_event
from openspec_py.session_store import SessionWriteResult, write_session_payload

FINAL_ACTION_ORDER = [
    "ready_for_merge",
    "archive",
    "mark_success",
    "pending_tasks",
    "running",
    "wait_dependencies",
    "not_started",
    "archived",
    "halted",
]


@dataclass(slots=True)
class FinalizeItem:
    change_id: str
    series: str
    step: int | None
    current_status: str
    latest_result_status: str | None
    tasks_completed: int
    tasks_total: int
    manual_completed: int
    manual_total: int
    managed_git: bool
    archived: bool
    action: str
    outcome: str
    reason: str
    tasks_path: Path | None
    validation_ok: bool | None = None
    archive_applied: bool | None = None
    result_path: Path | None = None
    notes: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["tasks_path"] = str(self.tasks_path) if self.tasks_path else None
        payload["result_path"] = str(self.result_path) if self.result_path else None
        payload["started_at"] = self.started_at.isoformat() if self.started_at else None
        payload["finished_at"] = self.finished_at.isoformat() if self.finished_at else None
        return payload


@dataclass(slots=True)
class FinalizeSession:
    workspace_root: Path
    generated_at: datetime
    session_key: str
    execute: bool
    strict_validate: bool
    skip_validate: bool
    archive_enabled: bool
    items: list[FinalizeItem] = field(default_factory=list)

    @property
    def action_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.action] = counts.get(item.action, 0) + 1
        return dict(sorted(counts.items()))

    @property
    def outcome_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.outcome] = counts.get(item.outcome, 0) + 1
        return dict(sorted(counts.items()))

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_root": str(self.workspace_root),
            "generated_at": self.generated_at.isoformat(),
            "session_key": self.session_key,
            "execute": self.execute,
            "strict_validate": self.strict_validate,
            "skip_validate": self.skip_validate,
            "archive_enabled": self.archive_enabled,
            "action_counts": self.action_counts,
            "outcome_counts": self.outcome_counts,
            "items": [item.to_dict() for item in self.items],
        }


def _derive_session_key(changes: list[ChangeSnapshot]) -> str:
    series = sorted({change.series for change in changes})
    if not series:
        return "empty-finalize"
    if len(series) == 1:
        return series[0]
    if len(series) <= 4:
        return "__".join(series)
    return f"multi-{len(series)}-series"


def _managed_git(change: ChangeSnapshot) -> bool:
    tasks_path = change.tasks_path
    if tasks_path is None or not tasks_path.exists():
        return False
    default_impl = f"feat/{change.change_id}"
    default_integ = f"series/{change.series}" if change.step is not None else "dev"
    metadata = inspect_managed_git_tasks(
        tasks_path,
        change.change_id,
        default_impl,
        default_integ,
    )
    return metadata.managed


def _classify_item(
    change: ChangeSnapshot,
    *,
    archive_enabled: bool,
) -> tuple[str, str]:
    latest_status = change.latest_result.status if change.latest_result else None
    tasks_completed = change.tasks.full_completed
    tasks_total = change.tasks.full_total
    manual_completed = change.tasks.manual_completed
    manual_total = change.tasks.manual_total
    managed_git = _managed_git(change)
    archived = bool(change.archived_in_changes or (change.latest_result and change.latest_result.archived))

    if archived:
        return "archived", "change is already archived"
    if change.status in {"failed", "needs_human"}:
        return "halted", "change currently requires recovery before finalization"
    if latest_status == "running":
        return "running", "command is still running; wait before validation or archive"
    if change.unmet_dependencies:
        return "wait_dependencies", "downstream change is still waiting on unresolved dependencies"
    if latest_status is None and change.status == "pending":
        return "not_started", "change has not started yet"
    if managed_git:
        if manual_total <= 0:
            return "ready_for_merge", "non-git tasks are complete and the change should move into the merge queue"
        if manual_completed < manual_total:
            return "pending_tasks", "manual tasks in tasks.md still have unchecked items"
        return "ready_for_merge", "tasks are complete and the change should move into the merge queue"
    if tasks_total <= 0 or tasks_completed < tasks_total:
        return "pending_tasks", "tasks.md still has unchecked items"
    if archive_enabled:
        return "archive", "tasks are complete and the change can be archived after validation"
    return "mark_success", "tasks are complete; mark the change successful without archiving"


def build_finalize_session(
    snapshot: WorkspaceSnapshot,
    *,
    execute: bool,
    strict_validate: bool,
    skip_validate: bool,
    archive_enabled: bool,
) -> FinalizeSession:
    changes = [change for series in snapshot.series for change in series.changes]
    items: list[FinalizeItem] = []

    for change in changes:
        managed_git = _managed_git(change)
        archived = bool(
            change.archived_in_changes
            or (change.latest_result.archived if change.latest_result else False)
        )
        action, reason = _classify_item(change, archive_enabled=archive_enabled)
        outcome = "planned" if execute else "dry_run"
        if action in {"archived", "halted", "wait_dependencies", "not_started", "running", "pending_tasks"}:
            outcome = "no_action"

        items.append(
            FinalizeItem(
                change_id=change.change_id,
                series=change.series,
                step=change.step,
                current_status=change.status,
                latest_result_status=change.latest_result.status if change.latest_result else None,
                tasks_completed=change.tasks.full_completed,
                tasks_total=change.tasks.full_total,
                manual_completed=change.tasks.manual_completed,
                manual_total=change.tasks.manual_total,
                managed_git=managed_git,
                archived=archived,
                action=action,
                outcome=outcome,
                reason=reason,
                tasks_path=change.tasks_path,
            )
        )

    items.sort(
        key=lambda item: (
            FINAL_ACTION_ORDER.index(item.action)
            if item.action in FINAL_ACTION_ORDER
            else len(FINAL_ACTION_ORDER),
            item.series,
            item.step if item.step is not None else 9999,
            item.change_id,
        )
    )

    return FinalizeSession(
        workspace_root=snapshot.workspace_root,
        generated_at=datetime.now(),
        session_key=_derive_session_key(changes),
        execute=execute,
        strict_validate=strict_validate,
        skip_validate=skip_validate,
        archive_enabled=archive_enabled,
        items=items,
    )


def write_finalize_session(
    session: FinalizeSession,
    output_path: Path,
    runtime_root: Path,
    *,
    event_name: str = "finalize_written",
) -> SessionWriteResult:
    return write_session_payload(
        session.to_dict(),
        output_path,
        runtime_root,
        event_name,
        {
            "session_key": session.session_key,
            "item_count": len(session.items),
            "action_counts": session.action_counts,
            "outcome_counts": session.outcome_counts,
            "execute": session.execute,
            "strict_validate": session.strict_validate,
            "skip_validate": session.skip_validate,
            "archive_enabled": session.archive_enabled,
        },
    )


def execute_finalize_session(
    session: FinalizeSession,
    runtime_root: Path,
) -> None:
    actionable = {
        "ready_for_merge",
        "archive",
        "mark_success",
    }

    for item in session.items:
        if item.action not in actionable:
            continue

        item.started_at = datetime.now()
        append_event(
            runtime_root,
            "finalize_started",
            {
                "change_id": item.change_id,
                "series": item.series,
                "action": item.action,
            },
        )

        try:
            if not session.skip_validate:
                validation = validate_change(
                    session.workspace_root,
                    item.change_id,
                    strict=session.strict_validate,
                )
                item.validation_ok = validation.ok
                if not validation.ok:
                    item.outcome = "validation_failed"
                    item.reason = "OpenSpec validation failed"
                    record = write_legacy_result(
                        workspace_root=session.workspace_root,
                        session_key=session.session_key,
                        change_id=item.change_id,
                        status="failed",
                        tasks_path=item.tasks_path,
                        human_reason=item.reason,
                        runtime_root=runtime_root,
                    )
                    item.result_path = record.path
                    continue
                item.notes.append("validation passed")

            if item.action == "ready_for_merge":
                record = write_legacy_result(
                    workspace_root=session.workspace_root,
                    session_key=session.session_key,
                    change_id=item.change_id,
                    status="ready_for_merge",
                    tasks_path=item.tasks_path,
                    runtime_root=runtime_root,
                )
                item.result_path = record.path
                item.outcome = "ready_for_merge_written"
                item.reason = "validation passed and the change is now queued for merge"
            elif item.action == "archive":
                archive_change(session.workspace_root, item.change_id)
                item.archive_applied = True
                record = write_legacy_result(
                    workspace_root=session.workspace_root,
                    session_key=session.session_key,
                    change_id=item.change_id,
                    status="success",
                    tasks_path=item.tasks_path,
                    archived=True,
                    runtime_root=runtime_root,
                    completed_tasks=item.tasks_completed,
                    total_tasks=item.tasks_total,
                )
                item.result_path = record.path
                item.outcome = "archived"
                item.reason = "validation passed and the change was archived"
            else:
                record = write_legacy_result(
                    workspace_root=session.workspace_root,
                    session_key=session.session_key,
                    change_id=item.change_id,
                    status="success",
                    tasks_path=item.tasks_path,
                    archived=False,
                    runtime_root=runtime_root,
                )
                item.result_path = record.path
                item.outcome = "success_written"
                item.reason = "validation passed and success state was written"

        except OpenSpecCommandError as error:
            item.outcome = "failed"
            item.reason = str(error)
            record = write_legacy_result(
                workspace_root=session.workspace_root,
                session_key=session.session_key,
                change_id=item.change_id,
                status="failed",
                tasks_path=item.tasks_path,
                human_reason=item.reason,
                runtime_root=runtime_root,
            )
            item.result_path = record.path
        finally:
            item.finished_at = datetime.now()
            append_event(
                runtime_root,
                "finalize_finished",
                {
                    "change_id": item.change_id,
                    "series": item.series,
                    "action": item.action,
                    "outcome": item.outcome,
                    "reason": item.reason,
                    "result_path": str(item.result_path) if item.result_path else None,
                },
            )
