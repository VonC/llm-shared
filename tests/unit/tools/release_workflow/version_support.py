"""Byte builders for version sources and helpers for read-once file views.

Step 2 of v0.14.0 version-sources starts this module with `version.txt`
documents in LF, CRLF and byte-order-mark variants, settings naming the
project root and a load-count helper; later steps add the ecosystem files.
Step 3 adds pattern declarations to those settings, `.env`-style line files,
`.release.ini` and nested-file writers, a `VersionInputs` builder over a
`git_sandbox` project and a synthetic adapter that locates one fixed span
and logs each root it visits, standing in for adapters later steps add.
Step 4 adds the transition's fixed clock and process id, a project builder,
the restoration fixture registry that Steps 5 to 7 extend with their
adapters' files (plan decision Q01), managed replacement and removal that
record calls and fail the chosen ones, a recording view factory and evidence
declarations. Step 5 adds component roots to the settings, `pyproject.toml`
and `uv.lock` builders for virtual and editable roots, their restoration
fixture sets and the adapter's planned edit of one pair that the lock evidence
recorder and its test share. Step 6 adds configured forms to the settings,
`package.json` and `package-lock.json` builders formatted as npm writes them,
the npm restoration fixture sets (lock formats 2 and 3, LF and CRLF, two lock
fields in one file), and generalizes that planned edit to any adapter as
`pair_edit`. Step 7 adds POM builders (`gav`, `pom_xml`, my-project's
`reactor_poms`), gives the settings the production physical path policy
(`authorize`), keys `pair_edit` by path relative to the root so a reactor's
several `pom.xml` files stay apart, and completes the restoration registry
with the Maven sets and the combined five-file project. Step 8 adds release
histories: `annotation` (notes, the tooling trailer, `[valid]`), `chain` (a
linear declared history) and `tagged_history` (a chain with tags by position
over the sandbox's recording Git observations). Nothing here starts a process
or interprets a version.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from tools.release_workflow.artifacts import resolve_artifacts
from tools.release_workflow.configuration import load_configuration
from tools.release_workflow.managed_files import ManagedWriteError, replace_bytes
from tools.release_workflow.paths import ProjectIdentity
from tools.release_workflow.sources.detection import plan_edits
from tools.release_workflow.sources.model import (
    Claim,
    Detection,
    FileCapture,
    FileView,
    Form,
    Inventory,
    LocatedSource,
    PatternDeclaration,
    Span,
    VersionInputs,
    VersionToken,
    participant_names,
)
from tools.release_workflow.sources.settings import authorize_source
from tools.release_workflow.version_evidence import remove_managed
from tools.release_workflow.version_transition import TransitionPorts

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tests.unit.tools.release_workflow.repository_simulation import (
        ReleaseHistory,
        RepositoryObservations,
    )
    from tools.release_workflow.managed_files import ManagedTarget
    from tools.release_workflow.sources.model import Adapter, AdapterSettings
    from tools.release_workflow.windows_process import ProcessIdentity, ProcessState

BOM = b"\xef\xbb\xbf"
UMBRELLA_PATTERN = r"^APP_SERVICE_VERSION=(.+)$"
_FIRST_SIX = Span(0, 6)
FIXED_NOW = datetime(2026, 11, 9, 12, 0, tzinfo=timezone(timedelta(hours=1)))
TRANSITION_PID = 4242
EVIDENCE_NAME = "a.version-transition.20261109T120000+0100-4242"
TARGET = VersionToken.parse("0.14.0")
PATTERN_INI = f"[source:cicd-env]\nfile = cicd/config/.env\npattern = {UMBRELLA_PATTERN}\nform = snapshot\n"
DEMO = "demo-app"
REGISTRY_PACKAGE = '[[package]]\nname = "colorama"\nversion = "0.4.6"\nsource = { registry = "https://pypi.org/simple" }\n\n'
_EDITABLE_BUILD = '[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n\n'
_VIRTUAL_TOOL = "\n[tool.uv]\npackage = false\n"
DEMO_GROUP = "com.demo"
ENGINE_TRAILER = "Release tooling: llm-shared v0.14.0-3-gabc1234"
_POM_HEAD = ('<?xml version="1.0" encoding="UTF-8"?>\n<project xmlns="http://maven.apache.org/POM/4.0.0">\n'
             "  <modelVersion>4.0.0</modelVersion>\n")


@dataclass(frozen=True)
class RootSettings:
    """Adapter settings naming the project root, its declared pattern sources, component roots and form overrides.

    `authorize` applies the production physical path policy from the project root.
    """

    project_root: Path
    patterns: tuple[PatternDeclaration, ...] = ()
    components: Mapping[str, Path] = field(default_factory=dict[str, "Path"])
    forms: Mapping[str, Form] = field(default_factory=dict[str, Form])

    def participant(self, path: Path) -> str | None:
        """Name the participating root a physical path is, or return `None`."""
        return participant_names(self.project_root, self.components).get(os.path.normcase(str(path)))

    def authorize(self, path: Path) -> Path:
        """Apply the production physical path policy from the project root."""
        return authorize_source(self.project_root, path)


def version_txt(first_line: str = "0.14.0", notes: str = "", *, newline: str = "\n", bom: bool = False) -> bytes:
    """Build a `version.txt` document; `notes` uses LF, converted to `newline`."""
    text = first_line + newline + notes.replace("\n", newline)
    return (BOM if bom else b"") + text.encode("utf-8")


def write_version_txt(root: Path, content: bytes) -> Path:
    """Write the anchor document at a project root and return its path."""
    root.mkdir(parents=True, exist_ok=True)
    path = root / "version.txt"
    path.write_bytes(content)
    return path


def load_counts(view: FileView, *paths: Path) -> tuple[int, ...]:
    """Return how many times the view loaded each path."""
    return tuple(view.loads(path) for path in paths)


def lines_file(lines: Sequence[str], *, newline: str = "\n", bom: bool = False) -> bytes:
    """Build a line-oriented file such as `.env`, each line ended by `newline`."""
    return (BOM if bom else b"") + "".join(line + newline for line in lines).encode("utf-8")


def pyproject_toml(version: str = "0.13.0", *, layout: str = "virtual", name: str = DEMO, extra: str = "", newline: str = "\n") -> bytes:
    """Build a uv project manifest for a virtual or editable root; `extra` (LF) is appended."""
    head = _EDITABLE_BUILD if layout == "editable" else ""
    tail = _VIRTUAL_TOOL if layout == "virtual" else ""
    text = f'{head}[project]\nname = "{name}"\nversion = "{version}"\nrequires-python = ">=3.13"\ndependencies = []\n{tail}{extra}'
    return text.replace("\n", newline).encode("utf-8")


def uv_lock(version: str = "0.13.0", *, layout: str = "virtual", name: str = DEMO, revision: int = 5, packages: str = "") -> bytes:
    """Build an LF `uv.lock` whose root package follows `packages`, earlier `[[package]]` blocks."""
    text = (f'version = 1\nrevision = {revision}\nrequires-python = ">=3.13"\n\n{packages}'
            f'[[package]]\nname = "{name}"\nversion = "{version}"\nsource = {{ {layout} = "." }}\n')
    return text.encode("utf-8")


def crlf(content: bytes) -> bytes:
    """Convert LF line endings to CRLF."""
    return content.replace(b"\n", b"\r\n")


def _npm_json(data: Mapping[str, object]) -> bytes:
    """Format JSON as npm writes it: two-space indent, raw non-ASCII text, a final LF."""
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def package_json(version: str | None = "0.13.0", *, name: str | None = DEMO, **members: object) -> bytes:
    """Build an LF npm manifest; `None` omits the name or the version, and `members` follow them."""
    data: dict[str, object] = {} if name is None else {"name": name}
    if version is not None:
        data["version"] = version
    return _npm_json({**data, **members})


def package_lock(version: str = "0.13.0", *, lockfile: object = 3, top: bool = True, root: Mapping[str, object] | None = None,
                 packages: Mapping[str, object] | None = None) -> bytes:
    """Build an LF `package-lock.json` as npm writes it for a root package without dependencies.

    `top=False` omits the top-level version, `root` replaces the root package
    entry `packages[""]`, and `packages` adds entries after it.
    """
    head: dict[str, object] = {"name": DEMO, "version": version} if top else {"name": DEMO}
    entry = {"name": DEMO, "version": version} if root is None else root
    return _npm_json({**head, "lockfileVersion": lockfile, "requires": True, "packages": {"": entry, **(packages or {})}})


def pair_edit(adapter: Adapter, root: Path, target: VersionToken) -> dict[str, bytes]:
    """Return, by path relative to the root, the new contents one adapter's planned edit gives the files at a root.

    The files are detected and planned exactly as `versions set` plans them,
    with the adapter's default form, in memory: no file is written. The lock
    evidence recorder applies it to each "before" pair, and the evidence test
    compares it with the recorded edited pair.
    """
    view = FileView()
    found = adapter.detect(root, view, RootSettings(root))
    captures = tuple(FileCapture.of(path, view.read(path)) for path in dict.fromkeys(source.path for source in found.sources))
    claims = tuple(Claim(source.path, source.field, source.adapter, source.spans) for source in found.sources)
    edits = plan_edits(Inventory(found.sources, found.visible, claims, captures), target, adapters=(adapter,))
    return {edit.capture.path.relative_to(root).as_posix(): edit.new for edit in edits}


def gav(group: str | None, artifact: str, version: str | None = None) -> str:
    """Write Maven coordinate elements on one line; `None` omits the groupId or the version."""
    group_element = "" if group is None else f"<groupId>{group}</groupId>"
    version_element = "" if version is None else f"<version>{version}</version>"
    return f"{group_element}<artifactId>{artifact}</artifactId>{version_element}"


def pom_xml(*elements: str) -> bytes:
    """Build an LF POM whose `<project>` holds these element snippets, one per line."""
    body = "".join(f"  {element}\n" for element in elements)
    return (_POM_HEAD + body + "</project>\n").encode("utf-8")


def reactor_poms(version: str = "0.13.0-SNAPSHOT") -> dict[str, bytes]:
    """my-project's shape: an external parent, a literal root version and module `PDF` with a literal internal parent.

    `${project.version}` appears only in a plugin configuration value and the
    plugin version uses a property; neither is a version source.
    """
    plugin = (f"<build><plugins><plugin>{gav('org.demo.plugins', 'pack', '${pack.version}')}"
              "<configuration><finalName>pdf-${project.version}</finalName></configuration></plugin></plugins></build>")
    root = pom_xml(f"<parent>{gav('org.springframework.boot', 'spring-boot-starter-parent', '3.3.4')}</parent>",
                   gav(DEMO_GROUP, "demo-root", version), "<packaging>pom</packaging>",
                   "<properties><java.version>21</java.version><pack.version>1.2.3</pack.version></properties>",
                   "<modules><module>PDF</module></modules>", plugin)
    module = pom_xml(f"<parent>{gav(DEMO_GROUP, 'demo-root', version)}</parent>", gav(None, "PDF"))
    return {"pom.xml": root, "PDF/pom.xml": module}


def write_file(root: Path, relative: str, content: bytes) -> Path:
    """Write a file below a root, creating its directories, and return its path."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def write_release_ini(root: Path, text: str) -> Path:
    """Write the project's `.release.ini` as UTF-8."""
    return write_file(root, ".release.ini", text.encode("utf-8"))


