"""Acceptance evidence for both read-only commit-plan checker entry points.

Step 4 exercises real repositories, exact state snapshots, rename inventory,
caller-owned redirection, operational failures, and request publication gates.
Slow Git setup runs in fixtures so measured assertion calls remain bounded.

Fix: this module now holds only the readiness-state parity scenario, and the
shared builders moved to ``commit_plan_check_support``. The remaining
contract scenarios live in ``test_commit_plan_check_contracts_tdd``, so the
two run on separate xdist workers instead of serializing behind one module.
"""

from __future__ import annotations

import json
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
    from pathlib import Path


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
) -> tuple[str, int, tuple[subprocess.CompletedProcess[str], ...], RepositoryState, RepositoryState]:
    """Run both formats and adapters outside the measured assertion phase."""
    scenario, expected_state, expected_status, stage_sample_file = request.param
    initialize_repository(tmp_path)
    if stage_sample_file:
        stage_sample(tmp_path)
    if scenario in {"valid", "empty-staged-set"}:
        (tmp_path / "a.commit").write_text(valid_plan("sample.txt"), encoding="utf-8")
    elif scenario == "empty-plan":
        (tmp_path / "a.commit").write_bytes(b"")
    elif scenario == "mismatch":
        (tmp_path / "a.commit").write_text(valid_plan("other.txt"), encoding="utf-8")
    before = snapshot(tmp_path)
    results = tuple(
        run_adapter(tmp_path, adapter, output_format)
        for output_format in ("human", "json")
        for adapter in ("module", "launcher")
    )
    return expected_state, expected_status, results, before, snapshot(tmp_path)


def test_entry_points_share_status_evidence_and_repository_immutability(
    evidence_case: tuple[
        str,
        int,
        tuple[subprocess.CompletedProcess[str], ...],
        RepositoryState,
        RepositoryState,
    ],
) -> None:
    """All readiness states have adapter parity and exact before/after state."""
    expected_state, expected_status, results, before, after = evidence_case
    module_human, launcher_human, module_json, launcher_json = results

    assert before == after
    assert {result.returncode for result in results} == {expected_status}
    assert all(result.stderr == "" for result in results)
    assert module_human.stdout == launcher_human.stdout
    assert module_json.stdout == launcher_json.stdout
    payload = json.loads(module_json.stdout)
    assert payload["state"] == expected_state
    assert all(fragment in module_human.stdout for fragment in human_fragments(payload))


# eof
