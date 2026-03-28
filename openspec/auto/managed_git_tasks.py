#!/usr/bin/env python3
"""Inspect and update standardized auto-managed git tasks inside tasks.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CHECKBOX_RE = re.compile(r"^(\s*[-*]\s+\[)([ xX])(\]\s+)(.*)$")
IMPL_RE = re.compile(r"`((?:feat|fix|chore)/[^`]+)`")
INTEG_RE = re.compile(r"`(series/[^`]+)`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    for name in ("inspect", "mark-start", "mark-merge"):
        subparser = sub.add_parser(name)
        subparser.add_argument("--tasks", required=True)
        subparser.add_argument("--change", required=True)
        subparser.add_argument("--default-impl", required=True)
        subparser.add_argument("--default-integ", required=True)

    return parser.parse_args()


def choose_branch(
    candidates: list[str], change: str, preferred: str, fallback: str
) -> str:
    unique: list[str] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    if preferred in unique:
        return preferred
    for candidate in unique:
        if change in candidate:
            return candidate
    if unique:
        return unique[0]
    return fallback


def detect_metadata(
    lines: list[str], change: str, default_impl: str, default_integ: str
) -> dict[str, object]:
    impl_candidates: list[str] = []
    integ_candidates: list[str] = []

    for line in lines:
        impl_candidates.extend(IMPL_RE.findall(line))
        integ_candidates.extend(INTEG_RE.findall(line))

    impl = choose_branch(impl_candidates, change, default_impl, default_impl)
    integ = choose_branch(integ_candidates, change, default_integ, default_integ)
    is_series = integ != "dev"

    start_indexes: list[int] = []
    merge_indexes: list[int] = []
    full_total = 0
    full_completed = 0
    apply_total = 0
    apply_completed = 0

    def is_start_task(content: str) -> bool:
        if not is_series:
            return False
        if integ not in content:
            return False
        if impl in content and "切出" in content:
            return True
        if (
            "自动化确认系列集成分支" in content
            or "同步最新" in content
            or "已就绪" in content
            or "切出或同步" in content
            or "从最新 `dev` 切出" in content
            or "从最新 `dev` 创建" in content
        ):
            return True
        return False

    def is_merge_task(content: str) -> bool:
        if not is_series:
            return False
        return impl in content and integ in content and "merge 回" in content

    for idx, line in enumerate(lines):
        match = CHECKBOX_RE.match(line)
        if not match:
            continue

        checked = match.group(2).lower() == "x"
        content = match.group(4)
        start = is_start_task(content)
        merge = is_merge_task(content)

        full_total += 1
        if checked:
            full_completed += 1

        if start:
            start_indexes.append(idx)
        if merge:
            merge_indexes.append(idx)

        if start or merge:
            continue

        apply_total += 1
        if checked:
            apply_completed += 1

    return {
        "impl": impl,
        "integ": integ,
        "is_series": int(is_series),
        "start_matches": len(start_indexes),
        "merge_matches": len(merge_indexes),
        "start_indexes": start_indexes,
        "merge_indexes": merge_indexes,
        "full_total": full_total,
        "full_completed": full_completed,
        "apply_total": apply_total,
        "apply_completed": apply_completed,
    }


def write_shell_metadata(meta: dict[str, object]) -> None:
    for key in (
        "impl",
        "integ",
        "is_series",
        "start_matches",
        "merge_matches",
        "full_total",
        "full_completed",
        "apply_total",
        "apply_completed",
    ):
        print(f"{key}={meta[key]}")


def mark_indexes(lines: list[str], indexes: list[int]) -> int:
    changed = 0
    for idx in indexes:
        match = CHECKBOX_RE.match(lines[idx])
        if not match or match.group(2).lower() == "x":
            continue
        lines[idx] = f"{match.group(1)}x{match.group(3)}{match.group(4)}"
        changed += 1
    return changed


def main() -> int:
    args = parse_args()
    tasks_path = Path(args.tasks)
    lines = tasks_path.read_text(encoding="utf-8", errors="replace").splitlines()
    meta = detect_metadata(lines, args.change, args.default_impl, args.default_integ)

    if args.cmd == "inspect":
      write_shell_metadata(meta)
      return 0

    indexes = (
        meta["start_indexes"] if args.cmd == "mark-start" else meta["merge_indexes"]
    )
    changed = mark_indexes(lines, indexes)
    tasks_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
