"""Mission dates, exact appends and real native lock contention on scratch files.

The opener and rollback failure paths are covered too: the default local
clock, the Windows handle and descriptor released when a later conversion
fails, a stalled write, and a rollback that cannot restore the old size. The
POSIX opener runs on every platform through a separate module instance loaded
with `os.name` set to `posix` and a recording `fcntl` stand-in, so its create,
reopen, busy and denied branches are proven where the suite runs.
"""

from __future__ import annotations

import errno
import importlib.util
import io
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Event
from types import ModuleType
from typing import TYPE_CHECKING

import pytest

from tools import copy_conversation_journal as journal

if TYPE_CHECKING:
    from collections.abc import Buffer, Callable
    from pathlib import Path
    from typing import BinaryIO


@pytest.mark.parametrize(
    ("instant", "relative", "heading"),
    [
        ("2026-11-16T05:59:59", "202611/project-a20261115.txt", "Dimanche 15 novembre 2026"),
        ("2026-11-16T06:00:00", "202611/project-a20261116.txt", "Lundi 16 novembre 2026"),
        ("2026-12-01T00:00:00", "202611/project-a20261130.txt", "Lundi 30 novembre 2026"),
        ("2027-01-01T05:00:00", "202612/project-a20261231.txt", "Jeudi 31 décembre 2026"),
        ("2024-03-01T05:00:00", "202402/project-a20240229.txt", "Jeudi 29 février 2024"),
    ],
)
def test_day_boundary_and_lowercase_prefix(tmp_path: Path, instant: str, relative: str, heading: str) -> None:
    """The filename and French heading agree across day, month and year boundaries."""
    root = tmp_path / "202401-PrOjEcT-A"
    root.mkdir()
    result = journal.journal_path({"JOURNAL_MISSION": str(root)}, datetime.fromisoformat(instant))
    assert result is not None
    assert result == root / relative
    assert not result.exists()
    journal.append_journal(result, "first")
    assert result.read_text(encoding="utf-8") == f"{heading}\n{'=' * len(heading)}\n\nfirst\n~~~~~~~~~~~~~~~~\n"


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
    journal.append_journal(root / "202611/demo20261130.txt", "copy")
    assert (root / "202611/demo20261130.txt").read_text(encoding="utf-8").startswith("Lundi 30 novembre 2026\n")


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
    heading = b"" if existing else b"Lundi 16 novembre 2026\n======================\n\n"
    assert path.read_bytes() == existing + heading + boundary + payload.encode() + ending + b"~~~~~~~~~~~~~~~~\n"


@pytest.mark.parametrize("existing", [b"", b"Mardi 17 novembre 2026\n======================\n\nold\n~~~~~~~~~~~~~~~~\n"])
def test_existing_file_never_gets_a_date_heading(tmp_path: Path, existing: bytes) -> None:
    """Both an empty existing file and a dated journal retain their exact prefix."""
    path = tmp_path / "demo20261117.txt"
    path.write_bytes(existing)
    journal.append_journal(path, "new")
    assert path.read_bytes() == existing + b"new\n~~~~~~~~~~~~~~~~\n"


def test_invalid_encoding_leaves_file_unchanged_and_releases_lock(tmp_path: Path) -> None:
    """A refused UTF-16 journal can be opened again immediately."""
    path = tmp_path / "daily.txt"
    original = "old".encode("utf-16")
    path.write_bytes(original)
    with pytest.raises(journal.JournalError, match="not UTF-8"):
        journal.append_journal(path, "new")
    assert path.read_bytes() == original
    with journal.locked_journal(path) as (stream, _):
        assert stream.read() == original


@pytest.mark.parametrize("existing", [None, b"old"])
def test_partial_failure_rolls_back_and_releases_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, existing: bytes | None,
) -> None:
    """Even a write that already changed the file restores the earlier content."""
    path = tmp_path / "demo20261117.txt"
    if existing is not None:
        path.write_bytes(existing)

    def fail_after_write(stream: BinaryIO, block: bytes) -> None:
        stream.write(block[:2])
        msg = "disk full"
        raise OSError(msg)

    monkeypatch.setattr(journal, "_write_all", fail_after_write)
    with pytest.raises(OSError, match="disk full"):
        journal.append_journal(path, "new")
    assert path.read_bytes() == (existing or b"")
    with journal.locked_journal(path) as (stream, _):
        assert stream.read() == (existing or b"")


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
            with journal.locked_journal(path) as (stream, _):
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


def test_stalled_write_fails_instead_of_looping() -> None:
    """A stream that accepts no byte raises before flushing instead of spinning."""
    class StalledStream(io.BytesIO):
        def write(self, _data: Buffer) -> int:
            return 0

    stream = StalledStream()
    with pytest.raises(OSError, match="made no progress"):
        journal._write_all(stream, b"abcdef")
    assert stream.getvalue() == b""


