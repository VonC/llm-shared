"""TDD contracts for the pure specification answer renderer."""

from __future__ import annotations

import re
from dataclasses import FrozenInstanceError, replace
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, cast

import pytest

from tools import spec_review_answer as answer_renderer
from tools.markdown_check.rules import check_md001, check_md025, check_md032
from tools.markdown_check.source import parse_markdown
from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_envelope import parse_envelope_markdown
from tools.spec_review_answer import (
    SpecificationAnswerRender,
    SpecificationAssessment,
    render_specification_answer,
)
from tools.spec_review_request import specification_context

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_models_envelope import Envelope

_TIMESTAMP = "2026-08-11T10:30:00+02:00"
_ROUND = 2
_SOURCE_NAMES = {
    "feature-request": "feature-request.v0.11.0.answer-topic.md",
    "issue": "issue.v0.11.0.answer-topic.md",
    "design-specification": "design.v0.11.0.answer-topic.md",
    "plan": "plan.v0.11.0.answer-topic.md",
}


def _assessment(
    tmp_path: Path,
    type_token: str,
    *,
    disposition: ReviewDisposition = ReviewDisposition.CHANGES_REQUESTED,
    guidance: bool = False,
) -> SpecificationAssessment:
    """Build one exact typed assessment under a repository-like root."""
    docs = tmp_path / "docs" / "v0.11.0"
    docs.mkdir(parents=True, exist_ok=True)
    document = docs / _SOURCE_NAMES[type_token]
    document.write_text("# Specification\n", encoding="utf-8")
    umbrella = docs / "draft.v0.11.0.review-mode.md"
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    convergence = disposition is ReviewDisposition.CONVERGENCE_RECOMMENDED
    return SpecificationAssessment(
        context=specification_context(document, umbrella),
        project_root=tmp_path,
        round_number=_ROUND,
        created_at=_TIMESTAMP,
        disposition=disposition,
        assessment="The specification is coherent and nearly complete.",
        question_verdicts="Q01: choose option A. Q02: retain option B.",
        writer_instructions="Apply the exact findings before another review.",
        requested_changes=(
            None if convergence else "Clarify the recovery owner in Q02."
        ),
        covered_wording=(
            "Polish 'may continue' to 'continues in session'." if convergence else None
        ),
        convergence_rationale=(
            "Only non-substantive wording polish remains." if convergence else None
        ),
        human_guidance="Keep Q01 settled." if guidance else None,
        guidance_response="Q01 remains unchanged." if guidance else None,
    )


def _assert_envelope(rendered: SpecificationAnswerRender, type_token: str) -> str:
    """Assert the shared machine envelope and return authored Markdown."""
    envelope, authored = parse_envelope_markdown(rendered.answer_content)
    assert envelope.identity.type_token == type_token
    assert envelope.role is ReviewRole.REVIEWER
    assert envelope.round_number == _ROUND
    assert envelope.disposition is ReviewDisposition.CHANGES_REQUESTED
    assert rendered.answer_content.startswith("# Review answer for ")
    return authored


def _assert_markdown_identity(authored: str, rendered: SpecificationAnswerRender) -> None:
    """Assert H1/JSON/H2 shape and one repository-relative human identity."""
    assert rendered.answer_content.splitlines()[2] == "## JSON"
    headings = re.findall(r"(?m)^## (.+)$", authored)
    assert headings
    assert len(headings) == len(set(headings))
    assert all("round 2" in heading for heading in headings)
    assert "Reviewed specification: docs/v0.11.0/" in authored
    assert authored.count("Reviewed specification:") == 1


def _assert_paired_findings(rendered: SpecificationAnswerRender) -> None:
    """Assert both outputs carry the same disposition and guidance findings."""
    assert "Q01: choose option A." in rendered.answer_content
    assert "Q01: choose option A." in rendered.transcript_summary
    assert "Clarify the recovery owner" in rendered.answer_content
    assert "Clarify the recovery owner" in rendered.transcript_summary
    assert "Human guidance:\n\nKeep Q01 settled." in rendered.answer_content
    assert "Guidance response:\n\nQ01 remains unchanged." in rendered.answer_content


