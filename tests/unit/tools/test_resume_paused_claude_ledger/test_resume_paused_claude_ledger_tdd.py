"""Claude lifecycle ledger tests.

Step 1 of v0.15.0 resume-paused: absence is proved only from complete,
classified, closed and matched transcripts bound to the pane's session,
version and process generation.

Fix (code review round 1): one regression case per finding. R1: sidechain
inputs, inputs without an identifier, repeated identifiers and broken parent
links are pending. R2: a nonbound or pre-boot transcript of another version or
with unknown records is pending. R3: a terminal before its start, a deletion
before its creation, a reused identifier and an unrelated session's terminal
close nothing, while a clear continuation still does. R4: only a recognized
requestor operation after the proved marked input is excluded; watchers,
chained or wrapped commands, earlier starts, a wrong checkout, an unreported
session identity and a changed process binding stay pending.

Fix (code review round 2): one regression group per finding. R2-1: an input
without its own closed turn, a pinned leaf outside a closed turn and a looping
parent chain are pending. R2-2: a call identifier shared by two calls or two
results, and a result recorded above its call, are pending. R2-3: an end at
the start's own instant closes nothing, and an end in another file needs a
proved continuation into a clear-marked file, for tasks and schedules alike.
R2-4: a bound transcript without a recorded cwd, or with one outside the
checkout, is pending. R2-5: a multiline command and a longer launcher file name
keep their start in scope. R2-6: an unknown message block is pending in every
read, a schedule-only one included.

Fix (code review round 4): the unlinked call and result case gives its result
an object container, so it keeps its single linkage reason; the round 4
regressions live in ``test_resume_paused_claude_ledger_evidence_tdd.py``.

Fix (design Q28=A follow-up): the scopes carry a resolved ``BootDecision``
instead of a bare instant, so these cases keep their true-boot meaning; the
unresolved and pending boundaries are covered in
``test_resume_paused_claude_ledger_boot_tdd.py``.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from tests.unit.tools.resume_paused_test_support import (
    CHECKOUT,
    HOST_PID,
    SESSION_ID,
    FakeTranscriptSource,
    at,
    claude_profile,
    closed_turn,
    closing,
    filetime,
    jsonl,
    record,
    reply,
    resolved_boot,
    session_start,
    task_ended,
    tool_call,
    tool_result,
    typed,
)
from tools.resume_paused_claude import REQUESTOR_MARKERS
from tools.resume_paused_claude_ledger import (
    Absence,
    ClaudeLedger,
    LedgerDecision,
    LedgerScope,
)
from tools.resume_paused_profiles import (
    DISCLOSED_LIMITS,
    ProcessIdentity,
    ReadAccount,
    Reason,
)

BOUND = "bound.jsonl"
PROCESS = ProcessIdentity(HOST_PID, filetime(at(1)))
SCOPE = LedgerScope(checkout=CHECKOUT, boot_boundary=resolved_boot(0), bound_path=BOUND, session_id=SESSION_ID, process=PROCESS)
WATCHER = ("PowerShell", {"backgroundTaskId": "task1"})
MARKED = "/resume-session rp1:launch-1"
LAUNCHER = '& "C:\\tools\\bin\\review_exchange.bat"'
WAIT_ANSWER = f"{LAUNCHER} wait-answer --family code --document docs/plan.md"
MARKED_SCOPE = replace(SCOPE, marked_input=MARKED)
OLD = "old.jsonl"
CLEAR_SCOPE = replace(SCOPE, markers=REQUESTOR_MARKERS)
LINKED_SCOPE = replace(CLEAR_SCOPE, continuations=frozenset({(OLD, BOUND)}))
CLEARED = [
    session_start("s2", 45, "SessionStart:clear"), task_ended(50, "task1"),
    typed("in2", "s2", 51), reply("r2", "in2", 52), *closing("t2", "r2", 53),
]
FUTURE = record("user", message={"content": [{"type": "future_input", "text": "later work"}]})
LEAVES = frozenset({"assistant"})
Files = dict[str, list[dict[str, Any]] | bytes | None]


def decide(files: Files, scope: LedgerScope = SCOPE, rebind: ProcessIdentity | None = PROCESS, **profile: Any) -> LedgerDecision:  # noqa: ANN401
    """Evaluate declared transcripts; lists of records are rendered as JSONL."""
    data = {path: jsonl(value) if isinstance(value, list) else value for path, value in files.items()}
    return ClaudeLedger(claude_profile(**profile), FakeTranscriptSource(data), lambda: rebind).evaluate(scope)


def reasons(decision: LedgerDecision) -> dict[str, int]:
    """Return the counted reason codes of a decision."""
    return {reason.code: reason.count for reason in decision.reasons}


def wait_started(command: str, task: str = "wait1") -> list[dict[str, Any]]:
    """Build a marked-input turn whose single tool starts a background task."""
    return closed_turn(("PowerShell", {"backgroundTaskId": task}, command), text=MARKED)


def without_cwd(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop the recorded cwd of every record."""
    return [{key: value for key, value in item.items() if key != "cwd"} for item in records]


