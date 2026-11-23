"""Generated marker and result-line properties.

Step 4 of v0.15.0 resume-paused: every well-formed marker renders and parses
back to itself, and a one-character change of a rendered marker either is
refused or names a different marker, never the same consent. Result lines
round-trip over their whole grammar.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.resume_paused_marker import Marker, ResultLine
from tools.resume_paused_models import ArtifactError, SessionRole

EXAMPLES = 25
HEX = "0123456789abcdef"
OUTCOME_TAIL = "abcdefghijklmnopqrstuvwxyz0123456789-"
SURROGATES = 0x800
FIRST_SURROGATE = 0xD800
LAST_SCALAR = 0x10FFFF


def scalar(index: int) -> str:
    """Map an integer onto one Unicode scalar value, skipping the surrogate block."""
    return chr(index if index < FIRST_SURROGATE else index + SURROGATES)


scalars = st.integers(min_value=0, max_value=LAST_SCALAR - SURROGATES).map(scalar)


def hex_text(size: int) -> st.SearchStrategy[str]:
    """Draw lowercase hexadecimal text of one exact length."""
    return st.text(HEX, min_size=size, max_size=size)


def uuids() -> st.SearchStrategy[str]:
    """Draw canonical lowercase UUID spellings."""
    return st.tuples(hex_text(8), hex_text(4), hex_text(4), hex_text(4), hex_text(12)).map("-".join)


markers = st.builds(Marker, hex_text(32), uuids(), st.sampled_from(list(SessionRole)), hex_text(64))


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(marker=markers)
def test_markers_round_trip(marker: Marker) -> None:
    """Rendering and parsing are inverse on the whole grammar."""
    assert Marker.parse(marker.render()) == marker


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(marker=markers, position=st.integers(min_value=0, max_value=200), replacement=scalars)
def test_one_character_change_never_names_the_same_marker(marker: Marker, position: int, replacement: str) -> None:
    """A changed character is refused or yields another marker."""
    text = marker.render()
    index = position % len(text)
    changed = text[:index] + replacement + text[index + 1 :]
    if changed == text:
        return
    try:
        parsed = Marker.parse(changed)
    except ArtifactError:
        return
    assert parsed != marker


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(
    launch=hex_text(32),
    outcome=st.builds(str.__add__, st.sampled_from("abcdefghijklmnopqrstuvwxyz"), st.text(OUTCOME_TAIL, max_size=31)),
    generation=st.none() | st.integers(min_value=1, max_value=9_999_999_999),
)
def test_result_lines_round_trip(launch: str, outcome: str, generation: int | None) -> None:
    """Every result line in the grammar renders and parses back."""
    line = ResultLine(launch, outcome, generation)
    assert ResultLine.parse(line.render()) == line


@pytest.mark.parametrize(
    ("index", "expected"),
    [(0, chr(0)), (0xD7FF, chr(0xD7FF)), (0xD800, chr(0xE000)), (LAST_SCALAR - SURROGATES, chr(LAST_SCALAR))],
    ids=["first", "below surrogates", "after surrogates", "last"],
)
def test_scalar_mapping_covers_every_scalar_value(index: int, expected: str) -> None:
    """The integer mapping reaches both ends of the scalar range around the surrogates."""
    assert scalar(index) == expected


@pytest.mark.parametrize("role", list(SessionRole))
def test_every_role_token_is_a_marker_role(role: SessionRole) -> None:
    """Each saved session role can be bound by a marker."""
    marker = Marker("0" * 32, "00000000-0000-0000-0000-000000000000", role, "0" * 64)
    assert Marker.parse(marker.render()).role is role


# eof
