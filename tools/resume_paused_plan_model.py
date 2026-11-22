"""Immutable plan vocabulary of the human-launched bulk resume.

Step 5 of v0.14.0 resume-paused separates the typed result of planning from
the planner that builds it (``tools.resume_paused_planner``), so preview
reporting (Step 8), guarded delivery (Step 6) and takeover observation
(Step 7) share one model:

- ``PlanRequest``: the human launch, its caller classification and pane,
  preview and clear flags, ``--except`` and ``--switch-roles`` names;
- ``GlobalReason`` and ``GlobalFailure``: run-wide refusals with no input
  anywhere, the agent caller included in a dry run;
- ``SkipReason`` (expected, successful) and ``ErrorReason`` (classification
  failure of one checkout, independent checkouts continue);
- ``PlannedAction``: one planned marked command to one saved target, or the
  reason that target gets none; reviewer actions are conditional on proved
  requestor takeover;
- ``CheckoutPlan`` and ``RunPlan``: one result per prompt-bearing checkout,
  with its duplicate evidence, and the omitted-pane count.

Fix (Step 7 code review round 1): ``CheckoutPlan.digest`` records the digest
of the saved prompt the plan accepted, so the takeover observes consumption
of that exact prompt: an older receipt keeps it waiting, and a prompt changed
since planning fails it, even before any receipt exists.

The module holds values only: no IO, no input and no argument parsing.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.resume_paused_artifacts import PromptState
    from tools.resume_paused_evidence import DuplicateEvidence
    from tools.resume_paused_models import CanonicalRoot, PromptDigest, SessionRole
    from tools.resume_paused_profiles import CallerDecision, Host


class GlobalReason(StrEnum):
    """Why a whole run plans nothing and allows no input anywhere."""

    AGENT_CALLER = "agent-caller"
    DISCOVERY_FAILED = "discovery-failed"
    EXCEPT_UNMATCHED = "except-unmatched"
    SWITCH_UNMATCHED = "switch-unmatched"


class SkipReason(StrEnum):
    """Expected reasons a checkout or one of its targets receives no input."""

    EXCLUDED = "excluded"
    CALLER_PANE = "caller-pane"
    ALREADY_USED = "already-used"
    SWITCH_REQUIRED = "switch-required"
    JOURNAL_RESUMED = "journal-resumed"
    ALREADY_RESUMING = "already-resuming"
    OVERRIDE_PENDING = "override-pending"
    ROUTING_MISSING = "routing-missing"
    ROUTING_TABLE_ONLY = "routing-table-only"
    ROUTING_UNRESOLVED = "routing-unresolved"
    PAIRING_AMBIGUOUS = "pairing-ambiguous"
    UNSUPPORTED_PAUSER = "unsupported-pauser"
    TARGET_ABSENT = "target-absent"
    TARGET_NOT_AGENT = "target-not-agent"
    TARGET_IDENTITY_UNAVAILABLE = "target-identity-unavailable"
    PANE_BLOCKED = "pane-blocked"
    PANE_DRAFT = "pane-draft"
    PANE_NOT_READY = "pane-not-ready"
    PANE_BUSY = "pane-busy"
    PANE_STATE_UNKNOWN = "pane-state-unknown"
    EXCHANGE_NOT_LIVE = "exchange-not-live"
    EXCHANGE_BUSY = "exchange-busy"


class ErrorReason(StrEnum):
    """Classification failures of one checkout; independent checkouts continue."""

    CHECKOUT_UNREADABLE = "checkout-unreadable"
    EVIDENCE_INVALID = "evidence-invalid"
    ROUTING_INVALID = "routing-invalid"
    DUPLICATE_UNCERTAIN = "duplicate-uncertain"
    SWITCH_NOT_APPLICABLE = "switch-not-applicable"
    SWITCH_MISMATCH = "switch-mismatch"
    PANE_AMBIGUOUS = "pane-ambiguous"
    HOST_CONTRADICTORY = "host-contradictory"
    TARGET_HOST_CHANGED = "target-host-changed"
    TARGET_SESSION_CHANGED = "target-session-changed"
    TARGET_CHECKOUT_CHANGED = "target-checkout-changed"
    EXCHANGE_SELECTION_CHANGED = "exchange-selection-changed"
    EXCHANGE_DAMAGED = "exchange-damaged"


class CheckoutOutcome(StrEnum):
    """The classified result of one prompt-bearing checkout."""

    PLANNED = "planned"
    SKIPPED = "skipped"
    ERROR = "error"


class ActionKind(StrEnum):
    """Planned input actions; reviewer actions wait on proved requestor takeover."""

    RESUME = "resume"
    REVIEWER = "reviewer"
    CONTINUE_REVIEWER = "continue-reviewer"


@dataclass(frozen=True)
class PlanRequest:
    """The human launch: caller classification and pane, preview, clear, exclusions and switches."""

    caller: CallerDecision
    caller_pane: str | None = None
    dry_run: bool = False
    clear: bool = False
    excepts: tuple[str, ...] = ()
    switch_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlannedAction:
    """One planned input to one saved target, or the reason it gets none."""

    kind: ActionKind
    role: SessionRole
    host: Host
    session: str
    pane_id: str
    label: str
    command: str | None = None
    clear: bool = False
    conditional: bool = False
    skip: SkipReason | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class CheckoutPlan:
    """The immutable classified plan of one prompt-bearing checkout.

    ``digest`` is the accepted saved prompt's digest, ``None`` when no prompt
    was read.
    """

    root: CanonicalRoot
    prompt_state: PromptState
    outcome: CheckoutOutcome
    reason: SkipReason | ErrorReason | None = None
    detail: str = ""
    title: str | None = None
    author: str | None = None
    paused_at: str | None = None
    switched: bool = False
    actions: tuple[PlannedAction, ...] = ()
    duplicates: tuple[DuplicateEvidence, ...] = ()
    digest: PromptDigest | None = None


@dataclass(frozen=True)
class GlobalFailure:
    """One run-wide refusal, with the names or caller signals behind it."""

    reason: GlobalReason
    names: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunPlan:
    """Every prompt-bearing checkout's plan, the omitted-pane count and any run-wide refusal."""

    dry_run: bool
    failures: tuple[GlobalFailure, ...]
    checkouts: tuple[CheckoutPlan, ...] = ()
    omitted_panes: int = 0

    @property
    def failed(self) -> bool:
        """Return whether the run fails: a run-wide refusal or a checkout error."""
        return bool(self.failures) or any(checkout.outcome is CheckoutOutcome.ERROR for checkout in self.checkouts)

    @property
    def input_allowed(self) -> bool:
        """Return whether any input may follow: never in a dry run or after a run-wide refusal."""
        return not self.dry_run and not self.failures


__all__ = [
    "ActionKind",
    "CheckoutOutcome",
    "CheckoutPlan",
    "ErrorReason",
    "GlobalFailure",
    "GlobalReason",
    "PlanRequest",
    "PlannedAction",
    "RunPlan",
    "SkipReason",
]


# eof
