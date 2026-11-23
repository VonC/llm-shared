"""Acquire evidence candidates independently of the manifest, keep their trust records immutable, provision them in the evidence namespace.

Step 6 of v0.14.0 git-cliff-provisioning (design "Candidate lifecycle and
admission order" and "Candidate cache"; design decisions Q04 and Q12;
requirement clarifications Q13 and Q16; plan decisions Q10 and Q19). Only the
evidence harness calls this module. It never reads the admitted pins and
never writes the manifest: it takes only the platform triple and the asset
URL derivation from the manifest module.

- `parse_listing` reads the release metadata of one version: the name, exact
  size and `sha256:` digest (or none) of its one Windows x64 asset.
- `Candidate` is a candidate's identity (asset, size, SHA-256, trust kind,
  HTTPS source, local acquisition time) and `TrustRecord` its committed
  record beside the bundle: written once by non-replacing publication, read
  strictly, compared with every later download, never rewritten.
  `upstream-digest` trust rests on GitHub's published digest;
  `evidence-only-https` trust, for a release that publishes none, exists only
  for `EVIDENCE_ONLY_VERSIONS`, the scope of the user's authorization of
  2026-11-13, and the record states that HTTPS anchored its first download.
- `acquire_candidate` uses an existing trust record as the identity; without
  one it reads the listing through the record-free metadata worker (60 s,
  one retry after 5 s for a retryable failure), refuses evidence-only trust
  for any other version before any download, and installs through the Step 3
  to 5 primitives in the evidence namespace (`provisioning.provision_target`
  with an `InstallTarget`): the ordinary recorded worker under D with one
  retry and `expected_size` the listed size, then the parent's own digest of
  the staged archive, compared with the trust record, or with the published
  digest when there is one, then extraction and the recorded staging probe.
  Only then, under the candidate lock and before publication, is the trust
  record written; any earlier failure writes none, and a record written by
  another acquisition while this one waited is compared instead. Since code
  review round 1, the reuse check reads the trust record again before each
  check, the recheck under the lock included: a waiter whose record another
  first acquisition wrote reuses that verified entry, guarded by its own
  check, instead of downloading again and retiring an entry still in use.
- `provision_candidate` is the reuse path of a candidate with its record: the
  entry record's archive digest against the trust record, then the
  executable against the entry, then the probe; an invalid entry is replaced
  by a download compared with the record.

The listing is read before the candidate lock: it writes nothing, and the
trust record itself is only read, compared and written under the lock.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, cast

from tools.release_workflow.git_cliff.archive import VerificationError, archive_identity
from tools.release_workflow.git_cliff.cache import CacheLayout, local_time
from tools.release_workflow.git_cliff.cache_lock import publish_file
from tools.release_workflow.git_cliff.download_worker import (
    WorkerRequest,
    outcome_fields,
    worker_command,
)
from tools.release_workflow.git_cliff.installation import InstallTarget
from tools.release_workflow.git_cliff.manifest import PLATFORM_TRIPLE, asset_url
from tools.release_workflow.git_cliff.network import Received
from tools.release_workflow.git_cliff.provisioning import provision_target
from tools.release_workflow.lock_records import decode_object, positive_integer, text
from tools.release_workflow.windows_child import ChildRequest, ContainmentError

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from datetime import datetime
    from pathlib import Path

    from tools.release_workflow.git_cliff.budget import BudgetPolicy
    from tools.release_workflow.git_cliff.invocation import GitCliffInvocation
    from tools.release_workflow.git_cliff.provisioning import ProvisioningSeams

EVIDENCE_ONLY_VERSIONS = frozenset({"2.7.0"})
UPSTREAM_DIGEST = "upstream-digest"
EVIDENCE_ONLY_HTTPS = "evidence-only-https"
TRUST_BASIS: Mapping[str, str] = MappingProxyType({
    UPSTREAM_DIGEST: "The SHA-256 GitHub publishes for this asset in its release metadata authenticated the download.",
    EVIDENCE_ONLY_HTTPS: (
        "Evidence-only exception authorized by the user on 2026-11-13: certificate-verified HTTPS to the upstream GitHub"
        " release anchored the first download. This SHA-256 identifies those bytes for every repetition; it does not"
        " authenticate them, and this version is never a project pin."
    ),
})
CALLER = "harness"
SCHEMA = 1
_METADATA = "https://api.github.com/repos/orhun/git-cliff/releases/tags/v{version}"
_ATTEMPTS = 2
_LABEL = "trust"
_KEYS = frozenset({"schema", "version", "asset", "size", "sha256", "trust", "basis", "source", "acquired"})
_DIGEST = re.compile(r"[0-9a-f]{64}")
_PUBLISHED = re.compile(r"sha256:([0-9a-f]{64})")


class CandidateError(ValueError):
    """A candidate's listing, identity or trust record cannot be used: a setup failure, status 2."""

    exit_code = 2


