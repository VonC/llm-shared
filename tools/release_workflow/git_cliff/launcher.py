"""Run the current worktree's pinned git-cliff for `gcliff`, with its arguments, output, status and environment passed through.

Step 8 of v0.14.0 git-cliff-provisioning (design "The gcliff launcher",
"Selecting the project and the pin" and "Statuses"; design decisions Q09, Q10
and Q11; requirement clarifications Q08 to Q12). The bootstrap's
`gcliff-batch` entry kind selects `main` once its readiness gate passed:

1. The batch guard refuses `%`, `^`, `!` and `"` in any argument: the batch
   launcher cannot pass them safely, and such values belong in `cliff.toml`.
2. The Git context is created from the caller's environment and working
   directory, and `paths.find_worktree` finds the worktree containing that
   directory, or none: a plain directory, a bare repository and a `.git`
   directory have none, and any other discovery failure fails.
3. Inside a worktree, its whole `.release.ini` is validated, every domain,
   and `configured_pin` gives `[git-cliff] version`, declared or defaulted;
   outside one, the manifest default applies. git-cliff's arguments never
   choose the project, so `--workdir` or `--repository` select no pin.
4. The download budget is resolved once, then the provisioning service
   returns the invocation object of the verified, guarded entry.
5. git-cliff runs once under the passthrough policy: the caller's arguments,
   environment, working directory and standard streams, while
   `ignore_console_interrupts` makes the launcher ignore Ctrl+C, so git-cliff
   alone decides how it stops. Its status is returned unchanged.

Every failure before git-cliff starts, a refused creation and an unconfirmed
end too, writes one `gcliff:` diagnostic line on standard error and returns
69 (`GCLIFF_UNAVAILABLE`), which the evidence bundle's exit-path audit showed
git-cliff 2.14.2 never returns. The parent console's environment and PATH are
never changed. `LauncherSeams` holds the provisioning seams, the console
filter and the pin table; `production_seams` binds the Windows layer, with
the verified runtime's interpreter for download workers.

Since code review round 1, a failure while leaving the console filter after
git-cliff ended, such as a handler removal Windows refuses, is reported with
its `gcliff:` line while git-cliff's confirmed status is still returned.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.release_workflow.configuration import load_configuration
from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.git_cliff import provisioning
from tools.release_workflow.git_cliff.invocation import Policy
from tools.release_workflow.git_cliff.manifest import (
    ADMITTED_PINS,
    admitted,
    default_version,
)
from tools.release_workflow.git_cliff.provisioning import (
    configured_pin,
    provision,
    provisioning_budget,
)
from tools.release_workflow.invocation import validate_arguments
from tools.release_workflow.paths import find_worktree
from tools.release_workflow.runtime_identity import RuntimeIdentity
from tools.release_workflow.windows_child import ignore_console_interrupts

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from contextlib import AbstractContextManager
    from pathlib import Path

    from tools.release_workflow.bootstrap import Identity
    from tools.release_workflow.git_cliff.invocation import GitCliffInvocation
    from tools.release_workflow.git_cliff.manifest import AdmittedPin
    from tools.release_workflow.git_cliff.provisioning import ProvisioningSeams
    from tools.release_workflow.windows_child import ChildOutcome

GCLIFF_UNAVAILABLE = 69
ENTRY_KIND = "gcliff-batch"
_CALLER = "gcliff"
_UNSAFE = 'an argument holds %, ^, ! or ", which the batch launcher cannot pass safely; put such values in cliff.toml'


@dataclass(frozen=True, kw_only=True)
class LauncherSeams:
    """The injected boundaries of `gcliff`: the provisioning seams, the console filter and the pin table."""

    provisioning: ProvisioningSeams
    console: Callable[[], AbstractContextManager[None]] = ignore_console_interrupts
    pins: tuple[AdmittedPin, ...] = ADMITTED_PINS


def production_seams(runtime: Path) -> LauncherSeams:
    """Bind the Windows layer, with this interpreter for download workers, the console filter and the shipped pins."""
    return LauncherSeams(provisioning=provisioning.production_seams(runtime))


def _check_arguments(arguments: list[str]) -> None:
    """Apply the batch guard to git-cliff's arguments, naming `cliff.toml` as the place for such values."""
    try:
        validate_arguments(ENTRY_KIND, tuple(arguments))
    except ValueError as error:
        raise ValueError(_UNSAFE) from error


