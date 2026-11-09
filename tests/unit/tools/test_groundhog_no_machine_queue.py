"""Groundhog never makes a run wait for a run of another checkout or project.

A per-user machine-wide run slot once serialized every checkout's children
behind one operating-system file lock: one slow suite then held every other
checkout's run for hours, inside their own time budgets. The slot is gone.
These tests keep it gone: groundhog's source takes no cross-process file
lock, a streamed child starts at once without touching a per-user folder, and
the canonical instruction keeps the rule that forbids such a queue.
Read each real source once for all lock markers, avoiding repeated native IO
inside the lifecycle budget while preserving the complete source scan.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING, cast

from tools.groundhog import runner

if TYPE_CHECKING:
    import subprocess

    import pytest

_ROOT = Path(__file__).resolve().parents[3]
_GROUNDHOG = _ROOT / "tools" / "groundhog"
# Cross-process lock primitives and the former slot's pass-through mark.
_LOCK_MARKERS = ("msvcrt", "fcntl", "LockFileEx", "SLOT_HELD")


class _Child:
    """A finished child process that printed two lines."""

    stdout = io.StringIO("first\nsecond\n")

    @staticmethod
    def wait() -> int:
        """Return the child's exit code."""
        return 0


def test_groundhog_source_takes_no_cross_process_lock() -> None:
    """No groundhog module can lock a file shared by runs of other checkouts."""
    offenders: list[str] = []
    for path in _GROUNDHOG.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        offenders.extend(f"{path.name}: {marker}" for marker in _LOCK_MARKERS if marker in source)
    assert offenders == []
    assert not (_GROUNDHOG / "slot.py").exists()


def test_streamed_child_starts_at_once_without_per_user_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The child starts immediately and nothing appears in the user's profile."""
    profile = tmp_path / "profile"
    profile.mkdir()
    monkeypatch.setenv("USERPROFILE", str(profile))
    monkeypatch.setenv("HOME", str(profile))
    started: list[list[str]] = []

    def popen(command: list[str], _cwd: Path) -> subprocess.Popen[str]:
        started.append(command)
        return cast("subprocess.Popen[str]", _Child())

    lines: list[str] = []
    config = runner.StreamConfig(["pytest"], tmp_path, popen)

    assert runner.run_streaming(config, lines.append) == 0
    assert started == [["pytest"]]
    assert lines == ["first", "second"]
    assert list(profile.iterdir()) == []


def test_instruction_forbids_a_machine_wide_queue() -> None:
    """The canonical groundhog instruction keeps the no-queue rule."""
    text = (_ROOT / "instructions" / "groundhog.md").read_text(encoding="utf-8")
    assert "Groundhog holds no machine-wide slot, lock or queue" in text
    assert "taskkill /T /F /PID <pid>" in text


# eof
