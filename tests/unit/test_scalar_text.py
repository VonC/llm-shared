"""The integer-mapped text strategy keeps the exact default-text domain.

``tests.scalar_text`` replaces Hypothesis's Unicode category tables in property
tests. These deterministic checks pin its domain edges: the mapping is ordered,
skips only the declared characters and the surrogate block, and ends at the
last scalar value. Edge characters are written with ``chr`` so no invisible or
private-use character appears in the source.
"""

from __future__ import annotations

import pytest

from tests.scalar_text import (
    LAST_SCALAR,
    SURROGATE_FIRST,
    last_index,
    scalar_character,
    scalar_text,
)

_CR_LF = (0x0A, 0x0D)
_BEFORE_SURROGATES = chr(0xD7FF)
_AFTER_SURROGATES = chr(0xE000)


def test_unskipped_mapping_is_identity_below_the_surrogates_then_jumps() -> None:
    """Without exclusions, ranks equal code points until the surrogate block."""
    assert scalar_character(0) == chr(0)
    assert scalar_character(SURROGATE_FIRST - 1) == _BEFORE_SURROGATES
    assert scalar_character(SURROGATE_FIRST) == _AFTER_SURROGATES
    assert scalar_character(last_index()) == chr(LAST_SCALAR)


def test_declared_characters_are_skipped_in_order() -> None:
    """Excluding LF and CR shifts later ranks and still ends at U+10FFFF."""
    mapped = [scalar_character(index, _CR_LF) for index in (0, 9, 10, 11, 12)]
    assert mapped == [chr(0x00), chr(0x09), chr(0x0B), chr(0x0C), chr(0x0E)]
    assert scalar_character(SURROGATE_FIRST - 3, _CR_LF) == _BEFORE_SURROGATES
    assert scalar_character(SURROGATE_FIRST - 2, _CR_LF) == _AFTER_SURROGATES
    assert scalar_character(last_index(_CR_LF), _CR_LF) == chr(LAST_SCALAR)


def test_exclusions_above_the_surrogate_block_are_rejected() -> None:
    """Only exclusions the ordered skip loop can honor are accepted."""
    with pytest.raises(ValueError, match="surrogate block"):
        scalar_text(exclude=_AFTER_SURROGATES)


# eof