def declare_pattern(root: Path, name: str = "cicd-env", file: str = ".env", pattern: str = UMBRELLA_PATTERN,
                    form: Form = Form.SNAPSHOT) -> PatternDeclaration:
    """Declare a pattern source as `read_settings` would, compiled with `re.MULTILINE`."""
    return PatternDeclaration(name, root / file, re.compile(pattern, re.MULTILINE), form)


def project_identity(root: Path) -> ProjectIdentity:
    """Supply a validated identity for a root without reproving Git discovery."""
    return ProjectIdentity(root, root / ".git", root / ".git", str(root))


def version_inputs(sandbox: GitSandbox, root: Path) -> VersionInputs:
    """Load the root's configuration and artifact declaration over the sandbox's Git port."""
    project = project_identity(root)
    git = sandbox.context()
    return VersionInputs(project, load_configuration(project), resolve_artifacts(project, git), git)


@dataclass(frozen=True)
class SyntheticAdapter:
    """A test adapter locating one fixed character span of one file at each root.

    It logs `(name, root)` for every detection call, reports a candidate when
    the content holds `version`, and renders a value as its UTF-8 bytes.
    """

    name: str
    forms: frozenset[Form] = frozenset()
    manifest_names: frozenset[str] = frozenset()
    file: str = "manifest.txt"
    key: str = "version"
    span: Span = _FIRST_SIX
    form: Form = Form.CORE
    log: list[tuple[str, Path]] = field(default_factory=list[tuple[str, "Path"]])

    @property
    def default_form(self) -> Form | None:
        """Return the form the synthetic source is located with."""
        return self.form

    def detect(self, root: Path, view: FileView, settings: AdapterSettings) -> Detection:
        """Log the call and locate the span when the file exists at this root."""
        del settings
        self.log.append((self.name, root))
        path = root / self.file
        content = view.read(path)
        if content is None:
            return Detection()
        value = content[self.span.start:self.span.end].decode("utf-8")
        return Detection((LocatedSource(path, self.key, self.name, self.form, value, (self.span,), root),))

    def render(self, source: LocatedSource, value: str) -> bytes:
        """Return the value's UTF-8 bytes."""
        del source
        return value.encode("utf-8")

    def has_project_version(self, name: str, content: bytes) -> bool:
        """Report a candidate when the content mentions `version`."""
        del name
        return b"version" in content


