"""groundhog (alias ``ghog``): the pytest reset tool package.

One Python entry point plus thin bat wrappers replace the ptr/pta/pts
doskey aliases, per ``tools/Pytest reset specs.md``: ``cli`` owns the
argument parsing and dispatch, ``commands`` the subcommand executors
and exit-code classification, ``context`` the injectable seams,
``runner`` the child processes, ``parser`` the streamed pytest output,
``baseline`` the focus comparison file, ``gate`` the coverage gate,
``reporting`` the report contract, ``redirect`` the Q31 self-redirect
guard of unredirected LLM runs, ``render`` the user-mode tqdm seam,
``init_files`` the skill registration of a consuming repository,
``snapshot`` the source digest behind the ghog day noop, and ``status``
the Q32 run lifecycle: the ``a.ghog.status`` contract, the read-only
``ghog status`` reporter, the live-run refusal and the detached day
walk.

v0.13.0 full_suite_levels, Step 1: ``verdicts`` now holds the exit-code
classification and ``progress`` the progress sink and labels, both moved out
of ``commands``; ``levels`` adds the full-suite level value and its
resolution, ``proof`` the accumulation, cap, noop and upgrade rules, and
``snapshot`` the key=value proof marker of each scope with the timing
fingerprint, all pure or adapter models the walk wires from Step 2.

v0.13.0 full_suite_levels, Step 2: the walk, the full run, the reports and
the status file run by level with saved proof; ``evidence`` holds the run
evidence (objective, source, proof, reuse and scope) that the closing line
and ``a.ghog.status`` append, and the outcome each executor returns; and
``detach`` the detached day walk and its survivor spawn, split out of
``status``.

Step 3 adds ``group_patterns``, ``groups`` and ``project_settings`` for group
resolution, plus read-only ``listings``. The shared ``tools.scope_capture``
value records exact resolutions for future run and review consumers.

Step 4 adds ``scope`` for explicit and environment selection and ``group_coverage``
for isolated source evidence. Walks share one inventory, carry scope in reports
and detached captures, and judge group durations without writing shared settings.
"""

from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_NOT_PYTEST_PROJECT,
    EXIT_OBJECTIVE_MET,
    EXIT_RUN_LIVE,
    EXIT_RUN_LOST,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    GroundhogError,
    Mode,
    RunResult,
    RunStats,
)

__all__ = [
    "EXIT_COVERAGE_GAP",
    "EXIT_DURATION_OUTLIERS",
    "EXIT_NOT_PYTEST_PROJECT",
    "EXIT_OBJECTIVE_MET",
    "EXIT_RUN_LIVE",
    "EXIT_RUN_LOST",
    "EXIT_SETUP_ERROR",
    "EXIT_SUITE_CRASH",
    "EXIT_TEST_FAILURES",
    "GroundhogError",
    "Mode",
    "RunResult",
    "RunStats",
]


# eof
