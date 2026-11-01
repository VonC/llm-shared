"""Property-based checks for the groundhog proof rules (v0.13.0 Step 1).

Exhaustive invariants of the bounded pure rules: the accumulated proof
never exceeds the highest input and is always below the lowest contradicted
level; with valid inputs a noop holds exactly when the requested level is at
or below the saved proof; ``--force`` or a stale digest always walks; and the
timing cap never raises a proof nor leaves it above ``cov``. Every ordered
gate list of length zero through four is exercised for every input pair,
including repeated gates. Enumeration happens inside the measured test.
"""

from __future__ import annotations

from itertools import product

import pytest

from tools.groundhog import proof
from tools.groundhog.levels import FullLevel
from tools.groundhog.proof import Decision, Gate


@pytest.mark.parametrize("earned", [None, *FullLevel])
@pytest.mark.parametrize("saved", [None, *FullLevel])
def test_accumulate_never_exceeds_the_inputs_nor_reaches_a_contradiction(
    earned: FullLevel | None,
    saved: FullLevel | None,
) -> None:
    """Check all 341 ordered gate lists for this independent input pair."""
    for size in range(5):
        for gates in product(Gate, repeat=size):
            result = proof.accumulate(earned, saved, list(gates))
            inputs = [level for level in (earned, saved) if level is not None]
            if result is None:
                continue
            assert inputs
            assert result <= max(inputs)
            assert all(result < gate.contradicts for gate in gates)


@pytest.mark.parametrize("saved", [None, *FullLevel])
@pytest.mark.parametrize("requested", list(FullLevel))
def test_noop_holds_exactly_when_requested_is_at_or_below_saved(
    saved: FullLevel | None,
    requested: FullLevel,
) -> None:
    """With matching digest and timing, noop iff saved proof meets the request."""
    decision = proof.decide(saved, requested, digest_matches=True, timing_matches=True, force=False)
    assert (decision is Decision.NOOP) == (saved is not None and requested <= saved)


@pytest.mark.parametrize("saved", [None, *FullLevel])
@pytest.mark.parametrize("requested", list(FullLevel))
@pytest.mark.parametrize("timing_matches", [False, True])
@pytest.mark.parametrize("force", [False, True])
def test_force_or_a_stale_digest_always_walks(
    saved: FullLevel | None,
    requested: FullLevel,
    *,
    timing_matches: bool,
    force: bool,
) -> None:
    """A stale digest always walks; so does --force on a matching digest."""
    stale = proof.decide(saved, requested, digest_matches=False, timing_matches=timing_matches, force=force)
    forced = proof.decide(saved, requested, digest_matches=True, timing_matches=timing_matches, force=True)
    assert stale is Decision.WALK
    assert forced is Decision.WALK


@pytest.mark.parametrize("saved", list(FullLevel))
def test_timing_cap_never_raises_and_stops_at_cov(saved: FullLevel) -> None:
    """A timing mismatch keeps the proof at most cov and never above itself."""
    capped = proof.cap_for_timing(saved, timing_matches=False)
    assert capped is not None
    assert capped <= saved
    assert capped <= FullLevel.COV


# eof
