"""Property coverage for deterministic review-status ordering."""

# pyright: reportPrivateUsage=false
# ruff: noqa: D103

from __future__ import annotations

from itertools import permutations

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.review_exchange_models import ExchangeIdentity, ReviewFamily
from tools.review_status import _sort_entries
from tools.review_status_models import DamagedCandidateStatus


@st.composite
def _damaged_entries(draw: st.DrawFn) -> tuple[DamagedCandidateStatus, ...]:
    suffixes = draw(
        st.lists(
            st.integers(min_value=0, max_value=999),
            min_size=1,
            max_size=7,
            unique=True,
        ),
    )
    return tuple(
        DamagedCandidateStatus(
            f"a.review-active.code.code.v0.11.0.topic_{suffix}.md",
            "generated damage",
            ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", f"topic_{suffix}"),
        )
        for suffix in suffixes
    )


@settings(max_examples=25)
@given(_damaged_entries(), st.data())
def test_sort_is_independent_of_enumeration_order(
    entries: tuple[DamagedCandidateStatus, ...],
    data: st.DataObject,
) -> None:
    shuffled = data.draw(st.permutations(entries))

    assert _sort_entries(shuffled) == _sort_entries(entries)


def test_sort_is_stable_for_equal_keys() -> None:
    first = DamagedCandidateStatus("a.review-active.bad-one.md", "first")
    second = DamagedCandidateStatus("a.review-active.bad-two.md", "second")

    for ordering in permutations((first, second)):
        assert set(_sort_entries(ordering)) == {first, second}
