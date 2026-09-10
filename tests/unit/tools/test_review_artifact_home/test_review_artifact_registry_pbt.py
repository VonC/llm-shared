"""Property coverage for registry round trips with a bounded example budget."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.review_artifact_registry import (
    RegisteredArtifactKind,
    ReviewArtifactRegistry,
)
from tools.review_exchange_models import ExchangeIdentity, ReviewFamily


@given(
    family=st.sampled_from(tuple(ReviewFamily)),
    version=st.tuples(
        st.integers(min_value=0, max_value=30),
        st.integers(min_value=0, max_value=30),
        st.integers(min_value=0, max_value=30),
    ).map(lambda value: f"v{value[0]}.{value[1]}.{value[2]}"),
    slug=st.from_regex(r"[a-z0-9][a-z0-9_-]{0,30}", fullmatch=True),
    kind=st.sampled_from(
        (
            RegisteredArtifactKind.REQUEST,
            RegisteredArtifactKind.ANSWER,
            RegisteredArtifactKind.COORDINATION,
            RegisteredArtifactKind.TOMBSTONE,
            RegisteredArtifactKind.TRANSITION_LOCK,
        ),
    ),
)
@settings(max_examples=40)
def test_registered_identity_names_round_trip(
    family: ReviewFamily,
    version: str,
    slug: str,
    kind: RegisteredArtifactKind,
) -> None:
    """Every rendered identity-bearing runtime name parses without collision."""
    type_token = "code" if family is ReviewFamily.CODE else "plan"
    identity = ExchangeIdentity(family, type_token, version, slug)
    registry = ReviewArtifactRegistry()

    parsed = registry.parse_name(registry.name_for(kind, identity))

    assert parsed is not None
    assert parsed.kind is kind
    assert parsed.identity == identity


# eof
