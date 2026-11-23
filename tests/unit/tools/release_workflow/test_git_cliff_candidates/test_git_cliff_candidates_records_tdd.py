"""Release listings, candidate identities and trust records are strict; the metadata worker is retried once within 60 s.

Step 6 of v0.14.0 git-cliff-provisioning (design "Candidate lifecycle and
admission order"; design decisions Q06 and Q12; requirement clarification
Q16; plan decision Q19).

- `parse_listing` reads the one Windows asset of the release named by the
  version: its exact size and its `sha256:` digest, or none; any other
  release, a missing or repeated asset, a size or digest of another form, or
  a body that is not a JSON object is refused.
- A `Candidate` names a version's asset, its size, its SHA-256, its trust
  kind, its HTTPS source and its local acquisition time; evidence-only trust
  exists only for 2.7.0.
- `TrustRecord` writes a record once by non-replacing publication and never
  rewrites it; it reads strictly (exact members, the basis of its trust kind,
  its own version) and `compare` fails a received archive of another size or
  digest, or a missing record.
- The metadata worker: a retryable failure is retried once after 5 s inside
  its 60 s; a second one, a fatal one, a timeout, a refused containment or a
  retry without time left fail the candidate.
"""

from __future__ import annotations

import dataclasses
import json
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_children_fake import (
    Child,
    ProvisionWorld,
    failed,
)
from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    BASELINE,
    PIN,
    asset_name,
    metadata,
    release_metadata,
)
from tests.unit.tools.release_workflow.git_cliff_support import synthetic_pin
from tools.release_workflow.git_cliff.archive import VerificationError
from tools.release_workflow.git_cliff.budget import resolve_budget
from tools.release_workflow.git_cliff.candidates import (
    EVIDENCE_ONLY_HTTPS,
    EVIDENCE_ONLY_VERSIONS,
    UPSTREAM_DIGEST,
    AssetListing,
    Candidate,
    CandidateError,
    TrustRecord,
    acquire_candidate,
    parse_listing,
)
from tools.release_workflow.git_cliff.manifest import download_url
from tools.release_workflow.git_cliff.network import Received

if TYPE_CHECKING:
    from pathlib import Path

_DIGEST = "a" * 64
_ACQUIRED = "2026-11-21T10:15:00+01:00"


def _candidate(version: str = BASELINE, trust: str = EVIDENCE_ONLY_HTTPS) -> Candidate:
    """A valid candidate identity."""
    return Candidate(version=version, asset=asset_name(version), size=1234, sha256=_DIGEST, trust=trust,
                     source=download_url(synthetic_pin(version)), acquired=_ACQUIRED)


def test_a_listing_names_the_windows_asset_its_size_and_its_published_digest() -> None:
    """The `sha256:` prefix is dropped; a null digest is no digest."""
    listed = parse_listing(PIN, release_metadata(PIN, size=7_428_304))
    assert listed == AssetListing(PIN, asset_name(PIN), 7_428_304, listed.published_sha256)
    assert listed.published_sha256 is not None
    assert len(listed.published_sha256) == len(_DIGEST)
    assert parse_listing(BASELINE, release_metadata(BASELINE, digest=False)).published_sha256 is None


def _replace_asset(version: str, **fields: object) -> str:
    """Release metadata whose Windows asset has some fields changed."""
    document = json.loads(release_metadata(version))
    document["assets"][1].update(fields)
    return json.dumps(document)


@pytest.mark.parametrize(("text", "reason"), [
    pytest.param("not json", "JSON", id="not-json"),
    pytest.param("[]", "object", id="not-object"),
    pytest.param(release_metadata(PIN, tag="v2.14.1"), "v2.14.1", id="other-release"),
    pytest.param(json.dumps({"tag_name": "v2.14.2", "assets": {}}), "assets", id="assets-not-list"),
    pytest.param(json.dumps({"tag_name": "v2.14.2", "assets": []}), "0 assets", id="no-asset"),
    pytest.param(json.dumps({"tag_name": "v2.14.2", "assets": [{"name": asset_name(PIN), "size": 1}] * 2}), "2 assets", id="two-assets"),
    pytest.param(_replace_asset(PIN, size=0), "size", id="zero-size"),
    pytest.param(_replace_asset(PIN, size=True), "size", id="boolean-size"),
    pytest.param(_replace_asset(PIN, size="12"), "size", id="text-size"),
    pytest.param(_replace_asset(PIN, digest="md5:" + "a" * 32), "digest", id="other-algorithm"),
    pytest.param(_replace_asset(PIN, digest="sha256:" + "A" * 64), "digest", id="uppercase"),
])
def test_any_other_listing_is_refused(text: str, reason: str) -> None:
    """Only the version's release and its one Windows asset, with a positive size and a lowercase SHA-256 or none."""
    with pytest.raises(CandidateError, match=reason):
        parse_listing(PIN, text)


