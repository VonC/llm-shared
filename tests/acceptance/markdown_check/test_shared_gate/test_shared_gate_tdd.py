"""Acceptance contracts for the checked repository and shared gate wiring."""

# ruff: noqa: S603

from __future__ import annotations

import json

from tools import prompt_workflow_steps as steps


def test_shared_gate_records_one_markdown_launcher_failure_path() -> None:
    """check.bat owns one launcher call and one named aggregate failure."""
    source = (steps.llm_shared_dir() / "check.bat").read_text(encoding="utf-8")

    assert source.count('call "%PRJ_DIR%\\markdown-check.bat"') == 1
    assert source.count("call :record_failure markdown %markdown_status%") == 1
    assert 'set "markdown_status=%ERRORLEVEL%"' in source
    assert 'set "markdown_status="' in source


def test_markdown_baseline_contains_only_authorized_rules() -> None:
    """Only confirmed MD033 and file-specific MD038 debt may be allowed."""
    root = steps.llm_shared_dir()
    payload = json.loads(
        (root / ".markdownlint-baseline.json").read_text(encoding="utf-8"),
    )
    allowances = payload["allowances"]
    markdown_rules = {
        allowance["rule"]
        for allowance in allowances
        if str(allowance["rule"]).startswith("MD")
    }
    md038_allowances = [
        allowance for allowance in allowances if allowance["rule"] == "MD038"
    ]

    assert markdown_rules == {"MD033", "MD038"}
    assert md038_allowances == [
        {
            "path": "docs/v0.11.0/review.design-specification.v0.11.0.review-status-command.md",
            "rule": "MD038",
            "count": 2,
        },
    ]


# eof
