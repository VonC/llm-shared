"""Claude lifecycle ledger ordering tests.

Step 1 of v0.15.0 resume-paused (code review round 3): one regression group
per finding. R3-1: the requestor exception covers one start record, so an
earlier or later start sharing its task id stays pending, with or without a
terminal record. R3-2: a pinned leaf recorded at or after its turn's final
record, or without an instant, is pending, while a leaf recorded before it
still proves. R3-3: a branching or looping continuation link closes nothing.

Fix (design Q28=A follow-up): ``continuation_places`` moved to
``tools.resume_paused_claude_generation``, and its two direct R3-3 cases (one
place per file along a long chain, nothing placed for a branch or a loop)
moved to ``test_resume_paused_claude_generation_tdd.py``.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from tests.unit.tools.resume_paused_test_support import (
    closed_turn,
    closing,
    reply,
    task_ended,
    tool_call,
    tool_result,
    typed,
)
from tests.unit.tools.test_resume_paused_claude_ledger.test_resume_paused_claude_ledger_tdd import (
    BOUND,
    CLEAR_SCOPE,
    CLEARED,
    LEAVES,
    MARKED,
    MARKED_SCOPE,
    OLD,
    WAIT_ANSWER,
    WATCHER,
    Files,
    decide,
    reasons,
    side,
)
from tools.resume_paused_claude_ledger import Absence

SHARED = {"backgroundTaskId": "wait1"}
REUSED = {"background-start-unmatched": 1, "task-id-reused": 1}


def later_start_sharing_the_exempt_id() -> list[dict[str, Any]]:
    """Build an ordinary start and a requestor wait sharing one task id, both after the marked input."""
    return closed_turn(("PowerShell", SHARED), ("PowerShell", SHARED, WAIT_ANSWER), text=MARKED)


def earlier_start_sharing_the_exempt_id() -> list[dict[str, Any]]:
    """Build an ordinary start before the marked input and a requestor wait after it, sharing one task id."""
    return [
        *closed_turn(("PowerShell", SHARED)), typed("in2", "t1-end", 50, MARKED),
        tool_call("call9", "in2", 51, "c9", "PowerShell", WAIT_ANSWER), tool_result("res9", "call9", 52, "c9", **SHARED),
        reply("r2", "res9", 53), *closing("t2", "r2", 54),
    ]


@pytest.mark.parametrize("records", [later_start_sharing_the_exempt_id(), earlier_start_sharing_the_exempt_id()])
def test_requestor_exception_covers_one_start_record_not_its_task_id(records: list[dict[str, Any]]) -> None:
    """Another start sharing the covered start's task id stays pending, with or without a terminal record."""
    assert reasons(decide({BOUND: records}, MARKED_SCOPE)) == REUSED
    assert reasons(decide({BOUND: [*records, task_ended(60, "wait1")]}, MARKED_SCOPE)) == REUSED


@pytest.mark.parametrize(
    "extra",
    [
        [side("late", "in", 50)],
        [side("late", "reply", 50)],
        [side("early", "in", 30), side("late", "early", 50)],
        [side("same", "in", 41)],
        [{key: value for key, value in side("undated", "in").items() if key != "timestamp"}],
    ],
)
def test_pinned_leaf_recorded_after_its_turn_closed_is_pending(extra: list[dict[str, Any]]) -> None:
    """A late sibling, a late descendant, an equal instant and a missing instant never precede the final record."""
    assert reasons(decide({BOUND: [*closed_turn(), *extra]}, leaf_shapes=LEAVES)) == {"leaf-after-closing": 1}


def test_pinned_leaf_needs_an_instant_on_its_closing_record() -> None:
    """A final record without a timestamp orders no leaf before it."""
    undated = [{key: value for key, value in item.items() if not (key == "timestamp" and item.get("uuid") == "t1-end")} for item in closed_turn()]

    assert reasons(decide({BOUND: [*undated, side("leaf", "in", 30)]}, leaf_shapes=LEAVES)) == {"leaf-after-closing": 1}
    assert decide({BOUND: [*closed_turn(), side("leaf", "in", 30)]}, leaf_shapes=LEAVES).absence is Absence.PROVED


def test_ambiguous_continuation_closes_no_start() -> None:
    """A second proved successor of the start's file leaves its start open."""
    branching = replace(CLEAR_SCOPE, continuations=frozenset({(OLD, BOUND), (OLD, "other.jsonl")}))
    files: Files = {OLD: closed_turn(WATCHER), "other.jsonl": CLEARED, BOUND: CLEARED}

    assert reasons(decide(files, branching)) == {"background-start-unmatched": 1}


# eof
