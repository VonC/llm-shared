"""Boundary coverage for the Step 3 review-exchange command adapter.

These tests cover construction, parser limits, Git ignore probing, unreadable
caller inputs, ownership pickup, disabled status, defensive dispatch, and the
script entry point. Lifecycle behavior remains covered by the core and the
primary CLI tests.
"""

from __future__ import annotations

import argparse
import io
import json
import runpy
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from tests.unit.tools.test_review_exchange_cli.test_review_exchange_cli_tdd import (
    _common,
    _run,
    _runtime,
)
from tools import review_exchange_cli as cli
from tools import review_exchange_cli_parser as cli_parser
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import Actor, ArtifactState, ReviewExchangeError
from tools.review_exchange_observer import ExchangeObservation
from tools.review_exchange_ownership import (
    OwnershipCapability,
    OwnershipFailure,
    OwnershipRejectedError,
)

_EXIT_FATAL = 2
_EXIT_STOP = 3
_POSITIVE_FLOAT = 0.5
_POSITIVE_INT = 2
_WAIT_TIMEOUT = 15
_OWNERSHIP_GENERATION = 4
_PICKED_UP_GENERATION = 2
_REJECTED_GENERATION = 3


def test_positive_number_parsers_reject_zero() -> None:
    """Wait durations and intervals must be positive before dispatch."""
    assert cli_parser.positive_int("2") == _POSITIVE_INT
    assert cli_parser.positive_float("0.5") == _POSITIVE_FLOAT
    with pytest.raises(argparse.ArgumentTypeError, match="positive"):
        cli_parser.positive_int("0")
    with pytest.raises(argparse.ArgumentTypeError, match="positive"):
        cli_parser.positive_float("-1")


def test_code_context_rejects_a_non_plan_document(tmp_path: Path) -> None:
    """The code family cannot reinterpret a specification file as a plan."""
    document = tmp_path / "design.v0.11.0.topic.md"
    document.write_text("# design\n", encoding="utf-8")
    with pytest.raises(ReviewExchangeError, match="exact plan"):
        cli._context_from_document("code", document, None, "4")


def test_build_runtime_constructs_the_real_core(tmp_path: Path) -> None:
    """Exact parsed context builds one configured production facade."""
    injected, _ = _runtime(tmp_path)
    (tmp_path / "a.review-mode").write_text(
        "wait_timeout_seconds=15\n",
        encoding="utf-8",
    )
    args = cli._parser().parse_args(["status", *_common(injected)])

    runtime = cli._build_runtime(args, tmp_path)

    assert runtime.project_root == tmp_path
    assert runtime.configuration.wait_timeout_seconds == _WAIT_TIMEOUT
    assert isinstance(runtime.core, ReviewExchangeCore)


