"""Verify the complete CPU window and unchanged hard lifecycle thresholds.

Synthetic clock samples exercise accounting directly; no workload is moved
outside its test and no real process is created.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from tests import simulation_policy as policy

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.mark.parametrize("setup_fails", [False, True])
@pytest.mark.parametrize(("cpu", "wall", "outcome"), [
    (0.1, 1.0, "passed"),
    (0.125, 0.05, "failed"),
    (0.0625, 1.125, "failed"),
])
def test_one_cpu_window_keeps_initialization_hooks_cleanup_and_limits(
    cpu: float, wall: float, outcome: str, *, setup_fails: bool,
) -> None:
    """Exactly two reads span setup through cleanup, even after failed setup."""
    current = 0.0
    readings: list[float] = []

    def clock() -> float:
        readings.append(current)
        return current

    limits = {"test_lifecycle_limit": "0.1", "test_lifecycle_wall_limit": "1.0"}
    item = cast("pytest.Item", SimpleNamespace(
        stash=pytest.Stash(), config=SimpleNamespace(getini=limits.__getitem__),
        nodeid="accounting-boundary",
    ))
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(policy, "process_time", clock)
        setup = policy.pytest_runtest_setup(item)
        next(setup)
        assert readings == [0.0]
        current = cpu / 4
        _finish_setup(setup, fails=setup_fails)
        # No call/report hook resets the start or samples intermediate CPU.
        assert policy._CPU not in item.stash
        for phase in ("setup", "call"):
            current += cpu / 4
            phase_report = pytest.TestReport(
                nodeid=item.nodeid, location=("boundary", 0, "boundary"), keywords={},
                outcome="passed", longrepr=None, when=phase, duration=wall / 4,
            )
            _deliver_report(item, phase_report)
            assert readings == [0.0]
        teardown = policy.pytest_runtest_teardown(item)
        next(teardown)
        assert readings == [0.0]
        current = cpu
        with pytest.raises(StopIteration):
            next(teardown)
        assert readings == [0.0, cpu]
    _assert_final_report(item, cpu, wall, outcome)


def _assert_final_report(item: pytest.Item, cpu: float, wall: float, outcome: str) -> None:
    """Verify both reported clocks and the unchanged pass/fail thresholds."""
    assert item.stash[policy._CPU] == cpu
    report = pytest.TestReport(
        nodeid=item.nodeid, location=("boundary", 0, "boundary"), keywords={},
        outcome="passed", longrepr=None, when="teardown", duration=wall / 2,
    )
    _deliver_report(item, report)
    assert report.outcome == outcome
    assert dict(report.user_properties)["test_lifecycle_cpu_seconds"] == cpu
    assert dict(report.user_properties)["test_lifecycle_seconds"] == wall


def _finish_setup(setup: Generator[None, object, object], *, fails: bool) -> None:
    """Complete the hook with either a successful or failed fixture setup."""
    if fails:
        message = "setup failed"
        with pytest.raises(RuntimeError, match=message):
            setup.throw(RuntimeError(message))
    else:
        with pytest.raises(StopIteration):
            next(setup)


def _deliver_report(item: pytest.Item, report: pytest.TestReport) -> None:
    """Send a phase report through the actual lifecycle accounting hook."""
    hook = policy.pytest_runtest_makereport(item, cast("pytest.CallInfo[None]", None))
    next(hook)
    with pytest.raises(StopIteration):
        hook.send(report)


# eof
