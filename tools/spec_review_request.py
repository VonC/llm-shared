#!/usr/bin/env python3
"""Render paired specification review request artifacts from one round input.

Step 1 prevents complete request Markdown and transcript feedback from drifting
apart. The pure renderer reuses the shared exchange envelope, while the command
adapter validates every caller-owned root file before it writes either output.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import argparse
import contextlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, NoReturn

# bin\spec_review_request.bat runs this file by path, so sys.path[0] is the
# tools directory and the `tools.` package below is not importable from it.
# Bootstrap the repository root the way new_draft.py does, or the launcher
# fails with "No module named 'tools'" from every project.
if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

from tools._models import find_project_root
from tools.review_artifact_configuration import caller_file_parents
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

if TYPE_CHECKING:
    from collections.abc import Sequence

_DOCUMENT_RE = re.compile(
    r"^(feature-request|issue|design|plan)\.(v\d+\.\d+\.\d+)\."
    r"([a-z0-9][a-z0-9_-]*)\.md$",
)
_TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / (
    "spec-review-request.template.md"
)
_JSON_SECTION = "## JSON"
_FATAL_EXIT = 2


@dataclass(frozen=True)
class SpecificationRoundInput:
    """Validated authored content and exact identity for one request round."""

    context: ReviewContext
    round_number: int
    created_at: str
    assessment: str
    change_summary: str
    writer_response: str
    human_guidance: str | None = None

    def __post_init__(self) -> None:
        """Reject invalid rounds, families, timestamps, or empty authored text."""
        if self.context.identity.family is not ReviewFamily.SPECIFICATION:
            raise ReviewExchangeError("renderer requires a specification context")
        if self.round_number <= 0:
            raise ReviewExchangeError("round must be positive")
        validate_local_timestamp(self.created_at)
        authored = {
            "assessment": self.assessment,
            "change summary": self.change_summary,
            "writer response": self.writer_response,
        }
        for label, value in authored.items():
            if not value.strip():
                raise ReviewExchangeError(f"{label} must be non-empty")
        if self.human_guidance is not None and not self.human_guidance.strip():
            raise ReviewExchangeError("human guidance must be non-empty when supplied")


@dataclass(frozen=True)
class SpecificationRequestRender:
    """Complete request content and its paired substantive transcript summary."""

    request_content: str
    transcript_summary: str

    def __post_init__(self) -> None:
        """Reject an incomplete paired rendering result."""
        if not self.request_content or not self.transcript_summary:
            raise ReviewExchangeError("paired request rendering must be non-empty")


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


def specification_context(
    document: str | Path,
    umbrella: str | Path | None,
) -> ReviewContext:
    """Derive one shared specification context from exact source filenames."""
    document_path = Path(document).expanduser().resolve()
    match = _DOCUMENT_RE.fullmatch(document_path.name)
    if match is None:
        raise ReviewExchangeError("reviewed document has an unsupported file name")
    prefix, version, slug = match.groups()
    type_token = "design-specification" if prefix == "design" else prefix
    identity = ExchangeIdentity(
        ReviewFamily.SPECIFICATION,
        type_token,
        version,
        slug,
    )
    umbrella_path = None if umbrella is None else Path(umbrella).expanduser().resolve()
    return ReviewContext(identity, document_path, umbrella_path, None)


def _identity_label(source: SpecificationRoundInput) -> str:
    """Return a filename-safe descriptive label for unique Markdown headings."""
    identity = source.context.identity
    return f"{identity.type_token} {identity.slug}"


def _identity_fields(source: SpecificationRoundInput) -> str:
    """Render the exact human-readable identity fields once."""
    umbrella = (
        source.context.umbrella_path.as_posix()
        if source.context.umbrella_path is not None
        else "none"
    )
    return "\n".join(
        (
            f"Umbrella draft: {umbrella}",
            f"Reviewed specification: {source.context.document_path.as_posix()}",
            f"Review round: {source.round_number}",
        ),
    )


def _response_section(
    source: SpecificationRoundInput,
    *,
    heading_level: int,
) -> str:
    """Nest optional guidance and the separate writer response."""
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
    source: SpecificationRoundInput,
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


def _answer_name(source: SpecificationRoundInput) -> str:
    """Return the exact project-root reviewer answer artifact name."""
    identity = source.context.identity
    return (
        f"a.review-answer.{identity.type_token}.{identity.version}.{identity.slug}.md"
    )


def _request_authored_content(source: SpecificationRoundInput) -> str:
    """Render specialized H2 content from the canonical request template."""
    label = _identity_label(source)
    values = {
        "identity_label": label,
        "round_number": str(source.round_number),
        "identity_fields": _identity_fields(source),
        "assessment": _authored_body(source, source.assessment, parent_heading_level=2),
        "change_summary": _authored_body(
            source,
            source.change_summary,
            parent_heading_level=2,
        ),
        "response_section": _response_section(source, heading_level=2),
        "answer_name": _answer_name(source),
    }
    try:
        template = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        raise ReviewExchangeError(f"cannot read request template: {error}") from error
    return template.substitute(values).rstrip() + "\n"


def _transcript_summary(source: SpecificationRoundInput) -> str:
    """Render substantive H3 feedback without fixed conclusion boilerplate."""
    label = _identity_label(source)
    sections = (
        f"### Review identity for {label} (round {source.round_number})\n\n"
        f"{_identity_fields(source)}",
        f"### Requestor assessment for {label} (round {source.round_number})\n\n"
        f"{_authored_body(source, source.assessment, parent_heading_level=3)}",
        f"### Change summary for {label} (round {source.round_number})\n\n"
        f"{_authored_body(source, source.change_summary, parent_heading_level=3)}",
        _response_section(source, heading_level=3),
        f"### Reviewer focus for {label} (round {source.round_number})\n\n"
        "Check for missing questions, assess the existing options and answers, "
        "and suggest any clearer wording.",
    )
    return "\n\n".join(sections) + "\n"


def render_specification_request(
    source: SpecificationRoundInput,
) -> SpecificationRequestRender:
    """Render and validate a complete request and substantive summary together."""
    context = source.context
    envelope = Envelope(
        identity=context.identity,
        umbrella_path=context.umbrella_path,
        document_path=context.document_path,
        implementation_step=None,
        role=ReviewRole.REQUESTOR,
        round_number=source.round_number,
        created_at=source.created_at,
    )
    request_content = render_envelope_markdown(
        envelope,
        _request_authored_content(source),
    )
    parsed, _authored = parse_envelope_markdown(request_content)
    if parsed != envelope or _JSON_SECTION not in request_content:
        raise ReviewExchangeError("rendered request failed shared envelope validation")
    return SpecificationRequestRender(request_content, _transcript_summary(source))


def _is_effectively_ignored(project_root: Path, path: Path) -> bool:
    """Ask Git whether a caller-owned root path is effectively ignored."""
    git_executable = shutil.which("git")
    if git_executable is None:
        raise ReviewExchangeError("cannot validate ignored file: git was not found")
    try:
        result = subprocess.run(  # noqa: S603 - fixed Git executable and arguments
            [
                git_executable,
                "-C",
                str(project_root),
                "check-ignore",
                "-q",
                "--",
                str(path.relative_to(project_root)),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise ReviewExchangeError(f"cannot validate ignored file: {error}") from error
    return result.returncode == 0


def _root_file(
    project_root: Path,
    value: str | Path,
    label: str,
    *,
    input_file: bool,
) -> Path:
    """Validate one ignored caller-owned home-local input or output path."""
    path = Path(value).expanduser().resolve()
    if path.parent not in caller_file_parents(project_root):
        raise ReviewExchangeError(f"{label} must be in the review artifact home")
    if not path.name.startswith("a."):
        raise ReviewExchangeError(f"{label} must use an a.* name")
    if input_file and not path.is_file():
        raise ReviewExchangeError(f"{label} does not exist")
    if not input_file and path.exists() and not path.is_file():
        raise ReviewExchangeError(f"{label} must not be a directory")
    if not _is_effectively_ignored(project_root, path):
        raise ReviewExchangeError(f"{label} is not effectively ignored")
    return path


def _read_utf8(path: Path, label: str) -> str:
    """Read one already validated caller-owned input exactly once."""
    try:
        with path.open(encoding="utf-8", newline="") as stream:
            return stream.read()
    except UnicodeError as error:
        raise ReviewExchangeError(f"{label} is not valid UTF-8") from error
    except OSError as error:
        raise ReviewExchangeError(f"cannot read {label}: {error}") from error


def _write_utf8(path: Path, content: str, label: str) -> None:
    """Write one validated caller-owned output in one UTF-8 operation."""
    try:
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    except OSError as error:
        raise ReviewExchangeError(f"cannot write {label}: {error}") from error


def _parser() -> _ArgumentParser:
    """Build the explicit context, authored-input, and paired-output contract."""
    parser = _ArgumentParser(prog="spec-review-request")
    parser.add_argument("--document", required=True)
    parser.add_argument("--umbrella")
    parser.add_argument("--round-number", required=True, type=_positive_int)
    parser.add_argument("--assessment-file", required=True)
    parser.add_argument("--change-summary-file", required=True)
    parser.add_argument("--writer-response-file", required=True)
    parser.add_argument("--guidance-file")
    parser.add_argument("--request-content-output", required=True)
    parser.add_argument("--transcript-summary-output", required=True)
    return parser


def _render_from_arguments(args: argparse.Namespace, project_root: Path) -> None:
    """Validate all paths, read each input once, and write the paired result."""
    root = project_root.resolve()
    context = specification_context(args.document, args.umbrella)
    inputs = {
        "assessment": _root_file(
            root,
            args.assessment_file,
            "assessment file",
            input_file=True,
        ),
        "change_summary": _root_file(
            root,
            args.change_summary_file,
            "change summary file",
            input_file=True,
        ),
        "writer_response": _root_file(
            root,
            args.writer_response_file,
            "writer response file",
            input_file=True,
        ),
    }
    guidance = (
        None
        if args.guidance_file is None
        else _root_file(root, args.guidance_file, "guidance file", input_file=True)
    )
    request_output = _root_file(
        root,
        args.request_content_output,
        "request content output",
        input_file=False,
    )
    summary_output = _root_file(
        root,
        args.transcript_summary_output,
        "transcript summary output",
        input_file=False,
    )
    all_paths = (*inputs.values(), request_output, summary_output)
    if guidance is not None:
        all_paths = (*all_paths, guidance)
    if len(set(all_paths)) != len(all_paths):
        raise ReviewExchangeError("caller-owned input and output paths must be distinct")
    source = SpecificationRoundInput(
        context=context,
        round_number=args.round_number,
        created_at=format_local_timestamp(),
        assessment=_read_utf8(inputs["assessment"], "assessment file"),
        change_summary=_read_utf8(inputs["change_summary"], "change summary file"),
        writer_response=_read_utf8(inputs["writer_response"], "writer response file"),
        human_guidance=(
            None if guidance is None else _read_utf8(guidance, "guidance file")
        ),
    )
    rendered = render_specification_request(source)
    _write_utf8(request_output, rendered.request_content, "request content output")
    _write_utf8(summary_output, rendered.transcript_summary, "transcript summary output")


def main(
    argv: Sequence[str] | None = None,
    *,
    project_root: Path | None = None,
) -> int:
    """Run the paired renderer command and return a stable process exit code."""
    try:
        args = _parser().parse_args(argv)
        root = find_project_root(Path.cwd()) if project_root is None else project_root
        _render_from_arguments(args, root)
    except (ReviewExchangeError, OSError) as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return _FATAL_EXIT
    return 0


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


# eof
