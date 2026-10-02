"""Unit tests for the groundhog run evidence (v0.13.0 full_suite_levels).

Step 2: the closing keys of a day walk (``full= src= proof= reused= scope=``),
of a direct full run (no ``reused=``) and of any other run (``scope=`` alone),
with ``unproven`` for an absent proof; the running keys with ``proof=pending``;
the evidence each invocation carries, a step inside a walk carrying its scope
only; and the outcome defaults of a run without a pytest child.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools.groundhog import evidence, runner
from tools.groundhog.context import Invocation
from tools.groundhog.evidence import Reused, RunEvidence, RunOutcome
from tools.groundhog.levels import FullLevel, LevelSource, ResolvedLevel
from tools.groundhog.models import Mode, RunStats

if TYPE_CHECKING:
    from pathlib import Path

_WHOLE = "whole"


def _invocation(sub: str, root: Path) -> Invocation:
    """Build a directly constructed invocation of one subcommand.

    Args:
        sub: The subcommand name.
        root: The project root.

    Returns:
        The invocation, at its command default level.
    """
    return Invocation(sub=sub, files=(), no_cov=False, mode=Mode.LLM, root=root)


def test_walk_closing_keys_name_level_source_proof_reuse_and_scope() -> None:
    """A day walk's done keys carry all five values, in order."""
    walk = RunEvidence(
        _WHOLE,
        ResolvedLevel(FullLevel.COV, LevelSource.PARAM),
        FullLevel.PASS,
        Reused.CHECK_AFFECTED,
    )
    assert walk.closing_keys() == "full=cov src=param proof=pass reused=check+affected scope=whole"
    assert walk.running_keys() == "full=cov src=param scope=whole proof=pending"


def test_absent_proof_reads_unproven() -> None:
    """No valid proof renders as unproven, never as a level."""
    walk = RunEvidence(_WHOLE, ResolvedLevel(FullLevel.NONE, LevelSource.DEFAULT), None, Reused.NONE)
    assert walk.closing_keys() == "full=none src=default proof=unproven reused=none scope=whole"


def test_scope_only_evidence() -> None:
    """A run without a level carries its scope alone, running or done."""
    plain = RunEvidence(_WHOLE)
    assert plain.closing_keys() == "scope=whole"
    assert plain.running_keys() == "scope=whole"


@pytest.mark.parametrize(
    ("sub", "keys"),
    [
        (runner.SUB_DAY, "full=none src=default proof=unproven reused=none scope=whole"),
        (runner.SUB_FULL, "full=speed src=default proof=unproven scope=whole"),
        (runner.SUB_CHECK, "scope=whole"),
        (runner.SUB_SINGLE, "scope=whole"),
        (runner.SUB_TIMINGS, "scope=whole"),
    ],
)
def test_for_invocation_per_subcommand(tmp_path: Path, sub: str, keys: str) -> None:
    """The walk and the direct full run carry their level; others their scope."""
    assert evidence.for_invocation(_invocation(sub, tmp_path)).closing_keys() == keys


def test_for_invocation_carries_the_earned_proof(tmp_path: Path) -> None:
    """A direct full run reports its resolved level and the proof it earned."""
    full = replace(
        _invocation(runner.SUB_FULL, tmp_path),
        level=FullLevel.PASS,
        level_source=LevelSource.PARAM,
    )
    assert evidence.for_invocation(full, FullLevel.PASS).closing_keys() == (
        "full=pass src=param proof=pass scope=whole"
    )


def test_a_step_inside_the_walk_carries_its_scope_only(tmp_path: Path) -> None:
    """The walk owns the level evidence; its full step reports the scope."""
    step = replace(_invocation(runner.SUB_FULL, tmp_path), level=FullLevel.COV, in_walk=True)
    assert evidence.for_invocation(step, FullLevel.COV).closing_keys() == "scope=whole"


def test_outcome_defaults_without_a_pytest_child() -> None:
    """An outcome without a pytest child carries empty counters and no values."""
    outcome = RunOutcome(0, RunEvidence(_WHOLE))
    assert outcome.stats == RunStats()
    assert outcome.metrics is None


# eof
