"""TDD coverage for Step 1 paired specification review request rendering.

The tests keep complete request Markdown and transcript feedback on one frozen
round input, and exercise the thin file-based command boundary separately.
"""

# ruff: noqa: S105

from __future__ import annotations

import subprocess
from dataclasses import FrozenInstanceError, replace
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

import pytest

from tools import spec_review_request as requestor
from tools.markdown_check.rules import check_md001
from tools.markdown_check.source import parse_markdown
from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
)
from tools.review_exchange_models_envelope import parse_envelope_markdown

if TYPE_CHECKING:
    from pathlib import Path

_VERSION = "v0.11.0"
_SLUG = "spec-review-requestor"
_TIMESTAMP = "2026-08-07T09:15:00+02:00"
_RENDER_ROUND = 2
_CLI_ROUND = 3
_FATAL_EXIT = 2


def _document(tmp_path: Path, prefix: str) -> Path:
    """Create one exact reviewed specification document."""
    document = tmp_path / f"{prefix}.{_VERSION}.{_SLUG}.md"
    document.write_text("# Reviewed specification\n", encoding="utf-8")
    return document


def _round_input(
    tmp_path: Path,
    prefix: str = "feature-request",
    *,
    umbrella: bool = True,
    guidance: str | None = None,
) -> requestor.SpecificationRoundInput:
    """Create one complete immutable renderer input."""
    document = _document(tmp_path, prefix)
    umbrella_path = tmp_path / "draft.v0.11.0.review-mode.md" if umbrella else None
    if umbrella_path is not None:
        umbrella_path.write_text("# Umbrella\n", encoding="utf-8")
    context = requestor.specification_context(document, umbrella_path)
    return requestor.SpecificationRoundInput(
        context=context,
        round_number=2,
        created_at=_TIMESTAMP,
        assessment="The implementation questions are ready for review.",
        change_summary="Q01 and Q02 were added.",
        writer_response="The writer applied the requested direction.",
        human_guidance=guidance,
    )


@pytest.mark.parametrize(
    ("prefix", "type_token"),
    [
        ("feature-request", "feature-request"),
        ("issue", "issue"),
        ("design", "design-specification"),
        ("plan", "plan"),
    ],
)
def test_render_pairs_supported_identity_round_and_markdown_shape(
    tmp_path: Path,
    prefix: str,
    type_token: str,
) -> None:
    """Every supported specification type produces one coherent pair."""
    source = _round_input(tmp_path, prefix)

    rendered = requestor.render_specification_request(source)
    envelope, authored = parse_envelope_markdown(rendered.request_content)

    _assert_rendered_envelope(envelope, source, type_token)
    _assert_request_markdown_shape(rendered, authored, source)
    _assert_paired_authored_content(rendered, authored)


def _assert_rendered_envelope(
    envelope: requestor.Envelope,
    source: requestor.SpecificationRoundInput,
    type_token: str,
) -> None:
    """Check exact shared envelope identity and round data."""
    assert envelope.identity.type_token == type_token
    assert envelope.round_number == _RENDER_ROUND
    assert envelope.document_path == source.context.document_path


def _assert_request_markdown_shape(
    rendered: requestor.SpecificationRequestRender,
    authored: str,
    source: requestor.SpecificationRoundInput,
) -> None:
    """Check the required H1, JSON-first, H2, and human identity shape."""
    assert authored.startswith("## Review identity")
    assert source.context.umbrella_path is not None
    assert "Umbrella draft: " + source.context.umbrella_path.as_posix() in authored
    assert "Reviewed specification: " + source.context.document_path.as_posix() in authored
    assert "Review round: 2" in authored
    assert rendered.request_content.startswith("# Review request for specification/")
    assert "\n\n## JSON\n\n```json\n" in rendered.request_content


def _assert_paired_authored_content(
    rendered: requestor.SpecificationRequestRender,
    authored: str,
) -> None:
    """Check substantive content pairing without inflating test complexity."""
    assert "The implementation questions are ready for review." in authored
    assert "Q01 and Q02 were added." in rendered.transcript_summary
    assert "Review round: 2" in rendered.transcript_summary
    assert "if there are very few edits" not in rendered.transcript_summary
    assert "publish the project-root" not in rendered.transcript_summary


