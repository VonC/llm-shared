"""Permutation and omission properties for synthetic evidence accounting."""

# ruff: noqa: PLR2004 - Expected synthetic measurements belong beside assertions.

from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from .test_collector_tdd import collect, event, lifecycle

pytestmark = pytest.mark.timeout(10)


class TestCollectorProperties:
    """Duplicate and delayed arrivals preserve counts without inventing coverage."""

    @given(st.permutations(tuple(range(5))))
    def test_ingestion_order_preserves_totals(self, order: tuple[int, ...]) -> None:
        """Logical identities, rather than arrival order, own accounting."""
        rows = [
            event("request_attempt", 20, attempt_id="a1", request_id="r1", end_at=21),
            event("usage_completion", 30, attempt_id="a1", epoch="epoch-1",
                  usage={"input": 10, "output": 2}),
            event("usage_completion", 30, attempt_id="a1", epoch="epoch-1",
                  usage={"input": 10, "output": 2}),
            event("request_attempt", 20, attempt_id="a1", request_id="r1", end_at=21),
            event("compaction", 40),
        ]
        report = collect(Path.cwd(), [*lifecycle(), *(rows[index] for index in order)]).report(486)
        assert report["attempts"] == 1
        assert report["completions"] == 1
        assert report["usage"]["input"] == 10
        assert report["compactions"] == 1

    @given(requests=st.booleans(), usage=st.booleans())
    def test_coverage_dimensions_are_independent(self, *, requests: bool, usage: bool) -> None:
        """Suppressing an evidence channel cannot improve its confidence."""
        rows = [*lifecycle()[:-1], event("coverage", 486, requests=requests,
                                       usage=usage, through=366)]
        report = collect(Path.cwd(), rows).report(486)
        assert (report["request_coverage"] == "complete") is requests
        assert (report["usage_coverage"] == "complete") is usage
        assert report["strict_zero_inference"] is requests

# eof
