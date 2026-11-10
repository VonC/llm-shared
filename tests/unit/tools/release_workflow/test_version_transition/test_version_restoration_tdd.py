"""Restoration before the completion boundary, and cleanup faults after it.

Step 4 of v0.14.0 version-sources: for every fixture set of the restoration
registry (anchor, pattern and one file with two disjoint claims; Step 5 adds
the Python virtual and editable roots with their `uv.lock`, so `pyproject.toml`
and `uv.lock` are restored byte for byte too; Steps 6 and 7 add theirs), a
failure at each source write restores every replaced file,
verifies it, deletes the evidence and returns status 1. A concurrent change
before a replacement, a failed verification and a failed completion marker
restore too. A restoration that cannot finish returns status 3, keeps the
evidence as `restoration-incomplete` and names each unrestored source with its
retained copy, whatever secondary failure follows. After the durable
`complete` marker, a cleanup or lock-release failure returns `applied with
cleanup failed` (status 1) with the new versions in place, and the next `set`
removes the completed residue. `writing` evidence stops a same-target rerun,
and an `unchanged` run whose lock release fails stops with status 1 (code
review, step 4 round 1).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    EVIDENCE_NAME,
    FIXED_NOW,
    RESTORATION_FIXTURES,
    TARGET,
    Faults,
    declare_evidence,
    lines_file,
    source_bytes,
    version_project,
    version_txt,
)
from tools.release_workflow.operation_lock import OperationLock, OperationLockError
from tools.release_workflow.sources.model import FileView
from tools.release_workflow.version_evidence import (
    STANDALONE,
    EvidenceManifest,
    EvidenceState,
)
from tools.release_workflow.version_transition import (
    TransitionError,
    TransitionOutcome,
    set_versions,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.artifacts import PreparedArtifacts
    from tools.release_workflow.sources.model import VersionInputs
    from tools.release_workflow.version_transition import TransitionPorts
    from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

_RESTORED = 1
_EXECUTION = 1
_INCOMPLETE = 3
_PREFLIGHT = 2
_PATTERN = RESTORATION_FIXTURES["pattern"]
_ENV = "cicd/config/.env"
_NEW = {"version.txt": version_txt("0.14.0"), _ENV: lines_file(["A=1", "APP_SERVICE_VERSION=0.14.0"], newline="\r\n")}
_POSITIONS = [(name, position) for name, fixture in RESTORATION_FIXTURES.items() for position in range(fixture.writes)]


@dataclass
class _ReleaseFails:
    """A real operation lock whose release fails, leaving its record."""

    inner: OperationLock

    def acquire(self) -> _ReleaseFails:
        """Acquire the real lock."""
        self.inner.acquire()
        return self

    def release(self) -> None:
        """Fail as a lock record that cannot be removed."""
        msg = "a.release-operation.lock: injected release failure"
        raise OperationLockError(msg)


def _release_fails(artifacts: PreparedArtifacts, *, probe: Callable[[ProcessIdentity], ProcessState]) -> _ReleaseFails:
    """Build a lock whose release fails."""
    return _ReleaseFails(OperationLock(artifacts, probe=probe))


class _UnreadableView(FileView):
    """A view that cannot read one path, as a file an editor holds open."""

    def __init__(self, unreadable: Path) -> None:
        """Remember the path that fails."""
        super().__init__()
        self._unreadable = unreadable

    def read(self, path: Path) -> bytes | None:
        """Fail for the chosen path, read any other."""
        if path == self._unreadable:
            msg = f"{path} is locked"
            raise PermissionError(msg)
        return super().read(path)


@dataclass
class _UnreadableFrom:
    """A view factory whose views from a given one on cannot read one path."""

    unreadable: Path
    first: int
    created: int = 0

    def __call__(self) -> FileView:
        """Create an ordinary view, or an unreadable one from the chosen view on."""
        self.created += 1
        return _UnreadableView(self.unreadable) if self.created > self.first else FileView()


def _pattern_project(git_sandbox: GitSandbox, files: dict[str, bytes] | None = None) -> VersionInputs:
    """Load the pattern fixture set, or other files with its declaration."""
    return version_project(git_sandbox, dict(_PATTERN.files) if files is None else files, _PATTERN.ini)


def _run(inputs: VersionInputs, ports: TransitionPorts) -> tuple[TransitionOutcome, int, tuple[str, ...]]:
    """Set 0.14.0 and return the outcome, status and diagnostics."""
    result = set_versions(inputs, TARGET, ports=ports)
    return result.outcome, result.status, result.diagnostics


def _clean(inputs: VersionInputs) -> bool:
    """Tell whether the home holds neither a lock record nor version evidence."""
    return not any(path.name.startswith(("a.release-operation.lock", "a.version-transition.")) for path in inputs.artifacts.home.iterdir())


@pytest.mark.parametrize(("name", "position"), _POSITIONS)
def test_failure_at_each_write_restores_every_replaced_file(git_sandbox: GitSandbox, lock_facts: LockFacts, name: str, position: int) -> None:
    """Every fixture set, every write position: restored, verified, evidence deleted, status 1."""
    fixture = RESTORATION_FIXTURES[name]
    inputs = version_project(git_sandbox, fixture.files, fixture.ini)
    faults = Faults(inputs.artifacts.home, fail_write=position)
    outcome, status, diagnostics = _run(inputs, faults.ports(lock_facts.probe))
    assert (outcome, status) == (TransitionOutcome.RESTORED, _RESTORED)
    assert source_bytes(inputs.project.root, list(fixture.files)) == dict(fixture.files)
    assert sorted(faults.sources[position + 1:]) == sorted(faults.sources[:position])
    assert any("injected failure" in diagnostic for diagnostic in diagnostics)
    assert any("restored" in diagnostic for diagnostic in diagnostics)
    assert _clean(inputs)


def test_concurrent_change_before_a_replacement_restores_and_keeps_it(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """Another writer's bytes are never overwritten; what this run replaced is restored."""
    inputs = _pattern_project(git_sandbox)
    anchor = inputs.project.root / "version.txt"
    foreign = version_txt("9.9.9")

    def other_writer(position: int) -> None:
        if position == 0:
            anchor.write_bytes(foreign)

    outcome, status, diagnostics = _run(inputs, Faults(inputs.artifacts.home, after_write=other_writer).ports(lock_facts.probe))
    assert (outcome, status) == (TransitionOutcome.RESTORED, _RESTORED)
    assert source_bytes(inputs.project.root, [_ENV, "version.txt"]) == {_ENV: _PATTERN.files[_ENV], "version.txt": foreign}
    assert any("changed since it was captured" in diagnostic for diagnostic in diagnostics)
    assert _clean(inputs)


