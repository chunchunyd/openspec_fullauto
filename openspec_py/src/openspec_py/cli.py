from __future__ import annotations

import argparse
import time
import threading
from pathlib import Path

from rich.console import Console
from rich.live import Live

from openspec_py.dashboard import build_dashboard, render_dashboard
from openspec_py.finalize_view import build_finalize_dashboard, render_finalize
from openspec_py.finalizer import (
    build_finalize_session,
    execute_finalize_session,
    write_finalize_session,
)
from openspec_py.launch_view import build_launch_dashboard, render_launch
from openspec_py.launcher import (
    build_launch_session,
    execute_launch_session,
    write_launch_session,
)
from openspec_py.merge_queue import (
    build_merge_queue_session,
    execute_merge_queue_session,
    write_merge_queue_session,
)
from openspec_py.merge_view import build_merge_dashboard, render_merge_queue
from openspec_py.orchestrate_view import render_orchestration
from openspec_py.orchestrator import (
    build_orchestration_session,
    write_orchestration_session,
)
from openspec_py.plan_view import render_plan
from openspec_py.planner import build_execution_plan, write_execution_plan
from openspec_py.prepare_view import build_preparation_dashboard, render_preparation
from openspec_py.preparation import (
    build_preparation_session,
    execute_preparation_session,
    write_preparation_session,
)
from openspec_py.run_view import build_run_dashboard
from openspec_py.run_workflow import (
    build_run_session,
    execute_run_session,
    write_run_session,
)
from openspec_py.scanner import build_workspace_snapshot
from openspec_py.scope import ScopeSelectionError
from openspec_py.snapshot import write_snapshot
from openspec_py.workspace import WorkspaceDiscoveryError, discover_workspace_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openspec-auto",
        description="Python tooling for OpenSpec workflow visibility and orchestration.",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Optional workspace root. Defaults to auto-discovery.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Render the active series dashboard.",
    )
    dashboard_parser.add_argument(
        "--series",
        action="append",
        default=[],
        help="Filter to one or more series prefixes.",
    )
    dashboard_parser.add_argument(
        "--watch",
        action="store_true",
        help="Refresh the dashboard continuously.",
    )
    dashboard_parser.add_argument(
        "--interval",
        type=float,
        default=3.0,
        help="Refresh interval in seconds when --watch is enabled.",
    )
    dashboard_parser.add_argument(
        "--snapshot-path",
        type=Path,
        help="Write the structured snapshot JSON to this path on each refresh.",
    )

    snapshot_parser = subparsers.add_parser(
        "snapshot",
        help="Write a structured snapshot JSON without the Rich dashboard.",
    )
    snapshot_parser.add_argument(
        "--series",
        action="append",
        default=[],
        help="Filter to one or more series prefixes.",
    )
    snapshot_parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime/latest-status.json"),
        help="Output JSON path, relative to openspec_py/ when not absolute.",
    )

    plan_parser = subparsers.add_parser(
        "plan",
        help="Build and render an execution plan from the current workspace state.",
    )
    plan_parser.add_argument(
        "--series",
        action="append",
        default=[],
        help="Filter to one or more series prefixes.",
    )
    plan_parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime/latest-plan.json"),
        help="Output JSON path, relative to openspec_py/ when not absolute.",
    )

    orchestrate_parser = subparsers.add_parser(
        "orchestrate",
        help="Build a dry-run orchestration batch from the current execution plan.",
    )
    orchestrate_parser.add_argument(
        "--series",
        action="append",
        default=[],
        help="Filter to one or more series prefixes.",
    )
    orchestrate_parser.add_argument(
        "--max-parallel",
        type=int,
        default=0,
        help="Parallelism cap. Use 0 for unlimited.",
    )
    orchestrate_parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime/latest-orchestration.json"),
        help="Output JSON path, relative to openspec_py/ when not absolute.",
    )

    prepare_parser = subparsers.add_parser(
        "prepare",
        help="Prepare isolated worktrees, session files, and branch context for the next launch batch.",
    )
    prepare_parser.add_argument(
        "--series",
        action="append",
        default=[],
        help="Filter to one or more series prefixes.",
    )
    prepare_parser.add_argument(
        "--max-parallel",
        type=int,
        default=0,
        help="Parallelism cap. Use 0 for unlimited.",
    )
    prepare_parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually create worktrees, allocate ports, and switch branches.",
    )
    prepare_parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime/latest-preparation.json"),
        help="Output JSON path, relative to openspec_py/ when not absolute.",
    )

    launch_parser = subparsers.add_parser(
        "launch",
        help="Build or execute the current launch batch from the orchestration session.",
    )
    launch_parser.add_argument(
        "--series",
        action="append",
        default=[],
        help="Filter to one or more series prefixes.",
    )
    launch_parser.add_argument(
        "--max-parallel",
        type=int,
        default=0,
        help="Parallelism cap. Use 0 for unlimited.",
    )
    launch_parser.add_argument(
        "--command-template",
        required=True,
        help=(
            "Command template for launch_now items. Supported placeholders: "
            "__CHANGE_ID__, __CHANGE_PATH__, __WORKTREE_PATH__, __EXECUTION_PATH__, "
            "__WORKTREE_CHANGE_PATH__, __SERIES__, __STEP__, __NEXT_TASK__, "
            "__PORT_PROFILE__, __IMPL_BRANCH__, __INTEGRATION_BRANCH__. "
            "The template is executed through the system shell."
        ),
    )
    launch_parser.add_argument(
        "--prepare-worktrees",
        action="store_true",
        help="Prepare isolated worktrees and series branch context before building the launch batch.",
    )
    launch_parser.add_argument(
        "--retry-limit",
        type=int,
        default=0,
        help="How many additional incomplete retries to allow per change after the first execution attempt.",
    )
    launch_parser.add_argument(
        "--task-sync-command-template",
        help=(
            "Optional command template to run when tasks remain incomplete after the main launch command. "
            "Supports the same placeholders as --command-template."
        ),
    )
    launch_parser.add_argument(
        "--assessment-command-template",
        help=(
            "Optional command template that must output NEEDS_HUMAN / REASON / NEXT_ACTION lines "
            "when tasks remain incomplete. Supports the same placeholders as --command-template."
        ),
    )
    launch_parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the launch batch. Without this flag the command is dry-run only.",
    )
    launch_parser.add_argument(
        "--preparation-output",
        type=Path,
        default=Path("runtime/latest-preparation.json"),
        help="Preparation session JSON path, relative to openspec_py/ when not absolute.",
    )
    launch_parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime/latest-launch.json"),
        help="Output JSON path, relative to openspec_py/ when not absolute.",
    )

    finalize_parser = subparsers.add_parser(
        "finalize",
        help="Validate runnable changes and optionally move them to ready_for_merge / success / archive.",
    )
    finalize_parser.add_argument(
        "--series",
        action="append",
        default=[],
        help="Filter to one or more series prefixes.",
    )
    finalize_parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually run validate and write shell-compatible result states.",
    )
    finalize_parser.add_argument(
        "--strict",
        action="store_true",
        help="Run OpenSpec validation in strict mode.",
    )
    finalize_parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip OpenSpec validate and only perform the final state write when eligible.",
    )
    finalize_parser.add_argument(
        "--archive",
        action="store_true",
        help="Archive task-complete non-series changes after validation.",
    )
    finalize_parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime/latest-finalize.json"),
        help="Output JSON path, relative to openspec_py/ when not absolute.",
    )

    merge_parser = subparsers.add_parser(
        "merge-queue",
        help="Inspect or execute the parent-managed series merge queue.",
    )
    merge_parser.add_argument(
        "--series",
        action="append",
        default=[],
        help="Filter to one or more series prefixes.",
    )
    merge_parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform queued series merges.",
    )
    merge_parser.add_argument(
        "--archive",
        action="store_true",
        help="Archive successfully merged changes after the merge step.",
    )
    merge_parser.add_argument(
        "--cleanup-worktrees",
        action="store_true",
        help="Remove clean isolated worktrees after a successful merge+archive.",
    )
    merge_parser.add_argument(
        "--handoff-command-template",
        help=(
            "Optional command template to run when the implementation branch is still dirty "
            "before merge. Supports __CHANGE_ID__, __WORKTREE_PATH__, __TASKS_PATH__, "
            "__IMPL_BRANCH__, __INTEGRATION_BRANCH__, and __HANDOFF_LOG__."
        ),
    )
    merge_parser.add_argument(
        "--merge-fallback-command-template",
        help=(
            "Optional command template to run when the parent-managed merge hits conflicts or an "
            "existing in-progress merge must be resumed. Supports __CHANGE_ID__, __WORKTREE_PATH__, "
            "__TASKS_PATH__, __IMPL_BRANCH__, __INTEGRATION_BRANCH__, __MERGE_LOG__, and "
            "__MERGE_COMMIT_MESSAGE__."
        ),
    )
    merge_parser.add_argument(
        "--output",
        type=Path,
        default=Path("runtime/latest-merge-queue.json"),
        help="Output JSON path, relative to openspec_py/ when not absolute.",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Continuously execute the Python orchestration loop across launch, finalize, and merge stages.",
    )
    run_parser.add_argument("--series", action="append", default=[], help="Filter to one or more series prefixes.")
    run_parser.add_argument("--change", action="append", default=[], help="Limit the run to one or more target changes plus their transitive active dependencies.")
    run_parser.add_argument("--max-parallel", type=int, default=0, help="Parallelism cap for each orchestration cycle. Use 0 for unlimited.")
    run_parser.add_argument("--command-template", required=True, help="Command template for launch_now items.")
    run_parser.add_argument("--task-sync-command-template", help="Optional command template to run after launch when tasks remain incomplete.")
    run_parser.add_argument("--assessment-command-template", help="Optional assessment command template for incomplete launch items.")
    run_parser.add_argument("--retry-limit", type=int, default=0, help="How many additional incomplete retries to allow per change after the first execution attempt.")
    run_parser.add_argument("--prepare-worktrees", action="store_true", help="Prepare isolated worktrees before each launch cycle.")
    run_parser.add_argument("--strict", action="store_true", help="Run OpenSpec validation in strict mode during finalize.")
    run_parser.add_argument("--skip-validate", action="store_true", help="Skip OpenSpec validate and only perform final state writes when eligible.")
    run_parser.add_argument("--archive", action="store_true", help="Archive eligible changes after finalize or merge.")
    run_parser.add_argument("--cleanup-worktrees", action="store_true", help="Remove clean isolated worktrees after a successful merge+archive.")
    run_parser.add_argument("--handoff-command-template", help="Optional command template to clean a dirty implementation branch before merge.")
    run_parser.add_argument("--merge-fallback-command-template", help="Optional command template to recover a conflicted parent-managed merge.")
    run_parser.add_argument("--poll-interval", type=float, default=3.0, help="Seconds to wait between cycles when the workflow keeps running.")
    run_parser.add_argument("--max-cycles", type=int, default=1, help="Maximum number of orchestration cycles to run.")
    run_parser.add_argument("--stop-when-idle", action="store_true", help="Stop early once no launchable or in-progress work remains.")
    run_parser.add_argument("--execute", action="store_true", help="Actually run the loop. Without this flag the command only performs dry-run planning cycles.")

    return parser


