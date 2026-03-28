from __future__ import annotations

import json
from pathlib import Path

from openspec_py.models import WorkspaceSnapshot
from openspec_py.runtime_logging import append_event


def write_snapshot(
    snapshot: WorkspaceSnapshot,
    output_path: Path,
    runtime_root: Path,
) -> bool:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=True) + "\n"

    existing = None
    if output_path.exists():
        existing = output_path.read_text(encoding="utf-8", errors="replace")

    if existing == payload:
        return False

    output_path.write_text(payload, encoding="utf-8")
    append_event(
        runtime_root,
        "snapshot_written",
        {
            "path": str(output_path),
            "series_count": len(snapshot.series),
            "active_change_count": snapshot.active_change_count,
        },
    )
    return True
