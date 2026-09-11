"""TDD contracts for immutable no-growth baseline comparison."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tools.markdown_check.baseline import BaselineError, load_baseline
from tools.markdown_check.models import Finding

if TYPE_CHECKING:
    from pathlib import Path


def _write(
    tmp_path: Path,
    allowances: object,
    *,
    version: int = 1,
) -> Path:
    path = tmp_path / ".markdownlint-baseline.json"
    path.write_text(
        json.dumps({"version": version, "allowances": allowances}),
        encoding="utf-8",
    )
    return path


def _write_payload(tmp_path: Path, payload: object) -> Path:
    """Write one arbitrary baseline payload for closed-schema tests."""
    path = tmp_path / ".markdownlint-baseline.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_baseline_reports_growth_and_debt_reduction(tmp_path: Path) -> None:
    """New debt blocks while lower counts produce deterministic advisories."""
    baseline = load_baseline(
        _write(
            tmp_path,
            [
                {"path": "docs/a.md", "rule": "LS002", "count": 2},
                {"path": "docs/b.md", "rule": "MD033", "count": 2},
            ],
        ),
    )
    findings = (
        Finding("docs/a.md", 1, "LS002", "sections"),
        Finding("docs/c.md", 4, "MD032", "list"),
    )

    comparison = baseline.compare(findings)

    assert comparison.blocked_findings == (findings[1],)
    assert comparison.advisories == (
        "docs/a.md: LS002: debt-reduced: baseline 2, actual 1",
        "docs/b.md: MD033: debt-reduced: baseline 2, actual 0",
    )


def test_baseline_allows_unchanged_debt(tmp_path: Path) -> None:
    """An actual count equal to its positive allowance passes silently."""
    baseline = load_baseline(
        _write(tmp_path, [{"path": "docs/a.md", "rule": "LS002", "count": 1}]),
    )
    finding = Finding("docs/a.md", 1, "LS002", "sections")

    assert baseline.compare((finding,)).blocked_findings == ()
    assert baseline.compare((finding,)).advisories == ()


@pytest.mark.parametrize(
    ("allowances", "version"),
    [
        ([], 2),
        ([{"path": "docs/a.md", "rule": "NOPE", "count": 1}], 1),
        ([{"path": "docs/a.md", "rule": "LS002", "count": 0}], 1),
        ([{"path": "docs/a.md", "rule": "MD012", "count": 1}], 1),
        ([{"path": "docs/a.md", "rule": "MD024", "count": 1}], 1),
        ([{"path": "docs/a.md", "rule": "MD025", "count": 1}], 1),
        (
            [
                {"path": "docs/a.md", "rule": "LS002", "count": 1},
                {"path": "docs\\a.md", "rule": "LS002", "count": 2},
            ],
            1,
        ),
    ],
)
def test_baseline_rejects_versions_rules_counts_and_duplicates(
    tmp_path: Path,
    allowances: list[dict[str, object]],
    version: int,
) -> None:
    """Malformed allowances cannot weaken the policy boundary."""
    with pytest.raises(BaselineError):
        load_baseline(_write(tmp_path, allowances, version=version))


@pytest.mark.parametrize(
    "allowances",
    [
        [None],
        [{"path": "docs/a.md", "rule": "LS002"}],
        [{"path": 7, "rule": "LS002", "count": 1}],
        [{"path": "../docs/a.md", "rule": "LS002", "count": 1}],
    ],
)
def test_baseline_rejects_malformed_allowance_records(
    tmp_path: Path,
    allowances: object,
) -> None:
    """Every allowance must have typed, complete, repository-local fields."""
    with pytest.raises(BaselineError):
        load_baseline(_write(tmp_path, allowances))


@pytest.mark.parametrize("payload", [[], {"version": 1}])
def test_baseline_rejects_non_object_and_incomplete_documents(
    tmp_path: Path,
    payload: object,
) -> None:
    """The baseline document accepts exactly its versioned closed schema."""
    with pytest.raises(BaselineError):
        load_baseline(_write_payload(tmp_path, payload))


def test_baseline_rejects_invalid_json(tmp_path: Path) -> None:
    """Unreadable JSON cannot silently remove existing debt."""
    path = tmp_path / ".markdownlint-baseline.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(BaselineError, match="invalid Markdown baseline"):
        load_baseline(path)


# eof