def test_render_accepts_no_umbrella_and_preserves_guidance_verbatim(
    tmp_path: Path,
) -> None:
    """Optional context and override guidance stay literal and unmerged."""
    source = _round_input(
        tmp_path,
        umbrella=False,
        guidance="Keep option A.\nDo not collapse its rationale.",
    )

    rendered = requestor.render_specification_request(source)

    assert "Umbrella draft: none" in rendered.request_content
    assert "Human guidance:\n\nKeep option A.\nDo not collapse its rationale." in (
        rendered.request_content
    )
    assert "Writer response:\n\nThe writer applied the requested direction." in (
        rendered.request_content
    )
    assert "Human guidance:\n\nKeep option A.\nDo not collapse its rationale." in (
        rendered.transcript_summary
    )
    assert rendered.request_content.count("Human guidance:") == 1
    assert rendered.transcript_summary.count("Human guidance:") == 1


def test_render_nests_and_qualifies_specification_headings(
    tmp_path: Path,
) -> None:
    """Caller and guidance headings remain unique children in both outputs."""
    source = replace(
        _round_input(
            tmp_path,
            guidance="## Human decision\n\nKeep Q01.\n\n### Evidence",
        ),
        assessment="Ready.\n\n## Assessment evidence",
    )

    rendered = requestor.render_specification_request(source)

    assert (
        "### Assessment evidence for feature-request spec-review-requestor "
        "(round 2)" in rendered.request_content
    )
    assert (
        "Human guidance:\n\n"
        "### Human decision for feature-request spec-review-requestor (round 2)"
        in rendered.request_content
    )
    assert (
        "#### Human decision for feature-request spec-review-requestor (round 2)"
        in rendered.transcript_summary
    )
    assert "round 2" not in "\n".join(
        line for line in rendered.request_content.splitlines() if line.startswith("## ")
    ).replace("(round 2)", "")


def test_writer_response_headings_remain_blocks_without_level_skips(
    tmp_path: Path,
) -> None:
    """A response label cannot swallow its first nested Markdown heading."""
    source = replace(
        _round_input(tmp_path),
        writer_response=(
            "# Writer response\n\nThe finding is addressed.\n\n"
            "## What changed\n\nThe wording is now explicit."
        ),
    )

    rendered = requestor.render_specification_request(source)

    assert "Writer response:\n\n### Writer response" in rendered.request_content
    assert "Writer response:\n\n#### Writer response" in rendered.transcript_summary
    for name, markdown in (
        ("request.md", rendered.request_content),
        ("transcript.md", rendered.transcript_summary),
    ):
        source_markdown = parse_markdown(PurePosixPath(name), markdown)
        assert check_md001(source_markdown) == ()


def test_round_input_is_frozen_and_rejects_invalid_content(tmp_path: Path) -> None:
    """The pure renderer cannot receive an invalid or mutable round."""
    source = _round_input(tmp_path)

    with pytest.raises(FrozenInstanceError):
        setattr(source, "round_number", 3)
    with pytest.raises(ReviewExchangeError, match="round must be positive"):
        requestor.SpecificationRoundInput(
            source.context,
            0,
            _TIMESTAMP,
            source.assessment,
            source.change_summary,
            source.writer_response,
        )
    with pytest.raises(ReviewExchangeError, match="assessment must be non-empty"):
        requestor.SpecificationRoundInput(
            source.context,
            1,
            _TIMESTAMP,
            "  ",
            source.change_summary,
            source.writer_response,
        )
    with pytest.raises(ReviewExchangeError, match="human guidance must be non-empty"):
        replace(source, human_guidance="  ")
    with pytest.raises(ReviewExchangeError, match="paired request rendering"):
        requestor.SpecificationRequestRender("", "summary")


def test_round_input_rejects_code_context(tmp_path: Path) -> None:
    """The specialized renderer accepts no implementation-code identity."""
    document = _document(tmp_path, "plan")
    context = ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", _VERSION, _SLUG),
        document,
        None,
        "1",
    )

    with pytest.raises(ReviewExchangeError, match="specification context"):
        replace(_round_input(tmp_path), context=context)