def _resolve_snapshot_path(base: Path, value: Path | None) -> Path | None:
    if value is None:
        return None
    if value.is_absolute():
        return value
    return (base / value).resolve()


def _series_filter(values: list[str]) -> set[str] | None:
    cleaned = {value.strip() for value in values if value.strip()}
    return cleaned or None


def _write_snapshot_if_requested(snapshot_path: Path | None, paths, snapshot) -> None:
    if snapshot_path is None:
        return
    write_snapshot(snapshot, snapshot_path, paths.runtime_root)


def _run_dashboard(args: argparse.Namespace) -> int:
    paths = discover_workspace_paths(args.workspace_root)
    console = Console()
    series_filter = _series_filter(args.series)
    snapshot_path = _resolve_snapshot_path(
        paths.workspace_root / "openspec_py", args.snapshot_path
    )

    if args.watch:
        refresh_interval = max(args.interval, 0.5)
        try:
            with Live(console=console, refresh_per_second=4, screen=False) as live:
                while True:
                    snapshot = build_workspace_snapshot(paths, series_filter)
                    _write_snapshot_if_requested(snapshot_path, paths, snapshot)
                    live.update(build_dashboard(snapshot), refresh=True)
                    time.sleep(refresh_interval)
        except KeyboardInterrupt:
            console.print("\nStopped dashboard watch.")
            return 0

    snapshot = build_workspace_snapshot(paths, series_filter)
    _write_snapshot_if_requested(snapshot_path, paths, snapshot)
    render_dashboard(console, snapshot)
    return 0


