"""Unit tests for the machine-wide groundhog run slot.

Cover the pass-through of a run nested in a holder, the first acquisition that
prepares the private folder and records its holder, the wait behind a slot held
by another handle (named once, then timed), the generic holder fallback, an
unexpected lock failure, the POSIX lock branches and the folder selection.
"""

from __future__ import annotations

import errno
import logging
import os
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from tools.groundhog import slot

if TYPE_CHECKING:
    from typing import BinaryIO


@pytest.fixture
def unheld(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear the suite-wide holder mark, so the slot is really taken."""
    monkeypatch.delenv(slot.SLOT_HELD_VARIABLE, raising=False)


def test_a_nested_run_passes_through(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A child of a holder neither creates nor waits for the slot."""
    monkeypatch.setenv(slot.SLOT_HELD_VARIABLE, "1")
    with slot.machine_slot("nested", tmp_path / "home"):
        pass
    assert not (tmp_path / "home").exists()


@pytest.mark.usefixtures("unheld")
def test_a_free_slot_is_taken_marked_and_released(tmp_path: Path) -> None:
    """The holder records itself, marks its children and frees the slot."""
    home = tmp_path / "home"
    with slot.machine_slot("C:/work/project: pytest.exe", home):
        assert os.environ[slot.SLOT_HELD_VARIABLE] == "1"
        holder = (home / slot.HOLDER_FILE_NAME).read_text(encoding="utf-8")
    assert holder.startswith(f"C:/work/project: pytest.exe (pid {os.getpid()}, since ")
    assert (home / ".gitignore").read_text(encoding="utf-8") == "*\n"
    assert slot.SLOT_HELD_VARIABLE not in os.environ
    with (home / slot.LOCK_FILE_NAME).open("a+b") as other:
        assert slot._try_lock(other)  # noqa: SLF001
        slot._unlock(other)  # noqa: SLF001


@pytest.mark.usefixtures("unheld")
def test_a_busy_slot_waits_names_its_holder_and_times_the_wait(
    tmp_path: Path, caplog: pytest.LogCaptureFixture,
) -> None:
    """A second handle waits, polling, until the first one releases."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".gitignore").write_text("*\n", encoding="utf-8")
    (home / slot.HOLDER_FILE_NAME).write_text("C:/other: check.bat (pid 7, since then)\n", encoding="utf-8")
    other = (home / slot.LOCK_FILE_NAME).open("a+b")
    slot._ensure_lock_byte(other)  # noqa: SLF001
    assert slot._try_lock(other)  # noqa: SLF001
    pauses: list[float] = []
    ticks = iter([10.0, 14.5])

    def release_on_second_pause(seconds: float) -> None:
        pauses.append(seconds)
        if len(pauses) == 2:  # noqa: PLR2004
            _release(other)

    with caplog.at_level(logging.INFO, logger="groundhog"), slot.machine_slot(
        "mine", home, release_on_second_pause, lambda: next(ticks),
    ):
        pass
    assert pauses == [slot.POLL_SECONDS, slot.POLL_SECONDS]
    assert "waiting for the machine run slot held by C:/other: check.bat (pid 7, since then)" in caplog.text
    assert "machine run slot taken after 4.5s of waiting" in caplog.text


def _release(stream: BinaryIO) -> None:
    """Release and close the competing handle."""
    slot._unlock(stream)  # noqa: SLF001
    stream.close()


def test_a_missing_holder_reads_as_another_run(tmp_path: Path) -> None:
    """A waiting run still says something when no holder was recorded."""
    assert slot._holder(tmp_path) == "another ghog run"  # noqa: SLF001


def test_an_unexpected_lock_failure_propagates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Only a lock held elsewhere means waiting; any other error is raised."""

    def broken(*_args: object) -> None:
        raise OSError(errno.EBADF, "bad descriptor")

    monkeypatch.setattr(slot, "msvcrt", SimpleNamespace(locking=broken, LK_NBLCK=2), raising=False)
    monkeypatch.setattr(slot.os, "name", "nt")
    with (tmp_path / "lock").open("a+b") as stream, pytest.raises(OSError, match="bad descriptor"):
        slot._try_lock(stream)  # noqa: SLF001


def test_posix_locks_use_flock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The POSIX branches take, refuse and release an exclusive flock."""
    calls: list[int] = []
    busy = [False]

    def flock(_descriptor: int, operation: int) -> None:
        calls.append(operation)
        if busy[0]:
            raise OSError(errno.EAGAIN, "held")

    stream = (tmp_path / "lock").open("a+b")
    monkeypatch.setattr(slot, "fcntl", SimpleNamespace(flock=flock, LOCK_EX=2, LOCK_NB=4, LOCK_UN=8), raising=False)
    try:
        monkeypatch.setattr(slot.os, "name", "posix")
        assert slot._try_lock(stream)  # noqa: SLF001
        busy[0] = True
        assert not slot._try_lock(stream)  # noqa: SLF001
        busy[0] = False
        slot._unlock(stream)  # noqa: SLF001
    finally:
        monkeypatch.undo()
        stream.close()
    assert calls == [6, 6, 8]


def test_the_folder_prefers_userprofile_then_home() -> None:
    """USERPROFILE wins, HOME serves elsewhere, the home directory last."""
    assert slot.slot_folder({"USERPROFILE": "C:/Users/me", "HOME": "D:/elsewhere"}) == Path("C:/Users/me/.llm-shared")
    assert slot.slot_folder({"HOME": "/home/me"}) == Path("/home/me/.llm-shared")
    assert slot.slot_folder({}) == Path.home() / ".llm-shared"


# eof
