"""Compose the floor file and the pure duration rule for a full run (Step 4).

The true-outlier rule in ``durations.py`` stays pure — no IO, no floor import
— so it is judged in isolation. This module is the application seam between a
run and that rule: it tells whether a run times its calls (``full`` only, Q39),
and for a run already green on tests and coverage it reads the override, persists
the auto floor and hands the call map to the rule. Keeping the gating and the
floor IO here keeps ``commands.py`` under its line budget and ``durations.py``
free of IO.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.groundhog import durations, floor, runner
from tools.groundhog.models import EXIT_OBJECTIVE_MET

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from tools.groundhog.context import Invocation
    from tools.groundhog.durations import DurationSummary
    from tools.groundhog.models import RunResult


def measures_durations(invocation: Invocation) -> bool:
    """Tell whether the invocation times each test call (Q39).

    Args:
        invocation: The parsed invocation.

    Returns:
        True for a ``full`` run, the only one given ``--durations`` (Q39).
    """
    return invocation.sub == runner.SUB_FULL


def judge(
    invocation: Invocation,
    result: RunResult,
    base_code: int,
) -> DurationSummary | None:
    """Form the duration verdict, judged last on a green full run (Q34).

    Outliers are judged last (Q34): a verdict is formed only for a ``full`` run
    already green on tests and coverage, so a failure, a gap or a crash keeps
    its own exit code and withholds the timing verdict.

    Args:
        invocation: The parsed invocation.
        result: The parsed run result.
        base_code: The exit code before the outlier rule, the green gate.

    Returns:
        The duration verdict, or ``None`` when none is formed.
    """
    if not measures_durations(invocation):
        return None
    if base_code != EXIT_OBJECTIVE_MET:
        return None
    return _judge_map(invocation.root, result.stats.durations)


def _judge_map(
    root: Path,
    durations_map: Mapping[str, float],
) -> DurationSummary | None:
    """Persist the auto floor and judge the run's call durations (Q42, Q48).

    The run reads its own line-2 floor (of ``a.ghog.outliers``), recomputes the
    auto floor (``k * median``) and writes both lines — line 1 a write-only
    record (Q48) — then gates the calls against the active floor: the line-2
    value when a project set one, else the one-second default (Q43). A fresh
    file is seeded with that default, so line 2 reads back as ``1.0``.

    Args:
        root: The consuming project root, where the floor file lives.
        durations_map: Node id to call-phase seconds of the full run.

    Returns:
        The verdict, or ``None`` when the run captured no durations (so no
        floor is written and nothing is judged).
    """
    if not durations_map:
        return None
    override = floor.read_floor(root)
    auto = durations.auto_floor(durations_map)
    floor.write_floor(
        root,
        auto,
        override if override is not None else floor.DEFAULT_FLOOR,
    )
    active = floor.active_floor(override)
    return durations.summarize(durations_map, active)


# eof
