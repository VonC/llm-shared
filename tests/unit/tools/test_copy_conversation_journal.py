"""Mission dates, exact appends and real native lock contention on scratch files."""

from __future__ import annotations

import errno
import io
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Event
from typing import TYPE_CHECKING

import pytest

from tools import copy_conversation_journal as journal

if TYPE_CHECKING:
    from collections.abc import Buffer
    from pathlib import Path
    from typing import BinaryIO


@pytest.mark.parametrize(
    ("instant", "relative"),
    [
        ("2026-11-16T05:59:59", "202611/project-a20261115.txt"),
        ("2026-11-16T06:00:00", "202611/project-a20261116.txt"),
        ("2026-12-01T00:00:00", "202611/project-a20261130.txt"),
        ("2027-01-01T05:00:00", "202612/project-a20261231.txt"),
        ("2024-03-01T05:00:00", "202402/project-a20240229.txt"),
    ],
)
def test_day_boundary_and_lowercase_prefix(tmp_path: Path, instant: str, relative: str) -> None:
    """The root's old month stays intact while the selected day crosses boundaries."""
    root = tmp_path / "202401-PrOjEcT-A"
    root.mkdir()
    result = journal.journal_path({"JOURNAL_MISSION": str(root)}, datetime.fromisoformat(instant))
    assert result is not None
    assert result == root / relative
    assert not result.exists()


def test_absent_environment_does_not_read_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disabled journaling has no filesystem or clock side effects."""
    def unexpected() -> datetime:
        pytest.fail("disabled journal read the clock")
    monkeypatch.setattr(journal, "local_now", unexpected)
    assert journal.journal_path({}) is None


def test_clock_is_captured_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """One time sample determines both path date components."""
    root = tmp_path / "202401-Demo"
    root.mkdir()
    samples = iter([datetime(2026, 12, 1, 5, 59, tzinfo=UTC)])
    monkeypatch.setattr(journal, "local_now", lambda: next(samples))
    assert journal.journal_path({"JOURNAL_MISSION": str(root)}) == root / "202611/demo20261130.txt"


@pytest.mark.parametrize("value", ["", " ", "relative/202401-Demo", "invalid", "202401-"])
def test_invalid_configuration_is_not_disabled(value: str) -> None:
    """A present but invalid variable never silently skips the journal."""
    with pytest.raises(journal.JournalError, match="absolute YYYYMM-NAME"):
        journal.journal_path({"JOURNAL_MISSION": value})


def test_missing_root_is_not_created(tmp_path: Path) -> None:
    """A typo cannot create a new mission tree."""
    root = tmp_path / "202401-Missing"
    with pytest.raises(journal.JournalError, match="does not exist"):
        journal.journal_path({"JOURNAL_MISSION": str(root)})
    assert not root.exists()


@pytest.mark.parametrize("existing", [b"", b"earlier", b"earlier\r\n", b"\xef\xbb\xbfearlier\n"])
@pytest.mark.parametrize("payload", ["Title:\n\nUnicode: café ☃", "Title:\n\nends in newline\n"])
def test_append_preserves_payload_and_existing_bytes(tmp_path: Path, existing: bytes, payload: str) -> None:
    """Only entry boundaries and the separator are added around the exact copy."""
    path = tmp_path / "202611" / "demo20261116.txt"
    if existing:
        path.parent.mkdir()
        path.write_bytes(existing)
    journal.append_journal(path, payload)
    boundary = b"\n" if existing and not existing.endswith(b"\n") else b""
    ending = b"" if payload.endswith("\n") else b"\n"
    assert path.read_bytes() == existing + boundary + payload.encode() + ending + b"~~~~~~~~~~~~~~~~\n"


def test_invalid_encoding_leaves_file_unchanged_and_releases_lock(tmp_path: Path) -> None:
    """A refused UTF-16 journal can be opened again immediately."""
    path = tmp_path / "daily.txt"
    original = "old".encode("utf-16")
    path.write_bytes(original)
    with pytest.raises(journal.JournalError, match="not UTF-8"):
        journal.append_journal(path, "new")
    assert path.read_bytes() == original
    with journal.locked_journal(path) as stream:
        assert stream.read() == original


def test_partial_failure_rolls_back_and_releases_lock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Even a write that already changed the file restores the earlier content."""
    path = tmp_path / "daily.txt"
    path.write_bytes(b"old")

    def fail_after_write(stream: BinaryIO, block: bytes) -> None:
        stream.write(block[:2])
        msg = "disk full"
        raise OSError(msg)

    monkeypatch.setattr(journal, "_write_all", fail_after_write)
    with pytest.raises(OSError, match="disk full"):
        journal.append_journal(path, "new")
    assert path.read_bytes() == b"old"
    with journal.locked_journal(path) as stream:
        assert stream.read() == b"old"


