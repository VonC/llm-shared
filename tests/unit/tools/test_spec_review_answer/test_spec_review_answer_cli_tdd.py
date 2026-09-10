"""TDD contracts for the fixed-path specification answer CLI."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from tools import spec_review_answer_cli as answer_cli
from tools.review_exchange_models_envelope import parse_envelope_markdown

_FATAL_EXIT = 2
_TIMESTAMP = "2026-08-11T11:00:00+02:00"
_ROUND = 2


def _files(tmp_path: Path) -> dict[str, Path]:
    """Create exact authored inputs and paired output paths."""
    home = tmp_path / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    files = {
        "assessment": home / "a.assessment.md",
        "verdicts": home / "a.question-verdicts.md",
        "instructions": home / "a.writer-instructions.md",
        "changes": home / "a.requested-changes.md",
        "guidance": home / "a.human-guidance.md",
        "guidance_response": home / "a.guidance-response.md",
        "answer": home / "a.answer-content.md",
        "summary": home / "a.answer-summary.md",
        "manifest": home / "a.retained-context.json",
    }
    content = {
        "assessment": "The plan is sound.\n",
        "verdicts": "Q01: choose A.\n",
        "instructions": "Clarify Q02.\n",
        "changes": "Name the recovery owner.\n",
        "guidance": "Keep Q01 settled.\n",
        "guidance_response": "Q01 remains settled.\n",
    }
    for name, value in content.items():
        files[name].write_text(value, encoding="utf-8")
    return files


def _document(tmp_path: Path) -> Path:
    """Create one reviewed plan and return its exact path."""
    docs = tmp_path / "docs" / "v0.11.0"
    docs.mkdir(parents=True)
    document = docs / "plan.v0.11.0.answer-cli.md"
    document.write_text("# Plan\n\nStable content.\n", encoding="utf-8")
    return document


def _digest(document: Path) -> str:
    """Return the lowercase SHA-256 expected by the command."""
    return hashlib.sha256(document.read_bytes()).hexdigest()


def _args(document: Path, files: dict[str, Path]) -> list[str]:
    """Return the explicit change-request command arguments."""
    return [
        "--document", str(document),
        "--round-number", "2",
        "--disposition", "changes-requested",
        "--expected-document-sha256", _digest(document),
        "--assessment-file", str(files["assessment"]),
        "--question-verdicts-file", str(files["verdicts"]),
        "--writer-instructions-file", str(files["instructions"]),
        "--requested-changes-file", str(files["changes"]),
        "--guidance-file", str(files["guidance"]),
        "--guidance-response-file", str(files["guidance_response"]),
        "--answer-content-output", str(files["answer"]),
        "--transcript-summary-output", str(files["summary"]),
    ]


def _ignored(_root: Path, _path: Path) -> bool:
    """Treat isolated caller paths as effectively ignored."""
    return True


def _git_path(_name: str) -> str:
    """Return a deterministic Git executable for process-seam tests."""
    return "git"


def _no_git(_name: str) -> None:
    """Represent a host where Git cannot be located."""
    return


def _mutate_argument_case(
    mutation: str,
    args: list[str],
    files: dict[str, Path],
) -> None:
    """Apply one parser or collision mutation without burdening the test body."""
    if mutation == "invalid-disposition":
        args[args.index("changes-requested")] = "approved"
    elif mutation == "invalid-round":
        args[args.index("2")] = "0"
    elif mutation == "collision":
        args[args.index(str(files["summary"]))] = str(files["answer"])


def _mutate_file_case(
    mutation: str,
    args: list[str],
    document: Path,
    files: dict[str, Path],
    tmp_path: Path,
) -> None:
    """Apply one encoding, location, or reviewed-content mutation."""
    if mutation == "bad-utf8":
        files["assessment"].write_bytes(b"\xff")
    elif mutation == "nested-input":
        nested = tmp_path / "nested"
        nested.mkdir()
        moved = nested / files["assessment"].name
        files["assessment"].replace(moved)
        args[args.index(str(files["assessment"]))] = str(moved)
    elif mutation == "drift":
        document.write_text("# Changed\n", encoding="utf-8")


def test_cli_reads_exact_inputs_and_writes_one_valid_pair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The command renders validated UTF-8 outputs without publication."""
    document = _document(tmp_path)
    files = _files(tmp_path)
    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)
    monkeypatch.setattr(answer_cli, "format_local_timestamp", lambda: _TIMESTAMP)

    result = answer_cli.main(_args(document, files), project_root=tmp_path)

    assert result == 0
    answer = files["answer"].read_text(encoding="utf-8")
    summary = files["summary"].read_text(encoding="utf-8")
    envelope, _ = parse_envelope_markdown(answer)
    assert envelope.round_number == _ROUND
    assert "Name the recovery owner." in answer
    assert "Name the recovery owner." in summary
    assert "Q01 remains settled." in answer


