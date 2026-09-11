"""TDD contracts for discriminated paired code-review answer rendering."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from typing import TYPE_CHECKING, cast

import pytest

from tools import code_review_answer as answer_renderer
from tools.code_review_answer import (
    CodeReviewAnswerRender,
    EarlyRejectionAssessment,
    ImplementationAssessment,
    render_code_review_answer,
)
from tools.code_review_request import code_review_context
from tools.review_exchange_models import (
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_envelope import parse_envelope_markdown

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_models_envelope import Envelope

_TIMESTAMP = "2026-08-17T19:00:00+02:00"
_ROUND = 2
_BASELINE = "a" * 40
_ASSESSED = "b" * 40


def _context(tmp_path: Path) -> ReviewContext:
    """Create one exact code-review context beneath a repository-like root."""
    docs = tmp_path / "docs" / "v0.11.0"
    docs.mkdir(parents=True, exist_ok=True)
    plan = docs / "plan.v0.11.0.answer-topic.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    umbrella = docs / "draft.v0.11.0.review-mode.md"
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    return code_review_context(plan, "4", umbrella)


def _early(tmp_path: Path, *, guidance: bool = False) -> EarlyRejectionAssessment:
    """Build one valid early-rejection source."""
    return EarlyRejectionAssessment(
        context=_context(tmp_path),
        project_root=tmp_path,
        round_number=_ROUND,
        exchange_occurrence=1,
        created_at=_TIMESTAMP,
        disposition=ReviewDisposition.CHANGES_REQUESTED,
        disagreement="The request index tree differs from the live index.",
        writer_instructions="Republish the request from the current index.",
        human_guidance="Inspect generated files." if guidance else None,
        guidance_response="Generated files were included in the comparison."
        if guidance
        else None,
    )


def _assessment(
    tmp_path: Path,
    *,
    disposition: ReviewDisposition = ReviewDisposition.CHANGES_REQUESTED,
    guidance: bool = False,
) -> ImplementationAssessment:
    """Build one fully assessed implementation source."""
    commit_ready = disposition is ReviewDisposition.CONVERGENCE_RECOMMENDED
    return ImplementationAssessment(
        context=_context(tmp_path),
        project_root=tmp_path,
        round_number=_ROUND,
        exchange_occurrence=1,
        created_at=_TIMESTAMP,
        disposition=disposition,
        baseline_index_tree=_BASELINE,
        assessed_index_tree=_ASSESSED,
        implementation_check="Yes. Step 4 has been fully implemented.",
        validation_plan_effects="Only Step 4 validation rows changed.",
        pre_repair_validation="ghog day: fail=0 cov=100 outliers=0.",
        resolved_validation_set="ghog day (sources: plan Step 4).",
        resolver_drift="No resolver drift; direction: unchanged.",
        repository_state_comparison="Tracked state stayed stable around validation.",
        repairs=() if commit_ready else ("Added the missing renderer assertion.",),
        staged_paths=() if commit_ready else ("tests/unit/tools/test_answer.py",),
        commit_plan_assessment="a.commit membership and ordering are exact.",
        unresolved_findings=() if commit_ready else ("Writer reassessment is required.",),
        boundary_crossing_work=(),
        writer_instructions=(
            "No rework is requested."
            if commit_ready
            else "Review the staged repair and publish another round."
        ),
        decision_rationale=(
            "All six readiness-floor items pass without substantive repair."
            if commit_ready
            else "A substantive reviewer repair requires another round."
        ),
        substantive_repair=not commit_ready,
        readiness_floor_complete=commit_ready,
        human_guidance="Inspect generated files." if guidance else None,
        guidance_response="Generated files were included in the comparison."
        if guidance
        else None,
    )


def test_early_rejection_renders_only_identity_disagreement_and_instructions(
    tmp_path: Path,
) -> None:
    """Early rejection omits every full-assessment section from both outputs."""
    rendered = render_code_review_answer(_early(tmp_path, guidance=True))

    envelope, authored = parse_envelope_markdown(rendered.answer_content)
    assert envelope.role is ReviewRole.REVIEWER
    assert envelope.disposition is ReviewDisposition.CHANGES_REQUESTED
    for field in (
        "Umbrella draft:",
        "Implementation plan:",
        "Implementation step:",
        "Review round:",
    ):
        assert authored.count(field) == 1
    for expected in (
        "Exact disagreement",
        "Human guidance:\n\nInspect generated files.",
    ):
        assert expected in authored
    assert "(exchange 1) (round 2)" in authored
    assert "request index tree differs" in rendered.transcript_summary
    assert "Pre-repair validation" not in authored


def test_assessment_renders_validation_repairs_drift_and_advisory_decision(
    tmp_path: Path,
) -> None:
    """One typed assessment supplies all paired substantive sections."""
    rendered = render_code_review_answer(_assessment(tmp_path, guidance=True))

    for content in (rendered.answer_content, rendered.transcript_summary):
        assert "Pre-repair mandatory checks and coverage" in content
        assert "ghog day: fail=0 cov=100 outliers=0." in content
        assert "No resolver drift; direction: unchanged." in content
        assert "Added the missing renderer assertion." in content
        assert "tests/unit/tools/test_answer.py" in content
        assert "a.commit membership and ordering are exact." in content
        assert "Decision: changes-requested" in content
        assert "does not authorize a commit" in content


def test_assessment_nests_and_qualifies_caller_headings_for_each_output(
    tmp_path: Path,
) -> None:
    """Reviewer prose cannot introduce sibling or duplicate transcript headings."""
    source = replace(
        _assessment(tmp_path),
        pre_repair_validation="Lead.\n\n## Test evidence\n\n### Detail",
    )

    rendered = render_code_review_answer(source)

    assert (
        "### Test evidence for step 4 answer-topic (exchange 1) (round 2)"
        in rendered.answer_content
    )
    assert (
        "#### Test evidence for step 4 answer-topic (exchange 1) (round 2)"
        in rendered.transcript_summary
    )
    assert "\n## Test evidence\n" not in rendered.answer_content
    assert "\n## Test evidence\n" not in rendered.transcript_summary


def test_commit_ready_requires_the_floor_and_remains_advisory(tmp_path: Path) -> None:
    """A complete repair-free assessment may recommend but never authorize commit."""
    source = _assessment(
        tmp_path,
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
    )

    rendered = render_code_review_answer(source)

    assert "Decision: commit-ready (advisory)." in rendered.answer_content
    assert "does not authorize a commit" in rendered.answer_content
    assert "Repairs made: None." in rendered.answer_content
    assert "Unresolved findings: None." in rendered.transcript_summary


def test_restarted_exchange_discriminator_qualifies_every_paired_heading(
    tmp_path: Path,
) -> None:
    """A restarted step-round cannot duplicate authored transcript headings."""
    source = replace(_assessment(tmp_path), exchange_occurrence=2)

    rendered = render_code_review_answer(source)

    for content in (rendered.answer_content, rendered.transcript_summary):
        headings = [
            line
            for line in content.splitlines()
            if line.startswith("##") and " for " in line
        ]
        assert headings
        assert all("(exchange 2) (round 2)" in heading for heading in headings)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"round_number": 0}, "round must be positive"),
        ({"exchange_occurrence": 0}, "exchange occurrence must be positive"),
        ({"disagreement": " "}, "disagreement must be non-empty"),
        ({"human_guidance": "Guide.", "guidance_response": None}, "supplied together"),
        ({"disposition": ReviewDisposition.CONVERGENCE_RECOMMENDED}, "changes-requested"),
    ],
)
def test_early_rejection_rejects_invalid_common_or_disposition_fields(
    tmp_path: Path,
    change: dict[str, object],
    message: str,
) -> None:
    """Early rejection fails before template rendering on invalid typed data."""
    with pytest.raises(ReviewExchangeError, match=message):
        replace(_early(tmp_path), **change)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"baseline_index_tree": "bad"}, "tree identity"),
        ({"implementation_check": " "}, "implementation check"),
        ({"repairs": ("",)}, "repair inventory"),
        ({"staged_paths": ("same", "same")}, "duplicate staged paths"),
        ({"repairs": (), "staged_paths": ("orphan.py",)}, "supplied together"),
        ({"human_guidance": None, "guidance_response": "Done."}, "supplied together"),
    ],
)
def test_assessment_rejects_missing_malformed_or_duplicate_evidence(
    tmp_path: Path,
    change: dict[str, object],
    message: str,
) -> None:
    """Every mandatory assessment field and inventory is validated once."""
    with pytest.raises(ReviewExchangeError, match=message):
        replace(_assessment(tmp_path), **change)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"readiness_floor_complete": False}, "readiness floor"),
        (
            {
                "substantive_repair": True,
                "repairs": ("Repair.",),
                "staged_paths": ("tools/repair.py",),
            },
            "substantive repair",
        ),
        ({"unresolved_findings": ("Finding.",)}, "unresolved findings"),
        ({"boundary_crossing_work": ("Outside work.",)}, "boundary-crossing"),
    ],
)
def test_commit_ready_rejects_any_incomplete_or_changed_assessment(
    tmp_path: Path,
    change: dict[str, object],
    message: str,
) -> None:
    """Commit-ready cannot coexist with a failed floor or blocking work."""
    source = _assessment(
        tmp_path,
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
    )
    with pytest.raises(ReviewExchangeError, match=message):
        replace(source, **change)


def test_models_are_immutable_and_context_must_stay_under_root(tmp_path: Path) -> None:
    """Typed variants and paired results keep their validated trust boundary."""
    source = _early(tmp_path)
    with pytest.raises(FrozenInstanceError):
        setattr(source, "round_number", 3)
    with pytest.raises(FrozenInstanceError):
        setattr(CodeReviewAnswerRender("answer", "summary"), "answer_content", "changed")
    outside = tmp_path / "other"
    outside.mkdir()
    with pytest.raises(ReviewExchangeError, match="under project root"):
        replace(source, project_root=outside)
    with pytest.raises(ReviewExchangeError, match="paired answer rendering"):
        CodeReviewAnswerRender("", "summary")


def test_models_reject_wrong_family_non_directory_root_and_non_tuple_inventory(
    tmp_path: Path,
) -> None:
    """Typed model boundaries fail closed before rendering authored content."""
    source = _early(tmp_path)
    wrong_identity = replace(
        source.context.identity,
        family=ReviewFamily.SPECIFICATION,
        type_token="feature-request",  # noqa: S106 - protocol type, not a password
    )
    wrong_context = replace(source.context)
    object.__setattr__(wrong_context, "identity", wrong_identity)
    with pytest.raises(ReviewExchangeError, match="code-review context"):
        replace(source, context=wrong_context)
    with pytest.raises(ReviewExchangeError, match="not a directory"):
        replace(source, project_root=source.context.document_path)
    assessment = _assessment(tmp_path)
    invalid_inventory = cast("tuple[str, ...]", ["not immutable"])
    with pytest.raises(ReviewExchangeError, match="must be a tuple"):
        replace(assessment, repairs=invalid_inventory)


def test_template_and_shared_envelope_validation_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing templates and mismatched envelopes cannot return a partial pair."""
    source = _early(tmp_path)
    template = answer_renderer._TEMPLATE_PATH
    monkeypatch.setattr(answer_renderer, "_TEMPLATE_PATH", tmp_path / "missing.md")
    with pytest.raises(ReviewExchangeError, match="cannot read answer template"):
        render_code_review_answer(source)
    monkeypatch.setattr(answer_renderer, "_TEMPLATE_PATH", template)

    def mismatch(_content: str) -> tuple[Envelope, str]:
        return cast("Envelope", None), ""

    monkeypatch.setattr(answer_renderer, "parse_envelope_markdown", mismatch)
    with pytest.raises(ReviewExchangeError, match="shared envelope validation"):
        render_code_review_answer(source)


# eof
