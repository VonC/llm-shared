"""Property-based checks for the groundhog duration rule (Step 2, Q46, Q67).

Invariants of the pure rule and its exclusion post-step, bounded in examples
and deadline so the property run never becomes a duration outlier itself
(Time-gated status for Step 2): scaling every call by a positive constant
scales the auto floor proportionally, and a call below the active floor is
never flagged; excluding every node leaves no outlier (Q54), and a written
baseline never rises above the recorded one (the baseline only ratchets down,
Q55).

Fix: the half-floor restore (Q70) adds one invariant -- an entry whose call
runs under half the active floor is never kept in the written section,
whatever its recorded baseline, so a test that became fast again always
returns to the normal rule.

Node names come from ``tests.scalar_text``, the default-text domain of every
Unicode scalar value drawn without Hypothesis's Unicode category tables.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tests.scalar_text import last_index, scalar_character, scalar_text
from tools.groundhog import durations

if TYPE_CHECKING:
    from hypothesis.strategies import SearchStrategy

# Bounded so each lifecycle stays tiny (Time-gated status for Step 2). Each
# batch is one Hypothesis run that first tries its minimal example, then one
# random draw: twenty batches keep 20 random examples per property, at least
# the 19 of a single 20-example run. Generating these dictionaries costs far
# more than the rule under test, most of all under testmon tracing, so one
# random dictionary per lifecycle keeps every lifecycle under the limit.
_BATCHES = 20
_MAX_EXAMPLES = 2
_DEADLINE_MS = 400
_REL_TOL = 1e-9

_NODES: SearchStrategy[str] = scalar_text(min_size=1, max_size=12)
_SECS: SearchStrategy[float] = st.floats(
    min_value=0.01,
    max_value=1000.0,
    allow_nan=False,
    allow_infinity=False,
)
_DURATIONS: SearchStrategy[dict[str, float]] = st.dictionaries(
    keys=_NODES,
    values=_SECS,
    min_size=1,
    max_size=20,
)
_SCALE: SearchStrategy[float] = st.floats(
    min_value=0.1,
    max_value=10.0,
    allow_nan=False,
    allow_infinity=False,
)


def _decoded_node(encoded: int) -> str:
    """Decode every nonempty scalar string up to twelve characters bijectively."""
    base = last_index() + 1
    characters: list[str] = []
    encoded += 1
    while encoded:
        encoded, character = divmod(encoded - 1, base)
        characters.append(scalar_character(character))
    return "".join(characters)


# The below-floor property needs arbitrary names, not uniqueness-rejection work.
# Integer ranks retain every bounded string, and repeated keys have normal dict
# semantics. Every original 1..20-entry dictionary remains reachable.
_RANKED_NODES = st.integers(0, sum((last_index() + 1) ** size for size in range(1, 13)) - 1).map(_decoded_node)
_FLOOR_VALUES = st.lists(st.tuples(_RANKED_NODES, _SECS), min_size=1, max_size=20).map(dict)


@pytest.mark.parametrize(("rank", "expected"), [
    (0, "\0"), (last_index(), chr(0x10FFFF)),
    (last_index() + 1, "\0\0"),
    (sum((last_index() + 1) ** size for size in range(1, 13)) - 1, chr(0x10FFFF) * 12),
])
def test_ranked_node_domain_edges(rank: int, expected: str) -> None:
    """The cheap encoding spans scalar endpoints and both length boundaries."""
    assert _decoded_node(rank) == expected


@pytest.mark.parametrize("_batch", range(_BATCHES))
@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(values=_DURATIONS, factor=_SCALE)
def test_auto_floor_scales_with_the_durations(
    _batch: int,
    values: dict[str, float],
    factor: float,
) -> None:
    """Scaling every call by a positive constant scales the auto floor (Q46)."""
    scaled = {node: secs * factor for node, secs in values.items()}
    assert math.isclose(
        durations.auto_floor(scaled),
        factor * durations.auto_floor(values),
        rel_tol=_REL_TOL,
    )


@pytest.mark.parametrize("_batch", range(_BATCHES))
@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(values=_FLOOR_VALUES)
def test_a_call_below_the_floor_is_never_an_outlier(
    _batch: int,
    values: dict[str, float],
) -> None:
    """A call under the active floor is spared, whatever its z-score (Q46)."""
    floor = durations.auto_floor(values)
    summary = durations.summarize(values, floor)
    flagged = {call.node for call in summary.outliers}
    for node, secs in values.items():
        if secs < floor:
            assert node not in flagged


@pytest.mark.parametrize("_batch", range(_BATCHES))
@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(values=_DURATIONS)
def test_excluding_every_node_leaves_no_outlier(
    _batch: int,
    values: dict[str, float],
) -> None:
    """With every node excluded the post-step spares all outliers (Q54)."""
    floor = durations.auto_floor(values)
    summary = durations.summarize(values, floor)
    spared, _ = durations.apply_exclusions(summary, values, dict(values))
    assert spared.outliers == ()


@pytest.mark.parametrize("_batch", range(_BATCHES))
@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(values=_DURATIONS, recorded=_SECS)
def test_a_written_baseline_never_rises_above_the_recorded_one(
    _batch: int,
    values: dict[str, float],
    recorded: float,
) -> None:
    """The section update only ever ratchets a baseline down, never up (Q55)."""
    node = next(iter(values))
    floor = durations.auto_floor(values)
    summary = durations.summarize(values, floor)
    _, updated = durations.apply_exclusions(summary, values, {node: recorded})
    # A kept entry holds the recorded value (ok or slower) or the lower
    # current value (a real improvement); it is never raised above recorded.
    if node in updated:
        assert updated[node] <= recorded


@pytest.mark.parametrize("_batch", range(_BATCHES))
@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(values=_DURATIONS, recorded=_SECS)
def test_a_call_back_under_half_the_floor_is_never_kept(
    _batch: int,
    values: dict[str, float],
    recorded: float,
) -> None:
    """An entry whose call runs under half the floor is always removed (Q70)."""
    floor = durations.auto_floor(values)
    summary = durations.summarize(values, floor)
    exclusion_map = dict.fromkeys(values, recorded)
    _, updated = durations.apply_exclusions(summary, values, exclusion_map)
    # Whatever the recorded baseline, a call back under half the floor has its
    # entry dropped, returning the test to the normal rule (Q70).
    for node, secs in values.items():
        if secs < floor / 2:
            assert node not in updated


# eof
