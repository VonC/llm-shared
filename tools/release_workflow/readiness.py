"""Validate the selected checkout's locked release closure with named lookups.

Read each input once, index candidates once, and visit applicable edges once.
Registry locations are opaque; readiness never installs or repairs anything.
"""

from __future__ import annotations

import re
import tomllib
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pathlib import Path

type Table = dict[str, object]
type Marker = Callable[[str, Mapping[str, str]], bool]
type Specifier = Callable[[str, str], bool]
type Key = tuple[str, str | None, str | None]


class InvalidMetadataError(ValueError):
    """A lock or project field has an unsupported shape."""


def table(value: object, context: str) -> Table:
    """Require a TOML table at an explicitly named boundary."""
    if not isinstance(value, dict):
        msg = f"Expected table: {context}"
        raise InvalidMetadataError(msg)
    return cast("Table", value)


def sequence(value: object, context: str) -> list[object]:
    """Require a TOML list, distinguishing absent from empty metadata."""
    if not isinstance(value, list):
        msg = f"Expected list: {context}"
        raise InvalidMetadataError(msg)
    return cast("list[object]", value)


def string(value: object, context: str) -> str:
    """Require nonempty text for package identity and input expressions."""
    if not isinstance(value, str) or not value:
        msg = f"Expected nonempty string: {context}"
        raise ValueError(msg)
    return value


def normalized(value: object) -> str:
    """Normalize distribution spelling without consulting import names."""
    return re.sub(r"[-_.]+", "-", string(value, "package name")).lower()


def source_kind(value: object) -> str:
    """Use a source's kind, never its registry location, as identity."""
    source = table(value, "package source")
    if len(source) != 1:
        msg = "Package source must identify exactly one kind"
        raise ValueError(msg)
    kind, location = next(iter(source.items()))
    string(location, "package source location")
    return kind


@dataclass(frozen=True)
class Package:
    """One locked candidate, independent of its installed distribution."""

    name: str
    version: str
    source: str
    data: Table


class Closure:
    """Resolve graph edges in constant time after a linear index build."""

    def __init__(self, packages: list[object], environment: Mapping[str, str], marker: Marker) -> None:
        """Index the four supported combinations of optional discriminators."""
        self.environment = environment
        self.marker = marker
        self.index: dict[Key, Package | None] = {}
        self.packages: list[Package] = []
        for value in packages:
            data = table(value, "locked package")
            package = Package(normalized(data.get("name")), string(data.get("version"), "package version"),
                              source_kind(data.get("source")), data)
            self.packages.append(package)
            for version in (None, package.version):
                for source in (None, package.source):
                    key = (package.name, version, source)
                    self.index[key] = None if key in self.index else package

    def resolve(self, value: object, parent: str) -> Package | None:
        """Reject unsupported extras/markers before selecting an active edge."""
        edge = table(value, f"dependency of {parent}")
        name = normalized(edge.get("name"))
        extras = sequence(edge.get("extra", []), f"{name} extra")
        if extras:
            msg = f"Unsupported dependency extra for {name}: {extras!r}"
            raise ValueError(msg)
        active = True
        if "marker" in edge:
            marker = string(edge["marker"], f"{name} marker")
            try:
                active = self.marker(marker, self.environment)
            except ValueError as exc:
                msg = f"Package {name} has unsupported marker {marker!r}: {exc}"
                raise ValueError(msg) from exc
        if not active:
            return None
        version = string(edge["version"], f"{name} version") if "version" in edge else None
        source = source_kind(edge["source"]) if "source" in edge else None
        key = name, version, source
        if key not in self.index:
            msg = f"Missing locked dependency: {name}"
            raise ValueError(msg)
        package = self.index[key]
        if package is None:
            msg = f"Locked dependency is ambiguous: {name}"
            raise ValueError(msg)
        return package

    def walk(self, edges: list[object], installed: Callable[[str], str]) -> tuple[str, ...]:
        """Visit cycles once and query only applicable release distributions."""
        pending = deque((edge, "release") for edge in edges)
        visited: set[Key] = set()
        names: list[str] = []
        while pending:
            edge, parent = pending.popleft()
            package = self.resolve(edge, parent)
            if package is None:
                continue
            key = package.name, package.version, package.source
            if key in visited:
                continue
            visited.add(key)
            actual = installed(package.name)
            if actual != package.version:
                msg = f"Release dependency {package.name}: expected {package.version}, installed {actual}"
                raise ValueError(msg)
            names.append(package.name)
            children = sequence(package.data.get("dependencies", []), f"{package.name} dependencies")
            pending.extend((child, package.name) for child in children)
        return tuple(names)


def root_edges(closure: Closure, name: str) -> list[object]:
    """Require one virtual root and the lock's explicit release metadata."""
    roots = [package for package in closure.packages if package.data["source"] == {"virtual": "."}]
    if len(roots) != 1 or roots[0].name != name:
        msg = "Lock needs one matching virtual project root"
        raise ValueError(msg)
    root = roots[0].data
    metadata = table(root.get("metadata"), "root metadata")
    declarations = table(metadata.get("requires-dev"), "root requires-dev")
    release = sequence(declarations.get("release"), "root release metadata")
    groups = table(root.get("dev-dependencies", {}), "root dev-dependencies")
    edges = sequence(groups.get("release", []), "root release edges")
    if release and not edges:
        msg = "Nonempty release metadata has no locked release edges"
        raise ValueError(msg)
    return edges


def validate(root: Path, environment: Mapping[str, str], installed: Callable[[str], str],
             marker: Marker, satisfies: Specifier) -> tuple[str, ...]:
    """Check interpreter requirements and the applicable locked release graph."""
    with (root / "pyproject.toml").open("rb") as stream:
        project_file = tomllib.load(stream)
    with (root / "uv.lock").open("rb") as stream:
        lock = tomllib.load(stream)
    project = table(project_file.get("project"), "project")
    requirement = string(project.get("requires-python"), "requires-python")
    if not satisfies(environment["python_full_version"], requirement):
        msg = f"Prepared interpreter does not satisfy {requirement}"
        raise ValueError(msg)
    groups = table(project_file.get("dependency-groups"), "dependency-groups")
    sequence(groups.get("release"), "release group")
    dev = sequence(groups.get("dev"), "dev group")
    if {"include-group": "release"} not in dev:
        msg = "Development dependencies must include the release group"
        raise ValueError(msg)
    if type(lock.get("version")) is not int or lock["version"] != 1:
        msg = "Unsupported lock format version"
        raise ValueError(msg)
    closure = Closure(sequence(lock.get("package"), "locked packages"), environment, marker)
    return closure.walk(root_edges(closure, normalized(project.get("name"))), installed)


# eof
