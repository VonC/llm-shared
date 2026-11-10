"""The `python` adapter: `pyproject.toml` and its `uv.lock` at each participating root.

Step 5 of v0.14.0 version-sources. `tomllib` gives each file's meaning and the
`toml_scan` line scanner the byte span of each owned value; the adapter never
writes, takes no lock and starts no process.

- A `pyproject.toml` without `[project]` is tool-only: it and its `uv.lock`
  are listed as not participating. A `version` missing, not a string or listed
  in `dynamic`, and a file that is not UTF-8 or TOML, fail with the remedy.
- `uv.lock` pairs with the participating manifest of its root: its
  `(version, revision)` schema must be registered, and exactly one
  `[[package]]` must carry the project's normalized name (lowercase, runs of
  `-`, `_` and `.` as one `-`) with a `virtual = "."` or `editable = "."`
  source; zero or several fail as an ambiguous lock root. An absent lock is
  not generated; a lock without a manifest fails as an orphan.
- uv workspaces and local links fail before any write: a participating
  manifest declaring `[tool.uv.workspace]`; a tool-only project root whose
  workspace `members`, net of `exclude`, match a component root (matched with
  `PurePosixPath.full_match` relative to the project root, by the
  filesystem's case rules); a lock whose `[manifest]` lists members; a
  `workspace = true` source; and a `path` source or a `file:` direct reference
  in dependencies, optional dependencies or dependency groups whose physical
  destination, resolved against the declaring root, is a participating root,
  found with one settings lookup per reference so detection stays linear in
  the roots. Every other reference is external and stays unchanged.

Python versions cannot carry the Maven suffix, so the only form is `core`, and
a `[source:python] form = core` override changes nothing.
"""

from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, cast
from urllib.parse import urlsplit
from urllib.request import url2pathname

