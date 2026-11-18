"""The cache lock recovers a holder and its attempt directories only when every recorded actor is DEAD.

Step 3 of v0.14.0 git-cliff-provisioning (design "Recovery of a dead holder
and its partial state" and "Child process lifecycle"; design decision Q03;
requirement clarifications Q06 and Q14). A record whose owner and every child
are `DEAD` is replaced inside the mutex; an `ALIVE` or `UNKNOWN` owner or
child keeps it however long the wait lasts, and an abandoned mutex authorizes
nothing. A lock holder removes a `.staging-` or `.retired-` directory only
when its name owner and every child of its owner file are `DEAD`; anything
unverifiable, live or not an attempt directory stays, and a removal that fails
keeps the directory for a later provisioning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_support import (
    CURRENT,
    LockWorld,
    deny_writes,
    install_entry,
    synthetic_pin,
)
from tools.release_workflow.git_cliff.cache import OWNER_FILE, CacheLayout, OwnerFile
from tools.release_workflow.git_cliff.cache_lock import (
    LockRecord,
    LockRecordError,
    LockWaitError,
)
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from pathlib import Path

PIN = synthetic_pin()
HOLDER = ProcessIdentity(4900, 133_000_000_000_000_900)
STRANGER = ProcessIdentity(5300, 133_000_000_000_005_300)
CHILD_A, CHILD_B = ProcessIdentity(4901, 901), ProcessIdentity(4902, 902)
STARTED = "2026-11-18T13:58:00+01:00"
NOW = "2026-11-18T14:02:31+01:00"
_DEAD, _ALIVE, _UNKNOWN = ProcessState.DEAD, ProcessState.ALIVE, ProcessState.UNKNOWN


@pytest.fixture
def world(tmp_path: Path) -> LockWorld:
    """Give each case its own cache, clock, process states and mutex."""
    return LockWorld(CacheLayout(tmp_path / "tooling"))


def test_a_dead_owner_with_dead_children_is_recovered_inside_the_mutex(world: LockWorld) -> None:
    """One transition proves every actor DEAD and publishes this caller's record in place of the old one."""
    world.hold(PIN, LockRecord(HOLDER, STARTED, "gcliff", (CHILD_A, CHILD_B)))
    world.declare(_DEAD, HOLDER, CHILD_A, CHILD_B)
    world.lock(PIN).acquire(1, world.on_wait)
    assert LockRecord.decode(world.layout.lock_path(PIN).read_bytes()) == LockRecord(CURRENT, NOW, "engine")
    assert (world.states.queries, len(world.mutex.entries), world.waits, world.clock.sleeps) == ([HOLDER, CHILD_A, CHILD_B], 1, [], [])
    assert [path.name for path in world.layout.version_dir(PIN).iterdir()] == [world.layout.lock_path(PIN).name]


@pytest.mark.parametrize("child", [_ALIVE, _UNKNOWN])
def test_a_dead_owner_with_a_live_or_unknown_child_is_kept(world: LockWorld, child: ProcessState) -> None:
    """A child still ending, or one that cannot be proven gone, keeps the record until the waiter fails."""
    content = world.hold(PIN, LockRecord(HOLDER, STARTED, "gcliff", (CHILD_A, CHILD_B)))
    world.declare(_DEAD, HOLDER, CHILD_A)
    world.declare(child, CHILD_B)
    with pytest.raises(LockWaitError):
        world.lock(PIN).acquire(1, world.on_wait)
    assert world.layout.lock_path(PIN).read_bytes() == content


def test_an_unknown_owner_is_kept_beyond_the_wait(world: LockWorld) -> None:
    """Age never proves death: an UNKNOWN owner is polled until W and its children are never asked about."""
    content = world.hold(PIN, LockRecord(HOLDER, STARTED, "gcliff", (CHILD_A,)))
    with pytest.raises(LockWaitError):
        world.lock(PIN).acquire(1, world.on_wait)
    assert (world.layout.lock_path(PIN).read_bytes(), world.states.queries) == (content, [HOLDER] * 5)


def test_an_abandoned_mutex_with_a_live_owner_keeps_the_record(world: LockWorld) -> None:
    """Mutex abandonment proves only that a thread ended; the live owner keeps its lock."""
    content = world.hold(PIN, LockRecord(HOLDER, STARTED, "gcliff"))
    world.declare(_ALIVE, HOLDER)
    world.mutex.abandoned = True
    with pytest.raises(LockWaitError):
        world.lock(PIN).acquire(1, world.on_wait)
    assert world.layout.lock_path(PIN).read_bytes() == content
    assert {abandoned for _name, abandoned in world.mutex.entries} == {True}


