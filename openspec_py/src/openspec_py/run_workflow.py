from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from openspec_py.finalizer import (
    FinalizeSession,
    build_finalize_session,
    execute_finalize_session,
    write_finalize_session,
)
from openspec_py.launcher import (
    LaunchSession,
    build_launch_session,
    execute_launch_session,
    write_launch_session,
)
from openspec_py.legacy_session_state import ensure_legacy_session_dir
from openspec_py.merge_queue import (
    MergeQueueSession,
    build_merge_queue_session,
    execute_merge_queue_session,
    write_merge_queue_session,
)
from openspec_py.orchestrator import (
    OrchestrationSession,
    build_orchestration_session,
    write_orchestration_session,
)
from openspec_py.planner import (
    ExecutionPlan,
    build_execution_plan,
    write_execution_plan,
)
from openspec_py.preflight import PreflightError, validate_workspace_snapshot
from openspec_py.preparation import (
    PreparationSession,
    build_preparation_session,
    execute_preparation_session,
    write_preparation_session,
)
from openspec_py.runtime_logging import append_event
from openspec_py.scanner import build_workspace_snapshot
from openspec_py.scope import select_change_scope
from openspec_py.session_store import SessionWriteResult, write_session_payload
from openspec_py.snapshot import write_snapshot
from openspec_py.workspace import WorkspacePaths


@dataclass(slots=True)
class RunCycle:
    index: int
    started_at: datetime
    finished_at: datetime | None = None
    snapshot_status_counts: dict[str, int] = field(default_factory=dict)
    plan_state_counts: dict[str, int] = field(default_factory=dict)
    orchestration_action_counts: dict[str, int] = field(default_factory=dict)
    launch_state_counts: dict[str, int] = field(default_factory=dict)
    finalize_action_counts: dict[str, int] = field(default_factory=dict)
    merge_action_counts: dict[str, int] = field(default_factory=dict)
    merge_outcome_counts: dict[str, int] = field(default_factory=dict)
    launched_now: int = 0
    ready_for_merge_seen: int = 0
    merged_now: int = 0
    stopped_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["started_at"] = self.started_at.isoformat()
        payload["finished_at"] = self.finished_at.isoformat() if self.finished_at else None
        return payload


