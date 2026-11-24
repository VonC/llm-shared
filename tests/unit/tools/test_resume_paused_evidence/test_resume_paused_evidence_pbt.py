"""Generated counted-command classification properties.

Step 5 of v0.15.0 resume-paused: for every native prefix, letter case and
selection form, ``review-resume`` selects exactly the role heading its
arguments, whatever explanatory later clauses say; the other role as an
alternative in the same clause, or in a second selection form anywhere, makes
the role uncertain; ``resume-session`` is always a counted command.

Fix (code review round 1): explanatory text may name either role without
selecting it. Fix (code review round 2): only the head of the arguments
selects, and alternatives and second selections stay uncertain, so no
ambiguous text can read as a reviewer-only continuation. Fix (code review
round 3): the generated explanations and alternatives vary their punctuation
(semicolon, comma, plain clause, parenthesis), which no longer changes the
meaning.

Each example draws one sampled product, keeping the whole domain at a fraction
of the draws.
"""

from __future__ import annotations

from itertools import product

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.resume_paused_evidence import CommandKind, classify_command, counted
from tools.resume_paused_models import SessionRole

EXAMPLES = 40
PREFIXES = ("", "/", "$", "$llm-shared:", "  /")
SPELLINGS = ("review-resume", "REVIEW-RESUME", "Review-Resume")
# Each head selection form with the role it selects; the empty form selects nothing.
HEADS: dict[str, SessionRole | None] = {
    "": None,
    "reviewer": SessionRole.REVIEWER,
    "Requestor,": SessionRole.REQUESTOR,
    "as reviewer": SessionRole.REVIEWER,
    "as the Requestor": SessionRole.REQUESTOR,
    "--role requestor": SessionRole.REQUESTOR,
    "--role=reviewer": SessionRole.REVIEWER,
}
# Explanatory phrases: they may name either role, whatever their punctuation, but never select one.
LATER = (
    "; after the reviewer replies", "; the requestor is busy", " while the requestor is busy", ", the requestor is busy",
    " (the reviewer answers later)", "; please", ". now", "; for step 4", "; once reviewers-only waits end",
    " (pre-reviewer notes)", "; the requestor-side wait",
)
# Ways to offer a second role as an alternative or a bare list, whatever the punctuation.
CONNECTORS = (" or ", " and ", "/", " or the ", ", ", " (or ", " | ", " (", "; ", " nor ")
ROLE_WORDS: dict[str, SessionRole] = {"reviewer": SessionRole.REVIEWER, "Requestor": SessionRole.REQUESTOR}
SECOND_FORMS: dict[str, SessionRole] = {
    "as reviewer": SessionRole.REVIEWER, "as the requestor": SessionRole.REQUESTOR,
    "--role reviewer": SessionRole.REVIEWER, "--role=requestor": SessionRole.REQUESTOR,
}
SELECTING = sorted(form for form in HEADS if form)

heads = st.sampled_from(list(product(PREFIXES, SPELLINGS, sorted(HEADS))))
clauses = st.lists(st.sampled_from(LATER), max_size=4)
alternatives = st.sampled_from(list(product(SELECTING, CONNECTORS, sorted(ROLE_WORDS))))
seconds = st.sampled_from(list(product(sorted(HEADS), sorted(SECOND_FORMS))))


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(head=heads, phrases=clauses)
def test_the_head_selection_decides_whatever_later_clauses_say(head: tuple[str, str, str], phrases: list[str]) -> None:
    """Later explanatory clauses never select a role and never make the head selection uncertain."""
    prefix, name, selection = head
    command = classify_command(" ".join(part for part in (f"{prefix}{name}", selection) if part) + "".join(phrases))
    assert command is not None
    assert (command.kind, command.role, command.uncertain) == (CommandKind.REVIEW_RESUME, HEADS[selection], False)


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(alternative=alternatives, phrases=clauses)
def test_an_alternative_in_the_same_clause_is_uncertain(alternative: tuple[str, str, str], phrases: list[str]) -> None:
    """``reviewer or requestor`` and its variants never resolve to one role."""
    selection, connector, word = alternative
    command = classify_command(f"/review-resume {selection}{connector}{word}" + "".join(phrases))
    other = ROLE_WORDS[word] is not HEADS[selection]
    assert command is not None
    assert (command.role, command.uncertain) == ((None, True) if other else (HEADS[selection], False))


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(pair=seconds, phrases=clauses)
def test_a_second_selection_of_the_other_role_is_uncertain(pair: tuple[str, str], phrases: list[str]) -> None:
    """A later ``as <role>`` or ``--role <role>`` naming the other role keeps the role uncertain; without a head nothing is selected."""
    selection, second = pair
    command = classify_command(" ".join(part for part in ("/review-resume", selection) if part) + "".join(phrases) + f"; later {second}")
    head = HEADS[selection]
    other = head is not None and SECOND_FORMS[second] is not head
    assert command is not None
    assert (command.role, command.uncertain) == ((None, True) if other else (head, False))


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(head=st.sampled_from(list(product(PREFIXES, (False, True)))), phrases=clauses)
def test_resume_session_always_counts(head: tuple[str, bool], phrases: list[str]) -> None:
    """Normal resume-session counts in every pane for every saved pause role."""
    prefix, reviewer_pause = head
    command = classify_command(f"{prefix}resume-session" + "".join(phrases))
    assert command is not None
    assert command.kind is CommandKind.RESUME_SESSION
    assert counted(command, reviewer_pause=reviewer_pause) is True


# eof
