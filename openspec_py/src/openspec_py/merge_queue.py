from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from openspec_py.git_ops import (
    GitCommandError,
    branch_is_ancestor,
    current_branch,
    current_head,
    delete_branch,
    git_path_exists,
    ref_exists,
    remove_worktree,
    run_git,
    worktree_holders_for_branch,
)
from openspec_py.git_tasks import inspect_managed_git_tasks, mark_merge_tasks
from openspec_py.legacy_results import legacy_session_dir, write_legacy_result
from openspec_py.models import ChangeSnapshot, WorkspaceSnapshot
from openspec_py.openspec_cli import OpenSpecCommandError, archive_change
from openspec_py.parsers import parse_tasks_summary
from openspec_py.preparation import default_worktree_root, ensure_local_integration_branch
from openspec_py.runtime_logging import append_event
from openspec_py.session_store import SessionWriteResult, write_session_payload

MERGE_ACTION_ORDER = [
    "merge_now",
    "waiting_ready_for_merge",
    "halted",
    "archived",
    "not_series",
]

PLACEHOLDER_MAP = {
    "__CHANGE_ID__": "change_id",
    "__SERIES__": "series",
    "__STEP__": "step",
    "__WORKTREE_PATH__": "worktree_path",
    "__EXECUTION_PATH__": "worktree_path",
    "__TASKS_PATH__": "tasks_path",
    "__IMPL_BRANCH__": "implementation_branch",
    "__INTEGRATION_BRANCH__": "integration_branch",
    "__HANDOFF_LOG__": "handoff_log_path",
    "__MERGE_LOG__": "merge_log_path",
    "__MERGE_COMMIT_MESSAGE__": "merge_commit_message",
}


@dataclass(slots=True)
class MergeQueueItem:
    change_id: str
    series: str
    step: int | None
    current_status: str
    latest_result_status: str | None
    action: str
    outcome: str
    reason: str
    implementation_branch: str | None
    integration_branch: str | None
    worktree_path: Path | None
    tasks_path: Path | None
    merge_log_path: Path | None = None
    handoff_state: str | None = None
    handoff_log_path: Path | None = None
    merge_recovery_state: str | None = None
    branch_cleanup_state: str | None = None
    branch_cleanup_log_path: Path | None = None
    worktree_cleanup_state: str | None = None
    worktree_cleanup_log_path: Path | None = None
    result_path: Path | None = None
    notes: list[str] = field(default_factory=list)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["worktree_path"] = str(self.worktree_path) if self.worktree_path else None
        payload["tasks_path"] = str(self.tasks_path) if self.tasks_path else None
        payload["merge_log_path"] = str(self.merge_log_path) if self.merge_log_path else None
        payload["handoff_log_path"] = (
            str(self.handoff_log_path) if self.handoff_log_path else None
        )
        payload["branch_cleanup_log_path"] = (
            str(self.branch_cleanup_log_path) if self.branch_cleanup_log_path else None
        )
        payload["worktree_cleanup_log_path"] = (
            str(self.worktree_cleanup_log_path)
            if self.worktree_cleanup_log_path
            else None
        )
        payload["result_path"] = str(self.result_path) if self.result_path else None
        payload["started_at"] = self.started_at.isoformat() if self.started_at else None
        payload["finished_at"] = self.finished_at.isoformat() if self.finished_at else None
        return payload


@dataclass(slots=True)
class MergeQueueSession:
    workspace_root: Path
    generated_at: datetime
    session_key: str
    execute: bool
    archive_enabled: bool
    cleanup_worktrees: bool
    handoff_command_template: str | None
    merge_fallback_command_template: str | None
    worktree_root: Path
    legacy_session_dir: Path
    items: list[MergeQueueItem] = field(default_factory=list)

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
            "archive_enabled": self.archive_enabled,
            "cleanup_worktrees": self.cleanup_worktrees,
            "handoff_command_template": self.handoff_command_template,
            "merge_fallback_command_template": self.merge_fallback_command_template,
            "worktree_root": str(self.worktree_root),
            "legacy_session_dir": str(self.legacy_session_dir),
            "action_counts": self.action_counts,
            "outcome_counts": self.outcome_counts,
            "items": [item.to_dict() for item in self.items],
        }