@dataclass(slots=True)
class RunSession:
    workspace_root: Path
    generated_at: datetime
    execute: bool
    series_filters: list[str]
    target_change_ids: list[str]
    session_key: str
    max_parallel: int
    command_template: str
    task_sync_command_template: str | None
    assessment_command_template: str | None
    retry_limit: int
    strict_validate: bool
    skip_validate: bool
    archive_enabled: bool
    cleanup_worktrees: bool
    prepare_worktrees: bool
    handoff_command_template: str | None
    merge_fallback_command_template: str | None
    poll_interval_seconds: float
    max_cycles: int
    stop_when_idle: bool
    latest_snapshot_path: Path
    latest_plan_path: Path
    latest_orchestration_path: Path
    latest_preparation_path: Path
    latest_launch_path: Path
    latest_finalize_path: Path
    latest_merge_path: Path
    latest_run_path: Path
    current_cycle: int = 0
    state: str = "planned"
    last_message: str | None = None
    cycles: list[RunCycle] = field(default_factory=list)
    latest_snapshot_counts: dict[str, int] = field(default_factory=dict)
    latest_plan_counts: dict[str, int] = field(default_factory=dict)
    latest_orchestration_counts: dict[str, int] = field(default_factory=dict)
    latest_launch_counts: dict[str, int] = field(default_factory=dict)
    latest_finalize_counts: dict[str, int] = field(default_factory=dict)
    latest_merge_counts: dict[str, int] = field(default_factory=dict)
    snapshot_write: SessionWriteResult | None = None
    plan_write: SessionWriteResult | None = None
    orchestration_write: SessionWriteResult | None = None
    preparation_write: SessionWriteResult | None = None
    launch_write: SessionWriteResult | None = None
    finalize_write: SessionWriteResult | None = None
    merge_write: SessionWriteResult | None = None
    run_write: SessionWriteResult | None = None
    last_plan: ExecutionPlan | None = None
    last_orchestration: OrchestrationSession | None = None
    last_preparation: PreparationSession | None = None
    last_launch: LaunchSession | None = None
    last_finalize: FinalizeSession | None = None
    last_merge_queue: MergeQueueSession | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_root": str(self.workspace_root),
            "generated_at": self.generated_at.isoformat(),
            "execute": self.execute,
            "series_filters": self.series_filters,
            "target_change_ids": self.target_change_ids,
            "session_key": self.session_key,
            "max_parallel": self.max_parallel,
            "command_template": self.command_template,
            "task_sync_command_template": self.task_sync_command_template,
            "assessment_command_template": self.assessment_command_template,
            "retry_limit": self.retry_limit,
            "strict_validate": self.strict_validate,
            "skip_validate": self.skip_validate,
            "archive_enabled": self.archive_enabled,
            "cleanup_worktrees": self.cleanup_worktrees,
            "prepare_worktrees": self.prepare_worktrees,
            "handoff_command_template": self.handoff_command_template,
            "merge_fallback_command_template": self.merge_fallback_command_template,
            "poll_interval_seconds": self.poll_interval_seconds,
            "max_cycles": self.max_cycles,
            "stop_when_idle": self.stop_when_idle,
            "latest_snapshot_path": str(self.latest_snapshot_path),
            "latest_plan_path": str(self.latest_plan_path),
            "latest_orchestration_path": str(self.latest_orchestration_path),
            "latest_preparation_path": str(self.latest_preparation_path),
            "latest_launch_path": str(self.latest_launch_path),
            "latest_finalize_path": str(self.latest_finalize_path),
            "latest_merge_path": str(self.latest_merge_path),
            "latest_run_path": str(self.latest_run_path),
            "current_cycle": self.current_cycle,
            "state": self.state,
            "last_message": self.last_message,
            "latest_snapshot_counts": self.latest_snapshot_counts,
            "latest_plan_counts": self.latest_plan_counts,
            "latest_orchestration_counts": self.latest_orchestration_counts,
            "latest_launch_counts": self.latest_launch_counts,
            "latest_finalize_counts": self.latest_finalize_counts,
            "latest_merge_counts": self.latest_merge_counts,
            "cycles": [cycle.to_dict() for cycle in self.cycles],
        }


def _derive_session_key(
    series_filters: set[str] | None,
    target_change_ids: list[str],
) -> str:
    if target_change_ids:
        if len(target_change_ids) == 1:
            return target_change_ids[0]
        if len(target_change_ids) <= 4:
            return "__".join(sorted(target_change_ids))
        return f"multi-{len(target_change_ids)}-changes"
    if not series_filters:
        return "all-series"
    series = sorted(series_filters)
    if len(series) == 1:
        return series[0]
    if len(series) <= 4:
        return "__".join(series)
    return f"multi-{len(series)}-series"


def build_run_session(
    paths: WorkspacePaths,
    *,
    execute: bool,
    series_filters: set[str] | None,
    target_change_ids: list[str],
    max_parallel: int,
    command_template: str,
    task_sync_command_template: str | None,
    assessment_command_template: str | None,
    retry_limit: int,
    strict_validate: bool,
    skip_validate: bool,
    archive_enabled: bool,
    cleanup_worktrees: bool,
    prepare_worktrees: bool,
    handoff_command_template: str | None,
    merge_fallback_command_template: str | None,
    poll_interval_seconds: float,
    max_cycles: int,
    stop_when_idle: bool,
) -> RunSession:
    openspec_py_root = paths.workspace_root / "openspec_py"
    runtime_root = openspec_py_root / "runtime"
    return RunSession(
        workspace_root=paths.workspace_root,
        generated_at=datetime.now(),
        execute=execute,
        series_filters=sorted(series_filters or []),
        target_change_ids=sorted(target_change_ids),
        session_key=_derive_session_key(series_filters, target_change_ids),
        max_parallel=max_parallel,
        command_template=command_template,
        task_sync_command_template=task_sync_command_template,
        assessment_command_template=assessment_command_template,
        retry_limit=max(retry_limit, 0),
        strict_validate=strict_validate,
        skip_validate=skip_validate,
        archive_enabled=archive_enabled,
        cleanup_worktrees=cleanup_worktrees,
        prepare_worktrees=prepare_worktrees,
        handoff_command_template=handoff_command_template,
        merge_fallback_command_template=merge_fallback_command_template,
        poll_interval_seconds=max(poll_interval_seconds, 0.5),
        max_cycles=max(max_cycles, 1),
        stop_when_idle=stop_when_idle,
        latest_snapshot_path=(runtime_root / "latest-status.json").resolve(),
        latest_plan_path=(runtime_root / "latest-plan.json").resolve(),
        latest_orchestration_path=(runtime_root / "latest-orchestration.json").resolve(),
        latest_preparation_path=(runtime_root / "latest-preparation.json").resolve(),
        latest_launch_path=(runtime_root / "latest-launch.json").resolve(),
        latest_finalize_path=(runtime_root / "latest-finalize.json").resolve(),
        latest_merge_path=(runtime_root / "latest-merge-queue.json").resolve(),
        latest_run_path=(runtime_root / "latest-run.json").resolve(),
    )


