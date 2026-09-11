"""Property coverage for v0.11.0 review-exchange model round trips.

Step 1: draw valid identity tuples and prove strict JSON data preserves their
complete keys without cross-family, type, version, or slug loss.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.review_exchange_models import ExchangeIdentity, ReviewFamily

_VERSIONS = st.tuples(
    st.integers(min_value=0, max_value=99),
    st.integers(min_value=0, max_value=99),
    st.integers(min_value=0, max_value=99),
).map(lambda parts: f"v{parts[0]}.{parts[1]}.{parts[2]}")
_SLUGS = st.from_regex(r"[a-z0-9][a-z0-9_-]{0,30}", fullmatch=True)
_SPEC_TYPES = st.sampled_from(
    ("feature-request", "issue", "design-specification", "plan"),
)


@st.composite
def _identity(draw: st.DrawFn) -> ExchangeIdentity:
    """Draw one valid specification or code identity."""
    family = draw(st.sampled_from(tuple(ReviewFamily)))
    type_token = "code" if family is ReviewFamily.CODE else draw(_SPEC_TYPES)
    return ExchangeIdentity(family, type_token, draw(_VERSIONS), draw(_SLUGS))


@settings(max_examples=40, deadline=None)
@given(_identity())
def test_identity_json_data_round_trip_is_exact(identity: ExchangeIdentity) -> None:
    """Every generated complete identity survives strict serialization."""
    restored = ExchangeIdentity.from_dict(identity.to_dict())

    assert restored == identity
    assert restored.key == identity.key


@settings(max_examples=10, deadline=None)
@given(_identity(), _identity())
def test_distinct_identity_keys_never_compare_equal(
    first: ExchangeIdentity,
    second: ExchangeIdentity,
) -> None:
    """Changing any identity dimension changes the canonical key."""
    if first != second:
        assert first.key != second.key


# eof
