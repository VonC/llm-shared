"""Explore preparation properties in 20 batches retaining 100 examples each."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools import pytest_plugin_environment as env


@pytest.mark.parametrize("_batch", range(20))
@settings(max_examples=5)
@given(st.binary(), st.integers(min_value=0, max_value=2))
def test_normalization_is_idempotent_and_preserves_members(_batch: int, encoded: bytes, whitespace: int) -> None:
    """Decode arbitrary repetitions cheaply without per-element strategy draws."""
    names = [("lifecycle", "process")[value % 2] for value in encoded]
    space = ("", " ", "\t")[whitespace]
    raw = ",".join(space + name + space for name in names)
    selected = env.normalize_selection(raw)
    assert set(selected) == set(names)
    assert env.normalize_selection(",".join(selected)) == selected
    assert len(selected) == len(set(names))


@pytest.mark.parametrize("_batch", range(20))
@settings(max_examples=5)
@given(st.binary(), st.binary())
def test_recomputing_owned_environment_entries_is_idempotent(_batch: int, path_bytes: bytes, option_bytes: bytes) -> None:
    """Keep arbitrary lists and the example budget using two bulk byte draws."""
    paths = [("consumer", "another", "owned")[value % 3] for value in path_bytes]
    options = [("-q", "-x", "-p llm_shared_pytest_loader", "-pll m")[value % 4] for value in option_bytes]
    result = env.clean_paths(paths, {"owned"})
    assert result == [path for path in paths if path != "owned"]
    assert env.clean_paths(result, {"owned"}) == result
    cleaned = env.clean_options(" ".join(options))
    assert env.clean_options(cleaned) == cleaned