def write_run_session(
    session: RunSession,
    runtime_root: Path,
    *,
    event_name: str = "run_session_written",
) -> SessionWriteResult:
    return write_session_payload(
        session.to_dict(),
        session.latest_run_path,
        runtime_root,
        event_name,
        {
            "session_key": session.session_key,
            "state": session.state,
            "current_cycle": session.current_cycle,
            "cycle_count": len(session.cycles),
            "execute": session.execute,
            "series_filters": session.series_filters,
            "target_change_ids": session.target_change_ids,
            "max_parallel": session.max_parallel,
        },
    )


def _count_plan_states(plan: ExecutionPlan) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in plan.items:
        counts[item.plan_state] = counts.get(item.plan_state, 0) + 1
    return dict(sorted(counts.items()))


def _count_finalize_actions(session: FinalizeSession) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in session.items:
        counts[item.action] = counts.get(item.action, 0) + 1
    return dict(sorted(counts.items()))


def _ensure_stage_legacy_session(
    paths: WorkspacePaths,
    *,
    session_key: str,
    change_ids: list[str],
) -> None:
    ensure_legacy_session_dir(
        paths.logs_root,
        session_dir=paths.logs_root / f".auto-apply-run.{session_key}",
        target_change_ids=change_ids,
        runtime_root=paths.runtime_root,
    )


