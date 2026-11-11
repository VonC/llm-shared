"""The `python` adapter: `pyproject.toml` and its `uv.lock` at a participating root.

Step 5 of v0.14.0 version-sources: llm-shared's shape (`name = "LLM-Shared"`,
lock package `llm-shared`, `source = { virtual = "." }`) pairs by normalized
name, and an editable root pairs too; each file is read once and each value's
byte span holds it. Zero or two matching lock roots fail as ambiguous, a lock
without a manifest as orphan, and an unregistered lock schema, a lock with no
project name to pair or a root without a version string fail before any
write. An absent lock is not generated. A manifest without `[project]` gives
tool-only records for it and its lock. Dynamic and missing versions fail with
the remedy, so do unparsable files. A snapshot anchor gives `core` values,
and only the owned strings change. Candidates carry a static project version.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    REGISTRY_PACKAGE,
    RootSettings,
    crlf,
    load_counts,
    pyproject_toml,
    uv_lock,
    version_project,
    version_txt,
    write_file,
)
from tools.release_workflow.sources import detection, python
from tools.release_workflow.sources.model import (
    FileView,
    Form,
    SourceError,
    VersionToken,
    VisibleRecord,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.sources.model import Detection, LocatedSource

_PREFLIGHT = 2
_TOOL_ONLY = b"[tool.uv]\ndev-dependencies = []\n"
_VERSION_LINE = 'version = "0.13.0"\n'


def _detect(root: Path, view: FileView | None = None) -> Detection:
    """Detect at the project root with a fresh or a given view."""
    return python.ADAPTER.detect(root, FileView() if view is None else view, RootSettings(root))


def _fails(root: Path, named: str) -> None:
    """Expect a status 2 detection failure matching `named`."""
    with pytest.raises(SourceError, match=named) as caught:
        _detect(root)
    assert caught.value.exit_code == _PREFLIGHT


def _owned(source: LocatedSource) -> bytes:
    """Return the bytes the source's span holds."""
    span, = source.spans
    return source.path.read_bytes()[span.start:span.end]


def test_llm_shared_shape_pairs_by_normalized_name(tmp_path: Path) -> None:
    """`LLM-Shared` pairs with the virtual lock root `llm-shared`, after a registry package."""
    manifest = write_file(tmp_path, "pyproject.toml", pyproject_toml(name="LLM-Shared"))
    lock = write_file(tmp_path, "uv.lock", uv_lock(name="llm-shared", revision=3, packages=REGISTRY_PACKAGE))
    view = FileView()
    first, second = _detect(tmp_path, view).sources
    assert (first.path, first.field, first.adapter, first.form, first.value, first.root, first.manifest) == (
        manifest, "project.version", "python", Form.CORE, "0.13.0", tmp_path, None)
    assert (second.path, second.field, second.adapter, second.form, second.value, second.root, second.manifest) == (
        lock, "package.version", "python", Form.CORE, "0.13.0", tmp_path, manifest)
    assert (_owned(first), _owned(second)) == (b"0.13.0", b"0.13.0")
    assert load_counts(view, manifest, lock) == (1, 1)


def test_an_editable_root_pairs(tmp_path: Path) -> None:
    """A built project's lock root has an editable `.` source; CRLF files keep their spans."""
    write_file(tmp_path, "pyproject.toml", pyproject_toml(layout="editable", name="Demo.App", newline="\r\n"))
    write_file(tmp_path, "uv.lock", crlf(uv_lock(layout="editable")))
    sources = _detect(tmp_path).sources
    assert [(source.path.name, _owned(source)) for source in sources] == [("pyproject.toml", b"0.13.0"), ("uv.lock", b"0.13.0")]


@pytest.mark.parametrize(("lock", "count"), [
    (uv_lock(name="other-app"), 0),
    (uv_lock(layout="registry"), 0),
    (uv_lock(packages='[[package]]\nname = "demo-app"\nversion = "0.12.0"\nsource = { editable = "." }\n\n'), 2),
])
def test_zero_or_two_matching_lock_roots_are_ambiguous(tmp_path: Path, lock: bytes, count: int) -> None:
    """Exactly one root package named like the project with a local `.` source must exist."""
    write_file(tmp_path, "pyproject.toml", pyproject_toml())
    write_file(tmp_path, "uv.lock", lock)
    _fails(tmp_path, rf"uv\.lock: ambiguous lock root: {count} \[\[package\]\] entries are named 'demo-app' with a virtual or editable '\.' source")


def test_a_lock_without_a_manifest_is_an_orphan(tmp_path: Path) -> None:
    """A lock nobody declares fails rather than staying stale."""
    write_file(tmp_path, "uv.lock", uv_lock())
    _fails(tmp_path, r"uv\.lock is an orphan lock: no pyproject\.toml beside it")


def test_an_absent_lock_is_not_generated(tmp_path: Path) -> None:
    """The manifest alone is a source; no lock file appears."""
    write_file(tmp_path, "pyproject.toml", pyproject_toml())
    assert [source.path.name for source in _detect(tmp_path).sources] == ["pyproject.toml"]
    assert [path.name for path in tmp_path.iterdir()] == ["pyproject.toml"]


@pytest.mark.parametrize("lock", [True, False])
def test_without_project_both_files_are_tool_only(tmp_path: Path, *, lock: bool) -> None:
    """A tool configuration participates in nothing; its lock is listed with it."""
    manifest = write_file(tmp_path, "pyproject.toml", _TOOL_ONLY)
    records = [VisibleRecord(manifest, "project.version", "python", "not-participating tool-only")]
    if lock:
        path = write_file(tmp_path, "uv.lock", b"this lock is never parsed")
        records.append(VisibleRecord(path, "package.version", "python", "not-participating tool-only"))
    found = _detect(tmp_path)
    assert (found.sources, list(found.visible)) == ((), records)


