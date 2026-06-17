"""Property-based checks for the groundhog duration rule (Step 2, Q46).

Two invariants of the pure rule, bounded in examples and deadline so the
property run never becomes a duration outlier itself (Time-gated status for
Step 2): scaling every call by a positive constant scales the auto floor
proportionally, and a call below the active floor is never flagged.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.groundhog import durations

if TYPE_CHECKING:
    from hypothesis.strategies import SearchStrategy

# Bounded so the property run stays tiny (Time-gated status for Step 2).
_MAX_EXAMPLES = 50
_DEADLINE_MS = 400
_REL_TOL = 1e-9

_NODES: SearchStrategy[str] = st.text(min_size=1, max_size=12)
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


@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(values=_DURATIONS, factor=_SCALE)
def test_auto_floor_scales_with_the_durations(
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


@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(values=_DURATIONS)
def test_a_call_below_the_floor_is_never_an_outlier(
    values: dict[str, float],
) -> None:
    """A call under the active floor is spared, whatever its z-score (Q46)."""
    floor = durations.auto_floor(values)
    summary = durations.summarize(values, floor)
    flagged = {call.node for call in summary.outliers}
    for node, secs in values.items():
        if secs < floor:
            assert node not in flagged


# eof
