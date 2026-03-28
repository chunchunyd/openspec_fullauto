from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from openspec_py.runtime_logging import append_event


@dataclass(frozen=True, slots=True)
class LegacySessionBootstrap:
    session_dir: Path
    adopted_from: Path | None
    created: bool


def _latest_mtime(path: Path) -> float:
    latest = path.stat().st_mtime
    for child in path.iterdir():
        try:
            latest = max(latest, child.stat().st_mtime)
        except FileNotFoundError:
            continue
    return latest


def select_legacy_session_dir(
    logs_root: Path,
    *,
    target_change_ids: list[str],
    destination_dir: Path,
) -> Path | None:
    if not logs_root.exists():
        return None

    best_dir: Path | None = None
    best_score = 0
    best_mtime = 0.0
    for session_dir in logs_root.glob(".auto-apply-run.*"):
        if not session_dir.is_dir():
            continue
        if session_dir.resolve() == destination_dir.resolve():
            continue
        score = sum(
            1 for change_id in target_change_ids if (session_dir / f"{change_id}.result").exists()
        )
        if score <= 0:
            continue
        mtime = _latest_mtime(session_dir)
        if score > best_score or (score == best_score and mtime > best_mtime):
            best_dir = session_dir
            best_score = score
            best_mtime = mtime
    return best_dir


def ensure_legacy_session_dir(
    logs_root: Path,
    *,
    session_dir: Path,
    target_change_ids: list[str],
    runtime_root: Path,
) -> LegacySessionBootstrap:
    if session_dir.exists():
        session_dir.mkdir(parents=True, exist_ok=True)
        append_event(
            runtime_root,
            "legacy_session_reused",
            {
                "session_dir": str(session_dir),
                "target_count": len(target_change_ids),
            },
        )
        return LegacySessionBootstrap(
            session_dir=session_dir,
            adopted_from=None,
            created=False,
        )

    session_dir.parent.mkdir(parents=True, exist_ok=True)
    adopted_from = select_legacy_session_dir(
        logs_root,
        target_change_ids=target_change_ids,
        destination_dir=session_dir,
    )
    if adopted_from is not None:
        shutil.copytree(adopted_from, session_dir)
        append_event(
            runtime_root,
            "legacy_session_adopted",
            {
                "session_dir": str(session_dir),
                "adopted_from": str(adopted_from),
                "target_count": len(target_change_ids),
            },
        )
        return LegacySessionBootstrap(
            session_dir=session_dir,
            adopted_from=adopted_from,
            created=True,
        )

    session_dir.mkdir(parents=True, exist_ok=True)
    append_event(
        runtime_root,
        "legacy_session_created",
        {
            "session_dir": str(session_dir),
            "target_count": len(target_change_ids),
        },
    )
    return LegacySessionBootstrap(
        session_dir=session_dir,
        adopted_from=None,
        created=True,
    )
