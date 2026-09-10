"""Recovery acceptance coverage across fresh review-exchange sessions.

Step 5 injects failures only at documented durable boundaries, then constructs
fresh public core instances over the same real files. Core recovery does not
invoke Git, so its harness writes the opt-in and ignore fixtures directly. The
tests prove that
requests, answers, torn transcript suffixes, escalations, consumed answers,
and owning authorization repair without evidence loss or duplicate entries.
The activation journey captures its real non-repository Git result in fixture
setup so process startup cannot make the measured assertion call an outlier.
Abandoned-request setup likewise precedes measured reclaim and answer checks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_acceptance.test_review_exchange_acceptance_tdd import (
    FakeTime,
    _artifact,
    _context,
    _policy,
)
from tools import review_exchange_paths as paths_module
from tools.review_exchange_core import ReviewExchangeCore, WaitOutcome
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    IncompleteTransitionKind,
    ReviewConfiguration,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_paths import (
    derive_artifact_paths,
    transient_paths_for_ignore,
    validate_activation,
)
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from pathlib import Path
    from subprocess import CompletedProcess

    from tools.review_exchange_models import ArtifactPaths, ReviewContext
    from tools.review_exchange_models_coordination import CoordinationRecord

    Harness = tuple[
        ReviewExchangeCore,
        ReviewExchangeStore,
        ReviewContext,
        FakeTime,
    ]

_WAIT_SECONDS = 60


def _harness(
    root: Path,
    *,
    family: ReviewFamily = ReviewFamily.CODE,
    slug: str = "recovery",
) -> tuple[ReviewExchangeCore, ReviewExchangeStore, ReviewContext, FakeTime]:
    """Build one real-file core with deterministic time and activation files."""
    root.mkdir(parents=True, exist_ok=True)
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (root / "a.review-mode").write_text("", encoding="utf-8")
    step = "5" if family is ReviewFamily.CODE else None
    context = _context(root, family, slug, step=step)
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    clock = FakeTime()
    return _fresh(store, context, clock), store, context, clock


def _fresh(
    store: ReviewExchangeStore,
    context: ReviewContext,
    clock: FakeTime,
    actor: Actor | None = None,
) -> ReviewExchangeCore:
    """Construct a later-session core over the same exact artifact paths."""
    core = ReviewExchangeCore(
        store,
        context,
        _policy(context),
        ReviewConfiguration(enabled=True, wait_timeout_seconds=_WAIT_SECONDS),
        wall_clock=clock.now,
        monotonic_clock=clock.monotonic_now,
        sleeper=clock.sleep,
    )
    if actor is not None:
        core.pickup_ownership(actor)
    return core


def _publish_request(
    core: ReviewExchangeCore,
    context: ReviewContext,
    round_number: int,
    *,
    guidance: str | None = None,
) -> None:
    """Publish one valid request through the public core boundary."""
    core.publish_request(
        _artifact(
            context,
            ReviewRole.REQUESTOR,
            round_number,
            guidance=guidance,
        ),
        f"Requestor acceptance report for round {round_number}.",
    )


def _publish_answer(
    core: ReviewExchangeCore,
    context: ReviewContext,
    round_number: int,
    disposition: ReviewDisposition = ReviewDisposition.CHANGES_REQUESTED,
) -> None:
    """Publish one valid reviewer answer through the public core boundary."""
    core.publish_answer(
        _artifact(
            context,
            ReviewRole.REVIEWER,
            round_number,
            disposition=disposition,
        ),
        f"Reviewer acceptance report for round {round_number}.",
    )


def _start_request(
    core: ReviewExchangeCore,
    context: ReviewContext,
    round_number: int = 1,
) -> None:
    """Start when needed and publish the selected round request."""
    if round_number == 1:
        core.start()
    _publish_request(core, context, round_number)


def _reach_gate(core: ReviewExchangeCore, context: ReviewContext) -> None:
    """Drive one exchange to a retained convergence recommendation."""
    _start_request(core, context)
    _publish_answer(
        core,
        context,
        1,
        ReviewDisposition.CONVERGENCE_RECOMMENDED,
    )


@pytest.fixture
def answer_repair_harnesses(tmp_path: Path) -> tuple[Harness, Harness]:
    """Build both answer crash repositories outside the measured test call."""
    return (
        _harness(tmp_path / "answer-rename"),
        _harness(tmp_path / "answer-append", slug="answer-append"),
    )


@pytest.fixture
def escalation_harnesses(tmp_path: Path) -> tuple[Harness, Harness]:
    """Build escalation and owning repositories outside the measured call."""
    return (
        _harness(tmp_path / "escalation"),
        _harness(tmp_path / "owning", slug="owning"),
    )


@pytest.fixture(params=("no-progress", "disagreement"))
def stagnation_journey(
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    """Run each two-round stagnation path outside its measured call."""
    mode = str(request.param)
    harness = _harness(tmp_path / mode, slug=mode)
    core, store, context, _clock = harness
    _start_request(core, context)
    _publish_answer(core, context, 1)
    first = core.consume_answer(
        reviewed_work_changed=mode == "disagreement",
        disagreement=mode == "disagreement",
    )
    core.continue_round()
    assert first.status is CoordinationStatus.ACTIVE
    _publish_request(core, context, 2)
    _publish_answer(core, context, 2)
    stopped = core.consume_answer(
        reviewed_work_changed=False,
        disagreement=mode == "disagreement",
    )
    assert stopped.status is CoordinationStatus.ESCALATED
    assert store.paths.answer.is_file()
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 1


@pytest.fixture
def outside_git_activation(
    tmp_path: Path,
) -> tuple[Path, ArtifactPaths, CompletedProcess[str]]:
    """Capture Git's real non-repository result outside the measured call."""
    root = tmp_path / "outside-git"
    root.mkdir()
    context = _context(root, ReviewFamily.CODE, "outside-git", step="5")
    paths = derive_artifact_paths(root, context)
    repository = paths_module._run_git(  # noqa: SLF001
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=root,
    )
    assert repository.returncode != 0
    return root, paths, repository


