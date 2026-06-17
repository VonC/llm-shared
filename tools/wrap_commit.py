r"""Reflow text inside delimited blocks of a commit-message file.

By default this tool reads ``<project_root>/a.commit`` and, for every
block delimited by a ```` ```log ```` opener and a ```` ``` ```` closer
(the conventional ``git_batch_commit`` body fence), wraps the lines so
that no line exceeds 80 characters. Empty lines are passed through. A
line matching ``^(\s*)- `` opens a list item; its continuation lines
(until an empty line or another list-item line) are merged with the
bullet content and re-wrapped together. The first emitted line keeps
the original ``- `` marker (with its leading whitespace); continuation
lines are indented by ``len(indent) + 2`` spaces -- matching the visual
column where the bullet text starts. Other lines are treated as a
paragraph: consecutive non-empty, non-bullet lines are merged and
wrapped at the requested width with no leading indent on the
continuation lines.

Before the width wrap runs, every merged paragraph or bullet is also
passed through an inline-backtick pass: existing ```` `...` ```` spans
are detected up front, then any whitespace-separated word that does
not overlap one of those spans is wrapped in single backticks when it
looks code-like, i.e. it starts with one or more ``-`` followed by
at least one non-dash character (CLI options such as ``-x``,
``--no-backticks``; bare ``-`` / ``--`` / ``---`` separators do
not), it contains an ``=`` mixed with at least one other character
(``KEY=value`` qualifies; bare ``=`` or ``==`` do not), it contains
an underscore mixed with at least one other character (``foo_bar``
qualifies; bare ``_`` or ``__`` do not), it has a non-trailing dot,
a non-leading open parenthesis, or is CamelCase (at least two
uppercase letters AND at least one lowercase letter -- so pure
acronyms such as ``PBT`` or ``URL`` stay bare, including when
followed by punctuation like ``PBT)``). When a wrapped token is bracketed by outer punctuation,
that punctuation is pulled outside the backticks: a trailing run of
``.``, ``,``, ``:``, ``;`` is always extracted (``foo_bar:`` becomes
```` `foo_bar`: ````), and a leading ``(`` or trailing ``)`` is
extracted only when unbalanced. So ``foo(bar)`` keeps both parens
inside (```` `foo(bar)` ````) while ``read_flag)`` strips the lone
``)`` (```` `read_flag`) ````) and ``(FlagValidationStatus,`` strips
the lone ``(`` (```` (`FlagValidationStatus`, ````). Any other
punctuation stays inside.

A short whitelist of conventional notations is exempted from the
backtick wrap altogether: any word starting with ``v\d+\.`` (version
literals like ``v1.0``, ``v2.5.3``) or ``[Oo]\(`` (big-O notation like
``O(n)``, ``o(log n)``) is left bare.

In a paragraph (not a bullet item list, and not the commit subject),
one more rule applies before the adjacent-span merge: any word holding a
forward slash ``/`` or a backslash ``\`` mixed with other characters is
wrapped too (path-shaped tokens like ``src/pdfss`` or ``C:\Users\vonc``,
and ``and/or``; a bare ``/`` or ``\`` separator stays bare). Bullet
items keep the regular code-like rules only, so this path-separator rule
never reaches a list line.

A wrap-list pass runs first, before the inline-backtick pass, whenever
one or more ``wrap-list.backtick`` files are found. Each file is looked
up in the wrap tool's own folder, in the calling folder and every parent
up to and including the project root, and in the user home folder (the
``HOME`` environment variable when set, otherwise the OS home); the
contents are concatenated, and every non-blank line is one string
literal (a word or a run of words separated by single spaces). Each
free-standing occurrence of a literal in a commit body -- bounded by a
non-word character or a line edge, so ``cat`` never matches inside
``concatenate`` -- is wrapped in backticks unless it already sits inside
a backtick span. Multi-word literals are wrapped as one span, and the
later adjacent-span merge can still fold neighbouring spans together.
The wrap-list pass touches commit bodies only, never a group line or a
commit subject. With no ``wrap-list.backtick`` file anywhere, this pass
does nothing and the output matches the earlier no-config behaviour.

After the inline-backtick pass and before the width wrap, an
adjacent-span merge runs on each merged paragraph or bullet: two
```` `...` ```` spans separated only by inter-span whitespace -- a run
of spaces, or a single newline with optional surrounding indentation --
are folded into one span whose contents are joined by a single space,
so ```` `a` `b` `c` ```` becomes ```` `a b c` ````. The merge repeats
to a fixpoint, so a whole run collapses at once. A blank line or a
following ``- `` bullet marker breaks the run, so spans in different
paragraphs or list items never merge. Because each paragraph or bullet
is collapsed to a single line first, spans that were split across two
lines in the input land side by side and merge here too.

The width wrap treats each inline backtick span as one indivisible
token, so a span like ```` `xx yyy zzz` ```` is never split across
lines even if it contains internal whitespace.

Once the backtick pass and width wrap are done, a final strip runs on
each emitted body line: a line that opens with a backticked
```` `type(scope)`: ```` -- the conventional-commit subject shape that
the word pass wraps via the non-leading open-paren rule (the colon
pulled outside, the balanced parens kept inside) -- has those two
backticks removed, so the opener reads ``type(scope):`` bare. The strip
is line-anchored, so it leaves bullet lines (which open with ``- ``) and
indented lines alone; ``--no-backticks`` skips it along with the rest of
the backtick work.

When the very first line of a delimited block matches
``^\S+\(.*?\):\s`` -- the conventional-commit subject shape such as
``feat(tools): add cert-aware uv launcher`` -- that line is emitted
verbatim: it is skipped by both the backtick pass and the width wrap.
The rule applies only to the first line of each block and only when
delimiters are configured (i.e. not under ``--no-delimiters``).

CLI flags ``--width``, ``--open`` and ``--close`` override the
defaults; ``--no-delimiters`` reflows the entire file in one go;
``--no-backticks`` skips the inline-backtick pass; ``--check`` performs
a dry run that reports whether the file would be rewritten without
touching it on disk.

Fix: split for the repo line budget -- the inline-backtick word rules
and passes moved to ``tools.wrap_commit_backticks``, the reflow and
block drivers to ``tools.wrap_commit_reflow``, and the wrap-list config
discovery to ``tools.wrap_commit_wraplist``; this file stays the script
entry point and import hub re-exporting the public API.
"""

