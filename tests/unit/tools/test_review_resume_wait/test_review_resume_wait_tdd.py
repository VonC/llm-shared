"""Test the quiet, cancellable global reviewer wait contract for Step 5.

Fix: covers the capped backoff of hint-less rescans, its reset on a hint, the
retry one interval after a hinted rescan that found nothing, and the rejected
non-positive cap. The ports record the wait count at each rescan.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from tools.review_exchange_models import ReviewExchangeError
from tools.review_resume_wait import (
    GlobalReviewerWait,
    GlobalWaitOutcome,
)

EXPECTED_RESCANS = 3
EXPECTED_QUIET_INTERVALS = 2
BACKOFF_CAP = 4
BACKOFF_QUIET_INTERVALS = 11
RESET_CAP = 8
RESET_QUIET_INTERVALS = 6
RESET_FALLBACKS = 5
PRODUCTION_CAP = 30

def _candidate_batches() -> list[tuple[str, ...]]:
    """Return an isolated default sequence of candidate batches."""
    return []


def _booleans() -> list[bool]:
    """Return an isolated default sequence of boolean port results."""
    return []


def _wait_counts() -> list[int]:
    """Return an isolated default record of wait counts at each rescan."""
    return []


@dataclass
class WaitPorts:
    """Provide deterministic discovery, notification, fallback, and claim ports."""

    batches: list[tuple[str, ...]] = field(default_factory=_candidate_batches)
    notifications: list[bool] = field(default_factory=_booleans)
    claims: list[bool] = field(default_factory=_booleans)
    rescans: int = 0
    waits: int = 0
    fallbacks: int = 0
    rescan_waits: list[int] = field(default_factory=_wait_counts)

    def rescan(self) -> tuple[str, ...]:
        """Return the next authoritative candidate batch."""
        self.rescans += 1
        self.rescan_waits.append(self.waits)
        return self.batches.pop(0) if self.batches else ()

    def wait_for_notification(self, _seconds: float) -> bool:
        """Return the next notification hint without emitting progress."""
        self.waits += 1
        return self.notifications.pop(0) if self.notifications else False

    def fallback_poll(self) -> None:
        """Record one bounded fallback poll."""
        self.fallbacks += 1

    def claim(self, _candidate: object) -> bool:
        """Return whether the compare-and-swap claim won."""
        return self.claims.pop(0) if self.claims else True


class TestGlobalReviewerWait:
    """Exercise all foreground wait terminal and bounded-seam outcomes."""

    def test_quiet_limit_returns_idle_after_bounded_polling(self) -> None:
        """A deterministic test limit performs no busy-loop work."""
        ports = WaitPorts()

        result = GlobalReviewerWait(
            rescan_candidates=ports.rescan,
            wait_for_notification=ports.wait_for_notification,
            fallback_poll=ports.fallback_poll,
            poll_interval_seconds=1.0,
        ).wait(max_quiet_intervals=2)

        assert result.outcome is GlobalWaitOutcome.IDLE
        assert result.candidates == ()
        assert ports.rescans == EXPECTED_RESCANS
        assert ports.waits == EXPECTED_QUIET_INTERVALS
        assert ports.fallbacks == EXPECTED_QUIET_INTERVALS

    def test_notification_hint_rescans_without_fallback(self) -> None:
        """A notification remains only a hint before the authoritative rescan."""
        ports = WaitPorts(batches=[(), ("request",)], notifications=[True])

        result = GlobalReviewerWait(
            rescan_candidates=ports.rescan,
            wait_for_notification=ports.wait_for_notification,
            fallback_poll=ports.fallback_poll,
            poll_interval_seconds=1.0,
        ).wait()

        assert result.outcome is GlobalWaitOutcome.FOUND
        assert result.candidate == "request"
        assert ports.fallbacks == 0

    def test_multiple_candidates_return_ambiguity_without_claiming(self) -> None:
        """Simultaneous requests require human selection instead of queueing."""
        ports = WaitPorts(batches=[("first", "second")])

        result = GlobalReviewerWait(
            rescan_candidates=ports.rescan,
            wait_for_notification=ports.wait_for_notification,
            fallback_poll=ports.fallback_poll,
            claim_candidate=ports.claim,
            poll_interval_seconds=1.0,
        ).wait()

        assert result.outcome is GlobalWaitOutcome.AMBIGUOUS
        assert result.candidates == ("first", "second")
        assert ports.claims == []

    def test_lost_claim_returns_to_discovery(self) -> None:
        """A compare-and-swap loser keeps waiting for another request."""
        ports = WaitPorts(batches=[("first",), (), ("second",)], claims=[False, True])

        result = GlobalReviewerWait(
            rescan_candidates=ports.rescan,
            wait_for_notification=ports.wait_for_notification,
            fallback_poll=ports.fallback_poll,
            claim_candidate=ports.claim,
            poll_interval_seconds=1.0,
        ).wait()

        assert result.outcome is GlobalWaitOutcome.FOUND
        assert result.candidate == "second"
        assert ports.waits == EXPECTED_QUIET_INTERVALS

    def test_keyboard_interrupt_returns_one_cancelled_result(self) -> None:
        """A graceful foreground interruption becomes a typed cancellation."""
        ports = WaitPorts()

        def interrupt(_seconds: float) -> bool:
            """Model a host or console interruption at the notification boundary."""
            raise KeyboardInterrupt

        result = GlobalReviewerWait(
            rescan_candidates=ports.rescan,
            wait_for_notification=interrupt,
            fallback_poll=ports.fallback_poll,
            poll_interval_seconds=1.0,
        ).wait()

        assert result.outcome is GlobalWaitOutcome.CANCELLED
        assert result.candidate is None
        assert result.candidates == ()
        assert ports.fallbacks == 0

    @pytest.mark.parametrize("interval", [0.0, -1.0])
    def test_non_positive_interval_is_rejected(self, interval: float) -> None:
        """The wait rejects intervals that could otherwise form a busy loop."""
        ports = WaitPorts()

        with pytest.raises(ReviewExchangeError, match="poll interval must be positive"):
            GlobalReviewerWait(
                rescan_candidates=ports.rescan,
                wait_for_notification=ports.wait_for_notification,
                fallback_poll=ports.fallback_poll,
                poll_interval_seconds=interval,
            )

    def test_negative_quiet_interval_limit_is_rejected(self) -> None:
        """The optional test seam cannot make the quiet wait unbounded by mistake."""
        ports = WaitPorts()
        waiter = GlobalReviewerWait(
            rescan_candidates=ports.rescan,
            wait_for_notification=ports.wait_for_notification,
            fallback_poll=ports.fallback_poll,
            poll_interval_seconds=1.0,
        )

        with pytest.raises(ReviewExchangeError, match="maximum quiet intervals"):
            waiter.wait(max_quiet_intervals=-1)

    def test_quiet_rescans_back_off_to_the_fallback_cap(self) -> None:
        """Without hints, rescans come after one, two and four intervals, then every cap."""
        ports = WaitPorts()

        result = GlobalReviewerWait(
            rescan_candidates=ports.rescan,
            wait_for_notification=ports.wait_for_notification,
            fallback_poll=ports.fallback_poll,
            poll_interval_seconds=1.0,
            fallback_rescan_intervals=BACKOFF_CAP,
        ).wait(max_quiet_intervals=BACKOFF_QUIET_INTERVALS)

        assert result.outcome is GlobalWaitOutcome.IDLE
        assert ports.rescan_waits == [0, 1, 3, 7, 11]
        assert ports.waits == ports.fallbacks == BACKOFF_QUIET_INTERVALS

    def test_hint_rescans_at_once_and_resets_the_backoff(self) -> None:
        """A hint rescans now, and the quiet interval after it rescans again."""
        ports = WaitPorts(notifications=[False, False, False, True, False, False])

        result = GlobalReviewerWait(
            rescan_candidates=ports.rescan,
            wait_for_notification=ports.wait_for_notification,
            fallback_poll=ports.fallback_poll,
            poll_interval_seconds=1.0,
            fallback_rescan_intervals=RESET_CAP,
        ).wait(max_quiet_intervals=RESET_QUIET_INTERVALS)

        assert result.outcome is GlobalWaitOutcome.IDLE
        assert ports.rescan_waits == [0, 1, 3, 4, 5]
        assert ports.fallbacks == RESET_FALLBACKS

    def test_hinted_rescan_that_finds_nothing_retries_next_interval(self) -> None:
        """A request still locked by its publisher at the hinted rescan is found one interval later."""
        ports = WaitPorts(batches=[(), (), ("request",)], notifications=[True])

        result = GlobalReviewerWait(
            rescan_candidates=ports.rescan,
            wait_for_notification=ports.wait_for_notification,
            fallback_poll=ports.fallback_poll,
            poll_interval_seconds=1.0,
            fallback_rescan_intervals=PRODUCTION_CAP,
        ).wait()

        assert result.outcome is GlobalWaitOutcome.FOUND
        assert result.candidate == "request"
        assert ports.rescan_waits == [0, 1, 2]
        assert ports.fallbacks == 1

    def test_non_positive_fallback_rescan_intervals_are_rejected(self) -> None:
        """A zero cap would never rescan without a hint, so it is refused."""
        ports = WaitPorts()

        with pytest.raises(ReviewExchangeError, match="fallback rescan intervals must be positive"):
            GlobalReviewerWait(
                rescan_candidates=ports.rescan,
                wait_for_notification=ports.wait_for_notification,
                fallback_poll=ports.fallback_poll,
                poll_interval_seconds=1.0,
                fallback_rescan_intervals=0,
            )
