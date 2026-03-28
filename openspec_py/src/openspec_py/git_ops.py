from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class GitCommandError(RuntimeError):
    """Raised when a git command fails."""


@dataclass(frozen=True, slots=True)
class WorktreeEntry:
    path: Path
    head: str | None = None
    branch: str | None = None
    detached: bool = False
    bare: bool = False
    prunable: bool = False


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        detail = stderr or stdout or f"exit={completed.returncode}"
        raise GitCommandError(f"git {' '.join(args)} failed in {repo}: {detail}")
    return completed


def git_output(repo: Path, *args: str) -> str:
    return run_git(repo, *args).stdout.strip()


def ref_exists(repo: Path, ref: str) -> bool:
    return run_git(repo, "show-ref", "--verify", "--quiet", ref, check=False).returncode == 0


def current_branch(repo: Path) -> str | None:
    completed = run_git(
        repo,
        "symbolic-ref",
        "--quiet",
        "--short",
        "HEAD",
        check=False,
    )
    branch = completed.stdout.strip()
    return branch or None


def current_head(repo: Path) -> str | None:
    completed = run_git(repo, "rev-parse", "HEAD", check=False)
    head = completed.stdout.strip()
    return head or None


def git_path_exists(repo: Path, name: str) -> bool:
    completed = run_git(
        repo,
        "rev-parse",
        "--path-format=absolute",
        "--git-path",
        name,
        check=False,
    )
    target = completed.stdout.strip()
    return bool(target) and Path(target).exists()


def git_common_dir(repo: Path) -> Path | None:
    completed = run_git(
        repo,
        "rev-parse",
        "--path-format=absolute",
        "--git-common-dir",
        check=False,
    )
    raw = completed.stdout.strip()
    if completed.returncode != 0 or not raw:
        completed = run_git(repo, "rev-parse", "--git-common-dir", check=False)
        raw = completed.stdout.strip()
        if completed.returncode != 0 or not raw:
            return None
    path = Path(raw)
    if path.is_absolute():
        return path
    return (repo / path).resolve()


def list_worktrees(repo: Path) -> list[WorktreeEntry]:
    output = git_output(repo, "worktree", "list", "--porcelain")
    entries: list[WorktreeEntry] = []
    current: dict[str, object] = {}

    def flush() -> None:
        if "path" not in current:
            current.clear()
            return
        entries.append(
            WorktreeEntry(
                path=Path(str(current["path"])),
                head=current.get("head") if isinstance(current.get("head"), str) else None,
                branch=(
                    str(current["branch"]).removeprefix("refs/heads/")
                    if isinstance(current.get("branch"), str)
                    else None
                ),
                detached=bool(current.get("detached", False)),
                bare=bool(current.get("bare", False)),
                prunable=bool(current.get("prunable", False)),
            )
        )
        current.clear()

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        key, _, value = stripped.partition(" ")
        if key == "worktree":
            current["path"] = Path(value.strip())
        elif key == "HEAD":
            current["head"] = value.strip()
        elif key == "branch":
            current["branch"] = value.strip()
        elif key in {"detached", "bare", "prunable"}:
            current[key] = True

    flush()
    return entries


def is_registered_worktree(repo: Path, worktree_path: Path) -> bool:
    desired = worktree_path.resolve()
    return any(entry.path.resolve() == desired for entry in list_worktrees(repo))


def worktree_path_is_reusable(repo: Path, worktree_path: Path) -> bool:
    if not worktree_path.exists():
        return False
    repo_common_dir = git_common_dir(repo)
    target_common_dir = git_common_dir(worktree_path)
    if repo_common_dir is None or target_common_dir is None:
        return False
    return repo_common_dir.resolve() == target_common_dir.resolve()


def worktree_holders_for_branch(repo: Path, branch: str) -> list[Path]:
    return [entry.path for entry in list_worktrees(repo) if entry.branch == branch]


def branch_is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    return (
        run_git(
            repo,
            "merge-base",
            "--is-ancestor",
            ancestor,
            descendant,
            check=False,
        ).returncode
        == 0
    )


def delete_branch(repo: Path, branch: str, *, force: bool = True) -> None:
    run_git(repo, "branch", "-D" if force else "-d", branch)


def remove_worktree(repo: Path, worktree_path: Path, *, force: bool = False) -> None:
    args = ["worktree", "remove"]
    if force:
        args.append("--force")
    args.append(str(worktree_path))
    run_git(repo, *args)