def side(uuid: str, parent: str | None, seconds: int = 50) -> dict[str, Any]:
    """Build a sidechain assistant reply."""
    return dict(reply(uuid, parent, seconds), isSidechain=True)


def test_closed_session_without_tasks_proves_absence() -> None:
    """A complete, closed, bound transcript with no start proves absence."""
    data = jsonl(closed_turn())

    decision = decide({BOUND: data})

    assert decision.absence is Absence.PROVED
    assert decision.reasons == ()
    assert decision.account == ReadAccount(files=1, bytes_read=len(data))
    assert decision.limits == DISCLOSED_LIMITS


def test_running_watcher_keeps_absence_pending() -> None:
    """A background start without its terminal record is pending."""
    decision = decide({BOUND: closed_turn(WATCHER)})

    assert decision.absence is Absence.PENDING
    assert decision.reasons == (Reason("background-start-unmatched"),)


@pytest.mark.parametrize("status", ["completed", "failed", "killed"])
def test_completed_watcher_proves_absence(status: str) -> None:
    """A later terminal enqueue with the same task id closes the start."""
    assert decide({BOUND: [*closed_turn(WATCHER), task_ended(50, "task1", status)]}).absence is Absence.PROVED


def test_non_terminal_status_or_other_task_does_not_close_a_start() -> None:
    """A running status or another task's terminal record leaves the start open."""
    running = decide({BOUND: [*closed_turn(WATCHER), task_ended(50, "task1", "running")]})
    other = decide({BOUND: [*closed_turn(WATCHER), task_ended(50, "task2")]})

    assert reasons(running) == {"background-start-unmatched": 1}
    assert reasons(other) == {"background-start-unmatched": 1}


def test_terminal_before_its_start_or_without_an_instant_closes_nothing() -> None:
    """A terminal recorded earlier than the start, or with no instant, is not its end."""
    earlier = [*closed_turn(WATCHER)[:2], task_ended(8, "task1"), *closed_turn(WATCHER)[2:]]
    undated = [*closed_turn(WATCHER), record("queue-operation", operation="enqueue", taskId="task1", status="completed")]

    assert reasons(decide({BOUND: earlier})) == {"background-start-unmatched": 1}
    assert reasons(decide({BOUND: undated})) == {"background-start-unmatched": 1}


def test_reused_task_identifier_stays_pending_even_with_terminals() -> None:
    """Two starts sharing an identifier cannot be told apart, so neither is closed."""
    twice = closed_turn(WATCHER, WATCHER)

    decision = decide({BOUND: [*twice, task_ended(50, "task1"), task_ended(51, "task1")]})

    assert reasons(decision) == {"background-start-unmatched": 2, "task-id-reused": 1}


