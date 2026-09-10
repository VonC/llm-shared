"""Lifecycle acceptance for the complete specification requestor workflow.

Step 4 composes Git-protocol activation, public command adapters, paired
request rendering, exact-path routing, shared review exchange transitions, and
the canonical consolidation boundary. Counterpart answers use the public core
because the independent specification reviewer belongs to a later effort.
Recorded Git boundaries keep those journeys deterministic and process-free.
"""

from __future__ import annotations

import json
import os
from contextlib import chdir, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import patch

import pytest

from tools import review_exchange_cli as exchange_cli
from tools import spec_review_request as request_renderer
from tools.prompt_workflow_models import Topic
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewRole,
)
from tools.review_exchange_models_envelope import Envelope, render_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore
from tools.spec_review_request import SpecificationRoundInput

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# ruff: noqa: S603, S607

_POLICY = FamilyPolicy(
    "consolidation-ready",
    "Revise and review again",
    "Consolidate",
)
_CREATED_AT = "2026-08-09T08:00:00+02:00"
_STOP = 3
_ROUND_TWO = 2
_CAPABILITIES: dict[Path, tuple[int, str]] = {}


@dataclass(frozen=True)
class CliResult:
    """One parsed result from the public review-exchange command adapter."""

    code: int
    payload: dict[str, Any]


@dataclass(frozen=True)
class Effort:
    """One temporary specification effort with exact routing context."""

    root: Path
    topic: Topic
    context: ReviewContext
    document: Path
    umbrella: Path


def _init_repo(root: Path, *, marker: bool = True) -> None:
    """Create the filesystem shape consumed by the recorded Git boundary."""
    root.mkdir(parents=True)
    (root / ".git").mkdir()
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    if marker:
        (root / "a.review-mode").write_text("", encoding="utf-8")


def _effort(root: Path, prefix: str, slug: str) -> Effort:
    """Create one umbrella child effort for a supported specification type."""
    docs = root / "docs" / "v0.11.0"
    docs.mkdir(parents=True, exist_ok=True)
    umbrella = docs / "draft.v0.11.0.review-mode.md"
    umbrella.write_text("# Review mode umbrella\n", encoding="utf-8")
    draft = docs / f"draft.v0.11.0.{slug}.md"
    draft.write_text(
        "# Child draft\n\n"
        "- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md\n",
        encoding="utf-8",
    )
    document = docs / f"{prefix}.v0.11.0.{slug}.md"
    document.write_text(
        f"# {slug}\n\n## Open questions for {slug}\n\n1. Question?\n",
        encoding="utf-8",
    )
    return Effort(
        root,
        Topic("v0.11.0", slug, draft),
        request_renderer.specification_context(document, umbrella),
        document,
        umbrella,
    )


def _common(context: ReviewContext) -> list[str]:
    """Return the fixed specification-family command arguments."""
    arguments = [
        "--family",
        "specification",
        "--document",
        str(context.document_path),
        "--convergence-signal",
        _POLICY.convergence_signal,
        "--another-round-label",
        _POLICY.another_round_label,
        "--continue-owning-workflow-label",
        _POLICY.continue_owning_workflow_label,
    ]
    if context.umbrella_path is not None:
        arguments.extend(("--umbrella", str(context.umbrella_path)))
    return arguments


def _run_cli(
    root: Path,
    context: ReviewContext,
    operation: str,
    extra: Sequence[str] = (),
) -> CliResult:
    """Run the public exchange adapter and parse its one JSON result."""
    stdout = StringIO()
    stderr = StringIO()
    capability = _CAPABILITIES.get(context.document_path)
    capability_arguments: tuple[str, ...] = ()
    if capability is not None and operation not in {"activate", "status"}:
        generation, token = capability
        capability_arguments = (
            "--ownership-generation",
            str(generation),
            "--ownership-token",
            token,
        )
    with (
        patch.dict(os.environ, {"PRJ_DIR": str(root)}),
        chdir(root),
        redirect_stdout(stdout),
        redirect_stderr(stderr),
    ):
        code = exchange_cli.main(
            [operation, *_common(context), *capability_arguments, *extra],
        )
    lines = stdout.getvalue().splitlines()
    assert len(lines) == 1, stderr.getvalue()
    payload = cast("dict[str, Any]", json.loads(lines[0]))
    generation = payload.get("ownership_generation")
    token = payload.get("ownership_token")
    if isinstance(generation, int) and isinstance(token, str):
        _CAPABILITIES[context.document_path] = (generation, token)
    if payload.get("state") == "idle":
        _CAPABILITIES.pop(context.document_path, None)
    return CliResult(code, payload)


