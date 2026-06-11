"""Unit tests for the groundhog failure baseline (Q07, Q18).

Cover the ``a.ghog.failures`` write/read cycle, the green-run emptying,
the unique failing files helper, and the focus comparison producing the
two Q07 lists across path-style differences.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.groundhog import baseline

if TYPE_CHECKING:
    from pathlib import Path


def test_write_then_read_round_trips_node_ids(tmp_path: Path) -> None:
    """The baseline file round-trips the failing node ids (Q18)."""
    ids = ["tests/test_a.py::test_one", "tests/test_b.py::test_two"]
    path = baseline.write_baseline(tmp_path, ids)
    assert path == tmp_path / baseline.BASELINE_FILE_NAME
    assert baseline.read_baseline(tmp_path) == tuple(ids)


def test_green_run_empties_the_baseline(tmp_path: Path) -> None:
    """A green full run leaves an empty, existing baseline (Q18)."""
    baseline.write_baseline(tmp_path, ["tests/test_a.py::test_one"])
    baseline.write_baseline(tmp_path, [])
    assert baseline.read_baseline(tmp_path) == ()


def test_read_without_baseline_returns_none(tmp_path: Path) -> None:
    """No baseline file means no comparison material (Q18)."""
    assert baseline.read_baseline(tmp_path) is None


def test_failing_files_are_unique_and_ordered() -> None:
    """The failing files keep first-occurrence order without duplicates."""
    ids = [
        "tests/test_a.py::test_one",
        "tests/test_a.py::test_two",
        "tests\\test_b.py::test_three",
    ]
    assert baseline.failing_files(ids) == ("tests/test_a.py", "tests/test_b.py")


def test_compare_focus_builds_the_two_lists() -> None:
    """The comparison splits still-failing and interaction suspects (Q07)."""
    baseline_ids = [
        "tests/test_a.py::test_one",
        "tests/test_a.py::test_two",
        "tests/test_c.py::test_out_of_scope",
    ]
    comparison = baseline.compare_focus(
        baseline_ids,
        ["tests/test_a.py"],
        ["tests/test_a.py::test_one"],
    )
    assert comparison.still_failing == ("tests/test_a.py::test_one",)
    assert comparison.suspects == ("tests/test_a.py::test_two",)


def test_compare_focus_matches_backslash_node_ids() -> None:
    """Baseline ids in backslash style still match the focus files."""
    comparison = baseline.compare_focus(
        ["tests\\test_a.py::test_one"],
        ["tests/test_a.py"],
        [],
    )
    assert comparison.suspects == ("tests\\test_a.py::test_one",)


def test_compare_focus_matches_short_focus_names() -> None:
    """A focus file given without its folder still scopes the baseline."""
    comparison = baseline.compare_focus(
        ["tests/test_a.py::test_one"],
        ["test_a.py"],
        [],
    )
    assert comparison.suspects == ("tests/test_a.py::test_one",)


def test_compare_focus_matches_longer_focus_paths() -> None:
    """A focus path longer than the node id file part still matches."""
    comparison = baseline.compare_focus(
        ["test_a.py::test_one"],
        ["tests/test_a.py"],
        [],
    )
    assert comparison.suspects == ("test_a.py::test_one",)


# eof
