"""Name every admitted git-cliff version with the published identity of its asset.

The manifest is a shipped, read-only table (design "The tested-pin manifest
and pin resolution"). A version enters it only with the evidence bundle that
admitted it (design Q01). Its digest is the one GitHub publishes, copied at
admission, so provisioning never calls the GitHub API; the download URL is
derived from the pin and keeps the upstream `vX.Y.Z` tag spelling.

Step 1 of v0.14.0 git-cliff-provisioning ships the empty admitted tuple: the
`[git-cliff]` domain then has no default and refuses every declared version
with `tested: none`, until Step 7 admits 2.14.2 after its reviewed evidence.

The configuration schema imports this module at load time, so it imports only
`dataclasses` and `re` and holds no network, filesystem or process code.

Step 6 adds `asset_url`, the same derivation from a version and an asset
name, for the evidence candidates that are not in any pin table.

Each pin table is validated and indexed on first use. The cache is keyed by
the identity of the table object and keeps that object, so its identity cannot
be reused for another table while cached; a later lookup is one dictionary
access on an integer and never hashes, compares or visits a pin (code review
round 1 of Step 1: a key made of the table itself hashed every pin on each
lookup). Tables are long-lived values: the shipped tuple and the table each
git-cliff domain captures.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PLATFORM_TRIPLE = "x86_64-pc-windows-msvc"
_RELEASES = "https://github.com/orhun/git-cliff/releases/download"
_PIN = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
_DIGEST = re.compile(r"[0-9a-f]{64}")


class PinError(ValueError):
    """A `[git-cliff] version` text is not an exact pin or names no admitted version."""


class ManifestError(ValueError):
    """The shipped pin table breaks an admission invariant before any lookup."""

    exit_code = 2


@dataclass(frozen=True)
class AdmittedPin:
    """One admitted git-cliff version and the published identity of its Windows asset.

    `size` and `sha256` are the archive's published size in bytes and digest;
    `member` is the archive member to extract; `evidence` is the
    repository-relative directory of the committed bundle that admitted the
    pin. The name says admitted rather than tested, so pytest never collects
    the record as a test class.
    """

    version: str
    default: bool
    triple: str
    asset: str
    size: int
    sha256: str
    member: str
    evidence: str


@dataclass(frozen=True)
class _Table:
    """One validated pin table: its index by version, its default and its listing."""

    by_version: dict[str, AdmittedPin]
    default: str | None
    tested: str


# Keyed by id(table); each entry keeps the table so the identity stays its own.
_TABLES: dict[int, tuple[tuple[AdmittedPin, ...], _Table]] = {}


def _invalid_field(pin: AdmittedPin) -> str | None:
    """Name the first field of one pin that breaks its form or its derivation."""
    checks = (
        ("version", _PIN.fullmatch(pin.version) is not None),
        ("triple", pin.triple == PLATFORM_TRIPLE),
        ("asset", pin.asset == f"git-cliff-{pin.version}-{pin.triple}.zip"),
        ("member", pin.member == f"git-cliff-{pin.version}/git-cliff.exe"),
        ("sha256", _DIGEST.fullmatch(pin.sha256) is not None),
        ("size", pin.size > 0),
        ("evidence", bool(pin.evidence)),
    )
    return next((name for name, valid in checks if not valid), None)


def validate_pins(pins: tuple[AdmittedPin, ...]) -> tuple[AdmittedPin, ...]:
    """Refuse an inconsistent table: field forms, duplicates and the single default.

    Args:
        pins: The pin table, shipped or synthetic.

    Returns:
        The same table, so the shipped constant is validated where it is defined.
    """
    versions: set[str] = set()
    for pin in pins:
        field = _invalid_field(pin)
        if field is not None:
            msg = f"Admitted git-cliff pin {pin.version!r}: invalid {field}"
            raise ManifestError(msg)
        if pin.version in versions:
            msg = f"Duplicate admitted git-cliff version: {pin.version}"
            raise ManifestError(msg)
        versions.add(pin.version)
    defaults = sum(1 for pin in pins if pin.default)
    if pins and defaults != 1:
        msg = f"Admitted git-cliff pins need exactly one default, found {defaults}"
        raise ManifestError(msg)
    return pins


def _table(pins: tuple[AdmittedPin, ...]) -> _Table:
    """Validate and index a table on first use; a warm lookup goes by identity and touches no pin."""
    entry = _TABLES.get(id(pins))
    if entry is not None and entry[0] is pins:
        return entry[1]
    validate_pins(pins)
    default = next((pin.version for pin in pins if pin.default), None)
    table = _Table({pin.version: pin for pin in pins}, default, ", ".join(pin.version for pin in pins) or "none")
    _TABLES[id(pins)] = (pins, table)
    return table


def default_version(pins: tuple[AdmittedPin, ...]) -> str | None:
    """Give the tested default version, or None for a table without pins."""
    return _table(pins).default


def admitted(version: str, pins: tuple[AdmittedPin, ...]) -> AdmittedPin:
    """Return the pin admitted for an exact version, listing the tested pins otherwise."""
    table = _table(pins)
    pin = table.by_version.get(version)
    if pin is None:
        msg = f"not a tested git-cliff pin; tested: {table.tested}"
        raise PinError(msg)
    return pin


def parse_pin(raw: str, *, pins: tuple[AdmittedPin, ...]) -> str:
    """Convert `[git-cliff] version` text into an admitted pin, refusing every other form.

    Args:
        raw: The declared or default text, never stripped or normalized here.
        pins: The pin table that decides admission.

    Returns:
        The admitted version, exactly as written.
    """
    if _PIN.fullmatch(raw) is None:
        msg = "expected an exact git-cliff version X.Y.Z, without a v prefix, prerelease or latest"
        raise PinError(msg)
    return admitted(raw, pins).version


def asset_url(version: str, asset: str) -> str:
    """Derive a release asset URL from its version and file name, keeping the upstream vX.Y.Z tag spelling."""
    return f"{_RELEASES}/v{version}/{asset}"


def download_url(pin: AdmittedPin) -> str:
    """Derive the release asset URL of an admitted pin."""
    return asset_url(pin.version, pin.asset)


# Empty until Step 7 admits 2.14.2 with its reviewed evidence bundle.
ADMITTED_PINS: tuple[AdmittedPin, ...] = validate_pins(())


# eof
