"""Tests for the Step 4 non-interactive review-exchange command interface.

The tests inject a shared fake lifecycle facade so command parsing, caller-owned input,
result rendering, progress routing, and exit classification never wait in real
time or duplicate core state behavior.
"""

# ruff: noqa: S105

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from tools import review_exchange_cli as cli
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_wait import WaitOutcome

from .review_exchange_cli_fake_core import FakeCore

if TYPE_CHECKING:
    from pathlib import Path

_EXIT_FATAL = 2
_EXIT_STOP = 3
_SECOND_EXCHANGE = 2


def _runtime(tmp_path: Path, *, enabled: bool = True) -> tuple[cli.Runtime, FakeCore]:
    """Build one typed injected runtime and fake facade."""
    document = tmp_path / "docs/v0.11.0/plan.v0.11.0.topic.md"
    document.parent.mkdir(parents=True)
    document.write_text("# plan\n", encoding="utf-8")
    identity = ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", "topic")
    context = ReviewContext(identity, document, None, "4")
    policy = FamilyPolicy("approved", "Rework", "Commit")
    configuration = ReviewConfiguration(enabled, 30)
    paths = derive_artifact_paths(tmp_path, context)
    record = CoordinationRecord(
        context,
        policy,
        CoordinationStatus.ACTIVE,
        Actor.REQUESTOR,
        Actor.REVIEWER,
        1,
        "2026-08-04T20:00:00+02:00",
    )
    core = FakeCore(record)
    return cli.Runtime(tmp_path, context, paths, configuration, core), core


def _common(runtime: cli.Runtime) -> list[str]:
    """Return common exact-context arguments for one command."""
    return [
        "--family",
        "code",
        "--document",
        str(runtime.context.document_path),
        "--implementation-step",
        "4",
        "--convergence-signal",
        "approved",
        "--another-round-label",
        "Rework",
        "--continue-owning-workflow-label",
        "Commit",
    ]


