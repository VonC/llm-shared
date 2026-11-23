"""Generated bundle contents round-trip through `bundle.json`, and the covered projection follows only the content.

Step 6 of v0.14.0 git-cliff-provisioning (plan "Shared test architecture":
property tests for record encoding round trips; plan decision Q16): any hunk
text (non-ASCII and control characters included), classification reason,
status and audit finding written to a bundle reads back to the same model,
with the same canonical projection, and two bundles share a projection only
when their covered content is equal.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    DIFFERING_INDEX,
    place_bundle,
    sample_bundle,
)
from tools.release_workflow.git_cliff.bundle import (
    AuditCategory,
    Classification,
    canonical_projection,
    read,
)
from tools.release_workflow.git_cliff.comparison import ComparisonResult, RunDigest

if TYPE_CHECKING:
    from pathlib import Path

_TEXT = st.text(min_size=1, max_size=40)
_STATUS = st.integers(min_value=0, max_value=255)


@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(hunk=_TEXT, reason=_TEXT, status=_STATUS, finding=_TEXT)
def test_generated_content_round_trips_through_bundle_json(tmp_path: Path, hunk: str, reason: str, status: int, finding: str) -> None:
    """Write, read, and compare the model and its projection; each example rewrites the same directory."""
    base = sample_bundle()
    cases = base.outputs.cases
    case = cases[DIFFERING_INDEX]
    differing = dataclasses.replace(case, hunks=(hunk,), results=(case.results[0], (case.results[1][0], RunDigest("3" * 64, status))))
    assert base.audit is not None
    changes = {
        "outputs": ComparisonResult((*cases[:DIFFERING_INDEX], differing, *cases[DIFFERING_INDEX + 1:])),
        "classification": (Classification(base.classification[0].hunk, "intentional", reason),),
        "audit": dataclasses.replace(base.audit, categories=(AuditCategory("panics", ("src/lib.rs:1",), finding),)),
    }
    written = place_bundle(tmp_path, **changes)
    again = read(tmp_path)
    assert again == written
    assert canonical_projection(again) == canonical_projection(written)


@settings(max_examples=20, deadline=None)
@given(first=_TEXT, second=_TEXT)
def test_two_bundles_share_a_projection_only_when_their_content_is_equal(first: str, second: str) -> None:
    """The projection tells two classification reasons apart exactly when they differ."""
    base = sample_bundle()
    one, two = (dataclasses.replace(base, classification=(Classification(base.classification[0].hunk, "intentional", reason),))
                for reason in (first, second))
    assert (canonical_projection(one) == canonical_projection(two)) == (first == second)


# eof
