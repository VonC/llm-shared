"""Publication, round-transition, and wait coverage for the exchange core.

Step 3 coordinates marker-first publication, bounded waits, automated progress,
and convergence over the Step 2 store without holding locks across counterpart
work. Recovery and escalation cases live in the focused recovery sibling.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_envelope import Envelope, render_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


_START = datetime(2026, 8, 4, 14, 0, tzinfo=UTC)
_SECOND_ROUND = 2
_REQUEST_EXPOSURE_TIME = 102.0
_EXPECTED_ARCHIVE_COUNT = 2


class FakeTime:
    """Advance wall and monotonic clocks together without a real sleep."""

    def __init__(self) -> None:
        """Start both clocks at deterministic values."""
        self.wall = _START
        self.monotonic = 100.0
        self.after_sleep: Callable[[], None] | None = None

    def now(self) -> datetime:
        """Return the current injected wall clock."""
        return self.wall

    def monotonic_now(self) -> float:
        """Return the current injected monotonic clock."""
        return self.monotonic

    def sleep(self, seconds: float) -> None:
        """Advance both clocks and invoke an optional poll hook."""
        self.monotonic += seconds
        self.wall += timedelta(seconds=seconds)
        if self.after_sleep is not None:
            self.after_sleep()


def _context(root: Path, implementation_step: str = "3") -> ReviewContext:
    """Create the exact code-review context used by lifecycle tests."""
    document = root / "docs" / "plan.v0.11.0.review-exchange-core.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# Plan\n", encoding="utf-8")
    umbrella = root / "docs" / "draft.v0.11.0.review-mode.md"
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    return ReviewContext(
        ExchangeIdentity(
            ReviewFamily.CODE,
            "code",
            "v0.11.0",
            "review-exchange-core",
        ),
        document,
        umbrella,
        implementation_step,
    )


def _harness(
    root: Path,
    *,
    wait_seconds: int = 60,
    implementation_step: str = "3",
) -> tuple[ReviewExchangeCore, ReviewExchangeStore, ReviewContext, FakeTime]:
    """Build one core with deterministic time and exact persistence."""
    context = _context(root, implementation_step)
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    clock = FakeTime()
    core = ReviewExchangeCore(
        store,
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        ReviewConfiguration(enabled=True, wait_timeout_seconds=wait_seconds),
        wall_clock=clock.now,
        monotonic_clock=clock.monotonic_now,
        sleeper=clock.sleep,
    )
    return core, store, context, clock


def _timestamp(clock: FakeTime) -> str:
    """Render the injected local timestamp in protocol format."""
    return clock.now().astimezone().isoformat(timespec="seconds")


def _summary(context: ReviewContext, round_number: int, guidance: str | None = None) -> str:
    """Render the mandatory code-family request summary."""
    umbrella = context.umbrella_path
    assert umbrella is not None
    lines = [
        f"Umbrella draft: {umbrella.as_posix()}",
        f"Implementation plan: {context.document_path.as_posix()}",
        f"Implementation step: {context.implementation_step}",
        f"Review round: {round_number}",
    ]
    if guidance is not None:
        lines.extend(("", f"Human guidance: {guidance}"))
    return "\n".join(lines) + "\n"


def _request(context: ReviewContext, clock: FakeTime, round_number: int) -> str:
    """Render one valid request with its identity-bearing summary."""
    envelope = Envelope(
        context.identity,
        context.umbrella_path,
        context.document_path,
        context.implementation_step,
        ReviewRole.REQUESTOR,
        round_number,
        _timestamp(clock),
    )
    return render_envelope_markdown(envelope, _summary(context, round_number))


def _answer(
    context: ReviewContext,
    clock: FakeTime,
    round_number: int,
    disposition: ReviewDisposition = ReviewDisposition.CHANGES_REQUESTED,
) -> str:
    """Render one valid reviewer answer."""
    envelope = Envelope(
        context.identity,
        context.umbrella_path,
        context.document_path,
        context.implementation_step,
        ReviewRole.REVIEWER,
        round_number,
        _timestamp(clock),
        disposition,
    )
    return render_envelope_markdown(envelope, "Reviewer feedback.\n")


def _start_and_request(
    core: ReviewExchangeCore,
    context: ReviewContext,
    clock: FakeTime,
    round_number: int = 1,
) -> None:
    """Start an exchange and publish its current request."""
    if round_number == 1:
        core.start()
    core.publish_request(
        _request(context, clock, round_number),
        f"Requestor report for round {round_number}.",
    )


def _reach_gate(
    core: ReviewExchangeCore,
    context: ReviewContext,
    clock: FakeTime,
) -> None:
    """Drive one exchange to a retained convergence answer."""
    _start_and_request(core, context, clock)
    core.publish_answer(
        _answer(
            context,
            clock,
            1,
            ReviewDisposition.CONVERGENCE_RECOMMENDED,
        ),
        "The reviewer recommends convergence.",
    )


def test_start_initializes_transcript_and_rejects_a_second_exchange(
    tmp_path: Path,
) -> None:
    """One exact document can own only one active coordination record."""
    core, store, _, _ = _harness(tmp_path)

    record = core.start()

    assert record.status is CoordinationStatus.ACTIVE
    assert record.owner is Actor.REQUESTOR
    assert record.expected_next_actor is Actor.REVIEWER
    assert record.round_number == 1
    assert record.lease_renewed_at == "2026-08-04T16:00:00+02:00"
    assert store.paths.transcript.is_file()
    with pytest.raises(ReviewExchangeError, match="already active"):
        core.start()


def test_disabled_configuration_rejects_start_without_writing(tmp_path: Path) -> None:
    """The application service remains inert when review mode is disabled."""
    _, store, context, clock = _harness(tmp_path)
    core = ReviewExchangeCore(
        store,
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        ReviewConfiguration(enabled=False, wait_timeout_seconds=60),
        wall_clock=clock.now,
        monotonic_clock=clock.monotonic_now,
        sleeper=clock.sleep,
    )

    with pytest.raises(ReviewExchangeError, match="review mode is disabled"):
        core.start()

    assert core.classify().state is ArtifactState.IDLE
    assert not store.paths.transcript.exists()


def test_publish_request_validates_summary_appends_once_and_renews_lease(
    tmp_path: Path,
) -> None:
    """Request publication is marker-first, identity-safe, and auditable."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    clock.sleep(5)

    record = core.publish_request(
        _request(context, clock, 1),
        "Requestor implementation report.",
    )

    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert store.paths.request.is_file()
    assert record.expected_next_actor is Actor.REVIEWER
    assert record.incomplete_transition is None
    assert record.lease_renewed_at == "2026-08-04T16:00:05+02:00"
    assert transcript.count("review-entry-id: request-step-3-round-1") == 1
    assert "Requestor implementation report." in transcript
    assert context.document_path.as_posix() not in transcript
    assert "docs/plan.v0.11.0.review-exchange-core.md" in transcript


