"""Coalesced source reconciliation, durable recovery and absolute UTC decisions.

Only the scheduler owner touches SQLite. Notification callbacks mark exact
sources dirty, and bounded ordinary workers return authoritative evidence.
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from threading import Lock
from typing import TYPE_CHECKING

from tools.wait_service.models import (
    Observation,
    Outcome,
    Registration,
    SourceIdentity,
    WaitError,
    require,
)
from tools.wait_service.work import CLOCK_TOLERANCE, WorkQueue, WorkResult

if TYPE_CHECKING:
    from tools.wait_service.ports import ClockPort, IOPort, SourcePort
    from tools.wait_service.store import WaitStore


@dataclass(frozen=True)
class SourcePolicy:
    """Versioned bounds declared before admitting a source kind's first wait."""

    version: str = "v1"
    notifications: bool = True
    reconciliation_seconds: float = 30.0
    recovery_seconds: float = 60.0
    observation_seconds: float = 5.0

    def validate(self) -> None:
        """Reject absent policies and nonfinite or unbounded observation intervals."""
        values = (self.reconciliation_seconds, self.recovery_seconds, self.observation_seconds)
        require(bool(self.version) and all(math.isfinite(value) and value > 0 for value in values), "finite positive source policy required")


@dataclass
class _Watch:
    source: SourceIdentity
    port: SourcePort
    policy: SourcePolicy
    waits: dict[str, Registration] = field(default_factory=dict[str, Registration])
    unsubscribe: Callable[[], None] | None = None
    observation: Observation | None = None
    reading: bool = False
    closed: bool = False
    serial: int = 0
    again: bool = False
    callbacks: dict[str, Callable[[], None]] = field(default_factory=dict[str, Callable[[], None]])


