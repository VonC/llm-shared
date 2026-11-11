"""Prove shared lock ownership, conservative recovery and validated handoffs.

Lock-only cases start with a prepared authorized home and declared process and
transition observations. Contention is scheduled at the transition boundary;
the Windows adapter has its own API contract tests, without native waits here.
Step 1 of v0.14.0 version-sources: ``verify_held`` accepts only the current
holder in this process, for the declared project root and artifact home.
"""

from __future__ import annotations

import json
from contextlib import contextmanager, nullcontext
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow import operation_lock, windows_process
from tools.release_workflow.artifacts import (
    ArtifactDeclaration,
    PreparedArtifacts,
    prepare_artifacts,
    resolve_artifacts,
)
from tools.release_workflow.managed_files import authorize_write
from tools.release_workflow.operation_lock import OperationLock, OperationLockError
from tools.release_workflow.paths import ProjectIdentity
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox


@pytest.fixture
def artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> PreparedArtifacts:
    """Give each lock case independent files and deterministic process facts."""
    monkeypatch.setattr(operation_lock, "current_identity", lambda: ProcessIdentity(42, 123))
    def process_alive(_pid: int) -> tuple[ProcessState, int]:
        return ProcessState.ALIVE, 123

    def uncontended(_name: str) -> nullcontext[None]:
        return nullcontext()

    monkeypatch.setattr(windows_process, "_probe", process_alive)
    monkeypatch.setattr(operation_lock, "transition_mutex", uncontended)
    root = tmp_path / "lock-project"
    home = root / ".reviews"
    home.mkdir(parents=True)
    (home / ".gitignore").write_bytes(b"*\n")
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    return PreparedArtifacts(project, authorize_write(project, home))


def test_live_owner_blocks_other_domains_and_release_is_owned(artifacts: PreparedArtifacts) -> None:
    """A single project record excludes a second operation until owned cleanup."""
    first = OperationLock(artifacts).acquire()
    with pytest.raises(OperationLockError, match="owner"):
        OperationLock(artifacts).acquire()
    first.release()
    second = OperationLock(artifacts).acquire()
    with pytest.raises(OperationLockError):
        first.release()
    second.release()
    assert {path.name for path in artifacts.home.iterdir()} == {".gitignore"}


@pytest.mark.parametrize("state", [ProcessState.ALIVE, ProcessState.DEAD, ProcessState.UNKNOWN])
def test_only_exact_dead_owner_can_be_recovered(artifacts: PreparedArtifacts, state: ProcessState) -> None:
    """Unknown process identity and live owners do not become stale by age."""
    first = OperationLock(artifacts).acquire()
    second = OperationLock(artifacts, probe=lambda _owner: state)
    if state is ProcessState.DEAD:
        second.acquire()
        with pytest.raises(OperationLockError):
            first.release()
        second.release()
    else:
        with pytest.raises(OperationLockError, match="owner"):
            second.acquire()
        first.release()


def test_retention_survives_process_exit_and_transfers_once(artifacts: PreparedArtifacts) -> None:
    """Only a validated retained capability can transfer ownership after pre."""
    first = OperationLock(artifacts).acquire()
    proof = first.retain("handoff-123")
    successor = OperationLock(artifacts, probe=lambda _owner: ProcessState.DEAD)
    with pytest.raises(OperationLockError, match="retained"):
        successor.acquire()
    with pytest.raises(OperationLockError):
        first.release()
    successor.transfer(proof)
    with pytest.raises(OperationLockError):
        OperationLock(artifacts).transfer(proof)
    successor.release()


@pytest.mark.parametrize("content", [b"{", b"{}", b'{"version":999,"pid":23}', b'{"version":1,"version":2}', b"\xff", b"[]"])
def test_unverifiable_records_are_preserved(artifacts: PreparedArtifacts, content: bytes) -> None:
    """Malformed and future records fail conservatively with recovery context."""
    path = artifacts.home / "a.release-operation.lock"
    path.write_bytes(content)
    with pytest.raises(OperationLockError) as caught:
        OperationLock(artifacts).acquire()
    assert "a.release-operation.lock" in str(caught.value)
    assert path.read_bytes() == content


def test_temporary_crash_record_confers_no_ownership(artifacts: PreparedArtifacts) -> None:
    """Only the atomically published owner record can block a new operation."""
    leftover = artifacts.home / ".release-crashed.tmp"
    leftover.write_bytes(b"partial")
    owner = OperationLock(artifacts).acquire()
    owner.release()
    assert leftover.read_bytes() == b"partial"


