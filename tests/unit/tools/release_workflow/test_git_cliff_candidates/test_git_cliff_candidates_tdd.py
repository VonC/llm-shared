"""Evidence candidates are acquired independently of the manifest and provisioned in the evidence namespace only.

Step 6 of v0.14.0 git-cliff-provisioning (design "Candidate lifecycle and
admission order" and "Candidate cache"; design decisions Q04 and Q12;
requirement clarifications Q13 and Q16; plan decisions Q10 and Q19). No
process: the children fake plays the metadata worker, the download worker,
the probes and simulated parent death.

- 2.14.2 takes its identity from canned release metadata (asset, size and
  `sha256:` digest) read by a record-free metadata worker within 60 s; 2.7.0
  has no published digest, so its recorded download is bounded by the listed
  size and the parent computes the digest. The trust record is written once,
  after extraction and the probe, before publication.
- A metadata failure, a size overflow, a short body, two retryable download
  failures, an extraction or probe failure, an unconfirmed child end and a
  parent death each leave no trust record and staging recoverable by the
  ordinary rules.
- Evidence-only trust for a version other than 2.7.0 is refused before any
  download; a later different archive fails and leaves the record byte for
  byte.
- The candidate reuse check compares the entry record's archive digest with
  the trust record, then the executable with the entry, then the probe.
- Code review round 2: a second bundle's acquisition, run as the first
  caller releases its lock, cannot replace the entry the first caller
  already guards.
- Code review round 1: a waiter of a concurrent first acquisition reads the
  trust record again under the lock and reuses the entry the other caller
  published and still uses: one download, no retirement, one record.
- Candidate layouts never reach a production path, and candidate downloads
  use the caller's resolved D.
"""

from __future__ import annotations

import dataclasses
import hashlib
import io
import json
import shutil
import zipfile
from contextlib import contextmanager
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_children_fake import (
    SECOND,
    Child,
    ProvisionWorld,
    failed,
    outcome_line,
)
from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    BASELINE,
    PIN,
    metadata,
)
from tests.unit.tools.release_workflow.git_cliff_support import (
    STAND_IN_EXECUTABLE,
    synthetic_archive,
    synthetic_pin,
)
from tools.release_workflow.git_cliff.budget import (
    DOWNLOAD_BUDGET_VARIABLE,
    resolve_budget,
)
from tools.release_workflow.git_cliff.cache import CacheLayout
from tools.release_workflow.git_cliff.candidates import (
    EVIDENCE_ONLY_HTTPS,
    UPSTREAM_DIGEST,
    Candidate,
    CandidateError,
    TrustRecord,
    acquire_candidate,
    metadata_url,
)
from tools.release_workflow.git_cliff.manifest import download_url
from tools.release_workflow.git_cliff.messages import ProvisioningError, Stage
from tools.release_workflow.windows_process import ProcessState

if TYPE_CHECKING:
    from collections.abc import Generator
    from contextlib import AbstractContextManager
    from pathlib import Path

    from tools.release_workflow.git_cliff.budget import BudgetPolicy
    from tools.release_workflow.git_cliff.invocation import GitCliffInvocation


_ATTEMPTS = 2


@pytest.fixture
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProvisionWorld:
    """Give each case its own evidence cache, clock, process states, guards and children."""
    return ProvisionWorld.build(tmp_path, monkeypatch, namespace="evidence")


def _trust(world: ProvisionWorld, version: str) -> Path:
    """Place the trust record of a version in the bundle directory beside the tooling root."""
    return world.layout.tooling_root.parent / "bundle" / f"trust.{version}.json"


def _acquire(world: ProvisionWorld, version: str, budget: BudgetPolicy | None = None) -> GitCliffInvocation:
    """Acquire a candidate as the current caller."""
    world.pin = synthetic_pin(version)
    policy = resolve_budget({}) if budget is None else budget
    return acquire_candidate(world.layout.tooling_root, version, policy, world.seams(), trust_path=_trust(world, version))


def _argument(world: ProvisionWorld, role: str, option: str) -> str:
    """Read one option of the first launch of a role."""
    arguments = world.children.of(role)[0].request.arguments
    return arguments[arguments.index(option) + 1]


