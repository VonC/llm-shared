"""Unit tests of the human-only resume_paused command line (Step 8 of v0.15.0 resume-paused).

The parser accepts only the documented flags; the help states the human-only
contract and defines ``limits=claude-wait-scope``; the caller is classified
before any discovery; the composition binds the real planner, delivery and
takeover to an injected ``Runtime``; ``main`` prints the rendered lines with
exit 0, 1 or 2; the launcher is checked statically. A fake ``tuios`` runner
answers ``list-agents`` from the declared planner world; no process, pane or
real wait is involved. The line rendering itself has its own leaf,
``test_resume_paused_report``, which shares the declared plans below.
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from itertools import count
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.resume_paused_receiver_test_support import scenario_routing
from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    TITLE,
    checkout,
)
from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    FakeClock,
    FakeGuard,
)
from tests.unit.tools.test_resume_paused_planner.planner_world import (
    API,
    World,
    binding,
    live,
    snapshot,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    SESSION,
)
from tools import resume_paused as cli
from tools.resume_paused_artifacts import PromptState
from tools.resume_paused_delivery_checks import PlanRecheck
from tools.resume_paused_delivery_model import (
    CLAUDE_WAIT_SCOPE,
    Phase,
    Refusal,
    SendStep,
    UnpinnedProfiles,
)
from tools.resume_paused_evidence import JournalIndex, PaneObservation, ScreenVerdict
from tools.resume_paused_input import (
    LIST_AGENTS,
    ClaudeInputProver,
    CodexInputProver,
    PaneRecord,
    SubprocessRunner,
)
from tools.resume_paused_marker import Marker
from tools.resume_paused_models import CanonicalRoot, SessionRole
from tools.resume_paused_pane_guard import UnpinnedClaudeScreens
from tools.resume_paused_plan_model import (
    ActionKind,
    CheckoutOutcome,
    CheckoutPlan,
    PlannedAction,
)
from tools.resume_paused_planner import marked_command
from tools.resume_paused_profiles import DISCLOSED_LIMITS, CommandResult, Host
from tools.resume_paused_review import ExchangeObservationKind
from tools.resume_paused_reviewer_wait import UnprovedAbsence
from tools.resume_paused_routing import SavedExchange
from tools.resume_paused_takeover import CLAUDE_WAIT_LIMITS, MarkedTakeover, NoResults
from tools.resume_paused_windows import ProcessRecord

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.resume_paused_delivery_model import LogEvent
    from tools.resume_paused_evidence import PaneActivity

LAUNCHER = Path(__file__).resolve().parents[4] / "bin" / "resume_paused.bat"
ROOT = CanonicalRoot.from_path(API)
PAUSED = "2026-11-17T17:37:18+01:00"
LAUNCHES = (f"{1:032x}", f"{2:032x}")
HUMAN_ENV = {"USERPROFILE": "C:\\Users\\person"}
OS_BUILD = 26200


def agent_json(pane: PaneRecord, activity: PaneActivity | None) -> dict[str, object]:
    """Render one TUIOS ``list-agents --json`` record of a declared pane and its activity."""
    record: dict[str, object] = {
        "window_id": pane.pane_id, "session": pane.session, "name": pane.name, "cwd": pane.cwd, "harness_id": pane.harness,
        "program_status": [{"app": app} for app in pane.apps], "agent_session_id": pane.agent_session_id or "",
    }
    if activity is not None:
        record |= {
            "state": activity.state, "blocked_by": activity.blocked_by, "draft_held": activity.draft_held,
            "message": activity.question, "ready": activity.ready,
        }
    return record


def listing_json(panes: Sequence[PaneRecord], activity: dict[str, PaneActivity]) -> str:
    """Render the whole ``list-agents --json`` answer."""
    return json.dumps({"agents": [agent_json(pane, activity.get(pane.pane_id)) for pane in panes]})


@dataclass
class ListingRunner:
    """Fake ``tuios``: answers ``list-agents`` from the declared world and fails every other command, recording all."""

    world: World
    calls: list[tuple[str, ...]] = field(default_factory=list[tuple[str, ...]])

    def bounded(self, seconds: float) -> ListingRunner:
        """Return this runner whatever bound is granted."""
        del seconds
        return self

    def run(self, arguments: Sequence[str]) -> CommandResult:
        """Answer the listing; refuse anything else."""
        self.calls.append(tuple(arguments))
        if tuple(arguments) != LIST_AGENTS:
            return CommandResult(1, "")
        return CommandResult(0, listing_json(self.world.panes, self.world.activity))


class _NoLog:
    """Agent log that is never readable."""

    def events(self, pane: PaneRecord) -> tuple[LogEvent, ...] | None:
        """Read nothing."""
        del pane


def _no_journal() -> JournalIndex:
    """Fail when an agent caller's launch would read the journal."""
    message = "the journal must not be read"
    raise AssertionError(message)