@pytest.mark.parametrize(("field", "value"), [("version", 999), ("pid", True), ("created", 0), ("handoff", 1), ("operation", ""), ("handoff", "orphan"), ("retained", True)])
def test_invalid_owner_fields_do_not_authorize_recovery(artifacts: PreparedArtifacts, field: str, value: object) -> None:
    """Malformed versioned records preserve all available diagnostic owner fields."""
    first = OperationLock(artifacts).acquire()
    path = artifacts.home / "a.release-operation.lock"
    record = json.loads(path.read_bytes())
    record[field] = value
    path.write_text(json.dumps(record), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(OperationLockError, match="version="):
        OperationLock(artifacts, probe=lambda _owner: ProcessState.DEAD).acquire()
    with pytest.raises(OperationLockError):
        first.release()
    assert path.read_bytes() == before


def test_retention_requires_identity_and_proof(artifacts: PreparedArtifacts) -> None:
    """Empty handoffs and forged capabilities cannot surrender or adopt ownership."""
    first = OperationLock(artifacts).acquire()
    with pytest.raises(OperationLockError, match="handoff"):
        first.retain("")
    proof = first.retain("build")
    with pytest.raises(OperationLockError):
        OperationLock(artifacts).transfer(replace(proof, secret="incorrect-é"))  # noqa: S106 - deliberately invalid capability
    successor = OperationLock(artifacts)
    successor.transfer(proof)
    successor.release()
    with pytest.raises(OperationLockError):
        OperationLock(artifacts).transfer(proof)


def test_failed_publication_preserves_competing_owner(artifacts: PreparedArtifacts, monkeypatch: pytest.MonkeyPatch) -> None:
    """Windows rename must not replace a destination appearing before publication."""
    rename = operation_lock.os.rename
    def competing(source: Path, destination: Path) -> None:
        destination.write_bytes(b"competitor")
        rename(source, destination)
    monkeypatch.setattr(operation_lock.os, "rename", competing)
    with pytest.raises(OperationLockError):
        OperationLock(artifacts).acquire()
    assert (artifacts.home / "a.release-operation.lock").read_bytes() == b"competitor"
    assert {path.name for path in artifacts.home.iterdir()} == {".gitignore", "a.release-operation.lock"}


def test_unreadable_record_is_preserved(artifacts: PreparedArtifacts, monkeypatch: pytest.MonkeyPatch) -> None:
    """Access errors cannot turn an existing owner into a missing record."""
    first = OperationLock(artifacts).acquire()
    path = artifacts.home / "a.release-operation.lock"
    before = path.read_bytes()
    with monkeypatch.context() as patch:
        def denied(_path: Path) -> bytes:
            msg = "record denied"
            raise PermissionError(msg)
        patch.setattr("pathlib.Path.read_bytes", denied)
        with pytest.raises(OperationLockError, match="record denied"):
            OperationLock(artifacts).acquire()
    assert path.read_bytes() == before
    first.release()


def test_two_stale_recoverers_cannot_remove_successor(artifacts: PreparedArtifacts, monkeypatch: pytest.MonkeyPatch) -> None:
    """A busy transition rejects the contender before it can remove a successor."""
    first = OperationLock(artifacts).acquire()
    contender = OperationLock(artifacts, probe=lambda _owner: ProcessState.DEAD)
    def busy(_name: str) -> None:
        message = "Project operation transition mutex unavailable (wait=258)"
        raise OSError(message)

    def dead_after_contention(_owner: ProcessIdentity) -> ProcessState:
        with monkeypatch.context() as patch:
            patch.setattr(operation_lock, "transition_mutex", busy)
            with pytest.raises(OperationLockError, match="mutex"):
                contender.acquire()
        return ProcessState.DEAD
    successor = OperationLock(artifacts, probe=dead_after_contention).acquire()
    before = (artifacts.home / "a.release-operation.lock").read_bytes()
    with pytest.raises(OperationLockError):
        first.release()
    assert (artifacts.home / "a.release-operation.lock").read_bytes() == before
    successor.release()


@pytest.mark.parametrize("transition", ["release", "retain", "transfer"])
def test_owner_transition_waits_for_contender_record_check(
    artifacts: PreparedArtifacts, monkeypatch: pytest.MonkeyPatch, transition: str,
) -> None:
    """Owner transitions wait for a scheduled contender check before changing bytes."""
    owner = OperationLock(artifacts).acquire()
    proof = owner.retain("build") if transition == "transfer" else None
    successor = OperationLock(artifacts)
    contender = OperationLock(artifacts)
    before = (artifacts.home / "a.release-operation.lock").read_bytes()
    checked: list[bool] = []

    @contextmanager
    def after_contender(_name: str) -> Generator[None]:
        if not checked:
            checked.append(True)
            with pytest.raises(OperationLockError, match=r"live or unverifiable owner|retained owner"):
                contender.acquire()
            assert (artifacts.home / "a.release-operation.lock").read_bytes() == before
        yield

    monkeypatch.setattr(operation_lock, "transition_mutex", after_contender)
    if transition == "release":
        owner.release()
    elif transition == "retain":
        proof = owner.retain("build")
        successor.transfer(proof)
        successor.release()
    else:
        assert proof is not None
        successor.transfer(proof)
        successor.release()
    assert checked == [True]
    assert {path.name for path in artifacts.home.iterdir()} == {".gitignore"}


def test_different_projects_hold_independent_locks(git_sandbox: GitSandbox, artifacts: PreparedArtifacts) -> None:
    """The physical project identity, not the tooling checkout, selects ownership."""
    root = git_sandbox.home / "A"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    other = prepare_artifacts(resolve_artifacts(project, git_sandbox.context()), git_sandbox.context())
    first = OperationLock(artifacts).acquire()
    second = OperationLock(other).acquire()
    first.release()
    second.release()


def test_failed_staging_keeps_dead_owner_evidence(artifacts: PreparedArtifacts, monkeypatch: pytest.MonkeyPatch) -> None:
    """A flush failure occurs before removal of a proven stale owner record."""
    first = OperationLock(artifacts).acquire()
    path = artifacts.home / "a.release-operation.lock"
    before = path.read_bytes()
    def denied(_fd: int) -> None:
        msg = "flush denied"
        raise OSError(msg)
    with monkeypatch.context() as patch:
        patch.setattr(operation_lock.os, "fsync", denied)
        with pytest.raises(OperationLockError, match="flush denied"):
            OperationLock(artifacts, probe=lambda _owner: ProcessState.DEAD).acquire()
    assert path.read_bytes() == before
    assert {entry.name for entry in artifacts.home.iterdir()} == {".gitignore", path.name}
    first.release()


def test_failed_retention_and_transfer_keep_previous_ownership(artifacts: PreparedArtifacts, monkeypatch: pytest.MonkeyPatch) -> None:
    """Failed atomic transitions cannot surrender a live owner or consume a proof."""
    first = OperationLock(artifacts).acquire()
    def denied(_source: Path, _destination: Path) -> None:
        msg = "replace denied"
        raise OSError(msg)
    with monkeypatch.context() as patch:
        patch.setattr(operation_lock.os, "replace", denied)
        with pytest.raises(OperationLockError, match="replace denied"):
            first.retain("build")
    proof = first.retain("build")
    successor = OperationLock(artifacts)
    with monkeypatch.context() as patch:
        patch.setattr(operation_lock.os, "replace", denied)
        with pytest.raises(OperationLockError, match="replace denied"):
            successor.transfer(proof)
    successor.transfer(proof)
    successor.release()


def _declaration(project: ProjectIdentity, home: Path) -> ArtifactDeclaration:
    """Declare an artifact home the way invocation preflight resolves it."""
    return ArtifactDeclaration(project, authorize_write(project, ".review-artifacts.ini"), authorize_write(project, home), declared=False)


def test_verify_held_returns_the_prepared_home(artifacts: PreparedArtifacts) -> None:
    """The current holder gets back the capability its lock was taken with."""
    owner = OperationLock(artifacts).acquire()
    assert owner.verify_held(_declaration(artifacts.project, artifacts.home)) is artifacts
    owner.release()


_REJECTIONS = {
    "released": "not held by this handle", "retained": "not held by this handle",
    "process": "not the current process", "project": "another project root",
    "home": "declared artifact home", "replaced": "not owned by this handle",
}


@pytest.mark.parametrize("case", list(_REJECTIONS))
def test_verify_held_rejects_an_unbound_handle(case: str, artifacts: PreparedArtifacts, tmp_path: Path,
                                               monkeypatch: pytest.MonkeyPatch) -> None:
    """A lifecycle caller's lock must be held here, now, for this project's home."""
    owner = OperationLock(artifacts).acquire()
    declaration = _declaration(artifacts.project, artifacts.home)
    record = artifacts.home / "a.release-operation.lock"
    if case == "released":
        owner.release()
    elif case == "retained":
        owner.retain("build")
    elif case == "process":
        monkeypatch.setattr(operation_lock, "current_identity", lambda: ProcessIdentity(43, 123))
    elif case == "project":
        root = tmp_path / "other-project"
        (root / ".reviews").mkdir(parents=True)
        other = ProjectIdentity(root, root / ".git", root / ".git", str(root))
        declaration = _declaration(other, root / ".reviews")
    elif case == "home":
        declaration = _declaration(artifacts.project, artifacts.project.root / "other-home")
    else:
        replaced = json.loads(record.read_bytes())
        replaced["pid"] = 43
        record.write_text(json.dumps(replaced), encoding="utf-8")
    before = record.read_bytes() if record.exists() else None
    with pytest.raises(OperationLockError, match=_REJECTIONS[case]):
        owner.verify_held(declaration)
    assert (record.read_bytes() if record.exists() else None) == before


# eof
