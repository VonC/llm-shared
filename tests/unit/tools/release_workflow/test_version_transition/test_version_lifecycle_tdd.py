"""Reuse by a lifecycle caller: a supplied held lock, kept evidence, a restore handle.

Step 4 of v0.14.0 version-sources (design decision Q07): the supplied lock is
verified, never acquired nor released; a released handle, one for another
project or a reserved transaction name fails before any source read. On
success the evidence is owned by the transaction, kept `complete`, and the
restore handle restores the sources with the same routine; `discard` deletes
it. The transaction's own earlier evidence is accepted, any other unfinished
evidence stops the call, and two calls with the same clock and process id
keep disjoint evidence whose first handle still restores the first originals.
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    EVIDENCE_NAME,
    FIXED_NOW,
    RESTORATION_FIXTURES,
    TARGET,
    Faults,
    ViewLog,
    declare_evidence,
    project_identity,
    source_bytes,
    version_project,
    version_txt,
)
from tools.release_workflow.artifacts import PreparedArtifacts, prepare_artifacts
from tools.release_workflow.managed_files import authorize_write
from tools.release_workflow.operation_lock import OperationLock
from tools.release_workflow.sources.model import VersionToken
from tools.release_workflow.version_evidence import (
    STANDALONE,
    EvidenceManifest,
    EvidenceState,
)
from tools.release_workflow.version_transition import (
    LifecycleOwnership,
    TransitionError,
    TransitionOutcome,
    set_versions,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.sources.model import VersionInputs
    from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

_TRANSACTION = "release-0.14.0"
_PATTERN = RESTORATION_FIXTURES["pattern"]
_EXECUTION = 1
_PREFLIGHT = 2


def _no_acquisition(artifacts: PreparedArtifacts, *, probe: Callable[[ProcessIdentity], ProcessState]) -> OperationLock:
    """Fail if the transition tries to take a lock of its own."""
    del artifacts, probe
    msg = "a lifecycle call must not acquire a lock"
    raise AssertionError(msg)


def _held(inputs: VersionInputs, lock_facts: LockFacts) -> OperationLock:
    """Take the operation lock as item 5 would, before calling the primitive."""
    return OperationLock(prepare_artifacts(inputs.artifacts, inputs.git), probe=lock_facts.probe).acquire()


def _manifest(owner: str, state: EvidenceState) -> bytes:
    """Encode a manifest with no file."""
    return EvidenceManifest(owner, "0.14.0", state, FIXED_NOW.isoformat(), ()).encode()


def test_supplied_lock_is_kept_and_the_handle_restores(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """Evidence stays complete and owned; `restore` puts the originals back, `discard` deletes it."""
    inputs = version_project(git_sandbox, _PATTERN.files, _PATTERN.ini)
    lock = _held(inputs, lock_facts)
    faults = Faults(inputs.artifacts.home)
    ports = replace(faults.ports(lock_facts.probe), lock_factory=_no_acquisition)
    result = set_versions(inputs, TARGET, lifecycle=LifecycleOwnership(lock, _TRANSACTION), ports=ports)
    assert (result.outcome, result.status) == (TransitionOutcome.APPLIED, 0)
    assert lock.verify_held(inputs.artifacts).home == inputs.artifacts.home
    evidence = inputs.artifacts.home / EVIDENCE_NAME
    manifest = EvidenceManifest.decode((evidence / "manifest.json").read_bytes())
    assert (manifest.owner, manifest.state) == (_TRANSACTION, EvidenceState.COMPLETE)
    assert result.restore is not None
    restored = result.restore.restore()
    assert (restored.outcome, restored.status) == (TransitionOutcome.RESTORED, 1)
    assert source_bytes(inputs.project.root, list(_PATTERN.files)) == dict(_PATTERN.files)
    assert evidence.is_dir()
    result.restore.discard()
    assert not evidence.exists()
    lock.release()


@pytest.mark.parametrize("case", ["released", "other project", "reserved name"])
def test_unbound_lifecycle_call_fails_before_any_source_read(git_sandbox: GitSandbox, lock_facts: LockFacts, case: str) -> None:
    """A released handle, another project's lock or the standalone name fails with no view opened."""
    inputs = version_project(git_sandbox, _PATTERN.files, _PATTERN.ini)
    transaction = STANDALONE if case == "reserved name" else _TRANSACTION
    if case == "other project":
        other = git_sandbox.home / "B"
        (other / ".reviews").mkdir()
        project = project_identity(other)
        lock = OperationLock(PreparedArtifacts(project, authorize_write(project, other / ".reviews")), probe=lock_facts.probe).acquire()
    else:
        lock = _held(inputs, lock_facts)
        if case == "released":
            lock.release()
    views = ViewLog()
    ports = replace(Faults(inputs.artifacts.home).ports(lock_facts.probe), view=views)
    with pytest.raises(TransitionError) as caught:
        set_versions(inputs, TARGET, lifecycle=LifecycleOwnership(lock, transaction), ports=ports)
    assert caught.value.exit_code == (_PREFLIGHT if case == "reserved name" else _EXECUTION)
    assert views.views == []


