"""Combining every detector: roots, claims, composed edits and candidates.

Step 3 of v0.14.0 version-sources: every adapter runs over every participating
root in tuple order; a second claim on one path and field, overlapping spans
under different fields, two pattern sources on the same bytes and a pattern on
the anchor's token all fail before any write, naming both claimants. Disjoint
fields of one file compose from one original, read once. A declared component
root that is missing or not a directory fails. Candidates come from one Git
listing, skipping excluded directories, the artifact home, participating
directories and manifest files without a project version.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.version_support import (
    SyntheticAdapter,
    lines_file,
    load_counts,
    version_inputs,
    version_txt,
    write_file,
    write_release_ini,
)
from tools.release_workflow.sources import ADAPTERS, detection
from tools.release_workflow.sources.model import (
    FileCapture,
    FileView,
    Form,
    Inventory,
    LocatedSource,
    SourceChange,
    SourceError,
    Span,
    VersionToken,
    VisibleRecord,
)
from tools.release_workflow.sources.settings import EXCLUDED_DIRECTORIES, read_settings

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tools.release_workflow.sources.model import Adapter, VersionInputs

_PREFLIGHT = 2
_TARGET = VersionToken.parse("0.14.0")


def _project(sandbox: GitSandbox, ini: str = "", files: dict[str, bytes] | None = None) -> VersionInputs:
    """Write the project files of sandbox repository A and load its inputs."""
    root = sandbox.home / "A"
    if ini:
        write_release_ini(root, ini)
    for relative, content in (files or {}).items():
        write_file(root, relative, content)
    return version_inputs(sandbox, root)


def _fails(inputs: VersionInputs, adapters: tuple[Adapter, ...], message: str) -> None:
    """Expect detection to fail with status 2 before any write."""
    root = inputs.project.root
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
    with pytest.raises(SourceError, match=message) as caught:
        detection.detect(inputs, FileView(), adapters=adapters)
    assert caught.value.exit_code == _PREFLIGHT
    assert {path: path.read_bytes() for path in root.rglob("*") if path.is_file()} == before


def test_second_claim_on_one_path_and_field_names_both_claimants(git_sandbox: GitSandbox) -> None:
    """Two adapters locating the same field of one file fail."""
    inputs = _project(git_sandbox, files={"manifest.txt": b"0.13.0\n"})
    _fails(inputs, (SyntheticAdapter("one"), SyntheticAdapter("two")), r"manifest\.txt field version is claimed twice: by one version .* and by two version")


def test_overlapping_spans_under_different_fields_fail(git_sandbox: GitSandbox) -> None:
    """Different fields whose byte spans overlap fail, naming both claimants."""
    inputs = _project(git_sandbox, files={"manifest.txt": b"0.13.0 0.13.0\n"})
    adapters = (SyntheticAdapter("one", key="a", span=Span(0, 6)), SyntheticAdapter("two", key="b", span=Span(3, 9)))
    _fails(inputs, adapters, r"bytes \[3, 9\) of two b .* overlap bytes \[0, 6\) of one a")


def test_two_pattern_sources_on_the_same_bytes_fail(git_sandbox: GitSandbox) -> None:
    """Pattern sources capturing the same bytes of one file fail before any write."""
    declaration = "file = .env\npattern = ^APP=(.+)$\nform = snapshot\n"
    files = {"version.txt": version_txt("0.14.0"), ".env": lines_file(["APP=0.13.0"])}
    inputs = _project(git_sandbox, f"[source:first]\n{declaration}[source:second]\n{declaration}", files)
    _fails(inputs, ADAPTERS, r"pattern source:second .* overlap .* of pattern source:first")


def test_pattern_on_the_anchor_token_fails(git_sandbox: GitSandbox) -> None:
    """A pattern capturing bytes the anchor claims fails, naming both adapters."""
    files = {"version.txt": version_txt("0.13.0 -- Title")}
    inputs = _project(git_sandbox, "[source:token]\nfile = version.txt\npattern = ^([0-9.]+) --\nform = core\n", files)
    _fails(inputs, ADAPTERS, r"version\.txt: bytes \[0, 6\) of pattern source:token .* overlap bytes \[0, 6\) of anchor version")


def test_span_outside_its_file_fails(git_sandbox: GitSandbox) -> None:
    """A claim past the end of the captured file fails."""
    inputs = _project(git_sandbox, files={"manifest.txt": b"0.13\n"})
    _fails(inputs, (SyntheticAdapter("one", span=Span(0, 9)),), r"bytes \[0, 9\) of one version .* lie outside the 5 bytes")


@pytest.mark.parametrize(("make", "message"), [(False, "does not exist"), (True, "is not a directory")])
def test_component_root_must_be_an_existing_directory(git_sandbox: GitSandbox, *, make: bool, message: str) -> None:
    """A declared component root that is missing or a file fails detection."""
    files = {"web": b"not a directory"} if make else {}
    inputs = _project(git_sandbox, "[component:web]\nroot = web\n", files)
    _fails(inputs, (SyntheticAdapter("one"),), rf"\[component:web\] root .*web {message}")


def test_every_adapter_runs_over_every_root_in_tuple_order(git_sandbox: GitSandbox) -> None:
    """Adapters run in tuple order, each over the project root then the components in declaration order."""
    log: list[tuple[str, Path]] = []
    inputs = _project(git_sandbox, "[component:web]\nroot = web\n[component:api]\nroot = services/api\n",
                      {"web/manifest.txt": b"0.13.0\n", "services/api/other.txt": b"0.13.0\n"})
    root = inputs.project.root
    roots = (root, root / "web", root / "services/api")
    assert detection.participating_roots(read_settings(inputs.configuration)) == roots
    inventory = detection.detect(inputs, FileView(), adapters=(SyntheticAdapter("one", log=log), SyntheticAdapter("two", file="other.txt", log=log)))
    assert log == [("one", path) for path in roots] + [("two", path) for path in roots]
    assert [(source.adapter, source.root) for source in inventory.sources] == [("one", root / "web"), ("two", root / "services/api")]


def test_inventory_captures_each_participating_file_once(git_sandbox: GitSandbox) -> None:
    """The anchor and two pattern sources of one file: three claims, two captures, one load each."""
    env = lines_file(["API=0.13.0", "WEB=0.13.0"], newline="\r\n")
    ini = ("[source:api]\nfile = .env\npattern = ^API=(.+)$\nform = core\n"
           "[source:web]\nfile = .env\npattern = ^WEB=(.+)$\nform = snapshot\n")
    inputs = _project(git_sandbox, ini, {"version.txt": version_txt("0.14.0-SNAPSHOT"), ".env": env})
    root = inputs.project.root
    view = FileView()
    inventory = detection.detect(inputs, view)
    assert [(claim.adapter, claim.field) for claim in inventory.claims] == [("anchor", "version"), ("pattern", "source:api"), ("pattern", "source:web")]
    assert inventory.captures == (FileCapture.of(root / "version.txt", version_txt("0.14.0-SNAPSHOT")), FileCapture.of(root / ".env", env))
    assert load_counts(view, root / "version.txt", root / ".env") == (1, 1)
    assert inventory.visible == ()


def test_disjoint_fields_of_one_file_compose_from_one_original(git_sandbox: GitSandbox) -> None:
    """Two fields of one file change in one edit; files whose values already match yield no edit."""
    content = b"0.13.0 0.13.0\n"
    inputs = _project(git_sandbox, files={"version.txt": version_txt("0.14.0"), "manifest.txt": content})
    adapters = (ADAPTERS[0], SyntheticAdapter("one", key="a", span=Span(0, 6)), SyntheticAdapter("two", key="b", span=Span(7, 13)))
    inventory = detection.detect(inputs, FileView(), adapters=adapters)
    edit, = detection.plan_edits(inventory, _TARGET, adapters=adapters)
    root = inputs.project.root
    path = root / "manifest.txt"
    assert (edit.capture, edit.new) == (FileCapture.of(path, content), b"0.14.0 0.14.0\n")
    assert edit.changes == (SourceChange(path, "a", "one", "0.13.0", "0.14.0"), SourceChange(path, "b", "two", "0.13.0", "0.14.0"))
    anchor_edit, = detection.plan_edits(inventory, VersionToken.parse("0.13.0"), adapters=adapters)
    assert (anchor_edit.capture.path, anchor_edit.new) == (root / "version.txt", version_txt("0.13.0"))


def test_planning_refuses_a_release_only_value_above_the_target(git_sandbox: GitSandbox) -> None:
    """The release-only guard runs while planning, before any edit exists."""
    inputs = _project(git_sandbox, files={"manifest.txt": b"0.15.0\n"})
    adapters = (SyntheticAdapter("one", form=Form.RELEASE_ONLY),)
    inventory = detection.detect(inputs, FileView(), adapters=adapters)
    with pytest.raises(SourceError, match=r"release-only value 0\.15\.0 is higher than the target 0\.14\.0"):
        detection.plan_edits(inventory, _TARGET, adapters=adapters)


def test_planning_a_source_without_its_captured_file_fails(tmp_path: Path) -> None:
    """A changed source whose file was captured as absent cannot be planned."""
    path = tmp_path / "manifest.txt"
    source = LocatedSource(path, "version", "one", Form.CORE, "0.13.0", (Span(0, 6),), tmp_path)
    inventory = Inventory((source,), (), (), (FileCapture.of(path, None),))
    with pytest.raises(SourceError, match=r"manifest\.txt was captured as absent"):
        detection.plan_edits(inventory, _TARGET, adapters=(SyntheticAdapter("one"),))


def test_candidates_come_from_one_listing(git_sandbox: GitSandbox) -> None:
    """Only undeclared manifest files with a project version are candidates, each read once."""
    versioned = b'{"version": "1.0.0"}'
    excluded = {f"{name}/app/package.json": versioned for name in sorted(EXCLUDED_DIRECTORIES)}
    files = {"package.json": versioned, "web/package.json": versioned, "frontend/package.json": versioned,
             "tools/package.json": b"{}", ".reviews/copy/package.json": versioned, "module/pom.xml": b"<version>1</version>",
             "module/package.json": versioned, "docs/readme.md": versioned, **excluded}
    inputs = _project(git_sandbox, "[component:web]\nroot = web\n", files)
    git_sandbox.verified_git.facts.history.names = (*files, "gone/package.json")
    adapters = (SyntheticAdapter("npm", manifest_names=frozenset({"package.json"})),
                SyntheticAdapter("maven", manifest_names=frozenset({"pom.xml"}), file="module/pom.xml", span=Span(9, 10)))
    view = FileView()
    inventory = detection.detect(inputs, view, adapters=adapters)
    root = inputs.project.root
    assert detection.candidates(inputs, inventory, view, adapters=adapters) == (
        VisibleRecord(root / "frontend/package.json", "version", "npm", "not-participating undeclared"),)
    assert git_sandbox.verified_git.facts.history.calls == [("listing",)]
    assert load_counts(view, root / "frontend/package.json", root / "tools/package.json") == (1, 1)
    skipped = [root / name for name in (*excluded, ".reviews/copy/package.json", "module/package.json", "docs/readme.md")]
    assert load_counts(view, *skipped) == (0,) * len(skipped)


# eof
