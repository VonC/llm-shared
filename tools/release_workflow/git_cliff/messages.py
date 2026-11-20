"""Name the stages of git-cliff provisioning, their remedies, the failure contract and the standard-error lines.

Step 5 of v0.14.0 git-cliff-provisioning (design "Messages, statuses and the
failure contract"; design decisions Q05 and Q18; requirement clarification
Q08; plan decision Q18).

- `Stage` lists the failure stages and `REMEDIES` gives each one the
  design's remedy. No remedy asks to install git-cliff or change PATH, and
  only the download and lock-wait remedies mention the budget variable.
- `ProvisioningError` is the one failure a provisioning caller handles: a
  setup failure (status 2 for engine operations) whose text is its
  diagnostic, naming the pin, the internal path, the stage, what happened and
  the remedy. `permission_failure` builds the permission stage from a refused
  write, naming the nearest existing directory above the refused path, the
  one that needs write access; `denied_write` does the same from a refused
  path and reason, such as a download worker's report (code review round 1).
- `downloading_line`, `ready_line` and `waiting_line` format the three
  standard-error lines. A valid entry reused prints nothing, and provisioning
  never writes to standard output, so a captured git-cliff output stays
  exactly git-cliff's.
- Since code review round 2, `announce` writes each of those lines: a stream
  that cannot take one is a twelfth stage, `reporting`, so a broken standard
  error still reaches the caller as a `ProvisioningError` (status 2) with its
  own error as cause.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Protocol

from tools.release_workflow.git_cliff.budget import (
    DEFAULT_DOWNLOAD_SECONDS,
    DOWNLOAD_BUDGET_VARIABLE,
    MAXIMUM_DOWNLOAD_SECONDS,
)
from tools.release_workflow.git_cliff.cache_lock import LOCK_WAIT_REMEDY

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

_MEBIBYTE = 1 << 20
_RANGE = f"{DEFAULT_DOWNLOAD_SECONDS} through {MAXIMUM_DOWNLOAD_SECONDS}"
_DELETE_AND_RETRY = "Delete the named staging or entry directory, then retry"


class Stage(Enum):
    """The stage of git-cliff provisioning that failed."""

    PLATFORM = "platform"
    CONTAINMENT = "containment"
    BUDGET_SETTING = "budget-setting"
    CONFIGURATION = "configuration"
    PERMISSION = "permission"
    LOCK_WAIT = "lock-wait"
    DOWNLOAD = "download"
    VERIFICATION = "verification"
    EXTRACTION = "extraction"
    PROBE = "probe"
    IN_USE = "in-use"
    REPORTING = "reporting"


REMEDIES: Mapping[Stage, str] = MappingProxyType({
    Stage.PLATFORM: "git-cliff provisioning supports Windows 10 or Windows Server 2016 and later, on x64 only, in v0.14.0",
    Stage.CONTAINMENT: (
        "Windows refused to create the child inside its job, for example under a host job that limits its processes;"
        " run from a console outside such a job"
    ),
    Stage.BUDGET_SETTING: f"Set {DOWNLOAD_BUDGET_VARIABLE} to a whole number of seconds from {_RANGE}, or unset it",
    Stage.CONFIGURATION: "This llm-shared checkout admits no tested git-cliff pin; use an llm-shared release whose manifest admits one",
    Stage.PERMISSION: "Grant write access to the named directory of this llm-shared checkout",
    Stage.LOCK_WAIT: LOCK_WAIT_REMEDY,
    Stage.DOWNLOAD: (
        "Check access to github.com and release-assets.githubusercontent.com through HTTPS_PROXY, HTTP_PROXY and NO_PROXY;"
        f" on a slow link, raise {DOWNLOAD_BUDGET_VARIABLE} ({_RANGE} s)"
    ),
    Stage.VERIFICATION: "The asset does not match llm-shared's recorded digest; retry, and report a persistent mismatch",
    Stage.EXTRACTION: _DELETE_AND_RETRY,
    Stage.PROBE: _DELETE_AND_RETRY,
    Stage.IN_USE: "Another release runs the binary being replaced; retry when it ends",
    Stage.REPORTING: "The calling command's standard error could not be written; check its console or redirection, then retry",
})


class ProvisioningError(ValueError):
    """A provisioning failure: a setup failure, status 2 for engine operations, whose text is its diagnostic."""

    exit_code = 2

    def __init__(self, stage: Stage, *, version: str | None, path: Path, detail: str) -> None:
        """Keep the stage, the pin (None before any pin exists), the internal path and what happened."""
        self.stage = stage
        self.version = version
        self.path = path
        self.detail = detail
        super().__init__(self.diagnostic())

    def diagnostic(self) -> str:
        """Name the pin, the path, the stage, what happened and the remedy."""
        pin = "git-cliff (no admitted pin)" if self.version is None else f"git-cliff {self.version}"
        return f"{pin} unavailable at {self.path} ({self.stage.value} stage): {self.detail.rstrip('.')}. {REMEDIES[self.stage]}"


def denied_write(version: str | None, refused: str | None, reason: str, fallback: Path) -> ProvisioningError:
    """Name the nearest existing directory above a refused path, or the fallback when no path is known."""
    directory = fallback
    if refused is not None:
        directory = next((parent for parent in Path(refused).parents if parent.is_dir()), fallback)
    return ProvisioningError(Stage.PERMISSION, version=version, path=directory, detail=f"cannot write below {directory}: {reason}")


def permission_failure(version: str | None, error: OSError, fallback: Path) -> ProvisioningError:
    """Describe a refused write of this process from its error, naming the directory that needs write access."""
    return denied_write(version, None if error.filename is None else str(error.filename), str(error), fallback)


class _Asset(Protocol):
    """What the download line names: the pin, its asset file name and its size."""

    @property
    def version(self) -> str:
        """Return the pin."""
        ...

    @property
    def asset(self) -> str:
        """Return the upstream archive file name."""
        ...

    @property
    def size(self) -> int:
        """Return the archive size in bytes."""
        ...


def announce(write: Callable[[str], None], line: str, *, version: str, path: Path) -> None:
    """Write one standard-error line; a stream that cannot take it is the reporting stage, its error kept as cause."""
    try:
        write(line)
    except (OSError, ValueError) as error:
        detail = f"the line {line!r} could not be written to standard error: {error}"
        raise ProvisioningError(Stage.REPORTING, version=version, path=path, detail=detail) from error


def downloading_line(pin: _Asset) -> str:
    """Announce a download with its asset and size in MiB, one decimal."""
    return f"git-cliff {pin.version}: downloading {pin.asset} ({pin.size / _MEBIBYTE:.1f} MiB) from GitHub"


def ready_line(version: str, path: Path) -> str:
    """Announce a published entry."""
    return f"git-cliff {version}: ready at {path}"


def waiting_line(version: str, pid: int, started: str, wait: float) -> str:
    """Announce a wait behind a live holder: its PID, its start as local time with offset, and the caller's own W."""
    since = datetime.fromisoformat(started).timetz().isoformat(timespec="seconds")
    return f"git-cliff {version}: waiting for provisioning by process {pid} since {since} (up to {wait:g} s)"


# eof