@pytest.mark.parametrize(("owner", "state", "accepted"), [
    (_TRANSACTION, EvidenceState.WRITING, True), ("release-0.13.0", EvidenceState.COMPLETE, False),
    (STANDALONE, EvidenceState.WRITING, False),
])
def test_only_the_transactions_own_evidence_is_accepted(git_sandbox: GitSandbox, lock_facts: LockFacts,
                                                        owner: str, state: EvidenceState, *, accepted: bool) -> None:
    """Earlier evidence of this transaction is left alone; any other unfinished evidence stops."""
    inputs = version_project(git_sandbox, _PATTERN.files, _PATTERN.ini)
    lock = _held(inputs, lock_facts)
    earlier = declare_evidence(inputs.artifacts.home, "a.version-transition.20261109T110000+0100-1", _manifest(owner, state))
    ports = Faults(inputs.artifacts.home).ports(lock_facts.probe)
    if accepted:
        result = set_versions(inputs, TARGET, lifecycle=LifecycleOwnership(lock, _TRANSACTION), ports=ports)
        assert result.outcome is TransitionOutcome.APPLIED
    else:
        with pytest.raises(TransitionError, match=re.escape(earlier.name)) as caught:
            set_versions(inputs, TARGET, lifecycle=LifecycleOwnership(lock, _TRANSACTION), ports=ports)
        assert caught.value.exit_code == _PREFLIGHT
    assert (earlier / "manifest.json").read_bytes() == _manifest(owner, state)
    lock.verify_held(inputs.artifacts)
    lock.release()


def test_two_calls_keep_disjoint_evidence_and_the_first_handle_restores(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """Same clock and process id: the second call takes the next suffix, never the first directory."""
    original = version_txt("0.13.0 -- Old", "Notes\n")
    inputs = version_project(git_sandbox, {"version.txt": original})
    lock = _held(inputs, lock_facts)
    ownership = LifecycleOwnership(lock, _TRANSACTION)
    ports = Faults(inputs.artifacts.home).ports(lock_facts.probe)
    first = set_versions(inputs, TARGET, lifecycle=ownership, ports=ports)
    second = set_versions(inputs, VersionToken.parse("0.15.0-SNAPSHOT"), lifecycle=ownership, ports=ports)
    home = inputs.artifacts.home
    assert sorted(path.name for path in home.iterdir() if path.name.startswith("a.version-transition.")) == [EVIDENCE_NAME, EVIDENCE_NAME + "-2"]
    assert (home / EVIDENCE_NAME / "original.1").read_bytes() == original
    assert (home / (EVIDENCE_NAME + "-2") / "original.1").read_bytes() == version_txt("0.14.0 -- Old", "Notes\n")
    assert second.restore is not None
    assert first.restore is not None
    first.restore.restore()
    assert (inputs.project.root / "version.txt").read_bytes() == original
    lock.release()


# eof