@pytest.mark.parametrize(("changes", "reason"), [
    pytest.param({"asset": "git-cliff.zip"}, "asset", id="asset"),
    pytest.param({"size": 0}, "size", id="size"),
    pytest.param({"sha256": "XYZ"}, "sha256", id="digest"),
    pytest.param({"trust": "hope"}, "trust", id="trust"),
    pytest.param({"source": "http://github.com/x.zip"}, "source", id="source"),
    pytest.param({"acquired": "2026-11-21T10:15:00"}, "acquired", id="acquired"),
])
def test_a_candidate_refuses_a_malformed_identity(changes: dict[str, object], reason: str) -> None:
    """Every field has one form."""
    with pytest.raises(CandidateError, match=reason):
        dataclasses.replace(_candidate(), **changes)


def test_evidence_only_trust_exists_only_for_2_7_0() -> None:
    """The user's authorization of 2026-11-13 covers 2.7.0 alone."""
    assert frozenset({"2.7.0"}) == EVIDENCE_ONLY_VERSIONS
    assert _candidate().trust == EVIDENCE_ONLY_HTTPS
    assert _candidate(PIN, UPSTREAM_DIGEST).triple == "x86_64-pc-windows-msvc"
    assert _candidate(PIN, UPSTREAM_DIGEST).member == "git-cliff-2.14.2/git-cliff.exe"
    with pytest.raises(CandidateError, match=r"2\.7\.0"):
        _candidate(PIN, EVIDENCE_ONLY_HTTPS)


def test_a_trust_record_is_written_once_and_read_back(tmp_path: Path) -> None:
    """The record reads back to the candidate; a second write refuses and leaves its bytes."""
    record = TrustRecord(tmp_path / "bundle" / "trust.2.7.0.json", BASELINE)
    assert record.read() is None
    record.write_once(_candidate())
    content = record.path.read_bytes()
    assert record.read() == _candidate()
    assert json.loads(content)["trust"] == EVIDENCE_ONLY_HTTPS
    with pytest.raises(CandidateError, match="never rewritten"):
        record.write_once(dataclasses.replace(_candidate(), sha256="b" * 64))
    assert record.path.read_bytes() == content
    assert [path.name for path in record.path.parent.iterdir()] == ["trust.2.7.0.json"]


def test_require_gives_the_recorded_identity_and_refuses_a_missing_record(tmp_path: Path) -> None:
    """An acquired candidate has its record; a missing one is named."""
    record = TrustRecord(tmp_path / "trust.2.7.0.json", BASELINE)
    with pytest.raises(CandidateError, match="missing"):
        record.require()
    record.write_once(_candidate())
    assert record.require() == _candidate()


def test_a_trust_record_of_another_version_cannot_be_written(tmp_path: Path) -> None:
    """A record file belongs to one version."""
    with pytest.raises(CandidateError, match=r"2\.14\.2"):
        TrustRecord(tmp_path / "trust.2.7.0.json", BASELINE).write_once(_candidate(PIN, UPSTREAM_DIGEST))


def _edited(path: Path, **fields: object) -> None:
    """Change members of a written record."""
    document = json.loads(path.read_bytes())
    document.update(fields)
    path.write_text(json.dumps(document), encoding="utf-8")


