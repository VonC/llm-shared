"""Claude transcript generation and continuation check tests.

Step 1 of v0.15.0 resume-paused, design Q28=A follow-up: the generation and
continuation checks moved out of the lifecycle ledger unchanged, and their
direct cases moved with them. A transcript holds one complete generation only
when its first timestamped record is an accepted marker, not older than the
bound process, and no later SessionStart other than a compaction follows.
Another writer's transcript accepts a clear marker only after a proved
continuation. Continuation chains are numbered in one pass, a branching or
looping link places nothing, and a proved continuation into a listed file
whose earlier file is unlisted or excluded counts as missing history. The two
``continuation_places`` cases come from the ledger ordering tests.
"""

from __future__ import annotations

from collections import Counter
from itertools import pairwise

import pytest

from tests.unit.tools.resume_paused_test_support import HOST_PID, at, filetime
from tools.resume_paused_claude import REQUESTOR_MARKERS, STARTUP_MARKERS, RecordFact
from tools.resume_paused_claude_generation import (
    clears,
    continuation_places,
    missing_predecessors,
    require_generation,
    writer_markers,
)
from tools.resume_paused_profiles import ProcessIdentity

CHAIN_LENGTH = 1000
UNSTAMPED = RecordFact(kind="mode")
NONE_OUTSIDE: frozenset[str] = frozenset()


def marker(hook: str = "SessionStart:startup", seconds: int = 5, attachment: str = "hook_success") -> RecordFact:
    """Build a timestamped SessionStart attachment."""
    return RecordFact(kind="attachment", timestamp=at(seconds), attachment=attachment, hook=hook)


def generation(*facts: RecordFact, markers: frozenset[str] = STARTUP_MARKERS, process: ProcessIdentity | None = None) -> dict[str, int]:
    """Return the reasons ``require_generation`` counts for the declared records."""
    reasons: Counter[str] = Counter()
    require_generation(facts, markers, process, reasons)
    return {code: count for code, count in reasons.items() if count}


def test_accepted_first_marker_opens_one_complete_generation() -> None:
    """A startup marker first, after unstamped records, with later compaction and other hooks, is complete."""
    later = (marker("SessionStart:compact", 30), marker("PreToolUse:PowerShell", 31), RecordFact(kind="user", timestamp=at(32)))

    assert generation(UNSTAMPED, marker(), *later) == {}


@pytest.mark.parametrize(
    "facts",
    [
        (),
        (UNSTAMPED,),
        (marker("SessionStart:resume"),),
        (marker("SessionStart:clear"),),
        (marker(attachment="hook_error"),),
    ],
)
def test_missing_or_unaccepted_first_marker_is_missing_history(facts: tuple[RecordFact, ...]) -> None:
    """No stamped record, a resume or clear marker, or a failed hook prove no generation."""
    assert generation(*facts) == {"generation-marker-missing": 1}


def test_marker_after_another_stamped_record_opens_another_generation() -> None:
    """Another record first is missing history, and the startup marker after it is a restart."""
    assert generation(RecordFact(kind="user", timestamp=at(4)), marker()) == {"generation-marker-missing": 1, "generation-restarted": 1}


def test_clear_marker_is_accepted_where_the_markers_allow_it() -> None:
    """The requestor's markers accept a clear first marker."""
    assert generation(marker("SessionStart:clear"), markers=REQUESTOR_MARKERS) == {}


def test_marker_older_than_the_bound_process_is_pending() -> None:
    """A marker before the process creation is another generation's; one at the creation instant is not."""
    late = ProcessIdentity(HOST_PID, filetime(at(6)))
    exact = ProcessIdentity(HOST_PID, filetime(at(5)))

    assert generation(marker(), process=late) == {"generation-marker-before-process": 1}
    assert generation(marker(), process=exact) == {}


def test_every_later_noncompact_session_start_is_a_restart() -> None:
    """Each later resume, startup or clear counts once; the first marker never counts as a restart."""
    facts = (marker(), marker("SessionStart:resume", 30), marker("SessionStart:startup", 40), marker("SessionStart:clear", 50))

    assert generation(*facts) == {"generation-restarted": 3}


def test_writer_markers_accept_a_clear_only_after_a_proved_continuation() -> None:
    """Another writer's transcript opens with a startup, or with a clear when its continuation is proved."""
    assert writer_markers(continued=False) == STARTUP_MARKERS
    assert writer_markers(continued=True) == REQUESTOR_MARKERS


@pytest.mark.parametrize(
    ("facts", "expected"),
    [
        ((UNSTAMPED, marker("SessionStart:clear")), True),
        ((marker(),), False),
        ((marker("SessionStart:clear", attachment="hook_error"),), False),
        ((UNSTAMPED,), False),
        ((), False),
    ],
)
def test_clears_reads_only_the_first_stamped_record(facts: tuple[RecordFact, ...], *, expected: bool) -> None:
    """Only a successful clear hook as the first timestamped record begins a cleared transcript."""
    assert clears(facts) is expected


def test_long_continuation_chain_is_numbered_once_per_file() -> None:
    """A chain of a thousand clears yields one place per file, not one entry per reachable pair."""
    names = [f"s{index}.jsonl" for index in range(CHAIN_LENGTH + 1)]

    places = continuation_places(pairwise(names))

    assert len(places) == CHAIN_LENGTH + 1
    assert places[names[0]] == (names[0], 0)
    assert places[names[-1]] == (names[0], CHAIN_LENGTH)


@pytest.mark.parametrize(
    "pairs",
    [
        {("a", "b"), ("a", "c")},
        {("a", "c"), ("b", "c")},
        {("a", "b"), ("b", "a")},
        {("a", "a")},
    ],
)
def test_branching_or_looping_continuation_places_nothing(pairs: set[tuple[str, str]]) -> None:
    """Two successors, two predecessors and a loop are ambiguous: no file is placed."""
    assert continuation_places(pairs) == {}


@pytest.mark.parametrize(
    ("pairs", "listed", "outside", "expected"),
    [
        ({("old", "new")}, {"old", "new"}, NONE_OUTSIDE, 0),
        ({("old", "new")}, {"new"}, NONE_OUTSIDE, 1),
        ({("old", "new")}, {"old", "new"}, {"old"}, 1),
        ({("old", "new")}, {"old"}, NONE_OUTSIDE, 0),
        ({("first", "mid"), ("mid", "new")}, {"mid", "new"}, NONE_OUTSIDE, 1),
    ],
)
def test_proved_continuation_into_a_listed_file_needs_its_earlier_file(
    pairs: set[tuple[str, str]], listed: set[str], outside: set[str] | frozenset[str], expected: int,
) -> None:
    """An unlisted or excluded earlier file is missing history; a pair into an unlisted file is not counted."""
    assert missing_predecessors(frozenset(pairs), frozenset(listed), set(outside)) == expected


# eof
