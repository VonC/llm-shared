"""Property-based checks for the groundhog level resolution (v0.13.0 Step 1).

Any string outside ``pass``, ``cov`` and ``speed`` raises ``LevelError`` from
either source -- the parameter, or a non-empty ``GHOG_FULL`` -- and every
accepted value resolves to its level with its source. Bounded in examples and
deadline so the property run never becomes a duration outlier itself.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.groundhog import levels, runner
from tools.groundhog.levels import LevelError, LevelSource

if TYPE_CHECKING:
    from hypothesis.strategies import SearchStrategy

_MAX_EXAMPLES = 50
_DEADLINE_MS = 400
_ACCEPTED = frozenset(level.token for level in levels.ACCEPTED_LEVELS)

_REJECTED: SearchStrategy[str] = st.text(max_size=12).filter(lambda text: text not in _ACCEPTED)
_SUBS: SearchStrategy[str] = st.sampled_from(
    (runner.SUB_DAY, runner.SUB_FULL, runner.SUB_CHECK, runner.SUB_AFFECTED, runner.SUB_SINGLE),
)


@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(value=_REJECTED, sub=_SUBS)
def test_rejected_parameter_always_raises(value: str, sub: str) -> None:
    """Any --full value outside the accepted three is a level error."""
    with pytest.raises(LevelError):
        levels.resolve_level(sub, value, lambda _name: None)


@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(value=_REJECTED.filter(bool), sub=_SUBS)
def test_rejected_variable_always_raises(value: str, sub: str) -> None:
    """Any non-empty GHOG_FULL outside the accepted three is a level error."""
    with pytest.raises(LevelError):
        levels.resolve_level(sub, None, lambda _name: value)


@settings(max_examples=_MAX_EXAMPLES, deadline=_DEADLINE_MS)
@given(level=st.sampled_from(levels.ACCEPTED_LEVELS), sub=_SUBS, from_param=st.booleans())
def test_accepted_value_resolves_with_its_source(
    level: levels.FullLevel,
    sub: str,
    *,
    from_param: bool,
) -> None:
    """Every accepted token resolves to its level, from either source."""
    param = level.token if from_param else None
    resolved = levels.resolve_level(sub, param, lambda _name: level.token)
    assert resolved.level is level
    assert resolved.source is (LevelSource.PARAM if from_param else LevelSource.ENV)


# eof
