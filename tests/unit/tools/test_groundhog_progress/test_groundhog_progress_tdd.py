"""Unit tests for the groundhog progress sink, postfix and label (Q03, Q20).

v0.13.0 full_suite_levels, Step 1: the label and postfix cases moved here
unchanged from ``test_groundhog_cli.py`` and ``test_groundhog_commands.py``,
beside the helpers that moved from ``commands.py`` to ``progress.py``. The
sink itself is driven directly in both modes against a fake bar, so the
module is fully covered on its own: governed LLM lines and the final verdict
line, the bar opened on the first collected total, advanced by finished
tests, topped off on completion and only caught up on a crash.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from tools.groundhog import progress, runner
from tools.groundhog.context import Deps, Invocation
from tools.groundhog.durations import DurationCall, DurationSummary
from tools.groundhog.models import Mode, RunStats

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

_GATE_FULL = 100.0
_FREAK_NODE = "tests/test_slow.py::test_freak"
_TOTAL = 4
_HALF = 2


class _FakeBar:
    """A fake user bar satisfying the ProgressBar protocol (Q20)."""

    def __init__(self) -> None:
        """Start with empty recordings."""
        self.updates: list[int] = []
        self.postfixes: list[str] = []
        self.closed = False

    def update(self, n: int) -> object:
        """Record one advance.

        Args:
            n: Finished tests since the previous advance.

        Returns:
            None.
        """
        self.updates.append(n)
        return None

    def set_postfix_str(self, s: str) -> object:
        """Record one postfix update.

        Args:
            s: The counters text.

        Returns:
            None.
        """
        self.postfixes.append(s)
        return None

    def close(self) -> object:
        """Record the close.

        Returns:
            None.
        """
        self.closed = True
        return None


def _invocation(sub: str, *, no_cov: bool, root: Path, mode: Mode = Mode.LLM) -> Invocation:
    """Build an invocation for direct helper tests.

    Args:
        sub: The subcommand name.
        no_cov: The coverage toggle.
        root: The project root.
        mode: The output mode.

    Returns:
        The invocation.
    """
    return Invocation(
        sub=sub,
        files=(),
        no_cov=no_cov,
        mode=mode,
        root=root,
    )


def _deps(bars: list[_FakeBar], descriptions: list[str]) -> Deps:
    """Build seams recording every bar the sink opens.

    Args:
        bars: Receives the fake bars created by the bar factory.
        descriptions: Receives the bar descriptions.

    Returns:
        The injectable seams with a frozen clock.
    """

    def _bar_factory(total: int, description: str) -> _FakeBar:
        del total
        descriptions.append(description)
        bar = _FakeBar()
        bars.append(bar)
        return bar

    return Deps(clock=lambda: 0.0, bar_factory=_bar_factory)


def _summary(outliers: tuple[DurationCall, ...]) -> DurationSummary:
    """Build a duration verdict for the postfix and final-line tests.

    Args:
        outliers: The flagged outliers carried by the verdict.

    Returns:
        The summary, with a fixed average and floor.
    """
    return DurationSummary(
        average=0.10,
        outliers=outliers,
        runners_up=(),
        floor=1.05,
        median=0.10,
    )


def _stats(total: int, done: int) -> RunStats:
    """Build counters for one streamed update.

    Args:
        total: The collected total.
        done: The finished tests.

    Returns:
        The counters.
    """
    stats = RunStats()
    stats.total = total
    stats.done = done
    return stats


def test_sub_label_for_the_ptanc_variant(tmp_path: Path) -> None:
    """The label spells the --no-cov variant (Q16)."""
    nocov = _invocation(runner.SUB_AFFECTED, no_cov=True, root=tmp_path)
    assert progress.sub_label(nocov) == "affected --no-cov"
    plain = _invocation(runner.SUB_AFFECTED, no_cov=False, root=tmp_path)
    assert progress.sub_label(plain) == "affected"


def test_postfix_with_and_without_coverage() -> None:
    """The bar postfix adds the coverage once parsed (Q20)."""
    stats = RunStats()
    assert progress.postfix(stats) == "fail=0 warn=0 xfail=0"
    stats.cov_percent = _GATE_FULL
    assert progress.postfix(stats) == "fail=0 warn=0 xfail=0 cov=100"


def test_postfix_appends_the_timing_verdict() -> None:
    """The closed-bar postfix gains avg= and outliers= once judged (Q37)."""
    stats = RunStats()
    stats.cov_percent = _GATE_FULL
    plain = progress.postfix(stats)
    assert "avg=" not in plain
    outlier = DurationCall(node=_FREAK_NODE, seconds=5.0, ratio=50.0)
    judged = progress.postfix(stats, _summary((outlier,)))
    assert "avg=0.100s" in judged
    assert "outliers=1" in judged


def test_llm_mode_emits_governed_lines_and_the_final_verdict(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """LLM lines follow the governor; only a judged finish adds the verdict (Q04, Q52)."""
    caplog.set_level(logging.INFO, logger="groundhog")
    bars: list[_FakeBar] = []
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    sink = progress.Progress(invocation, _deps(bars, []))
    sink.update(_stats(0, 0))
    sink.update(_stats(_TOTAL, 0))
    sink.update(_stats(_TOTAL, 0))
    assert caplog.messages == ["ghog full: 0% (0/4) fail=0 warn=0 xfail=0"]
    sink.finish(_stats(_TOTAL, _TOTAL), completed=True)
    assert len(caplog.messages) == 1
    sink.finish(_stats(_TOTAL, _TOTAL), completed=True, summary=_summary(()))
    assert caplog.messages[-1].endswith("avg=0.100s outliers=0")
    assert bars == []


def test_user_mode_opens_advances_and_tops_off_the_bar(tmp_path: Path) -> None:
    """The bar opens on the first total, advances, then fills on completion (Q20)."""
    bars: list[_FakeBar] = []
    descriptions: list[str] = []
    invocation = _invocation(runner.SUB_AFFECTED, no_cov=True, root=tmp_path, mode=Mode.USER)
    sink = progress.Progress(invocation, _deps(bars, descriptions))
    sink.update(_stats(0, 0))
    assert bars == []
    sink.update(_stats(_TOTAL, _HALF))
    sink.update(_stats(_TOTAL, _HALF))
    assert descriptions == ["ghog affected --no-cov"]
    assert bars[0].updates == [_HALF]
    assert bars[0].postfixes == ["fail=0 warn=0 xfail=0", "fail=0 warn=0 xfail=0"]
    sink.finish(_stats(_TOTAL, _HALF), completed=True, summary=_summary(()))
    assert bars[0].updates == [_HALF, _TOTAL - _HALF]
    assert bars[0].postfixes[-1].endswith("avg=0.100s outliers=0")
    assert bars[0].closed is True


def test_user_mode_crash_catches_up_without_topping_off(tmp_path: Path) -> None:
    """A crashed run closes the bar at the parsed count only (Q06)."""
    bars: list[_FakeBar] = []
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path, mode=Mode.USER)
    sink = progress.Progress(invocation, _deps(bars, []))
    sink.update(_stats(_TOTAL, _HALF))
    sink.finish(_stats(_TOTAL, _HALF), completed=False)
    assert bars[0].updates == [_HALF]
    assert bars[0].closed is True


def test_user_mode_without_a_total_closes_no_bar(tmp_path: Path) -> None:
    """A run that never collected anything never opens nor closes a bar (Q20)."""
    bars: list[_FakeBar] = []
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path, mode=Mode.USER)
    sink = progress.Progress(invocation, _deps(bars, []))
    sink.finish(_stats(0, 0), completed=True)
    assert bars == []


# eof
