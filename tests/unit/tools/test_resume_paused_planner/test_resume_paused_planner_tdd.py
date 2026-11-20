"""Read-only checkout planner tests: global refusals, classification and targets.

Step 5 of v0.14.0 resume-paused: a recognized agent caller, failed discovery
and unmatched ``--except`` or ``--switch-roles`` names refuse the whole run
before any checkout is read. Every other prompt-bearing checkout gets one
typed result: used prompts (with the later reviewer continuation of a saved
requestor pair), routing skips and errors, unsupported pausers, checkout-wide
duplicate evidence from every pane (excluded and caller panes included), and
saved targets validated by full pane UUID, TUIOS session, checkout and host.
Missing UUIDs and shell panes skip, another host fails, the switch swaps only
a saved requestor pair, and a dry run classifies the same plan with no input.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    raw_block,
)
from tests.unit.tools.test_resume_paused_planner.planner_world import (
    API,
    WEB,
    World,
    active,
    adding,
    binding,
    live,
    replacing,
    routing,
    snapshot,
    unchanged,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    SESSION,
    THIRD_PANE,
    mutated,
    part,
    single_agent,
    slot,
)
from tools.resume_paused_artifacts import (
    ROUTING_TABLE_HEADER,
    CheckoutSnapshot,
    PromptState,
)
from tools.resume_paused_evidence import (
    DuplicateSignal,
    JournalIndex,
    ObservedCommand,
    PaneActivity,
    ScreenVerdict,
    parse_session_journal,
)
from tools.resume_paused_marker import Marker
from tools.resume_paused_models import ArtifactError, CanonicalRoot, SessionRole
from tools.resume_paused_plan_model import (
    ActionKind,
    CheckoutOutcome,
    ErrorReason,
    GlobalReason,
    SkipReason,
)
from tools.resume_paused_profiles import CallerDecision, CallerOrigin, Host, Reason
from tools.resume_paused_review import ExchangeObservationKind

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.unit.tools.test_resume_paused_planner.planner_world import Change
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_plan_model import CheckoutPlan, RunPlan

LATER = datetime(2026, 11, 17, 17, 0, tzinfo=UTC)
OLDER = datetime(2026, 11, 17, 16, 0, tzinfo=UTC)


def only(plan: RunPlan) -> CheckoutPlan:
    """Return the single checkout result of a run."""
    (checkout,) = plan.checkouts
    return checkout


def verdict(plan: RunPlan) -> tuple[CheckoutOutcome, object]:
    """Return the single checkout's outcome and reason."""
    checkout = only(plan)
    return checkout.outcome, checkout.reason


@pytest.mark.parametrize("dry_run", [False, True])
def test_recognized_agent_caller_is_refused_before_any_read(dry_run: bool) -> None:  # noqa: FBT001
    """Q20: a recognized agent caller gets no plan, in a preview too."""
    world = World()
    agent = CallerDecision(CallerOrigin.AGENT, (Reason("agent-environment-marker"),))
    plan = world.plan(caller=agent, dry_run=dry_run)
    assert [(failure.reason, failure.names) for failure in plan.failures] == [(GlobalReason.AGENT_CALLER, ("agent-environment-marker",))]
    assert (plan.checkouts, world.reads, plan.failed, plan.input_allowed) == ((), [], True, False)


def test_failed_discovery_is_a_global_failure_not_absence() -> None:
    """Failed discovery reads no checkout and allows no input."""
    world = World()
    plan = world.plan(discovered=False)
    assert [failure.reason for failure in plan.failures] == [GlobalReason.DISCOVERY_FAILED]
    assert (plan.checkouts, world.reads) == ((), [])


def test_unmatched_names_prevent_all_input() -> None:
    """Every unmatched exclusion and switch name is reported; a pane label never matches a switch."""
    world = World()
    plan = world.plan(excepts=("API", "nowhere"), switch_roles=("requestor | pane", "WEB"))
    assert [(failure.reason, failure.names) for failure in plan.failures] == [
        (GlobalReason.EXCEPT_UNMATCHED, ("nowhere",)),
        (GlobalReason.SWITCH_UNMATCHED, ("requestor | pane", "WEB")),
    ]
    assert (plan.checkouts, world.reads, plan.input_allowed) == ((), [], False)


