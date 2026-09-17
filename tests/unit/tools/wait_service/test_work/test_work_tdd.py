"""Verify bounded worker capacity, timeout fencing and owner-only callbacks."""

from __future__ import annotations

from threading import Event

import pytest

from tools.wait_service.models import Observation, WaitError
from tools.wait_service.synthetic import ControlledIO, SyntheticClock
from tools.wait_service.work import BoundedIO, WorkQueue, WorkResult

pytestmark = pytest.mark.timeout(10)


def observation() -> Observation:
    """Use a nonterminal value to keep worker tests independent of deadline policy."""
    return Observation("pending", "generation", 0)


def test_fixed_pool_refuses_overflow_and_shutdown() -> None:
    """An occupied slot cannot create a queued future or replacement worker."""
    entered, release, completed = Event(), Event(), Event()
    workers = BoundedIO(1)

    def block() -> None:
        entered.set()
        release.wait()
        completed.set()

    try:
        assert workers.submit(block)
        assert entered.wait(2)
        assert not workers.submit(completed.set)
    finally:
        release.set()
        workers.close()
    assert completed.wait(2)
    assert not workers.submit(completed.set)


def test_results_are_owner_drained_and_delayed_drain_is_not_timeout() -> None:
    """Successful on-budget work remains valid when the owner resumes much later."""
    clock, workers = SyntheticClock(), ControlledIO()
    work = WorkQueue(clock, workers)
    results: list[WorkResult] = []
    work.submit("one", observation, results.append, 5)
    work.submit("one", observation, results.append, 5)
    work.pump()
    workers.run_all()
    assert not results
    clock.advance(100)
    work.pump()
    assert [result.value for result in results] == [observation()]
    assert work.delay() is None
    work.close()


def test_timeout_keeps_capacity_and_discards_late_result() -> None:
    """A timed-out active job is fenced while queued jobs also get bounded answers."""
    clock, workers = SyntheticClock(), ControlledIO(1)
    work = WorkQueue(clock, workers)
    results: list[WorkResult] = []
    work.submit("one", observation, results.append, 5)
    work.submit("two", observation, results.append, 5)
    work.pump()
    clock.advance(5)
    work.pump()
    expected_results = 2
    assert len(results) == expected_results
    assert all(isinstance(result.value, WaitError) and result.value.code == "observation-timeout" for result in results)
    assert workers.maximum == 1
    assert work.delay() is None
    work.submit("one", observation, results.append, 5)
    workers.run_all()
    work.pump()
    assert len(results) == expected_results
    work.submit("one", observation, results.append, 5)
    work.pump()
    workers.run_all()
    work.pump()
    assert results[-1].value == observation()
    work.close()


def test_completed_over_budget_operation_is_not_accepted() -> None:
    """A result arriving before the owner's next pump still obeys its I/O budget."""
    clock, workers = SyntheticClock(), ControlledIO()
    work = WorkQueue(clock, workers)
    results: list[WorkResult] = []

    def slow() -> Observation:
        clock.advance(6)
        return observation()

    work.submit("one", slow, results.append, 5)
    work.pump()
    workers.run_all()
    work.pump()
    assert isinstance(results[0].value, WaitError)
    assert results[0].value.code == "observation-timeout"
    work.close()


def test_discontinuity_is_retained_even_when_clock_returns_to_origin() -> None:
    """A known intermediate correction invalidates an apparently normal final span."""
    clock, workers = SyntheticClock(), ControlledIO()
    work = WorkQueue(clock, workers)
    results: list[WorkResult] = []
    work.submit("one", observation, results.append, 5)
    work.pump()
    work.discontinuity()
    workers.run_all()
    work.pump()
    assert results[0].uncertain
    work.close()


def test_close_fences_active_and_pending_callbacks() -> None:
    """Shutdown cannot write results back into the already closed owner's store."""
    clock, workers = SyntheticClock(), ControlledIO(1)
    work = WorkQueue(clock, workers)
    results: list[WorkResult] = []
    work.submit("active", observation, results.append, 5)
    work.submit("pending", observation, results.append, 5)
    work.pump()
    work.close()
    work.submit("closed", observation, results.append, 5)
    workers.run_all()
    work.pump()
    assert not results


@pytest.mark.parametrize("budget", [0, -1, float("nan"), float("inf")])
def test_unbounded_observation_budget_is_rejected(budget: float) -> None:
    """Worker admission needs a finite bound even for indefinite waits."""
    work = WorkQueue(SyntheticClock(), ControlledIO())
    with pytest.raises(WaitError, match="finite positive I/O budget"):
        work.submit("one", observation, lambda _result: None, budget)


def test_completed_jobs_do_not_accumulate_timeout_storage() -> None:
    """A busy source can repeat quickly without retaining every obsolete budget."""
    clock, workers = SyntheticClock(), ControlledIO()
    work = WorkQueue(clock, workers)
    results: list[WorkResult] = []
    for _ in range(100):
        work.submit("source", observation, results.append, 5)
        work.pump()
        workers.run_all()
        work.pump()
    limit = 34
    assert len(work._timers) <= limit
    assert work.delay() is None
    work.close()


# eof
