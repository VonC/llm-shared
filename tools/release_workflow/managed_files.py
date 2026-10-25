"""Revalidate project destinations and publish flushed same-parent writes.

Authorization retains the supplied spelling as well as its physical destination.
Ordinary junction changes therefore invalidate the capability before mutation.
Domains still own transaction ordering; these checks are not a hostile-race or
multi-file snapshot guarantee.
"""

from __future__ import annotations

import contextlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.paths import (
    ProjectIdentity,
    ProjectPathError,
    authorize_path,
)

if TYPE_CHECKING:
    from collections.abc import Generator

_DEVICES = frozenset({"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in "123456789¹²³"
})
_INVALID = frozenset('<>:"|?*')
_CONTROL_LIMIT = 32


class ManagedWriteError(ValueError):
    """A managed destination or an owned write cannot be completed safely."""


def _check_names(path: Path) -> None:
    """Reject Windows aliases before filesystem resolution can normalize them."""
    for part in path.parts:
        if part in {path.anchor, ".", ".."}:
            continue
        if part.endswith((".", " ")) or part.split(".", 1)[0].rstrip(" ").upper() in _DEVICES or any(
            char in _INVALID or ord(char) < _CONTROL_LIMIT for char in part
        ):
            msg = f"Invalid Windows managed path component: {part!r}"
            raise ManagedWriteError(msg)


@dataclass(frozen=True)
class ManagedTarget:
    """An immutable authorization whose lexical and physical paths are rechecked."""

    project: ProjectIdentity
    supplied: Path
    path: Path

    def revalidate(self) -> Path:
        """Reject a changed destination, even when its new location is in-project."""
        checked = authorize_write(self.project, self.supplied)
        if checked.path != self.path:
            msg = f"Managed destination changed after authorization: {self.supplied}"
            raise ManagedWriteError(msg)
        return checked.path


def authorize_write(project: ProjectIdentity, supplied: str | Path) -> ManagedTarget:
    """Authorize a non-root Windows write destination without creating anything."""
    spelling = Path(supplied)
    _check_names(spelling)
    try:
        physical = authorize_path(project, spelling)
        _check_names(physical)
        if physical == project.root:
            msg = "A managed write cannot target the project root"
            raise ManagedWriteError(msg)
    except ProjectPathError as exc:
        raise ManagedWriteError(str(exc)) from exc
    return ManagedTarget(project, spelling, physical)


def prepare_directory(target: ManagedTarget) -> None:
    """Recheck existing ancestors immediately before explicit directory creation."""
    try:
        target.revalidate().mkdir(parents=True, exist_ok=True)
        target.revalidate()
    except OSError as exc:
        raise ManagedWriteError(str(exc)) from exc


def _cleanup_owned(target: ManagedTarget, identity: tuple[int, int]) -> None:
    """Remove this invocation's temporary only while its identity still matches."""
    with contextlib.suppress(OSError, ManagedWriteError):
        path = target.revalidate()
        stat = path.stat()
        if (stat.st_dev, stat.st_ino) == identity:
            path.unlink()


@contextlib.contextmanager
def temporary_bytes(target: ManagedTarget, content: bytes) -> Generator[Path]:
    """Stage complete flushed bytes beside the checked target, then own cleanup.

    The caller revalidates and publishes using its required replace/no-replace
    semantics. A crash may leave a temporary, which confers no lock ownership.
    """
    temporary: ManagedTarget | None = None
    identity = (0, 0)
    try:
        parent = target.revalidate().parent
        with tempfile.NamedTemporaryFile(dir=parent, prefix=".release-", suffix=".tmp", delete=False) as stream:
            temporary = authorize_write(target.project, stream.name)
            stat = os.fstat(stream.fileno())
            identity = (stat.st_dev, stat.st_ino)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        target.revalidate()
        yield temporary.revalidate()
    except OSError as exc:
        raise ManagedWriteError(str(exc)) from exc
    finally:
        if temporary is not None:
            _cleanup_owned(temporary, identity)


def replace_bytes(target: ManagedTarget, content: bytes) -> None:
    """Atomically replace one file after preflight, leaving old bytes on failure."""
    with temporary_bytes(target, content) as temporary:
        os.replace(temporary, target.revalidate())  # noqa: PTH105 - explicit atomic OS boundary


# eof
