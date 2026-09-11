"""Shared real-file fixtures for specification reviewer acceptance tests."""

from __future__ import annotations

import hashlib
import json
import os
from contextlib import chdir, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from io import StringIO
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import patch

from tools import review_exchange_cli, spec_review_answer_cli, spec_review_request
from tools.prompt_workflow_models import Topic
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from datetime import datetime
    from pathlib import Path

POLICY = FamilyPolicy("consolidation-ready", "Revise and review again", "Consolidate")
TIMESTAMP = "2026-08-11T14:00:00+02:00"
_CAPABILITIES: dict[Path, tuple[int, str]] = {}


@dataclass(frozen=True)
class CliResult:
    """One parsed result from the public review-exchange CLI."""

    code: int
    payload: dict[str, Any]


@dataclass(frozen=True)
class Effort:
    """One exact specification effort in a temporary repository."""

    root: Path
    topic: Topic
    context: ReviewContext
    document: Path
    umbrella: Path


def init_repo(root: Path, *, marker: bool = True) -> None:
    """Create the filesystem shape consumed by the recorded Git boundary."""
    root.mkdir(parents=True)
    (root / ".git").mkdir()
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    if marker:
        (root / "a.review-mode").write_text("", encoding="utf-8")


def make_effort(
    root: Path,
    prefix: str,
    slug: str,
    *,
    marker: bool = True,
    initialize_git: bool = True,
) -> Effort:
    """Create one supported specification effort, optionally without Git setup."""
    if initialize_git:
        init_repo(root, marker=marker)
    else:
        root.mkdir(parents=True)
        if marker:
            (root / "a.review-mode").write_text("", encoding="utf-8")
    docs = root / "docs" / "v0.11.0"
    docs.mkdir(parents=True)
    umbrella = docs / "draft.v0.11.0.review-mode.md"
    umbrella.write_text("# Review mode umbrella\n", encoding="utf-8")
    draft = docs / f"draft.v0.11.0.{slug}.md"
    draft.write_text(
        "# Child draft\n\n- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md\n",
        encoding="utf-8",
    )
    document = docs / f"{prefix}.v0.11.0.{slug}.md"
    document.write_text(
        f"# {slug}\n\n## Open questions for {slug}\n\n1. Which option?\n",
        encoding="utf-8",
    )
    return Effort(
        root=root,
        topic=Topic("v0.11.0", slug, draft),
        context=spec_review_request.specification_context(document, umbrella),
        document=document,
        umbrella=umbrella,
    )


def common(context: ReviewContext) -> list[str]:
    """Return exact specification exchange identity and policy arguments."""
    args = [
        "--family",
        "specification",
        "--document",
        str(context.document_path),
        "--convergence-signal",
        POLICY.convergence_signal,
        "--another-round-label",
        POLICY.another_round_label,
        "--continue-owning-workflow-label",
        POLICY.continue_owning_workflow_label,
    ]
    if context.umbrella_path is not None:
        args.extend(("--umbrella", str(context.umbrella_path)))
    return args


def run_exchange(
    effort: Effort,
    operation: str,
    extra: Sequence[str] = (),
) -> CliResult:
    """Invoke the public exchange command and parse its sole JSON result."""
    stdout, stderr = StringIO(), StringIO()
    capability = _CAPABILITIES.get(effort.context.document_path)
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
        chdir(effort.root),
        redirect_stdout(stdout),
        redirect_stderr(stderr),
        patch.dict(os.environ, {"PRJ_DIR": str(effort.root)}),
    ):
        code = review_exchange_cli.main(
            [operation, *common(effort.context), *capability_arguments, *extra],
        )
    lines = stdout.getvalue().splitlines()
    assert len(lines) == 1, stderr.getvalue()
    payload = cast("dict[str, Any]", json.loads(lines[0]))
    generation = payload.get("ownership_generation")
    token = payload.get("ownership_token")
    if isinstance(generation, int) and isinstance(token, str):
        _CAPABILITIES[effort.context.document_path] = (generation, token)
    if payload.get("state") == "idle":
        _CAPABILITIES.pop(effort.context.document_path, None)
    return CliResult(code, payload)


def input_file(effort: Effort, name: str, content: str) -> Path:
    """Write one exact ignored reviewer-authored input."""
    home = effort.root / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    path = home / f"a.{name}.md"
    path.write_text(content, encoding="utf-8")
    return path


