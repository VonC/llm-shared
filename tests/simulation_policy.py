"""Enforce process-free tests and a complete per-test lifecycle budget.

The audit hook observes actual process creation, so tests may still replace
subprocess APIs with explicit dependency observations. It covers setup and
teardown, including shared fixtures, and leaves pytest worker startup alone.

Fix (CPU stability band, user decision of 2026-11-02): each process loads one
``LifecycleGate`` at configure time from ``tests/lifecycle_cpu_record.py``. The
CPU limit of a lifecycle is the gate's per-test limit: the ceiling, or the band
top for a test this checkout already proved under the ceiling. The wall limit
stays strict. Each teardown report also carries the limit it was judged by and
whether the lifecycle was measured (its call passed and nothing else failed).
The controller alone collects those reports and updates the record once.
Every limit stays a project setting: the four ``test_lifecycle_*`` ini keys
below give defaults that ``pyproject.toml`` overrides, or ``-o`` for one run.
A value that would switch the gate off is refused as a usage error.
"""

from __future__ import annotations

import sys
from time import process_time
from typing import TYPE_CHECKING

import pytest

from tests.lifecycle_cpu_record import BandCollector, LifecycleGate, record_key

if TYPE_CHECKING:
    from collections.abc import Generator

_ACTIVE: list[str] = []
_DURATIONS = pytest.StashKey[float]()
_CPU = pytest.StashKey[float]()
_CPU_START = pytest.StashKey[float]()
_FAILED = pytest.StashKey[bool]()
_CALL_PASSED = pytest.StashKey[bool]()
_GATE = pytest.StashKey[LifecycleGate]()
_PROCESS_EVENTS = frozenset({
    "subprocess.Popen", "_winapi.CreateProcess", "os.system", "os.posix_spawn",
    "os.spawn", "os.fork", "os.forkpty", "os.startfile", "os.exec",
})


def reject_process(event: str, _arguments: tuple[object, ...]) -> None:
    """Reject real process creation while a test or its fixtures are running."""
    if _ACTIVE and event in _PROCESS_EVENTS:
        message = f"{_ACTIVE[-1]} attempted {event}; inject dependency facts or call Python directly"
        raise AssertionError(message)


sys.addaudithook(reject_process)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Declare the lifecycle limits and the CPU band as visible project configuration."""
    parser.addini("test_lifecycle_limit", "Maximum setup-through-teardown CPU seconds", default="0.1")
    parser.addini("test_lifecycle_wall_limit", "Maximum setup + call + teardown wall seconds", default="1.0")
    parser.addini("test_lifecycle_cpu_band_factor", "A proven test passes up to this multiple of the CPU limit", default="2.5")
    parser.addini("test_lifecycle_cpu_drift_runs", "Consecutive runs above the CPU limit that cost a test its proof", default="3")


def pytest_configure(config: pytest.Config) -> None:
    """Load this checkout's gate; only the controller collects and records."""
    try:
        gate = LifecycleGate.load(config.rootpath, config.getini)
    except ValueError as error:
        raise pytest.UsageError(str(error)) from error
    config.stash[_GATE] = gate
    if not hasattr(config, "workerinput"):
        config.pluginmanager.register(BandCollector(gate), "lifecycle-cpu-band")


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> Generator[None, object, object]:
    """Start one CPU window before all fixtures, including shared initialization."""
    item.stash[_CPU_START] = process_time()
    return (yield)


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_teardown(item: pytest.Item) -> Generator[None, object, object]:
    """End after cleanup; intervening call and report-hook CPU stays included."""
    try:
        return (yield)
    finally:
        item.stash[_CPU] = process_time() - item.stash[_CPU_START]


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None) -> Generator[None, object, object]:
    """Cover every test phase, including session fixture creation and cleanup."""
    del nextitem
    _ACTIVE.append(item.nodeid)
    try:
        return (yield)
    finally:
        _ACTIVE.pop()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Fail on total fixture and call cost without hiding shared preparation."""
    del call
    report = yield
    elapsed = item.stash.get(_DURATIONS, 0.0) + report.duration
    item.stash[_DURATIONS] = elapsed
    failed = item.stash.get(_FAILED, False) or report.failed
    item.stash[_FAILED] = failed
    if report.when == "call":
        item.stash[_CALL_PASSED] = report.passed
    if report.when == "teardown":
        _judge_lifecycle(item, report, elapsed, failed=failed)
    return report


def _judge_lifecycle(item: pytest.Item, report: pytest.TestReport, elapsed: float, *, failed: bool) -> None:
    """Record both clocks and the limit, then fail a lifecycle over budget."""
    gate = item.config.stash[_GATE]
    key = record_key(item.nodeid)
    cpu = item.stash.get(_CPU, 0.0)
    limit = gate.cpu_limit(key)
    report.user_properties.append(("test_lifecycle_seconds", elapsed))
    report.user_properties.append(("test_lifecycle_cpu_seconds", cpu))
    report.user_properties.append(("test_lifecycle_cpu_limit", limit))
    report.user_properties.append(("test_lifecycle_measured", item.stash.get(_CALL_PASSED, False) and not failed))
    if (cpu > limit or elapsed > gate.wall_limit) and not failed:
        report.outcome = "failed"
        report.longrepr = (
            f"Test lifecycle CPU={cpu:.6f}s (limit {limit:.3f}s), "
            f"wall={elapsed:.6f}s (limit {gate.wall_limit:.3f}s) "
            f"exceeds budget (setup + call + teardown): {item.nodeid}; {gate.describe(key)}"
        )


# eof
