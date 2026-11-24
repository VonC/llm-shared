"""Duplicate-resume evidence and safe input eligibility for resume-paused.

Step 5 of v0.15.0 resume-paused classifies, read-only, whether a checkout is
already being resumed and whether one pane may receive input:

- ``observe_panes`` runs ``tuios list-agents --all-sessions --json`` once, as
  an argument list, and parses from the same output the strict pane records
  and each pane's activity: TUIOS state, ``blocked_by``, ``draft_held``,
  ``ready`` and the waiting question. Failed or malformed discovery is never
  absence.
- ``input_eligibility`` protects blocked, question, draft, busy and unknown
  panes, and an idle or done pane whose readiness is negative or absent. Only
  a supported fresh Codex idle, empty-input capture overrides a stale
  ``working`` status (requirement Q03), never a blocked one or a draft.
- ``classify_command`` recognizes ``resume-session`` and ``review-resume``
  after a native prefix (``/``, ``$`` or ``$llm-shared:``), whatever trailing
  context follows, and the role a ``review-resume`` selects: its marker, or a
  role word, ``--role <role>`` or ``as <role>`` heading its arguments. The
  other role offered as an alternative, whatever the punctuation (another
  selection form, a disjunction such as ``reviewer (or requestor)``, or a
  bare list after the head), makes the role uncertain; any other mention of
  it is explanatory text, and a role phrase inside prose selects nothing.
  ``counted`` applies Q14/Q26:
  ``resume-session`` always counts, a reviewer-only ``review-resume`` counts
  only for a saved reviewer pause, and an unknown role is uncertain.
- ``read_session_journal`` reads the private session journal strictly, as an
  index of resume entries by canonical checkout, never as prompt authority.
- ``classify_duplicates`` gathers checkout-wide evidence from every pane of
  the checkout, excluded and caller panes included: a resume journal entry or
  a counted command strictly later than the pause, and a pane blocked on the
  author-override question. Proven older evidence and a proved reviewer-only
  command for another pause are ignored; an equal timestamp, an unreadable
  history, an unattributed command that could count, an uncertain role or an
  unreadable journal is uncertain, never absence.

Fix (code review round 1): role selection ignores role words in explanatory
text; an undated reviewer-only command never counts for a non-reviewer pause;
only a strictly later timestamp proves a resume, an equal one stays
uncertain; TUIOS readiness gates an idle or done pane.

Fix (code review round 2): a role is selected only at the head of the
arguments, never by an ``as <role>`` phrase inside explanatory prose, and an
alternative in the same clause or a second selection form keeps it uncertain,
so a reviewer-only reading never hides a possible duplicate resume. A command
name followed directly by punctuation is still that command.

Fix (code review round 3): punctuation no longer decides whether the other
role is an alternative or an explanation; disjunctions, bare lists and second
selection forms do, so ``reviewer (or requestor)`` stays uncertain and ``as
reviewer while the requestor is busy`` keeps its reviewer selection.

Nothing here sends input, writes a file or reads a conversation; the command
history and the screen probe are injected.
"""

# ruff: noqa: EM102, TRY003

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Final, Protocol

from tools.resume_paused_input import LIST_AGENTS, parse_agents
from tools.resume_paused_marker import MARKER_FLAG, marker_in_command
from tools.resume_paused_models import (
    ArtifactError,
    CanonicalRoot,
    SessionRole,
    pane_id,
)
from tools.resume_paused_profiles import Host, as_items, as_mapping, loads_strict

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_profiles import CommandRunner

OVERRIDE_QUESTION: Final = "override that and resume it here"
JOURNAL_NAME: Final = "sessions.journal.md"
_MALFORMED: Final = "discovery-malformed"
_IDLE_STATES: Final = frozenset({"idle", "done"})
_BLOCKED_STATES: Final = frozenset({"needs_input", "blocked"})
_WORKING: Final = "working"
_COMMAND_RE: Final = re.compile(
    r"\s*(?:/|\$llm-shared:|\$)?(?P<name>resume-session|review-resume)(?![\w-])(?P<rest>.*)", re.IGNORECASE | re.DOTALL,
)
_SELECTION_PREFIX: Final = r"(?:--role(?:=|\s+)|as\s+(?:the\s+|a\s+)?)"
_HEAD_SELECTION_RE: Final = re.compile(rf"[ \t]*{_SELECTION_PREFIX}?(requestor|reviewer)(?![\w-])", re.IGNORECASE)
_SELECTION_FORM_RE: Final = re.compile(rf"(?<![\w-]){_SELECTION_PREFIX}(requestor|reviewer)(?![\w-])", re.IGNORECASE)
_OTHER_ROLE: Final = {"requestor": "reviewer", "reviewer": "requestor"}
_OPENERS: Final = r"[\s(\[{\"'`]*"
_CLOSERS: Final = r"[\s)\]}\"'`]*"
_DISJUNCTION: Final = r"(?:\bor\b|\bnor\b|/|\|)"


