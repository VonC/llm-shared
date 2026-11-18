"""The cache lock publishes a complete record, waits for a live holder within its own budget and owns its record.

Step 3 of v0.14.0 git-cliff-provisioning (design "Lock record and transition
mutex" and "Bounded wait with a message"; design decisions Q03 and Q04;
requirement clarification Q06). Acquisition publishes a complete record
without replacement, under a transition mutex named from the cache root's
file identity, namespace, version and triple. A live holder gives one waiting
callback, then a poll every 250 ms of fake time until the caller's own wait
ends with `LockWaitError`; a holder change never resets that deadline.
`record_child` appends under the mutex, `release` removes only this caller's
record, and after `retain_record()` nothing removes it. An unverifiable record
fails closed at once. Since code review round 1 (R1), a lock freed at exactly
W is still taken, while a late wake-up or liveness queries that run past W
publish nothing and replace nothing.
"""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_support import (
    CURRENT,
    LockWorld,
    synthetic_pin,
)
from tools.release_workflow.git_cliff.budget import DOWNLOAD_BUDGET_VARIABLE
from tools.release_workflow.git_cliff.cache import CacheLayout
from tools.release_workflow.git_cliff.cache_lock import (
    LockRecord,
    LockRecordError,
    LockSeams,
    LockWaitError,
)
from tools.release_workflow.git_cliff.manifest import PLATFORM_TRIPLE
from tools.release_workflow.windows_process import (
    ProcessIdentity,
    ProcessState,
    current_identity,
    process_state,
    transition_mutex,
)

if TYPE_CHECKING:
    from pathlib import Path

PIN = synthetic_pin()
HOLDER = ProcessIdentity(4900, 133_000_000_000_000_900)
SUCCESSOR = ProcessIdentity(5100, 133_000_000_000_005_100)
CHILD_A, CHILD_B = ProcessIdentity(4901, 901), ProcessIdentity(4902, 902)
STARTED = "2026-11-18T13:58:00+01:00"
NOW = "2026-11-18T14:02:31+01:00"


@pytest.fixture
def world(tmp_path: Path) -> LockWorld:
    """Give each case its own cache, clock, process states and mutex."""
    return LockWorld(CacheLayout(tmp_path / "tooling"))


def _listing(world: LockWorld) -> list[str]:
    """List the version directory, where no temporary may be left."""
    return sorted(path.name for path in world.layout.version_dir(PIN).iterdir())


def test_acquisition_publishes_a_complete_record_without_waiting(world: LockWorld) -> None:
    """The record names this process, its start time and caller kind; no temporary stays beside it."""
    lock = world.lock(PIN).acquire(1, world.on_wait)
    content = world.layout.lock_path(PIN).read_bytes()
    assert (lock.path, LockRecord.decode(content)) == (world.layout.lock_path(PIN), LockRecord(CURRENT, NOW, "engine"))
    assert list(json.loads(content)) == ["schema", "pid", "created", "started", "caller", "children"]
    assert (_listing(world), world.waits, world.clock.sleeps) == ([f"{PLATFORM_TRIPLE}.lock"], [], [])


@pytest.mark.parametrize("namespace", ["production", "evidence"])
def test_the_mutex_is_named_from_the_cache_root_namespace_version_and_triple(tmp_path: Path, namespace: str) -> None:
    """Evidence candidates lock in their own namespace; the cache root is created first for its identity."""
    world = LockWorld(CacheLayout(tmp_path / "tooling", namespace))
    world.lock(PIN).acquire(1, world.on_wait)
    root = world.layout.root.stat()
    name = f"Global\\llm-shared-git-cliff-{root.st_dev:x}-{root.st_ino:x}-{namespace}-2.14.2-{PLATFORM_TRIPLE}"
    assert world.mutex.entries == [(name, False)]


def test_a_live_holder_gives_one_waiting_callback_then_fails_at_the_callers_own_budget(world: LockWorld) -> None:
    """Polls every 250 ms of fake time and fails at W naming the lock, the owner and the remedy."""
    holder = LockRecord(HOLDER, STARTED, "gcliff")
    content = world.hold(PIN, holder)
    world.declare(ProcessState.ALIVE, HOLDER)
    with pytest.raises(LockWaitError) as caught:
        world.lock(PIN).acquire(1, world.on_wait)
    path = world.layout.lock_path(PIN)
    assert (world.waits, world.clock.sleeps, world.clock.elapsed, len(world.mutex.entries)) == ([(holder, 1)], [0.25] * 4, 1.0, 5)
    assert (caught.value.path, caught.value.owner, caught.value.started, caught.value.wait) == (path, HOLDER, STARTED, 1)
    assert str(caught.value) == (
        f"{path}: held by process 4900 since {STARTED} (gcliff) after waiting 1 s. Another process holds the named"
        f" lock; retry when it ends, or wait longer by raising {DOWNLOAD_BUDGET_VARIABLE} (300 through 3600 s)"
    )
    assert path.read_bytes() == content


