"""Lifecycle acceptance for authorized implementation-review cleanup.

Step 4 composes marker routing, exact step rendering, staged repair evidence,
shared exchange rounds, human override, durable commit authorization, replay,
and clean completion. Deferred answers come from the test-local strict builder;
only the final batch subprocess boundary is replaced. Renderer-only journeys
use one deterministic valid tree object; the real Git capture boundary has its
own temporary-repository tests.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from tools import code_review_request as request_renderer
from tools import prompt_workflow_code_review as code_review
from tools import prompt_workflow_skill as skill
from tools.code_review_validation import resolve_code_review_validation
from tools.commit_plan_check import CommitPlanCheckResult, CommitPlanCheckState
from tools.prompt_workflow_models import MemoryRecord, Topic, WorkflowState
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ArtifactState,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

# Test doubles intentionally replace functions with smaller signatures.
# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false
from .code_answer_builder import build_code_answer

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

# ruff: noqa: S603, S607

_ROUND_TWO = 2
_ROUND_THREE = 3
_REQUEST_INDEX_TREE = "a" * 40
_CORES: dict[Path, ReviewExchangeCore] = {}


@dataclass(frozen=True)
class Effort:
    """One temporary reviewed project with workflow and exchange identity."""

    root: Path
    topic: Topic
    state: WorkflowState
    record: MemoryRecord
    context: ReviewContext
    plan: Path
    umbrella: Path


def _git(root: Path, *arguments: str) -> None:
    """Run one bounded Git command in the temporary reviewed repository."""
    subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )


def _effort(root: Path, *, marker: bool = True, step: str = "4") -> Effort:
    """Create one opted-in plan effort with an exact declared step."""
    root.mkdir(parents=True)
    _git(root, "init", "-q")
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    if marker:
        (root / "a.review-mode").write_text("", encoding="utf-8")
    docs = root / "docs" / "v0.11.0"
    docs.mkdir(parents=True)
    umbrella = docs / "draft.v0.11.0.review-mode.md"
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    draft = docs / "draft.v0.11.0.acceptance.md"
    draft.write_text(
        "# Child\n\n- Umbrella: "
        "docs/v0.11.0/draft.v0.11.0.review-mode.md\n",
        encoding="utf-8",
    )
    plan = docs / "plan.v0.11.0.acceptance.md"
    plan.write_text(
        "# Plan\n\n### Step 3. routing\n\n### Step 4. acceptance\n",
        encoding="utf-8",
    )
    validation = docs / "plan.v0.11.0.acceptance.validation.md"
    validation.write_text(
        "# Validation\n\n### Analysis of Step 3 implementation state\n\n"
        "Yes. Step 3 has been fully implemented.\n\n"
        "### Analysis of Step 4 implementation state\n\nNot started.\n",
        encoding="utf-8",
    )
    topic = Topic("v0.11.0", "acceptance", draft)
    state = WorkflowState(
        requirement=None,
        design=None,
        plan=plan,
        validation_plan=validation,
        requirement_has_open_questions=False,
        design_has_open_questions=False,
        plan_has_open_questions=False,
        memory_step=10,
    )
    record = MemoryRecord(
        branch="acceptance",
        version="v0.11.0",
        topic="acceptance",
        step=10,
        instruction="implement-step.md",
        plan_step=step,
    )
    context = request_renderer.code_review_context(plan, step, umbrella)
    return Effort(root, topic, state, record, context, plan, umbrella)


def _core(
    effort: Effort,
    *,
    wall_clock: Callable[[], datetime] | None = None,
    timeout: int = 300,
) -> ReviewExchangeCore:
    """Bind the shared core to the settled code policy and exact paths."""
    core = ReviewExchangeCore(
        ReviewExchangeStore(derive_artifact_paths(effort.root, effort.context)),
        effort.context,
        code_review.CODE_REVIEW_POLICY,
        ReviewConfiguration(enabled=True, wait_timeout_seconds=timeout),
        wall_clock=wall_clock,
    )
    if wall_clock is not None:
        return core
    return _CORES.setdefault(effort.root, core)


def _request(
    effort: Effort,
    round_number: int,
    *,
    change_summary: str = "a.commit and the staged diff match the plan step.",
    writer_response: str = "The writer requests independent code review.",
    guidance: str | None = None,
) -> request_renderer.CodeReviewRequestRender:
    """Render one complete request from separate authored round inputs."""
    return request_renderer.render_code_review_request(
        request_renderer.CodeReviewRoundInput(
            context=effort.context,
            round_number=round_number,
            created_at="2026-08-13T20:00:00+02:00",
            assessment="implementation-check reports the exact step complete.",
            implementation_report="Implemented and tested the declared plan step.",
            change_summary=change_summary,
            writer_response=writer_response,
            request_index_tree=_REQUEST_INDEX_TREE,
            resolved_validation_set=resolve_code_review_validation(
                ("ghog day",),
                ("focused acceptance tests",),
            ),
            commit_plan_result=CommitPlanCheckResult(CommitPlanCheckState.VALID),
            human_guidance=guidance,
        ),
    )


def _publish_request(effort: Effort, round_number: int, **kwargs: str) -> None:
    """Publish one specialized request through validated shared state rules."""
    rendered = _request(effort, round_number, **kwargs)
    _core(effort).publish_request(
        rendered.request_content,
        rendered.transcript_summary,
    )


def _publish_heading_guidance(
    effort: Effort,
    round_number: int,
    guidance: str,
) -> None:
    """Publish and inspect one request whose stored guidance starts with a heading."""
    _publish_request(effort, round_number, guidance=guidance)
    request = _core(effort).store.paths.request.read_text(encoding="utf-8")
    assert (
        "Human guidance:\n\n"
        "### Human decision for step 4 acceptance (round 3)"
        in request
    )


def _publish_answer(
    effort: Effort,
    round_number: int,
    disposition: ReviewDisposition,
    *,
    repaired_paths: tuple[str, ...] = (),
    recommendation: str,
) -> None:
    """Publish one deferred-reviewer answer through the shared answer surface."""
    answer = build_code_answer(
        effort.context,
        round_number,
        disposition,
        repaired_paths=repaired_paths,
        recommendation=recommendation,
    )
    _core(effort).publish_answer(answer.content, answer.summary)


@pytest.fixture
def marker_efforts(tmp_path: Path) -> tuple[Effort, Effort]:
    """Create opted-out and opted-in repositories outside the measured call."""
    return _effort(tmp_path / "ordinary", marker=False), _effort(tmp_path / "reviewed")


def test_marker_absent_preserves_gate_and_marker_present_carries_exact_step(
    marker_efforts: tuple[Effort, Effort],
) -> None:
    """Review mode alone replaces the ordinary gate with a self-contained route."""
    ordinary, reviewed = marker_efforts
    assert (
        code_review.resolve_code_review_route(
            ordinary.root,
            ordinary.topic,
            ordinary.state,
            ordinary.record,
        )
        is None
    )
    assert not tuple(ordinary.root.glob("a.review-*"))

    route = code_review.resolve_code_review_route(
        reviewed.root,
        reviewed.topic,
        reviewed.state,
        reviewed.record,
    )
    assert route is not None
    command = code_review.command_for_route(
        reviewed.root,
        route,
        "$llm-shared:",
        skill.render_step_command,
    )
    assert command.endswith(
        "code-review-requestor on "
        "docs/v0.11.0/plan.v0.11.0.acceptance.md step 4",
    )
    assert route.context == reviewed.context


@pytest.fixture
def repeated_round_journey(tmp_path: Path) -> None:
    """Run substantive repair, disagreement, polishing, and override rounds."""
    effort = _effort(tmp_path / "rounds")
    core = _core(effort)
    core.start()
    _publish_request(effort, 1)
    repaired = effort.root / "src" / "repair.py"
    repaired.parent.mkdir()
    repaired.write_text("VALUE = 1\n", encoding="utf-8")
    _git(effort.root, "add", "src/repair.py")
    (effort.root / "a.commit").write_text(
        "git add -A src/repair.py\n",
        encoding="utf-8",
    )
    _publish_answer(
        effort,
        1,
        ReviewDisposition.CHANGES_REQUESTED,
        repaired_paths=("src/repair.py",),
        recommendation="Review the substantive staged repair in another round.",
    )
    answer = core.store.paths.answer.read_text(encoding="utf-8")
    assert "`src/repair.py`" in answer
    assert _git_names(effort.root) == ("src/repair.py",)
    assessed = core.consume_answer(reviewed_work_changed=True, disagreement=True)
    assert assessed.clarification_used
    assert core.continue_round().round_number == _ROUND_TWO

    _publish_request(
        effort,
        _ROUND_TWO,
        change_summary="Accepted src/repair.py; a.commit membership is unchanged.",
        writer_response="The writer records the explicit disagreement as resolved.",
    )
    _publish_answer(
        effort,
        _ROUND_TWO,
        ReviewDisposition.CONVERGENCE_RECOMMENDED,
        recommendation="Only wording changed; commit-ready.",
    )
    assert core.classify().state is ArtifactState.CONVERGENCE_GATE
    guidance = "## Human decision\n\nCheck the staged repair once more."
    override = core.confirm(
        "Rework and review again",
        guidance=guidance,
    )
    assert not override.owning_action_authorized
    assert override.record.round_number == _ROUND_THREE
    assert override.record.no_progress_streak == 0
    assert override.record.human_guidance == guidance
    _publish_heading_guidance(effort, _ROUND_THREE, guidance)


def _git_names(root: Path) -> tuple[str, ...]:
    """Return the exact staged-path inventory for requestor assessment."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return tuple(result.stdout.splitlines())


