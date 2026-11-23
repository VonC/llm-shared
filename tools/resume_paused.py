r"""Human-only bulk resume of paused agent sessions: parse, compose and render.

Step 8 of v0.14.0 resume-paused ships the ``resume_paused`` command, launched
through ``bin\resume_paused.bat``. This module only parses the documented
arguments, composes the Step 1 to 7 readers, planner, delivery and takeover
into one run, and renders the run's result:

1. ``parse_arguments`` accepts ``--dry-run``, ``--clear`` and the repeatable
   ``--except`` and ``--switch-roles`` name lists (``NAME[,NAME...]``), plus
   ``--help``; anything else, an empty name or a timeout override is a syntax
   error, exit 2, before any discovery.
2. ``execute`` classifies the caller first (design Q08, ``classify_caller``):
   a recognized agent caller is refused, dry runs included, before TUIOS is
   listed or a journal is read. The caller's own ``TUIOS_PANE_ID`` pane, when
   the command runs inside TUIOS, is protected; outside TUIOS none is set.
3. ``compose`` binds one run's ports: the TUIOS transport over argument-list
   runners, the saved-pause reader, the saved-exchange observer, the session
   journal index, the nonblocking checkout guard, the ``PlanRecheck`` of this
   request before every send (with a fresh journal read), and the marked
   takeover with its reviewer wait
   and design Q27=B all-pane idle guard. The host-profile adapters arrive in
   one ``HostAdapters`` bundle. No host profile is pinned yet (plan Q05), so
   ``unpinned_hosts`` reads no command history or agent log, proves no screen,
   selects no delivery profile and proves no reviewer absence: a real run
   fails closed before any input.
4. ``render_run`` (``tools.resume_paused_report``) prints one compact line per
   prompt-bearing checkout and the omitted-pane count; every Claude reviewer
   outcome and conditional Claude preview carries ``limits=claude-wait-scope``.
   Exit 0 for success, expected skips and pending reviewers, 1 for any
   classification or execution failure, 2 for invalid syntax.

Fix (Step 8 line budget): the rendering moved to
``tools.resume_paused_report`` so this module stays below the 650-line
ceiling, limited to parsing and composition.

Fix (Step 8 code review round 1): the ``PlanRecheck`` before every send reads
the session journal again instead of reusing the index read for planning, so
a resume recorded after planning skips the send and an unreadable journal at
that boundary fails it, with no input either way.

Agents never run this command, help and preview included; tests drive
``main`` with an injected ``Runtime``. Nothing here writes an artifact; only
the delivery types into panes.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Final, NoReturn, Protocol, TextIO

from tools.resume_paused_artifacts import read_checkout_snapshot
from tools.resume_paused_budget import (
    BoundedCapture,
    BoundedSessionStore,
    BoundedTranscriptSource,
    BoundedVersions,
)
from tools.resume_paused_claude import DirectoryTranscriptSource
from tools.resume_paused_codex import DirectorySessionStore
from tools.resume_paused_delivery import deliver_run
from tools.resume_paused_delivery_checks import PlanRecheck
from tools.resume_paused_delivery_model import (
    CALL_BOUND_SECONDS,
    DeliveryPorts,
    UnpinnedProfiles,
)
from tools.resume_paused_evidence import (
    JournalIndex,
    ScreenVerdict,
    journal_path,
    read_session_journal,
)
from tools.resume_paused_guard import CheckoutGuard
from tools.resume_paused_input import (
    ClaudeInputProver,
    CodexInputProver,
    SubprocessRunner,
    UnpinnedCodexVersions,
)
from tools.resume_paused_marker import new_launch_id
from tools.resume_paused_pane_guard import AllPaneIdleGuard, UnpinnedClaudeScreens
from tools.resume_paused_plan_model import PlanRequest
from tools.resume_paused_planner import PlannerPorts, plan_checkout, plan_run
from tools.resume_paused_profiles import (
    SUPPORTED_PROFILES,
    CallerOrigin,
    Host,
    classify_caller,
)
from tools.resume_paused_report import render_run
from tools.resume_paused_review import (
    ExchangeObservationKind,
    ExchangeSnapshot,
    observe_saved_exchange,
)
from tools.resume_paused_reviewer_wait import ReviewerWait, UnprovedAbsence
from tools.resume_paused_takeover import (
    CLAUDE_WAIT_LIMITS,
    MarkedTakeover,
    NoResults,
    TakeoverPorts,
)
from tools.resume_paused_transport import TuiosTransport
from tools.resume_paused_windows import Win32Api, ancestry_names
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ReviewExchangeError
from tools.review_exchange_paths import load_review_configuration

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from tools.resume_paused_artifacts import CheckoutSnapshot
    from tools.resume_paused_delivery_model import (
        AgentLog,
        GuardPort,
        LogEvent,
        ProfileGate,
        ProverFactory,
        Remaining,
        Sleeper,
    )
    from tools.resume_paused_evidence import (
        CommandHistory,
        ObservedCommand,
        PaneObservation,
        ScreenProbe,
    )
    from tools.resume_paused_input import InputProver, PaneRecord
    from tools.resume_paused_models import CanonicalRoot
    from tools.resume_paused_pane_guard import ClaudeScreens
    from tools.resume_paused_plan_model import CheckoutPlan
    from tools.resume_paused_planner import ExchangeObserver
    from tools.resume_paused_profiles import Clock, CommandRunner
    from tools.resume_paused_reviewer_wait import WaitAbsence
    from tools.resume_paused_routing import SavedExchange
    from tools.resume_paused_takeover import ResultSource
    from tools.resume_paused_windows import ProcessRecord

PROGRAM: Final = "resume_paused"
USAGE: Final = "resume_paused [--dry-run] [--clear] [--except NAME[,NAME...]] [--switch-roles NAME[,NAME...]]"
EXIT_SUCCESS: Final = 0
EXIT_FAILURE: Final = 1
EXIT_USAGE: Final = 2
NAMES: Final = "NAME[,NAME...]"
_CODEX_RESOLUTION_NS: Final = 100
_DESCRIPTION: Final = """\
Resume every paused agent session that waits in a TUIOS pane, from the
routing saved in each checkout's pause handoff, with no further question.

