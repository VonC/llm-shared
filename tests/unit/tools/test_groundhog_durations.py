"""Unit tests for the pure groundhog duration rule (Step 2, Q46, Q67).

Cover the auto floor (``k * median``), the two-condition true-outlier rule,
the MAD-zero fallback (Q50), the average over the non-outlier calls (Q37),
the empty-map summary, and the median-zero ratio guard. The bounded report
window (Q47) is rendered by ``durations_report.py`` and covered in
``test_groundhog_durations_report.py``.

Also cover the exclusion post-step ``apply_exclusions`` (Q67): a flagged
excluded call is spared from the outliers (Q54) and left out of the average
(Q64); the statuses ``ok``, ``slower``, ``faster`` and ``stale`` are
classified against the recorded baseline (Q63); the section update lowers a
baseline only on a beyond-two-second improvement (Q69), keeps a slower-drifted
baseline (never raised, Q57), and drops a below-floor or stale entry (Q60,
Q61); the median and the floor are unchanged by exclusion (Q54).

Fix: float comparisons use ``math.isclose`` like the property test, so the
strict pyright gate (``reportUnknownMemberType`` on ``pytest.approx``) stays
green.
"""

from __future__ import annotations

import math

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
# A run with two accepted-slow integration calls over the ~1.65s auto floor
# plus the normal suite, for the exclusion post-step (Q54, Q64). Both slow
# calls are flagged, so sparing must drop them from the outliers.
_INTEG_SLOW = "tests/test_integ.py::test_slow_path"
_INTEG_FAST = "tests/test_integ.py::test_other_path"
_NORMAL_NODE = "tests/test_a.py::test_two"
_GONE_NODE = "tests/test_gone.py::test_removed"
_EXCL = {
    "tests/test_a.py::test_one": 0.10,
    _NORMAL_NODE: 0.20,
    "tests/test_b.py::test_three": 0.15,
    "tests/test_b.py::test_four": 0.12,
    "tests/test_c.py::test_five": 0.18,
    "tests/test_c.py::test_six": 0.14,
    _INTEG_SLOW: 11.40,
    _INTEG_FAST: 6.80,
}
_RECORDED_SLOW = 11.40
_RECORDED_FAST = 6.80
# The mean of the six normal calls: the avg once both slow calls are out.
_EXCL_NORMAL_AVG = (0.10 + 0.20 + 0.15 + 0.12 + 0.18 + 0.14) / 6
# The mean once the 0.20s normal call is also excluded (Q64).
_EXCL_FIVE_AVG = (0.10 + 0.15 + 0.12 + 0.18 + 0.14) / 5


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
    assert math.isclose(summary.average, _TIDY_AVG)


def test_one_freak_is_the_single_outlier() -> None:
    """The order-of-magnitude freak is flagged; a ~2.7x call is not (Q46)."""
    summary = durations.summarize(_FREAK, durations.auto_floor(_FREAK))
    flagged = {call.node for call in summary.outliers}
    assert flagged == {_FREAK_NODE}
    assert _NEAR_NODE not in flagged
    outlier = summary.outliers[0]
    assert outlier.seconds == _FREAK_SECS
    assert math.isclose(outlier.ratio, _FREAK_RATIO)


def test_average_excludes_the_outliers() -> None:
    """avg= is the mean over the calls left unflagged, the freak left out."""
    summary = durations.summarize(_FREAK, durations.auto_floor(_FREAK))
    assert math.isclose(summary.average, _FREAK_AVG)


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


def test_zero_floor_spares_every_call() -> None:
    """A uniformly-fast suite (zero median, zero floor) flags nothing (Q41).

    Most calls round to ``0.00s``, so the median and the ``k * median`` auto
    floor are zero; with no scale to judge against, even a lone slower call is
    spared and the tidy suite is green from the start.
    """
    fast = {
        "tests/test_a.py::test_one": 0.0,
        "tests/test_b.py::test_two": 0.0,
        "tests/test_c.py::test_three": 0.0,
        "tests/test_d.py::test_four": _SPIKE_SECS,
    }
    summary = durations.summarize(fast, durations.auto_floor(fast))
    assert summary.floor == 0.0
    assert summary.outliers == ()


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


def _excl_summary() -> durations.DurationSummary:
    """Summarize the _EXCL run against its own auto floor for the post-step.

    Returns:
        The v0.2.0 verdict over _EXCL, with both integration calls flagged.
    """
    return durations.summarize(_EXCL, durations.auto_floor(_EXCL))