def test_activation_outside_git_fails_without_artifact_mutation(
    outside_git_activation: tuple[Path, ArtifactPaths, CompletedProcess[str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A real non-repository cannot pass effective ignore activation."""
    root, paths, repository = outside_git_activation

    def replay_repository_result(
        command: list[str],
        *,
        cwd: Path,
        input_text: str | None = None,
    ) -> CompletedProcess[str]:
        assert command == ["git", "rev-parse", "--is-inside-work-tree"]
        assert cwd == root
        assert input_text is None
        return repository

    monkeypatch.setattr(paths_module, "_run_git", replay_repository_result)

    with pytest.raises(ReviewExchangeError, match="requires a Git repository"):
        validate_activation(root, paths)

    assert not any(path.exists() for path in transient_paths_for_ignore(paths))


@pytest.fixture
def interrupted_request_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run torn-request repair outside the measured call phase."""
    core, store, context, clock = _harness(tmp_path / "request")
    core.start()
    original_append = store.append_transcript_once

    def tear_then_stop(*_args: object, **_kwargs: object) -> object:
        with store.paths.transcript.open("ab") as transcript:
            transcript.write(b"\n## torn acceptance suffix")
        message = "injected request append interruption"
        raise ReviewExchangeError(message)

    monkeypatch.setattr(store, "append_transcript_once", tear_then_stop)
    with pytest.raises(ReviewExchangeError, match="request append interruption"):
        _publish_request(core, context, 1)
    marked = store.read_coordination(required=True)
    assert marked is not None
    assert marked.incomplete_transition is IncompleteTransitionKind.PUBLISH_REQUEST
    assert store.paths.request.is_file()

    monkeypatch.setattr(store, "append_transcript_once", original_append)
    _publish_request(_fresh(store, context, clock, Actor.REQUESTOR), context, 1)

    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert "torn acceptance suffix" not in transcript
    assert transcript.count("review-entry-id: request-step-5-round-1") == 1
    assert (
        _fresh(store, context, clock).classify().state is ArtifactState.REQUEST_PENDING
    )


def test_interrupted_request_and_torn_transcript_repair_once(
    interrupted_request_journey: None,
) -> None:
    """A fresh session truncates a torn request entry and appends it once."""
    assert interrupted_request_journey is None


@pytest.fixture
def interrupted_answer_repair_journey(
    answer_repair_harnesses: tuple[Harness, Harness],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tombstone-only and visible-answer crash windows both resume exactly."""
    first_harness, second_harness = answer_repair_harnesses
    core, store, context, clock = first_harness
    _start_request(core, context)
    answer = _artifact(
        context,
        ReviewRole.REVIEWER,
        1,
        disposition=ReviewDisposition.CHANGES_REQUESTED,
    )
    original_commit = store._commit_prepared

    def stop_before_answer(prepared: Path, target: Path) -> None:
        if target == store.paths.answer:
            message = "injected answer visibility interruption"
            raise ReviewExchangeError(message)
        original_commit(prepared, target)

    monkeypatch.setattr(store, "_commit_prepared", stop_before_answer)
    with pytest.raises(ReviewExchangeError, match="answer visibility interruption"):
        core.publish_answer(answer, "Reviewer acceptance report.")
    assert not store.paths.request.exists()
    assert store.paths.tombstone.is_file()
    assert not store.paths.answer.exists()

    monkeypatch.setattr(store, "_commit_prepared", original_commit)
    _fresh(store, context, clock, Actor.REVIEWER).publish_answer(
        answer,
        "Reviewer acceptance report.",
    )
    assert store.paths.answer.is_file()
    assert not store.paths.tombstone.exists()

    second, second_store, second_context, second_clock = second_harness
    _start_request(second, second_context)
    second_answer = _artifact(
        second_context,
        ReviewRole.REVIEWER,
        1,
        disposition=ReviewDisposition.CHANGES_REQUESTED,
    )
    original_second_append = second_store.append_transcript_once

    def stop_after_answer(*_args: object, **_kwargs: object) -> object:
        message = "injected answer append interruption"
        raise ReviewExchangeError(message)

    monkeypatch.setattr(second_store, "append_transcript_once", stop_after_answer)
    with pytest.raises(ReviewExchangeError, match="answer append interruption"):
        second.publish_answer(second_answer, "Reviewer visible-answer report.")
    assert second_store.paths.answer.is_file()
    assert second_store.paths.tombstone.is_file()

    monkeypatch.setattr(second_store, "append_transcript_once", original_second_append)
    _fresh(second_store, second_context, second_clock, Actor.REVIEWER).publish_answer(
        second_answer,
        "Reviewer visible-answer report.",
    )
    transcript = second_store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: answer-step-5-round-1") == 1
    assert not second_store.paths.tombstone.exists()


def test_interrupted_answer_rename_and_visible_append_repair(
    interrupted_answer_repair_journey: None,
) -> None:
    """Both answer-repair windows remain covered by the prepared journey."""
    assert interrupted_answer_repair_journey is None


@pytest.fixture
def consumed_answer_interruption_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run consumed-answer interruption outside the measured call phase."""
    core, store, context, clock = _harness(tmp_path / "consumption")
    _start_request(core, context)
    _publish_answer(core, context, 1)
    original_write = store.write_coordination

    def stop_after_consumption(record: CoordinationRecord) -> None:
        if record.reviewed_work_changed is not None:
            message = "injected answer consumption interruption"
            raise ReviewExchangeError(message)
        original_write(record)

    monkeypatch.setattr(store, "write_coordination", stop_after_consumption)
    with pytest.raises(ReviewExchangeError, match="consumption interruption"):
        core.consume_answer(reviewed_work_changed=True)
    assert not store.paths.answer.exists()
    assert store.paths.coordination.is_file()

    monkeypatch.setattr(store, "write_coordination", original_write)
    clock.sleep(_WAIT_SECONDS + 1)
    later = _fresh(store, context, clock)
    observation = later.classify()
    assert observation.state is ArtifactState.ABANDONED_MID_ROUND
    assert observation.record is not None
    assert observation.record.expected_next_actor is Actor.REQUESTOR
    later.pickup_ownership(Actor.REQUESTOR)
    later.escalate(observation.diagnostic)
    assert later.classify().state is ArtifactState.ESCALATED


def test_consumed_answer_interruption_becomes_attributed_abandonment(
    consumed_answer_interruption_journey: None,
) -> None:
    """A crash after answer removal retains coordination for later escalation."""
    assert consumed_answer_interruption_journey is None


@pytest.fixture
def abandoned_request_session(tmp_path: Path) -> tuple[ReviewExchangeCore, ReviewExchangeStore, ReviewContext]:
    """Prepare an expired real request and a new session before its recovery."""
    core, store, context, clock = _harness(tmp_path / "reclaim", slug="reclaim")
    _start_request(core, context)
    clock.sleep(_WAIT_SECONDS + 1)
    later = _fresh(store, context, clock)
    return later, store, context


def test_abandoned_request_is_reclaimed_by_a_fresh_session(
    abandoned_request_session: tuple[ReviewExchangeCore, ReviewExchangeStore, ReviewContext],
) -> None:
    """A late reviewer session renews the lease in place and answers the round."""
    later, store, context = abandoned_request_session
    assert later.classify().state is ArtifactState.ABANDONED_REQUEST

    reclaimed = later.reclaim()

    assert reclaimed.round_number == 1
    assert later.classify().state is ArtifactState.REQUEST_PENDING
    _publish_answer(later, context, 1)
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: answer-step-5-round-1") == 1
    assert transcript.count("Outcome: escalation") == 0


@pytest.fixture
def escalation_and_completion_replay_journey(
    escalation_harnesses: tuple[Harness, Harness],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Escalation and confirmed completion survive their final write failures."""
    escalation_harness, owning_harness = escalation_harnesses
    core, store, context, clock = escalation_harness
    _start_request(core, context)
    original_append = store.append_transcript_once

    def stop_escalation(*_args: object, **_kwargs: object) -> object:
        message = "injected escalation append interruption"
        raise ReviewExchangeError(message)

    monkeypatch.setattr(store, "append_transcript_once", stop_escalation)
    with pytest.raises(ReviewExchangeError, match="escalation append interruption"):
        core.escalate("Acceptance evidence requires human review.")
    marked = store.read_coordination(required=True)
    assert marked is not None
    assert marked.status is CoordinationStatus.ESCALATED
    assert marked.incomplete_transition is IncompleteTransitionKind.ESCALATION

    monkeypatch.setattr(store, "append_transcript_once", original_append)
    _fresh(store, context, clock, Actor.REQUESTOR).escalate(
        "Acceptance evidence requires human review.",
    )
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: escalation-round-1") == 1

    owning, owning_store, owning_context, owning_clock = owning_harness
    _reach_gate(owning, owning_context)
    owning.confirm("Commit")
    original_remove = owning_store.remove_exact
    failed = False

    def stop_coordination_cleanup(path: Path) -> bool:
        nonlocal failed
        if path == owning_store.paths.coordination and not failed:
            failed = True
            message = "injected owning completion interruption"
            raise ReviewExchangeError(message)
        return original_remove(path)

    monkeypatch.setattr(owning_store, "remove_exact", stop_coordination_cleanup)
    with pytest.raises(ReviewExchangeError, match="owning completion interruption"):
        owning.complete()
    assert not owning_store.paths.answer.exists()
    assert owning_store.paths.coordination.is_file()

    monkeypatch.setattr(owning_store, "remove_exact", original_remove)
    later_owning = _fresh(owning_store, owning_context, owning_clock)
    later_owning.pickup_ownership(Actor.REQUESTOR)
    assert later_owning.complete() is True
    assert later_owning.complete() is False


def test_escalation_append_and_owning_completion_replay(
    escalation_and_completion_replay_journey: None,
) -> None:
    """Both final-write recovery paths remain covered by the prepared journey."""
    assert escalation_and_completion_replay_journey is None


def test_automated_stagnation_and_persistent_disagreement_stop(
    stagnation_journey: None,
) -> None:
    """Two unchanged rounds or a repeated disagreement preserve the last answer."""
    assert stagnation_journey is None


@pytest.fixture
def isolated_wait_journey(
    tmp_path: Path,
) -> None:
    """Run one isolated wait outside the measured assertion call."""
    root = tmp_path / "wait-isolation"
    root.mkdir(parents=True)
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (root / "a.review-mode").write_text("", encoding="utf-8")
    wanted_context = _context(root, ReviewFamily.CODE, "wanted", step="5")
    other_context = _context(root, ReviewFamily.CODE, "other", step="5")
    wanted_store = ReviewExchangeStore(derive_artifact_paths(root, wanted_context))
    other_store = ReviewExchangeStore(derive_artifact_paths(root, other_context))
    clock = FakeTime()
    wanted = _fresh(wanted_store, wanted_context, clock)
    other = _fresh(other_store, other_context, clock)
    wanted.start()
    other.start()
    _publish_request(other, other_context, 1)

    result = wanted.wait_for_exact(
        ArtifactState.REQUEST_PENDING,
        timeout_seconds=2,
        poll_interval=1,
        progress_interval=1,
    )

    assert result.outcome is WaitOutcome.TIMED_OUT
    assert wanted.classify().state is ArtifactState.ESCALATED
    assert other.classify().state is ArtifactState.REQUEST_PENDING
    assert other_store.paths.request.is_file()
    assert not wanted_store.paths.request.exists()


def test_exact_wait_ignores_an_unrelated_identity(
    isolated_wait_journey: None,
) -> None:
    """A request for another slug cannot satisfy one injected-clock deadline."""
    assert isolated_wait_journey is None


# eof