def _run_snapshot(args: argparse.Namespace) -> int:
    paths = discover_workspace_paths(args.workspace_root)
    series_filter = _series_filter(args.series)
    output = _resolve_snapshot_path(paths.workspace_root / "openspec_py", args.output)
    snapshot = build_workspace_snapshot(paths, series_filter)
    changed = write_snapshot(snapshot, output, paths.runtime_root)
    Console().print(
        f"Wrote snapshot to {output}" if changed else f"Snapshot already up to date: {output}"
    )
    return 0


def _run_plan(args: argparse.Namespace) -> int:
    paths = discover_workspace_paths(args.workspace_root)
    series_filter = _series_filter(args.series)
    output = _resolve_snapshot_path(paths.workspace_root / "openspec_py", args.output)
    snapshot = build_workspace_snapshot(paths, series_filter)
    plan = build_execution_plan(snapshot)
    changed = write_execution_plan(plan, output, paths.runtime_root)
    console = Console()
    render_plan(console, plan)
    console.print(
        f"\nWrote plan to {output}" if changed else f"\nPlan already up to date: {output}"
    )
    return 0


def _run_orchestrate(args: argparse.Namespace) -> int:
    paths = discover_workspace_paths(args.workspace_root)
    series_filter = _series_filter(args.series)
    output = _resolve_snapshot_path(paths.workspace_root / "openspec_py", args.output)
    snapshot = build_workspace_snapshot(paths, series_filter)
    plan = build_execution_plan(snapshot)
    session = build_orchestration_session(
        plan,
        max_parallel=args.max_parallel,
        dry_run=True,
    )
    result = write_orchestration_session(session, output, paths.runtime_root)
    console = Console()
    render_orchestration(console, session)
    console.print(
        (
            f"\nWrote orchestration session to {result.latest_path}"
            f"\nHistory record: {result.history_path}"
        )
        if result.changed
        else (
            f"\nOrchestration session already up to date: {result.latest_path}"
            f"\nHistory record refreshed: {result.history_path}"
        )
    )
    return 0


