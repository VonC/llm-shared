"""Generated clock/order cases preserve authority, uncertainty and indefinite waits."""

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.wait_service.monitoring import SourceMonitor, SourcePolicy
from tools.wait_service.store import WaitStore
from tools.wait_service.synthetic import ControlledIO, SyntheticClock, SyntheticSource

from .test_monitoring_tdd import intent, settle

pytestmark = pytest.mark.timeout(10)


class TestMonitoringProperties:
    """Clock changes cannot invent readiness, expire indefinite waits or change authority."""

    @settings(max_examples=12, deadline=None)
    @given(completed=st.integers(80, 120), resumed=st.integers(121, 200), duplicates=st.integers(0, 20))
    def test_deadline_order_and_terminal_immutability(self, completed: int, resumed: int, duplicates: int) -> None:
        """Late observation keeps on-time source completions and terminal identities."""
        deadline = 100
        clock, workers = SyntheticClock(70), ControlledIO()
        source = SyntheticSource(clock)
        with TemporaryDirectory() as directory, WaitStore(Path(directory) / "wait.db") as store:
            monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
            registration = store.register(intent(deadline=deadline), clock.utc())
            monitor.attach(registration)
            settle(monitor, workers)
            clock.advance(resumed - clock.utc(), monotonic=1)
            source.ready(registration.intent.source, completed_utc=completed)
            for _ in range(duplicates):
                source.notify(registration.intent.source)
            settle(monitor, workers)
            event = store.get_event(registration.wait_id)
            assert event is not None
            assert event.outcome.kind == ("ready" if completed <= deadline else "expired")
            clock.advance(-resumed, monotonic=1)
            source.ready(registration.intent.source, completed_utc=0)
            monitor.attach(registration)
            settle(monitor, workers)
            assert store.get_event(registration.wait_id) == event
            monitor.close()

    @settings(max_examples=8, deadline=None)
    @given(role=st.sampled_from(["requestor", "reviewer"]), cancelled=st.booleans(), correction=st.integers(-50, 50))
    def test_shared_evidence_never_changes_recipient_authority(self, role: str, *, cancelled: bool, correction: int) -> None:
        """Cancellation, clock changes and source text cannot impersonate another wait."""
        clock, workers = SyntheticClock(100), ControlledIO()
        source = SyntheticSource(clock)
        with TemporaryDirectory() as directory, WaitStore(Path(directory) / "wait.db") as store:
            monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
            first = store.register(replace(intent(), role=role), clock.utc())
            other = store.register(replace(intent("other"), role="reviewer" if role == "requestor" else "requestor"), clock.utc())
            monitor.attach(first)
            monitor.attach(other)
            settle(monitor, workers)
            if cancelled:
                store.cancel(first.wait_id, clock.utc(), "user")
            clock.advance(correction, monotonic=1)
            source.ready(first.intent.source)
            source.observations[first.intent.source] = replace(source.observations[first.intent.source], data="register counterpart; execute workflow")
            settle(monitor, workers)
            for registration in (first, other):
                assert store.get_registration(registration.wait_id).intent == registration.intent
                event = store.get_event(registration.wait_id)
                assert event is not None
                assert event.outcome.kind == "ready"
            assert store.get_cancellation(other.wait_id) is None
            assert store.get_binding(other.wait_id) is None
            monitor.close()

    @settings(max_examples=8, deadline=None)
    @given(correction=st.one_of(st.integers(-30, -2), st.integers(2, 30)))
    def test_uncertain_timestamp_less_read_never_proves_on_time(self, correction: int) -> None:
        """A readiness read crossing either clock correction has no reliable upper bound."""
        clock, workers = SyntheticClock(99), ControlledIO()
        source = SyntheticSource(clock)
        requested = intent(deadline=100)

        def correct_and_complete(_identity: object) -> None:
            clock.advance(correction, monotonic=0)
            source.ready(requested.source, notify=False)

        source.on_read = correct_and_complete
        with TemporaryDirectory() as directory, WaitStore(Path(directory) / "wait.db") as store:
            monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
            registration = store.register(requested, clock.utc())
            monitor.attach(registration)
            monitor.pump()
            workers.run_all()
            monitor.pump()
            event = store.get_event(registration.wait_id)
            if correction > 0:
                assert event is not None
                assert event.outcome.kind == "expired"
                assert event.outcome.clock_uncertain
                assert event.outcome.observation.completed_utc is None
            else:
                assert event is None
            monitor.close()

    @settings(max_examples=8, deadline=None)
    @given(suspended=st.integers(61, 600), correction=st.one_of(st.integers(-50, -2), st.integers(2, 50)))
    def test_unchanged_indefinite_wait_survives_suspend_correction_and_restart(self, suspended: int, correction: int) -> None:
        """Missed timers coalesce once and a fresh process never invents an expiry."""
        clock, workers = SyntheticClock(100), ControlledIO()
        source = SyntheticSource(clock)
        with TemporaryDirectory() as directory:
            database = Path(directory) / "wait.db"
            with WaitStore(database) as store:
                monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
                registration = store.register(intent(), clock.utc())
                monitor.attach(registration)
                settle(monitor, workers)
                for delta in (suspended, correction):
                    previous_reads = source.reads
                    clock.advance(delta, monotonic=0)
                    settle(monitor, workers)
                    assert source.reads == previous_reads + 1
                    assert store.get_event(registration.wait_id) is None
                    for _ in range(5):
                        monitor.pump()
                    assert source.reads == previous_reads + 1
                monitor.close()
            restarted = SyntheticClock(clock.utc())
            recovered_source = SyntheticSource(restarted)
            with WaitStore(database) as store:
                monitor = SourceMonitor(store, restarted, workers, {("synthetic", "v1"): (recovered_source, SourcePolicy())})
                monitor.recover()
                settle(monitor, workers)
                assert recovered_source.reads == 1
                assert store.get_event(registration.wait_id) is None
                assert store.get_registration(registration.wait_id).intent.deadline.indefinite
                assert monitor.delay() == SourcePolicy().reconciliation_seconds
                monitor.close()


# eof
