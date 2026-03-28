from __future__ import annotations

import shlex
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from openspec_py.parsers import parse_tasks_summary
from openspec_py.runtime_logging import append_event


@dataclass(frozen=True, slots=True)
class LegacyResultRecord:
    change_id: str
    status: str
    completed_tasks: int
    total_tasks: int
    archived: bool
    requires_human: bool
    human_reason: str | None
    human_next_action: str | None
    transition_at: int
    path: Path

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["path"] = str(self.path)
        return payload


def legacy_session_dir(workspace_root: Path, session_key: str) -> Path:
    return (
        workspace_root
        / "openspec"
        / "auto"
        / "logs"
        / f".auto-apply-run.{session_key}"
    ).resolve()


def legacy_result_path(session_dir: Path, change_id: str) -> Path:
    return session_dir / f"{change_id}.result"


def _shell_value(value: str | int) -> str:
    return shlex.quote(str(value))


def _task_progress(tasks_path: Path | None) -> tuple[int, int]:
    summary = parse_tasks_summary(tasks_path)
    return summary.full_completed, summary.full_total


def write_legacy_result(
    *,
    workspace_root: Path,
    session_key: str,
    change_id: str,
    status: str,
    tasks_path: Path | None,
    archived: bool = False,
    requires_human: bool = False,
    human_reason: str | None = None,
    human_next_action: str | None = None,
    transition_at: int | None = None,
    runtime_root: Path | None = None,
    completed_tasks: int | None = None,
    total_tasks: int | None = None,
) -> LegacyResultRecord:
    session_dir = legacy_session_dir(workspace_root, session_key)
    session_dir.mkdir(parents=True, exist_ok=True)
    target = legacy_result_path(session_dir, change_id)
    if completed_tasks is None or total_tasks is None:
        computed_completed, computed_total = _task_progress(tasks_path)
        if completed_tasks is None:
            completed_tasks = computed_completed
        if total_tasks is None:
            total_tasks = computed_total
    timestamp = transition_at if transition_at is not None else time.time_ns()
    payload = {
        "status": status,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "archived": int(archived),
        "requires_human": int(requires_human),
        "human_reason": human_reason or "",
        "human_next_action": human_next_action or "",
        "transition_at": timestamp,
    }
    body = "\n".join(f"{key}={_shell_value(value)}" for key, value in payload.items()) + "\n"
    target.write_text(body, encoding="utf-8")

    record = LegacyResultRecord(
        change_id=change_id,
        status=status,
        completed_tasks=completed_tasks,
        total_tasks=total_tasks,
        archived=archived,
        requires_human=requires_human,
        human_reason=human_reason,
        human_next_action=human_next_action,
        transition_at=timestamp,
        path=target,
    )

    if runtime_root is not None:
        append_event(
            runtime_root,
            "legacy_result_written",
            record.to_dict(),
        )

    return record
