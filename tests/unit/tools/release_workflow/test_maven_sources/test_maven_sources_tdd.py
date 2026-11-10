"""The `maven` adapter discovers a reactor from each participating root's `pom.xml`.

Step 7 of v0.14.0 version-sources (reactor discovery, plan decision Q10):
my-project's shape (external parent, literal root version, module `PDF` with
a literal internal parent, `${project.version}` only in a plugin
configuration) changes the root version and the module's parent version, each
POM read once; the snapshot form keeps the suffix and a release anchor gives
the core. Modules resolve recursively relative to the declaring POM, as a
directory or a POM file; a missing module POM, a module declared twice and
modules inside a profile fail. A module inherits a literal `groupId` from its
parent, which identifies it for internal references; a property in its own
coordinates, missing coordinates, a non-POM root element and malformed XML
fail. A configured `core` form is rejected by configuration. Candidates carry
their own version.

Code review round 1 adds the physical path policy at discovery: a module
reached through an in-project junction that is also a declared component is
claimed twice and refused by `versions set` before any write; two links to one
module POM are one module declared twice; a module outside the physical
project, directly or through a junction, or inside a nested repository,
directly or through a junction, fails with the files unchanged. A component's
module outside the component directory but inside the project, and a module
reached through an in-project junction, stay supported, named by their
physical path.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    DEMO_GROUP,
    Faults,
    RootSettings,
    gav,
    load_counts,
    pair_edit,
    pom_xml,
    reactor_poms,
    source_bytes,
    version_project,
    version_txt,
    write_file,
)
from tools.release_workflow.configuration import ConfigurationError
from tools.release_workflow.sources import detection, maven
from tools.release_workflow.sources.model import (
    FileView,
    Form,
    SourceError,
    VersionToken,
)
from tools.release_workflow.version_transition import set_versions

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.sources.model import Detection

_PREFLIGHT = 2
_ROOT = gav(DEMO_GROUP, "demo-root", "1.0.0")
_PARENT = f"<parent>{_ROOT}</parent>"
_ANCHOR = version_txt("1.0.0")


def _modules(*names: str) -> bytes:
    """Build the root POM declaring these modules."""
    return pom_xml(_ROOT, "<modules>" + "".join(f"<module>{name}</module>" for name in names) + "</modules>")


def _write(root: Path, files: dict[str, bytes]) -> None:
    """Write the reactor's files below a root."""
    for relative, content in files.items():
        write_file(root, relative, content)


def _detect(root: Path, view: FileView | None = None) -> Detection:
    """Detect at a root with its own settings and a fresh or a given view."""
    return maven.ADAPTER.detect(root, FileView() if view is None else view, RootSettings(root))


def _fails(root: Path, named: str) -> None:
    """Expect a status 2 detection failure matching `named`."""
    with pytest.raises(SourceError, match=named) as caught:
        _detect(root)
    assert caught.value.exit_code == _PREFLIGHT


def _fields(root: Path, detected: Detection) -> list[tuple[str, str, str]]:
    """List each source as its POM relative to the root, its field and its value."""
    return [(source.path.relative_to(root).as_posix(), source.field, source.value) for source in detected.sources]


def test_my_project_shape_changes_the_root_and_the_module_parent(git_sandbox: GitSandbox) -> None:
    """External parent, properties and the plugin configuration stay; each POM is read once."""
    inputs = version_project(git_sandbox, {"version.txt": version_txt("0.13.0-SNAPSHOT"), **reactor_poms()})
    root = inputs.project.root
    view = FileView()
    inventory = detection.detect(inputs, view)
    assert [(source.path.relative_to(root).as_posix(), source.field, source.form, source.value)
            for source in inventory.sources if source.adapter == "maven"] == [
        ("pom.xml", "project/version", Form.SNAPSHOT, "0.13.0-SNAPSHOT"),
        ("PDF/pom.xml", "project/parent/version", Form.SNAPSHOT, "0.13.0-SNAPSHOT")]
    edits = detection.plan_edits(inventory, VersionToken.parse("0.14.0-SNAPSHOT"))
    assert {edit.capture.path.relative_to(root).as_posix(): edit.new for edit in edits} == {
        "version.txt": version_txt("0.14.0-SNAPSHOT"), **reactor_poms("0.14.0-SNAPSHOT")}
    assert load_counts(view, root / "pom.xml", root / "PDF/pom.xml") == (1, 1)


