"""Live pane discovery and host complete-input proof for marked resume receivers.

Step 4 of v0.15.0 resume-paused supplies the evidence the receiving validator
needs about the receiving pane, read-only and through injected ports:

- ``TuiosDiscovery`` runs ``tuios list-agents --all-sessions --json`` as an
  argument list and parses each agent record's full ``window_id``, ``session``
  string, ``name``, ``cwd``, harness, program-status apps and agent session id.
  ``pane_host`` identifies Claude by its ``claude-code`` harness and Codex by
  its ``codex`` program-status app, falling back to a ``Codex`` pane name only
  when neither is present; contradictory evidence is an error.
- ``ClaudeInputProver`` reads the transcript named by the pane's agent session
  id and requires the marked command as its latest typed input, recorded at or
  after the pause snapshot in the checkout, under a pinned Claude profile for
  the recorded version and OS build. Notifications are never typed input.
- ``CodexInputProver`` ties the delivery to the pane through the pinned screen
  signatures on the first call, then proves the marked command as the latest
  input of exactly one session file (design Q14=A). Later calls carry the
  session identity and launch id and re-prove the same file (Q15=A).

No input is sent, no conversation content is kept or printed, and an empty
pinned-profile registry (plan Q05=A) leaves every real pane unsupported. The
Codex pre-input version and pane profile come from an injected source; until
Step 1 pins a release, ``UnpinnedCodexVersions`` reports it unavailable.
"""

# ruff: noqa: EM101

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import PureWindowsPath
from typing import TYPE_CHECKING, Final, Protocol

