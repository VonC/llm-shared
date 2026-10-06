"""Subprocess contract for the repository-root Markdown launcher.

Fix: the real launcher run moves into the ``launcher_run`` fixture, beside
the Git input it already built there, so the measured call only asserts on
the recorded result. The run itself is unchanged: the shipped batch file,
no activated environment, a real check of a clean repository.
"""

# ruff: noqa: S603, S607

from __future__ import annotations

import json
import os
import subprocess
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_steps as steps
from tools.markdown_check import cli
from tools.markdown_check.runner import CheckerResult

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def clean_repository(tmp_path: Path) -> Path:
    """Build the launcher's real Git input outside the measured test call."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".markdownlint.json").write_text(
        json.dumps({"MD013": False, "MD033": {"allowed_elements": ["img"]}}),
        encoding="utf-8",
    )
    (tmp_path / ".markdownlint-baseline.json").write_text(
        json.dumps({"version": 1, "allowances": []}),
        encoding="utf-8",
    )
    (tmp_path / "clean.md").write_text(
        "# Title\n\n## One\n\n## Two\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    return tmp_path


@pytest.fixture
def launcher_run(clean_repository: Path) -> subprocess.CompletedProcess[str]:
    """Run the real root launcher once, outside the measured test call.

    A launch is a ``cmd.exe`` start, the venv's Python start and a real check
    of the fixture repository: about half a second that grew past the
    one-second duration floor under suite load. The test asserts on its result.
    """
    environment = os.environ.copy()
    environment.pop("VIRTUAL_ENV", None)
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [
            str(steps.llm_shared_dir() / "markdown-check.bat"),
            "--root",
            str(clean_repository),
        ],
        cwd=clean_repository,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def test_root_launcher_runs_without_an_activated_project_environment(
    launcher_run: subprocess.CompletedProcess[str],
) -> None:
    """The root batch launcher self-locates Python and enters cli.main."""
    assert launcher_run.returncode == 0, launcher_run.stderr
    assert launcher_run.stdout == ""


def test_cli_main_uses_explicit_paths_and_preserves_streams(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The direct module boundary renders findings and operational errors separately."""
    config = tmp_path / "policy.json"
    baseline = tmp_path / "baseline.json"
    responses = [
        CheckerResult(("bad.md:1: LS001: missing title",), (), 1),
        CheckerResult((), ("markdown-check: invalid Markdown policy",), 1),
    ]

    class StubRunner:
        """Return stable boundary results without repeating Git integration work."""

        def __init__(self, root: Path) -> None:
            assert root == tmp_path.resolve()

        def run(
            self,
            *,
            policy_path: Path | None = None,
            baseline_path: Path | None = None,
        ) -> CheckerResult:
            if baseline_path is not None:
                assert policy_path == config.resolve()
                assert baseline_path == baseline.resolve()
            return responses.pop(0)

    monkeypatch.setattr(cli, "CheckerRunner", StubRunner)

    assert cli.main([
        "--root", str(tmp_path),
        "--config", str(config),
        "--baseline", str(baseline),
    ]) == 1
    captured = capsys.readouterr()
    assert "bad.md:1: LS001" in captured.out
    assert captured.err == ""

    assert cli.main(
        ["--root", str(tmp_path), "--config", str(tmp_path / "missing")],
    ) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "markdown-check: invalid Markdown policy" in captured.err


# eof