def _alternative_patterns(other: str) -> tuple[re.Pattern[str], re.Pattern[str]]:
    """Return the patterns that make ``other`` an alternative to a head selection.

    The first matches the start of the text after the head: ``other`` listed
    bare, with only punctuation, brackets, quotes or ``and`` between. The
    second finds ``other`` joined by a disjunction on either side, through
    brackets, quotes and an article, anywhere.
    """
    listed = re.compile(rf"[\s,;:(\[{{\"'`]*(?:(?:and|&){_OPENERS})?{other}(?![\w-])", re.IGNORECASE)
    disjoined = re.compile(
        rf"{_DISJUNCTION}{_OPENERS}(?:as\s+)?(?:the\s+|a\s+)?{other}(?![\w-])|(?<![\w-]){other}{_CLOSERS}{_DISJUNCTION}",
        re.IGNORECASE,
    )
    return listed, disjoined


_ALTERNATIVE_RES: Final = {other: _alternative_patterns(other) for other in _OTHER_ROLE}
_JOURNAL_HEADING_RE: Final = re.compile(r"## (Pause|Resume) by ([a-z0-9][a-z0-9-]*) at (\S+) in `([^`]+)`[ \t]*")
_FRACTION_RE: Final = re.compile(r"\.(\d+)")
_MICROSECOND_DIGITS: Final = 6


@dataclass(frozen=True)
class PaneActivity:
    """One pane's TUIOS activity: state, blocking reason, held draft, waiting question and readiness.

    ``ready`` is ``None`` when the record carries no readiness.
    """

    state: str
    blocked_by: str
    draft_held: bool
    question: str
    ready: bool | None

    @property
    def blocked(self) -> bool:
        """Return whether the pane waits on the person."""
        return bool(self.blocked_by) or self.state in _BLOCKED_STATES


@dataclass(frozen=True)
class PaneObservation:
    """Every live pane record and the activity of each, from one listing."""

    panes: tuple[PaneRecord, ...]
    activity: Mapping[str, PaneActivity]


def _string(value: object) -> str:
    """Return one JSON string, refusing every other type."""
    if not isinstance(value, str):
        raise ArtifactError(_MALFORMED)
    return value


def _activity(record: Mapping[str, object]) -> PaneActivity:
    """Parse the activity fields of one agent record; absent fields read as empty, absent readiness as unknown."""
    draft, ready = record.get("draft_held", False), record.get("ready")
    if not isinstance(draft, bool) or not (ready is None or isinstance(ready, bool)):
        raise ArtifactError(_MALFORMED)
    return PaneActivity(
        _string(record.get("state", "")), _string(record.get("blocked_by", "")), draft, _string(record.get("message", "")), ready,
    )


def parse_activity(text: str) -> dict[str, PaneActivity]:
    """Parse each pane's activity, keyed by full pane UUID; a repeated pane id gets none."""
    try:
        agents = as_mapping(loads_strict(text)).get("agents")
    except (ValueError, RecursionError) as error:
        raise ArtifactError(_MALFORMED) from error
    items = as_items(agents)
    if not isinstance(agents, list):
        raise ArtifactError(_MALFORMED)
    activity: dict[str, PaneActivity] = {}
    repeated: set[str] = set()
    for item in items:
        record = as_mapping(item)
        try:
            key = pane_id(record.get("window_id"), "pane id")
        except ArtifactError as error:
            raise ArtifactError(_MALFORMED) from error
        if key in activity:
            repeated.add(key)
        activity[key] = _activity(record)
    return {key: value for key, value in activity.items() if key not in repeated}


def observe_panes(runner: CommandRunner) -> PaneObservation | None:
    """List every live pane once across sessions, or ``None`` when discovery failed."""
    result = runner.run(LIST_AGENTS)
    if result.exit_code != 0:
        return None
    try:
        return PaneObservation(parse_agents(result.stdout), parse_activity(result.stdout))
    except ArtifactError:
        return None


class Activity(StrEnum):
    """Whether one pane may receive input now, or why not."""

    ELIGIBLE = "eligible"
    BUSY = "busy"
    BLOCKED = "blocked"
    DRAFT = "draft"
    NOT_READY = "not-ready"
    UNKNOWN = "unknown"


