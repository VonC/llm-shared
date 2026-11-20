"""Read and write the compact evidence bundle and bind the user's review to its exact content.

Step 6 of v0.14.0 git-cliff-provisioning (design "Outputs and
classification"; design decision Q13; plan decisions Q08 and Q16). A bundle
directory such as `git_cliff/bundles/2.14.2/` holds `bundle.json`,
`cliff.toml` (the exact bytes both versions read) and the two trust records
`trust.<version>.json`.

- `Bundle`: frozen inputs, each case's digests, statuses and hunks, the
  classification, the exit-path audit, the observed statuses, the `files`
  member (SHA-256 of `cliff.toml` and both trust records) and the `review`.
- `read` decodes schema 1 strictly, checks every listed file against its
  digest and reconciles each trust record with the candidate identity the
  inputs name (code review round 1); `write` publishes the whole readable
  UTF-8 file at once.
- `canonical_projection`, the covered content, is the bundle without
  `review` as canonical JSON (sorted keys, `(",", ":")` separators, ASCII
  escapes, UTF-8), and `covered_sha256` its digest; `with_review` records the
  decision, reviewer `user`, the ISO local date and that digest; `refreshed`
  keeps the hand-written entries and review over a rerun, whose changed
  content leaves the review stale.

Since code review round 2, the admission rules (`require_complete`,
`require_admissible`) live in `bundle_checks`, beside this storage model, and
the inputs record llm-shared's tags with their commits. Nothing here writes
the manifest.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, NoReturn, cast

from tools.release_workflow.git_cliff.candidates import CandidateError, TrustRecord
from tools.release_workflow.git_cliff.comparison import (
    REPOSITORIES,
    CandidateIdentity,
    CaseResult,
    CliffToml,
    ComparisonResult,
    FrozenInputs,
    RangeCase,
    RunDigest,
)
from tools.release_workflow.git_cliff.fixture_history import FixtureHashes
from tools.release_workflow.lock_records import decode_object

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

SCHEMA = 1
BUNDLE_FILE = "bundle.json"
CLIFF_TOML = "cliff.toml"
REVIEWER = "user"
DECISIONS = ("approved", "rejected")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_OBJECT = re.compile(r"[0-9a-f]{40}")
_MEMBERS = frozenset({"schema", "inputs", "outputs", "classification", "audit", "observed_statuses", "files"})
_INPUTS = frozenset({"pin", "baseline", "llm_shared_commit", "llm_shared_tags", "cliff_toml", "flags", "environment", "fixture", "ranges",
                     "candidates"})
_CANDIDATE = frozenset({"version", "asset", "size", "sha256", "trust", "executable_sha256"})
_CASE = frozenset({"repository", "range", "results", "hunks"})
_AUDIT = frozenset({"revision", "excludes_69", "commands", "categories"})
_REVIEW = frozenset({"decision", "reviewer", "date", "covered_sha256"})


class BundleError(ValueError):
    """The bundle is malformed, its files changed, or it cannot admit its pin."""

    exit_code = 2


@dataclass(frozen=True)
class Classification:
    """One hunk's classification: `intentional` with its upstream release-note reason, or `defect`."""

    hunk: str
    kind: str
    reason: str


@dataclass(frozen=True)
class AuditCategory:
    """One exit-path category of the audit: the files and call sites read, and what they show."""

    name: str
    references: tuple[str, ...]
    finding: str


@dataclass(frozen=True, kw_only=True)
class Audit:
    """The exit-path audit of the pin: the revision read, whether it excludes 69, the commands and the categories."""

    revision: str
    excludes_69: bool
    commands: tuple[str, ...] = ()
    categories: tuple[AuditCategory, ...] = ()


@dataclass(frozen=True)
class ObservedStatus:
    """A status observed by running the pin, corroborating the audit."""

    name: str
    command: str
    status: int


@dataclass(frozen=True)
class Review:
    """The user's decision over one projection of the bundle."""

    decision: str
    reviewer: str
    date: str
    covered_sha256: str


