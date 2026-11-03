"""Exercise real expiry artifacts, caching only stable symlink-free path identities."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from tests.unit.tools.test_review_exchange_lifecycle import (
    test_review_exchange_lifecycle_tdd as lifecycle,
)
from tests.unit.tools.test_review_resume.prepared_phase import prepare_phase
from tools import review_exchange_cli as launcher
from tools import review_exchange_cli_resume as cli
from tools.llm_nature import LlmNature
from tools.review_exchange_models import Actor, ArtifactState, ReviewRole
from tools.review_exchange_ownership import OwnershipCapability
from tools.review_resume import can_resume_expired_leases
from tools.review_resume_identity import claim_selected
from tools.review_resume_wait import GlobalReviewerWait, GlobalWaitOutcome

if TYPE_CHECKING:
    from collections.abc import Callable
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
def expiry_harness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stable_review_inputs: Callable[[], None],
) -> PreparedRequest:
    """Publish real artifacts with a deterministic host and a shared short lease."""
    monkeypatch.delenv("CLAUDECODE", raising=False)
    monkeypatch.setenv("CODEX_THREAD_ID", "expiry-fixture")
    core, store, context, clock = lifecycle._harness(tmp_path)
    cli.ReviewArtifactConfiguration.load(tmp_path).prepare_home()
    monkeypatch.setattr(cli.ReviewArtifactMigration, "_default_ignore_checker", _ignore_fixture_paths)
    (store.paths.coordination.parent / "a.review-mode").write_text(
        f"wait_timeout_seconds={core.configuration.wait_timeout_seconds}\n", encoding="utf-8",
    )
    stable_review_inputs()
    monkeypatch.setattr(cli, "_wall_clock", clock.now)
    return core, store, context, clock


@pytest.fixture
def request_for_expiry(expiry_harness: PreparedRequest) -> PreparedRequest:
    """Declare the request prerequisite without replaying publication."""
    core, _store, context, clock = expiry_harness
    prepare_phase(core, context, clock, "request")
    return expiry_harness


@pytest.fixture
def answered_for_expiry(expiry_harness: PreparedRequest) -> PreparedRequest:
    """Prepare a real published answer before the measured persistent wait."""
    core, _store, context, clock = expiry_harness
    prepare_phase(core, context, clock, "answer")
    return expiry_harness


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
    # The request already exists: discovery must succeed before any notification
    # wait. Native observer delivery and shutdown have their own acceptance tests.
    notifications = MagicMock(spec=cli.WatchdogNotificationAdapter)
    notifications.wait.side_effect = AssertionError("Existing request must be found on the initial scan")

    def notification_factory(_directory: Path) -> MagicMock:
        """Bind notification IO separately from real artifact discovery."""
        return notifications

    monkeypatch.setattr(cli, "WatchdogNotificationAdapter", notification_factory)
    result = cli.execute_resume_operation(launcher._parser().parse_args(["wait-any-request"]), root)
    notifications.wait.assert_not_called()
    notifications.__exit__.assert_called_once()
    return result


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
    tmp_path: Path, expired_request: PreparedRequest,
) -> tuple[PreparedRequest, dict[str, Any], bytes]:
    """Discover and claim the prerequisite without replaying CLI startup checks."""
    _core, store, _context, clock = expired_request
    before = store.paths.request.read_bytes()
    # The startup case separately asserts the public wait command and observer
    # cleanup. This continuation needs the real discovered capability itself.
    discovery = cli._RequestDiscovery(tmp_path, wall_clock=clock.now)
    (candidate,) = discovery.rescan()
    assert candidate.state is ArtifactState.ABANDONED_REQUEST
    assert discovery.claim(candidate)
    payload = discovery.capability(candidate)
    return expired_request, payload, before


def test_discovered_expired_request_resumes_with_same_capability(
    discovered_expired_request: tuple[PreparedRequest, dict[str, Any], bytes],
) -> None:
    """A discovered capability survives identity completion and permits an actual answer."""
    prepared, payload, before = discovered_expired_request
    core, store, context, clock = prepared
    presented = OwnershipCapability(payload["ownership_generation"], payload["ownership_token"])
    core.present_ownership(presented)
    capability = claim_selected(core, ReviewRole.REVIEWER, LlmNature.CODEX,
                                round_number=1, occurrence=1, override=False)
    assert capability == presented
    assert store.paths.request.read_bytes() != before  # Missing-only reviewer nature backfill.
    core.present_ownership(capability)
    core.reclaim()
    core.publish_answer(lifecycle._answer(context, clock, 1), "Reviewer summary")
    assert core.classify().state is ArtifactState.ANSWER_PENDING


def test_expired_request_inspection_selects_review(
    tmp_path: Path, expired_request: PreparedRequest,
) -> None:
    """The public inspection boundary selects the same recoverable reviewer action."""
    _core, _store, context, _clock = expired_request
    common = ["--document", str(context.document_path), "--role", "reviewer", "--trusted-host-hint", "codex"]
    inspected, code = cli.execute_resume_operation(launcher._parser().parse_args(["resume-inspect", *common]), tmp_path)
    assert code == 0
    assert inspected["action"] == "review-request"


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
