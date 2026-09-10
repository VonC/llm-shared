"""Tests for exact-path code-review routing and authorized commit replay.

The suite pins one plan-step context, marker-gated cold entry, live exchange
precedence, fail-closed identity checks, and the reviewed batch boundary before
the separately tested residual cleanup phase.
"""

from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools import prompt_workflow_code_review as code_review
from tools import prompt_workflow_skill as skill
from tools import prompt_workflow_steps as steps
from tools.prompt_workflow_models import MemoryRecord, Topic, WorkflowState
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ConfirmationOutcome,
    CoordinationStatus,
    ExchangeIdentity,
    ReviewContext,
    ReviewFamily,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

# Test doubles intentionally replace functions with smaller signatures.
# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false


def _effort(root: Path, step: str = "3") -> tuple[Topic, WorkflowState, MemoryRecord]:
    """Create one exact plan effort and matching workflow memory."""
    docs = root / "docs" / "v0.11.0"
    docs.mkdir(parents=True)
    draft = docs / "draft.v0.11.0.routing.md"
    plan = docs / "plan.v0.11.0.routing.md"
    validation = docs / "plan.v0.11.0.routing.validation.md"
    draft.write_text("# draft\n", encoding="utf-8")
    plan.write_text(
        "# plan\n\n### Step 1. one\n\n### Step 3. three\n\n### Step 4A. four\n",
        encoding="utf-8",
    )
    validation.write_text(
        "# validation\n\n### Analysis of Step 1 implementation state\n\n"
        "Yes. Step 1 has been fully implemented.\n\n"
        "### Analysis of Step 3 implementation state\n\nNot started.\n\n"
        "### Analysis of Step 4A implementation state\n\nNot started.\n",
        encoding="utf-8",
    )
    topic = Topic("v0.11.0", "routing", draft)
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
        branch="routing",
        version="v0.11.0",
        topic="routing",
        step=10,
        instruction="implement-step.md",
        plan_step=step,
    )
    return topic, state, record


def _context(root: Path, step: str = "3") -> ReviewContext:
    """Return the code-family context for the scratch plan and step."""
    document = root / "docs/v0.11.0/plan.v0.11.0.routing.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    if not document.exists():
        document.write_text("# plan\n", encoding="utf-8")
    return ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", "routing"),
        document,
        None,
        step,
    )


def _coordination(context: ReviewContext, status: CoordinationStatus) -> CoordinationRecord:
    """Build one valid active or authorized coordination record."""
    confirmed = status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
    return CoordinationRecord(
        context=context,
        policy=code_review.CODE_REVIEW_POLICY,
        status=status,
        owner=Actor.REQUESTOR,
        expected_next_actor=Actor.HUMAN if confirmed else Actor.REVIEWER,
        round_number=1,
        lease_renewed_at="2099-08-13T12:00:00+02:00",
        convergence_recommended=True if confirmed else None,
        confirmation_label="Commit" if confirmed else None,
        confirmed_outcome=(
            ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW if confirmed else None
        ),
        confirmation_timestamp=("2026-08-13T12:00:00+02:00" if confirmed else None),
    )


def test_resolve_route_is_disabled_without_marker_or_live_state(tmp_path: Path) -> None:
    """Cold routing stays absent and creates no artifacts without review mode."""
    topic, state, record = _effort(tmp_path)

    assert code_review.resolve_code_review_route(tmp_path, topic, state, record) is None
    assert (
        code_review.resolve_code_review_route(
            tmp_path,
            topic,
            state,
            replace(record, plan_step="unknown"),
        )
        is None
    )
    assert not tuple(tmp_path.glob("a.review-*"))


def test_marker_routes_exact_plan_step_and_rejects_unknown_context(tmp_path: Path) -> None:
    """Cold entry validates the declared plan step and ignores another topic."""
    topic, state, record = _effort(tmp_path, "4A")
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")

    route = code_review.resolve_code_review_route(tmp_path, topic, state, record)

    assert route is not None
    assert route.state is ArtifactState.IDLE
    assert route.context.document_path == state.plan
    assert route.context.implementation_step == "4A"
    with pytest.raises(code_review.CodeReviewRoutingError, match="unknown plan step"):
        code_review.resolve_code_review_route(
            tmp_path,
            topic,
            state,
            replace(record, plan_step="9"),
        )
    assert (
        code_review.resolve_code_review_route(
            tmp_path,
            topic,
            state,
            replace(record, topic="other"),
        )
        is None
    )
    assert (
        code_review.resolve_code_review_route(
            tmp_path,
            topic,
            state,
            replace(record, version="v0.12.0"),
        )
        is None
    )


