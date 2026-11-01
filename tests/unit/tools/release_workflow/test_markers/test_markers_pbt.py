"""Generated invariants for release tuples and boolean markers."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.release_workflow.markers import evaluate, satisfies


@pytest.mark.parametrize("_batch", range(20))
@settings(max_examples=5)
@given(st.integers(min_value=0, max_value=99), st.integers(min_value=0, max_value=99))
def test_padding_is_equivalent(_batch: int, major: int, minor: int) -> None:
    """Trailing zero components never change release-version equality."""
    version = f"{major}.{minor}"
    assert satisfies(version, f"=={version}.0")
    assert evaluate(f"python_version == '{version}.0'", {"python_version": version})


@given(left=st.booleans(), right=st.booleans())
def test_boolean_operators(*, left: bool, right: bool) -> None:
    """Parenthesized grammar implements boolean conjunction and disjunction."""
    env = {"os_name": "nt"}
    lhs = "os_name == 'nt'" if left else "os_name != 'nt'"
    rhs = "os_name == 'nt'" if right else "os_name != 'nt'"
    assert evaluate(f"({lhs}) and ({rhs})", env) == (left and right)
    assert evaluate(f"({lhs}) or ({rhs})", env) == (left or right)

# eof
