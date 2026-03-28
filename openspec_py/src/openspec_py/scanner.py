from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openspec_py.models import ChangeSnapshot, SeriesSnapshot, WorkspaceSnapshot
from openspec_py.parsers import (
    format_relative_time,
    parse_dependency_graph,
    parse_result_summary,
    parse_series_name,
    parse_step_number,
    parse_tasks_summary,
)
from openspec_py.workspace import WorkspacePaths


def _latest_path(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda item: item.stat().st_mtime)


def _iter_active_change_dirs(changes_root: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in changes_root.iterdir()
            if path.is_dir() and path.name != "archive"
        ),
        key=lambda item: item.name,
    )


def _iter_archived_change_names(archive_root: Path) -> set[str]:
    names: set[str] = set()
    if not archive_root.exists():
        return names
    for path in archive_root.iterdir():
        if not path.is_dir():
            continue
        names.add(path.name)
        parts = path.name.split("-", 3)
        if len(parts) >= 4 and all(part.isdigit() for part in parts[:3]):
            names.add(parts[3])
    return names


def _discover_dependency_files(
    paths: WorkspacePaths, active_series: set[str]
) -> dict[str, Path]:
    dependency_files: dict[str, Path] = {}
    for series_name in active_series:
        candidate = paths.deps_root / f"deps.{series_name}.json"
        if candidate.exists():
            dependency_files[series_name] = candidate
    return dependency_files


def _build_dependency_map(
    dependency_files: dict[str, Path]
) -> dict[str, list[str]]:
    dependency_map: dict[str, list[str]] = {}
    for path in dependency_files.values():
        dependency_map.update(parse_dependency_graph(path))
    return dependency_map


def _session_key_for_path(path: Path) -> str | None:
    parent_name = path.parent.name
    prefix = ".auto-apply-run."
    if parent_name.startswith(prefix):
        return parent_name[len(prefix) :]
    return parent_name


def _index_runtime_artifacts(
    logs_root: Path, change_names: list[str]
) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
    result_files: dict[str, list[Path]] = defaultdict(list)
    log_files: dict[str, list[Path]] = defaultdict(list)

    if not logs_root.exists():
        return result_files, log_files

    for session_dir in logs_root.iterdir():
        if not session_dir.is_dir():
            continue
        for artifact in session_dir.iterdir():
            if not artifact.is_file():
                continue
            for change_name in change_names:
                if artifact.name == f"{change_name}.result":
                    result_files[change_name].append(artifact)
                elif artifact.name.startswith(f"{change_name}.") and artifact.suffix == ".log":
                    log_files[change_name].append(artifact)

    return result_files, log_files


def _status_from_result(result_status: str, archived: bool, requires_human: bool) -> str:
    if requires_human or result_status == "needs_human":
        return "needs_human"
    if result_status == "success":
        return "archived" if archived else "done"
    if result_status in {"prepared", "preparing", "launched", "running", "in_progress"}:
        return "in_progress"
    if result_status in {"failed", "blocked", "ready_for_merge", "incomplete"}:
        return result_status
    return result_status or "unknown"


def _compute_change_status(change: ChangeSnapshot) -> str:
    if change.latest_result:
        return _status_from_result(
            change.latest_result.status,
            change.latest_result.archived,
            change.latest_result.requires_human,
        )
    if change.unmet_dependencies:
        return "blocked"
    if change.tasks.manual_total > 0 and change.tasks.manual_pending == 0:
        return "tasks_done"
    if change.tasks.manual_completed > 0 or change.tasks.full_completed > 0:
        return "in_progress"
    return "pending"


def build_workspace_snapshot(
    paths: WorkspacePaths,
    series_filters: set[str] | None = None,
) -> WorkspaceSnapshot:
    active_change_dirs = _iter_active_change_dirs(paths.changes_root)
    archived_names = _iter_archived_change_names(paths.archive_root)

    changes: list[ChangeSnapshot] = []
    active_series: set[str] = set()
    for change_dir in active_change_dirs:
        series_name = parse_series_name(change_dir.name)
        if series_filters and series_name not in series_filters:
            continue
        active_series.add(series_name)
        tasks_path = change_dir / "tasks.md"
        changes.append(
            ChangeSnapshot(
                change_id=change_dir.name,
                series=series_name,
                step=parse_step_number(change_dir.name),
                path=change_dir,
                tasks_path=tasks_path if tasks_path.exists() else None,
                tasks=parse_tasks_summary(tasks_path if tasks_path.exists() else None),
            )
        )

    dependency_files = _discover_dependency_files(paths, active_series)
    dependency_map = _build_dependency_map(dependency_files)
    result_index, log_index = _index_runtime_artifacts(
        paths.logs_root, [change.change_id for change in changes]
    )

    completed_like: set[str] = set()
    for change in changes:
        latest_result_path = _latest_path(result_index.get(change.change_id, []))
        latest_log_path = _latest_path(log_index.get(change.change_id, []))

        if latest_result_path:
            session_key = _session_key_for_path(latest_result_path)
            change.latest_result = parse_result_summary(latest_result_path, session_key)
        if latest_log_path:
            change.latest_log_path = latest_log_path
            change.latest_log_at = datetime.fromtimestamp(latest_log_path.stat().st_mtime)

        change.dependencies = dependency_map.get(change.change_id, [])
        change.archived_in_changes = change.change_id in archived_names

        timestamps = [
            datetime.fromtimestamp(change.tasks_path.stat().st_mtime)
            if change.tasks_path and change.tasks_path.exists()
            else None,
            change.latest_log_at,
            change.latest_result.updated_at if change.latest_result else None,
        ]
        valid_timestamps = [timestamp for timestamp in timestamps if timestamp is not None]
        change.latest_update_at = max(valid_timestamps) if valid_timestamps else None

        if change.latest_result and change.latest_result.status == "success":
            completed_like.add(change.change_id)
        if change.archived_in_changes:
            completed_like.add(change.change_id)

    completed_like.update(archived_names)

    for change in changes:
        change.unmet_dependencies = [
            dependency for dependency in change.dependencies if dependency not in completed_like
        ]
        change.status = _compute_change_status(change)

    series_map: dict[str, list[ChangeSnapshot]] = defaultdict(list)
    for change in changes:
        series_map[change.series].append(change)

    series_snapshots: list[SeriesSnapshot] = []
    for series_name, series_changes in sorted(series_map.items()):
        ordered_changes = sorted(
            series_changes,
            key=lambda item: (
                item.step if item.step is not None else 9999,
                item.change_id,
            ),
        )
        series_snapshots.append(
            SeriesSnapshot(
                name=series_name,
                changes=ordered_changes,
                dependency_file=dependency_files.get(series_name),
            )
        )

    return WorkspaceSnapshot(
        workspace_root=paths.workspace_root,
        generated_at=datetime.now(),
        active_changes_root=paths.changes_root,
        logs_root=paths.logs_root,
        series=series_snapshots,
    )


def summarize_change_update(change: ChangeSnapshot, now: datetime) -> str:
    return format_relative_time(change.latest_update_at, now)
