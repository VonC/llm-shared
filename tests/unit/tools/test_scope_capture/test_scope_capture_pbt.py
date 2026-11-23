"""Bounded generated membership and explicit limits retain order invariance.

Step 1 of v0.14.0 git-cliff-provisioning lowered the per-call cost after a
whole-suite walk measured 0.27 s of lifecycle CPU for one batch under load:
names are sampled from the precomputed pool of every name the former text
strategy could produce (one to four letters of `abcxyz`), so generation draws
no strings and needs no uniqueness filter, and the three explicit limits run
once each in their own test instead of in every batch.
"""

from itertools import product

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.scope_capture import scope_fingerprint

_NAMES = tuple("".join(letters) for size in range(1, 5) for letters in product("abcxyz", repeat=size))
_LIMITS: tuple[list[str], ...] = ([], ["a"], [a + b + "xyzabc" for a in "abcx" for b in "abcxy"])


def _assert_reversal_keeps_fingerprint(names: list[str]) -> None:
    """Reversing the resolved test and source files keeps the exact fingerprint."""
    files = [f"tools/{name}.py" for name in names]
    assert scope_fingerprint("demo", ["tests/**"], ["tools/**"], files, files) == scope_fingerprint(
        "demo", ["tests/**"], ["tools/**"], list(reversed(files)), list(reversed(files)),
    )


@pytest.mark.parametrize("batch", range(5))
@given(names=st.lists(st.sampled_from(_NAMES), unique=True, max_size=6))
@settings(max_examples=5)
def test_fingerprint_order_independent(batch: int, names: list[str]) -> None:
    """Reordering a resolution keeps the exact same fingerprint."""
    del batch
    _assert_reversal_keeps_fingerprint(names)


@pytest.mark.parametrize("names", _LIMITS, ids=["empty", "single", "twenty"])
def test_fingerprint_order_independent_at_the_limits(names: list[str]) -> None:
    """The empty, single-file and twenty-file resolutions keep their fingerprint reversed."""
    _assert_reversal_keeps_fingerprint(names)


# eof
