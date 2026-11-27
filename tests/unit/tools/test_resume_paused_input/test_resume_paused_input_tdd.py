"""Live pane discovery and host complete-input proof for marked receivers.

Step 4 of v0.15.0 resume-paused: TUIOS agent records parse strictly into full
pane UUIDs, session strings, checkouts and host evidence; host identification
follows the design's strong-evidence-first rule. The Claude prover requires the
marked command as the latest typed input of the transcript named by the pane's
agent session id, late enough, in the checkout, under a pinned profile. The
Codex prover ties the pane on its first call and re-proves the same session
file with the carried identity afterwards. No process starts and no real host
file is read: commands, captures, transcripts and session files are declared.
Step 6 adds the runner's process bound, which the delivery sets per call to
the remaining budget of a send, and checks that the caller environment is
inherited unchanged.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import replace
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.tools.resume_paused_test_support import (
    CHECKOUT,
    CLAUDE_VERSION,
    CODEX_VERSION,
    OS_BUILD,
    SESSION_ID,
    FakeSessionStore,
    FakeTranscriptSource,
    at,
    codex_session,
    jsonl,
    session_start,
    typed,
)
from tools.resume_paused_codex import CodexPaneProfile
from tools.resume_paused_input import (
    LIST_AGENTS,
    CarriedIdentity,
    ClaudeInputProver,
    CodexInputProver,
    PaneRecord,
    SubprocessRunner,
    TuiosDiscovery,
    UnpinnedCodexVersions,
    pane_host,
    parse_agents,
)
from tools.resume_paused_marker import MARKER_FLAG, Marker
from tools.resume_paused_models import ArtifactError, SessionRole
from tools.resume_paused_profiles import (
    CommandResult,
    Host,
    HostProfile,
    ProfileRegistry,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

LAUNCH = "0123456789abcdef0123456789abcdef"
PANE = "77e5f39c-0536-4cbb-a057-f4a1f5c715b0"
COMMAND = f"/resume-session {MARKER_FLAG} {Marker(LAUNCH, PANE, SessionRole.REQUESTOR, 'a' * 64).render()}"
TRANSCRIPT = f"C:/claude/projects/c--work-checkout/{SESSION_ID}.jsonl"
CLAUDE_REGISTRY = ProfileRegistry((HostProfile(Host.CLAUDE, CLAUDE_VERSION, frozenset({OS_BUILD}), "synthetic"),))
PANE_PROFILE = CodexPaneProfile("\N{SINGLE RIGHT-POINTING ANGLE QUOTATION MARK} ", r"\N{BULLET} Working.*")
CLAUDE_PANE = PaneRecord(PANE, "work", "Claude impl", CHECKOUT, "claude-code", (), SESSION_ID)
CODEX_PANE = PaneRecord(PANE, "work", "Codex rp", CHECKOUT, "", ("codex",), None)
ASK_BOUND = 100


def agent(**changes: Any) -> dict[str, Any]:  # noqa: ANN401
    """Return one ``list-agents --json`` agent record, with changes."""
    data: dict[str, Any] = {
        "window_id": PANE, "session": "work", "name": "Claude impl", "cwd": CHECKOUT,
        "harness_id": "claude-code", "program_status": None, "agent_session_id": SESSION_ID,
    }
    data.update(changes)
    return data


def listing(*agents: dict[str, Any]) -> str:
    """Render a JSON listing."""
    return json.dumps({"agents": list(agents)})


def test_listing_parses_full_identities_and_host_evidence() -> None:
    """Each record keeps its full pane UUID, session string, checkout and host evidence."""
    codex = agent(window_id="2fd92f30-1111-4222-8333-444455556666", name="Codex rp", harness_id="", program_status=[{"app": "codex", "state": "working"}], agent_session_id="")
    claude, codex_record = parse_agents(listing(agent(), codex))
    assert claude == CLAUDE_PANE
    assert (codex_record.apps, codex_record.agent_session_id) == (("codex",), None)


@pytest.mark.parametrize(
    "text",
    [
        "not json",
        '{"agents": [], "agents": []}',
        json.dumps({"agents": {}}),
        listing(agent(window_id="77e5f39c")),
        listing(agent(session=7)),
        listing(agent(program_status="codex")),
    ],
    ids=["not json", "repeated key", "agents not a list", "short pane id", "session not text", "status not a list"],
)
def test_malformed_listing_is_refused(text: str) -> None:
    """A malformed listing is never read as an absent pane."""
    with pytest.raises(ArtifactError, match=r"^discovery-malformed$"):
        parse_agents(text)


@pytest.mark.parametrize(
    ("record", "host"),
    [
        (CLAUDE_PANE, Host.CLAUDE),
        (CODEX_PANE, Host.CODEX),
        (replace(CODEX_PANE, apps=(), name="review", harness="codex"), Host.CODEX),
        (replace(CODEX_PANE, harness="gemini"), None),
        (replace(CODEX_PANE, apps=(), name="codex review"), Host.CODEX),
        (replace(CODEX_PANE, apps=(), name="Codex"), Host.CODEX),
        (replace(CODEX_PANE, apps=(), name="Codex rp", harness="other"), None),
        (replace(CODEX_PANE, apps=(), name="shell"), None),
    ],
    ids=["claude harness", "codex app", "codex harness", "other harness", "codex name", "bare codex name", "name with other harness", "unknown"],
)
def test_host_follows_strong_evidence_first(record: PaneRecord, host: Host | None) -> None:
    """The name fallback applies only without a harness or program-status app."""
    assert pane_host(record) is host


def test_contradictory_host_evidence_is_an_error() -> None:
    """A Claude harness with a Codex app is a classification error."""
    with pytest.raises(ArtifactError, match=r"^host-contradictory$"):
        pane_host(replace(CLAUDE_PANE, apps=("codex",)))


class FakeRunner:
    """Declared command results, recording each argument list."""

    def __init__(self, *results: CommandResult) -> None:
        """Keep the results to return in order."""
        self.results = list(results)
        self.calls: list[tuple[str, ...]] = []

    def run(self, arguments: Sequence[str]) -> CommandResult:
        """Record the call and return the next declared result."""
        self.calls.append(tuple(arguments))
        return self.results.pop(0)


def test_discovery_lists_agents_through_an_argument_list() -> None:
    """Discovery runs the fixed TUIOS listing and parses it."""
    runner = FakeRunner(CommandResult(0, listing(agent())))
    assert TuiosDiscovery(runner).agents() == (CLAUDE_PANE,)
    assert runner.calls == [LIST_AGENTS]


@pytest.mark.parametrize("result", [CommandResult(1, listing(agent())), CommandResult(0, "{")], ids=["failed", "malformed"])
def test_failed_discovery_is_not_absence(result: CommandResult) -> None:
    """A failed or malformed listing reports failure, never an empty listing."""
    assert TuiosDiscovery(FakeRunner(result)).agents() is None


def test_capture_reads_one_pane_by_session_and_full_uuid() -> None:
    """The capture names the session and the full pane UUID and unwraps rows."""
    runner = FakeRunner(CommandResult(0, "one\ntwo\n"), CommandResult(1, ""))
    discovery = TuiosDiscovery(runner)
    assert discovery.capture(CODEX_PANE) == ("one", "two")
    assert discovery.capture(CODEX_PANE) is None
    assert runner.calls[0] == ("tuios", "capture-pane", "-s", "work", "-w", PANE, "--unwrap", "--trim")


def test_subprocess_runner_never_uses_a_shell() -> None:
    """The runner passes an argument list with ``shell=False`` and keeps the output."""
    seen: dict[str, Any] = {}

    def run(arguments: list[str], **options: Any) -> subprocess.CompletedProcess[str]:  # noqa: ANN401
        """Record the call and return a declared completion."""
        seen.update(arguments=arguments, **options)
        return subprocess.CompletedProcess(arguments, 0, stdout="out")

    assert SubprocessRunner(run).run(("tuios", "x")) == CommandResult(0, "out")
    assert (seen["arguments"], seen["shell"], seen["encoding"], seen["timeout"]) == (["tuios", "x"], False, "utf-8", 30)
    assert "env" not in seen


def test_subprocess_runner_takes_a_longer_process_bound_for_the_delivery_ask() -> None:
    """Step 6: the delivery bounds a call by the remaining budget of its send, here above the default."""
    seen: dict[str, Any] = {}

    def run(arguments: list[str], **options: Any) -> subprocess.CompletedProcess[str]:  # noqa: ANN401
        """Record the process bound and return a declared completion."""
        seen.update(options)
        return subprocess.CompletedProcess(arguments, 1, stdout="")

    assert SubprocessRunner(run, timeout=ASK_BOUND).run(("tuios", "ask-agent")) == CommandResult(1, "")
    assert seen["timeout"] == ASK_BOUND


def test_subprocess_runner_reports_a_failed_start() -> None:
    """A command that cannot start is a failed result, not an exception."""

    def run(arguments: list[str], **options: Any) -> subprocess.CompletedProcess[str]:  # noqa: ANN401
        """Fail as a missing executable does."""
        del arguments, options
        raise FileNotFoundError

    assert SubprocessRunner(run).run(("tuios",)) == CommandResult(-1, "")


def claude(files: dict[str, bytes | None] | None = None, *, registry: ProfileRegistry = CLAUDE_REGISTRY, complete: bool = True) -> ClaudeInputProver:
    """Return a Claude prover over declared transcripts."""
    declared: dict[str, bytes | None] = {TRANSCRIPT: jsonl([session_start(), typed("in1", "start", 10, COMMAND)])} if files is None else files
    return ClaudeInputProver(FakeTranscriptSource(declared, complete=complete), registry, lambda: OS_BUILD)


def test_claude_proves_the_marked_latest_typed_input() -> None:
    """The marked command is the transcript's latest typed input, after the pause, in the checkout."""
    evidence = claude().prove(CLAUDE_PANE, COMMAND, at(5), None)
    assert (evidence.proved, evidence.reasons, evidence.account.files) == (True, (), 1)


