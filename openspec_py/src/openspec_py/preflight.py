from __future__ import annotations

from openspec_py.models import WorkspaceSnapshot


class PreflightError(RuntimeError):
    """Raised when the workspace state cannot safely enter automated execution."""


def validate_workspace_snapshot(snapshot: WorkspaceSnapshot) -> None:
    change_map = {
        change.change_id: change
        for series in snapshot.series
        for change in series.changes
    }

    missing_dependencies: list[str] = []
    cross_series_dependencies: list[str] = []

    for change in change_map.values():
        for dependency in change.dependencies:
            dep_change = change_map.get(dependency)
            if dep_change is None:
                if dependency in change.unmet_dependencies:
                    missing_dependencies.append(f"{change.change_id} -> {dependency}")
                continue
            if dep_change.series != change.series:
                cross_series_dependencies.append(
                    f"{change.change_id} -> {dependency} ({change.series} != {dep_change.series})"
                )

    if cross_series_dependencies:
        detail = "; ".join(sorted(dict.fromkeys(cross_series_dependencies)))
        raise PreflightError(f"cross-series dependencies are not allowed: {detail}")

    if missing_dependencies:
        detail = "; ".join(sorted(dict.fromkeys(missing_dependencies)))
        raise PreflightError(
            "dependencies are missing from the current active/archive state or current series filter: "
            f"{detail}"
        )

    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: list[str] = []

    def dfs(change_id: str, stack: list[str]) -> None:
        if change_id in visited or cycles:
            return
        if change_id in visiting:
            if change_id in stack:
                start = stack.index(change_id)
                cycle_path = stack[start:] + [change_id]
                cycles.append(" -> ".join(cycle_path))
            return

        visiting.add(change_id)
        stack.append(change_id)
        change = change_map[change_id]
        for dependency in change.dependencies:
            if dependency in change_map:
                dfs(dependency, stack)
        stack.pop()
        visiting.remove(change_id)
        visited.add(change_id)

    for change_id in sorted(change_map):
        dfs(change_id, [])
        if cycles:
            break

    if cycles:
        raise PreflightError(f"dependency cycle detected: {cycles[0]}")
