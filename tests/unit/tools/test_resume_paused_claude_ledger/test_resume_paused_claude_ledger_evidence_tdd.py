"""Claude lifecycle ledger evidence-completeness tests.

Step 1 of v0.15.0 resume-paused (code review round 4): one regression group
per finding. R4-1: every transcript read since boot needs a complete
generation, not only the bound one. Another writer's transcript without a
first marker, opened by a resume marker or restarted later is pending; a clear
marker counts there only with a proved continuation; the bound process
creation never applies to it. R4-2: a malformed task identifier, a plain or
absent result container and a schedule creation without its identifier are
pending, never absence, while a recorded error and a validated plain tool stay
classified.

Fix (code review round 5, R5-1): a cleared file whose proved predecessor is
absent, or whose ancestor is absent further up a chain of clears, is pending;
so is a predecessor excluded as another checkout's transcript. An unreadable or
incomplete predecessor stays pending under its own read reason, a predecessor
older than boot stays under the boot rule, and a complete chain proves absence.

Fix (design Q28=A follow-up): the boot rule needs a resolved ``BootDecision``;
the predecessor case now states one.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from tests.unit.tools.resume_paused_test_support import (
    FakeTranscriptSource,
    at,
    claude_profile,
    closed_turn,
    closing,
    jsonl,
    record,
    reply,
    resolved_boot,
    session_start,
    typed,
)
from tests.unit.tools.test_resume_paused_claude_ledger.test_resume_paused_claude_ledger_tdd import (
    BOUND,
    CLEARED,
    OLD,
    PROCESS,
    SCOPE,
    WATCHER,
    Files,
    decide,
    reasons,
)
from tools.resume_paused_claude_ledger import Absence, ClaudeLedger

OTHER = "other.jsonl"
MID = "mid.jsonl"
MISSING = {"generation-marker-missing": 1}
PREDECESSOR = {"continuation-predecessor-missing": 1}
LINKED = replace(SCOPE, continuations=frozenset({(OLD, OTHER)}))
CHAIN = replace(SCOPE, continuations=frozenset({(OLD, MID), (MID, OTHER)}))
UNCLASSIFIED = {"result-unclassified": 1}
UNMARKED = [record("mode"), typed("in", None, 10), reply("reply", "in", 40), *closing("t1", "reply", 41)]


def _changed(item: dict[str, Any], fields: dict[str, Any]) -> dict[str, Any]:
    """Merge declared fields into one record; a ``None`` field is removed."""
    return {key: value for key, value in {**item, **fields}.items() if value is not None}


def altered(records: list[dict[str, Any]], uuid: str, **fields: Any) -> list[dict[str, Any]]:  # noqa: ANN401
    """Return the records with the one carrying ``uuid`` changed."""
    return [_changed(item, fields) if item.get("uuid") == uuid else item for item in records]


def failed(records: list[dict[str, Any]], uuid: str, call: str) -> list[dict[str, Any]]:
    """Flag the result record ``uuid`` answering ``call`` as a recorded error."""
    return altered(records, uuid, message={"content": [{"type": "tool_result", "tool_use_id": call, "is_error": True}]})


def restarted(hook: str) -> list[dict[str, Any]]:
    """Build a closed session that a later SessionStart reopens for a second closed turn."""
    return [*closed_turn(), session_start("s2", 45, hook), typed("in2", "s2", 46), reply("r2", "in2", 47), *closing("t2", "r2", 48)]


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        (altered(closed_turn(), "start", attachment={"type": "hook_success", "hookName": "SessionStart:resume"}), MISSING),
        (UNMARKED, MISSING),
        (CLEARED, MISSING),
        (restarted("SessionStart:resume"), {"generation-restarted": 1}),
        (restarted("SessionStart:startup"), {"generation-restarted": 1}),
    ],
)
def test_other_writer_without_a_complete_generation_is_pending(other: list[dict[str, Any]], expected: dict[str, int]) -> None:
    """A nonbound transcript resumed, unmarked, opened by an unproved clear or restarted later is pending."""
    assert reasons(decide({BOUND: closed_turn(), OTHER: other})) == expected


@pytest.mark.parametrize(
    "other",
    [closed_turn(), restarted("SessionStart:compact"), altered(closed_turn(), "start", timestamp=at(0).isoformat())],
)
def test_complete_other_writer_proves_absence(other: list[dict[str, Any]]) -> None:
    """A startup-opened nonbound transcript proves, compacted or not, even when it starts before the bound process."""
    assert decide({BOUND: closed_turn(), OTHER: other}).absence is Absence.PROVED


def test_clear_opened_writer_needs_a_proved_continuation() -> None:
    """A nonbound file opened by a clear is complete only as the later file of a proved continuation."""
    files: Files = {OLD: closed_turn(), OTHER: CLEARED, BOUND: closed_turn()}

    assert reasons(decide(files)) == MISSING
    assert decide(files, LINKED).absence is Absence.PROVED


def test_cleared_writer_with_an_absent_predecessor_is_pending() -> None:
    """A proved continuation names its earlier file; that file missing from the enumeration is lost history."""
    assert reasons(decide({BOUND: closed_turn(), OTHER: CLEARED}, LINKED)) == PREDECESSOR


def test_missing_ancestor_through_successive_clears_is_pending() -> None:
    """Every link of a chain of clears needs its earlier file; the complete chain proves absence."""
    files: Files = {MID: CLEARED, OTHER: CLEARED, BOUND: closed_turn()}

    assert reasons(decide(files, CHAIN)) == PREDECESSOR
    assert decide({OLD: closed_turn(), **files}, CHAIN).absence is Absence.PROVED


@pytest.mark.parametrize(
    ("earlier", "expected"),
    [
        (None, {"read-failed": 1}),
        (jsonl(closed_turn())[:-1], {"transcript-incomplete": 1}),
        ([dict(item, cwd="C:/elsewhere") for item in closed_turn()], PREDECESSOR),
    ],
)
def test_unreadable_incomplete_or_foreign_predecessor_is_pending(earlier: list[dict[str, Any]] | bytes | None, expected: dict[str, int]) -> None:
    """An unreadable or incomplete earlier file keeps its read reason; one from another checkout is missing history."""
    assert reasons(decide({OLD: earlier, OTHER: CLEARED, BOUND: closed_turn()}, LINKED)) == expected


def test_predecessor_before_boot_stays_under_the_boot_rule() -> None:
    """A listed earlier file older than a resolved boot boundary is bounded by boot, not reported missing."""
    files: dict[str, bytes | None] = {OLD: jsonl(closed_turn(WATCHER)), OTHER: jsonl(CLEARED), BOUND: jsonl(closed_turn())}
    scope = replace(LINKED, boot_boundary=resolved_boot(30))

    decision = ClaudeLedger(claude_profile(), FakeTranscriptSource(files, {OLD: at(0)}), lambda: PROCESS).evaluate(scope)

    assert decision.absence is Absence.PROVED


@pytest.mark.parametrize("result", [{"backgroundTaskId": 7}, {"backgroundTaskId": ""}, {"taskId": 7}, {"taskId": ["wait1"]}])
def test_malformed_task_identifier_is_pending_never_erased(result: dict[str, Any]) -> None:
    """A supplied task id of the wrong type, or an empty one, rejects the transcript instead of hiding its start."""
    assert reasons(decide({BOUND: closed_turn(("PowerShell", result))})) == {"record-invalid": 1}


@pytest.mark.parametrize("result", [{"id": 7}, {"id": ""}, {"id": None}, {}])
def test_schedule_creation_without_its_identifier_is_unrecognized(result: dict[str, Any]) -> None:
    """A creation result without a nonempty string id is unrecognized, never read as no schedule."""
    assert reasons(decide({BOUND: closed_turn(("CronCreate", result))})) == {"schedule-result-unrecognized": 1}


@pytest.mark.parametrize("container", ["started in background", ["block"], 7, None])
def test_plain_or_absent_result_container_is_unclassified(container: object) -> None:
    """A result whose container is not an object, or is absent, may hide a start: it is pending."""
    records = altered(closed_turn(("PowerShell", {})), "res0", toolUseResult=container)

    assert reasons(decide({BOUND: records})) == UNCLASSIFIED


def test_recorded_error_or_validated_plain_tool_stays_classified() -> None:
    """A plain result flagged as an error, or from a tool validated to return one, proves absence."""
    plain = altered(closed_turn(("PowerShell", {})), "res0", toolUseResult="Error: denied")

    assert decide({BOUND: failed(plain, "res0", "c0")}).absence is Absence.PROVED
    assert decide({BOUND: plain}, plain_result_tools=frozenset({"PowerShell"})).absence is Absence.PROVED
    assert reasons(decide({BOUND: plain}, plain_result_tools=frozenset({"CronCreate"}))) == UNCLASSIFIED


def test_recorded_error_creates_and_deletes_no_schedule() -> None:
    """A failed creation leaves nothing to resolve, and a failed deletion resolves nothing."""
    created = closed_turn(("CronCreate", {}))
    deleted = closed_turn(("CronCreate", {"id": "job1"}), ("CronDelete", {"id": "job1"}))

    assert decide({BOUND: failed(created, "res0", "c0")}).absence is Absence.PROVED
    assert reasons(decide({BOUND: failed(deleted, "res1", "c1")})) == {"schedule-unresolved": 1}


# eof