@pytest.mark.parametrize(("fields", "reason"), [
    pytest.param({"extra": 1}, "members", id="extra"),
    pytest.param({"schema": 2}, "schema", id="schema"),
    pytest.param({"basis": "trust me"}, "basis", id="basis"),
    pytest.param({"version": PIN}, "2.14.2", id="other-version"),
    pytest.param({"size": "1234"}, "size", id="size"),
])
def test_a_trust_record_reads_strictly(fields: dict[str, object], reason: str, tmp_path: Path) -> None:
    """Exact members, schema 1, the basis of its trust kind, its own version."""
    record = TrustRecord(tmp_path / "trust.2.7.0.json", BASELINE)
    record.write_once(_candidate())
    _edited(record.path, **fields)
    with pytest.raises(CandidateError, match=reason) as raised:
        record.read()
    assert record.path.name in str(raised.value)


def test_compare_accepts_the_recorded_archive_and_refuses_any_other(tmp_path: Path) -> None:
    """Same size and digest pass; another digest or size, or a missing record, is a verification failure."""
    record = TrustRecord(tmp_path / "trust.2.7.0.json", BASELINE)
    with pytest.raises(VerificationError, match="missing"):
        record.compare(Received(1234, _DIGEST))
    record.write_once(_candidate())
    record.compare(Received(1234, _DIGEST))
    for received in (Received(1234, "b" * 64), Received(1233, _DIGEST)):
        with pytest.raises(VerificationError, match=r"trust record trust\.2\.7\.0\.json"):
            record.compare(received)


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProvisionWorld:
    """An evidence cache for 2.14.2."""
    built = ProvisionWorld.build(tmp_path, monkeypatch, namespace="evidence")
    built.pin = synthetic_pin(PIN)
    return built


def _acquire(world: ProvisionWorld) -> None:
    """Acquire 2.14.2 and release its invocation."""
    acquire_candidate(world.layout.tooling_root, PIN, resolve_budget({}), world.seams(),
                      trust_path=world.layout.tooling_root.parent / f"trust.{PIN}.json").close()


def test_a_retryable_metadata_failure_is_retried_once_after_5_s(world: ProvisionWorld) -> None:
    """The second attempt carries what remains of the 60 s."""
    world.children.script("metadata", failed("retryable", "URLError: reset"), metadata(PIN))
    _acquire(world)
    first, second = world.children.of("metadata")
    budget = resolve_budget({})
    assert world.clock.sleeps[0] == budget.retry_delay
    assert (first.remaining(), second.remaining()) == (budget.metadata, budget.metadata - budget.retry_delay)
    assert first.request.expires == second.request.expires == budget.metadata


@pytest.mark.parametrize(("children", "reason"), [
    pytest.param((failed("retryable", "reset"), failed("retryable", "reset again")), "after 2 attempts .reset again.", id="twice"),
    pytest.param((failed("fatal", "HTTPError: HTTP Error 403: rate limit"),), "after 1 attempt .HTTPError", id="fatal"),
    pytest.param((Child(hang=True),), "within its budget of 60 s", id="timeout"),
    pytest.param((Child(containment=True),), "contained", id="containment"),
    pytest.param((Child(status=1),), "no outcome", id="no-outcome"),
    pytest.param((Child(seconds=56, status=75, stdout=failed("retryable", "slow").stdout),), "no time remained", id="no-time"),
])
def test_a_metadata_failure_fails_the_candidate_before_any_download(children: tuple[Child, ...], reason: str, world: ProvisionWorld) -> None:
    """Each one is a candidate failure naming the release metadata; no archive is downloaded."""
    world.children.script("metadata", *children)
    with pytest.raises(CandidateError, match=reason) as raised:
        _acquire(world)
    assert "release metadata of git-cliff 2.14.2" in str(raised.value)
    assert world.children.of("worker") == []


def test_a_metadata_budget_spent_before_a_first_attempt_fails(world: ProvisionWorld) -> None:
    """A metadata budget with no time left when the first attempt would start launches nothing."""
    budget = dataclasses.replace(resolve_budget({}), metadata=0)
    with pytest.raises(CandidateError, match="spent before the first attempt"):
        acquire_candidate(world.layout.tooling_root, PIN, budget, world.seams(), trust_path=world.layout.tooling_root.parent / "trust.json")
    assert world.children.of("metadata") == []


# eof