def test_renderer_reports_template_and_shared_validation_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing templates and inconsistent shared validation fail closed."""
    source = _round_input(tmp_path)
    missing_template = tmp_path / "missing-template.md"
    monkeypatch.setattr(requestor, "_TEMPLATE_PATH", missing_template)
    with pytest.raises(ReviewExchangeError, match="cannot read request template"):
        requestor.render_specification_request(source)

    monkeypatch.undo()
    parse = requestor.parse_envelope_markdown

    def mismatched(markdown: str) -> tuple[requestor.Envelope, str]:
        """Return a valid but wrong shared envelope for the rendered request."""
        envelope, authored = parse(markdown)
        return replace(envelope, round_number=envelope.round_number + 1), authored

    monkeypatch.setattr(requestor, "parse_envelope_markdown", mismatched)
    with pytest.raises(ReviewExchangeError, match="shared envelope validation"):
        requestor.render_specification_request(source)


@pytest.mark.parametrize(
    "name",
    [
        "code.v0.11.0.spec-review-requestor.md",
        "notes.v0.11.0.spec-review-requestor.md",
        "feature-request.0.11.0.spec-review-requestor.md",
    ],
)
def test_context_rejects_unsupported_document_names(tmp_path: Path, name: str) -> None:
    """Only exact registered specification source filenames are accepted."""
    document = tmp_path / name
    document.write_text("# Invalid\n", encoding="utf-8")

    with pytest.raises(ReviewExchangeError, match="unsupported file name"):
        requestor.specification_context(document, None)


def _cli_files(tmp_path: Path) -> dict[str, Path]:
    """Create the four ignored authored inputs and two output paths."""
    home = tmp_path / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    files = {
        "assessment": home / "a.assessment.md",
        "changes": home / "a.changes.md",
        "response": home / "a.response.md",
        "guidance": home / "a.guidance.md",
        "content": home / "a.request-content.md",
        "summary": home / "a.request-summary.md",
    }
    files["assessment"].write_text("Assess these questions.\n", encoding="utf-8")
    files["changes"].write_text("Added Q01.\n", encoding="utf-8")
    files["response"].write_text("Accepted.\n", encoding="utf-8")
    files["guidance"].write_text("Keep the exact words.\n", encoding="utf-8")
    return files


def _cli_args(document: Path, files: dict[str, Path]) -> list[str]:
    """Return the explicit flag-and-file command contract."""
    return [
        "--document",
        str(document),
        "--round-number",
        "3",
        "--assessment-file",
        str(files["assessment"]),
        "--change-summary-file",
        str(files["changes"]),
        "--writer-response-file",
        str(files["response"]),
        "--guidance-file",
        str(files["guidance"]),
        "--request-content-output",
        str(files["content"]),
        "--transcript-summary-output",
        str(files["summary"]),
    ]


def _always_ignored(_root: Path, _path: Path) -> bool:
    """Treat caller-owned paths as ignored for isolated CLI unit tests."""
    return True


def _git_path(_name: str) -> str:
    """Return a deterministic Git executable path for subprocess seams."""
    return "git"


def _no_git(_name: str) -> None:
    """Represent a host where Git cannot be located."""
    return


@pytest.mark.parametrize("return_code", [0, 1])
def test_git_ignore_check_uses_fixed_command_and_return_code(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    return_code: int,
) -> None:
    """Effective-ignore validation maps Git's exact result without shell use."""
    calls: list[tuple[object, ...]] = []

    def fake_run(*args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return subprocess.CompletedProcess([], return_code)

    monkeypatch.setattr(requestor.shutil, "which", _git_path)
    monkeypatch.setattr(requestor.subprocess, "run", fake_run)

    assert requestor._is_effectively_ignored(
        tmp_path,
        tmp_path / "a.input.md",
    ) is (return_code == 0)
    assert calls


def test_git_ignore_check_reports_missing_git_and_process_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unavailable Git and process launch errors have stable diagnostics."""
    monkeypatch.setattr(requestor.shutil, "which", _no_git)
    with pytest.raises(ReviewExchangeError, match="git was not found"):
        requestor._is_effectively_ignored(tmp_path, tmp_path / "a.input.md")

    def fail_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        message = "git process failed"
        raise OSError(message)

    monkeypatch.setattr(requestor.shutil, "which", _git_path)
    monkeypatch.setattr(requestor.subprocess, "run", fail_run)
    with pytest.raises(ReviewExchangeError, match="cannot validate ignored file"):
        requestor._is_effectively_ignored(tmp_path, tmp_path / "a.input.md")


def test_cli_reads_explicit_files_and_writes_the_pair_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The command validates every path before producing both UTF-8 outputs."""
    document = _document(tmp_path, "plan")
    files = _cli_files(tmp_path)
    monkeypatch.setattr(requestor, "_is_effectively_ignored", _always_ignored)
    monkeypatch.setattr(requestor, "format_local_timestamp", lambda: _TIMESTAMP)

    result = requestor.main(_cli_args(document, files), project_root=tmp_path)

    assert result == 0
    request_text = files["content"].read_text(encoding="utf-8")
    summary_text = files["summary"].read_text(encoding="utf-8")
    envelope, _ = parse_envelope_markdown(request_text)
    assert envelope.identity.type_token == "plan"
    assert envelope.round_number == _CLI_ROUND
    assert "Assess these questions." in request_text
    assert "Added Q01." in summary_text
    assert "Human guidance:\n\nKeep the exact words." in summary_text


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("missing", "assessment file does not exist"),
        ("malformed", "assessment file is not valid UTF-8"),
        ("nested-output", "request content output must be in the review artifact home"),
        ("tracked-output", "request content output is not effectively ignored"),
    ],
)
def test_cli_rejects_invalid_input_or_output_before_writing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mutation: str,
    message: str,
) -> None:
    """Missing, malformed, non-root, or tracked paths leave no partial pair."""
    document = _document(tmp_path, "issue")
    files = _cli_files(tmp_path)
    def ignored(_root: Path, path: Path) -> bool:
        """Reject only the requested tracked-output case."""
        return not (mutation == "tracked-output" and path == files["content"])

    monkeypatch.setattr(requestor, "_is_effectively_ignored", ignored)
    if mutation == "missing":
        files["assessment"].unlink()
    elif mutation == "malformed":
        files["assessment"].write_bytes(b"\xff")
    elif mutation == "nested-output":
        nested = tmp_path / "nested"
        nested.mkdir()
        files["content"] = nested / "a.request-content.md"

    result = requestor.main(_cli_args(document, files), project_root=tmp_path)

    assert result == _FATAL_EXIT
    assert message in capsys.readouterr().err
    assert not files["content"].exists()
    assert not files["summary"].exists()


