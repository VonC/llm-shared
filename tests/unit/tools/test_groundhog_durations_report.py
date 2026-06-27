"""Unit tests for the groundhog duration-outlier report window (Step 2, Q47).

Cover the bounded window rendered from a ``DurationSummary``: the outliers
with the marked floor and the runners-up, the single green slowest-call line,
and the empty-map notice.

Also cover the per-test exclusion block (Step 3, Q58): the header and one line
per excluded call -- ``ok``, the slower-restore (Q57), the lowered baseline
(Q69), the below-floor removal (Q60) and the stale removal (Q61) -- and the
empty list rendering no block.
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
# Eight window lines: header, the freak, blank, floor, blank, three runners-up.
_WINDOW_LEN = 8

# The active floor the exclusion block compares a faster call against: a call
# below it is removed, a call at or above it has its baseline lowered (Q60).
_EXCL_FLOOR = 1.0
# One record per drift verdict: ok, slower, faster-lowered (above the floor),
# faster-removed (below the floor) and stale (no current call).
_OK_NODE = "tests/test_auth.py::test_init_all_writes_hashes"
_SLOWER_NODE = "tests/test_auth.py::test_only_the_exact_session_cookie"
_LOWERED_NODE = "tests/test_build.py::test_assembly_always_called"
_REMOVED_NODE = "tests/test_arch.py::test_archive_over_1000"
_STALE_NODE = "tests/test_gone.py::test_renamed_or_removed"
_EXCLUSIONS = (
    durations.DurationExclusion(_OK_NODE, 11.41, 11.33, durations.STATUS_OK),
    durations.DurationExclusion(_SLOWER_NODE, 6.80, 9.42, durations.STATUS_SLOWER),
    durations.DurationExclusion(_LOWERED_NODE, 3.92, 1.30, durations.STATUS_FASTER),
    durations.DurationExclusion(_REMOVED_NODE, 2.54, 0.30, durations.STATUS_FASTER),
    durations.DurationExclusion(_STALE_NODE, 4.10, None, durations.STATUS_STALE),
)
# Separator, header, plus one line per excluded call.
_BLOCK_LEN = 7


def _excluded_summary() -> durations.DurationSummary:
    """Build a verdict carrying the five excluded-call records.

    Returns:
        A summary with no outliers but the exclusion records attached, so only
        the exclusion block is exercised.
    """
    return durations.DurationSummary(
        average=0.10,
        outliers=(),
        runners_up=(),
        floor=_EXCL_FLOOR,
        median=0.10,
        exclusions=_EXCLUSIONS,
    )


def test_window_lists_outliers_floor_and_runners() -> None:
    """The window holds the header, the freak, the marked floor, runners (Q47)."""
    summary = durations.summarize(_FREAK, durations.auto_floor(_FREAK))
    lines = durations_report.window_lines(summary)
    assert lines[0].startswith("Duration outliers")
    assert _FREAK_NODE in lines[1]
    assert "30x median" in lines[1]
    assert lines[2] == ""
    assert lines[3] == _FREAK_FLOOR_LINE
    assert lines[4] == ""
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


def test_exclusion_block_heads_and_accepts() -> None:
    """The block heads the list and reads ``ok`` or restore for a slow call (Q58)."""
    lines = durations_report.exclusion_block(_excluded_summary())
    assert lines[0] == ""
    assert lines[1].startswith("Excluded (accepted slow")
    assert len(lines) == _BLOCK_LEN
    # ok: node, recorded and current shown, verdict ``ok`` (Q56).
    assert f"  {_OK_NODE}  recorded=11.41s  current=11.33s  ok" == lines[2]
    # slower: restore to within two seconds of the recorded baseline (Q57).
    assert _SLOWER_NODE in lines[3]
    assert "current=9.42s" in lines[3]
    assert "restore to within 2s of 6.80s" in lines[3]


def test_exclusion_block_ratchets_and_removes() -> None:
    """A faster or stale entry shows the lowered baseline or removal (Q60, Q61)."""
    lines = durations_report.exclusion_block(_excluded_summary())
    # faster above the floor: the baseline the tool lowered it to (Q69).
    assert _LOWERED_NODE in lines[4]
    assert "baseline lowered to 1.30s" in lines[4]
    # faster below the floor: the entry is removed, back to the normal rule (Q60).
    assert _REMOVED_NODE in lines[5]
    assert "removed (now under the floor)" in lines[5]
    # stale: no current call, the entry is removed (Q61).
    assert _STALE_NODE in lines[6]
    assert "current=(not run)" in lines[6]
    assert "removed (stale)" in lines[6]


def test_exclusion_block_empty_list_renders_no_block() -> None:
    """A run with no exclusions renders no block, so nothing is printed (Q58)."""
    summary = durations.summarize(_TIDY, durations.auto_floor(_TIDY))
    assert durations_report.exclusion_block(summary) == []


# eof
