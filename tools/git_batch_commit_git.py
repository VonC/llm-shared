"""Git subprocess helpers for git batch commit.

Fix: Split the Git command wrappers, add-phase checks, and commit helpers out
of `tools.git_batch_commit` so the workflow code can stay in a smaller file.

Fix: Add a staged-count validation helper so the root a.commit workflow can
confirm the plan lists one `git add` per file currently staged before it
commits anything, which stops a stale or partial plan from being applied.

Fix: Count a staged rename as its two paths (old removed, new added) so the
staged total matches an a.commit plan that lists a `git add` for each side of
the rename, instead of falling one short and failing validation.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import TYPE_CHECKING

from tools.git_batch_commit_models import (
    GIT_TRACE_ENABLED_VALUE as _GIT_TRACE_ENABLED_VALUE,
)
from tools.git_batch_commit_models import (
    CommitBlock,
    GitBatchCommitError,
    GitOperationError,
)
from tools.git_batch_commit_models import (
    GitAddOutcome as _GitAddOutcome,
)
from tools.git_batch_commit_models import (
    GitInvocationOptions as _GitCommandOptions,
)
from tools.git_batch_commit_parsing import (
    parse_git_add_command as _parse_git_add_command,
)
from tools.git_command import GitCommandOptions, run_cross_platform_git_command

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger("git_batch_commit")


# ----------------------------
# Git operations
# ----------------------------


def _run_git_command(
    args: list[str],
    *,
    cwd: Path,
    options: _GitCommandOptions | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the result."""
    if not args or args[0] != "git":
        msg = f"Git command failed: {' '.join(args)}"
        raise GitOperationError(msg)

    git_options = options or _GitCommandOptions()

    if git_options.require_tty and not _has_interactive_console():
        msg = (
            "Git command requires an interactive console. Re-run the tool in a "
            "foreground terminal with stdin, stdout, and stderr attached."
        )
        raise GitOperationError(msg)

    trace_env = _build_git_trace_environment() if git_options.trace_git else None

    if not git_options.capture_output:
        sys.stdout.flush()
        sys.stderr.flush()

    try:
        return run_cross_platform_git_command(
            args[1:],
            cwd=cwd,
            options=GitCommandOptions(
                check=git_options.check,
                capture_output=git_options.capture_output,
                env=trace_env,
            ),
        )
    except subprocess.SubprocessError as err:
        msg = f"Git command failed: {' '.join(args)}"
        raise GitOperationError(msg) from err


def _has_interactive_console() -> bool:
    """Return True when stdin, stdout, and stderr are attached to a console."""
    return sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()


def _build_git_trace_environment() -> dict[str, str]:
    """Build a one-command Git trace environment for commit diagnostics."""
    env = os.environ.copy()
    env.setdefault("GIT_TRACE", _GIT_TRACE_ENABLED_VALUE)
    env.setdefault("GIT_TRACE_SETUP", _GIT_TRACE_ENABLED_VALUE)
    env.setdefault("GIT_TRACE_PERFORMANCE", _GIT_TRACE_ENABLED_VALUE)
    return env


def git_reset(root: Path) -> None:
    """Execute git reset to unstage all files."""
    LOGGER.info("Executing git reset to unstage all files...")
    _run_git_command(["git", "reset"], cwd=root)
    LOGGER.info("Git reset completed.")


def _is_worktree_clean(root: Path) -> bool:
    """Return True when the repository has no staged, unstaged, or untracked changes."""
    result = _run_git_command(["git", "status", "--short"], cwd=root)
    return not bool((result.stdout or "").strip())


def _extract_file_path(cmd: str) -> str | None:
    """Extract file path from 'git add <path>' command."""
    parts = _parse_git_add_command(cmd)
    if parts is None:
        return None

    add_args = parts[2:]
    if not add_args:
        LOGGER.warning("Missing arguments in git add command: %s", cmd)
        return None

    if "--" in add_args:
        separator_index = add_args.index("--")
        path_args = add_args[separator_index + 1 :]
        if not path_args:
            LOGGER.warning("Missing file path after '--' in command: %s", cmd)
            return None
        return path_args[0]

    path_args = [arg for arg in add_args if not arg.startswith("-")]
    if not path_args:
        LOGGER.warning("No file path found in git add command: %s", cmd)
        return None

    return path_args[-1]