def runtime(world: World, runner: ListingRunner, environ: dict[str, str] | None = None, ancestry: tuple[str, ...] = ("cmd.exe",)) -> cli.Runtime:
    """Compose a runtime over the declared world: unpinned delivery profiles, deterministic launch ids."""
    ids = (f"{number:032x}" for number in count(1))
    hosts = cli.HostAdapters(
        world.history, world.probe, _NoLog(), UnpinnedProfiles(), {}, UnprovedAbsence(), UnpinnedClaudeScreens(), NoResults(),
    )
    clock = FakeClock()
    return cli.Runtime(
        HUMAN_ENV if environ is None else environ, lambda: ancestry, runner.bounded, clock, clock, FakeGuard(), hosts,
        world.read, lambda: world.journal, world.exchanges, lambda: next(ids),
    )


def launch(argv: list[str], *, environ: dict[str, str] | None = None) -> tuple[int, str, str, ListingRunner]:
    """Run ``main`` over the default declared world; return the exit code, both streams and the runner."""
    world = World()
    runner = ListingRunner(world)
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(argv, stdout=out, stderr=err, runtime=lambda: runtime(world, runner, environ))
    return code, out.getvalue(), err.getvalue(), runner


def no_runtime() -> cli.Runtime:
    """Fail when a launch that must stop first would compose its runtime."""
    message = "no runtime may be built"
    raise AssertionError(message)


def command(host: Host, kind: ActionKind, pane: str, role: SessionRole, launch_id: str) -> str:
    """Return the marked command the planner renders for the default world's pause."""
    return marked_command(host, kind, Marker(launch_id, pane, role, binding(snapshot(), pane, role)))


def planned(kind: ActionKind = ActionKind.RESUME, host: Host = Host.CLAUDE, **changes: object) -> PlannedAction:
    """Declare one planned action on the requestor pane, or the reviewer pane for a reviewer kind."""
    reviewer = kind is not ActionKind.RESUME
    pane, role = (REVIEWER_PANE, SessionRole.REVIEWER) if reviewer else (REQUESTOR_PANE, SessionRole.REQUESTOR)
    action = PlannedAction(kind, role, host, SESSION, pane, f"{role.value} | pane", f"/cmd {role.value}", conditional=reviewer)
    return replace(action, **changes)  # type: ignore[arg-type]


def plan(*actions: PlannedAction, **changes: object) -> CheckoutPlan:
    """Declare one planned checkout of the default pause."""
    base = CheckoutPlan(ROOT, PromptState.UNUSED, CheckoutOutcome.PLANNED, title=TITLE, author="claude", paused_at=PAUSED, actions=actions)
    return replace(base, **changes)  # type: ignore[arg-type]


VALIDATED = "(saved routing, validated)"
REQUESTOR = f"requestor claude {SESSION}/requestor | pane {REQUESTOR_PANE[:8]} {VALIDATED}"
REVIEWER = f"reviewer claude {SESSION}/reviewer | pane {REVIEWER_PANE[:8]} {VALIDATED}"
CODEX_REVIEWER = f"reviewer codex {SESSION}/reviewer | pane {REVIEWER_PANE[:8]} {VALIDATED}"
HEAD = f"'{TITLE}' paused by claude at 2026-11-17 17:37, prompt unused"


@pytest.mark.parametrize(
    "line",
    [
        'if not defined LLM_SHARED_DIR set "LLM_SHARED_DIR=%~dp0.."',
        'dir /b /ad /o-d "%PYTHON_BASE%\\python_3*llm-shared*"',
        'set "PYTHON_EXE=%PYTHON_BASE%\\%LATEST_PYTHON%\\Scripts\\python.exe"',
        "exit /b %ERRORLEVEL%",
        "setlocal DisableDelayedExpansion",
        "HUMAN-ONLY",
        "agents must\nREM never run it, not even with --dry-run or --help",
    ],
)
def test_launcher_self_locates_selects_the_shared_python_and_states_the_human_only_contract(line: str) -> None:
    """Checked statically, never executed: agents never run the bulk launcher, help and preview included."""
    assert line in LAUNCHER.read_text(encoding="utf-8")