def test_cli_rejects_wrong_round_and_non_root_authored_input(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Command flags reject non-positive rounds and authored files off-root."""
    document = _document(tmp_path, "design")
    files = _cli_files(tmp_path)
    monkeypatch.setattr(requestor, "_is_effectively_ignored", _always_ignored)
    args = _cli_args(document, files)
    args[args.index("3")] = "not-a-number"

    assert requestor.main(args, project_root=tmp_path) == _FATAL_EXIT
    assert "value must be positive" in capsys.readouterr().err

    args[args.index("not-a-number")] = "0"

    assert requestor.main(args, project_root=tmp_path) == _FATAL_EXIT
    assert "value must be positive" in capsys.readouterr().err

    nested = tmp_path / "nested"
    nested.mkdir()
    files["response"] = nested / "a.response.md"
    files["response"].write_text("Response\n", encoding="utf-8")

    assert requestor.main(_cli_args(document, files), project_root=tmp_path) == _FATAL_EXIT
    assert "writer response file must be in the review artifact home" in (
        capsys.readouterr().err
    )


def test_root_and_io_helpers_cover_defensive_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid names, directories, and OS failures remain caller-safe."""
    monkeypatch.setattr(requestor, "_is_effectively_ignored", _always_ignored)
    home = tmp_path / ".reviews"
    home.mkdir()
    with pytest.raises(ReviewExchangeError, match=r"a\.\* name"):
        requestor._root_file(
            tmp_path,
            home / "output.md",
            "request content output",
            input_file=False,
        )

    directory = home / "a.directory"
    directory.mkdir()
    with pytest.raises(ReviewExchangeError, match="must not be a directory"):
        requestor._root_file(
            tmp_path,
            directory,
            "request content output",
            input_file=False,
        )
    with pytest.raises(ReviewExchangeError, match="cannot read assessment file"):
        requestor._read_utf8(directory, "assessment file")
    with pytest.raises(ReviewExchangeError, match="cannot write request content output"):
        requestor._write_utf8(directory, "content", "request content output")


def test_cli_rejects_duplicate_input_and_output_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A caller-owned path cannot serve two roles in one render operation."""
    document = _document(tmp_path, "plan")
    files = _cli_files(tmp_path)
    files["summary"] = files["content"]
    monkeypatch.setattr(requestor, "_is_effectively_ignored", _always_ignored)

    result = requestor.main(_cli_args(document, files), project_root=tmp_path)

    assert result == _FATAL_EXIT
    assert "input and output paths must be distinct" in capsys.readouterr().err


# eof
