"""Bounded generated Unicode and explicit limits preserve lexical ordering.

Generated strings come from ``tests.scalar_text``, the default-text domain of
every Unicode scalar value drawn without Hypothesis's Unicode category tables.
"""

import sys

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tests.scalar_text import scalar_text
from tools.linear_order import ordered_strings


@pytest.mark.parametrize("_batch", range(5))
@given(st.lists(scalar_text(max_size=12), max_size=12))
@settings(max_examples=5)
def test_radix_order(_batch: int, values: list[str]) -> None:
    """Compare arbitrary Unicode strings against the language's lexical order."""
    assert ordered_strings(values) == tuple(sorted(values))


@pytest.mark.parametrize("values", [[], ["", "a", "a", "\u0000", "\U0010ffff", "\u00e9"] * 5,
                                  ["a" * 29 + chr(29 - index) for index in range(30)]])
def test_radix_order_boundaries(values: list[str]) -> None:
    """Keep explicit empty, duplicate, Unicode and shared-prefix examples."""
    assert ordered_strings(values) == tuple(sorted(values))


def test_long_shared_prefix_uses_no_recursion() -> None:
    """Deep paths cannot exceed the Python recursion limit."""
    frame = sys._getframe()  # noqa: SLF001 - measure the active harness depth
    depth = 0
    while frame is not None:
        depth += 1
        frame = frame.f_back
    original_limit = sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(depth + 100)
        prefix = "a" * 200
        assert ordered_strings([prefix + "z", "", prefix, prefix + "a", prefix]) == (
            "", prefix, prefix, prefix + "a", prefix + "z",
        )
    finally:
        sys.setrecursionlimit(original_limit)
