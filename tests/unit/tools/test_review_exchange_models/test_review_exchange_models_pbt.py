"""Property coverage for v0.11.0 review-exchange model round trips.

Step 1: draw valid identity tuples and prove strict JSON data preserves their
complete keys without cross-family, type, version, or slug loss. Both properties
construct the same bounded ASCII slug language directly, avoiding regex
generation and the Unicode character table required by text strategies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.review_exchange_models import ExchangeIdentity, ReviewFamily

if TYPE_CHECKING:
    from hypothesis.strategies import SearchStrategy

_VERSIONS = st.tuples(
    st.integers(min_value=0, max_value=99),
    st.integers(min_value=0, max_value=99),
    st.integers(min_value=0, max_value=99),
).map(lambda parts: f"v{parts[0]}.{parts[1]}.{parts[2]}")
_SLUGS = st.tuples(
    st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    st.lists(st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789_-"), max_size=30).map("".join),
).map("".join)
_SPEC_TYPES = st.sampled_from(
    ("feature-request", "issue", "design-specification", "plan"),
)


@st.composite
def _identity(draw: st.DrawFn, slugs: SearchStrategy[str] = _SLUGS) -> ExchangeIdentity:
    """Draw one valid specification or code identity."""
    family = draw(st.sampled_from(tuple(ReviewFamily)))
    type_token = "code" if family is ReviewFamily.CODE else draw(_SPEC_TYPES)
    return ExchangeIdentity(family, type_token, draw(_VERSIONS), draw(slugs))


@pytest.mark.parametrize("_batch", range(8))
@settings(max_examples=5, deadline=None)
@given(_identity())
def test_identity_json_data_round_trip_is_exact(_batch: int, identity: ExchangeIdentity) -> None:
    """Every generated complete identity survives strict serialization."""
    restored = ExchangeIdentity.from_dict(identity.to_dict())

    assert restored == identity
    assert restored.key == identity.key


@pytest.mark.parametrize("_batch", range(2))
@settings(max_examples=5, deadline=None)
@given(_identity(), _identity())
def test_distinct_identity_keys_never_compare_equal(
    _batch: int,
    first: ExchangeIdentity,
    second: ExchangeIdentity,
) -> None:
    """Changing any identity dimension changes the canonical key."""
    if first != second:
        assert first.key != second.key


# eof
