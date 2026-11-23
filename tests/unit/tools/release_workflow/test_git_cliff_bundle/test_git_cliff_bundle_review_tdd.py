"""The user's review binds to the exact evidence: the canonical projection of the bundle and the digests of its files.

Step 6 of v0.14.0 git-cliff-provisioning (plan decision Q16; design decision
Q13; requirement clarification Q16).

- The covered projection is the bundle without its `review` member, as
  canonical JSON (keys sorted, `(",", ":")` separators, ASCII escapes,
  UTF-8); it does not depend on how `bundle.json` is laid out.
- `with_review` records `decision`, `reviewer` `user`, the ISO local date and
  `covered_sha256`; it refuses a decision other than approved or rejected.
- `require_admissible` passes an approved, current review of a complete
  bundle and refuses an absent review, a rejected one, a reviewer other than
  `user`, a malformed date or decision, a `covered_sha256` different from the
  recomputed projection (a content change after approval), and a tampered
  listed file (refused by `read`, through which every committed bundle
  passes).
- A rerun that changes covered content keeps the review member but leaves it
  stale; a byte-identical projection keeps the approval.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import date
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    place_bundle,
    sample_bundle,
)
from tools.release_workflow.git_cliff.bundle import (
    BUNDLE_FILE,
    Review,
    canonical_projection,
    covered_sha256,
    read,
    refreshed,
    with_review,
)

if TYPE_CHECKING:
    from pathlib import Path

_DAY = date(2026, 11, 21)


def test_the_projection_is_canonical_json_of_the_bundle_without_its_review() -> None:
    """Sorted keys, compact separators, ASCII escapes; the review member is not covered."""
    bundle = sample_bundle()
    projection = canonical_projection(bundle)
    document = json.loads(projection)
    assert "review" not in document
    assert projection == json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    assert projection.isascii()
    assert canonical_projection(with_review(bundle, "approved", _DAY)) == projection


def test_the_projection_does_not_depend_on_the_layout_of_bundle_json(tmp_path: Path) -> None:
    """A bundle rewritten with other indentation and key order reads back to the same projection."""
    bundle = place_bundle(tmp_path)
    document = json.loads((tmp_path / BUNDLE_FILE).read_bytes())
    (tmp_path / BUNDLE_FILE).write_text(json.dumps(dict(reversed(document.items())), indent=None), encoding="utf-8")
    assert canonical_projection(read(tmp_path)) == canonical_projection(bundle)


def test_with_review_records_the_decision_the_user_the_day_and_the_covered_digest() -> None:
    """The review covers the projection it was given."""
    bundle = sample_bundle()
    reviewed = with_review(bundle, "approved", _DAY)
    assert reviewed.review == Review("approved", "user", "2026-11-21", hashlib.sha256(canonical_projection(bundle)).hexdigest())
    assert dataclasses.replace(reviewed, review=None) == bundle
    assert reviewed.review is not None
    assert with_review(bundle, "rejected", _DAY).review == dataclasses.replace(reviewed.review, decision="rejected")


def test_with_review_refuses_another_decision() -> None:
    """Only approved and rejected are decisions."""
    with pytest.raises(ValueError, match="approved or rejected"):
        with_review(sample_bundle(), "maybe", _DAY)


def test_refreshed_keeps_the_hand_written_entries_and_the_review_over_fresh_content() -> None:
    """Classification, audit, observed statuses and review come from the existing bundle, everything else from the rerun."""
    existing = with_review(sample_bundle(), "approved", _DAY)
    fresh = dataclasses.replace(sample_bundle(), classification=(), audit=None, observed_statuses=(),
                                inputs=dataclasses.replace(sample_bundle().inputs, llm_shared_commit="e" * 40))
    kept = refreshed(fresh, existing)
    assert (kept.review, kept.classification, kept.audit, kept.observed_statuses) == (
        existing.review, existing.classification, existing.audit, existing.observed_statuses)
    assert kept.inputs.llm_shared_commit == "e" * 40
    assert covered_sha256(kept) != covered_sha256(existing)


# eof
