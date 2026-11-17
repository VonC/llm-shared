"""Claude transcript graph tests.

Step 1 of v0.14.0 resume-paused (code review round 2, R2-1 and R2-2): creation
order comes from the parent links alone. A record is below another only
through its parent chain, its turn is the nearest input above it, a parent
loop is counted, and tool-call identifiers keep their multiplicity.
"""

from __future__ import annotations

import pytest

from tools.resume_paused_claude import RecordFact
from tools.resume_paused_claude_graph import TranscriptGraph, repeated


def node(uuid: str | None, parent: str | None = None, *, text: bool = False) -> RecordFact:
    """Build one record with its parent link; ``text`` makes it an input."""
    return RecordFact("user" if text else "assistant", uuid=uuid, parent=parent, text_input=text)


def call(uuid: str | None, parent: str | None, identifier: str) -> RecordFact:
    """Build a record carrying one tool call."""
    return RecordFact("assistant", uuid=uuid, parent=parent, calls=((identifier, "PowerShell"),))


def result(uuid: str | None, parent: str | None, identifier: str) -> RecordFact:
    """Build a record carrying one tool result."""
    return RecordFact("user", uuid=uuid, parent=parent, results=(identifier,))


def test_below_follows_the_parent_chain_only() -> None:
    """A record is below its ancestors, never below a sibling, itself or a later file position."""
    a, b, c, d, stray = node("a"), node("b", "a"), node("c", "b"), node("d", "a"), node("e", "ghost")
    graph = TranscriptGraph((a, b, c, d, stray, node(None, "a")))

    assert graph.below(c, "a")
    assert graph.below(c, "b")
    assert not graph.below(d, "b")
    assert not graph.below(a, "a")
    assert not graph.below(a, "c")
    assert not graph.below(stray, "a")
    assert not graph.below(c, None)
    assert not graph.below(node(None, "a"), "a")
    assert graph.looping() == 0


def test_turn_is_the_nearest_input_above_a_record() -> None:
    """Each record belongs to the closest input on its parent chain, asked once or again."""
    first, reply, tool = node("in1", text=True), node("r1", "in1"), node("r2", "r1")
    second, answer, leaf = node("in2", "r2", text=True), node("r3", "in2"), node("leaf", "r1")
    graph = TranscriptGraph((first, reply, tool, second, answer, leaf))

    assert graph.turn(tool) is first
    assert graph.turn(tool) is first
    assert graph.turn(leaf) is first
    assert graph.turn(answer) is second
    assert graph.turn(second) is first
    assert graph.turn(first) is None
    assert graph.turn(node("orphan", "ghost")) is None


@pytest.mark.parametrize(
    ("facts", "looping"),
    [
        ((node("loop", "loop"),), 1),
        ((node("a", "b"), node("b", "a")), 2),
        ((node("root"), node("a", "b"), node("b", "a"), node("c", "a")), 3),
        ((node("a"), node("a")), 0),
    ],
)
def test_parent_loops_are_counted_with_everything_below_them(facts: tuple[RecordFact, ...], looping: int) -> None:
    """A record on a loop, or below one, never reaches a root; a repeated identifier is not a loop."""
    graph = TranscriptGraph(facts)

    assert graph.looping() == looping
    assert graph.turn(facts[-1]) is None
    assert not graph.below(facts[-1], facts[0].uuid)


@pytest.mark.parametrize(
    ("facts", "expected"),
    [
        ((call("c", None, "x"), result("r", "c", "x")), {}),
        ((call("c", None, "x"),), {"tool-call-open": 1}),
        ((result("r", None, "x"),), {"tool-result-orphan": 1}),
        ((call("c1", None, "x"), result("r", "c1", "x"), call("c2", "r", "x")), {"tool-call-duplicate": 1}),
        ((call("c", None, "x"), result("r1", "c", "x"), result("r2", "r1", "x")), {"tool-result-duplicate": 1}),
        ((result("r", None, "x"), call("c", "r", "x")), {"tool-result-unlinked": 1}),
        ((call("c", None, "x"), result("r", None, "x")), {"tool-result-unlinked": 1}),
        ((call(None, None, "x"), result(None, None, "x")), {"tool-result-unlinked": 1}),
    ],
)
def test_call_faults_keep_identifier_multiplicity_and_order(facts: tuple[RecordFact, ...], expected: dict[str, int]) -> None:
    """One call, one result below it; anything else is counted under its own reason."""
    faults = TranscriptGraph(facts).call_faults()

    assert {reason: count for reason, count in faults.items() if count} == expected


def test_repeated_counts_identifiers_seen_more_than_once() -> None:
    """Only counts above one are repeats."""
    assert repeated([1, 2, 3, 1]) == 2  # noqa: PLR2004
    assert repeated([]) == 0


# eof
