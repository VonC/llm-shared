"""Batch source wiring and direct Python CLI contracts for Markdown checks."""

# ruff: noqa: S603, S607

from __future__ import annotations

from typing import TYPE_CHECKING

from tools import prompt_workflow_steps as steps
from tools.markdown_check import cli
from tools.markdown_check.runner import CheckerResult

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_root_launcher_source_self_locates_and_preserves_status() -> None:
    """Inspect the shim's wiring without interpreting or executing shell syntax."""
    source = (steps.llm_shared_dir() / "markdown-check.bat").read_text(encoding="utf-8")
    assert 'set "MARKDOWN_CHECK_ROOT=%~dp0"' in source
    assert '"%MARKDOWN_CHECK_PYTHON%" -m tools.markdown_check.cli %*' in source
    assert 'set "MARKDOWN_CHECK_STATUS=%ERRORLEVEL%"' in source
    assert "exit /b %MARKDOWN_CHECK_STATUS%" in source


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
