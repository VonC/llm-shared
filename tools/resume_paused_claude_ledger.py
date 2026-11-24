"""Claude lifecycle ledger: positive absence of recorded host-managed waiting work.

Step 1 of v0.15.0 resume-paused. ``ClaudeLedger`` proves absence only when
every in-scope transcript is complete, classified under the pinned profile,
closed and matched; any gap reports pending with counted reasons. No profile is
shipped, so no real pane can reach a proof.

Fix (code review round 1, split from ``tools.resume_paused_claude``):

- R1: closure covers every record with an identifier, sidechains included.
  A repeated identifier, an input without one, and a missing parent are
  pending; only profile-validated shapes may be chain tips.
- R2: every transcript read, bound or not, recent or read for schedules only,
  must carry the pinned version and pass closed-world classification.
- R3: each task start and schedule creation is matched to its own later
  terminal or deletion. A terminal that precedes its start, a reused
  identifier, and a terminal in an unrelated session file close nothing.
- R4: the bound transcript must belong to the checkout, the pane's session
  identity must come from a report, and the pane's process generation must be
  unchanged after the read. With a proved marked resume input, only starts
  whose single call descends from that input and is a recognized requestor
  operation are excluded; watchers and every other start stay in scope.

Fix (code review round 2):

- R2-1: the parent links must form no cycle, every input needs its own
  closed turn (a final record below it, reached before any other input), and
  a profile-validated leaf counts only inside such a closed turn.
- R2-2: each tool call identifier names one call and one result, and that
  result must be recorded below its call in the parent chain. The record
  graph answering these questions lives in ``tools.resume_paused_claude_graph``.
- R2-3: an end closes a start only when strictly later. Across files it also
  needs a continuation the caller proved, ``LedgerScope.continuations``, into
  a file that begins with a clear marker; the marker alone proves nothing.
- R2-4: the bound transcript needs positive checkout evidence: at least one
  recorded ``cwd`` and none outside the checkout.
- R2-6: a message content block type outside the pinned profile is
  unclassified in every transcript read.

Fix (code review round 3):

- R3-1: the requestor exception covers the qualifying start record itself,
  never its task id. A covered start still counts as a use of its
  identifier, so another start sharing it stays pending with the reuse.
  ``_requestor_calls`` collects the recognized requestor calls.
- R3-2: a pinned leaf must carry an instant strictly before the final record
  of its turn; a leaf recorded after its turn closed is pending.
- R3-3: ``continuation_places`` numbers each file along its single proved
  chain in one pass instead of expanding every reachable pair; a branching or
  looping continuation places nothing.

Fix (code review round 4):

- R4-1: every transcript read since boot needs a complete generation, not
  only the bound one: an accepted first marker and no later SessionStart
  other than a compaction. Another writer's transcript accepts the startup
  marker, or a clear marker only when the caller proved its continuation; the
  bound process identity is never applied to it.
- R4-2: a plain tool result that is neither a recorded error nor validated
  for its tools is unclassified, and a schedule creation without a recognized
  identifier is unrecognized; a recorded error creates and deletes nothing.

Fix (code review round 5):

- R5-1: a proved continuation into a listed file needs its earlier file in
  the scope. An earlier file missing from the enumeration, or excluded as
  another checkout's transcript, counts ``continuation-predecessor-missing``,
  so a cleared file never proves a complete generation over lost history.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Final

from tools.resume_paused_claude import (
    STARTUP_MARKERS,
    ClaudeLedgerProfile,
    ExchangeCall,
    ParseScope,
    RecordFact,
    TranscriptRejectedError,
    parse_transcript,
    record_shape,
)
from tools.resume_paused_claude_graph import INPUT_SHAPE, TranscriptGraph, repeated
from tools.resume_paused_profiles import DISCLOSED_LIMITS, ReadAccount, Reason
from tools.resume_paused_windows import filetime_to_datetime

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from datetime import datetime

    from tools.resume_paused_claude import TranscriptFile, TranscriptSource
    from tools.resume_paused_profiles import ProcessIdentity

_COMPACT_MARKER: Final = "SessionStart:compact"
_CLEAR_MARKER: Final = "SessionStart:clear"
_SESSION_START: Final = "SessionStart:"
_REPORT: Final = "report"


class Absence(StrEnum):
    """Whether recorded host-managed waiting work is proved absent."""

    PROVED = "proved"
    PENDING = "pending"


@dataclass(frozen=True)
class LedgerScope:
    """What one absence decision covers.

    ``bound_path`` is the transcript of the pane's reported session id and
    ``process`` the generation of the pane's single Claude child, observed
    before the read. ``markers`` are the SessionStart forms accepted as the
    first timestamped record. ``identity_source`` is how TUIOS learned the
    session id. ``marked_input`` is the complete marked resume command when
    the bound pane is the proved requestor; it is compared in memory only.
    ``continuations`` holds each (earlier transcript path, later transcript
    path) pair that independent pane evidence proved to be one Claude process
    cleared from the first session into the second. Without such a pair, no
    record in one file ends work started in another. The earlier file of each
    pair into a listed file must itself be listed and in the checkout.
    """

    checkout: str
    boot_boundary: datetime
    bound_path: str
    session_id: str
    process: ProcessIdentity
    markers: frozenset[str] = STARTUP_MARKERS
    identity_source: str = _REPORT
    marked_input: str | None = None
    continuations: frozenset[tuple[str, str]] = frozenset()


@dataclass(frozen=True)
class LedgerDecision:
    """Absence verdict with counted reasons, bytes read and disclosed limits."""

    absence: Absence
    reasons: tuple[Reason, ...]
    account: ReadAccount
    limits: tuple[str, ...] = DISCLOSED_LIMITS


@dataclass(frozen=True)
class _Event:
    """One lifecycle start or end: its identifier, instant and transcript path.

    ``exempt`` marks the one start record the requestor exception covers. It
    never blocks by itself, yet it still counts as a use of its identifier.
    """

    key: str
    at: datetime | None
    path: str
    exempt: bool = False


def _folded(path: str) -> str:
    return path.replace("\\", "/").rstrip("/").casefold()


def _placement(facts: tuple[RecordFact, ...], checkout: str) -> bool | None:
    """Tell where the recorded cwd values put a transcript.

    Returns:
        ``True`` when every recorded cwd lies in the checkout, ``False`` when
        every one lies outside, and ``None`` when none is recorded or they
        disagree.
    """
    root = _folded(checkout)
    cwds = {_folded(fact.cwd) for fact in facts if fact.cwd}
    inside = {cwd == root or cwd.startswith(root + "/") for cwd in cwds}
    return inside.pop() if len(inside) == 1 else None


def _restarts(fact: RecordFact) -> bool:
    """Tell whether a record is a SessionStart other than a compaction."""
    hook = fact.hook or ""
    return hook.startswith(_SESSION_START) and hook != _COMPACT_MARKER


def _versions(facts: tuple[RecordFact, ...]) -> set[str]:
    """Return every host version a transcript records."""
    return {fact.version for fact in facts if fact.version}


def _marked_uuid(facts: tuple[RecordFact, ...]) -> str | None:
    """Return the identifier of the single human-typed marked input, if exactly one exists."""
    marked = [fact.uuid for fact in facts if fact.marked and fact.origin == "human" and fact.prompt_source == "typed"]
    return marked[0] if len(marked) == 1 else None


def _requestor_calls(facts: Iterable[RecordFact]) -> set[tuple[str, ...]]:
    """Return each recognized requestor call as the single-result tuple that answers it."""
    return {(call,) for fact in facts for call, kind in fact.exchange_calls if kind is ExchangeCall.REQUESTOR}


def _first_stamped(facts: tuple[RecordFact, ...]) -> RecordFact | None:
    """Return the first record that carries a timestamp."""
    return next((fact for fact in facts if fact.timestamp is not None), None)


def continuation_places(pairs: Iterable[tuple[str, str]]) -> dict[str, tuple[str, int]]:
    """Number each transcript along its single proved continuation chain.

    A session clears into one next file, so a proved pair is kept only when
    its earlier file has no other successor and its later file no other
    predecessor; a branching or looping link places nothing. Each kept file
    is visited once: the work and the result grow with the number of pairs,
    never with their product.

    Args:
        pairs: The proved (earlier path, later path) continuation pairs.

    Returns:
        For each placed path, the head of its chain and its position in it.
    """
    links = list(pairs)
    successors = Counter(first for first, _ in links)
    predecessors = Counter(last for _, last in links)
    step = {first: last for first, last in links if successors[first] == 1 and predecessors[last] == 1}
    followers = set(step.values())
    places: dict[str, tuple[str, int]] = {}
    for head in step:
        node: str | None = None if head in followers else head
        position = 0
        while node is not None:
            places[node] = (head, position)
            position += 1
            node = step.get(node)
    return places


def _earliest(first: datetime | None, second: datetime | None) -> datetime | None:
    """Return the earlier instant, or ``None`` when either one is unknown."""
    return None if first is None or second is None else min(first, second)


def _ends(start: _Event, end: _Event, places: dict[str, tuple[str, int]]) -> bool:
    """Tell whether an end is this start's own end.

    The end must be strictly later: an equal instant orders nothing. In
    another file it also needs a proved continuation chain that leads from
    the start's file to the end's file.
    """
    if start.at is None or end.at is None or end.at <= start.at:
        return False
    first, last = places.get(start.path), places.get(end.path)
    chained = first is not None and last is not None and first[0] == last[0] and first[1] < last[1]
    return end.path == start.path or chained


def _unmatched(starts: list[_Event], ends: list[_Event], places: dict[str, tuple[str, int]]) -> tuple[int, int]:
    """Count starts without their own later end, and identifiers started twice.

    An exempt start is never counted open, but its identifier still counts:
    another start sharing it stays open, whatever end is recorded.
    """
    by_key: dict[str, list[_Event]] = {}
    for end in ends:
        by_key.setdefault(end.key, []).append(end)
    counts = Counter(start.key for start in starts)
    blocking = [start for start in starts if not start.exempt]
    open_starts = sum(
        1 for start in blocking if counts[start.key] > 1 or not any(_ends(start, end, places) for end in by_key.get(start.key, ()))
    )
    return open_starts, repeated(counts.values())


def _outside(values: Iterable[str], allowed: frozenset[str]) -> int:
    """Count the values outside a pinned closed set."""
    return sum(1 for value in values if value not in allowed)


def _clears(facts: tuple[RecordFact, ...]) -> bool:
    """Tell whether a transcript begins with a clear marker."""
    first = _first_stamped(facts)
    return first is not None and first.attachment == "hook_success" and first.hook == _CLEAR_MARKER


def _call_names(facts: tuple[RecordFact, ...]) -> dict[str, str]:
    """Return the tool name of each call identifier a transcript records."""
    return {call: name for fact in facts for call, name in fact.calls}


def _missing_predecessors(continuations: frozenset[tuple[str, str]], listed: frozenset[str], outside: set[str]) -> int:
    """Count proved continuations into a listed file whose earlier file is missing from the scope.

    The pair names the earlier file, so its absence from the enumeration, or
    its exclusion as another checkout's transcript, is detected missing
    history: the later file cannot prove that the earlier one held no other
    work. Each link of a chain is checked, so a missing ancestor is counted
    too. An unreadable or incomplete earlier file is counted by its own read
    reason, and one older than the boot boundary stays under the boot rule.
    """
    return sum(1 for earlier, later in continuations if later in listed and (earlier not in listed or earlier in outside))


def _writer_markers(*, continued: bool) -> frozenset[str]:
    """Return the first markers accepted for a transcript other than the bound one.

    A startup marker opens a complete generation. A clear marker does only
    when the caller proved that this file continues an earlier file of the
    same process: the requestor's own acceptance of a clear never extends to
    another writer.
    """
    return STARTUP_MARKERS | {_CLEAR_MARKER} if continued else STARTUP_MARKERS


def _marker(first: RecordFact | None, markers: frozenset[str], process: ProcessIdentity | None, reasons: Counter[str]) -> None:
    """Require the first timestamped record to be an accepted marker, after the process creation when known."""
    if first is None or first.timestamp is None or first.attachment != "hook_success" or first.hook not in markers:
        reasons["generation-marker-missing"] += 1
    elif process is not None and first.timestamp < filetime_to_datetime(process.created_at):
        reasons["generation-marker-before-process"] += 1


def _generation(facts: tuple[RecordFact, ...], markers: frozenset[str], process: ProcessIdentity | None, reasons: Counter[str]) -> None:
    """Require one complete generation: an accepted first marker and no later restart.

    A missing or unaccepted first marker means missing history, and a later
    SessionStart other than a compaction means another generation wrote into
    the file. Both are pending.
    """
    first = _first_stamped(facts)
    _marker(first, markers, process, reasons)
    reasons["generation-restarted"] += sum(1 for fact in facts if fact is not first and _restarts(fact))


@dataclass(frozen=True)
class _Transcript:
    """One parsed transcript in scope: its path, records, binding and record graph."""

    path: str
    facts: tuple[RecordFact, ...]
    bound: bool
    graph: TranscriptGraph


class _Tally:
    """Counted reasons and lifecycle events across in-scope transcripts.

    ``continued`` indexes, once per decision, the files a proved continuation
    leads into. ``listed`` holds every enumerated path and ``outside`` the
    read transcripts the checkout rule excluded.
    """

    def __init__(self, continuations: frozenset[tuple[str, str]] = frozenset()) -> None:
        self.continuations = continuations
        self.continued = frozenset(later for _, later in continuations)
        self.listed: frozenset[str] = frozenset()
        self.outside: set[str] = set()
        self.reasons: Counter[str] = Counter()
        self.account = ReadAccount()
        self.cleared: set[str] = set()
        self.task_starts: list[_Event] = []
        self.task_ends: list[_Event] = []
        self.schedule_starts: list[_Event] = []
        self.schedule_ends: list[_Event] = []

    def decision(self) -> LedgerDecision:
        """Match each start to its own end and render the verdict.

        A proved continuation counts only into a file that begins with a
        clear marker, and every earlier file a continuation names must be in
        the scope.
        """
        self.reasons["continuation-predecessor-missing"] += _missing_predecessors(self.continuations, self.listed, self.outside)
        places = continuation_places(pair for pair in self.continuations if pair[1] in self.cleared)
        tasks, reused_tasks = _unmatched(self.task_starts, self.task_ends, places)
        schedules, reused_schedules = _unmatched(self.schedule_starts, self.schedule_ends, places)
        self.reasons["background-start-unmatched"] += tasks
        self.reasons["task-id-reused"] += reused_tasks
        self.reasons["schedule-unresolved"] += schedules
        self.reasons["schedule-id-reused"] += reused_schedules
        reasons = tuple(Reason(code, count) for code, count in sorted(self.reasons.items()) if count)
        return LedgerDecision(Absence.PENDING if reasons else Absence.PROVED, reasons, self.account)


class ClaudeLedger:
    """Evaluate positive absence over the transcripts of one checkout."""

    def __init__(
        self, profile: ClaudeLedgerProfile, source: TranscriptSource, rebind: Callable[[], ProcessIdentity | None],
    ) -> None:
        """Keep the pinned classification, the transcript access and the process probe.

        Args:
            profile: The pinned closed-world classification.
            source: Injected access to the checkout's transcripts.
            rebind: Observes the pane's current Claude process generation; it
                is called after the read to detect a changed binding.
        """
        self._profile = profile
        self._source = source
        self._rebind = rebind

    def evaluate(self, scope: LedgerScope) -> LedgerDecision:
        """Prove absence only when every in-scope record is complete and matched."""
        tally = _Tally(scope.continuations)
        listing = self._source.list_files()
        if listing is None:
            return LedgerDecision(Absence.PENDING, (Reason("enumeration-incomplete"),), tally.account)
        tally.listed = frozenset(file.path for file in listing)
        tally.reasons["bound-transcript-missing"] += scope.bound_path not in tally.listed
        tally.reasons["session-identity-unreported"] += scope.identity_source != _REPORT
        for file in listing:
            self._read(file, scope, tally)
        tally.reasons["process-binding-changed"] += self._rebind() != scope.process
        return tally.decision()

    def _read(self, file: TranscriptFile, scope: LedgerScope, tally: _Tally) -> None:
        """Read one transcript: classification and schedules always, lifecycle since boot."""
        bound = file.path == scope.bound_path
        recent = bound or file.modified >= scope.boot_boundary
        if not (recent or self._profile.durable_schedules):
            return
        marked = scope.marked_input if bound else None
        facts = self._facts(file.path, ParseScope(marked, self._profile.requestor_operations), tally)
        if facts is None:
            return
        if not self._in_checkout(facts, scope.checkout, tally.reasons, bound=bound):
            tally.outside.add(file.path)
            return
        transcript = _Transcript(file.path, facts, bound, TranscriptGraph(facts))
        if _clears(facts):
            tally.cleared.add(file.path)
        self._classify(facts, tally.reasons)
        self._calls(transcript, tally.reasons)
        self._results(transcript, tally.reasons)
        self._schedules(transcript, tally)
        if recent:
            self._lifecycle(transcript, scope, tally)

    def _facts(self, path: str, scope: ParseScope, tally: _Tally) -> tuple[RecordFact, ...] | None:
        """Read and parse one transcript, accounting its bytes."""
        data = self._source.read(path)
        if data is None:
            tally.reasons["read-failed"] += 1
            return None
        tally.account = tally.account.plus(len(data))
        try:
            return parse_transcript(data, scope)
        except TranscriptRejectedError as rejected:
            tally.reasons[str(rejected)] += 1
            return None

    @staticmethod
    def _in_checkout(facts: tuple[RecordFact, ...], checkout: str, reasons: Counter[str], *, bound: bool) -> bool:
        """Apply the checkout rule and tell whether the transcript stays in scope.

        The bound transcript needs positive evidence: a recorded cwd, and none
        outside the checkout. Any other transcript leaves the scope only when
        every recorded cwd lies outside; one that cannot be excluded stays.
        """
        placed = _placement(facts, checkout)
        reasons["bound-transcript-other-checkout"] += bound and placed is False
        reasons["bound-transcript-checkout-unproved"] += bound and placed is None
        return placed is not False

    def _classify(self, facts: tuple[RecordFact, ...], reasons: Counter[str]) -> None:
        """Require the pinned version and count everything outside the closed world."""
        profile = self._profile
        attachments = (fact.attachment for fact in facts if fact.attachment is not None)
        reasons["version-unpinned"] += _versions(facts) != {profile.version}
        reasons["record-unclassified"] += _outside((fact.kind for fact in facts), profile.record_types)
        reasons["attachment-unclassified"] += _outside(attachments, profile.attachment_types)
        reasons["content-unclassified"] += _outside((block for fact in facts for block in fact.blocks), profile.block_types)
        reasons["tool-unclassified"] += _outside((name for fact in facts for _, name in fact.calls), profile.tool_names)

    @staticmethod
    def _calls(transcript: _Transcript, reasons: Counter[str]) -> None:
        """Require each tool call to have its own single result, recorded below it.

        An identifier naming two calls or two results is pending, and so is a
        result that does not descend from its call: it may answer earlier work.
        """
        reasons.update(transcript.graph.call_faults())

    def _results(self, transcript: _Transcript, reasons: Counter[str]) -> None:
        """Count plain tool results the profile cannot classify.

        A result container that is not an object may hide a start. It is
        classified only when the result is a recorded error, or when every
        tool it answers is validated to return a plain result and start no
        lifecycle work.
        """
        names = _call_names(transcript.facts)
        plain = self._profile.plain_result_tools
        unknown = (fact for fact in transcript.facts if fact.plain_result and not fact.failed)
        reasons["result-unclassified"] += sum(1 for fact in unknown if not {names.get(result) for result in fact.results} <= plain)

    def _schedules(self, transcript: _Transcript, tally: _Tally) -> None:
        """Record each schedule creation and deletion with its instant; a recorded error does neither."""
        names = _call_names(transcript.facts)
        for fact in transcript.facts:
            if fact.results and not fact.failed:
                self._schedule(fact, {names.get(result) for result in fact.results}, transcript.path, tally)

    def _schedule(self, fact: RecordFact, tools: set[str | None], path: str, tally: _Tally) -> None:
        """Record the schedule one result creates or deletes.

        A creation needs its recognized identifier: a creation result without
        one is unrecognized, never read as "no schedule".
        """
        event = _Event(fact.result_id, fact.timestamp, path) if fact.result_id else None
        if self._profile.schedule_create in tools:
            if event is None:
                tally.reasons["schedule-result-unrecognized"] += 1
            else:
                tally.schedule_starts.append(event)
        if self._profile.schedule_delete in tools and event is not None:
            tally.schedule_ends.append(event)

    def _lifecycle(self, transcript: _Transcript, scope: LedgerScope, tally: _Tally) -> None:
        """Check a transcript since boot: its generation, binding, graph, closure and task events.

        Every transcript needs a complete generation. The bound one is checked
        against the scope's markers and the pane's process; any other writer's
        transcript against ``_writer_markers``, with no process of its own.
        """
        facts = transcript.facts
        excluded: frozenset[str] = frozenset()
        if transcript.bound:
            excluded = self._bound(transcript, scope, tally.reasons)
        else:
            _generation(facts, _writer_markers(continued=transcript.path in tally.continued), None, tally.reasons)
        self._graph(transcript, tally.reasons)
        self._closure(transcript, tally.reasons)
        statuses = self._profile.terminal_statuses
        for fact in facts:
            if fact.started:
                tally.task_starts.append(_Event(fact.started, fact.timestamp, transcript.path, fact.uuid in excluded))
            if fact.terminal and fact.terminal[1] in statuses:
                tally.task_ends.append(_Event(fact.terminal[0], fact.timestamp, transcript.path))

    def _bound(self, transcript: _Transcript, scope: LedgerScope, reasons: Counter[str]) -> frozenset[str]:
        """Bind the pane's transcript; return the start records its requestor exception covers."""
        facts = transcript.facts
        _generation(facts, scope.markers, scope.process, reasons)
        reasons["session-mismatch"] += {fact.session for fact in facts if fact.session} != {scope.session_id}
        return self._requestor_starts(transcript, reasons) if scope.marked_input is not None else frozenset()

    @staticmethod
    def _requestor_starts(transcript: _Transcript, reasons: Counter[str]) -> frozenset[str]:
        """Return the start records that are recognized requestor operations after the marked input.

        Creation order comes from the parent chain: a record that descends
        from the marked input was created after it. File position is never
        used. A start qualifies only when its single answered call descends
        from the marked input and is a requestor operation. The result names
        records by their identifier, never task ids: another start sharing a
        covered start's task id is not covered.
        """
        root = _marked_uuid(transcript.facts)
        if root is None:
            reasons["marked-input-unproved"] += 1
            return frozenset()
        later = [fact for fact in transcript.graph.chain if transcript.graph.below(fact, root)]
        requestor = _requestor_calls(later)
        return frozenset(fact.uuid for fact in later if fact.uuid and fact.started and fact.results in requestor)

    @staticmethod
    def _graph(transcript: _Transcript, reasons: Counter[str]) -> None:
        """Require one record per identifier, identified inputs, present parents and no loop."""
        identifiers = Counter(fact.uuid for fact in transcript.graph.chain)
        parents = [fact.parent for fact in transcript.graph.chain if fact.parent]
        reasons["uuid-duplicate"] += repeated(identifiers.values())
        reasons["input-without-uuid"] += sum(1 for fact in transcript.facts if fact.text_input and not fact.uuid)
        reasons["parent-missing"] += sum(1 for parent in parents if parent not in identifiers)
        reasons["parent-cycle"] += transcript.graph.looping()

    def _closure(self, transcript: _Transcript, reasons: Counter[str]) -> None:
        """Require a closed turn for every input, sidechains included."""
        main = [fact for fact in transcript.graph.chain if not fact.sidechain]
        inputs = [fact for fact in transcript.graph.chain if record_shape(fact) == INPUT_SHAPE]
        closed = self._closings(transcript, reasons)
        reasons["turn-open"] += bool(main) and record_shape(main[-1]) != self._profile.final_shape
        reasons["input-turn-open"] += sum(1 for fact in inputs if fact.uuid not in closed)
        self._tips(transcript, closed, reasons)
        self._inputs(transcript, inputs, reasons)

    def _closings(self, transcript: _Transcript, reasons: Counter[str]) -> dict[str | None, datetime | None]:
        """Check each final record's Stop summary; return when each closed input's turn closed.

        A final record closes the nearest input above it, and only when it
        follows a Stop summary carrying the pinned handlers. The instant kept
        for an input is its earliest final record's, or ``None`` when one of
        them carries no timestamp.
        """
        profile = self._profile
        closed: dict[str | None, datetime | None] = {}
        for fact in transcript.graph.chain:
            if record_shape(fact) != profile.final_shape:
                continue
            parent = transcript.graph.by_uuid.get(fact.parent)
            if parent is None or record_shape(parent) != profile.closing_shape or parent.handlers != profile.stop_handlers:
                reasons["turn-closed-differently"] += 1
                continue
            owner = transcript.graph.turn(fact)
            key = owner.uuid if owner is not None else None
            closed[key] = _earliest(closed.get(key, fact.timestamp), fact.timestamp)
        return closed

    def _tips(self, transcript: _Transcript, closed: dict[str | None, datetime | None], reasons: Counter[str]) -> None:
        """Count chain tips that are neither a final record nor a pinned leaf recorded before its turn closed.

        Sharing an input with a final record is not enough: the closing
        record must come last, so a pinned leaf needs an instant strictly
        before its turn's final record. An unknown or equal instant is pending.
        """
        profile = self._profile
        parents = {fact.parent for fact in transcript.graph.chain}
        for fact in transcript.graph.chain:
            shape = record_shape(fact)
            if fact.uuid in parents or shape == profile.final_shape:
                continue
            if shape not in profile.leaf_shapes:
                reasons["leaf-unclassified"] += 1
                continue
            owner = transcript.graph.turn(fact)
            if owner is None or owner.uuid not in closed:
                reasons["leaf-outside-closed-turn"] += 1
                continue
            ending = closed[owner.uuid]
            reasons["leaf-after-closing"] += fact.timestamp is None or ending is None or fact.timestamp >= ending

    def _inputs(self, transcript: _Transcript, inputs: list[RecordFact], reasons: Counter[str]) -> None:
        """Require each input to attach to a closed turn, one input per parent."""
        allowed = {self._profile.final_shape, *self._profile.input_parents}
        parents = [transcript.graph.by_uuid[fact.parent] for fact in inputs if fact.parent in transcript.graph.by_uuid]
        reasons["input-after-open-turn"] += sum(1 for parent in parents if record_shape(parent) not in allowed)
        reasons["input-branch"] += repeated(Counter(parent.uuid for parent in parents).values())


# eof
