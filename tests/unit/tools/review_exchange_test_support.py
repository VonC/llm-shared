"""Canonical context, role, artifact-home and ownership builders for review tests.

Public-launcher acceptance and existing in-process journeys share these values
without substituting protocol transitions, Git, or ownership checks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import (
    ExchangeIdentity,
    FamilyPolicy,
    ReviewContext,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_envelope import Envelope, render_envelope_markdown

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path


def review_context(root: Path, family: ReviewFamily, slug: str, *, step: str | None = None) -> ReviewContext:
    """Create one exact document and its accepted review context."""
    docs = root / "docs" / "v0.11.0"
    docs.mkdir(parents=True, exist_ok=True)
    prefix = "plan" if family is ReviewFamily.CODE else "feature-request"
    token = "code" if family is ReviewFamily.CODE else "feature-request"
    document = docs / f"{prefix}.v0.11.0.{slug}.md"
    document.write_text(f"# {slug}\n", encoding="utf-8")
    return ReviewContext(ExchangeIdentity(family, token, "v0.11.0", slug), document.resolve(), None, step)


def review_policy(context: ReviewContext) -> FamilyPolicy:
    """Keep both registered families' convergence labels in one builder."""
    if context.identity.family is ReviewFamily.CODE:
        return FamilyPolicy("commit-ready", "Rework and review again", "Commit")
    return FamilyPolicy("consolidation-ready", "Revise and review again", "Consolidate")


def common_arguments(context: ReviewContext) -> list[str]:
    """Carry every exact identity and policy field to each public command."""
    policy = review_policy(context)
    arguments = [
        "--family", context.identity.family.value, "--document", str(context.document_path),
        "--convergence-signal", policy.convergence_signal,
        "--another-round-label", policy.another_round_label,
        "--continue-owning-workflow-label", policy.continue_owning_workflow_label,
    ]
    if context.implementation_step is not None:
        arguments.extend(("--implementation-step", context.implementation_step))
    if context.umbrella_path is not None:
        arguments.extend(("--umbrella", str(context.umbrella_path)))
    return arguments


def review_summary(context: ReviewContext, round_number: int, *, guidance: str | None = None) -> str:
    """Render the mandatory human-readable identity for the current request."""
    umbrella = context.umbrella_path.as_posix() if context.umbrella_path else "none"
    lines = [f"Umbrella draft: {umbrella}"]
    if context.identity.family is ReviewFamily.CODE:
        lines.extend((f"Implementation plan: {context.document_path.as_posix()}",
                      f"Implementation step: {context.implementation_step}"))
    else:
        lines.append(f"Reviewed specification: {context.document_path.as_posix()}")
    lines.append(f"Review round: {round_number}")
    if guidance is not None:
        lines.extend(("", f"Human guidance: {guidance}"))
    return "\n".join(lines) + "\n"


def review_artifact(
    context: ReviewContext, role: ReviewRole, round_number: int, *,
    disposition: ReviewDisposition | None = None, guidance: str | None = None,
) -> str:
    """Render complete exchange content while production supplies host evidence."""
    envelope = Envelope(context.identity, context.umbrella_path, context.document_path,
                        context.implementation_step, role, round_number,
                        "2026-08-05T09:00:00+02:00", disposition)
    authored = review_summary(context, round_number, guidance=guidance) if role is ReviewRole.REQUESTOR else "Reviewer feedback for the acceptance journey.\n"
    return render_envelope_markdown(envelope, authored)


def configured_home(root: Path, relative_home: str = ".reviews") -> Path:
    """Declare one home and create its effective ignore coverage before evidence."""
    if relative_home != ".reviews":
        (root / ".review-artifacts.ini").write_text(
            f"[review-artifacts]\nhome = {relative_home}\n", encoding="utf-8",
        )
    configuration = ReviewArtifactConfiguration.load(root)
    configuration.prepare_home()
    return configuration.home


def capability_arguments(payload: Mapping[str, Any]) -> list[str]:
    """Carry session-only capabilities without inventing or persisting a token."""
    return ["--ownership-generation", str(payload["ownership_generation"]),
            "--ownership-token", str(payload["ownership_token"])]


def session_environment(environment: Mapping[str, str], nature: str) -> dict[str, str]:
    """Isolate simulated hosts from both outer host signals and caller roots."""
    result = {key: value for key, value in environment.items()
              if key not in {"CLAUDECODE", "CODEX_THREAD_ID", "PRJ_DIR", "LLM_SHARED_DIR"}}
    variable = {"claude": "CLAUDECODE", "codex": "CODEX_THREAD_ID"}.get(nature)
    if variable:
        result[variable] = "acceptance-host-sentinel"
    return result


# eof