def test_2_14_2_takes_its_identity_from_the_release_metadata_and_records_upstream_trust(world: ProvisionWorld) -> None:
    """The listed digest is verified, then recorded once with its source and acquisition time."""
    world.children.script("metadata", metadata(PIN))
    invocation = _acquire(world, PIN)
    archive = synthetic_archive(PIN)
    recorded = TrustRecord(_trust(world, PIN), PIN).read()
    assert recorded is not None
    assert (recorded.asset, recorded.size, recorded.sha256, recorded.trust) == (
        synthetic_pin(PIN).asset, len(archive), hashlib.sha256(archive).hexdigest(), UPSTREAM_DIGEST)
    assert (recorded.source, recorded.acquired) == (download_url(synthetic_pin(PIN)), world.clock.now().isoformat(timespec="seconds"))
    assert invocation.executable == world.executable
    invocation.close()


def test_the_metadata_worker_is_record_free_bounded_by_60_s_and_asks_the_release_of_the_version(world: ProvisionWorld) -> None:
    """One metadata request in the tooling root, never recorded, expiring 60 s after it started."""
    world.children.script("metadata", metadata(PIN))
    _acquire(world, PIN).close()
    (lookup,) = world.children.of("metadata")
    assert (lookup.request.record, lookup.request.expires, lookup.request.cwd) == (None, 60, world.layout.tooling_root)
    assert _argument(world, "metadata", "--url") == metadata_url(PIN) == "https://api.github.com/repos/orhun/git-cliff/releases/tags/v2.14.2"


def test_2_7_0_records_the_digest_its_parent_computed_from_a_download_bounded_by_the_listed_size(world: ProvisionWorld) -> None:
    """No published digest: the worker's expected size is the listed one, and the record holds the computed digest."""
    archive = synthetic_archive(BASELINE)
    world.children.script("metadata", metadata(BASELINE, digest=False))
    _acquire(world, BASELINE).close()
    assert _argument(world, "worker", "--expected-size") == str(len(archive))
    recorded = TrustRecord(_trust(world, BASELINE), BASELINE).read()
    assert recorded is not None
    assert (recorded.sha256, recorded.trust) == (hashlib.sha256(archive).hexdigest(), EVIDENCE_ONLY_HTTPS)
    assert "2026-11-13" in json.loads(_trust(world, BASELINE).read_bytes())["basis"]


def test_the_trust_record_is_written_after_extraction_and_the_probe_and_before_publication(world: ProvisionWorld) -> None:
    """Absent when the staging probe starts, present when staging is renamed into the entry."""
    trust = _trust(world, BASELINE)
    seen: list[tuple[str, bool]] = []
    world.children.script("metadata", metadata(BASELINE, digest=False))
    world.children.script("probe", Child(before_record=lambda: seen.append(("probe", trust.exists()))))
    world.refusals.append(lambda _source, target: bool(target == world.entry and seen.append(("publish", trust.exists()))))
    _acquire(world, BASELINE).close()
    assert seen == [("probe", False), ("publish", True)]


_NOT_A_ZIP = b"x" * len(synthetic_archive(BASELINE))


@pytest.mark.parametrize(("version", "listed", "role", "child", "stage"), [
    pytest.param(PIN, True, "worker", failed("fatal", "SizeOverflowError: more than the expected bytes"), Stage.DOWNLOAD, id="size-overflow"),
    pytest.param(PIN, True, "worker", Child(write=synthetic_archive(PIN)[:-1]), Stage.VERIFICATION, id="short-body"),
    pytest.param(PIN, True, "worker", Child(write=synthetic_archive(PIN)[:-1] + b"!"), Stage.VERIFICATION, id="published-digest"),
    pytest.param(BASELINE, False, "worker", Child(write=_NOT_A_ZIP), Stage.EXTRACTION, id="extraction"),
    pytest.param(BASELINE, False, "probe", Child(stdout=b"git-cliff 2.6.0\n"), Stage.PROBE, id="probe"),
    pytest.param(BASELINE, False, "probe", Child(unconfirmed="after-run"), Stage.CONTAINMENT, id="unconfirmed"),
])
def test_a_failure_before_publication_leaves_no_trust_record(  # noqa: PLR0913 - one parametrized scenario per failure
        version: str, listed: bool, role: str, child: Child, stage: Stage, world: ProvisionWorld) -> None:  # noqa: FBT001 - a pytest parameter
    """Each failing stage leaves no record; staging is removed, or kept with its lock record after an unconfirmed end."""
    world.children.script("metadata", metadata(version, digest=listed))
    world.children.script(role, child)
    with pytest.raises(ProvisioningError) as raised:
        _acquire(world, version)
    assert raised.value.stage is stage
    assert not _trust(world, version).exists()
    assert bool(world.attempts()) is (stage is Stage.CONTAINMENT)
    assert (world.lock_record() is not None) is (stage is Stage.CONTAINMENT)