@pytest.mark.parametrize(
    ("prover", "pane", "not_before", "reason"),
    [
        (claude(), replace(CLAUDE_PANE, agent_session_id=None), at(5), "agent-session-unknown"),
        (claude(complete=False), CLAUDE_PANE, at(5), "enumeration-incomplete"),
        (claude({"C:/claude/projects/x/other.jsonl": b""}), CLAUDE_PANE, at(5), "transcript-not-found"),
        (claude({TRANSCRIPT: b"", TRANSCRIPT.replace("c--work", "d--work"): b""}), CLAUDE_PANE, at(5), "transcript-ambiguous"),
        (claude({TRANSCRIPT: None}), CLAUDE_PANE, at(5), "read-failed"),
        (claude({TRANSCRIPT: b'{"type": "user"}'}), CLAUDE_PANE, at(5), "transcript-incomplete"),
        (claude({TRANSCRIPT: jsonl([session_start(), typed("in1", "start", 10, COMMAND), typed("in2", "in1", 20)])}), CLAUDE_PANE, at(5), "marked-input-not-latest"),
        (claude(), CLAUDE_PANE, at(30), "marked-input-stale"),
        (claude(), replace(CLAUDE_PANE, cwd="C:\\work\\other"), at(5), "checkout-mismatch"),
        (claude(registry=ProfileRegistry(())), CLAUDE_PANE, at(5), "host-profile-unsupported"),
    ],
    ids=["no agent session", "incomplete listing", "no transcript", "two transcripts", "unreadable", "incomplete record", "later input", "stale", "other checkout", "unpinned"],
)
def test_claude_refuses_unproved_input(prover: ClaudeInputProver, pane: PaneRecord, not_before: Any, reason: str) -> None:  # noqa: ANN401
    """Missing, ambiguous, stale, later or unpinned evidence proves nothing."""
    evidence = prover.prove(pane, COMMAND, not_before, None)
    assert (evidence.proved, evidence.reasons) == (False, (reason,))


