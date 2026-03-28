from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class WorkspaceDiscoveryError(RuntimeError):
    """Raised when the OpenSpec workspace root cannot be located."""


@dataclass(frozen=True, slots=True)
class WorkspacePaths:
    workspace_root: Path
    openspec_root: Path
    changes_root: Path
    archive_root: Path
    auto_root: Path
    deps_root: Path
    logs_root: Path
    runtime_root: Path


def _is_workspace_root(path: Path) -> bool:
    return (
        (path / "openspec").is_dir()
        and (path / "openspec" / "changes").is_dir()
        and (path / "openspec" / "auto").is_dir()
    )


def discover_workspace_paths(start: Path | None = None) -> WorkspacePaths:
    candidates: list[Path] = []

    if start is not None:
        candidates.extend([start.resolve(), *start.resolve().parents])

    cwd = Path.cwd().resolve()
    candidates.extend([cwd, *cwd.parents])

    module_path = Path(__file__).resolve()
    candidates.extend(module_path.parents)

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if not _is_workspace_root(candidate):
            continue
        openspec_root = candidate / "openspec"
        return WorkspacePaths(
            workspace_root=candidate,
            openspec_root=openspec_root,
            changes_root=openspec_root / "changes",
            archive_root=openspec_root / "changes" / "archive",
            auto_root=openspec_root / "auto",
            deps_root=openspec_root / "auto" / "deps",
            logs_root=openspec_root / "auto" / "logs",
            runtime_root=candidate / "openspec_py" / "runtime",
        )

    raise WorkspaceDiscoveryError(
        "Could not find a workspace root containing openspec/changes and openspec/auto."
    )
