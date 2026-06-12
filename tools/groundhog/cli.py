"""groundhog (alias ``ghog``): the pytest reset tool entry point.

Subcommands (Q02, Q15): ``check`` runs check.bat from the project root,
``full`` re-runs the whole suite with a fresh testmon database and
coverage (ptr), ``affected`` runs the testmon-selected tests (pta, with
``--no-cov`` for ptanc), ``single`` runs named test files in focus (pts),
``day`` walks the whole chain — check, then affected --no-cov, then
full — stopping at the first non-green step (Q22), ``init`` registers
the skill pointers (Claude skill, AGENTS.md section) in the consuming
project (Q23), and ``status`` replays the run lifecycle recorded in
``a.ghog.status`` (Q32).

The output mode is picked by TTY auto-detection with ``--user``/``--llm``
force flags (Q03). Every run ends with the next-step message of the
run-state table and the key=value closing line (Q16), and exits with the
contract codes: 0 objective met, 2 test failures, 3 coverage gap, 4 suite
crash, 5 environment or setup error (Q12), plus the two lifecycle codes
of Q32: 6 a run is live, 7 the last run is lost. An LLM run whose stdout
is an unredirected harness capture self-redirects its report to
``a.ghog.log`` and hands the capture only the envelope lines (Q31),
through the ``redirect`` guard armed right after the invocation is
parsed. Every run also brackets itself in ``a.ghog.status`` (Q32):
``status`` reports it without starting anything, a run started while
another one is alive refuses with exit 6, and ``day --detach`` spawns
the walk as a survivor process polled through ``ghog status``.

Split for the repo line budget: this module keeps the argument parsing,
the mode pick, the logging setup and the dispatch; the subcommand
executors live in ``commands.py`` and the injectable seams in
``context.py``.

Usage::

    python cli.py full [--root PATH] [--user | --llm]
    python cli.py affected [--no-cov]
    python cli.py single tests/test_a.py tests/test_b.py
    python cli.py check
"""

from __future__ import annotations

import argparse
import contextlib
import io
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _bootstrap_root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(_bootstrap_root))

from tools import find_project_root
from tools.groundhog import commands, redirect, runner, status
from tools.groundhog.context import Deps, Invocation
from tools.groundhog.models import EXIT_SETUP_ERROR, Mode

if TYPE_CHECKING:
    from collections.abc import Sequence

LOGGER = logging.getLogger("groundhog")


def pick_mode(*, user: bool, llm: bool, tty: bool) -> Mode:
    """Pick the output mode (Q03).

    Args:
        user: The ``--user`` force flag.
        llm: The ``--llm`` force flag.
        tty: Whether stdout is a terminal.

    Returns:
        USER when forced or on a terminal, LLM otherwise.
    """
    if user:
        return Mode.USER
    if llm:
        return Mode.LLM
    return Mode.USER if tty else Mode.LLM


