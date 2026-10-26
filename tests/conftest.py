"""Suite-wide Hypothesis defaults and Git isolation for a parallel test run.

The full suite runs on xdist workers, so wall-clock time inside a test now
measures contention as much as the code under test. Hypothesis enforces a
200ms per-example deadline by default and reports a ``FlakyFailure`` when one
example crosses it and a rerun does not, which is exactly what contention
produces: an example measured at 72ms alone was measured at 288ms under load.

Fix: default ``deadline`` to ``None`` for the whole suite. This removes a
wall-clock assertion that parallel scheduling makes unreliable; it does not
remove slowness detection, which belongs to the project's own duration gate in
the covered full run at speed. Several property suites already set
``deadline=None`` by hand for the same reason, so this makes the established
convention the default. A module that sets its own ``deadline`` still wins,
because an explicit ``@settings`` value overrides the active profile.

Fix: fixture repositories commit with throwaway identities, so a developer's
global ``commit.gpgsign = true`` made every such commit fail (exit 128) when the
signing-key command refuses an identity it does not own. The session fixture
below appends ``commit.gpgsign=false`` through ``GIT_CONFIG_COUNT`` for every
Git child process the suite starts, which covers the helpers that never passed
the per-command ``-c commit.gpgsign=false``; any configuration entries already
in the environment are kept (``tests.git_isolation`` computes them).

Automatic worker selection is capped at four: spawning a worker per core
multiplies coverage and filesystem contention in this I/O-heavy suite.
An explicit worker count or PYTEST_XDIST_AUTO_NUM_WORKERS still wins.

Fix: groundhog now runs each child inside the user's machine-wide run slot.
The suite drives groundhog in-process with faked children, so the session
marks itself as a slot holder (``GHOG_SLOT_HELD``): a plain pytest run never
takes, or waits for, the slot of a real walk in another checkout. The slot's
own tests clear the mark and use a temporary slot folder.

Fix: a plain ``pytest -n auto`` uses groundhog's own default bound
(``tools.groundhog.runner.auto_workers``: a quarter of the logical CPUs, at
most two) instead of a separate cap of four, so the two never disagree.

Fix: every Git call went through Git for Windows' launcher, two processes per
call. ``pytest_configure`` puts the native ``git.exe`` folder first on
``PATH`` (``tests.git_isolation.native_git_path``) before collection, so module
level copies of the environment carry it too. That halves the Git processes of
the suite and of the CLI children that inherit its environment.
"""

from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING

import pytest
from hypothesis import HealthCheck, settings

from tests.git_isolation import native_git_path, unsigned_commit_settings
from tools.groundhog.runner import auto_workers

if TYPE_CHECKING:
    from collections.abc import Iterator

_PROFILE = "llm-shared"

settings.register_profile(
    _PROFILE,
    deadline=None,
    # Contended workers make per-example setup slow rather than wrong; the
    # duration gate, not Hypothesis, owns the verdict on how slow is too slow.
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile(_PROFILE)


@pytest.fixture(scope="session", autouse=True)
def unsigned_fixture_commits() -> Iterator[None]:
    """Keep fixture-repository commits independent of the developer's signing setup."""
    with pytest.MonkeyPatch.context() as patch:
        for name, value in unsigned_commit_settings(os.environ).items():
            patch.setenv(name, value)
        yield


def pytest_configure() -> None:
    """Start the native ``git.exe`` instead of its launcher for every Git child."""
    path = os.environ.get("PATH", "")
    os.environ["PATH"] = native_git_path(path, shutil.which("git", path=path))


@pytest.fixture(scope="session", autouse=True)
def groundhog_slot_held() -> Iterator[None]:
    """Let in-process groundhog runs pass through the machine-wide run slot."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("GHOG_SLOT_HELD", "1")
        yield


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_auto_num_workers() -> int | None:
    """Bound automatic contention while preserving explicit xdist choices."""
    if os.environ.get("PYTEST_XDIST_AUTO_NUM_WORKERS"):
        return None
    return auto_workers(os.cpu_count())


# eof
