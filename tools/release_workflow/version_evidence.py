"""Per-transition recovery evidence in the project's artifact home.

Step 4 of v0.14.0 version-sources. Before its first overwrite, a transition
writes a directory `a.version-transition.<timestamp>-<pid>` holding one copy
of each captured participating file and a manifest written last: owner
(`standalone` or a lifecycle transaction), target, state, creation time with
offset, and each file's root-relative path, SHA-256, existence and copy name.
Allocation creates the directory exclusively and takes the next `-2`, `-3`
suffix when the name is taken, up to a fixed number of attempts, never
entering an existing directory (plan decision Q17). Every write goes through
the managed replacement and every removal through a revalidated managed
target. The manifest decodes strictly, rejecting duplicate keys, unknown or
missing fields, wrong types and any copy name other than `original.<n>`, so
removing residue never follows a recorded path out of its directory; removal
also checks that each copy and the manifest resolve directly inside it. The
listing reads only the artifact home, not recursively, and classifies
completed standalone residue (an empty evidence directory, left by a failed
cleanup, included), interrupted, unreadable (a directory that cannot be read
or listed included) and lifecycle-owned evidence.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, cast

from tools.release_workflow.managed_files import ManagedWriteError, authorize_write

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from datetime import datetime
    from pathlib import Path

    from tools.release_workflow.artifacts import ArtifactDeclaration, PreparedArtifacts
    from tools.release_workflow.managed_files import ManagedTarget
    from tools.release_workflow.paths import ProjectIdentity
    from tools.release_workflow.sources.model import FileCapture

    type Replace = Callable[[ManagedTarget, bytes], None]
    type Remove = Callable[[ManagedTarget], None]

EVIDENCE_PREFIX = "a.version-transition."
MANIFEST_NAME = "manifest.json"
STANDALONE = "standalone"
ATTEMPT_LIMIT = 99
_VERSION = 1
_FIELDS = frozenset({"version", "owner", "target", "state", "created", "files"})
_FILE_FIELDS = frozenset({"path", "sha256", "exists", "copy"})
_COPY = re.compile(r"original\.[1-9][0-9]*")


class EvidenceError(ValueError):
    """Evidence that cannot be allocated, written, marked or removed: status 1."""

    exit_code = 1


class EvidenceState(StrEnum):
    """Where a transition stood when it last wrote its manifest."""

    WRITING = "writing"
    COMPLETE = "complete"
    RESTORATION_INCOMPLETE = "restoration-incomplete"


class EvidenceKind(StrEnum):
    """How the next transition treats evidence it finds."""

    RESIDUE = "completed standalone residue"
    INTERRUPTED = "interrupted"
    UNREADABLE = "unreadable"
    LIFECYCLE = "lifecycle-owned"


@dataclass(frozen=True)
class EvidenceFile:
    """One captured file: its root-relative path, digest, existence and copy name."""

    path: str
    sha256: str | None
    exists: bool
    copy: str | None


@dataclass(frozen=True)
class EvidenceManifest:
    """The owner, target, state, creation time and captured files of one transition."""

    owner: str
    target: str
    state: EvidenceState
    created: str
    files: tuple[EvidenceFile, ...]

    @classmethod
    def of(cls, owner: str, target: str, created: datetime, files: tuple[EvidenceFile, ...]) -> EvidenceManifest:
        """Start a `writing` manifest created at a local time with its offset."""
        return cls(owner, target, EvidenceState.WRITING, created.isoformat(timespec="seconds"), files)

    def encode(self) -> bytes:
        """Return the indented UTF-8 JSON document."""
        files = [{"path": item.path, "sha256": item.sha256, "exists": item.exists, "copy": item.copy} for item in self.files]
        document = {"version": _VERSION, "owner": self.owner, "target": self.target, "state": str(self.state),
                    "created": self.created, "files": files}
        return (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    @classmethod
    def decode(cls, content: bytes) -> EvidenceManifest:
        """Read a manifest strictly; any defect is an unreadable manifest."""
        try:
            return _manifest(_object(json.loads(content, object_pairs_hook=_unique), _FIELDS))
        except (ValueError, TypeError) as exc:
            msg = f"unreadable evidence manifest: {exc}"
            raise ValueError(msg) from exc

    def with_state(self, state: EvidenceState) -> EvidenceManifest:
        """Return the same manifest in another state."""
        return EvidenceManifest(self.owner, self.target, state, self.created, self.files)


def _unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject a duplicated key instead of keeping its last value."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            msg = f"duplicate field {key}"
            raise ValueError(msg)
        result[key] = value
    return result


def _object(value: object, fields: frozenset[str]) -> dict[str, object]:
    """Require a JSON object with exactly these fields."""
    if not isinstance(value, dict) or frozenset(cast("dict[str, object]", value)) != fields:
        msg = f"expected exactly the fields {sorted(fields)}"
        raise TypeError(msg)
    return cast("dict[str, object]", value)


def _text(value: object) -> str:
    """Require a string."""
    if not isinstance(value, str):
        msg = f"expected text, found {value!r}"
        raise TypeError(msg)
    return value


def _optional_text(value: object) -> str | None:
    """Require a string or null."""
    return None if value is None else _text(value)


def _manifest(record: dict[str, object]) -> EvidenceManifest:
    """Require version 1, a nonempty owner, a known state and a list of file entries."""
    files, version, owner = record["files"], record["version"], _text(record["owner"])
    if type(version) is not int or version != _VERSION or not isinstance(files, list) or not owner:
        msg = "unsupported version, file list or owner"
        raise ValueError(msg)
    entries = tuple(_file(_object(item, _FILE_FIELDS)) for item in cast("list[object]", files))
    return EvidenceManifest(owner, _text(record["target"]), EvidenceState(record["state"]), _text(record["created"]), entries)


def _copy(value: object) -> str | None:
    """Accept only a direct `original.<n>` copy name, never a path or the manifest's name."""
    copy = _optional_text(value)
    if copy is not None and _COPY.fullmatch(copy) is None:
        msg = f"unsafe copy name {copy!r}: expected original.<n>"
        raise ValueError(msg)
    return copy