HUMAN-ONLY: run it yourself from a terminal, inside or outside TUIOS. Agents
must never run it, not even with --dry-run or --help; a recognized agent
caller is refused with no input and exit status 1. One launch authorizes the
saved resume, its requestor and reviewer roles and the author and role
overrides they need, through a marker bound to each target."""
_EPILOG: Final = """\
Each checkout holding a resume prompt gets one line: PLAN (dry run), DONE,
PENDING (a reviewer waits for takeover or for no-wait evidence), SKIP
(expected: excluded, protected, used, already resuming, guard held), ERROR
(classification failure) or FAIL (execution failure, never retried). The last
line counts the panes no prompt-bearing checkout targets.

Exit status: 0 success, expected skips or pending reviewers; 1 any failure;
2 invalid arguments.

limits=claude-wait-scope is printed with every Claude reviewer activation
outcome and every preview showing a conditional Claude activation. The
absence of waiting work in the reviewer's Claude root is checked only within
these five disclosed limits:
"""


class UsageError(Exception):
    """An invalid command line: exit 2 before any discovery."""


class _Parser(argparse.ArgumentParser):
    """Raise usage errors instead of exiting, so ``main`` returns exit 2."""

    def error(self, message: str) -> NoReturn:
        """Convert an argparse diagnostic into a usage error."""
        raise UsageError(message)


def _names(value: str) -> tuple[str, ...]:
    """Split one ``NAME[,NAME...]`` value; an empty name is a syntax error."""
    names = tuple(part.strip() for part in value.split(","))
    if not all(names):
        message = f"empty name in {value!r}"
        raise argparse.ArgumentTypeError(message)
    return names


def _limits_text() -> str:
    """Return the five disclosed limits of ``limits=claude-wait-scope``, one per line."""
    return "".join(f"  - {code}: {text}\n" for code, text in CLAUDE_WAIT_LIMITS.items())


def build_parser() -> argparse.ArgumentParser:
    """Build the documented grammar; the help names the human-only contract and the five limits."""
    parser = _Parser(
        prog=PROGRAM, usage=USAGE, description=_DESCRIPTION, epilog=_EPILOG + _limits_text(),
        formatter_class=argparse.RawDescriptionHelpFormatter, add_help=False, allow_abbrev=False,
    )
    parser.add_argument("--dry-run", action="store_true", help="type nothing; report every intended command, clear and skip reason")
    parser.add_argument("--clear", action="store_true", help="clear the resumed conversation first; a redundant Claude clear is skipped")
    parser.add_argument(
        "--except", dest="excepts", action="append", type=_names, default=[], metavar=NAMES,
        help="exclude TUIOS sessions, pane labels or checkout folders (exact, case-insensitive); repeatable",
    )
    parser.add_argument(
        "--switch-roles", dest="switch_roles", action="append", type=_names, default=[], metavar=NAMES,
        help="swap the saved requestor and reviewer of a saved requestor pair, by session or checkout folder; repeatable",
    )
    parser.add_argument("-h", "--help", action="store_true", help="show this help and exit")
    return parser


@dataclass(frozen=True)
class Options:
    """The parsed command line."""

    dry_run: bool = False
    clear: bool = False
    excepts: tuple[str, ...] = ()
    switch_roles: tuple[str, ...] = ()
    help: bool = False


def _flatten(groups: Sequence[tuple[str, ...]]) -> tuple[str, ...]:
    """Join the names of every repeated option, in their given order."""
    return tuple(name for group in groups for name in group)


def parse_arguments(argv: Sequence[str]) -> Options:
    """Parse the documented arguments, or raise ``UsageError``."""
    args = build_parser().parse_args(list(argv))
    return Options(args.dry_run, args.clear, _flatten(args.excepts), _flatten(args.switch_roles), args.help)


class _UnreadableHistory:
    """``CommandHistory`` while no agent-log or screen-command form is pinned: every history is unreadable."""

    def commands(self, pane: PaneRecord) -> tuple[ObservedCommand, ...] | None:
        """Report the pane's history unreadable, which keeps duplicate protection uncertain."""
        del pane


