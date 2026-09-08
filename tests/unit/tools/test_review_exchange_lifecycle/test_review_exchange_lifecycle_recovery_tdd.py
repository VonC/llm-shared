"""Timeout, reclaim, ownership pickup, and recovery coverage for the core.

Step 3 adds displaced-session fencing while this split continues to reuse the
deterministic lifecycle harness from the publication-transition sibling.
Convergence setup is prepared before measured pickup and fencing assertions.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools import review_exchange_core as core_module
from tools.review_exchange_core import ReviewExchangeCore, WaitOutcome, WaitResult
from tools.review_exchange_models import (
    Actor,
    ArchiveKind,
    ArtifactState,
    CoordinationStatus,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewDisposition,
    ReviewExchangeError,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_observer import ExchangeObservation
from tools.review_exchange_ownership import OwnershipRejectedError

from . import test_review_exchange_lifecycle_tdd as lifecycle

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_models import ReviewContext
    from tools.review_exchange_store import ReviewExchangeStore


def _detached_core(
    store: ReviewExchangeStore,
    context: ReviewContext,
    clock: lifecycle.FakeTime,
) -> ReviewExchangeCore:
    """Build another session over the same exact exchange evidence."""
    return ReviewExchangeCore(
        store,
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        lifecycle.ReviewConfiguration(enabled=True, wait_timeout_seconds=60),
        wall_clock=clock.now,
        monotonic_clock=clock.monotonic_now,
        sleeper=clock.sleep,
    )


def test_wait_timeout_escalates_once_and_preserves_state(tmp_path: Path) -> None:
    """A monotonic deadline records one timeout escalation without a heartbeat."""
    core, store, _, _ = lifecycle._harness(tmp_path)
    core.start()

    result = core.wait_for_exact(
        ArtifactState.REQUEST_PENDING,
        timeout_seconds=2,
        poll_interval=1,
        progress_interval=1,
    )
    again = core.escalate("wait timed out while request was absent")

    assert result.outcome is WaitOutcome.TIMED_OUT
    assert result.observation.state is ArtifactState.ESCALATED
    assert again.status is CoordinationStatus.ESCALATED
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 1


def test_wait_detects_abandonment_and_attributes_expected_actor(tmp_path: Path) -> None:
    """An expired active lease escalates with the expected actor in evidence."""
    core, store, context, _ = lifecycle._harness(tmp_path)
    expired = CoordinationRecord(
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        CoordinationStatus.ACTIVE,
        Actor.REQUESTOR,
        Actor.REVIEWER,
        1,
        "2026-08-04T12:00:00+00:00",
    )
    store.initialize_transcript(context)
    store.write_coordination(expired)

    result = core.wait_for_exact(
        ArtifactState.REQUEST_PENDING,
        timeout_seconds=5,
        poll_interval=1,
    )

    assert result.outcome is WaitOutcome.ABANDONED
    assert result.observation.record is not None
    assert result.observation.record.escalation_reason is not None
    assert "reviewer" in result.observation.record.escalation_reason


@pytest.fixture
def reclaimed_request_and_answer_journey(tmp_path: Path) -> None:
    """Run both abandoned-artifact reclaim paths outside the measured call."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    request_content = store.paths.request.read_text(encoding="utf-8")
    transcript_before = store.paths.transcript.read_text(encoding="utf-8")
    clock.sleep(61)
    assert core.classify().state is ArtifactState.ABANDONED_REQUEST

    reclaimed = core.reclaim()

    assert reclaimed.lease_renewed_at == lifecycle._timestamp(clock)
    assert reclaimed.status is CoordinationStatus.ACTIVE
    assert reclaimed.expected_next_actor is Actor.REVIEWER
    assert core.classify().state is ArtifactState.REQUEST_PENDING
    assert store.paths.request.read_text(encoding="utf-8") == request_content
    assert store.paths.transcript.read_text(encoding="utf-8") == transcript_before

    core.publish_answer(
        lifecycle._answer(context, clock, 1),
        "Reviewer report after reclaim.",
    )
    clock.sleep(61)
    assert core.classify().state is ArtifactState.ABANDONED_ANSWER
    core.reclaim()
    assert core.classify().state is ArtifactState.ANSWER_PENDING


