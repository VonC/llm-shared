"""Generated budget texts: every in-range integer round-trips, the rest is refused.

Step 1 of v0.14.0 git-cliff-provisioning: each integer from 300 through 3600
gives exactly that download budget and a wait 60 s longer; any integer outside
the range, and any text holding one non-digit character, is refused.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.release_workflow.git_cliff.budget import (
    DOWNLOAD_BUDGET_VARIABLE,
    BudgetSettingError,
    resolve_budget,
)

_IN_RANGE = st.integers(min_value=300, max_value=3600)
_OUTSIDE = st.one_of(st.integers(max_value=299), st.integers(min_value=3601))
# Non-ASCII members by code point: no-break space, Arabic-Indic three,
# superscript three, fullwidth five and Devanagari nine.
_NON_DIGITS = st.sampled_from(["-", "+", ".", ",", "_", "e", "s", " ", "\t", *map(chr, (0x00A0, 0x0663, 0x00B3, 0xFF15, 0x096F))])


@settings(max_examples=25)
@given(seconds=_IN_RANGE)
def test_every_integer_in_range_round_trips(seconds: int) -> None:
    """The decimal text of an in-range integer gives that D and W = D + 60."""
    policy = resolve_budget({DOWNLOAD_BUDGET_VARIABLE: str(seconds)})
    assert (policy.download, policy.wait) == (seconds, seconds + 60)


@settings(max_examples=25)
@given(seconds=_OUTSIDE)
def test_every_integer_outside_the_range_is_refused(seconds: int) -> None:
    """Below 300, above 3600 and negative values are refused, never clamped."""
    with pytest.raises(BudgetSettingError, match="from 300 through 3600"):
        resolve_budget({DOWNLOAD_BUDGET_VARIABLE: str(seconds)})


@settings(max_examples=25)
@given(seconds=_IN_RANGE, character=_NON_DIGITS, position=st.integers(min_value=0, max_value=8))
def test_text_with_a_non_digit_character_is_refused(seconds: int, character: str, position: int) -> None:
    """One sign, separator, letter, space or non-ASCII digit anywhere refuses the value."""
    text = str(seconds)
    index = position % (len(text) + 1)
    with pytest.raises(BudgetSettingError, match=DOWNLOAD_BUDGET_VARIABLE):
        resolve_budget({DOWNLOAD_BUDGET_VARIABLE: text[:index] + character + text[index:]})


# eof