class _UnsupportedScreen:
    """``ScreenProbe`` while no Codex screen profile is pinned: no capture proves anything."""

    def probe(self, pane: PaneRecord) -> ScreenVerdict:
        """Report the capture unsupported."""
        del pane
        return ScreenVerdict.UNSUPPORTED


class _UnreadableLog:
    """``AgentLog`` while no Claude logged form is pinned: every agent log is unreadable."""

    def events(self, pane: PaneRecord) -> tuple[LogEvent, ...] | None:
        """Report the pane's log unreadable."""
        del pane


class SystemClock:
    """The real clock and sleeper of a human launch."""

    def now(self) -> datetime:
        """Return the current timezone-aware instant."""
        return datetime.now(UTC)

    def sleep(self, seconds: float) -> None:
        """Wait for the given number of seconds."""
        time.sleep(seconds)


@dataclass(frozen=True)
class SavedExchanges:
    """``ExchangeObserver`` over ``observe_saved_exchange``: read-only, no home preparation."""

    wall_clock: Callable[[], datetime]

    def observe(self, root: CanonicalRoot, exchange: SavedExchange) -> ExchangeSnapshot:
        """Load the checkout's review configuration and observe the saved exchange; failures read as damaged."""
        path = Path(root.display)
        try:
            configuration = ReviewArtifactConfiguration.load(path)
            review = load_review_configuration(path, configuration=configuration)
        except (OSError, ReviewExchangeError) as error:
            return ExchangeSnapshot(ExchangeObservationKind.DAMAGED, exchange.identity().key, f"review configuration unreadable: {error}")
        return observe_saved_exchange(configuration, review, exchange, self.wall_clock)


@dataclass(frozen=True)
class HostAdapters:
    """Host-profile adapters: unpinned in production (plan Q05), declared by tests."""

    history: CommandHistory
    probe: ScreenProbe
    log: AgentLog
    profiles: ProfileGate
    provers: Mapping[Host, ProverFactory]
    absence: WaitAbsence
    screens: ClaudeScreens
    results: ResultSource


