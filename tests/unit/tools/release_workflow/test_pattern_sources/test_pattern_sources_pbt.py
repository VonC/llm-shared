"""The CRLF-to-LF view and its offset map over generated line lists.

Step 3 of v0.14.0 version-sources: whatever the mix of LF and CRLF endings,
including stray carriage returns, the view equals the text with each CRLF
read as LF, and every span of the view maps back to the same characters of
the original: identical when the span holds no line feed, and equal after the
same CRLF-to-LF reading otherwise. Mapped offsets never split a CRLF. The line
list is drawn as one integer, the cheapest encoding, to stay inside the
lifecycle budget.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.release_workflow.sources import pattern

# One base-12 digit per line: a width of "a=1" (0 to 2), a stray carriage return, a CRLF or LF end.
_DIGIT = 12
_LINES = 6
_CODES = st.integers(min_value=0, max_value=_DIGIT**_LINES - 1)
_CUT = st.integers(min_value=0, max_value=40)


def _text(code: int) -> str:
    """Decode one integer into lines of `a=1` prefixes with mixed endings."""
    lines: list[str] = []
    for _ in range(_LINES):
        code, digit = divmod(code, _DIGIT)
        width, stray, crlf = digit // 4, digit // 2 % 2, digit % 2
        lines.append("a=1"[:width] + "\r" * stray + ("\r\n" if crlf else "\n"))
    return "".join(lines)


@settings(max_examples=25)
@given(code=_CODES, first_cut=_CUT, second_cut=_CUT)
def test_view_spans_map_back_to_the_same_characters(code: int, first_cut: int, second_cut: int) -> None:
    """Each view span maps to original offsets holding the same characters."""
    original = _text(code)
    view = pattern.lf_view(original)
    assert view.text == original.replace("\r\n", "\n")
    start, end = sorted(cut % (len(view.text) + 1) for cut in (first_cut, second_cut))
    first, last = view.original_offset(start), view.original_offset(end)
    captured = view.text[start:end]
    mapped = original[first:last]
    assert mapped.replace("\r\n", "\n") == captured
    if "\n" not in captured:
        assert mapped == captured
    for offset in (first, last):
        assert original[offset - 1:offset + 1] != "\r\n"


# eof