def test_saved_requestor_pair_plans_resume_then_conditional_reviewer() -> None:
    """The requestor resume comes first; the reviewer command waits on takeover; only the resume clears."""
    world = World()
    checkout = only(world.plan(clear=True))
    resume, reviewer = checkout.actions
    state = world.snapshots["c:\\work\\api"]
    assert isinstance(state, CheckoutSnapshot)
    assert (checkout.outcome, checkout.title, checkout.author, checkout.prompt_state) == (CheckoutOutcome.PLANNED, "Step 2 tests", "claude", PromptState.UNUSED)
    assert (resume.kind, resume.role, resume.host, resume.pane_id, resume.clear, resume.conditional) == (
        ActionKind.RESUME, SessionRole.REQUESTOR, Host.CLAUDE, REQUESTOR_PANE, True, False,
    )
    assert resume.command == f"/resume-session --resume-paused {'0' * 31}1.rp1.{REQUESTOR_PANE}.requestor.{binding(state, REQUESTOR_PANE, SessionRole.REQUESTOR)}"
    assert (reviewer.kind, reviewer.role, reviewer.clear, reviewer.conditional, reviewer.skip) == (ActionKind.REVIEWER, SessionRole.REVIEWER, False, True, None)
    assert reviewer.command is not None
    assert reviewer.command.startswith("$llm-shared:review-resume --resume-paused ")
    assert Marker.parse(reviewer.command.split()[-1]).binding == binding(state, REVIEWER_PANE, SessionRole.REVIEWER)


def test_dry_run_plans_the_same_checkouts_without_input() -> None:
    """A preview classifies exactly what a run would, counts omitted panes and allows no input."""
    world = World()
    world.panes.append(live(THIRD_PANE, Host.CLAUDE, name="spare"))
    run = world.plan(clear=True)
    preview = world.plan(clear=True, dry_run=True)
    assert (run.omitted_panes, run.failed, run.input_allowed) == (1, False, True)
    assert (preview.checkouts, preview.omitted_panes, preview.input_allowed, preview.failed) == (run.checkouts, 1, False, False)


def claude_single(mapping: dict[str, object]) -> None:
    """Turn the pause into a single Claude implementation pause."""
    single_agent(mapping)
    part(mapping, "pause")["session_role"] = "implementation"


def codex_single(mapping: dict[str, object]) -> None:
    """Turn the pause into a single Codex implementation pause."""
    claude_single(mapping)
    slot(mapping, "resumed")["host"] = "codex"


def reviewer_pause(mapping: dict[str, object]) -> None:
    """Turn the pause into a saved reviewer pause of the pair."""
    part(mapping, "pause")["session_role"] = "reviewer"
    part(mapping, "targets")["resumed"] = dict(slot(mapping, "reviewer"))


@pytest.mark.parametrize(
    ("change", "role", "host", "pane", "command"),
    [
        (claude_single, "implementation", Host.CLAUDE, REQUESTOR_PANE, "/resume-session"),
        (codex_single, "implementation", Host.CODEX, REQUESTOR_PANE, "$llm-shared:resume-session"),
        (reviewer_pause, "reviewer", Host.CODEX, REVIEWER_PANE, "$llm-shared:resume-session"),
    ],
)
def test_single_agent_and_reviewer_pauses_resume_only_their_agent(
    change: Callable[[dict[str, object]], None], role: str, host: Host, pane: str, command: str,
) -> None:
    """Non-requestor pauses resume their own agent and never activate a counterpart."""
    world = World(snapshots={"c:\\work\\api": snapshot(saved=routing(API, change), role=role)})
    world.panes = [live(pane, host)]
    (action,) = only(world.plan()).actions
    assert (action.kind, action.role.value, action.host, action.pane_id) == (ActionKind.RESUME, role, host, pane)
    assert action.command is not None
    assert action.command.startswith(f"{command} --resume-paused ")


@pytest.mark.parametrize("name", ["LLM-Shared_Resume-Paused", "api"])
def test_switch_roles_swaps_only_the_saved_requestor_pair(name: str) -> None:
    """A session or folder name swaps the saved pair; panes stay the saved ones."""
    world = World()
    checkout = only(world.plan(switch_roles=(name,)))
    resume, reviewer = checkout.actions
    state = world.snapshots["c:\\work\\api"]
    assert isinstance(state, CheckoutSnapshot)
    assert checkout.switched
    assert (resume.role, resume.host, resume.pane_id) == (SessionRole.REQUESTOR, Host.CODEX, REVIEWER_PANE)
    assert (reviewer.role, reviewer.host, reviewer.pane_id) == (SessionRole.REVIEWER, Host.CLAUDE, REQUESTOR_PANE)
    assert resume.command is not None
    assert Marker.parse(resume.command.split()[-1]).binding == binding(state, REVIEWER_PANE, SessionRole.REQUESTOR)


