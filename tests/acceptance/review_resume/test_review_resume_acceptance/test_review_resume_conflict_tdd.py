"""Explicit Stop and Override on equivalent recorded role-nature conflicts.

Fix: split out of ``test_review_resume_identity_tdd``, whose four-provider
journey dominated that module. ``--dist loadscope`` keeps a whole module on
one worker, so the conflict scenarios now run beside it rather than behind it.
The scenarios and their assertions are unchanged, and ``legacy_natures`` moved
to the package conftest because both halves seed the same legacy shape.
Immutable path and artifact settings are read once per journey; protocol
records and every CLI transition remain live within the measured lifecycle.
Stop and Override each use independent copies of the same legacy evidence.
Stop uses the real resume dispatcher; Override retains the public CLI boundary.
Both asserting tests execute the relevant operation on current records;
migration/preflight sequencing has separate acceptance coverage.
Legacy records are declared at the data boundary instead of replaying request
publication and transcript append transactions during prerequisite setup.
"""

# ruff: noqa: PLR2004
from __future__ import annotations

import os
from argparse import Namespace
from datetime import datetime
from typing import TYPE_CHECKING, Any

import pytest

from tests.acceptance.review_resume.conftest import (
    ReviewRepository,
    module_session_environment,
)
from tests.acceptance.review_resume.prepared_request import transcript_header
from tests.scenario_cli import cache_review_inputs
from tests.unit.tools.review_exchange_test_support import review_policy, review_summary
from tools.llm_nature import LlmNature
from tools.review_exchange_cli_resume import execute_resume_operation
from tools.review_exchange_models import Actor, CoordinationStatus, ReviewRole
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    Envelope,
    render_envelope_markdown,
    render_json_markdown,
)
from tools.review_exchange_ownership import OwnershipService
from tools.review_role_nature import RoleNatureSnapshot

if TYPE_CHECKING:
    from pathlib import Path

# Keep these related CLI scenarios together in the parallel full stage.
pytestmark = pytest.mark.xdist_group("resume-conflict")


def _prepare_conflict(repo: ReviewRepository) -> None:
    """Declare existing legacy records without replaying atomic publication.

    Publication and transcript repair are not the behavior under test here.
    The real resume calls still read and validate every record, and the Stop
    assertion snapshots request, coordination and transcript bytes unchanged.
    """
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    token = "scenario-request-token-000000000000000"  # noqa: S105 - deterministic test capability
    record = CoordinationRecord(
        repo.context, review_policy(repo.context), CoordinationStatus.ACTIVE,
        Actor.REQUESTOR, Actor.REVIEWER, 1, timestamp,
        role_natures=RoleNatureSnapshot(LlmNature.CODEX, LlmNature.CLAUDE),
        ownership_generation=1, ownership_token_digest=OwnershipService.digest(token),
    )
    title = f"Review exchange coordination for {repo.context.identity.key}"
    repo.paths.coordination.write_text(render_json_markdown(title, record.to_dict(), ""), encoding="utf-8")
    envelope = Envelope(
        repo.context.identity, repo.context.umbrella_path, repo.context.document_path,
        repo.context.implementation_step, ReviewRole.REQUESTOR, 1,
        "2026-08-05T09:00:00+02:00", role_natures=RoleNatureSnapshot(LlmNature.CODEX, None),
    )
    repo.paths.request.write_text(render_envelope_markdown(envelope, review_summary(repo.context, 1)), encoding="utf-8")
    repo.paths.transcript.write_text(transcript_header(repo), encoding="utf-8")


@pytest.fixture
def conflict_journey(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Declare an independent conflict inside each asserting test's lifecycle."""
    freeze_review_mode = cache_review_inputs(monkeypatch)
    repo = ReviewRepository(tmp_path / "caller")
    _prepare_conflict(repo)
    freeze_review_mode()
    return {"repo": repo}


def test_conflict_stop_makes_no_partial_backfill_and_returns_all_evidence(conflict_journey: dict[str, Any]) -> None:
    """AC8-9: a known mismatch stops before claim and reports the conflicting artifact."""
    journey = conflict_journey
    repo = journey["repo"]
    journey["before"] = repo.evidence()
    arguments = Namespace(operation="resume-inspect", document=str(repo.context.document_path),
                          implementation_step=repo.context.implementation_step,
                          role="reviewer", trusted_host_hint=None, override=False,
                          ownership_generation=None, ownership_token=None)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(os, "environ", module_session_environment("codex"))
        payload, code = execute_resume_operation(arguments, repo.root)
    journey["after_stop"] = repo.evidence()
    assert payload["operation"] == "resume-inspect"
    assert payload["outcome"] == "confirmation-required"
    assert code == 3
    assert journey["before"] == journey["after_stop"]
    assert "ownership_token" not in payload
    candidate = payload["candidates"][0]
    assert candidate["reviewer_llm_nature"] == "claude"
    assert candidate["reviewer_evidence"][0]["nature"] == "claude"


def test_override_preserves_conflict_and_fills_only_missing_selected_role(
    conflict_journey: dict[str, Any],
) -> None:
    """AC9: approved Override claims while keeping existing contrary evidence intact."""
    journey = conflict_journey
    repo = journey["repo"]
    journey["override"] = [repo.claim_known(role="reviewer", nature="codex", override=True)]
    journey["snapshots"] = {path.name: repo.natures(path) for path in (repo.paths.request, repo.paths.coordination)}
    assert journey["override"][-1].code == 0
    assert journey["snapshots"][repo.paths.coordination.name] == {"requestor": "codex", "reviewer": "claude"}
    assert journey["snapshots"][repo.paths.request.name] == {"requestor": "codex", "reviewer": "codex"}
    assert journey["override"][-1].payload["action"] == "review-request"


# eof