def test_cli_accepts_matching_retained_manifest_from_an_earlier_round(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fresh-round rendering reuses retained findings only with exact context."""
    document = _document(tmp_path)
    files = _files(tmp_path)
    manifest = {
        "document_sha256": _digest(document),
        "identity": {
            "family": "specification",
            "type_token": "plan",
            "version": "v0.11.0",
            "slug": "answer-cli",
        },
        "original_round_number": 1,
        "assessment_input_paths": [
            files[name].resolve().as_posix()
            for name in (
                "assessment", "verdicts", "instructions", "changes",
                "guidance", "guidance_response",
            )
        ],
    }
    files["manifest"].write_text(json.dumps(manifest), encoding="utf-8")
    args = [
        *_args(document, files),
        "--retained-manifest-file",
        str(files["manifest"]),
    ]
    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)
    monkeypatch.setattr(answer_cli, "format_local_timestamp", lambda: _TIMESTAMP)

    assert answer_cli.main(args, project_root=tmp_path) == 0
    assert files["manifest"].exists(), "renderer CLI must not retire caller evidence"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("invalid-disposition", "invalid disposition"),
        ("invalid-round", "value must be positive"),
        ("bad-utf8", "assessment file is not valid UTF-8"),
        ("nested-input", "assessment file must be in the review artifact home"),
        ("tracked-output", "answer content output is not effectively ignored"),
        ("drift", "reviewed document content drifted"),
        ("collision", "caller paths must be distinct"),
    ],
)
def test_cli_rejects_invalid_trust_inputs_without_partial_outputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mutation: str,
    message: str,
) -> None:
    """Invalid disposition, round, files, drift, or collisions write nothing."""
    document = _document(tmp_path)
    files = _files(tmp_path)
    args = _args(document, files)

    def ignored(_root: Path, path: Path) -> bool:
        return not (mutation == "tracked-output" and path == files["answer"])

    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", ignored)
    _mutate_argument_case(mutation, args, files)
    _mutate_file_case(mutation, args, document, files, tmp_path)

    assert answer_cli.main(args, project_root=tmp_path) == _FATAL_EXIT
    assert message in capsys.readouterr().err
    assert not files["answer"].exists()
    assert not files["summary"].exists()


def test_cli_rejects_stale_or_malformed_manifest_without_writing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Retained evidence must be UTF-8 JSON matching the exact current digest."""
    document = _document(tmp_path)
    files = _files(tmp_path)
    files["manifest"].write_text("{}", encoding="utf-8")
    args = [
        *_args(document, files),
        "--retained-manifest-file",
        str(files["manifest"]),
    ]
    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)

    assert answer_cli.main(args, project_root=tmp_path) == _FATAL_EXIT
    assert "retained manifest" in capsys.readouterr().err
    assert not files["answer"].exists()
    assert not files["summary"].exists()