def test_two_retryable_download_failures_and_a_metadata_failure_leave_no_trust_record(world: ProvisionWorld) -> None:
    """Both fail their stage without any record."""
    world.children.script("metadata", metadata(PIN))
    world.children.script("worker", failed("retryable", "ConnectionResetError"), failed("retryable", "ConnectionResetError"))
    with pytest.raises(ProvisioningError, match="after 2 attempts"):
        _acquire(world, PIN)
    world.children.script("metadata", failed("fatal", "HTTPError: HTTP Error 404: Not Found"))
    with pytest.raises(CandidateError, match="404"):
        _acquire(world, PIN)
    assert not _trust(world, PIN).exists()
    assert len(world.children.of("worker")) == _ATTEMPTS


def test_an_unconfirmed_end_is_recovered_by_the_next_caller_once_every_actor_is_dead(world: ProvisionWorld) -> None:
    """The kept staging and lock record go once the owner and the child are DEAD; the record is written then."""
    world.children.script("metadata", metadata(BASELINE, digest=False))
    world.children.script("probe", Child(unconfirmed="after-run"))
    with pytest.raises(ProvisioningError):
        _acquire(world, BASELINE)
    world.kill(world.current)
    world.current = SECOND
    world.states.states[SECOND] = ProcessState.ALIVE
    world.children.script("metadata", metadata(BASELINE, digest=False))
    _acquire(world, BASELINE).close()
    assert _trust(world, BASELINE).exists()
    assert world.attempts() == []


def test_a_parent_death_during_the_download_leaves_no_trust_record_and_a_recoverable_staging(world: ProvisionWorld) -> None:
    """The dead caller's staging is recovered by the next one, which writes the record."""
    world.children.script("metadata", metadata(PIN))
    world.children.script("worker", Child(death="running"))
    with world.dies():
        _acquire(world, PIN)
    assert not _trust(world, PIN).exists()
    assert len(world.attempts()) == 1
    world.children.script("metadata", metadata(PIN))
    _acquire(world, PIN).close()
    assert _trust(world, PIN).exists()
    assert world.attempts() == []


def test_evidence_only_trust_for_another_version_is_refused_before_any_download(world: ProvisionWorld) -> None:
    """A version without a published digest outside the authorization never downloads."""
    world.children.script("metadata", metadata("2.13.0", digest=False))
    with pytest.raises(CandidateError, match=r"2\.7\.0"):
        _acquire(world, "2.13.0")
    assert world.children.of("worker") == []
    assert not _trust(world, "2.13.0").exists()


def test_a_later_different_archive_fails_and_leaves_the_trust_record_byte_for_byte(world: ProvisionWorld) -> None:
    """With a record, the identity comes from it; a changed archive is a verification failure."""
    world.children.script("metadata", metadata(BASELINE, digest=False))
    _acquire(world, BASELINE).close()
    before = _trust(world, BASELINE).read_bytes()
    shutil.rmtree(world.entry)
    world.children.script("worker", Child(write=synthetic_archive(BASELINE)[:-1] + b"!"))
    with pytest.raises(ProvisioningError) as raised:
        _acquire(world, BASELINE)
    assert raised.value.stage is Stage.VERIFICATION
    assert "trust record" in str(raised.value)
    assert _trust(world, BASELINE).read_bytes() == before
    assert len(world.children.of("metadata")) == 1