def _derive_session_key(changes: list[ChangeSnapshot]) -> str:
    series = sorted({change.series for change in changes})
    if not series:
        return "empty-merge-queue"
    if len(series) == 1:
        return series[0]
    if len(series) <= 4:
        return "__".join(series)
    return f"multi-{len(series)}-series"


def _metadata(change: ChangeSnapshot):
    tasks_path = change.tasks_path
    if tasks_path is None or not tasks_path.exists():
        return None
    default_impl = f"feat/{change.change_id}"
    default_integ = f"series/{change.series}" if change.step is not None else "dev"
    return inspect_managed_git_tasks(
        tasks_path,
        change.change_id,
        default_impl,
        default_integ,
    )


def _action_for_change(change: ChangeSnapshot) -> tuple[str, str]:
    metadata = _metadata(change)
    if metadata is None or not metadata.managed:
        return "not_series", "change does not use managed series merge tasks"
    if change.archived_in_changes or (change.latest_result and change.latest_result.archived):
        return "archived", "change is already archived"
    if change.status in {"failed", "needs_human"}:
        return "halted", "change currently needs human recovery before merge"
    latest_status = change.latest_result.status if change.latest_result else None
    if latest_status == "ready_for_merge":
        return "merge_now", "queued for parent-managed merge"
    return "waiting_ready_for_merge", "waiting for finalize to write ready_for_merge"


def build_merge_queue_session(
    snapshot: WorkspaceSnapshot,
    *,
    execute: bool,
    archive_enabled: bool,
    cleanup_worktrees: bool,
    handoff_command_template: str | None,
    merge_fallback_command_template: str | None,
) -> MergeQueueSession:
    changes = [change for series in snapshot.series for change in series.changes]
    session_key = _derive_session_key(changes)
    worktree_root = default_worktree_root(snapshot.workspace_root)
    session_dir = legacy_session_dir(snapshot.workspace_root, session_key)
    items: list[MergeQueueItem] = []

    for change in changes:
        metadata = _metadata(change)
        action, reason = _action_for_change(change)
        outcome = "planned" if execute and action == "merge_now" else "no_action"
        worktree_path = (
            worktree_root / change.change_id if metadata and metadata.managed else None
        )
        items.append(
            MergeQueueItem(
                change_id=change.change_id,
                series=change.series,
                step=change.step,
                current_status=change.status,
                latest_result_status=change.latest_result.status
                if change.latest_result
                else None,
                action=action,
                outcome=outcome,
                reason=reason,
                implementation_branch=metadata.implementation_branch if metadata else None,
                integration_branch=metadata.integration_branch if metadata else None,
                worktree_path=worktree_path,
                tasks_path=change.tasks_path,
            )
        )

    items.sort(
        key=lambda item: (
            MERGE_ACTION_ORDER.index(item.action)
            if item.action in MERGE_ACTION_ORDER
            else len(MERGE_ACTION_ORDER),
            next(
                (
                    change.latest_result.transition_at
                    for change in changes
                    if change.change_id == item.change_id
                    and change.latest_result
                    and change.latest_result.transition_at is not None
                ),
                0,
            ),
            item.series,
            item.step if item.step is not None else 9999,
            item.change_id,
        )
    )

    return MergeQueueSession(
        workspace_root=snapshot.workspace_root,
        generated_at=datetime.now(),
        session_key=session_key,
        execute=execute,
        archive_enabled=archive_enabled,
        cleanup_worktrees=cleanup_worktrees,
        handoff_command_template=handoff_command_template,
        merge_fallback_command_template=merge_fallback_command_template,
        worktree_root=worktree_root,
        legacy_session_dir=session_dir,
        items=items,
    )


def write_merge_queue_session(
    session: MergeQueueSession,
    output_path: Path,
    runtime_root: Path,
    *,
    event_name: str = "merge_queue_written",
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
            "archive_enabled": session.archive_enabled,
            "cleanup_worktrees": session.cleanup_worktrees,
            "handoff_command_enabled": bool(session.handoff_command_template),
            "merge_fallback_enabled": bool(session.merge_fallback_command_template),
        },
    )


