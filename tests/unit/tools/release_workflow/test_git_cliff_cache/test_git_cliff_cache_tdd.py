"""The cache layout, its ignore rule, the strict entry record and owner file, and the lock-free reuse check.

Step 3 of v0.14.0 git-cliff-provisioning (design "Cache layout and the local
integrity record" and "Reuse check and the use guard"; design decisions Q03,
Q07 and Q12; requirement clarifications Q03, Q04 and Q05). A production entry
lives at `<root>/.tools/git-cliff/<pin>/<triple>/git-cliff.exe`, the evidence
namespace under `evidence/`, and a name that is not a version or a triple is
refused, so production never resolves into `evidence/`. Attempt names parse
back to their owner. Records are strict schema 1. Reuse opens the guard,
reads the record, hashes and probes in that order, stops at the first failure
and closes the guard; an unconfirmed probe end retains the guard instead, and
a valid reuse writes nothing.

Step 6: given an expected archive digest (an evidence candidate's trust
record), the check compares it with the record's before hashing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from tests.unit.tools.release_workflow.git_cliff_support import (
    CURRENT,
    STAND_IN_EXECUTABLE,
    FakeGuardOpener,
    FakeProbe,
    deny_writes,
    entry_record,
    install_entry,
    synthetic_pin,
)
from tools.release_workflow.git_cliff.cache import (
    Attempt,
    CacheLayout,
    EntryRecord,
    OwnerFile,
    UnusableEntry,
    ValidEntry,
    check_entry,
)
from tools.release_workflow.git_cliff.manifest import PLATFORM_TRIPLE
from tools.release_workflow.windows_child import ContainmentError, UnconfirmedEndError
from tools.release_workflow.windows_process import ProcessIdentity

PIN = synthetic_pin()
_REPOSITORY = Path(__file__).parents[5]
_RANDOM = "0a1b2c3d"


@dataclass(frozen=True)
class _Place:
    """A version and triple to place in the cache, outside any manifest."""

    version: str
    triple: str = PLATFORM_TRIPLE


def _fields() -> dict[str, object]:
    """Return the JSON fields of a valid entry record."""
    return json.loads(entry_record(PIN).encode())


def _encoded(**changes: object) -> bytes:
    """Encode a valid record's fields with some replaced, or removed when the change is None."""
    fields = {**_fields(), **changes}
    return json.dumps({key: value for key, value in fields.items() if value is not None}).encode()


def test_the_production_entry_path_is_fixed(tmp_path: Path) -> None:
    """The entry, its record, its lock and its version directory sit at fixed names."""
    layout = CacheLayout(tmp_path)
    version = tmp_path / ".tools" / "git-cliff" / "2.14.2"
    assert (layout.root, layout.version_dir(PIN), layout.entry_dir(PIN)) == (version.parent, version, version / PLATFORM_TRIPLE)
    assert layout.executable(PIN) == version / PLATFORM_TRIPLE / "git-cliff.exe"
    assert (layout.record(PIN), layout.lock_path(PIN)) == (version / PLATFORM_TRIPLE / "entry.json", version / f"{PLATFORM_TRIPLE}.lock")


@pytest.mark.parametrize("version", ["0.0.0", "2.7.0", "2.14.2", "10.20.30"])
def test_production_never_resolves_into_the_evidence_namespace(tmp_path: Path, version: str) -> None:
    """Evidence candidates live under `evidence/`, where no production version directory can be."""
    production, evidence = CacheLayout(tmp_path), CacheLayout(tmp_path, "evidence")
    assert evidence.entry_dir(_Place(version)) == production.root / "evidence" / version / PLATFORM_TRIPLE
    assert production.root / "evidence" not in production.entry_dir(_Place(version)).parents


@pytest.mark.parametrize("place", [
    _Place("evidence"), _Place(".."), _Place("2.14"), _Place("v2.14.2"), _Place("2.14.2/.."),
    _Place("2.14.2", "../x86_64"), _Place("2.14.2", ""), _Place("2.14.2", "x86_64"),
])
def test_a_name_that_is_not_a_version_or_a_triple_is_refused(tmp_path: Path, place: _Place) -> None:
    """Only `X.Y.Z` and a dashed triple become directory names."""
    with pytest.raises(ValueError, match="not a cache place"):
        CacheLayout(tmp_path).entry_dir(place)