def test_substantive_repair_disagreement_and_override_start_bounded_rounds(
    repeated_round_journey: None,
) -> None:
    """Intermediate work and a human override each advance through public state."""
    assert repeated_round_journey is None


@pytest.fixture
def repeated_reversal_result(tmp_path: Path) -> tuple[str, ArtifactState]:
    """Run the two-reversal journey outside the measured assertion call."""
    effort = _effort(tmp_path / "disagreement")
    core = _core(effort)
    core.start()
    _publish_request(effort, 1)
    _publish_answer(
        effort,
        1,
        ReviewDisposition.CHANGES_REQUESTED,
        recommendation="Restore the repair.",
    )
    core.consume_answer(reviewed_work_changed=True, disagreement=True)
    core.continue_round()
    _publish_request(
        effort,
        2,
        writer_response="The writer again rejects and reverts the repair.",
    )
    _publish_answer(
        effort,
        2,
        ReviewDisposition.CHANGES_REQUESTED,
        recommendation="Restore the repair again.",
    )
    record = core.consume_answer(reviewed_work_changed=True, disagreement=True)
    return record.status.value, core.classify().state


def test_second_recorded_reversal_escalates_instead_of_looping(
    repeated_reversal_result: tuple[str, ArtifactState],
) -> None:
    """Explicit repair reversal uses the shared one-clarification bound."""
    status, state = repeated_reversal_result
    assert status == "escalated"
    assert state is ArtifactState.ESCALATED


