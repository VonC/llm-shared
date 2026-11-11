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

Step 6 adds the npm 10.8.3 records (Node 22.9.0), the "before" pair being a
`package.json` and its `package-lock.json` both at `0.0.24`, edited to
`0.0.25`: every supported lock format has a record, plus a CRLF variant of
format 3, each stating that the frozen install does not compare the root
version; `npm ci` accepted the "before" and edited pairs without changing
them, and the lock-only check of plan decision Q05 (`npm install
--package-lock-only`) left both pairs unchanged but rewrote the
manifest-only control's lock, whose two root version fields actually moved to
the target in the same format; the adapter still reproduces each edited
pair, and an unregistered format fails detection.
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
    pair_edit,
    write_file,
)
from tools.release_workflow.sources import npm, python
from tools.release_workflow.sources.model import FileView, SourceError, VersionToken

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from tools.release_workflow.sources.model import Adapter

_EVIDENCE = Path(__file__).with_name("lock_evidence.v1.json")
_FILES = ("pyproject.toml", "uv.lock")
_COMMAND = ["<uv>", "lock", "--locked", "--offline", "--no-config", "--python", "<python>"]
_LAYOUTS = frozenset({"virtual", "editable"})
_RUNS = ["before", "edited", "manifest-only"]
_NPM_FILES = ("package.json", "package-lock.json")
_NPM_FLAGS = ["--offline", "--ignore-scripts", "--no-audit", "--no-fund"]
_FROZEN = ["<npm>", "ci", *_NPM_FLAGS]
_LOCK_ONLY = ["<npm>", "install", "--package-lock-only", *_NPM_FLAGS]
_NPM_RUNS = [("before", "frozen"), ("before", "lock-only"), ("edited", "frozen"), ("edited", "lock-only"), ("manifest-only", "lock-only")]

type Record = dict[str, Any]


def load_evidence(path: Path = _EVIDENCE) -> dict[str, Any]:
    """Decode the committed evidence file."""
    return json.loads(path.read_bytes())


@pytest.fixture(scope="session")
def evidence() -> dict[str, Any]:
    """Read the evidence, uv and npm records together, once per session."""
    return load_evidence()


def _uv(evidence: Mapping[str, Any]) -> list[Record]:
    """Return the uv records."""
    return [record for record in evidence["records"] if record["tool"] == "uv"]


def _npm(evidence: Mapping[str, Any]) -> list[Record]:
    """Return the npm records."""
    return [record for record in evidence["records"] if record["tool"] == "npm"]


def _hashes(record: Record, pair: str, files: Sequence[str] = _FILES) -> dict[str, str]:
    """Hash both recorded files of one pair."""
    return {name: hashlib.sha256(record["files"][name][pair].encode("utf-8")).hexdigest() for name in files}


def _reproduced(root: Path, record: Record, adapter: Adapter, files: Sequence[str]) -> bool:
    """Write the recorded "before" pair and tell whether the adapter's edit gives the recorded edited pair."""
    for name in files:
        write_file(root, name, record["files"][name]["before"].encode("utf-8"))
    edited = pair_edit(adapter, root, VersionToken.parse(record["target_version"]))
    return edited == {name: record["files"][name]["edited"].encode("utf-8") for name in files}


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
        assert _reproduced(tmp_path / record["id"], record, python.ADAPTER, _FILES), record["id"]


def test_a_pair_outside_the_registry_fails_detection(tmp_path: Path, evidence: dict[str, Any]) -> None:
    """A recorded lock relabelled with an unrecorded revision is refused before any write."""
    record = next(record for record in _uv(evidence) if record["id"] == "uv-0.13.4-v1r5-virtual")
    write_file(tmp_path, "pyproject.toml", record["files"]["pyproject.toml"]["before"].encode("utf-8"))
    write_file(tmp_path, "uv.lock", record["files"]["uv.lock"]["before"].replace("revision = 5", "revision = 4", 1).encode("utf-8"))
    with pytest.raises(SourceError, match=r"unsupported uv lock schema version 1, revision 4"):
        python.ADAPTER.detect(tmp_path, FileView(), RootSettings(tmp_path))


