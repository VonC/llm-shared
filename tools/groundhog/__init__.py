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
"""

from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
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
