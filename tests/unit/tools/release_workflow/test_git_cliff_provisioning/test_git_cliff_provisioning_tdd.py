"""A valid entry is reused silently and lock-free; an absent or invalid one is provisioned, or fails with its stage.

Step 5 of v0.14.0 git-cliff-provisioning (design "Target flow of git-cliff
provisioning", "Reuse check and the use guard" and "The provisioning entry
point for items 4 and 5"; design decisions Q03, Q07 and Q09; requirement
clarifications Q03 and Q04; plan decision Q18). Reuse opens one guard, reads
the record, hashes once and creates one probe holding the guard; it prints
nothing, takes no lock, starts no worker and writes nothing, also under the
write-denying helper. A truncated executable or a missing record leads to
provisioning online and to the download diagnostic offline. The entry point
also refuses a missing pin, reports an unreadable entry, an entry that cannot
be guarded after its publication and a lock record that cannot be removed,
reads `[git-cliff] version` and builds the production seams. A version
directory that recovery cannot list is the permission stage. A ready line that
cannot be written releases the new entry's guard (code review round 1) and is
the reporting stage, its error kept as cause (round 2). Step 6: a target whose
reuse function allows none, as an evidence candidate without its trust
record, skips both reuse checks and replaces a valid entry.
"""

from __future__ import annotations

