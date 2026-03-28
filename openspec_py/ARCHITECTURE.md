# Architecture Notes

This document maps the current shell workflow to the new Python framework.

## Current shell responsibilities

The existing `openspec/auto/auto_apply.sh` currently handles:

- CLI argument parsing
- dependency graph loading
- worktree preparation
- branch and merge orchestration
- child agent execution
- retry and incomplete assessment flows
- archive and cleanup decisions
- append-only run logs and `.result` files

## Python migration approach

The Python framework in `openspec_py/` migrates this in layers.

### Layer 1: visibility and state

Implemented in this iteration:

- workspace discovery
- change, task, result, and dependency parsing
- Rich dashboard for active series and change status
- execution plan builder for ready, active, queued, blocked, halted, and completed changes
- dry-run orchestrator that selects the next launch batch under a max-parallel cap
- structured JSON snapshots
- append-only snapshot event log

### Layer 2: orchestration

- subprocess runner abstraction
- session store and state transitions
- retry and assessment pipeline
- worktree and merge services

Partially implemented now:

- dry-run orchestration sessions
- latest orchestration JSON
- timestamped orchestration session history
- worktree/session preparation service
- session-compatible port profile allocation
- `.env` seeding from `.env.example` when available
- managed series branch preparation from standardized `tasks.md` checkboxes
- command-template launch batches with optional execution
- optional worktree-aware launch batches
- per-change launch logs and live terminal run-state display
- optional task-sync and incomplete-assessment command hooks
- launch retry loop with heuristic or external assessment decisions
- OpenSpec CLI service wrapper for validate / archive
- finalize state machine for `pending_tasks / ready_for_merge / success / archive`
- shell-compatible `.result` writeback from both launch and finalize phases
- parent-managed merge queue for `ready_for_merge -> success/archive`
- post-merge full-task verification before success is written
- pre-merge implementation handoff cleanliness checks with optional cleanup hook
- merge-conflict recovery hook for direct merge failures or resumed in-place merges
- post-archive implementation branch cleanup
- optional clean worktree removal after merge+archive

Still planned next:

- real execution state transitions
- tool-specific runner adapters for Claude / OpenSpec / git services
- richer merge-conflict fallback or delegated recovery flows

### Layer 3: feature parity

Planned after the state model is stable:

- full `auto_apply.sh` parity
- parent-managed merge queue
- validation and archive pipeline
- cleanup fallback and branch lifecycle handling

## Module map

- `src/openspec_py/workspace.py`
  - workspace root discovery and path model
- `src/openspec_py/models.py`
  - structured in-memory state
- `src/openspec_py/parsers.py`
  - tasks, result, dependency, and naming parsers
- `src/openspec_py/scanner.py`
  - aggregates the current workspace state
- `src/openspec_py/dashboard.py`
  - Rich table and panel rendering
- `src/openspec_py/snapshot.py`
  - structured JSON snapshot writer
- `src/openspec_py/runtime_logging.py`
  - append-only timestamped event log
- `src/openspec_py/git_ops.py`
  - reusable git and worktree helpers
- `src/openspec_py/git_tasks.py`
  - standardized managed-git checkbox parsing and marking
- `src/openspec_py/preparation.py`
  - worktree/session preparation state model and executor
- `src/openspec_py/prepare_view.py`
  - Rich dashboard for preparation sessions
- `src/openspec_py/legacy_results.py`
  - shell-compatible `.result` file writer for cross-workflow session state
- `src/openspec_py/launch_execution.py`
  - launch execution loop, optional task-sync hooks, assessment hooks, and retry handling
- `src/openspec_py/openspec_cli.py`
  - OpenSpec CLI adapter for validate / archive
- `src/openspec_py/finalizer.py`
  - post-run finalization state model and executor
- `src/openspec_py/finalize_view.py`
  - Rich dashboard for finalize sessions
- `src/openspec_py/merge_queue.py`
  - parent-managed series merge queue state model, post-merge verification, and cleanup executor
- `src/openspec_py/merge_view.py`
  - Rich dashboard for merge-queue sessions
- `src/openspec_py/cli.py`
  - terminal entrypoint

## Snapshot and log files

- `openspec_py/runtime/latest-status.json`
  - last structured snapshot for machines or future UI layers
- `openspec_py/runtime/events.log`
  - timestamped append-only event log for snapshot writes
- `openspec_py/runtime/latest-preparation.json`
  - latest worktree/session preparation state
- `openspec_py/runtime/latest-launch.json`
  - latest launch state, optionally targeting prepared worktrees

These files complement the existing historical logs under
`openspec/auto/logs/`. They do not replace them.

The Python framework now also writes shell-compatible `.result` files back into
`openspec/auto/logs/.auto-apply-run.<session-key>/` so the scanner, planner,
and future merge/archive services can share the same session truth.
## Current runtime shape

The Python implementation now has two layers:

- composable stage commands
  - `snapshot`, `plan`, `orchestrate`, `prepare`, `launch`, `finalize`, `merge-queue`
- continuous workflow command
  - `run`
  - repeatedly rebuilds workspace state and chains the stage commands into a
    resumable loop
  - keeps writing the same per-stage JSON outputs while also writing
    `runtime/latest-run.json`

This means the stage modules remain independently testable, while the `run`
command provides the operator-facing replacement for the shell script's main
loop.
