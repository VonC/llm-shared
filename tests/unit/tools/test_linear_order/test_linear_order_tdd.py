"""Radix ordering agrees with lexical order without losing repeated strings."""

from hypothesis import given
from hypothesis import strategies as st

from tools.linear_order import ordered_strings


@given(st.lists(st.text(max_size=30), max_size=30))
def test_radix_order(values: list[str]) -> None:
    """Compare arbitrary Unicode strings against the language's lexical order."""
    assert ordered_strings(values) == tuple(sorted(values))


def test_long_shared_prefix_uses_no_recursion() -> None:
    """Deep paths cannot exceed the Python recursion limit."""
    prefix = "a" * 1500
    assert ordered_strings([prefix + "z", "", prefix, prefix + "a", prefix]) == (
        "", prefix, prefix, prefix + "a", prefix + "z",
    )