def test_a_release_anchor_gives_the_core(tmp_path: Path) -> None:
    """The snapshot form drops the suffix for a release anchor."""
    _write(tmp_path, reactor_poms())
    assert pair_edit(maven.ADAPTER, tmp_path, VersionToken.parse("0.14.0")) == reactor_poms("0.14.0")


def test_modules_resolve_recursively_relative_to_the_declaring_pom(tmp_path: Path) -> None:
    """A module is a directory or a POM file below its declaring POM, at any depth; each is read once."""
    files = {
        "pom.xml": pom_xml(_ROOT, "<modules><module>app</module><module>tools/build.xml</module></modules>"),
        "app/pom.xml": pom_xml(_PARENT, gav(None, "app"), "<modules><module> web </module><module>../shared</module></modules>"),
        "app/web/pom.xml": pom_xml(_PARENT, gav(None, "web")),
        "shared/pom.xml": pom_xml(_PARENT, gav(None, "shared")),
        "tools/build.xml": pom_xml(_PARENT, gav(None, "build")),
    }
    _write(tmp_path, files)
    view = FileView()
    assert _fields(tmp_path, _detect(tmp_path, view)) == [
        ("pom.xml", "project/version", "1.0.0"), ("app/pom.xml", "project/parent/version", "1.0.0"),
        ("tools/build.xml", "project/parent/version", "1.0.0"), ("app/web/pom.xml", "project/parent/version", "1.0.0"),
        ("shared/pom.xml", "project/parent/version", "1.0.0")]
    assert load_counts(view, *(tmp_path / name for name in files)) == (1, 1, 1, 1, 1)


@pytest.mark.parametrize(("modules", "named"), [
    ("<module>gone</module>", r"pom\.xml: <module>gone</module> names .*gone[\\/]pom\.xml, which does not exist"),
    ("<module>app</module><module>./app/</module>", r"<module>\./app/</module> names .*app[\\/]pom\.xml, which the reactor already declares"),
])
def test_missing_and_repeated_modules_fail(tmp_path: Path, modules: str, named: str) -> None:
    """Every declared module exists and is declared once."""
    _write(tmp_path, {"pom.xml": pom_xml(_ROOT, f"<modules>{modules}</modules>"), "app/pom.xml": pom_xml(_PARENT, gav(None, "app"))})
    _fails(tmp_path, named)