@dataclass(frozen=True)
class Runtime:
    """Everything one launch reads from its host: environment, ancestry, processes, time, guard and evidence."""

    environ: Mapping[str, str]
    ancestry: Callable[[], Sequence[str] | None]
    runner_for: Callable[[float], CommandRunner]
    clock: Clock
    sleeper: Sleeper
    guard: GuardPort
    hosts: HostAdapters
    read_snapshot: Callable[[CanonicalRoot], CheckoutSnapshot]
    journal: Callable[[], JournalIndex]
    exchanges: ExchangeObserver
    launch_id: Callable[[], str] = new_launch_id


@dataclass(frozen=True)
class RunPorts:
    """The composed ports of one launch."""

    transport: TuiosTransport
    planner: PlannerPorts
    delivery: DeliveryPorts


def _replan(
    request: PlanRequest, planner: PlannerPorts, journal: Callable[[], JournalIndex], root: CanonicalRoot, observation: PaneObservation,
) -> CheckoutPlan | None:
    """Replan one checkout from a fresh observation and a fresh journal read, with this launch's request and readers."""
    return plan_checkout(request, observation, replace(planner, journal=journal()), root)


def compose(runtime: Runtime, request: PlanRequest, journal: JournalIndex) -> RunPorts:
    """Bind the planner, delivery and takeover of one launch to its runtime."""
    hosts, clock = runtime.hosts, runtime.clock
    transport = TuiosTransport(runtime.runner_for)
    planner = PlannerPorts(runtime.read_snapshot, runtime.exchanges, hosts.history, hosts.probe, journal, runtime.launch_id)
    takeover = MarkedTakeover(TakeoverPorts(
        clock, runtime.sleeper, transport, runtime.read_snapshot, runtime.exchanges,
        ReviewerWait(hosts.history, hosts.probe, hosts.absence), AllPaneIdleGuard(transport, hosts.screens, clock), hosts.results,
    ))
    recheck = PlanRecheck(partial(_replan, request, planner, runtime.journal))
    delivery = DeliveryPorts(
        transport, runtime.guard, clock, runtime.sleeper, hosts.profiles, hosts.log, hosts.provers, hosts.probe, (recheck,), takeover,
    )
    return RunPorts(transport, planner, delivery)


def _read_file(path: str) -> bytes | None:
    """Read one host evidence file completely, or ``None`` when unreadable."""
    try:
        return Path(path).read_bytes()
    except OSError:
        return None


def _os_build() -> int | None:
    """Read the OS build only when a Claude proof reaches profile selection."""
    return Win32Api().os_build()


def unpinned_hosts(environ: Mapping[str, str], runner_for: Callable[[float], CommandRunner]) -> HostAdapters:
    """Compose the host adapters while no host profile is pinned: nothing is read as proof."""
    home = Path(environ.get("USERPROFILE", ""))
    transcripts = DirectoryTranscriptSource(str(home / ".claude" / "projects"), _read_file)
    sessions = DirectorySessionStore(str(home / ".codex" / "sessions"), _read_file)
    capture = TuiosTransport(runner_for).capture

    def claude(remaining: Remaining) -> InputProver:
        """Build one Claude proof's prover over the budget-bounded transcripts."""
        return ClaudeInputProver(BoundedTranscriptSource(transcripts, remaining), SUPPORTED_PROFILES, _os_build)

    def codex(remaining: Remaining) -> InputProver:
        """Build one Codex proof's prover over the budget-bounded session files, capture and versions."""
        return CodexInputProver(
            BoundedSessionStore(sessions, remaining), BoundedCapture(capture, remaining),
            BoundedVersions(UnpinnedCodexVersions(), remaining), _CODEX_RESOLUTION_NS,
        )

    return HostAdapters(
        _UnreadableHistory(), _UnsupportedScreen(), _UnreadableLog(), UnpinnedProfiles(), {Host.CLAUDE: claude, Host.CODEX: codex},
        UnprovedAbsence(), UnpinnedClaudeScreens(), NoResults(),
    )


