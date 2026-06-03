"""Read-only git helpers for prompt_workflow: branch, fork point, changed files.

Every command is a read; nothing here mutates the repository. The functions are
thin wrappers around ``git`` run through ``subprocess`` (located with
``shutil.which`` like the other ``tools/`` scripts), so tests monkeypatch
``run_git`` to feed canned output. The branch-start logic implements the draft
detection rule of the spec: walk the first-parent history and find the first
commit that belongs to more than the current branch; that commit is the fork
point used as the diff base for "created since the start of the branch".
"""

from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

from tools.prompt_workflow_models import PromptWorkflowError

if TYPE_CHECKING:
    from pathlib import Path

# Marker separating the two sides of a renamed path in porcelain output.
_RENAME_ARROW = " -> "
# Length of the porcelain status field plus its trailing space ("XY ").
_PORCELAIN_PREFIX_LEN = 3


def run_git(args: list[str], *, cwd: Path) -> str:
    """Run one read-only git command and return its stdout text.

    Args:
        args: The git arguments, without the ``git`` program name.
        cwd: The working directory the command runs in.

    Returns:
        The command stdout, decoded as UTF-8.

    Raises:
        PromptWorkflowError: When the git command exits non-zero.
    """
    git_executable = shutil.which("git") or "git"
    command = [git_executable, *args]
    try:
        result = subprocess.run(  # noqa: S603
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            cwd=cwd,
        )
    except subprocess.CalledProcessError as err:
        stderr = err.stderr.strip() if err.stderr else ""
        detail = f": {stderr}" if stderr else ""
        msg = f"git {' '.join(args)} failed{detail}"
        raise PromptWorkflowError(msg) from err
    return result.stdout


def _non_empty_lines(text: str) -> list[str]:
    """Return the stripped, non-empty lines of a text block."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def current_branch(cwd: Path) -> str:
    """Return the current branch name (``HEAD`` when detached)."""
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd).strip()


def _other_branches(cwd: Path, current: str) -> list[str]:
    """Return the local branch names other than the current one."""
    names = _non_empty_lines(
        run_git(["for-each-ref", "--format=%(refname:short)", "refs/heads/"], cwd=cwd),
    )
    return [name for name in names if name != current]


def fork_point(cwd: Path) -> str | None:
    """Return the commit where the current branch forked from another branch.

    The branch start is found with a single ``git rev-list --first-parent
    --boundary HEAD --not <other branches>``. The boundary commit (prefixed with
    ``-`` in the output) is the newest commit the current branch shares with
    another local branch, and is returned as the diff base for files created on
    the branch. When there is no other branch, or no shared commit (for example
    on the default branch), None is returned and the caller falls back to the
    working-tree drafts (Q07). This replaces the previous per-commit
    ``git branch --contains`` walk, which spawned one git process per commit.
    """
    current = current_branch(cwd)
    others = _other_branches(cwd, current)
    if not others:
        return None
    output = run_git(
        ["rev-list", "--first-parent", "--boundary", "HEAD", "--not", *others],
        cwd=cwd,
    )
    for line in _non_empty_lines(output):
        if line.startswith("-"):
            return line[1:]
    return None


def changed_files_since(cwd: Path, base: str) -> list[str]:
    """Return the repo-relative paths added or modified between base and HEAD."""
    output = run_git(
        ["diff", "--name-only", "--diff-filter=AM", base, "HEAD"],
        cwd=cwd,
    )
    return _non_empty_lines(output)


def _porcelain_path(line: str) -> str:
    """Extract the target path from one ``git status --porcelain`` line."""
    payload = line[_PORCELAIN_PREFIX_LEN:] if len(line) > _PORCELAIN_PREFIX_LEN else ""
    if _RENAME_ARROW in payload:
        return payload.split(_RENAME_ARROW, 1)[1].strip()
    return payload.strip()


def working_tree_changed_files(cwd: Path) -> list[str]:
    """Return the repo-relative paths changed in the working tree.

    ``--untracked-files=all`` lists files inside a brand-new untracked directory
    individually, instead of collapsing them to the directory name, so a new
    draft under a fresh ``docs/`` folder is still detected.
    """
    output = run_git(["status", "--porcelain", "--untracked-files=all"], cwd=cwd)
    paths: list[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = _porcelain_path(line)
        if path:
            paths.append(path)
    return paths


def status_entries(cwd: Path) -> list[tuple[str, str]]:
    """Return ``(status, path)`` pairs from ``git status --porcelain``.

    ``status`` is the two-character porcelain code (index column then work-tree
    column); ``path`` is the target path (the new name for a rename). Used by the
    implement cycle to classify staged versus non-staged and code versus docs
    changes.
    """
    output = run_git(["status", "--porcelain", "--untracked-files=all"], cwd=cwd)
    entries: list[tuple[str, str]] = []
    for line in output.splitlines():
        if len(line) < _PORCELAIN_PREFIX_LEN:
            continue
        path = _porcelain_path(line)
        if path:
            entries.append((line[:2], path))
    return entries


def staged_files(cwd: Path) -> list[str]:
    """Return the repo-relative paths currently staged for commit."""
    return _non_empty_lines(run_git(["diff", "--cached", "--name-only"], cwd=cwd))


def has_step_commit(cwd: Path, step: int, base: str | None) -> bool:
    """Return whether a ``record step <n> validation`` commit exists in range (Q16).

    The range is ``base..HEAD`` when a branch start is known, otherwise the whole
    history of HEAD. The grep is case-insensitive.
    """
    args = ["log", "-i", f"--grep=record step {step} validation", "--format=%H"]
    args.append(f"{base}..HEAD" if base is not None else "HEAD")
    return bool(_non_empty_lines(run_git(args, cwd=cwd)))


def stage_all(cwd: Path) -> None:
    """Stage every change with ``git add -A`` (the only git write the tool makes)."""
    run_git(["add", "-A"], cwd=cwd)


# eof
