"""Property coverage for registry round trips with a bounded example budget."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.review_artifact_registry import (
    RegisteredArtifactKind,
    ReviewArtifactRegistry,
)
from tools.review_exchange_models import ExchangeIdentity, ReviewFamily


def _slug_tail(data: bytes) -> str:
    """Retain the full allowed alphabet without string-constant discovery."""
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789_-"
    return "".join(alphabet[value % len(alphabet)] for value in data)


@pytest.mark.parametrize("_batch", range(20))
@given(
    family=st.sampled_from(tuple(ReviewFamily)),
    version=st.tuples(
        st.integers(min_value=0, max_value=30),
        st.integers(min_value=0, max_value=30),
        st.integers(min_value=0, max_value=30),
    ).map(lambda value: f"v{value[0]}.{value[1]}.{value[2]}"),
    slug=st.tuples(st.sampled_from(tuple("abcdefghijklmnopqrstuvwxyz0123456789")),
                   st.binary(max_size=30).map(_slug_tail)).map("".join),
    kind=st.sampled_from(
        (
            RegisteredArtifactKind.REQUEST,
            RegisteredArtifactKind.ANSWER,
            RegisteredArtifactKind.COORDINATION,
            RegisteredArtifactKind.TOMBSTONE,
            RegisteredArtifactKind.TRANSITION_LOCK,
            RegisteredArtifactKind.SCOPE_CAPTURE,
        ),
    ),
)
@settings(max_examples=2)
def test_registered_identity_names_round_trip(
    _batch: int,
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