def _is_git_pathspec(file_path_str: str) -> bool:
    """Return True when the git-add target uses Git pathspec magic syntax."""
    return file_path_str.startswith(":(")


def _is_tracked_path(root: Path, file_path_str: str) -> bool:
    """Return True when git tracks the given path in the current repository."""
    result = _run_git_command(
        ["git", "ls-files", "--error-unmatch", "--", file_path_str],
        cwd=root,
        options=_GitCommandOptions(check=False),
    )
    return result.returncode == 0


def _is_path_in_head(root: Path, file_path_str: str) -> bool:
    """Return True when the given path exists in the HEAD tree.

    This allows dry-run validation to accept deletion paths that are gone from
    disk and index but still represent a valid tracked file being removed.
    """
    result = _run_git_command(
        ["git", "cat-file", "-e", f"HEAD:{file_path_str}"],
        cwd=root,
        options=_GitCommandOptions(check=False),
    )
    return result.returncode == 0


def _check_missing_files(git_adds: list[str], root: Path) -> list[str]:
    """Check which files in git_adds are missing and return their paths."""
    missing_files: list[str] = []

    for cmd in git_adds:
        file_path_str = _extract_file_path(cmd)
        if file_path_str is None:
            continue

        if _is_git_pathspec(file_path_str):
            continue

        file_path = root / file_path_str
        if (
            not file_path.exists()
            and not _is_tracked_path(root, file_path_str)
            and not _is_path_in_head(root, file_path_str)
        ):
            missing_files.append(file_path_str)
            LOGGER.warning("File not found: %s", file_path_str)

    return missing_files


def _collect_git_add_paths(git_adds: list[str]) -> list[str]:
    """Collect the repo-relative paths targeted by git add commands."""
    paths: list[str] = []

    for cmd in git_adds:
        file_path_str = _extract_file_path(cmd)
        if file_path_str is not None:
            paths.append(file_path_str)

    return paths


def _block_has_staged_changes(git_adds: list[str], root: Path) -> bool:
    """Return True when the current commit block staged at least one diff."""
    paths = _collect_git_add_paths(git_adds)
    args = ["git", "diff", "--cached", "--name-only"]

    if paths:
        args.extend(["--", *paths])

    result = _run_git_command(args, cwd=root)
    return bool((result.stdout or "").strip())


def _validate_missing_files_for_blocks(blocks: list[CommitBlock], root: Path) -> None:
    """Validate that all git-add file paths exist across parsed commit blocks."""
    missing_by_title: list[tuple[str, list[str]]] = []

    for block in blocks:
        missing_files = _check_missing_files(block.git_adds, root)
        if missing_files:
            missing_by_title.append((block.commit_title, missing_files))

    if not missing_by_title:
        return

    details: list[str] = []
    for title, files in missing_by_title:
        details.append(f"- {title}")
        details.extend(f"  - {file_path}" for file_path in files)

    msg = "Dry-run failed: missing files referenced by git add commands:\n"
    msg += "\n".join(details)
    raise GitBatchCommitError(msg)


def _count_staged_files(root: Path) -> int:
    """Return the number of files currently staged in the index.

    Fix: pass `--no-renames` so a staged rename is reported as two paths (the
    old path removed and the new path added). The a.commit plan lists one
    `git add` per path, including both sides of a rename, so without this the
    staged count falls one short of the plan and validation fails on a rename.
    """
    result = _run_git_command(
        ["git", "diff", "--cached", "--name-only", "--no-renames"],
        cwd=root,
    )
    staged_lines = [line for line in (result.stdout or "").splitlines() if line.strip()]
    return len(staged_lines)


def _count_plan_git_adds(blocks: list[CommitBlock]) -> int:
    """Return the total number of git add commands across all commit blocks."""
    return sum(len(block.git_adds) for block in blocks)


def _validate_staged_count_matches_git_adds(
    blocks: list[CommitBlock],
    root: Path,
) -> None:
    """Validate the a.commit plan covers exactly the files currently staged.

    The plan in a.commit must list one `git add` per staged file. When the
    number of `git add` commands differs from the number of files currently
    staged, the plan is stale or partial: committing it would leave staged or
    planned files out of sync. Raise so the run stops before any commit.
    """
    plan_adds = _count_plan_git_adds(blocks)
    staged = _count_staged_files(root)
    if plan_adds == staged:
        return

    msg = (
        "Validation failed: the commit plan lists "
        f"{plan_adds} 'git add' command(s) but {staged} file(s) are staged. "
        "Stage exactly the files described by a.commit (for example with "
        "'git add -A') so the plan and the index match before committing."
    )
    raise GitBatchCommitError(msg)