def metadata_url(version: str) -> str:
    """Name the GitHub release metadata of a version."""
    return _METADATA.format(version=version)


def candidate_asset(version: str) -> str:
    """Name the Windows x64 asset of a version."""
    return f"git-cliff-{version}-{PLATFORM_TRIPLE}.zip"


@dataclass(frozen=True)
class AssetListing:
    """The Windows asset of one release as its metadata lists it: name, exact size and published SHA-256, if any."""

    version: str
    asset: str
    size: int
    published_sha256: str | None


def _assets(version: str, metadata: str) -> list[dict[str, object]]:
    """Read the assets of the release named by the version."""
    where = f"the release metadata of git-cliff {version}"
    try:
        document: object = json.loads(metadata)
    except ValueError as error:
        msg = f"{where} is not JSON: {error}"
        raise CandidateError(msg) from error
    if not isinstance(document, dict):
        msg = f"{where} is not a JSON object"
        raise CandidateError(msg)
    fields = cast("dict[str, object]", document)
    if fields.get("tag_name") != f"v{version}":
        msg = f"{where} describes the release {fields.get('tag_name')!r}, not v{version}"
        raise CandidateError(msg)
    assets = fields.get("assets")
    if not isinstance(assets, list):
        msg = f"{where} lists no assets"
        raise CandidateError(msg)
    return [cast("dict[str, object]", item) for item in cast("list[object]", assets) if isinstance(item, dict)]


def parse_listing(version: str, metadata: str) -> AssetListing:
    """Read the one Windows x64 asset of a release: its exact size and its published SHA-256, or none."""
    name = candidate_asset(version)
    matches = [asset for asset in _assets(version, metadata) if asset.get("name") == name]
    where = f"the release metadata of git-cliff {version}"
    if len(matches) != 1:
        msg = f"{where} lists {len(matches)} assets named {name}"
        raise CandidateError(msg)
    size, digest = matches[0].get("size"), matches[0].get("digest")
    if type(size) is not int or size <= 0:
        msg = f"{where}: {name} has no positive size ({size!r})"
        raise CandidateError(msg)
    published = _PUBLISHED.fullmatch(digest) if isinstance(digest, str) else None
    if digest is not None and published is None:
        msg = f"{where}: {name} has a digest of another form ({digest!r})"
        raise CandidateError(msg)
    return AssetListing(version, name, size, None if published is None else published.group(1))


@dataclass(frozen=True, kw_only=True)
class Candidate:
    """The identity of one evidence candidate, as its trust record keeps it."""

    version: str
    asset: str
    size: int
    sha256: str
    trust: str
    source: str
    acquired: str

    def __post_init__(self) -> None:
        """Refuse a malformed identity, and evidence-only trust outside the user's authorization."""
        invalid = next((name for name, valid in (
            ("asset", self.asset == candidate_asset(self.version)),
            ("size", type(self.size) is int and self.size > 0),
            ("sha256", _DIGEST.fullmatch(self.sha256) is not None),
            ("trust", self.trust in TRUST_BASIS),
            ("source", self.source.startswith("https://")),
        ) if not valid), None)
        if invalid is not None:
            msg = f"invalid candidate {invalid} for git-cliff {self.version}"
            raise CandidateError(msg)
        try:
            local_time({"acquired": self.acquired}, "acquired", label="candidate")
        except ValueError as error:
            msg = f"invalid candidate acquired time {self.acquired!r}: {error}"
            raise CandidateError(msg) from error
        if self.trust == EVIDENCE_ONLY_HTTPS and self.version not in EVIDENCE_ONLY_VERSIONS:
            msg = (f"evidence-only trust covers only {', '.join(sorted(EVIDENCE_ONLY_VERSIONS))}, authorized by the user on 2026-11-13,"
                   f" not git-cliff {self.version}")
            raise CandidateError(msg)

    @property
    def triple(self) -> str:
        """Return the platform of the asset."""
        return PLATFORM_TRIPLE

    @property
    def member(self) -> str:
        """Return the archive member holding `git-cliff.exe`."""
        return f"git-cliff-{self.version}/git-cliff.exe"


