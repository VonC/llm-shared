"""Real-artifact resume tests with independent stores and locked concurrent claims.

Conflict request setup precedes the measured rejection and Override transitions.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_lifecycle import (
    test_review_exchange_lifecycle_tdd as lifecycle,
)
from tools.llm_nature import LlmNature
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_models_envelope import parse_envelope_markdown
from tools.review_exchange_ownership import OwnershipRejectedError
from tools.review_resume_identity import claim_discovered_request, claim_selected
from tools.review_role_nature import RoleNatureSnapshot

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_exchange_store import ReviewExchangeStore


def test_pickup_backfills_and_fences_a_live_session(tmp_path: Path) -> None:
    """A bare resume claim needs no lease expiry and preserves counterpart nature."""
    old, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(old, context, clock)
    record = store.read_coordination(required=True)
    assert record is not None
    store.write_coordination(replace(record, role_natures=RoleNatureSnapshot(LlmNature.CODEX, None)))
    resumed = ReviewExchangeCore(store, context, old.policy, old.configuration, wall_clock=clock.now)
    capability = claim_selected(resumed, ReviewRole.REVIEWER, LlmNature.CLAUDE, round_number=1, occurrence=1, override=False)
    updated = store.read_coordination(required=True)
    assert updated is not None
    assert updated.owner is Actor.REVIEWER
    assert updated.ownership_generation > record.ownership_generation
    assert updated.role_natures == RoleNatureSnapshot(LlmNature.CODEX, LlmNature.CLAUDE)
    envelope, _ = parse_envelope_markdown(store.paths.request.read_text(encoding="utf-8"))
    assert envelope.role_natures.reviewer is LlmNature.CLAUDE
    assert capability.token not in store.paths.coordination.read_text(encoding="utf-8")
    with pytest.raises(OwnershipRejectedError):
        old.publish_request(lifecycle._request(context, clock, 1), "Displaced writer")
    resumed.present_ownership(capability)
    same = claim_selected(resumed, ReviewRole.REVIEWER, LlmNature.CLAUDE, round_number=1, occurrence=1, override=False)
    assert same == capability

@pytest.mark.parametrize(("round_number", "occurrence"), [(2, 1), (1, 2)])
def test_stale_exact_selection_cannot_change_artifacts(tmp_path: Path, round_number: int, occurrence: int) -> None:
    """Changed round or occurrence is rejected under lock before backfill or claim."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    before = store.paths.coordination.read_bytes()
    with pytest.raises(ReviewExchangeError, match="selection changed"):
        claim_selected(core, ReviewRole.REVIEWER, LlmNature.CLAUDE,
                       round_number=round_number, occurrence=occurrence, override=False)
    assert store.paths.coordination.read_bytes() == before
    assert claim_discovered_request(core, round_number, occurrence) is None


def test_locked_state_recheck_blocks_interrupted_continuation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A state change after inspection stops the pickup before identity mutation."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    observation = replace(core.classify(), state=ArtifactState.ESCALATED)
    monkeypatch.setattr(core, "classify", lambda: observation)
    with pytest.raises(ReviewExchangeError, match="no longer permits"):
        claim_selected(core, ReviewRole.REVIEWER, LlmNature.CLAUDE, round_number=1, occurrence=1, override=False)
    assert store.read_coordination(required=True) is not None


@pytest.fixture
def conflicting_role_request(tmp_path: Path) -> tuple[ReviewExchangeCore, ReviewExchangeStore, CoordinationRecord]:
    """Publish real conflicting evidence before measuring its guarded pickup."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    record = store.read_coordination(required=True)
    assert record is not None
    store.write_coordination(replace(record, role_natures=RoleNatureSnapshot(None, LlmNature.CLAUDE)))
    return core, store, record


def test_conflicting_role_needs_override_and_preserves_recorded_evidence(
    conflicting_role_request: tuple[ReviewExchangeCore, ReviewExchangeStore, CoordinationRecord],
) -> None:
    """Override fills only gaps and cannot rewrite known contrary role evidence."""
    core, store, record = conflicting_role_request
    with pytest.raises(ReviewExchangeError, match="conflicts require Override"):
        claim_selected(core, ReviewRole.REVIEWER, LlmNature.CODEX, round_number=1, occurrence=1, override=False)
    capability = claim_selected(core, ReviewRole.REVIEWER, LlmNature.CODEX, round_number=1, occurrence=1, override=True)
    updated = store.read_coordination(required=True)
    assert updated is not None
    assert updated.role_natures.reviewer is LlmNature.CLAUDE
    assert capability.generation > record.ownership_generation

@pytest.mark.timeout(3)
def test_concurrent_waiters_have_exactly_one_atomic_winner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Independent stores use real transition locks and return exactly one typed loser."""
    first, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(first, context, clock)
    second_store = lifecycle.ReviewExchangeStore(store.paths)
    # Override the shared unit fixture only here: concurrency must exercise the lock.
    monkeypatch.setattr(store, "transition_lock", store.ownership_store.transition_lock)
    monkeypatch.setattr(second_store, "transition_lock", second_store.ownership_store.transition_lock)
    second = ReviewExchangeCore(second_store, context, first.policy, first.configuration, wall_clock=clock.now)
    barrier = Barrier(2)

    def claim(core: ReviewExchangeCore) -> str:
        """Align both independent callers before the real transition lock."""
        barrier.wait(timeout=1)
        try:
            capability = claim_discovered_request(core, 1, 1)
        except OwnershipRejectedError as error:
            return error.failure.code
        assert capability is not None
        return "found"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = tuple(pool.map(claim, (first, second)))
    assert results.count("found") == 1
    assert results.count("already-claimed") == 1
    assert store.paths.request.exists()
