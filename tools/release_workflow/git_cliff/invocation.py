"""Start git-cliff only through one object: contained, guarded, under the engine or the passthrough environment policy.

Step 5 of v0.14.0 git-cliff-provisioning (design "The provisioning entry point
for items 4 and 5", "Version probe" and "Reuse check and the use guard";
design decisions Q07, Q09 and Q17).

- `Policy.ENGINE` (item 4 rendering, item 5 `pre`, the version probes, the
  harness comparison): every `GIT_CLIFF_*` variable removed in any case, from
  the given environment or the process one, standard input closed, output
  captured or inherited as the caller asks.
- `Policy.PASSTHROUGH` (`gcliff`): the given environment, or the process one
  inherited as is, the working directory and the inherited standard streams.
- `engine_environment` is the only place of the `GIT_CLIFF_*` removal rule;
  `probe_request` builds the `--version` probe under the engine policy for
  the reuse check (guard inherited, record-free) and the staging probe
  (recorded, no guard).
- `GitCliffInvocation` carries the verified executable, its version and the
  open use guard, and starts one git-cliff run: through the injected launcher
  (`run_contained` in production), inside its own kill-on-close job, with the
  guard handle in the child's inherited-handle list. It closes its own copy of
  the guard once the child has ended, or at once when no child was created; an
  unconfirmed end retains the guard copy instead. A refused or unconfirmed
  creation is `ProvisioningError` with the containment stage. The executable
  path is the launcher-local `GIT_CLIFF` value: it is never exported to an
  environment.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import TYPE_CHECKING, Literal, Self

from tools.release_workflow.git_cliff.messages import ProvisioningError, Stage
from tools.release_workflow.windows_child import (
    ChildRequest,
    ContainmentError,
    UnconfirmedEndError,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from pathlib import Path

    from tools.release_workflow.git_cliff.cache import Guard
    from tools.release_workflow.windows_child import ChildOutcome
    from tools.release_workflow.windows_process import ProcessIdentity

_UPSTREAM_PREFIX = "GIT_CLIFF_"


class Policy(Enum):
    """How a git-cliff child receives its environment and standard streams."""

    ENGINE = "engine"
    PASSTHROUGH = "passthrough"


def engine_environment(environment: Mapping[str, str] | None = None) -> dict[str, str]:
    """Copy the given or the process environment without any `GIT_CLIFF_*` variable, whatever its case."""
    source = os.environ if environment is None else environment
    return {name: value for name, value in source.items() if not name.upper().startswith(_UPSTREAM_PREFIX)}


def probe_request(executable: Path, *, inherited: tuple[int, ...], deadline: float,
                  record: Callable[[ProcessIdentity], None] | None = None) -> ChildRequest:
    """Build `git-cliff.exe --version` in its own directory under the engine policy, with the probe's budget."""
    return ChildRequest(executable, ("--version",), cwd=executable.parent, environment=engine_environment(), inherited=inherited,
                        deadline=deadline, record=record)


def _streams(policy: Policy, environment: Mapping[str, str] | None,
             output: Literal["capture", "inherit"]) -> tuple[Mapping[str, str] | None, Literal["closed", "inherit"]]:
    """Give the child's environment and standard input under a policy."""
    if policy is Policy.ENGINE:
        return engine_environment(environment), "closed"
    if output != "inherit":
        msg = "the passthrough policy inherits the standard streams; start it with output='inherit'"
        raise ValueError(msg)
    return environment, "inherit"


class GitCliffInvocation:
    """The verified git-cliff of one pin, held by its use guard until the one run it starts has ended."""

    def __init__(self, executable: Path, version: str, guard: Guard, *, launch: Callable[[ChildRequest], ChildOutcome]) -> None:
        """Own the open guard of the verified executable."""
        self._executable = executable
        self._version = version
        self._guard = guard
        self._launch = launch
        self._used = False

    @property
    def executable(self) -> Path:
        """Return the verified executable, the launcher-local `GIT_CLIFF` value."""
        return self._executable

    @property
    def version(self) -> str:
        """Return the pin this executable reported."""
        return self._version

    def run(self, arguments: Sequence[str], *, policy: Policy, cwd: Path, environment: Mapping[str, str] | None = None,  # noqa: PLR0913 - the planned start signature: every choice is the caller's
            output: Literal["capture", "inherit"] = "capture", deadline: float | None = None) -> ChildOutcome:
        """Start git-cliff once as a contained child that inherits the guard, and return once it has ended.

        Args:
            arguments: git-cliff's own arguments.
            policy: The engine or the passthrough environment policy.
            cwd: The working directory of the run.
            environment: The environment to start from; None means the process one.
            output: Capture or inherit the output (engine policy); the passthrough policy inherits.
            deadline: The caller's own bound in seconds, or None.

        Returns:
            The ended child's status and captured output.

        Raises:
            ProvisioningError: The creation was refused, or the child's end is unconfirmed (its guard copy is then retained).
            ValueError: This invocation already started its run, or the passthrough policy was asked to capture.
        """
        if self._used:
            msg = f"this git-cliff invocation of {self._executable} has already been used"
            raise ValueError(msg)
        self._used = True
        try:
            child_environment, stdin = _streams(policy, environment, output)
            return self._launch(ChildRequest(self._executable, tuple(arguments), cwd=cwd, environment=child_environment, stdin=stdin,
                                             output=output, inherited=(self._guard.handle,), deadline=deadline))
        except UnconfirmedEndError as error:
            self._guard.retain()
            detail = f"{error}; its use guard stays open until this process ends"
            raise self._failure(detail) from error
        except ContainmentError as error:
            raise self._failure(str(error)) from error
        finally:
            self._guard.close()

    def _failure(self, detail: str) -> ProvisioningError:
        """Describe a contained start that failed, at the entry of this executable."""
        return ProvisioningError(Stage.CONTAINMENT, version=self._version, path=self._executable.parent, detail=detail)

    def close(self) -> None:
        """Release the guard of an invocation that will not start its run; idempotent."""
        self._used = True
        self._guard.close()

    def __enter__(self) -> Self:
        """Use the invocation for a block."""
        return self

    def __exit__(self, *_exception: object) -> None:
        """Release the guard when the block ends."""
        self.close()


# eof
