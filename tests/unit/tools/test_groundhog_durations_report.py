"""Unit tests for the groundhog duration-outlier report window (Step 2, Q47).

Cover the bounded window rendered from a ``DurationSummary``: the outliers
with the marked floor and the runners-up, the single green slowest-call line,
and the empty-map notice.
"""

from __future__ import annotations

from tools.groundhog import durations, durations_report

# One freak an order of magnitude over the median, with runners-up under it.
_FREAK_NODE = "tests/test_slow.py::test_freak"
_FREAK = {
    "tests/test_a.py::test_one": 0.10,
    "tests/test_a.py::test_two": 0.20,
    "tests/test_b.py::test_three": 0.15,
    "tests/test_b.py::test_four": 0.12,
    "tests/test_c.py::test_five": 0.18,
    "tests/test_c.py::test_six": 0.14,
    _FREAK_NODE: 5.00,
    "tests/test_d.py::test_double": 0.40,
}
# A tidy suite: no outlier, so the window is a single slowest-call line.
_TIDY = {
    "tests/test_a.py::test_one": 0.10,
    "tests/test_b.py::test_two": 0.12,
    "tests/test_c.py::test_three": 0.08,
    "tests/test_d.py::test_four": 0.10,
    "tests/test_e.py::test_five": 0.10,
}
_FREAK_FLOOR_LINE = "  -- floor 1.65s --"
# Six window lines: header, the freak, the floor, three runners-up.
_WINDOW_LEN = 6


def test_window_lists_outliers_floor_and_runners() -> None:
    """The window holds the header, the freak, the marked floor, runners (Q47)."""
    summary = durations.summarize(_FREAK, durations.auto_floor(_FREAK))
    lines = durations_report.window_lines(summary)
    assert lines[0].startswith("Duration outliers")
    assert _FREAK_NODE in lines[1]
    assert "30x median" in lines[1]
    assert lines[2] == _FREAK_FLOOR_LINE
    assert len(lines) == _WINDOW_LEN


def test_window_green_run_is_a_single_slowest_line() -> None:
    """A run with no outliers prints one slowest-call line with the floor (Q47)."""
    summary = durations.summarize(_TIDY, durations.auto_floor(_TIDY))
    lines = durations_report.window_lines(summary)
    assert len(lines) == 1
    assert lines[0].startswith("Slowest call:")
    assert "outliers=0" in lines[0]


def test_window_empty_map_is_a_notice() -> None:
    """An empty durations map renders the no-durations notice."""
    summary = durations.summarize({}, 0.0)
    assert durations_report.window_lines(summary) == ["No call durations captured."]


# eof