def test_launcher_forwards_every_argument_only_to_the_cli() -> None:
    """The one Python invocation runs the CLI module with every argument; nothing else receives them."""
    source = LAUNCHER.read_text(encoding="utf-8")
    invocations = [line for line in source.splitlines() if line.startswith('"%PYTHON_EXE%"')]
    assert invocations == ['"%PYTHON_EXE%" "%LLM_SHARED_DIR%\\tools\\resume_paused.py" %*']
    assert source.count("%*") == 1
    assert "EnableDelayedExpansion" not in source


def test_parser_accepts_every_documented_flag_and_joins_repeated_name_lists() -> None:
    """Repeated ``--except`` and ``--switch-roles`` values join in order; comma lists are split and trimmed."""
    options = cli.parse_arguments(["--dry-run", "--clear", "--except", "api, web", "--except", "docs", "--switch-roles", "pair"])
    assert options == cli.Options(dry_run=True, clear=True, excepts=("api", "web", "docs"), switch_roles=("pair",))
    assert cli.parse_arguments([]) == cli.Options()


@pytest.mark.parametrize(
    "argv",
    [["--timeout", "5"], ["--except", ""], ["--except", "a,,b"], ["api"], ["--dry"], ["--except"], ["--switch-roles", " "]],
)
def test_syntax_errors_exit_2_before_any_runtime_is_built(argv: list[str]) -> None:
    """Undocumented flags, abbreviations, positionals and empty names are syntax errors with no discovery."""
    out, err = io.StringIO(), io.StringIO()
    assert cli.main(argv, stdout=out, stderr=err, runtime=no_runtime) == cli.EXIT_USAGE
    assert out.getvalue() == ""
    assert err.getvalue().startswith(f"usage: {cli.USAGE}\nresume_paused: error: ")


def help_text() -> str:
    """Print the help without composing any runtime and return it with its whitespace folded."""
    out = io.StringIO()
    assert cli.main(["--help"], stdout=out, runtime=no_runtime) == cli.EXIT_SUCCESS
    return " ".join(out.getvalue().split())


@pytest.mark.parametrize(
    "phrase",
    [
        f"usage: {cli.USAGE}",
        "HUMAN-ONLY",
        "Agents must never run it, not even with --dry-run or --help",
        "a recognized agent caller is refused with no input and exit status 1",
        "0 success, expected skips or pending reviewers; 1 any failure; 2 invalid arguments",
        "--dry-run",
        "--clear",
        "--except NAME[,NAME...]",
        "--switch-roles NAME[,NAME...]",
        CLAUDE_WAIT_SCOPE,
    ],
)
def test_help_states_the_human_only_contract_flags_and_exit_codes(phrase: str) -> None:
    """Help names the agent prohibition, every documented flag, the exit codes and the limits code."""
    assert phrase in help_text()


@pytest.mark.parametrize(("code", "meaning"), list(CLAUDE_WAIT_LIMITS.items()))
def test_help_defines_each_of_the_five_wait_scope_limits(code: str, meaning: str) -> None:
    """Every disclosed limit is defined; the third carries the since-boot clock scope (Q21=A)."""
    assert tuple(CLAUDE_WAIT_LIMITS) == DISCLOSED_LIMITS
    assert f"- {code}: {' '.join(meaning.split())}" in help_text()
    assert "since the last OS boot" in CLAUDE_WAIT_LIMITS["undetectable-backward-clock-change"]


@pytest.mark.parametrize(
    ("environ", "ancestry", "signals"),
    [
        ({"CLAUDECODE": "1"}, ("cmd.exe",), "agent-environment-marker"),
        ({}, ("powershell.exe", "codex.exe"), "agent-ancestor"),
    ],
)
@pytest.mark.parametrize("argv", [[], ["--dry-run"]])
def test_a_recognized_agent_caller_is_refused_before_discovery(
    argv: list[str], environ: dict[str, str], ancestry: tuple[str, ...], signals: str,
) -> None:
    """Normal and dry runs from an agent read no listing and no journal and exit 1 (design Q08)."""
    world = World()
    runner = ListingRunner(world)
    agent = runtime(world, runner, environ, ancestry)
    out = io.StringIO()
    code = cli.main(argv, stdout=out, runtime=lambda: replace(agent, journal=_no_journal))
    assert code == cli.EXIT_FAILURE
    assert out.getvalue() == f"REFUSED run: agent-caller: {signals} (human-only command: agents must not run it); no input sent\n"
    assert runner.calls == []


