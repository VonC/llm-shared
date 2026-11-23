"""An approved, current review by the user is what admits a complete bundle.

Step 6 of v0.14.0 git-cliff-provisioning (plan decision Q16; design decision
Q13; requirement clarification Q16); split from the bundle leaf with
`bundle_checks` in code review round 2.

- `require_admissible` passes an approved, current review of a complete
  bundle and refuses an absent review, a rejected one, a reviewer other than
  `user`, a malformed date or decision, a `covered_sha256` different from the
  recomputed projection (a content change after approval) and an incomplete
  bundle; a tampered listed file never reaches it, `read` refuses it first.
- A rerun that changes covered content keeps the review member but leaves it
  stale; a byte-identical projection keeps the approval.
"""

from __future__ import annotations

import dataclasses
from datetime import date
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    PIN,
    place_bundle,
    sample_bundle,
)
from tools.release_workflow.git_cliff.bundle import (
    CLIFF_TOML,
    BundleError,
    Classification,
    read,
    refreshed,
    with_review,
    write,
)
from tools.release_workflow.git_cliff.bundle_checks import require_admissible

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.git_cliff.bundle import Bundle

_DAY = date(2026, 11, 21)
_LOCATION = f"tools/release_workflow/git_cliff/bundles/{PIN}"


def _admissible(bundle: Bundle) -> None:
    """Check admission for a pin the manifest does not admit yet."""
    require_admissible(bundle, location=_LOCATION, pins=())


def test_an_approved_current_review_of_a_complete_bundle_is_admissible(tmp_path: Path) -> None:
    """The written review reads back and still covers the projection."""
    place_bundle(tmp_path)
    write(tmp_path, with_review(read(tmp_path), "approved", _DAY))
    _admissible(read(tmp_path))


def _reviewed(**review: str) -> Bundle:
    """An approved bundle whose review fields are changed as given."""
    approved = with_review(sample_bundle(), "approved", _DAY)
    assert approved.review is not None
    return dataclasses.replace(approved, review=dataclasses.replace(approved.review, **review))


@pytest.mark.parametrize(("bundle", "reason"), [
    pytest.param(sample_bundle(), "no review", id="absent"),
    pytest.param(with_review(sample_bundle(), "rejected", _DAY), "rejected", id="rejected"),
    pytest.param(_reviewed(reviewer="someone"), "reviewer", id="reviewer"),
    pytest.param(_reviewed(decision="maybe"), "decision", id="decision"),
    pytest.param(_reviewed(date="2026-13-45"), "date", id="impossible-date"),
    pytest.param(_reviewed(date="20261121"), "date", id="basic-date"),
    pytest.param(_reviewed(date="2026-11-21T10:00:00+01:00"), "date", id="date-time"),
    pytest.param(_reviewed(covered_sha256="0" * 64), "changed after", id="stale"),
])
def test_require_admissible_refuses_each_review_problem(bundle: Bundle, reason: str) -> None:
    """No admission without the user's current approval."""
    with pytest.raises(BundleError, match=reason):
        _admissible(bundle)


def test_a_content_change_after_approval_is_refused() -> None:
    """Editing a classification reason after the approval leaves it stale."""
    approved = with_review(sample_bundle(), "approved", _DAY)
    edited = dataclasses.replace(approved, classification=(Classification(approved.classification[0].hunk, "intentional", "another reason"),))
    with pytest.raises(BundleError, match="changed after"):
        _admissible(edited)


def test_an_incomplete_bundle_is_not_admissible_even_when_approved() -> None:
    """Admission needs the completeness checks too."""
    approved = with_review(dataclasses.replace(sample_bundle(), audit=None), "approved", _DAY)
    with pytest.raises(BundleError, match="audit"):
        _admissible(approved)


def test_a_tampered_listed_file_never_reaches_admission(tmp_path: Path) -> None:
    """The committed copy of `cliff.toml` changed after the approval: reading the bundle refuses it."""
    place_bundle(tmp_path)
    write(tmp_path, with_review(read(tmp_path), "approved", _DAY))
    (tmp_path / CLIFF_TOML).write_bytes(b'[changelog]\nbody = "changed"\n')
    with pytest.raises(BundleError, match=CLIFF_TOML):
        _admissible(read(tmp_path))


def test_a_rerun_that_changes_covered_content_keeps_the_review_but_leaves_it_stale() -> None:
    """The kept review no longer covers the fresh projection."""
    existing = with_review(sample_bundle(), "approved", _DAY)
    fresh = dataclasses.replace(sample_bundle(), classification=(), audit=None, observed_statuses=(),
                                inputs=dataclasses.replace(sample_bundle().inputs, llm_shared_commit="e" * 40))
    kept = refreshed(fresh, existing)
    assert (kept.review, kept.classification, kept.audit, kept.observed_statuses) == (
        existing.review, existing.classification, existing.audit, existing.observed_statuses)
    assert kept.inputs.llm_shared_commit == "e" * 40
    with pytest.raises(BundleError, match="changed after"):
        _admissible(kept)


def test_a_byte_identical_projection_keeps_the_approval() -> None:
    """A rerun reproducing every covered byte stays admissible."""
    existing = with_review(sample_bundle(), "approved", _DAY)
    fresh = dataclasses.replace(sample_bundle(), classification=(), audit=None, observed_statuses=())
    _admissible(refreshed(fresh, existing))



# eof
