"""Exercise lease expiry during one persistent wait and the selected CLI continuation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_lifecycle import (
    test_review_exchange_lifecycle_tdd as lifecycle,
)
from tools import review_exchange_cli_resume as cli
from tools.review_exchange_cli_parser import parser
from tools.review_exchange_models import Actor, ArtifactState
from tools.review_exchange_ownership import OwnershipCapability
from tools.review_resume import can_resume_expired_leases
from tools.review_resume_wait import GlobalReviewerWait, GlobalWaitOutcome

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

_NEXT_ROUND = 2

PreparedRequest = tuple[
    lifecycle.ReviewExchangeCore, lifecycle.ReviewExchangeStore,
    lifecycle.ReviewContext, lifecycle.FakeTime,
]


def _ignore_fixture_paths(*_paths: object) -> bool:
    """Keep repository ignore probing outside real-artifact fixture scenarios."""
    return True


@pytest.fixture
def request_for_expiry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> PreparedRequest:
    """Publish real artifacts with a deterministic host and a shared short lease."""
    monkeypatch.delenv("CLAUDECODE", raising=False)
    monkeypatch.setenv("CODEX_THREAD_ID", "expiry-fixture")
    core, store, context, clock = lifecycle._harness(tmp_path)
    cli.ReviewArtifactConfiguration.load(tmp_path).prepare_home()
    monkeypatch.setattr(cli.ReviewArtifactMigration, "_default_ignore_checker", _ignore_fixture_paths)
    (store.paths.coordination.parent / "a.review-mode").write_text(
        f"wait_timeout_seconds={core.configuration.wait_timeout_seconds}\n", encoding="utf-8",
    )
    lifecycle._start_and_request(core, context, clock)
    monkeypatch.setattr(cli, "_wall_clock", clock.now)
    return core, store, context, clock


@pytest.fixture
def answered_for_expiry(request_for_expiry: PreparedRequest) -> PreparedRequest:
    """Prepare a real published answer before the measured persistent wait."""
    core, _store, context, clock = request_for_expiry
    core.reclaim()
    core.publish_answer(lifecycle._answer(context, clock, 1), "Reviewer summary")
    return request_for_expiry


def test_running_wait_survives_answer_expiry_and_finds_next_round(
    tmp_path: Path, answered_for_expiry: PreparedRequest,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """One wait crosses lease expiry without touching the answer, then claims round two."""
    core, store, context, clock = answered_for_expiry
    discovery = cli._RequestDiscovery(tmp_path, wall_clock=clock.now)
    before = (store.paths.coordination.read_bytes(), store.paths.answer.read_bytes())
    intervals: list[ArtifactState] = []

    def advance_requestor(_seconds: float) -> bool:
        """Age the lease, then let the requestor publish its replacement on the next wake."""
        intervals.append(core.classify().state)
        if len(intervals) == 1:
            clock.sleep(core.configuration.wait_timeout_seconds + 1)
            assert core.classify().state is ArtifactState.ABANDONED_ANSWER
        else:
            assert intervals[-1] is ArtifactState.ABANDONED_ANSWER
            assert (store.paths.coordination.read_bytes(), store.paths.answer.read_bytes()) == before
            core.pickup_ownership(Actor.REQUESTOR)
            core.reclaim()
            core.consume_answer(reviewed_work_changed=True)
            core.continue_round()
            core.publish_request(lifecycle._request(context, clock, 2), "Replacement request")
        return False

    result = GlobalReviewerWait(
        rescan_candidates=discovery.rescan, claim_candidate=discovery.claim,
        wait_for_notification=advance_requestor, fallback_poll=lambda: None,
        poll_interval_seconds=1,
    ).wait(max_quiet_intervals=2)

    assert intervals == [ArtifactState.ANSWER_PENDING, ArtifactState.ABANDONED_ANSWER]
    assert result.outcome is GlobalWaitOutcome.FOUND
    assert isinstance(result.candidate, cli.ExchangeStatus)
    assert result.candidate.round_number == _NEXT_ROUND
    assert discovery.capability(result.candidate)["ownership_generation"]
    assert capsys.readouterr() == ("", "")


@pytest.fixture
def expired_request(request_for_expiry: PreparedRequest) -> PreparedRequest:
    """Age an unclaimed published request without modifying its durable evidence."""
    core, _store, _context, clock = request_for_expiry
    clock.sleep(core.configuration.wait_timeout_seconds + 1)
    assert core.classify().state is ArtifactState.ABANDONED_REQUEST
    return request_for_expiry


def _discover_expired_request(
    root: Path, prepared: PreparedRequest, monkeypatch: pytest.MonkeyPatch,
) -> tuple[dict[str, Any], int]:
    """Enter the real CLI wait with the fixture clock and its actual discovery service."""
    _core, _store, _context, clock = prepared
    discovery = cli._RequestDiscovery(root, wall_clock=clock.now)

    def current_discovery(_root: Path) -> cli._RequestDiscovery:
        """Reuse the deterministic discovery clock in the public CLI path."""
        return discovery

    monkeypatch.setattr(cli, "_RequestDiscovery", current_discovery)
    return cli.execute_resume_operation(parser().parse_args(["wait-any-request"]), root)


def test_expired_request_passes_wait_startup(
    tmp_path: Path, expired_request: PreparedRequest, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An expired request passes startup and is found and claimed by the running CLI wait."""
    payload, code = _discover_expired_request(tmp_path, expired_request, monkeypatch)
    assert code == 0
    assert payload["outcome"] == "found"
    assert payload["candidates"][0]["state"] == "abandoned-request"