def test_an_unknown_namespace_is_refused(tmp_path: Path) -> None:
    """Only the production and evidence namespaces exist."""
    with pytest.raises(ValueError, match="namespace"):
        CacheLayout(tmp_path, "staging")


@pytest.mark.parametrize("kind", ["staging", "retired"])
def test_attempt_names_parse_back_to_their_owner(tmp_path: Path, kind: str) -> None:
    """A staging or retired directory name carries the owner's PID, creation time and token."""
    layout = CacheLayout(tmp_path)
    directory = layout.attempt_dir(PIN, kind, CURRENT, _RANDOM)
    assert directory == layout.version_dir(PIN) / f".{kind}-{CURRENT.pid}-{CURRENT.created}-{_RANDOM}"
    assert CacheLayout.parse_attempt(directory.name) == Attempt(kind, CURRENT, _RANDOM)


@pytest.mark.parametrize("name", [
    ".staging-0-1-ab", ".staging-01-1-ab", ".staging-1-0-ab", ".staging-1-1-", ".staging-1-1-AB", ".staging-1-1-ab.exe",
    ".pending-1-1-ab", "staging-1-1-ab", ".retired-1-x-ab", ".retired--1-1-ab", PLATFORM_TRIPLE, f"{PLATFORM_TRIPLE}.lock",
])
def test_a_malformed_attempt_name_is_refused(name: str) -> None:
    """Only canonical attempt names parse; anything else is not an attempt."""
    assert CacheLayout.parse_attempt(name) is None


@pytest.mark.parametrize(("kind", "owner", "token"), [
    ("pending", CURRENT, _RANDOM), ("staging", ProcessIdentity(0, 1), _RANDOM), ("staging", ProcessIdentity(1, 0), _RANDOM),
    ("staging", CURRENT, ""), ("staging", CURRENT, "AB"), ("staging", CURRENT, "a-b"),
])
def test_an_attempt_name_needs_a_kind_an_owner_and_a_token(tmp_path: Path, kind: str, owner: ProcessIdentity, token: str) -> None:
    """A name that would not parse back is never built."""
    with pytest.raises(ValueError, match="attempt"):
        CacheLayout(tmp_path).attempt_dir(PIN, kind, owner, token)


