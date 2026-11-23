"""The lock holder installs a pin in staging, retires an invalid entry and publishes by one directory rename.

Step 5 of v0.14.0 git-cliff-provisioning (design "Download, verification and
extraction", "Publication", "Child process lifecycle" and "Time budgets and
retries"; design decisions Q01, Q06, Q07 and Q17; requirement clarifications
Q04 and Q14; plan decisions Q10 and Q18 and the plan risk pass).

- A first download prints the download and ready lines, records each child in
  the lock record and the owner file before it resumes, and publishes an entry
  holding only `git-cliff.exe` and `entry.json` by one directory rename.
- A digest mismatch removes staging without a retry; a reset then a success
  retries once after 5 s of fake time; two retryable failures report
  `download failed after 2 attempts`; a fatal failure is not retried; a retry
  needs time left in D after its delay.
- A denied write gives the permission diagnostic naming the directory.
- Code review round 1: a budget spent before the first attempt fails the
  download stage with no worker; a staging file the worker cannot write is
  the permission stage, not retried; a staging name collision keeps the
  existing directory and its contents, while a staging directory this call
  created is removed when its owner file cannot be written.
- Code review round 2: each worker request carries D's absolute expiry, and a
  worker that reaches its resume past it, after a delay at launcher entry or
  during its recording, never runs; a download line that cannot be written is
  the reporting stage.
- Retirement and publication faults, each followed by a second caller: an
  executable rename refused by a held guard changes nothing; a refused
  directory rename leaves the entry without its executable and the next caller
  moves the directory without a first rename; a parent death between the two
  renames leaves that same state, repaired once the parent is `DEAD`; an
  entry already without its executable is moved without a first rename; a
  failed publication leaves no entry and the next caller provisions afresh.
  No case renames or deletes a guarded executable.
"""

from __future__ import annotations

import dataclasses
import errno
import hashlib
import os
import secrets
import tempfile
from pathlib import Path

import pytest

from tests.unit.tools.release_workflow.git_cliff_children_fake import (
    SECOND,
    Child,
    ProvisionWorld,
    failed,
    outcome_line,
)
from tests.unit.tools.release_workflow.git_cliff_support import (
    CURRENT,
    STAND_IN_EXECUTABLE,
    deny_writes,
)
from tools.release_workflow.git_cliff.cache import (
    ENTRY_RECORD,
    EXECUTABLE,
    OWNER_FILE,
    Attempt,
    EntryRecord,
)
from tools.release_workflow.git_cliff.installation import retire_entry
from tools.release_workflow.git_cliff.manifest import download_url
from tools.release_workflow.git_cliff.messages import (
    ProvisioningError,
    Stage,
    downloading_line,
    ready_line,
)
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

STRANGER = ProcessIdentity(5300, 133_000_000_000_005_300)
_DEAD, _ALIVE, _UNKNOWN = ProcessState.DEAD, ProcessState.ALIVE, ProcessState.UNKNOWN


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProvisionWorld:
    """Give each case its own cache, clock, process states, guards and children."""
    return ProvisionWorld.build(tmp_path, monkeypatch)


def _fails(world: ProvisionWorld) -> ProvisioningError:
    """Provision and return the expected failure."""
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    return raised.value


def _second(world: ProvisionWorld) -> None:
    """Continue as another live caller."""
    world.current = SECOND
    world.states.states[SECOND] = _ALIVE


def test_a_first_download_records_each_child_in_the_lock_record_and_owner_file_before_it_resumes(world: ProvisionWorld) -> None:
    """The worker, then the staging probe, run in this caller's staging directory and are recorded twice each."""
    world.provision()
    worker, probe = world.children.launched
    assert worker.identity is not None
    assert probe.identity is not None
    staging = worker.request.cwd
    assert staging is not None
    assert staging.name.startswith(f".staging-{CURRENT.pid}-{CURRENT.created}-")
    assert (worker.recorded, probe.recorded) == (((worker.identity,),) * 2, ((worker.identity, probe.identity),) * 2)
    assert download_url(world.pin) in worker.request.arguments
    assert (probe.request.executable, probe.request.cwd, probe.request.deadline, probe.request.inherited) == (
        staging / EXECUTABLE, staging, 15, ())


