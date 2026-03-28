from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from openspec_py.models import ResultSummary, TaskSummary

CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[(?P<mark>[ xX])\]\s+(?P<text>.+?)\s*$")
IMPL_RE = re.compile(r"`((?:feat|fix|chore)/[^`]+)`")
INTEG_RE = re.compile(r"`(series/[^`]+)`")
STEP_RE = re.compile(r"-step-(\d+)")


@dataclass(frozen=True, slots=True)
class AssessmentSummary:
    needs_human: bool
    reason: str
    next_action: str


def parse_step_number(change_id: str) -> int | None:
    match = STEP_RE.search(change_id)
    if not match:
        return None
    return int(match.group(1))


def parse_series_name(change_id: str) -> str:
    match = re.match(r"^(.+)-step-\d+($|-)", change_id)
    if not match:
        return change_id
    return match.group(1)


def parse_dependency_graph(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "changes" in payload:
        graph: dict[str, list[str]] = {}
        for entry in payload["changes"]:
            name = str(entry["name"])
            depends_on = [str(item) for item in entry.get("dependsOn", [])]
            graph[name] = depends_on
        return graph
    if isinstance(payload, dict):
        return {
            str(change_name): [str(item) for item in depends_on]
            for change_name, depends_on in payload.items()
        }
    raise ValueError(f"Unsupported dependency graph format: {path}")


def _extract_managed_branches(lines: list[str]) -> tuple[str | None, str | None]:
    impl_candidates: list[str] = []
    integ_candidates: list[str] = []
    for line in lines:
        impl_candidates.extend(IMPL_RE.findall(line))
        integ_candidates.extend(INTEG_RE.findall(line))
    impl = impl_candidates[0] if impl_candidates else None
    integ = integ_candidates[0] if integ_candidates else None
    return impl, integ


def _is_managed_start_task(
    text: str, implementation_branch: str | None, integration_branch: str | None
) -> bool:
    if not integration_branch or integration_branch == "dev":
        return False
    if integration_branch not in text:
        return False
    if implementation_branch and implementation_branch in text and "切出" in text:
        return True
    start_markers = (
        "自动化确认系列集成分支",
        "同步最新",
        "已就绪",
        "从最新 `dev` 切出",
        "从最新 `dev` 创建",
    )
    return any(marker in text for marker in start_markers)


def _is_managed_merge_task(
    text: str, implementation_branch: str | None, integration_branch: str | None
) -> bool:
    if not implementation_branch or not integration_branch or integration_branch == "dev":
        return False
    return implementation_branch in text and integration_branch in text and "merge 回" in text


def parse_tasks_summary(path: Path | None) -> TaskSummary:
    if path is None or not path.exists():
        return TaskSummary()

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    implementation_branch, integration_branch = _extract_managed_branches(lines)
    summary = TaskSummary()

    pending_candidates: list[str] = []

    for line in lines:
        match = CHECKBOX_RE.match(line)
        if not match:
            continue

        checked = match.group("mark").lower() == "x"
        text = match.group("text")
        is_automation = _is_managed_start_task(
            text, implementation_branch, integration_branch
        ) or _is_managed_merge_task(text, implementation_branch, integration_branch)

        summary.full_total += 1
        if checked:
            summary.full_completed += 1

        if is_automation:
            summary.automation_total += 1
            if checked:
                summary.automation_completed += 1
        else:
            summary.manual_total += 1
            if checked:
                summary.manual_completed += 1
            else:
                pending_candidates.append(text)

    if pending_candidates:
        preferred = next(
            (
                item
                for item in pending_candidates
                if not item.startswith("在进入 `")
            ),
            None,
        )
        summary.next_pending = preferred or pending_candidates[0]

    return summary


def parse_shell_kv_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            continue
        if raw_value == "":
            data[key] = ""
            continue
        parsed = shlex.split(raw_value)
        if not parsed:
            data[key] = ""
        elif len(parsed) == 1:
            data[key] = parsed[0]
        else:
            data[key] = " ".join(parsed)
    return data


def parse_assessment_output(path: Path) -> AssessmentSummary:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    data: dict[str, str] = {}

    for raw in lines:
        line = raw.strip()
        for key in ("NEEDS_HUMAN", "REASON", "NEXT_ACTION"):
            prefix = key + "="
            if line.startswith(prefix) and key not in data:
                data[key] = line[len(prefix) :].strip()
                break

    needs_human = data.get("NEEDS_HUMAN", "").lower()
    reason = data.get("REASON", "")
    next_action = data.get("NEXT_ACTION", "")
    if needs_human not in {"yes", "no"} or not reason or not next_action:
        raise ValueError(f"Invalid assessment output: {path}")

    return AssessmentSummary(
        needs_human=needs_human == "yes",
        reason=reason,
        next_action=next_action,
    )


def parse_result_summary(path: Path, session_key: str | None = None) -> ResultSummary:
    payload = parse_shell_kv_file(path)

    def parse_bool(name: str) -> bool:
        return payload.get(name, "0") in {"1", "true", "True"}

    def parse_int(name: str) -> int | None:
        raw = payload.get(name)
        if raw is None or raw == "":
            return None
        return int(raw)

    updated_at = datetime.fromtimestamp(path.stat().st_mtime)
    return ResultSummary(
        status=payload.get("status", "unknown"),
        completed_tasks=parse_int("completed_tasks"),
        total_tasks=parse_int("total_tasks"),
        archived=parse_bool("archived"),
        requires_human=parse_bool("requires_human"),
        human_reason=payload.get("human_reason") or None,
        human_next_action=payload.get("human_next_action") or None,
        transition_at=parse_int("transition_at"),
        source_path=path,
        session_key=session_key,
        updated_at=updated_at,
    )


def format_relative_time(moment: datetime | None, now: datetime) -> str:
    if moment is None:
        return "-"
    delta = now - moment
    total_seconds = int(delta.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds}s ago"
    if total_seconds < 3600:
        return f"{total_seconds // 60}m ago"
    if total_seconds < 86400:
        return f"{total_seconds // 3600}h ago"
    return f"{total_seconds // 86400}d ago"
