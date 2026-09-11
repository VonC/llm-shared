"""Properties for monotonic Step 3 ownership generation fencing."""

from __future__ import annotations

from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.review_exchange_models import (
    Actor,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewContext,
    ReviewFamily,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_ownership import OwnershipCapability, OwnershipService

_PROPERTY_TOKEN = "p" * 43


def _record() -> CoordinationRecord:
    """Build one active record before its first ownership claim."""
    document = (
        Path(__file__).resolve().parents[4]
        / "docs/v0.11.0/plan.v0.11.0.review-resume-command.md"
    )
    context = ReviewContext(
        ExchangeIdentity(
            ReviewFamily.CODE,
            "code",
            "v0.11.0",
            "review-resume-command",
        ),
        document,
        None,
        "3",
    )
    return CoordinationRecord(
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        CoordinationStatus.ACTIVE,
        Actor.REQUESTOR,
        Actor.REVIEWER,
        1,
        "2026-09-04T09:00:00+02:00",
    )


@given(st.lists(st.sampled_from((Actor.REQUESTOR, Actor.REVIEWER)), min_size=1, max_size=40))
@settings(max_examples=40)
def test_every_forced_pickup_strictly_advances_and_rejects_prior_generations(
    actors: list[Actor],
) -> None:
    """No capability from any earlier generation validates after a pickup."""
    service = OwnershipService(token_factory=lambda: _PROPERTY_TOKEN)
    record = _record()
    capabilities: list[OwnershipCapability] = []

    for expected_generation, actor in enumerate(actors, start=1):
        claim = service.claim(record, actor, force=True)
        record = claim.record
        capabilities.append(claim.capability)
        assert claim.capability.generation == expected_generation
        assert service.failure_for(record, claim.capability) is None
    for stale in capabilities[:-1]:
        failure = service.failure_for(record, stale)
        assert failure is not None
        assert failure.code == "ownership-superseded"


# eof
