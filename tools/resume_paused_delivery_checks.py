"""Fresh pre-send checks of the guarded bulk delivery.

Step 6 of v0.15.0 resume-paused revalidates every send, under the held
checkout guard, from one fresh observation taken immediately before it:

- ``target_refusal`` (always applied by the delivery): the planned full pane
  UUID is listed exactly once, in its saved TUIOS session, still runs the
  planned host in the planned checkout (design Q10), is neither the caller's
  pane nor an excluded session or pane label, and may take input now: before a
  clear, a resume or a reviewer command it must be eligible as Step 5 decides
  (busy, blocked, question, draft, not-ready and unknown panes skip; a busy
  Codex pane needs a supported idle, empty-input capture). Before the single
  Codex recovery Enter, the pane holds this run's own unsubmitted command, so
  only a blocked or draft-holding pane, an idle pane that is not ready or an
  unknown state refuses it; the delivery's two identical captures stand in
  for the screen probe.
- ``PlanRecheck`` (an injected check Step 8 composes): replans the checkout
  through the Step 5 planner from the same fresh observation, so a changed
  prompt or digest, a later duplicate resume, changed routing, a moved
  exchange or a new protection refuses the send. The replanned action must
  carry the same native command and marker identity (pane, role and
  assignment binding; only the launch id is fresh). Before the recovery Enter,
  the target's own activity is read as ready, so only its unsubmitted command
  is discounted, never a duplicate or a routing change.

Nothing here sends input or writes a file.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.resume_paused_delivery_model import Phase, Refusal
from tools.resume_paused_evidence import (
    Activity,
    PaneActivity,
    PaneObservation,
    input_eligibility,
)
from tools.resume_paused_input import pane_host
from tools.resume_paused_marker import MARKER_FLAG, marker_in_command
from tools.resume_paused_models import ArtifactError, CanonicalRoot, SessionRole
from tools.resume_paused_plan_model import ActionKind, CheckoutOutcome

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.resume_paused_delivery_model import SendStep
    from tools.resume_paused_evidence import ScreenProbe
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_plan_model import CheckoutPlan, PlannedAction, PlanRequest

_ACTIVITY_REASONS: Final = {
    Activity.BUSY: "pane-busy",
    Activity.BLOCKED: "pane-blocked",
    Activity.DRAFT: "pane-draft",
    Activity.NOT_READY: "pane-not-ready",
    Activity.UNKNOWN: "pane-state-unknown",
}
_IDLE_STATES: Final = frozenset({"idle", "done"})
_RECOVERY_STATES: Final = _IDLE_STATES | {"working"}
_READY: Final = PaneActivity("idle", "", draft_held=False, question="", ready=True)

type _Identity = tuple[str, str, SessionRole, str]


def _locate(observation: PaneObservation, action: PlannedAction) -> PaneRecord | Refusal:
    """Return the one live record of the planned UUID."""
    records = [pane for pane in observation.panes if pane.pane_id == action.pane_id]
    if len(records) != 1:
        return Refusal("pane-ambiguous", failed=True) if records else Refusal("target-absent")
    return records[0]


def _identify(pane: PaneRecord, action: PlannedAction, root: CanonicalRoot) -> Refusal | None:
    """Require the planned session, host and checkout; a shell pane is no agent."""
    if pane.session != action.session:
        return Refusal("target-session-changed", failed=True)
    try:
        host = pane_host(pane)
    except ArtifactError:
        return Refusal("host-contradictory", failed=True)
    if host is None:
        return Refusal("target-not-agent")
    if host is not action.host:
        return Refusal("target-host-changed", failed=True)
    try:
        checkout = CanonicalRoot.parse(pane.cwd, "pane checkout")
    except ArtifactError:
        return Refusal("target-identity-unavailable")
    return None if checkout == root else Refusal("target-checkout-changed", failed=True)


def _protect(pane: PaneRecord, caller_pane: str | None, excepts: frozenset[str]) -> Refusal | None:
    """Protect the caller's pane and every excluded session or pane label."""
    if pane.pane_id == caller_pane:
        return Refusal("caller-pane")
    if pane.session.casefold() in excepts or pane.name.casefold() in excepts:
        return Refusal("excluded")
    return None