class ScreenVerdict(StrEnum):
    """A supported pane capture's reading; ``UNSUPPORTED`` proves nothing."""

    IDLE_EMPTY = "idle-empty"
    DRAFT = "draft"
    QUESTION = "question"
    WORKING = "working"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class Eligibility:
    """Input eligibility of one pane, with a note when fresher evidence decided it."""

    activity: Activity
    note: str = ""


class ScreenProbe(Protocol):
    """Injected fresh capture of one Codex pane under its pinned screen profile."""

    def probe(self, pane: PaneRecord) -> ScreenVerdict:
        """Return the capture's reading, ``UNSUPPORTED`` when no profile applies."""
        ...


_SCREEN: Final = {
    ScreenVerdict.IDLE_EMPTY: Eligibility(Activity.ELIGIBLE, "stale-working-overridden"),
    ScreenVerdict.DRAFT: Eligibility(Activity.DRAFT),
    ScreenVerdict.QUESTION: Eligibility(Activity.BLOCKED),
    ScreenVerdict.WORKING: Eligibility(Activity.BUSY),
    ScreenVerdict.UNSUPPORTED: Eligibility(Activity.BUSY),
}


def _status(activity: PaneActivity | None) -> Eligibility | None:
    """Classify from TUIOS activity alone; ``None`` for a working pane, which needs more evidence."""
    if activity is None:
        return Eligibility(Activity.UNKNOWN)
    if activity.blocked:
        return Eligibility(Activity.BLOCKED)
    if activity.draft_held:
        return Eligibility(Activity.DRAFT)
    if activity.state in _IDLE_STATES:
        return Eligibility(Activity.ELIGIBLE if activity.ready is True else Activity.NOT_READY)
    return None if activity.state == _WORKING else Eligibility(Activity.UNKNOWN)


def input_eligibility(pane: PaneRecord, host: Host, activity: PaneActivity | None, probe: ScreenProbe) -> Eligibility:
    """Classify one pane; a busy Claude pane skips at once, a busy Codex pane gets one capture."""
    status = _status(activity)
    if status is not None:
        return status
    if host is not Host.CODEX:
        return Eligibility(Activity.BUSY)
    return _SCREEN[probe.probe(pane)]


class CommandKind(StrEnum):
    """Resume commands that count as checkout-wide duplicate evidence."""

    RESUME_SESSION = "resume-session"
    REVIEW_RESUME = "review-resume"


@dataclass(frozen=True)
class ClassifiedCommand:
    """A resume command, the role a ``review-resume`` selects, and whether that role is uncertain."""

    kind: CommandKind
    role: SessionRole | None
    uncertain: bool


def _selected_role(rest: str) -> tuple[SessionRole | None, bool]:
    """Return the role the text after ``review-resume`` selects, and whether it is uncertain.

    Only the marker, or a role word, ``--role <role>`` or ``as <role>``
    heading the arguments, selects a role; a role phrase inside prose selects
    nothing. The other role makes the selection uncertain when it is offered
    as an alternative, whatever the punctuation: in another selection form
    anywhere, joined by ``or``, ``nor``, ``/`` or ``|`` (``reviewer (or
    requestor)``), or listed bare right after the head (``reviewer and
    requestor``). Any other mention of it, such as ``as reviewer while the
    requestor is busy``, is explanatory.
    """
    if MARKER_FLAG in rest.split():
        try:
            return marker_in_command(rest).role, False
        except ArtifactError:
            return None, True
    head = _HEAD_SELECTION_RE.match(rest)
    if head is None:
        return None, False
    role, remainder = head[1].lower(), rest[head.end():]
    other = _OTHER_ROLE[role]
    listed, disjoined = _ALTERNATIVE_RES[other]
    selected = {word.lower() for word in _SELECTION_FORM_RE.findall(remainder)}
    if other in selected or listed.match(remainder) or disjoined.search(remainder):
        return None, True
    return SessionRole(role), False


def classify_command(text: str) -> ClassifiedCommand | None:
    """Classify one typed text; ``None`` when it is not a resume command."""
    match = _COMMAND_RE.fullmatch(text)
    if match is None:
        return None
    kind = CommandKind(match["name"].lower())
    if kind is CommandKind.RESUME_SESSION:
        return ClassifiedCommand(kind, None, uncertain=False)
    role, uncertain = _selected_role(match["rest"])
    return ClassifiedCommand(kind, role, uncertain=uncertain)


