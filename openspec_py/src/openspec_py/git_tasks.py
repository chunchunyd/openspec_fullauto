from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openspec_py.parsers import CHECKBOX_RE, IMPL_RE, INTEG_RE


@dataclass(frozen=True, slots=True)
class ManagedGitMetadata:
    implementation_branch: str
    integration_branch: str
    is_series: bool
    managed: bool
    start_indexes: tuple[int, ...]
    merge_indexes: tuple[int, ...]
    full_total: int
    full_completed: int
    apply_total: int
    apply_completed: int


def _choose_branch(
    candidates: list[str],
    change_id: str,
    preferred: str,
    fallback: str,
) -> str:
    unique: list[str] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    if preferred in unique:
        return preferred
    for candidate in unique:
        if change_id in candidate:
            return candidate
    if unique:
        return unique[0]
    return fallback


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def inspect_managed_git_tasks(
    tasks_path: Path,
    change_id: str,
    default_implementation_branch: str,
    default_integration_branch: str,
) -> ManagedGitMetadata:
    lines = _read_lines(tasks_path)
    impl_candidates: list[str] = []
    integ_candidates: list[str] = []

    for line in lines:
        impl_candidates.extend(IMPL_RE.findall(line))
        integ_candidates.extend(INTEG_RE.findall(line))

    implementation_branch = _choose_branch(
        impl_candidates,
        change_id,
        default_implementation_branch,
        default_implementation_branch,
    )
    integration_branch = _choose_branch(
        integ_candidates,
        change_id,
        default_integration_branch,
        default_integration_branch,
    )
    is_series = integration_branch != "dev"

    start_indexes: list[int] = []
    merge_indexes: list[int] = []
    full_total = 0
    full_completed = 0
    apply_total = 0
    apply_completed = 0

    def is_start_task(content: str) -> bool:
        if not is_series:
            return False
        if integration_branch not in content:
            return False
        if implementation_branch in content and "切出" in content:
            return True
        return any(
            marker in content
            for marker in (
                "自动化确认系列集成分支",
                "同步最新",
                "已就绪",
                "切出或同步",
                "从最新 `dev` 切出",
                "从最新 `dev` 创建",
            )
        )

    def is_merge_task(content: str) -> bool:
        if not is_series:
            return False
        return (
            implementation_branch in content
            and integration_branch in content
            and "merge 回" in content
        )

    for index, line in enumerate(lines):
        match = CHECKBOX_RE.match(line)
        if not match:
            continue

        checked = match.group("mark").lower() == "x"
        content = match.group("text")
        start_task = is_start_task(content)
        merge_task = is_merge_task(content)

        full_total += 1
        if checked:
            full_completed += 1

        if start_task:
            start_indexes.append(index)
        if merge_task:
            merge_indexes.append(index)

        if start_task or merge_task:
            continue

        apply_total += 1
        if checked:
            apply_completed += 1

    managed = is_series and bool(start_indexes) and bool(merge_indexes)

    return ManagedGitMetadata(
        implementation_branch=implementation_branch,
        integration_branch=integration_branch,
        is_series=is_series,
        managed=managed,
        start_indexes=tuple(start_indexes),
        merge_indexes=tuple(merge_indexes),
        full_total=full_total,
        full_completed=full_completed,
        apply_total=apply_total,
        apply_completed=apply_completed,
    )


def _mark_indexes(tasks_path: Path, indexes: tuple[int, ...]) -> int:
    lines = _read_lines(tasks_path)
    changed = 0
    for index in indexes:
        match = CHECKBOX_RE.match(lines[index])
        if not match or match.group("mark").lower() == "x":
            continue
        mark_start = match.start("mark")
        mark_end = match.end("mark")
        lines[index] = f"{lines[index][:mark_start]}x{lines[index][mark_end:]}"
        changed += 1
    if changed:
        tasks_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def mark_start_tasks(tasks_path: Path, metadata: ManagedGitMetadata) -> int:
    return _mark_indexes(tasks_path, metadata.start_indexes)


def mark_merge_tasks(tasks_path: Path, metadata: ManagedGitMetadata) -> int:
    return _mark_indexes(tasks_path, metadata.merge_indexes)