def test_dry_run_reports_the_exact_marked_commands_and_types_nothing() -> None:
    """A preview lists the requestor command and the conditional reviewer command, then the omitted count."""
    code, out, _, runner = launch(["--dry-run"])
    resume = command(Host.CLAUDE, ActionKind.RESUME, REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCHES[0])
    reviewer = command(Host.CODEX, ActionKind.REVIEWER, REVIEWER_PANE, SessionRole.REVIEWER, LAUNCHES[1])
    assert code == cli.EXIT_SUCCESS
    assert out.splitlines() == [
        f"PLAN api: {HEAD}; {REQUESTOR}: {resume}; {CODEX_REVIEWER}: after takeover, {reviewer}",
        "omitted 0 pane(s) without a prompt-bearing target; dry run, nothing typed",
    ]
    assert runner.calls == [LIST_AGENTS]


def test_a_run_without_a_pinned_profile_fails_closed_before_any_input() -> None:
    """The unpinned profile gate refuses the resume after its fresh checks; nothing is captured or typed."""
    code, out, _, runner = launch(["--clear"])
    assert code == cli.EXIT_FAILURE
    assert out.splitlines()[0] == (
        f"FAIL api: {HEAD}; {REQUESTOR}: failed: host-profile-unsupported; "
        f"{CODEX_REVIEWER}: skipped: requestor-not-accepted"
    )
    assert set(runner.calls) == {LIST_AGENTS}


def test_the_caller_pane_inside_tuios_is_protected() -> None:
    """``TUIOS_PANE_ID`` names the caller's pane, whatever its case; the resume target is skipped, exit 0."""
    code, out, _, _ = launch(["--dry-run"], environ={**HUMAN_ENV, "TUIOS_PANE_ID": f" {REQUESTOR_PANE.upper()} "})
    assert code == cli.EXIT_SUCCESS
    assert out.splitlines()[0] == f"SKIP api: {HEAD}; skip caller-pane: {REQUESTOR_PANE}; {REQUESTOR}: skip caller-pane"


def test_an_unmatched_exclusion_refuses_the_whole_run() -> None:
    """Name validation failures print one refusal and exit 1 with no checkout line."""
    code, out, _, _ = launch(["--dry-run", "--except", "nowhere,api"])
    assert (code, out) == (cli.EXIT_FAILURE, "REFUSED run: except-unmatched: nowhere; no input sent\n")


def test_composition_binds_the_request_recheck_and_the_marked_takeover() -> None:
    """The delivery runs one ``PlanRecheck`` of this request before each send; its replan reads the fresh listing."""
    world = World()
    ports = cli.compose(runtime(world, ListingRunner(world)), cli.PlanRequest(cli.classify_caller({}, ())), JournalIndex())
    (recheck,) = ports.delivery.checks
    assert isinstance(recheck, PlanRecheck)
    assert isinstance(ports.delivery.takeover, MarkedTakeover)
    step = SendStep(Phase.RESUME, ROOT, planned(), PaneObservation((), {}), live(REQUESTOR_PANE))
    assert recheck.check(step) == Refusal("checkout-unplanned")


def test_every_recheck_reads_the_session_journal_again() -> None:
    """The journal read for planning is never reused at a send: each pre-send replan reads it afresh (code review round 1)."""
    world = World()
    reads: list[int] = []

    def journal() -> JournalIndex:
        """Count each read of the declared journal."""
        reads.append(len(reads))
        return world.journal

    composed = replace(runtime(world, ListingRunner(world)), journal=journal)
    (recheck,) = cli.compose(composed, cli.PlanRequest(cli.classify_caller({}, ())), JournalIndex()).delivery.checks
    step = SendStep(Phase.RESUME, ROOT, planned(), PaneObservation((), {}), live(REQUESTOR_PANE))
    recheck.check(step)
    recheck.check(step)
    assert reads == [0, 1]