@dataclass(frozen=True, kw_only=True)
class Bundle:
    """The compact evidence of one pin against its baseline."""

    inputs: FrozenInputs
    outputs: ComparisonResult
    files: tuple[tuple[str, str], ...]
    classification: tuple[Classification, ...] = ()
    audit: Audit | None = None
    observed_statuses: tuple[ObservedStatus, ...] = ()
    review: Review | None = None

    @property
    def pin(self) -> str:
        """Return the version the bundle can admit."""
        return self.inputs.pin

    @property
    def baseline(self) -> str:
        """Return the version it is compared with."""
        return self.inputs.baseline


def trust_name(version: str) -> str:
    """Name a candidate's trust record in its bundle directory."""
    return f"trust.{version}.json"


def listed_files(pin: str, baseline: str) -> tuple[str, ...]:
    """Name the files the `files` member lists: the `cliff.toml` copy and both trust records."""
    return CLIFF_TOML, trust_name(pin), trust_name(baseline)


def file_digests(directory: Path, pin: str, baseline: str) -> tuple[tuple[str, str], ...]:
    """Hash the listed files of a bundle directory, sorted by name."""
    return tuple(sorted((name, hashlib.sha256((directory / name).read_bytes()).hexdigest()) for name in listed_files(pin, baseline)))


def _fail(message: str) -> NoReturn:
    """Refuse the document, naming the file."""
    msg = f"{BUNDLE_FILE}: {message}"
    raise BundleError(msg)


def _object(value: object, where: str, keys: frozenset[str], optional: frozenset[str] = frozenset()) -> dict[str, object]:
    """Require an object holding all the keys and nothing but them and the optional ones."""
    if not isinstance(value, dict):
        _fail(f"{where} is not an object")
    fields = cast("dict[str, object]", value)
    if not keys <= fields.keys() <= keys | optional:
        _fail(f"{where} must hold exactly {sorted(keys)}")
    return fields


def _items(value: object, where: str) -> list[object]:
    """Require a list."""
    if not isinstance(value, list):
        _fail(f"{where} is not a list")
    return cast("list[object]", value)


def _text(value: object, where: str) -> str:
    """Require a string."""
    if not isinstance(value, str):
        _fail(f"{where} is not text")
    return value


def _texts(value: object, where: str) -> tuple[str, ...]:
    """Require a list of strings."""
    return tuple(_text(item, where) for item in _items(value, where))


def _number(value: object, where: str) -> int:
    """Require an integer of zero or more, never a boolean."""
    if type(value) is not int or value < 0:
        _fail(f"{where} is not a whole number")
    return value


def _hex(value: object, where: str, form: re.Pattern[str]) -> str:
    """Require a lowercase hexadecimal object name or digest."""
    text = _text(value, where)
    if form.fullmatch(text) is None:
        _fail(f"{where} is not a lowercase hexadecimal hash")
    return text


def _cliff(value: object) -> CliffToml:
    """Decode the `cliff.toml` input."""
    fields = _object(value, "inputs.cliff_toml", frozenset({"source", "sha256", "dev_workflow_commit"}))
    return CliffToml(source=_text(fields["source"], "inputs.cliff_toml.source"), sha256=_hex(fields["sha256"], "inputs.cliff_toml.sha256", _SHA256),
                     dev_workflow_commit=_hex(fields["dev_workflow_commit"], "inputs.cliff_toml.dev_workflow_commit", _OBJECT))


def _fixture(value: object) -> FixtureHashes:
    """Decode the fixture hashes: the head commit and each tag object in stream order."""
    fields = _object(value, "inputs.fixture", frozenset({"head", "tags"}))
    tags = [_object(item, "inputs.fixture.tags", frozenset({"name", "object"})) for item in _items(fields["tags"], "inputs.fixture.tags")]
    return FixtureHashes(_hex(fields["head"], "inputs.fixture.head", _OBJECT),
                         tuple((_text(tag["name"], "a fixture tag name"), _hex(tag["object"], "a fixture tag object", _OBJECT)) for tag in tags))


