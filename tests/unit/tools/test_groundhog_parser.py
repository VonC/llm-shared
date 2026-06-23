"""Unit tests for the groundhog streaming pytest output parser.

Cover the collected count, the -v result statuses, the warnings summary,
the TOTAL coverage line (Q19), the FAILURES/ERRORS block capture (Q08),
the slowest-durations block capture (Q36, Q39), the last started tests,
the output tail and the INTERNALERROR crash marker (Q06).

Fix: the slowest-durations block of a full run is now captured into
stats.durations, call phase only, keyed by node and kept whole for a
parametrized id with spaces (Q49); the block opens on its banner and
closes on the next banner, the final summary line included.
"""

from __future__ import annotations

from tools.groundhog.parser import LAST_STARTED_KEPT, PytestOutputParser

_COLLECTED = 4
_ANSI_COLLECTED = 3
_EXPECTED_DONE = 4
_EXPECTED_FAILED = 2
_EXPECTED_WARNINGS = 3
_FULL_COVERAGE = 100.0
_PARTIAL_COVERAGE = 97.4
_SELECTED = 128
_SLOW_CALL_SECS = 1.83
_FAST_CALL_SECS = 0.02
_PARAM_CALL_SECS = 0.5


def _feed_lines(parser: PytestOutputParser, lines: list[str]) -> None:
    """Feed a canned transcript line by line.

    Args:
        parser: The parser under test.
        lines: The transcript lines, newline free.
    """
    for line in lines:
        parser.feed(line)


def test_collected_and_results_update_counters() -> None:
    """Result lines update done, failed, xfailed and the failing ids."""
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            f"collected {_COLLECTED} items",
            "tests/test_a.py::test_one PASSED [ 25%]",
            "tests/test_a.py::test_two FAILED [ 50%]",
            "tests/test_b.py::test_three ERROR [ 75%]",
            "tests/test_b.py::test_four XFAIL [100%]",
        ],
    )
    assert parser.stats.total == _COLLECTED
    assert parser.stats.done == _EXPECTED_DONE
    assert parser.stats.failed == _EXPECTED_FAILED
    assert parser.stats.xfailed == 1
    assert parser.stats.failed_ids == [
        "tests/test_a.py::test_two",
        "tests/test_b.py::test_three",
    ]


def test_ansi_colored_lines_still_update_counters() -> None:
    """Forced color escapes are stripped before matching (FORCE_COLOR pipe).

    pytest honors FORCE_COLOR even on a non-TTY pipe, so the collected line
    arrives as a reset code butted against ``collected`` and the statuses as
    color-wrapped words. Stripping the escapes first keeps the total, the done
    count, the xfail count and the failing ids correct, so the LLM-mode progress
    governor is not silenced by a zero total.
    """
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "\x1b[1mcollecting ... \x1b[0mcollected 3 items",
            "tests/test_a.py::test_one \x1b[32mPASSED\x1b[0m\x1b[32m [ 33%]\x1b[0m",
            "tests/test_a.py::test_two \x1b[31mFAILED\x1b[0m\x1b[31m [ 66%]\x1b[0m",
            "tests/test_a.py::test_three \x1b[32mXFAIL\x1b[0m [100%]",
        ],
    )
    assert parser.stats.total == _ANSI_COLLECTED
    assert parser.stats.done == _ANSI_COLLECTED
    assert parser.stats.failed == 1
    assert parser.stats.xfailed == 1
    assert parser.stats.failed_ids == ["tests/test_a.py::test_two"]


def test_ansi_colored_durations_block_still_captures_call_times() -> None:
    """Color escapes never hide the slowest-durations block (the outlier gate).

    The durations block is colorized under FORCE_COLOR too; stripping the
    escapes keeps the call-phase seconds captured, so the true-outlier rule is
    not silently skipped on a forced-color pipe (Q36, Q39).
    """
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "\x1b[1m========== slowest durations ==========\x1b[0m",
            "\x1b[33m1.83s call     tests/test_a.py::test_one\x1b[0m",
            "\x1b[32m0.02s call     tests/test_b.py::test_two\x1b[0m",
        ],
    )
    assert parser.stats.durations == {
        "tests/test_a.py::test_one": _SLOW_CALL_SECS,
        "tests/test_b.py::test_two": _FAST_CALL_SECS,
    }


def test_skipped_and_xpass_count_as_done_only() -> None:
    """SKIPPED and XPASS finish a test without counting as a failure."""
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "collected 2 items",
            "tests/test_a.py::test_skip SKIPPED [ 50%]",
            "tests/test_a.py::test_xpass XPASS [100%]",
        ],
    )
    assert parser.stats.done == _EXPECTED_FAILED
    assert parser.stats.failed == 0
    assert parser.stats.xfailed == 0


def test_deselected_tests_reduce_the_total() -> None:
    """A testmon collect line counts only the selected tests (Q20)."""
    parser = PytestOutputParser()
    parser.feed("collected 5238 items / 5110 deselected / 128 selected")
    assert parser.stats.total == _SELECTED


def test_total_line_sets_coverage_percent() -> None:
    """The TOTAL line of the coverage report sets cov_percent (Q19)."""
    parser = PytestOutputParser()
    parser.feed("TOTAL     1234    0   100%")
    assert parser.stats.cov_percent == _FULL_COVERAGE


def test_total_line_with_decimal_percent() -> None:
    """A decimal TOTAL percentage is parsed as a float (Q19)."""
    parser = PytestOutputParser()
    parser.feed("TOTAL     1234   12   97.4%")
    assert parser.stats.cov_percent == _PARTIAL_COVERAGE


