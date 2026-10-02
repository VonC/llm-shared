"""Unit tests for the groundhog proof rules (v0.13.0 full_suite_levels).

Step 1: every example of the design's "Proof after a walk" (accumulate, then
cap below the lowest contradicted level), a run that judged no gate keeping
the saved proof, the noop, upgrade and walk decision with its timing cap,
the one effective-saved rule (scope, fingerprint and digest must match, a
timing mismatch caps at ``cov``), and the earned proof of a direct
``ghog full`` per level, result and parallel flag.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from tools.groundhog import proof
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
)
from tools.groundhog.proof import Decision, Gate

_SCOPE = "whole"
_FINGERPRINT = "f" * 64
_DIGEST = "d" * 64
_TIMING = "t" * 64
_OTHER = "0" * 64


@dataclass(frozen=True)
class _Marker:
    """A saved proof satisfying the ``SavedProof`` port."""

    scope: str = _SCOPE
    fingerprint: str = _FINGERPRINT
    timing: str = _TIMING
    digest: str = _DIGEST
    proof: FullLevel = FullLevel.SPEED


def _effective(marker: _Marker | None, *, timing: str = _TIMING) -> FullLevel | None:
    """Apply the effective-saved rule against the default current values.

    Args:
        marker: The saved marker, or ``None``.
        timing: The current timing fingerprint.

    Returns:
        The effective saved proof.
    """
    return proof.effective_saved(
        marker,
        scope_key=_SCOPE,
        fingerprint=_FINGERPRINT,
        digest=_DIGEST,
        timing=timing,
    )


def test_each_gate_contradicts_the_level_it_guards() -> None:
    """check/affected -> none, full tests -> pass, coverage -> cov, durations -> speed."""
    assert [gate.contradicts for gate in Gate] == list(FullLevel)


@pytest.mark.parametrize(
    ("earned", "saved", "contradicted", "expected"),
    [
        # Saved pass, --full=cov, coverage gap: proof stays pass.
        (FullLevel.PASS, FullLevel.PASS, (Gate.COVERAGE,), FullLevel.PASS),
        # Saved cov, --full=speed, outliers: proof cov.
        (FullLevel.COV, FullLevel.COV, (Gate.DURATIONS,), FullLevel.COV),
        # Saved pass, --full=cov, a full test failure: proof none.
        (FullLevel.NONE, FullLevel.PASS, (Gate.FULL_TESTS,), FullLevel.NONE),
        # Parallel --full=speed, no marker: cov earned, then the timing pass fails.
        (FullLevel.COV, None, (Gate.FULL_TESTS,), FullLevel.NONE),
        # The same with --force and saved speed.
        (FullLevel.COV, FullLevel.SPEED, (Gate.FULL_TESTS,), FullLevel.NONE),
        # Parallel --full=speed, green full run, outliers only in timings: cov.
        (FullLevel.COV, None, (Gate.DURATIONS,), FullLevel.COV),
        # --force at none with saved speed and a green walk: speed stays.
        (FullLevel.NONE, FullLevel.SPEED, (), FullLevel.SPEED),
        # --force --full=cov with saved speed and a coverage gap: pass.
        (FullLevel.PASS, FullLevel.SPEED, (Gate.COVERAGE,), FullLevel.PASS),
        # A failing check or affected step leaves nothing: unproven.
        (FullLevel.NONE, FullLevel.SPEED, (Gate.CHECK_OR_AFFECTED,), None),
        # The lowest contradiction wins, wherever it happened in the walk.
        (FullLevel.SPEED, None, (Gate.DURATIONS, Gate.FULL_TESTS), FullLevel.NONE),
    ],
)
def test_accumulate_matches_the_design_examples(
    earned: FullLevel | None,
    saved: FullLevel | None,
    contradicted: tuple[Gate, ...],
    expected: FullLevel | None,
) -> None:
    """The proof is the highest input, capped below the lowest contradiction."""
    assert proof.accumulate(earned, saved, contradicted) is expected


def test_a_run_judging_no_gate_keeps_the_saved_proof() -> None:
    """Setup errors, exit 9 and lost runs earn and contradict nothing."""
    assert proof.accumulate(None, FullLevel.COV, ()) is FullLevel.COV
    assert proof.accumulate(None, None, ()) is None
    assert proof.accumulate(None, None, (Gate.FULL_TESTS,)) is None


@pytest.mark.parametrize(
    ("saved", "requested", "expected"),
    [
        (FullLevel.SPEED, FullLevel.NONE, Decision.NOOP),
        (FullLevel.COV, FullLevel.COV, Decision.NOOP),
        (FullLevel.NONE, FullLevel.NONE, Decision.NOOP),
        (FullLevel.NONE, FullLevel.COV, Decision.UPGRADE),
        (FullLevel.PASS, FullLevel.SPEED, Decision.UPGRADE),
        (None, FullLevel.NONE, Decision.WALK),
    ],
)
def test_decide_noops_at_or_below_and_upgrades_above(
    saved: FullLevel | None,
    requested: FullLevel,
    expected: Decision,
) -> None:
    """Noop when requested <= saved, upgrade above, walk without saved proof."""
    decision = proof.decide(saved, requested, digest_matches=True, timing_matches=True, force=False)
    assert decision is expected


def test_decide_walks_on_a_stale_digest_or_force() -> None:
    """A digest mismatch or --force walks the whole chain whatever was saved."""
    stale = proof.decide(FullLevel.SPEED, FullLevel.NONE, digest_matches=False, timing_matches=True, force=False)
    forced = proof.decide(FullLevel.SPEED, FullLevel.NONE, digest_matches=True, timing_matches=True, force=True)
    assert stale is Decision.WALK
    assert forced is Decision.WALK


def test_decide_caps_saved_proof_at_cov_on_a_timing_mismatch() -> None:
    """A changed floor or exclusion keeps cov valid but not speed."""
    cov = proof.decide(FullLevel.SPEED, FullLevel.COV, digest_matches=True, timing_matches=False, force=False)
    speed = proof.decide(FullLevel.SPEED, FullLevel.SPEED, digest_matches=True, timing_matches=False, force=False)
    assert cov is Decision.NOOP
    assert speed is Decision.UPGRADE


def test_cap_for_timing() -> None:
    """Only a timing mismatch caps, and only speed is above the cap."""
    assert proof.cap_for_timing(None, timing_matches=False) is None
    assert proof.cap_for_timing(FullLevel.SPEED, timing_matches=True) is FullLevel.SPEED
    assert proof.cap_for_timing(FullLevel.SPEED, timing_matches=False) is FullLevel.COV
    assert proof.cap_for_timing(FullLevel.PASS, timing_matches=False) is FullLevel.PASS


def test_effective_saved_requires_scope_fingerprint_and_digest() -> None:
    """Any scope, fingerprint or digest mismatch leaves no valid proof."""
    assert _effective(None) is None
    assert _effective(_Marker(scope="group:sentinel")) is None
    assert _effective(_Marker(fingerprint=_OTHER)) is None
    assert _effective(_Marker(digest=_OTHER)) is None
    assert _effective(_Marker()) is FullLevel.SPEED


def test_effective_saved_caps_speed_at_cov_on_a_timing_mismatch() -> None:
    """A saved speed marker whose timing differs is worth cov only."""
    assert _effective(_Marker(), timing=_OTHER) is FullLevel.COV
    assert _effective(_Marker(proof=FullLevel.PASS), timing=_OTHER) is FullLevel.PASS


@pytest.mark.parametrize(
    ("level", "exit_code", "parallel", "expected"),
    [
        (FullLevel.PASS, EXIT_OBJECTIVE_MET, False, FullLevel.PASS),
        (FullLevel.PASS, EXIT_TEST_FAILURES, False, None),
        (FullLevel.PASS, EXIT_COVERAGE_GAP, False, None),
        (FullLevel.COV, EXIT_OBJECTIVE_MET, True, FullLevel.COV),
        (FullLevel.COV, EXIT_COVERAGE_GAP, False, FullLevel.PASS),
        (FullLevel.COV, EXIT_DURATION_OUTLIERS, False, None),
        (FullLevel.COV, EXIT_SUITE_CRASH, False, None),
        (FullLevel.SPEED, EXIT_OBJECTIVE_MET, False, FullLevel.SPEED),
        (FullLevel.SPEED, EXIT_DURATION_OUTLIERS, False, FullLevel.COV),
        (FullLevel.SPEED, EXIT_COVERAGE_GAP, False, FullLevel.PASS),
        (FullLevel.SPEED, EXIT_SETUP_ERROR, False, None),
        # A green parallel speed run never measured durations: cov only.
        (FullLevel.SPEED, EXIT_OBJECTIVE_MET, True, FullLevel.COV),
        (FullLevel.SPEED, EXIT_COVERAGE_GAP, True, FullLevel.PASS),
        (FullLevel.SPEED, EXIT_DURATION_OUTLIERS, True, None),
        (FullLevel.SPEED, EXIT_TEST_FAILURES, True, None),
        # A direct full run never runs at none.
        (FullLevel.NONE, EXIT_OBJECTIVE_MET, False, None),
    ],
)
def test_earned_by_direct_full_follows_the_design_table(
    level: FullLevel,
    exit_code: int,
    *,
    parallel: bool,
    expected: FullLevel | None,
) -> None:
    """A direct ghog full earns its level, the level below one failed gate, or nothing."""
    assert proof.earned_by_direct_full(level, exit_code, parallel=parallel) is expected


# eof