def _range(value: object) -> RangeCase:
    """Decode one range of a known repository."""
    fields = _object(value, "a range", frozenset({"repository", "range"}))
    repository = _text(fields["repository"], "a range repository")
    if repository not in REPOSITORIES:
        _fail(f"unknown repository {repository!r}")
    return RangeCase(repository, None if fields["range"] is None else _text(fields["range"], "a range"))


def _candidate(value: object) -> CandidateIdentity:
    """Decode one candidate identity."""
    fields = _object(value, "a candidate", _CANDIDATE)
    return CandidateIdentity(
        version=_text(fields["version"], "a candidate version"), asset=_text(fields["asset"], "a candidate asset"),
        size=_number(fields["size"], "a candidate size"), sha256=_hex(fields["sha256"], "a candidate sha256", _SHA256),
        trust=_text(fields["trust"], "a candidate trust"), executable_sha256=_hex(fields["executable_sha256"], "a candidate executable_sha256", _SHA256),
    )


def _tags(value: object) -> tuple[tuple[str, str], ...]:
    """Decode llm-shared's recorded tags: each name with its commit, in history order."""
    tags = [_object(item, "inputs.llm_shared_tags", frozenset({"name", "commit"})) for item in _items(value, "inputs.llm_shared_tags")]
    return tuple((_text(tag["name"], "an llm-shared tag name"), _hex(tag["commit"], "an llm-shared tag commit", _OBJECT)) for tag in tags)


def _inputs(value: object) -> FrozenInputs:
    """Decode the frozen inputs."""
    fields = _object(value, "inputs", _INPUTS)
    return FrozenInputs(
        pin=_text(fields["pin"], "inputs.pin"), baseline=_text(fields["baseline"], "inputs.baseline"),
        llm_shared_commit=_hex(fields["llm_shared_commit"], "inputs.llm_shared_commit", _OBJECT),
        llm_shared_tags=_tags(fields["llm_shared_tags"]), cliff_toml=_cliff(fields["cliff_toml"]),
        fixture=_fixture(fields["fixture"]), ranges=tuple(_range(item) for item in _items(fields["ranges"], "inputs.ranges")),
        candidates=tuple(_candidate(item) for item in _items(fields["candidates"], "inputs.candidates")),
        flags=_texts(fields["flags"], "inputs.flags"), environment=_texts(fields["environment"], "inputs.environment"),
    )


def _case(value: object, versions: tuple[str, str]) -> CaseResult:
    """Decode one case, its results in baseline then pin order."""
    fields = _object(value, "a case", _CASE)
    case = _range({"repository": fields["repository"], "range": fields["range"]})
    results = _object(fields["results"], f"{case.key} results", frozenset(versions))
    digests: list[tuple[str, RunDigest]] = []
    for version in versions:
        result = _object(results[version], f"{case.key} {version}", frozenset({"sha256", "status"}))
        digests.append((version, RunDigest(_hex(result["sha256"], f"{case.key} sha256", _SHA256), _number(result["status"], f"{case.key} status"))))
    return CaseResult(case, tuple(digests), _texts(fields["hunks"], f"{case.key} hunks"))


def _classification(value: object) -> Classification:
    """Decode one classification entry."""
    fields = _object(value, "a classification", frozenset({"hunk", "kind", "reason"}))
    return Classification(*(_text(fields[key], f"a classification {key}") for key in ("hunk", "kind", "reason")))


def _audit(value: object) -> Audit | None:
    """Decode the audit, absent until it is written."""
    if value is None:
        return None
    fields = _object(value, "audit", _AUDIT)
    if not isinstance(fields["excludes_69"], bool):
        _fail("audit.excludes_69 is not true or false")
    categories: list[AuditCategory] = []
    for item in _items(fields["categories"], "audit.categories"):
        category = _object(item, "an audit category", frozenset({"name", "references", "finding"}))
        categories.append(AuditCategory(_text(category["name"], "an audit category name"), _texts(category["references"], "audit references"),
                                        _text(category["finding"], "an audit finding")))
    return Audit(revision=_text(fields["revision"], "audit.revision"), excludes_69=fields["excludes_69"],
                 commands=_texts(fields["commands"], "audit.commands"), categories=tuple(categories))