def main(argv: Sequence[str] | None = None, deps: Deps | None = None) -> int:
    """Run one groundhog subcommand.

    Args:
        argv: Command-line arguments, ``sys.argv[1:]`` when ``None``.
        deps: Injectable seams, the defaults outside tests.

    Returns:
        The contract exit code (Q12), or check.bat's own code for
        ``ghog check``.
    """
    _configure_logging()
    active = deps if deps is not None else Deps()
    args = _build_arg_parser().parse_args(list(argv) if argv is not None else None)
    try:
        root = _resolve_root(args.root)
    except FileNotFoundError as error:
        LOGGER.info("ghog: %s", error)
        return EXIT_SETUP_ERROR
    invocation = Invocation(
        sub=str(args.sub),
        files=tuple(getattr(args, "files", ()) or ()),
        no_cov=bool(getattr(args, "no_cov", False)),
        mode=pick_mode(user=args.user, llm=args.llm, tty=_stdout_is_tty()),
        root=root,
        force=bool(getattr(args, "force", False)),
        detach=bool(getattr(args, "detach", False)),
    )
    # The Q32 paths keep their bounded envelope on stdout: no guard, no
    # senv replay, and no mirror left armed by an earlier in-process run.
    redirect.disarm()
    if invocation.sub == runner.SUB_STATUS:
        redirect.consume_senv_log()
        return status.run_status(invocation)
    live = status.live_run(invocation.root)
    if live is not None:
        redirect.consume_senv_log()
        return status.refuse_live_run(live)
    if invocation.sub == runner.SUB_DAY and invocation.detach:
        return status.run_day_detached(invocation, active)
    redirect.activate_if_captured(invocation.mode, invocation.root)
    redirect.replay_senv_log()
    if invocation.sub == runner.SUB_INIT:
        return commands.run_init(invocation, active)
    return status.run_with_lifecycle(invocation, active)


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the ghog argument parser with its subcommands (Q15).

    Returns:
        The configured parser.
    """
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        help="Project root override (defaults to the .git root, Q14).",
    )
    common.add_argument(
        "--user",
        action="store_true",
        help="Force user mode: progress bar (Q03).",
    )
    common.add_argument(
        "--llm",
        action="store_true",
        help="Force LLM mode: plain progress lines (Q03).",
    )
    parser = argparse.ArgumentParser(
        prog="ghog",
        description="groundhog: pytest reset tool (see tools/Pytest reset specs.md).",
    )
    subparsers = parser.add_subparsers(dest="sub", required=True)
    subparsers.add_parser(
        runner.SUB_CHECK,
        parents=[common],
        help="Run check.bat from the project root (Q10).",
    )
    subparsers.add_parser(
        runner.SUB_FULL,
        parents=[common],
        help="Full suite, fresh testmon data, coverage (ptr).",
    )
    affected = subparsers.add_parser(
        runner.SUB_AFFECTED,
        parents=[common],
        help="testmon-selected tests with appended coverage (pta).",
    )
    affected.add_argument(
        "--no-cov",
        action="store_true",
        help="Skip coverage, the ptanc variant.",
    )
    single = subparsers.add_parser(
        runner.SUB_SINGLE,
        parents=[common],
        help="Named test files in focus, no coverage (pts).",
    )
    single.add_argument("files", nargs="+", help="Test files, not functions.")
    day = subparsers.add_parser(
        runner.SUB_DAY,
        parents=[common],
        help=(
            "Walk the chain: check, then affected --no-cov, then full, "
            "stopping at the first non-green step (Q22)."
        ),
    )
    day.add_argument(
        "--force",
        action="store_true",
        help="Walk even when nothing changed since the last green walk (Q28).",
    )
    day.add_argument(
        "--detach",
        action="store_true",
        help=(
            "Spawn the walk as a survivor process wired to a.ghog.log and "
            "return at once; poll ghog status until state=done (Q32)."
        ),
    )
    subparsers.add_parser(
        runner.SUB_INIT,
        parents=[common],
        help=(
            "Register the groundhog skill pointers in the project: "
            ".claude skill and AGENTS.md section (Q23)."
        ),
    )
    subparsers.add_parser(
        runner.SUB_STATUS,
        parents=[common],
        help=(
            "Replay the run lifecycle recorded in a.ghog.status without "
            "starting anything (Q32)."
        ),
    )
    return parser


def _resolve_root(root_arg: str | None) -> Path:
    """Resolve the consuming project root.

    Args:
        root_arg: The ``--root`` override, or ``None``.

    Returns:
        The resolved project root.

    Raises:
        FileNotFoundError: When no ``.git`` root is found.
    """
    if root_arg:
        return Path(root_arg).resolve()
    return find_project_root(Path.cwd())


def _stdout_is_tty() -> bool:
    """Tell whether stdout is a terminal, the Q03 auto-detection.

    Returns:
        True on a terminal, False on a captured stream.
    """
    return sys.stdout.isatty()


def _configure_logging() -> None:
    """Configure a single stdout handler at INFO level for the tool.

    The stream is switched to replace-on-encoding-error first, so a
    child line carrying characters outside the console code page (the
    box-drawing output of ty, for example) degrades to placeholders
    instead of crashing the logging handler (Q29).
    """
    stream = sys.stdout
    if isinstance(stream, io.TextIOWrapper):
        with contextlib.suppress(OSError, ValueError):
            stream.reconfigure(errors="replace")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    for old_handler in root_logger.handlers:
        old_handler.close()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


# eof
