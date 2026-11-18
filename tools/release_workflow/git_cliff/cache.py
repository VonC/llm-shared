"""Lay out the git-cliff cache, describe a published entry and check it before use, without a lock or a write.

Step 3 of v0.14.0 git-cliff-provisioning (design "Cache layout and the local
integrity record" and "Reuse check and the use guard"; design decisions Q03,
Q07 and Q12; requirement clarifications Q03, Q04 and Q14; plan decisions Q02
and Q12).

- `CacheLayout` places a pin below `<tooling_root>/.tools/git-cliff/`: the
  entry `<pin>/<triple>/` with `git-cliff.exe` and `entry.json`, the lock
  record `<pin>/<triple>.lock` and the attempt directories
  `<pin>/.staging-<pid>-<created>-<token>/` and `.retired-...`, whose names
  carry their owner for recovery. The evidence namespace lives under
  `evidence/`. A version directory name is `X.Y.Z` digits and a triple a
  dashed name, so a production pin never resolves into `evidence/` and no
  name leaves its directory.
- `EntryRecord` (schema 1, written once in staging) and `OwnerFile` (the
  attempt's owner and the children recorded before they resumed) decode
  strictly through `lock_records`: an extra, missing, duplicate or mistyped
  field is refused.
- `check_entry` opens the use guard, reads the record, hashes through the
  guard and runs the version probe, in that order, stopping at the first
  failure. A missing executable makes the entry absent; any other failure
  makes it invalid with its reason. An ordinary failure closes the guard; an
  `UnconfirmedEndError` from the probe retains it first, since no invocation
  exists yet to own it. A valid entry returns the open guard. The check takes
  no lock and writes nothing, so a read-only checkout reuses a valid entry.

A pin is anything with a `version` and a `triple`: an admitted pin, or an
evidence candidate in the evidence namespace.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Protocol, Self, cast

from tools.release_workflow.lock_records import decode_object, positive_integer, text
from tools.release_workflow.windows_child import UnconfirmedEndError
from tools.release_workflow.windows_process import ProcessIdentity

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tools.release_workflow.windows_child import ChildOutcome

SCHEMA = 1
EXECUTABLE = "git-cliff.exe"
ENTRY_RECORD = "entry.json"
OWNER_FILE = "owner.json"
NAMESPACES = ("production", "evidence")
ATTEMPT_KINDS = ("staging", "retired")
_CACHE = (".tools", "git-cliff")
_VERSION_NAME = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
_TRIPLE_NAME = re.compile(r"[a-z0-9_]+(?:-[a-z0-9_]+)+")
_TOKEN = re.compile(r"[0-9a-f]+")
_ATTEMPT = re.compile(r"\.(staging|retired)-([1-9][0-9]*)-([1-9][0-9]*)-([0-9a-f]+)")
_DIGEST = re.compile(r"[0-9a-f]{64}")
_ENTRY_KEYS = ("schema", "version", "triple", "asset", "asset_sha256", "executable_sha256", "executable_size", "provisioned")
_OWNER_KEYS = frozenset({"schema", "pid", "created", "children"})
_IDENTITY_KEYS = frozenset({"pid", "created"})
_ENTRY, _OWNER = "entry", "owner file"


class CachePin(Protocol):
    """What places a pin in the cache: its exact version and its platform triple."""

    @property
    def version(self) -> str:
        """Return the exact `X.Y.Z` version."""
        ...

    @property
    def triple(self) -> str:
        """Return the Rust target name of the platform."""
        ...


class Guard(Protocol):
    """The use guard the reuse check holds: `windows_guard.UseGuard`, or a fake in tests."""

    @property
    def path(self) -> Path:
        """Return the guarded executable."""
        ...

    @property
    def handle(self) -> int:
        """Return the handle a child lists among the handles it inherits."""
        ...

    def sha256_and_size(self) -> tuple[str, int]:
        """Hash the guarded bytes."""
        ...

    def close(self) -> None:
        """Close the guard, unless it was retained."""
        ...

    def retain(self) -> None:
        """Keep the guard open until the process ends."""
        ...


@dataclass(frozen=True)
class Attempt:
    """A staging or retired directory name parsed back to the process that created it."""

    kind: str
    owner: ProcessIdentity
    token: str


@dataclass(frozen=True)
class CacheLayout:
    """The fixed paths of the cache of one executing checkout, in the production or evidence namespace."""

    tooling_root: Path
    namespace: str = "production"

    def __post_init__(self) -> None:
        """Refuse a namespace other than production and evidence."""
        if self.namespace not in NAMESPACES:
            msg = f"unknown git-cliff cache namespace {self.namespace!r}"
            raise ValueError(msg)

    @property
    def root(self) -> Path:
        """Return the namespace root: `.tools/git-cliff`, or its `evidence` folder."""
        base = self.tooling_root.joinpath(*_CACHE)
        return base if self.namespace == "production" else base / "evidence"

    def version_dir(self, pin: CachePin) -> Path:
        """Return `<root>/<version>`, refusing a version or triple that is not a plain name."""
        if _VERSION_NAME.fullmatch(pin.version) is None or _TRIPLE_NAME.fullmatch(pin.triple) is None:
            msg = f"not a cache place: version {pin.version!r}, triple {pin.triple!r}"
            raise ValueError(msg)
        return self.root / pin.version

    def entry_dir(self, pin: CachePin) -> Path:
        """Return the published entry directory `<version>/<triple>`."""
        return self.version_dir(pin) / pin.triple

    def executable(self, pin: CachePin) -> Path:
        """Return the entry's `git-cliff.exe`."""
        return self.entry_dir(pin) / EXECUTABLE

    def record(self, pin: CachePin) -> Path:
        """Return the entry's `entry.json`."""
        return self.entry_dir(pin) / ENTRY_RECORD

    def lock_path(self, pin: CachePin) -> Path:
        """Return the lock record `<version>/<triple>.lock`."""
        return self.version_dir(pin) / f"{pin.triple}.lock"

    def attempt_dir(self, pin: CachePin, kind: str, owner: ProcessIdentity, token: str) -> Path:
        """Return `<version>/.<kind>-<pid>-<created>-<token>`, only for a name that parses back to its owner."""
        if kind not in ATTEMPT_KINDS or owner.pid <= 0 or owner.created <= 0 or _TOKEN.fullmatch(token) is None:
            msg = f"invalid attempt name parts: {kind!r}, {owner!r}, {token!r}"
            raise ValueError(msg)
        return self.version_dir(pin) / f".{kind}-{owner.pid}-{owner.created}-{token}"

    @staticmethod
    def parse_attempt(name: str) -> Attempt | None:
        """Read the kind, owner and token from an attempt directory name, or None for any other name."""
        found = _ATTEMPT.fullmatch(name)
        if found is None:
            return None
        kind, pid, created, token = found.groups()
        return Attempt(kind, ProcessIdentity(int(pid), int(created)), token)