def test_a_linked_module_that_is_also_a_component_is_refused_before_any_write(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """The root reactor reaches `real` through `alias`; both claims name the physical `real/pom.xml`."""
    files = {"version.txt": _ANCHOR, "pom.xml": _modules("alias"), "real/pom.xml": pom_xml(_PARENT, gav(None, "real", "1.0.0"))}
    inputs = version_project(git_sandbox, files, "[component:real]\nroot = real\n")
    git_sandbox.junction("A/alias", inputs.project.root / "real")
    faults = Faults(inputs.artifacts.home)
    with pytest.raises(SourceError, match=r"real[\\/]pom\.xml field project/version is claimed twice") as caught:
        set_versions(inputs, VersionToken.parse("1.1.0"), ports=faults.ports(lock_facts.probe))
    assert caught.value.exit_code == _PREFLIGHT
    assert (faults.sources, faults.evidence) == ([], [])
    assert source_bytes(inputs.project.root, list(files)) == files


def test_two_links_to_one_module_declare_it_twice(git_sandbox: GitSandbox) -> None:
    """A module and a link to it are one physical POM."""
    inputs = version_project(git_sandbox, {"version.txt": _ANCHOR, "pom.xml": _modules("real", "alias"),
                                           "real/pom.xml": pom_xml(_PARENT, gav(None, "real"))})
    git_sandbox.junction("A/alias", inputs.project.root / "real")
    with pytest.raises(SourceError, match=r"<module>alias</module> names .*real[\\/]pom\.xml, which the reactor already declares"):
        detection.detect(inputs, FileView())


@pytest.mark.parametrize(("module", "named"), [
    ("../outside", "escapes physical project root"),
    ("link", "escapes physical project root"),
    ("nested", "crosses a nested repository"),
    ("linked-nested", "crosses a nested repository"),
])
def test_modules_outside_the_project_or_in_a_nested_repository_fail(git_sandbox: GitSandbox, module: str, named: str) -> None:
    """The physical path policy applies to every module POM before it is read, through links too."""
    files = {"version.txt": _ANCHOR, "pom.xml": _modules(module), "nested/.git/HEAD": b"ref: refs/heads/main\n",
             "nested/pom.xml": pom_xml(_PARENT, gav(None, "nested"))}
    inputs = version_project(git_sandbox, files)
    write_file(git_sandbox.home, "outside/pom.xml", pom_xml(_PARENT, gav(None, "outside")))
    git_sandbox.junction("A/link", git_sandbox.home / "outside")
    git_sandbox.junction("A/linked-nested", inputs.project.root / "nested")
    match = rf"<module>{re.escape(module)}</module> names .*, which versions set may not read: .*{named}"
    with pytest.raises(SourceError, match=match) as caught:
        detection.detect(inputs, FileView())
    assert caught.value.exit_code == _PREFLIGHT
    assert source_bytes(inputs.project.root, list(files)) == files


def test_in_project_modules_beyond_a_component_and_through_links_stay_supported(git_sandbox: GitSandbox) -> None:
    """A component's `../shared` module and a linked module are read, each named by its physical path."""
    files = {"version.txt": _ANCHOR, "pom.xml": _modules("alias"), "real/pom.xml": pom_xml(_PARENT, gav(None, "real")),
             "app/pom.xml": pom_xml(gav(DEMO_GROUP, "app", "1.0.0"), "<modules><module>../shared</module></modules>"),
             "shared/pom.xml": pom_xml(f"<parent>{gav(DEMO_GROUP, 'app', '1.0.0')}</parent>", gav(None, "shared"))}
    inputs = version_project(git_sandbox, files, "[component:app]\nroot = app\n")
    root = inputs.project.root
    git_sandbox.junction("A/alias", root / "real")
    sources = [(source.path.relative_to(root).as_posix(), source.field) for source in detection.detect(inputs, FileView()).sources
               if source.adapter == "maven"]
    assert sources == [("pom.xml", "project/version"), ("real/pom.xml", "project/parent/version"), ("app/pom.xml", "project/version"),
                       ("shared/pom.xml", "project/parent/version")]


def test_modules_inside_a_profile_are_ambiguous(tmp_path: Path) -> None:
    """A reactor that depends on profile activation is refused."""
    profile = "<profiles><profile><id>extra</id><modules><module>app</module></modules></profile></profiles>"
    _write(tmp_path, {"pom.xml": pom_xml(_ROOT, profile), "app/pom.xml": pom_xml(_PARENT, gav(None, "app"))})
    _fails(tmp_path, r"pom\.xml: <profiles> declare modules, so the reactor depends on profile activation and is ambiguous")


def test_an_inherited_literal_group_identifies_the_module(tmp_path: Path) -> None:
    """A module without its own groupId takes its parent's, which internal references then match."""
    dependency = f"<dependencies><dependency>{gav(DEMO_GROUP, 'core', '1.0.0')}</dependency></dependencies>"
    _write(tmp_path, {
        "pom.xml": pom_xml(_ROOT, "<modules><module>core</module><module>app</module></modules>"),
        "core/pom.xml": pom_xml(_PARENT, gav(None, "core")),
        "app/pom.xml": pom_xml(_PARENT, gav(None, "app"), dependency),
    })
    assert ("app/pom.xml", "project/dependencies/dependency[com.demo:core]/version", "1.0.0") in _fields(tmp_path, _detect(tmp_path))


@pytest.mark.parametrize(("elements", "named"), [
    ((gav("${demo.group}", "demo-root", "1.0.0"),), r"<project/groupId> '\$\{demo\.group\}' uses a property"),
    ((gav(DEMO_GROUP, "${demo.name}", "1.0.0"),), r"<project/artifactId> '\$\{demo\.name\}' uses a property"),
    ((f"<parent>{gav('${parent.group}', 'base', '1.0.0')}</parent>", gav(None, "demo-root", "1.0.0")),
     r"<project/parent/groupId> '\$\{parent\.group\}' uses a property"),
    ((gav(DEMO_GROUP, "", "1.0.0"),), r"pom\.xml: <project> has no artifactId; add the literal artifactId"),
    ((gav(None, "demo-root", "1.0.0"),), r"pom\.xml: <project> has no groupId and no parent groupId to inherit"),
])
def test_unusable_module_coordinates_fail(tmp_path: Path, elements: tuple[str, ...], named: str) -> None:
    """A module's own coordinates are literal and complete."""
    write_file(tmp_path, "pom.xml", pom_xml(*elements))
    _fails(tmp_path, named)


@pytest.mark.parametrize(("content", "named"), [
    (b"<settings><version>1</version></settings>", r"pom\.xml: the root element is <settings>, not <project>"),
    (b"<project>", r"pom\.xml is not well-formed XML"),
])
def test_files_that_are_not_poms_fail(tmp_path: Path, content: bytes, named: str) -> None:
    """A participating `pom.xml` is a well-formed `<project>` document."""
    write_file(tmp_path, "pom.xml", content)
    _fails(tmp_path, named)


def test_a_root_without_pom_detects_nothing(tmp_path: Path) -> None:
    """No `pom.xml`, no reactor."""
    detected = _detect(tmp_path)
    assert (detected.sources, detected.visible) == ((), ())


def test_a_configured_core_form_is_rejected_by_configuration(git_sandbox: GitSandbox) -> None:
    """Maven allows only the snapshot form, for every command."""
    with pytest.raises(ConfigurationError, match=r"\[source:maven\] form='core': maven allows only snapshot"):
        version_project(git_sandbox, {"version.txt": version_txt("0.13.0-SNAPSHOT")}, "[source:maven]\nform = core\n")


@pytest.mark.parametrize(("content", "candidate"), [
    (pom_xml(_ROOT), True),
    (pom_xml(_PARENT, gav(None, "app")), False),
    (pom_xml(gav(DEMO_GROUP, "app", "")), False),
    (b"<project>", False),
    (b"\xff", False),
])
def test_a_candidate_carries_its_own_version(content: bytes, *, candidate: bool) -> None:
    """Only a POM with its own version text is an undeclared candidate."""
    assert maven.ADAPTER.has_project_version("pom.xml", content) is candidate


def test_the_adapter_renders_the_element_text(tmp_path: Path) -> None:
    """A value renders as the element's text bytes; snapshot is the only form."""
    write_file(tmp_path, "pom.xml", pom_xml(_ROOT))
    source, = _detect(tmp_path).sources
    assert maven.ADAPTER.render(source, "0.14.0-SNAPSHOT") == b"0.14.0-SNAPSHOT"
    assert (maven.ADAPTER.name, maven.ADAPTER.default_form, maven.ADAPTER.forms) == ("maven", Form.SNAPSHOT, frozenset({Form.SNAPSHOT}))
    assert maven.ADAPTER.manifest_names == frozenset({"pom.xml"})


# eof