class FakeVersions:
    """Declared pre-input Codex version evidence."""

    def __init__(self, evidence: tuple[str, CodexPaneProfile] | None = (CODEX_VERSION, PANE_PROFILE)) -> None:
        """Keep the declared evidence."""
        self._evidence = evidence

    def evidence(self, pane: PaneRecord) -> tuple[str, CodexPaneProfile] | None:
        """Return the declared evidence for any pane."""
        del pane
        return self._evidence


class FakeCapture:
    """Declared pane capture."""

    def __init__(self, lines: tuple[str, ...] | None) -> None:
        """Keep the declared lines."""
        self.lines = lines

    def capture(self, pane: PaneRecord) -> tuple[str, ...] | None:
        """Return the declared lines for any pane."""
        del pane
        return self.lines


TIED = (f"{PANE_PROFILE.prompt_prefix}{COMMAND}", "\N{BULLET} Working (3s)")


def codex(
    lines: tuple[str, ...] | None = TIED, *, versions: FakeVersions | None = None, inputs: list[tuple[str, Any]] | None = None,
) -> CodexInputProver:
    """Return a Codex prover over one declared session file and capture."""
    store = FakeSessionStore({"C:/codex/sessions/s.jsonl": codex_session(inputs if inputs is not None else [(COMMAND, at(30))])})
    return CodexInputProver(store, FakeCapture(lines), versions or FakeVersions(), 0)