def _input_files(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create ignored-name caller inputs for content, summary, and guidance."""
    home = tmp_path / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    content = home / "a.review-content.md"
    summary = home / "a.review-summary.md"
    guidance = home / "a.review-guidance.md"
    content.write_text("content", encoding="utf-8")
    summary.write_text("summary", encoding="utf-8")
    guidance.write_text("guidance", encoding="utf-8")
    return content, summary, guidance


def test_status_exposes_the_current_request_exchange_occurrence(tmp_path: Path) -> None:
    """A reviewer gets the renderer discriminator without reading a transcript."""
    runtime, core = _runtime(tmp_path)
    core.state = ArtifactState.REQUEST_PENDING
    runtime.paths.transcript.write_text(
        "# Review transcript\n\n"
        "<!-- review-entry-id: request-step-4-round-1 -->\n\n"
        "<!-- review-entry-id: request-step-4-round-1-exchange-2 -->\n",
        encoding="utf-8",
    )

    payload = cli._success_payload(runtime, "status", cli.OperationResult("observed"))

    assert payload["exchange_occurrence"] == _SECOND_EXCHANGE


def _run(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    runtime: cli.Runtime,
    argv: list[str],
) -> tuple[int, dict[str, Any], str]:
    """Run main with a fixed root/runtime and parse its one stdout object."""
    def fixed_root(_start: Path) -> Path:
        return runtime.project_root

    def fixed_runtime(_args: object, _root: Path) -> cli.Runtime:
        return runtime

    def ignored(_root: Path, _path: Path) -> bool:
        return True

    def valid_activation(_root: Path, _paths: object) -> None:
        return None

    monkeypatch.setattr(cli, "find_project_root", fixed_root)
    monkeypatch.setattr(cli, "_build_runtime", fixed_runtime)
    monkeypatch.setattr(cli, "_is_effectively_ignored", ignored)
    monkeypatch.setattr(cli, "validate_activation", valid_activation)
    code = cli.main(argv)
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert len(lines) == 1
    return code, json.loads(lines[0]), captured.err


def _expected_result_state(operation: str) -> str:
    """Return the state scripted by one successful operation."""
    return {
        "wait-request": ArtifactState.REQUEST_PENDING.value,
        "wait-answer": ArtifactState.ANSWER_PENDING.value,
    }.get(operation, ArtifactState.ROUND_IN_PROGRESS.value)


def _last_call_name(core: FakeCore) -> str | None:
    """Return the last delegated method name when one exists."""
    return core.calls[-1][0] if core.calls else None


def _assert_progress_channel(operation: str, error: str) -> None:
    """Assert only wait operations emit the scripted progress diagnostic."""
    if operation.startswith("wait-"):
        assert json.loads(error)["progress"]["elapsed_seconds"] == 1.0
    else:
        assert error == ""


def _assert_common_payload(
    payload: dict[str, Any],
    operation: str,
    runtime: cli.Runtime,
) -> None:
    """Check the stable final JSON fields shared by successful operations."""
    assert payload["operation"] == operation
    assert payload["identity"] == runtime.context.identity.to_dict()
    assert payload["state"] == _expected_result_state(operation)
    assert payload["round"] == 1
    assert set(payload["paths"]) == {
        "answer",
        "coordination",
        "request",
        "tombstone",
        "transcript",
        "transition_lock",
    }
    assert payload["diagnostic"]


def _assert_inputs_retained(content: Path, summary: Path, guidance: Path) -> None:
    """Check that the CLI never deletes caller-owned inputs."""
    assert content.exists()
    assert summary.exists()
    assert guidance.exists()


@pytest.mark.parametrize(
    ("operation", "extra", "expected_call"),
    [
        ("activate", [], None),
        ("status", [], None),
        ("start", [], "start"),
        (
            "publish-request",
            ["--content-file", "CONTENT", "--summary-file", "SUMMARY"],
            "publish_request",
        ),
        (
            "amend-request",
            ["--content-file", "CONTENT", "--summary-file", "SUMMARY"],
            "amend_request",
        ),
        (
            "publish-answer",
            ["--content-file", "CONTENT", "--summary-file", "SUMMARY"],
            "publish_answer",
        ),
        (
            "repair-request-transcript",
            ["--summary-file", "SUMMARY"],
            "repair_current_request_transcript",
        ),
        ("wait-request", ["--timeout-seconds", "5"], "wait_for_exact"),
        ("wait-answer", ["--timeout-seconds", "5"], "wait_for_exact"),
        (
            "consume-answer",
            ["--reviewed-work-changed", "false", "--disagreement"],
            "consume_answer",
        ),
        ("continue", [], "continue_round"),
        ("reclaim", [], "reclaim"),
        ("pickup", [], "pickup_ownership"),
        ("escalate", ["--summary-file", "SUMMARY"], "escalate"),
        (
            "confirm",
            ["--choice-label", "Commit", "--guidance-file", "GUIDANCE"],
            "confirm",
        ),
        ("cancel", ["--summary-file", "SUMMARY"], "cancel"),
        ("resolve", ["--summary-file", "SUMMARY"], "resolve_escalation"),
        ("archive", ["--summary-file", "SUMMARY"], "resolve_escalation"),
        ("complete", [], "complete"),
    ],
)
def test_operations_delegate_and_emit_stable_json(  # noqa: PLR0913
    operation: str,
    extra: list[str],
    expected_call: str | None,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Every operation emits the common schema and delegates only its action."""
    runtime, core = _runtime(tmp_path)
    content, summary, guidance = _input_files(tmp_path)
    replacements = {
        "CONTENT": str(content),
        "SUMMARY": str(summary),
        "GUIDANCE": str(guidance),
    }
    concrete = [replacements.get(value, value) for value in extra]
    code, payload, error = _run(
        monkeypatch,
        capsys,
        runtime,
        [operation, *_common(runtime), *concrete],
    )

    assert code == 0
    _assert_common_payload(payload, operation, runtime)
    assert _last_call_name(core) == expected_call
    _assert_progress_channel(operation, error)
    _assert_inputs_retained(content, summary, guidance)


def test_operation_specific_values_reach_core(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Boolean, guidance, archive, and exact wait values retain their types."""
    runtime, core = _runtime(tmp_path)
    _, summary, guidance = _input_files(tmp_path)

    _run(
        monkeypatch,
        capsys,
        runtime,
        [
            "consume-answer",
            *_common(runtime),
            "--reviewed-work-changed",
            "false",
            "--disagreement",
        ],
    )
    assert core.calls[-1] == (
        "consume_answer",
        (),
        {"reviewed_work_changed": False, "disagreement": True},
    )

    _run(
        monkeypatch,
        capsys,
        runtime,
        [
            "confirm",
            *_common(runtime),
            "--choice-label",
            "Commit",
            "--guidance-file",
            str(guidance),
        ],
    )
    assert core.calls[-1] == ("confirm", ("Commit",), {"guidance": "guidance"})

    _run(
        monkeypatch,
        capsys,
        runtime,
        ["archive", *_common(runtime), "--summary-file", str(summary)],
    )
    assert core.calls[-1] == (
        "resolve_escalation",
        ("summary",),
        {"archive": True},
    )


@pytest.mark.parametrize(
    "state",
    [
        ArtifactState.CONVERGENCE_GATE,
        ArtifactState.OWNING_ACTION_PENDING,
        ArtifactState.ESCALATED,
        ArtifactState.ABANDONED_REQUEST,
        ArtifactState.INCONSISTENT,
        ArtifactState.TRANSCRIPT_REPAIR_PENDING,
    ],
)
def test_status_maps_expected_protocol_stops_to_exit_three(
    state: ArtifactState,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Durable gates and stopped states are machine-readable exit 3 results."""
    runtime, core = _runtime(tmp_path)
    core.state = state
    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["status", *_common(runtime)],
    )
    assert code == _EXIT_STOP
    assert payload["state"] == state.value


def test_disabled_mode_is_an_expected_stop_without_activation(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """An absent marker reports disabled and never calls the lifecycle facade."""
    runtime, core = _runtime(tmp_path, enabled=False)
    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["start", *_common(runtime)],
    )
    assert code == _EXIT_STOP
    assert payload["state"] == "disabled"
    assert payload["outcome"] == "disabled"
    assert core.calls == []


@pytest.mark.parametrize(
    "outcome",
    [
        WaitOutcome.TIMED_OUT,
        WaitOutcome.ABANDONED,
        WaitOutcome.ESCALATED,
        WaitOutcome.INCONSISTENT,
        WaitOutcome.REPAIR_REQUIRED,
    ],
)
def test_wait_non_success_outcomes_exit_three(
    outcome: WaitOutcome,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Each bounded non-success result remains data, not a fatal parse error."""
    runtime, core = _runtime(tmp_path)
    core.wait_outcome = outcome
    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["wait-answer", *_common(runtime)],
    )
    assert code == _EXIT_STOP
    assert payload["outcome"] == outcome.value


def test_invalid_arguments_and_fatal_errors_emit_one_json_object(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Parser, protocol, and unexpected failures use exit 2 and stdout JSON."""
    code = cli.main(["status"])
    first = capsys.readouterr()
    assert code == _EXIT_FATAL
    assert json.loads(first.out)["outcome"] == "fatal-input"

    runtime, core = _runtime(tmp_path)
    core.fail = ReviewExchangeError("bad protocol input")
    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["status", *_common(runtime)],
    )
    assert code == _EXIT_FATAL
    assert payload["diagnostic"] == "bad protocol input"

    core.fail = RuntimeError("unexpected failure")
    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["status", *_common(runtime)],
    )
    assert code == _EXIT_FATAL
    assert payload["diagnostic"] == "unexpected failure"


