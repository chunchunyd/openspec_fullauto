from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class TaskSummary:
    full_total: int = 0
    full_completed: int = 0
    manual_total: int = 0
    manual_completed: int = 0
    automation_total: int = 0
    automation_completed: int = 0
    next_pending: str | None = None

    @property
    def full_pending(self) -> int:
        return max(self.full_total - self.full_completed, 0)

    @property
    def manual_pending(self) -> int:
        return max(self.manual_total - self.manual_completed, 0)

    @property
    def automation_pending(self) -> int:
        return max(self.automation_total - self.automation_completed, 0)


@dataclass(slots=True)
class ResultSummary:
    status: str
    completed_tasks: int | None = None
    total_tasks: int | None = None
    archived: bool = False
    requires_human: bool = False
    human_reason: str | None = None
    human_next_action: str | None = None
    transition_at: int | None = None
    source_path: Path | None = None
    session_key: str | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class ChangeSnapshot:
    change_id: str
    series: str
    step: int | None
    path: Path
    tasks_path: Path | None
    tasks: TaskSummary
    dependencies: list[str] = field(default_factory=list)
    unmet_dependencies: list[str] = field(default_factory=list)
    latest_result: ResultSummary | None = None
    latest_log_path: Path | None = None
    latest_log_at: datetime | None = None
    latest_update_at: datetime | None = None
    status: str = "pending"
    archived_in_changes: bool = False

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["path"] = str(self.path)
        payload["tasks_path"] = str(self.tasks_path) if self.tasks_path else None
        payload["latest_log_path"] = (
            str(self.latest_log_path) if self.latest_log_path else None
        )
        payload["latest_log_at"] = (
            self.latest_log_at.isoformat() if self.latest_log_at else None
        )
        payload["latest_update_at"] = (
            self.latest_update_at.isoformat() if self.latest_update_at else None
        )
        if self.latest_result and self.latest_result.source_path:
            payload["latest_result"]["source_path"] = str(
                self.latest_result.source_path
            )
        if self.latest_result and self.latest_result.updated_at:
            payload["latest_result"]["updated_at"] = (
                self.latest_result.updated_at.isoformat()
            )
        return payload


@dataclass(slots=True)
class SeriesSnapshot:
    name: str
    changes: list[ChangeSnapshot] = field(default_factory=list)
    dependency_file: Path | None = None

    @property
    def status(self) -> str:
        statuses = {change.status for change in self.changes}
        if not statuses:
            return "empty"
        if "needs_human" in statuses:
            return "needs_human"
        if "failed" in statuses:
            return "failed"
        if statuses <= {"archived", "done"}:
            return "done"
        if "in_progress" in statuses or "ready_for_merge" in statuses:
            return "in_progress"
        if "blocked" in statuses:
            return "blocked"
        if "tasks_done" in statuses:
            return "tasks_done"
        return "pending"

    @property
    def change_count(self) -> int:
        return len(self.changes)

    @property
    def completed_change_count(self) -> int:
        return sum(change.status in {"archived", "done"} for change in self.changes)

    @property
    def manual_completed(self) -> int:
        return sum(change.tasks.manual_completed for change in self.changes)

    @property
    def manual_total(self) -> int:
        return sum(change.tasks.manual_total for change in self.changes)

    @property
    def full_completed(self) -> int:
        return sum(change.tasks.full_completed for change in self.changes)

    @property
    def full_total(self) -> int:
        return sum(change.tasks.full_total for change in self.changes)

    @property
    def latest_update_at(self) -> datetime | None:
        timestamps = [
            change.latest_update_at for change in self.changes if change.latest_update_at
        ]
        return max(timestamps) if timestamps else None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status,
            "dependency_file": str(self.dependency_file) if self.dependency_file else None,
            "change_count": self.change_count,
            "completed_change_count": self.completed_change_count,
            "manual_completed": self.manual_completed,
            "manual_total": self.manual_total,
            "full_completed": self.full_completed,
            "full_total": self.full_total,
            "latest_update_at": (
                self.latest_update_at.isoformat() if self.latest_update_at else None
            ),
            "changes": [change.to_dict() for change in self.changes],
        }


@dataclass(slots=True)
class WorkspaceSnapshot:
    workspace_root: Path
    generated_at: datetime
    active_changes_root: Path
    logs_root: Path
    series: list[SeriesSnapshot]

    @property
    def active_change_count(self) -> int:
        return sum(series.change_count for series in self.series)

    @property
    def status_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for series in self.series:
            for change in series.changes:
                counts[change.status] = counts.get(change.status, 0) + 1
        return dict(sorted(counts.items()))

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_root": str(self.workspace_root),
            "generated_at": self.generated_at.isoformat(),
            "active_changes_root": str(self.active_changes_root),
            "logs_root": str(self.logs_root),
            "active_change_count": self.active_change_count,
            "status_counts": self.status_counts,
            "series": [series.to_dict() for series in self.series],
        }
