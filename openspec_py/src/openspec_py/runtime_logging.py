from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def append_event(runtime_root: Path, event: str, payload: dict[str, object]) -> None:
    runtime_root.mkdir(parents=True, exist_ok=True)
    target = runtime_root / "events.log"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "payload": payload,
    }
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