def test_monitor_task_start_needs_its_terminal_record() -> None:
    """A Monitor start is recorded by ``taskId`` and matched the same way."""
    monitor = ("PowerShell", {"taskId": "mon1", "timeoutMs": 1000, "persistent": False})

    assert reasons(decide({BOUND: closed_turn(monitor)})) == {"background-start-unmatched": 1}
    assert decide({BOUND: [*closed_turn(monitor), task_ended(50, "mon1")]}).absence is Absence.PROVED


def test_terminal_record_in_a_later_file_closes_a_start_after_a_proved_clear() -> None:
    """A start before a clear is matched in the cleared file when the continuation is proved."""
    decision = decide({OLD: closed_turn(WATCHER), BOUND: CLEARED}, LINKED_SCOPE)

    assert decision.absence is Absence.PROVED
    assert decision.account.files == 2  # noqa: PLR2004


def test_clear_marker_alone_continues_no_other_file() -> None:
    """Another root's cleared file, a reversed pair and a startup-marked file close nothing."""
    files: Files = {OLD: closed_turn(WATCHER), BOUND: CLEARED}
    reverse = replace(CLEAR_SCOPE, continuations=frozenset({(BOUND, OLD)}))
    startup: Files = {OLD: closed_turn(WATCHER), BOUND: [*closed_turn(), task_ended(50, "task1")]}

    assert reasons(decide(files, CLEAR_SCOPE)) == {"background-start-unmatched": 1}
    assert reasons(decide(files, reverse)) == {"background-start-unmatched": 1}
    assert reasons(decide(startup, replace(LINKED_SCOPE, markers=SCOPE.markers))) == {"background-start-unmatched": 1}


def test_schedule_deleted_in_another_file_needs_a_proved_clear() -> None:
    """A deletion in a cleared file resolves an earlier file's schedule only with a proved continuation."""
    deleted = [session_start(hook="SessionStart:clear"), *closed_turn(("PowerShell", {}), ("CronDelete", {"id": "job1"}))[2:]]
    files: Files = {OLD: closed_turn(("CronCreate", {"id": "job1"})), BOUND: deleted}

    assert reasons(decide(files, CLEAR_SCOPE)) == {"schedule-unresolved": 1}
    assert decide(files, LINKED_SCOPE).absence is Absence.PROVED


def test_continuation_chain_across_two_clears_closes_the_first_start() -> None:
    """Two proved clears in a row carry a start to the terminal record in the last file."""
    middle = [session_start("s1", 43, "SessionStart:clear"), typed("m", "s1", 44), reply("mr", "m", 44), *closing("tm", "mr", 44)]
    chained = replace(CLEAR_SCOPE, continuations=frozenset({(OLD, "mid.jsonl"), ("mid.jsonl", BOUND)}))

    decision = decide({OLD: closed_turn(WATCHER), "mid.jsonl": middle, BOUND: CLEARED}, chained)

    assert decision.absence is Absence.PROVED


def test_end_at_the_same_instant_as_its_start_closes_nothing() -> None:
    """An equal timestamp orders nothing: the start stays open."""
    assert reasons(decide({BOUND: [*closed_turn(WATCHER), task_ended(21, "task1")]})) == {"background-start-unmatched": 1}


def test_terminal_in_an_unrelated_session_file_closes_nothing() -> None:
    """Without a clear continuation, another file's terminal is not this start's end."""
    decision = decide({"other.jsonl": closed_turn(WATCHER), BOUND: [*closed_turn(), task_ended(50, "task1")]})

    assert reasons(decision) == {"background-start-unmatched": 1}


def test_restart_does_not_end_an_earlier_generation_watcher() -> None:
    """An unmatched start in another session file stays pending after a restart."""
    decision = decide({"earlier.jsonl": closed_turn(WATCHER), BOUND: closed_turn()})

    assert reasons(decision) == {"background-start-unmatched": 1}


