"""Bounded proof transitions and record serialization without filesystem work."""

from __future__ import annotations

import llm_shared_lifecycle_gate as gate
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

_CEILING = 0.1

# Keep 100 generated cases per property, split into independent lifecycles.
# Integer encodings retain every list/dictionary in the original bounded domain.
@pytest.mark.parametrize("_batch", range(20))
@settings(max_examples=5)
@given(st.integers(min_value=0, max_value=1001**30 - 1), st.integers(min_value=1, max_value=30), st.integers(min_value=1, max_value=10))
def test_proof_and_drift_follow_consecutive_measurements(_batch: int, encoded: int, length: int, drift_runs: int) -> None:
    """The oracle tracks eligibility and consecutive overruns independently."""
    state = None
    proven, drift = False, 0
    for _ in range(length):
        encoded, sample = divmod(encoded, 1001)
        cpu = sample / 1000
        if cpu <= _CEILING:
            proven, drift = True, 0
        elif proven:
            drift += 1
            if drift >= drift_runs:
                proven, drift = False, 0
        state = gate.advance(state, cpu, _CEILING, drift_runs)
        assert (state.proven, state.over_runs, state.cpu) == (proven, drift, cpu)
        assert state.holds(_CEILING) == proven


@pytest.mark.parametrize("_batch", range(20))
@settings(max_examples=5)
@given(st.integers(min_value=0, max_value=101**15 - 1), st.integers(min_value=0, max_value=1001**15 - 1), st.integers(min_value=0, max_value=15))
def test_record_round_trip_preserves_keys_and_proofs(_batch: int, keys: int, values: int, length: int) -> None:
    """Serialization preserves schema fields and strips only a terminal group."""
    nodes: dict[str, gate.NodeState] = {}
    for _ in range(length):
        keys, key = divmod(keys, 101)
        values, value = divmod(values, 1001)
        nodes[f"t.py::test[{key}@inner]"] = gate.NodeState(proven=True, over_runs=0, cpu=value / 1000, proven_cpu=value / 1000)
    text = gate.render_record({"extra": {"kept": True}}, nodes)
    parsed, document = gate.parse_record(text)
    assert parsed.nodes == nodes
    assert document["extra"] == {"kept": True}
    for key in nodes:
        assert gate.record_key(key) == key
        assert gate.record_key(f"{key}@worker-group_1.0") == key


# eof
