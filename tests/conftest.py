"""Suite-wide Hypothesis defaults and process-free test policy.

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

The example database is disabled to avoid per-test cache I/O. Strategies,
explicit examples and example budgets are unchanged. Random generation stays
enabled so parametrized batches continue to explore different examples.

Automatic worker selection is capped at two: spawning a worker per core
multiplies coverage and filesystem contention in this I/O-heavy suite.
An explicit worker count or PYTEST_XDIST_AUTO_NUM_WORKERS still wins.

Fix: a plain ``pytest -n auto`` uses groundhog's own default bound
(``tools.groundhog.runner.auto_workers``: a quarter of the logical CPUs, at
most two) instead of a separate cap, so the two never disagree.

Fix: groundhog no longer has a machine-wide run slot, so the session does not
mark itself as a slot holder. The suite needs no Git isolation either: the
standalone process audit fails any test that starts Git. Both shared policies
load here, after pytest-cov starts, so their import-time code stays covered.

Host-agent signals (``CLAUDECODE``, ``CODEX_THREAD_ID``) select the detected
LLM nature. Each worker drops them from its own environment once, at import:
a suite launched from a Claude session otherwise detected ``claude`` where a
typed prerequisite recorded ``codex``, and in-process publications failed on
the role-nature conflict, while the same tests passed from Codex. Tests of
detection set the signal they assert through ``monkeypatch`` or an explicit
mapping; launcher acceptance already strips both through
``session_environment``.

"""

from __future__ import annotations

import gc
import os

import pytest
from hypothesis import HealthCheck, settings

from tools.groundhog.runner import auto_workers

pytest_plugins = [
    "llm_shared_lifecycle_gate", "llm_shared_process_audit",
    "tests.memory_filesystem", "tests.scenario_cli",
    "tests.scenario_generation", "tests.testmon_monitoring",
]

# Testmon creates Coverage(config_file=False), ignoring pyproject's core.
# Use the same supported collector for both test dependencies and coverage.
os.environ.setdefault("COVERAGE_CORE", "sysmon")

# No test inherits the launching agent's host; see the module docstring.
for _host_signal in ("CLAUDECODE", "CODEX_THREAD_ID"):
    os.environ.pop(_host_signal, None)

_PROFILE = "llm-shared"

settings.register_profile(
    _PROFILE,
    deadline=None,
    database=None,
    # Contended workers make per-example setup slow rather than wrong; the
    # duration gate, not Hypothesis, owns the verdict on how slow is too slow.
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile(_PROFILE)


def pytest_collection_finish() -> None:
    """Keep the immutable collected suite out of later cyclic-GC traversals."""
    gc.collect()
    gc.freeze()


def pytest_sessionfinish() -> None:
    """Restore normal collection when pytest is embedded in a longer session."""
    gc.unfreeze()


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_auto_num_workers() -> int | None:
    """Bound automatic contention while preserving explicit xdist choices."""
    if os.environ.get("PYTEST_XDIST_AUTO_NUM_WORKERS"):
        return None
    return auto_workers(os.cpu_count())


# eof
