"""Property-based checks for the groundhog proof rules (v0.13.0 Step 1).

Invariants of the pure rules, bounded in examples and deadline so the
property run never becomes a duration outlier itself: the accumulated proof
never exceeds the highest input and is always below the lowest contradicted
level; with valid inputs a noop holds exactly when the requested level is at
or below the saved proof; ``--force`` or a stale digest always walks; and the
timing cap never raises a proof nor leaves it above ``cov``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.groundhog import proof
from tools.groundhog.levels import FullLevel
from tools.groundhog.proof import Decision, Gate

if TYPE_CHECKING:
    from hypothesis.strategies import SearchStrategy

_MAX_EXAMPLES = 100
_DEADLINE_MS = 400

_LEVELS: SearchStrategy[FullLevel] = st.sampled_from(FullLevel)
_OPTIONAL: SearchStrategy[FullLevel | None] = st.none() | _LEVELS
_GATES: SearchStrategy[list[Gate]] = st.lists(st.sampled_from(Gate), max_size=4)


@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(earned=_OPTIONAL, saved=_OPTIONAL, gates=_GATES)
def test_accumulate_never_exceeds_the_inputs_nor_reaches_a_contradiction(
    earned: FullLevel | None,
    saved: FullLevel | None,
    gates: list[Gate],
) -> None:
    """The result is at most the highest input and below every contradiction."""
    result = proof.accumulate(earned, saved, gates)
    inputs = [level for level in (earned, saved) if level is not None]
    if result is None:
        return
    assert inputs
    assert result <= max(inputs)
    assert all(result < gate.contradicts for gate in gates)


@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(saved=_OPTIONAL, requested=_LEVELS)
def test_noop_holds_exactly_when_requested_is_at_or_below_saved(
    saved: FullLevel | None,
    requested: FullLevel,
) -> None:
    """With matching digest and timing, noop iff saved proof meets the request."""
    decision = proof.decide(saved, requested, digest_matches=True, timing_matches=True, force=False)
    assert (decision is Decision.NOOP) == (saved is not None and requested <= saved)


@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(saved=_OPTIONAL, requested=_LEVELS, timing_matches=st.booleans(), force=st.booleans())
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


@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(saved=_LEVELS)
def test_timing_cap_never_raises_and_stops_at_cov(saved: FullLevel) -> None:
    """A timing mismatch keeps the proof at most cov and never above itself."""
    capped = proof.cap_for_timing(saved, timing_matches=False)
    assert capped is not None
    assert capped <= saved
    assert capped <= FullLevel.COV


# eof
