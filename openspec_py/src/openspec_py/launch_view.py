from __future__ import annotations

from collections import defaultdict
from textwrap import shorten

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table

from openspec_py.launcher import LaunchItem, LaunchSession

RUN_STYLE = {
    "pending_execution": "bright_green",
    "dry_run": "bright_green",
    "already_running": "cyan",
    "waiting_capacity": "magenta",
    "waiting_dependencies": "yellow",
    "failed_preparation": "red",
    "blocked": "yellow",
    "halted": "bold red",
    "completed": "green",
    "running": "cyan",
    "retrying": "magenta",
    "succeeded": "green",
    "failed": "red",
    "needs_human": "bold red",
}


def _style(run_state: str) -> str:
    return RUN_STYLE.get(run_state, "white")


def _summary_panel(session: LaunchSession) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(style="bold", no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_row("Workspace", str(session.workspace_root))
    grid.add_row("Generated", session.generated_at.strftime("%Y-%m-%d %H:%M:%S"))
    grid.add_row("Session key", session.session_key)
    grid.add_row("Execute", "yes" if session.execute else "no")
    grid.add_row(
        "Parallelism",
        "unlimited" if session.max_parallel <= 0 else str(session.max_parallel),
    )
    grid.add_row("Command template", session.command_template)
    grid.add_row("Retry limit", str(session.retry_limit))
    grid.add_row("Task sync", "yes" if session.task_sync_command_template else "no")
    grid.add_row("Assessment", "yes" if session.assessment_command_template else "heuristic")
    grid.add_row("Prepared worktrees", "yes" if session.used_preparation else "no")
    grid.add_row("Legacy session", str(session.legacy_session_dir))
    grid.add_row(
        "Run states",
        ", ".join(f"{name}={value}" for name, value in session.state_counts.items()) or "-",
    )
    return Panel(grid, title="Launch Summary", expand=True)


def _overview_table(session: LaunchSession) -> Table:
    grouped: dict[str, list[LaunchItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.series].append(item)

    states = [
        "pending_execution",
        "dry_run",
        "already_running",
        "waiting_capacity",
        "waiting_dependencies",
        "failed_preparation",
        "running",
        "retrying",
        "succeeded",
        "failed",
        "needs_human",
    ]
    table = Table(title="Series Launch Allocation", expand=True)
    table.add_column("Series", style="bold")
    for state in states:
        table.add_column(state, justify="right")

    for series_name in sorted(grouped):
        counts = defaultdict(int)
        for item in grouped[series_name]:
            counts[item.run_state] += 1
        table.add_row(series_name, *(str(counts[state]) for state in states))
    return table


def _items_panel(title: str, run_state: str, items: list[LaunchItem]) -> Panel:
    if not items:
        return Panel("None", title=title, border_style=_style(run_state), expand=True)

    table = Table(expand=True)
    table.add_column("Series", style="bold")
    table.add_column("Step", no_wrap=True)
    table.add_column("Try", no_wrap=True)
    table.add_column("Current", no_wrap=True)
    table.add_column("Progress", no_wrap=True)
    table.add_column("Reason")

    for item in items:
        step = f"{item.step:02d}" if item.step is not None else item.change_id
        progress = (
            f"{item.manual_completed}/{item.manual_total}"
            if item.manual_total > 0
            else (
                f"{item.full_completed}/{item.full_total}"
                if item.full_total > 0
                else "-"
            )
        )
        if item.command and run_state in {
            "pending_execution",
            "dry_run",
            "running",
            "retrying",
            "succeeded",
            "failed",
            "needs_human",
        }:
            reason = shorten(item.command, width=84, placeholder="...")
        else:
            reason = item.reason
            if item.next_task and run_state in {"waiting_capacity", "waiting_dependencies", "already_running"}:
                reason = (
                    f"{reason} | next: "
                    f"{shorten(item.next_task, width=72, placeholder='...')}"
                )
        if item.exit_code is not None:
            reason = f"{reason} | exit={item.exit_code}"
        if item.assessment_reason and run_state in {"retrying", "needs_human"}:
            reason = (
                f"{reason} | assess: "
                f"{shorten(item.assessment_reason, width=56, placeholder='...')}"
            )
        table.add_row(
            item.series,
            step,
            str(item.attempt) if item.attempt else "-",
            item.current_status,
            progress,
            reason,
            style=_style(run_state),
        )

    return Panel(table, title=title, border_style=_style(run_state), expand=True)


def build_launch_dashboard(session: LaunchSession) -> RenderableType:
    grouped: dict[str, list[LaunchItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.run_state].append(item)

    order = [
        "pending_execution",
        "dry_run",
        "already_running",
        "waiting_capacity",
        "waiting_dependencies",
        "failed_preparation",
        "running",
        "retrying",
        "succeeded",
        "failed",
        "needs_human",
        "halted",
        "completed",
        "blocked",
    ]
    renderables: list[RenderableType] = [
        _summary_panel(session),
        _overview_table(session),
    ]
    for state in order:
        renderables.append(
            _items_panel(
                state.replace("_", " ").title(),
                state,
                grouped.get(state, []),
            )
        )
    return Group(*renderables)


def render_launch(console: Console, session: LaunchSession) -> None:
    console.print(build_launch_dashboard(session))
