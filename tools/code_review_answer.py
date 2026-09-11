"""Pure discriminated rendering for paired implementation review answers.

The module accepts either a narrow early rejection or a complete assessed
implementation. It owns no command parsing, Git access, publication, manifest
retirement, or review-exchange mutation.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import re
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
    "code-review-answer.template.md"
)
_TREE_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_JSON_SECTION = "## JSON"


def _required_text(value: object, label: str) -> None:
    """Reject one missing, non-string, or empty authored field."""
    if not isinstance(value, str) or not value.strip():
        raise ReviewExchangeError(f"{label} must be non-empty")


def _validated_common(
    context: ReviewContext,
    project_root: Path,
    round_identity: tuple[int, int],
    created_at: str,
    guidance: tuple[str | None, str | None],
) -> Path:
    """Validate the shared code identity, root, round, time, and guidance."""
    if context.identity.family is not ReviewFamily.CODE:
        raise ReviewExchangeError("renderer requires a code-review context")
    round_number, exchange_occurrence = round_identity
    if round_number <= 0:
        raise ReviewExchangeError("round must be positive")
    if exchange_occurrence <= 0:
        raise ReviewExchangeError("exchange occurrence must be positive")
    validate_local_timestamp(created_at)
    root = project_root.resolve()
    if not root.is_dir():
        raise ReviewExchangeError(f"project root is not a directory: {root}")
    try:
        context.document_path.relative_to(root)
        if context.umbrella_path is not None:
            context.umbrella_path.relative_to(root)
    except ValueError as error:
        raise ReviewExchangeError("review context must remain under project root") from error
    human_guidance, guidance_response = guidance
    if (human_guidance is None) != (guidance_response is None):
        raise ReviewExchangeError(
            "human guidance and guidance response must be supplied together",
        )
    if human_guidance is not None:
        _required_text(human_guidance, "human guidance")
        _required_text(guidance_response, "guidance response")
    return root


def _validated_inventory(values: object, label: str) -> tuple[str, ...]:
    """Return one immutable, unique, non-empty authored inventory."""
    if not isinstance(values, tuple):
        raise ReviewExchangeError(f"{label} must be a tuple")
    typed = cast("tuple[object, ...]", values)  # ty: ignore[redundant-cast]
    if any(not isinstance(value, str) or not value.strip() for value in typed):
        raise ReviewExchangeError(f"{label} contains an empty item")
    normalized = tuple(value.strip() for value in typed if isinstance(value, str))
    if len(set(normalized)) != len(normalized):
        duplicate_label = "duplicate staged paths" if label == "staged path inventory" else (
            f"duplicate {label}"
        )
        raise ReviewExchangeError(duplicate_label)
    return normalized


@dataclass(frozen=True)
class EarlyRejectionAssessment:
    """Protocol-valid disagreement detected before full assessment."""

    context: ReviewContext
    project_root: Path
    round_number: int
    exchange_occurrence: int
    created_at: str
    disposition: ReviewDisposition
    disagreement: str
    writer_instructions: str
    human_guidance: str | None = None
    guidance_response: str | None = None

    def __post_init__(self) -> None:
        """Validate the narrow early-rejection evidence shape."""
        root = _validated_common(
            self.context,
            self.project_root,
            (self.round_number, self.exchange_occurrence),
            self.created_at,
            (self.human_guidance, self.guidance_response),
        )
        object.__setattr__(self, "project_root", root)
        _required_text(self.disagreement, "disagreement")
        _required_text(self.writer_instructions, "writer instructions")
        if self.disposition is not ReviewDisposition.CHANGES_REQUESTED:
            raise ReviewExchangeError("early rejection must use changes-requested")


@dataclass(frozen=True)
class ImplementationAssessment:
    """Complete validated implementation evidence for one answer round."""

    context: ReviewContext
    project_root: Path
    round_number: int
    exchange_occurrence: int
    created_at: str
    disposition: ReviewDisposition
    baseline_index_tree: str
    assessed_index_tree: str
    implementation_check: str
    validation_plan_effects: str
    pre_repair_validation: str
    resolved_validation_set: str
    resolver_drift: str
    repository_state_comparison: str
    repairs: tuple[str, ...]
    staged_paths: tuple[str, ...]
    commit_plan_assessment: str
    unresolved_findings: tuple[str, ...]
    boundary_crossing_work: tuple[str, ...]
    writer_instructions: str
    decision_rationale: str
    substantive_repair: bool
    readiness_floor_complete: bool
    human_guidance: str | None = None
    guidance_response: str | None = None

    def __post_init__(self) -> None:
        """Validate every mandatory field and the advisory disposition."""
        root = _validated_common(
            self.context,
            self.project_root,
            (self.round_number, self.exchange_occurrence),
            self.created_at,
            (self.human_guidance, self.guidance_response),
        )
        object.__setattr__(self, "project_root", root)
        for tree in (self.baseline_index_tree, self.assessed_index_tree):
            if _TREE_RE.fullmatch(tree) is None:
                raise ReviewExchangeError("assessment tree identity is invalid")
        required = (
            ("implementation check", self.implementation_check),
            ("validation plan effects", self.validation_plan_effects),
            ("pre-repair validation", self.pre_repair_validation),
            ("resolved validation set", self.resolved_validation_set),
            ("resolver drift", self.resolver_drift),
            ("repository state comparison", self.repository_state_comparison),
            ("commit plan assessment", self.commit_plan_assessment),
            ("writer instructions", self.writer_instructions),
            ("decision rationale", self.decision_rationale),
        )
        for label, value in required:
            _required_text(value, label)
        object.__setattr__(
            self,
            "repairs",
            _validated_inventory(self.repairs, "repair inventory"),
        )
        object.__setattr__(
            self,
            "staged_paths",
            _validated_inventory(self.staged_paths, "staged path inventory"),
        )
        object.__setattr__(
            self,
            "unresolved_findings",
            _validated_inventory(self.unresolved_findings, "unresolved finding inventory"),
        )
        object.__setattr__(
            self,
            "boundary_crossing_work",
            _validated_inventory(self.boundary_crossing_work, "boundary work inventory"),
        )
        if bool(self.repairs) != bool(self.staged_paths):
            raise ReviewExchangeError("repairs and staged paths must be supplied together")
        if self.disposition is ReviewDisposition.CONVERGENCE_RECOMMENDED:
            self._validate_commit_ready()

    def _validate_commit_ready(self) -> None:
        """Reject any blocking evidence paired with commit-ready."""
        if not self.readiness_floor_complete:
            raise ReviewExchangeError("commit-ready requires the complete readiness floor")
        if self.substantive_repair:
            raise ReviewExchangeError("commit-ready cannot follow a substantive repair")
        if self.unresolved_findings:
            raise ReviewExchangeError("commit-ready cannot carry unresolved findings")
        if self.boundary_crossing_work:
            raise ReviewExchangeError("commit-ready cannot carry boundary-crossing work")


type CodeReviewAssessment = EarlyRejectionAssessment | ImplementationAssessment


@dataclass(frozen=True)
class CodeReviewAnswerRender:
    """Complete answer content and paired substantive transcript summary."""

    answer_content: str
    transcript_summary: str

    def __post_init__(self) -> None:
        """Reject a partial paired rendering result."""
        if not self.answer_content or not self.transcript_summary:
            raise ReviewExchangeError("paired answer rendering must be non-empty")


def _identity_label(source: CodeReviewAssessment) -> str:
    return f"step {source.context.implementation_step} {source.context.identity.slug}"


def _heading_qualifier(source: CodeReviewAssessment) -> str:
    return f"{_identity_label(source)} (exchange {source.exchange_occurrence})"


def _heading_label(source: CodeReviewAssessment) -> str:
    return f"{_heading_qualifier(source)} (round {source.round_number})"


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _identity_fields(source: CodeReviewAssessment) -> str:
    umbrella = (
        _relative(source.context.umbrella_path, source.project_root)
        if source.context.umbrella_path is not None
        else "none"
    )
    return "\n".join(
        (
            f"Umbrella draft: {umbrella}",
            f"Implementation plan: {_relative(source.context.document_path, source.project_root)}",
            f"Implementation step: {source.context.implementation_step}",
            f"Review round: {source.round_number}",
        ),
    )


def _section(
    level: int,
    title: str,
    source: CodeReviewAssessment,
    body: str,
) -> str:
    nested = qualify_round_headings(
        body.strip(),
        minimum_level=level + 1,
        qualifier=_heading_qualifier(source),
        round_number=source.round_number,
    )
    return f"{'#' * level} {title} for {_heading_label(source)}\n\n{nested}"


def _inventory(label: str, values: tuple[str, ...]) -> str:
    if not values:
        return f"{label}: None."
    return f"{label}:\n\n" + "\n".join(f"- {value}" for value in values)


def _guidance_section(source: CodeReviewAssessment, level: int) -> str:
    if source.human_guidance is None:
        return ""
    response = cast("str", source.guidance_response)
    return _section(
        level,
        "Human guidance response",
        source,
        f"Human guidance:\n\n{source.human_guidance.rstrip()}\n\n"
        f"Guidance response:\n\n{response.strip()}",
    )


def _early_sections(source: EarlyRejectionAssessment, level: int) -> list[str]:
    sections = [
        _section(level, "Exact disagreement", source, source.disagreement),
    ]
    guidance = _guidance_section(source, level)
    if guidance:
        sections.append(guidance)
    sections.append(
        _section(
            level,
            "Writer instructions",
            source,
            source.writer_instructions,
        ),
    )
    return sections


def _assessment_sections(source: ImplementationAssessment, level: int) -> list[str]:
    sections = [
        _section(
            level,
            "Assessed index identity",
            source,
            f"Baseline index tree: {source.baseline_index_tree}\n\n"
            f"Assessed index tree: {source.assessed_index_tree}",
        ),
        _section(
            level,
            "Implementation check",
            source,
            f"Result:\n\n{source.implementation_check.strip()}\n\n"
            f"Validation plan effects:\n\n{source.validation_plan_effects.strip()}",
        ),
        _section(
            level,
            "Pre-repair mandatory checks and coverage",
            source,
            source.pre_repair_validation,
        ),
        _section(
            level,
            "Resolved validation set and sources",
            source,
            source.resolved_validation_set,
        ),
        _section(
            level,
            "Resolver drift and direction",
            source,
            source.resolver_drift,
        ),
        _section(
            level,
            "Repository state around validation",
            source,
            source.repository_state_comparison,
        ),
        _section(
            level,
            "Repair inventory",
            source,
            f"{_inventory('Repairs made', source.repairs)}\n\n"
            f"{_inventory('Paths staged', source.staged_paths)}",
        ),
        _section(
            level,
            "Commit plan assessment",
            source,
            source.commit_plan_assessment,
        ),
        _section(
            level,
            "Findings and boundaries",
            source,
            f"{_inventory('Unresolved findings', source.unresolved_findings)}\n\n"
            f"{_inventory('Boundary-crossing work', source.boundary_crossing_work)}",
        ),
    ]
    guidance = _guidance_section(source, level)
    if guidance:
        sections.append(guidance)
    sections.extend(
        (
            _section(
                level,
                "Writer instructions",
                source,
                source.writer_instructions,
            ),
            _section(
                level,
                "Decision rationale",
                source,
                source.decision_rationale,
            ),
        ),
    )
    return sections


def _final_decision(source: CodeReviewAssessment) -> str:
    if source.disposition is ReviewDisposition.CHANGES_REQUESTED:
        return (
            "Decision: changes-requested. The writer must address the concrete "
            "instructions and publish another review round. This advisory answer "
            "does not authorize a commit."
        )
    return (
        "Decision: commit-ready (advisory). The evidence floor is complete, but "
        "this recommendation does not authorize a commit; authority remains at "
        "the durable human gate."
    )


def _sections(source: CodeReviewAssessment, level: int) -> list[str]:
    if isinstance(source, EarlyRejectionAssessment):
        return _early_sections(source, level)
    return _assessment_sections(source, level)


def _answer_authored_content(source: CodeReviewAssessment) -> str:
    values = {
        "heading_label": _heading_label(source),
        "identity_fields": _identity_fields(source),
        "body_sections": "\n\n".join(_sections(source, 2)),
        "final_decision": _final_decision(source),
    }
    try:
        template = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        raise ReviewExchangeError(f"cannot read answer template: {error}") from error
    return template.substitute(values).rstrip() + "\n"


def _transcript_summary(source: CodeReviewAssessment) -> str:
    sections = _sections(source, 3)
    sections.append(
        _section(
            3,
            "Final reviewer decision",
            source,
            _final_decision(source),
        ),
    )
    return "\n\n".join(sections) + "\n"


def render_code_review_answer(source: CodeReviewAssessment) -> CodeReviewAnswerRender:
    """Render and validate one complete code answer and transcript pair."""
    context = source.context
    envelope = Envelope(
        identity=context.identity,
        umbrella_path=context.umbrella_path,
        document_path=context.document_path,
        implementation_step=context.implementation_step,
        role=ReviewRole.REVIEWER,
        round_number=source.round_number,
        created_at=source.created_at,
        disposition=source.disposition,
    )
    answer = render_envelope_markdown(envelope, _answer_authored_content(source))
    parsed, _authored = parse_envelope_markdown(answer)
    if parsed != envelope or _JSON_SECTION not in answer:
        raise ReviewExchangeError("rendered answer failed shared envelope validation")
    return CodeReviewAnswerRender(answer, _transcript_summary(source))


__all__ = [
    "CodeReviewAnswerRender",
    "EarlyRejectionAssessment",
    "ImplementationAssessment",
    "render_code_review_answer",
]


# eof
