"""Marked claim binding: strict durable model and ownership threading.

Step 4 of v0.15.0 resume-paused records a marked claim's non-secret evidence,
launch id, receiving pane, host, assignment binding, round and occurrence, in
the coordination record together with the ownership generation it was issued
with. The binding parses strictly, must equal the record's generation, rides
through every current-owner transition unchanged, and is cleared or replaced
by every newly issued claim. It never holds a token or its digest.
"""

# ruff: noqa: S105

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.tools.test_review_exchange_ownership.test_review_exchange_ownership_tdd import (
    _record,
)
from tools.review_exchange_models import Actor, ReviewExchangeError
from tools.review_exchange_models_coordination import (
    CoordinationRecord,
    MarkedClaimBinding,
    MarkedClaimEvidence,
)
from tools.review_exchange_ownership import OwnershipService
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

LAUNCH = "0123456789abcdef0123456789abcdef"
OTHER_LAUNCH = "fedcba9876543210fedcba9876543210"
PANE = "77e5f39c-0536-4cbb-a057-f4a1f5c715b0"
BINDING = "a" * 64
EVIDENCE = MarkedClaimEvidence(LAUNCH, PANE, "codex", BINDING, 1, 1)
OTHER = MarkedClaimEvidence(OTHER_LAUNCH, PANE, "codex", "c" * 64, 1, 1)
TOKENS = ("a" * 43, "b" * 43, "c" * 43)
SECOND = 2


def service() -> OwnershipService:
    """Return a service with deterministic tokens."""
    tokens = iter(TOKENS)
    return OwnershipService(token_factory=lambda: next(tokens))


def test_binding_round_trips_through_the_coordination_record(tmp_path: Path) -> None:
    """A recorded binding serializes under its own key and parses back equal."""
    claim = service().claim(_record(tmp_path), Actor.REQUESTOR, marked=EVIDENCE)
    data = claim.record.to_dict()
    assert data["marked_claim"] == {
        "launch_id": LAUNCH, "pane_id": PANE, "host": "codex", "assignment_binding": BINDING,
        "round": 1, "occurrence": 1, "issued_generation": 1,
    }
    assert CoordinationRecord.from_dict(data) == claim.record
    assert "ownership_token" not in str(data["marked_claim"])


def test_legacy_record_carries_no_binding(tmp_path: Path) -> None:
    """Records without the key parse with no binding and serialize without it."""
    record = _record(tmp_path)
    assert "marked_claim" not in record.to_dict()
    assert CoordinationRecord.from_dict(record.to_dict()).marked_claim is None


def test_binding_must_equal_the_ownership_generation(tmp_path: Path) -> None:
    """A binding issued for another generation cannot sit on the record."""
    claimed = service().claim(_record(tmp_path), Actor.REQUESTOR).record
    with pytest.raises(ReviewExchangeError, match="marked claim generation"):
        replace(claimed, marked_claim=EVIDENCE.issued(SECOND))


@pytest.mark.parametrize(
    "changes",
    [
        {"launch_id": LAUNCH.upper()}, {"launch_id": LAUNCH[:-1]}, {"pane_id": PANE[:-1]}, {"pane_id": PANE.upper()},
        {"host": ""}, {"host": "Codex"}, {"assignment_binding": BINDING[:-1]}, {"round_number": 0}, {"occurrence": 0},
    ],
    ids=["upper launch", "short launch", "short pane", "upper pane", "empty host", "upper host", "short binding", "zero round", "zero occurrence"],
)
def test_binding_refuses_malformed_evidence(changes: dict[str, Any]) -> None:
    """Every evidence field keeps its strict spelling."""
    with pytest.raises(ReviewExchangeError, match="marked claim"):
        replace(EVIDENCE, **changes)


def test_binding_refuses_a_zero_generation() -> None:
    """A binding belongs to an issued, positive generation."""
    with pytest.raises(ReviewExchangeError, match="marked claim"):
        EVIDENCE.issued(0)