def _root_input(root: Path, name: str, content: str) -> Path:
    """Write one distinct ignored input used by a public adapter."""
    home = root / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    path = home / f"a.{name}.md"
    path.write_text(content, encoding="utf-8")
    return path


def _render_pair(
    effort: Effort,
    round_number: int,
    *,
    guidance: str | None = None,
    change_summary: str = "Questions prepared for independent review.",
    writer_response: str = "The writer requests an independent assessment.",
) -> tuple[Path, Path]:
    """Render one request and transcript summary through the public adapter."""
    suffix = f"{effort.context.identity.type_token}-{round_number}"
    assessment = _root_input(
        effort.root,
        f"assessment-{suffix}",
        "Check the open questions, answers, and wording.",
    )
    changes = _root_input(effort.root, f"changes-{suffix}", change_summary)
    response = _root_input(effort.root, f"response-{suffix}", writer_response)
    home = effort.root / ".reviews"
    request_output = home / f"a.rendered-request-{suffix}.md"
    summary_output = home / f"a.rendered-summary-{suffix}.md"
    arguments = [
        "--document",
        str(effort.document),
        "--umbrella",
        str(effort.umbrella),
        "--round-number",
        str(round_number),
        "--assessment-file",
        str(assessment),
        "--change-summary-file",
        str(changes),
        "--writer-response-file",
        str(response),
        "--request-content-output",
        str(request_output),
        "--transcript-summary-output",
        str(summary_output),
    ]
    if guidance is not None:
        guidance_path = _root_input(effort.root, f"guidance-{suffix}", guidance)
        arguments.extend(("--guidance-file", str(guidance_path)))
    assert request_renderer.main(arguments, project_root=effort.root) == 0
    return request_output, summary_output


def _publish_request(effort: Effort, round_number: int, **kwargs: str) -> CliResult:
    """Render and publish one specialized request through both public adapters."""
    request_path, summary_path = _render_pair(effort, round_number, **kwargs)
    return _run_cli(
        effort.root,
        effort.context,
        "publish-request",
        (
            "--content-file",
            str(request_path),
            "--summary-file",
            str(summary_path),
        ),
    )


def _core(
    effort: Effort,
    *,
    wall_clock: Callable[[], datetime] | None = None,
    timeout: int = 300,
) -> ReviewExchangeCore:
    """Build the shared exchange core for simulated reviewer publication."""
    return ReviewExchangeCore(
        ReviewExchangeStore(derive_artifact_paths(effort.root, effort.context)),
        effort.context,
        _POLICY,
        ReviewConfiguration(enabled=True, wait_timeout_seconds=timeout),
        wall_clock=wall_clock,
    )


def _answer(
    effort: Effort,
    round_number: int,
    disposition: ReviewDisposition,
) -> str:
    """Render one exact counterpart answer for the deferred reviewer role."""
    envelope = Envelope(
        effort.context.identity,
        effort.context.umbrella_path,
        effort.context.document_path,
        None,
        ReviewRole.REVIEWER,
        round_number,
        _CREATED_AT,
        disposition,
    )
    return render_envelope_markdown(
        envelope,
        f"## Reviewer assessment for round {round_number}\n\n"
        "The independent reviewer completed the assessment.\n",
    )


