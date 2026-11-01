"""Check ownership transitions against declared process facts and a model.

Four generated traces complement the explicit retained-ownership lifecycle;
every trace retains the full action range and per-transition assertions.
"""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tools.release_workflow import operation_lock
from tools.release_workflow.artifacts import PreparedArtifacts
from tools.release_workflow.managed_files import authorize_write
from tools.release_workflow.operation_lock import (
    OperationLock,
    OperationLockError,
    RetainedOwnership,
)
from tools.release_workflow.paths import ProjectIdentity
from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class LockModel:
    """Model absent, active and retained states without inspecting record internals."""

    artifacts: PreparedArtifacts
    active: OperationLock | None = None
    retained: RetainedOwnership | None = None

    def acquire(self) -> None:
        """Only absence allows a fresh operation to acquire."""
        candidate = OperationLock(self.artifacts, probe=lambda _owner: ProcessState.ALIVE)
        if self.active is not None or self.retained is not None:
            with pytest.raises(OperationLockError):
                candidate.acquire()
        else:
            self.active = candidate.acquire()

    def release(self) -> None:
        """Only the active handle can end an operation."""
        if self.active is None:
            with pytest.raises(OperationLockError):
                OperationLock(self.artifacts).release()
        else:
            self.active.release()
            self.active = None

    def retain(self) -> None:
        """Retention removes the live handle while preserving durable exclusion."""
        if self.active is None:
            with pytest.raises(OperationLockError):
                OperationLock(self.artifacts).retain("build")
        else:
            self.retained = self.active.retain("build")
            self.active = None

    def transfer(self) -> None:
        """Only the current retained capability allows an engine to return."""
        candidate = OperationLock(self.artifacts)
        if self.retained is None:
            with pytest.raises(OperationLockError):
                candidate.transfer(RetainedOwnership("unknown", "build", "unknown"))
        else:
            candidate.transfer(self.retained)
            self.active = candidate
            self.retained = None


def _uncontended_mutex(_name: str) -> nullcontext[None]:
    """Declare immediate serialization for the single-threaded model trace."""
    return nullcontext()


@pytest.mark.parametrize("_batch", range(2))
@settings(max_examples=2, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(actions=st.lists(st.sampled_from(["acquire", "retain", "transfer", "release"]), min_size=1, max_size=8))
def test_lock_transitions_preserve_single_ownership(
    _batch: int, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, actions: list[str],
) -> None:
    """Generated transitions cannot lose retained ownership or grant a second owner."""
    _assert_trace(tmp_path, monkeypatch, actions)


def test_retained_ownership_lifecycle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Retain the full seven-transition counterexample independently of generation."""
    _assert_trace(tmp_path, monkeypatch, ["acquire", "retain", "release", "acquire", "transfer", "transfer", "release"])


def _assert_trace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, actions: list[str]) -> None:
    """Check the model after every real transition and release every issued handle."""
    monkeypatch.setattr(operation_lock, "current_identity", lambda: ProcessIdentity(101, 1))
    monkeypatch.setattr(operation_lock, "transition_mutex", _uncontended_mutex)
    root = tmp_path
    project = ProjectIdentity(root, root / ".git", root / ".git", str(root))
    home = root / ".reviews"
    home.mkdir(exist_ok=True)
    artifacts = PreparedArtifacts(project, authorize_write(project, home))
    model = LockModel(artifacts)
    transitions = {"acquire": model.acquire, "retain": model.retain, "transfer": model.transfer, "release": model.release}
    for action in actions:
        transitions[action]()
        assert (home / "a.release-operation.lock").exists() == (model.active is not None or model.retained is not None)
    if model.retained is not None:
        model.transfer()
    if model.active is not None:
        model.release()


# eof
