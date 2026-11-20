"""Generated planner properties: discovery order and exclusion scope.

Step 5 of v0.14.0 resume-paused: the plan of a run never depends on the order
in which TUIOS lists its panes, launch ids included, and no combination of
``--except`` names can lift checkout-wide duplicate protection: a checkout
with a counted resume command after its pause never plans a command, whichever
of its panes, sessions or folder is excluded.
"""

from __future__ import annotations

from datetime import UTC, datetime
from functools import cache
from typing import TYPE_CHECKING

from hypothesis import given, settings
from hypothesis import strategies as st

from tests.unit.tools.test_resume_paused_planner.planner_world import (
    IDLE,
    WEB,
    World,
    live,
    routing,
    snapshot,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    SESSION,
    THIRD_PANE,
    single_agent,
    slot,
)
from tools.resume_paused_evidence import ObservedCommand
from tools.resume_paused_plan_model import CheckoutOutcome
from tools.resume_paused_profiles import Host

if TYPE_CHECKING:
    from tools.resume_paused_artifacts import CheckoutSnapshot
    from tools.resume_paused_plan_model import RunPlan

EXAMPLES = 30
AFTER_PAUSE = datetime(2026, 11, 17, 17, 0, tzinfo=UTC)
WEB_PANE = "9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d"
NAMES = ("api", SESSION, "requestor | pane", "reviewer | pane", "Spare")


def web_single(mapping: dict[str, object]) -> None:
    """Route the web checkout's single-agent pause to its own Codex pane."""
    single_agent(mapping)
    slot(mapping, "resumed").update(host="codex", pane_id=WEB_PANE, session="web", label="Codex web")


@cache
def saved_pauses() -> dict[str, CheckoutSnapshot | Exception]:
    """Parse the two immutable saved pauses once, inside the first test that needs them."""
    return {"c:\\work\\api": snapshot(), "c:\\work\\web": snapshot(WEB, routing(WEB, web_single))}


def two_checkouts() -> World:
    """Declare a paired checkout, a single-agent checkout and spare panes."""
    world = World(snapshots=dict(saved_pauses()))
    world.panes += [
        live(WEB_PANE, Host.CODEX, WEB, session="web", name="Codex web"),
        live(THIRD_PANE, Host.CLAUDE, name="Spare"),
        live(THIRD_PANE.replace("5b", "6b"), None, "", session="web"),
    ]
    world.activity |= {WEB_PANE: IDLE, THIRD_PANE: IDLE}
    return world


@cache
def listed_order_plan() -> RunPlan:
    """Plan the world once in its declared discovery order; the plan is immutable."""
    return two_checkouts().plan(clear=True)


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(order=st.permutations(range(5)))
def test_plan_is_invariant_under_discovery_order(order: list[int]) -> None:
    """Grouping by canonical root and full UUID makes the listing order irrelevant."""
    shuffled = two_checkouts()
    shuffled.panes = [shuffled.panes[index] for index in order]
    assert shuffled.plan(clear=True) == listed_order_plan()


@settings(max_examples=EXAMPLES, database=None, deadline=None)
@given(
    resumed_in=st.sampled_from((REQUESTOR_PANE, REVIEWER_PANE, THIRD_PANE)),
    excluded=st.sets(st.sampled_from(NAMES)),
    switched=st.booleans(),
)
def test_exclusions_never_remove_duplicate_protection(resumed_in: str, excluded: set[str], switched: bool) -> None:  # noqa: FBT001
    """A counted resume in any pane keeps the whole checkout from any planned command."""
    world = two_checkouts()
    world.history.by_pane[resumed_in] = (ObservedCommand("$llm-shared:resume-session", AFTER_PAUSE),)
    plan = world.plan(excepts=tuple(sorted(excluded)), switch_roles=("api",) if switched else ())
    (api,) = [checkout for checkout in plan.checkouts if checkout.root.display == "C:\\work\\api"]
    assert api.outcome is CheckoutOutcome.SKIPPED
    assert all(action.command is None for action in api.actions)


# eof