def counted(command: ClassifiedCommand, *, reviewer_pause: bool) -> bool | None:
    """Return whether the command suppresses the pause, or ``None`` when its role is uncertain."""
    if command.kind is CommandKind.RESUME_SESSION or reviewer_pause:
        return True
    if command.uncertain or command.role is None:
        return None
    return command.role is not SessionRole.REVIEWER


@dataclass(frozen=True)
class ObservedCommand:
    """One typed command seen on a pane, with its time when attributable."""

    text: str
    at: datetime | None


class CommandHistory(Protocol):
    """Injected typed-command evidence of one pane: agent-log prompts or screen commands."""

    def commands(self, pane: PaneRecord) -> tuple[ObservedCommand, ...] | None:
        """Return the pane's observed commands, or ``None`` when its history is unreadable."""
        ...


@dataclass(frozen=True)
class JournalResume:
    """One resume entry of the private session journal."""

    agent: str
    at: datetime
    checkout: CanonicalRoot


def _no_entries() -> dict[CanonicalRoot, tuple[JournalResume, ...]]:
    """Start an empty journal index."""
    return {}


@dataclass(frozen=True)
class JournalIndex:
    """Resume entries by canonical checkout, or the error that makes the journal unusable."""

    entries: Mapping[CanonicalRoot, tuple[JournalResume, ...]] = field(default_factory=_no_entries)
    error: str = ""

    def resumes(self, root: CanonicalRoot) -> tuple[JournalResume, ...] | None:
        """Return the checkout's resume entries, or ``None`` when the journal is unusable."""
        return None if self.error else self.entries.get(root, ())


def journal_time(stamp: str) -> datetime:
    """Parse one journal timestamp, cutting or padding its fraction to microseconds."""
    normalized = _FRACTION_RE.sub(lambda match: "." + match[1][:_MICROSECOND_DIGITS].ljust(_MICROSECOND_DIGITS, "0"), stamp, count=1)
    try:
        moment = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ArtifactError(f"session journal has a bad timestamp {stamp!r}") from error
    if moment.tzinfo is None:
        raise ArtifactError(f"session journal timestamp without offset {stamp!r}")
    return moment


def _journal_entries(text: str) -> dict[CanonicalRoot, list[JournalResume]]:
    """Index the resume entries; any unrecognized entry heading makes the journal unusable."""
    entries: dict[CanonicalRoot, list[JournalResume]] = {}
    for line in text.splitlines():
        if not line.startswith("## "):
            continue
        heading = _JOURNAL_HEADING_RE.fullmatch(line)
        if heading is None:
            raise ArtifactError(f"session journal has an unrecognized heading {line!r}")
        if heading[1] == "Resume":
            root = CanonicalRoot.parse(heading[4], "session journal checkout")
            entries.setdefault(root, []).append(JournalResume(heading[2], journal_time(heading[3]), root))
    return entries


def parse_session_journal(data: bytes) -> JournalIndex:
    """Parse the journal's exact bytes into its resume index, or report why it is unusable."""
    try:
        entries = _journal_entries(data.decode("utf-8"))
    except UnicodeDecodeError:
        return JournalIndex(error="session journal is not UTF-8")
    except ArtifactError as error:
        return JournalIndex(error=str(error))
    return JournalIndex({root: tuple(resumes) for root, resumes in entries.items()})


def _read_bytes(path: Path) -> bytes:
    """Read one file's exact bytes."""
    return path.read_bytes()


def read_session_journal(path: Path, *, read: Callable[[Path], bytes] = _read_bytes) -> JournalIndex:
    """Read the session journal as an index: missing means no entry, unreadable is an error."""
    try:
        data = read(path)
    except FileNotFoundError:
        return JournalIndex()
    except OSError as error:
        return JournalIndex(error=f"session journal is unreadable: {error.strerror or error}")
    return parse_session_journal(data)


def journal_path(environ: Mapping[str, str]) -> Path | None:
    """Return the journal path under ``USERPROFILE``, or ``None`` when the profile is unset."""
    profile = environ.get("USERPROFILE", "")
    return Path(profile) / ".llm-shared" / JOURNAL_NAME if profile else None


class DuplicateSignal(StrEnum):
    """Kinds of evidence that a checkout is already being resumed."""

    RECEIPT = "receipt"
    JOURNAL = "journal"
    COMMAND = "command"
    OVERRIDE = "override-pending"


@dataclass(frozen=True)
class DuplicateEvidence:
    """One duplicate-resume signal: its pane when known, a non-secret detail and its time when known."""

    signal: DuplicateSignal
    pane_id: str | None
    detail: str
    at: datetime | None