def test_a_holder_that_releases_mid_wait_lets_the_caller_acquire(world: LockWorld) -> None:
    """The record freed after two polls is published for this caller at the next one."""
    world.hold(PIN, LockRecord(HOLDER, STARTED, "gcliff"))
    world.declare(ProcessState.ALIVE, HOLDER)
    world.clock.at(0.5, world.layout.lock_path(PIN).unlink)
    world.lock(PIN).acquire(1, world.on_wait)
    # Acquired at 0.5 s of fake time; the stamp keeps whole seconds.
    assert LockRecord.decode(world.layout.lock_path(PIN).read_bytes()) == LockRecord(CURRENT, NOW, "engine")
    assert (len(world.waits), world.clock.sleeps) == (1, [0.25, 0.25])


def test_a_holder_change_never_resets_the_callers_deadline(world: LockWorld) -> None:
    """A successor taking the lock mid-wait gives no new callback and no new budget."""
    first = LockRecord(HOLDER, STARTED, "gcliff")
    world.hold(PIN, first)
    world.declare(ProcessState.ALIVE, HOLDER, SUCCESSOR)
    world.clock.at(0.5, lambda: world.hold(PIN, LockRecord(SUCCESSOR, NOW, "engine")))
    with pytest.raises(LockWaitError) as caught:
        world.lock(PIN).acquire(1, world.on_wait)
    assert (caught.value.owner, world.clock.elapsed, world.waits) == (SUCCESSOR, 1.0, [(first, 1)])


def test_a_lock_freed_at_the_deadline_is_still_taken_by_the_last_poll(world: LockWorld) -> None:
    """The poll at exactly W is within the budget: a lock freed by then is acquired."""
    world.hold(PIN, LockRecord(HOLDER, STARTED, "gcliff"))
    world.declare(ProcessState.ALIVE, HOLDER)
    world.clock.at(1.0, world.layout.lock_path(PIN).unlink)
    world.lock(PIN).acquire(1, world.on_wait)
    assert LockRecord.decode(world.layout.lock_path(PIN).read_bytes()) == LockRecord(CURRENT, "2026-11-18T14:02:32+01:00", "engine")
    assert (len(world.waits), world.clock.sleeps) == (1, [0.25] * 4)


def test_a_waiter_waking_after_its_deadline_never_takes_the_freed_lock(world: LockWorld) -> None:
    """Code review round 1, R1: a late wake-up finds the lock freed, yet fails without publishing anything."""
    holder = LockRecord(HOLDER, STARTED, "gcliff")
    world.hold(PIN, holder)
    world.declare(ProcessState.ALIVE, HOLDER)
    world.clock.oversleep = 0.1
    world.clock.at(1.0, world.layout.lock_path(PIN).unlink)
    with pytest.raises(LockWaitError) as caught:
        world.lock(PIN).acquire(1, world.on_wait)
    assert (caught.value.owner, caught.value.started, world.waits, world.clock.sleeps) == (HOLDER, STARTED, [(holder, 1)], [0.25] * 3)
    assert (world.clock.elapsed, _listing(world)) == (pytest.approx(1.05), [])


def test_liveness_queries_crossing_the_deadline_never_replace_a_dead_record(world: LockWorld) -> None:
    """Code review round 1, R1: proving a dead holder takes past W, so its record stays and no holder is named."""
    content = world.hold(PIN, LockRecord(HOLDER, STARTED, "gcliff", (CHILD_A,)))
    world.declare(ProcessState.DEAD, HOLDER, CHILD_A)
    world.query_seconds = 0.6
    with pytest.raises(LockWaitError) as caught:
        world.lock(PIN).acquire(1, world.on_wait)
    path = world.layout.lock_path(PIN)
    assert (caught.value.owner, caught.value.started, world.waits, world.clock.sleeps) == (None, None, [], [])
    assert str(caught.value).startswith(f"{path}: not acquired before its deadline after waiting 1 s. Another process")
    assert (path.read_bytes(), world.states.queries) == (content, [HOLDER, CHILD_A])


def test_record_child_appends_each_identity_under_the_mutex(world: LockWorld) -> None:
    """Each child is added to the held record in its own transition, oldest first."""
    lock = world.lock(PIN).acquire(1, world.on_wait)
    lock.record_child(CHILD_A)
    lock.record_child(CHILD_B)
    assert LockRecord.decode(world.layout.lock_path(PIN).read_bytes()).children == (CHILD_A, CHILD_B)
    assert (len(world.mutex.entries), _listing(world)) == (3, [f"{PLATFORM_TRIPLE}.lock"])


