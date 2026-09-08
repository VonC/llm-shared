"""Quiet foreground waiting for any reviewer-owned review request.

Step 5 supplies one identity-free, script-managed wait that treats notification
events as hints, rescans authoritatively, falls back to bounded polling, and
returns one typed result. It keeps no durable waiter state and writes no
progress: its caller alone renders the final machine result.
"""


from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Callable


class GlobalWaitOutcome(StrEnum):
    """Terminal and deterministic-test outcomes for a global reviewer wait."""

    FOUND = "found"
    AMBIGUOUS = "ambiguous"
    CANCELLED = "cancelled"
    IDLE = "idle"


@dataclass(frozen=True)
class GlobalWaitResult:
    """One silent global-wait result with optional selected request evidence."""

    outcome: GlobalWaitOutcome
    candidate: object | None = None
    candidates: tuple[object, ...] = ()
    diagnostic: str | None = None


class GlobalReviewerWait:
    """Wait for one request through injected notification and claim boundaries."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        rescan_candidates: Callable[[], tuple[object, ...]],
        wait_for_notification: Callable[[float], bool],
        fallback_poll: Callable[[], None],
        claim_candidate: Callable[[object], bool] | None = None,
        monotonic_clock: Callable[[], float] | None = None,
        poll_interval_seconds: float,
    ) -> None:
        """Bind pure wait ports while rejecting a busy-loop interval."""
        if not math.isfinite(poll_interval_seconds) or poll_interval_seconds <= 0:
            message = "poll interval must be positive"
            raise ReviewExchangeError(message)
        self._rescan_candidates = rescan_candidates
        self._wait_for_notification = wait_for_notification
        self._fallback_poll = fallback_poll
        self._claim_candidate = claim_candidate
        self._monotonic_clock = monotonic_clock
        self._poll_interval_seconds = poll_interval_seconds

    def wait(self, *, max_quiet_intervals: int | None = None) -> GlobalWaitResult:
        """Block quietly until a request, ambiguity, cancellation, or test limit."""
        if max_quiet_intervals is not None and max_quiet_intervals < 0:
            message = "maximum quiet intervals cannot be negative"
            raise ReviewExchangeError(message)
        quiet_intervals = 0
        try:
            while True:
                result = self._rescan_result()
                if result is not None:
                    return result
                if max_quiet_intervals is not None and quiet_intervals >= max_quiet_intervals:
                    return GlobalWaitResult(GlobalWaitOutcome.IDLE)
                notified = self._wait_for_notification(self._poll_interval_seconds)
                if not notified:
                    self._fallback_poll()
                quiet_intervals += 1
        except KeyboardInterrupt:
            return GlobalWaitResult(
                GlobalWaitOutcome.CANCELLED,
                diagnostic="foreground wait was cancelled",
            )

    def _rescan_result(self) -> GlobalWaitResult | None:
        """Convert one authoritative candidate set into a result or another wait."""
        candidates = self._rescan_candidates()
        if len(candidates) > 1:
            return GlobalWaitResult(
                GlobalWaitOutcome.AMBIGUOUS,
                candidates=candidates,
                diagnostic="multiple review requests require selection",
            )
        if not candidates:
            return None
        candidate = candidates[0]
        if self._claim_candidate is not None and not self._claim_candidate(candidate):
            return None
        return GlobalWaitResult(
            GlobalWaitOutcome.FOUND,
            candidate=candidate,
            candidates=(candidate,),
        )


__all__ = [
    "GlobalReviewerWait",
    "GlobalWaitOutcome",
    "GlobalWaitResult",
]


# eof
