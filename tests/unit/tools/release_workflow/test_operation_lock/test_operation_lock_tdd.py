"""Prove shared lock ownership, conservative recovery and validated handoffs."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Event, get_ident
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from tools.release_workflow import operation_lock, windows_process
from tools.release_workflow.artifacts import prepare_artifacts, resolve_artifacts
from tools.release_workflow.operation_lock import OperationLock, OperationLockError
from tools.release_workflow.paths import ProjectIdentity
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.artifacts import PreparedArtifacts


@pytest.fixture
def artifacts(git_sandbox: GitSandbox) -> PreparedArtifacts:
    """Prepare only this case's isolated project home through the real adapter."""
    root = git_sandbox.home / "B"
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    return prepare_artifacts(resolve_artifacts(project, git_sandbox.context()), git_sandbox.context())


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
    """Real kernel serialization excludes another thread during dead-owner proof."""
    monkeypatch.setattr(windows_process, "_TRANSITION_WAIT_MS", 20, raising=False)
    first = OperationLock(artifacts).acquire()
    contender = OperationLock(artifacts, probe=lambda _owner: ProcessState.DEAD)
    def dead_after_contention(_owner: ProcessIdentity) -> ProcessState:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(contender.acquire)
            with pytest.raises(OperationLockError, match="mutex"):
                future.result(timeout=2)
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
    """A real busy kernel mutex delays owner cleanup and handoff without losing them."""
    owner = OperationLock(artifacts).acquire()
    proof = owner.retain("build") if transition == "transfer" else None
    successor = OperationLock(artifacts)
    contender = OperationLock(artifacts)
    entered, finish = Event(), Event()
    read, kernel = OperationLock._read, windows_process._kernel
    owner_thread = get_ident()

    def held_read(lock: OperationLock) -> operation_lock._Owner | None:
        record = read(lock)
        if lock is contender:
            entered.set()
            assert finish.wait(0.5), "Owner never attempted the contended transition"
        return record

    def observed_kernel() -> MagicMock:
        native = kernel()
        api = MagicMock(wraps=native)

        def wait(handle: int, milliseconds: int) -> int:
            if api.CreateMutexW.called and get_ident() == owner_thread and not finish.is_set():
                timeout = 0x102
                assert native.WaitForSingleObject(handle, 0) == timeout
                finish.set()
                if milliseconds == 0:
                    return timeout
            return native.WaitForSingleObject(handle, milliseconds)

        api.WaitForSingleObject.side_effect = wait
        return api

    monkeypatch.setattr(OperationLock, "_read", held_read)
    monkeypatch.setattr(windows_process, "_kernel", observed_kernel)
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(contender.acquire)
        try:
            assert entered.wait(0.5), "Contender never entered its record check"
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
            with pytest.raises(OperationLockError, match=r"live or unverifiable owner|retained owner"):
                future.result(timeout=0.5)
        finally:
            finish.set()
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


# eof
