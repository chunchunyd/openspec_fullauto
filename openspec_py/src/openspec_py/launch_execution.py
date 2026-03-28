from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from openspec_py.legacy_results import write_legacy_result
from openspec_py.parsers import AssessmentSummary, parse_assessment_output, parse_tasks_summary
from openspec_py.runtime_logging import append_event

if TYPE_CHECKING:
    from openspec_py.launcher import LaunchItem, LaunchSession


@dataclass(frozen=True, slots=True)
class AttemptPaths:
    transcript: Path
    task_sync: Path
    assessment: Path
    retry_guidance: Path


def attempt_paths(
    session: "LaunchSession",
    item: "LaunchItem",
    attempt: int,
    launch_logs_root: Path,
) -> AttemptPaths:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return AttemptPaths(
        transcript=launch_logs_root / f"{item.change_id}.attempt-{attempt}.{timestamp}.log",
        task_sync=session.legacy_session_dir / f"{item.change_id}.attempt-{attempt}.tasks-sync.log",
        assessment=session.legacy_session_dir / f"{item.change_id}.incomplete-assessment.log",
        retry_guidance=session.legacy_session_dir / f"{item.change_id}.attempt-{attempt}.retry-guidance.txt",
    )


def template_values(
    item: "LaunchItem",
    *,
    attempt: int,
    paths: AttemptPaths,
) -> dict[str, str]:
    return {
        "change_id": item.change_id,
        "change_path": str(item.change_path),
        "execution_path": str(item.execution_path),
        "worktree_change_path": str(item.worktree_change_path),
        "series": item.series,
        "step": "" if item.step is None else str(item.step),
        "next_task": item.next_task or "",
        "port_profile_path": str(item.port_profile_path) if item.port_profile_path else "",
        "implementation_branch": item.implementation_branch or "",
        "integration_branch": item.integration_branch or "",
        "attempt": str(attempt),
        "tasks_completed": str(item.full_completed),
        "tasks_total": str(item.full_total),
        "manual_completed": str(item.manual_completed),
        "manual_total": str(item.manual_total),
        "transcript_file": str(paths.transcript),
        "task_sync_log": str(paths.task_sync),
        "assessment_log": str(paths.assessment),
        "retry_guidance_file": str(paths.retry_guidance),
    }


def _run_shell_command(
    command: str,
    *,
    cwd: Path,
    log_path: Path,
    metadata_lines: list[str],
) -> subprocess.CompletedProcess[str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        for line in metadata_lines:
            handle.write(f"{line}\n")
        handle.write("\n")
        handle.flush()
        return subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            stdout=handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )


def refresh_task_progress(item: "LaunchItem") -> None:
    summary = parse_tasks_summary(item.tasks_path)
    item.manual_completed = summary.manual_completed
    item.manual_total = summary.manual_total
    item.full_completed = summary.full_completed
    item.full_total = summary.full_total
    item.next_task = summary.next_pending or item.next_task


def write_item_result(
    session: "LaunchSession",
    item: "LaunchItem",
    runtime_root: Path,
    *,
    status: str,
    requires_human: bool = False,
    human_reason: str | None = None,
    human_next_action: str | None = None,
) -> None:
    record = write_legacy_result(
        workspace_root=session.workspace_root,
        session_key=session.session_key,
        change_id=item.change_id,
        status=status,
        tasks_path=item.tasks_path,
        requires_human=requires_human,
        human_reason=human_reason,
        human_next_action=human_next_action,
        runtime_root=runtime_root,
        completed_tasks=item.full_completed,
        total_tasks=item.full_total,
    )
    item.result_path = record.path


def _heuristic_assessment(item: "LaunchItem", *, final_attempt: bool) -> AssessmentSummary:
    next_action = item.next_task or "Finish the remaining manual tasks and sync tasks.md."
    if not final_attempt:
        return AssessmentSummary(
            needs_human=False,
            reason="manual tasks remain incomplete after apply/tasks-sync; retry once with focused guidance",
            next_action=next_action,
        )
    return AssessmentSummary(
        needs_human=True,
        reason="the change remained incomplete after the automatic retry limit",
        next_action=(
            f"Review the remaining checkbox tasks in {item.tasks_path or item.change_path / 'tasks.md'} "
            f"and continue this change manually or rerun launch for this single change."
        ),
    )


