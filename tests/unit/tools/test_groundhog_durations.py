"""Unit tests for the pure groundhog duration rule (Step 2, Q46).

Cover the auto floor (``k * median``), the two-condition true-outlier rule,
the MAD-zero fallback (Q50), the average over the non-outlier calls (Q37),
the empty-map summary, and the median-zero ratio guard. The bounded report
window (Q47) is rendered by ``durations_report.py`` and covered in
``test_groundhog_durations_report.py``.
"""

from __future__ import annotations

import pytest

from tools.groundhog import durations

# Expected auto-floor values, k * median for an odd then an even count.
_AUTO_FLOOR_ODD = 20.0
_AUTO_FLOOR_EVEN = 25.0
# A tidy suite: every call near the median, so no call clears the floor.
_TIDY = {
    "tests/test_a.py::test_one": 0.10,
    "tests/test_b.py::test_two": 0.12,
    "tests/test_c.py::test_three": 0.08,
    "tests/test_d.py::test_four": 0.10,
    "tests/test_e.py::test_five": 0.10,
}
_TIDY_AVG = 0.10
# A run with one freak an order of magnitude over the median, plus a call
# only ~2.7x the median that must stay unflagged (Q46).
_FREAK_NODE = "tests/test_slow.py::test_freak"
_NEAR_NODE = "tests/test_d.py::test_double"
_FREAK = {
    "tests/test_a.py::test_one": 0.10,
    "tests/test_a.py::test_two": 0.20,
    "tests/test_b.py::test_three": 0.15,
    "tests/test_b.py::test_four": 0.12,
    "tests/test_c.py::test_five": 0.18,
    "tests/test_c.py::test_six": 0.14,
    _FREAK_NODE: 5.00,
    _NEAR_NODE: 0.40,
}
_FREAK_SECS = 5.00
_FREAK_MEDIAN = 0.165
_FREAK_RATIO = _FREAK_SECS / _FREAK_MEDIAN
_FREAK_AVG = (0.10 + 0.20 + 0.15 + 0.12 + 0.18 + 0.14 + 0.40) / 7
# A spike used by the MAD-zero and median-zero edge cases.
_SPIKE_SECS = 2.00
# Three runners-up are kept for the window (Q51).
_EXPECTED_RUNNERS = 3


def test_auto_floor_of_an_empty_map_is_zero() -> None:
    """A non-full run leaves the map empty, so the auto floor is zero."""
    assert durations.auto_floor({}) == 0.0


def test_auto_floor_uses_the_odd_count_median() -> None:
    """The auto floor is k * median for an odd number of calls (Q46)."""
    values = {"a": 1.0, "b": 2.0, "c": 3.0}
    assert durations.auto_floor(values) == _AUTO_FLOOR_ODD


def test_auto_floor_uses_the_even_count_median() -> None:
    """The auto floor averages the two middle calls for an even count."""
    values = {"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0}
    assert durations.auto_floor(values) == _AUTO_FLOOR_EVEN


def test_summarize_empty_map_is_empty() -> None:
    """An empty durations map yields an empty summary, no division."""
    summary = durations.summarize({}, 0.0)
    assert summary.outliers == ()
    assert summary.runners_up == ()
    assert summary.average == 0.0


def test_tidy_suite_has_no_outliers() -> None:
    """Every call near the median stays under the floor: zero outliers."""
    summary = durations.summarize(_TIDY, durations.auto_floor(_TIDY))
    assert summary.outliers == ()
    assert len(summary.runners_up) == _EXPECTED_RUNNERS
    assert summary.average == pytest.approx(_TIDY_AVG)


def test_one_freak_is_the_single_outlier() -> None:
    """The order-of-magnitude freak is flagged; a ~2.7x call is not (Q46)."""
    summary = durations.summarize(_FREAK, durations.auto_floor(_FREAK))
    flagged = {call.node for call in summary.outliers}
    assert flagged == {_FREAK_NODE}
    assert _NEAR_NODE not in flagged
    outlier = summary.outliers[0]
    assert outlier.seconds == _FREAK_SECS
    assert outlier.ratio == pytest.approx(_FREAK_RATIO)


def test_average_excludes_the_outliers() -> None:
    """avg= is the mean over the calls left unflagged, the freak left out."""
    summary = durations.summarize(_FREAK, durations.auto_floor(_FREAK))
    assert summary.average == pytest.approx(_FREAK_AVG)


def test_mad_zero_drops_the_z_condition() -> None:
    """A tie-heavy suite judges on the floor alone, sparing near-median (Q50)."""
    tied = {
        "tests/test_a.py::test_one": 0.10,
        "tests/test_b.py::test_two": 0.10,
        "tests/test_c.py::test_three": 0.10,
        "tests/test_d.py::test_four": 0.10,
        _FREAK_NODE: _SPIKE_SECS,
    }
    summary = durations.summarize(tied, durations.auto_floor(tied))
    flagged = {call.node for call in summary.outliers}
    assert flagged == {_FREAK_NODE}


def test_median_zero_yields_a_zero_ratio() -> None:
    """A zero median reports a zero ratio, never a division crash."""
    zeroed = {
        "tests/test_a.py::test_one": 0.0,
        "tests/test_b.py::test_two": 0.0,
        "tests/test_c.py::test_three": 0.0,
        "tests/test_d.py::test_four": 0.0,
        _FREAK_NODE: _SPIKE_SECS,
    }
    summary = durations.summarize(zeroed, 1.0)
    assert summary.outliers[0].node == _FREAK_NODE
    assert summary.outliers[0].ratio == 0.0


# eof