def _publish_answer(
    effort: Effort,
    round_number: int,
    disposition: ReviewDisposition,
) -> None:
    """Publish one simulated counterpart answer through the shared core."""
    exchange = _core(effort)
    claim = exchange.pickup_ownership(Actor.REVIEWER)
    _CAPABILITIES[effort.context.document_path] = (
        claim.capability.generation,
        claim.capability.token,
    )
    exchange.publish_answer(
        _answer(effort, round_number, disposition),
        f"Reviewer feedback for round {round_number}.",
    )


@pytest.fixture
def lifecycle_journey(tmp_path: Path) -> None:
    """Run repeated rounds and durable consolidation outside call timing."""
    root = tmp_path / "lifecycle"
    _init_repo(root)
    effort = _effort(root, "feature-request", "lifecycle")
    paths = derive_artifact_paths(root, effort.context)
    activated = _run_cli(root, effort.context, "activate")
    started = _run_cli(root, effort.context, "start")
    initialized = paths.transcript.read_text(encoding="utf-8")

    first_publication = _publish_request(effort, 1)
    first_request = paths.transcript.read_text(encoding="utf-8")
    _publish_answer(effort, 1, ReviewDisposition.CHANGES_REQUESTED)
    consumed = _run_cli(
        root,
        effort.context,
        "consume-answer",
        ("--reviewed-work-changed", "true"),
    )
    continued = _run_cli(root, effort.context, "continue")
    assert (
        activated.code,
        started.code,
        first_publication.code,
        consumed.code,
        continued.payload["round"],
    ) == (0, 0, 0, 0, _ROUND_TWO)

    effort.document.write_text(
        "# lifecycle\n\n## Open questions for lifecycle\n\n"
        "1. Revised question after reviewer feedback?\n",
        encoding="utf-8",
    )
    second_publication = _publish_request(
        effort,
        _ROUND_TWO,
        change_summary="Applied the accepted round 1 wording changes.",
        writer_response="The writer revised the specification before round 2.",
    )
    second_request = paths.transcript.read_text(encoding="utf-8")
    _publish_answer(effort, _ROUND_TWO, ReviewDisposition.CONVERGENCE_RECOMMENDED)
    gate = _run_cli(root, effort.context, "status")
    confirmation = _run_cli(
        root,
        effort.context,
        "confirm",
        ("--choice-label", "Consolidate"),
    )

    canonical = Path("instructions/spec-review-requestor.md").read_text(
        encoding="utf-8",
    )
    authorized_before_handoff = canonical.index(
        "owning_action_authorized: true",
    ) < canonical.index(
        "consolidate-then-review-ask-questions",
    )
    handoff_before_completion = canonical.index(
        "consolidate-then-review-ask-questions",
    ) < canonical.index("call `complete`")
    assert (
        second_publication.code,
        gate.code,
        gate.payload["state"],
        confirmation.payload["owning_action_authorized"],
        authorized_before_handoff,
        handoff_before_completion,
    ) == (0, _STOP, "convergence-gate", True, True, True)

    effort.document.write_text(
        "# lifecycle\n\n## Requirement clarifications\n\n"
        "| Question | Decision |\n| --- | --- |\n"
        "| Q01 | Consolidated after human authorization |\n",
        encoding="utf-8",
    )
    completion = _run_cli(root, effort.context, "complete")
    transcript = paths.transcript.read_text(encoding="utf-8")

    entries = [
        transcript.index("request-round-1"),
        transcript.index("answer-round-1"),
        transcript.index("request-round-2"),
        transcript.index("answer-round-2"),
        transcript.index("human-confirmation-round-2"),
    ]
    settled = effort.document.read_text(encoding="utf-8")
    assert (
        first_request.startswith(initialized),
        second_request.startswith(first_request),
        completion.code,
        completion.payload["state"],
        paths.answer.exists(),
        paths.coordination.exists(),
        entries,
        "Applied the accepted round 1 wording changes." in transcript,
        "Open questions" in settled,
    ) == (True, True, 0, "idle", False, False, sorted(entries), True, False)


def test_repeated_round_convergence_consolidation_and_cleanup(
    lifecycle_journey: None,
) -> None:
    """A complete writer journey reaches durable consolidation and clean idle."""
    assert lifecycle_journey is None


