from __future__ import annotations

from collections import defaultdict
from textwrap import shorten

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table

from openspec_py.merge_queue import MergeQueueItem, MergeQueueSession

ACTION_STYLE = {
    "merge_now": "bright_green",
    "waiting_ready_for_merge": "yellow",
    "halted": "bold red",
    "archived": "green",
    "not_series": "white",
}


def _style(action: str) -> str:
    return ACTION_STYLE.get(action, "white")


def _summary_panel(session: MergeQueueSession) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(style="bold", no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_row("Workspace", str(session.workspace_root))
    grid.add_row("Generated", session.generated_at.strftime("%Y-%m-%d %H:%M:%S"))
    grid.add_row("Session key", session.session_key)
    grid.add_row("Execute", "yes" if session.execute else "no")
    grid.add_row("Archive enabled", "yes" if session.archive_enabled else "no")
    grid.add_row("Cleanup worktrees", "yes" if session.cleanup_worktrees else "no")
    grid.add_row("Handoff cleanup", "yes" if session.handoff_command_template else "no")
    grid.add_row("Merge recovery", "yes" if session.merge_fallback_command_template else "no")
    grid.add_row("Worktree root", str(session.worktree_root))
    grid.add_row("Legacy session", str(session.legacy_session_dir))
    grid.add_row(
        "Actions",
        ", ".join(f"{name}={value}" for name, value in session.action_counts.items()) or "-",
    )
    grid.add_row(
        "Outcomes",
        ", ".join(f"{name}={value}" for name, value in session.outcome_counts.items()) or "-",
    )
    return Panel(grid, title="Merge Queue Summary", expand=True)


def _overview_table(session: MergeQueueSession) -> Table:
    grouped: dict[str, list[MergeQueueItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.series].append(item)

    actions = [
        "merge_now",
        "waiting_ready_for_merge",
        "halted",
        "archived",
        "not_series",
    ]
    table = Table(title="Series Merge Allocation", expand=True)
    table.add_column("Series", style="bold")
    for action in actions:
        table.add_column(action, justify="right")

    for series_name in sorted(grouped):
        counts = defaultdict(int)
        for item in grouped[series_name]:
            counts[item.action] += 1
        table.add_row(series_name, *(str(counts[action]) for action in actions))
    return table


def _items_panel(title: str, action: str, items: list[MergeQueueItem]) -> Panel:
    if not items:
        return Panel("None", title=title, border_style=_style(action), expand=True)

    table = Table(expand=True)
    table.add_column("Series", style="bold")
    table.add_column("Step", no_wrap=True)
    table.add_column("Current", no_wrap=True)
    table.add_column("Latest", no_wrap=True)
    table.add_column("Outcome", no_wrap=True)
    table.add_column("Branches")
    table.add_column("Cleanup", no_wrap=True)
    table.add_column("Reason")

    for item in items:
        step = f"{item.step:02d}" if item.step is not None else item.change_id
        branches = " -> ".join(
            [
                value
                for value in [item.integration_branch, item.implementation_branch]
                if value
            ]
        ) or "-"
        cleanup_parts: list[str] = []
        if item.handoff_state:
            cleanup_parts.append(f"handoff:{item.handoff_state}")
        if item.merge_recovery_state:
            cleanup_parts.append(f"merge:{item.merge_recovery_state}")
        if item.branch_cleanup_state:
            cleanup_parts.append(f"branch:{item.branch_cleanup_state}")
        if item.worktree_cleanup_state:
            cleanup_parts.append(f"worktree:{item.worktree_cleanup_state}")
        cleanup = ", ".join(cleanup_parts) if cleanup_parts else "-"
        reason = item.reason
        if item.notes:
            reason = f"{reason} | {shorten(' | '.join(item.notes), width=56, placeholder='...')}"
        table.add_row(
            item.series,
            step,
            item.current_status,
            item.latest_result_status or "-",
            item.outcome,
            branches,
            cleanup,
            reason,
            style=_style(action),
        )

    return Panel(table, title=title, border_style=_style(action), expand=True)


def build_merge_dashboard(session: MergeQueueSession) -> RenderableType:
    grouped: dict[str, list[MergeQueueItem]] = defaultdict(list)
    for item in session.items:
        grouped[item.action].append(item)

    order = [
        "merge_now",
        "waiting_ready_for_merge",
        "halted",
        "archived",
        "not_series",
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


def render_merge_queue(console: Console, session: MergeQueueSession) -> None:
    console.print(build_merge_dashboard(session))