def _observed(value: object) -> ObservedStatus:
    """Decode one observed status."""
    fields = _object(value, "an observed status", frozenset({"name", "command", "status"}))
    return ObservedStatus(_text(fields["name"], "an observed status name"), _text(fields["command"], "an observed command"),
                          _number(fields["status"], "an observed status"))


def _files(value: object, pin: str, baseline: str) -> tuple[tuple[str, str], ...]:
    """Decode the listed digests: exactly the `cliff.toml` copy and both trust records."""
    fields = _object(value, "files", frozenset(listed_files(pin, baseline)))
    return tuple(sorted((name, _hex(digest, f"files.{name}", _SHA256)) for name, digest in fields.items()))


def _review(value: object) -> Review | None:
    """Decode the review member, absent until the user's decision."""
    if value is None:
        return None
    fields = _object(value, "review", _REVIEW)
    return Review(*(_text(fields[key], f"review.{key}") for key in ("decision", "reviewer", "date", "covered_sha256")))


def _decode(document: dict[str, object]) -> Bundle:
    """Decode a schema 1 document."""
    fields = _object(document, "the bundle", _MEMBERS, frozenset({"review"}))
    if type(fields["schema"]) is not int or fields["schema"] != SCHEMA:
        _fail(f"schema {fields['schema']!r} is not {SCHEMA}")
    inputs = _inputs(fields["inputs"])
    versions = (inputs.baseline, inputs.pin)
    return Bundle(
        inputs=inputs, outputs=ComparisonResult(tuple(_case(item, versions) for item in _items(fields["outputs"], "outputs"))),
        files=_files(fields["files"], inputs.pin, inputs.baseline),
        classification=tuple(_classification(item) for item in _items(fields["classification"], "classification")),
        audit=_audit(fields["audit"]), observed_statuses=tuple(_observed(item) for item in _items(fields["observed_statuses"], "observed_statuses")),
        review=_review(fields.get("review")),
    )


def _encode_inputs(inputs: FrozenInputs) -> dict[str, object]:
    """Encode the frozen inputs."""
    cliff, fixture = inputs.cliff_toml, inputs.fixture
    return {
        "pin": inputs.pin, "baseline": inputs.baseline, "llm_shared_commit": inputs.llm_shared_commit,
        "llm_shared_tags": [{"name": name, "commit": commit} for name, commit in inputs.llm_shared_tags],
        "cliff_toml": {"source": cliff.source, "sha256": cliff.sha256, "dev_workflow_commit": cliff.dev_workflow_commit},
        "flags": list(inputs.flags), "environment": list(inputs.environment),
        "fixture": {"head": fixture.head, "tags": [{"name": name, "object": sha} for name, sha in fixture.tags]},
        "ranges": [{"repository": case.repository, "range": case.range} for case in inputs.ranges],
        "candidates": [{"version": candidate.version, "asset": candidate.asset, "size": candidate.size, "sha256": candidate.sha256,
                        "trust": candidate.trust, "executable_sha256": candidate.executable_sha256} for candidate in inputs.candidates],
    }


