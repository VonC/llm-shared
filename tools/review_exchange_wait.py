"""Bounded monotonic waiting policy for review exchanges.

Step 3 keeps counterpart polling in one in-process call with one monotonic
deadline. The policy reports periodic progress without renewing durable leases
and delegates escalation through an injected lifecycle callback. A repair state
whose marker is the counterpart's own in-flight publication of the expected
artifact is polled through; any other pending marker ends the wait as
repair-required.
"""

# ruff: noqa: EM101, PLR0913, TRY003

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Final

from tools.review_exchange_models import (
    ArtifactState,
    IncompleteTransitionKind,
    ReviewExchangeError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.review_exchange_observer import ExchangeObservation


_COUNTERPART_MARKERS: Final[dict[ArtifactState, IncompleteTransitionKind]] = {
    ArtifactState.REQUEST_PENDING: IncompleteTransitionKind.PUBLISH_REQUEST,
    ArtifactState.ANSWER_PENDING: IncompleteTransitionKind.PUBLISH_ANSWER,
}


class WaitOutcome(StrEnum):
    """Bounded exact-wait outcomes exposed to later adapters."""

    FOUND = "found"
    TIMED_OUT = "timed-out"
    ABANDONED = "abandoned"
    ESCALATED = "escalated"
    INCONSISTENT = "inconsistent"
    REPAIR_REQUIRED = "repair-required"


@dataclass(frozen=True)
class WaitProgress:
    """One periodic in-process progress update from a bounded wait."""

    elapsed_seconds: float
    remaining_seconds: float
    state: ArtifactState


@dataclass(frozen=True)
class WaitResult:
    """Final exact-wait outcome returned once per invocation."""

    outcome: WaitOutcome
    observation: ExchangeObservation


def wait_for_exact(
    expected: ArtifactState,
    *,
    timeout_seconds: int,
    poll_interval: float,
    progress_interval: float,
    progress_callback: Callable[[WaitProgress], None] | None,
    monotonic_clock: Callable[[], float],
    sleeper: Callable[[float], None],
    observe: Callable[[], ExchangeObservation],
    escalate: Callable[[str], ExchangeObservation],
) -> WaitResult:
    """Poll one exact counterpart state against one monotonic deadline."""
    _validate_wait(expected, timeout_seconds, poll_interval, progress_interval)
    started = monotonic_clock()
    deadline = started + timeout_seconds
    next_progress = started + progress_interval
    while True:
        current = monotonic_clock()
        if current >= deadline:
            observation = escalate(_timeout_reason(expected))
            return WaitResult(WaitOutcome.TIMED_OUT, observation)
        observation = observe()
        if _matches_expected(expected, observation.state):
            return WaitResult(WaitOutcome.FOUND, observation)
        terminal = _terminal_result(observation, escalate, expected)
        if terminal is not None:
            return terminal
        next_progress = _report_progress(
            progress_callback,
            current=current,
            started=started,
            deadline=deadline,
            next_progress=next_progress,
            progress_interval=progress_interval,
            state=observation.state,
        )
        sleeper(
            _poll_delay(
                poll_interval,
                deadline=deadline,
                current=current,
                next_progress=(next_progress if progress_callback is not None else None),
            ),
        )


def _validate_wait(
    expected: ArtifactState,
    timeout_seconds: int,
    poll_interval: float,
    progress_interval: float,
) -> None:
    """Reject targets and intervals that cannot form a bounded wait."""
    if expected not in {ArtifactState.REQUEST_PENDING, ArtifactState.ANSWER_PENDING}:
        raise ReviewExchangeError("wait target must be request pending or answer pending")
    if timeout_seconds <= 0 or poll_interval <= 0 or progress_interval <= 0:
        raise ReviewExchangeError("wait intervals must be positive")


def _matches_expected(expected: ArtifactState, observed: ArtifactState) -> bool:
    """Accept an exact counterpart or its authoritative convergence form."""
    return observed is expected or (
        expected is ArtifactState.ANSWER_PENDING
        and observed is ArtifactState.CONVERGENCE_GATE
    )


def _report_progress(
    callback: Callable[[WaitProgress], None] | None,
    *,
    current: float,
    started: float,
    deadline: float,
    next_progress: float,
    progress_interval: float,
    state: ArtifactState,
) -> float:
    """Emit at most one due progress event and return its next deadline."""
    if callback is not None and current >= next_progress:
        callback(WaitProgress(current - started, deadline - current, state))
        return current + progress_interval
    return next_progress


def _poll_delay(
    poll_interval: float,
    *,
    deadline: float,
    current: float,
    next_progress: float | None,
) -> float:
    """Bound one sleep by the wait and optional progress deadlines."""
    delay = min(poll_interval, deadline - current)
    if next_progress is not None:
        delay = min(delay, max(0.0, next_progress - current))
    return delay


def _terminal_result(
    observation: ExchangeObservation,
    escalate: Callable[[str], ExchangeObservation],
    expected: ArtifactState,
) -> WaitResult | None:
    """Convert non-waitable states to final outcomes and escalation evidence."""
    if observation.state in {
        ArtifactState.ABANDONED_MID_ROUND,
        ArtifactState.ABANDONED_REQUEST,
        ArtifactState.ABANDONED_ANSWER,
        ArtifactState.INTERRUPTED_ANSWER_PUBLICATION,
        ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND,
    }:
        actor = (
            observation.record.expected_next_actor.value
            if observation.record is not None
            else "unknown actor"
        )
        escalated = escalate(f"exchange was abandoned while waiting for {actor}")
        return WaitResult(WaitOutcome.ABANDONED, escalated)
    if observation.state is ArtifactState.ESCALATED:
        return WaitResult(WaitOutcome.ESCALATED, observation)
    if observation.state is ArtifactState.INCONSISTENT:
        return WaitResult(WaitOutcome.INCONSISTENT, observation)
    if observation.state in {
        ArtifactState.TRANSCRIPT_REPAIR_PENDING,
        ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS,
    }:
        marker = (
            observation.record.incomplete_transition
            if observation.record is not None
            else None
        )
        if marker is _COUNTERPART_MARKERS[expected]:
            return None
        return WaitResult(WaitOutcome.REPAIR_REQUIRED, observation)
    return None


def _timeout_reason(expected: ArtifactState) -> str:
    """Return stable timeout evidence for one counterpart artifact."""
    noun = "request" if expected is ArtifactState.REQUEST_PENDING else "answer"
    return f"wait timed out while {noun} was absent"


# eof
