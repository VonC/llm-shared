"""Maven reference rules: owned fields, inheritance and the property boundary.

Step 7 of v0.14.0 version-sources (`maven_references`, plan decision Q10):
internal dependency and dependency-management versions are owned when literal
and left alone when absent (managed elsewhere) or exactly `${project.version}`;
a literal group or exactly `${project.groupId}` identifies an internal entry,
another group expression naming a module's `artifactId` fails as ambiguous,
and another literal group is external. `${revision}` and ranges in an owned
field fail naming the file, the field and the expression. A version inherited
through an internal parent chain changes the ancestor's literal version and
each `<parent>` version, the modules staying inherited; an external parent, or
no parent, without an own version fails with the remedy. External parents,
external dependencies, plugins and `<properties>` never change, even when they
hold the project version. An internal reference in a profile or a plugin
dependency fails as unsupported (plan decision Q15). Duplicate coordinates, an
internal parent without a literal version, an inheritance loop and markup
inside an owned field fail; repeated internal entries get distinct fields. A
declared component that is also a reactor module fails as a conflicting claim
on its `pom.xml`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    DEMO_GROUP,
    RootSettings,
    gav,
    pair_edit,
    pom_xml,
    version_project,
    version_txt,
    write_file,
)
from tools.release_workflow.sources import detection, maven
from tools.release_workflow.sources.model import FileView, SourceError, VersionToken

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox

_PREFLIGHT = 2
_SNAPSHOT = "0.13.0-SNAPSHOT"
_TARGET = VersionToken.parse("0.14.0-SNAPSHOT")
_ROOT = gav(DEMO_GROUP, "demo-root", _SNAPSHOT)
_PARENT = f"<parent>{_ROOT}</parent>"
_MODULES = "<modules><module>core</module><module>app</module></modules>"
_CORE = pom_xml(_PARENT, gav(None, "core"))


def _dependencies(*entries: str, managed: bool = False) -> str:
    """Wrap dependency coordinate snippets in `<dependencies>`, inside `<dependencyManagement>` when managed."""
    block = "<dependencies>" + "".join(f"<dependency>{entry}</dependency>" for entry in entries) + "</dependencies>"
    return f"<dependencyManagement>{block}</dependencyManagement>" if managed else block


def _reactor(root: Path, *app: str, top: tuple[str, ...] = ()) -> None:
    """Write a root with modules `core` (inheriting) and `app` (inheriting, with the given elements)."""
    write_file(root, "pom.xml", pom_xml(_ROOT, "<packaging>pom</packaging>", _MODULES, *top))
    write_file(root, "core/pom.xml", _CORE)
    write_file(root, "app/pom.xml", pom_xml(_PARENT, gav(None, "app"), *app))


def _fields(root: Path) -> list[tuple[str, str]]:
    """List each detected source as its POM relative to the root and its field."""
    detected = maven.ADAPTER.detect(root, FileView(), RootSettings(root))
    return [(source.path.relative_to(root).as_posix(), source.field) for source in detected.sources]


def _fails(root: Path, named: str) -> None:
    """Expect a status 2 detection failure matching `named`."""
    with pytest.raises(SourceError, match=named) as caught:
        maven.ADAPTER.detect(root, FileView(), RootSettings(root))
    assert caught.value.exit_code == _PREFLIGHT


def test_internal_dependency_versions_are_owned_when_literal(tmp_path: Path) -> None:
    """Managed and direct internal literals are owned; absent versions and external entries are not."""
    managed = _dependencies(gav(DEMO_GROUP, "core", _SNAPSHOT), gav("org.ext", "lib", "1.0"), managed=True)
    _reactor(tmp_path, _dependencies(gav(DEMO_GROUP, "core"), gav("${project.groupId}", "core", _SNAPSHOT)), top=(managed,))
    assert _fields(tmp_path) == [
        ("pom.xml", "project/version"),
        ("pom.xml", "project/dependencyManagement/dependencies/dependency[com.demo:core]/version"),
        ("core/pom.xml", "project/parent/version"),
        ("app/pom.xml", "project/parent/version"),
        ("app/pom.xml", "project/dependencies/dependency[com.demo:core]/version"),
    ]


def test_project_version_references_stay_and_inherited_modules_stay_inherited(tmp_path: Path) -> None:
    """`${project.version}` is kept; the root version and both `<parent>` versions move."""
    _reactor(tmp_path, _dependencies(gav("${project.groupId}", "core", "${project.version}")))
    edited = pair_edit(maven.ADAPTER, tmp_path, _TARGET)
    target_root = gav(DEMO_GROUP, "demo-root", str(_TARGET))
    assert edited == {
        "pom.xml": pom_xml(target_root, "<packaging>pom</packaging>", _MODULES),
        "core/pom.xml": pom_xml(f"<parent>{target_root}</parent>", gav(None, "core")),
        "app/pom.xml": pom_xml(f"<parent>{target_root}</parent>", gav(None, "app"),
                               _dependencies(gav("${project.groupId}", "core", "${project.version}"))),
    }


def test_an_inherited_version_follows_the_internal_parent_chain(tmp_path: Path) -> None:
    """A module inheriting from an inheriting module ends at the root's literal version."""
    _reactor(tmp_path, "<modules><module>sub</module></modules>")
    write_file(tmp_path, "app/sub/pom.xml", pom_xml(f"<parent>{gav(DEMO_GROUP, 'app', _SNAPSHOT)}</parent>", gav(None, "sub")))
    assert _fields(tmp_path) == [("pom.xml", "project/version"), ("core/pom.xml", "project/parent/version"),
                                 ("app/pom.xml", "project/parent/version"), ("app/sub/pom.xml", "project/parent/version")]


