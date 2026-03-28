from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from openspec_py.planner import ExecutionPlan, PlanItem
from openspec_py.session_store import SessionWriteResult, write_session_payload


@dataclass(slots=True)
class OrchestrationItem:
    change_id: str
    series: str
    step: int | None
    current_status: str
    plan_state: str
    action: str
    wave: int | None
    reason: str
    blockers: list[str]
    next_task: str | None
    path: Path

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["path"] = str(self.path)
        return payload


@dataclass(slots=True)
class OrchestrationSession:
    workspace_root: Path
    generated_at: datetime
    session_key: str
    dry_run: bool
    max_parallel: int
    available_slots: int
    items: list[OrchestrationItem]

    @property
    def action_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.action] = counts.get(item.action, 0) + 1
        return dict(sorted(counts.items()))

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_root": str(self.workspace_root),
            "generated_at": self.generated_at.isoformat(),
            "session_key": self.session_key,
            "dry_run": self.dry_run,
            "max_parallel": self.max_parallel,
            "available_slots": self.available_slots,
            "action_counts": self.action_counts,
            "items": [item.to_dict() for item in self.items],
        }


def _sort_key(item: PlanItem) -> tuple[object, ...]:
    return (
        item.wave if item.wave is not None else 9999,
        item.series,
        item.step if item.step is not None else 9999,
        item.change_id,
    )


def _derive_session_key(items: list[PlanItem]) -> str:
    series = sorted({item.series for item in items})
    if not series:
        return "empty-plan"
    if len(series) == 1:
        return series[0]
    if len(series) <= 4:
        return "__".join(series)
    return f"multi-{len(series)}-series"


def build_orchestration_session(
    plan: ExecutionPlan,
    *,
    max_parallel: int = 0,
    dry_run: bool = True,
) -> OrchestrationSession:
    active_items = sorted(
        [item for item in plan.items if item.plan_state == "active"],
        key=_sort_key,
    )
    ready_items = sorted(
        [item for item in plan.items if item.plan_state == "ready"],
        key=_sort_key,
    )

    if max_parallel <= 0:
        available_slots = len(ready_items)
    else:
        available_slots = max(max_parallel - len(active_items), 0)

    launch_now = ready_items[:available_slots]
    wait_capacity = ready_items[available_slots:]

    items: list[OrchestrationItem] = []
    for plan_item in plan.items:
        if plan_item.plan_state == "active":
            action = "keep_running"
            reason = "already running; keep this change in the current execution set"
        elif plan_item in launch_now:
            action = "launch_now"
            reason = "selected for the next launch batch"
        elif plan_item in wait_capacity:
            action = "wait_capacity"
            reason = "ready to run, but current parallelism limit leaves no free slot"
        elif plan_item.plan_state == "queued":
            action = "wait_dependencies"
            reason = plan_item.reason
        elif plan_item.plan_state == "blocked":
            action = "blocked"
            reason = plan_item.reason
        elif plan_item.plan_state == "halted":
            action = "halted"
            reason = plan_item.reason
        else:
            action = "completed"
            reason = "already completed; no scheduling action needed"

        items.append(
            OrchestrationItem(
                change_id=plan_item.change_id,
                series=plan_item.series,
                step=plan_item.step,
                current_status=plan_item.current_status,
                plan_state=plan_item.plan_state,
                action=action,
                wave=plan_item.wave,
                reason=reason,
                blockers=list(plan_item.blockers),
                next_task=plan_item.next_task,
                path=plan_item.path,
            )
        )

    return OrchestrationSession(
        workspace_root=plan.workspace_root,
        generated_at=datetime.now(),
        session_key=_derive_session_key(plan.items),
        dry_run=dry_run,
        max_parallel=max_parallel,
        available_slots=available_slots,
        items=sorted(
            items,
            key=lambda item: (
                item.action,
                item.wave if item.wave is not None else 9999,
                item.series,
                item.step if item.step is not None else 9999,
                item.change_id,
            ),
        ),
    )


def write_orchestration_session(
    session: OrchestrationSession,
    output_path: Path,
    runtime_root: Path,
) -> SessionWriteResult:
    return write_session_payload(
        session.to_dict(),
        output_path,
        runtime_root,
        "orchestration_written",
        {
            "session_key": session.session_key,
            "item_count": len(session.items),
            "action_counts": session.action_counts,
            "max_parallel": session.max_parallel,
            "available_slots": session.available_slots,
        },
    )