def test_context_validation_rejects_missing_inputs_and_bad_identity(tmp_path: Path) -> None:
    """Exact context derivation fails closed before any protocol mutation."""
    topic, state, record = _effort(tmp_path)
    with pytest.raises(code_review.CodeReviewRoutingError, match="plan document"):
        code_review._context(tmp_path, topic, replace(state, plan=None), record)  # noqa: SLF001
    with pytest.raises(code_review.CodeReviewRoutingError, match="implementation step"):
        code_review._context(tmp_path, topic, state, None)  # noqa: SLF001
    with pytest.raises(code_review.CodeReviewRoutingError, match="validation plan"):
        code_review._context(  # noqa: SLF001
            tmp_path,
            topic,
            replace(state, validation_plan=None),
            record,
        )
    wrong_topic = replace(topic, version="v0.12.0")
    wrong_record = replace(record, version="v0.12.0")
    with pytest.raises(code_review.CodeReviewRoutingError, match="plan identity"):
        code_review._context(tmp_path, wrong_topic, state, wrong_record)  # noqa: SLF001


def test_umbrella_validation_accepts_one_exact_in_root_path(tmp_path: Path) -> None:
    """Umbrella parsing accepts one file and rejects malformed or unsafe markers."""
    topic, _, _ = _effort(tmp_path)
    umbrella = tmp_path / "docs/v0.11.0/draft.v0.11.0.collection.md"
    umbrella.write_text("# umbrella\n", encoding="utf-8")
    topic.draft_path.write_text(
        "# draft\n\n- Umbrella: docs/v0.11.0/draft.v0.11.0.collection.md\n",
        encoding="utf-8",
    )
    assert code_review._umbrella_path(tmp_path, topic) == umbrella.resolve()  # noqa: SLF001
    topic.draft_path.write_text("- Umbrella: \n", encoding="utf-8")
    with pytest.raises(code_review.CodeReviewRoutingError, match="ambiguous"):
        code_review._umbrella_path(tmp_path, topic)  # noqa: SLF001
    topic.draft_path.write_text("- Umbrella: ../outside.md\n", encoding="utf-8")
    with pytest.raises(code_review.CodeReviewRoutingError, match="outside"):
        code_review._umbrella_path(tmp_path, topic)  # noqa: SLF001
    topic.draft_path.write_text("- Umbrella: docs/missing.md\n", encoding="utf-8")
    with pytest.raises(code_review.CodeReviewRoutingError, match="does not exist"):
        code_review._umbrella_path(tmp_path, topic)  # noqa: SLF001


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (CoordinationStatus.ACTIVE, ArtifactState.ROUND_IN_PROGRESS),
        (CoordinationStatus.AWAITING_HUMAN_CONFIRMATION, ArtifactState.OWNING_ACTION_PENDING),
    ],
)
def test_live_route_wins_after_marker_removal(
    tmp_path: Path,
    status: CoordinationStatus,
    expected: ArtifactState,
) -> None:
    """Durable coordination, not a later marker change, governs live routing."""
    topic, state, record = _effort(tmp_path)
    context = _context(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, context))
    store.write_coordination(_coordination(context, status))

    route = code_review.resolve_code_review_route(tmp_path, topic, state, record)

    assert route is not None
    assert route.state is expected


def test_live_route_rejects_another_step_and_duplicate_coordination(tmp_path: Path) -> None:
    """Another step or a second exact code identity fails closed."""
    topic, state, record = _effort(tmp_path)
    wanted = _context(tmp_path)
    other_step = replace(wanted, implementation_step="4A")
    ReviewExchangeStore(derive_artifact_paths(tmp_path, other_step)).write_coordination(
        _coordination(other_step, CoordinationStatus.ACTIVE),
    )
    with pytest.raises(code_review.CodeReviewRoutingError, match="implementation step"):
        code_review.resolve_code_review_route(tmp_path, topic, state, record)

    wanted_store = ReviewExchangeStore(derive_artifact_paths(tmp_path, wanted))
    wanted_store.write_coordination(_coordination(wanted, CoordinationStatus.ACTIVE))
    wanted_store.paths.request.parent.mkdir(parents=True, exist_ok=True)
    wanted_store.paths.request.write_text("conflicting request", encoding="utf-8")
    with pytest.raises(code_review.CodeReviewRoutingError, match="inconsistent"):
        code_review.resolve_code_review_route(tmp_path, topic, state, record)