def test_two_writers_wait_and_append_complete_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Actual separate file handles serialize writers without interleaving bytes."""
    path = tmp_path / "daily.txt"
    contended = Event()
    released = Event()

    def wait_for_release(_delay: float) -> None:
        contended.set()
        assert released.wait(2), "first writer never released its lock"

    monkeypatch.setattr(journal.time, "sleep", wait_for_release)
    with ThreadPoolExecutor(max_workers=1) as executor:
        try:
            with journal.locked_journal(path) as stream:
                future = executor.submit(journal.append_journal, path, "second")
                assert contended.wait(2), "second writer did not encounter the real lock"
                journal._append_locked(stream, "first")
        finally:
            released.set()
        future.result(timeout=2)
    assert path.read_bytes() == b"first\n~~~~~~~~~~~~~~~~\nsecond\n~~~~~~~~~~~~~~~~\n"


def test_native_contention_times_out(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A fake deadline ends a real sharing violation without sleeping."""
    path = tmp_path / "daily.txt"
    with journal.locked_journal(path):
        samples = iter([0.0, journal._LOCK_TIMEOUT])
        monkeypatch.setattr(journal.time, "monotonic", lambda: next(samples))
        with pytest.raises(journal.JournalError, match="Timed out"):
            journal.append_journal(path, "blocked")
    assert path.read_bytes() == b""


@pytest.mark.parametrize("error_code", [errno.EPERM, errno.EACCES])
def test_permission_error_is_not_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error_code: int,
) -> None:
    """Only contention is retryable, not an access-denied failure."""
    calls: list[Path] = []

    def denied(path: Path) -> BinaryIO:
        calls.append(path)
        raise OSError(error_code, "denied")

    monkeypatch.setattr(journal, "_open_windows" if os.name == "nt" else "_open_posix", denied)
    path = tmp_path / "daily.txt"
    with pytest.raises(OSError, match="denied"), journal.locked_journal(path):
        pytest.fail("permission error was ignored")
    assert calls == [path]


def test_export_cannot_alias_journal(tmp_path: Path) -> None:
    """Path normalization prevents the ordinary export from truncating a journal."""
    path = tmp_path / "daily.txt"
    path.write_bytes(b"keep")
    with pytest.raises(journal.JournalError, match="must not overwrite"):
        journal.check_output_path(str(tmp_path / "." / "daily.txt"), path)
    assert path.read_bytes() == b"keep"
    journal.check_output_path(None, path)
    journal.check_output_path(str(path), None)
    journal.check_output_path(str(tmp_path / "copy.txt"), path)


def test_short_writes_are_completed(monkeypatch: pytest.MonkeyPatch) -> None:
    """The journal writer cannot lose the unwritten tail of a short write."""
    class ShortStream(io.BytesIO):
        def write(self, data: Buffer) -> int:
            return super().write(memoryview(data)[:2])

        def fileno(self) -> int:
            return 123

    flushed: list[int] = []
    monkeypatch.setattr(journal.os, "fsync", flushed.append)
    stream = ShortStream()
    journal._write_all(stream, b"abcdef")
    assert stream.getvalue() == b"abcdef"
    assert flushed == [123]


# eof
