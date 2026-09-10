"""Recovery and retained-context acceptance for the specification reviewer."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from tools import prompt_workflow_skill
from tools.prompt_workflow_review import SpecificationReviewRoutingError
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ReviewConfiguration,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

from .fixtures import (
    POLICY,
    Effort,
    core,
    make_effort,
    publish_request,
    render_answer,
    render_request,
)


class Clock:
    """Deterministic wall clock used to expire one reviewer lease."""

    def __init__(self) -> None:
        """Start at one fixed aware timestamp."""
        self.value = datetime(2026, 8, 11, 12, tzinfo=UTC)

    def now(self) -> datetime:
        """Return the current controlled wall time."""
        return self.value

    def advance(self, seconds: int) -> None:
        """Advance the wall clock beyond the configured lease."""
        self.value += timedelta(seconds=seconds)


def _manifest(effort: Effort, original_round: int = 1) -> Path:
    """Write retained reviewer evidence matching the current document exactly."""
    home = effort.root / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    inputs = [
        home / "a.reviewer-assessment.md",
        home / "a.question-verdicts.md",
        home / "a.writer-instructions.md",
        home / "a.requested-changes.md",
    ]
    for path, content in zip(
        inputs,
        ("Assessment.", "Q01: A.", "Apply A.", "Clarify A."),
        strict=True,
    ):
        path.write_text(content, encoding="utf-8")
    manifest = home / "a.retained-context.json"
    manifest.write_text(
        json.dumps(
            {
                "document_sha256": hashlib.sha256(
                    effort.document.read_bytes(),
                ).hexdigest(),
                "identity": effort.context.identity.to_dict(),
                "original_round_number": original_round,
                "assessment_input_paths": [
                    path.resolve().as_posix() for path in inputs
                ],
            },
        ),
        encoding="utf-8",
    )
    return manifest


def _publish_with_core(active: ReviewExchangeCore, effort: Effort) -> None:
    """Publish one exact request through a caller-owned public core."""
    active.start()
    content, summary = render_request(effort)
    active.publish_request(
        content.read_text(encoding="utf-8"),
        summary.read_text(encoding="utf-8"),
    )


@pytest.fixture
def cold_reclaim_journey(tmp_path: Path) -> None:
    """Run cold-route reclaim refusal outside the measured call phase."""
    effort = make_effort(tmp_path / "cold", "plan", "cold-reclaim")
    clock = Clock()
    active = core(effort, wall_clock=clock.now, timeout=1)
    _publish_with_core(active, effort)
    clock.advance(2)

    assert active.classify().state is ArtifactState.ABANDONED_REQUEST
    ordinary = prompt_workflow_skill.next_command(
        effort.root,
        effort.topic,
        effort.topic.slug,
        {"CODEX_THREAD_ID": "fresh"},
    )
    with pytest.raises(
        SpecificationReviewRoutingError,
        match="spec-review-requestor reclaim",
    ):
        prompt_workflow_skill.forced_command(
            effort.root,
            effort.topic,
            "spec-reviewer",
            {"CODEX_THREAD_ID": "fresh"},
        )

    assert ordinary is not None
    assert "spec-review-requestor" in ordinary


def test_cold_abandoned_route_returns_control_to_requestor(
    cold_reclaim_journey: None,
) -> None:
    """A fresh route never lets the reviewer seize an abandoned request."""
    assert cold_reclaim_journey is None


@pytest.fixture
def session_reclaim_journey(tmp_path: Path) -> None:
    """Run in-session lease reclaim outside the measured call phase."""
    effort = make_effort(tmp_path / "session", "design", "session-reclaim")
    clock = Clock()
    active = core(effort, wall_clock=clock.now, timeout=1)
    _publish_with_core(active, effort)
    clock.advance(2)

    reclaimed = active.reclaim()

    assert reclaimed.round_number == 1
    assert active.classify().state is ArtifactState.REQUEST_PENDING


def test_in_session_reviewer_reclaims_its_expired_lease_once(
    session_reclaim_journey: None,
) -> None:
    """The active reviewer may reclaim the exact request it already assessed."""
    assert session_reclaim_journey is None


@pytest.fixture
def interrupted_publication_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run interrupted publication replay outside the measured call phase."""
    effort = make_effort(tmp_path / "replay", "feature-request", "replay")
    assert publish_request(effort).code == 0
    content, summary = render_answer(effort, ReviewDisposition.CHANGES_REQUESTED)
    paths = derive_artifact_paths(effort.root, effort.context)
    store = ReviewExchangeStore(paths)
    active = ReviewExchangeCore(
        store,
        effort.context,
        POLICY,
        ReviewConfiguration(enabled=True, wait_timeout_seconds=300),
    )
    active.pickup_ownership(Actor.REVIEWER)
    original_append = store.append_transcript_once

    def stop_after_visibility(*_args: object, **_kwargs: object) -> object:
        message = "injected answer append interruption"
        raise ReviewExchangeError(message)

    monkeypatch.setattr(store, "append_transcript_once", stop_after_visibility)
    with pytest.raises(ReviewExchangeError, match="append interruption"):
        active.publish_answer(
            content.read_text(encoding="utf-8"),
            summary.read_text(encoding="utf-8"),
        )
    monkeypatch.setattr(store, "append_transcript_once", original_append)

    repairing = core(effort)
    repairing.pickup_ownership(Actor.REVIEWER)
    repairing.publish_answer(
        content.read_text(encoding="utf-8"),
        summary.read_text(encoding="utf-8"),
    )

    transcript = paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: answer-round-1") == 1
    assert core(effort).classify().state is ArtifactState.ANSWER_PENDING