def test_cli_passes_paired_ownership_flags_without_echoing_them(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """A mutation validates the supplied pair without returning its old secret."""
    runtime, core = _runtime(tmp_path)
    token = "session-token-value-0123456789abcdef"  # noqa: S105

    code, payload, error = _run(
        monkeypatch,
        capsys,
        runtime,
        [
            "continue",
            *_common(runtime),
            "--ownership-generation",
            "4",
            "--ownership-token",
            token,
        ],
    )

    assert code == 0
    assert core.ownership_capability == OwnershipCapability(
        _OWNERSHIP_GENERATION,
        token,
    )
    assert "ownership_generation" not in payload
    assert "ownership_token" not in payload
    assert error == ""


def test_ownership_stop_never_echoes_presented_capability(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """A rejected stale capability is absent from the final stop payload."""
    runtime, core = _runtime(tmp_path)
    capability_secret = "stale-token-value-0123456789abcd"  # noqa: S105
    core.fail = OwnershipRejectedError(
        OwnershipFailure(
            "ownership-superseded",
            "ownership capability was superseded",
            _REJECTED_GENERATION,
        ),
    )

    code, payload, _error = _run(
        monkeypatch,
        capsys,
        runtime,
        [
            "continue",
            *_common(runtime),
            "--ownership-generation",
            "2",
            "--ownership-token",
            capability_secret,
        ],
    )

    assert code == _EXIT_STOP
    assert payload["outcome"] == "ownership-superseded"
    assert payload["current_ownership_generation"] == _REJECTED_GENERATION
    assert "ownership_generation" not in payload
    assert "ownership_token" not in payload


@pytest.mark.parametrize(
    "state",
    [
        ArtifactState.CONVERGENCE_GATE,
        ArtifactState.OWNING_ACTION_PENDING,
    ],
)
def test_new_session_pickup_claims_requestor_at_owning_workflow_gates(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    state: ArtifactState,
) -> None:
    """A fresh requestor session can replace its missing capability at a gate."""
    runtime, core = _runtime(tmp_path)
    core.state = state
    core.record = replace(core.record, expected_next_actor=Actor.HUMAN)

    code, payload, _error = _run(
        monkeypatch,
        capsys,
        runtime,
        ["pickup", *_common(runtime)],
    )

    assert code == _EXIT_STOP
    assert payload["outcome"] == "ownership-picked-up"
    assert payload["ownership_generation"] == _PICKED_UP_GENERATION
    assert isinstance(payload["ownership_token"], str)
    assert core.calls[-1] == ("pickup_ownership", (Actor.REQUESTOR,), {})


def test_new_session_pickup_uses_expected_llm_actor_during_a_round(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Pickup keeps normal round ownership aligned with the expected actor."""
    runtime, core = _runtime(tmp_path)
    core.state = ArtifactState.REQUEST_PENDING

    code, payload, _error = _run(
        monkeypatch,
        capsys,
        runtime,
        ["pickup", *_common(runtime)],
    )

    assert code == 0
    assert payload["outcome"] == "ownership-picked-up"
    assert core.calls[-1] == ("pickup_ownership", (Actor.REVIEWER,), {})


def test_pickup_without_coordination_reports_a_fatal_input(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """A pickup needs a durable record to name the actor it hands ownership to."""
    runtime, core = _runtime(tmp_path)
    no_exchange = ExchangeObservation(
        ArtifactState.IDLE,
        None,
        None,
        None,
        "no exchange",
    )
    monkeypatch.setattr(core, "classify", lambda: no_exchange)

    code, payload, _error = _run(
        monkeypatch,
        capsys,
        runtime,
        ["pickup", *_common(runtime)],
    )

    assert code == _EXIT_FATAL
    assert payload["diagnostic"] == "ownership pickup requires durable coordination"
    assert [name for name, _args, _kwargs in core.calls] == []


def test_effective_ignore_probe_uses_fixed_git_arguments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The probe handles found, visible, missing-Git, and process errors."""
    path = tmp_path / "a.input.md"
    path.write_text("input", encoding="utf-8")
    commands: list[list[str]] = []

    def git_path(_name: str) -> str:
        return "C:/Git/bin/git.exe"

    def run_git(command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(cli.shutil, "which", git_path)
    monkeypatch.setattr(cli.subprocess, "run", run_git)
    assert cli._is_effectively_ignored(tmp_path, path) is True
    assert commands[0][-2:] == ["--", "a.input.md"]

    def visible_git(
        command: list[str],
        **_kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, "", "")

    monkeypatch.setattr(cli.subprocess, "run", visible_git)
    assert cli._is_effectively_ignored(tmp_path, path) is False
    def no_git(_name: str) -> None:
        return None

    monkeypatch.setattr(cli.shutil, "which", no_git)
    with pytest.raises(ReviewExchangeError, match="git was not found"):
        cli._is_effectively_ignored(tmp_path, path)

    def broken_git(_command: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise OSError

    monkeypatch.setattr(cli.shutil, "which", git_path)
    monkeypatch.setattr(cli.subprocess, "run", broken_git)
    with pytest.raises(ReviewExchangeError, match="cannot validate ignored input"):
        cli._is_effectively_ignored(tmp_path, path)


def test_input_reader_reports_missing_and_invalid_utf8(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Caller input failures become typed diagnostics before core delegation."""
    def ignored(_root: Path, _path: Path) -> bool:
        return True

    monkeypatch.setattr(cli, "_is_effectively_ignored", ignored)
    home = tmp_path / ".reviews"
    home.mkdir()
    with pytest.raises(ReviewExchangeError, match="does not exist"):
        cli._read_input_file(tmp_path, home / "a.missing.md", "summary")
    invalid = home / "a.invalid.md"
    invalid.write_bytes(b"\xff")
    with pytest.raises(ReviewExchangeError, match="UTF-8"):
        cli._read_input_file(tmp_path, invalid, "summary")


def test_dispatch_covers_disabled_status_and_unknown_operation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Disabled status is expected while an unknown internal operation fails."""
    disabled, _ = _runtime(tmp_path, enabled=False)
    result = cli._dispatch(argparse.Namespace(operation="status"), disabled, io.StringIO())
    assert result.outcome == "disabled"
    assert result.exit_code == _EXIT_STOP

    active, _ = _runtime(tmp_path / "active")

    def valid_activation(_root: Path, _paths: object) -> None:
        return None

    monkeypatch.setattr(cli, "validate_activation", valid_activation)
    with pytest.raises(ReviewExchangeError, match="unsupported operation"):
        cli._dispatch(argparse.Namespace(operation="unknown"), active, io.StringIO())


def test_forced_reclaim_requires_its_authorized_summary_pairing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Only `--force` with `--summary-file` delegates one forced resume."""
    runtime, core = _runtime(tmp_path)
    home = tmp_path / ".reviews"
    home.mkdir()
    summary = home / "a.review-summary.md"
    summary.write_text("Manual back-and-forth resume.", encoding="utf-8")

    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["reclaim", *_common(runtime), "--force", "--summary-file", str(summary)],
    )

    assert code == 0
    assert payload["outcome"] == "force-reclaimed"
    assert core.calls[-1] == ("force_reclaim", ("Manual back-and-forth resume.",), {})

    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["reclaim", *_common(runtime), "--force"],
    )
    assert code == _EXIT_FATAL
    assert "--summary-file" in payload["diagnostic"]

    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["reclaim", *_common(runtime), "--summary-file", str(summary)],
    )
    assert code == _EXIT_FATAL
    assert "only with --force" in payload["diagnostic"]


def test_forced_completion_requires_its_authorized_summary_pairing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Only --force with --summary-file delegates forced completion."""
    runtime, core = _runtime(tmp_path)
    home = tmp_path / ".reviews"
    home.mkdir()
    summary = home / "a.completion-summary.md"
    summary.write_text("The human closes the abandoned round.", encoding="utf-8")

    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["complete", *_common(runtime), "--force", "--summary-file", str(summary)],
    )

    assert code == 0
    assert payload["outcome"] == "force-completed"
    assert payload["removed"] is True
    assert core.calls[-1] == (
        "force_complete",
        ("The human closes the abandoned round.",),
        {},
    )

    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["complete", *_common(runtime), "--force"],
    )
    assert code == _EXIT_FATAL
    assert "--summary-file" in payload["diagnostic"]

    code, payload, _ = _run(
        monkeypatch,
        capsys,
        runtime,
        ["complete", *_common(runtime), "--summary-file", str(summary)],
    )
    assert code == _EXIT_FATAL
    assert "only with --force" in payload["diagnostic"]


def test_script_entry_point_returns_fatal_json(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Direct script execution exits through main and retains its JSON result."""
    monkeypatch.setattr(sys, "argv", ["review_exchange_cli.py", "status"])
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(str(Path(cli.__file__)), run_name="__main__")
    assert raised.value.code == _EXIT_FATAL
    assert json.loads(capsys.readouterr().out)["outcome"] == "fatal-input"


# eof
