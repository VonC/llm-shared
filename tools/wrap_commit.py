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
import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from collections.abc import Callable

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
# Config file name whose lines are extra string literals to backtick in
# commit bodies. Searched in the tool folder, the calling folder and its
# parents up to the project root, and the user home folder.
WRAP_LIST_FILE_NAME = "wrap-list.backtick"
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

# Two inline backtick spans separated only by inter-span whitespace --
# a run of spaces/tabs, or a single newline with optional surrounding
# indentation -- are merged into one span by
# ``_merge_adjacent_backtick_spans``. Allowing at most one newline keeps
# a blank line (a paragraph break) or a following ``- `` bullet marker
# from joining spans that belong to different paragraphs or list items.
ADJACENT_BACKTICK_SPANS_PATTERN = re.compile(
    r"`([^`\r\n]+)`(?:[ \t]*\r?\n[ \t]*|[ \t]+)`([^`\r\n]+)`",
)

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


def _word_has_path_separator(word: str) -> bool:
    r"""Return True if ``word`` carries a path separator mixed with content.

    A word qualifies when it contains a forward slash ``/`` or a
    backslash ``\`` plus at least one character that is neither, so
    path-shaped tokens like ``src/pdfss``, ``C:\Users\vonc``, or
    ``and/or`` qualify while bare separators (``/``, ``\``, ``//``)
    stay bare. This mirrors the mixed-content rule used for ``=`` and
    ``_`` so a lone separator is never wrapped on its own.
    """
    has_separator = "/" in word or "\\" in word
    has_other = any(ch not in "/\\" for ch in word)
    return has_separator and has_other


def _word_needs_backticks_in_paragraph(word: str) -> bool:
    r"""Return True if ``word`` needs backticks under the paragraph rules.

    Paragraph bodies use the regular ``_word_needs_backticks`` rules plus
    the path-separator rule: a word holding a ``/`` or ``\`` is wrapped
    too. Bullets (the item list) keep the regular rules only, so this
    extra rule never reaches a list item.
    """
    return _word_needs_backticks(word) or _word_has_path_separator(word)


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


