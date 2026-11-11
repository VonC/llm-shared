"""The standalone transition: plan, lock, evidence check, ordered writes, cleanup.

Step 4 of v0.14.0 version-sources: a plan failure before the lock leaves no
artifact home, lock record or evidence (status 2); a held lock fails with
status 1 naming its owner. Under the lock, completed standalone residue is
removed with a warning, while interrupted, unreadable or another lifecycle's
evidence stops with status 2, even when the plan is empty; a manifest naming a
copy outside its directory, or a directory that can be neither read nor
listed, is unreadable and deletes nothing (code review, step 4 round 1). An empty locked plan
reports `unchanged`. Evidence that cannot be written fails with status 1
before any source write. A successful run writes in path order with
`version.txt` last, verifies in a fresh view, marks the evidence complete,
deletes it and releases the lock, reporting each old and new value. The
default ports are the production boundaries.
"""

from __future__ import annotations

import os
import re
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.acceptance_support import hold, snapshot
from tests.unit.tools.release_workflow.version_support import (
    EVIDENCE_NAME,
    FIXED_NOW,
    PATTERN_INI,
    TARGET,
    Faults,
    ViewLog,
    declare_evidence,
    lines_file,
    source_bytes,
    version_project,
    version_txt,
)
from tools.release_workflow.managed_files import replace_bytes
from tools.release_workflow.operation_lock import OperationLock
from tools.release_workflow.sources.model import FileView, SourceChange, SourceError
from tools.release_workflow.version_evidence import (
    STANDALONE,
    EvidenceError,
    EvidenceFile,
    EvidenceManifest,
    EvidenceState,
    remove_managed,
)
from tools.release_workflow.version_transition import (
    TransitionError,
    TransitionOutcome,
    TransitionPorts,
    set_versions,
)
from tools.release_workflow.windows_process import process_state

if TYPE_CHECKING:
    from collections.abc import Iterator

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.sources.model import VersionInputs
    from tools.release_workflow.version_transition import TransitionResult

_PREFLIGHT = 2
_EXECUTION = 1
_AT_TARGET = {"version.txt": version_txt("0.14.0"), "cicd/config/.env": lines_file(["APP_SERVICE_VERSION=0.14.0"])}
_OLD = {"version.txt": version_txt("0.13.0"), "cicd/config/.env": lines_file(["APP_SERVICE_VERSION=0.13.0"])}


def _manifest(owner: str, state: EvidenceState) -> bytes:
    """Encode a manifest with no file, as a stopped transition left it."""
    return EvidenceManifest(owner, "0.14.0", state, FIXED_NOW.isoformat(), ()).encode()


def test_default_ports_are_the_production_boundaries() -> None:
    """Managed replacement and removal, the operation lock, local time with offset, this process."""
    ports = TransitionPorts()
    assert (ports.replace, ports.remove, ports.lock_factory, ports.probe, ports.view) == (
        replace_bytes, remove_managed, OperationLock, process_state, FileView)
    assert ports.clock().utcoffset() is not None
    assert ports.pid() == os.getpid()


def _no_lock_and_no_evidence(inputs: VersionInputs) -> bool:
    """Tell whether the home holds neither a lock record nor version evidence."""
    home = inputs.artifacts.home
    return not any(path.name.startswith(("a.release-operation.lock", "a.version-transition.")) for path in home.iterdir())


@pytest.mark.parametrize(("ini", "files", "message"), [
    (PATTERN_INI, {"version.txt": version_txt("0.13.0"), "cicd/config/.env": lines_file(["OTHER=1"])}, "matches nothing"),
    (PATTERN_INI + PATTERN_INI.replace("cicd-env", "copy"), _OLD, "overlap"),
    (PATTERN_INI.replace("snapshot", "release-only"),
     {"version.txt": version_txt("0.14.0"), "cicd/config/.env": lines_file(["APP_SERVICE_VERSION=0.15.0"])}, "higher than the target"),
])
def test_plan_failure_leaves_no_artifact_home_lock_or_evidence(git_sandbox: GitSandbox, lock_facts: LockFacts,
                                                                ini: str, files: dict[str, bytes], message: str) -> None:
    """Unsupported arrangements, overlapping claims and release-only refusals fail before any side effect."""
    inputs = version_project(git_sandbox, files, ini)
    before = snapshot(inputs.project.root)
    with pytest.raises(SourceError, match=message) as caught:
        set_versions(inputs, TARGET, ports=Faults(inputs.artifacts.home).ports(lock_facts.probe))
    assert caught.value.exit_code == _PREFLIGHT
    assert snapshot(inputs.project.root) == before


