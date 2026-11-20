"""Example tests of the nonblocking per-checkout guard of resume-paused.

Step 6 of v0.14.0 resume-paused: the guard file is named by the canonical
checkout digest in the temporary guard folder, a held guard is an immediate
skip, and every exit releases an acquired guard. Policy cases use a declared
lock primitive; the native cases lock a real empty file through two
independent handles, which Windows treats exactly as two processes, because
tests never start a process. Code review round 1 adds the checkout itself as
guard folder, an unavailable lock state and a raising lock attempt, both
closing their descriptor, and a native seek failure that is not contention.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tools.resume_paused_guard import (
    GUARD_FOLDER,
    CheckoutGuard,
    GuardState,
    NativeFileLock,
    guard_path,
)
from tools.resume_paused_models import CanonicalRoot

ROOT = CanonicalRoot.parse("C:\\work\\api")
OTHER = CanonicalRoot.parse("C:\\work\\web")
TEMP = "C:\\Users\\person\\AppData\\Local\\Temp"


@dataclass
class FakeLock:
    """Declared lock primitive recording every native call."""

    opened: int | None = 5
    state: GuardState = GuardState.ACQUIRED
    fail_lock: bool = False
    fail_unlock: bool = False
    calls: list[str] = field(default_factory=list[str])

    def open(self, path: Path) -> int | None:
        """Record the opened path and return the declared descriptor."""
        self.calls.append(f"open {path.name}")
        return self.opened

    def try_lock(self, descriptor: int) -> GuardState:
        """Record the attempt and return the declared state, or fail when declared."""
        self.calls.append(f"lock {descriptor}")
        if self.fail_lock:
            message = "lock crashed"
            raise RuntimeError(message)
        return self.state

    def unlock(self, descriptor: int) -> None:
        """Record the unlock, failing when declared."""
        self.calls.append(f"unlock {descriptor}")
        if self.fail_unlock:
            message = "unlock failed"
            raise OSError(message)

    def close(self, descriptor: int) -> None:
        """Record the close."""
        self.calls.append(f"close {descriptor}")


def test_guard_path_is_the_checkout_digest_in_the_temporary_guard_folder() -> None:
    """Every spelling of one checkout names one guard file outside the checkout."""
    digest = hashlib.sha256(b"c:\\work\\api").hexdigest()

    assert guard_path(ROOT, TEMP) == Path(TEMP) / GUARD_FOLDER / f"{digest}.guard"
    assert guard_path(CanonicalRoot.parse("c:/WORK/Api/"), TEMP) == guard_path(ROOT, TEMP)
    assert guard_path(OTHER, TEMP) != guard_path(ROOT, TEMP)


def test_an_acquired_guard_is_released_once_when_its_block_ends() -> None:
    """The lease unlocks then closes its descriptor; a second release does nothing."""
    lock = FakeLock()

    with CheckoutGuard(lock, lambda: TEMP).acquire(ROOT) as lease:
        assert lease.state is GuardState.ACQUIRED
        assert lock.calls[1:] == ["lock 5"]
    lease.release()

    assert lock.calls[2:] == ["unlock 5", "close 5"]


@pytest.mark.parametrize("state", [GuardState.HELD, GuardState.UNAVAILABLE])
def test_a_guard_held_elsewhere_or_unlockable_closes_its_descriptor(state: GuardState) -> None:
    """Contention is an immediate skip, another lock error unavailability; neither unlocks anything."""
    lock = FakeLock(state=state)

    with CheckoutGuard(lock, lambda: TEMP).acquire(ROOT) as lease:
        assert lease.state is state

    assert lock.calls[1:] == ["lock 5", "close 5"]


def test_a_raising_lock_attempt_closes_its_descriptor() -> None:
    """An unexpected error in the attempt still releases the descriptor before it propagates."""
    lock = FakeLock(fail_lock=True)

    with pytest.raises(RuntimeError, match="lock crashed"):
        CheckoutGuard(lock, lambda: TEMP).acquire(ROOT)

    assert lock.calls[1:] == ["lock 5", "close 5"]


def test_the_checkout_itself_as_guard_folder_is_unavailable() -> None:
    """A checkout named like the guard folder, inside the temporary folder, never holds its own guard."""
    lock = FakeLock()
    checkout = CanonicalRoot.parse(f"{TEMP}\\{GUARD_FOLDER}")

    lease = CheckoutGuard(lock, lambda: TEMP).acquire(checkout)

    assert (lease.state, lock.calls) == (GuardState.UNAVAILABLE, [])


def test_an_unopenable_guard_file_is_unavailable() -> None:
    """A guard file that cannot be created permits no input."""
    lock = FakeLock(opened=None)

    lease = CheckoutGuard(lock, lambda: TEMP).acquire(ROOT)

    assert lease.state is GuardState.UNAVAILABLE
    assert len(lock.calls) == 1


@pytest.mark.parametrize("temp", ["C:\\WORK\\api\\tmp", "relative\\tmp", "C:\\work\\api\\.reviews"])
def test_a_temporary_folder_in_the_checkout_or_unreadable_is_unavailable(temp: str) -> None:
    """The guard is never created in the checkout, its artifact home included."""
    lock = FakeLock()

    lease = CheckoutGuard(lock, lambda: temp).acquire(ROOT)

    assert lease.state is GuardState.UNAVAILABLE
    assert lock.calls == []


def test_a_sibling_folder_sharing_the_checkout_prefix_is_outside_it() -> None:
    """A sibling folder whose name only starts with the checkout name is outside it."""
    lease = CheckoutGuard(FakeLock(), lambda: "C:\\work\\api-tmp").acquire(ROOT)

    assert lease.state is GuardState.ACQUIRED


def test_an_exception_in_the_protected_sequence_still_releases_the_guard() -> None:
    """The ``with`` block releases the guard before the error propagates."""
    lock = FakeLock()
    message = "transport failed"

    with pytest.raises(RuntimeError, match=message), CheckoutGuard(lock, lambda: TEMP).acquire(ROOT):
        raise RuntimeError(message)

    assert lock.calls[-2:] == ["unlock 5", "close 5"]


def test_a_failed_unlock_still_closes_the_descriptor() -> None:
    """Closing the handle drops the OS lock even when the unlock call fails."""
    lock = FakeLock(fail_unlock=True)
    lease = CheckoutGuard(lock, lambda: TEMP).acquire(ROOT)

    with pytest.raises(OSError, match="unlock failed"):
        lease.release()

    assert lock.calls[-2:] == ["unlock 5", "close 5"]


def test_a_native_guard_refuses_a_second_handle_until_released(tmp_path: Path) -> None:
    """Two independent handles contend as two invocations do; release frees the guard."""
    first = CheckoutGuard(temp_dir=lambda: str(tmp_path))
    second = CheckoutGuard(NativeFileLock(), lambda: str(tmp_path))

    with first.acquire(ROOT) as held:
        assert held.state is GuardState.ACQUIRED
        with second.acquire(ROOT) as contended:
            assert contended.state is GuardState.HELD
        with second.acquire(OTHER) as independent:
            assert independent.state is GuardState.ACQUIRED
    with second.acquire(ROOT) as freed:
        assert freed.state is GuardState.ACQUIRED

    assert held.path.parent == tmp_path / GUARD_FOLDER
    assert held.path.stat().st_size == 0


def test_a_native_guard_folder_that_cannot_be_created_is_unavailable(tmp_path: Path) -> None:
    """A file standing where the guard folder belongs makes the guard unavailable."""
    (tmp_path / GUARD_FOLDER).write_bytes(b"")

    lease = CheckoutGuard(temp_dir=lambda: str(tmp_path)).acquire(ROOT)

    assert lease.state is GuardState.UNAVAILABLE


def test_a_native_lock_error_other_than_contention_is_unavailability(tmp_path: Path) -> None:
    """A closed descriptor fails the seek with ``EBADF``: unavailable, not held."""
    lock = NativeFileLock()
    descriptor = lock.open(tmp_path / "guard")
    assert descriptor is not None
    lock.close(descriptor)

    assert lock.try_lock(descriptor) is GuardState.UNAVAILABLE


# eof
