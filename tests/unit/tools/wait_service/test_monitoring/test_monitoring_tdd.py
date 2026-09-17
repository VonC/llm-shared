"""Exercise shared monitoring with deterministic I/O and independent wait policy."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools.wait_service.models import (
    Continuation,
    DeadlinePolicy,
    Observation,
    Recipient,
    SourceIdentity,
    WaitError,
    WaitIntent,
)
from tools.wait_service.monitoring import SourceMonitor, SourcePolicy
from tools.wait_service.store import WaitStore
from tools.wait_service.synthetic import (
    ControlledIO,
    SyntheticClock,
    SyntheticHost,
    SyntheticSource,
)
from tools.wait_service.work import WorkResult

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.timeout(10)


def intent(key: str = "one", deadline: float | None = None) -> WaitIntent:
    """Supply complete physical identity and an explicit lifetime policy."""
    return WaitIntent(
        key,
        SourceIdentity("synthetic", "repo", "worktree", "home", "run", "round", "generation", "v1"),
        Recipient("synthetic", "v1", key, "profile"),
        DeadlinePolicy(deadline, indefinite=deadline is None),
        Continuation.RESUME,
        "same-session",
        "requestor",
    )


def settle(monitor: SourceMonitor, workers: ControlledIO) -> None:
    """Advance only admitted work; no wall-clock delay or model callback exists."""
    monitor.pump()
    for _ in range(4):
        if not workers.pending:
            break
        workers.run_all()
        monitor.pump()


@pytest.mark.parametrize(("completion", "expected"), [(99.0, "ready"), (100.0, "ready"), (101.0, "expired"), (None, "expired")])
def test_late_read_uses_source_time(tmp_path: Path, completion: float | None, expected: str) -> None:
    """Resume can establish on-time readiness only from comparable source evidence."""
    clock = SyntheticClock(90.0)
    source = SyntheticSource(clock)
    workers = ControlledIO()
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        registration = store.register(intent(deadline=100.0), clock.utc())
        monitor.attach(registration)
        settle(monitor, workers)
        clock.advance(20.0)
        source.ready(registration.intent.source, completed_utc=completion, notify=False)
        monitor.resume()
        settle(monitor, workers)
        event = store.get_event(registration.wait_id)
        assert event is not None
        assert event.outcome.kind == expected
        assert event.outcome.observation.completed_utc == completion
        monitor.close()


def test_shared_watch_keeps_deadlines_and_cancellation_separate(tmp_path: Path) -> None:
    """One read supplies evidence while recipients and cancellation remain per wait."""
    clock, workers = SyntheticClock(90.0), ControlledIO()
    source = SyntheticSource(clock)
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        early = store.register(intent("early", 95.0), clock.utc())
        late = store.register(replace(intent("late", 110.0), role="reviewer"), clock.utc())
        monitor.attach(early)
        monitor.attach(late)
        settle(monitor, workers)
        store.cancel(early.wait_id, clock.utc(), "user")
        clock.advance(10.0)
        source.ready(early.intent.source, completed_utc=100.0)
        for _ in range(100):
            source.notify(early.intent.source)
        settle(monitor, workers)
        assert source.subscriptions == 1
        expected_reads = 2
        assert source.reads == expected_reads
        early_event, late_event = store.get_event(early.wait_id), store.get_event(late.wait_id)
        assert early_event is not None
        assert early_event.outcome.kind == "expired"
        assert late_event is not None
        assert late_event.outcome.kind == "ready"
        assert store.get_cancellation(late.wait_id) is None
        assert store.get_registration(late.wait_id).intent.role == "reviewer"
        monitor.close()


def test_unknown_recovery_interval_survives_restart(tmp_path: Path) -> None:
    """An inaccessible source keeps its first UTC loss epoch across process clocks."""
    clock, workers = SyntheticClock(100.0), ControlledIO()
    source = SyntheticSource(clock)
    source.error = OSError("temporarily inaccessible")
    database = tmp_path / "wait.sqlite3"
    with WaitStore(database) as store:
        registration = store.register(intent(), clock.utc())
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        monitor.attach(registration)
        settle(monitor, workers)
        assert store.get_event(registration.wait_id) is None
        observation = store.get_observation(registration.wait_id)
        assert observation is not None
        assert observation.access_loss_utc == clock.utc()
        monitor.close()
    clock = SyntheticClock(160.0)
    with WaitStore(database) as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        monitor.recover()
        settle(monitor, workers)
        event = store.get_event(registration.wait_id)
        assert event is not None
        assert event.outcome.kind == "monitoring-failure"
        monitor.close()


def test_subscribe_precedes_initial_read(tmp_path: Path) -> None:
    """A completion injected by subscription is retained without a later hint."""
    clock, workers = SyntheticClock(100.0), ControlledIO()
    source = SyntheticSource(clock)
    source.on_subscribe = lambda identity: source.ready(identity, completed_utc=100.0)
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        registration = store.register(intent(), clock.utc())
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        monitor.attach(registration)
        settle(monitor, workers)
        event = store.get_event(registration.wait_id)
        assert event is not None
        assert event.outcome.kind == "ready"
        assert source.trace[:2] == ["subscribe", "read"]
        monitor.close()


@pytest.mark.parametrize("notifications", [True, False])
def test_missing_notification_is_reconciled_at_declared_interval(tmp_path: Path, *, notifications: bool) -> None:
    """Idle turns read nothing; periodic reconciliation covers lost or absent hints."""
    clock, workers = SyntheticClock(), ControlledIO()
    source = SyntheticSource(clock)
    policy = SourcePolicy(notifications=notifications)
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, policy)})
        registration = store.register(intent(), clock.utc())
        monitor.attach(registration)
        settle(monitor, workers)
        assert monitor.delay() == policy.reconciliation_seconds
        source.ready(registration.intent.source, notify=False)
        for _ in range(10):
            monitor.pump()
        assert source.reads == 1
        clock.advance(policy.reconciliation_seconds)
        settle(monitor, workers)
        event = store.get_event(registration.wait_id)
        assert event is not None
        assert event.outcome.kind == "ready"
        assert source.subscriptions == int(notifications)
        assert monitor.delay() is None
        monitor.close()


def test_inflight_read_can_establish_completion_at_deadline(tmp_path: Path) -> None:
    """A deadline hint cannot expire a wait using the previous pending snapshot."""
    clock, workers = SyntheticClock(98), ControlledIO()
    source = SyntheticSource(clock)
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        registration = store.register(intent(deadline=100), clock.utc())
        monitor.attach(registration)
        settle(monitor, workers)
        source.notify(registration.intent.source)
        monitor.pump()
        clock.advance(2)
        monitor.pump()
        assert store.get_event(registration.wait_id) is None
        source.ready(registration.intent.source, completed_utc=100, notify=False)
        settle(monitor, workers)
        event = store.get_event(registration.wait_id)
        assert event is not None
        assert event.outcome.kind == "ready"
        monitor.close()


@pytest.mark.parametrize("startup_failure", [True, False])
def test_observer_and_read_failures_recover_without_resetting_epoch(tmp_path: Path, *, startup_failure: bool) -> None:
    """Subscription and read access failures use one bounded, durable recovery clock."""
    clock, workers = SyntheticClock(100), ControlledIO()
    source = SyntheticSource(clock)
    if startup_failure:
        source.subscribe_error = OSError("observer unavailable")
    else:
        source.error = WaitError("access-unavailable")
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        registration = store.register(intent(deadline=101), clock.utc())
        monitor.attach(registration)
        settle(monitor, workers)
        first = store.get_observation(registration.wait_id)
        assert first is not None
        clock.advance(30)
        settle(monitor, workers)
        second = store.get_observation(registration.wait_id)
        assert second is not None
        assert second.access_loss_utc == first.access_loss_utc
        assert store.get_event(registration.wait_id) is None
        source.subscribe_error, source.error = None, None
        source.ready(registration.intent.source, completed_utc=100)
        monitor.resume()
        settle(monitor, workers)
        event = store.get_event(registration.wait_id)
        assert event is not None
        assert event.outcome.kind == "ready"
        assert event.outcome.observation.access_loss_utc is None
        monitor.close()


def test_blocked_workers_reach_recovery_failure_without_replacement(tmp_path: Path) -> None:
    """Overruns retain their capacity; even queued waits receive bounded failures."""
    clock, workers = SyntheticClock(), ControlledIO(capacity=1)
    source = SyntheticSource(clock)
    policy = SourcePolicy()
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, policy)})
        one = store.register(intent(), clock.utc())
        other = intent("two")
        two = store.register(replace(other, source=replace(other.source, run_id="two")), clock.utc())
        monitor.attach(one)
        monitor.attach(two)
        monitor.pump()
        assert monitor.delay() == policy.observation_seconds
        clock.advance(policy.observation_seconds)
        monitor.pump()
        for registration in (one, two):
            observation = store.get_observation(registration.wait_id)
            assert observation is not None
            assert observation.state == "unknown"
        clock.advance(policy.reconciliation_seconds)
        monitor.pump()
        clock.advance(policy.recovery_seconds)
        monitor.pump()
        for registration in (one, two):
            event = store.get_event(registration.wait_id)
            assert event is not None
            assert event.outcome.kind == "monitoring-failure"
        assert workers.maximum == 1
        settle(monitor, workers)
        monitor.close()


@pytest.mark.parametrize(("delta", "completion", "expected"), [(20, None, "expired"), (-20, None, None), (20, 99, "ready"), (-20, 99, "ready")])
def test_clock_correction_during_read_fences_upper_bounds(tmp_path: Path, delta: float, completion: float | None, expected: str | None) -> None:
    """Clock-spanning reads require comparable source time; later reliable reads work."""
    clock, workers = SyntheticClock(99), ControlledIO()
    source = SyntheticSource(clock)
    requested = intent(deadline=100)

    def correct(identity: SourceIdentity) -> None:
        clock.advance(delta, monotonic=1)
        source.ready(identity, completed_utc=completion, notify=False)

    source.on_read = correct
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        registration = store.register(requested, clock.utc())
        monitor.attach(registration)
        monitor.pump()
        workers.run_all()
        monitor.pump()
        event = store.get_event(registration.wait_id)
        if expected is None:
            assert event is None
            source.on_read = None
            settle(monitor, workers)
            event = store.get_event(registration.wait_id)
            assert event is not None
            assert event.outcome.kind == "ready"
            assert not event.outcome.clock_uncertain
        else:
            assert event is not None
            assert event.outcome.kind == expected
            assert event.outcome.clock_uncertain
        monitor.close()


def test_timer_replacement_is_bounded_and_close_fences_callbacks(tmp_path: Path) -> None:
    """Repeated hints compact stale timer entries and shutdown prevents new work."""
    clock, workers = SyntheticClock(), ControlledIO()
    source = SyntheticSource(clock)
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        registration = store.register(intent(), clock.utc())
        monitor.attach(registration)
        for _ in range(100):
            source.notify(registration.intent.source)
            settle(monitor, workers)
        limit = 34
        assert len(monitor._timers) <= limit
        callback = source.callbacks[registration.intent.source]
        source.notify(registration.intent.source)
        monitor.pump()
        monitor.close()
        callback()
        settle(monitor, workers)
        assert monitor.delay() is None
        assert not source.callbacks
        with pytest.raises(WaitError, match="monitor closed"):
            monitor.attach(registration)


@pytest.mark.parametrize("state", ["invalid", "wrong-generation"])
def test_invalid_identity_never_becomes_ready(tmp_path: Path, state: str) -> None:
    """Malformed identity produces a distinct immutable monitoring failure."""
    clock, workers = SyntheticClock(), ControlledIO()
    source = SyntheticSource(clock)
    requested = intent()
    source.observations[requested.source] = Observation("invalid" if state == "invalid" else "ready", "other" if state == "wrong-generation" else requested.source.generation, clock.utc())
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        registration = store.register(requested, clock.utc())
        monitor.attach(registration)
        settle(monitor, workers)
        event = store.get_event(registration.wait_id)
        assert event is not None
        assert event.outcome.kind == "monitoring-failure"
        monitor.close()


@pytest.mark.parametrize("seconds", [0, -1, float("inf"), float("nan")])
def test_policy_requires_finite_positive_bounds(seconds: float) -> None:
    """An indefinite wait never permits an unbounded observation or recovery call."""
    with pytest.raises(WaitError, match="finite positive"):
        SourcePolicy(observation_seconds=seconds).validate()


def test_misdirected_worker_result_is_unknown_and_closed_watch_is_fenced(tmp_path: Path) -> None:
    """Source-side handoff never treats host-route evidence as source readiness."""
    clock, workers = SyntheticClock(), ControlledIO()
    source = SyntheticSource(clock)
    with WaitStore(tmp_path / "wait.db") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        registration = store.register(intent(), clock.utc())
        monitor.attach(registration)
        watch = monitor._watches[registration.intent.source]
        result = WorkResult(SyntheticHost().arm(registration.intent.recipient), clock.utc(), uncertain=False)
        monitor._received(watch, result)
        observation = store.get_observation(registration.wait_id)
        assert observation is not None
        assert observation.state == "unknown"
        assert observation.data == "invalid-source-result"
        monitor.close()
        monitor._received(watch, result)
        assert store.get_observation(registration.wait_id) == observation


# eof