def version_project(sandbox: GitSandbox, files: Mapping[str, bytes], ini: str = "") -> VersionInputs:
    """Write the files and `.release.ini` of sandbox repository A and load its inputs."""
    root = sandbox.home / "A"
    if ini:
        write_release_ini(root, ini)
    for relative, content in files.items():
        write_file(root, relative, content)
    return version_inputs(sandbox, root)


@dataclass(frozen=True)
class RestorationFixture:
    """One adapter's files at 0.13.0 and how many files a `set 0.14.0` rewrites."""

    files: Mapping[str, bytes]
    ini: str = ""
    writes: int = 1


# The restoration contract registry: Step 5 adds the Python virtual and editable
# sets, Step 6 the npm format 2 (LF) and format 3 (CRLF) sets, whose lock holds
# two composed fields, Step 7 the Maven sets (my-project's CRLF reactor, and a
# marked root with inherited versions and internal dependencies) and the
# combined five-file project, now that every adapter exists (plan decision Q01).
RESTORATION_FIXTURES: dict[str, RestorationFixture] = {
    "anchor": RestorationFixture({"version.txt": version_txt("0.13.0 -- Old", "Notes\n", newline="\r\n", bom=True)}),
    "pattern": RestorationFixture({
        "version.txt": version_txt("0.13.0-SNAPSHOT"),
        "cicd/config/.env": lines_file(["A=1", "APP_SERVICE_VERSION=0.13.0-SNAPSHOT"], newline="\r\n"),
    }, PATTERN_INI, writes=2),
    "two-claims": RestorationFixture({
        "version.txt": version_txt("0.13.0"),
        "deploy.env": lines_file(["API=0.13.0", "WEB=0.13.0"]),
    }, "[source:api]\nfile = deploy.env\npattern = ^API=(.+)$\nform = core\n"
       "[source:web]\nfile = deploy.env\npattern = ^WEB=(.+)$\nform = snapshot\n", writes=2),
    "python-virtual": RestorationFixture({
        "version.txt": version_txt("0.13.0"),
        "pyproject.toml": pyproject_toml(name="Demo_App"),
        "uv.lock": uv_lock(revision=3, packages=REGISTRY_PACKAGE),
    }, writes=3),
    "python-editable": RestorationFixture({
        "version.txt": version_txt("0.13.0-SNAPSHOT", newline="\r\n"),
        "pyproject.toml": pyproject_toml(layout="editable", newline="\r\n"),
        "uv.lock": crlf(uv_lock(layout="editable")),
    }, writes=3),
    "npm-lock2": RestorationFixture({
        "version.txt": version_txt("0.13.0"),
        "package.json": package_json(private=True),
        "package-lock.json": package_lock(lockfile=2),
    }, writes=3),
    "npm-lock3-crlf": RestorationFixture({
        "version.txt": version_txt("0.13.0", newline="\r\n"),
        "package.json": crlf(package_json(private=True, description="Café 🎉")),
        "package-lock.json": crlf(package_lock(packages={"node_modules/left-pad": {"version": "0.13.0", "dev": True}})),
    }, writes=3),
    "maven-reactor": RestorationFixture({
        "version.txt": version_txt("0.13.0-SNAPSHOT", newline="\r\n"),
        **{name: crlf(content) for name, content in reactor_poms().items()},
    }, writes=3),
    "maven-inherited": RestorationFixture({
        "version.txt": version_txt("0.13.0-SNAPSHOT"),
        "pom.xml": BOM + pom_xml(gav(DEMO_GROUP, "demo-root", "0.13.0-SNAPSHOT"), "<packaging>pom</packaging>",
                                 "<modules><module>core</module><module>app</module></modules>",
                                 f"<dependencyManagement><dependencies><dependency>{gav(DEMO_GROUP, 'core', '0.13.0-SNAPSHOT')}"
                                 "</dependency></dependencies></dependencyManagement>"),
        "core/pom.xml": pom_xml(f"<parent>{gav(DEMO_GROUP, 'demo-root', '0.13.0-SNAPSHOT')}</parent>", gav(None, "core")),
        "app/pom.xml": pom_xml(f"<parent>{gav(DEMO_GROUP, 'demo-root', '0.13.0-SNAPSHOT')}</parent>", gav(None, "app"),
                               f"<dependencies><dependency>{gav('${project.groupId}', 'core', '${project.version}')}</dependency></dependencies>"),
    }, writes=4),
    "combined": RestorationFixture({
        "version.txt": version_txt("0.13.0-SNAPSHOT"),
        "pyproject.toml": pyproject_toml(),
        "package.json": package_json(private=True),
        "pom.xml": pom_xml(gav(DEMO_GROUP, "demo-root", "0.13.0-SNAPSHOT")),
        "cicd/config/.env": lines_file(["A=1", "APP_SERVICE_VERSION=0.13.0-SNAPSHOT"]),
    }, PATTERN_INI, writes=5),
}


