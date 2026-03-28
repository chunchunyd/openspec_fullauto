from __future__ import annotations

from textwrap import shorten

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from openspec_py.models import SeriesSnapshot, WorkspaceSnapshot
from openspec_py.parsers import format_relative_time
from openspec_py.scanner import summarize_change_update

STATUS_STYLE = {
    "archived": "green",
    "done": "green",
    "tasks_done": "bright_green",
    "in_progress": "cyan",
    "pending": "white",
    "blocked": "yellow",
    "failed": "red",
    "needs_human": "bold red",
    "ready_for_merge": "magenta",
    "incomplete": "yellow",
    "unknown": "dim",
}


def _style_for_status(status: str) -> str:
    return STATUS_STYLE.get(status, "white")


def _overview_table(snapshot: WorkspaceSnapshot) -> Table:
    table = Table(title="OpenSpec Series Overview", expand=True)
    table.add_column("Series", style="bold")
    table.add_column("Status")
    table.add_column("Changes", justify="right")
    table.add_column("Done", justify="right")
    table.add_column("Manual Tasks", justify="right")
    table.add_column("All Tasks", justify="right")
    table.add_column("Updated", justify="right")

    now = snapshot.generated_at
    for series in snapshot.series:
        updated = format_relative_time(series.latest_update_at, now)
        table.add_row(
            series.name,
            Text(series.status, style=_style_for_status(series.status)),
            str(series.change_count),
            str(series.completed_change_count),
            f"{series.manual_completed}/{series.manual_total}",
            f"{series.full_completed}/{series.full_total}",
            updated,
        )
    return table


def _render_change_table(series: SeriesSnapshot, now) -> Table:
    table = Table(expand=True)
    table.add_column("Step", style="bold", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Deps", justify="right", no_wrap=True)
    table.add_column("Progress", no_wrap=True)
    table.add_column("Next Task", overflow="ellipsis")

    for change in series.changes:
        result = change.latest_result
        step_label = f"{change.step:02d}" if change.step is not None else change.change_id
        deps_label = (
            f"{len(change.dependencies) - len(change.unmet_dependencies)}/{len(change.dependencies)}"
            if change.dependencies
            else "-"
        )
        next_task = "-"
        if change.status == "needs_human" and result and result.human_reason:
            next_task = shorten(result.human_reason, width=88, placeholder="...")
        elif change.tasks.next_pending:
            next_task = shorten(change.tasks.next_pending, width=88, placeholder="...")

        table.add_row(
            step_label,
            Text(change.status, style=_style_for_status(change.status)),
            deps_label,
            (
                f"M {change.tasks.manual_completed}/{change.tasks.manual_total} "
                f"A {change.tasks.automation_completed}/{change.tasks.automation_total}"
            ),
            next_task,
            style=_style_for_status(change.status),
        )

    return table


def _render_series_panel(series: SeriesSnapshot, now) -> Panel:
    subtitle = (
        f"deps: {series.dependency_file.name}"
        if series.dependency_file
        else "deps: none"
    )
    return Panel(
        _render_change_table(series, now),
        title=f"{series.name} [{series.status}]",
        subtitle=subtitle,
        border_style=_style_for_status(series.status),
        expand=True,
    )


def _summary_panel(snapshot: WorkspaceSnapshot) -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column()

    counts = snapshot.status_counts
    grid.add_row("Workspace", str(snapshot.workspace_root))
    grid.add_row("Generated", snapshot.generated_at.strftime("%Y-%m-%d %H:%M:%S"))
    grid.add_row("Active series", str(len(snapshot.series)))
    grid.add_row("Active changes", str(snapshot.active_change_count))
    grid.add_row(
        "Status counts",
        ", ".join(f"{name}={value}" for name, value in counts.items()) or "-",
    )
    return Panel(grid, title="Snapshot Summary", expand=True)


def build_dashboard(snapshot: WorkspaceSnapshot) -> RenderableType:
    if not snapshot.series:
        return Panel("No active OpenSpec changes were found.", title="OpenSpec Dashboard")

    renderables: list[RenderableType] = [
        _summary_panel(snapshot),
        _overview_table(snapshot),
    ]
    now = snapshot.generated_at
    for series in snapshot.series:
        renderables.append(_render_series_panel(series, now))
    return Group(*renderables)


def render_dashboard(console: Console, snapshot: WorkspaceSnapshot) -> None:
    console.print(build_dashboard(snapshot))