@pytest.mark.parametrize(("manifest", "named"), [
    ('[project]\nname = "demo"\ndynamic = ["version"]\n', r"\[project\] lists version in dynamic.*declare a static version"),
    ('[project]\nname = "demo"\n', r"\[project\] has no version string; add version = \"X\.Y\.Z\""),
    ('[project]\nname = "demo"\nversion = 13\n', r"\[project\] has no version string"),
    ('[project]\nname = "demo"\nversion = "0.13\\u002e0"\n', r"the version in \[project\] reads .* escape sequences are unsupported"),
])
def test_dynamic_missing_or_escaped_versions_fail_with_the_remedy(tmp_path: Path, manifest: str, named: str) -> None:
    """A value versions set cannot write fails before any write, naming the file."""
    write_file(tmp_path, "pyproject.toml", manifest.encode())
    _fails(tmp_path, rf"pyproject\.toml: {named}")


@pytest.mark.parametrize(("files", "named"), [
    ({"pyproject.toml": b"[project\n"}, r"pyproject\.toml is not valid TOML: .*; correct the file"),
    ({"pyproject.toml": b"\xff[project]\n"}, r"pyproject\.toml is not valid UTF-8 at byte 0"),
    ({"pyproject.toml": pyproject_toml(), "uv.lock": b"version = = 1\n"}, r"uv\.lock is not valid TOML"),
])
def test_unparsable_files_fail(tmp_path: Path, files: dict[str, bytes], named: str) -> None:
    """Invalid TOML or UTF-8 fails with the file and its remedy."""
    for name, content in files.items():
        write_file(tmp_path, name, content)
    _fails(tmp_path, named)


@pytest.mark.parametrize(("manifest", "lock", "named"), [
    (pyproject_toml(), uv_lock(revision=4), r"uv\.lock: unsupported uv lock schema version 1, revision 4: only \(1, 3\) and \(1, 5\)"),
    (pyproject_toml(), uv_lock().replace(b"version = 1\n", b"version = true\n"), r"unsupported uv lock schema version True, revision 5"),
    (pyproject_toml(), uv_lock().replace(b"revision = 5\n", b""), r"unsupported uv lock schema version 1, revision None"),
    (pyproject_toml().replace(b'name = "demo-app"\n', b""), uv_lock(), r"\[project\] has no name, so .*uv\.lock cannot be paired"),
    (pyproject_toml(), uv_lock().replace(_VERSION_LINE.encode(), b""), r"the \[\[package\]\] entry 'demo-app' has no version string"),
])
def test_lock_problems_fail_before_any_write(tmp_path: Path, manifest: bytes, lock: bytes, named: str) -> None:
    """Only registered schemas pair, and only with a named project and a versioned root package."""
    write_file(tmp_path, "pyproject.toml", manifest)
    write_file(tmp_path, "uv.lock", lock)
    _fails(tmp_path, named)


def test_a_snapshot_anchor_gives_core_values_and_only_the_owned_strings_change(git_sandbox: GitSandbox) -> None:
    """`0.14.0-SNAPSHOT` sets `0.14.0` in both files; every other byte stays."""
    lock = crlf(uv_lock(packages=REGISTRY_PACKAGE))
    inputs = version_project(git_sandbox, {"version.txt": version_txt("0.14.0-SNAPSHOT"), "pyproject.toml": pyproject_toml(), "uv.lock": lock})
    inventory = detection.detect(inputs, FileView())
    edits = detection.plan_edits(inventory, VersionToken.parse("0.14.0-SNAPSHOT"))
    assert {edit.capture.path.name: edit.new for edit in edits} == {
        "pyproject.toml": pyproject_toml("0.14.0"), "uv.lock": crlf(uv_lock("0.14.0", packages=REGISTRY_PACKAGE))}
    assert [(change.field, change.old, change.new) for edit in edits for change in edit.changes] == [
        ("project.version", "0.13.0", "0.14.0"), ("package.version", "0.13.0", "0.14.0")]


@pytest.mark.parametrize(("content", "candidate"), [
    (pyproject_toml(), True),
    (_TOOL_ONLY, False),
    (b'[project]\nname = "demo"\ndynamic = ["version"]\n', False),
    (b"[project\n", False),
    (b"\xff", False),
])
def test_a_candidate_carries_a_static_project_version(content: bytes, *, candidate: bool) -> None:
    """Only a manifest with its own version string is an undeclared candidate."""
    assert python.ADAPTER.has_project_version("pyproject.toml", content) is candidate


def test_the_adapter_renders_the_string_content(tmp_path: Path) -> None:
    """A value renders as the bytes between the quotes, in a core-only form set."""
    write_file(tmp_path, "pyproject.toml", pyproject_toml())
    source, = _detect(tmp_path).sources
    assert python.ADAPTER.render(source, "0.14.0") == b"0.14.0"
    assert (python.ADAPTER.name, python.ADAPTER.default_form, python.ADAPTER.forms) == ("python", Form.CORE, frozenset({Form.CORE}))
    assert python.ADAPTER.manifest_names == frozenset({"pyproject.toml"})
    assert python.normalize("My_App..Core-") == "my-app-core-"
    assert python.normalize("LLM.Shared") == "llm-shared"


# eof
