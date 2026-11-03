"""Readiness output and nonmutation over declared repository observations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.commit_plan_check.commit_plan_check_support import (
    NON_READY_STATUS,
    RepositoryState,
    human_fragments,
    initialize_repository,
    run_adapter,
    snapshot,
    stage_sample,
    valid_plan,
)

if TYPE_CHECKING:
    import subprocess


@pytest.fixture(
    params=(
        ("valid", "valid", 0, True),
        ("missing-plan", "missing-plan", NON_READY_STATUS, True),
        ("empty-plan", "empty-plan", NON_READY_STATUS, True),
        ("empty-staged-set", "empty-staged-set", NON_READY_STATUS, False),
        ("mismatch", "invalid-plan", NON_READY_STATUS, True),
    ),
    ids=lambda value: value[0],
)
def evidence_case(
    tmp_path: Path,
    request: pytest.FixtureRequest,
    commit_plan_repository_seed: Path,
) -> tuple[str, int, tuple[subprocess.CompletedProcess[str], ...], RepositoryState, RepositoryState]:
    """Run the production CLI in both formats from an independent baseline."""
    scenario, expected_state, expected_status, stage_sample_file = request.param
    initialize_repository(tmp_path, commit_plan_repository_seed)
    if stage_sample_file:
        stage_sample(tmp_path)
    if scenario in {"valid", "empty-staged-set"}:
        (tmp_path / "a.commit").write_text(valid_plan("sample.txt"), encoding="utf-8")
    elif scenario == "empty-plan":
        (tmp_path / "a.commit").write_bytes(b"")
    elif scenario == "mismatch":
        (tmp_path / "a.commit").write_text(valid_plan("other.txt"), encoding="utf-8")
    before = snapshot(tmp_path)
    results = tuple(run_adapter(tmp_path, output_format)
                    for output_format in ("human", "json"))
    return expected_state, expected_status, results, before, snapshot(tmp_path)


def test_formats_share_status_evidence_and_repository_immutability(
    evidence_case: tuple[
        str,
        int,
        tuple[subprocess.CompletedProcess[str], ...],
        RepositoryState,
        RepositoryState,
    ],
) -> None:
    """All readiness states have format parity and exact before/after state."""
    expected_state, expected_status, results, before, after = evidence_case
    human, structured = results

    assert before == after
    assert {result.returncode for result in results} == {expected_status}
    assert all(result.stderr == "" for result in results)
    payload = json.loads(structured.stdout)
    assert payload["state"] == expected_state
    assert all(fragment in human.stdout for fragment in human_fragments(payload))


def test_launcher_source_delegates_to_checker_and_returns_status() -> None:
    """Check batch wiring as text; runtime policy is exercised through Python."""
    source = (Path(__file__).resolve().parents[4] / "commit-plan-check.bat").read_text(encoding="utf-8")
    assert "tools.commit_plan_check" in source
    assert "%*" in source
    assert "errorlevel" in source.lower()
    assert "exit /b" in source.lower()


# eof
