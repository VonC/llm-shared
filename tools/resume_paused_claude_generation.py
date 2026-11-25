"""Claude transcript generation and continuation checks for the resume-paused ledger.

Step 1 of v0.15.0 resume-paused, design Q28=A follow-up: the lifecycle ledger
stood at 642 of its 650 lines, so its generation and continuation checks moved
here unchanged before the ledger grows. ``require_generation`` counts a missing
or unaccepted first marker, a marker older than the bound process and every
later SessionStart other than a compaction. ``writer_markers`` accepts a clear
marker for another writer's transcript only after a proved continuation, and
``clears`` tells whether a transcript begins with one. ``continuation_places``
numbers each file along its single proved chain (code review round 3, R3-3),
and ``missing_predecessors`` counts a proved continuation whose earlier file is
missing from the scope (code review round 5, R5-1).
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Final

from tools.resume_paused_claude import STARTUP_MARKERS
from tools.resume_paused_windows import filetime_to_datetime

if TYPE_CHECKING:
    from collections.abc import Iterable

    from tools.resume_paused_claude import RecordFact
    from tools.resume_paused_profiles import ProcessIdentity

_COMPACT_MARKER: Final = "SessionStart:compact"
_CLEAR_MARKER: Final = "SessionStart:clear"
_SESSION_START: Final = "SessionStart:"


def _restarts(fact: RecordFact) -> bool:
    """Tell whether a record is a SessionStart other than a compaction."""
    hook = fact.hook or ""
    return hook.startswith(_SESSION_START) and hook != _COMPACT_MARKER


def _first_stamped(facts: tuple[RecordFact, ...]) -> RecordFact | None:
    """Return the first record that carries a timestamp."""
    return next((fact for fact in facts if fact.timestamp is not None), None)


def clears(facts: tuple[RecordFact, ...]) -> bool:
    """Tell whether a transcript begins with a clear marker."""
    first = _first_stamped(facts)
    return first is not None and first.attachment == "hook_success" and first.hook == _CLEAR_MARKER


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


def missing_predecessors(continuations: frozenset[tuple[str, str]], listed: frozenset[str], outside: set[str]) -> int:
    """Count proved continuations into a listed file whose earlier file is missing from the scope.

    The pair names the earlier file, so its absence from the enumeration, or
    its exclusion as another checkout's transcript, is detected missing
    history: the later file cannot prove that the earlier one held no other
    work. Each link of a chain is checked, so a missing ancestor is counted
    too. An unreadable or incomplete earlier file is counted by its own read
    reason, and one older than a resolved boot boundary stays under the boot
    rule.
    """
    return sum(1 for earlier, later in continuations if later in listed and (earlier not in listed or earlier in outside))


def writer_markers(*, continued: bool) -> frozenset[str]:
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


def require_generation(
    facts: tuple[RecordFact, ...], markers: frozenset[str], process: ProcessIdentity | None, reasons: Counter[str],
) -> None:
    """Require one complete generation: an accepted first marker and no later restart.

    A missing or unaccepted first marker means missing history, and a later
    SessionStart other than a compaction means another generation wrote into
    the file. Both are pending.

    Args:
        facts: The parsed records of one transcript, in file order.
        markers: The SessionStart forms accepted as its first marker.
        process: The bound pane's process generation, or ``None`` for another
            writer's transcript, which has no process of its own.
        reasons: The decision's counted reasons, updated in place.
    """
    first = _first_stamped(facts)
    _marker(first, markers, process, reasons)
    reasons["generation-restarted"] += sum(1 for fact in facts if fact is not first and _restarts(fact))


# eof
