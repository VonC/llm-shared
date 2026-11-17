"""Parent-link graph of one Claude transcript for the resume-paused ledger.

Step 1 of v0.14.0 resume-paused. ``TranscriptGraph`` answers the ordering
questions the lifecycle ledger asks about the records of one transcript:
which record was created below which, which input a record belongs to, which
records sit on a parent loop, and whether each tool call has its own result
below it. It keeps structural facts only and reads nothing.

Fix (code review round 2, R2-1 and R2-2, split from
``tools.resume_paused_claude_ledger``): creation order comes from one
depth-first numbering of the parent links, never from file position. A record
on a parent loop is counted instead of being skipped, the nearest input above
a record names its turn, and call identifiers keep their multiplicity: two
calls or two results sharing one identifier, and a result that is not below
its call, are counted. Every question is answered in time linear in the
number of records.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Final

from tools.resume_paused_claude import record_shape

if TYPE_CHECKING:
    from collections.abc import Iterable

    from tools.resume_paused_claude import RecordFact

INPUT_SHAPE: Final = "input"


def repeated(counts: Iterable[int]) -> int:
    """Count the identifiers that occur more than once."""
    return sum(1 for count in counts if count > 1)


class TranscriptGraph:
    """The identified records of one transcript and their parent links.

    ``chain`` lists the records that carry an identifier, in file order, and
    ``by_uuid`` indexes them; a repeated identifier keeps its last record.
    """

    def __init__(self, facts: tuple[RecordFact, ...]) -> None:
        """Index the identified records and number the rooted ones once.

        Args:
            facts: Every record of one transcript, identified or not.
        """
        self.facts = facts
        self.chain = [fact for fact in facts if fact.uuid]
        self.by_uuid: dict[str | None, RecordFact] = {fact.uuid: fact for fact in self.chain}
        self._turns: dict[str | None, RecordFact | None] = {}
        self._spans = self._walk()

    def _walk(self) -> dict[str | None, tuple[int, int]]:
        """Number each rooted record on entry and exit of one depth-first walk.

        A record whose parent is absent counts as a root. A record on a
        parent loop, or below one, is never reached and gets no numbers.
        """
        children: dict[str | None, list[str | None]] = {}
        for fact in self.chain:
            children.setdefault(fact.parent if fact.parent in self.by_uuid else None, []).append(fact.uuid)
        spans: dict[str | None, tuple[int, int]] = {}
        stack = [(root, False) for root in children.get(None, ())]
        clock = 0
        while stack:
            uuid, leaving = stack.pop()
            clock += 1
            if leaving:
                spans[uuid] = (spans[uuid][0], clock)
            elif uuid not in spans:
                spans[uuid] = (clock, clock)
                stack.append((uuid, True))
                stack.extend((child, False) for child in children.get(uuid, ()))
        return spans

    def below(self, fact: RecordFact, ancestor: str | None) -> bool:
        """Tell whether a record was created below an identified one.

        Args:
            fact: The record whose position is asked.
            ancestor: The identifier of the record it should descend from.

        Returns:
            ``True`` only when both records are rooted and the parent chain
            of ``fact`` passes through ``ancestor``. A record without an
            identifier, or on a parent loop, is below nothing.
        """
        inner, outer = self._spans.get(fact.uuid), self._spans.get(ancestor)
        return inner is not None and outer is not None and outer[0] < inner[0] and inner[1] <= outer[1]

    def turn(self, fact: RecordFact) -> RecordFact | None:
        """Return the nearest input above a record: the turn it belongs to.

        Each record is walked once: the answer is kept for every record on
        the way up. A loop or a missing parent ends the walk without a turn.
        """
        path: dict[str | None, None] = {}
        owner: RecordFact | None = None
        node: RecordFact | None = fact
        while node is not None and node.uuid not in path:
            if node.uuid in self._turns:
                owner = self._turns[node.uuid]
                break
            path[node.uuid] = None
            node = self.by_uuid.get(node.parent)
            if node is not None and record_shape(node) == INPUT_SHAPE:
                owner = node
                break
        self._turns.update(dict.fromkeys(path, owner))
        return owner

    def looping(self) -> int:
        """Count the records whose parent chain loops instead of reaching a root."""
        return len(self.by_uuid) - len(self._spans)

    def call_faults(self) -> Counter[str]:
        """Count tool-call faults by reason.

        Returns:
            The identifiers naming several calls or several results, the calls
            without a result, the results without a call, and the single call
            and result pairs whose result does not descend from its call in
            the parent chain.
        """
        callers: dict[str, list[RecordFact]] = {}
        answers: dict[str, list[RecordFact]] = {}
        for fact in self.facts:
            for call, _ in fact.calls:
                callers.setdefault(call, []).append(fact)
            for result in fact.results:
                answers.setdefault(result, []).append(fact)
        pairs = [(facts[0], answers[call][0]) for call, facts in callers.items() if len(facts) == 1 and len(answers.get(call, ())) == 1]
        return Counter({
            "tool-call-duplicate": repeated(map(len, callers.values())),
            "tool-result-duplicate": repeated(map(len, answers.values())),
            "tool-call-open": len(callers.keys() - answers.keys()),
            "tool-result-orphan": len(answers.keys() - callers.keys()),
            "tool-result-unlinked": sum(1 for caller, answer in pairs if not self.below(answer, caller.uuid)),
        })


# eof