def test_a_record_written_while_a_first_acquisition_waited_is_compared_and_kept(world: ProvisionWorld) -> None:
    """Another acquisition wrote the record during this one's download: the archive is compared with it, never rewritten."""
    world.children.script("metadata", metadata(BASELINE, digest=False))
    _acquire(world, BASELINE).close()
    record = _trust(world, BASELINE).read_bytes()
    _trust(world, BASELINE).unlink()
    shutil.rmtree(world.entry)
    world.children.script("metadata", metadata(BASELINE, digest=False))
    world.children.script("worker", Child(before_record=lambda: _trust(world, BASELINE).write_bytes(record)))
    _acquire(world, BASELINE).close()
    assert _trust(world, BASELINE).read_bytes() == record
    world.children.script("metadata", metadata(BASELINE, digest=False))
    world.children.script("worker", Child(write=synthetic_archive(BASELINE)[:-1] + b"!",
                                          before_record=lambda: _trust(world, BASELINE).write_bytes(record)))
    _trust(world, BASELINE).unlink()
    shutil.rmtree(world.entry)
    with pytest.raises(ProvisioningError, match="trust record"):
        _acquire(world, BASELINE)
    assert _trust(world, BASELINE).read_bytes() == record


def test_a_waiter_reuses_the_entry_a_concurrent_first_acquisition_published_and_still_uses(world: ProvisionWorld) -> None:
    """Code review round 1: two first acquisitions; the second, past its listing, finds the first one's record under the lock.

    The first caller acquires while the second enters the lock's transition, and keeps its invocation open. The second
    reads the trust record again under the lock, checks the published entry with its own guard and reuses it: one
    download, no retirement of the entry in use, the record written once.
    """
    world.pin = synthetic_pin(BASELINE)
    root, trust, budget, seams = world.layout.tooling_root, _trust(world, BASELINE), resolve_budget({}), world.seams()
    world.children.script("metadata", metadata(BASELINE, digest=False), metadata(BASELINE, digest=False))
    first: list[GitCliffInvocation] = []
    written: list[bytes] = []

    def mutex(name: str) -> AbstractContextManager[None]:
        if not first:
            first.append(acquire_candidate(root, BASELINE, budget, seams, trust_path=trust))
            written.append(trust.read_bytes())
        return seams.mutex(name)

    second = acquire_candidate(root, BASELINE, budget, dataclasses.replace(seams, mutex=mutex), trust_path=trust)
    assert len(world.children.of("worker")) == 1
    assert world.attempts("retired") == []
    assert (first[0].executable, second.executable) == (world.executable, world.executable)
    assert [guard.closed for guard in world.opener.opened].count(False) == len(first) + 1
    assert trust.read_bytes() == written[0]
    first[0].close()
    second.close()


