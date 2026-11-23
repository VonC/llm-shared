"""Each lifecycle boundary leaves the state the design describes, and a second caller recovers only what every actor left DEAD.

Step 5 of v0.14.0 git-cliff-provisioning (design "Child process lifecycle",
"Deadline enforcement" and "Reuse check and the use guard"; design decisions
Q07 and Q17; requirement clarification Q14; plan risk pass). The fake child
launcher stops the caller at a boundary; the cache is then exactly what the
dead caller left, and a second caller runs against it:

- death during creation leaves no child or a job member that ends; death
  after a suspended worker was created, before its recording, leaves an empty
  staging directory recovered once the parent is `DEAD`;
- death while a recorded worker writes, or during a staging probe, keeps
  staging while the child is `ALIVE` and removes it once `DEAD`;
- a recording failure ends the suspended child, which wrote nothing;
- a worker or probe that never finishes is terminated and reaped before
  staging removal and lock release;
- death during a reuse probe or a git-cliff run keeps the inherited guard
  until the child ends; death between validation and child start leaves
  nothing to protect;
- a containment failure writes nothing; a Windows release below the baseline
  fails before any guard, download or child;
- an unconfirmed end of a worker or staging probe keeps staging and the lock
  record until the owner and every recorded child are `DEAD`; one before the
  child's identity records nothing; from a reuse probe or a git-cliff run the
  guard copy is retained.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_children_fake import (
    SECOND,
    Child,
    ProvisionWorld,
)
from tests.unit.tools.release_workflow.git_cliff_support import (
    CURRENT,
    STAND_IN_EXECUTABLE,
)
from tools.release_workflow.git_cliff.cache import OWNER_FILE
from tools.release_workflow.git_cliff.cache_lock import LockRecord
from tools.release_workflow.git_cliff.invocation import Policy
from tools.release_workflow.git_cliff.messages import ProvisioningError, Stage
from tools.release_workflow.windows_child import PlatformError
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from pathlib import Path

STRANGER = ProcessIdentity(5300, 133_000_000_000_005_300)
_DEAD, _ALIVE, _UNKNOWN = ProcessState.DEAD, ProcessState.ALIVE, ProcessState.UNKNOWN
_LATE = 29.75


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProvisionWorld:
    """Give each case its own cache, clock, process states, guards and children."""
    return ProvisionWorld.build(tmp_path, monkeypatch)


def _waiter_fails(world: ProvisionWorld) -> None:
    """A second caller waits its whole 360 s behind what is left, and fails without removing it."""
    files = world.tree()
    world.clock.oversleep = _LATE
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    world.clock.oversleep = 0.0
    assert (raised.value.stage, world.tree()) == (Stage.LOCK_WAIT, files)


def _provisions_afresh(world: ProvisionWorld, left: list[Path]) -> None:
    """The next caller recovers what was left and publishes a new entry."""
    world.provision()
    assert ([path for path in left if path.exists()], world.executable.read_bytes()) == ([], STAND_IN_EXECUTABLE)
    assert world.layout.lock_path(world.pin).exists() is False


@pytest.mark.parametrize("created", [True, False])
def test_death_during_creation_leaves_no_child_or_a_member_that_ends(world: ProvisionWorld, created: bool) -> None:  # noqa: FBT001
    """Nothing was recorded, so the dead parent's lock and staging are recovered at once."""
    world.children.script("worker", Child(death="creation", created=created))
    with world.dies():
        world.provision()
    staging = world.attempts()
    assert ([path.name for path in staging[0].iterdir()], world.recorded_children()) == ([OWNER_FILE], ((), ()))
    assert all(state is _DEAD for identity, state in world.states.states.items() if identity != SECOND)
    _provisions_afresh(world, staging)


def test_death_before_recording_a_suspended_worker_leaves_an_empty_staging_recovered_once_the_parent_is_dead(world: ProvisionWorld) -> None:
    """The worker ended with the job, unrun; an UNKNOWN parent still keeps everything."""
    world.children.script("worker", Child(death="before-record"))
    with world.dies():
        world.provision()
    staging = world.attempts()
    worker = world.children.launched[0].identity
    assert worker is not None
    assert ([path.name for path in staging[0].iterdir()], world.states.states[worker], world.recorded_children()) == (
        [OWNER_FILE], _DEAD, ((), ()))
    world.states.states[CURRENT] = _UNKNOWN
    _waiter_fails(world)
    world.states.states[CURRENT] = _DEAD
    _provisions_afresh(world, staging)