def test_transcript_before_boot_is_read_for_schedules_only() -> None:
    """A true boot bounds old task starts but never discards a schedule."""
    old = closed_turn(WATCHER, ("CronCreate", {"id": "job1"}))
    source = FakeTranscriptSource({"old.jsonl": jsonl(old), BOUND: jsonl(closed_turn())}, {"old.jsonl": at(0)})
    scope = replace(SCOPE, boot_boundary=resolved_boot(30))

    durable = ClaudeLedger(claude_profile(), source, lambda: PROCESS).evaluate(scope)
    session_only = ClaudeLedger(claude_profile(durable_schedules=False), source, lambda: PROCESS).evaluate(scope)

    assert reasons(durable) == {"schedule-unresolved": 1}
    assert durable.account.files == 2  # noqa: PLR2004
    assert session_only.absence is Absence.PROVED
    assert session_only.account.files == 1


@pytest.mark.parametrize(
    ("old", "expected"),
    [
        ([dict(item, version="2.1.200") for item in closed_turn()], {"version-unpinned": 1}),
        ([*closed_turn(), record("durable-schedule")], {"record-unclassified": 1}),
        (closed_turn(("ScheduleWakeup", {"id": "job9"})), {"tool-unclassified": 1}),
        ([*closed_turn(), FUTURE], {"content-unclassified": 1}),
        (jsonl(closed_turn())[:-1], {"transcript-incomplete": 1}),
    ],
)
def test_pre_boot_transcript_must_still_be_classified(old: list[dict[str, Any]] | bytes, expected: dict[str, int]) -> None:
    """A schedule-only read of another version or with unknown records proves nothing."""
    data = old if isinstance(old, bytes) else jsonl(old)
    source = FakeTranscriptSource({"old.jsonl": data, BOUND: jsonl(closed_turn())}, {"old.jsonl": at(0)})

    decision = ClaudeLedger(claude_profile(), source, lambda: PROCESS).evaluate(replace(SCOPE, boot_boundary=resolved_boot(30)))

    assert reasons(decision) == expected


def test_nonbound_transcript_of_another_version_is_pending() -> None:
    """Every contributing transcript needs the pinned version, not only the bound one."""
    other = [dict(item, version="2.1.326") for item in closed_turn()]

    assert reasons(decide({"other.jsonl": other, BOUND: closed_turn()})) == {"version-unpinned": 1}


def test_deleted_schedule_proves_absence_only_when_deleted_after_creation() -> None:
    """A creation is resolved by its own later deletion, never by an earlier one."""
    created = ("CronCreate", {"id": "job1", "recurring": False})
    deleted = ("CronDelete", {"id": "job1"})

    assert reasons(decide({BOUND: closed_turn(created)})) == {"schedule-unresolved": 1}
    assert decide({BOUND: closed_turn(created, deleted)}).absence is Absence.PROVED
    assert reasons(decide({BOUND: closed_turn(deleted, created)})) == {"schedule-unresolved": 1}
    assert reasons(decide({BOUND: closed_turn(created, created, deleted)})) == {"schedule-id-reused": 1, "schedule-unresolved": 2}


def test_other_checkout_transcript_is_excluded_only_on_recorded_cwd() -> None:
    """Recorded cwd outside the checkout excludes a file; a subdirectory stays in scope."""
    def elsewhere(cwd: str) -> list[dict[str, Any]]:
        return [dict(item, cwd=cwd) for item in closed_turn(WATCHER)]

    outside = decide({"x.jsonl": elsewhere("C:/work/checkout2"), BOUND: closed_turn()})
    inside = decide({"x.jsonl": elsewhere("C:\\Work\\Checkout\\sub\\"), BOUND: closed_turn()})

    assert outside.absence is Absence.PROVED
    assert outside.account.files == 2  # noqa: PLR2004
    assert reasons(inside) == {"background-start-unmatched": 1}


def test_bound_transcript_of_another_checkout_is_pending() -> None:
    """The pane's own transcript must record this checkout."""
    foreign = [dict(item, cwd="C:/work/elsewhere") for item in closed_turn()]

    assert reasons(decide({BOUND: foreign})) == {"bound-transcript-other-checkout": 1}


