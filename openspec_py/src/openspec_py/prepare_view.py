from __future__ import annotations

from collections import defaultdict
from textwrap import shorten

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table

from openspec_py.preparation import PreparationItem, PreparationSession

PREPARATION_STYLE = {
    "pending_preparation": "bright_green",
    "dry_run": "bright_green",
    "already_running": "cyan",
    "waiting_capacity": "magenta",
    "waiting_dependencies": "yellow",
    "blocked": "yellow",
    "halted": "bold red",
    "completed": "green",
    "preparing": "cyan",
    "prepared": "green",
    "failed_preparation": "red",
}


def _style(prep_state: str) -> str:
    return PREPARATION_STYLE.get(prep_state, "white")


def _summary_panel(session: PreparationSession) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(style="bold", no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_row("Workspace", str(session.workspace_root))
    grid.add_row("Repo", str(session.repo_root))
    grid.add_row("Generated", session.generated_at.strftime("%Y-%m-%d %H:%M:%S"))
    grid.add_row("Session key", session.session_key)
    grid.add_row("Execute", "yes" if session.execute else "no")
    grid.add_row("Worktree root", str(session.worktree_root))
    grid.add_row("Legacy session", str(session.legacy_session_dir))
    grid.add_row(
        "Parallelism",
        "unlimited" if session.max_parallel <= 0 else str(session.max_parallel),
    )
    grid.add_row(
        "Ports",
        f"base={session.port_block_base}, block_size={session.port_block_size}",
    )
    grid.add_row(
        "Prep states",
        ", ".join(f"{name}={value}" for name, value in session.state_counts.items()) or "-",
    )
    return Panel(grid, title="Preparation Summary", expand=True)


def _overview_table(session: PreparationSession) -> Table:
    grouped: dict[str, list[PreparationItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.series].append(item)

    states = [
        "pending_preparation",
        "dry_run",
        "already_running",
        "waiting_capacity",
        "waiting_dependencies",
        "preparing",
        "prepared",
        "failed_preparation",
    ]
    table = Table(title="Series Preparation Allocation", expand=True)
    table.add_column("Series", style="bold")
    for state in states:
        table.add_column(state, justify="right")

    for series_name in sorted(grouped):
        counts = defaultdict(int)
        for item in grouped[series_name]:
            counts[item.prep_state] += 1
        table.add_row(series_name, *(str(counts[state]) for state in states))
    return table


def _items_panel(title: str, prep_state: str, items: list[PreparationItem]) -> Panel:
    if not items:
        return Panel("None", title=title, border_style=_style(prep_state), expand=True)

    table = Table(expand=True)
    table.add_column("Series", style="bold")
    table.add_column("Step", no_wrap=True)
    table.add_column("Current", no_wrap=True)
    table.add_column("Ref / Branch")
    table.add_column("Reason")

    for item in items:
        step = f"{item.step:02d}" if item.step is not None else item.change_id
        refs = [item.base_ref] if item.base_ref else []
        if item.integration_branch:
            refs.append(item.integration_branch)
        if item.implementation_branch:
            refs.append(item.implementation_branch)
        ref_text = " -> ".join(refs) if refs else "-"

        if item.notes:
            reason = shorten(" | ".join(item.notes), width=104, placeholder="...")
        else:
            reason = item.reason
        if item.worktree_path and prep_state in {"prepared", "preparing", "failed_preparation"}:
            reason = (
                f"{reason} | worktree={shorten(str(item.worktree_path), width=36, placeholder='...')}"
            )
        table.add_row(
            item.series,
            step,
            item.current_status,
            ref_text,
            reason,
            style=_style(prep_state),
        )

    return Panel(table, title=title, border_style=_style(prep_state), expand=True)


def build_preparation_dashboard(session: PreparationSession) -> RenderableType:
    grouped: dict[str, list[PreparationItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.prep_state].append(item)

    order = [
        "pending_preparation",
        "dry_run",
        "already_running",
        "waiting_capacity",
        "waiting_dependencies",
        "preparing",
        "prepared",
        "failed_preparation",
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


def render_preparation(console: Console, session: PreparationSession) -> None:
    console.print(build_preparation_dashboard(session))