def _execute_cycle(
    session: RunSession,
    paths: WorkspacePaths,
    series_filters: set[str] | None,
) -> RunCycle:
    cycle = RunCycle(index=session.current_cycle + 1, started_at=datetime.now())
    session.current_cycle = cycle.index

    snapshot = build_workspace_snapshot(paths, series_filters)
    snapshot = select_change_scope(snapshot, target_change_ids=session.target_change_ids)
    validate_workspace_snapshot(snapshot)
    cycle.snapshot_status_counts = snapshot.status_counts
    session.latest_snapshot_counts = snapshot.status_counts
    write_snapshot(snapshot, session.latest_snapshot_path, paths.runtime_root)

    plan = build_execution_plan(snapshot)
    cycle.plan_state_counts = _count_plan_states(plan)
    session.latest_plan_counts = cycle.plan_state_counts
    session.plan_write = write_execution_plan(plan, session.latest_plan_path, paths.runtime_root)
    session.last_plan = plan

    orchestration = build_orchestration_session(
        plan,
        max_parallel=session.max_parallel,
        dry_run=not session.execute,
    )
    cycle.orchestration_action_counts = orchestration.action_counts
    session.latest_orchestration_counts = orchestration.action_counts
    session.orchestration_write = write_orchestration_session(
        orchestration,
        session.latest_orchestration_path,
        paths.runtime_root,
    )
    session.last_orchestration = orchestration

    launchable = [item for item in orchestration.items if item.action == "launch_now"]
    cycle.launched_now = len(launchable)
    preparation = None
    if session.prepare_worktrees:
        preparation = build_preparation_session(
            orchestration,
            execute=session.execute,
        )
        session.preparation_write = write_preparation_session(
            preparation,
            session.latest_preparation_path,
            paths.runtime_root,
            event_name="preparation_session_planned",
        )
        if session.execute:
            execute_preparation_session(preparation, paths.runtime_root)
            session.preparation_write = write_preparation_session(
                preparation,
                session.latest_preparation_path,
                paths.runtime_root,
                event_name="preparation_session_completed",
            )
    session.last_preparation = preparation

    launch = build_launch_session(
        orchestration,
        command_template=session.command_template,
        execute=session.execute,
        retry_limit=session.retry_limit,
        task_sync_command_template=session.task_sync_command_template,
        assessment_command_template=session.assessment_command_template,
        preparation_session=preparation,
    )
    _ensure_stage_legacy_session(
        paths,
        session_key=launch.session_key,
        change_ids=[item.change_id for item in launch.items],
    )
    session.launch_write = write_launch_session(
        launch,
        session.latest_launch_path,
        paths.runtime_root,
        event_name="launch_session_planned",
    )
    if session.execute and launchable:
        execute_launch_session(launch, paths.runtime_root)
        session.launch_write = write_launch_session(
            launch,
            session.latest_launch_path,
            paths.runtime_root,
            event_name="launch_session_completed",
        )
    cycle.launch_state_counts = launch.state_counts
    session.latest_launch_counts = launch.state_counts
    session.last_launch = launch

    post_launch_snapshot = build_workspace_snapshot(paths, series_filters)
    post_launch_snapshot = select_change_scope(
        post_launch_snapshot,
        target_change_ids=session.target_change_ids,
    )
    finalize = build_finalize_session(
        post_launch_snapshot,
        execute=session.execute,
        strict_validate=session.strict_validate,
        skip_validate=session.skip_validate,
        archive_enabled=session.archive_enabled,
    )
    _ensure_stage_legacy_session(
        paths,
        session_key=finalize.session_key,
        change_ids=[item.change_id for item in finalize.items],
    )
    session.finalize_write = write_finalize_session(
        finalize,
        session.latest_finalize_path,
        paths.runtime_root,
        event_name="finalize_session_planned",
    )
    if session.execute:
        execute_finalize_session(finalize, paths.runtime_root)
        session.finalize_write = write_finalize_session(
            finalize,
            session.latest_finalize_path,
            paths.runtime_root,
            event_name="finalize_session_completed",
        )
    cycle.finalize_action_counts = _count_finalize_actions(finalize)
    cycle.ready_for_merge_seen = cycle.finalize_action_counts.get("ready_for_merge", 0)
    session.latest_finalize_counts = cycle.finalize_action_counts
    session.last_finalize = finalize

    post_finalize_snapshot = build_workspace_snapshot(paths, series_filters)
    post_finalize_snapshot = select_change_scope(
        post_finalize_snapshot,
        target_change_ids=session.target_change_ids,
    )
    merge_queue = build_merge_queue_session(
        post_finalize_snapshot,
        execute=session.execute,
        archive_enabled=session.archive_enabled,
        cleanup_worktrees=session.cleanup_worktrees,
        handoff_command_template=session.handoff_command_template,
        merge_fallback_command_template=session.merge_fallback_command_template,
    )
    _ensure_stage_legacy_session(
        paths,
        session_key=merge_queue.session_key,
        change_ids=[item.change_id for item in merge_queue.items],
    )
    session.merge_write = write_merge_queue_session(
        merge_queue,
        session.latest_merge_path,
        paths.runtime_root,
        event_name="merge_queue_planned",
    )
    if session.execute:
        execute_merge_queue_session(merge_queue, paths.runtime_root)
        session.merge_write = write_merge_queue_session(
            merge_queue,
            session.latest_merge_path,
            paths.runtime_root,
            event_name="merge_queue_completed",
        )
    cycle.merge_action_counts = merge_queue.action_counts
    cycle.merge_outcome_counts = merge_queue.outcome_counts
    cycle.merged_now = merge_queue.outcome_counts.get("merged", 0) + merge_queue.outcome_counts.get(
        "merged_and_archived", 0
    )
    session.latest_merge_counts = merge_queue.outcome_counts
    session.last_merge_queue = merge_queue

    final_snapshot = build_workspace_snapshot(paths, series_filters)
    final_snapshot = select_change_scope(
        final_snapshot,
        target_change_ids=session.target_change_ids,
    )
    cycle.snapshot_status_counts = final_snapshot.status_counts
    session.latest_snapshot_counts = final_snapshot.status_counts
    write_snapshot(final_snapshot, session.latest_snapshot_path, paths.runtime_root)

    cycle.finished_at = datetime.now()
    return cycle


