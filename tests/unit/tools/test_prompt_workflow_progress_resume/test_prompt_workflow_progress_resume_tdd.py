"""Contracts for the `pw progress` prompts that resume an abnormal review.

Abandoned and interrupted exchanges get one role-instruction prompt for the
role `rwst` says continues them; escalated and inconsistent exchanges go to
the requestor. Each prompt is prefixed and named for the target role's
recorded nature. Normal states get none.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from tools import prompt_workflow_progress_resume as progress_resume
from tools.llm_nature import LlmNature
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ExchangeIdentity,
    ReviewFamily,
    ReviewRole,
)
from tools.review_status_models import (
    SCHEMA_VERSION,
    ArtifactApplicability,
    ArtifactKind,
    ArtifactStatus,
    DamagedCandidateStatus,
    ExchangeStatus,
    LeaseFreshness,
    LeaseStatus,
    MigrationStatus,
    NextAction,
    ReviewStatusOutcome,
    ReviewStatusResult,
    RoleNatureEvidenceStatus,
    RoleNatureStatus,
    RoleSpecialization,
)

_PLAN = "docs/v10.0.0/plan.v10.0.0.dex-navigation.md"
_DESIGN = "docs/v10.0.0/design.v10.0.0.dex-navigation.md"
_CLAUDE_ENV = {"CLAUDECODE": "1"}
_UMBRELLA = "docs/v10.0.0/draft.v10.0.0.family.md"
_ESCALATION_TASK = (
    "show me the escalation reason, then ask me to choose reclaim --force, "
    "resolve, or archive to restart the cycle"
)
_REPAIR_TASK = "rerun the interrupted operation with the same content to complete it, then continue"


def _nature(nature: LlmNature) -> RoleNatureStatus:
    return RoleNatureStatus(nature, (RoleNatureEvidenceStatus(".reviews/coordination.md", nature),))


def _exchange(
    state: ArtifactState,
    action: NextAction,
    role: ReviewRole = ReviewRole.REQUESTOR,
) -> ExchangeStatus:
    """Return a code exchange for step 3, Claude requestor and Codex reviewer."""
    return ExchangeStatus(
        identity=ExchangeIdentity(ReviewFamily.CODE, "code", "v10.0.0", "dex-navigation"),
        reviewed_document=_PLAN,
        umbrella=None,
        implementation_step="3",
        round_number=2,
        occurrence=1,
        state=state,
        diagnostic="diagnostic",
        continuing_role=role,
        specialization=RoleSpecialization(f"code-{role.value}"),
        owner=Actor.REQUESTOR,
        lease=LeaseStatus(None, None, "2026-09-26T09:00:00+02:00", 3600, LeaseFreshness.NOT_HELD),
        artifacts={
            kind: ArtifactStatus(
                path=f".reviews/{kind.value}.md",
                applicability=ArtifactApplicability.EXPECTED,
                present=True,
            )
            for kind in ArtifactKind
        },
        requestor_llm_nature=_nature(LlmNature.CLAUDE),
        reviewer_llm_nature=_nature(LlmNature.CODEX),
        next_action=action,
        next_action_text="text",
    )


def _spec(state: ArtifactState, action: NextAction) -> ExchangeStatus:
    """Return a design exchange whose reviewer nature was never recorded."""
    return replace(
        _exchange(state, action, ReviewRole.REVIEWER),
        identity=ExchangeIdentity(
            ReviewFamily.SPECIFICATION, "design-specification", "v10.0.0", "dex-navigation",
        ),
        reviewed_document=_DESIGN,
        implementation_step=None,
        specialization=RoleSpecialization.SPECIFICATION_REVIEWER,
        reviewer_llm_nature=RoleNatureStatus.unrecorded(),
    )


@pytest.mark.parametrize(
    ("state", "action"),
    [
        (ArtifactState.REQUEST_PENDING, NextAction.REVIEWER_WORK),
        (ArtifactState.ANSWER_PENDING, NextAction.REQUESTOR_WORK),
        (ArtifactState.REQUEST_PENDING, NextAction.WAIT_FOR_COUNTERPART),
        (ArtifactState.CONVERGENCE_GATE, NextAction.HUMAN_CONFIRMATION),
        (ArtifactState.OWNING_ACTION_PENDING, NextAction.AUTHORIZED_OWNING_WORK),
    ],
)
def test_a_normal_exchange_needs_no_resume_prompt(state: ArtifactState, action: NextAction) -> None:
    """Waiting, working, the human gate, and the authorized action are normal."""
    assert progress_resume.resume_prompt(_exchange(state, action), _CLAUDE_ENV) is None


def test_an_escalated_exchange_goes_to_the_claude_requestor() -> None:
    """Even a reviewer-shaped escalation asks the requestor for the human choice."""
    exchange = _exchange(ArtifactState.ESCALATED, NextAction.RESOLVE_ESCALATION, ReviewRole.REVIEWER)

    assert progress_resume.target_role(exchange) is ReviewRole.REQUESTOR
    assert progress_resume.resume_prompt(exchange, {}) == (
        f"/code-review-requestor on {_PLAN} step 3: escalated, {_ESCALATION_TASK} (claude)"
    )


def test_an_abandoned_request_goes_to_the_codex_reviewer() -> None:
    """The reviewer continues an abandoned request, with the Codex skill namespace."""
    exchange = _exchange(ArtifactState.ABANDONED_REQUEST, NextAction.RECLAIM, ReviewRole.REVIEWER)

    assert progress_resume.resume_prompt(exchange, _CLAUDE_ENV) == (
        f"$llm-shared:code-reviewer on {_PLAN} step 3: abandoned-request, "
        "reclaim the abandoned round and continue it (codex)"
    )


def test_an_unrecorded_role_uses_the_detected_host_and_names_the_role() -> None:
    """No recorded nature: the host prefix, or the placeholder, and `(reviewer)`."""
    exchange = _spec(ArtifactState.INTERRUPTED_ANSWER_PUBLICATION, NextAction.REPAIR)
    state = "interrupted-answer-publication"

    assert progress_resume.resume_prompt(exchange, _CLAUDE_ENV) == (
        f"/spec-reviewer on {_DESIGN}: {state}, {_REPAIR_TASK} (reviewer)"
    )
    assert progress_resume.resume_prompt(exchange, {}, "codex") == (
        f"$llm-shared:spec-reviewer on {_DESIGN}: {state}, {_REPAIR_TASK} (reviewer)"
    )
    assert progress_resume.resume_prompt(replace(exchange, umbrella=_UMBRELLA), {}) == (
        f"<command-prefix>spec-reviewer on {_DESIGN} with umbrella {_UMBRELLA}: "
        f"{state}, {_REPAIR_TASK} (reviewer)"
    )


def test_resume_prompts_keep_only_abnormal_exchanges() -> None:
    """Damaged candidates and normal exchanges add nothing; order follows the status."""
    inconsistent = _exchange(ArtifactState.INCONSISTENT, NextAction.NO_SAFE_ACTION, ReviewRole.REVIEWER)
    normal = _exchange(ArtifactState.ANSWER_PENDING, NextAction.REQUESTOR_WORK)
    damaged = DamagedCandidateStatus(candidate_path="a.review-active.broken.md", diagnostic="bad")
    result = ReviewStatusResult(
        schema_version=SCHEMA_VERSION,
        repository_root="C:/repo",
        outcome=ReviewStatusOutcome.UNTRUSTWORTHY,
        exchanges=(normal, damaged, inconsistent),
        active_count=3,
        has_errors=True,
        migration=MigrationStatus.unnecessary(".reviews"),
    )

    assert progress_resume.resume_prompts(result, {}) == [
        f"/code-review-requestor on {_PLAN} step 3: inconsistent, explain the "
        "inconsistent evidence and propose a repair without editing review artifacts (claude)",
    ]


# eof