from tools.release_workflow.sources import toml_scan
from tools.release_workflow.sources.model import (
    Detection,
    Form,
    LocatedSource,
    SourceError,
    VisibleRecord,
    decode_utf8,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from tools.release_workflow.sources.model import AdapterSettings, FileView, Span

# Registered uv lock schemas, as the lock's (version, revision) pair. Each pair
# is backed by uv 0.13.4 records of
# tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json:
# (1, 3): uv-0.13.4-v1r3-virtual, -editable and -virtual-crlf, revision 5 locks
#         written by uv 0.13.4 with their revision line set to 3 (plan decision Q04);
# (1, 5): uv-0.13.4-v1r5-virtual and -editable, written by `uv lock --offline`.
REGISTERED_LOCK_SCHEMAS = frozenset({(1, 3), (1, 5)})

_MANIFEST = "pyproject.toml"
_LOCK = "uv.lock"
_MANIFEST_FIELD = "project.version"
_LOCK_FIELD = "package.version"
_TOOL_ONLY = "not-participating tool-only"
_LOCAL_SOURCES = ({"virtual": "."}, {"editable": "."})
_SEPARATORS = re.compile(r"[-_.]+")
_CASE_SENSITIVE = os.path.normcase("A") == "A"
_UNSUPPORTED_WORKSPACE = "uv workspaces are unsupported; remove the workspace or keep its members out of the participating roots"
_LINK = "local links between participating components are unsupported; depend on a published version or declare only one of them"

type _Table = dict[str, object]


def normalize(name: str) -> str:
    """Normalize a distribution name: lowercase, each run of `-`, `_` and `.` as one `-`."""
    return _SEPARATORS.sub("-", name).lower()


def _table(value: object) -> _Table:
    """Return a TOML table, or an empty one for any other value."""
    return cast("_Table", value) if isinstance(value, dict) else {}


def _array(value: object) -> list[object]:
    """Return the items of a TOML array, or none for any other value."""
    return cast("list[object]", value) if isinstance(value, list) else []


def _strings(value: object) -> list[str]:
    """Return the strings of a TOML array, or none for any other value."""
    return [item for item in _array(value) if isinstance(item, str)]


def _uv(data: _Table) -> _Table:
    """Return the `[tool.uv]` table."""
    return _table(_table(data.get("tool")).get("uv"))


@dataclass(frozen=True)
class _Document:
    """One decoded TOML file: its path, text, byte-order mark and parsed tables."""

    path: Path
    text: str
    bom: bytes
    data: _Table

    @classmethod
    def parse(cls, path: Path, content: bytes) -> _Document:
        """Decode strict UTF-8, keeping the byte-order mark apart, and parse the TOML."""
        text, bom = decode_utf8(content, str(path))
        try:
            return cls(path, text, bom, tomllib.loads(text))
        except tomllib.TOMLDecodeError as exc:
            msg = f"{path} is not valid TOML: {exc}; correct the file"
            raise SourceError(msg) from exc

    def span(self, table: str, value: str, *, package: str | None = None) -> Span:
        """Return the byte span of the owned value, naming the file on failure."""
        try:
            return toml_scan.byte_span(self.text, self.bom, table, value, package=package)
        except SourceError as exc:
            msg = f"{self.path}: {exc}"
            raise SourceError(msg) from exc


def _matches(path: PurePosixPath, patterns: Sequence[str]) -> bool:
    """Tell whether a relative path matches one of the workspace patterns."""
    return any(path.full_match(PurePosixPath(pattern), case_sensitive=_CASE_SENSITIVE) for pattern in patterns)


def _check_members(manifest: Path, workspace: _Table, settings: AdapterSettings) -> None:
    """Fail when a tool-only root workspace's members, net of its exclusions, include a component."""
    members, exclude = _strings(workspace.get("members")), _strings(workspace.get("exclude"))
    for component, root in settings.components.items():
        relative = PurePosixPath(root.relative_to(settings.project_root).as_posix())
        if _matches(relative, members) and not _matches(relative, exclude):
            msg = f"{manifest}: [tool.uv.workspace] members include [component:{component}] ({relative}): {_UNSUPPORTED_WORKSPACE}"
            raise SourceError(msg)


def _file_destination(requirement: str, root: Path) -> Path | None:
    """Return the path a `name @ file:...` direct reference names, or `None` for any other requirement."""
    _name, at, reference = requirement.replace("${PROJECT_ROOT}", root.as_posix()).partition("@")
    url = reference.split(";", 1)[0].strip()
    if not at or not url.startswith("file:"):
        return None
    return Path(url2pathname(urlsplit(url).path))


def _requirements(data: _Table) -> Iterator[tuple[str, str]]:
    """Yield each dependency string with where it is declared."""
    project = _table(data.get("project"))
    yield from (("[project] dependencies", item) for item in _strings(project.get("dependencies")))
    for extra, items in _table(project.get("optional-dependencies")).items():
        yield from ((f"[project.optional-dependencies] {extra}", item) for item in _strings(items))
    for group, items in _table(data.get("dependency-groups")).items():
        yield from ((f"[dependency-groups] {group}", item) for item in _strings(items))


def _local_references(manifest: Path, root: Path, data: _Table) -> Iterator[tuple[str, Path]]:
    """Yield each `path` source and `file:` reference with its destination; fail on a workspace reference."""
    for name, entry in _table(_uv(data).get("sources")).items():
        for spec in map(_table, _array(entry) or [entry]):
            if spec.get("workspace") is True:
                msg = f"{manifest}: [tool.uv.sources] {name} is a workspace reference: {_UNSUPPORTED_WORKSPACE}"
                raise SourceError(msg)
            path = spec.get("path")
            if isinstance(path, str):
                yield f"[tool.uv.sources] {name} path {path!r}", root / path
    for location, requirement in _requirements(data):
        destination = _file_destination(requirement, root)
        if destination is not None:
            yield f"{location} {requirement!r}", root / destination


def _check_links(manifest: Path, root: Path, data: _Table, settings: AdapterSettings) -> None:
    """Fail when a local reference resolves to a participating root, one lookup per reference."""
    for location, destination in _local_references(manifest, root, data):
        physical = destination.resolve()
        other = settings.participant(physical)
        if other is not None:
            msg = f"{manifest}: {location} links {settings.participant(root)} to {other} ({physical}): {_LINK}"
            raise SourceError(msg)


def _static_version(manifest: Path, project: _Table) -> str:
    """Return the project's static version string, or fail with the remedy."""
    if "version" in _strings(project.get("dynamic")):
        msg = (f"{manifest}: [project] lists version in dynamic, so a build backend computes it and versions set cannot "
               'write it; declare a static version = "X.Y.Z" in [project] instead')
        raise SourceError(msg)
    version = project.get("version")
    if not isinstance(version, str):
        msg = f'{manifest}: [project] has no version string; add version = "X.Y.Z" to [project], or remove [project] if the file only configures tools'
        raise SourceError(msg)
    return version


def _root_package(package: _Table, wanted: str) -> bool:
    """Tell whether a lock package is the project's own local root."""
    name = package.get("name")
    return isinstance(name, str) and normalize(name) == wanted and package.get("source") in _LOCAL_SOURCES


def _check_schema(path: Path, data: _Table) -> None:
    """Require a registered `(version, revision)` lock schema and no shared workspace."""
    version, revision = data.get("version"), data.get("revision")
    schema = tuple(value if type(value) is int else None for value in (version, revision))
    if schema not in REGISTERED_LOCK_SCHEMAS:
        supported = " and ".join(str(pair) for pair in sorted(REGISTERED_LOCK_SCHEMAS))
        msg = (f"{path}: unsupported uv lock schema version {version!r}, revision {revision!r}: only {supported} are "
               "supported, each backed by recorded uv 0.13.4 evidence; regenerate the lock with uv 0.13.4 or record evidence for this schema")
        raise SourceError(msg)
    if _strings(_table(data.get("manifest")).get("members")):
        msg = f"{path}: [manifest] lists workspace members: a shared workspace lock is unsupported; lock each component on its own"
        raise SourceError(msg)


@dataclass(frozen=True)
class PythonAdapter:
    """Locate `[project].version` and its uv lock root's version at each participating root."""

    name: str = "python"
    default_form: Form | None = Form.CORE
    forms: frozenset[Form] = frozenset({Form.CORE})
    manifest_names: frozenset[str] = frozenset({_MANIFEST})

    def detect(self, root: Path, view: FileView, settings: AdapterSettings) -> Detection:
        """Return the manifest and lock sources at a root, or their tool-only records."""
        manifest_path, lock_path = root / _MANIFEST, root / _LOCK
        manifest, lock = view.read(manifest_path), view.read(lock_path)
        if manifest is None:
            if lock is None:
                return Detection()
            msg = f"{lock_path} is an orphan lock: no pyproject.toml beside it; remove the lock or add its project"
            raise SourceError(msg)
        document = _Document.parse(manifest_path, manifest)
        workspace = _uv(document.data).get("workspace")
        if "project" not in document.data:
            if workspace is not None and root == settings.project_root:
                _check_members(manifest_path, _table(workspace), settings)
            return Detection(visible=self._tool_only(manifest_path, None if lock is None else lock_path))
        if workspace is not None:
            msg = f"{manifest_path} declares [tool.uv.workspace]: {_UNSUPPORTED_WORKSPACE}"
            raise SourceError(msg)
        _check_links(manifest_path, root, document.data, settings)
        project = _table(document.data["project"])
        version = _static_version(manifest_path, project)
        source = LocatedSource(manifest_path, _MANIFEST_FIELD, self.name, Form.CORE, version, (document.span("project", version),), root)
        if lock is None:
            return Detection((source,))
        return Detection((source, self._lock(_Document.parse(lock_path, lock), manifest_path, project, root)))

    def _tool_only(self, manifest: Path, lock: Path | None) -> tuple[VisibleRecord, ...]:
        """List a tool-only manifest and its lock, when present."""
        records = [VisibleRecord(manifest, _MANIFEST_FIELD, self.name, _TOOL_ONLY)]
        if lock is not None:
            records.append(VisibleRecord(lock, _LOCK_FIELD, self.name, _TOOL_ONLY))
        return tuple(records)

    def _lock(self, lock: _Document, manifest: Path, project: _Table, root: Path) -> LocatedSource:
        """Locate the version of the lock's one local root package named like the project."""
        path, data = lock.path, lock.data
        _check_schema(path, data)
        name = project.get("name")
        if not isinstance(name, str):
            msg = f"{manifest}: [project] has no name, so {path} cannot be paired with it; add name to [project]"
            raise SourceError(msg)
        wanted = normalize(name)
        packages = [package for package in map(_table, _array(data.get("package"))) if _root_package(package, wanted)]
        if len(packages) != 1:
            msg = (f"{path}: ambiguous lock root: {len(packages)} [[package]] entries are named {wanted!r} with a virtual or "
                   "editable '.' source; expected exactly one: regenerate the lock with uv lock")
            raise SourceError(msg)
        package, = packages
        value, entry = package.get("version"), cast("str", package["name"])
        if not isinstance(value, str):
            msg = f"{path}: the [[package]] entry {entry!r} has no version string; regenerate the lock with uv lock"
            raise SourceError(msg)
        return LocatedSource(path, _LOCK_FIELD, self.name, Form.CORE, value, (lock.span("package", value, package=entry),), root, manifest)

    def render(self, source: LocatedSource, value: str) -> bytes:
        """Return the bytes between the quotes: a version token needs no TOML escape."""
        del source
        return value.encode("utf-8")

    def has_project_version(self, name: str, content: bytes) -> bool:
        """Tell whether a candidate manifest declares a static project version."""
        del name
        try:
            text, _bom = decode_utf8(content, _MANIFEST)
            project = _table(tomllib.loads(text).get("project"))
        except (SourceError, tomllib.TOMLDecodeError):
            return False
        return isinstance(project.get("version"), str) and "version" not in _strings(project.get("dynamic"))


ADAPTER = PythonAdapter()


# eof
