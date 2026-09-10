"""TDD coverage for Step 1 paired implementation code-review rendering.

The tests pin one immutable code-round identity to both rendered artifacts and
exercise the caller-owned UTF-8 file boundary without involving the exchange.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import FrozenInstanceError, replace
from typing import TYPE_CHECKING

import pytest

from tools import code_review_request as requestor
from tools.code_review_validation import resolve_code_review_validation
from tools.commit_plan_check import CommitPlanCheckResult, CommitPlanCheckState
from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
)
from tools.review_exchange_models_envelope import parse_envelope_markdown

# ruff: noqa: S105

if TYPE_CHECKING:
    from pathlib import Path

_VERSION = "v0.11.0"
_SLUG = "code-review-requestor"
_TIMESTAMP = "2026-08-13T10:15:00+02:00"
_RENDER_ROUND = 2
_FATAL_EXIT = 2
_TREE = "1" * 40
_READY_RESULT = CommitPlanCheckResult(CommitPlanCheckState.VALID)


def _validation_set() -> requestor.ResolvedValidationSet:
    """Return one resolved default-plus-plan validation set."""
    return resolve_code_review_validation(("ghog day",), ("focused Step 1 tests",))


def _plan(tmp_path: Path, name: str = f"plan.{_VERSION}.{_SLUG}.md") -> Path:
    """Create one exact implementation plan."""
    plan = tmp_path / name
    plan.write_text("# Plan\n", encoding="utf-8")
    return plan


def _round_input(
    tmp_path: Path,
    *,
    umbrella: bool = True,
    guidance: str | None = None,
) -> requestor.CodeReviewRoundInput:
    """Create one complete immutable code-review round input."""
    plan = _plan(tmp_path)
    umbrella_path = tmp_path / "draft.v0.11.0.review-mode.md" if umbrella else None
    if umbrella_path is not None:
        umbrella_path.write_text("# Umbrella\n", encoding="utf-8")
    return requestor.CodeReviewRoundInput(
        context=requestor.code_review_context(plan, "1", umbrella_path),
        round_number=2,
        created_at=_TIMESTAMP,
        assessment="Step 1 is implemented and its focused checks pass.",
        implementation_report="Added the renderer, launcher, template, and tests.",
        change_summary="Five Step 1 paths are staged for review.",
        writer_response="No earlier reviewer feedback exists for round 1.",
        request_index_tree=_TREE,
        resolved_validation_set=_validation_set(),
        commit_plan_result=_READY_RESULT,
        human_guidance=guidance,
    )


def test_render_pairs_exact_code_identity_and_markdown_shape(tmp_path: Path) -> None:
    """The request and summary carry the same exact plan-step-round identity."""
    source = _round_input(tmp_path)

    rendered = requestor.render_code_review_request(source)
    envelope, authored = parse_envelope_markdown(rendered.request_content)

    _assert_envelope_identity(envelope, source)
    _assert_paired_identity(rendered, authored, source)


def test_render_nests_and_qualifies_caller_headings_for_each_output(
    tmp_path: Path,
) -> None:
    """Bare input headings become unique children of each generated section."""
    source = replace(
        _round_input(tmp_path),
        assessment="Lead.\n\n## Test evidence\n\n### Detail",
    )

    rendered = requestor.render_code_review_request(source)

    assert (
        "### Test evidence for step 1 code-review-requestor (round 2)"
        in rendered.request_content
    )
    assert (
        "#### Detail for step 1 code-review-requestor (round 2)"
        in rendered.request_content
    )
    assert (
        "#### Test evidence for step 1 code-review-requestor (round 2)"
        in rendered.transcript_summary
    )
    assert (
        "##### Detail for step 1 code-review-requestor (round 2)"
        in rendered.transcript_summary
    )
    assert "\n## Test evidence\n" not in rendered.request_content
    assert "\n## Test evidence\n" not in rendered.transcript_summary


def _assert_envelope_identity(
    envelope: requestor.Envelope,
    source: requestor.CodeReviewRoundInput,
) -> None:
    """Assert the fixed code-family envelope and exact reviewed context."""
    assert envelope.identity.family is ReviewFamily.CODE
    assert envelope.identity.type_token == "code"
    assert envelope.document_path == source.context.document_path
    assert envelope.implementation_step == "1"


def _assert_paired_identity(
    rendered: requestor.CodeReviewRequestRender,
    authored: str,
    source: requestor.CodeReviewRoundInput,
) -> None:
    """Assert both outputs carry the same visible round identity."""
    _assert_request_shape(rendered, authored)
    _assert_visible_identity(rendered, authored, source)
    _assert_visible_authored_content(rendered, authored, source)


def _assert_request_shape(
    rendered: requestor.CodeReviewRequestRender,
    authored: str,
) -> None:
    """Assert the shared envelope and specialized authored section shape."""
    envelope, _ = parse_envelope_markdown(rendered.request_content)
    assert envelope.round_number == _RENDER_ROUND
    assert rendered.request_content.startswith("# Review request for code/code/")
    assert "\n\n## JSON\n\n```json\n" in rendered.request_content
    assert "\n\n## Code review evidence " in authored
    assert authored.startswith("## Review identity")


def test_render_carries_one_canonical_evidence_object_and_round_trips(
    tmp_path: Path,
) -> None:
    """Authored evidence remains distinct from and transparent to the envelope JSON."""
    source = _round_input(tmp_path)
    rendered = requestor.render_code_review_request(source)
    envelope, authored = parse_envelope_markdown(rendered.request_content)
    evidence_text = authored.split("```json\n", 1)[1].split("\n```", 1)[0]

    assert json.loads(evidence_text) == {
        "commit_plan_result": {
            "diagnostics": [],
            "groups": [],
            "ready": True,
            "schema_version": 1,
            "staged_paths": [],
            "state": "valid",
        },
        "request_index_tree": _TREE,
        "resolved_validation_set": {
            "commands": [
                {"command": "ghog day", "sources": ["project"]},
                {"command": "focused Step 1 tests", "sources": ["plan"]},
            ],
        },
    }
    assert json.dumps(json.loads(evidence_text), indent=2, sort_keys=True) == evidence_text
    assert parse_envelope_markdown(rendered.request_content) == (envelope, authored)
    assert f"request_index_tree: {_TREE}" in rendered.transcript_summary
    assert "commit_plan_result:\n\n```text\nstate: valid\nready: true" in rendered.transcript_summary
    assert "resolved_validation_set:\n\n- ghog day" in rendered.transcript_summary
    assert "ghog day (sources: project)" in rendered.transcript_summary


def _assert_visible_identity(
    rendered: requestor.CodeReviewRequestRender,
    authored: str,
    source: requestor.CodeReviewRoundInput,
) -> None:
    """Assert the exact visible plan, step, and round in both artifacts."""
    plan_field = "Implementation plan: " + source.context.document_path.as_posix()
    assert plan_field in authored
    assert plan_field in rendered.transcript_summary
    assert "Implementation step: 1" in authored
    assert "Implementation step: 1" in rendered.transcript_summary
    assert "Review round: 2" in authored
    assert "Review round: 2" in rendered.transcript_summary


def _assert_visible_authored_content(
    rendered: requestor.CodeReviewRequestRender,
    authored: str,
    source: requestor.CodeReviewRoundInput,
) -> None:
    """Assert the umbrella and substantive authored fields stay paired."""
    assert source.context.umbrella_path is not None
    assert "Umbrella draft: " + source.context.umbrella_path.as_posix() in authored
    assert "Added the renderer, launcher, template, and tests." in authored
    assert "Five Step 1 paths are staged for review." in rendered.transcript_summary


def test_render_carries_review_scope_staged_repairs_and_optional_guidance(
    tmp_path: Path,
) -> None:
    """The specialized request preserves bounded repair and staged-state rules."""
    source = _round_input(
        tmp_path,
        umbrella=False,
        guidance="Pay special attention to exact-path validation.",
    )

    rendered = requestor.render_code_review_request(source)
    request_text = rendered.request_content.lower()

    assert "umbrella draft: none" in request_text
    assert "implementation-check" in request_text
    assert "inspect\nthe staged changes" in request_text
    assert "leave each repair staged" in request_text
    assert "name every repaired path" in request_text
    assert "do not commit" in request_text
    assert "a.commit" in request_text
    assert "Human guidance:\n\nPay special attention" in rendered.request_content
    assert "Human guidance:\n\nPay special attention" in rendered.transcript_summary


def test_render_nests_human_guidance_headings_as_a_separate_block(
    tmp_path: Path,
) -> None:
    """Stored guidance headings remain real children of the generated section."""
    guidance = "## Human decision\n\nKeep the repair.\n\n### Evidence"
    rendered = requestor.render_code_review_request(
        _round_input(tmp_path, guidance=guidance),
    )

    assert (
        "Human guidance:\n\n"
        "### Human decision for step 1 code-review-requestor (round 2)"
        in rendered.request_content
    )
    assert (
        "#### Evidence for step 1 code-review-requestor (round 2)"
        in rendered.request_content
    )
    assert (
        "Human guidance:\n\n"
        "#### Human decision for step 1 code-review-requestor (round 2)"
        in rendered.transcript_summary
    )
    assert (
        "##### Evidence for step 1 code-review-requestor (round 2)"
        in rendered.transcript_summary
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("assessment", " ", "assessment must be non-empty"),
        ("implementation_report", "", "implementation report must be non-empty"),
        ("change_summary", "\n", "change summary must be non-empty"),
        ("writer_response", "", "writer response must be non-empty"),
        ("human_guidance", " ", "human guidance must be non-empty"),
        ("request_index_tree", "missing", "request index tree must be a Git tree object"),
    ],
)
def test_round_input_is_frozen_and_rejects_empty_authored_content(
    tmp_path: Path,
    field: str,
    value: str,
    message: str,
) -> None:
    """The pure renderer cannot receive mutable or empty authored input."""
    source = _round_input(tmp_path)
    with pytest.raises(FrozenInstanceError):
        setattr(source, "round_number", 3)
    with pytest.raises(ReviewExchangeError, match=message):
        replace(source, **{field: value})


def test_context_and_round_reject_invalid_identity(tmp_path: Path) -> None:
    """Only exact plans, non-empty steps, and positive rounds are accepted."""
    with pytest.raises(ReviewExchangeError, match="unsupported plan file name"):
        requestor.code_review_context(_plan(tmp_path, "design.v0.11.0.topic.md"), "1")
    with pytest.raises(ReviewExchangeError, match="implementation step"):
        requestor.code_review_context(_plan(tmp_path), " ")
    source = _round_input(tmp_path)
    with pytest.raises(ReviewExchangeError, match="round must be positive"):
        replace(source, round_number=0)
    with pytest.raises(ReviewExchangeError, match="paired request rendering"):
        requestor.CodeReviewRequestRender("", "summary")
    with pytest.raises(ReviewExchangeError, match="resolved validation set"):
        replace(source, resolved_validation_set=None)  # type: ignore[arg-type]


def test_round_rejects_non_code_context(tmp_path: Path) -> None:
    """The specialized renderer rejects a specification-family context."""
    plan = _plan(tmp_path)
    context = ReviewContext(
        ExchangeIdentity(ReviewFamily.SPECIFICATION, "plan", _VERSION, _SLUG),
        plan,
        None,
        None,
    )
    with pytest.raises(ReviewExchangeError, match="code review context"):
        replace(_round_input(tmp_path), context=context)


def test_renderer_reports_template_and_envelope_validation_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing templates and inconsistent shared envelopes fail closed."""
    source = _round_input(tmp_path)
    monkeypatch.setattr(requestor, "_TEMPLATE_PATH", tmp_path / "missing.md")
    with pytest.raises(ReviewExchangeError, match="cannot read request template"):
        requestor.render_code_review_request(source)

    monkeypatch.undo()
    parse = requestor.parse_envelope_markdown

    def mismatched(markdown: str) -> tuple[requestor.Envelope, str]:
        """Return one valid but wrong envelope for the rendered request."""
        envelope, authored = parse(markdown)
        return replace(envelope, round_number=envelope.round_number + 1), authored

    monkeypatch.setattr(requestor, "parse_envelope_markdown", mismatched)
    with pytest.raises(ReviewExchangeError, match="shared envelope validation"):
        requestor.render_code_review_request(source)