def test_a_first_download_publishes_an_entry_of_two_files_by_one_directory_rename(world: ProvisionWorld) -> None:
    """Download and ready lines; one rename of staging; `git-cliff.exe` and its record, nothing else."""
    invocation = world.provision()
    staging = world.children.launched[0].request.cwd
    assert world.lines == [downloading_line(world.pin), ready_line(world.pin.version, world.entry)]
    assert [(source, target) for source, target in world.renames if target == world.entry] == [(staging, world.entry)]
    assert sorted(path.name for path in world.entry.iterdir()) == [ENTRY_RECORD, EXECUTABLE]
    record = EntryRecord.decode(world.layout.record(world.pin).read_bytes())
    assert (record.executable_sha256, record.executable_size, record.asset_sha256) == (
        hashlib.sha256(STAND_IN_EXECUTABLE).hexdigest(), len(STAND_IN_EXECUTABLE), world.pin.sha256)
    assert record.provisioned == world.clock.now().isoformat(timespec="seconds")
    assert (invocation.executable, world.attempt_state()) == (world.executable, {"staging": False, "lock": False})


def test_a_digest_mismatch_removes_staging_without_a_retry(world: ProvisionWorld) -> None:
    """A wrong asset is never downloaded again."""
    world.children.script("worker", Child(write=b"not the asset"))
    error = _fails(world)
    assert (error.stage, error.path, len(world.children.of("worker")), world.clock.sleeps) == (Stage.VERIFICATION, world.entry, 1, [])
    assert (world.attempt_state(), world.entry.exists()) == ({"staging": False, "lock": False}, False)


def test_a_reset_then_a_success_retries_once_after_5_seconds(world: ProvisionWorld) -> None:
    """The delay comes from D, and the download line is printed once."""
    world.children.script("worker", failed("retryable", "ConnectionResetError: reset by peer"), Child())
    world.provision()
    workers = world.children.of("worker")
    assert [(launched.request.expires, launched.remaining()) for launched in workers] == [(300, 300), (300, 295)]
    assert (world.clock.sleeps, world.lines[0], len(world.lines)) == ([5], downloading_line(world.pin), 2)


def test_two_retryable_failures_report_both_attempts(world: ProvisionWorld) -> None:
    """The second failure ends the stage with its own error."""
    world.children.script("worker", failed("retryable", "ConnectionResetError: reset"), failed("retryable", "TimeoutError: timed out"))
    error = _fails(world)
    assert (error.stage, error.detail, world.clock.sleeps) == (Stage.DOWNLOAD, "download failed after 2 attempts (TimeoutError: timed out)", [5])
    assert world.attempt_state() == {"staging": False, "lock": False}


@pytest.mark.parametrize(("child", "detail"), [
    (failed("fatal", "HTTPError: HTTP Error 404: Not Found"), "download failed after 1 attempt (HTTPError: HTTP Error 404: Not Found)"),
    (Child(status=1, stdout=b"Traceback (most recent call last):\n"), "download failed after 1 attempt (the download worker reported no outcome, status 1)"),
    (Child(stdout=b'{"outcome": "unknown"}\n'), "download failed after 1 attempt (the download worker reported no outcome, status 0)"),
])
def test_a_fatal_failure_or_a_missing_outcome_is_not_retried(world: ProvisionWorld, child: Child, detail: str) -> None:
    """Another HTTP status, a size overflow or a broken worker would not change on a second attempt."""
    world.children.script("worker", child)
    error = _fails(world)
    assert (error.stage, error.detail, world.clock.sleeps) == (Stage.DOWNLOAD, detail, [])


@pytest.mark.parametrize(("seconds", "late"), [(296.0, 0.0), (294.0, 2.0)])
def test_a_retry_needs_time_left_in_d_after_its_delay(world: ProvisionWorld, seconds: float, late: float) -> None:
    """A slow first attempt leaves no room for the delay, or a late wake-up spends what was left."""
    world.children.script("worker", Child(status=75, stdout=failed("retryable", "ConnectionResetError: reset").stdout, seconds=seconds))
    world.clock.oversleep = late
    error = _fails(world)
    assert error.detail == (
        "download failed after 1 attempt (ConnectionResetError: reset); no time remained for a retry within its budget of 300 s")
    assert len(world.children.of("worker")) == 1