import dataclasses
import errno
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.tools.release_workflow.git_cliff_children_fake import (
    RUNTIME,
    Child,
    ProvisionWorld,
    failed,
)
from tests.unit.tools.release_workflow.git_cliff_support import (
    STAND_IN_EXECUTABLE,
    deny_writes,
)
from tools.release_workflow import windows_guard
from tools.release_workflow.configuration import Configuration
from tools.release_workflow.git_cliff import provisioning
from tools.release_workflow.git_cliff.budget import resolve_budget
from tools.release_workflow.git_cliff.installation import manifest_target
from tools.release_workflow.git_cliff.messages import (
    ProvisioningError,
    Stage,
    ready_line,
)
from tools.release_workflow.schemas import ConfigValue
from tools.release_workflow.windows_child import (
    ContainmentError,
    require_supported_platform,
    run_contained,
)
from tools.release_workflow.windows_process import (
    current_identity,
    process_state,
    transition_mutex,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.unit.tools.release_workflow.git_cliff_support import FakeGuard


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProvisionWorld:
    """Give each case its own cache, clock, process states, guards and children."""
    return ProvisionWorld.build(tmp_path, monkeypatch)


def _offline(world: ProvisionWorld) -> None:
    """Make every download attempt fail as an unreachable host does."""
    world.children.script("worker", failed("retryable", "URLError: getaddrinfo failed"), failed("retryable", "URLError: getaddrinfo failed"))


def test_a_valid_entry_is_reused_silently_without_lock_network_or_write(world: ProvisionWorld, capsys: pytest.CaptureFixture[str]) -> None:
    """One guard, one record read, one hash and one probe inheriting the guard; nothing else."""
    world.install()
    before = world.tree()
    invocation = world.provision()
    guard: FakeGuard = world.opener.opened[0]
    (probe,) = world.children.launched
    assert (invocation.executable, invocation.version) == (world.executable, world.pin.version)
    assert (probe.role, probe.request.inherited, probe.request.deadline, probe.request.record) == ("probe", (guard.handle,), 15, None)
    assert (len(world.opener.opened), guard.hashed, guard.closed) == (1, 1, False)
    captured = capsys.readouterr()
    assert (world.lines, captured.out, captured.err) == ([], "", "")
    assert (world.mutex.entries, world.tree(), world.layout.lock_path(world.pin).exists()) == ([], before, False)


def test_a_read_only_checkout_reuses_a_valid_entry_without_any_write_attempt(world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reuse needs read access only: the write-denying helper records no attempt."""
    world.install()
    denial = deny_writes(monkeypatch)
    invocation = world.provision()
    assert (invocation.executable, denial.attempts, world.children.of("worker")) == (world.executable, [], [])
    assert world.children.launched[0].request.inherited == (world.opener.opened[0].handle,)


def _truncate(world: ProvisionWorld) -> None:
    """Cut the cached executable short."""
    world.executable.write_bytes(STAND_IN_EXECUTABLE[:100])


def _drop_record(world: ProvisionWorld) -> None:
    """Remove the entry record."""
    world.layout.record(world.pin).unlink()


@pytest.mark.parametrize("damage", [_truncate, _drop_record])
def test_an_invalid_entry_is_provisioned_again_online(world: ProvisionWorld, damage: Callable[[ProvisionWorld], None]) -> None:
    """The entry fails before any probe runs, is moved aside under the lock, and a new one is published."""
    world.install()
    damage(world)
    invocation = world.provision()
    assert [launched.role for launched in world.children.launched] == ["worker", "probe"]
    assert world.lines[-1] == ready_line(world.pin.version, world.entry)
    assert (invocation.executable, world.executable.read_bytes()) == (world.executable, STAND_IN_EXECUTABLE)
    assert len(world.attempts("retired")) == 1


@pytest.mark.parametrize("damage", [_truncate, _drop_record])
def test_an_invalid_entry_offline_gives_the_download_diagnostic(world: ProvisionWorld, damage: Callable[[ProvisionWorld], None]) -> None:
    """Without the network, the stage is download and the old entry is left as it was."""
    world.install()
    damage(world)
    _offline(world)
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.DOWNLOAD, world.entry)
    assert "download failed after 2 attempts (URLError: getaddrinfo failed)" in str(raised.value)
    assert (world.attempts(), world.layout.lock_path(world.pin).exists(), world.entry.is_dir()) == ([], False, True)


def test_a_missing_pin_is_the_configuration_stage_before_any_work(world: ProvisionWorld) -> None:
    """No admitted pin means no default: nothing is checked, locked or started."""
    with pytest.raises(ProvisioningError) as raised:
        provisioning.provision(world.layout.tooling_root, None, resolve_budget({}), seams=world.seams(), caller="engine")
    assert (raised.value.stage, raised.value.version, raised.value.path) == (Stage.CONFIGURATION, None, world.layout.root)
    assert (world.opener.opened, world.children.launched, world.tree()) == ([], [], {})


def test_a_reuse_probe_refused_by_containment_closes_the_guard(world: ProvisionWorld) -> None:
    """No probe child exists, so the guard is released and the stage is containment."""
    world.install()
    world.children.script("probe", Child(containment=True))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.CONTAINMENT, world.entry)
    assert isinstance(raised.value.__cause__, ContainmentError)
    assert world.opener.opened[0].closed


def test_an_unreadable_entry_is_the_extraction_stage(world: ProvisionWorld) -> None:
    """A guard that cannot open for another reason than a missing file names the entry to delete."""
    world.install()
    world.guard_errors[0] = PermissionError(errno.EACCES, "access denied", str(world.executable))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.EXTRACTION, world.entry)
    assert "the entry cannot be read" in raised.value.detail


def test_a_published_entry_that_cannot_be_guarded_fails_once_without_the_ready_line(world: ProvisionWorld) -> None:
    """Plan Q18: the actual cause and path under the extraction stage, no rerun, no ready line."""
    world.guard_errors[2] = FileNotFoundError(errno.ENOENT, "removed meanwhile", str(world.executable))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.EXTRACTION, world.entry)
    assert "the entry just published cannot be guarded" in raised.value.detail
    assert (len(world.children.of("worker")), world.lines[-1].endswith("from GitHub")) == (1, True)


def test_a_ready_line_that_cannot_be_written_releases_the_new_guard(world: ProvisionWorld) -> None:
    """The broken stream is the reporting stage, status 2, with its cause; the published entry stays replaceable afterwards."""

    def broken(line: str) -> None:
        if "ready at" in line:
            msg = "standard error is closed"
            raise OSError(msg)

    world.on_line = broken
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.exit_code, raised.value.path) == (Stage.REPORTING, 2, world.entry)
    assert str(raised.value.__cause__) == "standard error is closed"
    assert world.opener.opened[-1].closed
    world.executable.rename(world.entry / "moved.exe")
    assert (world.entry / "moved.exe").read_bytes() == STAND_IN_EXECUTABLE


def _refuse_lock_removal(world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """Refuse the removal of the lock record, as a checkout turned read-only would."""
    original = os.unlink
    lock = world.layout.lock_path(world.pin)

    def unlink(path: str | Path, **keywords: Any) -> None:
        if Path(path) == lock:
            raise PermissionError(errno.EACCES, "denied", str(path))
        original(path, **keywords)

    monkeypatch.setattr(os, "unlink", unlink)


def test_a_lock_record_that_cannot_be_removed_after_provisioning_is_the_lock_wait_stage(
        world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """The entry is published, but the caller reports the record it leaves behind instead of a ready line."""
    _refuse_lock_removal(world, monkeypatch)
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.LOCK_WAIT, world.layout.lock_path(world.pin))
    assert "the lock record could not be removed" in raised.value.detail
    assert (world.executable.exists(), world.lines[-1].startswith("git-cliff 2.14.2: downloading")) == (True, True)


def test_a_lock_record_that_cannot_be_removed_after_a_valid_recheck_closes_the_guard(
        world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """The recheck's guard is not handed out when the lock cannot be released."""
    world.install()
    world.guard_errors[0] = FileNotFoundError(errno.ENOENT, "not yet published", str(world.executable))
    _refuse_lock_removal(world, monkeypatch)
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert raised.value.stage is Stage.LOCK_WAIT
    assert world.opener.opened[0].closed


def test_a_lock_record_that_cannot_be_removed_after_a_failure_is_noted_on_that_failure(
        world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """The original stage stays; the record left behind is added as a note."""
    _refuse_lock_removal(world, monkeypatch)
    world.children.script("worker", failed("fatal", "HTTPError: HTTP Error 404: Not Found"))
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert raised.value.stage is Stage.DOWNLOAD
    assert any("the lock record could not be removed" in note for note in raised.value.__notes__)


def test_a_version_directory_that_cannot_be_listed_for_recovery_is_the_permission_stage(
        world: ProvisionWorld, monkeypatch: pytest.MonkeyPatch) -> None:
    """Recovery lists the version directory once under the lock; a refusal names the cache directory and releases the lock."""
    original = os.scandir
    version = world.layout.version_dir(world.pin)

    def scandir(path: str | Path = ".") -> object:
        if Path(path) == version:
            raise PermissionError(errno.EACCES, "denied", str(path))
        return original(path)

    monkeypatch.setattr(os, "scandir", scandir)
    with pytest.raises(ProvisioningError) as raised:
        world.provision()
    assert (raised.value.stage, raised.value.path) == (Stage.PERMISSION, version.parent)
    assert (world.children.launched, world.layout.lock_path(world.pin).exists()) == ([], False)


def _configuration(sections: dict[str, dict[str, ConfigValue]]) -> Configuration:
    """Build a validated configuration holding these sections."""
    return Configuration(Path("C:/project/.release.ini"), sections)


def test_configured_pin_reads_the_validated_version_or_none() -> None:
    """The declared or defaulted value, None without a value or without the section."""
    declared = ConfigValue(Path("C:/project/.release.ini"), "git-cliff", "version", "2.14.2", "2.14.2", defaulted=False)
    assert provisioning.configured_pin(_configuration({"git-cliff": {"version": declared}})) == "2.14.2"
    assert provisioning.configured_pin(_configuration({"git-cliff": {}})) is None
    assert provisioning.configured_pin(_configuration({})) is None


def test_production_seams_bind_the_windows_layer_without_calling_it(capsys: pytest.CaptureFixture[str]) -> None:
    """The real launcher, guard, liveness probe, identity, mutex, clock and platform check; stderr gets whole lines."""
    seams = provisioning.production_seams(RUNTIME)
    assert (seams.launch, seams.open_guard, seams.process_state, seams.current_identity, seams.mutex, seams.platform_check) == (
        run_contained, windows_guard.open_guard, process_state, current_identity, transition_mutex, require_supported_platform)
    assert seams.runtime == RUNTIME
    assert seams.now().utcoffset() is not None
    seams.stderr("git-cliff 2.14.2: ready at C:/x")
    assert capsys.readouterr() == ("", "git-cliff 2.14.2: ready at C:/x\n")


def _no_reuse() -> str | None:
    """Allow no reuse at any check, as an evidence candidate without its trust record."""
    return None


def test_a_target_that_allows_no_reuse_is_installed_again_over_a_valid_entry(world: ProvisionWorld) -> None:
    """Step 6: `provision_target` runs the same flow for any target; one whose reuse function allows none skips both reuse checks."""
    world.install()
    target = dataclasses.replace(manifest_target(world.pin), reuse=_no_reuse)
    invocation = provisioning.provision_target(world.layout, target, resolve_budget({}), seams=world.seams(), caller="harness")
    assert [launch.role for launch in world.children.launched] == ["worker", "probe"]
    assert world.opener.opened[0].path == world.executable
    assert len(world.opener.opened) == 1
    assert world.attempts("retired") != []
    invocation.close()


# eof