def test_apply_exclusions_spares_a_flagged_call() -> None:
    """A flagged call in the exclusion set is dropped from the outliers (Q54)."""
    summary = _excl_summary()
    # Both slow integration calls are recorded within tolerance, so neither
    # stays flagged and the suite-wide avg is the mean of the six normal calls.
    spared, _ = durations.apply_exclusions(
        summary, _EXCL, {_INTEG_SLOW: _RECORDED_SLOW, _INTEG_FAST: _RECORDED_FAST},
    )
    assert spared.outliers == ()
    assert math.isclose(spared.average, _EXCL_NORMAL_AVG)


def test_apply_exclusions_keeps_the_scale() -> None:
    """Sparing after the rule never moves the median or the floor (Q54)."""
    summary = _excl_summary()
    spared, _ = durations.apply_exclusions(summary, _EXCL, {_INTEG_SLOW: _RECORDED_SLOW})
    # The scale the rest of the suite is judged against is computed over the
    # whole run, so an exclusion leaves the median and the floor untouched.
    assert spared.median == summary.median
    assert spared.floor == summary.floor


def test_apply_exclusions_drops_a_non_outlier_from_the_average() -> None:
    """An excluded non-outlier call is left out of the run average (Q64)."""
    summary = _excl_summary()
    # The 0.20s normal call is not an outlier, so summarize counts it in the
    # average; excluding it drops it, the same as an outlier (Q64), while the
    # two integration calls stay flagged.
    spared, _ = durations.apply_exclusions(summary, _EXCL, {_NORMAL_NODE: 0.20})
    assert math.isclose(spared.average, _EXCL_FIVE_AVG)
    assert {call.node for call in spared.outliers} == {_INTEG_SLOW, _INTEG_FAST}


def test_apply_exclusions_classifies_the_four_statuses() -> None:
    """ok, slower, faster and stale are read against the baseline (Q61, Q63)."""
    summary = _excl_summary()
    exclusion_map = {
        _INTEG_SLOW: _RECORDED_SLOW,  # current 11.40 == baseline -> ok
        _INTEG_FAST: 4.00,  # current 6.80 is +2.80s over 4.00 -> slower
        "tests/test_a.py::test_one": 5.00,  # current 0.10 is -4.90s -> faster
        _GONE_NODE: 9.00,  # absent from the run -> stale
    }
    spared, _ = durations.apply_exclusions(summary, _EXCL, exclusion_map)
    status = {entry.node: entry.status for entry in spared.exclusions}
    assert status[_INTEG_SLOW] == durations.STATUS_OK
    assert status[_INTEG_FAST] == durations.STATUS_SLOWER
    assert status["tests/test_a.py::test_one"] == durations.STATUS_FASTER
    assert status[_GONE_NODE] == durations.STATUS_STALE
    stale = next(e for e in spared.exclusions if e.node == _GONE_NODE)
    assert stale.current is None


def test_apply_exclusions_section_update_ratchets_and_prunes() -> None:
    """The update keeps ok, lowers a real improvement, drops the rest (Q60)."""
    summary = _excl_summary()
    exclusion_map = {
        _INTEG_SLOW: _RECORDED_SLOW,  # ok -> kept at 11.40
        _INTEG_FAST: 10.00,  # current 6.80 is a -3.20s improvement, over floor
        "tests/test_a.py::test_one": 5.00,  # current 0.10 under floor -> removed
        _GONE_NODE: 9.00,  # stale -> removed
    }
    _, updated = durations.apply_exclusions(summary, _EXCL, exclusion_map)
    # The faster call ratchets down to its current time (Q69); the below-floor
    # and stale entries are dropped (Q60, Q61).
    assert updated == {_INTEG_SLOW: _RECORDED_SLOW, _INTEG_FAST: _RECORDED_FAST}


def test_apply_exclusions_never_raises_a_slower_baseline() -> None:
    """A slower-drifted call keeps its recorded baseline, never raised (Q57)."""
    summary = _excl_summary()
    # _INTEG_FAST ran at 6.80, recorded at 4.00: a +2.80s regression. The
    # baseline must stay 4.00 -- a slower call is a regression, not a new
    # baseline -- so the section keeps the recorded value.
    _, updated = durations.apply_exclusions(summary, _EXCL, {_INTEG_FAST: 4.00})
    assert updated == {_INTEG_FAST: 4.00}


def test_apply_exclusions_small_improvement_keeps_the_baseline() -> None:
    """A faster reading within two seconds is ok and never lowers (Q69)."""
    summary = _excl_summary()
    # _INTEG_FAST ran at 6.80, recorded at 7.50: only 0.70s faster, within
    # tolerance, so it reads ok and keeps its 7.50 baseline (Q69).
    spared, updated = durations.apply_exclusions(summary, _EXCL, {_INTEG_FAST: 7.50})
    assert updated == {_INTEG_FAST: 7.50}
    assert spared.exclusions[0].status == durations.STATUS_OK


# eof
