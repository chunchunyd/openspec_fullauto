from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from openspec_py.models import ChangeSnapshot, WorkspaceSnapshot
from openspec_py.runtime_logging import append_event

COMPLETED_STATUSES = {"archived", "done"}
HALTED_STATUSES = {"needs_human", "failed"}
ACTIVE_STATUSES = {"in_progress", "ready_for_merge", "tasks_done"}


@dataclass(slots=True)
class PlanItem:
    change_id: str
    series: str
    step: int | None
    current_status: str
    plan_state: str
    wave: int | None
    dependencies: list[str]
    blockers: list[str]
    reason: str
    next_task: str | None
    path: Path

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["path"] = str(self.path)
        return payload


@dataclass(slots=True)
class ExecutionPlan:
    workspace_root: Path
    generated_at: datetime
    items: list[PlanItem]

    @property
    def max_wave(self) -> int:
        waves = [item.wave for item in self.items if item.wave is not None]
        return max(waves) if waves else 0

    @property
    def state_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.plan_state] = counts.get(item.plan_state, 0) + 1
        return dict(sorted(counts.items()))

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_root": str(self.workspace_root),
            "generated_at": self.generated_at.isoformat(),
            "max_wave": self.max_wave,
            "state_counts": self.state_counts,
            "items": [item.to_dict() for item in self.items],
        }


def _reason_for_halted(change: ChangeSnapshot) -> str:
    if change.latest_result and change.latest_result.human_reason:
        return change.latest_result.human_reason
    if change.latest_result:
        return f"latest result status is {change.latest_result.status}"
    return "change is halted and needs inspection"


def build_execution_plan(snapshot: WorkspaceSnapshot) -> ExecutionPlan:
    change_map = {
        change.change_id: change
        for series in snapshot.series
        for change in series.changes
    }
    memo: dict[str, int | None] = {}
    visiting: set[str] = set()

    def compute_wave(change_id: str) -> int | None:
        if change_id in memo:
            return memo[change_id]

        change = change_map[change_id]
        if change.status in COMPLETED_STATUSES | HALTED_STATUSES:
            memo[change_id] = None
            return None

        if change_id in visiting:
            memo[change_id] = None
            return None

        visiting.add(change_id)
        max_dep_wave = -1
        unresolved_missing = False
        halted_dependency = False

        for dependency in change.dependencies:
            dep_change = change_map.get(dependency)
            if dep_change is None:
                if dependency in change.unmet_dependencies:
                    unresolved_missing = True
                    break
                continue

            if dep_change.status in HALTED_STATUSES:
                halted_dependency = True
                break

            if dep_change.status in COMPLETED_STATUSES:
                continue

            dep_wave = compute_wave(dependency)
            if dep_wave is None and dep_change.status not in COMPLETED_STATUSES:
                halted_dependency = True
                break
            if dep_wave is not None:
                max_dep_wave = max(max_dep_wave, dep_wave)

        visiting.remove(change_id)

        if unresolved_missing or halted_dependency:
            memo[change_id] = None
            return None

        memo[change_id] = max_dep_wave + 1 if max_dep_wave >= 0 else 0
        return memo[change_id]

    items: list[PlanItem] = []
    for series in snapshot.series:
        for change in series.changes:
            blockers: list[str] = []
            wave = compute_wave(change.change_id)

            if change.status in COMPLETED_STATUSES:
                plan_state = "completed"
                reason = "already completed in current workspace state"
            elif change.status in HALTED_STATUSES:
                plan_state = "halted"
                reason = _reason_for_halted(change)
            elif wave is None:
                blockers = list(change.unmet_dependencies)
                halted_blockers = [
                    dep
                    for dep in change.dependencies
                    if dep in change_map and change_map[dep].status in HALTED_STATUSES
                ]
                blockers.extend(halted_blockers)
                blockers = sorted(dict.fromkeys(blockers))
                plan_state = "blocked"
                if halted_blockers:
                    reason = "waiting on upstream change(s) that currently need human recovery"
                elif blockers:
                    reason = "waiting on unresolved or incomplete dependencies"
                else:
                    reason = "dependency wave could not be resolved"
            elif wave == 0:
                if change.status in ACTIVE_STATUSES:
                    plan_state = "active"
                    if change.status == "tasks_done":
                        reason = "manual tasks appear complete; ready for the next workflow stage"
                    else:
                        reason = "dependencies satisfied and work is already in progress"
                else:
                    plan_state = "ready"
                    reason = "dependencies satisfied; this change can start now"
            else:
                plan_state = "queued"
                blockers = list(change.unmet_dependencies)
                reason = f"becomes runnable in wave {wave} after earlier dependencies complete"

            items.append(
                PlanItem(
                    change_id=change.change_id,
                    series=change.series,
                    step=change.step,
                    current_status=change.status,
                    plan_state=plan_state,
                    wave=wave,
                    dependencies=list(change.dependencies),
                    blockers=blockers,
                    reason=reason,
                    next_task=change.tasks.next_pending,
                    path=change.path,
                )
            )

    items.sort(
        key=lambda item: (
            item.series,
            item.wave if item.wave is not None else 9999,
            item.step if item.step is not None else 9999,
            item.change_id,
        )
    )

    return ExecutionPlan(
        workspace_root=snapshot.workspace_root,
        generated_at=datetime.now(),
        items=items,
    )


def write_execution_plan(
    plan: ExecutionPlan,
    output_path: Path,
    runtime_root: Path,
) -> bool:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(plan.to_dict(), indent=2, ensure_ascii=True) + "\n"
    existing = output_path.read_text(encoding="utf-8", errors="replace") if output_path.exists() else None
    if existing == payload:
        return False

    output_path.write_text(payload, encoding="utf-8")
    append_event(
        runtime_root,
        "plan_written",
        {
            "path": str(output_path),
            "item_count": len(plan.items),
            "state_counts": plan.state_counts,
        },
    )
    return True