def test_input_files_must_be_ignored_home_local_a_names(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Caller Markdown is validated before its single UTF-8 read and retained."""
    home = tmp_path / ".reviews"
    home.mkdir()
    valid = home / "a.valid.md"
    valid.write_text("hello", encoding="utf-8")
    def ignored(_root: Path, _path: Path) -> bool:
        return True

    monkeypatch.setattr(cli, "_is_effectively_ignored", ignored)
    assert cli._read_input_file(tmp_path, valid, "content") == "hello"
    assert valid.exists()

    with pytest.raises(ReviewExchangeError, match="review artifact home"):
        cli._read_input_file(tmp_path, tmp_path / "nested/a.bad.md", "content")
    bad_name = home / "content.md"
    bad_name.write_text("bad", encoding="utf-8")
    with pytest.raises(ReviewExchangeError, match=r"a\.\*"):
        cli._read_input_file(tmp_path, bad_name, "content")
    def visible(_root: Path, _path: Path) -> bool:
        return False

    monkeypatch.setattr(cli, "_is_effectively_ignored", visible)
    with pytest.raises(ReviewExchangeError, match="effectively ignored"):
        cli._read_input_file(tmp_path, valid, "content")


def test_context_is_inferred_from_exact_document_name(tmp_path: Path) -> None:
    """Code and specification identities come from the selected exact file."""
    code = tmp_path / "plan.v0.11.0.topic.md"
    design = tmp_path / "design.v0.11.0.topic.md"
    code.write_text("# plan\n", encoding="utf-8")
    design.write_text("# design\n", encoding="utf-8")

    code_context = cli._context_from_document("code", code, None, "4")
    spec_context = cli._context_from_document(
        "specification",
        design,
        None,
        None,
    )
    assert code_context.identity.to_dict() == {
        "family": "code",
        "type_token": "code",
        "version": "v0.11.0",
        "slug": "topic",
    }
    assert spec_context.identity.type_token == "design-specification"
    with pytest.raises(ReviewExchangeError, match="file name"):
        cli._context_from_document("code", tmp_path / "README.md", None, "4")


# eof
