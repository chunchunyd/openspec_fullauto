from __future__ import annotations

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.table import Table

from openspec_py.run_workflow import RunSession


def _fmt_counts(values: dict[str, int]) -> str:
    if not values:
        return "-"
    return ", ".join(f"{key}={value}" for key, value in values.items())


def _summary_panel(session: RunSession) -> Panel:
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(style="bold", no_wrap=True)
    grid.add_column(ratio=1)
    grid.add_row("Workspace", str(session.workspace_root))
    grid.add_row("Session key", session.session_key)
    grid.add_row("State", session.state)
    grid.add_row("Series", ", ".join(session.series_filters) if session.series_filters else "all active series")
    grid.add_row("Execute", "yes" if session.execute else "no")
    grid.add_row("Cycles", f"{session.current_cycle}/{session.max_cycles}")
    grid.add_row("Parallelism", "unlimited" if session.max_parallel <= 0 else str(session.max_parallel))
    grid.add_row("Prepare worktrees", "yes" if session.prepare_worktrees else "no")
    grid.add_row("Archive", "yes" if session.archive_enabled else "no")
    grid.add_row("Cleanup worktrees", "yes" if session.cleanup_worktrees else "no")
    grid.add_row("Poll interval", f"{session.poll_interval_seconds:.1f}s")
    grid.add_row("Stop when idle", "yes" if session.stop_when_idle else "no")
    grid.add_row("Last message", session.last_message or "-")
    return Panel(grid, title="Run Summary", expand=True)


def _latest_stage_panel(session: RunSession) -> Panel:
    table = Table(expand=True)
    table.add_column("Stage", style="bold")
    table.add_column("Counts")
    table.add_row("Snapshot", _fmt_counts(session.latest_snapshot_counts))
    table.add_row("Plan", _fmt_counts(session.latest_plan_counts))
    table.add_row("Orchestration", _fmt_counts(session.latest_orchestration_counts))
    table.add_row("Launch", _fmt_counts(session.latest_launch_counts))
    table.add_row("Finalize", _fmt_counts(session.latest_finalize_counts))
    table.add_row("Merge", _fmt_counts(session.latest_merge_counts))
    return Panel(table, title="Latest Stage Counts", expand=True)


def _cycles_panel(session: RunSession) -> Panel:
    table = Table(expand=True)
    table.add_column("Cycle", justify="right", no_wrap=True)
    table.add_column("Snapshot")
    table.add_column("Plan")
    table.add_column("Launch", no_wrap=True)
    table.add_column("Finalize", no_wrap=True)
    table.add_column("Merge", no_wrap=True)
    table.add_column("Stop")

    recent = session.cycles[-8:]
    for cycle in recent:
        table.add_row(
            str(cycle.index),
            _fmt_counts(cycle.snapshot_status_counts),
            _fmt_counts(cycle.plan_state_counts),
            f"batch={cycle.launched_now}; {_fmt_counts(cycle.launch_state_counts)}",
            _fmt_counts(cycle.finalize_action_counts),
            f"merged={cycle.merged_now}; {_fmt_counts(cycle.merge_outcome_counts)}",
            cycle.stopped_reason or "-",
        )
    if not recent:
        table.add_row("-", "-", "-", "-", "-", "-", "-")
    return Panel(table, title="Recent Cycles", expand=True)


def build_run_dashboard(session: RunSession) -> RenderableType:
    return Group(
        _summary_panel(session),
        _latest_stage_panel(session),
        _cycles_panel(session),
    )


def render_run(console: Console, session: RunSession) -> None:
    console.print(build_run_dashboard(session))