def test_release_removes_this_callers_record(world: LockWorld) -> None:
    """A released lock leaves an empty version directory, and a second release is refused."""
    lock = world.lock(PIN).acquire(1, world.on_wait)
    lock.record_child(CHILD_A)
    lock.release()
    assert _listing(world) == []
    with pytest.raises(LockRecordError, match="not held by this caller"):
        lock.release()


def test_release_leaves_a_record_that_is_no_longer_this_callers(world: LockWorld) -> None:
    """A record replaced by hand is never removed by the caller that lost it."""
    lock = world.lock(PIN).acquire(1, world.on_wait)
    content = world.hold(PIN, LockRecord(HOLDER, STARTED, "gcliff"))
    with pytest.raises(LockRecordError, match="no longer this caller's"):
        lock.release()
    assert world.layout.lock_path(PIN).read_bytes() == content


def test_after_retain_record_nothing_removes_or_changes_the_record(world: LockWorld) -> None:
    """An unconfirmed end keeps the record for a later recovery; `release` in a finally path removes nothing."""
    lock = world.lock(PIN).acquire(1, world.on_wait)
    lock.record_child(CHILD_A)
    content = world.layout.lock_path(PIN).read_bytes()
    lock.retain_record()
    lock.release()
    for refused in (lambda: lock.record_child(CHILD_B), lock.recover_attempts):
        with pytest.raises(LockRecordError, match="not held by this caller"):
            refused()
    assert world.layout.lock_path(PIN).read_bytes() == content


def test_an_unheld_lock_can_be_neither_retained_nor_acquired_twice(world: LockWorld) -> None:
    """Retention needs a held lock, and a held lock is not acquired again."""
    lock = world.lock(PIN)
    with pytest.raises(LockRecordError, match="not held by this caller"):
        lock.retain_record()
    lock.acquire(1, world.on_wait)
    with pytest.raises(LockRecordError, match="already held by this caller"):
        lock.acquire(1, world.on_wait)


def test_a_cache_lock_needs_a_caller_kind(world: LockWorld) -> None:
    """The record always says which kind of caller holds it."""
    with pytest.raises(ValueError, match="caller kind"):
        world.lock(PIN, caller="")


def test_the_default_seams_are_the_windows_primitives_and_the_local_clock() -> None:
    """Production passes only its clock and sleep; liveness, identity and mutex come from `windows_process`."""
    seams = LockSeams(clock=time.monotonic, sleep=time.sleep)
    assert (seams.probe, seams.current, seams.mutex) == (process_state, current_identity, transition_mutex)
    assert seams.now().utcoffset() is not None


def _record(**changes: object) -> bytes:
    """Encode a valid holder record with some fields replaced, or removed when the change is None."""
    fields = {**json.loads(LockRecord(HOLDER, STARTED, "gcliff", (CHILD_A,)).encode()), **changes}
    return json.dumps({key: value for key, value in fields.items() if value is not None}).encode()


@pytest.mark.parametrize("content", [
    pytest.param(b"{", id="not-json"),
    pytest.param(b"[]", id="not-an-object"),
    pytest.param(_record(caller=None), id="missing-field"),
    pytest.param(_record(note="x"), id="extra-field"),
    pytest.param(_record().replace(b'"schema": 1,', b'"schema": 1, "schema": 1,'), id="duplicate-key"),
    pytest.param(_record(schema=2), id="other-schema"),
    pytest.param(_record(pid=0), id="pid-zero"),
    pytest.param(_record(started="2026-11-18T13:58:00"), id="start-without-offset"),
    pytest.param(_record(caller=""), id="empty-caller"),
    pytest.param(_record(children={"pid": 1, "created": 1}), id="children-not-a-list"),
    pytest.param(_record(children=[{"pid": True, "created": 1}]), id="boolean-child-pid"),
])
def test_an_unverifiable_lock_record_fails_closed_at_once(world: LockWorld, content: bytes) -> None:
    """A record that cannot name a provable owner is neither waited for nor recovered."""
    world.layout.version_dir(PIN).mkdir(parents=True)
    world.layout.lock_path(PIN).write_bytes(content)
    with pytest.raises(LockRecordError, match="unverifiable lock record"):
        world.lock(PIN).acquire(1, world.on_wait)
    assert (world.layout.lock_path(PIN).read_bytes(), world.waits, world.clock.sleeps) == (content, [], [])


# eof
