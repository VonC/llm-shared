"""Pure schema-2 renderers for migration and role-nature review status."""

from __future__ import annotations

import json

from tools.review_status_models import (
    ArtifactApplicability,
    ArtifactKind,
    DamagedCandidateStatus,
    ExchangeStatus,
    ReviewStatusResult,
    RoleNatureStatus,
)


def _presence(
    applicability: ArtifactApplicability,
    *,
    present: bool,
) -> str:
    """Return the concise human artifact state without hiding either fact."""
    if applicability is ArtifactApplicability.EXPECTED:
        observed = "present" if present else "missing"
    else:
        observed = "present" if present else "absent"
    return f"{applicability.value}, {observed}"


def _nature_evidence(status: RoleNatureStatus) -> str:
    """Render complete typed nature evidence without inferring missing values."""
    if not status.evidence:
        return "none"
    return ", ".join(
        f"{item.path}={item.nature.value if item.nature is not None else 'unrecorded'}"
        for item in status.evidence
    )


def _exchange_lines(position: int, exchange: ExchangeStatus) -> list[str]:
    """Render one complete trustworthy exchange as a stable labelled block."""
    identity = exchange.identity
    lease = exchange.lease
    lines = [
        f"Exchange {position}:",
        f"  Family: {identity.family.value}",
        f"  Type: {identity.type_token}",
        f"  Version: {identity.version}",
        f"  Slug: {identity.slug}",
        f"  Reviewed document: {exchange.reviewed_document}",
        f"  Umbrella: {exchange.umbrella or 'none'}",
        f"  Implementation step: {exchange.implementation_step or 'none'}",
        f"  Round: {exchange.round_number}",
        f"  Occurrence: {exchange.occurrence}",
        f"  State: {exchange.state.value}",
        f"  Role: {exchange.continuing_role.value}",
        f"  Specialization: {exchange.specialization.value}",
        f"  Owner: {exchange.owner.value}",
        f"  Requestor LLM nature: {exchange.requestor_llm_nature.value.value}",
        "  Requestor LLM nature evidence: "
        f"{_nature_evidence(exchange.requestor_llm_nature)}",
        f"  Reviewer LLM nature: {exchange.reviewer_llm_nature.value.value}",
        "  Reviewer LLM nature evidence: "
        f"{_nature_evidence(exchange.reviewer_llm_nature)}",
        f"  Lease: {lease.freshness.value}",
        f"  Lease renewed at: {lease.renewed_at or 'none'}",
        f"  Lease expires at: {lease.expires_at or 'none'}",
        f"  Lease evaluated at: {lease.evaluated_at}",
        f"  Lease timeout seconds: {lease.timeout_seconds}",
    ]
    lines.extend(
        (
            f"  Artifact {kind.value}: "
            f"{_presence(exchange.artifacts[kind].applicability, present=exchange.artifacts[kind].present)}; "
            f"{exchange.artifacts[kind].path}"
        )
        for kind in ArtifactKind
    )
    lines.extend(
        (
            f"  Next action: {exchange.next_action.value}",
            f"  Next action detail: {exchange.next_action_text}",
            f"  Diagnostic: {exchange.diagnostic}",
        ),
    )
    return lines


def _damaged_lines(
    position: int,
    candidate: DamagedCandidateStatus,
) -> list[str]:
    """Render only identity evidence that a damaged candidate can support."""
    identity = (
        candidate.candidate_identity.key
        if candidate.candidate_identity is not None
        else "unknown"
    )
    return [
        f"Damaged candidate {position}:",
        f"  Candidate: {candidate.candidate_path}",
        f"  Identity: {identity}",
        f"  Diagnostic: {candidate.diagnostic}",
    ]


def render_human(result: ReviewStatusResult) -> str:
    """Render one deterministic human report without crossing an IO boundary."""
    lines = [
        f"Repository: {result.repository_root}",
        f"Outcome: {result.outcome.value}",
        f"Migration: {result.migration.state.value}",
        f"Artifact home: {result.migration.artifact_home}",
        f"Migrated artifacts: {result.migration.moved_count}",
        "Migration diagnostics: "
        f"{'; '.join(result.migration.diagnostics) if result.migration.diagnostics else 'none'}",
        f"Active exchanges: {result.active_count}",
        f"Errors: {'yes' if result.has_errors else 'no'}",
    ]
    for position, entry in enumerate(result.exchanges, start=1):
        lines.append("")
        if isinstance(entry, ExchangeStatus):
            lines.extend(_exchange_lines(position, entry))
        else:
            lines.extend(_damaged_lines(position, entry))
    return "\n".join(lines)


def render_json(result: ReviewStatusResult) -> str:
    """Render the typed schema as deterministic compact Unicode JSON."""
    return json.dumps(
        result.to_dict(),
        ensure_ascii=False,
        separators=(",", ":"),
    )


__all__ = ["render_human", "render_json"]


# eof