def test_bound_transcript_needs_positive_checkout_evidence() -> None:
    """No recorded cwd, one outside the checkout or a malformed one proves no binding."""
    mixed = [*closed_turn(), record("mode", cwd="C:/work/elsewhere")]
    malformed = [*closed_turn(), record("mode", cwd=7)]

    assert reasons(decide({BOUND: without_cwd(closed_turn())})) == {"bound-transcript-checkout-unproved": 1}
    assert reasons(decide({BOUND: mixed})) == {"bound-transcript-checkout-unproved": 1}
    assert reasons(decide({BOUND: malformed})) == {"record-invalid": 1}


def test_nonbound_transcript_without_checkout_evidence_stays_in_scope() -> None:
    """A file that cannot be placed outside the checkout keeps its starts in scope."""
    decision = decide({"x.jsonl": without_cwd(closed_turn(WATCHER)), BOUND: closed_turn()})

    assert reasons(decision) == {"background-start-unmatched": 1}


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ([record("mode", sessionId="another-session")], {"session-mismatch": 1}),
        ([record("mode", version="2.1.326")], {"version-unpinned": 1}),
        ([record("attachment", None, None, 60, attachment={"type": "hook_success", "hookName": "SessionStart:resume"})], {"generation-restarted": 1}),
        ([record("attachment", None, None, 60, attachment={"type": "hook_success", "hookName": "SessionStart:compact"})], {}),
        ([record("attachment", None, None, 60, attachment={"type": "hook_success", "hookName": "PreToolUse:PowerShell"})], {}),
    ],
)
def test_bound_transcript_generation_binding(change: list[dict[str, Any]], expected: dict[str, int]) -> None:
    """Session, version and any later noncompact SessionStart bind the generation."""
    assert reasons(decide({BOUND: closed_turn() + change})) == expected


def test_generation_marker_must_be_the_first_timestamped_record() -> None:
    """A transcript whose first timestamped record is not the marker is pending."""
    without_marker = [item for item in closed_turn() if item.get("uuid") != "start"]

    assert reasons(decide({BOUND: without_marker})) == {"generation-marker-missing": 1, "parent-missing": 1}
    assert reasons(decide({BOUND: [record("mode")]})) == {"generation-marker-missing": 1}


def test_generation_marker_must_follow_process_creation() -> None:
    """A marker timestamped before the pane's Claude child was created is pending."""
    late = ProcessIdentity(HOST_PID, filetime(at(6)))
    exact = ProcessIdentity(HOST_PID, filetime(at(5)))

    assert reasons(decide({BOUND: closed_turn()}, replace(SCOPE, process=late), late)) == {"generation-marker-before-process": 1}
    assert decide({BOUND: closed_turn()}, replace(SCOPE, process=exact), exact).absence is Absence.PROVED


def test_clear_marker_is_accepted_only_for_the_requestor_binding() -> None:
    """A clear marker binds the requestor file but not the reviewer's generation."""
    cleared = [session_start(hook="SessionStart:clear"), *closed_turn()[2:]]

    assert decide({BOUND: cleared}, replace(SCOPE, markers=REQUESTOR_MARKERS)).absence is Absence.PROVED
    assert reasons(decide({BOUND: cleared})) == {"generation-marker-missing": 1}


def test_changed_process_binding_or_unreported_identity_is_pending() -> None:
    """A different process after the read, or a session id not from a report, proves nothing."""
    replaced = ProcessIdentity(HOST_PID + 1, PROCESS.created_at)

    assert reasons(decide({BOUND: closed_turn()}, rebind=replaced)) == {"process-binding-changed": 1}
    assert reasons(decide({BOUND: closed_turn()}, rebind=None)) == {"process-binding-changed": 1}
    assert reasons(decide({BOUND: closed_turn()}, replace(SCOPE, identity_source="inferred"))) == {"session-identity-unreported": 1}


