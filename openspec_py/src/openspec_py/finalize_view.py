from __future__ import annotations

from collections import defaultdict
from textwrap import shorten

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table

from openspec_py.finalizer import FinalizeItem, FinalizeSession

ACTION_STYLE = {
    "ready_for_merge": "bright_green",
    "archive": "bright_green",
    "mark_success": "green",
    "pending_tasks": "yellow",
    "running": "cyan",
    "wait_dependencies": "magenta",
    "not_started": "white",
    "archived": "green",
    "halted": "bold red",
}


def _style(action: str) -> str:
    return ACTION_STYLE.get(action, "white")


def _summary_panel(session: FinalizeSession) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(style="bold", no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_row("Workspace", str(session.workspace_root))
    grid.add_row("Generated", session.generated_at.strftime("%Y-%m-%d %H:%M:%S"))
    grid.add_row("Session key", session.session_key)
    grid.add_row("Execute", "yes" if session.execute else "no")
    grid.add_row("Strict validate", "yes" if session.strict_validate else "no")
    grid.add_row("Skip validate", "yes" if session.skip_validate else "no")
    grid.add_row("Archive enabled", "yes" if session.archive_enabled else "no")
    grid.add_row(
        "Actions",
        ", ".join(f"{name}={value}" for name, value in session.action_counts.items()) or "-",
    )
    grid.add_row(
        "Outcomes",
        ", ".join(f"{name}={value}" for name, value in session.outcome_counts.items()) or "-",
    )
    return Panel(grid, title="Finalize Summary", expand=True)


def _overview_table(session: FinalizeSession) -> Table:
    grouped: dict[str, list[FinalizeItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.series].append(item)

    actions = [
        "ready_for_merge",
        "archive",
        "mark_success",
        "pending_tasks",
        "running",
        "wait_dependencies",
        "halted",
    ]
    table = Table(title="Series Finalize Allocation", expand=True)
    table.add_column("Series", style="bold")
    for action in actions:
        table.add_column(action, justify="right")

    for series_name in sorted(grouped):
        counts = defaultdict(int)
        for item in grouped[series_name]:
            counts[item.action] += 1
        table.add_row(series_name, *(str(counts[action]) for action in actions))
    return table


def _items_panel(title: str, action: str, items: list[FinalizeItem]) -> Panel:
    if not items:
        return Panel("None", title=title, border_style=_style(action), expand=True)

    table = Table(expand=True)
    table.add_column("Series", style="bold")
    table.add_column("Step", no_wrap=True)
    table.add_column("Current", no_wrap=True)
    table.add_column("Tasks", no_wrap=True)
    table.add_column("Manual", no_wrap=True)
    table.add_column("Outcome", no_wrap=True)
    table.add_column("Reason")

    for item in items:
        step = f"{item.step:02d}" if item.step is not None else item.change_id
        tasks = f"{item.tasks_completed}/{item.tasks_total}"
        manual = f"{item.manual_completed}/{item.manual_total}"
        reason = item.reason
        if item.notes:
            reason = f"{reason} | {shorten(' | '.join(item.notes), width=52, placeholder='...')}"
        table.add_row(
            item.series,
            step,
            item.current_status,
            tasks,
            manual,
            item.outcome,
            reason,
            style=_style(action),
        )

    return Panel(table, title=title, border_style=_style(action), expand=True)


def build_finalize_dashboard(session: FinalizeSession) -> RenderableType:
    grouped: dict[str, list[FinalizeItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.action].append(item)

    order = [
        "ready_for_merge",
        "archive",
        "mark_success",
        "pending_tasks",
        "running",
        "wait_dependencies",
        "not_started",
        "archived",
        "halted",
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


def render_finalize(console: Console, session: FinalizeSession) -> None:
    console.print(build_finalize_dashboard(session))