def test_cli_rejects_a_boolean_manifest_round(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A JSON boolean cannot pass as a positive retained round number."""
    document = _document(tmp_path)
    files = _files(tmp_path)
    manifest: dict[str, object] = {
        "document_sha256": _digest(document),
        "identity": {
            "family": "specification",
            "type_token": "plan",
            "version": "v0.11.0",
            "slug": "answer-cli",
        },
        "original_round_number": True,
        "assessment_input_paths": [],
    }
    files["manifest"].write_text(json.dumps(manifest), encoding="utf-8")
    args = [*_args(document, files), "--retained-manifest-file", str(files["manifest"])]
    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)

    assert answer_cli.main(args, project_root=tmp_path) == _FATAL_EXIT
    assert "retained manifest original round" in capsys.readouterr().err
    assert not files["answer"].exists()
    assert not files["summary"].exists()


def test_paired_write_rolls_back_when_second_publication_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A second replace failure cannot leave only one renderer output visible."""
    document = _document(tmp_path)
    files = _files(tmp_path)
    files["answer"].write_text("previous answer\n", encoding="utf-8")
    files["summary"].write_text("previous summary\n", encoding="utf-8")
    real_replace = answer_cli.os.replace
    output_replaces = 0

    def fail_second(source: str | Path, target: str | Path) -> None:
        nonlocal output_replaces
        if Path(target) in {files["answer"], files["summary"]}:
            output_replaces += 1
            if output_replaces == _ROUND:
                message = "simulated second output failure"
                raise OSError(message)
        real_replace(source, target)

    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)
    monkeypatch.setattr(answer_cli, "format_local_timestamp", lambda: _TIMESTAMP)
    monkeypatch.setattr(answer_cli.os, "replace", fail_second)

    assert answer_cli.main(_args(document, files), project_root=tmp_path) == _FATAL_EXIT
    assert "cannot write paired outputs" in capsys.readouterr().err
    assert files["answer"].read_text(encoding="utf-8") == "previous answer\n"
    assert files["summary"].read_text(encoding="utf-8") == "previous summary\n"