@pytest.mark.parametrize("type_token", tuple(_SOURCE_NAMES))
def test_render_pairs_supported_identity_markdown_and_findings(
    tmp_path: Path,
    type_token: str,
) -> None:
    """Every specification identity produces one complete paired answer."""
    source = _assessment(tmp_path, type_token, guidance=True)

    rendered = render_specification_answer(source)

    authored = _assert_envelope(rendered, type_token)
    _assert_markdown_identity(authored, rendered)
    assert str(tmp_path).replace("\\", "/") not in authored
    _assert_paired_findings(rendered)


def test_convergence_requires_and_renders_covered_wording_and_rationale(
    tmp_path: Path,
) -> None:
    """Convergence is advisory and carries both required evidence fields."""
    source = _assessment(
        tmp_path,
        "plan",
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
    )

    rendered = render_specification_answer(source)

    assert "Covered wording:\n\nPolish 'may continue'" in rendered.answer_content
    assert "Convergence rationale:\n\nOnly non-substantive" in rendered.answer_content
    assert "Decision: convergence-recommended" in rendered.answer_content
    assert "recommendation is advisory" in rendered.answer_content
    assert "consolidation is not confirmed" in rendered.answer_content
    assert "Covered wording:" in rendered.transcript_summary
    assert "Convergence rationale:" in rendered.transcript_summary


@pytest.mark.parametrize(
    ("disposition", "changes", "wording", "rationale"),
    [
        (
            ReviewDisposition.CHANGES_REQUESTED,
            "1. Clarify the owner.\n2. Name the recovery path.",
            None,
            None,
        ),
        (
            ReviewDisposition.CONVERGENCE_RECOMMENDED,
            None,
            "- Replace one ambiguous verb.\n- Preserve the settled behavior.",
            "Only wording changes remain.",
        ),
    ],
)
def test_labeled_lists_are_separate_blocks_without_md032(
    tmp_path: Path,
    disposition: ReviewDisposition,
    changes: str | None,
    wording: str | None,
    rationale: str | None,
) -> None:
    """Every reviewer list starts after the blank line following its label."""
    source = replace(
        _assessment(tmp_path, "issue", disposition=disposition),
        requested_changes=changes,
        covered_wording=wording,
        convergence_rationale=rationale,
    )

    rendered = render_specification_answer(source)

    for name, markdown in (
        ("answer.md", rendered.answer_content),
        ("transcript.md", rendered.transcript_summary),
    ):
        parsed = parse_markdown(PurePosixPath(name), markdown)
        assert check_md032(parsed) == ()


def test_reviewer_headings_are_nested_without_md001(tmp_path: Path) -> None:
    """Authored answer headings remain children of their generated section."""
    source = replace(
        _assessment(tmp_path, "issue"),
        requested_changes=(
            "# Required correction\n\nClarify the owner.\n\n"
            "## Recovery detail\n\nName the recovery path."
        ),
    )

    rendered = render_specification_answer(source)

    for name, markdown in (
        ("answer.md", rendered.answer_content),
        ("transcript.md", rendered.transcript_summary),
    ):
        parsed = parse_markdown(PurePosixPath(name), markdown)
        assert check_md001(parsed) == ()
        assert check_md025(parsed) == ()
    assert "### Required correction for issue answer-topic (round 2)" in rendered.answer_content
    assert "#### Required correction for issue answer-topic (round 2)" in rendered.transcript_summary


@pytest.mark.parametrize(
    ("changes", "wording", "rationale", "message"),
    [
        (None, None, None, "requested changes"),
        ("Change it.", "stale", None, "convergence evidence"),
    ],
)
def test_changes_requested_requires_only_concrete_changes(
    tmp_path: Path,
    changes: str | None,
    wording: str | None,
    rationale: str | None,
    message: str,
) -> None:
    """Change requests cannot omit actions or carry stale convergence data."""
    source = _assessment(tmp_path, "feature-request")

    with pytest.raises(ReviewExchangeError, match=message):
        replace(
            source,
            requested_changes=changes,
            covered_wording=wording,
            convergence_rationale=rationale,
        )


@pytest.mark.parametrize(
    ("wording", "rationale", "message"),
    [
        (None, "Only polish remains.", "covered wording"),
        ("Polish one sentence.", None, "convergence rationale"),
    ],
)
def test_convergence_rejects_incomplete_evidence(
    tmp_path: Path,
    wording: str | None,
    rationale: str | None,
    message: str,
) -> None:
    """Both convergence-specific fields are mandatory."""
    source = _assessment(
        tmp_path,
        "feature-request",
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
    )

    with pytest.raises(ReviewExchangeError, match=message):
        replace(source, covered_wording=wording, convergence_rationale=rationale)


