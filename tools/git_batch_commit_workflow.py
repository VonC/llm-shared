"""Workflow helpers for git batch commit.

Fix: Split the CLI setup, root-plan replay, input reading, and commit loop out
of `tools.git_batch_commit` so the main script stays below the repository size
limit while keeping the same behavior.

Fix: Hide tracebacks for clear handled errors by default while keeping a verbose
flag for diagnostic runs.

Fix: In the root a.commit validation phase, check that the plan lists one
`git add` per staged file, and empty a.commit after every commit lands so a
stale plan is not mistaken for pending work on the next run.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import NoReturn

from tools import find_project_root
from tools.git_batch_commit_git import (
    block_has_staged_changes as _block_has_staged_changes,
)
from tools.git_batch_commit_git import (
    git_add_files,
    git_commit,
    git_reset,
)
from tools.git_batch_commit_git import (
    is_worktree_clean as _is_worktree_clean,
)
from tools.git_batch_commit_git import (
    validate_missing_files_for_blocks as _validate_missing_files_for_blocks,
)
from tools.git_batch_commit_git import (
    validate_staged_count_matches_git_adds as _validate_staged_count_matches_git_adds,
)
from tools.git_batch_commit_models import (
    ClipboardError,
    CommitBlock,
    CommitMessageError,
    GitBatchCommitError,
    GitOperationError,
)
from tools.git_batch_commit_parsing import (
    get_clipboard_text as _get_clipboard_text,
)
from tools.git_batch_commit_parsing import (
    parse_clipboard_content,
)

LOGGER = logging.getLogger("git_batch_commit")


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
        "-v",
        "--verbose",
        action="store_true",
        help="Show Python tracebacks for handled errors.",
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

    if _is_worktree_clean(root):
        msg = (
            "Refusing to replay project root a.commit because the working tree "
            "is clean. The commit plan is already applied or there is nothing "
            "to commit."
        )
        raise GitBatchCommitError(msg)

    _validate_staged_count_matches_git_adds(blocks, root)
    LOGGER.info("Validation phase passed.")

    LOGGER.info("Commit phase: applying commit plan now...")
    if not _process_all_commits(
        blocks,
        root,
        trace_git_commit=trace_git_commit,
    ):
        return 1

    _empty_a_commit_file(root)
    return 0


def _empty_a_commit_file(root: Path) -> None:
    """Empty <root>/a.commit after a fully successful root commit run.

    Once every block has been committed the plan is spent. Truncating the file
    keeps a later reader (a human or an LLM) from seeing leftover git add lines
    and believing some commits are still pending.
    """
    a_commit_path = root / "a.commit"
    try:
        a_commit_path.write_text("", encoding="utf-8")
    except OSError as err:
        LOGGER.warning("Could not empty %s: %s", a_commit_path, err)
        return
    LOGGER.info("Emptied %s after a successful commit run.", a_commit_path)


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
    except OSError as err:
        msg = f"Failed to read input file: {resolved_path}"
        raise GitBatchCommitError(msg) from err


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


def _log_handled_error(label: str, err: Exception, *, verbose: bool) -> None:
    """Log a handled CLI error with an optional traceback."""
    if verbose:
        LOGGER.exception(label)
        return
    LOGGER.error(label)
    LOGGER.error("%s", err)


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
    add_outcome = git_add_files(block.git_adds, root)
    if not add_outcome.should_continue:
        LOGGER.info("Stopping at commit %d on user request.", i)
        return False
    if add_outcome.should_skip_commit:
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
    except ClipboardError as err:
        _log_handled_error(
            "Failed to read clipboard",
            err,
            verbose=args.verbose,
        )
        exit_code = 1
    except CommitMessageError as err:
        _log_handled_error(
            "Stopped due to invalid commit message",
            err,
            verbose=args.verbose,
        )
        exit_code = 1
    except GitOperationError as err:
        _log_handled_error(
            "Git operation failed",
            err,
            verbose=args.verbose,
        )
        exit_code = 1

    return exit_code


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with code 2."""
    _configure_logging(debug=False)
    LOGGER.exception("ERROR: %s", err)
    raise SystemExit(2) from err


__all__ = [
    "_configure_logging",
    "_empty_a_commit_file",
    "_get_arg_parser",
    "_log_fatal",
    "_log_handled_error",
    "_process_all_commits",
    "_process_commit_block",
    "_read_and_parse_content",
    "_read_input_content",
    "_run_root_a_commit_workflow",
    "main",
]


# eof