def _archive_holding(version: str, executable: bytes) -> bytes:
    """A candidate archive whose member holds other executable bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(f"git-cliff-{version}/git-cliff.exe", executable)
    return buffer.getvalue()


def test_a_fresh_entry_is_guarded_before_another_bundle_can_replace_it(world: ProvisionWorld) -> None:
    """Code review round 2: two bundles share the evidence cache with different trust records for 2.7.0.

    The second bundle's acquisition runs the moment the first caller's lock record is removed. The first caller already
    holds the guard of the entry it published, so the second one cannot retire it: in-use stage, and the first
    invocation keeps the bytes it verified.
    """
    world.pin = synthetic_pin(BASELINE)
    root, budget, seams = world.layout.tooling_root, resolve_budget({}), world.seams()
    other = _archive_holding(BASELINE, b"MZ another build")
    other_trust = root.parent / "other-bundle" / f"trust.{BASELINE}.json"
    TrustRecord(other_trust, BASELINE).write_once(Candidate(
        version=BASELINE, asset=synthetic_pin(BASELINE).asset, size=len(other), sha256=hashlib.sha256(other).hexdigest(),
        trust=EVIDENCE_ONLY_HTTPS, source=download_url(synthetic_pin(BASELINE)), acquired="2026-11-21T10:00:00+01:00"))
    world.children.script("metadata", metadata(BASELINE, digest=False))
    world.children.script("worker", Child(), Child(write=other))
    second: list[ProvisioningError] = []
    ran: list[bool] = []

    @contextmanager
    def mutex(name: str) -> Generator[None]:
        with seams.mutex(name):
            yield
        if not ran and not world.layout.lock_path(world.pin).exists() and world.executable.exists():
            ran.append(True)
            try:
                acquire_candidate(root, BASELINE, budget, seams, trust_path=other_trust).close()
            except ProvisioningError as error:
                second.append(error)

    first = acquire_candidate(root, BASELINE, budget, dataclasses.replace(seams, mutex=mutex), trust_path=_trust(world, BASELINE))
    assert [error.stage for error in second] == [Stage.IN_USE]
    assert world.executable.read_bytes() == STAND_IN_EXECUTABLE
    assert len(world.children.of("worker")) == len(["first bundle", "second bundle"])
    first.close()


def test_a_valid_cached_candidate_is_reused_without_metadata_or_download(world: ProvisionWorld) -> None:
    """With its trust record and a matching entry, a candidate runs one reuse probe and nothing else."""
    world.children.script("metadata", metadata(PIN))
    _acquire(world, PIN).close()
    launched = len(world.children.launched)
    _acquire(world, PIN).close()
    assert [launch.role for launch in world.children.launched[launched:]] == ["probe"]


def test_an_entry_recording_another_archive_digest_is_replaced_before_its_executable_is_hashed(world: ProvisionWorld) -> None:
    """The archive digest of `entry.json` is compared with the trust record first: no hash, no reuse probe."""
    world.children.script("metadata", metadata(PIN))
    _acquire(world, PIN).close()
    record = json.loads(world.layout.record(world.pin).read_bytes())
    record["asset_sha256"] = "0" * 64
    world.layout.record(world.pin).write_bytes((json.dumps(record) + "\n").encode())
    opened, launched = len(world.opener.opened), len(world.children.launched)
    _acquire(world, PIN).close()
    assert world.opener.opened[opened].hashed == 0
    assert [launch.role for launch in world.children.launched[launched:]] == ["worker", "probe"]


def test_an_executable_differing_from_its_entry_is_replaced_without_a_reuse_probe(world: ProvisionWorld) -> None:
    """Then the executable is compared with the entry, before any probe."""
    world.children.script("metadata", metadata(PIN))
    _acquire(world, PIN).close()
    world.executable.write_bytes(b"MZ changed")
    opened, launched = len(world.opener.opened), len(world.children.launched)
    _acquire(world, PIN).close()
    assert world.opener.opened[opened].hashed == 1
    assert [launch.role for launch in world.children.launched[launched:]] == ["worker", "probe"]


def test_candidate_layouts_never_reach_a_production_path(world: ProvisionWorld) -> None:
    """Entry, lock and staging of a candidate live below `evidence/`; the production version directory never appears."""
    root = world.layout.tooling_root
    world.children.script("metadata", metadata(PIN))
    _acquire(world, PIN).close()
    evidence = CacheLayout(root, "evidence")
    assert world.executable == evidence.executable(world.pin)
    assert world.executable.relative_to(root).as_posix().startswith(".tools/git-cliff/evidence/2.14.2/")
    staging = world.children.of("worker")[0].request.cwd
    assert staging is not None
    assert staging.parent == evidence.version_dir(world.pin)
    assert world.layout.lock_path(world.pin).parent == evidence.version_dir(world.pin)
    assert not CacheLayout(root).version_dir(world.pin).exists()


def test_candidate_downloads_use_the_resolved_download_budget(world: ProvisionWorld) -> None:
    """A raised D bounds the archive worker, while the metadata worker keeps its 60 s."""
    world.children.script("metadata", metadata(PIN))
    _acquire(world, PIN, resolve_budget({DOWNLOAD_BUDGET_VARIABLE: "900"})).close()
    (worker,) = world.children.of("worker")
    assert (worker.request.expires, worker.remaining()) == (900, 900)
    assert world.children.of("metadata")[0].request.expires == resolve_budget({}).metadata


def test_the_parent_records_the_digest_it_computed_not_the_one_the_worker_reported(world: ProvisionWorld) -> None:
    """A worker report naming another size and digest changes nothing: the staged bytes decide."""
    world.children.script("metadata", metadata(BASELINE, digest=False))
    world.children.script("worker", Child(write=synthetic_archive(BASELINE), stdout=outcome_line("ok", size=1, sha256="0" * 64)))
    _acquire(world, BASELINE).close()
    recorded = TrustRecord(_trust(world, BASELINE), BASELINE).read()
    assert recorded is not None
    assert recorded.sha256 == hashlib.sha256(synthetic_archive(BASELINE)).hexdigest()


# eof