@pytest.mark.parametrize("role", ["worker", "probe"])
def test_death_while_a_recorded_child_runs_keeps_staging_while_it_is_alive(world: ProvisionWorld, role: str) -> None:
    """Kill-on-close is pending: the child is ALIVE, so its lock and staging wait for it to be DEAD."""
    world.children.script(role, Child(death="running", write=b"partial", after=_ALIVE))
    with world.dies():
        world.provision()
    child = world.children.of(role)[0].identity
    assert child is not None
    lock_children, owner_children = world.recorded_children()
    assert (child in lock_children, child in owner_children) == (True, True)
    staging = world.attempts()
    _waiter_fails(world)
    world.end(child)
    _provisions_afresh(world, staging)


def test_a_recording_failure_ends_the_suspended_worker_which_wrote_nothing(world: ProvisionWorld) -> None:
    """Another record replaced this caller's: recording fails, the child never ran, staging goes, the record stays."""
    foreign = LockRecord(STRANGER, "2026-11-18T14:00:00+01:00", "gcliff")

    def replace_record() -> None:
        world.layout.lock_path(world.pin).write_bytes(foreign.encode())

    world.children.script("worker", Child(before_record=replace_record))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    (worker,) = world.children.launched
    assert worker.identity is not None
    assert (raised.value.stage, worker.recorded, world.states.states[worker.identity]) == (Stage.CONTAINMENT, None, _DEAD)
    assert "record failed" in raised.value.detail
    assert any("the lock record could not be removed" in note for note in raised.value.__notes__)
    assert (world.attempts(), world.lock_record()) == ([], foreign)


@pytest.mark.parametrize(("role", "stage", "detail"), [
    ("worker", Stage.DOWNLOAD, "the download did not finish within its budget of 300 s"),
    ("probe", Stage.PROBE, "the version probe did not end within its budget of 15 s"),
])
def test_a_child_that_never_finishes_is_reaped_before_staging_removal_and_lock_release(
        world: ProvisionWorld, role: str, stage: Stage, detail: str) -> None:
    """At the reap both still exist; once the stage failed both are gone."""
    world.children.script(role, Child(hang=True))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.detail) == (stage, detail)
    assert world.children.of(role)[0].reaped == {"staging": True, "lock": True}
    assert world.attempt_state() == {"staging": False, "lock": False}


def _invalid_entry_refused_until_the_child_ends(world: ProvisionWorld, child: ProcessIdentity) -> None:
    """While the child holds its copy, a repair is refused; once it ended, the next caller repairs the entry."""
    world.corrupt_record()
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, world.attempts("retired")) == (Stage.IN_USE, [])
    world.end(child)
    world.provision()
    assert (len(world.attempts("retired")), world.executable.read_bytes()) == (1, STAND_IN_EXECUTABLE)


def test_death_during_a_reuse_probe_keeps_the_inherited_guard_until_the_probe_ends(world: ProvisionWorld) -> None:
    """The caller's own guard closed with it; the probe's copy still refuses the rename."""
    world.install()
    world.children.script("probe", Child(death="running", after=_ALIVE))
    with world.dies():
        world.provision()
    probe = world.children.of("probe")[0].identity
    assert probe is not None
    assert world.tree().get("2.14.2/x86_64-pc-windows-msvc.lock") is None
    _invalid_entry_refused_until_the_child_ends(world, probe)


def test_death_during_a_git_cliff_run_keeps_the_inherited_guard_until_the_run_ends(world: ProvisionWorld) -> None:
    """The launcher died; its git-cliff child, still running, keeps the executable in place."""
    world.install()
    invocation = world.provision()
    world.children.script("run", Child(death="running", after=_ALIVE))
    with world.dies():
        invocation.run(["--unreleased"], policy=Policy.ENGINE, cwd=world.entry, environment={})
    run = world.children.of("run")[0].identity
    assert run is not None
    _invalid_entry_refused_until_the_child_ends(world, run)


