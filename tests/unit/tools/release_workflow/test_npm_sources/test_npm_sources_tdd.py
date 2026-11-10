"""The `npm` adapter: `package.json` and its `package-lock.json` at a participating root.

Step 6 of v0.14.0 version-sources: workspace-halo's shape (format 3, CRLF
lock) changes only the manifest version and the two lock version strings,
each file read once; Yarn and pnpm locks are never read. The default
`release-only` form keeps `0.0.25` for anchor `0.0.25-SNAPSHOT`, and
`[source:npm] form = snapshot` gives the suffix. A release-only source at
`0.0.25` refuses `set 0.0.24` before any write, its value differing from its
expected value, which `check` (Step 9) reports as drift. A manifest without
`version` gives tool-only records for it and its lock. A `workspaces` field, a
shrinkwrap file and `file:`, `link:` or `workspace:` references into another
participating root fail before any write, naming both roots; other references
stay external. Formats 2 and 3 locate the top-level `version` where present
and `packages[""].version`; format 1 fails with the remedy to regenerate the
lock with npm 7 or later; another format, a root entry naming another
package, a missing root version and an orphan lock fail, so do unparsable,
ambiguous and escaped values. Candidates carry their own version.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    BOM,
    Faults,
    RootSettings,
    crlf,
    load_counts,
    package_json,
    package_lock,
    source_bytes,
    version_project,
    version_txt,
    write_file,
)
from tools.release_workflow.sources import detection, npm
from tools.release_workflow.sources.model import (
    FileView,
    Form,
    SourceError,
    VersionToken,
    VisibleRecord,
)
from tools.release_workflow.version_transition import set_versions

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.sources.model import Detection, LocatedSource

_PREFLIGHT = 2
_ROOT_FIELD = 'packages[""].version'
_LINK = "local links between participating components are unsupported"
_LEFT_PAD = {"node_modules/left-pad": {"version": "0.0.24", "dev": True}}
_COMPONENTS = "[component:api]\nroot = api\n[component:web]\nroot = web\n"


def _detect(root: Path, view: FileView | None = None, settings: RootSettings | None = None) -> Detection:
    """Detect at a root with a fresh or a given view and the root's own settings by default."""
    return npm.ADAPTER.detect(root, FileView() if view is None else view, RootSettings(root) if settings is None else settings)


def _fails(root: Path, named: str) -> None:
    """Expect a status 2 detection failure matching `named`."""
    with pytest.raises(SourceError, match=named) as caught:
        _detect(root)
    assert caught.value.exit_code == _PREFLIGHT


def _owned(source: LocatedSource) -> bytes:
    """Return the bytes the source's span holds."""
    span, = source.spans
    return source.path.read_bytes()[span.start:span.end]


def _components(root: Path, files: dict[str, bytes]) -> RootSettings:
    """Write the files and declare the `api` and `web` components below the project root."""
    for name in ("api", "web"):
        (root / name).mkdir(exist_ok=True)
    for relative, content in files.items():
        write_file(root, relative, content)
    return RootSettings(root, components={"api": root / "api", "web": root / "web"})


def test_workspace_halo_shape_changes_only_the_three_version_strings(git_sandbox: GitSandbox) -> None:
    """A CRLF format 3 lock keeps every other byte; a dependency's version is not a source."""
    files = {"version.txt": version_txt("0.0.24-SNAPSHOT"), "package.json": package_json("0.0.24", private=True),
             "package-lock.json": crlf(package_lock("0.0.24", packages=_LEFT_PAD)), "yarn.lock": b"# yarn\n",
             "pnpm-lock.yaml": b"lockfileVersion: '9.0'\n"}
    inputs = version_project(git_sandbox, files)
    view = FileView()
    inventory = detection.detect(inputs, view)
    assert [(source.path.name, source.field, source.form, source.value) for source in inventory.sources if source.adapter == "npm"] == [
        ("package.json", "version", Form.RELEASE_ONLY, "0.0.24"), ("package-lock.json", "version", Form.RELEASE_ONLY, "0.0.24"),
        ("package-lock.json", _ROOT_FIELD, Form.RELEASE_ONLY, "0.0.24")]
    edits = detection.plan_edits(inventory, VersionToken.parse("0.0.25-SNAPSHOT"))
    assert {edit.capture.path.name: edit.new for edit in edits} == {
        "version.txt": version_txt("0.0.25-SNAPSHOT"), "package.json": package_json("0.0.25", private=True),
        "package-lock.json": crlf(package_lock("0.0.25", packages=_LEFT_PAD))}
    root = inputs.project.root
    assert load_counts(view, *(root / name for name in ("package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"))) == (1, 1, 0, 0)


