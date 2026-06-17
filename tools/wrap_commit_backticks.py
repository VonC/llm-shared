r"""Inline-backtick word rules and passes of the wrap-commit tool.

Holds the code-like word predicates (dash-prefixed tokens, ``=`` and
``_`` mixed-content tokens, non-trailing dots, non-leading open parens,
CamelCase, the paragraph-only path-separator rule), the wrap-exception
whitelist, the outer-punctuation splitter, the wrap-list literal pass,
the adjacent-span merge, the subject-wrap backtick stripper, and the
backtick-aware tokenizer used by the width wrap. See
``tools.wrap_commit`` for the full tool description.

Fix: split for the repo line budget -- the word rules and backtick
passes moved here from ``tools.wrap_commit``, which stays the script
entry point and import hub.

Fix: add ``strip_subject_wrap_backticks`` -- once the backtick passes
have run, a line that opens with a backticked ``\`type(scope)\`:`` (a
conventional-commit subject the word pass wrapped via the open-paren
rule) has those two backticks removed so the opener reads bare.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

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

# A conventional-commit subject whose ``type(scope)`` was auto-wrapped
# by the word pass opens a line as ``\`type(scope)\`:`` -- a backtick, a
# type (no ``(``), a ``(scope)`` group, a closing backtick, then the
# ``:`` separator. ``strip_subject_wrap_backticks`` matches that opener
# and removes the two backticks so the line reads ``type(scope):`` bare,
# like a verbatim first-line subject. The capture group keeps the
# ``type(scope)`` text for the bare rewrite.
SUBJECT_WRAP_BACKTICKS_PATTERN = re.compile(r"^`([^(]+\([^)]+\))`:")


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


def tokenize_keeping_backticks(text: str) -> list[str]:
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


def word_needs_backticks_in_paragraph(word: str) -> bool:
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
    paragraph caller passes ``word_needs_backticks_in_paragraph`` to add
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


def apply_inline_backticks(
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
            ``word_needs_backticks_in_paragraph`` (regular rules plus the
            path-separator rule); bullets keep the default regular rules.

    Returns:
        The segment after the wrap-list, word, and merge passes.
    """
    if not add_backticks:
        return text
    text = _add_backticks_to_literals(text, literals)
    text = _add_backticks_to_words(text, needs_backticks)
    return _merge_adjacent_backtick_spans(text)


def strip_subject_wrap_backticks(text: str) -> str:
    r"""Strip the wrap backticks from a ``\`type(scope)\`:`` line opener.

    The word pass wraps a conventional-commit subject token such as
    ``feat(tools):`` via the open-paren rule, producing
    ``\`feat(tools)\`:`` -- the balanced parens stay inside the span and
    the trailing ``:`` sits just outside it. The first line of a block is
    kept verbatim, but any other line (a second subject in the body, or
    the whole file under ``--no-delimiters``) can end up opening with
    such a backticked ``type(scope)``. This pass matches that opener with
    ``SUBJECT_WRAP_BACKTICKS_PATTERN`` and drops the opening backtick and
    the backtick before the ``:``, leaving ``type(scope):`` bare and the
    rest of the line untouched. The ``^`` anchor keeps the strip to a
    line that starts with the backtick, so bullet lines (which open with
    ``- ``) and indented lines are never matched. A line that does not
    open with the pattern is returned unchanged.

    Args:
        text: One already-wrapped output line to clean up.

    Returns:
        The line with the two subject-wrap backticks removed, or the
        original line when the opener does not match.
    """
    return SUBJECT_WRAP_BACKTICKS_PATTERN.sub(r"\1:", text)


# eof
