"""Evaluate fixture documents with explicitly declared repository inventories."""

# ruff: noqa: S603, S607

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tools.markdown_check import cli
from tools.markdown_check.runner import (
    CheckerResult,
    CheckerRunner,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path


_POLICY = {"MD013": False, "MD033": {"allowed_elements": ["img"]}}
_BASELINE_FINDING_COUNT = 2
_GROWING_FINDING_COUNT = 4
_BASELINE_RELATIVE = "docs/legacy.md"
_BASELINE_STRUCTURE = "# Legacy\n\n## First\n\n{body}\n\n## Second\n"


def _write_repository(
    root: Path,
    files: Mapping[str, str],
    *,
    policy: object = _POLICY,
    allowances: list[dict[str, object]] | None = None,
) -> None:
    """Create one tracked repository with explicit policy and baseline inputs."""
    documents = {
        ".markdownlint.json": json.dumps(policy),
        ".markdownlint-baseline.json": json.dumps(
            {"version": 1, "allowances": allowances or []},
        ),
        **files,
    }
    for relative, content in documents.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _fixed_inventory_runner(root: Path, *paths: str) -> CheckerRunner:
    """Build a checker whose focused inventory avoids redundant Git process I/O."""
    return CheckerRunner(root, inventory_loader=lambda _root: paths)


@pytest.fixture
def complete_repository(tmp_path: Path) -> Path:
    """Build structured and adapter documents outside the measured test call."""
    _write_repository(
        tmp_path,
        {
            "docs/structured.md": (
                "# Structured\n\n## First\n\n### Child\n\n## Second\n"
            ),
            ".claude/skills/example/SKILL.md": (
                "---\ndescription: frontmatter adapter\n---\nBody.\n"
            ),
            ".agents/llm-shared/instructions/pointer.md": (
                "Read [the rule](../../../instructions/rule.md).\n"
            ),
            "instructions/rule.md": "# Rule\n\n## First\n\n## Second\n",
            "templates/fragment.md": "## Fragment\n\n### Child\n",
            "docs/code.md": (
                "# Code examples\n\n## Preserved spaces\n\n"
                "Use `  genuine  `, `   `, and `` `literal` ``.\n\n"
                "Use **strong** for emphasis and quote `__init__.py`.\n\n"
                '## Allowed HTML\n\n<img src="logo.png">\n'
            ),
        },
    )
    return tmp_path


@pytest.fixture
def baseline_repository(tmp_path: Path) -> Path:
    """Build accepted raw-HTML debt outside the measured test call."""
    allowance: list[dict[str, object]] = [
        {
            "path": _BASELINE_RELATIVE,
            "rule": "MD033",
            "count": _BASELINE_FINDING_COUNT,
        },
    ]
    _write_repository(
        tmp_path,
        {
            _BASELINE_RELATIVE: _BASELINE_STRUCTURE.format(
                body="<span>legacy</span>",
            ),
        },
        allowances=allowance,
    )
    return tmp_path


@pytest.fixture
def overlap_repository(tmp_path: Path) -> Path:
    """Build duplicate-heading input outside the measured test call."""
    _write_repository(
        tmp_path,
        {"docs/repeated.md": "# Title\n\n## Repeated\n\n## Repeated\n"},
    )
    return tmp_path


@pytest.fixture
def complete_repository_inventory(complete_repository: Path) -> tuple[str, ...]:
    """Declare tracked documents independently of production inventory discovery."""
    del complete_repository
    return ("docs/structured.md", ".claude/skills/example/SKILL.md",
            ".agents/llm-shared/instructions/pointer.md", "instructions/rule.md",
            "templates/fragment.md", "docs/code.md")


def test_complete_repository_covers_structured_and_adapter_contracts(
    complete_repository: Path, complete_repository_inventory: tuple[str, ...],
) -> None:
    """Structured files, adapters, MD038 exceptions, and allowed img all pass."""
    result = _fixed_inventory_runner(complete_repository, *complete_repository_inventory).run()

    assert result == CheckerResult((), (), 0)


def test_rule_overlap_and_configuration_failure_are_deterministic(
    overlap_repository: Path,
) -> None:
    """Overlapping rules stay independent and policy failure precedes evaluation."""
    runner = _fixed_inventory_runner(overlap_repository, "docs/repeated.md")
    first = runner.run()
    second = runner.run()

    assert first == second
    assert first.stdout == (
        "docs/repeated.md:5: LS003: heading title is not globally unique",
        "docs/repeated.md:5: MD024: duplicate heading content",
    )

    (overlap_repository / ".markdownlint.json").write_text(
        json.dumps({"UNKNOWN": True}),
        encoding="utf-8",
    )
    invalid = runner.run()
    assert invalid.stdout == ()
    assert invalid.stderr[0].startswith("markdown-check: unsupported Markdown rules")


def test_baseline_blocks_growth_and_reports_shrink(
    baseline_repository: Path,
) -> None:
    """An accepted raw-HTML count passes, growth fails, and shrink is visible."""
    runner = _fixed_inventory_runner(baseline_repository, _BASELINE_RELATIVE)

    assert runner.run() == CheckerResult((), (), 0)

    path = baseline_repository / _BASELINE_RELATIVE
    path.write_text(
        _BASELINE_STRUCTURE.format(body="<span>one</span> <span>two</span>"),
        encoding="utf-8",
    )
    growth = runner.run()
    assert growth.exit_code == 1
    assert len(growth.stdout) == _GROWING_FINDING_COUNT

    path.write_text(_BASELINE_STRUCTURE.format(body="plain"), encoding="utf-8")
    shrink = runner.run()
    assert shrink.exit_code == 0
    assert shrink.stderr == (
        "docs/legacy.md: MD033: debt-reduced: baseline 2, actual 0",
    )


def test_cli_returns_failure_for_unbaselined_finding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """The public Python entry preserves real checker findings and status."""
    _write_repository(tmp_path, {"docs/bad.md": "## Only section\n"})
    def selected_runner(root: Path) -> CheckerRunner:
        return _fixed_inventory_runner(root, "docs/bad.md")

    monkeypatch.setattr(cli, "CheckerRunner", selected_runner)
    assert cli.main(["--root", str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "docs/bad.md:1: LS001" in captured.out
    assert captured.err == ""


# eof