@dataclass(frozen=True)
class _Case:
    """One attempt directory: its name owner's state, its owner file, its children's states and the verdict."""

    owner: ProcessState
    owner_file: bytes | None
    children: tuple[tuple[ProcessIdentity, ProcessState], ...]
    removed: bool


_BOTH = OwnerFile(HOLDER, (CHILD_A, CHILD_B)).encode()
_ATTEMPTS = [
    pytest.param(_Case(_DEAD, _BOTH, ((CHILD_A, _DEAD), (CHILD_B, _DEAD)), removed=True), id="dead-owner-dead-children"),
    pytest.param(_Case(_DEAD, None, (), removed=True), id="dead-owner-without-owner-file"),
    pytest.param(_Case(_DEAD, _BOTH, ((CHILD_A, _DEAD), (CHILD_B, _ALIVE)), removed=False), id="live-child"),
    pytest.param(_Case(_DEAD, OwnerFile(HOLDER, (CHILD_A,)).encode(), (), removed=False), id="unknown-child"),
    pytest.param(_Case(_ALIVE, None, (), removed=False), id="live-owner"),
    pytest.param(_Case(_UNKNOWN, None, (), removed=False), id="unknown-owner"),
    pytest.param(_Case(_DEAD, b"{", (), removed=False), id="unreadable-owner-file"),
    pytest.param(_Case(_DEAD, OwnerFile(STRANGER).encode(), ((STRANGER, _DEAD),), removed=False), id="owner-file-of-another-owner"),
]


@pytest.mark.parametrize("kind", ["staging", "retired"])
@pytest.mark.parametrize("case", _ATTEMPTS)
def test_an_attempt_is_removed_only_when_its_owner_and_every_child_are_dead(world: LockWorld, kind: str, case: _Case) -> None:
    """The name gives the owner, the owner file the children; anything live or unverifiable stays."""
    lock = world.lock(PIN).acquire(1, world.on_wait)
    directory = world.attempt(PIN, HOLDER, case.owner_file, kind)
    world.declare(case.owner, HOLDER)
    world.states.states.update(case.children)
    assert lock.recover_attempts() == ((directory.name,) if case.removed else ())
    assert directory.exists() is not case.removed

def test_recovery_looks_only_at_attempt_directories(world: LockWorld) -> None:
    """The entry, the lock record, a file with an attempt name and an unknown directory are never touched."""
    install_entry(world.layout, PIN)
    lock = world.lock(PIN).acquire(1, world.on_wait)
    version = world.layout.version_dir(PIN)
    world.declare(_DEAD, HOLDER)
    decoy = world.layout.attempt_dir(PIN, "staging", HOLDER, "f11e")
    decoy.write_bytes(b"not a directory")
    (version / ".pending-4900-1-aa").mkdir()
    own = world.attempt(PIN, CURRENT, OwnerFile(CURRENT).encode())
    before = sorted(path.name for path in version.iterdir())
    world.states.queries.clear()
    assert lock.recover_attempts() == ()
    assert (sorted(path.name for path in version.iterdir()), world.states.queries) == (before, [CURRENT])
    assert own.is_dir()


def test_an_attempt_whose_owner_file_cannot_be_read_is_kept(world: LockWorld) -> None:
    """An owner file that exists but cannot be read may name live children, so its directory stays."""
    lock = world.lock(PIN).acquire(1, world.on_wait)
    directory = world.attempt(PIN, HOLDER, None)
    (directory / OWNER_FILE).mkdir()
    world.declare(_DEAD, HOLDER)
    assert lock.recover_attempts() == ()
    assert directory.is_dir()


def test_only_a_lock_holder_recovers_attempts(world: LockWorld) -> None:
    """Without the lock, a DEAD owner's staging directory is left alone."""
    directory = world.attempt(PIN, HOLDER, None)
    world.declare(_DEAD, HOLDER)
    with pytest.raises(LockRecordError, match="not held by this caller"):
        world.lock(PIN).recover_attempts()
    assert directory.is_dir()


def test_a_dead_attempt_that_cannot_be_removed_is_kept(world: LockWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """A refused removal leaves the directory for a later provisioning instead of failing this one."""
    lock = world.lock(PIN).acquire(1, world.on_wait)
    directory = world.attempt(PIN, HOLDER, None)
    world.declare(_DEAD, HOLDER)
    denial = deny_writes(monkeypatch)
    assert lock.recover_attempts() == ()
    assert directory.is_dir()
    assert denial.attempts


# eof