def test_failed_verification_restores(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """A source not holding its expected value after the writes restores every file."""
    inputs = _pattern_project(git_sandbox)
    faults = Faults(inputs.artifacts.home, tamper=lambda _path, content: content.replace(b"0.14.0", b"0.14.9"))
    outcome, status, diagnostics = _run(inputs, faults.ports(lock_facts.probe))
    assert (outcome, status) == (TransitionOutcome.RESTORED, _RESTORED)
    assert source_bytes(inputs.project.root, list(_PATTERN.files)) == dict(_PATTERN.files)
    assert any("verification" in diagnostic for diagnostic in diagnostics)


def test_failed_completion_marker_restores(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """The marker is part of the transition: until it is durable, failures restore."""
    inputs = _pattern_project(git_sandbox)
    faults = Faults(inputs.artifacts.home, fail_when=lambda path, content: path.name == "manifest.json" and b'"complete"' in content)
    outcome, status, _diagnostics = _run(inputs, faults.ports(lock_facts.probe))
    assert (outcome, status) == (TransitionOutcome.RESTORED, _RESTORED)
    assert source_bytes(inputs.project.root, list(_PATTERN.files)) == dict(_PATTERN.files)
    assert _clean(inputs)


def test_restored_sources_with_undeletable_evidence_name_it(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """A restoration that cannot delete its evidence still reports status 1 and names what remains."""
    inputs = _pattern_project(git_sandbox)
    outcome, status, diagnostics = _run(inputs, Faults(inputs.artifacts.home, fail_write=1, fail_remove="manifest.json").ports(lock_facts.probe))
    assert (outcome, status) == (TransitionOutcome.RESTORED, _RESTORED)
    assert source_bytes(inputs.project.root, list(_PATTERN.files)) == dict(_PATTERN.files)
    assert any(EVIDENCE_NAME in diagnostic and "remove it" in diagnostic for diagnostic in diagnostics)


@pytest.mark.parametrize("secondary", ["none", "release", "mark", "unreadable"])
def test_incomplete_restoration_returns_status_3(git_sandbox: GitSandbox, lock_facts: LockFacts, secondary: str) -> None:
    """The unrestored source and its retained copy are named; secondary failures only add diagnostics."""
    inputs = _pattern_project(git_sandbox)
    root = inputs.project.root
    original = _PATTERN.files[_ENV]
    mark = secondary == "mark"

    def fails(path: Path, content: bytes) -> bool:
        restoring = path.name == ".env" and content == original and secondary != "unreadable"
        return restoring or (mark and path.name == "manifest.json" and b"restoration-incomplete" in content)

    ports = Faults(inputs.artifacts.home, fail_write=1, fail_when=fails).ports(lock_facts.probe)
    if secondary == "release":
        ports = replace(ports, lock_factory=_release_fails)
    if secondary == "unreadable":
        ports = replace(ports, view=_UnreadableFrom(root / _ENV, first=3))
    outcome, status, diagnostics = _run(inputs, ports)
    assert (outcome, status) == (TransitionOutcome.RESTORATION_INCOMPLETE, _INCOMPLETE)
    copy = inputs.artifacts.home / EVIDENCE_NAME / "original.2"
    assert any(str(root / _ENV) in diagnostic and str(copy) in diagnostic for diagnostic in diagnostics)
    assert copy.read_bytes() == original
    assert not any("every replaced source was restored" in diagnostic for diagnostic in diagnostics)
    state = EvidenceManifest.decode((copy.parent / "manifest.json").read_bytes()).state
    assert state is (EvidenceState.WRITING if mark else EvidenceState.RESTORATION_INCOMPLETE)
    expected = {"none": None, "release": "release", "mark": "manifest", "unreadable": None}[secondary]
    assert expected is None or any(expected in diagnostic for diagnostic in diagnostics[1:])


def test_writing_evidence_after_the_last_replacement_stops_a_same_target_rerun(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """Synchronized sources prove nothing while the evidence still says `writing`."""
    inputs = _pattern_project(git_sandbox, _NEW)
    manifest = EvidenceManifest(STANDALONE, "0.14.0", EvidenceState.WRITING, FIXED_NOW.isoformat(), ()).encode()
    evidence = declare_evidence(inputs.artifacts.home, EVIDENCE_NAME, manifest, {"original.1": _PATTERN.files["version.txt"]})
    with pytest.raises(TransitionError, match=re.escape(EVIDENCE_NAME)) as caught:
        set_versions(inputs, TARGET, ports=Faults(inputs.artifacts.home).ports(lock_facts.probe))
    assert caught.value.exit_code == _PREFLIGHT
    assert evidence.is_dir()


@pytest.mark.parametrize(("failing", "residue"), [
    ("original.1", "with its copies and manifest"), ("manifest.json", "evidence manifest"), (EVIDENCE_NAME, "empty evidence directory"),
])
def test_cleanup_failure_after_completion_keeps_the_new_versions(git_sandbox: GitSandbox, lock_facts: LockFacts,
                                                                 failing: str, residue: str) -> None:
    """No restoration after the marker: status 1 names the residue, which the next set removes."""
    inputs = _pattern_project(git_sandbox)
    faults = Faults(inputs.artifacts.home, fail_remove=failing)
    outcome, status, diagnostics = _run(inputs, faults.ports(lock_facts.probe))
    assert (outcome, status) == (TransitionOutcome.APPLIED_CLEANUP_FAILED, 1)
    assert len(faults.sources) == _PATTERN.writes
    assert source_bytes(inputs.project.root, list(_NEW)) == _NEW
    assert any("new versions are applied" in diagnostic and residue in diagnostic for diagnostic in diagnostics)
    outcome, status, diagnostics = _run(inputs, Faults(inputs.artifacts.home).ports(lock_facts.probe))
    assert (outcome, status) == (TransitionOutcome.UNCHANGED, 0)
    assert any("removed" in diagnostic and EVIDENCE_NAME in diagnostic for diagnostic in diagnostics)
    assert _clean(inputs)


def test_lock_release_failure_after_an_unchanged_run_fails_with_status_1(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """A clean same-target run cannot report success while its lock record remains."""
    inputs = _pattern_project(git_sandbox, _NEW)
    ports = replace(Faults(inputs.artifacts.home).ports(lock_facts.probe), lock_factory=_release_fails)
    with pytest.raises(TransitionError, match=r"no source changed.*a\.release-operation\.lock") as caught:
        set_versions(inputs, TARGET, ports=ports)
    assert caught.value.exit_code == _EXECUTION
    assert source_bytes(inputs.project.root, list(_NEW)) == _NEW
    assert not any(path.name.startswith("a.version-transition.") for path in inputs.artifacts.home.iterdir())


def test_lock_release_failure_after_completion_names_the_record(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """The new versions stay applied; the lock record is the reported residue."""
    inputs = _pattern_project(git_sandbox)
    ports = replace(Faults(inputs.artifacts.home).ports(lock_facts.probe), lock_factory=_release_fails)
    outcome, status, diagnostics = _run(inputs, ports)
    assert (outcome, status) == (TransitionOutcome.APPLIED_CLEANUP_FAILED, 1)
    assert source_bytes(inputs.project.root, list(_NEW)) == _NEW
    assert any("new versions are applied" in diagnostic and "a.release-operation.lock" in diagnostic for diagnostic in diagnostics)
    assert not (inputs.artifacts.home / EVIDENCE_NAME).exists()


# eof