def _cli_files(tmp_path: Path) -> dict[str, Path]:
    """Create five ignored authored inputs and two paired output paths."""
    home = tmp_path / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    files = {
        "assessment": home / "a.assessment.md",
        "report": home / "a.report.md",
        "changes": home / "a.changes.md",
        "response": home / "a.response.md",
        "guidance": home / "a.guidance.md",
        "content": home / "a.request-content.md",
        "summary": home / "a.request-summary.md",
    }
    for key in ("assessment", "report", "changes", "response", "guidance"):
        files[key].write_text(f"{key} content\n", encoding="utf-8")
    return files


def _cli_args(plan: Path, files: dict[str, Path]) -> list[str]:
    """Return the explicit code-review renderer command contract."""
    return [
        "--plan", str(plan), "--implementation-step", "1", "--round-number", "3",
        "--assessment-file", str(files["assessment"]),
        "--implementation-report-file", str(files["report"]),
        "--change-summary-file", str(files["changes"]),
        "--writer-response-file", str(files["response"]),
        "--guidance-file", str(files["guidance"]),
        "--plan-validation-command", "focused Step 1 tests",
        "--request-validation-command", "request audit",
        "--request-content-output", str(files["content"]),
        "--transcript-summary-output", str(files["summary"]),
    ]


