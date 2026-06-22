"""The ghog day walk: check, affected --no-cov, full, with per-step timing.

Split out of ``commands.py`` so that module stays under the repo line budget
(Q22): the walk orchestration and its per-step timestamp headers live here,
while the individual step executors (check and the pytest runs) stay in
``commands.py``. ``status.py`` dispatches the ``day`` subcommand to
:func:`run_day`.

Each step is bracketed by a ``started``/``ended`` header carrying a full local
timestamp and, on the end header, the step duration measured on the injected
monotonic clock. The headers land in ``a.ghog.log`` (and the mirrored
envelope), so a stale log read after a silent no-op shows old timestamps
instead of passing as a fresh green result.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from tools.groundhog import commands, reporting, runner, snapshot
from tools.groundhog.models import EXIT_OBJECTIVE_MET, RunStats

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.groundhog.context import Deps, Invocation


def run_day(invocation: Invocation, deps: Deps) -> int:
    """Walk the whole chain: check, affected --no-cov, full (Q22).

    The walk stops at the first non-green step, whose report already
    names the fix to apply; the fixing, and the loop around it, stay
    with the caller. A missing check.bat skips to the test steps (Q10).
    A walk whose source snapshot matches the last green walk is a noop
    (Q28), unless forced, so chained instructions may call it twice for
    free; a fully green walk records the new snapshot. Each step is
    bracketed by timestamped start/end headers (:func:`_timed_step`).

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        The exit code of the first non-green step, or the full run's.
    """
    if not invocation.force and snapshot.is_unchanged(invocation.root):
        commands.emit_summary([reporting.MSG_DAY_NOOP])
        closing = reporting.closing_line(
            invocation.root.name,
            runner.SUB_DAY,
            RunStats(),
            EXIT_OBJECTIVE_MET,
            reporting.ClosingMetrics(reporting.COV_SKIPPED),
        )
        commands.emit_summary([closing])
        return EXIT_OBJECTIVE_MET
    project = invocation.root.name
    code = _timed_step(
        project,
        "check",
        deps,
        lambda: commands.run_check(replace(invocation, sub=runner.SUB_CHECK), deps),
    )
    if code != EXIT_OBJECTIVE_MET:
        return code
    code = _timed_step(
        project,
        "affected --no-cov",
        deps,
        lambda: commands.run_tests(
            replace(invocation, sub=runner.SUB_AFFECTED, no_cov=True),
            deps,
        ),
    )
    if code != EXIT_OBJECTIVE_MET:
        return code
    code = _timed_step(
        project,
        "full",
        deps,
        lambda: commands.run_tests(
            replace(invocation, sub=runner.SUB_FULL, no_cov=False),
            deps,
        ),
    )
    if code == EXIT_OBJECTIVE_MET:
        snapshot.write_marker(invocation.root)
    return code


def _timed_step(
    project: str,
    label: str,
    deps: Deps,
    run: Callable[[], int],
) -> int:
    """Run one day-walk step framed by a separator rule and timestamp headers.

    A dashed rule and a start header are emitted before the step, an end
    header and a closing rule after it; each header carries the local
    wall-clock time, and the end header also carries the step duration
    measured on the injected monotonic clock.

    Args:
        project: The consuming project name, the report prefix.
        label: The step label (``check``, ``affected --no-cov``, ``full``).
        deps: The injectable seams, for the monotonic duration clock.
        run: The step thunk returning its exit code.

    Returns:
        The step exit code, unchanged.
    """
    commands.emit_summary(
        [
            reporting.step_open_banner(project),
            reporting.step_started_line(project, label, reporting.now_local()),
            reporting.step_rule(project),
        ],
    )
    start = deps.clock()
    code = run()
    duration = max(0.0, deps.clock() - start)
    commands.emit_summary(
        [
            reporting.step_rule(project),
            reporting.step_ended_line(project, label, reporting.now_local(), duration),
            reporting.step_close_banner(project),
        ],
    )
    return code


# eof
