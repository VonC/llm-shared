"""Real-repository fixtures for code-reviewer acceptance tests.

The helpers keep Git setup outside measured test calls where practical while
leaving every scenario on the public renderer, evidence, and exchange seams.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools import code_review_answer, code_review_request
from tools.code_review_evidence import capture_index_tree
from tools.code_review_validation import resolve_code_review_validation
from tools.commit_plan_check import CommitPlanCheckResult, CommitPlanCheckState
from tools.prompt_workflow_code_review import CODE_REVIEW_POLICY
from tools.prompt_workflow_models import MemoryRecord, Topic, WorkflowState
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ArtifactState,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from pathlib import Path

# ruff: noqa: S603, S607

_CREATED_AT = "2026-08-18T12:00:00+02:00"
_repository_template: Path | None = None


def ready_commit_plan_result() -> CommitPlanCheckResult:
    """Return typed ready checker evidence for public renderer fixtures."""
    return CommitPlanCheckResult(CommitPlanCheckState.VALID)


@dataclass(frozen=True)
class Effort:
    """One exact Step 6 effort inside a temporary Git repository."""

    root: Path
    topic: Topic
    state: WorkflowState
    record: MemoryRecord
    context: ReviewContext
    plan: Path
    validation: Path
    umbrella: Path
    source: Path


def git(root: Path, *arguments: str, check: bool = True) -> str:
    """Run one bounded Git command in the temporary repository."""
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout.strip()


def staged_paths(root: Path) -> tuple[str, ...]:
    """Return the exact ordered staged-path inventory."""
    output = git(root, "diff", "--cached", "--name-only")
    return tuple(output.splitlines()) if output else ()


def configure_repository_template(template: Path | None) -> None:
    """Set the session-built real repository copied by acceptance efforts."""
    global _repository_template  # noqa: PLW0603
    _repository_template = template


def create_repository_template(root: Path) -> None:
    """Create one reusable real repository with baseline and staged content."""
    root.mkdir(parents=True)
    git(root, "init", "-q")
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (root / "a.review-mode").write_text("", encoding="utf-8")
    docs = root / "docs" / "v0.11.0"
    docs.mkdir(parents=True)
    umbrella = docs / "draft.v0.11.0.review-mode.md"
    umbrella.write_text("# Review mode\n\n| code-reviewer | pending |\n", encoding="utf-8")
    draft = docs / "draft.v0.11.0.acceptance.md"
    draft.write_text(
        "# Acceptance\n\n- Umbrella: "
        "docs/v0.11.0/draft.v0.11.0.review-mode.md\n",
        encoding="utf-8",
    )
    plan = docs / "plan.v0.11.0.acceptance.md"
    plan.write_text(
        "# Plan\n\n### Step 5. routing\n\n### Step 6. acceptance\n",
        encoding="utf-8",
    )
    validation = docs / "plan.v0.11.0.acceptance.validation.md"
    validation.write_text(
        "# Validation\n\n### Analysis of Step 6 implementation state\n\n"
        "Not started.\n",
        encoding="utf-8",
    )
    source = root / "reviewed.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    git(root, "add", ".gitignore", "docs", "reviewed.py")
    git(
        root,
        "-c",
        "user.name=Acceptance",
        "-c",
        "user.email=acceptance@example.invalid",
        "commit",
        "-qm",
        "baseline",
    )
    source.write_text("VALUE = 2\n", encoding="utf-8")
    git(root, "add", "reviewed.py")


def make_effort(root: Path, *, step: str = "6") -> Effort:
    """Copy one marker-enabled real Git effort and bind its typed context."""
    if _repository_template is None:
        create_repository_template(root)
    else:
        shutil.copytree(_repository_template, root)
    docs = root / "docs" / "v0.11.0"
    umbrella = docs / "draft.v0.11.0.review-mode.md"
    draft = docs / "draft.v0.11.0.acceptance.md"
    plan = docs / "plan.v0.11.0.acceptance.md"
    validation = docs / "plan.v0.11.0.acceptance.validation.md"
    source = root / "reviewed.py"
    context = code_review_request.code_review_context(plan, step, umbrella)
    topic = Topic("v0.11.0", "acceptance", draft)
    state = WorkflowState(
        requirement=None,
        design=None,
        plan=plan,
        validation_plan=validation,
        requirement_has_open_questions=False,
        design_has_open_questions=False,
        plan_has_open_questions=False,
        memory_step=10,
    )
    record = MemoryRecord(
        branch="acceptance",
        version="v0.11.0",
        topic="acceptance",
        step=10,
        instruction="implement-step.md",
        plan_step=step,
    )
    return Effort(root, topic, state, record, context, plan, validation, umbrella, source)


def core(effort: Effort) -> ReviewExchangeCore:
    """Bind the shared exchange to the code-review policy."""
    ReviewArtifactConfiguration.load(effort.root).prepare_home()
    return ReviewExchangeCore(
        ReviewExchangeStore(derive_artifact_paths(effort.root, effort.context)),
        effort.context,
        CODE_REVIEW_POLICY,
        ReviewConfiguration(enabled=True, wait_timeout_seconds=300),
    )


def render_request(
    effort: Effort,
    *,
    round_number: int = 1,
    guidance: str | None = None,
    tree: str | None = None,
) -> code_review_request.CodeReviewRequestRender:
    """Render one exact request from the live Git index."""
    return code_review_request.render_code_review_request(
        code_review_request.CodeReviewRoundInput(
            context=effort.context,
            round_number=round_number,
            created_at=_CREATED_AT,
            assessment="Step 6 is ready for independent assessment.",
            implementation_report="Acceptance behavior is staged and tested.",
            change_summary="The staged paths match the Step 6 plan.",
            writer_response="Please assess the exact staged subject.",
            request_index_tree=tree or capture_index_tree(effort.root),
            resolved_validation_set=resolve_code_review_validation(
                ("ghog day",),
                ("focused Step 6 acceptance",),
            ),
            commit_plan_result=ready_commit_plan_result(),
            human_guidance=guidance,
        ),
    )


def publish_rendered_request(
    exchange: ReviewExchangeCore,
    rendered: code_review_request.CodeReviewRequestRender,
) -> None:
    """Publish one already-rendered request through the shared exchange."""
    exchange.publish_request(rendered.request_content, rendered.transcript_summary)


def start_request(
    effort: Effort,
    *,
    guidance: str | None = None,
) -> tuple[ReviewExchangeCore, code_review_request.CodeReviewRequestRender]:
    """Start the exchange and publish one paired request."""
    exchange = core(effort)
    exchange.start()
    rendered = render_request(effort, guidance=guidance)
    publish_rendered_request(exchange, rendered)
    assert exchange.classify().state is ArtifactState.REQUEST_PENDING
    return exchange, rendered


def render_early_rejection(
    effort: Effort,
    disagreement: str,
    *,
    round_number: int = 1,
) -> code_review_answer.CodeReviewAnswerRender:
    """Render one valid early-rejection answer."""
    return code_review_answer.render_code_review_answer(
        code_review_answer.EarlyRejectionAssessment(
            context=effort.context,
            project_root=effort.root,
            round_number=round_number,
            exchange_occurrence=1,
            created_at=_CREATED_AT,
            disposition=ReviewDisposition.CHANGES_REQUESTED,
            disagreement=disagreement,
            writer_instructions="Publish a corrected request.",
        ),
    )


def render_assessment(  # noqa: PLR0913
    effort: Effort,
    disposition: ReviewDisposition,
    *,
    round_number: int = 1,
    repairs: tuple[str, ...] = (),
    staged: tuple[str, ...] = (),
    findings: tuple[str, ...] = (),
    boundary: tuple[str, ...] = (),
    substantive_repair: bool = False,
    readiness_floor_complete: bool = True,
    guidance: tuple[str, str] | None = None,
) -> code_review_answer.CodeReviewAnswerRender:
    """Render one complete implementation assessment with typed evidence."""
    tree = capture_index_tree(effort.root)
    human_guidance, guidance_response = guidance or (None, None)
    return code_review_answer.render_code_review_answer(
        code_review_answer.ImplementationAssessment(
            context=effort.context,
            project_root=effort.root,
            round_number=round_number,
            exchange_occurrence=1,
            created_at=_CREATED_AT,
            disposition=disposition,
            baseline_index_tree=tree,
            assessed_index_tree=tree,
            implementation_check="Yes. The exact plan step is implemented.",
            validation_plan_effects="Only the reviewed Step 6 row changed.",
            pre_repair_validation="All mandatory checks completed.",
            resolved_validation_set="Project and Step 6 commands agree.",
            resolver_drift="No validation command drift was found.",
            repository_state_comparison="The explicit path set is acceptable.",
            repairs=repairs,
            staged_paths=staged,
            commit_plan_assessment="The typed commit groups are accurate.",
            unresolved_findings=findings,
            boundary_crossing_work=boundary,
            writer_instructions="Address findings or continue to the human gate.",
            decision_rationale="The disposition follows the complete evidence floor.",
            substantive_repair=substantive_repair,
            readiness_floor_complete=readiness_floor_complete,
            human_guidance=human_guidance,
            guidance_response=guidance_response,
        ),
    )
