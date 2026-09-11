"""Property coverage for review-exchange artifact-state classification.

Generated valid artifact/status combinations must either map to the explicit
state table or reach its fail-closed inconsistent catch-all.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ConfirmationOutcome,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import Envelope, render_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

_NOW = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)
_CURRENT = "2026-08-04T11:59:30+00:00"


def _build(root: Path) -> tuple[ReviewExchangeCore, ReviewExchangeStore, ReviewContext]:
    """Build one isolated generated-state harness."""
    document = root / "docs" / "plan.v0.11.0.generated.md"
    document.parent.mkdir(parents=True)
    document.write_text("# Plan\n", encoding="utf-8")
    context = ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", "generated"),
        document,
        None,
        "3",
    )
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    core = ReviewExchangeCore(
        store,
        context,
        FamilyPolicy("ready", "Again", "Commit"),
        ReviewConfiguration(enabled=True, wait_timeout_seconds=60),
        wall_clock=lambda: _NOW,
        monotonic_clock=lambda: 0.0,
        sleeper=lambda _: None,
    )
    return core, store, context


def _content(
    context: ReviewContext,
    role: ReviewRole,
    disposition: ReviewDisposition | None = None,
) -> str:
    """Render a generated artifact with valid identity metadata."""
    return render_envelope_markdown(
        Envelope(
            context.identity,
            None,
            context.document_path,
            "3",
            role,
            1,
            _CURRENT,
            disposition,
        ),
        "Generated.\n",
    )


@dataclass(frozen=True)
class GeneratedShape:
    """One generated fixed-path presence and coordination combination."""

    request: bool
    answer: bool
    tombstone: bool
    status: CoordinationStatus | None
    confirmed: bool


@st.composite
def _shapes(draw: st.DrawFn) -> GeneratedShape:
    """Generate one arbitrary artifact and coordination shape."""
    return GeneratedShape(
        request=draw(st.booleans()),
        answer=draw(st.booleans()),
        tombstone=draw(st.booleans()),
        status=draw(st.one_of(st.none(), st.sampled_from(tuple(CoordinationStatus)))),
        confirmed=draw(st.booleans()),
    )


def _publish_shape(
    store: ReviewExchangeStore,
    context: ReviewContext,
    shape: GeneratedShape,
) -> None:
    """Publish the generated exact-path evidence."""
    if shape.request:
        store.publish_atomic(store.paths.request, _content(context, ReviewRole.REQUESTOR))
    if shape.answer:
        disposition = (
            ReviewDisposition.CONVERGENCE_RECOMMENDED
            if shape.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
            else ReviewDisposition.CHANGES_REQUESTED
        )
        store.publish_atomic(
            store.paths.answer,
            _content(context, ReviewRole.REVIEWER, disposition),
        )
    if shape.tombstone:
        store.publish_atomic(
            store.paths.tombstone,
            _content(context, ReviewRole.REQUESTOR),
        )


def _write_shape_coordination(
    store: ReviewExchangeStore,
    context: ReviewContext,
    shape: GeneratedShape,
) -> None:
    """Persist generated coordination when the shape includes it."""
    status = shape.status
    if status is None:
        return
    owner, expected, lease, convergence, escalation = _generated_status_fields(status)
    outcome = _generated_outcome(status, confirmed=shape.confirmed)
    label, confirmation_timestamp = _generated_confirmation_fields(outcome)
    store.write_coordination(
        CoordinationRecord(
            context,
            FamilyPolicy("ready", "Again", "Commit"),
            status,
            owner,
            expected,
            1,
            lease,
            convergence_recommended=convergence,
            escalation_reason=escalation,
            confirmation_label=label,
            confirmed_outcome=outcome,
            confirmation_timestamp=confirmation_timestamp,
        ),
    )


def _generated_status_fields(
    status: CoordinationStatus,
) -> tuple[Actor, Actor, str | None, bool | None, str | None]:
    """Return actors, lease, convergence, and escalation for one status."""
    if status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION:
        return Actor.REVIEWER, Actor.HUMAN, None, True, None
    if status is CoordinationStatus.ESCALATED:
        return Actor.REQUESTOR, Actor.HUMAN, None, None, "generated"
    return Actor.REQUESTOR, Actor.REVIEWER, _CURRENT, None, None


def _generated_outcome(
    status: CoordinationStatus,
    *,
    confirmed: bool,
) -> ConfirmationOutcome | None:
    """Return owning authorization only for a generated confirmed gate."""
    if status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION and confirmed:
        return ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW
    return None


def _generated_confirmation_fields(
    outcome: ConfirmationOutcome | None,
) -> tuple[str | None, str | None]:
    """Return paired confirmation metadata for an optional outcome."""
    if outcome is None:
        return None, None
    return "Commit", _CURRENT


def _assert_boundary_state(state: ArtifactState, shape: GeneratedShape) -> None:
    """Assert fail-closed conflicts and escalation authority boundaries."""
    assert state in ArtifactState
    if shape.request and shape.answer and shape.status is not CoordinationStatus.ESCALATED:
        assert state is ArtifactState.INCONSISTENT
    if shape.status is CoordinationStatus.ESCALATED:
        assert state is ArtifactState.ESCALATED


def _assert_generated_shape(shape: GeneratedShape) -> None:
    with TemporaryDirectory() as raw_root:
        core, store, context = _build(Path(raw_root))
        _publish_shape(store, context, shape)
        _write_shape_coordination(store, context, shape)

        observation = core.classify()
        _assert_boundary_state(observation.state, shape)


@given(shape=_shapes())
@settings(max_examples=2)
def test_generated_shapes_are_listed_or_fail_closed(shape: GeneratedShape) -> None:
    """The first two generated shapes remain inside the closed state enum."""
    _assert_generated_shape(shape)


@given(shape=_shapes())
@settings(max_examples=2)
def test_additional_generated_shapes_are_listed_or_fail_closed(
    shape: GeneratedShape,
) -> None:
    """A second pair of generated shapes stays inside the closed state enum."""
    _assert_generated_shape(shape)


@given(shape=_shapes())
@settings(max_examples=2)
def test_third_generated_shape_pair_is_listed_or_fails_closed(
    shape: GeneratedShape,
) -> None:
    """A third pair of generated shapes stays inside the closed state enum."""
    _assert_generated_shape(shape)


@given(shape=_shapes())
@settings(max_examples=2)
def test_fourth_generated_shape_pair_is_listed_or_fails_closed(
    shape: GeneratedShape,
) -> None:
    """A fourth pair of generated shapes stays inside the closed state enum."""
    _assert_generated_shape(shape)


@given(shape=_shapes())
@settings(max_examples=2)
def test_fifth_generated_shape_pair_is_listed_or_fails_closed(
    shape: GeneratedShape,
) -> None:
    """A fifth pair preserves the complete ten-example property budget."""
    _assert_generated_shape(shape)


# eof
