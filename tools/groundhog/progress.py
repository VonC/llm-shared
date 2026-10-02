"""Progress sink and labels of the groundhog pytest runs (Q03, Q20).

Split out of ``commands.py`` (v0.13.0 full_suite_levels, Step 1) so the
subcommand executors keep headroom for the level-shaped runs: this module
carries the per-mode progress sink (``Progress``, the former ``_Progress``),
the user-bar postfix and the subcommand label shared by the progress lines,
the closing lines and the run lifecycle. The code moved verbatim.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from tools.groundhog import reporting, runner
from tools.groundhog.models import Mode

if TYPE_CHECKING:
    from tools.groundhog.context import Deps, Invocation
    from tools.groundhog.durations import DurationSummary
    from tools.groundhog.models import RunStats
    from tools.groundhog.render import ProgressBar

LOGGER = logging.getLogger("groundhog")


class Progress:
    """Per-mode progress sink: governed LLM lines or the user bar (Q03).

    In LLM mode the cadence governor decides when a key=value line goes
    out (Q04, Q16). In user mode a tqdm bar advances per finished test
    and its postfix carries the same counters to the end of the run (Q20).
    A run that ended without crashing tops the bar off to its total, so
    the bar always closes full instead of just short of 100%.

    Fix: moved out of ``commands.py`` as ``Progress`` (formerly
    ``_Progress``), with no behavior change.
    """

    def __init__(self, invocation: Invocation, deps: Deps) -> None:
        """Wire the sink for one run.

        Args:
            invocation: The parsed invocation, for the mode and label.
            deps: The injectable seams, for the clock and bar factory.
        """
        self._label = sub_label(invocation)
        self._mode = invocation.mode
        self._deps = deps
        self._governor = reporting.ProgressGovernor(deps.clock)
        self._bar: ProgressBar | None = None
        self._seen = 0

    def update(self, stats: RunStats) -> None:
        """Handle one statistics update from the streamed run.

        Args:
            stats: The counters parsed so far.
        """
        if self._mode is Mode.LLM:
            if self._governor.should_emit(stats):
                LOGGER.info("%s", reporting.progress_line(self._label, stats))
            return
        if self._bar is None and stats.total > 0:
            self._bar = self._deps.bar_factory(stats.total, f"ghog {self._label}")
        if self._bar is not None:
            if stats.done > self._seen:
                self._bar.update(stats.done - self._seen)
                self._seen = stats.done
            self._bar.set_postfix_str(postfix(stats))

    def finish(
        self,
        stats: RunStats,
        *,
        completed: bool,
        summary: DurationSummary | None = None,
    ) -> None:
        """Close the run with the final counters and the timing verdict (Q20).

        In LLM mode a full run emits exactly one final summary line carrying
        the ``avg=``/``outliers=`` verdict, after the governor's bare 100%
        line (Q52); any other run emits nothing here, as before.

        In user mode a completed run fills the bar to its total before closing,
        so it reads 100% even when a parameterized node id escaped the parser
        pattern; a crashed run only catches up to the parsed count (Q06). The
        closed bar carries the same verdict in its postfix (Q37).

        Args:
            stats: The final counters of the run.
            completed: Whether the child ended without crashing.
            summary: The duration verdict of a full run, or ``None``.
        """
        if self._mode is Mode.LLM:
            if summary is not None:
                LOGGER.info(
                    "%s",
                    reporting.progress_line(self._label, stats, summary),
                )
            return
        if self._bar is None:
            return
        target = stats.total if completed else stats.done
        if target > self._seen:
            self._bar.update(target - self._seen)
            self._seen = target
        self._bar.set_postfix_str(postfix(stats, summary))
        self._bar.close()


def sub_label(invocation: Invocation) -> str:
    """Return the subcommand label of the progress and closing lines.

    Args:
        invocation: The parsed invocation.

    Returns:
        The label, ``affected --no-cov`` for the ptanc variant.
    """
    if invocation.sub == runner.SUB_AFFECTED and invocation.no_cov:
        return f"{runner.SUB_AFFECTED} --no-cov"
    return invocation.sub


def postfix(stats: RunStats, summary: DurationSummary | None = None) -> str:
    """Build the user-bar postfix carrying the runtime counters (Q20).

    Args:
        stats: The counters parsed so far.
        summary: The duration verdict of a full run, for the closed bar (Q37).

    Returns:
        The postfix text, with the coverage percentage once parsed and the
        ``avg=``/``outliers=`` verdict once the run is judged.
    """
    text = f"fail={stats.failed} warn={stats.warnings} xfail={stats.xfailed}"
    if stats.cov_percent is not None:
        text = f"{text} cov={reporting.format_percent(stats.cov_percent)}"
    if summary is not None:
        text = f"{text} {reporting.progress_suffix(summary)}"
    return text


# eof