def _file(record: dict[str, object]) -> EvidenceFile:
    """Read one file entry, whose existence must be a JSON boolean."""
    exists = record["exists"]
    if not isinstance(exists, bool):
        msg = f"expected a boolean existence, found {exists!r}"
        raise TypeError(msg)
    return EvidenceFile(_text(record["path"]), _optional_text(record["sha256"]), exists, _copy(record["copy"]))


def evidence_files(root: Path, captures: Sequence[FileCapture]) -> tuple[EvidenceFile, ...]:
    """Describe each capture, numbering a copy for each file that exists."""
    files: list[EvidenceFile] = []
    copies = 0
    for capture in captures:
        copy = None
        if capture.original is not None:
            copies += 1
            copy = f"original.{copies}"
        files.append(EvidenceFile(capture.path.relative_to(root).as_posix(), capture.sha256, capture.original is not None, copy))
    return tuple(files)


def remove_managed(target: ManagedTarget) -> None:
    """Remove one authorized file, if still present, or one empty authorized directory."""
    path = target.revalidate()
    if path.is_dir():
        path.rmdir()
    else:
        path.unlink(missing_ok=True)


def _inside(project: ProjectIdentity, directory: Path, name: str) -> ManagedTarget:
    """Authorize a name that must resolve directly inside the evidence directory."""
    target = authorize_write(project, directory / name)
    if target.path.parent != directory:
        msg = f"{name!r} resolves to {target.path}, outside the evidence directory"
        raise ManagedWriteError(msg)
    return target


def _remove_one(remove: Remove, authorize: Callable[[], ManagedTarget], residue: str) -> None:
    """Authorize and remove one evidence path, naming what remains when that fails."""
    try:
        remove(authorize())
    except (ManagedWriteError, OSError) as exc:
        msg = f"{residue} remains: {exc}"
        raise EvidenceError(msg) from exc


def _delete(target: ManagedTarget, copies: Sequence[str], remove: Remove) -> None:
    """Remove the copies, then the manifest, each inside the directory, then the directory itself."""
    project, directory = target.project, target.path
    for name in copies:
        _remove_one(remove, lambda name=name: _inside(project, directory, name), f"evidence directory {directory} with its copies and manifest")
    _remove_one(remove, lambda: _inside(project, directory, MANIFEST_NAME), f"evidence manifest {directory / MANIFEST_NAME}")
    _remove_one(remove, lambda: authorize_write(project, directory), f"empty evidence directory {directory}")