@dataclass
class Faults:
    """Managed replacement and removal that record each call and fail the chosen ones.

    A source write is any replacement outside the artifact home; `fail_write`
    fails the one at that position. `fail_when` fails any replacement it
    accepts, `tamper` changes the bytes actually written, `after_write` runs
    after each source write, and `fail_remove` fails removing that name.
    """

    home: Path
    fail_write: int | None = None
    fail_when: Callable[[Path, bytes], bool] | None = None
    tamper: Callable[[Path, bytes], bytes] | None = None
    after_write: Callable[[int], None] | None = None
    fail_remove: str | None = None
    sources: list[Path] = field(default_factory=list["Path"])
    evidence: list[tuple[str, bytes]] = field(default_factory=list[tuple[str, bytes]])
    removed: list[str] = field(default_factory=list[str])

    def replace(self, target: ManagedTarget, content: bytes) -> None:
        """Record the write, fail it when chosen, otherwise replace the bytes."""
        path = target.path
        if self.fail_when is not None and self.fail_when(path, content):
            msg = f"injected failure writing {path.name}"
            raise ManagedWriteError(msg)
        if path.is_relative_to(self.home):
            self.evidence.append((path.name, content))
            replace_bytes(target, content)
            return
        position = len(self.sources)
        self.sources.append(path)
        if position == self.fail_write:
            msg = f"injected failure at source write {position}"
            raise ManagedWriteError(msg)
        replace_bytes(target, content if self.tamper is None else self.tamper(path, content))
        if self.after_write is not None:
            self.after_write(position)

    def remove(self, target: ManagedTarget) -> None:
        """Record the removal, fail it when chosen, otherwise remove the path."""
        if target.path.name == self.fail_remove:
            msg = f"injected failure removing {target.path.name}"
            raise OSError(msg)
        self.removed.append(target.path.name)
        remove_managed(target)

    def ports(self, probe: Callable[[ProcessIdentity], ProcessState]) -> TransitionPorts:
        """Return transition ports with these faults, a fixed clock and process id."""
        return TransitionPorts(replace=self.replace, remove=self.remove, probe=probe, clock=lambda: FIXED_NOW, pid=lambda: TRANSITION_PID)