def test_reclaim_renews_abandoned_request_and_answer_in_place(
    reclaimed_request_and_answer_journey: None,
) -> None:
    """A returning expected actor restores pending rounds by lease renewal."""
    assert reclaimed_request_and_answer_journey is None


@pytest.fixture
def reclaimed_mid_round_journey(
    tmp_path: Path,
) -> None:
    """Run repeated mid-round reclaim outside the measured assertion call."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    core.publish_answer(lifecycle._answer(context, clock, 1), "Reviewer report.")
    core.consume_answer(reviewed_work_changed=True)
    clock.sleep(61)
    assert core.classify().state is ArtifactState.ABANDONED_MID_ROUND

    first = core.reclaim()
    second = core.reclaim()

    assert core.classify().state is ArtifactState.ROUND_IN_PROGRESS
    assert first.round_number == 1
    assert second.round_number == 1
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 0


def test_reclaim_restores_mid_round_and_stays_idempotent_on_live_rounds(
    reclaimed_mid_round_journey: None,
) -> None:
    """Mid-round work can resume and live rounds tolerate a repeated reclaim."""
    assert reclaimed_mid_round_journey is None


def test_direct_pickup_displaces_live_session_before_its_next_mutation(
    tmp_path: Path,
) -> None:
    """A fresh-lease pickup advances generation and fences the old secret."""
    first, store, context, clock = lifecycle._harness(tmp_path)
    started = first.start()
    first_capability = first.ownership_capability
    assert first_capability is not None

    second = _detached_core(store, context, clock)
    pickup = second.pickup_ownership(Actor.REQUESTOR)

    assert pickup.record.ownership_generation == started.ownership_generation + 1
    assert pickup.capability == second.ownership_capability
    before = store.paths.transcript.read_bytes()
    with pytest.raises(OwnershipRejectedError) as raised:
        first.escalate("the displaced session must not append this")
    assert raised.value.failure.code == "ownership-superseded"
    assert store.paths.transcript.read_bytes() == before


def test_pickup_rejects_human_and_requires_coordination(tmp_path: Path) -> None:
    """Direct LLM pickup cannot claim a human or an absent exchange."""
    core, _, _, _ = lifecycle._harness(tmp_path)
    with pytest.raises(ReviewExchangeError, match="cannot claim human"):
        core.pickup_ownership(Actor.HUMAN)
    with pytest.raises(ReviewExchangeError, match="requires coordination"):
        core.pickup_ownership(Actor.REQUESTOR)


def test_wait_claim_revalidates_state_and_record(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A wake cannot claim after its observed state or coordination disappears."""
    core, _, _, _ = lifecycle._harness(tmp_path)
    found = ExchangeObservation(
        ArtifactState.REQUEST_PENDING,
        None,
        None,
        None,
        "found",
    )

    def found_wait(*_args: object, **_kwargs: object) -> WaitResult:
        return WaitResult(WaitOutcome.FOUND, found)

    monkeypatch.setattr(core_module, "wait_for_exact", found_wait)
    monkeypatch.setattr(
        core,
        "classify",
        lambda: ExchangeObservation(ArtifactState.IDLE, None, None, None, "changed"),
    )
    with pytest.raises(ReviewExchangeError, match="changed before ownership claim"):
        core.wait_for_exact(ArtifactState.REQUEST_PENDING)

    monkeypatch.setattr(core, "classify", lambda: found)
    with pytest.raises(ReviewExchangeError, match="requires coordination"):
        core.wait_for_exact(ArtifactState.REQUEST_PENDING)


@pytest.fixture
def convergence_sessions(tmp_path: Path) -> tuple[ReviewExchangeCore, ReviewExchangeCore]:
    """Reach the real convergence gate before measuring pickup and displaced-session fencing."""
    first, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._reach_gate(first, context, clock)
    return first, _detached_core(store, context, clock)


def test_convergence_pickup_fences_old_session_before_human_transition(
    convergence_sessions: tuple[ReviewExchangeCore, ReviewExchangeCore],
) -> None:
    """A requestor can pick up the gate and the displaced session cannot confirm."""
    first, second = convergence_sessions

    second.pickup_ownership(Actor.REQUESTOR)

    with pytest.raises(OwnershipRejectedError) as raised:
        first.confirm("Commit")
    assert raised.value.failure.code == "ownership-superseded"
    assert second.confirm("Commit").owning_action_authorized is True
    assert second.complete() is True