def test_authorized_continuation_calls_batch_once_and_keeps_failures_pending(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The continuation checks durable authority and calls one external boundary."""
    topic, state, record = _effort(tmp_path)
    context = _context(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, context))
    store.write_coordination(
        _coordination(context, CoordinationStatus.AWAITING_HUMAN_CONFIRMATION),
    )
    calls: list[tuple[str, ...]] = []
    failed_exit = 9

    def failed(command: tuple[str, ...], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        assert cwd == tmp_path.resolve()
        return subprocess.CompletedProcess(command, failed_exit)

    monkeypatch.setattr(code_review, "run_batch_commit", failed)

    assert (
        code_review.continue_authorized_commit(tmp_path, topic, state, record)
        == failed_exit
    )
    assert calls == [("--root-a-commit", "--non-interactive")]
    pending = store.read_coordination(required=True)
    assert pending is not None
    assert pending.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
    assert (
        pending.confirmed_outcome
        is ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW
    )


def test_authorized_continuation_rejects_missing_authority(tmp_path: Path) -> None:
    """A cold or merely active exchange cannot enter the commit continuation."""
    topic, state, record = _effort(tmp_path)
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    with pytest.raises(code_review.CodeReviewRoutingError, match="not authorized"):
        code_review.continue_authorized_commit(tmp_path, topic, state, record)


def test_command_rendering_and_batch_boundary_are_direct(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The route renderer carries the step and the batch adapter forwards once."""
    topic, state, record = _effort(tmp_path)
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    route = code_review.resolve_code_review_route(tmp_path, topic, state, record)
    assert route is not None
    assert code_review.command_for_route(
        tmp_path,
        route,
        "$",
        skill.render_step_command,
    ) == "$llm-shared:code-review-requestor on docs/v0.11.0/plan.v0.11.0.routing.md step 3"
    calls: list[tuple[list[str], Path]] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        cwd = kwargs["cwd"]
        if not isinstance(cwd, Path):
            raise TypeError
        calls.append((command, cwd))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(code_review.subprocess, "run", fake_run)
    result = code_review.run_batch_commit(("--root-a-commit",), cwd=tmp_path)
    assert result.returncode == 0
    launcher = steps.llm_shared_dir() / "bin" / "gcba.bat"
    assert calls == [([str(launcher), "--root-a-commit"], tmp_path)]
    assert launcher.is_file(), "the batch launcher ships with llm-shared"
    assert not str(launcher).startswith(str(tmp_path))


def test_successful_authorized_continuation_completes_exchange(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A zero batch result consumes durable authorization and retained evidence."""
    topic, state, record = _effort(tmp_path)
    context = _context(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, context))
    store.write_coordination(
        _coordination(context, CoordinationStatus.AWAITING_HUMAN_CONFIRMATION),
    )
    monkeypatch.setattr(
        code_review,
        "run_batch_commit",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0),
    )
    monkeypatch.setattr(code_review.git, "status_entries", lambda _root: [])
    assert code_review.continue_authorized_commit(tmp_path, topic, state, record) == 0
    assert not store.paths.coordination.exists()


def test_authorized_continuation_rechecks_confirmation_outcome(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The owning state alone cannot bypass the persisted confirmation outcome."""
    topic, state, record = _effort(tmp_path)
    context = _context(tmp_path)
    route = code_review.CodeReviewRoute(
        context,
        ArtifactState.OWNING_ACTION_PENDING,
        code_review.CodeReviewActor.REQUESTOR,
    )
    coordination = replace(
        _coordination(context, CoordinationStatus.AWAITING_HUMAN_CONFIRMATION),
        confirmed_outcome=ConfirmationOutcome.ANOTHER_ROUND,
    )
    fake_core = SimpleNamespace(
        store=SimpleNamespace(read_coordination=lambda **_kwargs: coordination),
    )
    monkeypatch.setattr(code_review, "resolve_code_review_route", lambda *_args: route)
    monkeypatch.setattr(code_review, "_core", lambda *_args: fake_core)
    with pytest.raises(code_review.CodeReviewRoutingError, match="durably authorized"):
        code_review.continue_authorized_commit(tmp_path, topic, state, record)


def test_skill_delegates_live_forced_and_authorized_routes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The risk-band skill router delegates each code-review entry unchanged."""
    topic, state, record = _effort(tmp_path)
    context = _context(tmp_path)
    route = code_review.CodeReviewRoute(
        context,
        ArtifactState.REQUEST_PENDING,
        code_review.CodeReviewActor.REVIEWER,
    )
    monkeypatch.setattr(skill.steps, "compute_state", lambda *_args: state)
    monkeypatch.setattr(skill.memory, "read_memory", lambda _root: record)
    monkeypatch.setattr(code_review, "resolve_code_review_route", lambda *_args: route)

    live = skill.next_command(tmp_path, topic, "routing", {"CLAUDECODE": "1"})
    forced = skill.forced_command(
        tmp_path,
        topic,
        "code-review-requestor",
        {"CODEX_THREAD_ID": "x"},
    )
    assert live == "/code-reviewer on docs/v0.11.0/plan.v0.11.0.routing.md step 3"
    assert forced is None
    monkeypatch.setattr(skill.git, "current_branch", lambda _root: "routing")
    monkeypatch.setattr(skill.handoff, "resolve_current_topic", lambda *_args: topic)
    continuation_exit = 7
    monkeypatch.setattr(
        code_review,
        "continue_authorized_commit",
        lambda *_args, **_kwargs: continuation_exit,
    )
    assert skill.run_authorized_code_review_commit(tmp_path) == continuation_exit
    monkeypatch.setattr(skill.handoff, "resolve_current_topic", lambda *_args: None)
    with pytest.raises(code_review.CodeReviewRoutingError, match="no resolved"):
        skill.run_authorized_code_review_commit(tmp_path)


@pytest.mark.parametrize(
    ("state", "actor"),
    [
        (ArtifactState.REQUEST_PENDING, code_review.CodeReviewActor.REVIEWER),
        (ArtifactState.IDLE, code_review.CodeReviewActor.REQUESTOR),
        (ArtifactState.ROUND_IN_PROGRESS, code_review.CodeReviewActor.REQUESTOR),
        (ArtifactState.ABANDONED_REQUEST, code_review.CodeReviewActor.REVIEWER),
        (ArtifactState.ANSWER_PENDING, code_review.CodeReviewActor.REQUESTOR),
        (ArtifactState.ABANDONED_ANSWER, code_review.CodeReviewActor.REQUESTOR),
        (ArtifactState.CONVERGENCE_GATE, code_review.CodeReviewActor.REQUESTOR),
        (ArtifactState.OWNING_ACTION_PENDING, code_review.CodeReviewActor.REQUESTOR),
        (ArtifactState.ESCALATED, code_review.CodeReviewActor.REQUESTOR),
        (ArtifactState.TRANSCRIPT_REPAIR_PENDING, code_review.CodeReviewActor.REQUESTOR),
    ],
)
def test_route_actor_is_resolved_once_from_the_classified_state(
    state: ArtifactState,
    actor: code_review.CodeReviewActor,
    tmp_path: Path,
) -> None:
    """Only pending or reclaimable requests belong to the reviewer."""
    route = code_review.CodeReviewRoute(_context(tmp_path), state, actor)

    assert route.actor is actor


def test_route_rejects_an_actor_that_disagrees_with_its_state(tmp_path: Path) -> None:
    """A caller cannot forge reviewer or requestor ownership after classify."""
    with pytest.raises(code_review.CodeReviewRoutingError, match="actor"):
        code_review.CodeReviewRoute(
            _context(tmp_path),
            ArtifactState.REQUEST_PENDING,
            code_review.CodeReviewActor.REQUESTOR,
        )
    with pytest.raises(code_review.CodeReviewRoutingError, match="actor"):
        code_review.CodeReviewRoute(
            _context(tmp_path),
            ArtifactState.ANSWER_PENDING,
            code_review.CodeReviewActor.REVIEWER,
        )