def _run_prepare(args: argparse.Namespace) -> int:
    paths = discover_workspace_paths(args.workspace_root)
    series_filter = _series_filter(args.series)
    output = _resolve_snapshot_path(paths.workspace_root / "openspec_py", args.output)
    snapshot = build_workspace_snapshot(paths, series_filter)
    plan = build_execution_plan(snapshot)
    orchestration = build_orchestration_session(
        plan,
        max_parallel=args.max_parallel,
        dry_run=not args.execute,
    )
    session = build_preparation_session(
        orchestration,
        execute=args.execute,
    )
    initial_write = write_preparation_session(
        session,
        output,
        paths.runtime_root,
        event_name="preparation_session_planned",
    )

    console = Console()
    if args.execute:
        worker = threading.Thread(
            target=execute_preparation_session,
            args=(session, paths.runtime_root),
            daemon=True,
        )
        worker.start()
        with Live(
            build_preparation_dashboard(session),
            console=console,
            refresh_per_second=4,
            screen=False,
        ) as live:
            while worker.is_alive():
                live.update(build_preparation_dashboard(session), refresh=True)
                time.sleep(0.25)
            worker.join()
            live.update(build_preparation_dashboard(session), refresh=True)

        final_write = write_preparation_session(
            session,
            output,
            paths.runtime_root,
            event_name="preparation_session_completed",
        )
        console.print(
            (
                f"\nPlanned session: {initial_write.history_path}"
                f"\nCompleted session: {final_write.history_path}"
                f"\nLatest preparation state: {final_write.latest_path}"
            )
        )
        return 0

    render_preparation(console, session)
    console.print(
        (
            f"\nWrote preparation session to {initial_write.latest_path}"
            f"\nHistory record: {initial_write.history_path}"
        )
    )
    return 0