def test_summary_line_sets_warnings() -> None:
    """The final tally line carries the warnings count."""
    parser = PytestOutputParser()
    parser.feed("====== 2 failed, 40 passed, 3 warnings in 1.23s ======")
    assert parser.stats.warnings == _EXPECTED_WARNINGS


def test_summary_line_without_warnings_keeps_zero() -> None:
    """A tally line without warnings leaves the counter at zero."""
    parser = PytestOutputParser()
    parser.feed("====== 42 passed in 1.23s ======")
    assert parser.stats.warnings == 0


def test_failure_block_is_captured_verbatim() -> None:
    """The FAILURES section is captured until the next banner (Q08)."""
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "=================== FAILURES ===================",
            "______ test_two ______",
            "E   AssertionError",
            "============ short test summary info ============",
            "FAILED tests/test_a.py::test_two - AssertionError",
        ],
    )
    assert parser.failure_block == (
        "=================== FAILURES ===================",
        "______ test_two ______",
        "E   AssertionError",
    )


def test_errors_banner_also_opens_the_capture() -> None:
    """The ERRORS section is captured like the FAILURES one (Q08)."""
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "=================== ERRORS ===================",
            "E   ImportError",
        ],
    )
    assert parser.failure_block == (
        "=================== ERRORS ===================",
        "E   ImportError",
    )


def test_non_failure_banner_does_not_capture() -> None:
    """A non-failure banner outside a capture stays uncaptured."""
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "============ warnings summary ============",
            "some warning detail",
        ],
    )
    assert parser.failure_block == ()


def test_internal_error_marker_sets_the_crash_flag() -> None:
    """An INTERNALERROR line raises the crash flag (Q06)."""
    parser = PytestOutputParser()
    parser.feed("INTERNALERROR> Traceback (most recent call last):")
    assert parser.internal_error is True


def test_last_started_keeps_the_most_recent_tests() -> None:
    """Only the last started tests are kept as crash context (Q06)."""
    parser = PytestOutputParser()
    count = LAST_STARTED_KEPT + 2
    parser.feed(f"collected {count} items")
    for index in range(count):
        parser.feed(f"tests/test_a.py::test_{index} PASSED")
    assert len(parser.stats.last_started) == LAST_STARTED_KEPT
    assert parser.stats.last_started[-1] == f"tests/test_a.py::test_{count - 1}"


def test_coverage_table_is_captured_for_the_gap_report() -> None:
    """The term-missing table is captured, header to TOTAL line (Q24)."""
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "before the table",
            "Name                  Stmts   Miss  Cover   Missing",
            "---------------------------------------------------",
            "src/pkg/mod.py          120      7    94%   48, 86-88, 100",
            "---------------------------------------------------",
            "TOTAL                 34000      8    99%",
            "1 file skipped due to complete coverage.",
        ],
    )
    assert parser.coverage_block[0].startswith("Name")
    assert "src/pkg/mod.py" in parser.coverage_block[2]
    assert parser.coverage_block[-1].startswith("TOTAL")
    assert "skipped due to complete coverage" not in parser.coverage_block[-1]


def test_no_coverage_table_means_an_empty_block() -> None:
    """Without the table header, nothing is captured (Q24)."""
    parser = PytestOutputParser()
    _feed_lines(parser, ["collected 1 items", "TOTAL    10    0   100%"])
    assert parser.coverage_block == ()


def test_tail_skips_blank_lines() -> None:
    """Blank lines never enter the output tail."""
    parser = PytestOutputParser()
    _feed_lines(parser, ["first", "", "second"])
    assert parser.tail == ("first", "second")


def test_durations_block_captures_call_phase_only() -> None:
    """The slowest-durations block records only call-phase seconds (Q36).

    The setup and teardown phases are skipped, and a call line after the
    next banner is left out, so the block stops at that banner (Q39).
    """
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "================= slowest durations =================",
            "1.83s call     tests/test_a.py::test_one",
            "0.40s setup    tests/test_a.py::test_one",
            "0.02s teardown tests/test_a.py::test_one",
            "0.02s call     tests/test_b.py::test_two",
            "============ short test summary info ============",
            "9.99s call     tests/test_c.py::test_after_banner",
        ],
    )
    assert parser.stats.durations == {
        "tests/test_a.py::test_one": _SLOW_CALL_SECS,
        "tests/test_b.py::test_two": _FAST_CALL_SECS,
    }


def test_durations_block_stops_at_the_summary_line() -> None:
    """The final tally line, itself a banner, closes the capture (Q39)."""
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "================= slowest durations =================",
            "1.83s call     tests/test_a.py::test_one",
            "====== 2 passed in 2.31s ======",
            "0.50s call     tests/test_late.py::test_late",
        ],
    )
    assert parser.stats.durations == {"tests/test_a.py::test_one": _SLOW_CALL_SECS}


def test_no_durations_block_leaves_the_map_empty() -> None:
    """A duration line with no opening banner is ignored (Q39)."""
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "collected 1 items",
            "tests/test_a.py::test_one PASSED [100%]",
            "1.83s call     tests/test_a.py::test_one",
        ],
    )
    assert parser.stats.durations == {}


def test_durations_keep_a_parametrized_id_with_spaces() -> None:
    """A space-bearing parametrized id is captured whole, not chopped (Q49)."""
    parser = PytestOutputParser()
    _feed_lines(
        parser,
        [
            "================= slowest durations =================",
            "0.50s call     tests/test_p.py::test_x[a b]",
        ],
    )
    assert parser.stats.durations == {"tests/test_p.py::test_x[a b]": _PARAM_CALL_SECS}


# eof
