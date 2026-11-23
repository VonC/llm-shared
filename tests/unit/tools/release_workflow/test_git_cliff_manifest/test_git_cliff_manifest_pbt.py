"""Generated pin texts are admitted or refused consistently with a synthetic table.

Step 1 of v0.14.0 git-cliff-provisioning: any integer triple formats to a
version admitted exactly when the table holds it, and inserting a `v`, a sign,
a letter or whitespace anywhere in such a text refuses it with the form message.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.release_workflow.git_cliff.manifest import (
    PLATFORM_TRIPLE,
    AdmittedPin,
    PinError,
    parse_pin,
)


def _pin(version: str, *, default: bool) -> AdmittedPin:
    """Build a synthetic pin whose asset and member names derive from its version."""
    return AdmittedPin(
        version=version, default=default, triple=PLATFORM_TRIPLE, asset=f"git-cliff-{version}-{PLATFORM_TRIPLE}.zip",
        size=1, sha256="f" * 64, member=f"git-cliff-{version}/git-cliff.exe", evidence="bundle",
    )


_TABLE = (_pin("2.14.2", default=True), _pin("2.7.0", default=False))
_TABLED = frozenset(pin.version for pin in _TABLE)
_NUMBERS = st.integers(min_value=0, max_value=10_000)
_TRIPLES = st.one_of(st.sampled_from([(2, 14, 2), (2, 7, 0)]), st.tuples(_NUMBERS, _NUMBERS, _NUMBERS))
# Non-ASCII members by code point: no-break space and ideographic space.
_INSERTED = st.sampled_from(["v", "V", "+", "-", "a", "z", "Q", " ", "\t", "\n", *map(chr, (0x00A0, 0x3000))])


def _text(triple: tuple[int, int, int]) -> str:
    """Format an integer triple the way a pin is written."""
    major, minor, patch = triple
    return f"{major}.{minor}.{patch}"


@settings(max_examples=25)
@given(triple=_TRIPLES)
def test_formatted_triples_are_admitted_exactly_when_tabled(triple: tuple[int, int, int]) -> None:
    """A well-formed version is returned when tabled and refused with the listing otherwise."""
    text = _text(triple)
    if text in _TABLED:
        assert parse_pin(text, pins=_TABLE) == text
    else:
        with pytest.raises(PinError, match=r"^not a tested git-cliff pin; tested: 2\.14\.2, 2\.7\.0$"):
            parse_pin(text, pins=_TABLE)


@settings(max_examples=25)
@given(triple=_TRIPLES, character=_INSERTED, position=st.integers(min_value=0, max_value=32))
def test_text_with_a_v_sign_letter_or_whitespace_is_refused(triple: tuple[int, int, int], character: str, position: int) -> None:
    """One foreign character anywhere, admitted version or not, fails the form check."""
    text = _text(triple)
    index = position % (len(text) + 1)
    with pytest.raises(PinError, match=r"^expected an exact git-cliff version X\.Y\.Z"):
        parse_pin(text[:index] + character + text[index:], pins=_TABLE)


# eof