from __future__ import annotations

import argparse
import contextlib
import logging
import sys
from pathlib import Path
from typing import NoReturn

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools import find_project_root
from tools.wrap_commit_reflow import (
    COMMIT_SUBJECT_PATTERN,
    process_text,
    reflow_lines,
)
from tools.wrap_commit_wraplist import (
    WRAP_LIST_FILE_NAME,
)
from tools.wrap_commit_wraplist import (
    collect_wrap_list_literals as _collect_wrap_list_literals,
)

# Default maximum line width inside a delimited block.
DEFAULT_WIDTH = 80
# Default opening fence (matches the ``git_batch_commit`` body marker).
DEFAULT_OPEN = "```log"
# Default closing fence.
DEFAULT_CLOSE = "```"
# Default file name relative to the project root.
DEFAULT_FILE_NAME = "a.commit"
# Exit code returned by ``--check`` when the file would be rewritten.
EXIT_CHANGES_PENDING = 1
# Exit code used by the script entry point for fatal errors.
EXIT_FATAL = 2

LOGGER = logging.getLogger("wrap_commit")


class WrapCommitError(Exception):
    """Base exception raised by the wrap-commit tool."""


def _configure_logging() -> None:
    """Configure a single stdout handler at INFO level for the tool."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Parse command-line arguments for the wrap-commit tool."""
    parser = argparse.ArgumentParser(
        description=(
            "Reflow text inside delimited blocks of a commit-message "
            "file to a maximum line width."
        ),
    )
    parser.add_argument(
        "--file",
        default=None,
        help=(
            "Path to the file to process "
            f"(default: <project_root>/{DEFAULT_FILE_NAME})."
        ),
    )
    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_WIDTH,
        help=f"Maximum line width (default: {DEFAULT_WIDTH}).",
    )
    parser.add_argument(
        "--open",
        default=DEFAULT_OPEN,
        help=f"Opening delimiter line (default: {DEFAULT_OPEN!r}).",
    )
    parser.add_argument(
        "--close",
        default=DEFAULT_CLOSE,
        help=f"Closing delimiter line (default: {DEFAULT_CLOSE!r}).",
    )
    parser.add_argument(
        "--no-delimiters",
        action="store_true",
        help="Reflow the entire file instead of just the delimited blocks.",
    )
    parser.add_argument(
        "--no-backticks",
        action="store_true",
        help=(
            "Skip the inline-backtick pass that auto-wraps code-like "
            "tokens (underscore, non-trailing dot, non-leading open "
            "paren, or CamelCase with 2+ uppercase AND 1+ lowercase) "
            "before the width wrap."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Do not write the file; exit with code 1 if changes would "
            "be made, 0 otherwise."
        ),
    )
    return parser.parse_args(argv)