@pytest.mark.parametrize(("ini", "form", "changed"), [
    ("", Form.RELEASE_ONLY, set[str]()),
    ("[source:npm]\nform = core\n", Form.CORE, set[str]()),
    ("[source:npm]\nform = snapshot\n", Form.SNAPSHOT, {"0.0.25-SNAPSHOT"}),
])
def test_the_form_decides_the_expected_value(git_sandbox: GitSandbox, ini: str, form: Form, changed: set[str]) -> None:
    """Release-only and core keep `0.0.25` for anchor `0.0.25-SNAPSHOT`; a snapshot form gives the suffix."""
    files = {"version.txt": version_txt("0.0.25-SNAPSHOT"), "package.json": package_json("0.0.25"), "package-lock.json": package_lock("0.0.25")}
    inventory = detection.detect(version_project(git_sandbox, files, ini), FileView())
    assert {source.form for source in inventory.sources if source.adapter == "npm"} == {form}
    edits = detection.plan_edits(inventory, VersionToken.parse("0.0.25-SNAPSHOT"))
    assert {change.new for edit in edits for change in edit.changes} == changed


def test_a_release_only_value_above_the_target_refuses_before_any_write(git_sandbox: GitSandbox, lock_facts: LockFacts) -> None:
    """`set 0.0.24` stops while planning, naming the source, its value and the target."""
    files = {"version.txt": version_txt("0.0.25"), "package.json": package_json("0.0.25"), "package-lock.json": package_lock("0.0.25")}
    inputs = version_project(git_sandbox, files)
    faults = Faults(inputs.artifacts.home)
    target = VersionToken.parse("0.0.24")
    with pytest.raises(SourceError, match=r"package\.json version: release-only value 0\.0\.25 is higher than the target 0\.0\.24") as caught:
        set_versions(inputs, target, ports=faults.ports(lock_facts.probe))
    assert caught.value.exit_code == _PREFLIGHT
    assert (faults.sources, faults.evidence) == ([], [])
    assert source_bytes(inputs.project.root, list(files)) == files
    manifest, = (source for source in detection.detect(inputs, FileView()).sources if source.path.name == "package.json")
    assert (manifest.value, manifest.form.expected(target)) == ("0.0.25", "0.0.24")


@pytest.mark.parametrize("lock", [True, False])
def test_without_a_version_both_files_are_tool_only(tmp_path: Path, *, lock: bool) -> None:
    """A manifest without `version` participates in nothing; its lock is listed with it, never parsed."""
    manifest = write_file(tmp_path, "package.json", package_json(None, private=True, scripts={"lint": "eslint ."}))
    records = [VisibleRecord(manifest, "version", "npm", "not-participating tool-only")]
    if lock:
        path = write_file(tmp_path, "package-lock.json", b"this lock is never parsed")
        records.append(VisibleRecord(path, _ROOT_FIELD, "npm", "not-participating tool-only"))
    found = _detect(tmp_path)
    assert (found.sources, list(found.visible)) == ((), records)


@pytest.mark.parametrize("version", ["0.13.0", None])
def test_a_workspaces_field_fails(tmp_path: Path, version: str | None) -> None:
    """Npm workspaces are unsupported, whether or not the root package has a version."""
    write_file(tmp_path, "package.json", package_json(version, workspaces=["packages/*"]))
    _fails(tmp_path, r"package\.json declares workspaces: npm workspaces are unsupported")


def test_a_shrinkwrap_file_fails(tmp_path: Path) -> None:
    """Npm prefers `npm-shrinkwrap.json`, which versions set would leave stale."""
    write_file(tmp_path, "package.json", package_json())
    write_file(tmp_path, "npm-shrinkwrap.json", package_lock())
    _fails(tmp_path, r"npm-shrinkwrap\.json takes precedence over package-lock\.json")


@pytest.mark.parametrize(("lockfile", "top"), [(2, True), (3, True), (3, False), (2, False)])
def test_formats_2_and_3_locate_both_lock_fields(tmp_path: Path, lockfile: int, *, top: bool) -> None:
    """The top-level version where present and the root entry's version, each read once."""
    manifest = write_file(tmp_path, "package.json", BOM + package_json())
    lock = write_file(tmp_path, "package-lock.json", package_lock(lockfile=lockfile, top=top, packages={"node_modules/x": {"version": "0.13.0"}}))
    view = FileView()
    sources = _detect(tmp_path, view).sources
    lock_fields = ["version", _ROOT_FIELD] if top else [_ROOT_FIELD]
    assert [(source.path.name, source.field) for source in sources] == [
        ("package.json", "version"), *(("package-lock.json", field) for field in lock_fields)]
    assert [(_owned(source), source.form, source.root, source.manifest) for source in sources] == [
        (b"0.13.0", Form.RELEASE_ONLY, tmp_path, None), *((b"0.13.0", Form.RELEASE_ONLY, tmp_path, manifest) for _ in lock_fields)]
    assert load_counts(view, manifest, lock) == (1, 1)


