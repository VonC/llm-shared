"""Properties of version tokens and span composition over generated inputs.

Step 2 of v0.14.0 version-sources: a token prints and parses back to itself
for any integer triple, with or without the suffix, and its order equals the
order of the triples; composing random disjoint spans at once equals applying
the same replacements one by one from right to left.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.release_workflow.sources.model import Span, VersionToken, compose

_NUMBERS = st.integers(min_value=0, max_value=10_000)
_TRIPLES = st.tuples(_NUMBERS, _NUMBERS, _NUMBERS)


@settings(max_examples=25)
@given(triple=_TRIPLES, snapshot=st.booleans())
def test_token_round_trip(triple: tuple[int, int, int], *, snapshot: bool) -> None:
    """`str` and `parse` are inverse for every well-formed token."""
    token = VersionToken(*triple, snapshot=snapshot)
    assert VersionToken.parse(str(token)) == token
    assert token.key == triple


@settings(max_examples=25)
@given(first=_TRIPLES, second=_TRIPLES, snapshots=st.tuples(st.booleans(), st.booleans()))
def test_order_equals_triple_order(first: tuple[int, int, int], second: tuple[int, int, int], snapshots: tuple[bool, bool]) -> None:
    """Comparing keys is comparing the integer triples, whatever the suffixes."""
    left, right = VersionToken(*first, snapshot=snapshots[0]), VersionToken(*second, snapshot=snapshots[1])
    assert (left.key < right.key) == (first < second)
    assert (left.key == right.key) == (first == second)


@st.composite
def _disjoint_edits(draw: st.DrawFn) -> tuple[bytes, list[tuple[Span, bytes]]]:
    """Draw short content and sorted, disjoint spans with replacements."""
    content = draw(st.binary(max_size=24))
    cuts = sorted(set(draw(st.lists(st.integers(min_value=0, max_value=len(content)), max_size=8))))
    spans = [Span(cuts[index], cuts[index + 1]) for index in range(0, len(cuts) - 1, 2)]
    replacements = draw(st.lists(st.binary(max_size=4), min_size=len(spans), max_size=len(spans)))
    edits = list(zip(spans, replacements, strict=True))
    return content, draw(st.permutations(edits))


@settings(max_examples=25)
@given(case=_disjoint_edits())
def test_composition_equals_sequential_right_to_left_replacement(case: tuple[bytes, list[tuple[Span, bytes]]]) -> None:
    """One composition from the original equals replacing spans from the end backwards."""
    content, edits = case
    expected = content
    for span, replacement in sorted(edits, key=lambda edit: edit[0].start, reverse=True):
        expected = expected[:span.start] + replacement + expected[span.end:]
    assert compose(content, edits) == expected


# eof
