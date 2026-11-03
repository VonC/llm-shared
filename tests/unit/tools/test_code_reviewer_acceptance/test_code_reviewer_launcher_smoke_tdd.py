"""Direct public CLI help and explicit source contracts for batch wiring."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

import pytest

# ruff: noqa: S603

_LAUNCHERS = (
    ("code_review_request.bat", "code_review_request", "usage: code-review-request"),
    ("code_review_evidence.bat", "code_review_evidence_cli", "usage: code-review-evidence"),
    ("code_review_answer.bat", "code_review_answer_cli", "usage: code_review_answer_cli.py"),
)


@pytest.mark.parametrize(("launcher", "module", "usage"), _LAUNCHERS)
def test_public_entry_point_help_and_launcher_source(
    launcher: str,
    module: str,
    usage: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Requirement AC08: exercise CLI help and launcher delegation without a shell."""
    source = (Path("bin") / launcher).read_text(encoding="utf-8")
    assert f"tools\\{module}.py" in source
    assert "%~dp0.." in source
    assert "%*" in source
    monkeypatch.setattr(sys, "argv", [f"{module}.py"])
    with pytest.raises(SystemExit) as stopped:
        import_module(f"tools.{module}").main(["--help"])
    assert stopped.value.code == 0
    assert usage in capsys.readouterr().out
