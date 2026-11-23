"""Prove the admission of git-cliff 2.14.2: the shipped manifest copies the committed, user-approved evidence bundle.

Step 7 of v0.14.0 git-cliff-provisioning (design "Candidate lifecycle and
admission order", "Outputs and classification" and "Statuses"; design
decisions Q01, Q11 and Q13; requirement clarifications Q01, Q13 and Q16; plan
decisions Q03, Q08 and Q16). The harness ran by hand, the user approved its
bundle, and the manifest now admits one pin. These tests read the committed
files only; nothing runs git-cliff or reaches the network.

- The shipped manifest holds exactly 2.14.2, default, with its published
  asset name, size, digest and member, and its evidence reference names the
  committed bundle directory.
- That bundle passes `require_admissible` against the shipped manifest at its
  default location: its review is the user's approval, dated, covering the
  recomputed projection; its listed digests are those of the committed
  `cliff.toml` and both trust records; its 2.14.2 candidate is the manifest
  entry, with upstream-digest trust.
- The 2.7.0 baseline keeps its evidence-only trust record and never enters
  the manifest: `version = 2.7.0` stays a configuration error.

Code review round 1 of Step 7: with `core.autocrlf=true`, a fresh checkout
rewrote the bundle's hashed files with CRLF line endings, and `read` refused
them. `.gitattributes` now unsets `text` for the bundle directory, so Git
converts nothing there. The suite never starts Git: the test checks that
attribute line and that a CRLF conversion of each listed file would change
its digest; the checkout itself was verified by hand.
"""

from __future__ import annotations

import functools
import hashlib
from datetime import date
from pathlib import Path

import pytest

from tests.unit.tools.release_workflow.version_support import (
    project_identity,
    write_release_ini,
)
from tools.release_workflow.configuration import ConfigurationError, load_configuration
from tools.release_workflow.git_cliff.bundle import (
    CLIFF_TOML,
    REVIEWER,
    Bundle,
    covered_sha256,
    listed_files,
    read,
    trust_name,
)
from tools.release_workflow.git_cliff.bundle_checks import require_admissible
from tools.release_workflow.git_cliff.candidates import (
    EVIDENCE_ONLY_HTTPS,
    UPSTREAM_DIGEST,
    TrustRecord,
)
from tools.release_workflow.git_cliff.manifest import (
    ADMITTED_PINS,
    PLATFORM_TRIPLE,
    AdmittedPin,
    PinError,
    default_version,
    download_url,
    parse_pin,
)

_ROOT = Path(__file__).resolve().parents[5]
_PIN = "2.14.2"
_BASELINE = "2.7.0"
_EVIDENCE = f"tools/release_workflow/git_cliff/bundles/{_PIN}"
_BYTES_KEPT = "tools/release_workflow/git_cliff/bundles/** -text"
_ADMITTED = AdmittedPin(
    version=_PIN, default=True, triple=PLATFORM_TRIPLE, asset=f"git-cliff-{_PIN}-{PLATFORM_TRIPLE}.zip", size=7_428_304,
    sha256="6ece2112b3f4af462190ecbea4aeb1315fff6af415629b597f84319073c31131", member=f"git-cliff-{_PIN}/git-cliff.exe", evidence=_EVIDENCE,
)
INVALID_INPUT = 2


@functools.cache
def _bundle() -> Bundle:
    """Read the committed bundle once; `read` already refuses a listed file that changed."""
    return read(_ROOT / _EVIDENCE)


def test_the_shipped_manifest_admits_exactly_2_14_2_as_its_default() -> None:
    """One pin, the default, with the published identity and the committed bundle as evidence."""
    assert ADMITTED_PINS == (_ADMITTED,)
    assert default_version(ADMITTED_PINS) == _PIN
    assert parse_pin(_PIN, pins=ADMITTED_PINS) == _PIN
    assert download_url(ADMITTED_PINS[0]) == f"https://github.com/orhun/git-cliff/releases/download/v{_PIN}/{_ADMITTED.asset}"


def test_the_committed_bundle_is_admissible_with_the_users_current_approval() -> None:
    """The shipped manifest and the default location pass, and the review is the user's dated approval of this content."""
    bundle = _bundle()
    require_admissible(bundle)
    review = bundle.review
    assert review is not None
    assert (review.decision, review.reviewer) == ("approved", REVIEWER)
    assert date.fromisoformat(review.date).isoformat() == review.date
    assert review.covered_sha256 == covered_sha256(bundle)


def test_the_listed_digests_are_those_of_the_committed_files() -> None:
    """`files` names the `cliff.toml` copy and both trust records with the digests of the committed bytes."""
    bundle = _bundle()
    directory = _ROOT / _EVIDENCE
    committed = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in listed_files(_PIN, _BASELINE)}
    assert dict(bundle.files) == committed
    assert bundle.inputs.cliff_toml.sha256 == committed[CLIFF_TOML]


def test_git_keeps_the_bytes_of_the_listed_files_on_every_checkout() -> None:
    """No line ending is converted in the bundle directory, whose listed digests a CRLF checkout would otherwise break."""
    assert _BYTES_KEPT in (_ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    for name, digest in _bundle().files:
        content = (_ROOT / _EVIDENCE / name).read_bytes()
        assert b"\r" not in content
        assert hashlib.sha256(content.replace(b"\n", b"\r\n")).hexdigest() != digest


def test_the_admitted_identity_is_the_bundles_pin_candidate() -> None:
    """The manifest entry copies the 2.14.2 candidate the bundle compared with 2.7.0, trusted by its upstream digest."""
    bundle = _bundle()
    (candidate,) = (item for item in bundle.inputs.candidates if item.version == _PIN)
    assert (bundle.pin, bundle.baseline) == (_PIN, _BASELINE)
    assert (candidate.asset, candidate.size, candidate.sha256, candidate.trust) == (_ADMITTED.asset, _ADMITTED.size, _ADMITTED.sha256, UPSTREAM_DIGEST)


def test_the_evidence_only_baseline_never_enters_the_manifest() -> None:
    """The 2.7.0 trust record stays evidence-only and no admitted pin carries its version or digest."""
    baseline = TrustRecord(_ROOT / _EVIDENCE / trust_name(_BASELINE), _BASELINE).require()
    assert baseline.trust == EVIDENCE_ONLY_HTTPS
    assert all(pin.version != _BASELINE and pin.sha256 != baseline.sha256 for pin in ADMITTED_PINS)
    with pytest.raises(PinError, match=r"^not a tested git-cliff pin; tested: 2\.14\.2$"):
        parse_pin(_BASELINE, pins=ADMITTED_PINS)


def test_version_2_7_0_stays_a_configuration_error(tmp_path: Path) -> None:
    """A project that declares the evidence-only baseline is refused with the tested pin listed."""
    source = write_release_ini(tmp_path, f"[git-cliff]\nversion = {_BASELINE}\n")
    with pytest.raises(ConfigurationError) as caught:
        load_configuration(project_identity(tmp_path))
    assert str(caught.value) == f"{source} [git-cliff] version='{_BASELINE}': not a tested git-cliff pin; tested: {_PIN}"
    assert caught.value.exit_code == INVALID_INPUT


# eof