@dataclass(frozen=True)
class EvidenceDirectory:
    """Written evidence: its authorized directory and the manifest it holds."""

    target: ManagedTarget
    manifest: EvidenceManifest

    @property
    def path(self) -> Path:
        """Return the physical evidence directory."""
        return self.target.path

    def copy_path(self, relative: str) -> Path | None:
        """Return the retained copy of a root-relative source path, if it has one."""
        copy = next((item.copy for item in self.manifest.files if item.path == relative), None)
        return None if copy is None else self.path / copy

    def mark(self, state: EvidenceState, replace_file: Replace) -> EvidenceDirectory:
        """Replace the manifest atomically with one in the given state."""
        manifest = self.manifest.with_state(state)
        try:
            replace_file(authorize_write(self.target.project, self.path / MANIFEST_NAME), manifest.encode())
        except (ManagedWriteError, OSError) as exc:
            msg = f"cannot mark {self.path} {state}: {exc}"
            raise EvidenceError(msg) from exc
        return EvidenceDirectory(self.target, manifest)

    def delete(self, remove: Remove) -> None:
        """Remove the copies, then the manifest, then the directory."""
        _delete(self.target, [item.copy for item in self.manifest.files if item.copy is not None], remove)


@dataclass(frozen=True)
class EvidenceEntry:
    """Evidence found in the artifact home, with its manifest when readable."""

    path: Path
    manifest: EvidenceManifest | None
    empty: bool = False

    @property
    def owner(self) -> str | None:
        """Return the recorded owner, or `None` when the manifest is unreadable."""
        return None if self.manifest is None else self.manifest.owner

    @property
    def kind(self) -> EvidenceKind:
        """Classify the evidence for the next transition."""
        if self.manifest is None:
            return EvidenceKind.RESIDUE if self.empty else EvidenceKind.UNREADABLE
        if self.manifest.owner != STANDALONE:
            return EvidenceKind.LIFECYCLE
        return EvidenceKind.RESIDUE if self.manifest.state is EvidenceState.COMPLETE else EvidenceKind.INTERRUPTED

    def delete(self, project: ProjectIdentity, remove: Remove) -> None:
        """Remove this residue, whatever part of it a failed cleanup left."""
        copies = [] if self.manifest is None else [item.copy for item in self.manifest.files if item.copy is not None]
        _delete(authorize_write(project, self.path), copies, remove)


def allocate(prepared: PreparedArtifacts, now: datetime, pid: int, *, attempts: int = ATTEMPT_LIMIT) -> ManagedTarget:
    """Create a new evidence directory exclusively, taking the next free suffix."""
    base = f"{EVIDENCE_PREFIX}{now.strftime('%Y%m%dT%H%M%S%z')}-{pid}"
    for attempt in range(1, attempts + 1):
        name = base if attempt == 1 else f"{base}-{attempt}"
        try:
            target = authorize_write(prepared.project, prepared.home / name)
            target.revalidate().mkdir(exist_ok=False)
        except FileExistsError:
            continue
        except (ManagedWriteError, OSError) as exc:
            msg = f"cannot create evidence directory {name}: {exc}"
            raise EvidenceError(msg) from exc
        target.revalidate()
        return target
    msg = f"no free evidence directory after {attempts} attempts from {prepared.home / base}"
    raise EvidenceError(msg)


def write_evidence(directory: ManagedTarget, manifest: EvidenceManifest, captures: Sequence[FileCapture], *,
                   replace: Replace, remove: Remove) -> EvidenceDirectory:
    """Write each original copy, then the manifest; remove the partial directory on failure."""
    written: list[str] = []
    try:
        for item, capture in zip(manifest.files, captures, strict=True):
            if item.copy is not None and capture.original is not None:
                replace(authorize_write(directory.project, directory.path / item.copy), capture.original)
                written.append(item.copy)
        replace(authorize_write(directory.project, directory.path / MANIFEST_NAME), manifest.encode())
    except (ManagedWriteError, OSError) as exc:
        cleanup = ""
        try:
            _delete(directory, written, remove)
        except EvidenceError as error:
            cleanup = f"; {error}"
        msg = f"cannot write evidence in {directory.path}: {exc}{cleanup}"
        raise EvidenceError(msg) from exc
    return EvidenceDirectory(directory, manifest)


def find_evidence(declaration: ArtifactDeclaration) -> tuple[EvidenceEntry, ...]:
    """List the evidence directories of the artifact home, by name, reading each manifest once."""
    home = declaration.home
    if not home.is_dir():
        return ()
    return tuple(_entry(path) for path in sorted(home.iterdir()) if path.name.startswith(EVIDENCE_PREFIX) and path.is_dir())


def _empty(path: Path) -> bool:
    """Tell whether a directory is provably empty; one that cannot be listed is not."""
    try:
        return not any(path.iterdir())
    except OSError:
        return False


def _entry(path: Path) -> EvidenceEntry:
    """Read one directory's manifest; an empty directory has nothing to read."""
    try:
        return EvidenceEntry(path, EvidenceManifest.decode((path / MANIFEST_NAME).read_bytes()))
    except (OSError, ValueError):
        return EvidenceEntry(path, None, empty=_empty(path))


# eof