@pytest.mark.parametrize(("lock", "named"), [
    (package_lock(lockfile=1), r"lockfileVersion 1 is unsupported.*regenerate the lock with npm 7 or later"),
    (package_lock(lockfile=4), r"unsupported lockfileVersion 4: only 2 and 3 are supported"),
    (package_lock(lockfile="3"), r"unsupported lockfileVersion '3'"),
    (package_lock(lockfile=True), r"unsupported lockfileVersion True"),
    (b'{"name": "demo-app", "version": "0.13.0", "requires": true, "packages": {}}', r"unsupported lockfileVersion None"),
    (package_lock(root={"name": "other-app", "version": "0.13.0"}), r"packages\[\"\"\] names 'other-app', not 'demo-app'"),
    (package_lock(root={"name": "demo-app"}), r"packages\[\"\"\]\.version is missing or not a string"),
    (b'{"name": "demo-app", "version": "0.13.0", "lockfileVersion": 3, "packages": {}}', r"packages\[\"\"\]\.version is missing"),
    (package_lock().replace(b'"version": "0.13.0",\n  "lockfileVersion"', b'"version": 13,\n  "lockfileVersion"'),
     r"the top-level version is not a string"),
    (package_lock().replace(b'  "lockfileVersion"', b'  "version": "0.13.0",\n  "lockfileVersion"'), r"package-lock\.json: version is ambiguous"),
    (package_lock().replace(b'"lockfileVersion": 3', b'"lockfileVersion": 1, "lockfileVersion": 3'), r"lockfileVersion is ambiguous"),
    (package_lock().replace(b'"version": "0.13.0"\n    }', b'"version": "0.13\\u002e0"\n    }'),
     r"packages\[\"\"\]\.version value reads .* escape sequences are unsupported"),
    (b"[]", r"package-lock\.json: the JSON root is not an object"),
    (b"{", r"package-lock\.json is not valid JSON: .*; correct the file"),
])
def test_lock_problems_fail_before_any_write(tmp_path: Path, lock: bytes, named: str) -> None:
    """Only formats 2 and 3 of this package, with a root version string, pair."""
    write_file(tmp_path, "package.json", package_json())
    write_file(tmp_path, "package-lock.json", lock)
    _fails(tmp_path, named)


def test_a_root_entry_without_a_name_pairs_with_an_unnamed_manifest(tmp_path: Path) -> None:
    """Npm names the root entry after the folder when the manifest has no name, so only a named manifest is compared."""
    write_file(tmp_path, "package.json", package_json(name=None))
    write_file(tmp_path, "package-lock.json", package_lock(root={"name": "folder-name", "version": "0.13.0"}))
    assert [source.field for source in _detect(tmp_path).sources] == ["version", "version", _ROOT_FIELD]


def test_a_lock_without_a_manifest_is_an_orphan(tmp_path: Path) -> None:
    """A lock nobody declares fails rather than staying stale."""
    write_file(tmp_path, "package-lock.json", package_lock())
    _fails(tmp_path, r"package-lock\.json is an orphan lock: no package\.json beside it")


@pytest.mark.parametrize(("manifest", "named"), [
    (b"{", r"package\.json is not valid JSON"),
    (b"\xff{}", r"package\.json is not valid UTF-8 at byte 0"),
    (b'["version"]', r"package\.json: the JSON root is not an object"),
    (b'{"name": "demo-app", "version": 13}', r'package\.json: version is not a string; write "version": "X\.Y\.Z"'),
    (b'{"version": "0.13.0", "version": "0.13.0"}', r"package\.json: version is ambiguous"),
    (b'{"version": "0.13\\u002e0"}', r"package\.json: the version value reads .* escape sequences are unsupported"),
])
def test_unusable_manifests_fail(tmp_path: Path, manifest: bytes, named: str) -> None:
    """A manifest versions set cannot read or write exactly fails, naming the file."""
    write_file(tmp_path, "package.json", manifest)
    _fails(tmp_path, named)


