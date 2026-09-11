"""Nonblocking snapshot locks defer writers without creating or modifying evidence."""

# pyright: reportPrivateUsage=false
from __future__ import annotations

import errno
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from tools import review_exchange_ownership_store as module

if TYPE_CHECKING:
    from pathlib import Path
    from typing import BinaryIO


def test_absent_legacy_lock_does_not_create_a_file(tmp_path: Path) -> None:
    """Legacy evidence remains observable without adding a lock or its parent."""
    lock = tmp_path / "missing" / "transition.lock"
    with module.observe_transition(lock) as available:
        assert available
    assert not lock.parent.exists()


def test_snapshot_lock_preserves_bytes_and_releases_after_reader_failure(tmp_path: Path) -> None:
    """A reader holds the native lock and releases it even when validation fails."""
    lock = tmp_path / "transition.lock"
    lock.write_bytes(b"\0")
    failure = "injected read failure"

    def fail_reader() -> None:
        """Fail only after acquiring the real snapshot lock."""
        with module.observe_transition(lock) as available:
            assert available
            raise ValueError(failure)

    with pytest.raises(ValueError, match=failure):
        fail_reader()
    with module.observe_transition(lock) as available:
        assert available
    assert lock.read_bytes() == b"\0"


def test_local_writer_is_deferred_without_waiting(tmp_path: Path) -> None:
    """A different thread holding the transition lock cannot delay a discovery pass."""
    lock = tmp_path / "transition.lock"
    entered, finish = Event(), Event()

    def hold_writer() -> None:
        """Hold the same process lock that production transitions acquire."""
        with module._local_lock(lock):
            entered.set()
            assert finish.wait(timeout=5)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(hold_writer)
        try:
            assert entered.wait(timeout=5)
            with module.observe_transition(lock) as available:
                assert not available
        finally:
            finish.set()
        future.result(timeout=5)


@pytest.mark.parametrize("platform", ["nt", "posix"])
@pytest.mark.parametrize("error_code", [None, errno.EACCES, errno.EAGAIN, errno.EDEADLK, errno.EIO])
def test_native_contention_is_deferred_but_io_failure_propagates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, platform: str, error_code: int | None,
) -> None:
    """Both OS adapters distinguish a live publisher from a broken locking operation."""
    native = Mock(side_effect=None if error_code is None else OSError(error_code, "native lock result"))
    lock = tmp_path / "transition.lock"
    lock.write_bytes(b"\0")
    with lock.open("rb") as stream:
        monkeypatch.setattr(module, "os", SimpleNamespace(name=platform))
        monkeypatch.setattr(module, "msvcrt", SimpleNamespace(locking=native, LK_NBRLCK=6), raising=False)
        monkeypatch.setattr(module, "fcntl", SimpleNamespace(flock=native, LOCK_SH=1, LOCK_NB=4), raising=False)
        if error_code == errno.EIO:
            with pytest.raises(OSError, match="native lock result") as caught:
                module._try_observation_lock(stream)
            assert caught.value.errno == errno.EIO
        else:
            assert module._try_observation_lock(stream) is (error_code is None)
        if platform == "nt":
            native.assert_called_once_with(stream.fileno(), 6, 1)
        else:
            native.assert_called_once_with(stream.fileno(), 5)


def test_busy_native_lock_is_not_unlocked_by_the_reader(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A losing reader never releases another process's lock."""
    lock = tmp_path / "transition.lock"
    lock.write_bytes(b"\0")

    def busy(_stream: BinaryIO) -> bool:
        """Model a publisher in a separate process."""
        return False

    unlock = Mock()
    monkeypatch.setattr(module, "_try_observation_lock", busy)
    monkeypatch.setattr(module, "_unlock_stream", unlock)
    with module.observe_transition(lock) as available:
        assert not available
    unlock.assert_not_called()


# eof