def render_request(effort: Effort, *, guidance: str | None = None) -> tuple[Path, Path]:
    """Render one exact round-one request and transcript summary."""
    assessment = input_file(effort, "request-assessment", "Review every open question.")
    changes = input_file(effort, "request-changes", "Initial independent review.")
    response = input_file(effort, "writer-response", "Please assess the specification.")
    home = effort.root / ".reviews"
    output = home / "a.rendered-request.md"
    summary = home / "a.rendered-request-summary.md"
    args = [
        "--document",
        str(effort.document),
        "--umbrella",
        str(effort.umbrella),
        "--round-number",
        "1",
        "--assessment-file",
        str(assessment),
        "--change-summary-file",
        str(changes),
        "--writer-response-file",
        str(response),
        "--request-content-output",
        str(output),
        "--transcript-summary-output",
        str(summary),
    ]
    if guidance is not None:
        guidance_path = input_file(effort, "human-guidance", guidance)
        args.extend(("--guidance-file", str(guidance_path)))
    assert spec_review_request.main(args, project_root=effort.root) == 0
    return output, summary


def publish_request(effort: Effort, *, guidance: str | None = None) -> CliResult:
    """Start and publish one request through public command boundaries."""
    assert run_exchange(effort, "activate").code == 0
    assert run_exchange(effort, "start").code == 0
    content, summary = render_request(effort, guidance=guidance)
    return run_exchange(
        effort,
        "publish-request",
        ("--content-file", str(content), "--summary-file", str(summary)),
    )


def render_answer(
    effort: Effort,
    disposition: ReviewDisposition,
    *,
    guidance: bool = False,
    manifest: Path | None = None,
) -> tuple[Path, Path]:
    """Render paired reviewer output through the fixed-path public CLI."""
    authored = {
        "assessment": input_file(
            effort,
            "reviewer-assessment",
            "The wording was checked.",
        ),
        "question-verdicts": input_file(effort, "question-verdicts", "Q01: option A."),
        "writer-instructions": input_file(
            effort,
            "writer-instructions",
            "Apply the verdict.",
        ),
    }
    home = effort.root / ".reviews"
    answer = home / "a.rendered-answer.md"
    summary = home / "a.rendered-answer-summary.md"
    args = [
        "--document",
        str(effort.document),
        "--umbrella",
        str(effort.umbrella),
        "--round-number",
        "1",
        "--disposition",
        disposition.value,
        "--expected-document-sha256",
        hashlib.sha256(effort.document.read_bytes()).hexdigest(),
    ]
    for name, path in authored.items():
        args.extend((f"--{name.replace('_', '-')}-file", str(path)))
    if disposition is ReviewDisposition.CHANGES_REQUESTED:
        path = input_file(effort, "requested-changes", "Clarify the recovery owner.")
        args.extend(("--requested-changes-file", str(path)))
    else:
        covered = input_file(
            effort,
            "covered-wording",
            "All open questions are settled.",
        )
        rationale = input_file(
            effort,
            "convergence-rationale",
            "The specification is complete.",
        )
        args.extend(("--covered-wording-file", str(covered)))
        args.extend(("--convergence-rationale-file", str(rationale)))
    if guidance:
        source = input_file(effort, "answer-guidance", "Keep Q01 settled.")
        response = input_file(effort, "guidance-response", "Q01 remains settled.")
        args.extend(
            ("--guidance-file", str(source), "--guidance-response-file", str(response)),
        )
    if manifest is not None:
        args.extend(("--retained-manifest-file", str(manifest)))
    args.extend(
        (
            "--answer-content-output",
            str(answer),
            "--transcript-summary-output",
            str(summary),
        ),
    )
    assert spec_review_answer_cli.main(args, project_root=effort.root) == 0
    return answer, summary


def publish_answer(
    effort: Effort,
    disposition: ReviewDisposition,
    *,
    guidance: bool = False,
) -> CliResult:
    """Render and publish one paired answer through public adapters."""
    content, summary = render_answer(effort, disposition, guidance=guidance)
    return run_exchange(
        effort,
        "publish-answer",
        ("--content-file", str(content), "--summary-file", str(summary)),
    )


def core(
    effort: Effort,
    *,
    wall_clock: Callable[[], datetime] | None = None,
    timeout: int = 300,
) -> ReviewExchangeCore:
    """Construct a public core over the effort's durable exact paths."""
    return ReviewExchangeCore(
        ReviewExchangeStore(derive_artifact_paths(effort.root, effort.context)),
        effort.context,
        POLICY,
        ReviewConfiguration(enabled=True, wait_timeout_seconds=timeout),
        wall_clock=wall_clock,
    )