def test_held_lock_fails_naming_its_owner(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """Another live operation keeps the project: status 1, no source written."""
    inputs = version_project(git_sandbox, _OLD, PATTERN_INI)
    hold(inputs.project.root, lock_facts, 77)
    with pytest.raises(TransitionError, match="pid=77") as caught:
        set_versions(inputs, TARGET, ports=Faults(inputs.artifacts.home).ports(lock_facts.probe))
    assert caught.value.exit_code == _EXECUTION
    assert source_bytes(inputs.project.root, list(_OLD)) == _OLD


def test_completed_standalone_residue_is_removed_with_a_warning(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """Residue of a finished transition does not stop the next one."""
    inputs = version_project(git_sandbox, _OLD, PATTERN_INI)
    residue = declare_evidence(inputs.artifacts.home, "a.version-transition.20261108T090000+0100-7", _manifest(STANDALONE, EvidenceState.COMPLETE))
    result = set_versions(inputs, TARGET, ports=Faults(inputs.artifacts.home).ports(lock_facts.probe))
    assert result.outcome is TransitionOutcome.APPLIED
    assert any(residue.name in diagnostic and "removed" in diagnostic for diagnostic in result.diagnostics)
    assert not residue.exists()


@pytest.mark.parametrize("manifest", [
    _manifest(STANDALONE, EvidenceState.WRITING), _manifest(STANDALONE, EvidenceState.RESTORATION_INCOMPLETE),
    _manifest("release-9", EvidenceState.COMPLETE), b"{not json",
])
def test_unfinished_evidence_stops_even_an_empty_plan(git_sandbox: GitSandbox, lock_facts: LockFacts, manifest: bytes) -> None:
    """Interrupted, unreadable or foreign evidence stops with status 2, naming its directory."""
    inputs = version_project(git_sandbox, _AT_TARGET, PATTERN_INI)
    evidence = declare_evidence(inputs.artifacts.home, "a.version-transition.20261108T090000+0100-7", manifest)
    with pytest.raises(TransitionError, match=re.escape(evidence.name)) as caught:
        set_versions(inputs, TARGET, ports=Faults(inputs.artifacts.home).ports(lock_facts.probe))
    assert caught.value.exit_code == _PREFLIGHT
    assert (evidence / "manifest.json").read_bytes() == manifest
    assert not (inputs.artifacts.home / "a.release-operation.lock").exists()


@pytest.mark.parametrize("copy", ["../../version.txt", "absolute"])
def test_residue_with_an_unsafe_copy_name_stops_and_deletes_nothing(git_sandbox: GitSandbox, lock_facts: LockFacts, copy: str) -> None:
    """A completed manifest naming a copy outside its directory is unreadable: status 2, every byte kept."""
    inputs = version_project(git_sandbox, _OLD, PATTERN_INI)
    root = inputs.project.root
    name = str(root / "version.txt") if copy == "absolute" else copy
    entry = EvidenceFile("version.txt", None, exists=True, copy=name)
    manifest = EvidenceManifest(STANDALONE, "0.14.0", EvidenceState.COMPLETE, FIXED_NOW.isoformat(), (entry,)).encode()
    evidence = declare_evidence(inputs.artifacts.home, "a.version-transition.20261108T090000+0100-7", manifest)
    before = snapshot(root)
    with pytest.raises(TransitionError, match=re.escape(evidence.name) + ".*unreadable") as caught:
        set_versions(inputs, TARGET, ports=Faults(inputs.artifacts.home).ports(lock_facts.probe))
    assert caught.value.exit_code == _PREFLIGHT
    assert snapshot(root) == before


def test_evidence_that_cannot_be_read_or_listed_stops_the_transition(git_sandbox: GitSandbox, lock_facts: LockFacts,
                                                                     monkeypatch: pytest.MonkeyPatch) -> None:
    """A manifest read and a directory listing both denied: unreadable evidence, status 2, lock released."""
    inputs = version_project(git_sandbox, _OLD, PATTERN_INI)
    evidence = declare_evidence(inputs.artifacts.home, "a.version-transition.20261108T090000+0100-7", b"{}")
    read_bytes, iterdir = Path.read_bytes, Path.iterdir

    def denied_read(path: Path) -> bytes:
        if path == evidence / "manifest.json":
            msg = f"{path} is denied"
            raise PermissionError(msg)
        return read_bytes(path)

    def denied_listing(path: Path) -> Iterator[Path]:
        if path == evidence:
            msg = f"{path} is denied"
            raise PermissionError(msg)
        return iterdir(path)

    monkeypatch.setattr(Path, "read_bytes", denied_read)
    monkeypatch.setattr(Path, "iterdir", denied_listing)
    with pytest.raises(TransitionError, match=re.escape(evidence.name) + ".*unreadable") as caught:
        set_versions(inputs, TARGET, ports=Faults(inputs.artifacts.home).ports(lock_facts.probe))
    assert caught.value.exit_code == _PREFLIGHT
    assert source_bytes(inputs.project.root, list(_OLD)) == _OLD
    assert not (inputs.artifacts.home / "a.release-operation.lock").exists()


def test_empty_locked_plan_reports_unchanged(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """A same-target run takes and releases the lock and writes no source and no evidence."""
    inputs = version_project(git_sandbox, _AT_TARGET, PATTERN_INI)
    faults = Faults(inputs.artifacts.home)
    result = set_versions(inputs, TARGET, ports=faults.ports(lock_facts.probe))
    assert (result.outcome, result.status, result.changes, result.restore) == (TransitionOutcome.UNCHANGED, 0, (), None)
    assert (faults.sources, faults.evidence) == ([], [])
    assert source_bytes(inputs.project.root, list(_AT_TARGET)) == _AT_TARGET
    assert _no_lock_and_no_evidence(inputs)


def test_unwritable_evidence_fails_before_any_source_write(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """Partial evidence is removed, the lock released, and the status is 1."""
    inputs = version_project(git_sandbox, _OLD, PATTERN_INI)
    faults = Faults(inputs.artifacts.home, fail_when=lambda path, _content: path.name == "original.2")
    with pytest.raises(EvidenceError, match=r"original\.2") as caught:
        set_versions(inputs, TARGET, ports=faults.ports(lock_facts.probe))
    assert caught.value.exit_code == _EXECUTION
    assert faults.sources == []
    assert source_bytes(inputs.project.root, list(_OLD)) == _OLD
    assert _no_lock_and_no_evidence(inputs)


_ORDER_INI = ("[source:b]\nfile = b.env\npattern = ^B=(.+)$\nform = core\n"
              "[source:a]\nfile = a.env\npattern = ^A=(.+)$\nform = snapshot\n")
_ORDER_FILES = {"version.txt": version_txt("0.13.0 -- Title", "Notes\n"), "b.env": lines_file(["B=0.13.0"]), "a.env": lines_file(["A=0.13.0"])}


def _ordered_run(git_sandbox: GitSandbox, lock_facts: LockFacts) -> tuple[VersionInputs, Faults, ViewLog, TransitionResult]:
    """Set 0.14.0 over the anchor and two pattern files, recording writes and views."""
    inputs = version_project(git_sandbox, _ORDER_FILES, _ORDER_INI)
    faults = Faults(inputs.artifacts.home)
    views = ViewLog()
    result = set_versions(inputs, TARGET, ports=replace(faults.ports(lock_facts.probe), view=views))
    return inputs, faults, views, result


def test_successful_run_writes_in_path_order_with_the_anchor_last(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """Each file once, `version.txt` last; every change carries its old and new value."""
    inputs, faults, _views, result = _ordered_run(git_sandbox, lock_facts)
    root = inputs.project.root
    assert (result.outcome, result.status) == (TransitionOutcome.APPLIED, 0)
    assert faults.sources == [root / "a.env", root / "b.env", root / "version.txt"]
    assert result.changes == (
        SourceChange(root / "a.env", "source:a", "pattern", "0.13.0", "0.14.0"),
        SourceChange(root / "b.env", "source:b", "pattern", "0.13.0", "0.14.0"),
        SourceChange(root / "version.txt", "version", "anchor", "0.13.0", "0.14.0"),
    )
    assert source_bytes(root, list(_ORDER_FILES)) == {"version.txt": version_txt("0.14.0 -- Title", "Notes\n"),
                                                       "b.env": lines_file(["B=0.14.0"]), "a.env": lines_file(["A=0.14.0"])}


def test_successful_run_verifies_marks_complete_then_cleans_up(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """One view per phase, verification included; the `complete` marker precedes every removal."""
    inputs, faults, views, _result = _ordered_run(git_sandbox, lock_facts)
    path = inputs.project.root / "a.env"
    assert [view.loads(path) for view in views.views] == [1, 1, 1, 1]
    states = [EvidenceManifest.decode(content).state for name, content in faults.evidence if name == "manifest.json"]
    assert states == [EvidenceState.WRITING, EvidenceState.COMPLETE]
    assert faults.removed == ["original.1", "original.2", "original.3", "manifest.json", EVIDENCE_NAME]
    assert _no_lock_and_no_evidence(inputs)


# eof
