"""Exercise resume on real artifacts with explicit host identity and prepared phases."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_lifecycle import (
    test_review_exchange_lifecycle_tdd as lifecycle,
)
from tools import review_exchange_cli as launcher
from tools import review_exchange_cli_resume as cli
from tools.llm_nature import LlmNature
from tools.review_exchange_cli_parser import parser
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ReviewDisposition,
    ReviewRole,
)
from tools.review_exchange_ownership import OwnershipCapability, OwnershipRejectedError
from tools.review_resume import (
    ResumeAction,
    ResumeContext,
    ResumeDecisionOutcome,
    ResumeExchange,
    ReviewResumeService,
)
from tools.review_resume_identity import claim_discovered_request, claim_selected
from tools.review_resume_wait import GlobalReviewerWait, GlobalWaitOutcome

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(("state", "role", "action"), [
    (ArtifactState.REQUEST_PENDING, ReviewRole.REVIEWER, ResumeAction.REVIEW_REQUEST),
    (ArtifactState.REQUEST_PENDING, ReviewRole.REQUESTOR, ResumeAction.WAIT_EXACT_ANSWER),
    (ArtifactState.ANSWER_PENDING, ReviewRole.REQUESTOR, ResumeAction.WAIT_EXACT_ANSWER),
    (ArtifactState.CONVERGENCE_GATE, ReviewRole.REQUESTOR, ResumeAction.CONTINUE_REQUESTOR),
    (ArtifactState.OWNING_ACTION_PENDING, ReviewRole.REQUESTOR, ResumeAction.CONTINUE_REQUESTOR),
    (ArtifactState.ANSWER_PENDING, ReviewRole.REVIEWER, ResumeAction.WAIT_ANY_REQUEST),
])
def test_role_resolution_acquires_before_returning_continuation(
    state: ArtifactState, role: ReviewRole, action: ResumeAction,
) -> None:
    """Every selected live role receives exactly one automatic in-session capability."""
    claimed: list[ReviewRole] = []
    capability = OwnershipCapability(1, "s" * 32)

    def acquire(selected: ReviewRole) -> OwnershipCapability:
        """Record the automatic claim before exposing the next action."""
        claimed.append(selected)
        return capability

    result = ReviewResumeService().resume(
        ResumeContext(LlmNature.CODEX, (ResumeExchange(state, LlmNature.CODEX, LlmNature.CODEX),), role), acquire,
    )
    assert claimed == [role]
    assert result.capability is capability
    assert result.decision.action is action


@pytest.mark.parametrize("state", [ArtifactState.ESCALATED, ArtifactState.INCONSISTENT])
def test_stopped_evidence_never_claims(state: ArtifactState) -> None:
    """Blocked state cannot be turned into ownership by a role choice or override."""
    result = ReviewResumeService().resume(
        ResumeContext(LlmNature.CODEX, (ResumeExchange(state, None, None),), ReviewRole.REVIEWER, override=True),
        lambda _: pytest.fail("blocked resume claimed"),
    )
    assert result.decision.outcome is ResumeDecisionOutcome.BLOCKED
    assert result.capability is None


def test_selected_role_conflict_requires_override_but_counterpart_gap_does_not() -> None:
    """Only selected-role identity conflicts gate pickup; idle roles never claim."""
    service = ReviewResumeService()
    exchange = ResumeExchange(ArtifactState.REQUEST_PENDING, None, None, reviewer_conflicting=True)
    context = ResumeContext(LlmNature.CODEX, (exchange,), ReviewRole.REVIEWER)
    result = service.resume(context, lambda _: pytest.fail("conflicting role claimed"))
    assert result.decision.outcome is ResumeDecisionOutcome.CONFIRMATION_REQUIRED
    allowed = service.resume(replace(context, override=True), lambda _: OwnershipCapability(1, "n" * 32))
    assert allowed.capability is not None
    idle = service.resume(ResumeContext(LlmNature.UNKNOWN, (), ReviewRole.REVIEWER), lambda _: pytest.fail("idle claim"))
    assert idle.decision.action is ResumeAction.WAIT_ANY_REQUEST


def _ignore_fixture_paths(*_paths: object) -> bool:
    """Keep Git ignore probing outside these real-artifact unit scenarios."""
    return True


def _advance_phase(
    core: ReviewExchangeCore, context: lifecycle.ReviewContext,
    clock: lifecycle.FakeTime, phase: str,
) -> None:
    """Prepare one real durable phase without hiding the resume operation under test."""
    if phase != "request":
        core.reclaim()
        disposition = ReviewDisposition.CHANGES_REQUESTED if phase == "answer" else ReviewDisposition.CONVERGENCE_RECOMMENDED
        core.publish_answer(lifecycle._answer(context, clock, 1, disposition), "Reviewer summary")
        if phase == "authorized":
            core.pickup_ownership(Actor.REQUESTOR)
            core.confirm("Commit")


@pytest.fixture
def prepared_requestor_phase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str,
) -> tuple[ReviewExchangeCore, lifecycle.ReviewExchangeStore, lifecycle.ReviewContext, lifecycle.FakeTime]:
    """Publish as the explicit Codex fixture host regardless of the test runner's host."""
    monkeypatch.delenv("CLAUDECODE", raising=False)
    monkeypatch.setenv("CODEX_THREAD_ID", "resume-requestor-fixture")
    core, store, context, clock = lifecycle._harness(tmp_path)
    cli.ReviewArtifactConfiguration.load(tmp_path).prepare_home()
    monkeypatch.setattr(cli.ReviewArtifactMigration, "_default_ignore_checker", _ignore_fixture_paths)
    (store.paths.coordination.parent / "a.review-mode").write_text("", encoding="utf-8")
    lifecycle._start_and_request(core, context, clock)
    _advance_phase(core, context, clock, phase)
    monkeypatch.setattr(cli, "_wall_clock", clock.now)
    return core, store, context, clock