@pytest.mark.parametrize(("name", "section", "spec", "other"), [
    ("web", "dependencies", "file:../web", r"\[component:web\]"),
    ("web", "devDependencies", "link:../WEB/", r"\[component:web\]"),
    ("root", "optionalDependencies", "file:..", "the project root"),
    ("web", "peerDependencies", "WEB_URI", r"\[component:web\]"),
    ("@demo/web", "dependencies", "workspace:*", r"\[component:web\]"),
])
def test_local_links_into_another_participating_root_fail(tmp_path: Path, name: str, section: str, spec: str, other: str) -> None:
    """A `file:` or `link:` destination, or a `workspace:` package name, that is a participating root fails, naming both."""
    spec = spec.replace("WEB_URI", (tmp_path / "web").as_uri())
    manifest = json.dumps({"name": "api", "version": "0.13.0", section: {name: spec}}).encode()
    settings = _components(tmp_path, {"api/package.json": manifest, "web/package.json": package_json(name="@demo/web")})
    match = rf"api[\\/]package\.json: {section} '{name}' '.*' links \[component:api\] to {other} .*{_LINK}"
    with pytest.raises(SourceError, match=match):
        _detect(tmp_path / "api", settings=settings)


def test_external_references_stay_unchanged(tmp_path: Path) -> None:
    """Registry ranges, outside paths, tarballs, Git and URL specifiers, and other packages' `workspace:` names are external."""
    dependencies = {"left-pad": "^1.3.0", "near": "file:../vendor/near", "tarball": "file:../web.tgz", "far": "link:../../outside",
                    "git": "github:example/lib", "url": "https://example.org/x.tgz", "tool": "workspace:^1", "odd": {"version": "1"}}
    files = {"api/package.json": package_json(name="api", dependencies=dependencies, devDependencies={"web": "workspace:*"}),
             "web/package.json": b"{", "package.json": package_json(None, name="tool")}
    settings = _components(tmp_path, files)
    assert [(source.field, source.value, source.root) for source in _detect(tmp_path / "api", settings=settings).sources] == [
        ("version", "0.13.0", tmp_path / "api")]


def test_a_link_between_declared_components_fails_through_detection(git_sandbox: GitSandbox) -> None:
    """With `.release.ini` components, the settings name both ends of the link."""
    files = {"version.txt": version_txt("0.13.0"), "api/package.json": package_json(name="api", dependencies={"web": "file:../web"}),
             "web/package.json": package_json(name="web")}
    with pytest.raises(SourceError, match=rf"links \[component:api\] to \[component:web\] .*{_LINK}"):
        detection.detect(version_project(git_sandbox, files, _COMPONENTS), FileView())


def test_workspace_names_are_indexed_once_per_view(git_sandbox: GitSandbox) -> None:
    """Two `workspace:` references and three roots still read each manifest once; a tool-only package is not participating."""
    files = {"version.txt": version_txt("0.13.0"), "package.json": package_json(name="root", dependencies={"web": "workspace:*"}),
             "api/package.json": package_json(name="api", dependencies={"web": "workspace:^0"}),
             "web/package.json": package_json(None, name="web")}
    inputs = version_project(git_sandbox, files, _COMPONENTS)
    view = FileView()
    inventory = detection.detect(inputs, view)
    root = inputs.project.root
    assert [source.path for source in inventory.sources if source.adapter == "npm"] == [root / "package.json", root / "api/package.json"]
    assert load_counts(view, root / "package.json", root / "api/package.json", root / "web/package.json") == (1, 1, 1)


@pytest.mark.parametrize(("content", "candidate"), [
    (package_json(), True),
    (BOM + package_json(), True),
    (package_json(None), False),
    (b'{"version": 1}', False),
    (b"[]", False),
    (b"{", False),
    (b"\xff", False),
])
def test_a_candidate_carries_its_own_version(content: bytes, *, candidate: bool) -> None:
    """Only a manifest with its own version string is an undeclared candidate."""
    assert npm.ADAPTER.has_project_version("package.json", content) is candidate


def test_the_adapter_renders_the_string_content(tmp_path: Path) -> None:
    """A value renders as the bytes between the quotes; the forms are the design's."""
    write_file(tmp_path, "package.json", package_json())
    source, = _detect(tmp_path).sources
    assert npm.ADAPTER.render(source, "0.14.0-SNAPSHOT") == b"0.14.0-SNAPSHOT"
    assert (npm.ADAPTER.name, npm.ADAPTER.default_form, npm.ADAPTER.forms) == ("npm", Form.RELEASE_ONLY, frozenset(Form))
    assert (npm.ADAPTER.manifest_names, npm.SUPPORTED_LOCK_FORMATS) == (frozenset({"package.json"}), frozenset({2, 3}))


# eof