@pytest.mark.parametrize(("group", "named"), [
    ("${other.group}", r"names the reactor module artifactId 'core' with groupId '\$\{other\.group\}'"),
    (None, r"names the reactor module artifactId 'core' with groupId None"),
])
def test_an_unresolvable_group_naming_a_module_is_ambiguous(tmp_path: Path, group: str | None, named: str) -> None:
    """Only a literal group or exactly `${project.groupId}` is resolved."""
    _reactor(tmp_path, _dependencies(gav(group, "core", _SNAPSHOT)))
    _fails(tmp_path, rf"app[\\/]pom\.xml: <project/dependencies/dependency> {named}")


def test_another_literal_group_is_external(tmp_path: Path) -> None:
    """A module's `artifactId` under another literal group is a different artifact."""
    _reactor(tmp_path, _dependencies(gav("org.other", "core", "9.9.9")))
    assert ("app/pom.xml", "project/dependencies/dependency[org.other:core]/version") not in _fields(tmp_path)


@pytest.mark.parametrize(("app", "top", "named"), [
    ((), (), None),
    ((_dependencies(gav(DEMO_GROUP, "core", "${revision}")),), (),
     r"app[\\/]pom\.xml project/dependencies/dependency\[com\.demo:core\]/version: '\$\{revision\}' is a Maven property expression"),
    ((_dependencies(gav(DEMO_GROUP, "core", "[0.13,0.14)"), managed=True),), (),
     r"project/dependencyManagement/dependencies/dependency\[com\.demo:core\]/version: '\[0\.13,0\.14\)' is a version range"),
])
def test_expressions_and_ranges_in_owned_fields_fail(tmp_path: Path, app: tuple[str, ...], top: tuple[str, ...], named: str | None) -> None:
    """An owned dependency version must be literal, `${project.version}` or absent."""
    _reactor(tmp_path, *app, top=top)
    if named is None:
        assert len(_fields(tmp_path)) == 3  # noqa: PLR2004
    else:
        _fails(tmp_path, named)


@pytest.mark.parametrize(("root", "named"), [
    (pom_xml(gav(DEMO_GROUP, "demo-root", "${revision}")), r"pom\.xml project/version: '\$\{revision\}' is a Maven property expression"),
    (pom_xml(gav(DEMO_GROUP, "demo-root", "")), r"pom\.xml project/version: the version is empty; write the literal version"),
    (pom_xml(f"<parent>{gav('org.springframework.boot', 'spring-boot-starter-parent', '3.3.4')}</parent>", gav(DEMO_GROUP, "demo-root")),
     r"<project> has no version of its own and its parent org\.springframework\.boot:spring-boot-starter-parent is not a reactor module"
     r".*declare a literal <version> in this POM"),
    (pom_xml(gav(DEMO_GROUP, "demo-root")), r"<project> has no version and no parent to inherit one from; declare a literal <version>"),
])
def test_unusable_project_versions_fail_with_the_remedy(tmp_path: Path, root: bytes, named: str) -> None:
    """A project version is literal, or inherited through internal parents only."""
    write_file(tmp_path, "pom.xml", root)
    _fails(tmp_path, named)


@pytest.mark.parametrize(("parent", "named"), [
    (f"<parent>{gav(DEMO_GROUP, 'demo-root', '${revision}')}</parent>", r"core[\\/]pom\.xml project/parent/version: '\$\{revision\}'"),
    (f"<parent>{gav(DEMO_GROUP, 'demo-root')}</parent>", r"core[\\/]pom\.xml: the internal <parent> com\.demo:demo-root has no version"),
    (f"<parent>{gav(DEMO_GROUP, '${root.name}', _SNAPSHOT)}</parent>", r"<project/parent/artifactId> '\$\{root\.name\}' uses a property"),
])
def test_unusable_internal_parents_fail(tmp_path: Path, parent: str, named: str) -> None:
    """An internal parent has literal coordinates and a literal version."""
    _reactor(tmp_path)
    write_file(tmp_path, "core/pom.xml", pom_xml(parent, gav(DEMO_GROUP, "core", _SNAPSHOT)))
    _fails(tmp_path, named)


