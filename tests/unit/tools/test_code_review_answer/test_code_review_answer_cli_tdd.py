"""TDD contracts for fixed-path code-review answer CLI boundaries.

The full assessment journey runs in fixture setup so its bounded file reads and
writes do not make the measured assertion call depend on Windows IO jitter.
"""

from __future__ import annotations

import os
import subprocess
from argparse import Namespace
from pathlib import Path

import pytest

from tools import code_review_answer_cli as answer_cli
from tools.code_review_evidence import CodeReviewEvidence
from tools.review_exchange_models import ReviewExchangeError
from tools.review_exchange_models_envelope import parse_envelope_markdown

_FATAL = 2
_ROUND = 2
_TIMESTAMP = "2026-08-17T19:10:00+02:00"
_BASELINE = "a" * 40
_ASSESSED = "b" * 40


def _document(tmp_path: Path) -> Path:
    """Create one exact implementation plan."""
    docs = tmp_path / "docs" / "v0.11.0"
    docs.mkdir(parents=True)
    plan = docs / "plan.v0.11.0.answer-cli.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    return plan


def _files(tmp_path: Path) -> dict[str, Path]:
    """Create every explicit caller input and paired output path."""
    home = tmp_path / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    names = {
        "disagreement": "The request index differs.",
        "implementation_check": "Yes. Step 4 has been fully implemented.",
        "validation_effects": "Only Step 4 rows changed.",
        "pre_repair_validation": "ghog day: fail=0 cov=100.",
        "resolved_validation_set": "ghog day (sources: Step 4).",
        "resolver_drift": "No drift; direction unchanged.",
        "repository_state": "Tracked state stayed stable.",
        "repairs": "Added one assertion.",
        "staged_paths": "tests/unit/tools/test_answer.py",
        "commit_plan": "a.commit is exact.",
        "unresolved": "Writer reassessment remains.",
        "boundary_work": "None.",
        "instructions": "Publish another review round.",
        "rationale": "A substantive repair requires another round.",
        "guidance": "Inspect generated files.",
        "guidance_response": "Generated files were inspected.",
    }
    files = {key: home / f"a.{key}.md" for key in names}
    for key, content in names.items():
        files[key].write_text(content + "\n", encoding="utf-8")
    files.update(
        {
            "manifest": home / "a.code-review-evidence.v0.11.0.answer-cli.step-4.json",
            "answer": home / "a.answer.md",
            "summary": home / "a.summary.md",
        },
    )
    files["manifest"].write_text("{}\n", encoding="utf-8")
    return files


def _common(plan: Path, files: dict[str, Path], kind: str) -> list[str]:
    """Return common exact-context and paired-output arguments."""
    return [
        "--document", str(plan),
        "--implementation-step", "4",
        "--round-number", "2",
        "--exchange-occurrence", "1",
        "--answer-kind", kind,
        "--disposition", "changes-requested",
        "--writer-instructions-file", str(files["instructions"]),
        "--guidance-file", str(files["guidance"]),
        "--guidance-response-file", str(files["guidance_response"]),
        "--answer-content-output", str(files["answer"]),
        "--transcript-summary-output", str(files["summary"]),
    ]


def _assessment_args(plan: Path, files: dict[str, Path]) -> list[str]:
    """Return the full-assessment command contract."""
    args = _common(plan, files, "assessment")
    for flag, key in (
        ("implementation-check", "implementation_check"),
        ("validation-plan-effects", "validation_effects"),
        ("pre-repair-validation", "pre_repair_validation"),
        ("resolved-validation-set", "resolved_validation_set"),
        ("resolver-drift", "resolver_drift"),
        ("repository-state-comparison", "repository_state"),
        ("repairs", "repairs"),
        ("staged-paths", "staged_paths"),
        ("commit-plan-assessment", "commit_plan"),
        ("unresolved-findings", "unresolved"),
        ("boundary-crossing-work", "boundary_work"),
        ("decision-rationale", "rationale"),
        ("retained-manifest", "manifest"),
    ):
        args.extend((f"--{flag}-file", str(files[key])))
    args.extend(("--substantive-repair", "--readiness-floor-incomplete"))
    return args


def _early_args(plan: Path, files: dict[str, Path]) -> list[str]:
    """Return the early-rejection command contract."""
    return [
        *_common(plan, files, "early-rejection"),
        "--disagreement-file", str(files["disagreement"]),
    ]


def _ignored(_root: Path, _path: Path) -> bool:
    return True


