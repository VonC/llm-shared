"""Maven reference rules: the reactor index, owned fields, inheritance and the property boundary.

Step 7 of v0.14.0 version-sources (plan decision Q10). `maven` discovers the
reactor's modules; this support module decides which version fields of those
POMs the transition owns. It declares no adapter.

- The index maps each module's `(groupId, artifactId)` to it; two modules with
  the same coordinates fail.
- A module's own `<version>` is owned when present. When absent, the version
  is inherited: the `<parent>` chain must stay inside the reactor and end in a
  module with its own version, which the transition updates; an external
  parent, no parent, or a chain that loops fails with the remedy to declare a
  literal version. Each module's chain is resolved once.
- An internal `<parent>` (its literal coordinates name a module) has its
  version owned, which must be present; an external parent is never edited.
- Every `<dependency>` is examined. One naming a module's `artifactId` is
  internal when its group is literal or exactly `${project.groupId}` (the
  declaring module's group) and the pair is a module; another literal group is
  external, and any other group, or none, fails as ambiguous (design decision
  Q12). An internal entry outside `project/dependencies` and
  `project/dependencyManagement/dependencies`, such as a profile or plugin
  dependency, fails, since it would stay stale (plan decision Q15). In those
  two sections, an absent version is managed elsewhere and exactly
  `${project.version}` stays unchanged; any other version is owned.
- An owned value must be literal: a property expression or a version range
  fails naming the file, the field and the expression, and markup inside it
  fails through `XmlValue.owned`.

Plugins and `<properties>` are never read. Every owned field takes the snapshot
form. The work is one pass over the modules and their recorded values, with
dictionary lookups: linear in the reactor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tools.release_workflow.sources.model import Form, LocatedSource, SourceError

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from pathlib import Path

    from tools.release_workflow.sources.xml_scan import PomDocument, XmlValue

_PROJECT_VERSION = "project/version"
_PARENT = "project/parent"
_PARENT_VERSION = "project/parent/version"
_DEPENDENCY = "/dependency/"
_SUPPORTED = frozenset({"project/dependencies", "project/dependencyManagement/dependencies"})
_PROJECT_GROUP = "${project.groupId}"
_KEEP = "${project.version}"
_RANGE = frozenset("[](),")
_REMEDY = "declare a literal <version> in this POM"

type Coordinates = tuple[str, str]


@dataclass(frozen=True)
class PomModule:
    """One reactor module: its POM path, scanned document and literal coordinates."""

    path: Path
    document: PomDocument
    group: str
    artifact: str

    @property
    def coordinates(self) -> Coordinates:
        """Return the module's `(groupId, artifactId)`."""
        return (self.group, self.artifact)


@dataclass(frozen=True)
class _Dependency:
    """The recorded fields of one `<dependency>` element and the section holding it."""

    location: str
    group: XmlValue | None
    artifact: XmlValue | None
    version: XmlValue | None


def literal_coordinate(module_path: Path, value: XmlValue) -> str:
    """Return a coordinate's text, failing when it uses a property."""
    if "${" in value.text:
        msg = f"{module_path}: <{value.path}> {value.text!r} uses a property; versions set reads literal coordinates only; write the literal value"
        raise SourceError(msg)
    return value.text


def _literal_version(module_path: Path, field: str, value: XmlValue) -> str:
    """Return an owned version's text, failing on an empty value, an expression or a range."""
    text = value.text
    if not text:
        msg = f"{module_path} {field}: the version is empty; write the literal version"
        raise SourceError(msg)
    if "${" in text:
        msg = (f"{module_path} {field}: {text!r} is a Maven property expression; versions set writes literal versions only, "
               f"and keeps {_KEEP} only as a whole internal dependency version; write the literal version")
        raise SourceError(msg)
    if any(character in _RANGE for character in text):
        msg = f"{module_path} {field}: {text!r} is a version range; versions set writes literal versions only; write the literal version"
        raise SourceError(msg)
    return text


def index(modules: Sequence[PomModule]) -> dict[Coordinates, PomModule]:
    """Map each module's coordinates to it; duplicate coordinates fail."""
    modules_by_key: dict[Coordinates, PomModule] = {}
    for module in modules:
        other = modules_by_key.setdefault(module.coordinates, module)
        if other is not module:
            msg = f"{module.path}: the reactor already has a module {module.group}:{module.artifact} ({other.path}); give each module its own coordinates"
            raise SourceError(msg)
    return modules_by_key


def _parent(module: PomModule, modules: dict[Coordinates, PomModule]) -> tuple[Coordinates | None, PomModule | None]:
    """Return the declared parent's coordinates, when any, and the module they name, when internal."""
    document = module.document
    artifact = document.first(f"{_PARENT}/artifactId")
    if artifact is None:
        return None, None
    group = document.first(f"{_PARENT}/groupId")
    key = ("" if group is None else literal_coordinate(module.path, group), literal_coordinate(module.path, artifact))
    return key, modules.get(key)


