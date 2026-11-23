"""Single-checkout replanning tests of the read-only planner.

Step 6 of v0.15.0 resume-paused replans one checkout from a fresh
observation immediately before each send. ``plan_checkout`` returns exactly
what the whole-run planner returns for that checkout, reads only that
checkout, reflects fresh activity, and returns ``None`` when the checkout has
no live pane or no saved prompt any more.
"""

from __future__ import annotations

from itertools import count

from tests.unit.tools.test_resume_paused_planner.planner_world import API, HUMAN, World
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
)
from tools.resume_paused_evidence import PaneActivity, PaneObservation
from tools.resume_paused_models import CanonicalRoot
from tools.resume_paused_plan_model import (
    CheckoutOutcome,
    CheckoutPlan,
    PlanRequest,
    SkipReason,
)
from tools.resume_paused_planner import PlannerPorts, plan_checkout

ROOT = CanonicalRoot.from_path(API)


def replan(world: World, root: CanonicalRoot = ROOT) -> CheckoutPlan | None:
    """Replan one checkout of the declared world with launch ids 1, 2, ..."""
    ids = (f"{number:032x}" for number in count(1))
    ports = PlannerPorts(world.read, world.exchanges, world.history, world.probe, world.journal, lambda: next(ids))
    return plan_checkout(PlanRequest(HUMAN), PaneObservation(tuple(world.panes), world.activity), ports, root)


def test_a_replan_equals_the_whole_run_plan_of_that_checkout() -> None:
    """Same gates, same targets, same markers for the same launch ids."""
    world = World()
    (planned,) = world.plan().checkouts
    assert replan(world) == planned


def test_a_replan_reads_only_its_checkout() -> None:
    """Other checkouts are neither read nor planned."""
    world = World()
    world.reads.clear()
    replan(world)
    assert world.reads == ["c:\\work\\api"]


def test_a_replan_reflects_fresh_activity() -> None:
    """A target that turned busy since planning skips."""
    world = World()
    world.activity[REQUESTOR_PANE] = PaneActivity("working", "", draft_held=False, question="", ready=False)
    replanned = replan(world)
    assert replanned is not None
    assert (replanned.outcome, replanned.reason) == (CheckoutOutcome.SKIPPED, SkipReason.PANE_BUSY)


def test_a_checkout_without_a_live_pane_or_a_prompt_is_not_replanned() -> None:
    """Nothing is left to deliver there."""
    world = World()
    assert replan(world, CanonicalRoot.parse("C:\\work\\gone")) is None
    world.snapshots.clear()
    assert replan(world) is None


# eof
