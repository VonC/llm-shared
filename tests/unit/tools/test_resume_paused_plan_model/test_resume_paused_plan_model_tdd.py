"""Plan vocabulary tests: run failure and input permission.

Step 5 of v0.14.0 resume-paused: a run fails on any run-wide refusal or any
checkout error, while expected skips and planned checkouts succeed; input is
allowed only in a normal run without a run-wide refusal, never in a dry run,
whatever the checkouts hold.
"""

from __future__ import annotations

import pytest

from tools.resume_paused_artifacts import PromptState
from tools.resume_paused_models import CanonicalRoot
from tools.resume_paused_plan_model import (
    CheckoutOutcome,
    CheckoutPlan,
    ErrorReason,
    GlobalFailure,
    GlobalReason,
    PlanRequest,
    RunPlan,
    SkipReason,
)
from tools.resume_paused_profiles import CallerDecision, CallerOrigin

ROOT = CanonicalRoot.parse("C:\\work\\api")
PLANNED = CheckoutPlan(ROOT, PromptState.UNUSED, CheckoutOutcome.PLANNED)
SKIPPED = CheckoutPlan(ROOT, PromptState.USED, CheckoutOutcome.SKIPPED, SkipReason.ALREADY_USED)
FAILED = CheckoutPlan(ROOT, PromptState.ERROR, CheckoutOutcome.ERROR, ErrorReason.CHECKOUT_UNREADABLE)
REFUSED = (GlobalFailure(GlobalReason.EXCEPT_UNMATCHED, ("nowhere",)),)


@pytest.mark.parametrize(
    ("plan", "failed", "input_allowed"),
    [
        (RunPlan(dry_run=False, failures=(), checkouts=(PLANNED, SKIPPED)), False, True),
        (RunPlan(dry_run=False, failures=(), checkouts=(PLANNED, FAILED)), True, True),
        (RunPlan(dry_run=True, failures=(), checkouts=(PLANNED,)), False, False),
        (RunPlan(dry_run=False, failures=REFUSED), True, False),
        (RunPlan(dry_run=False, failures=()), False, True),
    ],
)
def test_run_verdict_separates_failure_from_input_permission(plan: RunPlan, failed: bool, input_allowed: bool) -> None:  # noqa: FBT001
    """Skips succeed, checkout errors fail without stopping others, refusals and previews allow no input."""
    assert (plan.failed, plan.input_allowed) == (failed, input_allowed)


def test_request_defaults_are_a_plain_normal_run() -> None:
    """A request without options is a normal run with no clear, exclusion, switch or caller pane."""
    request = PlanRequest(CallerDecision(CallerOrigin.UNPROVED, ()))
    assert (request.caller_pane, request.dry_run, request.clear, request.excepts, request.switch_roles) == (None, False, False, (), ())


# eof
