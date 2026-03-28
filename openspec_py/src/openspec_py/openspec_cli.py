from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path


class OpenSpecCommandError(RuntimeError):
    """Raised when the OpenSpec CLI returns an unexpected failure."""


def _openspec_command() -> list[str]:
    raw = os.environ.get("OPENSPEC_CMD", "").strip()
    if raw:
        return shlex.split(raw)
    return ["npx", "-y", "@fission-ai/openspec"]


def _run_openspec(
    workspace_root: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    command = [*_openspec_command(), *args]
    completed = subprocess.run(
        command,
        cwd=workspace_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        detail = stderr or stdout or f"exit={completed.returncode}"
        raise OpenSpecCommandError(
            f"openspec {' '.join(args)} failed in {workspace_root}: {detail}"
        )
    return completed


@dataclass(frozen=True, slots=True)
class ValidateIssue:
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ValidateItem:
    item_id: str
    item_type: str
    valid: bool
    duration_ms: int | None = None
    issues: list[ValidateIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
            "valid": self.valid,
            "duration_ms": self.duration_ms,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True, slots=True)
class ValidationResult:
    ok: bool
    items: list[ValidateItem]
    raw: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "items": [item.to_dict() for item in self.items],
            "raw": self.raw,
        }


def validate_change(
    workspace_root: Path,
    change_id: str,
    *,
    strict: bool = False,
) -> ValidationResult:
    args = ["validate", change_id, "--type", "change", "--json"]
    if strict:
        args.append("--strict")
    completed = _run_openspec(workspace_root, *args)
    raw = json.loads(completed.stdout)
    items: list[ValidateItem] = []
    all_valid = True

    for entry in raw.get("items", []):
        issues = [
            ValidateIssue(
                message=str(issue.get("message", "")),
                path=str(issue.get("path")) if issue.get("path") is not None else None,
            )
            for issue in entry.get("issues", [])
        ]
        valid = bool(entry.get("valid", False))
        all_valid = all_valid and valid
        items.append(
            ValidateItem(
                item_id=str(entry.get("id", change_id)),
                item_type=str(entry.get("type", "change")),
                valid=valid,
                duration_ms=int(entry["durationMs"])
                if entry.get("durationMs") is not None
                else None,
                issues=issues,
            )
        )

    return ValidationResult(
        ok=all_valid and bool(items),
        items=items,
        raw=raw,
    )


def archive_change(workspace_root: Path, change_id: str) -> bool:
    completed = _run_openspec(
        workspace_root,
        "archive",
        change_id,
        "-y",
        check=False,
    )
    if completed.returncode == 0:
        return True
    stderr = completed.stderr.strip()
    stdout = completed.stdout.strip()
    detail = f"{stdout}\n{stderr}".strip().lower()
    if "already archived" in detail:
        return True
    raise OpenSpecCommandError(
        f"openspec archive {change_id} failed in {workspace_root}: {stderr or stdout or completed.returncode}"
    )
