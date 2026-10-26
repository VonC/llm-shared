"""A stopped waiter, or one whose test process died, leaves no interpreter running.

A real waiter survived an hour after its test process was killed mid-run: no
cleanup ran, so its interpreter kept polling every 0.05s. These scenarios
start real waiters in setup and check, through the pid each driver reported,
that the shared cleanup ends that exact interpreter, and that a waiter exits
by itself once the test process that started it is gone (a short-lived
stand-in process plays that test process).

The stand-in runs the base interpreter on Windows: a virtual environment's
``python`` is a launcher stub, so ``sys.executable`` would start two processes.
"""

# ruff: noqa: S603
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from time import monotonic, sleep
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.review_resume.conftest import (
    ReviewRepository,
    start_wait,
    stop_waiter,
    waiter_interpreter,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

# Seconds an orphaned driver may take to notice its test process is gone.
_ORPHAN_EXIT_SECONDS = 5.0
# A single-process interpreter for the stand-in test process.
_STAND_IN_INTERPRETER = str(Path(sys.base_prefix) / "python.exe") if os.name == "nt" else sys.executable


@pytest.fixture
def started_waiter(tmp_path: Path) -> Iterator[subprocess.Popen[str]]:
    """Start one real waiter on a seeded repository, stopping it in any case."""
    process = start_wait(ReviewRepository(tmp_path / "caller", fast_git=True))
    assert waiter_interpreter(process).alive()
    try:
        yield process
    finally:
        stop_waiter(process)


@pytest.fixture
def orphanable_waiter(tmp_path: Path) -> Iterator[tuple[subprocess.Popen[str], subprocess.Popen[str]]]:
    """Start a waiter that watches a stand-in test process instead of this one."""
    stand_in = subprocess.Popen([_STAND_IN_INTERPRETER, "-I", "-S", "-c", "import time; time.sleep(120)"], text=True)
    try:
        process = start_wait(ReviewRepository(tmp_path / "caller", fast_git=True), parent_pid=stand_in.pid)
        try:
            yield process, stand_in
        finally:
            stop_waiter(process)
    finally:
        stand_in.kill()
        stand_in.wait(timeout=5)


def test_stop_waiter_ends_the_real_interpreter(started_waiter: subprocess.Popen[str]) -> None:
    """The shared cleanup reaches the interpreter behind any launcher."""
    interpreter = waiter_interpreter(started_waiter)
    stop_waiter(started_waiter)
    assert not interpreter.alive()


def test_a_waiter_exits_once_its_test_process_is_gone(
    orphanable_waiter: tuple[subprocess.Popen[str], subprocess.Popen[str]],
) -> None:
    """A test process killed mid-run can no longer leave its waiter polling."""
    process, stand_in = orphanable_waiter
    interpreter = waiter_interpreter(process)
    assert interpreter.alive()
    stand_in.kill()
    stand_in.wait(timeout=5)
    deadline = monotonic() + _ORPHAN_EXIT_SECONDS
    while interpreter.alive() and monotonic() < deadline:
        sleep(0.02)
    assert not interpreter.alive()


# eof