def _add_backticks_to_words(
    text: str,
    needs_backticks: Callable[[str], bool] = _word_needs_backticks,
) -> str:
    """Wrap rule-matching words with backticks, skipping existing spans.

    Inline backtick spans in ``text`` are detected first and any
    whitespace-separated token whose character range overlaps one of
    those spans is left untouched. Other tokens are passed through
    ``needs_backticks`` (``_word_needs_backticks`` by default; the
    paragraph caller passes ``_word_needs_backticks_in_paragraph`` to add
    the path-separator rule); matching ones come back wrapped in a single
    pair of backticks. Outer punctuation is then split off via
    ``_split_outer_punctuation``: a trailing run of ``.,;:`` plus any
    unbalanced trailing ``)`` sits outside the closing backtick, and
    any unbalanced leading ``(`` sits outside the opening backtick.
    Balanced parens (``foo(bar)``, ``(foo_bar)``) stay inside.
    Whitespace runs are preserved verbatim.

    Args:
        text: The text whose qualifying words should be backticked.
        needs_backticks: The predicate that decides whether a word
            qualifies for wrapping.

    Returns:
        The text with each qualifying free-standing word backticked.
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
                and needs_backticks(word)
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


def _add_backticks_to_literals(text: str, literals: list[str]) -> str:
    r"""Wrap each configured wrap-list literal in backticks.

    Every literal is matched as a free-standing token or token run --
    bounded on each side by a non-word character or a string edge, so
    ``cat`` never matches inside ``concatenate`` -- and each occurrence
    that does not overlap an existing inline backtick span is wrapped in
    a single backtick pair. Longer literals are handled first (ties
    broken alphabetically for a stable result), so a multi-word literal
    such as ``del .testmondata`` wins over a shorter literal that is also
    one of its words.

    Args:
        text: The text whose configured literals should be backticked.
        literals: The wrap-list literal strings, in any order. Empty
            strings and duplicates are ignored.

    Returns:
        The text with each free-standing literal occurrence backticked.
    """
    for literal in sorted({lit for lit in literals if lit}, key=lambda s: (-len(s), s)):
        pattern = re.compile(rf"(?<!\w){re.escape(literal)}(?!\w)")
        regions = _find_backtick_regions(text)
        parts: list[str] = []
        last = 0
        for match in pattern.finditer(text):
            start, end = match.start(), match.end()
            # Skip an occurrence that already lives inside a backtick span.
            if _word_overlaps_region(start, end, regions):
                continue
            parts.append(text[last:start])
            parts.append(f"`{literal}`")
            last = end
        parts.append(text[last:])
        text = "".join(parts)
    return text


def _merge_adjacent_backtick_spans(text: str) -> str:
    r"""Fold runs of whitespace-separated backtick spans into one span.

    Two inline ``\`...\``` spans separated only by inter-span whitespace
    -- a run of spaces or tabs, or a single newline with optional
    surrounding indentation -- are merged into a single span whose two
    contents are joined by one space. The substitution repeats until it
    reaches a fixpoint, so a whole run such as ``\`a\` \`b\` \`c\```
    collapses to ``\`a b c\```.

    The separator allows at most one newline and no other characters, so
    a blank line (a paragraph break) or a following ``- `` bullet marker
    never pulls two spans together: spans living in different paragraphs
    or list items are left apart.

    Args:
        text: The text whose adjacent backtick spans should be merged.

    Returns:
        The text with each whitespace-separated run of backtick spans
        folded into a single span.
    """
    while True:
        merged = ADJACENT_BACKTICK_SPANS_PATTERN.sub(r"`\1 \2`", text)
        if merged == text:
            return text
        text = merged


def _apply_inline_backticks(
    text: str,
    *,
    add_backticks: bool,
    literals: list[str],
    needs_backticks: Callable[[str], bool] = _word_needs_backticks,
) -> str:
    """Run the wrap-list, code-like, and merge passes on one segment.

    When ``add_backticks`` is False the text is returned unchanged.
    Otherwise the configured wrap-list ``literals`` are backticked first
    (multi-word literals as one span), then the words matched by
    ``needs_backticks``, and finally adjacent backtick spans are merged
    into one. Running the wrap-list pass before the word pass keeps a
    multi-word literal whole and lets the word pass skip the words it
    already wrapped. The merge always runs last, so the path-separator
    spans added under the paragraph predicate can still fold together.

    Args:
        text: One merged paragraph or bullet segment, on a single line.
        add_backticks: When False, skip every backtick pass.
        literals: The wrap-list literals to backtick before the word
            pass.
        needs_backticks: The word predicate. Paragraphs pass
            ``_word_needs_backticks_in_paragraph`` (regular rules plus the
            path-separator rule); bullets keep the default regular rules.

    Returns:
        The segment after the wrap-list, word, and merge passes.
    """
    if not add_backticks:
        return text
    text = _add_backticks_to_literals(text, literals)
    text = _add_backticks_to_words(text, needs_backticks)
    return _merge_adjacent_backtick_spans(text)


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
    literals: list[str] | None = None,
) -> list[str]:
    r"""Reflow ``lines`` to enforce a maximum line width.

    Empty lines are passed through. Consecutive non-empty non-bullet
    lines collapse into one paragraph and wrap at column 0. A line that
    matches ``^(\s*)- `` opens a list item; its continuation lines
    (until a blank line or another list-item opener) are merged with
    the bullet content and re-wrapped, with continuation indented by
    ``len(indent) + 2`` spaces to line up under the bullet text.

    When ``add_backticks`` is True (the default), each merged paragraph
    or bullet content is first passed through ``_add_backticks_to_literals``
    with ``literals``, so any configured wrap-list literal that is not
    already inside a span gets wrapped, then through
    ``_add_backticks_to_words``, so code-like tokens get wrapped in single
    backticks unless they already live inside an inline backtick span. A
    paragraph also wraps any word holding a ``/`` or ``\`` path separator
    (the bullet item list keeps the regular rules only).
    The same content then goes through ``_merge_adjacent_backtick_spans``,
    so a run of whitespace-separated spans like ``\`a\` \`b\` \`c\```
    (including spans that the source split across two lines, now joined
    by the paragraph collapse) folds into one ``\`a b c\``` span before
    the width wrap re-flows it as a single token.

    The width wrap tokenises through ``_tokenize_keeping_backticks``,
    so any inline backtick span (whether pre-existing or just added) is
    treated as one indivisible token -- a span like ``\`xx yyy zzz\```
    will never be split across lines.

    Args:
        lines: The input lines without their terminating newlines.
        width: The maximum allowed line width, in characters.
        add_backticks: When True, auto-wrap code-like tokens in
            backticks before the width wrap.
        literals: Extra wrap-list string literals to backtick before the
            code-like pass. ``None`` (the default) means no wrap-list.

    Returns:
        The reflowed lines, without terminating newlines.
    """
    wrap_literals = literals or []
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
            merged = _apply_inline_backticks(
                merged, add_backticks=add_backticks, literals=wrap_literals,
            )
            words = _tokenize_keeping_backticks(merged)
            first_prefix = f"{indent}- "
            cont_prefix = " " * (len(indent) + 2)
            out.extend(_wrap_words(words, width, first_prefix, cont_prefix))
            i = j
        else:
            # Paragraph: collect everything until the next blank or
            # bullet, merge, then wrap at column 0. Paragraphs add the
            # path-separator rule (a ``/`` or ``\`` word gets backticked);
            # the bullet branch above keeps the regular rules only.
            j, cont_parts = _collect_continuation(lines, i + 1)
            merged = " ".join(p for p in (line.strip(), *cont_parts) if p)
            merged = _apply_inline_backticks(
                merged,
                add_backticks=add_backticks,
                literals=wrap_literals,
                needs_backticks=_word_needs_backticks_in_paragraph,
            )
            words = _tokenize_keeping_backticks(merged)
            out.extend(_wrap_words(words, width, "", ""))
            i = j

    return out