def test_inapplicable_switch_fails_its_checkout_only() -> None:
    """A named reviewer pause receives no input and fails; an independent checkout still plans."""
    web = routing(WEB, reviewer_pause)
    world = World(snapshots={"c:\\work\\api": snapshot(), "c:\\work\\web": snapshot(WEB, web, role="reviewer")})
    world.panes.append(live(THIRD_PANE, Host.CODEX, WEB, session="other"))
    plan = world.plan(switch_roles=("web",))
    assert [(checkout.root.display, checkout.outcome, checkout.reason) for checkout in plan.checkouts] == [
        ("C:\\work\\api", CheckoutOutcome.PLANNED, None),
        ("C:\\work\\web", CheckoutOutcome.ERROR, ErrorReason.SWITCH_NOT_APPLICABLE),
    ]
    assert (plan.failed, plan.input_allowed) == (True, True)


@pytest.mark.parametrize(
    ("receipt", "switch", "outcome", "reason"),
    [
        ({"schema": 2}, (), CheckoutOutcome.SKIPPED, SkipReason.ALREADY_USED),
        ({"schema": 3}, (), CheckoutOutcome.PLANNED, None),
        ({"schema": 3, "Receiving pane": THIRD_PANE}, (), CheckoutOutcome.SKIPPED, SkipReason.ALREADY_USED),
        ({"schema": 3, "Receiving pane": REVIEWER_PANE}, (), CheckoutOutcome.SKIPPED, SkipReason.SWITCH_REQUIRED),
        ({"schema": 3, "Receiving pane": REVIEWER_PANE}, ("api",), CheckoutOutcome.PLANNED, None),
        ({"schema": 3}, ("api",), CheckoutOutcome.ERROR, ErrorReason.SWITCH_MISMATCH),
    ],
)
def test_used_prompts_report_the_receipt_and_continue_only_the_resumed_pair(
    receipt: dict[str, object], switch: tuple[str, ...], outcome: CheckoutOutcome, reason: object,
) -> None:
    """A receipt suppresses every initial resume; the resumed requestor's pair may continue its reviewer."""
    world = World(snapshots={"c:\\work\\api": snapshot(receipt=receipt)})
    checkout = only(world.plan(switch_roles=switch))
    assert (checkout.outcome, checkout.reason) == (outcome, reason)
    assert [(item.signal, item.detail) for item in checkout.duplicates] == [(DuplicateSignal.RECEIPT, "claude")]
    if outcome is CheckoutOutcome.PLANNED:
        (action,) = checkout.actions
        assert (action.kind, action.role, action.conditional) == (ActionKind.CONTINUE_REVIEWER, SessionRole.REVIEWER, True)
        assert action.pane_id == (REQUESTOR_PANE if switch else REVIEWER_PANE)


def test_prompt_replaced_since_its_receipt_is_planned_again() -> None:
    """A receipt for other bytes lets the new prompt resume."""
    world = World(snapshots={"c:\\work\\api": snapshot(receipt={"schema": 2, "digest": "c" * 64})})
    assert verdict(world.plan()) == (CheckoutOutcome.PLANNED, None)


def contradicted(mapping: dict[str, object]) -> None:
    """Make the routing contradict the prompt snapshot."""
    part(mapping, "pause")["snapshot"] = "2026-11-17T18:00:00+01:00"


def unknown_resumed(mapping: dict[str, object]) -> None:
    """Record the resumed target as unknown."""
    part(mapping, "targets")["resumed"] = {"unknown": "pane not observed"}


def unknown_exchange(mapping: dict[str, object]) -> None:
    """Record the exchange as unknown: several live exchanges and no saved identity."""
    mapping["exchange"] = {"unknown": "two live exchanges"}