@pytest.fixture
def discovered_expired_request(
    tmp_path: Path, expired_request: PreparedRequest, monkeypatch: pytest.MonkeyPatch,
) -> tuple[PreparedRequest, dict[str, Any], bytes]:
    """Prepare the already-tested discovery result before measuring selected continuation."""
    _core, store, _context, _clock = expired_request
    before = store.paths.request.read_bytes()
    payload, code = _discover_expired_request(tmp_path, expired_request, monkeypatch)
    assert code == 0
    return expired_request, payload, before


def test_discovered_expired_request_resumes_with_same_capability(
    tmp_path: Path, discovered_expired_request: tuple[PreparedRequest, dict[str, Any], bytes],
) -> None:
    """A discovered capability survives identity completion and permits an actual answer."""
    prepared, payload, before = discovered_expired_request
    core, store, context, clock = prepared
    capability = _complete_reviewer_identity(tmp_path, context, payload)
    assert store.paths.request.read_bytes() != before  # Missing-only reviewer nature backfill.
    core.present_ownership(capability)
    core.reclaim()
    core.publish_answer(lifecycle._answer(context, clock, 1), "Reviewer summary")
    assert core.classify().state is ArtifactState.ANSWER_PENDING


def _complete_reviewer_identity(
    root: Path, context: lifecycle.ReviewContext, payload: dict[str, Any],
) -> OwnershipCapability:
    """Inspect the expired request and reuse exactly the capability returned by discovery."""
    common = ["--document", str(context.document_path), "--role", "reviewer", "--trusted-host-hint", "codex"]
    inspected, code = cli.execute_resume_operation(parser().parse_args(["resume-inspect", *common]), root)
    assert code == 0
    assert inspected["action"] == "review-request"
    claimed, code = cli.execute_resume_operation(parser().parse_args([
        "claim", *common, "--round", "1", "--occurrence", "1",
        "--ownership-generation", str(payload["ownership_generation"]),
        "--ownership-token", payload["ownership_token"],
    ]), root)
    assert code == 0
    assert claimed["ownership_generation"] == payload["ownership_generation"]
    assert claimed["ownership_token"] == payload["ownership_token"]
    return OwnershipCapability(claimed["ownership_generation"], claimed["ownership_token"])


@pytest.mark.parametrize("state", [*ArtifactState, None])
def test_lease_exception_never_masks_nonrecoverable_evidence(state: ArtifactState | None) -> None:
    """A damaged or repair-required neighbor still blocks a home containing an expired lease."""
    allowed = {
        ArtifactState.IDLE, ArtifactState.ROUND_IN_PROGRESS,
        ArtifactState.REQUEST_PENDING, ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS,
        ArtifactState.ANSWER_PENDING, ArtifactState.CONVERGENCE_GATE,
        ArtifactState.OWNING_ACTION_PENDING, ArtifactState.ABANDONED_MID_ROUND,
        ArtifactState.ABANDONED_REQUEST, ArtifactState.ABANDONED_ANSWER,
    }
    assert can_resume_expired_leases((ArtifactState.ABANDONED_ANSWER, state)) is (state in allowed)


# eof