def _run_launch(args: argparse.Namespace) -> int:
    paths = discover_workspace_paths(args.workspace_root)
    series_filter = _series_filter(args.series)
    output = _resolve_snapshot_path(paths.workspace_root / "openspec_py", args.output)
    preparation_output = _resolve_snapshot_path(
        paths.workspace_root / "openspec_py",
        args.preparation_output,
    )
    snapshot = build_workspace_snapshot(paths, series_filter)
    plan = build_execution_plan(snapshot)
    orchestration = build_orchestration_session(
        plan,
        max_parallel=args.max_parallel,
        dry_run=not args.execute,
    )
    preparation_session = None
    preparation_write = None
    if args.prepare_worktrees:
        preparation_session = build_preparation_session(
            orchestration,
            execute=args.execute,
        )
        preparation_write = write_preparation_session(
            preparation_session,
            preparation_output,
            paths.runtime_root,
            event_name="preparation_session_planned",
        )
        if args.execute:
            execute_preparation_session(preparation_session, paths.runtime_root)
            preparation_write = write_preparation_session(
                preparation_session,
                preparation_output,
                paths.runtime_root,
                event_name="preparation_session_completed",
            )
    session = build_launch_session(
        orchestration,
        command_template=args.command_template,
        execute=args.execute,
        retry_limit=args.retry_limit,
        task_sync_command_template=args.task_sync_command_template,
        assessment_command_template=args.assessment_command_template,
        preparation_session=preparation_session,
    )
    initial_write = write_launch_session(
        session,
        output,
        paths.runtime_root,
        event_name="launch_session_planned",
    )

    console = Console()
    if args.execute:
        worker = threading.Thread(
            target=execute_launch_session,
            args=(session, paths.runtime_root),
            daemon=True,
        )
        worker.start()
        with Live(build_launch_dashboard(session), console=console, refresh_per_second=4, screen=False) as live:
            while worker.is_alive():
                live.update(build_launch_dashboard(session), refresh=True)
                time.sleep(0.25)
            worker.join()
            live.update(build_launch_dashboard(session), refresh=True)

        final_write = write_launch_session(
            session,
            output,
            paths.runtime_root,
            event_name="launch_session_completed",
        )
        prep_summary = (
            f"\nPreparation session: {preparation_write.history_path}"
            if preparation_write is not None
            else ""
        )
        console.print(
            (
                f"{prep_summary}"
                f"\nPlanned session: {initial_write.history_path}"
                f"\nCompleted session: {final_write.history_path}"
                f"\nLatest launch state: {final_write.latest_path}"
            )
        )
        return 0

    render_launch(console, session)
    prep_summary = (
        f"\nPreparation session: {preparation_write.history_path}"
        if preparation_write is not None
        else ""
    )
    console.print(
        (
            f"{prep_summary}"
            f"\nWrote launch session to {initial_write.latest_path}"
            f"\nHistory record: {initial_write.history_path}"
        )
    )
    return 0


def _run_finalize(args: argparse.Namespace) -> int:
    paths = discover_workspace_paths(args.workspace_root)
    series_filter = _series_filter(args.series)
    output = _resolve_snapshot_path(paths.workspace_root / "openspec_py", args.output)
    snapshot = build_workspace_snapshot(paths, series_filter)
    session = build_finalize_session(
        snapshot,
        execute=args.execute,
        strict_validate=args.strict,
        skip_validate=args.skip_validate,
        archive_enabled=args.archive,
    )
    initial_write = write_finalize_session(
        session,
        output,
        paths.runtime_root,
        event_name="finalize_session_planned",
    )

    console = Console()
    if args.execute:
        worker = threading.Thread(
            target=execute_finalize_session,
            args=(session, paths.runtime_root),
            daemon=True,
        )
        worker.start()
        with Live(
            build_finalize_dashboard(session),
            console=console,
            refresh_per_second=4,
            screen=False,
        ) as live:
            while worker.is_alive():
                live.update(build_finalize_dashboard(session), refresh=True)
                time.sleep(0.25)
            worker.join()
            live.update(build_finalize_dashboard(session), refresh=True)

        final_write = write_finalize_session(
            session,
            output,
            paths.runtime_root,
            event_name="finalize_session_completed",
        )
        console.print(
            (
                f"\nPlanned session: {initial_write.history_path}"
                f"\nCompleted session: {final_write.history_path}"
                f"\nLatest finalize state: {final_write.latest_path}"
            )
        )
        return 0

    render_finalize(console, session)
    console.print(
        (
            f"\nWrote finalize session to {initial_write.latest_path}"
            f"\nHistory record: {initial_write.history_path}"
        )
    )
    return 0