@pytest.mark.parametrize(
    ("section", "expected"),
    [
        ("", (CheckoutOutcome.SKIPPED, SkipReason.ROUTING_MISSING)),
        (f"{ROUTING_TABLE_HEADER}\n| --- | --- |\n", (CheckoutOutcome.SKIPPED, SkipReason.ROUTING_TABLE_ONLY)),
        (raw_block(mutated(API, unknown_resumed)), (CheckoutOutcome.SKIPPED, SkipReason.ROUTING_UNRESOLVED)),
        (raw_block(mutated(API, unknown_exchange)), (CheckoutOutcome.SKIPPED, SkipReason.PAIRING_AMBIGUOUS)),
        (raw_block(mutated(API, contradicted)), (CheckoutOutcome.ERROR, ErrorReason.ROUTING_INVALID)),
    ],
)
def test_routing_states_skip_or_fail(section: str, expected: tuple[CheckoutOutcome, object]) -> None:
    """Missing, table-only and unknown routing skip; ambiguous pairing has no counterpart; invalid routing fails."""
    world = World(snapshots={"c:\\work\\api": snapshot(section=section)})
    plan = world.plan()
    assert verdict(plan) == expected
    assert (only(plan).actions, world.exchanges.observed) == ((), [])


def test_unsupported_pauser_is_an_expected_skip() -> None:
    """A pause by an agent without a bulk host is skipped, not guessed."""
    saved = routing(API, lambda mapping: part(mapping, "pause").update(author="gemini"))
    world = World(snapshots={"c:\\work\\api": snapshot(saved=saved, author="gemini")})
    assert verdict(world.plan()) == (CheckoutOutcome.SKIPPED, SkipReason.UNSUPPORTED_PAUSER)


def test_checkout_errors_are_isolated_and_folder_exclusions_skip() -> None:
    """An unreadable pause and a raising reader fail alone; an excluded folder skips; others plan."""
    docs = CheckoutSnapshot(CanonicalRoot.parse("C:\\work\\docs"), None, PromptState.ERROR, diagnostic="artifact home is unusable: denied")
    world = World(snapshots={
        "c:\\work\\api": snapshot(), "c:\\work\\docs": docs,
        "c:\\work\\ops": ArtifactError("usage receipt repeats Schema"), "c:\\work\\web": snapshot(WEB, routing(WEB)),
    })
    world.panes += [live(THIRD_PANE, None, "C:\\work\\docs"), live(THIRD_PANE.replace("5b", "6b"), None, "C:\\work\\ops"), live(THIRD_PANE.replace("5b", "7b"), None, WEB)]
    plan = world.plan(excepts=("WEB",))
    assert [(checkout.root.display, checkout.outcome, checkout.reason, checkout.detail) for checkout in plan.checkouts] == [
        ("C:\\work\\api", CheckoutOutcome.PLANNED, None, ""),
        ("C:\\work\\docs", CheckoutOutcome.ERROR, ErrorReason.CHECKOUT_UNREADABLE, "artifact home is unusable: denied"),
        ("C:\\work\\ops", CheckoutOutcome.ERROR, ErrorReason.EVIDENCE_INVALID, "usage receipt repeats Schema"),
        ("C:\\work\\web", CheckoutOutcome.SKIPPED, SkipReason.EXCLUDED, "checkout folder"),
    ]
    assert world.reads == ["c:\\work\\api", "c:\\work\\docs", "c:\\work\\ops", "c:\\work\\web"]


def journal_after_pause() -> JournalIndex:
    """Return a journal holding a resume of the checkout after its pause."""
    return parse_session_journal(b"# Session journal\n\n## Resume by chatgpt at 2026-11-17T18:00:00+01:00 in `C:\\work\\api`\n")


