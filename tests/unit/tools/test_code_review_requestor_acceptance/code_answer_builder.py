"""Test-local builder for valid deferred code-reviewer answers.

Step 4 needs executable requestor journeys before the independent reviewer
renderer exists. This module freezes the shared code-family envelope and keeps
scenario-specific disposition, repaired paths, and recommendation in authored
Markdown without bypassing exchange validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.review_exchange_models import (
    ReviewContext,
    ReviewDisposition,
    ReviewRole,
)
from tools.review_exchange_models_envelope import Envelope, render_envelope_markdown

if TYPE_CHECKING:
    from collections.abc import Sequence

_CREATED_AT = "2026-08-13T20:00:00+02:00"


@dataclass(frozen=True)
class CodeAnswer:
    """One complete answer plus its substantive transcript summary."""

    content: str
    summary: str


def build_code_answer(
    context: ReviewContext,
    round_number: int,
    disposition: ReviewDisposition,
    *,
    repaired_paths: Sequence[str] = (),
    recommendation: str,
) -> CodeAnswer:
    """Build one strict code answer for the exact plan, step, and round."""
    repaired = (
        "None."
        if not repaired_paths
        else "\n".join(f"- `{path}`" for path in repaired_paths)
    )
    body = (
        f"## Code review assessment for step {context.implementation_step}\n\n"
        f"Implementation plan: {context.document_path.as_posix()}\n"
        f"Implementation step: {context.implementation_step}\n"
        f"Review round: {round_number}\n\n"
        "## Repaired paths\n\n"
        f"{repaired}\n\n"
        "## Reviewer recommendation\n\n"
        f"{recommendation}\n"
    )
    envelope = Envelope(
        context.identity,
        context.umbrella_path,
        context.document_path,
        context.implementation_step,
        ReviewRole.REVIEWER,
        round_number,
        _CREATED_AT,
        disposition,
    )
    summary = (
        f"Step {context.implementation_step} round {round_number}: "
        f"{recommendation}\nRepaired paths:\n{repaired}\n"
    )
    return CodeAnswer(render_envelope_markdown(envelope, body), summary)


# eof