def test_a_denied_write_gives_the_permission_diagnostic_naming_the_directory(world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """A read-only checkout without an entry cannot even take the lock: the checkout directory is named."""
    deny_writes(monkeypatch)
    error = _fails(world)
    assert (error.stage, error.path) == (Stage.PERMISSION, world.layout.tooling_root)
    assert "Grant write access to the named directory" in str(error)


def test_a_budget_spent_before_the_first_attempt_fails_without_a_worker(world: ProvisionWorld) -> None:
    """D is one absolute deadline: once spent, no worker starts with a nonpositive budget, staging and lock are released."""

    def slow_line(line: str) -> None:
        if "downloading" in line:
            world.clock.elapsed += 301

    world.on_line = slow_line
    error = _fails(world)
    assert (error.stage, error.detail) == (Stage.DOWNLOAD, "its budget of 300 s was spent before the first attempt")
    assert (world.children.launched, world.attempt_state()) == ([], {"staging": False, "lock": False})


def _slow_recording(world: ProvisionWorld) -> Child:
    """A worker whose recording takes the download budget and more."""

    def spend() -> None:
        world.clock.elapsed += 301

    return Child(before_record=spend)


@pytest.mark.parametrize("delay", ["launcher entry", "recording"])
def test_a_worker_reaching_its_resume_past_the_download_expiry_never_runs(world: ProvisionWorld, delay: str) -> None:
    """The request carries D's absolute expiry: time spent before the resume cannot restart it, and the worker never runs."""
    world.children.script("worker", Child(entry_seconds=301) if delay == "launcher entry" else _slow_recording(world))
    error = _fails(world)
    (worker,) = world.children.of("worker")
    assert (error.stage, error.detail) == (Stage.DOWNLOAD, "the download did not finish within its budget of 300 s")
    assert (worker.request.expires, worker.ran, world.attempt_state()) == (300, False, {"staging": False, "lock": False})


def test_a_download_line_that_cannot_be_written_is_the_reporting_stage(world: ProvisionWorld) -> None:
    """A broken standard error stops the installation as a provisioning failure; staging and lock are released."""

    def broken(line: str) -> None:
        if "downloading" in line:
            msg = "I/O operation on closed file."
            raise ValueError(msg)

    world.on_line = broken
    error = _fails(world)
    assert (error.stage, isinstance(error.__cause__, ValueError), world.children.launched) == (Stage.REPORTING, True, [])
    assert world.attempt_state() == {"staging": False, "lock": False}


def test_a_staging_file_the_worker_cannot_write_is_the_permission_stage(world: ProvisionWorld) -> None:
    """A local write failure reported by the worker names its directory and is not retried as a network failure."""
    refused = world.layout.version_dir(world.pin) / ".staging-gone" / world.pin.asset
    world.children.script("worker", Child(status=65, stdout=outcome_line("fatal", error="PermissionError: denied", path=str(refused))))
    error = _fails(world)
    assert (error.stage, error.path, len(world.children.of("worker")), world.clock.sleeps) == (
        Stage.PERMISSION, world.layout.version_dir(world.pin), 1, [])
    assert "the download worker reported PermissionError: denied" in error.detail
    assert world.attempt_state() == {"staging": False, "lock": False}


def test_a_staging_name_collision_keeps_the_existing_directory(world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """A directory this call did not create is never removed, whatever it holds."""

    def token(_count: int) -> str:
        return "5eed"

    monkeypatch.setattr(secrets, "token_hex", token)
    staging = world.layout.attempt_dir(world.pin, "staging", CURRENT, "5eed")
    staging.mkdir(parents=True)
    (staging / "sentinel").write_bytes(b"kept")
    error = _fails(world)
    assert (error.stage, (staging / "sentinel").read_bytes(), world.children.launched) == (Stage.PERMISSION, b"kept", [])


def test_an_owner_file_that_cannot_be_written_removes_the_staging_this_call_created(
        world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """The directory this call created is removed again; no worker starts and the lock is released."""
    original = Path.write_bytes

    def write_bytes(self: Path, data: bytes) -> int:
        if self.name.startswith(OWNER_FILE):
            raise PermissionError(errno.EACCES, "denied", str(self))
        return original(self, data)

    monkeypatch.setattr(Path, "write_bytes", write_bytes)
    error = _fails(world)
    assert (error.stage, error.path, world.children.launched) == (Stage.PERMISSION, world.layout.version_dir(world.pin), [])
    assert world.attempt_state() == {"staging": False, "lock": False}


def test_a_denied_staging_directory_names_the_version_directory(world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """The lock was taken; the staging directory cannot be created; the lock is released."""
    original = os.mkdir

    def mkdir(path: str | Path, *arguments: int) -> None:
        if Path(path).name.startswith(".staging-"):
            raise PermissionError(errno.EACCES, "denied", str(path))
        original(path, *arguments)

    monkeypatch.setattr(os, "mkdir", mkdir)
    error = _fails(world)
    assert (error.stage, error.path, world.attempt_state()) == (Stage.PERMISSION, world.layout.version_dir(world.pin), {"staging": False, "lock": False})


def test_a_recording_refused_for_permission_names_the_version_directory(world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """The lock record cannot be rewritten for the worker: the child never ran, staging and lock are released."""
    version = world.layout.version_dir(world.pin)

    def refuse(*_arguments: object, **_keywords: object) -> tuple[int, str]:
        raise PermissionError(errno.EACCES, "denied", str(version / ".lock-temporary.tmp"))

    world.children.script("worker", Child(before_record=lambda: monkeypatch.setattr(tempfile, "mkstemp", refuse)))
    error = _fails(world)
    assert (error.stage, error.path, world.children.launched[0].recorded) == (Stage.PERMISSION, version, None)
    assert world.attempt_state() == {"staging": False, "lock": False}


def test_an_archive_without_the_manifest_member_is_the_extraction_stage(world: ProvisionWorld) -> None:
    """The verified archive does not hold the member the manifest names."""
    world.pin = dataclasses.replace(world.pin, member="git-cliff-2.14.2/missing.exe")
    error = _fails(world)
    assert (error.stage, error.path, world.attempt_state()) == (Stage.EXTRACTION, world.entry, {"staging": False, "lock": False})


def test_a_staging_probe_reporting_another_version_is_the_probe_stage(world: ProvisionWorld) -> None:
    """The extracted binary must report the pin before it is published."""
    world.children.script("probe", Child(stdout=b"git-cliff 2.7.0\n"))
    error = _fails(world)
    assert (error.stage, error.detail) == (Stage.PROBE, "the version probe reported 'git-cliff 2.7.0' with status 0, expected 'git-cliff 2.14.2'")
    assert (world.attempt_state(), world.entry.exists()) == ({"staging": False, "lock": False}, False)


@pytest.mark.parametrize(("role", "child", "stage", "kept"), [
    ("worker", Child(containment=True), Stage.CONTAINMENT, {"staging": False, "lock": False}),
    ("worker", Child(hang=True), Stage.DOWNLOAD, {"staging": False, "lock": False}),
    ("probe", Child(hang=True), Stage.PROBE, {"staging": False, "lock": False}),
    ("worker", Child(unconfirmed="after-run", after=_UNKNOWN), Stage.CONTAINMENT, {"staging": True, "lock": True}),
])
def test_each_end_of_a_recorded_child_leaves_staging_and_the_lock_as_the_design_says(
        world: ProvisionWorld, role: str, child: Child, stage: Stage, kept: dict[str, bool]) -> None:
    """Every ended worker or staging probe releases both; an unconfirmed end retains the record and staging."""
    world.children.script(role, child)
    error = _fails(world)
    assert (error.stage, world.attempt_state()) == (stage, kept)


def _invalid_entry(world: ProvisionWorld) -> None:
    """Publish an entry, then make its record describe other bytes."""
    world.install()
    world.corrupt_record()


def test_an_executable_rename_refused_by_a_held_guard_changes_nothing(world: ProvisionWorld) -> None:
    """Another release runs the binary: in-use, the entry stays whole, and the next caller finds the same state."""
    _invalid_entry(world)
    guard = world.hold_guard(STRANGER)
    files = sorted(path.name for path in world.entry.iterdir())
    first = _fails(world)
    _second(world)
    second = _fails(world)
    assert (first.stage, second.stage, first.path) == (Stage.IN_USE, Stage.IN_USE, world.entry)
    assert (sorted(path.name for path in world.entry.iterdir()), world.executable.read_bytes()) == (files, STAND_IN_EXECUTABLE)
    assert (world.attempts(), world.attempts("retired")) == ([], [])
    guard.close()
    world.provision()
    assert len(world.attempts("retired")) == 1


def test_a_refused_directory_rename_leaves_the_entry_without_its_executable_for_the_next_caller(world: ProvisionWorld) -> None:
    """Another open handle inside: in-use; readers see no executable; the next caller only moves the directory."""
    _invalid_entry(world)
    world.busy.add(world.entry)
    error = _fails(world)
    names = sorted(path.name for path in world.entry.iterdir())
    assert (error.stage, len(names), EXECUTABLE in names, ENTRY_RECORD in names) == (Stage.IN_USE, 2, False, True)
    world.busy.clear()
    _second(world)
    world.renames.clear()
    world.provision()
    assert [source for source, _target in world.renames if source.name == EXECUTABLE] == []
    assert [target.name.startswith(".retired-") for source, target in world.renames if source == world.entry] == [True]
    assert world.executable.read_bytes() == STAND_IN_EXECUTABLE


def test_a_parent_death_between_the_two_renames_is_repaired_once_the_parent_is_dead(world: ProvisionWorld) -> None:
    """The same state as a refused directory rename, behind the dead holder's lock and staging."""
    _invalid_entry(world)

    def directory_retirement(source: Path, target: Path) -> bool:
        return source == world.entry and target.name.startswith(".retired-")

    world.die_on_rename = directory_retirement
    with world.dies():
        world.provision()
    world.die_on_rename = None
    assert (EXECUTABLE in [path.name for path in world.entry.iterdir()], len(world.attempts())) == (False, 1)
    staging = world.attempts()
    world.provision()
    assert (staging[0].exists(), world.executable.read_bytes(), len(world.attempts("retired"))) == (False, STAND_IN_EXECUTABLE, 1)


def test_an_entry_already_without_its_executable_is_moved_without_a_first_rename(world: ProvisionWorld) -> None:
    """A hand removal: readers treat the entry as absent, and retirement starts at the directory."""
    world.install()
    world.executable.unlink()
    world.provision()
    assert [source for source, _target in world.renames if source.name == EXECUTABLE] == []
    assert len(world.attempts("retired")) == 1


def test_a_failed_publication_after_retirement_leaves_no_entry_and_the_next_caller_provisions_afresh(world: ProvisionWorld) -> None:
    """Staging is removed, the old entry is already aside, and nothing half-published remains."""
    _invalid_entry(world)

    def publication(_source: Path, target: Path) -> bool:
        return target == world.entry

    world.refusals.append(publication)
    error = _fails(world)
    assert (error.stage, error.path, world.entry.exists()) == (Stage.PERMISSION, world.layout.version_dir(world.pin), False)
    assert (world.attempts(), len(world.attempts("retired"))) == ([], 1)
    world.refusals.clear()
    _second(world)
    world.provision()
    assert (len(world.children.of("worker")), world.executable.read_bytes()) == (2, STAND_IN_EXECUTABLE)


def test_retirement_without_an_entry_does_nothing(world: ProvisionWorld) -> None:
    """No `<triple>/`: nothing to retire and no rename."""
    retire_entry(world.layout, world.pin, Attempt("staging", CURRENT, "5eed"))
    assert world.renames == []


# eof
