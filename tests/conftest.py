"""Suite-wide Hypothesis defaults for a parallel test run.

The full suite runs on xdist workers, so wall-clock time inside a test now
measures contention as much as the code under test. Hypothesis enforces a
200ms per-example deadline by default and reports a ``FlakyFailure`` when one
example crosses it and a rerun does not, which is exactly what contention
produces: an example measured at 72ms alone was measured at 288ms under load.

Fix: default ``deadline`` to ``None`` for the whole suite. This removes a
wall-clock assertion that parallel scheduling makes unreliable; it does not
remove slowness detection, which belongs to the project's own duration gate.
Several property suites already set
``deadline=None`` by hand for the same reason, so this makes the established
convention the default. A module that sets its own ``deadline`` still wins,
because an explicit ``@settings`` value overrides the active profile.

Automatic worker selection is capped at four: spawning a worker per core
multiplies coverage and filesystem contention in this I/O-heavy suite.
An explicit worker count or PYTEST_XDIST_AUTO_NUM_WORKERS still wins.
"""

from __future__ import annotations

import os

import pytest
from hypothesis import HealthCheck, settings

_PROFILE = "llm-shared"

settings.register_profile(
    _PROFILE,
    deadline=None,
    # Contended workers make per-example setup slow rather than wrong; the
    # duration gate, not Hypothesis, owns the verdict on how slow is too slow.
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile(_PROFILE)


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_auto_num_workers() -> int | None:
    """Bound automatic contention while preserving explicit xdist choices."""
    if os.environ.get("PYTEST_XDIST_AUTO_NUM_WORKERS"):
        return None
    return min(4, os.cpu_count() or 1)


# eof