@pytest.mark.parametrize("phase", ["request", "answer", "convergence", "authorized"])
def test_exact_cli_claim_resumes_each_live_requestor_phase(
    tmp_path: Path, phase: str,
    prepared_requestor_phase: tuple[ReviewExchangeCore, lifecycle.ReviewExchangeStore, lifecycle.ReviewContext, lifecycle.FakeTime],
) -> None:
    """Inspection is read-only; automatic claim preserves live phase and enables its next mutation."""
    core, store, context, clock = prepared_requestor_phase
    before = store.paths.coordination.read_bytes()
    common = ["--document", str(context.document_path), "--role", "requestor", "--trusted-host-hint", "codex"]
    inspected, code = cli.execute_resume_operation(parser().parse_args(["resume-inspect", *common]), tmp_path)
    assert code == 0
    assert store.paths.coordination.read_bytes() == before
    candidate = inspected["candidates"][0]
    payload, code = cli.execute_resume_operation(parser().parse_args([
        "claim", *common, "--round", str(candidate["round"]), "--occurrence", str(candidate["occurrence"]),
    ]), tmp_path)
    assert code == 0
    assert payload["role"] == "requestor"
    capability = OwnershipCapability(payload["ownership_generation"], payload["ownership_token"])
    assert capability.token not in store.paths.coordination.read_text(encoding="utf-8")
    assert capability.token not in store.paths.transcript.read_text(encoding="utf-8")
    resumed = ReviewExchangeCore(store, context, core.policy, core.configuration, wall_clock=clock.now)
    resumed.present_ownership(capability)
    _finish_resumed_phase(resumed, phase, tmp_path)


def _finish_resumed_phase(resumed: ReviewExchangeCore, phase: str, tmp_path: Path) -> None:
    """Prove the fresh capability permits only the selected phase continuation."""
    if phase == "answer":
        resumed.consume_answer(reviewed_work_changed=False)
    elif phase == "convergence":
        resumed.confirm("Commit")
    elif phase == "authorized":
        resumed.complete()
        idle, code = cli.execute_resume_operation(parser().parse_args([
            "resume-inspect", "--role", "requestor", "--trusted-host-hint", "codex",
        ]), tmp_path)
        assert code == 0
        assert idle["action"] == "follow-workflow"


def test_stale_capability_is_replaced_by_authorized_resume(tmp_path: Path) -> None:
    """A fresh lease cannot prevent an explicitly authorized stale-session pickup."""
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    old = core.ownership_capability
    assert old is not None
    first = claim_selected(core, ReviewRole.REVIEWER, LlmNature.UNKNOWN, round_number=1, occurrence=1, override=False)
    core.present_ownership(old)
    second = claim_selected(core, ReviewRole.REVIEWER, LlmNature.UNKNOWN, round_number=1, occurrence=1, override=False)
    assert second.generation > first.generation
    assert second.token != first.token
    assert store.read_coordination(required=True) is not None


def test_competing_reviewers_claim_once_and_loser_returns_to_wait(tmp_path: Path) -> None:
    """Two independent actors observing one request cannot both own its publication."""
    first, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(first, context, clock)
    second = ReviewExchangeCore(store, context, first.policy, first.configuration, wall_clock=clock.now)
    assert claim_discovered_request(first, 1, 1) is not None
    with pytest.raises(OwnershipRejectedError, match="claimed"):
        claim_discovered_request(second, 1, 1)
    assert claim_discovered_request(second, 2, 1) is None
    polls: list[float] = []
    waiter = GlobalReviewerWait(
        rescan_candidates=lambda: (context,), claim_candidate=lambda _: False,
        wait_for_notification=lambda seconds: bool(polls.append(seconds)),
        fallback_poll=lambda: None, poll_interval_seconds=1,
    )
    assert waiter.wait(max_quiet_intervals=1).outcome is GlobalWaitOutcome.IDLE
    assert polls == [1]


@pytest.mark.parametrize(("arguments", "outcome", "code"), [
    (["wait-any-request", "--poll-interval", "nan"], "fatal-input", 2),
    (["wait-any-request", "--poll-interval", "0"], "fatal-input", 2),
    (["claim"], "fatal-input", 2),
])
def test_invalid_input_emits_one_terminal_json(
    arguments: list[str], outcome: str, code: int, capsys: pytest.CaptureFixture[str],
) -> None:
    """Invalid support arguments keep the stable machine result and never emit a secret."""
    assert launcher.main(arguments) == code
    output = capsys.readouterr()
    payload = json.loads(output.out)
    assert payload["outcome"] == outcome
    assert {"operation", "outcome", "identity", "candidates", "diagnostic"} <= payload.keys()
    assert "ownership_token" not in payload
    assert not output.err


# eof
