from __future__ import annotations

from collections import defaultdict
from textwrap import shorten

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from openspec_py.planner import ExecutionPlan, PlanItem

PLAN_STYLE = {
    "completed": "green",
    "active": "cyan",
    "ready": "bright_green",
    "queued": "magenta",
    "blocked": "yellow",
    "halted": "bold red",
}


def _style(plan_state: str) -> str:
    return PLAN_STYLE.get(plan_state, "white")


def _summary_panel(plan: ExecutionPlan) -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column()
    grid.add_row("Workspace", str(plan.workspace_root))
    grid.add_row("Generated", plan.generated_at.strftime("%Y-%m-%d %H:%M:%S"))
    grid.add_row("Max wave", str(plan.max_wave))
    grid.add_row(
        "Plan states",
        ", ".join(f"{name}={value}" for name, value in plan.state_counts.items()) or "-",
    )
    return Panel(grid, title="Execution Plan Summary", expand=True)


def _overview_table(plan: ExecutionPlan) -> Table:
    grouped: dict[str, list[PlanItem]] = defaultdict(list)
    for item in plan.items:
        grouped[item.series].append(item)

    table = Table(title="Series Execution Plan", expand=True)
    table.add_column("Series", style="bold")
    table.add_column("Ready", justify="right")
    table.add_column("Active", justify="right")
    table.add_column("Queued", justify="right")
    table.add_column("Blocked", justify="right")
    table.add_column("Halted", justify="right")
    table.add_column("Completed", justify="right")

    for series_name in sorted(grouped):
        states = defaultdict(int)
        for item in grouped[series_name]:
            states[item.plan_state] += 1
        table.add_row(
            series_name,
            str(states["ready"]),
            str(states["active"]),
            str(states["queued"]),
            str(states["blocked"]),
            str(states["halted"]),
            str(states["completed"]),
        )
    return table


def _items_panel(title: str, items: list[PlanItem], plan_state: str) -> Panel:
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
        if item.plan_state in {"ready", "active", "queued"} and item.next_task:
            reason = f"{reason} | next: {shorten(item.next_task, width=72, placeholder='...')}"
        elif item.blockers:
            reason = f"{reason} | blockers: {', '.join(item.blockers)}"

        table.add_row(
            item.series,
            step,
            wave,
            item.current_status,
            reason,
            style=_style(plan_state),
        )

    if not items:
        return Panel("None", title=title, border_style=_style(plan_state), expand=True)

    return Panel(table, title=title, border_style=_style(plan_state), expand=True)


def build_plan_dashboard(plan: ExecutionPlan) -> RenderableType:
    grouped_by_state: dict[str, list[PlanItem]] = defaultdict(list)
    for item in plan.items:
        grouped_by_state[item.plan_state].append(item)

    order = ["ready", "active", "queued", "blocked", "halted", "completed"]
    renderables: list[RenderableType] = [
        _summary_panel(plan),
        _overview_table(plan),
    ]
    for state in order:
        renderables.append(
            _items_panel(
                f"{state.title()} Changes",
                grouped_by_state.get(state, []),
                state,
            )
        )
    return Group(*renderables)


def render_plan(console: Console, plan: ExecutionPlan) -> None:
    console.print(build_plan_dashboard(plan))