def _status_porcelain(repo: Path) -> list[str]:
    completed = run_git(
        repo,
        "status",
        "--porcelain",
        "--untracked-files=normal",
        check=False,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _tasks_path_for_merge(item: MergeQueueItem) -> Path | None:
    if item.worktree_path is None:
        return item.tasks_path
    candidate = item.worktree_path / "openspec" / "changes" / item.change_id / "tasks.md"
    if candidate.exists():
        return candidate
    return item.tasks_path


def _write_merge_log(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_log_note(path: Path, note: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {note}\n")


def _render_command(template: str, values: dict[str, str]) -> str:
    rendered = template
    for placeholder, key in PLACEHOLDER_MAP.items():
        rendered = rendered.replace(placeholder, values[key])
    return rendered


def _run_shell_command_append(
    command: str,
    *,
    cwd: Path,
    log_path: Path,
    metadata_lines: list[str],
) -> subprocess.CompletedProcess[str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        for line in metadata_lines:
            handle.write(f"{line}\n")
        handle.write("\n")
        handle.flush()
        return subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            stdout=handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )


def _unmerged_paths(repo: Path) -> list[str]:
    completed = run_git(repo, "diff", "--name-only", "--diff-filter=U", check=False)
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _has_pending_parent_managed_merge_state(
    worktree_path: Path,
    integration_branch: str,
) -> bool:
    if current_branch(worktree_path) != integration_branch:
        return False
    if _unmerged_paths(worktree_path):
        return True
    return any(
        git_path_exists(worktree_path, marker)
        for marker in ("MERGE_HEAD", "SQUASH_MSG", "MERGE_MSG", "AUTO_MERGE")
    )


def _switch_worktree_branch(
    session: MergeQueueSession,
    item: MergeQueueItem,
    branch: str,
    *,
    log_path: Path,
) -> None:
    if item.worktree_path is None:
        raise RuntimeError("isolated worktree is missing")
    completed = run_git(item.worktree_path, "switch", branch, check=False)
    if completed.returncode == 0:
        _append_log_note(log_path, f"Switched worktree to {branch}")
        return

    holders = [
        str(path)
        for path in worktree_holders_for_branch(session.workspace_root, branch)
        if item.worktree_path is None or path.resolve() != item.worktree_path.resolve()
    ]
    if holders:
        raise RuntimeError(
            f"failed to switch worktree to {branch}; branch is checked out by {', '.join(holders)}"
        )
    detail = completed.stderr.strip() or completed.stdout.strip() or f"exit={completed.returncode}"
    raise RuntimeError(f"failed to switch worktree to {branch}: {detail}")


def _ensure_clean_implementation_handoff(
    session: MergeQueueSession,
    item: MergeQueueItem,
    runtime_root: Path,
) -> tuple[bool, str | None, str | None]:
    item.handoff_log_path = (
        session.legacy_session_dir / f"{item.change_id}.attempt-queue.handoff.log"
    )
    log_path = item.handoff_log_path
    _write_merge_log(log_path, [])

    impl = item.implementation_branch
    integ = item.integration_branch
    if item.worktree_path is None or impl is None or integ is None:
        item.handoff_state = "missing_metadata"
        return False, "implementation handoff metadata is incomplete", None

    if not ref_exists(session.workspace_root, f"refs/heads/{impl}"):
        item.handoff_state = "implementation_missing"
        _append_log_note(log_path, f"Implementation branch {impl} is missing")
        return (
            False,
            f"implementation branch {impl} is missing before merge",
            f"Inspect {item.worktree_path} and recreate or restore {impl} before rerunning merge-queue.",
        )

    try:
        _switch_worktree_branch(session, item, impl, log_path=log_path)
    except RuntimeError as error:
        item.handoff_state = "switch_failed"
        _append_log_note(log_path, str(error))
        return (
            False,
            str(error),
            f"Inspect {item.worktree_path} and release {impl} if it is occupied elsewhere before rerunning merge-queue.",
        )

    status_lines = _status_porcelain(item.worktree_path)
    if not status_lines:
        item.handoff_state = "clean"
        _append_log_note(log_path, f"Implementation branch {impl} is already clean for parent-managed merge")
        return True, None, None

    item.handoff_state = "dirty"
    _append_log_note(log_path, f"Implementation branch {impl} still has local changes before parent-managed merge")
    for line in status_lines:
        _append_log_note(log_path, line)

    if not session.handoff_command_template:
        return (
            False,
            f"implementation branch {impl} was not handed off cleanly before merge",
            f"Inspect {item.worktree_path} and {log_path}, clean up or commit the remaining implementation work on {impl}, and rerun merge-queue.",
        )

    command = _render_command(
        session.handoff_command_template,
        {
            "change_id": item.change_id,
            "series": item.series,
            "step": "" if item.step is None else str(item.step),
            "worktree_path": str(item.worktree_path),
            "tasks_path": str(item.tasks_path) if item.tasks_path else "",
            "implementation_branch": impl,
            "integration_branch": integ,
            "handoff_log_path": str(log_path),
        },
    )
    append_event(
        runtime_root,
        "merge_queue_handoff_started",
        {
            "change_id": item.change_id,
            "series": item.series,
            "command": command,
            "handoff_log_path": str(log_path),
        },
    )
    completed = _run_shell_command_append(
        command,
        cwd=item.worktree_path,
        log_path=log_path,
        metadata_lines=[
            f"command={command}",
            f"change_id={item.change_id}",
            f"implementation_branch={impl}",
            f"integration_branch={integ}",
        ],
    )
    if completed.returncode != 0:
        item.handoff_state = "cleanup_failed"
        _append_log_note(log_path, f"Handoff cleanup command failed with exit {completed.returncode}")
        return (
            False,
            f"implementation handoff cleanup failed for {item.change_id}; inspect {log_path}",
            f"Inspect {item.worktree_path} and {log_path}, clean up or commit the remaining implementation work on {impl}, and rerun merge-queue.",
        )

    current = current_branch(item.worktree_path)
    if current != impl:
        item.handoff_state = "wrong_branch"
        _append_log_note(log_path, f"Handoff cleanup left the worktree on {current or 'detached'} instead of {impl}")
        return (
            False,
            f"implementation handoff cleanup did not leave the worktree on {impl}",
            f"Return {item.worktree_path} to {impl}, verify the implementation work is committed, and rerun merge-queue.",
        )

    remaining = _status_porcelain(item.worktree_path)
    if remaining:
        item.handoff_state = "dirty_preserved"
        _append_log_note(log_path, "Implementation handoff cleanup did not leave the branch clean")
        for line in remaining:
            _append_log_note(log_path, line)
        return (
            False,
            f"implementation handoff cleanup did not leave {impl} clean",
            f"Inspect {item.worktree_path} and {log_path}, clean up or commit the remaining implementation work on {impl}, and rerun merge-queue.",
        )

    item.handoff_state = "cleaned"
    item.notes.append(f"handoff cleanup left {impl} clean for merge")
    _append_log_note(log_path, "Implementation handoff cleanup completed successfully")
    return True, None, None


def _merge_fallback_completed(
    worktree_path: Path,
    integration_branch: str,
    initial_head: str | None,
) -> bool:
    if current_branch(worktree_path) != integration_branch:
        return False
    if _unmerged_paths(worktree_path):
        return False
    if _status_porcelain(worktree_path):
        return False
    head = current_head(worktree_path)
    return bool(head and initial_head and head != initial_head)


def _run_merge_fallback(
    session: MergeQueueSession,
    item: MergeQueueItem,
    runtime_root: Path,
    *,
    initial_head: str | None,
    resume_existing_merge: bool,
) -> tuple[bool, str | None, str | None]:
    if item.worktree_path is None or item.integration_branch is None or item.merge_log_path is None:
        return False, "merge fallback metadata is incomplete", None

    if not session.merge_fallback_command_template:
        item.merge_recovery_state = "not_configured"
        if resume_existing_merge:
            return (
                False,
                "worktree already has an unresolved parent-managed merge state",
                (
                    f"Inspect {item.worktree_path}, finish or abort the in-progress merge on "
                    f"{item.integration_branch}, and rerun merge-queue."
                ),
            )
        return (
            False,
            f"direct merge failed for {item.change_id}; inspect {item.merge_log_path}",
            (
                f"Inspect {item.worktree_path}, resolve the merge on "
                f"{item.integration_branch}, and rerun merge-queue."
            ),
        )

    command = _render_command(
        session.merge_fallback_command_template,
        {
            "change_id": item.change_id,
            "series": item.series,
            "step": "" if item.step is None else str(item.step),
            "worktree_path": str(item.worktree_path),
            "tasks_path": str(item.tasks_path) if item.tasks_path else "",
            "implementation_branch": item.implementation_branch or "",
            "integration_branch": item.integration_branch,
            "handoff_log_path": str(item.handoff_log_path) if item.handoff_log_path else "",
            "merge_log_path": str(item.merge_log_path),
            "merge_commit_message": item.change_id,
        },
    )
    item.merge_recovery_state = "running"
    _append_log_note(
        item.merge_log_path,
        "Launching merge fallback command to continue the in-place merge"
        if resume_existing_merge
        else "Direct merge failed; launching merge fallback command",
    )
    append_event(
        runtime_root,
        "merge_queue_fallback_started",
        {
            "change_id": item.change_id,
            "series": item.series,
            "resume_existing_merge": resume_existing_merge,
            "command": command,
            "merge_log_path": str(item.merge_log_path),
        },
    )
    completed = _run_shell_command_append(
        command,
        cwd=item.worktree_path,
        log_path=item.merge_log_path,
        metadata_lines=[
            f"command={command}",
            f"change_id={item.change_id}",
            f"implementation_branch={item.implementation_branch or ''}",
            f"integration_branch={item.integration_branch}",
            f"resume_existing_merge={int(resume_existing_merge)}",
        ],
    )
    if completed.returncode != 0:
        item.merge_recovery_state = "failed"
        _append_log_note(
            item.merge_log_path,
            f"Merge fallback command failed with exit {completed.returncode}",
        )
        return (
            False,
            f"merge fallback command failed for {item.change_id}; inspect {item.merge_log_path}",
            (
                f"Inspect {item.worktree_path} and {item.merge_log_path}, resolve the merge on "
                f"{item.integration_branch}, and rerun merge-queue."
            ),
        )

    if not _merge_fallback_completed(
        item.worktree_path,
        item.integration_branch,
        initial_head,
    ):
        item.merge_recovery_state = "incomplete"
        _append_log_note(
            item.merge_log_path,
            "Merge fallback command did not leave a completed clean merge state",
        )
        return (
            False,
            f"merge fallback command did not complete the merge for {item.change_id}",
            (
                f"Inspect {item.worktree_path} and {item.merge_log_path}, finish the merge on "
                f"{item.integration_branch}, and rerun merge-queue."
            ),
        )

    item.merge_recovery_state = "recovered"
    item.notes.append("merge fallback completed the in-place merge")
    _append_log_note(item.merge_log_path, "Merge fallback completed the merge successfully")
    return True, None, None


def _write_needs_human_result(
    session: MergeQueueSession,
    item: MergeQueueItem,
    tasks_path: Path | None,
    runtime_root: Path,
    *,
    reason: str,
    next_action: str,
    completed_tasks: int | None = None,
    total_tasks: int | None = None,
) -> None:
    record = write_legacy_result(
        workspace_root=session.workspace_root,
        session_key=session.session_key,
        change_id=item.change_id,
        status="needs_human",
        tasks_path=tasks_path,
        requires_human=True,
        human_reason=reason,
        human_next_action=next_action,
        runtime_root=runtime_root,
        completed_tasks=completed_tasks,
        total_tasks=total_tasks,
    )
    item.result_path = record.path
    item.outcome = "needs_human"
    item.reason = reason


def _cleanup_implementation_branch(
    session: MergeQueueSession,
    item: MergeQueueItem,
) -> None:
    item.branch_cleanup_log_path = (
        session.legacy_session_dir / f"{item.change_id}.branch-cleanup.log"
    )
    log_path = item.branch_cleanup_log_path
    impl = item.implementation_branch
    integ = item.integration_branch

    _append_log_note(
        log_path,
        f"Attempting implementation branch cleanup for {impl or 'unknown'} after successful archive",
    )

    if not impl or not integ:
        item.branch_cleanup_state = "missing_metadata"
        _append_log_note(log_path, "Skipping cleanup because branch metadata is incomplete")
        return

    if not ref_exists(session.workspace_root, f"refs/heads/{impl}"):
        item.branch_cleanup_state = "already_absent"
        _append_log_note(log_path, f"Implementation branch {impl} is already absent")
        return

    if not ref_exists(session.workspace_root, f"refs/heads/{integ}"):
        item.branch_cleanup_state = "integration_missing"
        _append_log_note(
            log_path,
            f"Integration branch {integ} is missing; cannot verify branch ancestry for {impl}",
        )
        item.notes.append(f"kept {impl} because integration branch {integ} is missing")
        return

    holders = [str(path) for path in worktree_holders_for_branch(session.workspace_root, impl)]
    if holders:
        item.branch_cleanup_state = "held_by_worktree"
        _append_log_note(
            log_path,
            f"Implementation branch {impl} is still checked out by: {', '.join(holders)}",
        )
        item.notes.append(
            f"kept {impl} because it is still checked out by {', '.join(holders)}"
        )
        return

    if not branch_is_ancestor(session.workspace_root, impl, integ):
        item.branch_cleanup_state = "not_merged"
        _append_log_note(
            log_path,
            f"Implementation branch {impl} is not an ancestor of {integ}; refusing to delete it",
        )
        item.notes.append(f"kept {impl} because it is not fully merged into {integ}")
        return

    delete_branch(session.workspace_root, impl, force=True)
    item.branch_cleanup_state = "deleted"
    _append_log_note(log_path, f"Deleted merged implementation branch {impl}")
    item.notes.append(f"deleted merged implementation branch {impl}")


def _cleanup_worktree(
    session: MergeQueueSession,
    item: MergeQueueItem,
) -> None:
    item.worktree_cleanup_log_path = session.legacy_session_dir / f"{item.change_id}.cleanup.log"
    log_path = item.worktree_cleanup_log_path

    if item.worktree_path is None:
        item.worktree_cleanup_state = "missing_worktree"
        _append_log_note(
            log_path,
            "Skipping worktree cleanup because no worktree path is recorded",
        )
        return

    if not item.worktree_path.exists():
        item.worktree_cleanup_state = "already_removed"
        _append_log_note(log_path, f"Worktree is already absent: {item.worktree_path}")
        return

    _append_log_note(log_path, f"Attempting direct git worktree remove for {item.worktree_path}")
    status_lines = _status_porcelain(item.worktree_path)
    if status_lines:
        item.worktree_cleanup_state = "dirty_preserved"
        _append_log_note(
            log_path,
            "Skipping worktree removal because uncommitted changes are still present",
        )
        for line in status_lines:
            _append_log_note(log_path, line)
        item.notes.append(
            f"preserved worktree {item.worktree_path} because it still has local changes"
        )
        return

    remove_worktree(session.workspace_root, item.worktree_path)
    item.worktree_cleanup_state = "removed"
    _append_log_note(log_path, f"Removed isolated worktree {item.worktree_path}")
    item.notes.append(f"removed isolated worktree {item.worktree_path}")


def _run_post_archive_cleanup(
    session: MergeQueueSession,
    item: MergeQueueItem,
) -> None:
    try:
        _cleanup_implementation_branch(session, item)
    except GitCommandError as error:
        item.branch_cleanup_state = "failed"
        if item.branch_cleanup_log_path is None:
            item.branch_cleanup_log_path = (
                session.legacy_session_dir / f"{item.change_id}.branch-cleanup.log"
            )
        _append_log_note(item.branch_cleanup_log_path, str(error))
        item.notes.append(f"branch cleanup failed: {error}")

    if not session.cleanup_worktrees:
        return

    try:
        _cleanup_worktree(session, item)
    except GitCommandError as error:
        item.worktree_cleanup_state = "failed"
        if item.worktree_cleanup_log_path is None:
            item.worktree_cleanup_log_path = (
                session.legacy_session_dir / f"{item.change_id}.cleanup.log"
            )
        _append_log_note(item.worktree_cleanup_log_path, str(error))
        item.notes.append(f"worktree cleanup failed: {error}")


def execute_merge_queue_session(
    session: MergeQueueSession,
    runtime_root: Path,
) -> None:
    for item in session.items:
        if item.action != "merge_now":
            continue

        item.started_at = datetime.now()
        item.merge_log_path = session.legacy_session_dir / f"{item.change_id}.merge.log"
        append_event(
            runtime_root,
            "merge_queue_started",
            {
                "change_id": item.change_id,
                "series": item.series,
                "worktree_path": str(item.worktree_path) if item.worktree_path else None,
                "handoff_command_enabled": bool(session.handoff_command_template),
                "merge_fallback_enabled": bool(session.merge_fallback_command_template),
            },
        )

        tasks_path: Path | None = None
        try:
            if item.worktree_path is None or not item.worktree_path.exists():
                raise RuntimeError("isolated worktree is missing")
            if item.implementation_branch is None or item.integration_branch is None:
                raise RuntimeError("managed branch metadata is missing")

            tasks_path = _tasks_path_for_merge(item)
            if tasks_path is None or not tasks_path.exists():
                raise RuntimeError("tasks.md is missing for this change")

            merge_logs = [
                f"change_id={item.change_id}",
                f"worktree_path={item.worktree_path}",
                f"implementation_branch={item.implementation_branch}",
                f"integration_branch={item.integration_branch}",
            ]
            resume_existing_merge = _has_pending_parent_managed_merge_state(
                item.worktree_path,
                item.integration_branch,
            )

            if resume_existing_merge:
                merge_logs.append("pending_merge_state=1")
                merge_logs.append("resume_existing_merge=1")
                _write_merge_log(item.merge_log_path, merge_logs)
                initial_head = current_head(item.worktree_path)
                recovered, recovery_reason, recovery_next_action = _run_merge_fallback(
                    session,
                    item,
                    runtime_root,
                    initial_head=initial_head,
                    resume_existing_merge=True,
                )
                if not recovered:
                    _write_needs_human_result(
                        session,
                        item,
                        tasks_path,
                        runtime_root,
                        reason=recovery_reason or "merge fallback did not complete successfully",
                        next_action=recovery_next_action
                        or (
                            f"Inspect {item.worktree_path}, finish or abort the in-progress "
                            f"merge on {item.integration_branch}, and rerun merge-queue."
                        ),
                    )
                    item.notes.append("preserved existing merge state for manual recovery")
                    continue

            clean, handoff_reason, handoff_next_action = _ensure_clean_implementation_handoff(
                session,
                item,
                runtime_root,
            )
            if not clean:
                _write_needs_human_result(
                    session,
                    item,
                    tasks_path,
                    runtime_root,
                    reason=handoff_reason or "implementation handoff did not complete cleanly",
                    next_action=handoff_next_action
                    or (
                        f"Inspect {item.worktree_path} and {item.handoff_log_path}, clean up the "
                        f"implementation branch, and rerun merge-queue."
                    ),
                )
                continue

            ensure_local_integration_branch(session.workspace_root, item.integration_branch)

            current = current_branch(item.worktree_path)
            if current != item.implementation_branch:
                _switch_worktree_branch(
                    session,
                    item,
                    item.implementation_branch,
                    log_path=item.merge_log_path,
                )
                merge_logs.append(f"switched_to={item.implementation_branch}")

            _switch_worktree_branch(
                session,
                item,
                item.integration_branch,
                log_path=item.merge_log_path,
            )
            merge_logs.append(f"switched_to={item.integration_branch}")
            initial_head = current_head(item.worktree_path)

            completed = run_git(
                item.worktree_path,
                "merge",
                "--no-ff",
                "-m",
                item.change_id,
                item.implementation_branch,
                check=False,
            )
            merge_logs.append(completed.stdout.strip())
            merge_logs.append(completed.stderr.strip())
            _write_merge_log(item.merge_log_path, [line for line in merge_logs if line])

            if completed.returncode != 0:
                recovered, recovery_reason, recovery_next_action = _run_merge_fallback(
                    session,
                    item,
                    runtime_root,
                    initial_head=initial_head,
                    resume_existing_merge=False,
                )
                if not recovered:
                    if _has_pending_parent_managed_merge_state(
                        item.worktree_path,
                        item.integration_branch,
                    ):
                        item.notes.append("merge command left an unresolved merge state behind")
                    _write_needs_human_result(
                        session,
                        item,
                        tasks_path,
                        runtime_root,
                        reason=recovery_reason
                        or f"direct merge failed for {item.change_id}; inspect {item.merge_log_path}",
                        next_action=recovery_next_action
                        or (
                            f"Inspect {item.worktree_path}, resolve the merge on "
                            f"{item.integration_branch}, and rerun merge-queue."
                        ),
                    )
                    continue

            metadata = inspect_managed_git_tasks(
                tasks_path,
                item.change_id,
                item.implementation_branch,
                item.integration_branch,
            )
            marked = mark_merge_tasks(tasks_path, metadata)
            item.notes.append(f"marked {marked} merge task(s) complete")

            run_git(item.worktree_path, "switch", "--detach", "HEAD")
            item.notes.append("detached worktree at merged integration commit")

            progress = parse_tasks_summary(tasks_path)
            if progress.full_total <= 0 or progress.full_completed < progress.full_total:
                _write_needs_human_result(
                    session,
                    item,
                    tasks_path,
                    runtime_root,
                    reason="tasks.md still has unchecked items after the parent-managed merge",
                    next_action=(
                        f"Inspect {tasks_path} and reconcile the remaining checkbox items "
                        f"before rerunning merge-queue for {item.change_id}."
                    ),
                    completed_tasks=progress.full_completed,
                    total_tasks=progress.full_total,
                )
                item.notes.append(
                    f"post-merge tasks remain {progress.full_completed}/{progress.full_total}"
                )
                continue

            if session.archive_enabled:
                archive_change(session.workspace_root, item.change_id)
                item.notes.append("archived merged change")
                _run_post_archive_cleanup(session, item)
                record = write_legacy_result(
                    workspace_root=session.workspace_root,
                    session_key=session.session_key,
                    change_id=item.change_id,
                    status="success",
                    tasks_path=tasks_path,
                    archived=True,
                    runtime_root=runtime_root,
                    completed_tasks=progress.full_completed,
                    total_tasks=progress.full_total,
                )
                item.outcome = "merged_and_archived"
                item.reason = "merge completed and the change was archived"
            else:
                record = write_legacy_result(
                    workspace_root=session.workspace_root,
                    session_key=session.session_key,
                    change_id=item.change_id,
                    status="success",
                    tasks_path=tasks_path,
                    archived=False,
                    runtime_root=runtime_root,
                    completed_tasks=progress.full_completed,
                    total_tasks=progress.full_total,
                )
                item.outcome = "merged"
                item.reason = "merge completed successfully"
            item.result_path = record.path

        except (RuntimeError, GitCommandError, OpenSpecCommandError) as error:
            item.outcome = "failed"
            item.reason = str(error)
            tasks_for_result = tasks_path or item.tasks_path
            if tasks_for_result is not None:
                record = write_legacy_result(
                    workspace_root=session.workspace_root,
                    session_key=session.session_key,
                    change_id=item.change_id,
                    status="needs_human",
                    tasks_path=tasks_for_result,
                    requires_human=True,
                    human_reason=item.reason,
                    human_next_action=(
                        f"Inspect {item.worktree_path or 'the original worktree'} and continue "
                        f"the merge manually."
                    ),
                    runtime_root=runtime_root,
                )
                item.result_path = record.path
            if item.merge_log_path is not None and not item.merge_log_path.exists():
                _write_merge_log(item.merge_log_path, [item.reason])
        finally:
            item.finished_at = datetime.now()
            append_event(
                runtime_root,
                "merge_queue_finished",
                {
                    "change_id": item.change_id,
                    "series": item.series,
                    "outcome": item.outcome,
                    "reason": item.reason,
                    "handoff_state": item.handoff_state,
                    "merge_recovery_state": item.merge_recovery_state,
                    "result_path": str(item.result_path) if item.result_path else None,
                    "merge_log_path": str(item.merge_log_path)
                    if item.merge_log_path
                    else None,
                    "handoff_log_path": str(item.handoff_log_path)
                    if item.handoff_log_path
                    else None,
                    "branch_cleanup_log_path": str(item.branch_cleanup_log_path)
                    if item.branch_cleanup_log_path
                    else None,
                    "worktree_cleanup_log_path": str(item.worktree_cleanup_log_path)
                    if item.worktree_cleanup_log_path
                    else None,
                },
            )