@dataclass
class ViewLog:
    """A file-view factory that keeps every view it creates, in order."""

    views: list[FileView] = field(default_factory=list[FileView])

    def __call__(self) -> FileView:
        """Create, record and return a fresh view."""
        view = FileView()
        self.views.append(view)
        return view


def declare_evidence(home: Path, name: str, manifest: bytes | None, copies: Mapping[str, bytes] | None = None) -> Path:
    """Declare an evidence directory as a stopped transition left it.

    A home that does not exist yet is created with its `*` ignore file, as
    an earlier transition prepared it.
    """
    if not home.exists():
        home.mkdir(parents=True)
        (home / ".gitignore").write_bytes(b"*\n")
    directory = home / name
    directory.mkdir()
    for copy, content in (copies or {}).items():
        (directory / copy).write_bytes(content)
    if manifest is not None:
        (directory / "manifest.json").write_bytes(manifest)
    return directory


def source_bytes(root: Path, relative_paths: Sequence[str]) -> dict[str, bytes]:
    """Read the named files below a root."""
    return {relative: (root / relative).read_bytes() for relative in relative_paths}


def annotation(notes: str = "Release notes", *, trailer: bool = False, valid: bool = False) -> str:
    """Build a tag annotation as item 5 writes it: notes, then the tooling trailer, then `[valid]`."""
    lines = [notes, *([ENGINE_TRAILER] if trailer else []), *(["[valid]"] if valid else [])]
    return "\n".join(lines) + "\n"


def chain(history: ReleaseHistory, length: int, *, prefix: str = "c") -> list[str]:
    """Declare a linear history `c1 <- c2 <- ... <- cN` with HEAD and `main` on its last commit."""
    commits: list[str] = []
    for index in range(1, length + 1):
        commits.append(history.commit(f"{prefix}{index}", *commits[-1:]))
    history.head = history.main = commits[-1]
    return commits


def tagged_history(sandbox: GitSandbox, length: int, tags: Mapping[str, tuple[int, str | None]]) -> tuple[RepositoryObservations, ReleaseHistory]:
    """Declare a linear history and tags by name: commit position (1-based) and annotation, `None` for lightweight."""
    git = sandbox.context()
    history = git.facts.history
    commits = chain(history, length)
    for name, (position, text) in tags.items():
        history.tag(name, commits[position - 1], text)
    return git, history


# eof