def _should_stop(session: RunSession, cycle: RunCycle) -> tuple[bool, str]:
    if cycle.index >= session.max_cycles:
        return True, f"reached max cycles ({session.max_cycles})"
    if not session.stop_when_idle:
        return False, "continuing"

    activeish = (
        cycle.snapshot_status_counts.get("in_progress", 0)
        + cycle.snapshot_status_counts.get("ready_for_merge", 0)
        + cycle.snapshot_status_counts.get("running", 0)
    )
    pending_ready = cycle.orchestration_action_counts.get("launch_now", 0)
    if activeish == 0 and cycle.launched_now == 0 and cycle.merged_now == 0 and pending_ready == 0:
        return True, "workflow is idle"
    return False, "continuing"


def execute_run_session(
    session: RunSession,
    paths: WorkspacePaths,
    *,
    series_filters: set[str] | None,
) -> None:
    try:
        session.state = "running"
        session.last_message = "starting run loop"
        write_run_session(session, paths.runtime_root, event_name="run_session_started")
        append_event(
            paths.runtime_root,
            "run_loop_started",
            {
                "session_key": session.session_key,
                "execute": session.execute,
                "series_filters": session.series_filters,
                "max_cycles": session.max_cycles,
                "poll_interval_seconds": session.poll_interval_seconds,
            },
        )

        while True:
            cycle = _execute_cycle(session, paths, series_filters)
            session.cycles.append(cycle)
            should_stop, reason = _should_stop(session, cycle)
            cycle.stopped_reason = reason if should_stop else None
            session.last_message = reason
            session.run_write = write_run_session(
                session,
                paths.runtime_root,
                event_name="run_session_cycle_completed",
            )
            append_event(
                paths.runtime_root,
                "run_loop_cycle_completed",
                {
                    "session_key": session.session_key,
                    "cycle": cycle.index,
                    "snapshot_status_counts": cycle.snapshot_status_counts,
                    "plan_state_counts": cycle.plan_state_counts,
                    "orchestration_action_counts": cycle.orchestration_action_counts,
                    "launch_state_counts": cycle.launch_state_counts,
                    "finalize_action_counts": cycle.finalize_action_counts,
                    "merge_outcome_counts": cycle.merge_outcome_counts,
                    "stopped_reason": cycle.stopped_reason,
                },
            )
            if should_stop:
                session.state = "completed"
                session.last_message = reason
                break
            session.state = "sleeping"
            session.last_message = (
                f"sleeping {session.poll_interval_seconds:.1f}s before cycle {session.current_cycle + 1}"
            )
            write_run_session(session, paths.runtime_root, event_name="run_session_sleeping")
            time.sleep(session.poll_interval_seconds)
            session.state = "running"

        session.run_write = write_run_session(
            session,
            paths.runtime_root,
            event_name="run_session_completed",
        )
        append_event(
            paths.runtime_root,
            "run_loop_completed",
            {
                "session_key": session.session_key,
                "cycle_count": len(session.cycles),
                "final_state": session.state,
                "last_message": session.last_message,
            },
        )
    except (PreflightError, RuntimeError, ValueError) as error:
        session.state = "failed"
        session.last_message = str(error)
        session.run_write = write_run_session(
            session,
            paths.runtime_root,
            event_name="run_session_failed",
        )
        append_event(
            paths.runtime_root,
            "run_loop_failed",
            {
                "session_key": session.session_key,
                "cycle_count": len(session.cycles),
                "error": str(error),
            },
        )
