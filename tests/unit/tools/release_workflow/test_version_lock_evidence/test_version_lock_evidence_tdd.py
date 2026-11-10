"""Recorded uv lock evidence backs every registered schema and matches the adapter.

Step 5 of v0.14.0 version-sources (plan decisions Q03, Q04 and Q06). The
committed `lock_evidence.v1.json` was produced by `lock_evidence_recorder.py`,
started by hand with uv 0.13.4; no test starts uv. In it, the "before" pair is
a `pyproject.toml` and its `uv.lock` both at `0.13.0`, the edited pair the
same files after the adapter's version-only edit to `0.14.0`, and the
manifest-only control edits the manifest alone. The tests check that every
registered `(version, revision)` pair has a record for the virtual and the
editable root; that each record names its tool, version, schema, layout, line
endings, command and outcomes, with SHA-256 of both files before and after
each run; that uv accepted the "before" and the edited pairs without changing
them and refused the control; that the adapter's edit of each recorded
"before" pair still equals the recorded edited pair byte for byte; that a
pair outside the registry fails detection; and that no host path leaked into
the data. The file is read once per session through one loader fixture.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.tools.release_workflow.version_support import (
    RootSettings,
    python_pair_edit,
    write_file,
)
from tools.release_workflow.sources import python
from tools.release_workflow.sources.model import FileView, SourceError, VersionToken

if TYPE_CHECKING:
    from collections.abc import Mapping

_EVIDENCE = Path(__file__).with_name("lock_evidence.v1.json")
_FILES = ("pyproject.toml", "uv.lock")
_COMMAND = ["<uv>", "lock", "--locked", "--offline", "--no-config", "--python", "<python>"]
_LAYOUTS = frozenset({"virtual", "editable"})
_RUNS = ["before", "edited", "manifest-only"]

type Record = dict[str, Any]


def load_evidence(path: Path = _EVIDENCE) -> dict[str, Any]:
    """Decode the committed evidence file."""
    return json.loads(path.read_bytes())


@pytest.fixture(scope="session")
def evidence() -> dict[str, Any]:
    """Read the evidence once per session; Step 6 adds its npm records to the same file."""
    return load_evidence()


def _uv(evidence: Mapping[str, Any]) -> list[Record]:
    """Return the uv records."""
    return [record for record in evidence["records"] if record["tool"] == "uv"]


def _hashes(record: Record, pair: str) -> dict[str, str]:
    """Hash both recorded files of one pair."""
    return {name: hashlib.sha256(record["files"][name][pair].encode("utf-8")).hexdigest() for name in _FILES}


def test_every_registered_pair_and_layout_has_a_record(evidence: dict[str, Any]) -> None:
    """The registry claims exactly the recorded pairs, each for both root layouts, plus a CRLF variant."""
    covered = {(record["lock_schema"]["version"], record["lock_schema"]["revision"], record["layout"]) for record in _uv(evidence)}
    assert {(version, revision) for version, revision, _layout in covered} == python.REGISTERED_LOCK_SCHEMAS
    assert {(*pair, layout) for pair in python.REGISTERED_LOCK_SCHEMAS for layout in _LAYOUTS} <= covered
    assert [record["id"] for record in _uv(evidence) if record["line_endings"] == "crlf"] == ["uv-0.13.4-v1r3-virtual-crlf"]
    assert evidence["format"] == 1


def test_records_name_their_tool_schema_layout_and_command(evidence: dict[str, Any]) -> None:
    """Each record says what ran, on which pair shape, from which provenance."""
    for record in _uv(evidence):
        assert (record["tool"], record["tool_version"], record["command"]) == ("uv", "0.13.4", _COMMAND)
        assert record["layout"] in _LAYOUTS
        assert record["provenance"]
        assert (record["before_version"], record["target_version"]) == ("0.13.0", "0.14.0")
        crlf = record["line_endings"] == "crlf"
        assert all(("\r\n" in record["files"][name][pair]) is crlf for name in _FILES for pair in ("before", "edited"))


def test_uv_accepted_both_pairs_unchanged_and_refused_the_control(evidence: dict[str, Any]) -> None:
    """Locked mode exited 0 on the "before" and edited pairs, changing neither file, and refused a missed lock field."""
    for record in _uv(evidence):
        before, edited = _hashes(record, "before"), _hashes(record, "edited")
        runs = {run["pair"]: run for run in record["runs"]}
        assert [run["pair"] for run in record["runs"]] == _RUNS
        assert [(runs[pair]["exit_code"], runs[pair]["sha256_before"], runs[pair]["sha256_after"]) for pair in _RUNS[:2]] == [
            (0, before, before), (0, edited, edited)]
        control = runs["manifest-only"]
        mixed = {"pyproject.toml": edited["pyproject.toml"], "uv.lock": before["uv.lock"]}
        assert (control["sha256_before"], control["sha256_after"]) == (mixed, mixed)
        assert control["exit_code"] != 0
        assert any("needs to be updated" in line for line in control["errors"])


def test_the_adapter_reproduces_each_recorded_edited_pair(tmp_path: Path, evidence: dict[str, Any]) -> None:
    """The current adapter edit of each recorded "before" pair equals the recorded edited pair."""
    for record in _uv(evidence):
        root = tmp_path / record["id"]
        for name in _FILES:
            write_file(root, name, record["files"][name]["before"].encode("utf-8"))
        edited = python_pair_edit(root, VersionToken.parse(record["target_version"]))
        assert edited == {name: record["files"][name]["edited"].encode("utf-8") for name in _FILES}, record["id"]


def test_a_pair_outside_the_registry_fails_detection(tmp_path: Path, evidence: dict[str, Any]) -> None:
    """A recorded lock relabelled with an unrecorded revision is refused before any write."""
    record = next(record for record in _uv(evidence) if record["id"] == "uv-0.13.4-v1r5-virtual")
    write_file(tmp_path, "pyproject.toml", record["files"]["pyproject.toml"]["before"].encode("utf-8"))
    write_file(tmp_path, "uv.lock", record["files"]["uv.lock"]["before"].replace("revision = 5", "revision = 4", 1).encode("utf-8"))
    with pytest.raises(SourceError, match=r"unsupported uv lock schema version 1, revision 4"):
        python.ADAPTER.detect(tmp_path, FileView(), RootSettings(tmp_path))


def test_the_evidence_holds_placeholders_and_no_host_path(evidence: dict[str, Any]) -> None:
    """Commands use placeholders; no drive, home directory or user path was recorded."""
    text = json.dumps(evidence)
    assert re.search(r"[A-Za-z]:[\\/]|[\\/](?:Users|home)[\\/]", text) is None
    assert "<python>" in text


# eof