def local_time(record: dict[str, object], key: str, *, label: str) -> str:
    """Require an ISO local time with its offset, as every record stamp is written."""
    value = text(record, key, label=label)
    try:
        moment = datetime.fromisoformat(value)
    except ValueError as error:
        msg = f"Invalid {label} {key}"
        raise ValueError(msg) from error
    if moment.tzinfo is None:
        msg = f"Invalid {label} {key}: no offset"
        raise ValueError(msg)
    return value


def identity_fields(identity: ProcessIdentity) -> dict[str, int]:
    """Encode one process identity as its PID and creation time."""
    return {"pid": identity.pid, "created": identity.created}


def decode_children(record: dict[str, object], *, label: str) -> tuple[ProcessIdentity, ...]:
    """Decode the `children` list: objects holding exactly a positive PID and creation time."""
    value = record.get("children")
    if not isinstance(value, list):
        msg = f"Invalid {label} children"
        raise TypeError(msg)
    children: list[ProcessIdentity] = []
    for item in cast("list[object]", value):
        if not isinstance(item, dict) or item.keys() != _IDENTITY_KEYS:
            msg = f"Invalid {label} child"
            raise ValueError(msg)
        fields = cast("dict[str, object]", item)
        children.append(ProcessIdentity(positive_integer(fields, "pid", label=label), positive_integer(fields, "created", label=label)))
    return tuple(children)


