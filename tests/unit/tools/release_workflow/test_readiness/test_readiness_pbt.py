"""Generated invariants for reachable dependencies in cyclic lock graphs."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from tools.release_workflow.markers import evaluate
from tools.release_workflow.readiness import Closure


@given(st.lists(st.sets(st.integers(min_value=0, max_value=11), max_size=12), min_size=1, max_size=12))
def test_graph_visits_exactly_reachable_nodes(adjacency: list[set[int]]) -> None:
    """Cycles, diamonds and repeated incoming edges never repeat lookups."""
    graph = [{child % len(adjacency) for child in children} for children in adjacency]
    packages: list[object] = [
        {"name": f"node-{index}", "version": "1", "source": {"registry": "https://registry.example"},
         "dependencies": [{"name": f"node-{child}"} for child in children]}
        for index, children in enumerate(graph)
    ]
    expected: set[int] = set()
    pending = [0]
    while pending:
        node = pending.pop()
        if node not in expected:
            expected.add(node)
            pending.extend(graph[node])
    visits: list[str] = []

    def installed(name: str) -> str:
        visits.append(name)
        return "1"

    actual = Closure(packages, {}, evaluate).walk([{"name": "node-0"}], installed)
    assert set(actual) == {f"node-{node}" for node in expected}
    assert len(visits) == len(set(visits)) == len(expected)

# eof