@pytest.mark.parametrize(
    ("records", "expected"),
    [
        ([*closed_turn(), record("telemetry")], {"record-unclassified": 1}),
        ([*closed_turn(), record("attachment", attachment={"type": "task_status"})], {"attachment-unclassified": 1}),
        (closed_turn(("Bash", {})), {"tool-unclassified": 1}),
        ([*closed_turn(), FUTURE], {"content-unclassified": 1}),
        ([*closed_turn(), record("user", message="text")], {"record-invalid": 1}),
        (
            [item for item in closed_turn(("PowerShell", {})) if item.get("uuid") != "res0"],
            {"input-turn-open": 1, "leaf-unclassified": 1, "parent-missing": 1, "tool-call-open": 1},
        ),
        (
            [item for item in closed_turn(("PowerShell", {})) if item.get("uuid") != "call0"],
            {"input-turn-open": 1, "leaf-unclassified": 1, "parent-missing": 1, "tool-result-orphan": 1},
        ),
    ],
)
def test_closed_world_classification(records: list[dict[str, Any]], expected: dict[str, int]) -> None:
    """Unknown records, attachments, blocks and tools, open calls and orphan results are pending.

    A missing result or call record also breaks its neighbour's parent link,
    leaves a stray chain tip and cuts the final record off from its input.
    """
    assert reasons(decide({BOUND: records})) == expected


def shared_call_identifier() -> list[dict[str, Any]]:
    """Build two calls sharing one identifier, answered by a single result."""
    swapped: dict[str | None, dict[str, Any]] = {"call1": tool_call("call1", "res0", 22, "c0"), "reply": reply("reply", "call1", 40)}
    records = closed_turn(("PowerShell", {}), ("PowerShell", {}))
    return [swapped.get(item.get("uuid"), item) for item in records if item.get("uuid") != "res1"]


def result_before_its_call() -> list[dict[str, Any]]:
    """Build a result recorded above the call it names."""
    return [
        *closed_turn()[:3], tool_result("res0", "in", 20, "c0"), tool_call("call0", "res0", 21, "c0"),
        reply("reply", "call0", 40), *closing("t1", "reply", 41),
    ]


def repeated_result() -> list[dict[str, Any]]:
    """Build one call answered by two results, the second a leaf of the closed turn."""
    records = closed_turn(("PowerShell", {}))
    return [*records[:-3], tool_result("again", "res0", 22, "c0"), *records[-3:]]


def unidentified_call_and_result() -> list[dict[str, Any]]:
    """Build a call and its result on records without identifiers."""
    call = record("assistant", None, None, 50, message={"content": [{"type": "tool_use", "id": "c9", "name": "PowerShell"}]})
    answer = record("user", None, None, 51, message={"content": [{"type": "tool_result", "tool_use_id": "c9"}]}, toolUseResult={})
    return [*closed_turn(), call, answer]


@pytest.mark.parametrize(
    ("records", "expected"),
    [
        (shared_call_identifier(), {"tool-call-duplicate": 1}),
        (result_before_its_call(), {"tool-result-unlinked": 1}),
        (repeated_result(), {"tool-result-duplicate": 1}),
        (unidentified_call_and_result(), {"tool-result-unlinked": 1}),
    ],
)
def test_each_call_needs_its_own_result_below_it(records: list[dict[str, Any]], expected: dict[str, int]) -> None:
    """A shared identifier, an earlier result and an unlinked pair never close a call."""
    assert reasons(decide({BOUND: records}, leaf_shapes=frozenset({"tool-result"}))) == expected


