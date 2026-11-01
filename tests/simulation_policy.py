"""Enforce process-free tests and a complete per-test lifecycle budget.

The audit hook observes actual process creation, so tests may still replace
subprocess APIs with explicit dependency observations. It covers setup and
teardown, including shared fixtures, and leaves pytest worker startup alone.
"""

from __future__ import annotations

import sys
from time import process_time
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

_ACTIVE: list[str] = []
_DURATIONS = pytest.StashKey[float]()
_CPU = pytest.StashKey[float]()
_CPU_START = pytest.StashKey[float]()
_FAILED = pytest.StashKey[bool]()
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
    """Declare the lifecycle limit as visible project configuration."""
    parser.addini("test_lifecycle_limit", "Maximum setup-through-teardown CPU seconds", default="0.1")
    parser.addini("test_lifecycle_wall_limit", "Maximum setup + call + teardown wall seconds", default="1.0")


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
    if report.when == "teardown":
        limit = float(item.config.getini("test_lifecycle_limit"))
        wall_limit = float(item.config.getini("test_lifecycle_wall_limit"))
        cpu = item.stash.get(_CPU, 0.0)
        report.user_properties.append(("test_lifecycle_seconds", elapsed))
        report.user_properties.append(("test_lifecycle_cpu_seconds", cpu))
        if (cpu > limit or elapsed > wall_limit) and not failed:
            report.outcome = "failed"
            report.longrepr = (
                f"Test lifecycle CPU={cpu:.6f}s (limit {limit:.3f}s), "
                f"wall={elapsed:.6f}s (limit {wall_limit:.3f}s) "
                f"exceeds budget (setup + call + teardown): {item.nodeid}"
            )
    return report


# eof
