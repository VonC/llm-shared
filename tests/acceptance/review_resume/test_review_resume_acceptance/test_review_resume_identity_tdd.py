"""Public CLI identity acceptance for legacy completion across providers.

Each test owns independent legacy records and only its asserted transitions.
Known current records go straight to the real claim command; dedicated
migration tests retain the complete preflight and discovery journey.
Provider-independent ambiguity is checked once. Each provider exercises the
real backfill, capability-reuse and identity-stamping publication transactions.
The codex cases also exercise the public claim and publication adapters;
initial claim orchestration has separate acceptance coverage. The variants
call the same locked transaction without replaying repository-wide discovery.
Every original identity, body, capability and publication assertion remains.
Immutable configuration is cached only inside the measured test lifecycle.
"""

# ruff: noqa: PLR2004
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import pytest

from tests.acceptance.review_resume.conftest import (
    ReviewRepository,
    module_session_environment,
)
from tests.acceptance.review_resume.prepared_request import prepare_request
from tests.scenario_cli import cache_review_inputs
from tests.unit.tools.review_exchange_test_support import review_artifact, review_policy
from tools.llm_nature import LlmNature
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ReviewConfiguration,
    ReviewDisposition,
    ReviewRole,
)
from tools.review_exchange_models_envelope import parse_json_markdown
from tools.review_exchange_ownership import OwnershipCapability
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture(
    params=[
        pytest.param(nature, marks=pytest.mark.xdist_group(f"identity-{nature}"))
        for nature in ("claude", "codex", "gemini", "unknown")
    ],
)
def identity_journey(tmp_path: Path, request: pytest.FixtureRequest) -> Iterator[dict[str, Any]]:
    """Declare legacy prerequisites without executing another test's journey."""
    with pytest.MonkeyPatch.context() as patch:
        freeze_review_mode = cache_review_inputs(patch)
        repo = ReviewRepository(tmp_path / "caller")
        freeze_review_mode()
        yield {"repo": repo, "nature": request.param}


def test_legacy_role_prompt_is_read_only_and_explicit_role_continues(identity_journey: dict[str, Any]) -> None:
    """AC7,10-11,14: an explicit role reuses ownership without rewriting authored content."""
    journey = identity_journey
    repo, nature = journey["repo"], journey["nature"]
    presented = prepare_request(repo, None, owner=Actor.REVIEWER,
                               reviewer_nature=None if nature == "unknown" else nature)
    capability = OwnershipCapability(presented["ownership_generation"], presented["ownership_token"])
    journey["body_before"] = parse_json_markdown(repo.paths.request.read_text(encoding="utf-8"))[1]
    if nature == "codex":
        claimed = repo.claim_known(role="reviewer", nature=nature, capability=presented)
        assert claimed.code == 0, claimed.payload
        assert claimed.payload["action"] == "review-request"
        same = OwnershipCapability(claimed.payload["ownership_generation"], claimed.payload["ownership_token"])
    else:
        same = _claim_transaction(repo, nature, presented)
    journey["body_after"] = parse_json_markdown(repo.paths.request.read_text(encoding="utf-8"))[1]
    assert same == capability
    assert journey["body_before"] == journey["body_after"]


def test_missing_role_inspection_preserves_all_legacy_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The public role prompt is read-only before any explicit claim."""
    freeze_review_mode = cache_review_inputs(monkeypatch)
    repo = ReviewRepository(tmp_path / "caller")
    prepare_request(repo, None)
    freeze_review_mode()
    before = repo.evidence()
    ambiguous = repo.run("resume-inspect", nature="unknown")
    assert ambiguous.payload["outcome"] == "role-selection-required"
    assert ambiguous.code == 3
    assert before == repo.evidence()


def test_selected_identity_backfills_all_runtime_evidence_and_leaves_counterpart_missing(identity_journey: dict[str, Any]) -> None:
    """AC6-7,10: known providers fill only their role; unknown remains absent."""
    journey = identity_journey
    repo, nature = journey["repo"], journey["nature"]
    prepare_request(repo, None)
    _claim_transaction(repo, nature)
    journey["recorded"] = {path.name: repo.natures(path) for path in (repo.paths.request, repo.paths.coordination)}
    expected = None if journey["nature"] == "unknown" else journey["nature"]
    for snapshot in journey["recorded"].values():
        assert snapshot.get("reviewer") == expected
        assert snapshot.get("requestor") is None


def test_answer_publication_records_provider_and_leaves_counterpart_missing(identity_journey: dict[str, Any]) -> None:
    """Publication records even unknown identity from an independently claimed prerequisite."""
    journey = identity_journey
    repo, nature = journey["repo"], journey["nature"]
    capability = prepare_request(repo, None, owner=Actor.REVIEWER,
                                 reviewer_nature=None if nature == "unknown" else nature)
    if nature == "codex":
        answer = repo.publish(ReviewRole.REVIEWER, capability, nature=nature)
        assert answer.code == 0
    else:
        core = ReviewExchangeCore(ReviewExchangeStore(repo.paths), repo.context,
                                  review_policy(repo.context), ReviewConfiguration(enabled=True))
        core.present_ownership(OwnershipCapability(capability["ownership_generation"], capability["ownership_token"]))
        content = review_artifact(repo.context, ReviewRole.REVIEWER, 1,
                                  disposition=ReviewDisposition.CHANGES_REQUESTED)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(os, "environ", module_session_environment(nature))
            core.publish_answer(content, "Acceptance evidence.\n")
    journey["published"] = repo.natures(repo.paths.answer)
    assert journey["published"]["reviewer"] == journey["nature"]
    assert journey["published"]["requestor"] is None


def _claim_transaction(
    repo: ReviewRepository, nature: str, presented: dict[str, Any] | None = None,
) -> OwnershipCapability:
    """Exercise actual locked backfill/claim on explicitly selected records."""
    core = ReviewExchangeCore(ReviewExchangeStore(repo.paths), repo.context,
                              review_policy(repo.context), ReviewConfiguration(enabled=True))
    if presented is not None:
        core.present_ownership(OwnershipCapability(presented["ownership_generation"], presented["ownership_token"]))
    return claim_selected(core, ReviewRole.REVIEWER, LlmNature(nature),
                          round_number=1, occurrence=1, override=False)


# eof
