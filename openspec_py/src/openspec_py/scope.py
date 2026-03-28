from __future__ import annotations

from openspec_py.models import SeriesSnapshot, WorkspaceSnapshot


class ScopeSelectionError(RuntimeError):
    """Raised when a requested change scope cannot be resolved safely."""


def select_change_scope(
    snapshot: WorkspaceSnapshot,
    *,
    target_change_ids: list[str],
) -> WorkspaceSnapshot:
    if not target_change_ids:
        return snapshot

    change_map = {
        change.change_id: change
        for series in snapshot.series
        for change in series.changes
    }

    missing = [change_id for change_id in target_change_ids if change_id not in change_map]
    if missing:
        raise ScopeSelectionError(
            "requested target changes are not present in the current active workspace: "
            + ", ".join(sorted(missing))
        )

    selected: set[str] = set()

    def visit(change_id: str) -> None:
        if change_id in selected:
            return
        selected.add(change_id)
        change = change_map[change_id]
        for dependency in change.dependencies:
            if dependency in change_map:
                visit(dependency)

    for change_id in target_change_ids:
        visit(change_id)

    scoped_series: list[SeriesSnapshot] = []
    for series in snapshot.series:
        scoped_changes = [change for change in series.changes if change.change_id in selected]
        if not scoped_changes:
            continue
        scoped_series.append(
            SeriesSnapshot(
                name=series.name,
                changes=scoped_changes,
                dependency_file=series.dependency_file,
            )
        )

    return WorkspaceSnapshot(
        workspace_root=snapshot.workspace_root,
        generated_at=snapshot.generated_at,
        active_changes_root=snapshot.active_changes_root,
        logs_root=snapshot.logs_root,
        series=scoped_series,
    )
