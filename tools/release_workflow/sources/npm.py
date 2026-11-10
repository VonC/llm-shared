"""The `npm` adapter: `package.json` and its `package-lock.json` at each participating root.

Step 6 of v0.14.0 version-sources. `json` gives each file's meaning and the
`json_scan` key-path scanner the byte span of each owned value; the adapter
never writes, takes no lock and starts no process.

- A `package.json` without `version` is tool-only: it and its lock are listed
  as not participating, and the lock is never parsed. A `version` that is not
  a string, and a file that is not UTF-8 or one JSON object, fail with the
  remedy.
- A `workspaces` field fails as an unsupported npm workspace, whether or not
  the manifest has a version (npm workspaces are deferred).
- In `dependencies`, `devDependencies`, `optionalDependencies` and
  `peerDependencies` of a participating manifest, a `file:` or `link:`
  specifier resolved against the declaring root whose physical destination is
  a participating root fails as an unsupported local link, naming both roots,
  in one settings lookup per reference. A `workspace:` specifier fails when
  its package name is the name of a participating npm manifest; those names
  are indexed once per file view, so detection stays linear in the roots.
  Every other specifier is external and stays unchanged.
- `npm-shrinkwrap.json` takes precedence over `package-lock.json` in npm, so a
  participating root that has one fails rather than leaving it stale. Yarn and
  pnpm locks record no root version and are never read.
- `package-lock.json` pairs with the participating manifest of its root. Its
  `lockfileVersion` must be a supported format: format 1 fails with the
  remedy to regenerate the lock with npm 7 or later, and any other format
  fails. Its root entry `packages[""]` must not name another package and must
  carry a version string; the top-level `version` is owned too where present.
  A duplicate key on an owned path fails as ambiguous. A lock without a
  manifest fails as an orphan.

The default form is `release-only` (design decision Q10); `[source:npm] form`
selects `core` or `snapshot` at every participating root (design decision
Q14). Every owned field of a root takes that form.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast
from urllib.parse import urlsplit
from urllib.request import url2pathname

from tools.release_workflow.sources import json_scan
from tools.release_workflow.sources.model import (
    Detection,
    Form,
    LocatedSource,
    SourceError,
    VisibleRecord,
    decode_utf8,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path

    from tools.release_workflow.sources.json_scan import JsonPath
    from tools.release_workflow.sources.model import AdapterSettings, FileView, Span

# Supported `package-lock.json` formats, each backed by npm 10.8.3 records of
# tests/unit/tools/release_workflow/test_version_lock_evidence/lock_evidence.v1.json:
# 2: npm-10.8.3-lock2-root; 3: npm-10.8.3-lock3-root and npm-10.8.3-lock3-root-crlf,
# each lock written by `npm install --package-lock-only --lockfile-version <format>`.
SUPPORTED_LOCK_FORMATS = frozenset({2, 3})

_MANIFEST = "package.json"
_LOCK = "package-lock.json"
_SHRINKWRAP = "npm-shrinkwrap.json"
_VERSION: JsonPath = ("version",)
_ROOT_VERSION: JsonPath = ("packages", "", "version")
_FORMAT: JsonPath = ("lockfileVersion",)
_LOCK_PATHS = (_VERSION, _ROOT_VERSION, _FORMAT)
_ROOT_FIELD = json_scan.spell(_ROOT_VERSION)
_TOOL_ONLY = "not-participating tool-only"
_SECTIONS = ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies")
_LOCAL = ("file:", "link:")
_WORKSPACE = "workspace:"
_NAMES = "npm.participating-names"
_REGENERATE = "regenerate it with npm install --package-lock-only"
_LINK = "local links between participating components are unsupported; depend on a published version or declare only one of them"

type _Object = dict[str, object]


def _object(value: object) -> _Object:
    """Return a JSON object, or an empty one for any other value."""
    return cast("_Object", value) if isinstance(value, dict) else {}


def _lenient(content: bytes | None) -> _Object:
    """Parse a manifest for an index or a candidate check; anything unreadable is an empty object."""
    if content is None:
        return {}
    try:
        return _object(json.loads(decode_utf8(content, _MANIFEST)[0]))
    except ValueError:
        return {}


@dataclass(frozen=True)
class _Document:
    """One decoded JSON file: its path, text, byte-order mark and parsed root object."""

    path: Path
    text: str
    bom: bytes
    data: _Object

    @classmethod
    def parse(cls, path: Path, content: bytes) -> _Document:
        """Decode strict UTF-8, keeping the byte-order mark apart, and parse one JSON object."""
        text, bom = decode_utf8(content, str(path))
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            msg = f"{path} is not valid JSON: {exc}; correct the file"
            raise SourceError(msg) from exc
        if not isinstance(data, dict):
            msg = f"{path}: the JSON root is not an object; an npm manifest or lock is one JSON object"
            raise SourceError(msg)
        return cls(path, text, bom, cast("_Object", data))

    def spans(self, paths: Iterable[JsonPath], values: Mapping[JsonPath, str]) -> dict[JsonPath, Span]:
        """Return the byte span of each owned string, naming the file on failure."""
        try:
            return json_scan.byte_spans(self.text, self.bom, paths, values)
        except SourceError as exc:
            msg = f"{self.path}: {exc}"
            raise SourceError(msg) from exc


def _participating_names(view: FileView, settings: AdapterSettings) -> dict[str, Path]:
    """Index the participating npm manifests of every participating root by package name."""
    names: dict[str, Path] = {}
    for root in (settings.project_root, *settings.components.values()):
        data = _lenient(view.read(root / _MANIFEST))
        name = data.get("name")
        if isinstance(name, str) and isinstance(data.get("version"), str):
            names.setdefault(name, root)
    return names


def _linked(name: str, spec: str, root: Path, view: FileView, settings: AdapterSettings) -> str | None:
    """Name the participating root a specifier reaches, or return `None` for an external one."""
    if spec.startswith(_WORKSPACE):
        target = view.derived(_NAMES, lambda: _participating_names(view, settings)).get(name)
        return None if target is None else f"{settings.participant(target)} ({target})"
    if not spec.startswith(_LOCAL):
        return None
    physical = (root / url2pathname(urlsplit(spec).path)).resolve()
    other = settings.participant(physical)
    return None if other is None else f"{other} ({physical})"


def _check_links(manifest: _Document, root: Path, view: FileView, settings: AdapterSettings) -> None:
    """Fail when a dependency specifier reaches a participating root, one lookup per specifier."""
    for section in _SECTIONS:
        for name, spec in _object(manifest.data.get(section)).items():
            other = _linked(name, spec, root, view, settings) if isinstance(spec, str) else None
            if other is not None:
                msg = f"{manifest.path}: {section} {name!r} {spec!r} links {settings.participant(root)} to {other}: {_LINK}"
                raise SourceError(msg)


def _check_format(path: Path, value: object) -> None:
    """Require a supported `lockfileVersion`, with the npm 7 remedy for format 1."""
    lock_format = value if type(value) is int else None
    if lock_format == 1:
        msg = (f"{path}: lockfileVersion 1 is unsupported: versions set edits lock formats 2 and 3 only; regenerate the lock "
               "with npm 7 or later (npm install --package-lock-only)")
        raise SourceError(msg)
    if lock_format not in SUPPORTED_LOCK_FORMATS:
        supported = " and ".join(str(item) for item in sorted(SUPPORTED_LOCK_FORMATS))
        msg = (f"{path}: unsupported lockfileVersion {value!r}: only {supported} are supported, each backed by recorded npm "
               "10.8.3 evidence; regenerate the lock with npm 7 or later or record evidence for this format")
        raise SourceError(msg)


def _lock_values(lock: _Document, manifest: _Document) -> dict[JsonPath, str]:
    """Return the owned lock strings in file order: the top-level version where present, then the root entry's."""
    data = lock.data
    entry = _object(_object(data.get("packages")).get(""))
    name, wanted = entry.get("name"), manifest.data.get("name")
    if isinstance(wanted, str) and name is not None and name != wanted:
        msg = f'{lock.path}: packages[""] names {name!r}, not {wanted!r} from {manifest.path}: the lock belongs to another package; {_REGENERATE}'
        raise SourceError(msg)
    root_version = entry.get("version")
    if not isinstance(root_version, str):
        msg = f'{lock.path}: packages[""].version is missing or not a string; {_REGENERATE}'
        raise SourceError(msg)
    values: dict[JsonPath, str] = {}
    if "version" in data:
        top = data["version"]
        if not isinstance(top, str):
            msg = f"{lock.path}: the top-level version is not a string; {_REGENERATE}"
            raise SourceError(msg)
        values[_VERSION] = top
    values[_ROOT_VERSION] = root_version
    return values


