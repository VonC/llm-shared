"""Git operations for the `new_draft` tool: branch checks and creation.

Every command goes through the shared cross-platform helper
(`run_cross_platform_git_command`) so Windows runs `git` directly while Linux
runs `command git` through `/bin/sh`. Read-only checks capture output and never
fail the process; the mutating helpers (`create_local_branch`, `add_worktree`)
turn a non-zero Git exit into a `NewDraftError` with the captured stderr so the
workflow can report a clean message instead of a raw traceback.

The branch-collision check looks at local heads first, then at every declared
remote with `git ls-remote --heads` (not just `origin`). When no remote is
configured there is nothing to query, so only the local check runs.

Fix: add the file helpers the `--from-draft` mode needs to relocate a draft into
the chosen working tree: `path_is_tracked` (does Git track this path here),
`git_move` (a staged `git mv` for the in-place rename), and `stage_path` (a
`git add` used both to stage the copy in a worktree and to stage the source
removal). The filesystem read/write and the choice between these stays in the
workflow; this module only runs the Git side.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.git_command import GitCommandOptions, run_cross_platform_git_command
from tools.new_draft_models import NewDraftError

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

# Result labels returned by `branch_collision`.
COLLISION_LOCAL = "local"
COLLISION_REMOTE = "remote"


def _git(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run one git command, capturing output without raising on failure."""
    return run_cross_platform_git_command(
        args,
        cwd=cwd,
        options=GitCommandOptions(check=False, capture_output=True, encoding="utf-8"),
    )


def _git_strict(args: list[str], *, cwd: Path, action: str) -> None:
    """Run one git command and raise `NewDraftError` when it exits non-zero.

    Args:
        args: The git arguments without the leading `git` token.
        cwd: The working directory for the command.
        action: A short label used in the error message (for example `branch`).

    Raises:
        NewDraftError: When the git command exits with a non-zero code.
    """
    result = _git(args, cwd=cwd)
    if result.returncode != 0:
        detail = result.stderr.strip() if result.stderr else ""
        msg = f"git {action} failed: {detail}" if detail else f"git {action} failed."
        raise NewDraftError(msg)


def local_branch_exists(slug: str, *, cwd: Path) -> bool:
    """Return whether a local branch named `slug` already exists."""
    result = _git(["branch", "--list", slug], cwd=cwd)
    return bool(result.stdout.strip())


def list_remotes(cwd: Path) -> list[str]:
    """Return the configured remote names (empty when none are declared)."""
    result = _git(["remote"], cwd=cwd)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def remote_branch_exists(slug: str, *, cwd: Path) -> bool:
    """Return whether `slug` exists as a branch on any declared remote.

    Each configured remote is queried with `git ls-remote --heads <remote>
    <slug>`, so the check covers every remote name, not only `origin`. With no
    remote configured the function returns False (nothing to check).

    Args:
        slug: The candidate branch name.
        cwd: The repository working directory.

    Returns:
        True when any remote already has a `refs/heads/<slug>` branch.
    """
    for remote in list_remotes(cwd):
        result = _git(["ls-remote", "--heads", remote, slug], cwd=cwd)
        if result.stdout.strip():
            return True
    return False


def branch_collision(slug: str, *, cwd: Path) -> str | None:
    """Return where `slug` collides with an existing branch, else None.

    Args:
        slug: The candidate branch name.
        cwd: The repository working directory.

    Returns:
        `COLLISION_LOCAL`, `COLLISION_REMOTE`, or None when the name is free.
    """
    if local_branch_exists(slug, cwd=cwd):
        return COLLISION_LOCAL
    if remote_branch_exists(slug, cwd=cwd):
        return COLLISION_REMOTE
    return None


def current_head_branch(cwd: Path) -> str:
    """Return the current branch name (`HEAD` when detached)."""
    return _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd).stdout.strip()


def create_local_branch(slug: str, *, cwd: Path) -> None:
    """Create and switch to a new branch `slug` in the current worktree."""
    _git_strict(["switch", "-c", slug], cwd=cwd, action=f"switch -c {slug}")


def add_worktree(worktree_path: Path, slug: str, *, cwd: Path) -> None:
    """Create branch `slug` in a new worktree at `worktree_path`."""
    _git_strict(
        ["worktree", "add", "-b", slug, str(worktree_path)],
        cwd=cwd,
        action=f"worktree add {worktree_path}",
    )


def path_is_tracked(path: Path, *, cwd: Path) -> bool:
    """Return whether Git tracks `path` in the `cwd` working tree.

    Args:
        path: The file path to test.
        cwd: The working directory whose index is consulted.

    Returns:
        True when `git ls-files --error-unmatch` exits zero for the path, which
        means the path is tracked; False otherwise.
    """
    result = _git(["ls-files", "--error-unmatch", "--", str(path)], cwd=cwd)
    return result.returncode == 0


def git_move(source: Path, target: Path, *, cwd: Path) -> None:
    """Rename a tracked file with `git mv`, staging the rename.

    Args:
        source: The tracked file to rename.
        target: The new path for the file.
        cwd: The working directory for the command.

    Raises:
        NewDraftError: When `git mv` exits with a non-zero code.
    """
    _git_strict(
        ["mv", str(source), str(target)],
        cwd=cwd,
        action=f"mv {source} -> {target}",
    )


def stage_path(path: Path, *, cwd: Path) -> None:
    """Stage a path with `git add`, whether it was added, changed, or removed.

    Args:
        path: The path to stage; `git add` records a copy or, when the file is
            now missing, the deletion of a tracked path.
        cwd: The working directory for the command.

    Raises:
        NewDraftError: When `git add` exits with a non-zero code.
    """
    _git_strict(["add", "--", str(path)], cwd=cwd, action=f"add {path}")


# eof
