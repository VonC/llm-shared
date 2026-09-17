"""Bound admitted I/O and return its results to the single persistence writer.

A timed-out operation keeps its worker slot until it really returns. Its late
result cannot overwrite the timeout, and no replacement thread is created.
"""

from __future__ import annotations

import heapq
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from queue import SimpleQueue
from threading import BoundedSemaphore, Event
from typing import TYPE_CHECKING

from tools.wait_service.models import HostBinding, Observation, WaitError, require

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.wait_service.ports import ClockPort, IOPort

type WorkValue = Observation | HostBinding
CLOCK_TOLERANCE = 0.001


@dataclass(frozen=True)
class WorkResult:
    """Completed I/O and its clock span, including explicit adapter failures."""

    value: WorkValue | WaitError
    observed_utc: float
    uncertain: bool
    duration: float = 0.0


@dataclass
class _Job:
    key: str
    operation: Callable[[], WorkValue]
    finish: Callable[[WorkResult], None]
    budget: float
    started_utc: float = 0.0
    started_mono: float = 0.0
    expired: bool = False
    uncertain: bool = False


class BoundedIO:
    """A fixed ordinary worker pool without an unbounded executor backlog."""

    def __init__(self, capacity: int = 4) -> None:
        """Reserve capacity before submission, including work that exceeds its budget."""
        require(capacity > 0, "positive worker capacity required")
        self._slots = BoundedSemaphore(capacity)
        self._executor = ThreadPoolExecutor(max_workers=capacity, thread_name_prefix="wait-source")
        self._closed = False

    def submit(self, operation: Callable[[], None]) -> bool:
        """Reject saturated work without allocating a queued future or worker."""
        if self._closed or not self._slots.acquire(blocking=False):
            return False

        def run() -> None:
            try:
                operation()
            finally:
                self._slots.release()

        self._executor.submit(run)
        return True

    def close(self) -> None:
        """Stop accepting work; existing bounded I/O retains its own handles."""
        self._closed = True
        self._executor.shutdown(wait=False)


class WorkQueue:
    """One owner drains results and timeouts; workers never touch the store."""

    def __init__(self, clock: ClockPort, workers: IOPort) -> None:
        """Keep pending requests keyed, so identical retries cannot duplicate I/O."""
        self.clock, self.workers = clock, workers
        self.wake = Event()
        self._pending: dict[str, _Job] = {}
        self._active: dict[str, _Job] = {}
        self._results: SimpleQueue[tuple[_Job, WorkResult]] = SimpleQueue()
        self._timers: list[tuple[float, int, _Job]] = []
        self._serial = 0
        self._closed = False

    def submit(self, key: str, operation: Callable[[], WorkValue], finish: Callable[[WorkResult], None], budget: float) -> None:
        """Coalesce keyed submissions; persistence acknowledgement belongs to finish."""
        require(math.isfinite(budget) and budget > 0, "finite positive I/O budget required")
        if not self._closed and key not in self._pending and key not in self._active:
            job = _Job(key, operation, finish, budget, self.clock.utc(), self.clock.monotonic())
            self._pending[key] = job
            self._serial += 1
            heapq.heappush(self._timers, (job.started_mono + budget, self._serial, job))
            if len(self._timers) > 2 * (len(self._pending) + len(self._active)) + 32:
                self._timers = [timer for timer in self._timers if not timer[2].expired]
                heapq.heapify(self._timers)
            self.wake.set()

    def discontinuity(self) -> None:
        """Fence timestamp-less upper bounds across a detected UTC correction."""
        for job in self._active.values():
            job.uncertain = True

    def delay(self) -> float | None:
        """Return the next I/O budget, allowing the owner to block between events."""
        while self._timers and self._timers[0][2].expired:
            heapq.heappop(self._timers)
        return max(0.0, self._timers[0][0] - self.clock.monotonic()) if self._timers else None

    def _execute(self, job: _Job) -> None:
        value: WorkValue | WaitError
        try:
            value = job.operation()
        except (OSError, WaitError) as error:
            value = error if isinstance(error, WaitError) else WaitError("access-unavailable", str(error))
        now, mono = self.clock.utc(), self.clock.monotonic()
        uncertain = job.uncertain or abs((now - job.started_utc) - (mono - job.started_mono)) > CLOCK_TOLERANCE
        self._results.put((job, WorkResult(value, now, uncertain, mono - job.started_mono)))
        self.wake.set()

    def _drain(self) -> None:
        while not self._results.empty():
            job, result = self._results.get()
            self._active.pop(job.key, None)
            if not job.expired and not self._closed:
                job.expired = True
                if result.duration > job.budget:
                    # Measure the operation itself, not a delayed owner's drain.
                    result = WorkResult(WaitError("observation-timeout"), result.observed_utc, uncertain=True)
                job.finish(result)

    def _expire(self) -> None:
        while self._timers and self._timers[0][0] <= self.clock.monotonic():
            _, _, job = heapq.heappop(self._timers)
            if not job.expired:
                job.expired = True
                self._pending.pop(job.key, None)
                job.finish(WorkResult(WaitError("observation-timeout"), self.clock.utc(), uncertain=True))

    def pump(self) -> None:
        """Apply returned work before deadlines, then admit only available capacity."""
        self._drain()
        if self._closed:
            return
        self._expire()
        while self._pending and not self._closed:
            key = next(iter(self._pending))
            job = self._pending[key]
            if not self.workers.submit(lambda job=job: self._execute(job)):
                break
            self._active[key] = self._pending.pop(key)

    def close(self) -> None:
        """Discard undispatched jobs and fence late callbacks after service shutdown."""
        self._closed = True
        self._pending.clear()
        self._timers.clear()


# eof