def test_external_parents_dependencies_plugins_and_properties_never_change(tmp_path: Path) -> None:
    """Only the project version moves, even where other elements hold the same text."""
    others = (f"<properties><demo.version>{_SNAPSHOT}</demo.version></properties>",
              _dependencies(gav("org.ext", "lib", _SNAPSHOT)),
              f"<build><plugins><plugin>{gav(DEMO_GROUP, 'demo-root', _SNAPSHOT)}</plugin></plugins></build>")
    external = f"<parent>{gav('org.ext', 'base', _SNAPSHOT)}</parent>"
    write_file(tmp_path, "pom.xml", pom_xml(external, _ROOT, *others))
    assert pair_edit(maven.ADAPTER, tmp_path, _TARGET) == {"pom.xml": pom_xml(external, gav(DEMO_GROUP, "demo-root", str(_TARGET)), *others)}


@pytest.mark.parametrize("location", [
    "<profiles><profile><id>p</id>{deps}</profile></profiles>",
    "<build><plugins><plugin>" + gav("org.ext", "tool", "1.0") + "{deps}</plugin></plugins></build>",
    "<profiles><profile><id>p</id><dependencyManagement>{deps}</dependencyManagement></profile></profiles>",
])
def test_internal_references_outside_the_supported_sections_fail(tmp_path: Path, location: str) -> None:
    """A profile or plugin dependency on a reactor module would stay stale, so it fails."""
    _reactor(tmp_path, location.format(deps=_dependencies(gav(DEMO_GROUP, "core", _SNAPSHOT))))
    _fails(tmp_path, r"app[\\/]pom\.xml: <project/.*/dependency> com\.demo:core refers to a reactor module outside project/dependencies")


def test_external_references_outside_the_supported_sections_are_ignored(tmp_path: Path) -> None:
    """A profile dependency on an external artifact is never read for writing."""
    _reactor(tmp_path, f"<profiles><profile><id>p</id>{_dependencies(gav('org.ext', 'lib', '1.0'))}</profile></profiles>")
    assert len(_fields(tmp_path)) == 3  # noqa: PLR2004


def test_repeated_internal_entries_get_distinct_fields(tmp_path: Path) -> None:
    """Two entries on one module, such as a jar and its test jar, are two fields of one file."""
    _reactor(tmp_path, _dependencies(gav(DEMO_GROUP, "core", _SNAPSHOT), gav(DEMO_GROUP, "core", _SNAPSHOT) + "<type>test-jar</type>"))
    assert _fields(tmp_path)[-2:] == [("app/pom.xml", "project/dependencies/dependency[com.demo:core]/version"),
                                      ("app/pom.xml", "project/dependencies/dependency[com.demo:core#2]/version")]


def test_duplicate_module_coordinates_fail(tmp_path: Path) -> None:
    """Two modules with the same coordinates make internal references ambiguous."""
    _reactor(tmp_path)
    write_file(tmp_path, "app/pom.xml", pom_xml(_PARENT, gav(None, "core")))
    _fails(tmp_path, r"app[\\/]pom\.xml: the reactor already has a module com\.demo:core")


def test_an_inheritance_loop_fails(tmp_path: Path) -> None:
    """Modules inheriting from each other never reach a literal version."""
    write_file(tmp_path, "pom.xml", pom_xml(_ROOT, _MODULES))
    write_file(tmp_path, "core/pom.xml", pom_xml(f"<parent>{gav(DEMO_GROUP, 'app', _SNAPSHOT)}</parent>", gav(DEMO_GROUP, "core")))
    write_file(tmp_path, "app/pom.xml", pom_xml(f"<parent>{gav(DEMO_GROUP, 'core', _SNAPSHOT)}</parent>", gav(DEMO_GROUP, "app")))
    _fails(tmp_path, r"the internal parent chain loops back to .*; give one of these POMs a literal <version>")


def test_markup_inside_an_owned_field_fails(tmp_path: Path) -> None:
    """A comment inside an owned version cannot be edited byte for byte."""
    write_file(tmp_path, "pom.xml", pom_xml(gav(DEMO_GROUP, "demo-root", "0.13.0<!-- bump -->")))
    _fails(tmp_path, r"pom\.xml: <project/version> holds a comment, which versions set cannot edit")


def test_a_component_that_is_also_a_reactor_module_is_a_conflicting_claim(git_sandbox: GitSandbox) -> None:
    """The root reactor and the component root both claim `frontend/pom.xml`."""
    files = {"version.txt": version_txt(_SNAPSHOT), "pom.xml": pom_xml(_ROOT, "<modules><module>frontend</module></modules>"),
             "frontend/pom.xml": pom_xml(_PARENT, gav(None, "frontend", _SNAPSHOT))}
    with pytest.raises(SourceError, match=r"frontend[\\/]pom\.xml field project/version is claimed twice"):
        detection.detect(version_project(git_sandbox, files, "[component:frontend]\nroot = frontend\n"), FileView())


# eof