def _run_assessment(
    session: "LaunchSession",
    item: "LaunchItem",
    *,
    attempt: int,
    paths: AttemptPaths,
    runtime_root: Path,
    render_command,
) -> AssessmentSummary:
    if not session.assessment_command_template:
        summary = _heuristic_assessment(item, final_attempt=attempt >= item.max_attempts)
        paths.assessment.parent.mkdir(parents=True, exist_ok=True)
        paths.assessment.write_text(
            "\n".join(
                [
                    f"NEEDS_HUMAN={'yes' if summary.needs_human else 'no'}",
                    f"REASON={summary.reason}",
                    f"NEXT_ACTION={summary.next_action}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return summary

    command = render_command(session.assessment_command_template, template_values(item, attempt=attempt, paths=paths))
    append_event(
        runtime_root,
        "launch_assessment_started",
        {"change_id": item.change_id, "series": item.series, "attempt": attempt, "command": command},
    )
    completed = _run_shell_command(
        command,
        cwd=item.execution_path,
        log_path=paths.assessment,
        metadata_lines=[f"command={command}", f"attempt={attempt}", f"execution_path={item.execution_path}"],
    )
    if completed.returncode != 0:
        raise RuntimeError(f"assessment command failed for {item.change_id}; inspect {paths.assessment}")
    return parse_assessment_output(paths.assessment)


def _write_retry_guidance(path: Path, summary: AssessmentSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "- Assessment decided this change is still finishable without human intervention.",
                f"- Focus specifically on this next action: {summary.next_action}",
                "- Before stopping, make sure tasks.md matches the real completion state of the change.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def execute_launch_item(
    session: "LaunchSession",
    item: "LaunchItem",
    runtime_root: Path,
    launch_logs_root: Path,
    lock: threading.Lock,
    render_command,
) -> "LaunchItem":
    with lock:
        item.run_state = "running"
        item.started_at = datetime.now()

    attempt = 1
    while attempt <= item.max_attempts:
        paths = attempt_paths(session, item, attempt, launch_logs_root)
        command = render_command(session.command_template, template_values(item, attempt=attempt, paths=paths))
        with lock:
            item.attempt = attempt
            item.command = command
            item.log_path = paths.transcript
            item.task_sync_log_path = paths.task_sync
            item.assessment_log_path = paths.assessment
            item.retry_guidance_path = paths.retry_guidance
            item.assessment_state = None
            item.assessment_reason = None
            item.assessment_next_action = None

        write_item_result(session, item, runtime_root, status="running")
        append_event(
            runtime_root,
            "launch_started",
            {
                "change_id": item.change_id,
                "series": item.series,
                "attempt": attempt,
                "command": command,
                "execution_path": str(item.execution_path),
                "log_path": str(paths.transcript),
            },
        )
        completed = _run_shell_command(
            command,
            cwd=item.execution_path,
            log_path=paths.transcript,
            metadata_lines=[f"command={command}", f"attempt={attempt}", f"execution_path={item.execution_path}"],
        )
        refresh_task_progress(item)
        item.exit_code = completed.returncode

        if completed.returncode == 0 and session.task_sync_command_template and (item.manual_total <= 0 or item.manual_completed < item.manual_total):
            sync_command = render_command(
                session.task_sync_command_template,
                template_values(item, attempt=attempt, paths=paths),
            )
            append_event(
                runtime_root,
                "launch_task_sync_started",
                {
                    "change_id": item.change_id,
                    "series": item.series,
                    "attempt": attempt,
                    "command": sync_command,
                    "task_sync_log_path": str(paths.task_sync),
                },
            )
            _run_shell_command(sync_command, cwd=item.execution_path, log_path=paths.task_sync, metadata_lines=[f"command={sync_command}", f"attempt={attempt}"])
            refresh_task_progress(item)
            append_event(
                runtime_root,
                "launch_task_sync_finished",
                {
                    "change_id": item.change_id,
                    "series": item.series,
                    "attempt": attempt,
                    "task_sync_log_path": str(paths.task_sync),
                    "manual_completed": item.manual_completed,
                    "manual_total": item.manual_total,
                },
            )

        if completed.returncode != 0:
            item.run_state = "failed"
            item.reason = "launch command failed"
            write_item_result(session, item, runtime_root, status="failed")
            break

        if item.manual_total > 0 and item.manual_completed == item.manual_total:
            item.run_state = "succeeded"
            item.reason = "launch command completed and manual tasks are in sync"
            write_item_result(session, item, runtime_root, status="launched")
            break

        try:
            assessment = _run_assessment(
                session,
                item,
                attempt=attempt,
                paths=paths,
                runtime_root=runtime_root,
                render_command=render_command,
            )
        except (RuntimeError, ValueError) as error:
            item.run_state = "needs_human"
            item.assessment_state = "failed"
            item.assessment_reason = str(error)
            item.reason = "assessment failed"
            write_item_result(
                session,
                item,
                runtime_root,
                status="needs_human",
                requires_human=True,
                human_reason=str(error),
                human_next_action=f"Inspect {paths.assessment} and the remaining checkbox tasks before rerunning launch.",
            )
            break

        if attempt >= item.max_attempts and not assessment.needs_human:
            assessment = AssessmentSummary(
                needs_human=True,
                reason="the change remained incomplete after the automatic retry limit",
                next_action=assessment.next_action,
            )

        item.assessment_state = "needs_human" if assessment.needs_human else "retry"
        item.assessment_reason = assessment.reason
        item.assessment_next_action = assessment.next_action

        if assessment.needs_human or attempt >= item.max_attempts:
            item.run_state = "needs_human"
            item.reason = assessment.reason
            write_item_result(
                session,
                item,
                runtime_root,
                status="needs_human",
                requires_human=True,
                human_reason=assessment.reason,
                human_next_action=assessment.next_action,
            )
            break

        _write_retry_guidance(paths.retry_guidance, assessment)
        append_event(
            runtime_root,
            "launch_retry_scheduled",
            {"change_id": item.change_id, "series": item.series, "attempt": attempt, "next_attempt": attempt + 1},
        )
        item.run_state = "retrying"
        item.reason = assessment.reason
        attempt += 1

    item.finished_at = datetime.now()
    return item