@dataclass(frozen=True, kw_only=True)
class EntryRecord:
    """The local integrity record of a published entry, written once in staging and never edited."""

    schema: int = SCHEMA
    version: str
    triple: str
    asset: str
    asset_sha256: str
    executable_sha256: str
    executable_size: int
    provisioned: str

    def __post_init__(self) -> None:
        """Refuse a foreign schema, an empty name, a malformed digest or size, or a stamp without offset."""
        invalid = next((key for key, valid in (
            ("schema", self.schema == SCHEMA),
            ("names", bool(self.version and self.triple and self.asset)),
            ("asset_sha256", _DIGEST.fullmatch(self.asset_sha256) is not None),
            ("executable_sha256", _DIGEST.fullmatch(self.executable_sha256) is not None),
            ("executable_size", self.executable_size > 0),
        ) if not valid), None)
        if invalid is not None:
            msg = f"Invalid {_ENTRY} {invalid}"
            raise ValueError(msg)
        local_time({"provisioned": self.provisioned}, "provisioned", label=_ENTRY)

    def encode(self) -> bytes:
        """Produce the complete record, one JSON object on one line."""
        return (json.dumps({key: getattr(self, key) for key in _ENTRY_KEYS}, ensure_ascii=True) + "\n").encode("utf-8")

    @classmethod
    def decode(cls, content: bytes) -> Self:
        """Decode a schema 1 record holding exactly its eight fields."""
        record = decode_object(content, label=_ENTRY)
        if record.keys() != set(_ENTRY_KEYS):
            msg = f"Invalid {_ENTRY} fields"
            raise ValueError(msg)
        version, triple, asset, asset_sha256, executable_sha256 = (
            text(record, key, label=_ENTRY) for key in ("version", "triple", "asset", "asset_sha256", "executable_sha256")
        )
        return cls(
            schema=positive_integer(record, "schema", label=_ENTRY), version=version, triple=triple, asset=asset,
            asset_sha256=asset_sha256, executable_sha256=executable_sha256,
            executable_size=positive_integer(record, "executable_size", label=_ENTRY),
            provisioned=local_time(record, "provisioned", label=_ENTRY),
        )


@dataclass(frozen=True)
class OwnerFile:
    """`owner.json` of a staging directory: its owner and every child recorded before it resumed."""

    owner: ProcessIdentity
    children: tuple[ProcessIdentity, ...] = ()

    def with_child(self, child: ProcessIdentity) -> OwnerFile:
        """Return the file with one more recorded child."""
        return OwnerFile(self.owner, (*self.children, child))

    def encode(self) -> bytes:
        """Produce the complete file, one JSON object on one line."""
        fields = {"schema": SCHEMA, **identity_fields(self.owner), "children": [identity_fields(child) for child in self.children]}
        return (json.dumps(fields, ensure_ascii=True) + "\n").encode("utf-8")

    @classmethod
    def decode(cls, content: bytes) -> OwnerFile:
        """Decode a schema 1 owner file holding exactly its four fields."""
        record = decode_object(content, label=_OWNER)
        if record.keys() != _OWNER_KEYS or positive_integer(record, "schema", label=_OWNER) != SCHEMA:
            msg = f"Invalid {_OWNER} fields"
            raise ValueError(msg)
        owner = ProcessIdentity(positive_integer(record, "pid", label=_OWNER), positive_integer(record, "created", label=_OWNER))
        return cls(owner, decode_children(record, label=_OWNER))