def test_publish_request_rejects_summary_mismatch_before_mutation(tmp_path: Path) -> None:
    """Human-readable context must agree with the request envelope."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    invalid = _request(context, clock, 1).replace(
        f"Implementation plan: {context.document_path.as_posix()}",
        "Implementation plan: docs/plan.v0.11.0.wrong.md",
    )

    with pytest.raises(ReviewExchangeError, match="summary identity mismatch"):
        core.publish_request(invalid, "Invalid summary.")

    assert not store.paths.request.exists()
    record = store.read_coordination(required=True)
    assert record is not None
    assert record.incomplete_transition is None


@pytest.fixture
def repaired_request_append_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repair one torn request append outside the measured assertion call."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    original_append = store._append_bytes
    failed = False

    def fail_once(path: Path, content: bytes) -> None:
        nonlocal failed
        if not failed:
            failed = True
            path.write_bytes(path.read_bytes() + content[:20])
            message = "injected torn request append"
            raise OSError(message)
        original_append(path, content)

    monkeypatch.setattr(store, "_append_bytes", fail_once)
    request = _request(context, clock, 1)
    with pytest.raises(ReviewExchangeError, match="transcript append failed"):
        core.publish_request(request, "Repair this request entry.")

    marked = store.read_coordination(required=True)
    assert marked is not None
    assert marked.incomplete_transition is IncompleteTransitionKind.PUBLISH_REQUEST
    record = core.publish_request(request, "Repair this request entry.")
    transcript = store.paths.transcript.read_text(encoding="utf-8")

    assert record.incomplete_transition is None
    assert transcript.count("review-entry-id: request-step-3-round-1") == 1


def test_request_append_failure_repairs_from_marker_without_duplication(
    repaired_request_append_journey: None,
) -> None:
    """Re-running a marked request truncates only its torn suffix and completes it."""
    assert repaired_request_append_journey is None


@pytest.fixture
def restarted_exchange_journey(
    tmp_path: Path,
) -> None:
    """Complete and inspect two exchanges outside the measured call."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)
    core.confirm("Commit")
    assert core.complete()
    core.start()
    core.publish_request(
        _request(context, clock, 1),
        "Requestor report for exchange two.",
    )
    core.publish_answer(
        _answer(context, clock, 1),
        "Reviewer report for exchange two.",
    )

    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert "by requestor - Step 3 (exchange 2)" in transcript
    assert "by reviewer - Step 3 (exchange 2)" in transcript
    assert transcript.count("review-entry-id: request-step-3-round-1 -->") == 1
    assert transcript.count("review-entry-id: answer-step-3-round-1 -->") == 1
    assert "review-entry-id: request-step-3-round-1-exchange-2" in transcript
    assert "review-entry-id: answer-step-3-round-1-exchange-2" in transcript


def test_restarted_exchange_disambiguates_request_and_answer_entries(
    restarted_exchange_journey: None,
) -> None:
    """A new exchange may restart at round one without transcript collisions."""
    assert restarted_exchange_journey is None


@pytest.fixture
def legacy_request_repair_journey(
    tmp_path: Path,
) -> tuple[ReviewExchangeCore, ReviewExchangeStore]:
    """Prepare the legacy pending request outside the measured call phase."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)
    core.confirm("Commit")
    assert core.complete()
    core.start()
    core.publish_request(
        _request(context, clock, 1),
        "### Assessment (exchange 2)\n\nCurrent summary.",
    )
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    legacy = transcript.replace(" - Step 3 (exchange 2)", " - Step 3").replace(
        "request-step-3-round-1-exchange-2",
        "request-step-3-round-1",
    )
    store.paths.transcript.write_text(legacy, encoding="utf-8")
    return core, store


def test_pending_legacy_request_entry_is_repaired_through_the_core(
    legacy_request_repair_journey: tuple[ReviewExchangeCore, ReviewExchangeStore],
) -> None:
    """Only the final pending legacy collision can be re-rendered in place."""
    core, store = legacy_request_repair_journey

    record = core.repair_current_request_transcript(
        "### Assessment (exchange 2)\n\nCorrected summary.",
    )

    repaired = store.paths.transcript.read_text(encoding="utf-8")
    assert record.incomplete_transition is None
    assert repaired.count("## Round 1 by requestor - Step 3") == len(
        ("exchange one", "exchange two"),
    )
    assert "## Round 1 by requestor - Step 3 (exchange 2)" in repaired
    assert "review-entry-id: request-step-3-round-1-exchange-2" in repaired
    assert "Corrected summary." in repaired


# eof