@pytest.mark.parametrize(
    ("guidance", "response"),
    [("Address this.", None), (None, "Addressed.")],
)
def test_guidance_and_response_are_a_required_pair(
    tmp_path: Path,
    guidance: str | None,
    response: str | None,
) -> None:
    """A dedicated guidance response exists exactly when guidance exists."""
    source = _assessment(tmp_path, "feature-request")

    with pytest.raises(ReviewExchangeError, match="guidance response"):
        replace(source, human_guidance=guidance, guidance_response=response)


def test_models_are_immutable_and_reject_invalid_round_root_and_disposition(
    tmp_path: Path,
) -> None:
    """Typed inputs fail before rendering when trust fields are invalid."""
    source = _assessment(tmp_path, "feature-request")
    with pytest.raises(FrozenInstanceError):
        setattr(source, "round_number", 3)
    with pytest.raises(FrozenInstanceError):
        setattr(SpecificationAnswerRender("answer", "summary"), "answer_content", "changed")

    with pytest.raises(ReviewExchangeError, match="round must be positive"):
        replace(source, round_number=0)
    with pytest.raises(ReviewExchangeError, match="project root"):
        replace(source, project_root=tmp_path / "elsewhere")


def test_assessment_rejects_non_specification_context_and_empty_authored_text(
    tmp_path: Path,
) -> None:
    """Common typed fields fail before any template rendering."""
    source = _assessment(tmp_path, "plan")
    code_identity = ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", "answer-topic")
    code_context = replace(
        source.context,
        identity=code_identity,
        implementation_step="Step 2",
    )
    with pytest.raises(ReviewExchangeError, match="specification context"):
        replace(source, context=code_context)
    with pytest.raises(ReviewExchangeError, match="assessment must be non-empty"):
        replace(source, assessment=" ")
    with pytest.raises(ReviewExchangeError, match="human guidance must be non-empty"):
        replace(source, human_guidance=" ", guidance_response="Addressed.")


def test_assessment_rejects_context_outside_root_and_stale_disposition_fields(
    tmp_path: Path,
) -> None:
    """Containment and mutually exclusive disposition evidence are enforced."""
    source = _assessment(
        tmp_path,
        "feature-request",
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
    )
    other_root = tmp_path / "other-root"
    other_root.mkdir()
    with pytest.raises(ReviewExchangeError, match="under project root"):
        replace(source, project_root=other_root)
    with pytest.raises(ReviewExchangeError, match="cannot carry requested changes"):
        replace(source, requested_changes="Stale action.")


def test_render_result_template_and_shared_validation_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Incomplete pairs, missing templates, and invalid shared output fail closed."""
    source = _assessment(tmp_path, "issue")
    template_path = answer_renderer._TEMPLATE_PATH
    with pytest.raises(ReviewExchangeError, match="paired answer rendering"):
        SpecificationAnswerRender("", "summary")

    monkeypatch.setattr(answer_renderer, "_TEMPLATE_PATH", tmp_path / "missing.template.md")
    with pytest.raises(ReviewExchangeError, match="cannot read answer template"):
        render_specification_answer(source)

    monkeypatch.setattr(
        answer_renderer,
        "_TEMPLATE_PATH",
        template_path,
    )
    def mismatched_envelope(_content: str) -> tuple[Envelope, str]:
        return cast("Envelope", None), ""

    monkeypatch.setattr(answer_renderer, "parse_envelope_markdown", mismatched_envelope)
    with pytest.raises(ReviewExchangeError, match="shared envelope validation"):
        render_specification_answer(source)


def test_absent_guidance_leaves_no_blank_section_gap(tmp_path: Path) -> None:
    """An omitted guidance section cannot widen the spacing between sections."""
    rendered = render_specification_answer(_assessment(tmp_path, "plan"))

    for content in (rendered.answer_content, rendered.transcript_summary):
        lines = content.splitlines()
        runs = [
            index
            for index in range(len(lines) - 1)
            if lines[index] == "" and lines[index + 1] == ""
        ]
        assert runs == [], content
        assert "Human guidance response" not in content