@pytest.mark.parametrize(
    ("records", "expected"),
    [
        (closed_turn()[:-2], {"input-turn-open": 1, "leaf-unclassified": 1, "turn-open": 1}),
        (
            [*closed_turn(), typed("in2", "t1-end", 50), reply("r2", "in2", 51), record("system", "end2", "r2", 52, subtype="turn_duration")],
            {"input-turn-open": 1, "turn-closed-differently": 1},
        ),
        ([*closed_turn()[:-2], *closing("t1", "reply", 41, "another stop command")], {"input-turn-open": 1, "turn-closed-differently": 1}),
        ([*closed_turn(), typed("in2", "reply", 50), reply("r2", "in2", 51), *closing("t2", "r2", 52)], {"input-after-open-turn": 1}),
        (
            [*closed_turn(), typed("in2", "t1-end", 50), reply("r2", "in2", 51), *closing("t2", "r2", 52),
             typed("in3", "t1-end", 53), reply("r3", "in3", 54), *closing("t3", "r3", 55)],
            {"input-branch": 1},
        ),
        ([*closed_turn()[:-2], reply("stray", "in", 40), *closing("t1", "reply", 41)], {"leaf-unclassified": 1}),
    ],
)
def test_turn_closure(records: list[dict[str, Any]], expected: dict[str, int]) -> None:
    """Open turns, foreign closures, branched or misplaced inputs and stray tips are pending."""
    assert reasons(decide({BOUND: records})) == expected


@pytest.mark.parametrize(
    ("extra", "expected"),
    [
        ([dict(typed("nested", "t1-end", 50), isSidechain=True)], {"input-turn-open": 1, "leaf-unclassified": 1}),
        ([dict(typed("nested", None, 50), isSidechain=True), side("side", "nested", 51)], {"input-turn-open": 1, "leaf-unclassified": 1}),
        ([record("user", None, None, 50, message={"content": "typed without an identifier"})], {"input-without-uuid": 1}),
        ([reply("reply", "in", 40)], {"turn-open": 1, "uuid-duplicate": 1}),
        ([typed("in2", "ghost", 50), reply("r2", "in2", 51), *closing("t2", "r2", 52)], {"parent-missing": 1}),
    ],
)
def test_every_input_and_chain_tip_is_checked(extra: list[dict[str, Any]], expected: dict[str, int]) -> None:
    """Sidechain work, unidentified inputs, repeated identifiers and broken links are pending."""
    assert reasons(decide({BOUND: [*closed_turn(), *extra]})) == expected


def test_only_pinned_leaf_shapes_may_end_a_chain() -> None:
    """A fan-out leaf proves nothing unless the profile validated its shape."""
    stray = [*closed_turn()[:-2], reply("stray", "in", 40), *closing("t1", "reply", 41)]

    assert reasons(decide({BOUND: stray})) == {"leaf-unclassified": 1}
    assert reasons(decide({BOUND: [*closed_turn(), side("side", None)]})) == {"leaf-unclassified": 1}
    assert decide({BOUND: stray}, leaf_shapes=LEAVES).absence is Absence.PROVED


@pytest.mark.parametrize(
    ("extra", "expected"),
    [
        ([dict(typed("nested", None, 50), isSidechain=True), side("side", "nested", 51)], {"input-turn-open": 1, "leaf-outside-closed-turn": 1}),
        ([side("side", None)], {"leaf-outside-closed-turn": 1}),
        ([side("loop", "loop")], {"parent-cycle": 1}),
        ([side("a", "b"), side("b", "a")], {"parent-cycle": 2}),
        ([side("a", "b"), side("b", "a"), side("c", "a")], {"leaf-outside-closed-turn": 1, "parent-cycle": 3}),
    ],
)
def test_pinned_leaf_needs_a_closed_turn_and_an_acyclic_graph(extra: list[dict[str, Any]], expected: dict[str, int]) -> None:
    """With the leaf shape pinned, an open sidechain turn, a leaf under no input and a parent loop stay pending."""
    assert reasons(decide({BOUND: [*closed_turn(), *extra]}, leaf_shapes=LEAVES)) == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (jsonl(closed_turn())[:-1], {"transcript-incomplete": 1}),
        (b"", {"transcript-incomplete": 1}),
        (jsonl(closed_turn()) + b"{truncated\n", {"record-invalid": 1}),
        (jsonl([*closed_turn(), record("mode", None, None, None, timestamp="not-a-time")]), {"record-invalid": 1}),
        (jsonl([*closed_turn(), record("mode", None, None, None, timestamp="2026-11-14T10:00:05")]), {"record-invalid": 1}),
        (None, {"read-failed": 1}),
        (jsonl(closed_turn()) + b"3\n\n", {"record-unclassified": 1}),
    ],
)
def test_incomplete_or_damaged_transcript_is_pending(data: bytes | None, expected: dict[str, int]) -> None:
    """A truncated, unparsable or unreadable transcript never proves absence."""
    assert reasons(decide({BOUND: data})) == expected