def test_the_root_gitignore_ignores_the_cache() -> None:
    """The tracked root `.gitignore` holds the exact cache entry."""
    assert "/.tools/git-cliff/" in (_REPOSITORY / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_an_entry_record_round_trips_with_every_field() -> None:
    """Schema 1 encodes each field once and decodes back to the same record."""
    record = entry_record(PIN)
    assert EntryRecord.decode(record.encode()) == record
    assert list(json.loads(record.encode())) == [
        "schema", "version", "triple", "asset", "asset_sha256", "executable_sha256", "executable_size", "provisioned",
    ]


@pytest.mark.parametrize("content", [
    pytest.param(_encoded(note="extra"), id="extra-field"),
    pytest.param(_encoded(asset=None), id="missing-field"),
    pytest.param(entry_record(PIN).encode().replace(b'"schema": 1,', b'"schema": 1, "schema": 1,'), id="duplicate-key"),
    pytest.param(_encoded(schema=2), id="other-schema"),
    pytest.param(_encoded(executable_size=True), id="boolean-size"),
    pytest.param(_encoded(executable_size="15"), id="text-size"),
    pytest.param(_encoded(executable_sha256="abc"), id="short-digest"),
    pytest.param(_encoded(asset_sha256="F" * 64), id="upper-case-digest"),
    pytest.param(_encoded(provisioned="2026-11-18T14:02:31"), id="time-without-offset"),
    pytest.param(_encoded(provisioned="yesterday"), id="not-a-time"),
    pytest.param(_encoded(version=""), id="empty-version"),
    pytest.param(b"[]", id="not-an-object"),
    pytest.param(b"{", id="not-json"),
])
def test_an_invalid_entry_record_is_refused(content: bytes) -> None:
    """An extra, missing, duplicate or mistyped field, or a foreign schema, never decodes."""
    with pytest.raises((ValueError, TypeError)):
        EntryRecord.decode(content)


def test_an_owner_file_round_trips_and_refuses_a_malformed_child() -> None:
    """The owner and its recorded children survive encoding; a child needs exactly a PID and a creation time."""
    owner = OwnerFile(CURRENT).with_child(ProcessIdentity(7, 70)).with_child(ProcessIdentity(8, 80))
    assert OwnerFile.decode(owner.encode()) == owner
    assert owner.children == (ProcessIdentity(7, 70), ProcessIdentity(8, 80))
    malformed = owner.encode().replace(b'{"pid": 7, "created": 70}', b'{"pid": 7, "created": 70, "x": 1}')
    with pytest.raises(ValueError, match="child"):
        OwnerFile.decode(malformed)


@pytest.mark.parametrize("content", [
    pytest.param(OwnerFile(CURRENT).encode().replace(b'"schema": 1', b'"schema": 2'), id="other-schema"),
    pytest.param(OwnerFile(CURRENT).encode().replace(b'"children"', b'"note": 1, "children"'), id="extra-field"),
])
def test_an_owner_file_with_other_fields_or_schema_is_refused(content: bytes) -> None:
    """Only the four schema 1 fields make an owner file."""
    with pytest.raises(ValueError, match="owner file fields"):
        OwnerFile.decode(content)


def test_a_missing_executable_makes_the_entry_absent(tmp_path: Path) -> None:
    """Without an executable no guard is held and nothing else is read or run."""
    opener, probe = FakeGuardOpener(), FakeProbe()
    result = check_entry(CacheLayout(tmp_path), PIN, open_guard=opener, probe=probe)
    assert result == UnusableEntry(absent=True, reason="git-cliff.exe is missing")
    assert (opener.opened, probe.guards) == ([], [])


@pytest.mark.parametrize(("content", "reason"), [
    (None, "entry.json is missing"),
    (b"{", "entry.json is invalid"),
    (replace(entry_record(PIN), version="2.14.1").encode(), "entry.json names 2.14.1 for x86_64-pc-windows-msvc"),
    (replace(entry_record(PIN), triple="aarch64-pc-windows-msvc").encode(), "entry.json names 2.14.2 for aarch64-pc-windows-msvc"),
])
def test_a_missing_or_unusable_record_is_invalid_without_hashing_or_probing(tmp_path: Path, content: bytes | None, reason: str) -> None:
    """The record is read before any hash, and a wrong one stops the check with the guard closed."""
    layout = CacheLayout(tmp_path)
    install_entry(layout, PIN)
    if content is None:
        layout.record(PIN).unlink()
    else:
        layout.record(PIN).write_bytes(content)
    opener, probe = FakeGuardOpener(), FakeProbe()
    result = check_entry(layout, PIN, open_guard=opener, probe=probe)
    assert isinstance(result, UnusableEntry)
    assert (result.absent, result.reason.startswith(reason)) == (False, True)
    assert [(guard.hashed, guard.closed) for guard in opener.opened] == [(0, True)]
    assert probe.guards == []


@pytest.mark.parametrize(("executable", "reason"), [
    (STAND_IN_EXECUTABLE[:-1], f"git-cliff.exe has {len(STAND_IN_EXECUTABLE) - 1} bytes; entry.json records {len(STAND_IN_EXECUTABLE)}"),
    (STAND_IN_EXECUTABLE[:-1] + b"!", "git-cliff.exe differs from the SHA-256 in entry.json"),
])
def test_a_size_or_digest_mismatch_is_invalid_without_probing(tmp_path: Path, executable: bytes, reason: str) -> None:
    """A truncated or altered executable never runs, not even for its version probe."""
    layout = CacheLayout(tmp_path)
    install_entry(layout, PIN)
    layout.executable(PIN).write_bytes(executable)
    opener, probe = FakeGuardOpener(), FakeProbe()
    assert check_entry(layout, PIN, open_guard=opener, probe=probe) == UnusableEntry(absent=False, reason=reason)
    assert [(guard.hashed, guard.closed) for guard in opener.opened] == [(1, True)]
    assert probe.guards == []


@pytest.mark.parametrize(("probe", "reason"), [
    (FakeProbe(stdout=b"git-cliff 2.14.1\n"), "the version probe reported 'git-cliff 2.14.1' with status 0"),
    (FakeProbe(stdout=b""), "the version probe reported '' with status 0"),
    (FakeProbe(status=1), "the version probe reported 'git-cliff 2.14.2' with status 1"),
    (FakeProbe(timed_out=True), "the version probe did not end within its budget"),
])
def test_a_probe_that_does_not_report_the_pin_is_invalid(tmp_path: Path, probe: FakeProbe, reason: str) -> None:
    """The probe runs with the guard and must exit 0 with `git-cliff <pin>` as its first line."""
    layout = CacheLayout(tmp_path)
    install_entry(layout, PIN)
    opener = FakeGuardOpener()
    result = check_entry(layout, PIN, open_guard=opener, probe=probe)
    assert isinstance(result, UnusableEntry)
    assert (result.absent, result.reason.startswith(reason)) == (False, True)
    assert probe.guards == opener.opened
    assert [guard.closed for guard in opener.opened] == [True]


def test_a_valid_entry_returns_its_open_guard_and_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Under the write-denying helper the reuse check succeeds with one guard, one hash and one probe."""
    layout = CacheLayout(tmp_path)
    record = install_entry(layout, PIN)
    denial = deny_writes(monkeypatch)
    opener, probe = FakeGuardOpener(), FakeProbe(stdout=b"git-cliff 2.14.2\r\nextra line\n")
    result = check_entry(layout, PIN, open_guard=opener, probe=probe)
    assert result == ValidEntry(opener.opened[0], record)
    assert [(guard.hashed, guard.closed) for guard in opener.opened] == [(1, False)]
    assert (probe.guards, denial.attempts) == (opener.opened, [])
    with pytest.raises(PermissionError):
        layout.record(PIN).write_bytes(b"{}")
    assert denial.attempts == [("open", str(layout.record(PIN)))]


def test_an_unconfirmed_probe_end_retains_the_guard_before_it_propagates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No invocation exists yet, so the check itself retains the guard; the caller's cleanup leaves it open."""
    layout = CacheLayout(tmp_path)
    install_entry(layout, PIN)
    denial = deny_writes(monkeypatch)
    unconfirmed = UnconfirmedEndError(pid=4242, identity=None, call="TerminateJobObject", error=5)
    opener, probe = FakeGuardOpener(), FakeProbe(error=unconfirmed)
    with pytest.raises(UnconfirmedEndError) as caught:
        check_entry(layout, PIN, open_guard=opener, probe=probe)
    guard = opener.opened[0]
    guard.close()
    assert (caught.value, guard.retained, guard.closed, denial.attempts) == (unconfirmed, True, False, [])


def test_another_probe_failure_closes_the_guard_and_propagates(tmp_path: Path) -> None:
    """A containment failure means the probe child ended or never existed, so the guard is closed."""
    layout = CacheLayout(tmp_path)
    install_entry(layout, PIN)
    opener = FakeGuardOpener()
    failure = ContainmentError("refused", call="CreateProcessW", error=1816)
    with pytest.raises(ContainmentError) as caught:
        check_entry(layout, PIN, open_guard=opener, probe=FakeProbe(error=failure))
    assert (caught.value, [(guard.closed, guard.retained) for guard in opener.opened]) == (failure, [(True, False)])


def test_an_expected_archive_digest_is_compared_after_the_record_and_before_the_hash(tmp_path: Path) -> None:
    """Step 6: an evidence candidate's entry must record its trust record's archive digest; another one is invalid unhashed."""
    layout = CacheLayout(tmp_path, "evidence")
    record = install_entry(layout, PIN)
    opener, probe = FakeGuardOpener(), FakeProbe()
    assert check_entry(layout, PIN, open_guard=opener, probe=probe, asset_sha256=record.asset_sha256) == ValidEntry(opener.opened[0], record)
    opener.opened[0].close()
    expected = "0" * 64
    result = check_entry(layout, PIN, open_guard=opener, probe=probe, asset_sha256=expected)
    assert result == UnusableEntry(absent=False, reason=f"entry.json records the archive SHA-256 {record.asset_sha256}, expected {expected}")
    assert [(guard.hashed, guard.closed) for guard in opener.opened] == [(1, True), (0, True)]
    assert probe.guards == opener.opened[:1]


# eof