def test_failed_rollback_reports_both_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """When the old size cannot be restored, the caller is told to inspect the journal."""
    class FrozenStream(io.BytesIO):
        def truncate(self, _size: int | None = None) -> int:
            msg = "read-only medium"
            raise OSError(msg)

    def fail(_stream: BinaryIO, _block: bytes) -> None:
        msg = "disk full"
        raise OSError(msg)

    monkeypatch.setattr(journal, "_write_all", fail)
    stream = FrozenStream(b"old")
    expected = r"write failed \(disk full\); rollback failed \(read-only medium\); inspect the file"
    with pytest.raises(journal.JournalError, match=expected) as caught:
        journal._append_locked(stream, "new")
    assert isinstance(caught.value.__cause__, OSError)
    assert str(caught.value.__cause__) == "disk full"
    assert stream.getvalue() == b"old"


def test_local_now_samples_the_aware_local_clock() -> None:
    """The default clock carries the offset that the 06:00 day start is read in."""
    before = datetime.now(UTC)
    now = journal.local_now()
    after = datetime.now(UTC)
    assert now.utcoffset() is not None
    assert before <= now <= after


@pytest.mark.skipif(os.name != "nt", reason="Win32 handles exist on Windows only")
def test_windows_handle_is_closed_when_descriptor_creation_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed handle-to-descriptor conversion closes the exclusive handle it opened."""
    path = tmp_path / "daily.txt"
    path.write_bytes(b"keep")

    def refuse(_handle: int, _flags: int) -> int:
        msg = "no descriptor"
        raise OSError(msg)

    with monkeypatch.context() as patch:
        patch.setattr("msvcrt.open_osfhandle", refuse)
        with pytest.raises(OSError, match="no descriptor"):
            journal._open_windows(path)
    assert path.read_bytes() == b"keep"


@pytest.mark.skipif(os.name != "nt", reason="Win32 handles exist on Windows only")
def test_windows_descriptor_is_closed_when_stream_creation_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed stream wrapper closes the descriptor, which releases the exclusive handle."""
    path = tmp_path / "daily.txt"
    path.write_bytes(b"keep")
    descriptors: list[int] = []

    def refuse(descriptor: int, *_args: object, **_kwargs: object) -> BinaryIO:
        descriptors.append(descriptor)
        msg = "no stream"
        raise OSError(msg)

    with monkeypatch.context() as patch:
        patch.setattr(journal.os, "fdopen", refuse)
        with pytest.raises(OSError, match="no stream"):
            journal._open_windows(path)
    assert path.read_bytes() == b"keep"
    _assert_closed(descriptors[0])


def _assert_closed(descriptor: int) -> None:
    """A descriptor the opener closed can no longer be queried.

    The message text is localized; only its code prefix is stable.
    """
    with pytest.raises(OSError, match=r"^\[(?:WinError 6|Errno 9)\] ") as closed:
        os.fstat(descriptor)
    assert closed.value.errno == errno.EBADF


def _posix_journal(monkeypatch: pytest.MonkeyPatch, flock: Callable[[int, int], None]) -> ModuleType:
    """Load a separate journal module whose import-time platform test selects POSIX."""
    fcntl = ModuleType("fcntl")
    vars(fcntl).update(LOCK_EX=2, LOCK_NB=4, flock=flock)
    monkeypatch.setitem(sys.modules, "fcntl", fcntl)
    spec = importlib.util.spec_from_file_location("posix_copy_conversation_journal", journal.__file__)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with monkeypatch.context() as patch:
        patch.setattr(os, "name", "posix")
        spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("existing", [False, True])
def test_posix_opener_creates_or_reopens_then_locks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, existing: bool,
) -> None:
    """A POSIX writer creates the daily file or reopens it untruncated, then locks without blocking."""
    locks: list[tuple[int, int]] = []
    posix = _posix_journal(monkeypatch, lambda descriptor, operation: locks.append((descriptor, operation)))
    path = tmp_path / "daily.txt"
    if existing:
        path.write_bytes(b"keep")
    stream, created = posix._open_posix(path)
    with stream:
        assert created is not existing
        assert stream.readable()
        assert stream.writable()
        assert locks == [(stream.fileno(), 2 | 4)]
    assert path.read_bytes() == (b"keep" if existing else b"")


@pytest.mark.parametrize(
    ("code", "raised", "reason"),
    [
        (errno.EAGAIN, errno.EAGAIN, "Journal lock is busy"),
        (errno.EACCES, errno.EAGAIN, "Journal lock is busy"),
        (errno.EPERM, errno.EPERM, "refused"),
    ],
)
def test_posix_lock_failure_closes_the_descriptor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, code: int, raised: int, reason: str,
) -> None:
    """Contention becomes the retryable busy error, other refusals propagate, and neither leaks."""
    descriptors: list[int] = []

    def refuse(descriptor: int, _operation: int) -> None:
        descriptors.append(descriptor)
        raise OSError(code, "refused")

    posix = _posix_journal(monkeypatch, refuse)
    with pytest.raises(OSError, match=reason) as caught:
        posix._open_posix(tmp_path / "daily.txt")
    assert (caught.value.errno, caught.value.strerror) == (raised, reason)
    _assert_closed(descriptors[0])


# eof
