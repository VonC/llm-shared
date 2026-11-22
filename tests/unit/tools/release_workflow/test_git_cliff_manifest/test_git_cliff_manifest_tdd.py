"""Prove the tested-pin manifest: admission, pin text, invariants and the URL.

Step 1 of v0.14.0 git-cliff-provisioning shipped the manifest with an empty
admitted tuple (design Q01). An empty table still refuses every declared
version with `tested: none` and has no default. Synthetic tables prove
admission, the default, the invariant check and that each table is validated
and indexed once, so a later lookup is one dictionary access.

Step 7 admits 2.14.2: the shipped table is valid, defaults to it and lists it
when refusing another version; the admission leaf
`test_git_cliff_acceptance` ties its identity to the committed bundle.

Code review round 1 of Step 1 found that a cache key made of the table hashed
every pin on each lookup; an instrumented table now proves that warm
`parse_pin`, `admitted` and `default_version` calls never hash, compare, size
or visit the pins.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, ClassVar

import pytest

from tools.release_workflow.git_cliff import manifest
from tools.release_workflow.git_cliff.manifest import (
    ADMITTED_PINS,
    PLATFORM_TRIPLE,
    AdmittedPin,
    ManifestError,
    PinError,
    admitted,
    default_version,
    download_url,
    parse_pin,
    validate_pins,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

_SIZE = 7_428_304
_DIGEST = "0123456789abcdef" * 4
_EVIDENCE = "tools/release_workflow/git_cliff/bundles/2.14.2"


def _pin(version: str = "2.14.2", *, default: bool = True) -> AdmittedPin:
    """Build a synthetic pin whose asset and member names derive from its version."""
    return AdmittedPin(
        version=version, default=default, triple=PLATFORM_TRIPLE, asset=f"git-cliff-{version}-{PLATFORM_TRIPLE}.zip",
        size=_SIZE, sha256=_DIGEST, member=f"git-cliff-{version}/git-cliff.exe", evidence=_EVIDENCE,
    )


_PINS = (_pin(), _pin("2.15.1", default=False))


class _CountingPins(tuple[AdmittedPin, ...]):
    """A pin table that records every access that would hash, compare, size or visit its pins.

    A tuple subtype cannot keep instance attributes in slots, so the record is
    one class-level list; the only test that uses this table clears it first.
    """

    __slots__ = ()
    operations: ClassVar[list[str]] = []

    def __iter__(self) -> Iterator[AdmittedPin]:
        """Record a traversal."""
        self.operations.append("iter")
        return super().__iter__()

    def __hash__(self) -> int:
        """Record a hash, which hashes every pin."""
        self.operations.append("hash")
        return super().__hash__()

    def __eq__(self, value: object, /) -> bool:
        """Record a comparison, which compares pins."""
        self.operations.append("eq")
        return super().__eq__(value)

    def __len__(self) -> int:
        """Record a size query."""
        self.operations.append("len")
        return super().__len__()

    def __contains__(self, key: object, /) -> bool:
        """Record a membership scan."""
        self.operations.append("contains")
        return super().__contains__(key)


def test_a_synthetic_default_is_admitted_and_given_as_default() -> None:
    """Every tabled version is admitted; the default is the one marked as such."""
    assert default_version(_PINS) == "2.14.2"
    assert admitted("2.15.1", _PINS) is _PINS[1]
    assert parse_pin("2.14.2", pins=_PINS) == "2.14.2"
    assert parse_pin("2.15.1", pins=_PINS) == "2.15.1"


@pytest.mark.parametrize("raw", ["v2.14.2", "2.14", "2.14.2-rc.1", "latest", " 2.14.2", "2.14.2 ", "", "02.14.2", "2.14.2.0", chr(0x0662) + ".14.2"])
def test_other_pin_forms_are_refused_with_the_form_message(raw: str) -> None:
    """Only exact ASCII X.Y.Z is a pin: no v, prerelease, latest, padding or other digits."""
    with pytest.raises(PinError, match=r"^expected an exact git-cliff version X\.Y\.Z"):
        parse_pin(raw, pins=_PINS)


def test_a_well_formed_absent_version_lists_the_tested_pins() -> None:
    """A version outside the table is refused with every tested pin, in table order."""
    with pytest.raises(PinError, match=r"^not a tested git-cliff pin; tested: 2\.14\.2, 2\.15\.1$"):
        parse_pin("2.15.0", pins=_PINS)
    with pytest.raises(PinError, match=r"tested: 2\.14\.2, 2\.15\.1$"):
        admitted("2.15.0", _PINS)


def test_an_empty_table_refuses_with_tested_none_and_has_no_default() -> None:
    """Without an admitted pin, no version is tested and the domain has no default."""
    empty: tuple[AdmittedPin, ...] = ()
    assert validate_pins(empty) == ()
    assert default_version(empty) is None
    with pytest.raises(PinError, match=r"^not a tested git-cliff pin; tested: none$"):
        parse_pin("2.14.2", pins=empty)


def test_the_shipped_table_is_valid_and_defaults_to_its_admitted_pin() -> None:
    """Since Step 7, the shipped table passes its own invariants, defaults to 2.14.2 and lists it."""
    assert validate_pins(ADMITTED_PINS) is ADMITTED_PINS
    assert default_version(ADMITTED_PINS) == "2.14.2"
    with pytest.raises(PinError, match=r"^not a tested git-cliff pin; tested: 2\.14\.2$"):
        parse_pin("2.15.0", pins=ADMITTED_PINS)


@pytest.mark.parametrize(("pins", "message"), [
    ((_pin(), _pin("2.15.1")), "exactly one default, found 2"),
    ((_pin(default=False),), "exactly one default, found 0"),
    ((_pin(), _pin(default=False)), "Duplicate admitted git-cliff version: 2.14.2"),
    ((replace(_pin(), version="v2.14.2"),), "'v2.14.2': invalid version$"),
    ((replace(_pin(), triple="x86_64-unknown-linux-gnu"),), "invalid triple$"),
    ((replace(_pin(), asset="git-cliff.zip"),), "invalid asset$"),
    ((replace(_pin(), asset=_pin("2.15.1").asset),), "invalid asset$"),
    ((replace(_pin(), member="git-cliff.exe"),), "invalid member$"),
    ((replace(_pin(), member=_pin("2.15.1").member),), "invalid member$"),
    ((replace(_pin(), sha256=_DIGEST.upper()),), "invalid sha256$"),
    ((replace(_pin(), sha256=_DIGEST[:-1]),), "invalid sha256$"),
    ((replace(_pin(), size=0),), "invalid size$"),
    ((replace(_pin(), evidence=""),), "invalid evidence$"),
])
def test_the_invariant_check_refuses_an_inconsistent_table(pins: tuple[AdmittedPin, ...], message: str) -> None:
    """Defaults, duplicates, derived names, digest form, size and evidence are all checked."""
    with pytest.raises(ManifestError, match=message):
        validate_pins(pins)


def test_a_table_is_validated_and_indexed_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Repeated lookups reuse one validated index instead of scanning the table again."""
    calls: list[tuple[AdmittedPin, ...]] = []
    original = manifest.validate_pins

    def counted(pins: tuple[AdmittedPin, ...]) -> tuple[AdmittedPin, ...]:
        calls.append(pins)
        return original(pins)

    monkeypatch.setattr(manifest, "_TABLES", {})
    monkeypatch.setattr(manifest, "validate_pins", counted)
    table = (_pin("3.1.4"),)
    lookups = 3
    for _ in range(lookups):
        assert parse_pin("3.1.4", pins=table) == "3.1.4"
    assert default_version(table) == "3.1.4"
    assert calls == [table]


def test_warm_lookups_never_hash_compare_or_visit_the_pins(monkeypatch: pytest.MonkeyPatch) -> None:
    """After the first use, all three entry points cost one identity lookup, hits and misses alike."""
    monkeypatch.setattr(manifest, "_TABLES", {})
    default, other = _pin(), _pin("2.15.1", default=False)
    table = _CountingPins((default, other))
    table.operations.clear()
    assert default_version(table) == "2.14.2"
    assert "iter" in table.operations
    table.operations.clear()
    lookups = 3
    for _ in range(lookups):
        assert parse_pin("2.15.1", pins=table) == "2.15.1"
        assert admitted("2.14.2", table) is default
        assert default_version(table) == "2.14.2"
        with pytest.raises(PinError, match=r"tested: 2\.14\.2, 2\.15\.1$"):
            parse_pin("2.15.0", pins=table)
    assert table.operations == []


def test_download_url_keeps_the_v_tag_spelling() -> None:
    """The URL is derived from the pin and keeps the upstream vX.Y.Z tag."""
    expected = "https://github.com/orhun/git-cliff/releases/download/v2.14.2/git-cliff-2.14.2-x86_64-pc-windows-msvc.zip"
    assert download_url(_pin()) == expected


# eof