def test_new_core_without_session_secret_cannot_mutate_claimed_exchange(
    tmp_path: Path,
) -> None:
    """Reading durable generation and digest cannot recover mutation authority."""
    first, store, context, clock = lifecycle._harness(tmp_path)
    first.start()
    detached = _detached_core(store, context, clock)

    with pytest.raises(OwnershipRejectedError) as raised:
        detached.escalate("missing session capability")

    assert raised.value.failure.code == "ownership-missing"


@pytest.fixture
def rejected_reclaim_states_journey(
    tmp_path: Path,
) -> None:
    """Reclaim never bypasses idle, convergence-gate, or escalated stops."""
    idle_core, _, _, _ = lifecycle._harness(tmp_path / "idle")
    with pytest.raises(ReviewExchangeError, match="durable coordination"):
        idle_core.reclaim()

    gate_core, _, gate_context, gate_clock = lifecycle._harness(tmp_path / "gate")
    lifecycle._reach_gate(gate_core, gate_context, gate_clock)
    gate_clock.sleep(61)
    with pytest.raises(ReviewExchangeError, match="reclaim requires"):
        gate_core.reclaim()

    core, _, context, clock = lifecycle._harness(tmp_path / "escalated")
    lifecycle._start_and_request(core, context, clock)
    clock.sleep(61)
    core.escalate("abandonment recorded before any reclaim")
    with pytest.raises(ReviewExchangeError, match="reclaim requires"):
        core.reclaim()


def test_reclaim_rejects_missing_coordination_gate_and_escalated_states(
    rejected_reclaim_states_journey: None,
) -> None:
    """All non-reclaimable states remain covered by the prepared journey."""
    assert rejected_reclaim_states_journey is None


