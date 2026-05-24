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

The width wrap treats each inline backtick span as one indivisible
token, so a span like ```` `xx yyy zzz` ```` is never split across
lines even if it contains internal whitespace.

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
"""

from __future__ import annotations

import argparse
import contextlib
import logging
import re
import sys
from pathlib import Path
from typing import NoReturn

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools import find_project_root

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

# A list item starts at any indent, with a single ``-`` followed by a
# literal space. The captured group is the indent, which drives the
# continuation indent during wrapping.
LIST_ITEM_PATTERN = re.compile(r"^(\s*)- ")

# Conventional-commit subject: ``<type>(<scope>): <rest>``. When this
# matches the first line of a delimited block, that line is emitted
# verbatim (no backtick pass, no width wrap).
COMMIT_SUBJECT_PATTERN = re.compile(r"^\S+\(.*?\):\s")

# A word qualifies for inline-backtick wrapping when it carries at
# least this many uppercase letters (the CamelCase rule -- ``Xyz`` is
# below the bar, ``XyzUvw`` clears it).
CAMELCASE_UPPERCASE_THRESHOLD = 2

# Words that start with one of these patterns are exempted from the
# backtick-wrap rules. ``v\d+\.`` catches version literals such as
# ``v1.0`` or ``v2.5.3``; ``[Oo]\(`` catches big-O notation such as
# ``O(n)`` or ``o(log n)``.
WRAP_EXCEPTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^v\d+\."),
    re.compile(r"^[Oo]\("),
)

# Trailing punctuation that, when a word ends with it, always lives
# outside the closing backtick (e.g. ``foo_bar:`` becomes
# ``\`foo_bar\`:``). A trailing ``)`` is also pulled outside, but
# only when it is unbalanced -- ``foo(bar)`` keeps both parens inside,
# ``foo_bar)`` extracts the lone ``)``. A leading ``(`` is symmetric:
# pulled outside only when unbalanced, so ``(FlagValidationStatus,``
# extracts the lone ``(`` but ``(foo_bar)`` keeps both parens inside.
SENTENCE_TRAILING_PUNCTUATION = (".", ",", ":", ";")

LOGGER = logging.getLogger("wrap_commit")


class WrapCommitError(Exception):
    """Base exception raised by the wrap-commit tool."""


def _is_list_item(line: str) -> re.Match[str] | None:
    """Return the regex match if ``line`` opens a list item, else None.

    Args:
        line: The single text line to inspect.

    Returns:
        The ``re.Match`` whose first group is the captured indent, or
        ``None`` when the line is not a list item.
    """
    return LIST_ITEM_PATTERN.match(line)


def _find_backtick_regions(text: str) -> list[tuple[int, int]]:
    """Return the half-open spans covered by inline backtick pairs.

    Each successive pair of single backticks defines one span. The
    returned tuple is ``(start, end)`` -- inclusive start, exclusive
    end -- of the entire span including the surrounding backticks.
    An unmatched trailing backtick is ignored.

    Args:
        text: The text to scan for backtick spans.

    Returns:
        The list of ``(start, end)`` index pairs.
    """
    regions: list[tuple[int, int]] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j == -1:
                break
            regions.append((i, j + 1))
            i = j + 1
        else:
            i += 1
    return regions


def _word_overlaps_region(
    start: int,
    end: int,
    regions: list[tuple[int, int]],
) -> bool:
    """Return True if ``[start, end)`` intersects any of ``regions``."""
    return any(rs < end and start < re for rs, re in regions)


def _tokenize_keeping_backticks(text: str) -> list[str]:
    r"""Split ``text`` into tokens, treating each backtick span as one token.

    Whitespace outside inline-backtick regions delimits tokens;
    whitespace *inside* a region (e.g. ``\`xx yyy zzz\```) is preserved
    so the region is returned as a single indivisible token. This lets
    the width wrap keep a code span on one line instead of splitting it
    at the inner spaces.
    """
    regions = _find_backtick_regions(text)
    in_region: set[int] = set()
    for start, end in regions:
        in_region.update(range(start, end))

    tokens: list[str] = []
    current: list[str] = []
    for i, ch in enumerate(text):
        if ch.isspace() and i not in in_region:
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def _word_matches_wrap_exception(word: str) -> bool:
    """Return True if ``word`` starts with any of ``WRAP_EXCEPTION_PATTERNS``.

    Matching words are exempted from the inline-backtick wrap regardless
    of the regular rules. Used for conventional notations that look
    code-like but read better bare (version literals, big-O notation).
    """
    return any(pattern.match(word) for pattern in WRAP_EXCEPTION_PATTERNS)


def _word_has_other_chars_than(word: str, char: str) -> bool:
    """Return True if ``word`` contains ``char`` and at least one other character.

    Used so that a word consisting only of repeats of ``char`` (e.g.
    ``=``, ``==``, ``_``, ``__``) does not match the ``=`` or ``_``
    wrap rules, while ``=xx`` or ``xx_yy`` still does.
    """
    return char in word and any(c != char for c in word)


def _word_is_dashed_token(word: str) -> bool:
    """Return True if ``word`` is a dash-prefixed token followed by other chars.

    Catches CLI options of both short (``-x``) and long
    (``--no-backticks``, ``---foo``) forms while keeping bare
    separators (``-``, ``--``, ``---``) unwrapped.
    """
    return word.startswith("-") and any(c != "-" for c in word)


def _word_needs_backticks(word: str) -> bool:
    """Return True if ``word`` qualifies for inline-backtick wrapping.

    The word is first checked against ``WRAP_EXCEPTION_PATTERNS``: any
    match short-circuits to ``False`` so conventional notations like
    ``v1.0`` or ``O(n)`` stay bare even though they would otherwise hit
    a regular rule. Then a word qualifies when any of these holds:

    - it starts with one or more ``-`` followed by at least one non-dash
      character (CLI options such as ``-x``, ``--foo``,
      ``--no-backticks``; bare separators ``-``, ``--``, ``---`` do not
      qualify);
    - it contains an ``=`` mixed with at least one other character
      (assignment-shaped tokens such as ``KEY=value`` or ``--width=80``
      qualify; bare ``=`` or ``==`` do not);
    - it contains an underscore mixed with at least one other character
      (``foo_bar`` qualifies; bare ``_`` or ``__`` do not);
    - it contains a dot anywhere except as the very last character;
    - it contains an open parenthesis anywhere except as the very
      first character (closing parens are irrelevant -- ``x(r)`` qualifies
      via the ``(`` rule, ``X)`` does not);
    - it is CamelCase: it has at least ``CAMELCASE_UPPERCASE_THRESHOLD``
      uppercase letters AND at least one lowercase letter. Pure
      acronyms (``PBT``, ``URL``) and acronyms followed by punctuation
      (``PBT)``) carry no lowercase letter, so they stay bare.
    """
    if _word_matches_wrap_exception(word):
        return False
    return (
        _word_is_dashed_token(word)
        or _word_has_other_chars_than(word, "=")
        or _word_has_other_chars_than(word, "_")
        or "." in word[:-1]
        or "(" in word[1:]
        or _word_is_camelcase(word)
    )


def _word_is_camelcase(word: str) -> bool:
    """Return True if ``word`` is CamelCase under the wrap rule.

    Requires at least ``CAMELCASE_UPPERCASE_THRESHOLD`` uppercase
    letters AND at least one lowercase letter, so pure acronyms
    (``PBT``, ``URL``) and acronyms followed by punctuation
    (``PBT)``) stay bare.
    """
    upper_count = sum(1 for ch in word if ch.isupper())
    if upper_count < CAMELCASE_UPPERCASE_THRESHOLD:
        return False
    return any(ch.islower() for ch in word)


def _split_outer_punctuation(word: str) -> tuple[str, str, str]:
    """Split a word into ``(leading, core, trailing)`` at outer punctuation.

    ``leading`` is the run of leading ``(`` characters that exceeds the
    matching ``)`` count in the word -- only unbalanced opening parens
    are pulled out. ``(foo_bar)`` keeps both parens inside the core,
    while ``(FlagValidationStatus,`` extracts the lone leading ``(``.

    ``trailing`` is the maximal suffix made of characters in
    ``SENTENCE_TRAILING_PUNCTUATION`` plus any unbalanced trailing
    ``)`` (whose count exceeds the matching ``(`` count in the
    remainder). ``read_flag)`` extracts the ``)``, ``foo(bar)`` keeps
    it inside.

    ``core`` is whatever remains between the two.
    """
    # Leading: how many ``(`` cannot be matched against a later ``)``.
    open_count = word.count("(")
    close_count = word.count(")")
    leading_paren_excess = max(0, open_count - close_count)
    leading_idx = 0
    while (
        leading_idx < len(word)
        and leading_idx < leading_paren_excess
        and word[leading_idx] == "("
    ):
        leading_idx += 1
    leading = word[:leading_idx]
    remainder = word[leading_idx:]

    # Trailing: how many extra ``)`` can be pulled out of the remainder.
    rem_open = remainder.count("(")
    rem_close = remainder.count(")")
    close_budget = max(0, rem_close - rem_open)

    j = len(remainder)
    closes_taken = 0
    while j > 0:
        ch = remainder[j - 1]
        if ch in SENTENCE_TRAILING_PUNCTUATION:
            j -= 1
        elif ch == ")" and closes_taken < close_budget:
            j -= 1
            closes_taken += 1
        else:
            break

    core = remainder[:j]
    trailing = remainder[j:]
    return leading, core, trailing


def _add_backticks_to_words(text: str) -> str:
    """Wrap rule-matching words with backticks, skipping existing spans.

    Inline backtick spans in ``text`` are detected first and any
    whitespace-separated token whose character range overlaps one of
    those spans is left untouched. Other tokens are passed through
    ``_word_needs_backticks``; matching ones come back wrapped in a
    single pair of backticks. Outer punctuation is then split off via
    ``_split_outer_punctuation``: a trailing run of ``.,;:`` plus any
    unbalanced trailing ``)`` sits outside the closing backtick, and
    any unbalanced leading ``(`` sits outside the opening backtick.
    Balanced parens (``foo(bar)``, ``(foo_bar)``) stay inside.
    Whitespace runs are preserved verbatim.
    """
    regions = _find_backtick_regions(text)
    parts: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i].isspace():
            # Preserve whitespace runs verbatim so the surrounding
            # reflow keeps its spacing.
            j = i
            while j < n and text[j].isspace():
                j += 1
            parts.append(text[i:j])
            i = j
        else:
            # Walk a non-whitespace token, then decide whether to wrap it.
            j = i
            while j < n and not text[j].isspace():
                j += 1
            word = text[i:j]
            if (
                not _word_overlaps_region(i, j, regions)
                and _word_needs_backticks(word)
            ):
                leading, core, trailing = _split_outer_punctuation(word)
                if core:
                    parts.append(f"{leading}`{core}`{trailing}")
                else:
                    # Degenerate case: the whole token is outer
                    # punctuation -- nothing to wrap, keep it as-is.
                    parts.append(word)
            else:
                parts.append(word)
            i = j
    return "".join(parts)


def _wrap_words(
    words: list[str],
    width: int,
    first_prefix: str,
    cont_prefix: str,
) -> list[str]:
    """Greedy-wrap ``words`` into lines under ``width`` characters.

    The first emitted line starts with ``first_prefix``; every following
    line starts with ``cont_prefix``. Words are packed onto the current
    line while the resulting length stays ``<= width``. A single word
    longer than ``width`` is still emitted alone on its own line.

    Args:
        words: The list of whitespace-separated tokens to wrap.
        width: The maximum allowed line length, in characters.
        first_prefix: The literal prefix prepended to the first line.
        cont_prefix: The literal prefix prepended to every other line.

    Returns:
        The list of wrapped lines, without their trailing newlines.
    """
    # No words: keep the prefix alone (e.g., a bare ``- `` bullet) so
    # the structure does not disappear; otherwise nothing to emit.
    if not words:
        return [first_prefix.rstrip()] if first_prefix else []

    lines: list[str] = []
    current = first_prefix + words[0]
    for word in words[1:]:
        candidate = current + " " + word
        if len(candidate) <= width:
            current = candidate
        else:
            lines.append(current)
            current = cont_prefix + word
    lines.append(current)
    return lines


def _collect_continuation(
    lines: list[str],
    start: int,
) -> tuple[int, list[str]]:
    """Gather continuation lines starting at ``start``.

    A continuation line is one that is neither blank nor a list-item
    opener. The walk stops at the first line that fails that check; the
    stop line itself is not consumed.

    Args:
        lines: The full list of input lines.
        start: The index from which to start collecting.

    Returns:
        A pair ``(stop_index, stripped_parts)`` where ``stop_index`` is
        the index of the first non-continuation line and
        ``stripped_parts`` is the list of collected lines, each
        whitespace-trimmed.
    """
    parts: list[str] = []
    j = start
    while j < len(lines):
        nxt = lines[j]
        if nxt.strip() == "" or _is_list_item(nxt) is not None:
            break
        parts.append(nxt.strip())
        j += 1
    return j, parts


def reflow_lines(
    lines: list[str],
    width: int,
    *,
    add_backticks: bool = True,
) -> list[str]:
    r"""Reflow ``lines`` to enforce a maximum line width.

    Empty lines are passed through. Consecutive non-empty non-bullet
    lines collapse into one paragraph and wrap at column 0. A line that
    matches ``^(\s*)- `` opens a list item; its continuation lines
    (until a blank line or another list-item opener) are merged with
    the bullet content and re-wrapped, with continuation indented by
    ``len(indent) + 2`` spaces to line up under the bullet text.

    When ``add_backticks`` is True (the default), each merged paragraph
    or bullet content is passed through ``_add_backticks_to_words``
    before the width wrap, so code-like tokens get wrapped in single
    backticks unless they already live inside an inline backtick span.

    The width wrap tokenises through ``_tokenize_keeping_backticks``,
    so any inline backtick span (whether pre-existing or just added) is
    treated as one indivisible token -- a span like ``\`xx yyy zzz\```
    will never be split across lines.

    Args:
        lines: The input lines without their terminating newlines.
        width: The maximum allowed line width, in characters.
        add_backticks: When True, auto-wrap code-like tokens in
            backticks before the width wrap.

    Returns:
        The reflowed lines, without terminating newlines.
    """
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Blank lines are passed through verbatim.
        if line.strip() == "":
            out.append("")
            i += 1
            continue

        match = _is_list_item(line)
        if match is not None:
            # List item: merge the bullet head with its continuation
            # lines, then wrap with a column-aligned continuation prefix.
            indent = match.group(1)
            head_content = line[match.end():].strip()
            j, cont_parts = _collect_continuation(lines, i + 1)
            merged = " ".join(p for p in (head_content, *cont_parts) if p)
            if add_backticks:
                merged = _add_backticks_to_words(merged)
            words = _tokenize_keeping_backticks(merged)
            first_prefix = f"{indent}- "
            cont_prefix = " " * (len(indent) + 2)
            out.extend(_wrap_words(words, width, first_prefix, cont_prefix))
            i = j
        else:
            # Paragraph: collect everything until the next blank or
            # bullet, merge, then wrap at column 0.
            j, cont_parts = _collect_continuation(lines, i + 1)
            merged = " ".join(p for p in (line.strip(), *cont_parts) if p)
            if add_backticks:
                merged = _add_backticks_to_words(merged)
            words = _tokenize_keeping_backticks(merged)
            out.extend(_wrap_words(words, width, "", ""))
            i = j

    return out


def _reflow_block(
    block_lines: list[str],
    width: int,
    *,
    add_backticks: bool,
) -> list[str]:
    r"""Reflow a delimited block, preserving a leading commit subject.

    When the first line of ``block_lines`` matches
    ``COMMIT_SUBJECT_PATTERN`` (``^\S+\(.*?\):\s`` -- e.g.
    ``feat(tools): add cert-aware uv launcher``), that line is emitted
    verbatim, skipping both the backtick pass and the width wrap. The
    remaining lines go through ``reflow_lines`` as usual. When the
    first line does not match, the whole block is reflowed normally.
    """
    if block_lines and COMMIT_SUBJECT_PATTERN.match(block_lines[0]):
        return [
            block_lines[0],
            *reflow_lines(
                block_lines[1:], width, add_backticks=add_backticks,
            ),
        ]
    return reflow_lines(block_lines, width, add_backticks=add_backticks)


def process_text(
    text: str,
    width: int,
    open_delim: str | None,
    close_delim: str | None,
    *,
    add_backticks: bool = True,
) -> str:
    r"""Reflow ``text`` either as a whole or only inside delimited blocks.

    When both delimiters are ``None``, the whole text is reflowed.
    Otherwise, only the content strictly between matching open/close
    delimiter lines is reflowed; delimiter lines and any text outside a
    block are preserved verbatim. An unterminated block at EOF still
    has its collected content reflowed so nothing is dropped.

    When delimiters are configured, the first line of each block is
    inspected against ``COMMIT_SUBJECT_PATTERN``; on a match the line
    is preserved verbatim, otherwise the block is fully reflowed.

    Args:
        text: The full input file content.
        width: The maximum allowed line width inside a block.
        open_delim: The opening fence line (matched after ``strip()``)
            or ``None`` to disable fence detection.
        close_delim: The closing fence line (matched after ``strip()``)
            or ``None`` to disable fence detection.
        add_backticks: When True, auto-wrap code-like tokens in
            backticks before the width wrap.

    Returns:
        The rewritten text. The presence of a trailing newline is
        carried over from the input.
    """
    has_trailing_newline = text.endswith("\n")

    # Whole-file mode: reflow everything in one pass.
    if open_delim is None and close_delim is None:
        out_lines = reflow_lines(
            text.splitlines(),
            width,
            add_backticks=add_backticks,
        )
        return "\n".join(out_lines) + ("\n" if has_trailing_newline else "")

    lines = text.splitlines()
    out_lines: list[str] = []
    block_lines: list[str] = []
    in_block = False

    for line in lines:
        if in_block:
            if line.strip() == close_delim:
                # End of block: reflow the collected body (preserving
                # a leading commit subject), then emit the close-fence.
                out_lines.extend(
                    _reflow_block(block_lines, width, add_backticks=add_backticks),
                )
                out_lines.append(line)
                in_block = False
                block_lines = []
            else:
                block_lines.append(line)
        else:
            out_lines.append(line)
            if line.strip() == open_delim:
                in_block = True
                block_lines = []

    # Unterminated block: still flush its content so nothing is lost.
    if in_block:
        out_lines.extend(
            _reflow_block(block_lines, width, add_backticks=add_backticks),
        )

    return "\n".join(out_lines) + ("\n" if has_trailing_newline else "")


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

    updated = process_text(
        original,
        args.width,
        open_delim,
        close_delim,
        add_backticks=not args.no_backticks,
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


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (WrapCommitError, OSError) as err:
        _log_fatal(err)


# eof