@pytest.mark.parametrize(
    ("journal", "commands", "options", "expected"),
    [
        (journal_after_pause(), {}, {}, (CheckoutOutcome.SKIPPED, SkipReason.JOURNAL_RESUMED)),
        (JournalIndex(), {REVIEWER_PANE: (ObservedCommand("/resume-session", LATER),)}, {"excepts": ("reviewer | pane",)}, (CheckoutOutcome.SKIPPED, SkipReason.ALREADY_RESUMING)),
        (JournalIndex(), {REQUESTOR_PANE: (ObservedCommand("/resume-session", LATER),)}, {"caller_pane": REQUESTOR_PANE}, (CheckoutOutcome.SKIPPED, SkipReason.ALREADY_RESUMING)),
        (JournalIndex(), {REQUESTOR_PANE: (ObservedCommand("/resume-session", OLDER),)}, {}, (CheckoutOutcome.PLANNED, None)),
        (JournalIndex(), {REQUESTOR_PANE: (ObservedCommand("/review-resume", LATER),)}, {}, (CheckoutOutcome.ERROR, ErrorReason.DUPLICATE_UNCERTAIN)),
        (journal_after_pause(), {REQUESTOR_PANE: None}, {}, (CheckoutOutcome.SKIPPED, SkipReason.JOURNAL_RESUMED)),
        (JournalIndex(error="session journal is not UTF-8"), {}, {}, (CheckoutOutcome.ERROR, ErrorReason.DUPLICATE_UNCERTAIN)),
    ],
)
def test_duplicate_evidence_from_every_pane_suppresses_the_checkout(
    journal: JournalIndex, commands: dict[str, tuple[ObservedCommand, ...] | None], options: dict[str, Any], expected: tuple[CheckoutOutcome, object],
) -> None:
    """Excluded and caller panes still count; older commands do not; certain evidence outranks uncertainty."""
    world = World(journal=journal)
    world.history.by_pane.update(commands)
    assert verdict(world.plan(**options)) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("/review-resume reviewer or requestor", (CheckoutOutcome.ERROR, ErrorReason.DUPLICATE_UNCERTAIN)),
        ("/review-resume after Alex signs in as reviewer", (CheckoutOutcome.ERROR, ErrorReason.DUPLICATE_UNCERTAIN)),
        ("/review-resume reviewer (or requestor)", (CheckoutOutcome.ERROR, ErrorReason.DUPLICATE_UNCERTAIN)),
        ("/review-resume as reviewer, then continue the review", (CheckoutOutcome.PLANNED, None)),
        ("/review-resume as reviewer while the requestor is busy", (CheckoutOutcome.PLANNED, None)),
        ("/review-resume as reviewer; the requestor is busy", (CheckoutOutcome.PLANNED, None)),
    ],
)
def test_ambiguous_reviewer_continuation_blocks_a_requestor_pause(text: str, expected: tuple[CheckoutOutcome, object]) -> None:
    """Q26: only an explicit reviewer selection leaves a requestor pause resumable; an ambiguous one sends no input."""
    world = World()
    world.history.by_pane[REVIEWER_PANE] = (ObservedCommand(text, LATER),)
    plan = world.plan()
    assert verdict(plan) == expected
    assert any(action.command for action in only(plan).actions) is (expected[0] is CheckoutOutcome.PLANNED)


def test_panes_spelling_one_checkout_differently_share_its_duplicate_evidence() -> None:
    """Windows case, separators and trailing slashes name one checkout: one read, one result, shared evidence."""
    world = World()
    world.panes.append(live(THIRD_PANE, Host.CODEX, "c:/WORK/Api/", session="other", name="Codex other"))
    world.history.by_pane[THIRD_PANE] = (ObservedCommand("$llm-shared:resume-session", LATER),)
    plan = world.plan()
    assert (verdict(plan), world.reads) == ((CheckoutOutcome.SKIPPED, SkipReason.ALREADY_RESUMING), ["c:\\work\\api"])
    assert [item.pane_id for item in only(plan).duplicates] == [THIRD_PANE]


def test_pending_author_override_suppresses_the_checkout() -> None:
    """A pane waiting on the override question means the checkout is already resuming."""
    world = World()
    world.activity[REVIEWER_PANE] = PaneActivity("needs_input", "question", draft_held=False, question="Do you want to override that and resume it here?", ready=False)
    checkout = only(world.plan())
    assert (checkout.outcome, checkout.reason) == (CheckoutOutcome.SKIPPED, SkipReason.OVERRIDE_PENDING)
    assert [(item.signal, item.pane_id) for item in checkout.duplicates] == [(DuplicateSignal.OVERRIDE, REVIEWER_PANE)]


def all_restored(world: World) -> None:
    """Move every live pane into a new session: the saved session is gone."""
    world.panes = [replace(record, session="restored") for record in world.panes]


