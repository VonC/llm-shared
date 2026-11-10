"""The `maven` adapter: the reactor of each participating root's `pom.xml`.

Step 7 of v0.14.0 version-sources (reactor discovery, plan decision Q10). The
`xml_scan` expat scanner reads each POM once; `maven_references` then decides
the owned version fields. The adapter never writes, takes no lock and starts
no process.

- A root `pom.xml` starts the reactor. Each `<module>` resolves relative to
  its declaring POM, as a directory holding `pom.xml` or as a POM file,
  recursively and breadth first. Every POM, the root one included, goes
  through the project's physical path policy (`AdapterSettings.authorize`,
  code review round 1): one outside the physical project root or entering a
  nested repository, directly or through a link, fails before it is read,
  and modules, sources and claims use the physical path, so a module reached
  through a link that is also a declared component is claimed twice and
  fails. A missing module POM, or a module declared twice, even through two
  links, fails; modules inside a `<profile>` make the reactor depend on
  activation and fail as ambiguous.
- A module's coordinates are its literal `artifactId` and its literal, or
  literal inherited `<parent>`, `groupId`. A property in them, a missing
  `artifactId` or `groupId`, a root element other than `<project>`, and a file
  that is not well-formed UTF-8 XML, fail before any write.

Maven builds must not publish release coordinates during a snapshot, so the
only form is `snapshot` (design decision Q10). A declared component that is
also a reactor module is detected twice, and the claim registry fails on its
`pom.xml`.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.sources import maven_references, xml_scan
from tools.release_workflow.sources.model import Detection, Form, SourceError

if TYPE_CHECKING:
    from tools.release_workflow.sources.model import (
        AdapterSettings,
        FileView,
        LocatedSource,
    )

_POM = "pom.xml"
_WANTED = re.compile(r"project/(?:groupId|artifactId|version|parent/(?:groupId|artifactId|version)|modules/module"
                     r"|profiles/profile/modules/module|.+/dependency/(?:groupId|artifactId|version))")
_MODULE = "project/modules/module"
_PROFILE_MODULE = "project/profiles/profile/modules/module"


def _module_path(declaring: Path, text: str) -> Path:
    """Resolve a `<module>` against its declaring POM's directory: a POM file, or a directory's `pom.xml`."""
    target = Path(os.path.normpath(declaring.parent / text))
    return target if target.suffix == ".xml" else target / _POM


def _coordinates(path: Path, document: xml_scan.PomDocument) -> tuple[str, str]:
    """Return a module's literal groupId, own or inherited from `<parent>`, and its literal artifactId."""
    artifact = document.first("project/artifactId")
    if artifact is None or not artifact.text:
        msg = f"{path}: <project> has no artifactId; add the literal artifactId"
        raise SourceError(msg)
    group = document.first("project/groupId") or document.first("project/parent/groupId")
    if group is None or not group.text:
        msg = f"{path}: <project> has no groupId and no parent groupId to inherit; add the literal groupId"
        raise SourceError(msg)
    return maven_references.literal_coordinate(path, group), maven_references.literal_coordinate(path, artifact)


def _module(path: Path, content: bytes) -> maven_references.PomModule:
    """Scan one POM and read its coordinates; a profile module or a non-POM root fails."""
    document = xml_scan.scan(content, str(path), _WANTED)
    if document.root != "project":
        msg = f"{path}: the root element is <{document.root}>, not <project>; a Maven POM starts with <project>"
        raise SourceError(msg)
    if document.every(_PROFILE_MODULE):
        msg = (f"{path}: <profiles> declare modules, so the reactor depends on profile activation and is ambiguous; "
               "declare every module in <modules> outside the profiles")
        raise SourceError(msg)
    group, artifact = _coordinates(path, document)
    return maven_references.PomModule(path, document, group, artifact)


def _authorized(declaring: Path, element: str, child: Path, settings: AdapterSettings) -> Path:
    """Return a module POM's physical path inside the project, naming the declaring POM on failure."""
    try:
        return settings.authorize(child)
    except SourceError as exc:
        msg = f"{declaring}: {element} names {child}, which versions set may not read: {exc}; declare only modules inside the project"
        raise SourceError(msg) from exc


def reactor(root_pom: Path, content: bytes, view: FileView, settings: AdapterSettings) -> list[maven_references.PomModule]:
    """Discover the reactor breadth first from its physical root POM, reading each module POM once.

    Each module POM is authorized and read by its physical path, so a module
    reached through a link is the same module, and source, as its target.
    """
    modules = [_module(root_pom, content)]
    declared = {root_pom}
    position = 0
    while position < len(modules):
        declaring = modules[position]
        position += 1
        for value in declaring.document.every(_MODULE):
            element = f"<module>{value.text}</module>"
            child = _authorized(declaring.path, element, _module_path(declaring.path, value.text), settings)
            if child in declared:
                msg = f"{declaring.path}: {element} names {child}, which the reactor already declares; declare each module once"
                raise SourceError(msg)
            module_content = view.read(child)
            if module_content is None:
                msg = f"{declaring.path}: {element} names {child}, which does not exist; create the module POM or remove the module"
                raise SourceError(msg)
            declared.add(child)
            modules.append(_module(child, module_content))
    return modules


@dataclass(frozen=True)
class MavenAdapter:
    """Locate a reactor's project, internal parent and internal dependency versions at each participating root."""

    name: str = "maven"
    default_form: Form | None = Form.SNAPSHOT
    forms: frozenset[Form] = frozenset({Form.SNAPSHOT})
    manifest_names: frozenset[str] = frozenset({_POM})

    def detect(self, root: Path, view: FileView, settings: AdapterSettings) -> Detection:
        """Return the reactor's owned version fields, or nothing without a root `pom.xml`."""
        root_pom = settings.authorize(root / _POM)
        content = view.read(root_pom)
        if content is None:
            return Detection()
        return Detection(maven_references.owned_sources(reactor(root_pom, content, view, settings), root, self.name))

    def render(self, source: LocatedSource, value: str) -> bytes:
        """Return the element text: a version token needs no XML escape."""
        del source
        return value.encode("utf-8")

    def has_project_version(self, name: str, content: bytes) -> bool:
        """Tell whether a candidate POM declares its own version text."""
        try:
            value = xml_scan.scan(content, name, _WANTED).first("project/version")
        except SourceError:
            return False
        return value is not None and bool(value.text)


ADAPTER = MavenAdapter()


# eof