def test_death_between_validation_and_child_start_leaves_nothing_to_protect(world: ProvisionWorld) -> None:
    """The guard closed with its caller and no child exists: the next caller may repair the entry."""
    world.install()
    world.provision()
    world.kill(CURRENT)
    world.current = SECOND
    world.states.states[SECOND] = _ALIVE
    world.corrupt_record()
    world.provision()
    assert (len(world.attempts("retired")), world.executable.read_bytes()) == (1, STAND_IN_EXECUTABLE)


def test_a_containment_failure_writes_nothing(world: ProvisionWorld) -> None:
    """The worker is never created: no archive, staging removed, lock released."""
    world.children.script("worker", Child(containment=True))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.CONTAINMENT, world.entry)
    assert (world.attempt_state(), world.entry.exists()) == ({"staging": False, "lock": False}, False)


def test_a_windows_release_below_the_baseline_fails_before_any_guard_download_or_child(world: ProvisionWorld) -> None:
    """The platform stage comes before the reuse check."""
    world.platform_error = PlatformError("git-cliff provisioning needs Windows 10 or Windows Server 2016 or later on x64")
    world.install()
    files = world.tree()
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.PLATFORM, world.entry)
    assert (world.opener.opened, world.children.launched, world.tree()) == ([], [], files)


@pytest.mark.parametrize("role", ["worker", "probe"])
def test_an_unconfirmed_end_of_a_recorded_child_keeps_staging_and_the_lock_record_until_every_actor_is_dead(
        world: ProvisionWorld, role: str) -> None:
    """The record is retained, so release removes nothing; a later caller recovers once owner and child are DEAD."""
    world.children.script(role, Child(unconfirmed="after-run", after=_UNKNOWN))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    child = world.children.of(role)[0].identity
    assert child is not None
    assert (raised.value.stage, child in world.recorded_children()[0]) == (Stage.CONTAINMENT, True)
    staging = world.attempts()
    assert (len(staging), world.layout.lock_path(world.pin).exists()) == (1, True)
    world.kill(CURRENT)
    world.current = SECOND
    world.states.states[SECOND] = _ALIVE
    _waiter_fails(world)
    world.end(child)
    _provisions_afresh(world, staging)


def test_an_unconfirmed_end_before_the_identity_records_nothing_and_staging_is_recovered_once_the_owner_is_dead(
        world: ProvisionWorld) -> None:
    """The child never ran and was never recorded: only the owner's death matters."""
    world.children.script("worker", Child(unconfirmed="before-identity", after=_UNKNOWN))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    staging = world.attempts()
    assert (raised.value.stage, world.recorded_children(), len(staging)) == (Stage.CONTAINMENT, ((), ()), 1)
    world.kill(CURRENT)
    world.current = SECOND
    world.states.states[SECOND] = _ALIVE
    _provisions_afresh(world, staging)


def test_an_unconfirmed_end_of_a_reuse_probe_retains_the_guard_and_writes_nothing(world: ProvisionWorld) -> None:
    """`check_entry` retained the guard before any invocation existed; the caller's cleanup leaves it open."""
    world.install()
    files = world.tree()
    world.children.script("probe", Child(unconfirmed="after-run", after=_UNKNOWN))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    guard = world.opener.opened[0]
    assert (raised.value.stage, guard.retained, guard.closed, world.tree()) == (Stage.CONTAINMENT, True, False, files)


def test_an_unconfirmed_end_of_a_git_cliff_run_retains_the_invocation_guard(world: ProvisionWorld) -> None:
    """The run may still execute the binary, so the invocation keeps its guard copy open."""
    world.install()
    invocation = world.provision()
    world.children.script("run", Child(unconfirmed="after-run", after=_UNKNOWN))
    with pytest.raises(ProvisioningError) as raised:
        invocation.run([], policy=Policy.ENGINE, cwd=world.entry, environment={})
    guard = world.opener.opened[0]
    assert (raised.value.stage, guard.retained, guard.closed) == (Stage.CONTAINMENT, True, False)


# eof
