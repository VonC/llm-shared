"""Concurrent callers download once; a dead holder is recovered; a live or unknown one is waited for, never removed.

Step 5 of v0.14.0 git-cliff-provisioning (design "Bounded wait with a
message", "Recovery of a dead holder and its partial state" and
"Publication"; design decisions Q03, Q06 and Q07; requirement clarifications
Q06 and Q14). The second of two first uses prints the waiting line, rechecks
after the holder publishes and reuses the entry without downloading. A lock
whose owner and every child are `DEAD` is recovered with its staging
directory; an `ALIVE` or `UNKNOWN` owner or child keeps both, and the waiter
fails at its own W with the lock-wait stage, naming the live holder (or no
holder when a dead one was proven only past W). A repair between another
caller's validation and its child start is refused by that caller's guard.
An unverifiable lock record or an unavailable transition mutex is the
lock-wait stage too; a waiting line that cannot be written is the reporting
stage (code review round 2). Long waits use a fake clock that wakes 30 s late, so a
360 s wait costs a dozen polls.
"""

from __future__ import annotations

import errno
import os
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_children_fake import (
    SECOND,
    ProvisionWorld,
)
from tests.unit.tools.release_workflow.git_cliff_support import STAND_IN_EXECUTABLE
from tools.release_workflow.git_cliff.cache import OwnerFile
from tools.release_workflow.git_cliff.cache_lock import LockRecord
from tools.release_workflow.git_cliff.invocation import Policy
from tools.release_workflow.git_cliff.messages import (
    ProvisioningError,
    Stage,
    waiting_line,
)
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from pathlib import Path

HOLDER = ProcessIdentity(4900, 133_000_000_000_000_900)
CHILD = ProcessIdentity(4901, 133_000_000_000_000_901)
STARTED = "2026-11-18T13:58:00+01:00"
_LATE = 29.75
_DEAD, _ALIVE, _UNKNOWN = ProcessState.DEAD, ProcessState.ALIVE, ProcessState.UNKNOWN


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProvisionWorld:
    """Give each case its own cache, clock, process states, guards and children."""
    return ProvisionWorld.build(tmp_path, monkeypatch)


def _holder_with_staging(world: ProvisionWorld, children: tuple[ProcessIdentity, ...]) -> tuple[bytes, Path]:
    """Leave another caller's lock record and its staging directory with an owner file listing its children."""
    content = world.hold(LockRecord(HOLDER, STARTED, "engine", children))
    staging = world.lock_world().attempt(world.pin, HOLDER, OwnerFile(HOLDER, children).encode())
    return content, staging


def test_two_first_uses_download_once_and_the_second_reuses_after_its_recheck(world: ProvisionWorld) -> None:
    """The waiter prints one waiting line, finds the holder's entry under the lock and starts no worker."""
    world.hold(LockRecord(HOLDER, STARTED, "engine"))
    world.states.states[HOLDER] = _ALIVE

    def publish_and_release() -> None:
        world.install()
        world.layout.lock_path(world.pin).unlink()
        world.states.states[HOLDER] = _DEAD

    world.clock.at(10, publish_and_release)
    invocation = world.provision()
    assert world.lines == [waiting_line(world.pin.version, HOLDER.pid, STARTED, 360)]
    assert ([launched.role for launched in world.children.launched], invocation.executable) == (["probe"], world.executable)
    assert world.layout.lock_path(world.pin).exists() is False


def test_a_waiting_line_that_cannot_be_written_is_the_reporting_stage(world: ProvisionWorld) -> None:
    """A broken standard error ends the wait as a provisioning failure; the holder's record is untouched."""
    content = world.hold(LockRecord(HOLDER, STARTED, "engine"))
    world.states.states[HOLDER] = _ALIVE

    def broken(line: str) -> None:
        msg = f"cannot write {line!r}"
        raise OSError(errno.EPIPE, msg)

    world.on_line = broken
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, isinstance(raised.value.__cause__, OSError)) == (Stage.REPORTING, True)
    assert world.layout.lock_path(world.pin).read_bytes() == content