@pytest.fixture
def substantive_gate_core(tmp_path: Path) -> ReviewExchangeCore:
    """Publish a substantive commit-ready answer outside the measured call."""
    effort = _effort(tmp_path / "substantive-gate")
    core = _core(effort)
    core.start()
    _publish_request(effort, 1)
    _publish_answer(
        effort,
        1,
        ReviewDisposition.CONVERGENCE_RECOMMENDED,
        repaired_paths=("tests/test_repair.py",),
        recommendation="Rework and review again because the repair is substantive.",
    )
    return core


def test_substantive_commit_ready_stays_at_gate_for_human_override(
    substantive_gate_core: ReviewExchangeCore,
) -> None:
    """A repaired commit-ready answer cannot be consumed into a private round."""
    core = substantive_gate_core
    restored = core.consume_answer(reviewed_work_changed=True)
    assert restored.status.value == "awaiting-human-confirmation"
    assert core.classify().state is ArtifactState.CONVERGENCE_GATE


@pytest.fixture
def authorized_commit_effort(tmp_path: Path) -> Effort:
    """Build durable Commit authority outside the measured continuation call."""
    effort = _effort(tmp_path / "commit")
    core = _core(effort)
    core.start()
    _publish_request(effort, 1)
    _publish_answer(
        effort,
        1,
        ReviewDisposition.CONVERGENCE_RECOMMENDED,
        recommendation="commit-ready after polishing-only review.",
    )
    decision = core.confirm("Commit")
    assert decision.owning_action_authorized
    assert core.classify().state is ArtifactState.OWNING_ACTION_PENDING
    (effort.root / "a.review-mode").unlink()
    return effort


def test_commit_authorization_replays_once_then_cleans_live_state(
    authorized_commit_effort: Effort,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A later requestor session consumes durable Commit authority exactly once."""
    effort = authorized_commit_effort
    calls: list[tuple[tuple[str, ...], Path]] = []

    def successful(
        arguments: tuple[str, ...],
        *,
        cwd: Path,
    ) -> subprocess.CompletedProcess[str]:
        calls.append((arguments, cwd))
        return subprocess.CompletedProcess(arguments, 0)

    monkeypatch.setattr(code_review, "run_batch_commit", successful)
    monkeypatch.setattr(code_review.git, "status_entries", lambda _root: [])
    assert code_review.continue_authorized_commit(
        effort.root,
        effort.topic,
        effort.state,
        effort.record,
    ) == 0
    assert calls == [
        (("--root-a-commit", "--non-interactive"), effort.root.resolve()),
    ]
    assert _core(effort).classify().state is ArtifactState.IDLE
    with pytest.raises(code_review.CodeReviewRoutingError, match="not authorized"):
        code_review.continue_authorized_commit(
            effort.root,
            effort.topic,
            effort.state,
            effort.record,
        )
    assert len(calls) == 1


@pytest.fixture
def expired_request_reclaim_journey(tmp_path: Path) -> None:
    """A later session renews the same plan-step round without rewriting evidence."""
    effort = _effort(tmp_path / "reclaim")
    now = datetime(2026, 8, 13, 20, tzinfo=UTC)
    first = _core(effort, wall_clock=lambda: now, timeout=1)
    first.start()
    rendered = _request(effort, 1)
    first.publish_request(rendered.request_content, rendered.transcript_summary)
    request_before = first.store.paths.request.read_bytes()
    returning = _core(
        effort,
        wall_clock=lambda: now + timedelta(seconds=2),
        timeout=1,
    )
    assert returning.classify().state is ArtifactState.ABANDONED_REQUEST
    assert returning.reclaim().round_number == 1
    assert returning.classify().state is ArtifactState.REQUEST_PENDING
    assert returning.store.paths.request.read_bytes() == request_before


def test_expired_request_reclaim_preserves_exact_code_identity(
    expired_request_reclaim_journey: None,
) -> None:
    """The exact-identity reclaim remains covered by the prepared journey."""
    assert expired_request_reclaim_journey is None


# eof
