#!/usr/bin/env python3
"""git_batch_commit.py Batch git commits from clipboard.

Reads clipboard content to extract tuples of (git_add_commands, commit_message).
Executes git operations with validation and user confirmation.

Commit message structure:
  xxxx(yyyy): zzz
  <empty line>
  Why:
  <empty line>
  <non-empty lines>
  <empty line>
  <non-empty lines (not "What:")>
  <empty line>
  What:
  <empty line>
  - xxx
  - xxx
  ...

Usage:
    python git_batch_commit.py [filename] [--dry-run]

Reads from clipboard by default. If filename is provided, reads from file.
Processes git add/commit operations interactively unless --dry-run is used.

Fix: Reduce complexity in _parse_commit_message and git_add_files by splitting
into smaller helper functions. Remove magic numbers. Fix logging calls.

Fix: Add noqa for intentional try-except in loop. Use try-except-else pattern in main().

Fix: Skip markdown and other non-relevant lines when parsing clipboard content.
Find git commands first, then find commit title pattern, then parse message.

Fix: Parse git add options like '-A <path>' correctly and validate missing
files in dry-run without git reset/add/commit.

Fix: Add --root-a-commit option to run a strict two-phase workflow on
<project-root>/a.commit: validate first (fail fast on error), then commit.

Fix: Use the shared project-root helper so `PRJ_DIR` can point batch commits
at the calling project before the local upward scan runs.

Fix: Vendor the cross-platform Git helper into `tools/` so this script no
longer depends on the `pdfss` package from another repository.

Fix: Route every Git subprocess through the cached cross-platform helper so
Linux uses `command git` while Windows uses `git` directly.

Fix: Run `git commit` with live stdout and stderr so Git prompts, post-commit
messages, and trace lines remain visible instead of stalling behind captured
pipes.

Fix: Fail fast when an interactive Git command is started without an attached
console, which gives a clear error instead of a wait that looks like a hang.

Fix: Add optional commit-only Git tracing so stuck post-commit work can be
diagnosed without turning on trace output for every Git subprocess.

Fix: Refuse to replay project-root a.commit when the working tree is already
clean, so reruns fail early with a clear already-applied message.

Fix: Skip a commit block before git commit when its listed paths stage no diff,
which avoids misleading "nothing to commit" failures for already-applied groups.

Fix: Return a non-zero exit code when the user stops after a Git operation
failure, so shell status matches the interrupted run.
"""


from __future__ import annotations

import argparse
import contextlib
import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))
        sys.path.insert(0, str((_project_root / "src").resolve()))

with contextlib.suppress(Exception):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import find_project_root
from tools.git_command import GitCommandOptions, run_cross_platform_git_command

LOGGER = logging.getLogger("git_batch_commit")

# Constants for git add command parsing
_GIT_ADD_MIN_PARTS: int = 3
_GIT_TRACE_ENABLED_VALUE = "1"

# Regex patterns for parsing
_COMMIT_TITLE_PATTERN = re.compile(r"^[^\(]+\([^\)]+\):\s+\S.*$")
_LIST_ITEM_PATTERN = re.compile(r"^- \S.*$")


# ----------------------------
# Exceptions
# ----------------------------


class GitBatchCommitError(Exception):
    """Base exception for this tool."""


class ClipboardError(GitBatchCommitError):
    """Raised when clipboard reading fails."""


class CommitMessageError(GitBatchCommitError):
    """Raised when commit message validation fails."""

    def __init__(
        self,
        message: str,
        lines_read: list[str],
        faulty_line: str | None = None,
    ) -> None:
        """Create a CommitMessageError with context about what was read."""
        self.lines_read = lines_read
        self.faulty_line = faulty_line
        super().__init__(message)


class GitOperationError(GitBatchCommitError):
    """Raised when a git operation fails."""


# ----------------------------
# Data model
# ----------------------------


@dataclass(frozen=True)
class CommitBlock:
    """A single commit with its git add commands and commit message."""

    git_adds: list[str]
    commit_message: str
    commit_title: str


@dataclass
class _ParseState:
    """State tracker for commit message parsing."""

    lines: list[str]
    idx: int
    lines_read: list[str]