@pytest.mark.parametrize("return_code", [0, 1])
def test_git_ignore_check_uses_fixed_command_and_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    return_code: int,
) -> None:
    """The ignore seam uses fixed Git arguments and maps its exact result."""
    calls: list[object] = []

    def fake_run(*args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.extend(args)
        return subprocess.CompletedProcess([], return_code)

    monkeypatch.setattr(answer_cli.shutil, "which", _git_path)
    monkeypatch.setattr(answer_cli.subprocess, "run", fake_run)

    assert answer_cli._is_effectively_ignored(tmp_path, tmp_path / "a.input.md") is (
        return_code == 0
    )
    assert calls


def test_git_ignore_check_reports_missing_git_and_process_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unavailable Git and launch failures have stable diagnostics."""
    monkeypatch.setattr(answer_cli.shutil, "which", _no_git)
    with pytest.raises(answer_cli.ReviewExchangeError, match="git was not found"):
        answer_cli._is_effectively_ignored(tmp_path, tmp_path / "a.input.md")

    def fail_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        message = "git process failed"
        raise OSError(message)

    monkeypatch.setattr(answer_cli.shutil, "which", _git_path)
    monkeypatch.setattr(answer_cli.subprocess, "run", fail_run)
    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot validate ignored file"):
        answer_cli._is_effectively_ignored(tmp_path, tmp_path / "a.input.md")


@pytest.mark.parametrize(
    ("kind", "message"),
    [
        ("bad-name", "must use an a.* file name"),
        ("missing", "does not exist"),
        ("output-directory", "is not a regular file"),
    ],
)
def test_root_path_rejects_bad_names_missing_sources_and_directories(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    message: str,
) -> None:
    """Exact root validation rejects every remaining defensive path shape."""
    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)
    home = tmp_path / ".reviews"
    home.mkdir()
    path = home / ("input.md" if kind == "bad-name" else "a.input.md")
    source = kind != "output-directory"
    if kind == "bad-name":
        path.write_text("input\n", encoding="utf-8")
    elif kind == "output-directory":
        path.mkdir()

    with pytest.raises(answer_cli.ReviewExchangeError, match=message):
        answer_cli._root_path(tmp_path, path, "test path", source=source)


def test_utf8_and_temporary_output_helpers_report_io_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Direct IO failures are normalized before renderer output is visible."""
    directory = tmp_path / "a.directory"
    directory.mkdir()
    with pytest.raises(answer_cli.argparse.ArgumentTypeError, match="value must be positive"):
        answer_cli._positive_int("not-a-number")
    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot read assessment"):
        answer_cli._read_utf8(directory, "assessment")
    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot read reviewed document"):
        answer_cli._document_sha256(directory)

    def fail_temp(**_kwargs: object) -> None:
        message = "temporary output denied"
        raise OSError(message)

    monkeypatch.setattr(answer_cli.tempfile, "NamedTemporaryFile", fail_temp)
    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot prepare paired outputs"):
        answer_cli._temp_output(tmp_path / "a.output.md", "content")


def test_paired_write_removes_new_first_output_when_second_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Rollback removes a newly visible first output when no prior pair existed."""
    answer = tmp_path / "a.answer.md"
    summary = tmp_path / "a.summary.md"
    real_replace = answer_cli.os.replace
    output_replaces = 0

    def fail_second(source: str | Path, target: str | Path) -> None:
        nonlocal output_replaces
        if Path(target) in {answer, summary}:
            output_replaces += 1
            if output_replaces == _ROUND:
                message = "simulated second output failure"
                raise OSError(message)
        real_replace(source, target)

    monkeypatch.setattr(answer_cli.os, "replace", fail_second)

    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot write paired outputs"):
        answer_cli._write_pair(answer, "answer", summary, "summary")
    assert not answer.exists()
    assert not summary.exists()


@pytest.mark.parametrize(
    ("manifest", "message"),
    [
        ("{", "invalid retained manifest JSON"),
        ("[]", "must be a JSON object"),
        (
            json.dumps(
                {
                    "document_sha256": "digest",
                    "identity": {},
                    "original_round_number": 0,
                    "assessment_input_paths": [],
                },
            ),
            "retained manifest original round",
        ),
        (
            json.dumps(
                {
                    "document_sha256": "digest",
                    "identity": {},
                    "original_round_number": _ROUND + 1,
                    "assessment_input_paths": [],
                },
            ),
            "invalid original round",
        ),
        (
            json.dumps(
                {
                    "document_sha256": "stale",
                    "identity": {},
                    "original_round_number": 1,
                    "assessment_input_paths": [],
                },
            ),
            "differs from current context",
        ),
    ],
)
def test_retained_manifest_rejects_malformed_or_stale_context(
    manifest: str,
    message: str,
) -> None:
    """Every retained-manifest defensive branch fails closed."""
    with pytest.raises(answer_cli.ReviewExchangeError, match=message):
        answer_cli._validate_manifest(
            manifest,
            digest="digest",
            identity={},
            round_number=2,
            input_paths=[],
        )


def test_document_and_context_validation_reject_bad_encoding_root_and_digest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Reviewed bytes, project root, and expected digest each fail independently."""
    document = _document(tmp_path)
    document.write_bytes(b"\xff")
    with pytest.raises(answer_cli.ReviewExchangeError, match="not valid UTF-8"):
        answer_cli._document_sha256(document)

    files = _files(tmp_path)
    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)
    missing_root = tmp_path / "missing-root"
    assert answer_cli.main(_args(document, files), project_root=missing_root) == _FATAL_EXIT
    assert "project root is not a directory" in capsys.readouterr().err

    document.write_text("# Plan\n", encoding="utf-8")
    args = _args(document, files)
    args[args.index(_digest(document))] = "not-a-digest"
    assert answer_cli.main(args, project_root=tmp_path) == _FATAL_EXIT
    assert "expected document SHA-256 is invalid" in capsys.readouterr().err
