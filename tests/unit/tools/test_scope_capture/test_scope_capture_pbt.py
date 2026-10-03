"""Captured fingerprints depend on membership, never input file order."""

from hypothesis import given
from hypothesis import strategies as st

from tools.scope_capture import scope_fingerprint


@given(st.lists(st.text(alphabet="abcxyz", min_size=1, max_size=8), unique=True, max_size=20))
def test_fingerprint_order_independent(names: list[str]) -> None:
    """Reordering a resolution keeps the exact same fingerprint."""
    files = [f"tools/{name}.py" for name in names]
    assert scope_fingerprint("demo", ["tests/**"], ["tools/**"], files, files) == scope_fingerprint(
        "demo", ["tests/**"], ["tools/**"], list(reversed(files)), list(reversed(files)),
    )