def _reflow_block(
    block_lines: list[str],
    width: int,
    *,
    add_backticks: bool,
    literals: list[str] | None = None,
) -> list[str]:
    r"""Reflow a delimited block, preserving a leading commit subject.

    When the first line of ``block_lines`` matches
    ``COMMIT_SUBJECT_PATTERN`` (``^\S+\(.*?\):\s`` -- e.g.
    ``feat(tools): add cert-aware uv launcher``), that line is emitted
    verbatim, skipping the backtick passes and the width wrap. The
    remaining lines go through ``reflow_lines`` as usual. When the
    first line does not match, the whole block is reflowed normally.

    Because the subject line is emitted verbatim, the wrap-list
    ``literals`` reach only the block body, never the commit subject.
    """
    if block_lines and COMMIT_SUBJECT_PATTERN.match(block_lines[0]):
        return [
            block_lines[0],
            *reflow_lines(
                block_lines[1:],
                width,
                add_backticks=add_backticks,
                literals=literals,
            ),
        ]
    return reflow_lines(
        block_lines, width, add_backticks=add_backticks, literals=literals,
    )


def process_text(  # noqa: PLR0913
    # Driver routes text through both fence delimiters plus the two
    # inline-backtick knobs (add_backticks, literals); six parameters is
    # the natural shape for this seam, so PLR0913 is suppressed here.
    text: str,
    width: int,
    open_delim: str | None,
    close_delim: str | None,
    *,
    add_backticks: bool = True,
    literals: list[str] | None = None,
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
        literals: Extra wrap-list string literals to backtick in block
            bodies. ``None`` (the default) means no wrap-list. Group
            lines and commit subjects are never touched.

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
            literals=literals,
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
                    _reflow_block(
                        block_lines,
                        width,
                        add_backticks=add_backticks,
                        literals=literals,
                    ),
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
            _reflow_block(
                block_lines,
                width,
                add_backticks=add_backticks,
                literals=literals,
            ),
        )

    return "\n".join(out_lines) + ("\n" if has_trailing_newline else "")


