r"""Width wrap, paragraph/bullet reflow, and block drivers of wrap-commit.

Holds the list-item recognizer, the greedy word wrapper, the
continuation-line collector, the per-block reflow (including the
verbatim commit-subject rule), and the ``process_text`` driver that
routes a whole file through the delimited blocks. See
``tools.wrap_commit`` for the full tool description.

Fix: split for the repo line budget -- the reflow and driver logic
moved here from ``tools.wrap_commit``, which stays the script entry
point and import hub; the inline-backtick passes live in
``tools.wrap_commit_backticks``.
"""

from __future__ import annotations

import re

from tools.wrap_commit_backticks import (
    apply_inline_backticks as _apply_inline_backticks,
)
from tools.wrap_commit_backticks import (
    strip_subject_wrap_backticks as _strip_subject_wrap_backticks,
)
from tools.wrap_commit_backticks import (
    tokenize_keeping_backticks as _tokenize_keeping_backticks,
)
from tools.wrap_commit_backticks import (
    word_needs_backticks_in_paragraph as _word_needs_backticks_in_paragraph,
)

# A list item starts at any indent, with a single ``-`` followed by a
# literal space. The captured group is the indent, which drives the
# continuation indent during wrapping.
LIST_ITEM_PATTERN = re.compile(r"^(\s*)- ")

# Conventional-commit subject: ``<type>(<scope>): <rest>``. When this
# matches the first line of a delimited block, that line is emitted
# verbatim (no backtick pass, no width wrap).
COMMIT_SUBJECT_PATTERN = re.compile(r"^\S+\(.*?\):\s")


def _is_list_item(line: str) -> re.Match[str] | None:
    """Return the regex match if ``line`` opens a list item, else None.

    Args:
        line: The single text line to inspect.

    Returns:
        The ``re.Match`` whose first group is the captured indent, or
        ``None`` when the line is not a list item.
    """
    return LIST_ITEM_PATTERN.match(line)


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


def _strip_subject_wraps(lines: list[str], *, add_backticks: bool) -> list[str]:
    r"""Undo a backticked ``\`type(scope)\`:`` opener on each output line.

    Runs ``strip_subject_wrap_backticks`` over every reflowed line so a
    line that opens with a backticked conventional-commit subject reads
    ``type(scope):`` bare. When ``add_backticks`` is False the backtick
    passes never ran, so there is nothing to strip and the lines are
    returned unchanged.

    Args:
        lines: The reflowed output lines, without terminating newlines.
        add_backticks: When False, skip the strip and return ``lines``.

    Returns:
        The lines with any subject-wrap backticks removed.
    """
    if not add_backticks:
        return lines
    return [_strip_subject_wrap_backticks(line) for line in lines]


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

    The width wrap tokenises through ``tokenize_keeping_backticks``,
    so any inline backtick span (whether pre-existing or just added) is
    treated as one indivisible token -- a span like ``\`xx yyy zzz\```
    will never be split across lines.

    After the width wrap, when ``add_backticks`` is True, each output
    line is passed through ``strip_subject_wrap_backticks``: a line that
    opens with a backticked ``\`type(scope)\`:`` (a conventional-commit
    subject the word pass wrapped via the open-paren rule) has those two
    backticks removed, so the opener reads ``type(scope):`` bare. Bullet
    lines open with ``- `` and indented lines with whitespace, so this
    line-anchored strip only touches a paragraph that starts at column 0.

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

    # Once the backtick passes and the width wrap are done, undo any
    # subject wrap: a line that now opens with a backticked
    # ``\`type(scope)\`:`` (a conventional-commit subject the word pass
    # wrapped via the open-paren rule) reads better bare, matching the
    # verbatim first-line subject.
    return _strip_subject_wraps(out, add_backticks=add_backticks)


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


# eof