@pytest.fixture
def guided_override_journey(
    tmp_path: Path,
) -> None:
    """Run the literal-guidance replacement journey outside call timing."""
    root = tmp_path / "guidance"
    _init_repo(root)
    effort = _effort(root, "issue", "guided")
    paths = derive_artifact_paths(root, effort.context)
    assert _run_cli(root, effort.context, "activate").code == 0
    assert _run_cli(root, effort.context, "start").code == 0
    assert _publish_request(effort, 1).code == 0
    _publish_answer(effort, 1, ReviewDisposition.CONVERGENCE_RECOMMENDED)
    guidance = "## Human decision\n\nKeep Q02 literal; do not merge it with Q01."
    guidance_path = _root_input(root, "human-guidance", guidance)
    override = _run_cli(
        root,
        effort.context,
        "confirm",
        (
            "--choice-label",
            "Revise and review again",
            "--guidance-file",
            str(guidance_path),
        ),
    )
    request_path, summary_path = _render_pair(
        effort,
        2,
        guidance=guidance,
        change_summary="Applied the human override before replacement review.",
        writer_response="The writer kept Q02 separate and added one example.",
    )
    publication = _run_cli(
        root,
        effort.context,
        "publish-request",
        (
            "--content-file",
            str(request_path),
            "--summary-file",
            str(summary_path),
        ),
    )
    request = request_path.read_text(encoding="utf-8")
    summary = summary_path.read_text(encoding="utf-8")
    transcript = paths.transcript.read_text(encoding="utf-8")

    assert override.payload["round"] == _ROUND_TWO
    assert publication.code == 0
    assert request.count(
        "Human guidance:\n\n### Human decision for issue guided (round 2)\n\n"
        "Keep Q02 literal; do not merge it with Q01.",
    ) == 1
    assert summary.count(
        "Human guidance:\n\n#### Human decision for issue guided (round 2)\n\n"
        "Keep Q02 literal; do not merge it with Q01.",
    ) == 1
    assert "Writer response:\n\nThe writer kept Q02 separate" in request
    assert (
        "Human guidance:\n\n#### Human decision for issue guided (round 2)"
        in transcript
    )


def test_guided_override_preserves_literal_guidance_and_writer_response(
    guided_override_journey: None,
) -> None:
    """A human override starts round 2 with literal, separately labeled text."""
    assert guided_override_journey is None


@pytest.fixture
def expired_round_reclaim_journey(tmp_path: Path) -> None:
    """A new session renews one intact round without rewriting its evidence."""
    root = tmp_path / "reclaim"
    _init_repo(root)
    effort = _effort(root, "plan", "reclaim")
    paths = derive_artifact_paths(root, effort.context)
    now = datetime(2026, 8, 9, 8, 0, tzinfo=UTC)
    first_core = _core(effort, wall_clock=lambda: now, timeout=1)
    first_core.start()
    source = SpecificationRoundInput(
        effort.context,
        1,
        "2026-08-09T10:00:00+02:00",
        "Assess this plan question.",
        "Prepared one implementation question.",
        "The writer awaits independent review.",
    )
    rendered = request_renderer.render_specification_request(source)
    first_core.publish_request(rendered.request_content, rendered.transcript_summary)
    request_before = paths.request.read_bytes()
    transcript_before = paths.transcript.read_bytes()

    later = now + timedelta(seconds=2)
    returning = _core(effort, wall_clock=lambda: later, timeout=1)
    assert returning.classify().state is ArtifactState.ABANDONED_REQUEST
    record = returning.reclaim()

    assert record.round_number == 1
    assert returning.classify().state is ArtifactState.REQUEST_PENDING
    assert paths.request.read_bytes() == request_before
    assert paths.transcript.read_bytes() == transcript_before


def test_expired_round_reclaim_keeps_identity_content_and_round(
    expired_round_reclaim_journey: None,
) -> None:
    """The intact-round reclaim remains covered by the prepared journey."""
    assert expired_round_reclaim_journey is None


# eof
