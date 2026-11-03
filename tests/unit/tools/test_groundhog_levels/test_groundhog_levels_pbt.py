"""Property-based checks for the groundhog level resolution (v0.13.0 Step 1).

Any string outside ``pass``, ``cov`` and ``speed`` raises ``LevelError`` from
either source -- the parameter, or a non-empty ``GHOG_FULL`` -- and every
accepted value resolves to its level with its source. The finite accepted
domain is exhaustive; rejection properties retain their bounded examples.
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

_DEADLINE_MS = 400
_ACCEPTED = frozenset(level.token for level in levels.ACCEPTED_LEVELS)
_SURROGATE_START = 0xD800

# Keep the full Unicode scalar domain without loading Unicode category/codec
# tables for a property that only compares strings with three ASCII tokens.
def _scalar_text(points: list[int]) -> str:
    """Map contiguous scalar indices around the surrogate block in one pass."""
    return "".join(chr(point if point < _SURROGATE_START else point + 0x800) for point in points)


def _rejected_text(*, min_size: int = 0) -> SearchStrategy[str]:
    """Draw whole strings without per-character composite strategy dispatch."""
    return st.lists(st.integers(0, 0x10FFFF - 0x800), min_size=min_size, max_size=12).map(
        _scalar_text,
    ).filter(lambda text: text not in _ACCEPTED)


_REJECTED = _rejected_text()
_SUBS: SearchStrategy[str] = st.sampled_from(
    (runner.SUB_DAY, runner.SUB_FULL, runner.SUB_CHECK, runner.SUB_AFFECTED, runner.SUB_SINGLE),
)


@pytest.mark.parametrize("_batch", range(10))
@settings(max_examples=5, deadline=_DEADLINE_MS)
@given(value=_REJECTED, sub=_SUBS)
def test_rejected_parameter_always_raises(_batch: int, value: str, sub: str) -> None:
    """Any --full value outside the accepted three is a level error."""
    with pytest.raises(LevelError):
        levels.resolve_level(sub, value, lambda _name: None)


@pytest.mark.parametrize("_batch", range(10))
@settings(max_examples=5, deadline=_DEADLINE_MS)
@given(value=_rejected_text(min_size=1), sub=_SUBS)
def test_rejected_variable_always_raises(_batch: int, value: str, sub: str) -> None:
    """Any non-empty GHOG_FULL outside the accepted three is a level error."""
    with pytest.raises(LevelError):
        levels.resolve_level(sub, None, lambda _name: value)


@pytest.mark.parametrize("level", levels.ACCEPTED_LEVELS)
@pytest.mark.parametrize("sub", [runner.SUB_DAY, runner.SUB_FULL, runner.SUB_CHECK,
                                 runner.SUB_AFFECTED, runner.SUB_SINGLE])
@pytest.mark.parametrize("from_param", [False, True])
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
