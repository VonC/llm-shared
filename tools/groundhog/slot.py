"""Machine-wide groundhog run slot: one heavy child at a time per user.

Two checkouts walking their suites at once ran eight xdist workers, plus the
multi-threaded linters of check.bat, on a laptop with two performance cores:
every CPU sat at 100%, the desktop stalled, and each suite's duration gate
measured the other suite's load instead of its own calls. Every child that
groundhog streams, ``check.bat`` or pytest, now runs inside one per-user slot:
an operating-system lock on one byte of ``ghog.slot.lock`` in the user's
private ``.llm-shared`` folder, the folder of the session journal. A stage of
another checkout or project waits, naming once the checkout that holds the
slot, and starts as soon as it is released. The operating system drops the
lock with its process, so a killed run never leaves the slot taken.

Nested runs pass through: the holder marks its children with
``GHOG_SLOT_HELD``, so a suite that drives groundhog itself (this project's
own tests) never waits for the slot its parent run holds.
"""

from __future__ import annotations

import errno
import logging
import os
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Mapping
    from typing import BinaryIO

if os.name == "nt":
    import msvcrt  # pragma: no cover - platform-specific import
else:
    import fcntl  # pragma: no cover - platform-specific import

LOGGER = logging.getLogger("groundhog")

# Set in the holder's environment, so its children pass through the slot.
SLOT_HELD_VARIABLE: Final = "GHOG_SLOT_HELD"
# The per-user private folder, shared with the session journal.
SLOT_FOLDER_NAME: Final = ".llm-shared"
# The locked file: its first byte is the slot.
LOCK_FILE_NAME: Final = "ghog.slot.lock"
# The holder's description, read by a waiting run to say whom it waits for.
HOLDER_FILE_NAME: Final = "ghog.slot.holder"
# Seconds between two attempts of a waiting run.
POLL_SECONDS: Final = 2.0
# The errno values of a lock held by another process.
_BUSY_ERRNOS: Final = frozenset({errno.EACCES, errno.EAGAIN, errno.EDEADLK})


def slot_folder(environ: Mapping[str, str]) -> Path:
    """Return the per-user private folder that holds the slot.

    ``USERPROFILE`` wins where it is set (Windows), as for the session
    journal: a shell may point ``HOME`` elsewhere. ``HOME`` serves elsewhere.

    Args:
        environ: The environment to read.

    Returns:
        The ``.llm-shared`` folder of the user.
    """
    base = environ.get("USERPROFILE") or environ.get("HOME") or str(Path.home())
    return Path(base) / SLOT_FOLDER_NAME


@contextmanager
def machine_slot(
    label: str,
    folder: Path | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> Generator[None]:
    """Hold the user's run slot for one heavy child, waiting while it is taken.

    Args:
        label: The holder's project root and child, recorded for waiting runs.
        folder: The slot folder, the user's ``.llm-shared`` by default.
        sleep: The pause between two attempts, injectable for tests.
        clock: The monotonic clock measuring the wait, injectable for tests.

    Yields:
        Nothing; the slot is held until the block exits.
    """
    if os.environ.get(SLOT_HELD_VARIABLE):
        yield
        return
    home = folder if folder is not None else slot_folder(os.environ)
    _prepare(home)
    with (home / LOCK_FILE_NAME).open("a+b") as stream:
        _ensure_lock_byte(stream)
        _wait_for(stream, home, sleep, clock)
        try:
            (home / HOLDER_FILE_NAME).write_text(_holder_text(label), encoding="utf-8")
            os.environ[SLOT_HELD_VARIABLE] = "1"
            yield
        finally:
            os.environ.pop(SLOT_HELD_VARIABLE, None)
            _unlock(stream)


def _wait_for(
    stream: BinaryIO,
    home: Path,
    sleep: Callable[[float], None],
    clock: Callable[[], float],
) -> None:
    """Take the slot, announcing the holder once and the wait when it ends.

    Args:
        stream: The open lock file.
        home: The slot folder.
        sleep: The pause between two attempts.
        clock: The monotonic clock measuring the wait.
    """
    if _try_lock(stream):
        return
    start = clock()
    LOGGER.info("ghog: waiting for the machine run slot held by %s", _holder(home))
    sleep(POLL_SECONDS)
    while not _try_lock(stream):
        sleep(POLL_SECONDS)
    LOGGER.info("ghog: machine run slot taken after %.1fs of waiting", max(0.0, clock() - start))


def _prepare(home: Path) -> None:
    """Create the private folder with its ignore-everything file once.

    Args:
        home: The slot folder.
    """
    home.mkdir(parents=True, exist_ok=True)
    ignore = home / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n", encoding="utf-8")


def _holder_text(label: str) -> str:
    """Describe this process as the slot holder.

    Args:
        label: The holder's project root and child, as the runner names them.

    Returns:
        The one-line description a waiting run prints.
    """
    since = datetime.now(tz=UTC).astimezone().isoformat(timespec="seconds")
    return f"{label} (pid {os.getpid()}, since {since})"


def _holder(home: Path) -> str:
    """Read the holder description, tolerating a missing or partial file.

    Args:
        home: The slot folder.

    Returns:
        The recorded description, or a generic one.
    """
    try:
        text = (home / HOLDER_FILE_NAME).read_text(encoding="utf-8").strip()
    except OSError:
        text = ""
    return text or "another ghog run"


def _ensure_lock_byte(stream: BinaryIO) -> None:
    """Give Windows one byte range to lock.

    Args:
        stream: The open lock file.
    """
    stream.seek(0, os.SEEK_END)
    if stream.tell() == 0:
        stream.write(b"\0")
        stream.flush()
    stream.seek(0)


def _try_lock(stream: BinaryIO) -> bool:
    """Take the exclusive platform lock without blocking.

    Args:
        stream: The open lock file.

    Returns:
        True once held; False while another process holds it.

    Raises:
        OSError: Any failure other than a lock held elsewhere.
    """
    stream.seek(0)
    try:
        if os.name == "nt":
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as error:
        if error.errno not in _BUSY_ERRNOS:
            raise
        return False
    return True


def _unlock(stream: BinaryIO) -> None:
    """Release the platform lock before the lock file closes.

    Args:
        stream: The open lock file.
    """
    stream.seek(0)
    if os.name == "nt":
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        return
    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


# eof