def _manifest() -> CodeReviewEvidence:
    return CodeReviewEvidence(
        family="code",
        type_token="code",  # noqa: S106 - protocol identity token, not a password
        version="v0.11.0",
        slug="answer-cli",
        implementation_step="4",
        baseline_index_tree=_BASELINE,
        assessed_index_tree=_ASSESSED,
    )


def _install_assessment_seams(monkeypatch: pytest.MonkeyPatch, files: dict[str, Path]) -> None:
    """Install deterministic ignored-path, manifest, tree, and time seams."""
    def retained_path(
        _repository: str | Path,
        _identity: tuple[str, str, str, str, str],
    ) -> Path:
        return files["manifest"]

    def retained_manifest(
        _repository: str | Path,
        _identity: tuple[str, str, str, str, str],
    ) -> CodeReviewEvidence:
        return _manifest()

    def assessed_tree(_repository: str | Path) -> str:
        return _ASSESSED

    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)
    monkeypatch.setattr(answer_cli, "format_local_timestamp", lambda: _TIMESTAMP)
    monkeypatch.setattr(answer_cli, "manifest_path", retained_path)
    monkeypatch.setattr(answer_cli, "read_manifest", retained_manifest)
    monkeypatch.setattr(answer_cli, "capture_index_tree", assessed_tree)