def _mapping() -> dict[str, object]:
    """Return one valid serialized binding."""
    return EVIDENCE.issued(1).to_dict()


MUTATIONS: dict[str, Callable[[dict[str, object]], object]] = {
    "extra key": lambda data: data.update(extra=1),
    "missing key": lambda data: data.pop("round"),
    "string round": lambda data: data.update(round="1"),
    "boolean occurrence": lambda data: data.update(occurrence=True),
    "integer launch": lambda data: data.update(launch_id=7),
}


@pytest.mark.parametrize("name", list(MUTATIONS))
def test_binding_mapping_is_strict(name: str) -> None:
    """Unknown, missing and mistyped keys are refused."""
    data = _mapping()
    MUTATIONS[name](data)
    with pytest.raises(ReviewExchangeError):
        MarkedClaimBinding.from_dict(data)


def test_marked_claim_issues_a_generation_with_its_binding(tmp_path: Path) -> None:
    """The binding is recorded atomically with the generation it was issued with."""
    claim = service().claim(_record(tmp_path), Actor.REQUESTOR, marked=EVIDENCE)
    assert claim.newly_issued
    assert claim.record.marked_claim == EVIDENCE.issued(claim.capability.generation)


def test_current_owner_transitions_keep_the_binding(tmp_path: Path) -> None:
    """An idempotent claim and an ordinary record replacement retain the binding."""
    owner = service()
    first = owner.claim(_record(tmp_path), Actor.REQUESTOR, marked=EVIDENCE)
    again = owner.claim(first.record, Actor.REQUESTOR, presented=first.capability)
    assert (again.newly_issued, again.record.marked_claim) == (False, first.record.marked_claim)
    renewed = replace(first.record, lease_renewed_at="2026-09-04T09:05:00+02:00")
    assert renewed.marked_claim == first.record.marked_claim


@pytest.mark.parametrize(
    ("actor", "force", "marked", "expected"),
    [
        (Actor.REVIEWER, False, None, None),
        (Actor.REQUESTOR, True, None, None),
        (Actor.REQUESTOR, True, OTHER, OTHER),
    ],
    ids=["counterpart claim clears", "competing pickup clears", "new marked claim replaces"],
)
def test_newly_issued_claims_clear_or_replace_the_binding(
    tmp_path: Path, actor: Actor, force: bool, marked: MarkedClaimEvidence | None, expected: MarkedClaimEvidence | None,  # noqa: FBT001
) -> None:
    """A new generation never inherits an earlier marked claim's binding."""
    owner = service()
    first = owner.claim(_record(tmp_path), Actor.REQUESTOR, marked=EVIDENCE)
    second = owner.claim(first.record, actor, force=force, marked=marked)
    assert second.capability.generation == SECOND
    assert second.record.marked_claim == (None if expected is None else expected.issued(SECOND))


def test_marked_claim_by_the_current_owner_issues_a_new_generation(tmp_path: Path) -> None:
    """Presenting the current capability does not skip issuing a marked claim."""
    owner = service()
    first = owner.claim(_record(tmp_path), Actor.REQUESTOR)
    marked = owner.claim(first.record, Actor.REQUESTOR, presented=first.capability, marked=EVIDENCE)
    assert (marked.newly_issued, marked.record.marked_claim) == (True, EVIDENCE.issued(SECOND))


def test_store_persists_the_binding_with_its_generation(tmp_path: Path) -> None:
    """The exchange store forwards the evidence to one locked compare-and-swap claim."""
    record = _record(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, record.context))
    store.write_coordination(record)
    claim = store.claim_ownership(record, service(), Actor.REQUESTOR, force=True, marked=EVIDENCE)
    stored = store.read_coordination(required=True)
    assert stored == claim.record
    assert stored is not None
    assert stored.marked_claim == EVIDENCE.issued(claim.capability.generation)


# eof