def _run_merge_queue(args: argparse.Namespace) -> int:
    paths = discover_workspace_paths(args.workspace_root)
    series_filter = _series_filter(args.series)
    output = _resolve_snapshot_path(paths.workspace_root / "openspec_py", args.output)
    snapshot = build_workspace_snapshot(paths, series_filter)
    session = build_merge_queue_session(
        snapshot,
        execute=args.execute,
        archive_enabled=args.archive,
        cleanup_worktrees=args.cleanup_worktrees,
        handoff_command_template=args.handoff_command_template,
        merge_fallback_command_template=args.merge_fallback_command_template,
    )
    initial_write = write_merge_queue_session(
        session,
        output,
        paths.runtime_root,
        event_name="merge_queue_planned",
    )

    console = Console()
    if args.execute:
        worker = threading.Thread(
            target=execute_merge_queue_session,
            args=(session, paths.runtime_root),
            daemon=True,
        )
        worker.start()
        with Live(
            build_merge_dashboard(session),
            console=console,
            refresh_per_second=4,
            screen=False,
        ) as live:
            while worker.is_alive():
                live.update(build_merge_dashboard(session), refresh=True)
                time.sleep(0.25)
            worker.join()
            live.update(build_merge_dashboard(session), refresh=True)

        final_write = write_merge_queue_session(
            session,
            output,
            paths.runtime_root,
            event_name="merge_queue_completed",
        )
        console.print(
            (
                f"\nPlanned session: {initial_write.history_path}"
                f"\nCompleted session: {final_write.history_path}"
                f"\nLatest merge queue state: {final_write.latest_path}"
            )
        )
        return 0

    render_merge_queue(console, session)
    console.print(
        (
            f"\nWrote merge queue session to {initial_write.latest_path}"
            f"\nHistory record: {initial_write.history_path}"
        )
    )
    return 0


def _run_workflow(args: argparse.Namespace) -> int:
    paths = discover_workspace_paths(args.workspace_root)
    series_filter = _series_filter(args.series)
    session = build_run_session(
        paths,
        execute=args.execute,
        series_filters=series_filter,
        target_change_ids=[value.strip() for value in args.change if value.strip()],
        max_parallel=args.max_parallel,
        command_template=args.command_template,
        task_sync_command_template=args.task_sync_command_template,
        assessment_command_template=args.assessment_command_template,
        retry_limit=args.retry_limit,
        strict_validate=args.strict,
        skip_validate=args.skip_validate,
        archive_enabled=args.archive,
        cleanup_worktrees=args.cleanup_worktrees,
        prepare_worktrees=args.prepare_worktrees,
        handoff_command_template=args.handoff_command_template,
        merge_fallback_command_template=args.merge_fallback_command_template,
        poll_interval_seconds=args.poll_interval,
        max_cycles=args.max_cycles,
        stop_when_idle=args.stop_when_idle,
    )
    initial_write = write_run_session(
        session,
        paths.runtime_root,
        event_name="run_session_planned",
    )

    console = Console()
    worker = threading.Thread(
        target=execute_run_session,
        args=(session, paths),
        kwargs={"series_filters": series_filter},
        daemon=True,
    )
    worker.start()
    with Live(
        build_run_dashboard(session),
        console=console,
        refresh_per_second=4,
        screen=False,
    ) as live:
        while worker.is_alive():
            live.update(build_run_dashboard(session), refresh=True)
            time.sleep(0.25)
        worker.join()
        live.update(build_run_dashboard(session), refresh=True)

    final_write = write_run_session(
        session,
        paths.runtime_root,
        event_name="run_session_rendered",
    )
    console.print(
        (
            f"\nPlanned session: {initial_write.history_path}"
            f"\nCompleted session: {final_write.history_path}"
            f"\nLatest run state: {final_write.latest_path}"
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "dashboard":
            return _run_dashboard(args)
        if args.command == "snapshot":
            return _run_snapshot(args)
        if args.command == "plan":
            return _run_plan(args)
        if args.command == "orchestrate":
            return _run_orchestrate(args)
        if args.command == "prepare":
            return _run_prepare(args)
        if args.command == "launch":
            return _run_launch(args)
        if args.command == "finalize":
            return _run_finalize(args)
        if args.command == "merge-queue":
            return _run_merge_queue(args)
        if args.command == "run":
            return _run_workflow(args)
    except WorkspaceDiscoveryError as error:
        Console(stderr=True).print(f"[red]{error}[/red]")
        return 2
    except ScopeSelectionError as error:
        Console(stderr=True).print(f"[red]{error}[/red]")
        return 2

    parser.error(f"Unsupported command: {args.command}")
    return 2
