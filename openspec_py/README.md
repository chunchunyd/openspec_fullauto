# OpenSpec Python Framework

This directory contains the Python replacement framework for the current
`openspec/auto/auto_apply.sh` workflow.

The first iteration focuses on:

- scanning the existing `openspec/` workspace state
- rendering active series and change progress with Rich tables
- preserving time-based logs while also writing structured snapshot files

## Environment

This project is managed with `uv`.

```powershell
cd openspec_py
uv sync
```

## Commands

Render the current dashboard once:

```powershell
uv run openspec-auto dashboard
```

Watch the dashboard and refresh every 3 seconds:

```powershell
uv run openspec-auto dashboard --watch --interval 3
```

Write a structured snapshot file while rendering:

```powershell
uv run openspec-auto dashboard --snapshot-path runtime/latest-status.json
```

Write a snapshot file without the Rich dashboard:

```powershell
uv run openspec-auto snapshot
```

Render the execution plan and write a plan JSON file:

```powershell
uv run openspec-auto plan
```

Build the next dry-run orchestration batch:

```powershell
uv run openspec-auto orchestrate --max-parallel 3
```

Prepare isolated worktrees, per-change port profiles, and series branch context:

```powershell
uv run openspec-auto prepare --max-parallel 3
uv run openspec-auto prepare --max-parallel 1 --series users-part1 --execute
```

Build a launch batch from the current orchestration result:

```powershell
uv run openspec-auto launch --max-parallel 3 --command-template "echo __CHANGE_ID__"
```

Build a launch batch that targets prepared worktrees instead of the raw
`openspec/changes/<change-id>` directories:

```powershell
uv run openspec-auto launch --max-parallel 2 --prepare-worktrees --command-template "echo __WORKTREE_PATH__"
```

Actually execute the selected launch batch:

```powershell
uv run openspec-auto launch --max-parallel 1 --execute --command-template "echo __CHANGE_ID__"
```

Actually execute inside prepared worktrees:

```powershell
uv run openspec-auto launch --max-parallel 2 --prepare-worktrees --execute --command-template "git branch --show-current"
```

Run launch with an optional incomplete retry loop. When tasks remain incomplete,
the framework can run a task-sync command, then either use a custom assessment
command or a built-in heuristic to decide whether to retry or stop with
`needs_human`:

```powershell
uv run openspec-auto launch --execute --retry-limit 1 --command-template "my-agent __CHANGE_ID__"
uv run openspec-auto launch --execute --retry-limit 1 --task-sync-command-template "my-sync __CHANGE_ID__"
uv run openspec-auto launch --execute --retry-limit 1 --assessment-command-template "cmd /c \"(echo NEEDS_HUMAN=no & echo REASON=retry & echo NEXT_ACTION=finish task)\""
```

Review which in-progress changes are actually ready for validation / merge / archive:

```powershell
uv run openspec-auto finalize
uv run openspec-auto finalize --series public-content
```

Actually run OpenSpec validation and write shell-compatible final states when a
change is eligible:

```powershell
uv run openspec-auto finalize --series public-content --execute
uv run openspec-auto finalize --series one-off-change-series --execute --archive
```

Inspect the parent-managed merge queue for series changes:

```powershell
uv run openspec-auto merge-queue
uv run openspec-auto merge-queue --series users-part1
```

Actually perform queued series merges:

```powershell
uv run openspec-auto merge-queue --series users-part1 --execute
uv run openspec-auto merge-queue --series users-part1 --execute --archive
uv run openspec-auto merge-queue --series users-part1 --execute --archive --cleanup-worktrees
uv run openspec-auto merge-queue --series users-part1 --execute --handoff-command-template "my-handoff __WORKTREE_PATH__"
uv run openspec-auto merge-queue --series users-part1 --execute --merge-fallback-command-template "my-merge-fix __WORKTREE_PATH__"
```

Run the full Python orchestration loop for one or more cycles:

```powershell
uv run openspec-auto run --command-template "my-agent __CHANGE_ID__" --max-cycles 1
uv run openspec-auto run --change users-part1-step-05-self-endpoints-request-validation-hardening --command-template "my-agent __CHANGE_ID__" --max-cycles 1
uv run openspec-auto run --execute --prepare-worktrees --archive --stop-when-idle --max-parallel 2 --max-cycles 20 --command-template "my-agent __CHANGE_ID__"
uv run openspec-auto run --execute --prepare-worktrees --task-sync-command-template "my-sync __CHANGE_ID__" --assessment-command-template "my-assess __CHANGE_ID__" --handoff-command-template "my-handoff __WORKTREE_PATH__" --merge-fallback-command-template "my-merge-fix __WORKTREE_PATH__" --command-template "my-agent __CHANGE_ID__"
```

## Output files

- `runtime/latest-status.json`
  - latest structured workspace snapshot
- `runtime/latest-plan.json`
  - latest structured execution plan
- `runtime/latest-orchestration.json`
  - latest dry-run orchestration session and current launch batch
- `runtime/latest-preparation.json`
  - latest worktree/session preparation state
- `runtime/latest-launch.json`
  - latest launch batch state
- `runtime/latest-finalize.json`
  - latest finalize planning/execution state
- `runtime/latest-merge-queue.json`
  - latest parent-managed merge queue state
- `runtime/latest-run.json`
  - latest end-to-end run loop state, including recent cycles and per-stage counts
- `runtime/sessions/*.json`
  - timestamped orchestration, preparation, launch, finalize, merge-queue, and run-loop session history
- `runtime/launch-logs/*.log`
  - per-change subprocess logs for executed launch batches
- `runtime/events.log`
  - append-only timestamped event log for snapshot, plan, orchestration, preparation, and launch writes

These files are intentionally separate from `openspec/auto/logs/`, which remain
the source of the historical run logs produced by the existing shell workflow.

When `prepare` or `launch --prepare-worktrees` runs with `--execute`, the
framework also reuses the shell workflow's session directory convention under:

- `openspec/auto/logs/.auto-apply-run.<session-key>/`
  - shared per-series port profiles and session-compatible `.result` files

When a target session directory does not exist yet, the Python workflow now
adopts the most relevant older `.auto-apply-run.*` directory for the same set
of changes before writing new results. This preserves shell-era port profiles,
result files, and per-change recovery context instead of starting from an empty
session archive every time.

`launch --execute` now writes shell-compatible `.result` files for the selected
changes:

- `running`
  - command is currently executing inside the prepared worktree
- `launched`
  - command finished successfully and the manual tasks are now in sync, but the overall change is still treated as `in_progress`
- `failed`
  - command failed and the change should be treated as halted
- `needs_human`
  - the command finished but tasks stayed incomplete after task-sync / assessment / retry handling

`finalize --execute` reuses the same `.result` convention:

- `ready_for_merge`
  - validation passed and a managed series step is ready for the merge queue
- `success`
  - validation passed and the change is complete, with or without archive
- `failed`
  - validation or archive failed and the change now needs recovery

`merge-queue --execute` continues from `ready_for_merge` and writes:

- `success`
  - parent-managed merge completed successfully
- `success` with `archived=1`
  - merge completed and the change was archived
- `needs_human`
  - merge preconditions, an existing unresolved merge, or the merge itself need manual recovery

Before the actual merge step, `merge-queue --execute` now checks that the
implementation branch is clean on its own branch head. If it is still dirty,
the framework can either stop with `needs_human` or run an optional
`--handoff-command-template` cleanup command first.

If the parent-managed merge itself fails or the worktree is already sitting in
an unresolved merge state, the framework can also run an optional
`--merge-fallback-command-template` in that original worktree to continue and
finish the merge in place.

When `merge-queue --execute --archive` succeeds, the framework now also tries to
perform the shell-equivalent post-archive cleanup steps:

- implementation branch cleanup
  - deletes the merged implementation branch only when it is fully merged, the
    integration branch exists, and no worktree still has that branch checked out
- optional worktree cleanup via `--cleanup-worktrees`
  - removes only clean detached worktrees and preserves dirty worktrees for
    manual inspection

## Scope of this first iteration

This framework now includes a Python-native `run` loop that chains snapshot,
plan, orchestration, preparation, launch, finalize, and merge-queue stages into
a resumable cycle. It still does not replicate every shell behavior yet, but it
now covers the core long-running execution path with clearer terminal state and
structured session history.

For the module layout and migration plan, see `ARCHITECTURE.md`.
