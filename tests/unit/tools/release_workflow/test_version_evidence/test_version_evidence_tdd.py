"""Recovery evidence: one copy per file, a strict manifest, its states and listing.

Step 4 of v0.14.0 version-sources: evidence holds one copy of each captured
participating file and a manifest (owner, target, state, created time with
offset, and each file's path, SHA-256, existence and copy name), written last.
A failed write removes the partial directory, or names what remains when it
cannot. Marking replaces the manifest
through the managed replacement; deletion removes the copies, then the
manifest, then the directory, refusing any copy that resolves outside it, and
decoding accepts only `original.<n>` copy names (code review, step 4 round 1). The listing reads only the artifact home and
classifies residue, interrupted, unreadable and lifecycle-owned evidence.
Allocation (plan decision Q17) never enters an existing directory: it takes
the next `-2`, `-3` suffix, up to a fixed number of attempts; any other
creation failure stops at once.
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.acceptance_support import snapshot
from tests.unit.tools.release_workflow.version_support import (
    EVIDENCE_NAME,
    FIXED_NOW,
    TRANSITION_PID,
    Faults,
    declare_evidence,
    project_identity,
    write_file,
)
from tools.release_workflow.artifacts import ArtifactDeclaration, PreparedArtifacts
from tools.release_workflow.managed_files import authorize_write, replace_bytes
from tools.release_workflow.sources.model import FileCapture
from tools.release_workflow.version_evidence import (
    STANDALONE,
    EvidenceDirectory,
    EvidenceError,
    EvidenceFile,
    EvidenceKind,
    EvidenceManifest,
    EvidenceState,
    allocate,
    evidence_files,
    find_evidence,
    remove_managed,
    write_evidence,
)

if TYPE_CHECKING:
    from pathlib import Path

_EXECUTION = 1


def _prepared(root: Path) -> PreparedArtifacts:
    """Prepare an artifact home holding only its ignore file."""
    home = root / ".reviews"
    home.mkdir(parents=True)
    (home / ".gitignore").write_bytes(b"*\n")
    project = project_identity(root)
    return PreparedArtifacts(project, authorize_write(project, home))


def _declaration(prepared: PreparedArtifacts) -> ArtifactDeclaration:
    """Declare the same home the way invocation preflight resolves it."""
    project = prepared.project
    return ArtifactDeclaration(project, authorize_write(project, ".review-artifacts.ini"), prepared.destination, declared=False)


def _captures(root: Path) -> tuple[FileCapture, ...]:
    """Capture two present files and one absent file."""
    first = write_file(root, "version.txt", b"0.13.0\n")
    second = write_file(root, "sub/.env", b"V=0.13.0\r\n")
    return FileCapture.of(first, b"0.13.0\n"), FileCapture.of(second, b"V=0.13.0\r\n"), FileCapture.of(root / "gone.txt", None)


def _manifest(owner: str = STANDALONE, state: EvidenceState = EvidenceState.COMPLETE) -> bytes:
    """Encode a manifest with no file, for listing cases."""
    return EvidenceManifest(owner, "0.14.0", state, FIXED_NOW.isoformat(), ()).encode()


def _write(prepared: PreparedArtifacts, faults: Faults | None = None) -> EvidenceDirectory:
    """Allocate and write standalone evidence for the three captures."""
    captures = _captures(prepared.project.root)
    manifest = EvidenceManifest.of(STANDALONE, "0.14.0", FIXED_NOW, evidence_files(prepared.project.root, captures))
    directory = allocate(prepared, FIXED_NOW, TRANSITION_PID)
    replace = replace_bytes if faults is None else faults.replace
    return write_evidence(directory, manifest, captures, replace=replace, remove=remove_managed)


def test_written_evidence_holds_each_original_and_a_writing_manifest(tmp_path: Path) -> None:
    """Present files are copied; the manifest records every capture, absent ones included."""
    prepared = _prepared(tmp_path)
    evidence = _write(prepared)
    directory = evidence.path
    assert directory == prepared.home / EVIDENCE_NAME
    assert sorted(path.name for path in directory.iterdir()) == ["manifest.json", "original.1", "original.2"]
    assert ((directory / "original.1").read_bytes(), (directory / "original.2").read_bytes()) == (b"0.13.0\n", b"V=0.13.0\r\n")
    manifest = EvidenceManifest.decode((directory / "manifest.json").read_bytes())
    assert manifest == evidence.manifest
    assert (manifest.owner, manifest.target, manifest.state, manifest.created) == (STANDALONE, "0.14.0", EvidenceState.WRITING, "2026-11-09T12:00:00+01:00")
    assert manifest.files == (
        EvidenceFile("version.txt", hashlib.sha256(b"0.13.0\n").hexdigest(), exists=True, copy="original.1"),
        EvidenceFile("sub/.env", hashlib.sha256(b"V=0.13.0\r\n").hexdigest(), exists=True, copy="original.2"),
        EvidenceFile("gone.txt", None, exists=False, copy=None),
    )
    assert evidence.copy_path("sub/.env") == directory / "original.2"
    assert evidence.copy_path("gone.txt") is None


@pytest.mark.parametrize("failing", ["original.2", "manifest.json"])
def test_failed_write_removes_the_partial_directory(tmp_path: Path, failing: str) -> None:
    """A copy or the manifest that cannot be written leaves no evidence behind (status 1)."""
    prepared = _prepared(tmp_path)
    faults = Faults(prepared.home, fail_when=lambda path, _content: path.name == failing)
    with pytest.raises(EvidenceError, match=failing) as caught:
        _write(prepared, faults)
    assert caught.value.exit_code == _EXECUTION
    assert [path.name for path in prepared.home.iterdir()] == [".gitignore"]


def test_failed_write_and_failed_cleanup_names_the_residue(tmp_path: Path) -> None:
    """When the partial directory cannot be removed either, the error says what remains."""
    prepared = _prepared(tmp_path)
    faults = Faults(prepared.home, fail_when=lambda path, _content: path.name == "manifest.json", fail_remove="original.1")
    captures = _captures(prepared.project.root)
    manifest = EvidenceManifest.of(STANDALONE, "0.14.0", FIXED_NOW, evidence_files(prepared.project.root, captures))
    directory = allocate(prepared, FIXED_NOW, TRANSITION_PID)
    with pytest.raises(EvidenceError, match=r"manifest\.json.*with its copies and manifest remains") as caught:
        write_evidence(directory, manifest, captures, replace=faults.replace, remove=faults.remove)
    assert caught.value.exit_code == _EXECUTION
    assert (directory.path / "original.1").read_bytes() == b"0.13.0\n"


def test_marking_replaces_the_manifest_through_the_managed_write(tmp_path: Path) -> None:
    """Each state is written in one replacement; a failed mark keeps the previous manifest."""
    prepared = _prepared(tmp_path)
    evidence = _write(prepared)
    faults = Faults(prepared.home)
    complete = evidence.mark(EvidenceState.COMPLETE, faults.replace)
    incomplete = complete.mark(EvidenceState.RESTORATION_INCOMPLETE, faults.replace)
    assert [name for name, _content in faults.evidence] == ["manifest.json", "manifest.json"]
    assert (complete.manifest.state, incomplete.manifest.state) == (EvidenceState.COMPLETE, EvidenceState.RESTORATION_INCOMPLETE)
    manifest = incomplete.path / "manifest.json"
    assert EvidenceManifest.decode(manifest.read_bytes()) == incomplete.manifest
    before = manifest.read_bytes()
    failing = Faults(prepared.home, fail_when=lambda path, _content: path.name == "manifest.json")
    with pytest.raises(EvidenceError, match="manifest"):
        incomplete.mark(EvidenceState.COMPLETE, failing.replace)
    assert manifest.read_bytes() == before


def test_deletion_removes_copies_then_the_manifest_then_the_directory(tmp_path: Path) -> None:
    """The manifest outlives every copy, and the directory goes last."""
    prepared = _prepared(tmp_path)
    evidence = _write(prepared)
    faults = Faults(prepared.home)
    evidence.delete(faults.remove)
    assert faults.removed == ["original.1", "original.2", "manifest.json", EVIDENCE_NAME]
    assert [path.name for path in prepared.home.iterdir()] == [".gitignore"]


def test_deletion_never_leaves_the_evidence_directory(tmp_path: Path) -> None:
    """A copy name resolving outside the directory is refused before anything is removed."""
    prepared = _prepared(tmp_path)
    evidence = _write(prepared)
    outside = write_file(prepared.home, "version.txt", b"keep")
    entry = EvidenceFile("version.txt", None, exists=True, copy="../version.txt")
    unsafe = EvidenceDirectory(evidence.target, EvidenceManifest(STANDALONE, "0.14.0", EvidenceState.COMPLETE, FIXED_NOW.isoformat(), (entry,)))
    with pytest.raises(EvidenceError, match="outside the evidence directory"):
        unsafe.delete(remove_managed)
    assert outside.read_bytes() == b"keep"
    assert (evidence.path / "manifest.json").is_file()


@pytest.mark.parametrize(("failing", "residue"), [
    ("original.1", "evidence directory .* with its copies and manifest"),
    ("manifest.json", r"evidence manifest .*manifest\.json"),
    (EVIDENCE_NAME, "empty evidence directory"),
])
def test_failed_deletion_names_the_residue(tmp_path: Path, failing: str, residue: str) -> None:
    """A removal failure reports what remains, with status 1."""
    prepared = _prepared(tmp_path)
    evidence = _write(prepared)
    with pytest.raises(EvidenceError, match=residue) as caught:
        evidence.delete(Faults(prepared.home, fail_remove=failing).remove)
    assert caught.value.exit_code == _EXECUTION


def test_listing_classifies_evidence_in_the_home_only(tmp_path: Path) -> None:
    """Residue, interrupted, unreadable and lifecycle evidence; nothing else, nothing nested."""
    prepared = _prepared(tmp_path)
    home = prepared.home
    prefix = "a.version-transition."
    declare_evidence(home, prefix + "1", _manifest())
    declare_evidence(home, prefix + "2", _manifest(state=EvidenceState.WRITING), {"original.1": b"x"})
    declare_evidence(home, prefix + "3", _manifest(state=EvidenceState.RESTORATION_INCOMPLETE))
    declare_evidence(home, prefix + "4", _manifest(owner="release-7", state=EvidenceState.WRITING))
    declare_evidence(home, prefix + "5", None, {"original.1": b"x"})
    declare_evidence(home, prefix + "6", b'{"version": 1, "version": 1}')
    declare_evidence(home, prefix + "7", None)
    declare_evidence(home / "nested", prefix + "8", _manifest(state=EvidenceState.WRITING))
    (home / (prefix + "file")).write_bytes(b"not a directory")
    (home / "a.release-operation.lock").write_bytes(b"{}")
    entries = find_evidence(_declaration(prepared))
    assert [(entry.path.name, entry.kind, entry.owner) for entry in entries] == [
        (prefix + "1", EvidenceKind.RESIDUE, STANDALONE),
        (prefix + "2", EvidenceKind.INTERRUPTED, STANDALONE),
        (prefix + "3", EvidenceKind.INTERRUPTED, STANDALONE),
        (prefix + "4", EvidenceKind.LIFECYCLE, "release-7"),
        (prefix + "5", EvidenceKind.UNREADABLE, None),
        (prefix + "6", EvidenceKind.UNREADABLE, None),
        (prefix + "7", EvidenceKind.RESIDUE, None),
    ]


def test_listing_without_a_home_finds_nothing(tmp_path: Path) -> None:
    """Read commands may run before any artifact home exists."""
    project = project_identity(tmp_path)
    declaration = ArtifactDeclaration(project, authorize_write(project, ".review-artifacts.ini"),
                                      authorize_write(project, ".reviews"), declared=False)
    assert find_evidence(declaration) == ()


_VALID = json.loads(_manifest().decode("utf-8"))
_FILE = {"path": "version.txt", "sha256": None, "exists": False, "copy": None}


@pytest.mark.parametrize("content", [
    b"not json", b"[]", b'{"owner": "a", "owner": "b"}',
    json.dumps({**_VALID, "version": 2}).encode(), json.dumps({**_VALID, "extra": 1}).encode(),
    json.dumps({key: value for key, value in _VALID.items() if key != "target"}).encode(),
    json.dumps({**_VALID, "owner": ""}).encode(), json.dumps({**_VALID, "state": "done"}).encode(),
    json.dumps({**_VALID, "created": 1}).encode(), json.dumps({**_VALID, "files": {}}).encode(),
    json.dumps({**_VALID, "files": [{**_FILE, "extra": 1}]}).encode(),
    json.dumps({**_VALID, "files": [{**_FILE, "exists": 1}]}).encode(),
    json.dumps({**_VALID, "files": [{**_FILE, "sha256": 1}]}).encode(),
    json.dumps({**_VALID, "files": [{**_FILE, "copy": 1}]}).encode(),
    *(json.dumps({**_VALID, "files": [{**_FILE, "copy": copy}]}).encode()
      for copy in ("../../version.txt", "C:/project/version.txt", "manifest.json", "sub/original.1", "original.0")),
])
def test_manifest_decoding_is_strict(content: bytes) -> None:
    """Duplicate keys, unknown or missing fields, wrong types and unsafe copy names are unreadable."""
    with pytest.raises(ValueError, match="manifest"):
        EvidenceManifest.decode(content)


def test_allocation_skips_taken_names_and_never_enters_them(tmp_path: Path) -> None:
    """A complete or partial directory of the same name stays byte for byte."""
    prepared = _prepared(tmp_path)
    declare_evidence(prepared.home, EVIDENCE_NAME, _manifest(), {"original.1": b"kept"})
    declare_evidence(prepared.home, EVIDENCE_NAME + "-2", None, {"original.1": b"partial"})
    before = snapshot(prepared.home)
    third = allocate(prepared, FIXED_NOW, TRANSITION_PID)
    fourth = allocate(prepared, FIXED_NOW, TRANSITION_PID)
    assert (third.path.name, fourth.path.name) == (EVIDENCE_NAME + "-3", EVIDENCE_NAME + "-4")
    assert list(third.path.iterdir()) == []
    after = snapshot(prepared.home)
    assert {name: content for name, content in after.items() if name in before} == before


def test_allocation_failure_other_than_a_taken_name_fails_at_once(tmp_path: Path) -> None:
    """A home removed after preparation cannot hold evidence: status 1, nothing created."""
    prepared = _prepared(tmp_path)
    (prepared.home / ".gitignore").unlink()
    prepared.home.rmdir()
    with pytest.raises(EvidenceError, match="cannot create evidence directory") as caught:
        allocate(prepared, FIXED_NOW, TRANSITION_PID)
    assert caught.value.exit_code == _EXECUTION
    assert not prepared.home.exists()


def test_allocation_stops_at_its_attempt_limit(tmp_path: Path) -> None:
    """Every candidate name taken fails with status 1 and creates nothing."""
    prepared = _prepared(tmp_path)
    declare_evidence(prepared.home, EVIDENCE_NAME, None)
    declare_evidence(prepared.home, EVIDENCE_NAME + "-2", None)
    before = snapshot(prepared.home)
    with pytest.raises(EvidenceError, match=r"no free evidence directory after 2 attempts") as caught:
        allocate(prepared, FIXED_NOW, TRANSITION_PID, attempts=2)
    assert caught.value.exit_code == _EXECUTION
    assert snapshot(prepared.home) == before


# eof