def _encode(bundle: Bundle, *, review: bool) -> dict[str, object]:
    """Encode the bundle, with its review member when asked and present."""
    audit = bundle.audit
    document: dict[str, object] = {
        "schema": SCHEMA, "inputs": _encode_inputs(bundle.inputs),
        "outputs": [{"repository": case.case.repository, "range": case.case.range,
                     "results": {version: {"sha256": digest.sha256, "status": digest.status} for version, digest in case.results},
                     "hunks": list(case.hunks)} for case in bundle.outputs.cases],
        "classification": [{"hunk": entry.hunk, "kind": entry.kind, "reason": entry.reason} for entry in bundle.classification],
        "audit": None if audit is None else {
            "revision": audit.revision, "excludes_69": audit.excludes_69, "commands": list(audit.commands),
            "categories": [{"name": item.name, "references": list(item.references), "finding": item.finding} for item in audit.categories]},
        "observed_statuses": [{"name": item.name, "command": item.command, "status": item.status} for item in bundle.observed_statuses],
        "files": dict(bundle.files),
    }
    if review and bundle.review is not None:
        entry = bundle.review
        document["review"] = {"decision": entry.decision, "reviewer": entry.reviewer, "date": entry.date, "covered_sha256": entry.covered_sha256}
    return document


def canonical_projection(bundle: Bundle) -> bytes:
    """Give the covered content: the bundle without its review, as canonical UTF-8 JSON."""
    return json.dumps(_encode(bundle, review=False), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def covered_sha256(bundle: Bundle) -> str:
    """Hash the covered content, as a review records it."""
    return hashlib.sha256(canonical_projection(bundle)).hexdigest()


def read(directory: Path) -> Bundle:
    """Read a bundle strictly, then require every listed file beside it to match its digest.

    Raises:
        BundleError: `bundle.json` is missing, malformed or of another schema, or a listed file is missing or changed.
    """
    path = directory / BUNDLE_FILE
    try:
        content = path.read_bytes()
    except OSError as error:
        msg = f"{path} cannot be read: {error}"
        raise BundleError(msg) from error
    try:
        document = decode_object(content, label="bundle")
    except (ValueError, TypeError) as error:
        msg = f"{BUNDLE_FILE}: {error}"
        raise BundleError(msg) from error
    bundle = _decode(document)
    for name, digest in bundle.files:
        try:
            actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        except OSError as error:
            msg = f"{name}, listed in {BUNDLE_FILE}, cannot be read: {error}"
            raise BundleError(msg) from error
        if actual != digest:
            msg = f"{name} has SHA-256 {actual}; {BUNDLE_FILE} lists {digest}"
            raise BundleError(msg)
    for identity in bundle.inputs.candidates:
        _reconcile(directory, identity)
    return bundle


def _reconcile(directory: Path, identity: CandidateIdentity) -> None:
    """Require the trust record of a candidate to record the identity the inputs name."""
    name = trust_name(identity.version)
    try:
        recorded = TrustRecord(directory / name, identity.version).read()
    except CandidateError as error:
        msg = f"{name}: {error}"
        raise BundleError(msg) from error
    found = None if recorded is None else (recorded.asset, recorded.size, recorded.sha256, recorded.trust)
    if found != (identity.asset, identity.size, identity.sha256, identity.trust):
        msg = f"{name} records {found}, not the identity the inputs name for git-cliff {identity.version}"
        raise BundleError(msg)


def write(directory: Path, bundle: Bundle) -> None:
    """Write `bundle.json` whole, readable UTF-8 JSON, replacing the previous file at once."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / BUNDLE_FILE
    temporary = target.with_name(f"{BUNDLE_FILE}.tmp")
    temporary.write_bytes((json.dumps(_encode(bundle, review=True), indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    temporary.replace(target)


def with_review(bundle: Bundle, decision: str, day: date) -> Bundle:
    """Record the user's decision over the bundle's current projection, with the local date of the decision."""
    if decision not in DECISIONS:
        msg = f"a review decision is approved or rejected, not {decision!r}"
        raise ValueError(msg)
    return replace(bundle, review=Review(decision, REVIEWER, day.isoformat(), covered_sha256(bundle)))


def refreshed(fresh: Bundle, existing: Bundle) -> Bundle:
    """Keep the hand-written classification, audit, observed statuses and review of an existing bundle over a rerun's content."""
    return replace(fresh, classification=existing.classification, audit=existing.audit, observed_statuses=existing.observed_statuses,
                   review=existing.review)


# eof