@dataclass(frozen=True)
class ValidEntry:
    """A valid entry, held by its open use guard from validation on."""

    guard: Guard
    record: EntryRecord


@dataclass(frozen=True)
class UnusableEntry:
    """An absent or invalid entry and why; no guard is held."""

    absent: bool
    reason: str


type EntryCheck = ValidEntry | UnusableEntry


def _first_line(output: bytes) -> str:
    """Return the first line of the probe output, without its line ending."""
    return next(iter(output.decode("utf-8", errors="replace").splitlines()), "")


def _invalid(reason: str) -> UnusableEntry:
    """Describe an entry that exists but must not be used."""
    return UnusableEntry(absent=False, reason=reason)


def _read_record(layout: CacheLayout, pin: CachePin) -> EntryRecord | str:
    """Read the entry's record for this pin, or say why it cannot describe the entry."""
    try:
        content = layout.record(pin).read_bytes()
    except FileNotFoundError:
        return f"{ENTRY_RECORD} is missing"
    try:
        record = EntryRecord.decode(content)
    except (ValueError, TypeError) as error:
        return f"{ENTRY_RECORD} is invalid: {error}"
    if (record.version, record.triple) != (pin.version, pin.triple):
        return f"{ENTRY_RECORD} names {record.version} for {record.triple}"
    return record


def _bytes_problem(guard: Guard, record: EntryRecord) -> str | None:
    """Hash through the guard; the size and SHA-256 must equal the record."""
    digest, size = guard.sha256_and_size()
    if size != record.executable_size:
        return f"{EXECUTABLE} has {size} bytes; {ENTRY_RECORD} records {record.executable_size}"
    if digest != record.executable_sha256:
        return f"{EXECUTABLE} differs from the SHA-256 in {ENTRY_RECORD}"
    return None


def _probe_problem(outcome: ChildOutcome, pin: CachePin) -> str | None:
    """The probe must end in time, exit 0 and report `git-cliff <pin>` as its first line."""
    if outcome.timed_out:
        return "the version probe did not end within its budget"
    reported, expected = _first_line(outcome.stdout), f"git-cliff {pin.version}"
    if outcome.status != 0 or reported != expected:
        return f"the version probe reported {reported!r} with status {outcome.status}, expected {expected!r}"
    return None


def _validate(layout: CacheLayout, pin: CachePin, guard: Guard, probe: Callable[[Guard], ChildOutcome]) -> EntryCheck:
    """Run the record, hash and probe checks under the held guard, stopping at the first failure."""
    record = _read_record(layout, pin)
    if isinstance(record, str):
        return _invalid(record)
    problem = _bytes_problem(guard, record)
    if problem is None:
        problem = _probe_problem(probe(guard), pin)
    return ValidEntry(guard, record) if problem is None else _invalid(problem)


def check_entry(layout: CacheLayout, pin: CachePin, *, open_guard: Callable[[Path], Guard],
                probe: Callable[[Guard], ChildOutcome]) -> EntryCheck:
    """Check an entry lock-free and read-only: guard, record, hash, then probe.

    Args:
        layout: The cache layout of the executing checkout.
        pin: The pin whose entry is checked.
        open_guard: Opens the use guard; a missing executable raises `FileNotFoundError`.
        probe: Runs `git-cliff.exe --version` as a record-free child inheriting the guard.

    Returns:
        A `ValidEntry` holding the open guard, or an `UnusableEntry` whose guard is closed.

    Raises:
        UnconfirmedEndError: The probe's end is unconfirmed; the guard was retained first.
    """
    try:
        guard = open_guard(layout.executable(pin))
    except FileNotFoundError:
        return UnusableEntry(absent=True, reason=f"{EXECUTABLE} is missing")
    try:
        found = _validate(layout, pin, guard, probe)
    except UnconfirmedEndError:
        guard.retain()
        raise
    except BaseException:
        guard.close()
        raise
    if isinstance(found, UnusableEntry):
        guard.close()
    return found


# eof
