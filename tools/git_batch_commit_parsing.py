"""Parsing helpers for git batch commit.

Fix: Split clipboard, commit-message, and git-add parsing helpers out of
`tools.git_batch_commit` so the workflow and git-operation code can stay in
smaller files without changing parsing behavior.

Fix: Keep wrapped continuation lines when parsing the What section, so a
multi-line `- ` item no longer truncates the commit message at its first
physical line.

Fix: Fail fast when a git-add block is followed by an unscoped conventional
commit title, so validation does not pair those paths with the next scoped
title later in the plan.
"""

from __future__ import annotations

import logging
import shlex
import shutil
import subprocess

from tools.git_batch_commit_models import (
    COMMIT_TITLE_PATTERN as _COMMIT_TITLE_PATTERN,
)
from tools.git_batch_commit_models import (
    GIT_ADD_MIN_PARTS as _GIT_ADD_MIN_PARTS,
)
from tools.git_batch_commit_models import (
    LIST_ITEM_PATTERN as _LIST_ITEM_PATTERN,
)
from tools.git_batch_commit_models import (
    ClipboardError,
    CommitBlock,
    CommitMessageError,
)
from tools.git_batch_commit_models import (
    ParseState as _ParseState,
)

LOGGER = logging.getLogger("git_batch_commit")


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
    except subprocess.SubprocessError as err:
        msg = f"Failed to read clipboard: {err}"
        raise ClipboardError(msg) from err


# ----------------------------
# Commit message validation helpers
# ----------------------------


def _is_commit_title(line: str) -> bool:
    """Check if a line matches the commit title pattern xxxx(yyyy): zzz."""
    return bool(_COMMIT_TITLE_PATTERN.match(line))


def _is_probable_unscoped_commit_title(line: str) -> bool:
    """Return whether a line looks like a title but misses the required scope."""
    stripped = line.strip()
    if _is_commit_title(stripped):
        return False
    if ": " not in stripped:
        return False
    title_type, _subject = stripped.split(": ", 1)
    return bool(title_type) and "(" not in title_type and " " not in title_type


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


def _ends_what_section(line: str) -> bool:
    """Check if a line ends the What list section.

    The What section is the last section of a commit message, and its
    list items may wrap onto continuation lines that do not start with
    '- '. The section only ends at a structural boundary: an empty line,
    a code fence, a markdown header, the next git add command, or the
    next commit title.
    """
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith(("```", "#")):
        return True
    if stripped.startswith("git add "):
        return True
    return _is_commit_title(stripped)


def _parse_list_items(state: _ParseState) -> list[str]:
    """Parse the What section, keeping wrapped continuation lines.

    A What item may span several physical lines: only the first line
    starts with '- ', and the following continuation lines do not. The
    section ends at the first boundary reported by `_ends_what_section`,
    or at the end of input. Continuation lines are kept so a multi-line
    item is not truncated at its first physical line.
    """
    items: list[str] = []
    started = False
    while state.idx < len(state.lines):
        line = state.lines[state.idx]
        if _is_list_item(line):
            started = True
        elif not started or _ends_what_section(line):
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
    lines_read: list[str] = []
    while idx < len(lines):
        line = lines[idx].strip()
        if _is_commit_title(line):
            return idx
        if _is_probable_unscoped_commit_title(line):
            msg = (
                "Invalid commit title format after git add commands: expected "
                "'type(scope): subject'. Add a scope instead of letting this "
                f"block bind to a later title. Found: {line!r}"
            )
            raise CommitMessageError(msg, lines_read, line)
        if line:
            lines_read.append(line)
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
        except CommitMessageError as err:
            LOGGER.warning("Invalid commit message structure:")
            LOGGER.warning("Lines read so far:")
            for line in err.lines_read:
                LOGGER.warning("  %s", line)
            if err.faulty_line:
                LOGGER.warning("Faulty line: %s", err.faulty_line)
            LOGGER.warning("Error: %s", err)

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


get_clipboard_text = _get_clipboard_text
parse_git_add_command = _parse_git_add_command


__all__ = [
    "_ends_what_section",
    "_expect_empty_line",
    "_expect_keyword",
    "_get_clipboard_text",
    "_is_commit_title",
    "_is_list_item",
    "_is_probable_unscoped_commit_title",
    "_parse_commit_message",
    "_parse_git_add_command",
    "_parse_git_adds",
    "_parse_list_items",
    "_parse_non_empty_section",
    "_parse_title",
    "_skip_until_commit_title",
    "_skip_until_git_add",
    "parse_clipboard_content",
]


# eof