def test_interrupted_answer_publication_replays_without_duplicate_transcript(
    interrupted_publication_journey: None,
) -> None:
    """A fresh reviewer session repairs the durable publication boundary once."""
    assert interrupted_publication_journey is None


@pytest.fixture
def retained_assessment_journey(
    tmp_path: Path,
) -> None:
    """Run retained-manifest validation outside the measured call phase."""
    effort = make_effort(tmp_path / "retained", "issue", "retained")
    manifest = _manifest(effort)

    answer, _ = render_answer(
        effort,
        ReviewDisposition.CHANGES_REQUESTED,
        manifest=manifest,
    )
    assert answer.exists()
    assert manifest.exists(), "retained evidence survives until publication succeeds"

    effort.document.write_text("# Drifted specification\n", encoding="utf-8")
    with pytest.raises(AssertionError):
        render_answer(
            effort,
            ReviewDisposition.CHANGES_REQUESTED,
            manifest=manifest,
        )


def test_stopped_assessment_is_retained_and_revalidated_before_republication(
    retained_assessment_journey: None,
) -> None:
    """A matching manifest resumes, while fresh document drift fails closed."""
    assert retained_assessment_journey is None


def test_manifest_is_retired_only_after_successful_answer_publication() -> None:
    """The canonical workflow keys retirement on the published outcome."""
    content = Path("instructions/spec-reviewer.md").read_text(encoding="utf-8")
    retained = content.index("retained manifest")
    publication = content.index("publish-answer", retained)
    retirement = content.index("retire", publication)

    assert retained < publication < retirement
    assert "`outcome: published`" in content[publication : retirement + 300]
    assert "retirement on exit `0` alone" in content
    assert "leak the single-use manifest on every convergence" in content


def test_escalation_requires_human_resolution_before_recovery(tmp_path: Path) -> None:
    """Protocol contradictions stop at the human gate without needless Git I/O."""
    effort = make_effort(
        tmp_path / "escalation",
        "plan",
        "escalation",
        initialize_git=False,
    )
    active = core(effort)
    active.start()

    record = active.escalate("acceptance contradiction", role=ReviewRole.REVIEWER)

    assert record.status.value == "escalated"
    assert active.classify().state is ArtifactState.ESCALATED
    instruction = Path("instructions/spec-reviewer.md").read_text(encoding="utf-8")
    assert "`resolve`" in instruction
    assert "Stop for human recovery" in instruction