def contradictory(pane: str) -> PaneRecord:
    """Declare a pane carrying both the Claude harness and the Codex app."""
    return replace(live(pane), apps=("codex",))


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        (replacing(REQUESTOR_PANE, None), (CheckoutOutcome.SKIPPED, SkipReason.TARGET_ABSENT)),
        (all_restored, (CheckoutOutcome.SKIPPED, SkipReason.TARGET_ABSENT)),
        (replacing(REVIEWER_PANE, live(REVIEWER_PANE, Host.CODEX, session="moved")), (CheckoutOutcome.ERROR, ErrorReason.TARGET_SESSION_CHANGED)),
        (replacing(REQUESTOR_PANE, live(REQUESTOR_PANE, None)), (CheckoutOutcome.SKIPPED, SkipReason.TARGET_NOT_AGENT)),
        (replacing(REQUESTOR_PANE, live(REQUESTOR_PANE, Host.CODEX)), (CheckoutOutcome.ERROR, ErrorReason.TARGET_HOST_CHANGED)),
        (replacing(REQUESTOR_PANE, contradictory(REQUESTOR_PANE)), (CheckoutOutcome.ERROR, ErrorReason.HOST_CONTRADICTORY)),
        (replacing(REQUESTOR_PANE, live(REQUESTOR_PANE, root=WEB)), (CheckoutOutcome.ERROR, ErrorReason.TARGET_CHECKOUT_CHANGED)),
        (replacing(REQUESTOR_PANE, live(REQUESTOR_PANE, root="work\\api")), (CheckoutOutcome.SKIPPED, SkipReason.TARGET_IDENTITY_UNAVAILABLE)),
        (adding(live(REQUESTOR_PANE, session="twin")), (CheckoutOutcome.ERROR, ErrorReason.PANE_AMBIGUOUS)),
    ],
)
def test_saved_targets_are_validated_by_uuid_session_checkout_and_host(change: Change, expected: tuple[CheckoutOutcome, object]) -> None:
    """Absent UUIDs, lost sessions and shell panes skip; reassignment, another host and reuse fail."""
    world = World()
    change(world)
    plan = world.plan()
    assert verdict(plan) == expected
    assert all(action.command is None for action in only(plan).actions)


def test_codex_name_fallback_and_reported_identity_changes() -> None:
    """A Codex pane without harness or app is found by name; label and agent session changes are notes."""
    saved = routing(API, lambda mapping: slot(mapping, "reviewer").update(agent_session_id="old-session"))
    world = World(snapshots={"c:\\work\\api": snapshot(saved=saved)})
    world.panes = [live(REQUESTOR_PANE, name="renamed"), replace(live(REVIEWER_PANE, None, name="Codex reviewer"), agent_session_id="new-session")]
    resume, reviewer = only(world.plan()).actions
    assert (resume.notes, reviewer.host, reviewer.notes) == (("label-changed",), Host.CODEX, ("label-changed", "agent-session-changed"))


@pytest.mark.parametrize(
    ("change", "options", "skip"),
    [
        (unchanged, {"excepts": ("Requestor | Pane",)}, SkipReason.EXCLUDED),
        (unchanged, {"excepts": (SESSION.upper(),)}, SkipReason.EXCLUDED),
        (unchanged, {"caller_pane": REQUESTOR_PANE}, SkipReason.CALLER_PANE),
        (active(REQUESTOR_PANE, PaneActivity("needs_input", "", draft_held=False, question="", ready=True)), {}, SkipReason.PANE_BLOCKED),
        (active(REQUESTOR_PANE, PaneActivity("idle", "", draft_held=True, question="", ready=True)), {}, SkipReason.PANE_DRAFT),
        (active(REQUESTOR_PANE, PaneActivity("idle", "", draft_held=False, question="", ready=False)), {}, SkipReason.PANE_NOT_READY),
        (active(REQUESTOR_PANE, PaneActivity("done", "", draft_held=False, question="", ready=None)), {}, SkipReason.PANE_NOT_READY),
        (active(REQUESTOR_PANE, PaneActivity("working", "", draft_held=False, question="", ready=False)), {}, SkipReason.PANE_BUSY),
        (active(REQUESTOR_PANE, None), {}, SkipReason.PANE_STATE_UNKNOWN),
    ],
)
def test_resume_target_protections_skip_without_input(change: Change, options: dict[str, Any], skip: SkipReason) -> None:
    """Excluded, caller, blocked, draft, not-ready, busy and unknown panes receive nothing, and nothing is captured."""
    world = World()
    change(world)
    checkout = only(world.plan(**options))
    (action,) = checkout.actions
    assert (checkout.outcome, checkout.reason, action.skip, action.command) == (CheckoutOutcome.SKIPPED, skip, skip, None)
    assert (world.probe.probed, world.exchanges.observed) == ([], [])