from tools.resume_paused_claude import (
    ParseScope,
    TranscriptRejectedError,
    latest_typed_input,
    parse_transcript,
)
from tools.resume_paused_codex import (
    CodexInputQuery,
    prove_codex_input,
    prove_codex_pane,
)
from tools.resume_paused_marker import marker_in_command
from tools.resume_paused_models import ArtifactError, pane_id
from tools.resume_paused_profiles import (
    CommandResult,
    Host,
    ReadAccount,
    Verdict,
    as_items,
    as_mapping,
    loads_strict,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from datetime import datetime

    from tools.resume_paused_claude import RecordFact, TranscriptSource
    from tools.resume_paused_codex import CodexPaneProfile, SessionStore
    from tools.resume_paused_profiles import CommandRunner, ProfileRegistry

LIST_AGENTS: Final = ("tuios", "list-agents", "--all-sessions", "--json")
_CODEX_NAME: Final = re.compile(r"Codex(?: .+)?", re.IGNORECASE)
_CLAUDE_HARNESS: Final = "claude-code"
_CODEX_APP: Final = "codex"
_COMMAND_TIMEOUT_SECONDS: Final = 30


@dataclass(frozen=True)
class PaneRecord:
    """One live TUIOS agent record: full pane UUID, session string, label, checkout and host evidence."""

    pane_id: str
    session: str
    name: str
    cwd: str
    harness: str
    apps: tuple[str, ...]
    agent_session_id: str | None


@dataclass(frozen=True)
class CarriedIdentity:
    """The non-secret Codex session identity and launch id proved by the first validation."""

    session_id: str
    launch_id: str


@dataclass(frozen=True)
class InputEvidence:
    """Whether the pane's complete-input channel proves the marked command, with bytes read."""

    proved: bool
    session_id: str | None
    reasons: tuple[str, ...]
    account: ReadAccount


class PaneDiscovery(Protocol):
    """Injected live pane discovery."""

    def agents(self) -> tuple[PaneRecord, ...] | None:
        """Return every live agent record, or ``None`` when discovery failed."""
        ...


class PaneCapture(Protocol):
    """Injected read of one pane's captured lines."""

    def capture(self, pane: PaneRecord) -> tuple[str, ...] | None:
        """Return the pane's unwrapped lines, oldest first, or ``None`` on failure."""
        ...


class InputProver(Protocol):
    """Host-specific complete-input proof for one receiving pane."""

    def prove(self, pane: PaneRecord, command: str, not_before: datetime, carried: CarriedIdentity | None) -> InputEvidence:
        """Prove the marked command as the pane's latest complete typed input."""
        ...


class CodexVersions(Protocol):
    """Injected independent pre-input Codex version and pinned screen profile of one pane."""

    def evidence(self, pane: PaneRecord) -> tuple[str, CodexPaneProfile] | None:
        """Return the pane's proved version and pane profile, or ``None`` when unavailable."""
        ...


def _text(value: object) -> str:
    """Return one JSON string value, refusing every other type."""
    if not isinstance(value, str):
        raise ArtifactError("discovery-malformed")
    return value


def _list(value: object) -> list[object]:
    """Return one JSON array, refusing every other type."""
    items = as_items(value)
    if not isinstance(value, list):
        raise ArtifactError("discovery-malformed")
    return items


def _apps(value: object) -> tuple[str, ...]:
    """Return the app names of one record's program-status list."""
    if value is None:
        return ()
    return tuple(_text(as_mapping(item).get("app", "")) for item in _list(value))


def _record(value: object) -> PaneRecord:
    """Parse one agent record of the JSON listing."""
    data = as_mapping(value)
    session_id = _text(data.get("agent_session_id", ""))
    return PaneRecord(
        pane_id(data.get("window_id"), "pane id"),
        _text(data.get("session")),
        _text(data.get("name", "")),
        _text(data.get("cwd", "")),
        _text(data.get("harness_id", "")),
        _apps(data.get("program_status")),
        session_id or None,
    )


def parse_agents(text: str) -> tuple[PaneRecord, ...]:
    """Parse ``list-agents --json`` output strictly; any malformed record fails the listing."""
    try:
        data = loads_strict(text)
    except (ValueError, RecursionError) as error:
        raise ArtifactError("discovery-malformed") from error
    try:
        return tuple(_record(agent) for agent in _list(as_mapping(data).get("agents")))
    except ArtifactError as error:
        raise ArtifactError("discovery-malformed") from error


def pane_host(record: PaneRecord) -> Host | None:
    """Identify the pane's agent host; contradictory evidence is an error."""
    claude = record.harness == _CLAUDE_HARNESS
    codex = _CODEX_APP in record.apps
    if claude and codex:
        raise ArtifactError("host-contradictory")
    if claude:
        return Host.CLAUDE
    if record.harness:
        return Host.CODEX if record.harness == _CODEX_APP else None
    if codex or (not record.apps and _CODEX_NAME.fullmatch(record.name)):
        return Host.CODEX
    return None


class SubprocessRunner:
    """``CommandRunner`` over an argument list, never through a shell.

    Step 6 adds the process bound as a parameter: the bulk delivery builds one
    runner per call, bounded by the remaining budget of the send in progress
    (up to the ask's 100 seconds) instead of the 30-second default.
    """

    def __init__(
        self, run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run, timeout: float = _COMMAND_TIMEOUT_SECONDS,
    ) -> None:
        """Keep the injectable process function and the process bound in seconds."""
        self._run = run
        self._timeout = timeout

    def run(self, arguments: Sequence[str]) -> CommandResult:
        """Run one command and return its exit code and standard output."""
        try:
            completed = self._run(
                list(arguments), shell=False, capture_output=True, text=True, encoding="utf-8",
                errors="strict", timeout=self._timeout, check=False,
            )
        except (OSError, subprocess.SubprocessError, UnicodeError):
            return CommandResult(-1, "")
        return CommandResult(completed.returncode, completed.stdout)


class TuiosDiscovery:
    """``PaneDiscovery`` and ``PaneCapture`` over the TUIOS command line."""

    def __init__(self, runner: CommandRunner) -> None:
        """Keep the injected argument-list runner."""
        self._runner = runner

    def agents(self) -> tuple[PaneRecord, ...] | None:
        """List every live agent record across sessions, or ``None`` on any failure."""
        result = self._runner.run(LIST_AGENTS)
        if result.exit_code != 0:
            return None
        try:
            return parse_agents(result.stdout)
        except ArtifactError:
            return None

    def capture(self, pane: PaneRecord) -> tuple[str, ...] | None:
        """Capture the pane's unwrapped, trimmed lines by its session and full UUID."""
        result = self._runner.run(("tuios", "capture-pane", "-s", pane.session, "-w", pane.pane_id, "--unwrap", "--trim"))
        return tuple(result.stdout.splitlines()) if result.exit_code == 0 else None


def _unproved(reason: str, account: ReadAccount | None = None) -> InputEvidence:
    """Return one failed proof with its reason."""
    return InputEvidence(proved=False, session_id=None, reasons=(reason,), account=account or ReadAccount())


def _folded(path: str) -> str:
    """Compare Windows paths by the filesystem's case and separator rules."""
    return os.path.normcase(os.path.normpath(path))


class ClaudeInputProver:
    """Prove the marked command in the transcript of the pane's agent session."""

    def __init__(self, source: TranscriptSource, registry: ProfileRegistry, os_build: Callable[[], int | None]) -> None:
        """Keep the transcript source, the pinned registry and the OS build reader."""
        self._source = source
        self._registry = registry
        self._os_build = os_build

    def _transcript(self, session_id: str) -> str | InputEvidence:
        """Return the path of the one transcript named by the session id."""
        listing = self._source.list_files()
        if listing is None:
            return _unproved("enumeration-incomplete")
        paths = [file.path for file in listing if PureWindowsPath(file.path).stem.lower() == session_id.lower()]
        if len(paths) != 1:
            return _unproved("transcript-ambiguous" if paths else "transcript-not-found")
        return paths[0]

    def prove(self, pane: PaneRecord, command: str, not_before: datetime, carried: CarriedIdentity | None) -> InputEvidence:
        """Require the marked command as the latest typed input, late enough, in the checkout."""
        del carried
        read = self._latest(pane, command)
        if isinstance(read, InputEvidence):
            return read
        fact, account = read
        reason = self._refusal(fact, pane, not_before)
        if reason is not None:
            return _unproved(reason, account)
        return InputEvidence(proved=True, session_id=None, reasons=(), account=account)

    def _latest(self, pane: PaneRecord, command: str) -> tuple[RecordFact | None, ReadAccount] | InputEvidence:
        """Read the pane's transcript and return its latest typed input, if any."""
        if pane.agent_session_id is None:
            return _unproved("agent-session-unknown")
        path = self._transcript(pane.agent_session_id)
        if isinstance(path, InputEvidence):
            return path
        data = self._source.read(path)
        if data is None:
            return _unproved("read-failed")
        account = ReadAccount().plus(len(data))
        try:
            facts = parse_transcript(data, ParseScope(marked_input=command))
        except TranscriptRejectedError as error:
            return _unproved(str(error), account)
        index = latest_typed_input(facts)
        return (None if index is None else facts[index]), account

    def _refusal(self, fact: RecordFact | None, pane: PaneRecord, not_before: datetime) -> str | None:
        """Return why the latest typed input does not prove this marked resume, if it does not."""
        if fact is None or not fact.marked:
            return "marked-input-not-latest"
        if fact.timestamp is None or fact.timestamp < not_before:
            return "marked-input-stale"
        if fact.cwd is None or _folded(fact.cwd) != _folded(pane.cwd):
            return "checkout-mismatch"
        selected = self._registry.select(Host.CLAUDE, fact.version or "", self._os_build() or 0)
        return None if selected.verdict is Verdict.SUPPORTED else "host-profile-unsupported"


class UnpinnedCodexVersions:
    """``CodexVersions`` while no Codex release is pinned: no pane version is proved."""

    def evidence(self, pane: PaneRecord) -> tuple[str, CodexPaneProfile] | None:
        """Report the independent pre-input version unavailable."""
        del pane


class CodexInputProver:
    """Prove the marked command in exactly one Codex session file, tied to its pane."""

    def __init__(self, store: SessionStore, capture: PaneCapture, versions: CodexVersions, resolution_ns: int) -> None:
        """Keep the session store, the pane capture, the version source and the timestamp resolution."""
        self._store = store
        self._capture = capture
        self._versions = versions
        self._resolution_ns = resolution_ns

    def prove(self, pane: PaneRecord, command: str, not_before: datetime, carried: CarriedIdentity | None) -> InputEvidence:
        """Tie the pane on the first call, then prove or re-prove the unique session file."""
        evidence = self._versions.evidence(pane)
        if evidence is None:
            return _unproved("codex-version-unavailable")
        version, profile = evidence
        launch_id = marker_in_command(command).launch_id
        if carried is None:
            lines = self._capture.capture(pane)
            if lines is None:
                return _unproved("capture-failed")
            tied = prove_codex_pane(lines, launch_id, profile)
            if tied:
                return _unproved(tied[0].code)
        query = CodexInputQuery(command, pane.cwd, not_before, self._resolution_ns, version, launch_id)
        decision = prove_codex_input(self._store, query)
        proof = decision.proof
        if decision.verdict is not Verdict.SUPPORTED or proof is None:
            return InputEvidence(proved=False, session_id=None, reasons=tuple(reason.code for reason in decision.reasons), account=decision.account)
        if carried is not None and (proof.session_id, proof.launch_id) != (carried.session_id, carried.launch_id):
            return _unproved("input-identity-changed", decision.account)
        return InputEvidence(proved=True, session_id=proof.session_id, reasons=(), account=decision.account)


__all__ = [
    "LIST_AGENTS",
    "CarriedIdentity",
    "ClaudeInputProver",
    "CodexInputProver",
    "CodexVersions",
    "InputEvidence",
    "InputProver",
    "PaneCapture",
    "PaneDiscovery",
    "PaneRecord",
    "SubprocessRunner",
    "TuiosDiscovery",
    "UnpinnedCodexVersions",
    "pane_host",
    "parse_agents",
]


# eof
