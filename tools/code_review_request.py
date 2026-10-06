#!/usr/bin/env python3
"""Render checked implementation code-review artifacts from one round input.

Step 3 binds one ready commit-plan result to a stable request index tree before
the command writes either artifact. Pure rendering keeps the shared exchange
envelope and both evidence projections on one frozen source of truth.
Step 6 binds the resolved effort capture and effective proof to that evidence.
Validation commands stay literal in transcript Markdown, including backticks.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import argparse
import contextlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, NoReturn

# bin\code_review_request.bat runs this file by path, so sys.path[0] is the
# tools directory and the `tools.` package below is not importable from it.
# Bootstrap the repository root the way new_draft.py does, or the launcher
# fails with "No module named 'tools'" from every project.
if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools import code_review_request_files as files
from tools import code_review_request_scope as scopes
from tools._models import find_project_root
from tools.code_review_evidence import capture_index_tree
from tools.code_review_validation import (
    ResolvedValidationSet,
    complete_project_default,
    group_claim_statement,
    load_project_validation,
    migration_notice,
    resolve_code_review_validation,
)
from tools.commit_plan_check import (
    CommitPlanCheckResult,
    CommitPlanCheckState,
    check_commit_plan,
    render_human,
)
from tools.effort_scope import EffortScopeError
from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    format_local_timestamp,
    validate_local_timestamp,
)
from tools.review_exchange_models_envelope import (
    Envelope,
    parse_envelope_markdown,
    render_envelope_markdown,
)
from tools.review_markdown_headings import qualify_round_headings
from tools.scope_capture import CaptureError, write_capture

if TYPE_CHECKING:
    from collections.abc import Sequence

_PLAN_RE = re.compile(r"^plan\.(v\d+\.\d+\.\d+)\.([a-z0-9][a-z0-9_-]*)\.md$")
_TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / (
    "code-review-request.template.md"
)
_JSON_SECTION = "## JSON"
_TREE_OBJECT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_FATAL_EXIT = 2


def _validate_authored_inputs(authored: dict[str, str]) -> None:
    """Reject blank authored fields with their stable public labels."""
    for label, value in authored.items():
        if not value.strip():
            raise ReviewExchangeError(f"{label} must be non-empty")


def _validate_request_evidence(
    request_index_tree: str,
    resolved_validation_set: ResolvedValidationSet,
    commit_plan_result: CommitPlanCheckResult,
) -> None:
    """Reject malformed or non-ready typed request evidence."""
    if _TREE_OBJECT_RE.fullmatch(request_index_tree) is None:
        raise ReviewExchangeError("request index tree must be a Git tree object")
    if resolved_validation_set.__class__ is not ResolvedValidationSet:
        raise ReviewExchangeError("resolved validation set must be typed")
    if commit_plan_result.__class__ is not CommitPlanCheckResult:
        raise ReviewExchangeError("commit plan result must be typed")
    if not commit_plan_result.ready:
        raise ReviewExchangeError("commit plan result must be ready")


@dataclass(frozen=True)
class CodeReviewRoundInput:
    """Validated round inputs with optional scope for legacy direct callers."""

    context: ReviewContext
    round_number: int
    created_at: str
    assessment: str
    implementation_report: str
    change_summary: str
    writer_response: str
    request_index_tree: str
    resolved_validation_set: ResolvedValidationSet
    commit_plan_result: CommitPlanCheckResult
    human_guidance: str | None = None
    project_root: Path | None = None
    test_scope: dict[str, str | None] | None = None
    validation_scope: str = "Scope evidence is missing."

    def __post_init__(self) -> None:
        """Reject invalid identity, round, timestamp, or authored content."""
        if self.context.identity.family is not ReviewFamily.CODE:
            raise ReviewExchangeError("renderer requires a code review context")
        if self.round_number <= 0:
            raise ReviewExchangeError("round must be positive")
        validate_local_timestamp(self.created_at)
        authored = {
            "assessment": self.assessment,
            "implementation report": self.implementation_report,
            "change summary": self.change_summary,
            "writer response": self.writer_response,
        }
        _validate_authored_inputs(authored)
        _validate_request_evidence(
            self.request_index_tree,
            self.resolved_validation_set,
            self.commit_plan_result,
        )
        if self.human_guidance is not None and not self.human_guidance.strip():
            raise ReviewExchangeError("human guidance must be non-empty when supplied")


@dataclass(frozen=True)
class CodeReviewRequestRender:
    """Complete implementation request and paired substantive summary."""

    request_content: str
    transcript_summary: str

    def __post_init__(self) -> None:
        """Reject an incomplete paired rendering result."""
        if not self.request_content or not self.transcript_summary:
            raise ReviewExchangeError("paired request rendering must be non-empty")


@dataclass(frozen=True)
class _CodeReviewEvidence:
    """One source for JSON, scope and evidence with Markdown-safe commands."""

    request_index_tree: str
    resolved_validation_set: ResolvedValidationSet
    commit_plan_result: CommitPlanCheckResult
    test_scope: dict[str, str | None] | None = None

    def to_payload(self) -> dict[str, object]:
        """Return the canonical authored JSON object."""
        return {
            "commit_plan_result": self.commit_plan_result.structured_payload(),
            "request_index_tree": self.request_index_tree,
            "resolved_validation_set": self.resolved_validation_set.to_payload(),
            **({"test_scope": self.test_scope} if self.test_scope is not None else {}),
        }

    def summary(self) -> str:
        """Return the paired human-readable representation."""
        lines = [
            f"request_index_tree: {self.request_index_tree}",
            "resolved_validation_set:",
            "",
        ]
        for entry in self.resolved_validation_set.commands:
            sources = ", ".join(entry.sources)
            lines.append(f"- {_command_code_span(entry.command)} (sources: {sources})")
        if self.test_scope is not None:
            lines.extend(("", "test_scope:", json.dumps(self.test_scope, sort_keys=True)))
        lines.extend(
            (
                "",
                "commit_plan_result:",
                "",
                "```text",
                render_human(self.commit_plan_result),
                "```",
            ),
        )
        return "\n".join(lines)


def _command_code_span(command: str) -> str:
    """Fence literal command text without colliding with its backtick runs."""
    longest = max((len(match[0]) for match in re.finditer(r"`+", command)), default=0)
    fence = "`" * (longest + 1)
    padding = " " if command.startswith("`") or command.endswith("`") else ""
    return f"{fence}{padding}{command}{padding}{fence}"


class _ArgumentParser(argparse.ArgumentParser):
    """Raise command errors so the adapter returns one stable exit code."""

    def error(self, message: str) -> NoReturn:
        """Convert argparse termination into a renderer validation error."""
        raise ReviewExchangeError(message)


def _positive_int(value: str) -> int:
    """Parse one positive command-line integer."""
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("value must be positive") from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def code_review_context(
    plan: str | Path,
    implementation_step: str,
    umbrella: str | Path | None = None,
) -> ReviewContext:
    """Derive one fixed code-family context from an exact plan and step."""
    plan_path = Path(plan).expanduser().resolve()
    match = _PLAN_RE.fullmatch(plan_path.name)
    if match is None:
        raise ReviewExchangeError("reviewed plan has an unsupported plan file name")
    if not implementation_step.strip():
        raise ReviewExchangeError("implementation step must be non-empty")
    version, slug = match.groups()
    identity = ExchangeIdentity(ReviewFamily.CODE, "code", version, slug)
    umbrella_path = None if umbrella is None else Path(umbrella).expanduser().resolve()
    return ReviewContext(identity, plan_path, umbrella_path, implementation_step.strip())


def _identity_label(source: CodeReviewRoundInput) -> str:
    """Return a filename-safe label for unique authored headings."""
    return f"step {source.context.implementation_step} {source.context.identity.slug}"


def _identity_fields(source: CodeReviewRoundInput) -> str:
    """Render the exact human-readable plan, step, round, and umbrella fields."""
    context = source.context
    umbrella = (
        context.umbrella_path.as_posix()
        if context.umbrella_path is not None
        else "none"
    )
    return "\n".join(
        (
            f"Umbrella draft: {umbrella}",
            f"Implementation plan: {context.document_path.as_posix()}",
            f"Implementation step: {context.implementation_step}",
            f"Review round: {source.round_number}",
        ),
    )


def _transcript_identity_fields(source: CodeReviewRoundInput) -> str:
    """Render portable paths for the tracked transcript when the root is known."""
    root = source.project_root
    if root is None:
        return _identity_fields(source)
    context = source.context
    try:
        plan = context.document_path.relative_to(root).as_posix()
        umbrella = (
            context.umbrella_path.relative_to(root).as_posix()
            if context.umbrella_path is not None
            else "none"
        )
    except ValueError as error:
        raise ReviewExchangeError("review paths must be within the project root") from error
    return "\n".join(
        (
            f"Umbrella draft: {umbrella}",
            f"Implementation plan: {plan}",
            f"Implementation step: {context.implementation_step}",
            f"Review round: {source.round_number}",
        ),
    )


def _response_section(source: CodeReviewRoundInput, *, heading_level: int) -> str:
    """Render optional literal guidance separately from the writer response."""
    hashes = "#" * heading_level
    label = _identity_label(source)
    response = qualify_round_headings(
        source.writer_response.strip(),
        minimum_level=heading_level + 1,
        qualifier=label,
        round_number=source.round_number,
    )
    if source.human_guidance is None:
        return (
            f"{hashes} Writer response for {label} (round {source.round_number})\n\n"
            f"Writer response:\n\n{response}"
        )
    guidance = qualify_round_headings(
        source.human_guidance.rstrip(),
        minimum_level=heading_level + 1,
        qualifier=label,
        round_number=source.round_number,
    )
    return (
        f"{hashes} Human guidance and writer response for {label} "
        f"(round {source.round_number})\n\n"
        f"Human guidance:\n\n{guidance}\n\n"
        f"Writer response:\n\n{response}"
    )


def _authored_body(
    source: CodeReviewRoundInput,
    body: str,
    *,
    parent_heading_level: int,
) -> str:
    """Nest and identify caller headings below their generated section."""
    return qualify_round_headings(
        body.strip(),
        minimum_level=parent_heading_level + 1,
        qualifier=_identity_label(source),
        round_number=source.round_number,
    )


def _code_review_evidence(source: CodeReviewRoundInput) -> _CodeReviewEvidence:
    """Return the one typed payload used by request and transcript rendering."""
    return _CodeReviewEvidence(
        source.request_index_tree,
        source.resolved_validation_set,
        source.commit_plan_result,
        source.test_scope,
    )


def _ready_commit_plan(root: Path) -> CommitPlanCheckResult:
    """Run the checker once and reject any result that cannot support a request."""
    result = check_commit_plan(root)
    diagnostics = "; ".join(result.diagnostics)
    if result.state is CommitPlanCheckState.OPERATIONAL_FAILURE:
        detail = diagnostics or result.state.value
        raise ReviewExchangeError(f"commit plan check failed operationally: {detail}")
    if not result.ready:
        detail = f": {diagnostics}" if diagnostics else ""
        raise ReviewExchangeError(
            f"commit plan is not ready ({result.state.value}){detail}",
        )
    return result


def _code_review_evidence_json(source: CodeReviewRoundInput) -> str:
    """Render canonical JSON for the authored evidence block."""
    return json.dumps(_code_review_evidence(source).to_payload(), indent=2, sort_keys=True)


def _code_review_evidence_summary(source: CodeReviewRoundInput) -> str:
    """Derive a human-readable paired summary from the same typed payload."""
    return _code_review_evidence(source).summary()


def _request_authored_content(source: CodeReviewRoundInput) -> str:
    """Render specialized H2 content from the canonical code template."""
    values = {
        "identity_label": _identity_label(source),
        "round_number": str(source.round_number),
        "identity_fields": _identity_fields(source),
        "code_review_evidence": _code_review_evidence_json(source),
        "validation_scope": _authored_body(source, source.validation_scope, parent_heading_level=2),
        "assessment": _authored_body(source, source.assessment, parent_heading_level=2),
        "implementation_report": _authored_body(
            source,
            source.implementation_report,
            parent_heading_level=2,
        ),
        "change_summary": _authored_body(
            source,
            source.change_summary,
            parent_heading_level=2,
        ),
        "response_section": _response_section(source, heading_level=2),
    }
    try:
        template = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        raise ReviewExchangeError(f"cannot read request template: {error}") from error
    return template.substitute(values).rstrip() + "\n"


def _transcript_summary(source: CodeReviewRoundInput) -> str:
    """Render substantive requestor feedback without protocol boilerplate."""
    label = _identity_label(source)
    sections = (
        f"### Review identity for {label} (round {source.round_number})\n\n"
        f"{_transcript_identity_fields(source)}",
        f"### Code review evidence for {label} (round {source.round_number})\n\n"
        f"{_code_review_evidence_summary(source)}",
        f"### Validation scope for {label} (round {source.round_number})\n\n"
        f"{_authored_body(source, source.validation_scope, parent_heading_level=3)}",
        f"### Requestor assessment for {label} (round {source.round_number})\n\n"
        f"{_authored_body(source, source.assessment, parent_heading_level=3)}",
        f"### Implementation report for {label} (round {source.round_number})\n\n"
        f"{_authored_body(source, source.implementation_report, parent_heading_level=3)}",
        f"### Change summary for {label} (round {source.round_number})\n\n"
        f"{_authored_body(source, source.change_summary, parent_heading_level=3)}",
        _response_section(source, heading_level=3),
        f"### Reviewer focus for {label} (round {source.round_number})\n\n"
        "Check the exact plan step, staged implementation, test evidence, repaired "
        "path inventory, and a.commit accuracy.",
    )
    return "\n\n".join(sections) + "\n"


def render_code_review_request(source: CodeReviewRoundInput) -> CodeReviewRequestRender:
    """Render and validate the complete code request and summary together."""
    context = source.context
    envelope = Envelope(
        identity=context.identity,
        umbrella_path=context.umbrella_path,
        document_path=context.document_path,
        implementation_step=context.implementation_step,
        role=ReviewRole.REQUESTOR,
        round_number=source.round_number,
        created_at=source.created_at,
        test_scope=source.test_scope,
    )
    request_content = render_envelope_markdown(
        envelope,
        _request_authored_content(source),
    )
    parsed, _authored = parse_envelope_markdown(request_content)
    if parsed != envelope or _JSON_SECTION not in request_content:
        raise ReviewExchangeError("rendered request failed shared envelope validation")
    return CodeReviewRequestRender(request_content, _transcript_summary(source))


def _parser() -> _ArgumentParser:
    """Build the exact context, input, and paired-output CLI contract."""
    parser = _ArgumentParser(prog="code-review-request")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--implementation-step", required=True)
    parser.add_argument("--umbrella")
    parser.add_argument("--round-number", required=True, type=_positive_int)
    parser.add_argument("--assessment-file", required=True)
    parser.add_argument("--implementation-report-file", required=True)
    parser.add_argument("--change-summary-file", required=True)
    parser.add_argument("--writer-response-file", required=True)
    parser.add_argument("--guidance-file")
    parser.add_argument("--scope-change-file")
    parser.add_argument("--plan-validation-command", action="append", default=[])
    parser.add_argument("--request-validation-command", action="append", default=[])
    parser.add_argument("--request-content-output", required=True)
    parser.add_argument("--transcript-summary-output", required=True)
    parser.add_argument("--scope-capture-output", required=True)
    return parser


def _render_from_arguments(args: argparse.Namespace, project_root: Path) -> None:
    """Validate paths, read each input once, and write the paired result once."""
    root = project_root.resolve()
    context = code_review_context(args.plan, args.implementation_step, args.umbrella)
    input_specs = (
        ("assessment", args.assessment_file, "assessment file"),
        ("implementation_report", args.implementation_report_file, "implementation report file"),
        ("change_summary", args.change_summary_file, "change summary file"),
        ("writer_response", args.writer_response_file, "writer response file"),
    )
    inputs = {
        key: files.root_file(root, value, label, input_file=True)
        for key, value, label in input_specs
    }
    guidance = None if args.guidance_file is None else files.root_file(
        root, args.guidance_file, "guidance file", input_file=True,
    )
    reason = None if args.scope_change_file is None else files.root_file(
        root, args.scope_change_file, "scope change file", input_file=True,
    )
    request_output = files.root_file(
        root, args.request_content_output, "request content output", input_file=False,
    )
    summary_output = files.root_file(
        root, args.transcript_summary_output, "transcript summary output", input_file=False,
    )
    capture_output = files.root_file(
        root, args.scope_capture_output, "scope capture output", input_file=False,
    )
    all_paths = (*inputs.values(), request_output, summary_output, capture_output)
    if guidance is not None:
        all_paths = (*all_paths, guidance)
    if reason is not None:
        all_paths = (*all_paths, reason)
    if len(set(all_paths)) != len(all_paths):
        raise ReviewExchangeError("caller-owned input and output paths must be distinct")
    effort = scopes.resolve_request_scope(root, context.document_path, context.identity)
    evidence = scopes.scope_evidence(root, effort)
    policy = load_project_validation(root)
    change = scopes.scope_change_block(
        scopes.bound_capture(root, context), evidence,
        None if reason is None else files.read_utf8(reason, "scope change file"),
    )
    resolved_validation_set = resolve_code_review_validation(
        complete_project_default(policy, effort.scope.selector()),
        args.plan_validation_command,
        args.request_validation_command,
    )
    authored_inputs = {
        "assessment": files.read_utf8(inputs["assessment"], "assessment file"),
        "implementation_report": files.read_utf8(
            inputs["implementation_report"],
            "implementation report file",
        ),
        "change_summary": files.read_utf8(inputs["change_summary"], "change summary file"),
        "writer_response": files.read_utf8(inputs["writer_response"], "writer response file"),
    }
    request_index_tree = capture_index_tree(root)
    commit_plan_result = _ready_commit_plan(root)
    confirmed_index_tree = capture_index_tree(root)
    if confirmed_index_tree != request_index_tree:
        raise ReviewExchangeError("index changed during commit plan check")
    source = CodeReviewRoundInput(
        context=context,
        round_number=args.round_number,
        created_at=format_local_timestamp(),
        assessment=authored_inputs["assessment"],
        implementation_report=authored_inputs["implementation_report"],
        change_summary=authored_inputs["change_summary"],
        writer_response=authored_inputs["writer_response"],
        request_index_tree=request_index_tree,
        resolved_validation_set=resolved_validation_set,
        commit_plan_result=commit_plan_result,
        human_guidance=None if guidance is None else files.read_utf8(guidance, "guidance file"),
        project_root=root,
        test_scope=evidence,
        validation_scope="\n\n".join(filter(None, (
            f"Validation scope: {effort.scope.label()}.", migration_notice(policy),
            group_claim_statement(policy, effort.scope.name), change,
        ))),
    )
    rendered = render_code_review_request(source)
    files.write_utf8(request_output, rendered.request_content, "request content output")
    files.write_utf8(summary_output, rendered.transcript_summary, "transcript summary output")
    write_capture(capture_output, effort.scope)


def main(
    argv: Sequence[str] | None = None,
    *,
    project_root: Path | None = None,
) -> int:
    """Run paired code-review rendering with one stable fatal exit code."""
    try:
        args = _parser().parse_args(argv)
        root = find_project_root(Path.cwd()) if project_root is None else project_root
        _render_from_arguments(args, root)
    except (ReviewExchangeError, EffortScopeError, CaptureError, OSError) as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return _FATAL_EXIT
    return 0


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


# eof
