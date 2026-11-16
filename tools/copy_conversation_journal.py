"""Append the copied conversation to an optional, exclusively locked journal.

JOURNAL_MISSION names an existing YYYYMM-NAME folder. Its leading month is
part of the mission identity, not the date of the daily journal. The local
journal day starts at 06:00; its month selects a child folder and its day
selects <name-lowercase>YYYYMMDD.txt.
"""

from __future__ import annotations

import ctypes
import errno
import os
import re
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping
    from typing import BinaryIO

_MISSION_NAME = re.compile(r'\d{6}-(?P<prefix>[^<>:"/\\|?*\x00-\x1f]+)')
_DAY_START_HOUR = 6
_LOCK_TIMEOUT = 10.0
_LOCK_INTERVAL = 0.1
_SHARING_ERRORS = (32, 33)
_SEPARATOR = b"~~~~~~~~~~~~~~~~\n"


class JournalError(Exception):
    """A mission destination or append could not be completed."""


def local_now() -> datetime:
    """Capture the local wall clock once, independently of trimming dates."""
    return datetime.now().astimezone()


def journal_path(environ: Mapping[str, str], now: datetime | None = None) -> Path | None:
    """Resolve the optional daily path without creating directories or files.

    Raises:
        JournalError: The configured mission folder is invalid or missing.
    """
    value = environ.get("JOURNAL_MISSION")
    if value is None:
        return None
    root = Path(value)
    match = _MISSION_NAME.fullmatch(root.name)
    if not value.strip() or not root.is_absolute() or match is None or root.name.endswith((" ", ".")):
        msg = "JOURNAL_MISSION must name an absolute YYYYMM-NAME folder."
        raise JournalError(msg)
    if not root.is_dir():
        msg = f"JOURNAL_MISSION folder does not exist: {root}"
        raise JournalError(msg)
    clock = now if now is not None else local_now()
    day = clock.date() - timedelta(days=int(clock.hour < _DAY_START_HOUR))
    prefix = match["prefix"].lower()
    return root / f"{day:%Y%m}" / f"{prefix}{day:%Y%m%d}.txt"


def check_output_path(output: str | None, journal: Path | None) -> None:
    """Prevent the optional export from overwriting the journal before locking.

    Raises:
        JournalError: The export and journal identify the same file.
    """
    if output is None or journal is None:
        return
    target = Path(output)
    if target.resolve() == journal.resolve() or (
        target.exists() and journal.exists() and target.samefile(journal)
    ):
        msg = "--output must not overwrite the mission journal."
        raise JournalError(msg)


def _open_windows(path: Path) -> BinaryIO:
    """Atomically create/open the actual file with exclusive Windows sharing."""
    import msvcrt  # noqa: PLC0415 - Windows-only descriptor ownership
    from ctypes import wintypes  # noqa: PLC0415 - Windows-only API

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)  # type: ignore[attr-defined]
    kernel32.CreateFileW.argtypes = (
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    )
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    # GENERIC_READ | GENERIC_WRITE, no sharing, OPEN_ALWAYS, normal attributes.
    handle = kernel32.CreateFileW(str(path), 0xC0000000, 0, None, 4, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())  # type: ignore[attr-defined]
    try:
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDWR | os.O_BINARY)
    except BaseException:
        kernel32.CloseHandle(handle)
        raise
    try:
        return os.fdopen(descriptor, "r+b", buffering=0)
    except BaseException:
        os.close(descriptor)
        raise


if os.name != "nt":
    def _open_posix(path: Path) -> BinaryIO:
        """Open/create and take a cooperative POSIX lock without truncating."""
        import fcntl  # noqa: PLC0415 - POSIX-only API

        descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as err:
                if err.errno in (errno.EAGAIN, errno.EACCES):
                    msg = "Journal lock is busy"
                    raise BlockingIOError(errno.EAGAIN, msg) from err
                raise
            return os.fdopen(descriptor, "r+b", buffering=0)
        except BaseException:
            os.close(descriptor)
            raise


@contextmanager
def locked_journal(path: Path) -> Generator[BinaryIO]:
    """Wait briefly for exclusive access; closing releases even after failure.

    Raises:
        JournalError: Another writer holds the journal past the deadline.
    """
    opener = _open_windows if os.name == "nt" else _open_posix
    deadline = time.monotonic() + _LOCK_TIMEOUT
    while True:
        try:
            stream = opener(path)
            break
        except OSError as err:
            busy = (
                getattr(err, "winerror", None) in _SHARING_ERRORS
                if os.name == "nt" else err.errno == errno.EAGAIN
            )
            if not busy:
                raise
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                msg = f"Timed out waiting for mission journal lock: {path}"
                raise JournalError(msg) from err
            time.sleep(min(_LOCK_INTERVAL, remaining))
    with stream:
        yield stream


def _write_all(stream: BinaryIO, block: bytes) -> None:
    """Finish partial writes before flushing the journal to disk."""
    pending = memoryview(block)
    while pending:
        written = stream.write(pending)
        if not written:
            msg = "Journal write made no progress."
            raise OSError(msg)
        pending = pending[written:]
    stream.flush()
    os.fsync(stream.fileno())


def _append_locked(stream: BinaryIO, copy: str) -> None:
    """Validate encoding and append, restoring the old size on caught errors.

    Raises:
        JournalError: Existing text is not UTF-8 or a failed write cannot roll back.
    """
    existing = stream.read()
    try:
        existing.decode("utf-8-sig")
    except UnicodeDecodeError as err:
        msg = "Existing mission journal is not UTF-8; no bytes appended."
        raise JournalError(msg) from err
    boundary = b"\n" if existing and not existing.endswith(b"\n") else b""
    payload = copy.encode("utf-8")
    ending = b"" if payload.endswith(b"\n") else b"\n"
    block = boundary + payload + ending + _SEPARATOR
    try:
        _write_all(stream, block)
    except (OSError, KeyboardInterrupt) as err:
        try:
            stream.truncate(len(existing))
            stream.flush()
            os.fsync(stream.fileno())
        except OSError as rollback:
            msg = f"Journal write failed ({err}); rollback failed ({rollback}); inspect the file before retrying."
            raise JournalError(msg) from err
        raise


def append_journal(path: Path, copy: str) -> None:
    """Append one exact copy and separator under the actual daily file lock."""
    path.parent.mkdir(exist_ok=True)
    with locked_journal(path) as stream:
        _append_locked(stream, copy)


# eof
