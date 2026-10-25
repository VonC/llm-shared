"""Check native ownership transitions with bounded I/O and an independent model.

Six generated traces complement the explicit retained-ownership lifecycle;
every trace retains the full action range and per-transition assertions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from tools.release_workflow.artifacts import PreparedArtifacts
from tools.release_workflow.managed_files import authorize_write
from tools.release_workflow.operation_lock import (
    OperationLock,
    OperationLockError,
    RetainedOwnership,
)
from tools.release_workflow.paths import ProjectIdentity

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
        candidate = OperationLock(self.artifacts)
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


@settings(max_examples=6, suppress_health_check=[HealthCheck.function_scoped_fixture])
@example(actions=["acquire", "retain", "release", "acquire", "transfer", "transfer", "release"])
@given(actions=st.lists(st.sampled_from(["acquire", "retain", "transfer", "release"]), min_size=1, max_size=8))
def test_lock_transitions_preserve_single_ownership(tmp_path: Path, actions: list[str]) -> None:
    """Generated transitions cannot lose retained ownership or grant a second owner."""
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