def test_incomplete_enumeration_and_missing_bound_transcript_are_pending() -> None:
    """Without a complete listing or the pane's own transcript nothing is proved."""
    unlisted = ClaudeLedger(claude_profile(), FakeTranscriptSource({}, complete=False), lambda: PROCESS).evaluate(SCOPE)

    assert unlisted.reasons == (Reason("enumeration-incomplete"),)
    assert unlisted.account == ReadAccount()
    assert reasons(decide({"other.jsonl": closed_turn()})) == {"bound-transcript-missing": 1}


def test_requestor_wait_answer_after_the_marked_input_is_excluded() -> None:
    """A recognized requestor operation started after the marked resume input does not block."""
    decision = decide({BOUND: wait_started(WAIT_ANSWER)}, MARKED_SCOPE)

    assert decision.absence is Absence.PROVED
    assert reasons(decide({BOUND: wait_started(WAIT_ANSWER)})) == {"background-start-unmatched": 1}


@pytest.mark.parametrize(
    "command",
    [
        f"{LAUNCHER} wait-any-request",
        f'{WAIT_ANSWER}; "wait=$LASTEXITCODE"',
        f"{WAIT_ANSWER} | Out-File a.log",
        'cmd /c "C:\\tools\\bin\\review_exchange.bat wait-answer"',
        f"{LAUNCHER} status --family code",
        "Start-Sleep 600",
        f"{WAIT_ANSWER}\nStart-Sleep 600",
        f"{WAIT_ANSWER}\r\nStart-Sleep 600",
        '& "C:\\tools\\bin\\not_review_exchange.bat" wait-answer --family code',
    ],
)
def test_watchers_and_unrecognized_commands_stay_in_scope(command: str) -> None:
    """A reviewer watcher, a chained, piped, wrapped or multiline command and other work still block."""
    assert reasons(decide({BOUND: wait_started(command)}, MARKED_SCOPE)) == {"background-start-unmatched": 1}


def test_start_before_the_marked_input_stays_in_scope() -> None:
    """Creation order comes from the parent chain: an earlier wait is not excluded."""
    earlier = closed_turn(("PowerShell", {"backgroundTaskId": "wait0"}, WAIT_ANSWER))
    resumed = [*earlier, typed("in2", "t1-end", 50, MARKED), reply("r2", "in2", 51), *closing("t2", "r2", 52)]

    assert reasons(decide({BOUND: resumed}, MARKED_SCOPE)) == {"background-start-unmatched": 1}


def test_unproved_marked_input_excludes_nothing() -> None:
    """A missing, repeated or untyped marked input leaves every start in scope."""
    missing = closed_turn(("PowerShell", {"backgroundTaskId": "wait1"}, WAIT_ANSWER))
    repeated = [*wait_started(WAIT_ANSWER), typed("in2", "t1-end", 50, MARKED), reply("r2", "in2", 51), *closing("t2", "r2", 52)]
    untyped = [dict(item, promptSource="system") if item.get("uuid") == "in" else item for item in wait_started(WAIT_ANSWER)]

    for records in (missing, repeated, untyped):
        assert reasons(decide({BOUND: records}, MARKED_SCOPE)) == {"background-start-unmatched": 1, "marked-input-unproved": 1}


# eof