def _resolve_target_file(args: argparse.Namespace) -> Path:
    """Resolve the target file path from CLI args.

    When ``--file`` is provided, the explicit path (after user-tilde
    expansion) is returned. Otherwise the shared ``find_project_root``
    helper locates the calling project's root and the default file name
    is appended.

    Args:
        args: The parsed argparse namespace.

    Returns:
        The resolved absolute path to the file the tool should rewrite.
    """
    if args.file:
        return Path(args.file).expanduser().resolve()
    root = find_project_root(Path.cwd())
    return root / DEFAULT_FILE_NAME


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: reflow text in the configured file in place.

    Args:
        argv: The argument vector (without the program name). When
            ``None``, ``argparse`` reads from ``sys.argv``.

    Returns:
        ``0`` on success, ``EXIT_CHANGES_PENDING`` (1) under ``--check``
        when the file would be rewritten.
    """
    _configure_logging()
    args = _parse_args(argv)

    target = _resolve_target_file(args)
    if not target.is_file():
        msg = f"File not found: {target}"
        raise WrapCommitError(msg)

    original = target.read_text(encoding="utf-8")
    open_delim = None if args.no_delimiters else args.open
    close_delim = None if args.no_delimiters else args.close
    literals = _collect_wrap_list_literals(Path.cwd())

    updated = process_text(
        original,
        args.width,
        open_delim,
        close_delim,
        add_backticks=not args.no_backticks,
        literals=literals,
    )

    if updated == original:
        LOGGER.info("No changes needed for %s", target)
        return 0

    if args.check:
        LOGGER.info("Changes would be made to %s", target)
        return EXIT_CHANGES_PENDING

    target.write_text(updated, encoding="utf-8")
    LOGGER.info("Reflowed %s", target)
    return 0


def _log_fatal(err: Exception) -> NoReturn:
    """Log a fatal error and exit with ``EXIT_FATAL``."""
    LOGGER.exception("ERROR: %s", err)
    raise SystemExit(EXIT_FATAL) from err


__all__ = [
    "COMMIT_SUBJECT_PATTERN",
    "DEFAULT_CLOSE",
    "DEFAULT_FILE_NAME",
    "DEFAULT_OPEN",
    "DEFAULT_WIDTH",
    "EXIT_CHANGES_PENDING",
    "EXIT_FATAL",
    "WRAP_LIST_FILE_NAME",
    "WrapCommitError",
    "main",
    "process_text",
    "reflow_lines",
]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (WrapCommitError, OSError) as err:
        _log_fatal(err)


# eof