def test_unpinned_host_adapters_prove_nothing() -> None:
    """While no profile is pinned: unreadable history and log, unsupported screens and profiles, real prover factories."""
    hosts = cli.unpinned_hosts({"USERPROFILE": "C:\\Users\\person"}, lambda seconds: SubprocessRunner(timeout=seconds))
    pane = live(REQUESTOR_PANE)
    assert (hosts.history.commands(pane), hosts.log.events(pane), hosts.profiles.profile(pane)) == (None, None, None)
    assert hosts.probe.probe(pane) is ScreenVerdict.UNSUPPORTED
    assert isinstance(hosts.provers[Host.CLAUDE](lambda: 1.0), ClaudeInputProver)
    assert isinstance(hosts.provers[Host.CODEX](lambda: 1.0), CodexInputProver)
    assert isinstance(hosts.absence, UnprovedAbsence)


def test_default_runtime_reads_the_journal_and_saved_pauses_read_only(tmp_path: Path) -> None:
    """The default composition reads a missing journal as empty, an unknown profile as unusable, a bare checkout as prompt-less."""
    root = checkout(tmp_path)
    composed = cli.default_runtime({"USERPROFILE": str(tmp_path)})
    assert composed.journal() == JournalIndex()
    assert composed.read_snapshot(CanonicalRoot.from_path(root)).state is PromptState.NO_PROMPT
    assert isinstance(composed.runner_for(2.0), SubprocessRunner)
    assert cli.default_runtime({}).journal().error == "session journal path unknown: USERPROFILE is unset"


def test_host_evidence_files_are_read_whole_or_reported_unreadable(tmp_path: Path) -> None:
    """The unpinned adapters' file reader returns exact bytes, and ``None`` for a missing file."""
    evidence = tmp_path / "session.jsonl"
    evidence.write_bytes(b'{"type": "user"}\n')
    assert cli._read_file(str(evidence)) == b'{"type": "user"}\n'  # noqa: SLF001 - the reader is a private composition seam
    assert cli._read_file(str(tmp_path / "missing.jsonl")) is None  # noqa: SLF001 - the reader is a private composition seam


def test_saved_exchanges_observes_read_only_and_reports_an_unloadable_checkout_damaged(tmp_path: Path) -> None:
    """A loadable checkout is observed through the real observer; an unloadable one is damaged."""
    root = checkout(tmp_path)
    exchange = scenario_routing(root).exchange
    assert isinstance(exchange, SavedExchange)
    assert exchange.umbrella is not None
    (root / "docs").mkdir()
    for document in (exchange.document, exchange.umbrella):
        (root / document).write_text("# Declared\n", encoding="utf-8")
    observer = cli.SavedExchanges(lambda: datetime(2026, 11, 23, tzinfo=UTC))
    assert observer.observe(CanonicalRoot.from_path(root), exchange).kind is not ExchangeObservationKind.DAMAGED
    missing = observer.observe(CanonicalRoot.from_path(tmp_path / "missing"), exchange)
    assert missing.kind is ExchangeObservationKind.DAMAGED
    assert missing.diagnostic.startswith("review configuration unreadable: ")


@dataclass
class _Lister:
    """Declared process listing."""

    listing: tuple[ProcessRecord, ...] | None

    def processes(self) -> tuple[ProcessRecord, ...] | None:
        """Return the declared listing."""
        return self.listing


def _unavailable() -> _Lister:
    """Model a Windows binding that cannot load."""
    message = "no kernel32"
    raise OSError(message)


def test_process_ancestry_reads_the_caller_chain_or_reports_it_unavailable() -> None:
    """The ancestry is nearest first; a failed listing or binding reads as unavailable, never as human proof."""
    chain = (ProcessRecord(30, 20, "python.exe"), ProcessRecord(20, 10, "cmd.exe"), ProcessRecord(10, 1, "claude.exe"))
    assert cli.process_ancestry(lambda: _Lister(chain), lambda: 30) == ("cmd.exe", "claude.exe")
    assert cli.process_ancestry(lambda: _Lister(None), lambda: 30) is None
    assert cli.process_ancestry(_unavailable, lambda: 30) is None


def test_system_clock_and_lazy_os_build(monkeypatch: pytest.MonkeyPatch) -> None:
    """The real clock is timezone-aware and sleeps through ``time.sleep``; the OS build is read only on demand."""
    slept: list[float] = []
    monkeypatch.setattr(cli.time, "sleep", slept.append)
    clock = cli.SystemClock()
    clock.sleep(0.5)
    assert slept == [0.5]
    assert clock.now().tzinfo is not None

    class _Build:
        def os_build(self) -> int:
            """Return a declared build."""
            return OS_BUILD

    monkeypatch.setattr(cli, "Win32Api", _Build)
    assert cli._os_build() == OS_BUILD  # noqa: SLF001 - the lazy reader is a private composition seam


# eof