def _recovery_ready(activity: PaneActivity | None) -> Refusal | None:
    """Refuse the recovery Enter to a blocked, draft-holding, not-ready or unknown pane."""
    if activity is None or activity.state not in _RECOVERY_STATES:
        return Refusal("pane-state-unknown")
    if activity.blocked:
        return Refusal("pane-blocked")
    if activity.draft_held:
        return Refusal("pane-draft")
    if activity.state in _IDLE_STATES and activity.ready is not True:
        return Refusal("pane-not-ready")
    return None


@dataclass(frozen=True)
class TargetContext:
    """What every send of one checkout is checked against: its root, the caller's pane, exclusions and the probe."""

    root: CanonicalRoot
    caller_pane: str | None
    excepts: frozenset[str]
    probe: ScreenProbe

    @classmethod
    def of(cls, root: CanonicalRoot, request: PlanRequest, probe: ScreenProbe) -> TargetContext:
        """Fold the run's exclusion names once for the checkout."""
        return cls(root, request.caller_pane, frozenset(name.casefold() for name in request.excepts), probe)


def target_refusal(phase: Phase, action: PlannedAction, observation: PaneObservation, context: TargetContext) -> PaneRecord | Refusal:
    """Return the fresh target record when it may take this send, or why it may not."""
    located = _locate(observation, action)
    if isinstance(located, Refusal):
        return located
    refusal = _identify(located, action, context.root) or _protect(located, context.caller_pane, context.excepts)
    if refusal is not None:
        return refusal
    activity = observation.activity.get(located.pane_id)
    if phase is Phase.RECOVERY:
        refusal = _recovery_ready(activity)
    else:
        eligibility = input_eligibility(located, action.host, activity, context.probe)
        refusal = None if eligibility.activity is Activity.ELIGIBLE else Refusal(_ACTIVITY_REASONS[eligibility.activity])
    return located if refusal is None else refusal


def _identity(command: str) -> _Identity | None:
    """Return the native command and the marker's pane, role and binding; the launch id is left out."""
    try:
        marker = marker_in_command(command)
    except ArtifactError:
        return None
    return command.split(MARKER_FLAG, 1)[0].strip(), marker.pane_id, marker.role, marker.binding


def _reviewer(kind: ActionKind) -> bool:
    """Return whether the action activates a reviewer, initially or as a later continuation."""
    return kind is not ActionKind.RESUME


def _same(candidate: PlannedAction, action: PlannedAction) -> bool:
    """Return whether a replanned action is the planned one, launch id aside."""
    if candidate.command is None or action.command is None:
        return False
    target = (candidate.role, candidate.host, candidate.session, candidate.pane_id, candidate.clear, _reviewer(candidate.kind))
    planned = (action.role, action.host, action.session, action.pane_id, action.clear, _reviewer(action.kind))
    identity = _identity(action.command)
    return target == planned and identity is not None and _identity(candidate.command) == identity


class PlanRecheck:
    """``PreSendCheck`` that replans the checkout from the step's fresh observation.

    ``replan`` is the Step 5 planner bound to the run's request and readers,
    for one checkout (``tools.resume_paused_planner.plan_checkout``).
    """

    def __init__(self, replan: Callable[[CanonicalRoot, PaneObservation], CheckoutPlan | None]) -> None:
        """Keep the single-checkout planner."""
        self._replan = replan

    def check(self, step: SendStep) -> Refusal | None:
        """Refuse the send unless the fresh plan still holds the same action."""
        observation = step.observation
        if step.phase is Phase.RECOVERY:
            observation = PaneObservation(observation.panes, {**observation.activity, step.action.pane_id: _READY})
        plan = self._replan(step.root, observation)
        if plan is None:
            return Refusal("checkout-unplanned")
        if plan.outcome is not CheckoutOutcome.PLANNED:
            return Refusal(str(plan.reason), failed=plan.outcome is CheckoutOutcome.ERROR)
        if any(_same(candidate, step.action) for candidate in plan.actions):
            return None
        return Refusal("plan-changed", failed=True)


__all__ = [
    "PlanRecheck",
    "TargetContext",
    "target_refusal",
]


# eof