def _pin(original_cwd: Path, environment: Mapping[str, str], pins: tuple[AdmittedPin, ...]) -> AdmittedPin | None:
    """Select the pin of the worktree containing the caller's directory, or the default outside any worktree."""
    git = GitExecutionContext.create(environment, original_cwd=original_cwd, non_interactive=True)
    project = find_worktree(original_cwd, git)
    version = default_version(pins) if project is None else configured_pin(load_configuration(project))
    return None if version is None else admitted(version, pins)


def _provisioned(arguments: list[str], original_cwd: Path, tooling_root: Path, environment: Mapping[str, str],
                 seams: LauncherSeams) -> GitCliffInvocation:
    """Check the arguments, select the pin, resolve the budget and provision the guarded entry."""
    _check_arguments(arguments)
    pin = _pin(original_cwd, environment, seams.pins)
    budget = provisioning_budget(environment, tooling_root=tooling_root, pin=pin)
    return provision(tooling_root, pin, budget, seams=seams.provisioning, caller=_CALLER)


def _report(error: BaseException) -> None:
    """Write the one `gcliff:` diagnostic line of a failure."""
    detail = "interrupted" if isinstance(error, KeyboardInterrupt) else str(error)
    sys.stderr.write(f"gcliff: {detail}\n")
    sys.stderr.flush()


def _unavailable(error: BaseException) -> int:
    """Report a failure that leaves no git-cliff status, and return 69."""
    _report(error)
    return GCLIFF_UNAVAILABLE


def _run(invocation: GitCliffInvocation, arguments: list[str], *, cwd: Path, environment: Mapping[str, str] | None,
         console: Callable[[], AbstractContextManager[None]]) -> int:
    """Run git-cliff once under the passthrough policy inside the console filter, and return its status.

    A failure leaving the filter after git-cliff ended (code review round 1 of Step 8) is reported, and git-cliff's
    confirmed status is still returned.
    """
    outcome: ChildOutcome | None = None
    with invocation:
        try:
            with console():
                outcome = invocation.run(arguments, policy=Policy.PASSTHROUGH, cwd=cwd, environment=environment, output="inherit")
        except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - reported; only a run that ended has a status
            if outcome is None:
                return _unavailable(error)
            _report(error)
    return outcome.status


def main(arguments: list[str], *, original_cwd: Path, tooling_root: Path, runtime: Identity,  # noqa: PLR0913 - the bootstrap facts and two seams
         environment: Mapping[str, str] | None = None, seams: LauncherSeams | None = None) -> int:
    """Run git-cliff for the pin of the caller's worktree and return its status, or 69 when it could not start.

    Args:
        arguments: git-cliff's own arguments, passed through unchanged.
        original_cwd: The caller's working directory: it selects the worktree and is git-cliff's.
        tooling_root: The executing llm-shared checkout, which holds the cache.
        runtime: The identity the bootstrap verified, whose interpreter runs download workers.
        environment: The caller's environment; None means the process one, which git-cliff then inherits as is.
        seams: The provisioning seams, the console filter and the pin table; None binds the production ones.

    Returns:
        git-cliff's status, or 69 for any failure before it started.
    """
    bound = production_seams(RuntimeIdentity(runtime.root, runtime.environment).executable) if seams is None else seams
    source = os.environ if environment is None else environment
    try:
        invocation = _provisioned(arguments, original_cwd, tooling_root, source, bound)
    except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - every failure before git-cliff starts is 69
        return _unavailable(error)
    return _run(invocation, arguments, cwd=original_cwd, environment=environment, console=bound.console)


# eof