def _always_ignored(_root: Path, _path: Path) -> bool:
    """Treat exact caller-owned paths as ignored in isolated CLI tests."""
    return True


def _git_path(_name: str) -> str:
    """Return a deterministic Git executable for subprocess seams."""
    return "git"


def _captured_tree(_root: Path) -> str:
    """Return a deterministic request-time index identity."""
    return _TREE


def _checked_plan(_root: Path) -> CommitPlanCheckResult:
    """Return deterministic ready evidence at the command checker seam."""
    return _READY_RESULT


def _no_git(_name: str) -> None:
    """Represent a host where Git cannot be located."""


@pytest.mark.parametrize("return_code", [0, 1])
def test_git_ignore_validation_uses_exact_subprocess_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    return_code: int,
) -> None:
    """Git ignore validation maps the fixed command's exact return code."""
    calls: list[tuple[object, ...]] = []

    def fake_run(*args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return subprocess.CompletedProcess([], return_code)

    monkeypatch.setattr(requestor.shutil, "which", _git_path)
    monkeypatch.setattr(requestor.subprocess, "run", fake_run)
    ignored = requestor._is_effectively_ignored(tmp_path, tmp_path / "a.input.md")
    assert ignored is (return_code == 0)
    assert calls


def test_git_ignore_validation_reports_missing_git_and_launch_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unavailable Git and process errors retain stable diagnostics."""
    monkeypatch.setattr(requestor.shutil, "which", _no_git)
    with pytest.raises(ReviewExchangeError, match="git was not found"):
        requestor._is_effectively_ignored(tmp_path, tmp_path / "a.input.md")

    def fail_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        message = "git failed"
        raise OSError(message)

    monkeypatch.setattr(requestor.shutil, "which", _git_path)
    monkeypatch.setattr(requestor.subprocess, "run", fail_run)
    with pytest.raises(ReviewExchangeError, match="cannot validate ignored file"):
        requestor._is_effectively_ignored(tmp_path, tmp_path / "a.input.md")


def test_cli_reads_and_writes_every_explicit_path_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The command performs one read per input and one write per output."""
    files = _cli_files(tmp_path)
    reads: list[Path] = []
    writes: list[Path] = []
    original_read = requestor._read_utf8
    original_write = requestor._write_utf8

    def counted_read(path: Path, label: str) -> str:
        reads.append(path)
        return original_read(path, label)

    def counted_write(path: Path, content: str, label: str) -> None:
        writes.append(path)
        original_write(path, content, label)

    monkeypatch.setattr(requestor, "_is_effectively_ignored", _always_ignored)
    monkeypatch.setattr(requestor, "format_local_timestamp", lambda: _TIMESTAMP)
    monkeypatch.setattr(requestor, "capture_index_tree", _captured_tree)
    monkeypatch.setattr(requestor, "check_commit_plan", _checked_plan)
    monkeypatch.setattr(requestor, "_read_utf8", counted_read)
    monkeypatch.setattr(requestor, "_write_utf8", counted_write)

    assert requestor.main(_cli_args(_plan(tmp_path), files), project_root=tmp_path) == 0
    assert reads == [files[key] for key in ("assessment", "report", "changes", "response", "guidance")]
    assert writes == [files["content"], files["summary"]]
    assert "Implementation step: 1" in files["summary"].read_text(encoding="utf-8")
    assert f"request_index_tree: {_TREE}" in files["summary"].read_text(encoding="utf-8")
    assert "request audit (sources: request)" in files["summary"].read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("malformed", "implementation report file is not valid UTF-8"),
        ("nested", "request content output must be in the review artifact home"),
        ("tracked", "request content output is not effectively ignored"),
        ("duplicate", "input and output paths must be distinct"),
    ],
)
def test_cli_rejects_unsafe_or_inconsistent_paths_before_writing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mutation: str,
    message: str,
) -> None:
    """Invalid UTF-8, root, ignore, and distinctness failures leave no pair."""
    files = _cli_files(tmp_path)
    if mutation == "malformed":
        files["report"].write_bytes(b"\xff")
    elif mutation == "nested":
        (tmp_path / "nested").mkdir()
        files["content"] = tmp_path / "nested" / "a.request.md"
    elif mutation == "duplicate":
        files["summary"] = files["content"]

    def ignored(_root: Path, path: Path) -> bool:
        return not (mutation == "tracked" and path == files["content"])

    monkeypatch.setattr(requestor, "_is_effectively_ignored", ignored)
    result = requestor.main(_cli_args(_plan(tmp_path), files), project_root=tmp_path)

    assert result == _FATAL_EXIT
    assert message in capsys.readouterr().err
    assert not files["content"].exists()
    assert not files["summary"].exists()


