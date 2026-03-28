from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from openspec_py.runtime_logging import append_event


@dataclass(frozen=True, slots=True)
class SessionWriteResult:
    latest_path: Path
    history_path: Path
    changed: bool


def write_session_payload(
    payload: dict[str, object],
    latest_path: Path,
    runtime_root: Path,
    event_name: str,
    event_payload: dict[str, object],
) -> SessionWriteResult:
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    sessions_root = runtime_root / "sessions"
    sessions_root.mkdir(parents=True, exist_ok=True)

    body = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
    existing = (
        latest_path.read_text(encoding="utf-8", errors="replace")
        if latest_path.exists()
        else None
    )

    changed = existing != body
    latest_path.write_text(body, encoding="utf-8")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    history_path = sessions_root / f"{latest_path.stem}.{timestamp}.json"
    history_path.write_text(body, encoding="utf-8")

    append_event(
        runtime_root,
        event_name,
        {
            **event_payload,
            "latest_path": str(latest_path),
            "history_path": str(history_path),
            "changed": changed,
        },
    )

    return SessionWriteResult(
        latest_path=latest_path,
        history_path=history_path,
        changed=changed,
    )