@dataclass(frozen=True)
class DuplicateVerdict:
    """Certain duplicate evidence and the uncertain observations, kept apart."""

    evidence: tuple[DuplicateEvidence, ...]
    uncertain: tuple[str, ...]


@dataclass(frozen=True)
class PauseFacts:
    """The pause a duplicate check protects: its checkout, snapshot instant and saved reviewer role."""

    root: CanonicalRoot
    at: datetime
    reviewer: bool


def _detail(command: ClassifiedCommand) -> str:
    """Name one counted command and the role it selects."""
    return command.kind.value if command.role is None else f"{command.kind.value} {command.role.value}"


def _order(at: datetime | None, pause: datetime) -> str:
    """Place one observation against the pause: ``later`` alone proves it followed the pause."""
    if at is None:
        return "unattributed"
    if at < pause:
        return "older"
    return "later" if at > pause else "unordered"


def _command_evidence(pause: PauseFacts, pane: PaneRecord, observed: ObservedCommand) -> DuplicateEvidence | str | None:
    """Return the evidence one observed command gives, its uncertainty, or ``None``.

    A command that can never count for this pause, such as a proved
    reviewer-only continuation of a non-reviewer pause, is ignored whatever
    its time; any other command needs a time strictly later than the pause.
    """
    command = classify_command(observed.text)
    decision = None if command is None else counted(command, reviewer_pause=pause.reviewer)
    order = _order(observed.at, pause.at)
    if command is None or decision is False or order == "older":
        return None
    if order != "later":
        return f"command-{order} {pane.pane_id}"
    if decision is None:
        return f"review-role-uncertain {pane.pane_id}"
    return DuplicateEvidence(DuplicateSignal.COMMAND, pane.pane_id, _detail(command), observed.at)


def _pane_evidence(pause: PauseFacts, pane: PaneRecord, history: CommandHistory, activity: PaneActivity | None) -> list[DuplicateEvidence | str]:
    """Gather one pane's override question and counted commands."""
    found: list[DuplicateEvidence | str] = []
    if activity is not None and activity.blocked and OVERRIDE_QUESTION in activity.question.lower():
        found.append(DuplicateEvidence(DuplicateSignal.OVERRIDE, pane.pane_id, "author-override question", None))
    commands = history.commands(pane)
    if commands is None:
        return [*found, f"command-history-unreadable {pane.pane_id}"]
    for observed in commands:
        item = _command_evidence(pause, pane, observed)
        if item is not None:
            found.append(item)
    return found


def _journal_evidence(pause: PauseFacts, journal: JournalIndex) -> list[DuplicateEvidence | str]:
    """Return the checkout's resume entries strictly later than the pause; an equal time stays uncertain."""
    resumes = journal.resumes(pause.root)
    if resumes is None:
        return ["session-journal-unreadable"]
    found: list[DuplicateEvidence | str] = []
    for entry in resumes:
        order = _order(entry.at, pause.at)
        if order == "later":
            found.append(DuplicateEvidence(DuplicateSignal.JOURNAL, None, entry.agent, entry.at))
        elif order == "unordered":
            found.append(f"journal-resume-unordered {entry.agent}")
    return found


def classify_duplicates(
    pause: PauseFacts, panes: Sequence[PaneRecord], history: CommandHistory, activity: Mapping[str, PaneActivity], journal: JournalIndex,
) -> DuplicateVerdict:
    """Gather checkout-wide duplicate evidence from the journal and every pane, in pane id order."""
    found = _journal_evidence(pause, journal)
    for pane in sorted(panes, key=lambda record: record.pane_id):
        found += _pane_evidence(pause, pane, history, activity.get(pane.pane_id))
    evidence = tuple(item for item in found if isinstance(item, DuplicateEvidence))
    return DuplicateVerdict(evidence, tuple(item for item in found if isinstance(item, str)))


__all__ = [
    "JOURNAL_NAME",
    "OVERRIDE_QUESTION",
    "Activity",
    "ClassifiedCommand",
    "CommandHistory",
    "CommandKind",
    "DuplicateEvidence",
    "DuplicateSignal",
    "DuplicateVerdict",
    "Eligibility",
    "JournalIndex",
    "JournalResume",
    "ObservedCommand",
    "PaneActivity",
    "PaneObservation",
    "PauseFacts",
    "ScreenProbe",
    "ScreenVerdict",
    "classify_command",
    "classify_duplicates",
    "counted",
    "input_eligibility",
    "journal_path",
    "journal_time",
    "observe_panes",
    "parse_activity",
    "parse_session_journal",
    "read_session_journal",
]


# eof