def trust_record_bytes(candidate: Candidate) -> bytes:
    """Produce the complete trust record of a candidate, with the basis of its trust kind."""
    fields = {"schema": SCHEMA, "version": candidate.version, "asset": candidate.asset, "size": candidate.size, "sha256": candidate.sha256,
              "trust": candidate.trust, "basis": TRUST_BASIS[candidate.trust], "source": candidate.source, "acquired": candidate.acquired}
    return (json.dumps(fields, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


@dataclass(frozen=True)
class TrustRecord:
    """The committed trust record of one candidate version: written once, compared with every later download."""

    path: Path
    version: str

    def _decode(self, content: bytes) -> Candidate:
        """Decode exactly the members of schema 1 for this version, with the basis of its trust kind."""
        record = decode_object(content, label=_LABEL)
        if record.keys() != _KEYS:
            msg = f"its members are not {sorted(_KEYS)}"
            raise ValueError(msg)
        if positive_integer(record, "schema", label=_LABEL) != SCHEMA:
            msg = f"its schema is not {SCHEMA}"
            raise ValueError(msg)
        version, trust = text(record, "version", label=_LABEL), text(record, "trust", label=_LABEL)
        if version != self.version:
            msg = f"it names git-cliff {version}, not {self.version}"
            raise ValueError(msg)
        if TRUST_BASIS.get(trust) != text(record, "basis", label=_LABEL):
            msg = f"its basis is not the one of {trust!r} trust"
            raise ValueError(msg)
        return Candidate(version=version, asset=text(record, "asset", label=_LABEL), size=positive_integer(record, "size", label=_LABEL),
                         sha256=text(record, "sha256", label=_LABEL), trust=trust, source=text(record, "source", label=_LABEL),
                         acquired=text(record, "acquired", label=_LABEL))

    def read(self) -> Candidate | None:
        """Return the recorded identity, or None when no record exists yet."""
        try:
            content = self.path.read_bytes()
        except FileNotFoundError:
            return None
        try:
            return self._decode(content)
        except (ValueError, TypeError) as error:
            msg = f"the trust record {self.path} is invalid: {error}"
            raise CandidateError(msg) from error

    def require(self) -> Candidate:
        """Return the recorded identity of an acquired candidate; a missing record is a candidate failure."""
        recorded = self.read()
        if recorded is None:
            msg = f"the trust record {self.path} is missing; acquire git-cliff {self.version} again"
            raise CandidateError(msg)
        return recorded

    def write_once(self, candidate: Candidate) -> None:
        """Publish the record complete and flushed, never replacing one."""
        if candidate.version != self.version:
            msg = f"the trust record {self.path.name} is for git-cliff {self.version}, not {candidate.version}"
            raise CandidateError(msg)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            publish_file(self.path, trust_record_bytes(candidate), replace=False)
        except FileExistsError as error:
            msg = f"the trust record {self.path} already exists; trust records are written once and never rewritten"
            raise CandidateError(msg) from error

    def compare(self, received: Received) -> None:
        """Require a received archive to be the recorded one: same size, same SHA-256."""
        recorded = self.read()
        if recorded is None:
            msg = f"the trust record {self.path.name} is missing; restore it from the bundle"
            raise VerificationError(msg)
        if (received.size, received.sha256) != (recorded.size, recorded.sha256):
            msg = (f"{recorded.asset}: {received.size} bytes with SHA-256 {received.sha256}; the trust record {self.path.name}"
                   f" names {recorded.size} bytes with SHA-256 {recorded.sha256}")
            raise VerificationError(msg)


class _Acceptance:
    """Accept a staged candidate archive under the candidate lock, and write its trust record once before publication."""

    def __init__(self, trust: TrustRecord, listing: AssetListing | None, kind: str, now: Callable[[], datetime]) -> None:
        """Accept against the record, or against the listing on a first acquisition."""
        self._trust = trust
        self._listing = listing
        self._kind = kind
        self._now = now
        self._pending: Candidate | None = None

    def accept(self, archive: Path) -> str:
        """Hash the staged archive and compare it; return the digest the entry records."""
        sha256, size = archive_identity(archive)
        listing = self._listing
        if listing is None or self._trust.read() is not None:
            self._trust.compare(Received(size, sha256))
            return sha256
        if size != listing.size:
            msg = f"{listing.asset}: {size} bytes, the release metadata lists {listing.size}"
            raise VerificationError(msg)
        if listing.published_sha256 is not None and sha256 != listing.published_sha256:
            msg = f"{listing.asset}: SHA-256 {sha256}, the release metadata publishes {listing.published_sha256}"
            raise VerificationError(msg)
        self._pending = Candidate(version=listing.version, asset=listing.asset, size=size, sha256=sha256, trust=self._kind,
                                  source=asset_url(listing.version, listing.asset), acquired=self._now().isoformat(timespec="seconds"))
        return sha256

    def before_publish(self) -> None:
        """Write the trust record of a first acquisition, extracted and probed, before its entry is published."""
        if self._pending is not None:
            self._trust.write_once(self._pending)

    def reusable_asset(self) -> str | None:
        """Give the archive digest a reused entry must record, read from the trust record now; None while there is none."""
        recorded = self._trust.read()
        return None if recorded is None else recorded.sha256


def _target(version: str, asset: str, size: int, acceptance: _Acceptance) -> InstallTarget:
    """Describe a candidate installation; an existing entry is reusable only when it records the trust record's digest."""
    return InstallTarget(version=version, triple=PLATFORM_TRIPLE, asset=asset, size=size, member=f"git-cliff-{version}/git-cliff.exe",
                         url=asset_url(version, asset), accept=acceptance.accept, before_publish=acceptance.before_publish,
                         reuse=acceptance.reusable_asset)


def _metadata_attempt(tooling_root: Path, version: str, deadline: float, budget: BudgetPolicy, seams: ProvisioningSeams) -> tuple[str, str]:
    """Run one record-free metadata worker and return `ok` with the metadata, or the failure class with its error."""
    request = WorkerRequest(mode="metadata", url=metadata_url(version), remaining=deadline - seams.clock())
    executable, arguments = worker_command(seams.runtime, tooling_root, request)
    where = f"the release metadata of git-cliff {version}"
    try:
        outcome = seams.launch(ChildRequest(executable, tuple(arguments), cwd=tooling_root, expires=deadline))
    except ContainmentError as error:
        msg = f"{where}: its worker could not run contained: {error}"
        raise CandidateError(msg) from error
    if outcome.timed_out:
        msg = f"{where} did not arrive within its budget of {budget.metadata} s"
        raise CandidateError(msg)
    fields = outcome_fields(outcome.stdout)
    kind, metadata = fields.get("outcome"), fields.get("metadata")
    if kind == "ok" and isinstance(metadata, str):
        return "ok", metadata
    if kind in {"retryable", "fatal"}:
        return str(kind), str(fields.get("error", ""))
    return "fatal", f"the metadata worker reported no outcome, status {outcome.status}"


def _attempts(count: int) -> str:
    """Count attempts in words."""
    return f"{count} attempt" if count == 1 else f"{count} attempts"


def _listing(tooling_root: Path, version: str, budget: BudgetPolicy, seams: ProvisioningSeams) -> AssetListing:
    """Read the listing within the metadata budget, retrying one retryable failure after the retry delay."""
    where = f"the release metadata of git-cliff {version}"
    deadline = seams.clock() + budget.metadata
    failures: list[str] = []
    while True:
        if deadline - seams.clock() <= 0:
            msg = (f"{where} failed after {_attempts(len(failures))} ({failures[-1]}); no time remained within its budget of {budget.metadata} s"
                   if failures else f"{where}: its budget of {budget.metadata} s was spent before the first attempt")
            raise CandidateError(msg)
        kind, payload = _metadata_attempt(tooling_root, version, deadline, budget, seams)
        if kind == "ok":
            return parse_listing(version, payload)
        failures.append(payload)
        if kind != "retryable" or len(failures) == _ATTEMPTS:
            msg = f"{where} failed after {_attempts(len(failures))} ({payload})"
            raise CandidateError(msg)
        if deadline - seams.clock() <= budget.retry_delay:
            msg = f"{where} failed after {_attempts(len(failures))} ({payload}); no time remained for a retry within its budget of {budget.metadata} s"
            raise CandidateError(msg)
        seams.sleep(budget.retry_delay)


def _trust_kind(listing: AssetListing) -> str:
    """Trust a published digest; without one, only an authorized evidence-only version, before any download."""
    if listing.published_sha256 is not None:
        return UPSTREAM_DIGEST
    if listing.version in EVIDENCE_ONLY_VERSIONS:
        return EVIDENCE_ONLY_HTTPS
    msg = (f"git-cliff {listing.version} publishes no SHA-256 for {listing.asset}, and evidence-only trust covers only"
           f" {', '.join(sorted(EVIDENCE_ONLY_VERSIONS))} (authorized by the user on 2026-11-13); nothing was downloaded")
    raise CandidateError(msg)


def provision_candidate(tooling_root: Path, candidate: Candidate, budget: BudgetPolicy, seams: ProvisioningSeams, *,
                        trust_path: Path) -> GitCliffInvocation:
    """Reuse or reinstall a candidate that has its trust record, in the evidence namespace.

    Args:
        tooling_root: The executing llm-shared checkout, which holds the cache.
        candidate: The identity read from the trust record.
        budget: The harness's budget policy, resolved once.
        seams: The provisioning seams.
        trust_path: The trust record every new download is compared with.

    Returns:
        The invocation object of the candidate's guarded executable.
    """
    acceptance = _Acceptance(TrustRecord(trust_path, candidate.version), None, candidate.trust, seams.now)
    target = _target(candidate.version, candidate.asset, candidate.size, acceptance)
    return provision_target(CacheLayout(tooling_root, "evidence"), target, budget, seams=seams, caller=CALLER)


def acquire_candidate(tooling_root: Path, version: str, budget: BudgetPolicy, seams: ProvisioningSeams, *,
                      trust_path: Path) -> GitCliffInvocation:
    """Give the invocation object of a candidate, acquiring its identity and trust record on first use.

    Args:
        tooling_root: The executing llm-shared checkout, which holds the cache.
        version: The candidate version, such as 2.14.2 or 2.7.0.
        budget: The harness's budget policy, resolved once; downloads use its D.
        seams: The provisioning seams; the metadata worker runs through their launcher.
        trust_path: The candidate's trust record in the bundle directory.

    Returns:
        The invocation object of the candidate's guarded executable.

    Raises:
        CandidateError: The listing, the trust kind or the trust record cannot be used.
        ProvisioningError: A provisioning stage failed; no trust record was written.
    """
    trust = TrustRecord(trust_path, version)
    recorded = trust.read()
    if recorded is not None:
        return provision_candidate(tooling_root, recorded, budget, seams, trust_path=trust_path)
    listing = _listing(tooling_root, version, budget, seams)
    acceptance = _Acceptance(trust, listing, _trust_kind(listing), seams.now)
    target = _target(version, listing.asset, listing.size, acceptance)
    return provision_target(CacheLayout(tooling_root, "evidence"), target, budget, seams=seams, caller=CALLER)


# eof
