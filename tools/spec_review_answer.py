"""Pure typed rendering for paired specification review answers.

This module deliberately owns no command-line parsing, path trust checks, or
review-exchange mutation.  It converts one already validated assessment into a
complete reviewer answer and the substantive summary that a caller can publish
through the shared exchange.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import cast

from tools.review_exchange_models import (
    ReviewContext,
    ReviewDisposition,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    validate_local_timestamp,
)
from tools.review_exchange_models_envelope import (
    Envelope,
    parse_envelope_markdown,
    render_envelope_markdown,
)
from tools.review_markdown_headings import qualify_round_headings

_TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / (
    "spec-review-answer.template.md"
)
_JSON_SECTION = "## JSON"


def _required_text(value: object, label: str) -> None:
    """Reject a missing, non-string, or empty authored value."""
    if not isinstance(value, str) or not value.strip():
        raise ReviewExchangeError(f"{label} must be non-empty")


def _optional_text(value: str | None, label: str) -> None:
    """Reject an explicitly supplied empty optional authored value."""
    if value is not None:
        _required_text(value, label)


@dataclass(frozen=True)
class SpecificationAssessment:
    """Immutable exact identity and reviewer findings for one answer round."""

    context: ReviewContext
    project_root: Path
    round_number: int
    created_at: str
    disposition: ReviewDisposition
    assessment: str
    question_verdicts: str
    writer_instructions: str
    requested_changes: str | None = None
    covered_wording: str | None = None
    convergence_rationale: str | None = None
    human_guidance: str | None = None
    guidance_response: str | None = None

    def __post_init__(self) -> None:
        """Validate identity, trust boundary, and disposition-specific fields."""
        if self.context.identity.family is not ReviewFamily.SPECIFICATION:
            raise ReviewExchangeError("renderer requires a specification context")
        if self.round_number <= 0:
            raise ReviewExchangeError("round must be positive")
        validate_local_timestamp(self.created_at)
        root = _validated_root(self)
        object.__setattr__(self, "project_root", root)
        _validate_authored_fields(self)
        _validate_disposition_fields(self)
        _validate_guidance_fields(self)


def _validated_root(source: SpecificationAssessment) -> Path:
    """Resolve the root and prove both context paths stay beneath it."""
    root = source.project_root.resolve()
    if not root.is_dir():
        raise ReviewExchangeError(f"project root is not a directory: {root}")
    try:
        source.context.document_path.relative_to(root)
        if source.context.umbrella_path is not None:
            source.context.umbrella_path.relative_to(root)
    except ValueError as error:
        raise ReviewExchangeError("review context must remain under project root") from error
    return root


def _validate_authored_fields(source: SpecificationAssessment) -> None:
    """Validate common required and optional reviewer-authored fields."""
    required = (
        ("assessment", source.assessment),
        ("question verdicts", source.question_verdicts),
        ("writer instructions", source.writer_instructions),
    )
    optional = (
        ("requested changes", source.requested_changes),
        ("covered wording", source.covered_wording),
        ("convergence rationale", source.convergence_rationale),
        ("human guidance", source.human_guidance),
        ("guidance response", source.guidance_response),
    )
    for label, value in required:
        _required_text(value, label)
    for label, value in optional:
        _optional_text(value, label)


def _validate_disposition_fields(source: SpecificationAssessment) -> None:
    """Require exactly the authored evidence for the selected disposition."""
    if source.disposition is ReviewDisposition.CHANGES_REQUESTED:
        if source.requested_changes is None:
            raise ReviewExchangeError("requested changes must be supplied")
        if source.covered_wording is not None or source.convergence_rationale is not None:
            raise ReviewExchangeError("changes-requested cannot carry convergence evidence")
        return
    if source.requested_changes is not None:
        raise ReviewExchangeError("convergence-recommended cannot carry requested changes")
    if source.covered_wording is None:
        raise ReviewExchangeError("covered wording must be supplied")
    if source.convergence_rationale is None:
        raise ReviewExchangeError("convergence rationale must be supplied")


def _validate_guidance_fields(source: SpecificationAssessment) -> None:
    """Require human guidance and its dedicated response as a pair."""
    if (source.human_guidance is None) != (source.guidance_response is None):
        raise ReviewExchangeError(
            "human guidance and guidance response must be supplied together",
        )


@dataclass(frozen=True)
class SpecificationAnswerRender:
    """Complete answer content and its paired substantive transcript summary."""

    answer_content: str
    transcript_summary: str

    def __post_init__(self) -> None:
        """Reject an incomplete paired renderer result."""
        if not self.answer_content or not self.transcript_summary:
            raise ReviewExchangeError("paired answer rendering must be non-empty")


def _identity_label(source: SpecificationAssessment) -> str:
    """Return a stable label used to make every authored heading unique."""
    identity = source.context.identity
    return f"{identity.type_token} {identity.slug}"


def _relative(path: Path, root: Path) -> str:
    """Render one trusted context path relative to the repository root."""
    return path.relative_to(root).as_posix()


def _identity_fields(source: SpecificationAssessment) -> str:
    """Render the repository-relative human identity exactly once."""
    umbrella = (
        _relative(source.context.umbrella_path, source.project_root)
        if source.context.umbrella_path is not None
        else "none"
    )
    return "\n".join(
        (
            f"Umbrella draft: {umbrella}",
            "Reviewed specification: "
            f"{_relative(source.context.document_path, source.project_root)}",
            f"Review round: {source.round_number}",
        ),
    )


def _authored_body(
    source: SpecificationAssessment,
    body: str,
    *,
    parent_heading_level: int,
) -> str:
    """Nest arbitrary reviewer Markdown below its generated section."""
    return qualify_round_headings(
        body.strip(),
        minimum_level=parent_heading_level + 1,
        qualifier=_identity_label(source),
        round_number=source.round_number,
    )


def _labeled_authored_body(
    source: SpecificationAssessment,
    label: str,
    body: str,
    *,
    parent_heading_level: int,
) -> str:
    """Separate a prose label from any following block-level Markdown."""
    nested = _authored_body(
        source,
        body,
        parent_heading_level=parent_heading_level,
    )
    return f"{label}:\n\n{nested}"


def _disposition_section(source: SpecificationAssessment, level: int) -> str:
    """Render the required findings for the selected disposition."""
    heading = "#" * level
    label = _identity_label(source)
    if source.disposition is ReviewDisposition.CHANGES_REQUESTED:
        requested = _labeled_authored_body(
            source,
            "Requested changes",
            cast("str", source.requested_changes),
            parent_heading_level=level,
        )
        return (
            f"{heading} Requested changes for {label} round {source.round_number}\n\n"
            f"{requested}"
        )
    wording = _labeled_authored_body(
        source,
        "Covered wording",
        cast("str", source.covered_wording),
        parent_heading_level=level,
    )
    rationale = _labeled_authored_body(
        source,
        "Convergence rationale",
        cast("str", source.convergence_rationale),
        parent_heading_level=level,
    )
    return (
        f"{heading} Convergence evidence for {label} round {source.round_number}\n\n"
        f"{wording}\n\n{rationale}"
    )


def _guidance_section(source: SpecificationAssessment, level: int) -> str:
    """Render the dedicated response only when human guidance is present."""
    if source.human_guidance is None:
        return ""
    heading = "#" * level
    label = _identity_label(source)
    guidance = _labeled_authored_body(
        source,
        "Human guidance",
        source.human_guidance,
        parent_heading_level=level,
    )
    response = _labeled_authored_body(
        source,
        "Guidance response",
        cast("str", source.guidance_response),
        parent_heading_level=level,
    )
    return (
        f"{heading} Human guidance response for {label} round "
        f"{source.round_number}\n\n"
        f"{guidance}\n\n{response}"
    )


def _final_decision(source: SpecificationAssessment) -> str:
    """Describe the machine disposition without taking requestor authority."""
    if source.disposition is ReviewDisposition.CHANGES_REQUESTED:
        return (
            "Decision: changes-requested. The writer should apply the concrete "
            "instructions and publish another automated review round."
        )
    return (
        "Decision: convergence-recommended. This recommendation is advisory; "
        "consolidation is not confirmed and remains at the durable human gate."
    )


def _answer_authored_content(source: SpecificationAssessment) -> str:
    """Layer specification-reviewer sections on the shared answer envelope."""
    values = {
        "identity_label": _identity_label(source),
        "round_number": str(source.round_number),
        "identity_fields": _identity_fields(source),
        "assessment": _authored_body(
            source,
            source.assessment,
            parent_heading_level=2,
        ),
        "question_verdicts": _authored_body(
            source,
            source.question_verdicts,
            parent_heading_level=2,
        ),
        "decision_sections": "\n\n".join(
            section
            for section in (
                _disposition_section(source, 2),
                _guidance_section(source, 2),
            )
            if section
        ),
        "writer_instructions": _authored_body(
            source,
            source.writer_instructions,
            parent_heading_level=2,
        ),
        "final_decision": _final_decision(source),
    }
    try:
        template = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        raise ReviewExchangeError(f"cannot read answer template: {error}") from error
    return template.substitute(values).rstrip() + "\n"


def _transcript_summary(source: SpecificationAssessment) -> str:
    """Render every substantive answer finding from the same typed source."""
    label = _identity_label(source)
    sections = [
        f"### Reviewer assessment for {label} round {source.round_number}\n\n"
        f"{_authored_body(source, source.assessment, parent_heading_level=3)}",
        f"### Question verdicts for {label} round {source.round_number}\n\n"
        f"{_authored_body(source, source.question_verdicts, parent_heading_level=3)}",
        _disposition_section(source, 3),
    ]
    guidance = _guidance_section(source, 3)
    if guidance:
        sections.append(guidance)
    instructions = _authored_body(
        source,
        source.writer_instructions,
        parent_heading_level=3,
    )
    sections.extend(
        (
            f"### Writer instructions for {label} round {source.round_number}\n\n"
            f"{instructions}",
            f"### Final reviewer decision for {label} round {source.round_number}\n\n"
            f"{_final_decision(source)}",
        ),
    )
    return "\n\n".join(sections) + "\n"


def render_specification_answer(
    source: SpecificationAssessment,
) -> SpecificationAnswerRender:
    """Render and validate one complete answer and substantive summary pair."""
    context = source.context
    envelope = Envelope(
        identity=context.identity,
        umbrella_path=context.umbrella_path,
        document_path=context.document_path,
        implementation_step=None,
        role=ReviewRole.REVIEWER,
        round_number=source.round_number,
        created_at=source.created_at,
        disposition=source.disposition,
    )
    answer = render_envelope_markdown(envelope, _answer_authored_content(source))
    parsed, _authored = parse_envelope_markdown(answer)
    if parsed != envelope or _JSON_SECTION not in answer:
        raise ReviewExchangeError("rendered answer failed shared envelope validation")
    return SpecificationAnswerRender(answer, _transcript_summary(source))


# eof