def _wrap_list_search_dirs(
    tool_dir: Path,
    start_dir: Path,
    project_root: Path,
    home: Path,
) -> list[Path]:
    """Return the ordered, de-duplicated dirs to scan for wrap-list files.

    The order is: the wrap tool's own folder, then the calling folder and
    each parent up to and including the project root, then the project
    root, then the user home folder. The walk also stops at the
    filesystem root, so a calling folder that is not under the project
    root still terminates. Duplicates are dropped while keeping the first
    occurrence, so a directory that plays several of these roles is
    scanned once.

    Args:
        tool_dir: The folder that holds this wrap tool.
        start_dir: The calling folder (already resolved).
        project_root: The resolved project root.
        home: The resolved user home folder.

    Returns:
        The de-duplicated directories to scan, in scan order.
    """
    candidates: list[Path] = [tool_dir]
    current = start_dir
    while True:
        candidates.append(current)
        parent = current.parent
        # Stop at the project root, or at the filesystem root when the
        # calling folder is not under the project root.
        if current in (project_root, parent):
            break
        current = parent
    candidates.append(project_root)
    candidates.append(home)

    ordered: list[Path] = []
    seen: set[Path] = set()
    for directory in candidates:
        if directory not in seen:
            seen.add(directory)
            ordered.append(directory)
    return ordered


def _load_wrap_list_literals(directories: list[Path]) -> list[str]:
    """Read every ``wrap-list.backtick`` found across ``directories``.

    Each file contributes one literal per non-blank line, with leading
    and trailing whitespace stripped. The literals from all files are
    concatenated in directory order. A directory without the file is
    skipped, and a file that cannot be read is skipped too, so one
    unreadable config never aborts the format.

    Args:
        directories: The folders to scan, in scan order.

    Returns:
        The concatenated list of literal strings.
    """
    literals: list[str] = []
    for directory in directories:
        path = directory / WRAP_LIST_FILE_NAME
        try:
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in content.splitlines():
            stripped = line.strip()
            if stripped:
                literals.append(stripped)
    return literals


def _collect_wrap_list_literals(start_dir: Path) -> list[str]:
    """Gather wrap-list literals visible from ``start_dir``.

    Scans the wrap tool folder, the calling folder and its parents up to
    the project root, the project root, and the user home folder. The
    home folder is taken from the ``HOME`` environment variable when it
    is set (matching ``%HOME%`` / ``$HOME``), otherwise from the OS home
    (``Path.home()``). When the project root cannot be located, the
    search falls back to the calling folder as the upper bound, so the
    tool folder, the calling folder and its parents, and the home folder
    are still scanned.

    Args:
        start_dir: The calling folder (typically the current directory).

    Returns:
        The concatenated wrap-list literals, possibly empty.
    """
    tool_dir = Path(__file__).resolve().parent
    home_env = os.environ.get("HOME")
    home = Path(home_env).resolve() if home_env else Path.home()
    resolved_start = start_dir.resolve()
    try:
        project_root = find_project_root(start_dir).resolve()
    except (FileNotFoundError, OSError, ValueError):
        project_root = resolved_start
    directories = _wrap_list_search_dirs(
        tool_dir, resolved_start, project_root, home,
    )
    return _load_wrap_list_literals(directories)


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


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (WrapCommitError, OSError) as err:
        _log_fatal(err)


# eof