def _prompt_add_issues_action(
    missing_files: list[str],
    failed_adds: list[str],
) -> _GitAddOutcome:
    """Prompt user for action when files are missing or git-add failed."""
    if missing_files:
        LOGGER.warning("\nThe following files are missing:")
        for file_path in missing_files:
            LOGGER.warning("  - %s", file_path)

    if failed_adds:
        LOGGER.warning("\nThe following git add commands failed:")
        for cmd in failed_adds:
            LOGGER.warning("  - %s", cmd)

    response = (
        input(
            "\nConfirm commit anyway, skip this commit, or stop? [confirm/skip/stop]: ",
        )
        .strip()
        .lower()
    )

    if response == "confirm":
        return _GitAddOutcome(should_continue=True, should_skip_commit=False)
    if response == "stop":
        return _GitAddOutcome(should_continue=False, should_skip_commit=False)
    return _GitAddOutcome(should_continue=True, should_skip_commit=True)


def _execute_git_adds(git_adds: list[str], root: Path) -> list[str]:
    """Execute git add commands and return commands that failed."""
    failed_adds: list[str] = []

    for cmd in git_adds:
        args = _parse_git_add_command(cmd)
        if args is None:
            failed_adds.append(cmd)
            continue

        result = _run_git_command(
            args,
            cwd=root,
            options=_GitCommandOptions(check=False),
        )
        if result.returncode != 0:
            failed_adds.append(cmd)
            stderr_text = (result.stderr or "").strip()
            if stderr_text:
                LOGGER.warning("git add failed (%s): %s", cmd, stderr_text)
            else:
                LOGGER.warning("git add failed: %s", cmd)
            continue

        LOGGER.debug("Added with command: %s", cmd)

    return failed_adds


def git_add_files(git_adds: list[str], root: Path) -> _GitAddOutcome:
    """Execute git add commands.

    Returns an outcome that distinguishes continue, skip, and stop.
    Logs warnings for missing files and asks for user confirmation.
    """
    missing_files = _check_missing_files(git_adds, root)
    failed_adds = _execute_git_adds(git_adds, root)

    if missing_files or failed_adds:
        return _prompt_add_issues_action(missing_files, failed_adds)

    return _GitAddOutcome(should_continue=True, should_skip_commit=False)


def git_commit(
    commit_message: str,
    commit_title: str,
    root: Path,
    *,
    trace_git_commit: bool = False,
) -> None:
    """Execute git commit with the provided message."""
    LOGGER.info("Committing: %s", commit_title)
    if trace_git_commit:
        LOGGER.info("Git commit trace is enabled for this run.")
    _run_git_command(
        ["git", "commit", "-m", commit_message],
        cwd=root,
        options=_GitCommandOptions(
            capture_output=False,
            require_tty=True,
            trace_git=trace_git_commit,
        ),
    )
    LOGGER.info("Commit completed.")


block_has_staged_changes = _block_has_staged_changes
count_plan_git_adds = _count_plan_git_adds
count_staged_files = _count_staged_files
is_worktree_clean = _is_worktree_clean
validate_missing_files_for_blocks = _validate_missing_files_for_blocks
validate_staged_count_matches_git_adds = _validate_staged_count_matches_git_adds


__all__ = [
    "GitCommandOptions",
    "_block_has_staged_changes",
    "_build_git_trace_environment",
    "_check_missing_files",
    "_collect_git_add_paths",
    "_count_plan_git_adds",
    "_count_staged_files",
    "_execute_git_adds",
    "_extract_file_path",
    "_has_interactive_console",
    "_is_git_pathspec",
    "_is_path_in_head",
    "_is_tracked_path",
    "_is_worktree_clean",
    "_prompt_add_issues_action",
    "_run_git_command",
    "_validate_missing_files_for_blocks",
    "_validate_staged_count_matches_git_adds",
    "git_add_files",
    "git_commit",
    "git_reset",
    "run_cross_platform_git_command",
]


# eof