@dataclass(frozen=True)
class _GitCommandOptions:
    """Options for one Git subprocess invocation."""

    check: bool = True
    capture_output: bool = True
    require_tty: bool = False
    trace_git: bool = False


# ----------------------------
# Clipboard utilities
# ----------------------------


def _get_clipboard_text() -> str:
    """Get text content from the Windows clipboard via PowerShell."""
    try:
        pwsh = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
        result = subprocess.run(  # noqa: S603
            [
                pwsh,
                "-noprofile",
                "-ExecutionPolicy",
                "Bypass",
                "-command",
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                "$PSModuleAutoloadingPreference = 'None'; "
                "Import-Module Microsoft.PowerShell.Management; "
                "Get-Clipboard -Raw",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        return result.stdout.strip() if result.stdout else ""
    except subprocess.SubprocessError as e:
        msg = f"Failed to read clipboard: {e}"
        raise ClipboardError(msg) from e


# ----------------------------
# Commit message validation helpers
# ----------------------------


def _is_commit_title(line: str) -> bool:
    """Check if a line matches the commit title pattern xxxx(yyyy): zzz."""
    return bool(_COMMIT_TITLE_PATTERN.match(line))


def _is_list_item(line: str) -> bool:
    """Check if a line matches the list item pattern '- xxx'."""
    return bool(_LIST_ITEM_PATTERN.match(line))


def _parse_title(state: _ParseState) -> str:
    """Parse and validate the commit title line."""
    if state.idx >= len(state.lines):
        msg = "Expected commit message title but reached end of input"
        raise CommitMessageError(msg, state.lines_read)

    title_line = state.lines[state.idx].strip()
    state.lines_read.append(title_line)
    if not _is_commit_title(title_line):
        msg = "Invalid commit title format: expected 'xxxx(yyyy): zzz'"
        raise CommitMessageError(msg, state.lines_read, title_line)
    state.idx += 1
    return title_line


def _expect_empty_line(state: _ParseState, context: str) -> None:
    """Expect an empty line at current position."""
    if state.idx >= len(state.lines):
        msg = f"Expected empty line {context}"
        raise CommitMessageError(msg, state.lines_read, None)
    if state.lines[state.idx].strip():
        msg = f"Expected empty line {context}"
        raise CommitMessageError(msg, state.lines_read, state.lines[state.idx])
    state.lines_read.append("")
    state.idx += 1


def _expect_keyword(state: _ParseState, keyword: str) -> None:
    """Expect a specific keyword at current position."""
    if state.idx >= len(state.lines):
        msg = f"Expected '{keyword}' section"
        raise CommitMessageError(msg, state.lines_read, None)
    if state.lines[state.idx].strip() != keyword:
        msg = f"Expected '{keyword}' section"
        raise CommitMessageError(msg, state.lines_read, state.lines[state.idx])
    state.lines_read.append(keyword)
    state.idx += 1


def _parse_non_empty_section(
    state: _ParseState,
    section_name: str,
    *,
    stop_at: str | None = None,
) -> list[str]:
    """Parse a section of non-empty lines."""
    section_lines: list[str] = []
    while state.idx < len(state.lines) and state.lines[state.idx].strip():
        if stop_at and state.lines[state.idx].strip() == stop_at:
            break
        section_lines.append(state.lines[state.idx])
        state.lines_read.append(state.lines[state.idx])
        state.idx += 1

    if not section_lines:
        msg = f"Expected non-empty lines in {section_name}"
        raise CommitMessageError(
            msg,
            state.lines_read,
            state.lines[state.idx] if state.idx < len(state.lines) else None,
        )
    return section_lines


def _parse_list_items(state: _ParseState) -> list[str]:
    """Parse list items starting with '- ' in What section."""
    items: list[str] = []
    while state.idx < len(state.lines):
        line = state.lines[state.idx]
        if not _is_list_item(line):
            break
        items.append(line)
        state.lines_read.append(line)
        state.idx += 1

    if not items:
        msg = "Expected at least one list item starting with '- ' in What section"
        raise CommitMessageError(
            msg,
            state.lines_read,
            state.lines[state.idx] if state.idx < len(state.lines) else None,
        )
    return items


def _parse_commit_message(lines: list[str], start_idx: int) -> tuple[str, str, int]:
    """Parse a commit message starting at start_idx.

    Returns: (commit_message, commit_title, next_idx)

    Raises CommitMessageError if structure is invalid.
    """
    state = _ParseState(lines=lines, idx=start_idx, lines_read=[])

    # Parse title
    title_line = _parse_title(state)

    # Empty line after title
    _expect_empty_line(state, "after title")

    # Why: section  # noqa: ERA001
    _expect_keyword(state, "Why:")
    _expect_empty_line(state, "after 'Why:'")

    # First section of Why: non-empty lines
    _parse_non_empty_section(state, "first Why section")
    _expect_empty_line(state, "after first Why section")

    # Second section of Why: non-empty lines (not "What:")
    _parse_non_empty_section(
        state,
        "second Why section (before 'What:')",
        stop_at="What:",
    )
    _expect_empty_line(state, "after second Why section")

    # Parse What section
    _expect_keyword(state, "What:")
    _expect_empty_line(state, "after 'What:'")

    # List items
    _parse_list_items(state)

    # Build the complete commit message
    commit_message = "\n".join(state.lines_read)
    return commit_message, title_line, state.idx


# ----------------------------
# Parsing clipboard content
# ----------------------------


def _skip_until_git_add(lines: list[str], start_idx: int) -> int:
    """Skip lines until we find a git add command or reach EOF."""
    idx = start_idx
    while idx < len(lines):
        line = lines[idx].strip()
        if line.startswith("git add "):
            return idx
        idx += 1
    return idx


def _skip_until_commit_title(lines: list[str], start_idx: int) -> int:
    """Skip lines until we find a commit title or reach EOF."""
    idx = start_idx
    while idx < len(lines):
        line = lines[idx].strip()
        if _is_commit_title(line):
            return idx
        idx += 1
    return idx


def _parse_git_adds(lines: list[str], start_idx: int) -> tuple[list[str], int]:
    """Parse consecutive git add commands starting at start_idx.

    Returns: (git_add_commands, next_idx)
    """
    git_adds: list[str] = []
    idx = start_idx

    while idx < len(lines):
        line = lines[idx].strip()

        # Skip empty lines
        if not line:
            idx += 1
            continue

        # Check if line is a git add command
        if line.startswith("git add "):
            # Remove any "&&" from the command
            clean_line = line.replace("&&", "").strip()
            git_adds.append(clean_line)
            idx += 1
        else:
            # Not a git add command, stop
            break

    return git_adds, idx


def _parse_git_add_command(cmd: str) -> list[str] | None:
    """Parse a git add command into argv form.

    Use POSIX-style shlex parsing so quoted repo-relative paths with spaces are
    kept as a single argument and surrounding quotes are stripped.
    """
    try:
        parts = shlex.split(cmd, posix=True)
    except ValueError:
        LOGGER.warning("Invalid git add command: %s", cmd)
        return None

    if len(parts) < _GIT_ADD_MIN_PARTS or parts[0] != "git" or parts[1] != "add":
        LOGGER.warning("Invalid git add command: %s", cmd)
        return None

    return parts


def parse_clipboard_content(
    content: str,
    *,
    interactive: bool = True,
) -> list[CommitBlock]:
    """Parse clipboard content into a list of CommitBlock instances."""
    lines = content.splitlines()
    blocks: list[CommitBlock] = []
    idx = 0

    while idx < len(lines):
        # Skip until we find a git add command
        idx = _skip_until_git_add(lines, idx)
        if idx >= len(lines):
            break

        # Parse git add commands
        git_adds, next_idx = _parse_git_adds(lines, idx)

        if not git_adds:
            # Should not happen since we just found a git add, but be safe
            idx += 1
            continue

        idx = next_idx

        # Skip until we find a commit title
        idx = _skip_until_commit_title(lines, idx)
        if idx >= len(lines):
            LOGGER.warning("Found git add commands but no commit message")
            break

        # Parse commit message
        try:
            commit_message, commit_title, next_idx = _parse_commit_message(lines, idx)
            idx = next_idx

            blocks.append(
                CommitBlock(
                    git_adds=git_adds,
                    commit_message=commit_message,
                    commit_title=commit_title,
                ),
            )
        except CommitMessageError as e:
            LOGGER.warning("Invalid commit message structure:")
            LOGGER.warning("Lines read so far:")
            for line in e.lines_read:
                LOGGER.warning("  %s", line)
            if e.faulty_line:
                LOGGER.warning("Faulty line: %s", e.faulty_line)
            LOGGER.warning("Error: %s", e)

            if not interactive:
                raise

            response = (
                input("\nSkip this commit or stop everything? [skip/stop]: ")
                .strip()
                .lower()
            )
            if response == "stop":
                raise
            # Skip to next potential git add command
            idx = next_idx + 1

    return blocks


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
    except subprocess.SubprocessError as e:
        msg = f"Git command failed: {' '.join(args)}"
        raise GitOperationError(msg) from e


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


def _prompt_add_issues_action(
    missing_files: list[str],
    failed_adds: list[str],
) -> str:
    """Prompt user for action when files are missing or git-add failed."""
    if missing_files:
        LOGGER.warning("\nThe following files are missing:")
        for file_path in missing_files:
            LOGGER.warning("  - %s", file_path)

    if failed_adds:
        LOGGER.warning("\nThe following git add commands failed:")
        for cmd in failed_adds:
            LOGGER.warning("  - %s", cmd)

    return (
        input(
            "\nConfirm commit anyway, skip this commit, or stop? [confirm/skip/stop]: ",
        )
        .strip()
        .lower()
    )


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


def git_add_files(git_adds: list[str], root: Path) -> bool:
    """Execute git add commands.

    Returns True if all files were added successfully, False otherwise.
    Logs warnings for missing files and asks for user confirmation.
    """
    missing_files = _check_missing_files(git_adds, root)
    failed_adds = _execute_git_adds(git_adds, root)

    if missing_files or failed_adds:
        response = _prompt_add_issues_action(missing_files, failed_adds)
        if response in ("stop", "skip"):
            return False

    return True


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


# ----------------------------
# Main logic
# ----------------------------


def _configure_logging(*, debug: bool) -> None:
    """Configure logging to stdout with message-only formatting."""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


def _get_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Batch git commits from clipboard.",
    )
    parser.add_argument(
        "filename",
        nargs="?",
        help=(
            "Optional input filename. If omitted, content is read from clipboard. "
            "Relative paths are resolved from project root."
        ),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Parse and validate input only (no git add/commit).",
    )
    parser.add_argument(
        "--root-a-commit",
        action="store_true",
        help=(
            "Use <project-root>/a.commit with a strict workflow: validate first, "
            "exit non-zero on validation failure, then run commits immediately."
        ),
    )
    parser.add_argument(
        "--trace-git-commit",
        action="store_true",
        help="Show Git trace output for commit commands only.",
    )
    return parser


def _run_root_a_commit_workflow(
    root: Path,
    *,
    trace_git_commit: bool = False,
) -> int:
    """Run validate-then-commit workflow on <root>/a.commit."""
    LOGGER.info("Reading root commit plan: %s", root / "a.commit")
    blocks = _read_and_parse_content(
        root,
        filename="a.commit",
        interactive=False,
    )

    if not blocks:
        msg = "No valid commit blocks found in project root a.commit"
        raise GitBatchCommitError(msg)

    LOGGER.info("Validation phase: checking commit plan before commit phase...")
    _validate_missing_files_for_blocks(blocks, root)
    LOGGER.info("Validation phase passed.")

    if _is_worktree_clean(root):
        msg = (
            "Refusing to replay project root a.commit because the working tree "
            "is clean. The commit plan is already applied or there is nothing "
            "to commit."
        )
        raise GitBatchCommitError(msg)

    LOGGER.info("Commit phase: applying commit plan now...")
    if not _process_all_commits(
        blocks,
        root,
        trace_git_commit=trace_git_commit,
    ):
        return 1
    return 0


def _read_input_content(root: Path, filename: str | None) -> str:
    """Read content from file when provided, otherwise from clipboard."""
    if filename is None:
        LOGGER.info("Reading clipboard...")
        return _get_clipboard_text()

    input_path = Path(filename)
    resolved_path = input_path if input_path.is_absolute() else root / input_path

    if not resolved_path.exists() or not resolved_path.is_file():
        msg = f"Input file does not exist: {resolved_path}"
        raise GitBatchCommitError(msg)

    LOGGER.info("Reading file: %s", resolved_path)
    try:
        return resolved_path.read_text(encoding="utf-8")
    except OSError as e:
        msg = f"Failed to read input file: {resolved_path}"
        raise GitBatchCommitError(msg) from e


def _read_and_parse_content(
    root: Path,
    *,
    filename: str | None,
    interactive: bool,
) -> list[CommitBlock]:
    """Read input content and parse commit blocks."""
    content = _read_input_content(root, filename)

    if not content:
        msg = "Input content is empty."
        raise GitBatchCommitError(msg)

    LOGGER.info("Parsing input content...")
    return parse_clipboard_content(content, interactive=interactive)


def _process_commit_block(
    block: CommitBlock,
    i: int,
    total: int,
    root: Path,
    *,
    trace_git_commit: bool = False,
) -> bool:
    """Process a single commit block. Returns True to continue, False to stop."""
    LOGGER.info("\n--- Processing commit %d/%d ---", i, total)
    LOGGER.info("Title: %s", block.commit_title)

    LOGGER.info("Git add commands: %d", len(block.git_adds))

    # Add files
    if not git_add_files(block.git_adds, root):
        LOGGER.warning("Skipping commit %d.", i)
        return True

    if not _block_has_staged_changes(block.git_adds, root):
        LOGGER.warning(
            "Skipping commit %d/%d for '%s': the listed paths stage no diff. "
            "The group looks already applied or the tree is clean for those "
            "paths.",
            i,
            total,
            block.commit_title,
        )
        return True

    # Commit
    git_commit(
        block.commit_message,
        block.commit_title,
        root,
        trace_git_commit=trace_git_commit,
    )
    return True


def _process_all_commits(
    blocks: list[CommitBlock],
    root: Path,
    *,
    trace_git_commit: bool = False,
) -> bool:
    """Process all commit blocks."""
    LOGGER.info("Found %d commit block(s).", len(blocks))

    git_reset(root)

    for i, block in enumerate(blocks, 1):
        try:
            should_continue = _process_commit_block(
                block,
                i,
                len(blocks),
                root,
                trace_git_commit=trace_git_commit,
            )
            if not should_continue:
                return False
        except GitOperationError:
            # Note: try-except in loop is intentional for interactive error handling
            LOGGER.exception("Git operation failed")
            response = (
                input("\nContinue with next commit or stop? [continue/stop]: ")
                .strip()
                .lower()
            )
            if response == "stop":
                LOGGER.info("Stopping after Git operation failure.")
                return False

    LOGGER.info("\n=== All commits processed successfully ===")
    return True


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = _get_arg_parser()
    args = parser.parse_args(argv)

    _configure_logging(debug=args.debug)

    # Find project root
    root = find_project_root(Path.cwd())
    LOGGER.info("Project root: %s", root)
    exit_code = 0

    try:
        if args.root_a_commit:
            if args.filename is not None:
                msg = "Cannot combine --root-a-commit with filename"
                raise GitBatchCommitError(msg)
            if args.dry_run:
                msg = "Cannot combine --root-a-commit with --dry-run"
                raise GitBatchCommitError(msg)
            exit_code = _run_root_a_commit_workflow(
                root,
                trace_git_commit=args.trace_git_commit,
            )
        else:
            blocks = _read_and_parse_content(
                root,
                filename=args.filename,
                interactive=not args.dry_run,
            )

            if args.dry_run:
                _validate_missing_files_for_blocks(blocks, root)
                LOGGER.info("clean content")
            elif not blocks:
                LOGGER.warning("No valid commit blocks found in clipboard.")
            elif not _process_all_commits(
                blocks,
                root,
                trace_git_commit=args.trace_git_commit,
            ):
                exit_code = 1
    except ClipboardError:
        LOGGER.exception("Failed to read clipboard")
        exit_code = 1
    except CommitMessageError:
        LOGGER.exception("Stopped due to invalid commit message")
        exit_code = 1
    except GitOperationError:
        LOGGER.exception("Git operation failed")
        exit_code = 1

    return exit_code


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with code 2."""
    _configure_logging(debug=False)
    LOGGER.exception("ERROR: %s", err)
    raise SystemExit(2) from err


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (GitBatchCommitError, OSError) as err:
        _log_fatal(err)


# eof