class ProcessLister(Protocol):
    """The one Windows observation the caller check needs: the process listing."""

    def processes(self) -> tuple[ProcessRecord, ...] | None:
        """Return one process listing, or ``None`` when it fails."""
        ...


def process_ancestry(api_factory: Callable[[], ProcessLister] = Win32Api, pid: Callable[[], int] = os.getpid) -> tuple[str, ...] | None:
    """Return the caller's ancestor image names, or ``None`` when the listing is unavailable."""
    try:
        processes = api_factory().processes()
    except (OSError, AttributeError):
        return None
    return None if processes is None else ancestry_names(processes, pid())


def _bounded_runner(seconds: float) -> CommandRunner:
    """Return an argument-list runner bounded by the seconds granted."""
    return SubprocessRunner(timeout=seconds)


def _read_snapshot(root: CanonicalRoot) -> CheckoutSnapshot:
    """Read one checkout's saved pause without preparing anything."""
    return read_checkout_snapshot(Path(root.display))


def _read_journal(path: Path | None) -> JournalIndex:
    """Read the private session journal index; an unknown path makes it unusable."""
    return JournalIndex(error="session journal path unknown: USERPROFILE is unset") if path is None else read_session_journal(path)


def default_runtime(environ: Mapping[str, str]) -> Runtime:
    """Compose a human launch over TUIOS, the real clock, the native guard and the unpinned host adapters."""
    clock = SystemClock()
    return Runtime(
        environ, process_ancestry, _bounded_runner, clock, clock, CheckoutGuard(), unpinned_hosts(environ, _bounded_runner),
        _read_snapshot, partial(_read_journal, journal_path(environ)), SavedExchanges(clock.now),
    )


def _caller_pane(environ: Mapping[str, str]) -> str | None:
    """Return the caller's own pane id inside TUIOS, ``None`` outside it."""
    return environ.get("TUIOS_PANE_ID", "").strip().lower() or None


def execute(options: Options, runtime: Runtime) -> tuple[list[str], int]:
    """Classify the caller, plan every checkout, deliver unless previewing, and render the result."""
    caller = classify_caller(runtime.environ, runtime.ancestry())
    request = PlanRequest(caller, _caller_pane(runtime.environ), options.dry_run, options.clear, options.excepts, options.switch_roles)
    agent = caller.origin is CallerOrigin.AGENT
    ports = compose(runtime, request, JournalIndex() if agent else runtime.journal())
    observation = None if agent else ports.transport.observe(CALL_BOUND_SECONDS)
    plan = plan_run(request, observation, ports.planner)
    lines, failed = render_run(plan, deliver_run(plan, request, ports.delivery))
    return lines, EXIT_FAILURE if failed else EXIT_SUCCESS


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    runtime: Callable[[], Runtime] | None = None,
) -> int:
    """Run one human launch: exit 0 success, 1 failure, 2 invalid arguments."""
    out, err = stdout or sys.stdout, stderr or sys.stderr
    try:
        options = parse_arguments(sys.argv[1:] if argv is None else argv)
    except UsageError as error:
        err.write(f"usage: {USAGE}\n{PROGRAM}: error: {error}\n")
        return EXIT_USAGE
    if options.help:
        out.write(build_parser().format_help())
        return EXIT_SUCCESS
    lines, code = execute(options, runtime() if runtime is not None else default_runtime(os.environ))
    out.write("".join(f"{line}\n" for line in lines))
    return code


__all__ = [
    "EXIT_FAILURE",
    "EXIT_SUCCESS",
    "EXIT_USAGE",
    "USAGE",
    "HostAdapters",
    "Options",
    "ProcessLister",
    "RunPorts",
    "Runtime",
    "SavedExchanges",
    "SystemClock",
    "UsageError",
    "build_parser",
    "compose",
    "default_runtime",
    "execute",
    "main",
    "parse_arguments",
    "process_ancestry",
    "unpinned_hosts",
]


if __name__ == "__main__":  # pragma: no cover - thin launcher boundary
    raise SystemExit(main())


# eof
