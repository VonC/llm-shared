"""Bounded generated membership and explicit limits retain order invariance."""

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from tools.scope_capture import scope_fingerprint


@pytest.mark.parametrize("batch", range(5))
@given(names=st.lists(st.text(alphabet="abcxyz", min_size=1, max_size=4), unique=True, max_size=6))
@settings(max_examples=5)
@example([])
@example(["a"])
@example([a + b + "xyzabc" for a in "abcx" for b in "abcxy"])
def test_fingerprint_order_independent(batch: int, names: list[str]) -> None:
    """Reordering a resolution keeps the exact same fingerprint."""
    del batch
    files = [f"tools/{name}.py" for name in names]
    assert scope_fingerprint("demo", ["tests/**"], ["tools/**"], files, files) == scope_fingerprint(
        "demo", ["tests/**"], ["tools/**"], list(reversed(files)), list(reversed(files)),
    )