def _check_npm_record(record: Record) -> None:
    """Check that one npm record names its tool, commands, versions, format, note and line endings."""
    assert (record["tool"], record["tool_version"], record["layout"], record["command"], record["lock_only_command"]) == (
        "npm", "10.8.3", "root", _FROZEN, _LOCK_ONLY)
    assert "Node v22.9.0" in record["tool_build"]
    assert record["provenance"]
    assert record["note"].startswith("npm ci does not compare the root version")
    assert (record["before_version"], record["target_version"]) == ("0.0.24", "0.0.25")
    assert json.loads(record["files"]["package-lock.json"]["before"])["lockfileVersion"] == record["lock_format"]
    crlf = record["line_endings"] == "crlf"
    assert all(("\r\n" in record["files"][name][pair]) is crlf for name in _NPM_FILES for pair in ("before", "edited"))


def test_every_supported_npm_format_has_a_record(evidence: dict[str, Any]) -> None:
    """The adapter supports exactly the recorded lock formats, each for a root package, plus a CRLF format 3 variant."""
    records = _npm(evidence)
    assert {record["lock_format"] for record in records} == npm.SUPPORTED_LOCK_FORMATS
    assert [record["id"] for record in records] == ["npm-10.8.3-lock2-root", "npm-10.8.3-lock3-root", "npm-10.8.3-lock3-root-crlf"]
    for record in records:
        _check_npm_record(record)


def test_npm_accepted_both_pairs_and_its_lock_only_check_caught_the_control(evidence: dict[str, Any]) -> None:
    """`npm ci` and the lock-only check left both pairs unchanged; the lock-only check rewrote the control's lock root fields."""
    for record in _npm(evidence):
        before, edited = _hashes(record, "before", _NPM_FILES), _hashes(record, "edited", _NPM_FILES)
        assert [(run["pair"], run["check"]) for run in record["runs"]] == _NPM_RUNS
        pairs = {"before": before, "edited": edited}
        for run in record["runs"][:4]:
            assert (run["exit_code"], run["errors"], run["sha256_before"], run["sha256_after"]) == (
                0, [], pairs[run["pair"]], pairs[run["pair"]]), (record["id"], run["pair"], run["check"])
        control = record["runs"][4]
        assert (control["exit_code"], control["sha256_before"]) == (0, {"package.json": edited["package.json"], "package-lock.json": before["package-lock.json"]})
        assert control["sha256_after"]["package.json"] == edited["package.json"]
        assert control["sha256_after"]["package-lock.json"] != before["package-lock.json"]
        assert control["lock_after"] == {"lockfileVersion": record["lock_format"], "version": "0.0.25", "packages_root_version": "0.0.25"}


def test_the_npm_adapter_reproduces_each_recorded_edited_pair(tmp_path: Path, evidence: dict[str, Any]) -> None:
    """The current npm adapter edit of each recorded "before" pair equals the recorded edited pair."""
    for record in _npm(evidence):
        assert _reproduced(tmp_path / record["id"], record, npm.ADAPTER, _NPM_FILES), record["id"]


def test_an_npm_format_outside_the_registry_fails_detection(tmp_path: Path, evidence: dict[str, Any]) -> None:
    """A recorded lock relabelled with an unrecorded format is refused before any write."""
    record = next(record for record in _npm(evidence) if record["id"] == "npm-10.8.3-lock3-root")
    write_file(tmp_path, "package.json", record["files"]["package.json"]["before"].encode("utf-8"))
    lock = record["files"]["package-lock.json"]["before"].replace('"lockfileVersion": 3', '"lockfileVersion": 4', 1)
    write_file(tmp_path, "package-lock.json", lock.encode("utf-8"))
    with pytest.raises(SourceError, match=r"unsupported lockfileVersion 4"):
        npm.ADAPTER.detect(tmp_path, FileView(), RootSettings(tmp_path))


def test_the_evidence_holds_placeholders_and_no_host_path(evidence: dict[str, Any]) -> None:
    """Commands use placeholders; no drive, home directory or user path was recorded."""
    text = json.dumps(evidence)
    assert re.search(r"[A-Za-z]:[\\/]|[\\/](?:Users|home)[\\/]", text) is None
    assert all(placeholder in text for placeholder in ("<python>", "<uv>", "<npm>"))


# eof