@pytest.fixture
def escalated_request_journey(
    tmp_path: Path,
) -> tuple[
    ReviewExchangeCore,
    ReviewExchangeStore,
    ReviewContext,
    lifecycle.FakeTime,
    str,
]:
    """Prepare an escalated request outside the measured assertion phase."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    request_content = store.paths.request.read_text(encoding="utf-8")
    clock.sleep(61)
    core.escalate("exchange was abandoned while waiting for reviewer")
    return core, store, context, clock, request_content


def test_forced_reclaim_resumes_an_escalated_request_round_in_place(
    escalated_request_journey: tuple[
        ReviewExchangeCore,
        ReviewExchangeStore,
        ReviewContext,
        lifecycle.FakeTime,
        str,
    ],
) -> None:
    """An authorized manual resume keeps the round, evidence, and ownership."""
    core, store, context, clock, request_content = escalated_request_journey

    resumed = core.force_reclaim("The human resumes round 1 as a manual exchange.")

    assert (
        resumed.status,
        resumed.round_number,
        resumed.escalation_reason,
        resumed.expected_next_actor,
    ) == (CoordinationStatus.ACTIVE, 1, None, Actor.REVIEWER)
    assert core.classify().state is ArtifactState.REQUEST_PENDING
    assert store.paths.request.read_text(encoding="utf-8") == request_content
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: human-reclaim") == 1
    assert "review-entry-id: human-reclaim-round-1" in transcript

    core.publish_answer(lifecycle._answer(context, clock, 1), "Answer after resume.")
    assert core.classify().state is ArtifactState.ANSWER_PENDING


@pytest.fixture
def escalated_answer_journey(
    tmp_path: Path,
) -> ReviewExchangeCore:
    """Prepare an escalated answer outside the measured assertion phase."""
    core, _, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    core.publish_answer(lifecycle._answer(context, clock, 1), "Reviewer report.")
    core.escalate("stopped while the answer awaited assessment")
    return core


def test_forced_reclaim_returns_a_pending_answer_to_the_requestor(
    escalated_answer_journey: ReviewExchangeCore,
) -> None:
    """The resumed actor follows the intact artifact shape, not the escalation."""
    core = escalated_answer_journey

    resumed = core.force_reclaim("The human resumes the pending answer.")

    assert resumed.expected_next_actor is Actor.REQUESTOR
    assert core.classify().state is ArtifactState.ANSWER_PENDING


def test_forced_reclaim_returns_mid_round_work_to_the_reviewer(tmp_path: Path) -> None:
    """A stopped round with no counterpart artifact resumes as reviewer-owned."""
    core, store, _, _ = lifecycle._harness(tmp_path)
    core.start()
    core.escalate("stopped between two rounds")

    resumed = core.force_reclaim("The human resumes the mid-round work.")

    assert resumed.expected_next_actor is Actor.REVIEWER
    assert core.classify().state is ArtifactState.ROUND_IN_PROGRESS
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert "## Round 1 by human - Step 3 - escalation" in transcript
    assert "## Round 1 by human - Step 3 - human-reclaim" in transcript


@pytest.fixture
def repeated_human_transition_journey(
    tmp_path: Path,
) -> None:
    """Run two stop-and-resume cycles outside the measured assertion call."""
    core, store, _, _ = lifecycle._harness(tmp_path)
    core.start()
    core.escalate("stopped between two rounds")
    core.force_reclaim("The human resumes the mid-round work.")
    core.escalate("stopped again after the manual resume")
    core.force_reclaim("The human resumes the mid-round work once more.")

    transcript = store.paths.transcript.read_text(encoding="utf-8")
    headings = [line for line in transcript.splitlines() if line.startswith("## ")]
    identities = [line for line in transcript.splitlines() if "review-entry-id:" in line]

    assert len(headings) == len(set(headings))
    assert len(identities) == len(set(identities))


def test_repeated_human_transitions_keep_every_heading_and_identity_unique(
    repeated_human_transition_journey: None,
) -> None:
    """A second stop-and-resume cycle in one round never repeats a heading."""
    assert repeated_human_transition_journey is None


@pytest.fixture
def rejected_forced_reclaim_journey(
    tmp_path: Path,
) -> None:
    """Reject invalid forced reclaims outside the measured assertion call."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    with pytest.raises(ReviewExchangeError, match="escalated exchange"):
        core.force_reclaim("No escalation is recorded yet.")

    core.escalate("stopped for the human")
    with pytest.raises(ReviewExchangeError, match="non-empty"):
        core.force_reclaim("   ")

    escalated = store.read_coordination(required=True)
    assert escalated is not None
    store.write_coordination(
        replace(
            escalated,
            incomplete_transition=IncompleteTransitionKind.ESCALATION,
            transcript_entry_id="escalation-round-1",
            transcript_offset=0,
        ),
    )
    with pytest.raises(ReviewExchangeError, match="pending transition"):
        core.force_reclaim("A different repair is still pending.")

    store.write_coordination(escalated)
    store.paths.answer.parent.mkdir(parents=True, exist_ok=True)
    store.paths.answer.write_text("orphan answer\n", encoding="utf-8")
    with pytest.raises(ReviewExchangeError, match="one intact escalated round"):
        core.force_reclaim("Request and answer are both present.")


def test_forced_reclaim_rejects_unauthorized_and_unusable_stops(
    rejected_forced_reclaim_journey: None,
) -> None:
    """Summary, escalation, marker, and artifact shape all fail closed."""
    assert rejected_forced_reclaim_journey is None


def test_forced_completion_closes_only_an_abandoned_mid_round(tmp_path: Path) -> None:
    """One explicit human decision retires an expired artifact-free round."""
    core, store, _, clock = lifecycle._harness(tmp_path)
    core.start()
    clock.sleep(61)

    removed = core.force_complete("The human confirms this round is concluded.")

    assert removed is True
    assert core.classify().state is ArtifactState.IDLE
    assert not store.paths.coordination.exists()
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: human-completion") == 1
    assert "review-entry-id: human-completion-round-1" in transcript