def test_codex_first_call_ties_the_pane_and_carries_the_session() -> None:
    """The first proof ties the launch id to the pane and returns the session to carry."""
    evidence = codex().prove(CODEX_PANE, COMMAND, at(5), None)
    assert (evidence.proved, evidence.session_id, evidence.account.files) == (True, SESSION_ID, 1)


def test_codex_later_call_reproves_the_carried_session_without_the_prefix() -> None:
    """After scroll-off, the carried identity re-proves the same unique file."""
    evidence = codex(None).prove(CODEX_PANE, COMMAND, at(5), CarriedIdentity(SESSION_ID, LAUNCH))
    assert (evidence.proved, evidence.session_id) == (True, SESSION_ID)


@pytest.mark.parametrize(
    ("prover", "carried", "reason"),
    [
        (codex(versions=FakeVersions(None)), None, "codex-version-unavailable"),
        (codex(None), None, "capture-failed"),
        (codex((f"{PANE_PROFILE.prompt_prefix}{COMMAND}",)), None, "working-signature-missing"),
        (codex(inputs=[("hello", at(30))]), None, "input-not-found"),
        (codex(None), CarriedIdentity("other-session", LAUNCH), "input-identity-changed"),
        (codex(None, inputs=[(COMMAND, at(30)), ("later", at(40))]), CarriedIdentity(SESSION_ID, LAUNCH), "input-not-found"),
    ],
    ids=["no version", "no capture", "no working line", "no input", "other carried session", "new typed input"],
)
def test_codex_refuses_unproved_input(prover: CodexInputProver, carried: CarriedIdentity | None, reason: str) -> None:
    """Missing version, pane tie or input, a changed identity or newer input proves nothing."""
    evidence = prover.prove(CODEX_PANE, COMMAND, at(5), carried)
    assert (evidence.proved, evidence.reasons) == (False, (reason,))


def test_unpinned_codex_versions_prove_no_pane() -> None:
    """Until a Codex release is pinned, no pane has a proved pre-input version."""
    assert UnpinnedCodexVersions().evidence(CODEX_PANE) is None


# eof