def test_a_lock_left_by_a_dead_owner_with_dead_children_is_recovered_with_its_staging(world: ProvisionWorld) -> None:
    """Only DEAD actors authorize recovery; the caller then provisions as usual."""
    _content, staging = _holder_with_staging(world, (CHILD,))
    world.states.states.update({HOLDER: _DEAD, CHILD: _DEAD})
    world.provision()
    assert (staging.exists(), world.executable.read_bytes()) == (False, STAND_IN_EXECUTABLE)
    assert world.lines[0].startswith("git-cliff 2.14.2: downloading")


@pytest.mark.parametrize(("owner", "child"), [(_ALIVE, _DEAD), (_UNKNOWN, _DEAD), (_DEAD, _ALIVE), (_DEAD, _UNKNOWN)])
def test_a_live_or_unknown_owner_or_child_is_preserved_and_the_waiter_fails_at_w(
        world: ProvisionWorld, owner: ProcessState, child: ProcessState) -> None:
    """However long it holds, the record and staging stay; the waiter fails at its own 360 s."""
    content, staging = _holder_with_staging(world, (CHILD,))
    world.states.states.update({HOLDER: owner, CHILD: child})
    world.clock.oversleep = _LATE
    files = world.tree()
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path, world.clock.elapsed) == (Stage.LOCK_WAIT, world.layout.lock_path(world.pin), 360)
    assert raised.value.detail == f"held by process {HOLDER.pid} since {STARTED} after waiting 360 s"
    assert (world.layout.lock_path(world.pin).read_bytes(), staging.is_dir(), world.tree()) == (content, True, files)
    assert world.children.launched == []


def test_a_dead_holder_proven_only_past_w_is_not_replaced_and_names_no_holder(world: ProvisionWorld) -> None:
    """Slow liveness queries push the proof past the deadline: the record stays and no live holder is named."""
    content = world.hold(LockRecord(HOLDER, STARTED, "gcliff"))
    world.states.states[HOLDER] = _DEAD
    world.query_seconds = 400
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.detail) == (Stage.LOCK_WAIT, "no live holder seen, not acquired before its deadline after waiting 360 s")
    assert world.layout.lock_path(world.pin).read_bytes() == content


def test_a_repair_between_validation_and_child_start_is_refused_by_the_guard(world: ProvisionWorld) -> None:
    """Caller A holds its guard from validation; caller B finds the entry invalid but cannot move it."""
    world.install()
    invocation = world.provision()
    world.corrupt_record()
    world.current = SECOND
    world.states.states[SECOND] = _ALIVE
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.IN_USE, world.entry)
    assert (world.executable.read_bytes(), world.attempts(), world.attempts("retired")) == (STAND_IN_EXECUTABLE, [], [])
    assert invocation.run([], policy=Policy.ENGINE, cwd=world.entry, environment={}).status == 0


def test_an_unverifiable_lock_record_is_the_lock_wait_stage(world: ProvisionWorld) -> None:
    """A record that proves no owner fails closed at once: it is never recovered."""
    world.layout.version_dir(world.pin).mkdir(parents=True)
    world.layout.lock_path(world.pin).write_bytes(b"{not json")
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, world.clock.elapsed) == (Stage.LOCK_WAIT, 0)
    assert "unverifiable lock record" in raised.value.detail
    assert world.layout.lock_path(world.pin).read_bytes() == b"{not json"


def test_an_unavailable_transition_mutex_is_the_lock_wait_stage(world: ProvisionWorld) -> None:
    """A mutex that stays busy fails visibly, without bypassing serialization."""
    world.mutex_error = OSError("Project operation transition mutex unavailable (wait=258)")
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.LOCK_WAIT, world.layout.lock_path(world.pin))
    assert "unavailable (wait=258)" in raised.value.detail


def test_a_cache_the_caller_cannot_create_is_the_permission_stage(world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """Taking the lock needs the version directory: a refused creation names the checkout directory."""

    def refuse(path: str | Path, *_arguments: object, **_keywords: object) -> None:
        raise PermissionError(errno.EACCES, "denied", str(path))

    monkeypatch.setattr(os, "mkdir", refuse)
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.PERMISSION, world.layout.tooling_root)


# eof
