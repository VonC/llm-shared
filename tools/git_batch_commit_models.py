"""Shared models and exceptions for git batch commit.

Fix: Split the data model and parser constants out of
`tools.git_batch_commit` so the script hub can stay below the repository size
limit while keeping the same public types.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

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


@dataclass(frozen=True)
class _GitAddOutcome:
    """Outcome of one git-add phase, including whether the batch should stop."""

    should_continue: bool
    should_skip_commit: bool = False


COMMIT_TITLE_PATTERN = _COMMIT_TITLE_PATTERN
GIT_ADD_MIN_PARTS = _GIT_ADD_MIN_PARTS
GIT_TRACE_ENABLED_VALUE = _GIT_TRACE_ENABLED_VALUE
LIST_ITEM_PATTERN = _LIST_ITEM_PATTERN
GitAddOutcome = _GitAddOutcome
GitInvocationOptions = _GitCommandOptions
ParseState = _ParseState


__all__ = [
    "_COMMIT_TITLE_PATTERN",
    "_GIT_ADD_MIN_PARTS",
    "_GIT_TRACE_ENABLED_VALUE",
    "_LIST_ITEM_PATTERN",
    "ClipboardError",
    "CommitBlock",
    "CommitMessageError",
    "GitBatchCommitError",
    "GitOperationError",
    "_GitAddOutcome",
    "_GitCommandOptions",
    "_ParseState",
]


# eof
