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

Fix: Preserve the difference between `skip` and `stop` when `git add` review
finds missing paths or failed add commands, so interactive stop choices really
stop the batch run.

Fix: Treat Git pathspec targets such as `:(glob)...` as valid `git add`
arguments during precheck instead of rejecting them as missing disk paths.

Fix (split): move models, parsing helpers, Git helpers, and workflow logic
into dedicated modules while keeping this file as the script and import hub.
"""

from __future__ import annotations

import contextlib
import logging
import sys
from pathlib import Path
from typing import NoReturn

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))
        sys.path.insert(0, str((_project_root / "src").resolve()))

with contextlib.suppress(Exception):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools.git_batch_commit_git import git_add_files, git_commit, git_reset
from tools.git_batch_commit_models import (
    ClipboardError,
    CommitBlock,
    CommitMessageError,
    GitBatchCommitError,
    GitOperationError,
)
from tools.git_batch_commit_parsing import parse_clipboard_content
from tools.git_batch_commit_workflow import main as _workflow_main

LOGGER = logging.getLogger("git_batch_commit")


def _configure_logging() -> None:
    """Configure fatal-error logging for direct script execution."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with code 2 when the script hub is executed directly."""
    _configure_logging()
    LOGGER.exception("ERROR: %s", err)
    raise SystemExit(2) from err


def main(argv: list[str] | None = None) -> int:
    """Delegate CLI execution to the workflow module."""
    return _workflow_main(argv)


__all__ = [
    "ClipboardError",
    "CommitBlock",
    "CommitMessageError",
    "GitBatchCommitError",
    "GitOperationError",
    "git_add_files",
    "git_commit",
    "git_reset",
    "main",
    "parse_clipboard_content",
]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (GitBatchCommitError, OSError) as err:
        _log_fatal(err)


# eof
