"""Pending request corrections retain round identity and reject reviewer races."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_lifecycle.test_review_exchange_lifecycle_tdd import (
    _answer,
    _harness,
    _request,
)
from tools.review_exchange_models import Actor, ArtifactState, ReviewExchangeError
from tools.review_exchange_ownership import OwnershipRejectedError

if TYPE_CHECKING:
    from pathlib import Path


def test_amendment_updates_request_and_transcript_without_advancing_round(tmp_path: Path) -> None:
    """Correct the final first request and keep one current round-one entry."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    core.publish_request(_request(context, clock, 1), "Incorrect consolidated design.")
    amended = _request(context, clock, 1) + "\nReview the restored questions Q01-Q07.\n"

    record = core.publish_request(amended, "Questions Q01-Q07 retained.", amend_pending=True)

    assert record.round_number == 1
    assert core.classify().state is ArtifactState.REQUEST_PENDING
    assert "restored questions Q01-Q07" in store.read_artifact(store.paths.request)
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert "Incorrect consolidated design." not in transcript
    assert "Questions Q01-Q07 retained." in transcript
    assert transcript.count("review-entry-id: request-step-3-round-1 -->") == 1
    assert "exchange 2" not in transcript


def test_amendment_preserves_prior_rounds(tmp_path: Path) -> None:
    """Replace only the final entry when an earlier reviewed round exists."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    core.publish_request(_request(context, clock, 1), "Prior request.")
    core.publish_answer(_answer(context, clock, 1), "Prior answer.")
    core.consume_answer(reviewed_work_changed=True)
    core.continue_round()
    core.publish_request(_request(context, clock, 2), "Stale current request.")
    before = store.paths.transcript.read_bytes()
    offset = store.current_entry_offset("request-step-3-round-2")

    core.publish_request(_request(context, clock, 2), "Corrected current request.", amend_pending=True)

    assert store.paths.transcript.read_bytes()[:offset] == before[:offset]
    assert "Stale current request." not in store.paths.transcript.read_text(encoding="utf-8")


def test_amendment_rejects_reviewer_pickup_without_mutating_evidence(tmp_path: Path) -> None:
    """A stale requestor cannot change the work already claimed by a reviewer."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    original_capability = core.ownership_capability
    core.publish_request(_request(context, clock, 1), "Original request.")
    core.pickup_ownership(Actor.REVIEWER)
    paths = (store.paths.request, store.paths.coordination, store.paths.transcript)
    before = [path.read_bytes() for path in paths]
    core.present_ownership(original_capability)

    with pytest.raises(OwnershipRejectedError):
        core.publish_request(_request(context, clock, 1), "Changed.", amend_pending=True)
    assert [path.read_bytes() for path in paths] == before


def test_reviewer_cannot_amend_with_its_own_capability(tmp_path: Path) -> None:
    """The mutation is reserved to the requestor even with a valid capability."""
    core, _, context, clock = _harness(tmp_path)
    core.start()
    core.publish_request(_request(context, clock, 1), "Original request.")
    core.pickup_ownership(Actor.REVIEWER)

    with pytest.raises(ReviewExchangeError, match="requestor ownership"):
        core.publish_request(_request(context, clock, 1), "Changed.", amend_pending=True)


@pytest.mark.parametrize("published", [False, True])
def test_invalid_amendment_leaves_artifacts_unchanged(tmp_path: Path, *, published: bool) -> None:
    """Reject a missing pending request or wrong replacement round before any write."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    if published:
        core.publish_request(_request(context, clock, 1), "Original request.")
    paths = (store.paths.request, store.paths.coordination, store.paths.transcript)
    before = [path.read_bytes() if path.exists() else None for path in paths]

    with pytest.raises(ReviewExchangeError):
        core.publish_request(_request(context, clock, 2), "Changed.", amend_pending=True)
    assert [path.read_bytes() if path.exists() else None for path in paths] == before


def test_interrupted_amendment_repairs_one_matching_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A crash after request publication resumes without duplicating the transcript."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    core.publish_request(_request(context, clock, 1), "Original request.")
    amended = _request(context, clock, 1) + "\nRestored questions.\n"

    def interrupted(*_args: object, **_kwargs: object) -> None:
        message = "simulated transcript interruption"
        raise OSError(message)

    with monkeypatch.context() as patch:
        patch.setattr(store, "append_transcript_once", interrupted)
        with pytest.raises(OSError, match="simulated"):
            core.publish_request(amended, "Corrected request.", amend_pending=True)

    assert core.classify().state is ArtifactState.TRANSCRIPT_REPAIR_PENDING
    core.publish_request(amended, "Corrected request.", amend_pending=True)
    assert core.classify().state is ArtifactState.REQUEST_PENDING
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Corrected request.") == 1
    assert "Original request." not in transcript


# eof