def test_forced_completion_repairs_cleanup_without_changing_the_decision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A cleanup retry reuses the durable summary and never duplicates its entry."""
    core, store, _, clock = lifecycle._harness(tmp_path)
    core.start()
    clock.sleep(61)
    original_remove = store.remove_exact
    failed = False

    def fail_coordination_once(path: Path) -> bool:
        nonlocal failed
        if path == store.paths.coordination and not failed:
            failed = True
            message = "injected forced completion cleanup failure"
            raise ReviewExchangeError(message)
        return original_remove(path)

    monkeypatch.setattr(store, "remove_exact", fail_coordination_once)
    summary = "The human confirms this round is concluded."
    with pytest.raises(ReviewExchangeError, match="completion cleanup"):
        core.force_complete(summary)

    marked = store.read_coordination(required=True)
    assert marked is not None
    assert marked.incomplete_transition is IncompleteTransitionKind.HUMAN_COMPLETION
    with pytest.raises(ReviewExchangeError, match="differs from durable decision"):
        core.force_complete("A different decision.")

    assert core.force_complete(summary) is True
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: human-completion-round-1") == 1


def test_forced_completion_rejects_live_empty_and_foreign_repair_states(
    tmp_path: Path,
) -> None:
    """The override cannot replace normal completion or another repair."""
    core, store, _, clock = lifecycle._harness(tmp_path)
    with pytest.raises(ReviewExchangeError, match="coordination"):
        core.force_complete("There is no exchange to close.")

    core.start()
    with pytest.raises(ReviewExchangeError, match="abandoned mid-round"):
        core.force_complete("The live round must continue normally.")

    clock.sleep(61)
    with pytest.raises(ReviewExchangeError, match="non-empty"):
        core.force_complete("   ")

    record = store.read_coordination(required=True)
    assert record is not None
    store.write_coordination(
        replace(
            record,
            incomplete_transition=IncompleteTransitionKind.ESCALATION,
            transcript_entry_id="escalation-round-1",
            transcript_offset=0,
        ),
    )
    with pytest.raises(ReviewExchangeError, match="pending transition"):
        core.force_complete("Another repair still owns this exchange.")


def test_invalid_transition_and_confirmation_labels_fail_without_mutation(
    tmp_path: Path,
) -> None:
    """Wrong actors, states, and labels cannot advance the exchange."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    core.start()
    with pytest.raises(ReviewExchangeError, match="request pending"):
        core.publish_answer(lifecycle._answer(context, clock, 1), "Too early.")
    with pytest.raises(ReviewExchangeError, match="answer pending"):
        core.consume_answer(reviewed_work_changed=True)
    with pytest.raises(ReviewExchangeError, match="completed answer assessment"):
        core.continue_round()

    core.publish_request(lifecycle._request(context, clock, 1), "Valid request.")
    core.publish_answer(
        lifecycle._answer(
            context,
            clock,
            1,
            ReviewDisposition.CONVERGENCE_RECOMMENDED,
        ),
        "Converged.",
    )
    with pytest.raises(ReviewExchangeError, match="unregistered confirmation label"):
        core.confirm("Reviewer says yes")
    assert store.paths.answer.is_file()


def test_escalation_append_failure_repairs_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An interrupted escalation append remains marker-owned and idempotent."""
    core, store, _, _ = lifecycle._harness(tmp_path)
    core.start()
    original_append = store._append_bytes
    failed = False

    def fail_once(path: Path, content: bytes) -> None:
        nonlocal failed
        if not failed:
            failed = True
            message = "injected escalation append failure"
            raise OSError(message)
        original_append(path, content)

    monkeypatch.setattr(store, "_append_bytes", fail_once)
    with pytest.raises(ReviewExchangeError, match="transcript append failed"):
        core.escalate("Manual review required")

    marked = store.read_coordination(required=True)
    assert marked is not None
    assert marked.incomplete_transition is IncompleteTransitionKind.ESCALATION
    record = core.escalate("Manual review required")

    assert record.status is CoordinationStatus.ESCALATED
    assert record.incomplete_transition is None
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 1


@pytest.fixture
def archived_resolution_journey(tmp_path: Path) -> None:
    """Archive a resolved escalation outside the measured assertion call."""
    core, _, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    core.escalate("Archive the stopped request")

    resolution = core.resolve_escalation("Restart cleanly.", archive=True)

    names = {path.name for path in resolution.archived_paths}
    assert len(names) == lifecycle._EXPECTED_ARCHIVE_COUNT
    assert any(f".{ArchiveKind.REQUEST.value}.md" in name for name in names)
    assert any(f".{ArchiveKind.COORDINATION.value}.md" in name for name in names)


def test_resolution_archives_only_supported_exact_evidence(
    archived_resolution_journey: None,
) -> None:
    """Resolution returns identity-scoped archives for each live evidence kind."""
    assert archived_resolution_journey is None


# eof
