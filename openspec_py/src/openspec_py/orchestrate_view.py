from __future__ import annotations

from collections import defaultdict
from textwrap import shorten

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from openspec_py.orchestrator import OrchestrationItem, OrchestrationSession

ACTION_STYLE = {
    "launch_now": "bright_green",
    "keep_running": "cyan",
    "wait_capacity": "magenta",
    "wait_dependencies": "yellow",
    "blocked": "yellow",
    "halted": "bold red",
    "completed": "green",
}


def _style(action: str) -> str:
    return ACTION_STYLE.get(action, "white")


def _summary_panel(session: OrchestrationSession) -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column()
    grid.add_row("Workspace", str(session.workspace_root))
    grid.add_row("Generated", session.generated_at.strftime("%Y-%m-%d %H:%M:%S"))
    grid.add_row("Session key", session.session_key)
    grid.add_row("Dry run", "yes" if session.dry_run else "no")
    grid.add_row(
        "Parallelism",
        "unlimited" if session.max_parallel <= 0 else str(session.max_parallel),
    )
    grid.add_row("Available slots", str(session.available_slots))
    grid.add_row(
        "Actions",
        ", ".join(f"{name}={value}" for name, value in session.action_counts.items()) or "-",
    )
    return Panel(grid, title="Orchestration Summary", expand=True)


def _overview_table(session: OrchestrationSession) -> Table:
    grouped: dict[str, list[OrchestrationItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.series].append(item)

    table = Table(title="Series Batch Allocation", expand=True)
    table.add_column("Series", style="bold")
    for name in [
        "launch_now",
        "keep_running",
        "wait_capacity",
        "wait_dependencies",
        "blocked",
        "halted",
        "completed",
    ]:
        table.add_column(name, justify="right")

    for series_name in sorted(grouped):
        counts = defaultdict(int)
        for item in grouped[series_name]:
            counts[item.action] += 1
        table.add_row(
            series_name,
            str(counts["launch_now"]),
            str(counts["keep_running"]),
            str(counts["wait_capacity"]),
            str(counts["wait_dependencies"]),
            str(counts["blocked"]),
            str(counts["halted"]),
            str(counts["completed"]),
        )
    return table


def _items_panel(title: str, action: str, items: list[OrchestrationItem]) -> Panel:
    if not items:
        return Panel("None", title=title, border_style=_style(action), expand=True)

    table = Table(expand=True)
    table.add_column("Series", style="bold")
    table.add_column("Step", no_wrap=True)
    table.add_column("Wave", no_wrap=True)
    table.add_column("Current", no_wrap=True)
    table.add_column("Reason")

    for item in items:
        step = f"{item.step:02d}" if item.step is not None else item.change_id
        wave = "-" if item.wave is None else str(item.wave)
        reason = item.reason
        if item.next_task and item.action in {"launch_now", "keep_running", "wait_capacity"}:
            reason = f"{reason} | next: {shorten(item.next_task, width=72, placeholder='...')}"
        elif item.blockers:
            reason = f"{reason} | blockers: {', '.join(item.blockers)}"
        table.add_row(
            item.series,
            step,
            wave,
            item.current_status,
            reason,
            style=_style(action),
        )

    return Panel(table, title=title, border_style=_style(action), expand=True)


def build_orchestration_dashboard(session: OrchestrationSession) -> RenderableType:
    grouped: dict[str, list[OrchestrationItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.action].append(item)

    order = [
        "launch_now",
        "keep_running",
        "wait_capacity",
        "wait_dependencies",
        "blocked",
        "halted",
        "completed",
    ]
    renderables: list[RenderableType] = [
        _summary_panel(session),
        _overview_table(session),
    ]
    for action in order:
        renderables.append(
            _items_panel(
                action.replace("_", " ").title(),
                action,
                grouped.get(action, []),
            )
        )
    return Group(*renderables)


def render_orchestration(console: Console, session: OrchestrationSession) -> None:
    console.print(build_orchestration_dashboard(session))