class SourceMonitor:
    """One source schedule with per-wait deadline outcomes and no workflow authority."""

    def __init__(self, store: WaitStore, clock: ClockPort, workers: IOPort, sources: dict[tuple[str, str], tuple[SourcePort, SourcePolicy]]) -> None:
        """Resolve only registered kind/version pairs; retain no repository search path."""
        for (_, version), (_, policy) in sources.items():
            policy.validate()
            require(version == policy.version, "source policy version mismatch")
        self.store, self.clock = store, clock
        self.work = WorkQueue(clock, workers)
        self._sources = dict(sources)
        self._watches: dict[SourceIdentity, _Watch] = {}
        self._dirty: set[SourceIdentity] = set()
        self._lock = Lock()
        self._timers: list[tuple[float, int, SourceIdentity]] = []
        self._serial = 0
        self._last_utc, self._last_mono = clock.utc(), clock.monotonic()
        self._closed = False

    def policy(self, source: SourceIdentity) -> SourcePolicy:
        """Validate the exact applied policy before durable preparation is inserted."""
        entry = self._sources.get((source.kind, source.policy_version))
        if entry is None:
            code = "source-policy-unavailable"
            raise WaitError(code, source.kind)
        return entry[1]

    def attach(self, registration: Registration, on_observed: Callable[[], None] | None = None) -> None:
        """Share one watch and retain every subscriber's own unchanged intent."""
        require(not self._closed, "monitor closed")
        source = registration.intent.source
        policy = self.policy(source)
        if self.store.get_event(registration.wait_id) is not None:
            if on_observed is not None:
                on_observed()
            return
        watch = self._watches.get(source)
        if watch is None:
            watch = _Watch(source, self._sources[source.kind, source.policy_version][0], policy)
            watch.observation = self.store.get_observation(registration.wait_id)
            self._watches[source] = watch
        if on_observed is not None:
            watch.callbacks[registration.wait_id] = on_observed
            self.dirty(source)
        if registration.wait_id not in watch.waits:
            watch.waits[registration.wait_id] = registration
            self.dirty(source)

    def recover(self) -> None:
        """Rebuild only unresolved durable waits; process monotonic epochs start anew."""
        for registration in self.store.recover_registrations():
            self.attach(registration)

    def dirty(self, source: SourceIdentity) -> None:
        """Coalesce hints without reading files, granting authority or waking a model."""
        with self._lock:
            if not self._closed:
                self._dirty.add(source)
                self.work.wake.set()

    def resume(self) -> None:
        """Coalesce missed timers after suspension, reconnect or UTC discontinuity."""
        for source in self._watches:
            self.dirty(source)

    def _read(self, watch: _Watch) -> Observation:
        if watch.unsubscribe is None and watch.policy.notifications:
            watch.unsubscribe = watch.port.subscribe(watch.source, lambda: self.dirty(watch.source))
        if watch.closed:
            self._unsubscribe(watch)
            code = "monitor-closed"
            raise WaitError(code)
        observation = watch.port.read(watch.source)
        observation.validate()
        if observation.generation != watch.source.generation:
            return Observation("invalid", watch.source.generation, self.clock.utc(), data="source-generation-mismatch")
        return observation

    @staticmethod
    def _unsubscribe(watch: _Watch) -> None:
        if watch.unsubscribe is not None:
            unsubscribe, watch.unsubscribe = watch.unsubscribe, None
            unsubscribe()

    def _received(self, watch: _Watch, result: WorkResult) -> None:
        if watch.closed:
            return
        watch.reading = False
        value = result.value
        if not isinstance(value, Observation):
            value = Observation("unknown", watch.source.generation, result.observed_utc, data=value.code if isinstance(value, WaitError) else "invalid-source-result")
        value = replace(value, observed_utc=result.observed_utc, access_loss_utc=None)
        if value.state == "unknown":
            previous = watch.observation
            loss = previous.access_loss_utc if previous is not None else None
            value = replace(value, access_loss_utc=result.observed_utc if loss is None else loss)
        watch.observation = value
        first = next(iter(watch.waits))
        self.store.observe(first, value)
        self._decide(watch, value, uncertain=result.uncertain)
        callbacks, watch.callbacks = watch.callbacks, {}
        for callback in callbacks.values():
            callback()
        if watch.again:
            watch.again = False
            self.dirty(watch.source)
        self._schedule(watch)

    def _decide(self, watch: _Watch, observation: Observation, *, uncertain: bool) -> None:
        now = self.clock.utc()
        for wait_id, registration in tuple(watch.waits.items()):
            decision = self._outcome(registration, observation, now, watch.policy, uncertain=uncertain)
            if decision is not None:
                self.store.record_outcome(wait_id, decision, now)
                del watch.waits[wait_id]

    @staticmethod
    def _outcome(registration: Registration, observation: Observation, now: float, policy: SourcePolicy, *, uncertain: bool) -> Outcome | None:
        deadline = registration.intent.deadline.deadline_utc
        if observation.state == "invalid":
            return Outcome("monitoring-failure", observation, "invalid-source-identity", uncertain)
        if observation.state == "unknown":
            if observation.access_loss_utc is not None and now - observation.access_loss_utc >= policy.recovery_seconds:
                return Outcome("monitoring-failure", observation, "access-recovery-exhausted", uncertain)
            return None
        if observation.state == "ready":
            ready = SourceMonitor._ready(observation, deadline, uncertain=uncertain)
            if ready is not None:
                return ready
        if deadline is not None and now >= deadline:
            return Outcome("expired", observation, "deadline-without-on-time-evidence", uncertain)
        return None

    @staticmethod
    def _ready(observation: Observation, deadline: float | None, *, uncertain: bool) -> Outcome | None:
        if deadline is None:
            return Outcome("ready", observation, "indefinite", uncertain)
        if observation.completed_utc is not None and observation.completed_utc <= deadline:
            return Outcome("ready", observation, "source-completed-on-time", uncertain)
        if observation.completed_utc is None and not uncertain and observation.observed_utc <= deadline:
            return Outcome("ready", observation, "authoritative-on-time-upper-bound", clock_uncertain=False)
        return None

    def _interval(self, watch: _Watch) -> float:
        now = self.clock.utc()
        delay = watch.policy.reconciliation_seconds
        for registration in watch.waits.values():
            deadline = registration.intent.deadline.deadline_utc
            if deadline is not None and deadline > now:
                delay = min(delay, deadline - now)
        if watch.observation is not None and watch.observation.access_loss_utc is not None:
            delay = min(delay, max(0.0, watch.observation.access_loss_utc + watch.policy.recovery_seconds - now))
        return delay

    def _schedule(self, watch: _Watch) -> None:
        if not watch.waits:
            watch.closed = True
            self._unsubscribe(watch)
            self._watches.pop(watch.source, None)
            return
        delay = self._interval(watch)
        self._serial += 1
        watch.serial = self._serial
        heapq.heappush(self._timers, (self.clock.monotonic() + delay, watch.serial, watch.source))
        # Hints may bring a read forward many times. Compact obsolete timers
        # amortized over those replacements, bounding storage by active sources.
        if len(self._timers) > 2 * len(self._watches) + 32:
            self._timers = [timer for timer in self._timers if timer[2] in self._watches and self._watches[timer[2]].serial == timer[1]]
            heapq.heapify(self._timers)

    def pump(self) -> None:
        """Drain one scheduler turn; reads scale with dirty/due sources, not all waits."""
        if self._closed:
            return
        self.work.wake.clear()
        now, mono = self.clock.utc(), self.clock.monotonic()
        if abs((now - self._last_utc) - (mono - self._last_mono)) > CLOCK_TOLERANCE:
            self.work.discontinuity()
            self.resume()
        self._last_utc, self._last_mono = now, mono
        self.work.pump()
        while self._timers and self._timers[0][0] <= mono:
            _, serial, source = heapq.heappop(self._timers)
            watch = self._watches.get(source)
            if watch is not None and watch.serial == serial:
                self.dirty(source)
        with self._lock:
            dirty, self._dirty = self._dirty, set()
        for source in dirty:
            self._poll(source)
        self.work.pump()

    def _poll(self, source: SourceIdentity) -> None:
        watch = self._watches.get(source)
        if watch is None:
            return
        if watch.reading:
            watch.again = True
            # A pending read can still supply on-time completion evidence.
            # Only the established access-loss bound may finish before it.
            if watch.observation is not None and watch.observation.state == "unknown":
                self._decide(watch, watch.observation, uncertain=True)
        else:
            watch.reading = True
            self.work.submit(f"source:{source!r}", lambda: self._read(watch), lambda result: self._received(watch, result), watch.policy.observation_seconds)
        self._schedule(watch)

    def delay(self) -> float | None:
        """Expose the next timer for a single event-driven owner wait."""
        if self._closed:
            return None
        while self._timers:
            _, serial, source = self._timers[0]
            if source in self._watches and self._watches[source].serial == serial:
                break
            heapq.heappop(self._timers)
        delays = [max(0.0, self._timers[0][0] - self.clock.monotonic())] if self._timers else []
        work_delay = self.work.delay()
        if work_delay is not None:
            delays.append(work_delay)
        return min(delays) if delays else None

    def close(self) -> None:
        """Fence callbacks and release shared subscriptions without deleting outcomes."""
        self._closed = True
        self.work.close()
        for watch in self._watches.values():
            watch.closed = True
            self._unsubscribe(watch)
        self._watches.clear()
        self._timers.clear()
        with self._lock:
            self._dirty.clear()


# eof