def _mutate_case(  # noqa: C901 - explicit matrix keeps each trust boundary visible
    mutation: str,
    args: list[str],
    files: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Apply one isolated trust-boundary mutation without branching in the test."""
    def mixed() -> None:
        args.extend(("--implementation-check-file", str(files["implementation_check"])))

    def missing() -> None:
        index = args.index("--implementation-check-file")
        del args[index:index + _ROUND]

    def wrong_manifest() -> None:
        def other_path(
            _repository: str | Path,
            _identity: tuple[str, str, str, str, str],
        ) -> Path:
            return tmp_path / "a.other.json"

        monkeypatch.setattr(answer_cli, "manifest_path", other_path)

    def drifted_index() -> None:
        def drifted(_repository: str | Path) -> str:
            return "c" * 40

        monkeypatch.setattr(answer_cli, "capture_index_tree", drifted)

    def bad_utf8() -> None:
        files["implementation_check"].write_bytes(b"\xff")

    def collision() -> None:
        args[args.index(str(files["summary"]))] = str(files["answer"])

    def tracked_output() -> None:
        def ignored(_root: Path, path: Path) -> bool:
            return path != files["answer"]

        monkeypatch.setattr(answer_cli, "_is_effectively_ignored", ignored)

    def early_missing() -> None:
        index = args.index("--disagreement-file")
        del args[index:index + _ROUND]

    def early_flag() -> None:
        args.append("--substantive-repair")

    def assessment_mixed() -> None:
        args.extend(("--disagreement-file", str(files["disagreement"])))

    def writer_missing() -> None:
        index = args.index("--writer-instructions-file")
        del args[index:index + _ROUND]

    def guidance_unpaired() -> None:
        index = args.index("--guidance-response-file")
        del args[index:index + _ROUND]

    mutations = {
        "mixed": mixed,
        "missing": missing,
        "manifest-path": wrong_manifest,
        "index-drift": drifted_index,
        "bad-utf8": bad_utf8,
        "collision": collision,
        "tracked": tracked_output,
        "early-missing": early_missing,
        "early-flag": early_flag,
        "assessment-mixed": assessment_mixed,
        "writer-missing": writer_missing,
        "guidance-unpaired": guidance_unpaired,
    }
    mutations[mutation]()


@pytest.fixture
def assessment_render_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, Path]:
    """Run the full assessment render outside the measured assertion call."""
    plan = _document(tmp_path)
    files = _files(tmp_path)
    _install_assessment_seams(monkeypatch, files)

    assert answer_cli.main(_assessment_args(plan, files), project_root=tmp_path) == 0
    return files


def test_assessment_cli_validates_manifest_index_and_writes_one_pair(
    assessment_render_journey: dict[str, Path],
) -> None:
    """Full assessment verifies retained evidence without retiring it."""
    files = assessment_render_journey
    envelope, _ = parse_envelope_markdown(files["answer"].read_text(encoding="utf-8"))
    assert envelope.round_number == _ROUND
    assert "Added one assertion." in files["summary"].read_text(encoding="utf-8")
    assert files["manifest"].is_file(), "rendering must not retire live evidence"


def test_assessment_cli_accepts_a_manifest_inside_the_artifact_home(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Retained evidence renders from the configured home, not only the root."""
    plan = _document(tmp_path)
    files = _files(tmp_path)
    home_manifest = files["manifest"]
    _install_assessment_seams(monkeypatch, files)

    assert answer_cli.main(_assessment_args(plan, files), project_root=tmp_path) == 0
    assert home_manifest.is_file(), "rendering must not retire live evidence"


def test_home_local_input_still_rejects_a_path_outside_the_repository(
    tmp_path: Path,
) -> None:
    """Accepting the artifact home keeps every other directory closed."""
    outside = tmp_path.parent / "a.code-review-evidence.v0.11.0.answer-cli.step-4.json"

    with pytest.raises(ReviewExchangeError, match="review artifact home"):
        answer_cli._root_path(  # noqa: SLF001
            tmp_path,
            outside,
            "retained manifest file",
            source=True,
        )


def test_early_rejection_needs_no_manifest_or_assessment_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Early rejection renders through the narrow pre-assessment variant."""
    plan = _document(tmp_path)
    files = _files(tmp_path)
    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)
    monkeypatch.setattr(answer_cli, "format_local_timestamp", lambda: _TIMESTAMP)

    assert answer_cli.main(_early_args(plan, files), project_root=tmp_path) == 0
    answer = files["answer"].read_text(encoding="utf-8")
    assert "The request index differs." in answer
    assert "Pre-repair validation" not in answer


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("mixed", "cannot carry assessment evidence"),
        ("missing", "implementation check file is required"),
        ("manifest-path", "exact live evidence manifest"),
        ("index-drift", "assessed index tree differs"),
        ("bad-utf8", "implementation check file is not valid UTF-8"),
        ("collision", "caller paths must be distinct"),
        ("tracked", "answer content output is not effectively ignored"),
        ("early-missing", "disagreement file is required"),
        ("early-flag", "cannot carry assessment flags"),
        ("assessment-mixed", "assessment cannot carry disagreement"),
        ("writer-missing", "writer instructions file is required"),
        ("guidance-unpaired", "guidance and guidance response files must be paired"),
    ],
)
def test_cli_rejects_mixed_missing_stale_or_untrusted_inputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mutation: str,
    message: str,
) -> None:
    """Every trust or variant failure returns two and writes no output."""
    plan = _document(tmp_path)
    files = _files(tmp_path)
    early = mutation in {"mixed", "early-missing", "early-flag", "guidance-unpaired"}
    args = _early_args(plan, files) if early else _assessment_args(plan, files)
    _install_assessment_seams(monkeypatch, files)
    _mutate_case(mutation, args, files, monkeypatch, tmp_path)

    assert answer_cli.main(args, project_root=tmp_path) == _FATAL
    assert message in capsys.readouterr().err
    assert not files["answer"].exists()
    assert not files["summary"].exists()


def test_cli_parser_context_and_path_helpers_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Parser, root, file-shape, and strict-read failures use fatal diagnostics."""
    assert answer_cli.main([], project_root=tmp_path) == _FATAL
    assert "required" in capsys.readouterr().err
    for value in ("invalid", "0"):
        with pytest.raises(Exception, match="positive"):
            answer_cli._positive_int(value)
    with pytest.raises(Exception, match="invalid disposition"):
        answer_cli._disposition("approved")

    monkeypatch.setattr(answer_cli, "_is_effectively_ignored", _ignored)
    home = tmp_path / ".reviews"
    home.mkdir()
    nested = tmp_path / "nested" / "a.input.md"
    with pytest.raises(answer_cli.ReviewExchangeError, match="review artifact home"):
        answer_cli._root_path(tmp_path, nested, "input", source=True)
    with pytest.raises(answer_cli.ReviewExchangeError, match=r"a.\*"):
        answer_cli._root_path(tmp_path, home / "input.md", "input", source=False)
    with pytest.raises(answer_cli.ReviewExchangeError, match="does not exist"):
        answer_cli._root_path(tmp_path, home / "a.missing.md", "input", source=True)
    directory = home / "a.directory"
    directory.mkdir()
    with pytest.raises(answer_cli.ReviewExchangeError, match="not a regular file"):
        answer_cli._root_path(tmp_path, directory, "output", source=False)
    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot read"):
        answer_cli._read_utf8(directory, "directory")


def test_git_ignore_and_temporary_output_failures_are_explicit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Git and filesystem failures cannot silently weaken the output boundary."""
    target = tmp_path / "a.output.md"

    def git_path(_name: str) -> str:
        return "git"

    def completed(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 0, "", "")

    def missing_git(_name: str) -> None:
        return None

    def failed_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        message = "git failed"
        raise OSError(message)

    monkeypatch.setattr(answer_cli.shutil, "which", git_path)
    monkeypatch.setattr(answer_cli.subprocess, "run", completed)
    assert answer_cli._is_effectively_ignored(tmp_path, target)
    monkeypatch.setattr(answer_cli.shutil, "which", missing_git)
    with pytest.raises(answer_cli.ReviewExchangeError, match="git was not found"):
        answer_cli._is_effectively_ignored(tmp_path, target)
    monkeypatch.setattr(answer_cli.shutil, "which", git_path)
    monkeypatch.setattr(answer_cli.subprocess, "run", failed_run)
    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot validate ignored"):
        answer_cli._is_effectively_ignored(tmp_path, target)

    def failed_temp(*_args: object, **_kwargs: object) -> None:
        message = "temporary output failed"
        raise OSError(message)

    monkeypatch.setattr(answer_cli.tempfile, "NamedTemporaryFile", failed_temp)
    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot prepare paired outputs"):
        answer_cli._temp_output(target, "content")


def test_assessment_source_rejects_missing_step_and_render_rejects_bad_root(
    tmp_path: Path,
) -> None:
    """The assessment and render boundaries require a step and directory root."""
    plan = _document(tmp_path)
    context = answer_cli.code_review_context(plan, "4")
    object.__setattr__(context, "implementation_step", None)
    with pytest.raises(answer_cli.ReviewExchangeError, match="step must be present"):
        answer_cli._assessment_source(
            Namespace(),
            tmp_path,
            context,
            {},
            {},
        )
    root_file = tmp_path / "root-file"
    root_file.write_text("root\n", encoding="utf-8")
    files = _files(tmp_path)
    assert answer_cli.main(_early_args(plan, files), project_root=root_file) == _FATAL


def test_paired_write_removes_new_first_output_when_second_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Rollback restores absence when the first output did not exist before."""
    answer = tmp_path / "a.answer.md"
    summary = tmp_path / "a.summary.md"
    summary.write_text("old summary\n", encoding="utf-8")
    real_replace = os.replace
    calls = 0

    def fail_second(source: str | Path, target: str | Path) -> None:
        nonlocal calls
        if Path(target) in {answer, summary}:
            calls += 1
            if calls == _ROUND:
                message = "second output failed"
                raise OSError(message)
        real_replace(source, target)

    monkeypatch.setattr(answer_cli.os, "replace", fail_second)
    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot write paired outputs"):
        answer_cli._write_pair(answer, "new answer", summary, "new summary")
    assert not answer.exists()
    assert summary.read_text(encoding="utf-8") == "old summary\n"


def test_cli_reads_each_authored_input_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One assessment phase reads no caller-authored input more than once."""
    plan = _document(tmp_path)
    files = _files(tmp_path)
    _install_assessment_seams(monkeypatch, files)
    reads: dict[Path, int] = {}
    real_read = answer_cli._read_utf8

    def counted(path: Path, label: str) -> str:
        reads[path] = reads.get(path, 0) + 1
        return real_read(path, label)

    monkeypatch.setattr(answer_cli, "_read_utf8", counted)

    assert answer_cli.main(_assessment_args(plan, files), project_root=tmp_path) == 0
    assert reads
    assert set(reads.values()) == {1}


def test_paired_write_restores_prior_outputs_after_second_replace_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A partial publication failure restores the exact prior pair."""
    answer = tmp_path / "a.answer.md"
    summary = tmp_path / "a.summary.md"
    answer.write_text("old answer\n", encoding="utf-8")
    summary.write_text("old summary\n", encoding="utf-8")
    real_replace = os.replace
    calls = 0

    def fail_second(source: str | Path, target: str | Path) -> None:
        nonlocal calls
        if Path(target) in {answer, summary}:
            calls += 1
            if calls == _ROUND:
                message = "second output failed"
                raise OSError(message)
        real_replace(source, target)

    monkeypatch.setattr(answer_cli.os, "replace", fail_second)
    with pytest.raises(answer_cli.ReviewExchangeError, match="cannot write paired outputs"):
        answer_cli._write_pair(answer, "new answer", summary, "new summary")
    assert answer.read_text(encoding="utf-8") == "old answer\n"
    assert summary.read_text(encoding="utf-8") == "old summary\n"


# eof
