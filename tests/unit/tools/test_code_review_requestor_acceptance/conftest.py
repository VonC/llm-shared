"""Fast bounded Git plumbing for requestor orchestration acceptance."""

from __future__ import annotations

import subprocess

import pytest

from tests.unit.tools.git_test_double import GitTestDouble


@pytest.fixture(autouse=True)
def bounded_git_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep lifecycle journeys in-process; focused evidence tests own real Git."""
    double = GitTestDouble(subprocess.run)
    monkeypatch.setattr(subprocess, "run", double.run)