def test_fresh_codex_idle_capture_overrides_stale_working_status() -> None:
    """Q03: a supported idle empty Codex screen lets a stale working pane receive its resume."""
    world = World(snapshots={"c:\\work\\api": snapshot(saved=routing(API, codex_single), role="implementation")})
    world.panes = [live(REQUESTOR_PANE, Host.CODEX)]
    world.activity[REQUESTOR_PANE] = PaneActivity("working", "", draft_held=False, question="", ready=True)
    world.probe.verdicts[REQUESTOR_PANE] = ScreenVerdict.IDLE_EMPTY
    (action,) = only(world.plan()).actions
    assert (action.skip, action.notes, world.probe.probed) == (None, ("stale-working-overridden",), [REQUESTOR_PANE])


@pytest.mark.parametrize(
    ("change", "options", "skip"),
    [
        (replacing(REVIEWER_PANE, live(REVIEWER_PANE, None)), {}, SkipReason.TARGET_NOT_AGENT),
        (unchanged, {"excepts": ("reviewer | pane",)}, SkipReason.EXCLUDED),
        (unchanged, {"caller_pane": REVIEWER_PANE}, SkipReason.CALLER_PANE),
        (active(REVIEWER_PANE, PaneActivity("working", "", draft_held=False, question="", ready=True)), {}, None),
    ],
)
def test_counterpart_is_never_a_shell_and_respects_static_protections(change: Change, options: dict[str, Any], skip: SkipReason | None) -> None:
    """The requestor still resumes; a shell, excluded or caller reviewer gets no command; its activity is checked later."""
    world = World()
    change(world)
    checkout = only(world.plan(**options))
    resume, reviewer = checkout.actions
    assert (checkout.outcome, resume.skip, reviewer.skip, reviewer.command is None) == (CheckoutOutcome.PLANNED, None, skip, skip is not None)


def test_continuation_without_a_usable_reviewer_is_skipped() -> None:
    """A later run with nothing to continue reports the reviewer's skip reason."""
    world = World(snapshots={"c:\\work\\api": snapshot(receipt={"schema": 3})})
    checkout = only(world.plan(excepts=("reviewer | pane",)))
    assert (checkout.outcome, checkout.reason, checkout.actions[0].kind) == (CheckoutOutcome.SKIPPED, SkipReason.EXCLUDED, ActionKind.CONTINUE_REVIEWER)


@pytest.mark.parametrize(
    ("kind", "round_number", "expected"),
    [
        (ExchangeObservationKind.NOT_LIVE, None, (CheckoutOutcome.SKIPPED, SkipReason.EXCHANGE_NOT_LIVE)),
        (ExchangeObservationKind.BUSY, None, (CheckoutOutcome.SKIPPED, SkipReason.EXCHANGE_BUSY)),
        (ExchangeObservationKind.SELECTION_CHANGED, None, (CheckoutOutcome.ERROR, ErrorReason.EXCHANGE_SELECTION_CHANGED)),
        (ExchangeObservationKind.DAMAGED, None, (CheckoutOutcome.ERROR, ErrorReason.EXCHANGE_DAMAGED)),
        (ExchangeObservationKind.OBSERVED, None, (CheckoutOutcome.ERROR, ErrorReason.EXCHANGE_DAMAGED)),
    ],
)
def test_live_exchange_must_be_observed_before_any_marker(kind: ExchangeObservationKind, round_number: int | None, expected: tuple[CheckoutOutcome, object]) -> None:
    """Only an observed exchange with its round and occurrence binds markers; nothing else is guessed."""
    world = World()
    world.exchanges.kind, world.exchanges.round_number = kind, round_number
    plan = world.plan()
    assert verdict(plan) == expected
    assert world.exchanges.observed == ["c:\\work\\api"]
    assert all(action.command is None for action in only(plan).actions)


def test_prompt_less_and_unrooted_panes_are_omitted_and_counted() -> None:
    """Prompt-less checkouts are not reported; their panes, shells and non-targets join the omitted count."""
    world = World()
    world.panes += [live(THIRD_PANE, None, WEB, session="web"), live(THIRD_PANE.replace("5b", "6b"), None, "", session="web")]
    plan = world.plan()
    assert [checkout.root.display for checkout in plan.checkouts] == ["C:\\work\\api"]
    assert (plan.omitted_panes, world.reads) == (2, ["c:\\work\\api", "c:\\work\\web"])


# eof

