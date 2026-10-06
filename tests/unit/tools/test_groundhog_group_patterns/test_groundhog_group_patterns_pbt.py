"""Pattern properties hold at arbitrary repository depths."""

from hypothesis import given
from hypothesis import strategies as st

from tools.groundhog.group_patterns import compile_patterns, matches

_SEGMENT = st.text(alphabet="abcxyz", min_size=1, max_size=8)


@given(st.lists(_SEGMENT, max_size=8))
def test_basename_at_any_depth(parts: list[str]) -> None:
    """A slash-free pattern selects the same basename at every depth."""
    assert matches(compile_patterns(["test_*.py"]), "/".join([*parts, "test_x.py"]))


@given(_SEGMENT)
def test_exclusion_cancels_inclusion(name: str) -> None:
    """A pattern followed by its negation selects nothing."""
    assert not matches(compile_patterns([name, f"!{name}"]), f"a/{name}/x.py")


@given(_SEGMENT, _SEGMENT)
def test_star_cannot_cross_segment(first: str, second: str) -> None:
    """An extra path segment cannot fit a single star."""
    assert not matches(compile_patterns(["tests/*.py"]), f"tests/{first}/{second}.py")