@dataclass(frozen=True)
class NpmAdapter:
    """Locate the manifest version and its lock's two version fields at each participating root."""

    name: str = "npm"
    default_form: Form | None = Form.RELEASE_ONLY
    forms: frozenset[Form] = frozenset(Form)
    manifest_names: frozenset[str] = frozenset({_MANIFEST})

    def detect(self, root: Path, view: FileView, settings: AdapterSettings) -> Detection:
        """Return the manifest and lock sources at a root, or their tool-only records."""
        manifest_path, lock_path = root / _MANIFEST, root / _LOCK
        manifest, lock = view.read(manifest_path), view.read(lock_path)
        if manifest is None:
            if lock is None:
                return Detection()
            msg = f"{lock_path} is an orphan lock: no package.json beside it; remove the lock or add its package"
            raise SourceError(msg)
        document = _Document.parse(manifest_path, manifest)
        if "workspaces" in document.data:
            msg = f"{manifest_path} declares workspaces: npm workspaces are unsupported; remove the workspaces field"
            raise SourceError(msg)
        if "version" not in document.data:
            return Detection(visible=self._tool_only(manifest_path, None if lock is None else lock_path))
        self._check_shrinkwrap(root / _SHRINKWRAP, view)
        _check_links(document, root, view, settings)
        version = document.data["version"]
        if not isinstance(version, str):
            msg = f'{manifest_path}: version is not a string; write "version": "X.Y.Z", or remove version if the file only configures tools'
            raise SourceError(msg)
        form = settings.forms.get(self.name, Form.RELEASE_ONLY)
        span = document.spans((_VERSION,), {_VERSION: version})[_VERSION]
        source = LocatedSource(manifest_path, "version", self.name, form, version, (span,), root)
        if lock is None:
            return Detection((source,))
        return Detection((source, *self._lock(_Document.parse(lock_path, lock), document, form, root)))

    def _tool_only(self, manifest: Path, lock: Path | None) -> tuple[VisibleRecord, ...]:
        """List a tool-only manifest and its lock, when present."""
        records = [VisibleRecord(manifest, "version", self.name, _TOOL_ONLY)]
        if lock is not None:
            records.append(VisibleRecord(lock, _ROOT_FIELD, self.name, _TOOL_ONLY))
        return tuple(records)

    def _check_shrinkwrap(self, path: Path, view: FileView) -> None:
        """Fail when the root has an `npm-shrinkwrap.json`, which npm prefers to the lock."""
        if view.read(path) is not None:
            msg = (f"{path}: npm-shrinkwrap.json takes precedence over package-lock.json and versions set does not edit it; "
                   "remove it or replace it with package-lock.json")
            raise SourceError(msg)

    def _lock(self, lock: _Document, manifest: _Document, form: Form, root: Path) -> tuple[LocatedSource, ...]:
        """Locate the lock's owned version strings, composed later from one original."""
        _check_format(lock.path, lock.data.get("lockfileVersion"))
        values = _lock_values(lock, manifest)
        spans = lock.spans(_LOCK_PATHS, values)
        return tuple(LocatedSource(lock.path, json_scan.spell(path), self.name, form, value, (spans[path],), root, manifest.path)
                     for path, value in values.items())

    def render(self, source: LocatedSource, value: str) -> bytes:
        """Return the bytes between the quotes: a version token needs no JSON escape."""
        del source
        return value.encode("utf-8")

    def has_project_version(self, name: str, content: bytes) -> bool:
        """Tell whether a candidate manifest declares its own version string."""
        del name
        return isinstance(_lenient(content).get("version"), str)


ADAPTER = NpmAdapter()


# eof