@dataclass
class _Rules:
    """The reference rules over one reactor, with each module's inheritance resolved once."""

    modules: dict[Coordinates, PomModule]
    artifacts: frozenset[str]
    root: Path
    adapter: str
    inherited: set[Path] = field(default_factory=set["Path"])

    def _source(self, module: PomModule, field: str, value: XmlValue, text: str) -> LocatedSource:
        """Locate one owned field of a module."""
        return LocatedSource(module.path, field, self.adapter, Form.SNAPSHOT, text, (value.owned(str(module.path)),), self.root)

    def _check_inherited(self, module: PomModule) -> None:
        """Require an absent version to come from internal parents ending in a literal version."""
        chain: set[Path] = set()
        current = module
        while current.document.first(_PROJECT_VERSION) is None and current.path not in self.inherited:
            if current.path in chain:
                msg = f"{module.path}: the internal parent chain loops back to {current.path}; give one of these POMs a literal <version>"
                raise SourceError(msg)
            chain.add(current.path)
            key, parent = _parent(current, self.modules)
            if key is None:
                msg = f"{current.path}: <project> has no version and no parent to inherit one from; {_REMEDY}"
                raise SourceError(msg)
            if parent is None:
                msg = (f"{current.path}: <project> has no version of its own and its parent {key[0]}:{key[1]} is not a reactor "
                       f"module, so versions set cannot keep it in step; {_REMEDY}")
                raise SourceError(msg)
            current = parent
        self.inherited |= chain

    def own(self, module: PomModule) -> Iterator[LocatedSource]:
        """Yield the module's own version when present, after checking an inherited one."""
        value = module.document.first(_PROJECT_VERSION)
        if value is None:
            self._check_inherited(module)
            return
        yield self._source(module, _PROJECT_VERSION, value, _literal_version(module.path, _PROJECT_VERSION, value))

    def parent(self, module: PomModule) -> Iterator[LocatedSource]:
        """Yield the version of an internal parent; an external parent is never edited."""
        key, parent = _parent(module, self.modules)
        if key is None or parent is None:
            return
        value = module.document.first(_PARENT_VERSION)
        if value is None:
            msg = f"{module.path}: the internal <parent> {key[0]}:{key[1]} has no version; write the reactor's literal version in <parent>"
            raise SourceError(msg)
        yield self._source(module, _PARENT_VERSION, value, _literal_version(module.path, _PARENT_VERSION, value))

    def _internal(self, module: PomModule, dependency: _Dependency) -> Coordinates | None:
        """Return the coordinates of a dependency on a reactor module, `None` for an external one."""
        artifact = None if dependency.artifact is None else dependency.artifact.text
        if artifact is None or artifact not in self.artifacts:
            return None
        group = None if dependency.group is None else dependency.group.text
        resolved = module.group if group == _PROJECT_GROUP else group
        if resolved is None or "${" in resolved:
            msg = (f"{module.path}: <{dependency.location}/dependency> names the reactor module artifactId {artifact!r} with groupId "
                   f"{group!r}, which versions set cannot resolve; write the literal groupId or {_PROJECT_GROUP}")
            raise SourceError(msg)
        return (resolved, artifact) if (resolved, artifact) in self.modules else None

    def dependencies(self, module: PomModule) -> Iterator[LocatedSource]:
        """Yield each owned internal dependency version; refuse internal references outside the two sections."""
        ordinals: dict[str, int] = {}
        for dependency in _dependencies(module.document):
            key = self._internal(module, dependency)
            if key is None:
                continue
            if dependency.location not in _SUPPORTED:
                msg = (f"{module.path}: <{dependency.location}/dependency> {key[0]}:{key[1]} refers to a reactor module outside "
                       "project/dependencies and project/dependencyManagement/dependencies, so versions set cannot keep it in step; "
                       "move it there or depend on a published version")
                raise SourceError(msg)
            value = dependency.version
            if value is None or value.text == _KEEP:
                continue
            entry = f"{dependency.location}/dependency[{key[0]}:{key[1]}"
            ordinals[entry] = ordinals.get(entry, 0) + 1
            owned = f"{entry}{'' if ordinals[entry] == 1 else f'#{ordinals[entry]}'}]/version"
            yield self._source(module, owned, value, _literal_version(module.path, owned, value))


def _dependencies(document: PomDocument) -> Iterator[_Dependency]:
    """Group the recorded dependency fields by their `<dependency>` element, in document order."""
    grouped: dict[int, dict[str, XmlValue]] = {}
    locations: dict[int, str] = {}
    for value in document.values:
        location, separator, leaf = value.path.rpartition(_DEPENDENCY)
        if separator:
            grouped.setdefault(value.parent, {})[leaf] = value
            locations[value.parent] = location
    for parent, fields in grouped.items():
        yield _Dependency(locations[parent], fields.get("groupId"), fields.get("artifactId"), fields.get("version"))


def owned_sources(modules: Sequence[PomModule], root: Path, adapter: str) -> tuple[LocatedSource, ...]:
    """Return every owned version field of the reactor, module by module, in discovery order."""
    modules_by_key = index(modules)
    rules = _Rules(modules_by_key, frozenset(artifact for _group, artifact in modules_by_key), root, adapter)
    sources: list[LocatedSource] = []
    for module in modules:
        sources += rules.own(module)
        sources += rules.parent(module)
        sources += rules.dependencies(module)
    return tuple(sources)


# eof
