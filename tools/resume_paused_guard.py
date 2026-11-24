"""Nonblocking per-checkout OS execution guard of the human-launched bulk resume.

Step 6 of v0.15.0 resume-paused serializes cooperating invocations per
checkout (design Q07=A): before any clear or resume reaches a checkout's
panes, the delivery takes that checkout's guard and holds it across every
revalidation and send of the protected sequence.

- The guard is a byte-range lock on an empty file named by the SHA-256 of the
  canonical checkout key, in a folder of the user's temporary directory. A
  temporary directory inside the checkout, so possibly inside its artifact
  home, makes the guard unavailable. The file holds no content: it is not a
  review lease and authorizes nothing.
- Acquisition never waits: a guard another invocation holds is an immediate
  skip, so independent checkouts keep progressing (``GuardState.HELD``).
- The operating system releases the lock with its handle, so a crashed
  invocation leaves no stale guard; ``GuardLease`` releases it on every exit
  of its ``with`` block, exceptions included.

The native primitive locks one byte through ``msvcrt``; Windows refuses that
byte to every other handle, of this process or another one. ``GuardState``
belongs to the delivery vocabulary (``tools.resume_paused_delivery_model``),
which this adapter uses and re-exports.

Fix (code review round 1): a temporary folder that is the checkout itself is
refused like one inside it; only a lock another handle holds (``EACCES`` or
``EDEADLK``) is contention, every other lock or seek error makes the guard
unavailable for that checkout alone; a failed acquisition always closes its
descriptor.
"""

from __future__ import annotations

import errno
import hashlib
import msvcrt
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, Protocol, Self

from tools.resume_paused_delivery_model import GuardState
from tools.resume_paused_models import ArtifactError, CanonicalRoot

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType

GUARD_FOLDER: Final = "llm-shared-resume-paused"
GUARD_SUFFIX: Final = ".guard"
_LOCKED_BYTES: Final = 1
_HELD_ERRNOS: Final = frozenset({errno.EACCES, errno.EDEADLK})


class LockPrimitive(Protocol):
    """Injected nonblocking file lock; tests may replace the native one."""

    def open(self, path: Path) -> int | None:
        """Open or create the guard file, returning its descriptor, or ``None`` on failure."""
        ...

    def try_lock(self, descriptor: int) -> GuardState:
        """Lock the guard without waiting: acquired, held by another handle, or unavailable."""
        ...

    def unlock(self, descriptor: int) -> None:
        """Release the lock taken through this descriptor."""
        ...

    def close(self, descriptor: int) -> None:
        """Close the descriptor."""
        ...


class NativeFileLock:
    """``LockPrimitive`` over a Windows byte-range lock that the OS drops with the handle."""

    def open(self, path: Path) -> int | None:
        """Create the guard folder and open the empty guard file, not inheritable."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            return os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOINHERIT, 0o600)
        except OSError:
            return None

    def try_lock(self, descriptor: int) -> GuardState:
        """Lock the first byte at once: another holder is contention, any other error unavailability."""
        try:
            os.lseek(descriptor, 0, os.SEEK_SET)
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, _LOCKED_BYTES)
        except OSError as error:
            return GuardState.HELD if error.errno in _HELD_ERRNOS else GuardState.UNAVAILABLE
        return GuardState.ACQUIRED

    def unlock(self, descriptor: int) -> None:
        """Unlock the first byte."""
        os.lseek(descriptor, 0, os.SEEK_SET)
        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, _LOCKED_BYTES)

    def close(self, descriptor: int) -> None:
        """Close the guard file."""
        os.close(descriptor)


def guard_path(root: CanonicalRoot, temp_dir: str) -> Path:
    """Return the guard file of one checkout: its key digest in the temporary guard folder."""
    digest = hashlib.sha256(root.key.encode("utf-8")).hexdigest()
    return Path(temp_dir) / GUARD_FOLDER / f"{digest}{GUARD_SUFFIX}"


def _inside(path: Path, root: CanonicalRoot) -> bool:
    """Return whether a guard file would fall in the checkout, the checkout folder itself included, or cannot be compared."""
    try:
        folder = CanonicalRoot.parse(str(path.parent), "guard folder")
    except ArtifactError:
        return True
    return folder == root or folder.key.startswith(root.key.rstrip("\\") + "\\")


@dataclass
class GuardLease:
    """One acquisition; a ``with`` block releases an acquired guard on every exit."""

    state: GuardState
    path: Path
    _primitive: LockPrimitive | None = field(default=None, repr=False)
    _descriptor: int | None = field(default=None, repr=False)

    def release(self) -> None:
        """Unlock and close an acquired guard; later calls do nothing."""
        primitive, descriptor = self._primitive, self._descriptor
        self._primitive = self._descriptor = None
        if primitive is None or descriptor is None:
            return
        try:
            primitive.unlock(descriptor)
        finally:
            primitive.close(descriptor)

    def __enter__(self) -> Self:
        """Return the lease itself."""
        return self

    def __exit__(self, kind: type[BaseException] | None, error: BaseException | None, trace: TracebackType | None) -> None:
        """Release the guard, whatever ended the block."""
        del kind, error, trace
        self.release()


class CheckoutGuard:
    """Acquire one checkout's guard without waiting."""

    def __init__(self, primitive: LockPrimitive | None = None, temp_dir: Callable[[], str] = tempfile.gettempdir) -> None:
        """Keep the lock primitive, native by default, and the temporary directory source."""
        self._primitive: LockPrimitive = primitive if primitive is not None else NativeFileLock()
        self._temp_dir = temp_dir

    def acquire(self, root: CanonicalRoot) -> GuardLease:
        """Take the checkout's guard, or report it held or unavailable; nothing waits."""
        path = guard_path(root, self._temp_dir())
        if _inside(path, root):
            return GuardLease(GuardState.UNAVAILABLE, path)
        descriptor = self._primitive.open(path)
        if descriptor is None:
            return GuardLease(GuardState.UNAVAILABLE, path)
        try:
            state = self._primitive.try_lock(descriptor)
        except BaseException:
            self._primitive.close(descriptor)
            raise
        if state is not GuardState.ACQUIRED:
            self._primitive.close(descriptor)
            return GuardLease(state, path)
        return GuardLease(GuardState.ACQUIRED, path, self._primitive, descriptor)


__all__ = [
    "GUARD_FOLDER",
    "CheckoutGuard",
    "GuardLease",
    "GuardState",
    "LockPrimitive",
    "NativeFileLock",
    "guard_path",
]


# eof