def test_cli_rejects_invalid_round_and_non_root_input(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Invalid round flags and nested authored inputs fail at the boundary."""
    files = _cli_files(tmp_path)
    monkeypatch.setattr(requestor, "_is_effectively_ignored", _always_ignored)
    args = _cli_args(_plan(tmp_path), files)
    args[args.index("3")] = "0"
    assert requestor.main(args, project_root=tmp_path) == _FATAL_EXIT
    assert "value must be positive" in capsys.readouterr().err

    args[args.index("0")] = "not-a-number"
    assert requestor.main(args, project_root=tmp_path) == _FATAL_EXIT
    assert "value must be positive" in capsys.readouterr().err

    (tmp_path / "nested").mkdir()
    files["response"] = tmp_path / "nested" / "a.response.md"
    files["response"].write_text("response\n", encoding="utf-8")
    assert requestor.main(_cli_args(_plan(tmp_path), files), project_root=tmp_path) == _FATAL_EXIT
    assert "writer response file must be in the review artifact home" in capsys.readouterr().err


def test_root_and_io_helpers_cover_defensive_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing inputs, invalid names, directories, and OS failures stay safe."""
    monkeypatch.setattr(requestor, "_is_effectively_ignored", _always_ignored)
    home = tmp_path / ".reviews"
    home.mkdir()
    with pytest.raises(ReviewExchangeError, match="does not exist"):
        requestor._root_file(
            tmp_path, home / "a.missing.md", "assessment file", input_file=True,
        )
    with pytest.raises(ReviewExchangeError, match=r"a\.\* name"):
        requestor._root_file(
            tmp_path, home / "output.md", "request output", input_file=False,
        )

    directory = home / "a.directory"
    directory.mkdir()
    with pytest.raises(ReviewExchangeError, match="must not be a directory"):
        requestor._root_file(
            tmp_path, directory, "request output", input_file=False,
        )
    with pytest.raises(ReviewExchangeError, match="cannot read assessment file"):
        requestor._read_utf8(directory, "assessment file")
    malformed = home / "a.malformed.md"
    malformed.write_bytes(b"\xff")
    with pytest.raises(ReviewExchangeError, match="assessment file is not valid UTF-8"):
        requestor._read_utf8(malformed, "assessment file")
    with pytest.raises(ReviewExchangeError, match="cannot write request output"):
        requestor._write_utf8(directory, "content", "request output")


# eof
