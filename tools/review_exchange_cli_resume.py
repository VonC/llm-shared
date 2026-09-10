"""Typed support operations used by the LLM-only review-resume skill.

Step 5 keeps resume sequencing in its canonical instruction while this adapter
exposes bounded migration, non-mutating inspection, and the one quiet global
reviewer wait through the existing review-exchange launcher. Lease-only
abandonment remains resumable without weakening migration or damage gates.
"""


from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from tools.llm_nature import LlmNature, LlmNatureDetector
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_migration import (
    MigrationCheckResult,
    ReviewArtifactMigration,
)
from tools.review_exchange_cli_ownership import capability_from_args, capability_payload
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ReviewContext,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_ownership import OwnershipRejectedError
from tools.review_exchange_paths import derive_artifact_paths, load_review_configuration
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_resume import (
    ResumeContext,
    ResumeDecisionOutcome,
    ResumeExchange,
    ReviewResumeService,
    can_resume_expired_leases,
)
from tools.review_resume_identity import claim_discovered_request, claim_selected
from tools.review_resume_notifications import WatchdogNotificationAdapter
from tools.review_resume_wait import (
    GlobalReviewerWait,
    GlobalWaitOutcome,
)
from tools.review_status import collect_ready_review_requests, collect_review_status
from tools.review_status_models import (
    ExchangeStatus,
    ReviewStatusOutcome,
    RoleNatureState,
)

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Callable, Mapping, Sequence
    from pathlib import Path

    from tools.review_exchange_ownership import OwnershipCapability
    from tools.review_status_models import ReviewStatusResult


_RESUME_OPERATIONS = frozenset(
    {"migration-check", "migrate-artifacts", "resume-inspect", "claim", "wait-any-request"},
)


def is_resume_operation(operation: str) -> bool:
    """Return whether the parsed operation belongs to the resume adapter."""
    return operation in _RESUME_OPERATIONS


def _wall_clock() -> datetime:
    """Return the local timezone-aware status timestamp for one rescan."""
    return datetime.now().astimezone()


def execute_resume_operation(
    args: Namespace,
    project_root: Path,
) -> tuple[dict[str, Any], int]:
    """Run one resume support operation and return its final JSON payload."""
    operation = args.operation
    if operation == "migration-check":
        return _migration_payload(operation, ReviewArtifactMigration(project_root=project_root).migration_check())
    if operation == "migrate-artifacts":
        migration = ReviewArtifactMigration(project_root=project_root)
        checked = migration.migration_check()
        if checked.state.value == "blocked":
            return _migration_payload(operation, checked, exit_code=2)
        return _migration_payload(operation, migration.migrate(checked))
    if operation == "resume-inspect":
        return _resume_inspect(args, project_root)
    if operation == "claim":
        return _resume_claim(args, project_root)
    if operation == "wait-any-request":
        return _terminal_wait(args, project_root)
    message = f"unsupported resume operation: {operation}"
    raise ReviewExchangeError(message)


def _terminal_wait(args: Namespace, project_root: Path) -> tuple[dict[str, Any], int]:
    """Contain host cancellation and operational failures at the terminal JSON boundary."""
    operation = args.operation
    try:
        return _wait_any_request(args, project_root)
    except KeyboardInterrupt:
        return {"operation": operation, "outcome": "cancelled", "identity": None,
                "candidates": [], "diagnostic": "foreground wait was cancelled"}, 3
    except Exception as error:  # noqa: BLE001 - one terminal result for operational failures
        return {"operation": operation, "outcome": "operational-failure", "identity": None,
                "candidates": [], "diagnostic": str(error)}, 2


def _migration_payload(
    operation: str,
    result: MigrationCheckResult,
    *,
    exit_code: int | None = None,
) -> tuple[dict[str, Any], int]:
    """Render the bounded migration evidence without full status projection."""
    code = exit_code if exit_code is not None else (0 if result.state.value == "ready" else 3)
    return (
        {
            "diagnostic": "; ".join(result.diagnostics) or None,
            "identity": None,
            "operation": operation,
            "outcome": result.state.value,
            "artifact_home": result.configuration.relative_home,
            "candidates": [],
        },
        code,
    )


def _status_allows_resume(status: ReviewStatusResult) -> bool:
    """Apply pure lease-recovery policy to a successfully projected artifact home."""
    return status.outcome is ReviewStatusOutcome.TRUSTWORTHY or (
        status.outcome is ReviewStatusOutcome.UNTRUSTWORTHY
        and can_resume_expired_leases(tuple(
            entry.state if isinstance(entry, ExchangeStatus) else None
            for entry in status.exchanges
        ))
    )


def _resume_inspect(args: Namespace, root: Path) -> tuple[dict[str, Any], int]:
    """Collect typed status once and return a pure role-routing decision."""
    status = collect_review_status(root, _wall_clock)
    if not _status_allows_resume(status):
        message = "resume inspection requires trustworthy review status"
        raise ReviewExchangeError(message)
    detected = LlmNatureDetector().detect(
        os.environ,
        trusted_hint=args.trusted_host_hint,
    )
    exchanges = _selected_exchanges(status.exchanges, args, root)
    decision = ReviewResumeService().decide(
        detected.nature,
        tuple(_resume_exchange(entry) for entry in exchanges),
        forced_role=(None if args.role is None else ReviewRole(args.role)),
        override=getattr(args, "override", False),
    )
    return (
        {
            "diagnostic": detected.diagnostic,
            "identity": exchanges[0].identity.to_dict() if len(exchanges) == 1 else None,
            "operation": args.operation,
            "outcome": decision.outcome.value,
            "role": None if decision.role is None else decision.role.value,
            "action": None if decision.action is None else decision.action.value,
            "candidates": [_candidate_payload(entry) for entry in exchanges],
        },
        0 if decision.outcome.value == "ready" else 3,
    )


def _resume_exchange(entry: ExchangeStatus) -> ResumeExchange:
    """Reduce status role evidence to the pure service's nullable nature facts."""
    return ResumeExchange(
        entry.state,
        _known_nature(entry.requestor_llm_nature.value),
        _known_nature(entry.reviewer_llm_nature.value),
        entry.requestor_llm_nature.value is RoleNatureState.CONFLICTING,
        entry.reviewer_llm_nature.value is RoleNatureState.CONFLICTING,
    )


def _known_nature(value: object) -> LlmNature | None:
    """Keep recorded host natures and map status-only values to legacy absence."""
    return value if isinstance(value, LlmNature) else None


def _resume_claim(args: Namespace, root: Path) -> tuple[dict[str, Any], int]:
    """Resolve a fresh exact selection before the authorized automatic pickup."""
    status = collect_review_status(root, _wall_clock)
    if not _status_allows_resume(status):
        message = "resume claim requires trustworthy review status"
        raise ReviewExchangeError(message)
    exchanges = _selected_exchanges(status.exchanges, args, root)
    if len(exchanges) != 1:
        message = "resume claim requires one current exchange"
        raise ReviewExchangeError(message)
    entry = exchanges[0]
    if entry.round_number != args.round_number or entry.occurrence != args.occurrence:
        message = "resume selection changed; inspect again"
        raise ReviewExchangeError(message)
    nature = LlmNatureDetector().detect(os.environ, trusted_hint=args.trusted_host_hint).nature
    context = _context_from_status(root, entry)
    artifact_configuration = ReviewArtifactConfiguration.load(root)
    configuration = load_review_configuration(root, configuration=artifact_configuration)
    paths = derive_artifact_paths(root, context, configuration=artifact_configuration)
    store = ReviewExchangeStore(paths)
    record = store.read_coordination(required=True)
    if record is None:
        message = "resume pickup requires durable coordination"
        raise ReviewExchangeError(message)
    core = ReviewExchangeCore(store, context, record.policy, configuration)
    core.present_ownership(capability_from_args(args))

    def acquire(role: ReviewRole) -> OwnershipCapability:
        """Keep backfill, claim and the secret inside the selected invocation."""
        return claim_selected(
            core, role, nature, round_number=entry.round_number,
            occurrence=entry.occurrence, override=args.override,
        )

    resolution = ReviewResumeService().resume(
        ResumeContext(nature, (_resume_exchange(entry),), ReviewRole(args.role), args.override), acquire,
    )
    payload: dict[str, Any] = {
        "operation": "claim", "outcome": resolution.decision.outcome.value,
        "identity": entry.identity.to_dict(), "candidates": [_candidate_payload(entry)],
        "diagnostic": None, "role": args.role,
        "action": None if resolution.decision.action is None else resolution.decision.action.value,
    }
    if resolution.capability is not None:
        payload.update(capability_payload(resolution.capability))
    return payload, 0 if resolution.decision.outcome is ResumeDecisionOutcome.READY else 3


def _selected_exchanges(entries: Sequence[object], args: Namespace, root: Path) -> tuple[ExchangeStatus, ...]:
    """Apply a human-selected exact document without filename ordering guesses."""
    document = getattr(args, "document", None)
    result = tuple(
        entry for entry in entries if isinstance(entry, ExchangeStatus)
        and (document is None or (root / entry.reviewed_document).resolve() == (root / document).resolve())
        and (getattr(args, "implementation_step", None) is None or entry.implementation_step == args.implementation_step)
    )
    if document is not None and not result:
        message = "selected exchange is no longer active; inspect again"
        raise ReviewExchangeError(message)
    return result


@dataclass
class _RequestDiscovery:
    """Discover and atomically claim pending reviewer requests for one home."""

    project_root: Path
    wall_clock: Callable[[], datetime] = _wall_clock

    def __post_init__(self) -> None:
        """Keep claims process-local so waiting creates no durable waiter record."""
        self._capabilities: dict[int, Mapping[str, object]] = {}
        self.configuration = ReviewArtifactConfiguration.load(self.project_root)

    def rescan(self) -> tuple[ExchangeStatus, ...]:
        """Return every pending request after one authoritative status projection."""
        status = collect_ready_review_requests(self.project_root, self.wall_clock, self.configuration)
        if not _status_allows_resume(status):
            message = "global wait requires trustworthy review status"
            raise ReviewExchangeError(message)
        return tuple(
            entry
            for entry in status.exchanges
            if isinstance(entry, ExchangeStatus) and entry.state in {ArtifactState.REQUEST_PENDING, ArtifactState.ABANDONED_REQUEST}
        )

    def claim(self, candidate: object) -> bool:
        """Try the normal locked reviewer claim and retain only its process secret."""
        if not isinstance(candidate, ExchangeStatus):
            message = "global wait candidate is not a review exchange"
            raise ReviewExchangeError(message)
        context = _context_from_status(self.project_root, candidate)
        artifact_configuration = self.configuration
        configuration = load_review_configuration(
            self.project_root,
            configuration=artifact_configuration,
        )
        paths = derive_artifact_paths(
            self.project_root,
            context,
            configuration=artifact_configuration,
        )
        store = ReviewExchangeStore(paths)
        record = store.read_coordination(required=True)
        if record is None or record.expected_next_actor is not Actor.REVIEWER:
            return False
        core = ReviewExchangeCore(store, context, record.policy, configuration)
        try:
            capability = claim_discovered_request(core, candidate.round_number, candidate.occurrence)
        except OwnershipRejectedError as error:
            if error.failure.code == "already-claimed":
                return False
            raise
        if capability is None:
            return False
        capability_data: dict[str, object] = dict(capability_payload(capability))
        self._capabilities[id(candidate)] = capability_data
        return True

    def capability(self, candidate: object) -> dict[str, object]:
        """Return a found request's session-only ownership capability once."""
        try:
            return dict(self._capabilities[id(candidate)])
        except KeyError as error:
            message = "found request has no ownership capability"
            raise ReviewExchangeError(message) from error


def _wait_any_request(args: Namespace, root: Path) -> tuple[dict[str, Any], int]:
    """Run the silent global wait and render its one terminal machine object."""
    status = collect_review_status(root, _wall_clock)
    if not _status_allows_resume(status):
        message = "global wait requires ready migration and trustworthy status"
        raise ReviewExchangeError(message)
    discovery = _RequestDiscovery(root)
    configuration = ReviewArtifactConfiguration.load(root)
    notification_wait = WatchdogNotificationAdapter(configuration.home)
    waiter = GlobalReviewerWait(
        rescan_candidates=discovery.rescan,
        wait_for_notification=notification_wait.wait,
        fallback_poll=_no_op_poll,
        claim_candidate=discovery.claim,
        poll_interval_seconds=args.poll_interval,
    )
    with notification_wait:
        result = waiter.wait()
    candidates = [_candidate_payload(item) for item in result.candidates if isinstance(item, ExchangeStatus)]
    selected = result.candidate if isinstance(result.candidate, ExchangeStatus) else None
    payload: dict[str, Any] = {
        "diagnostic": result.diagnostic,
        "identity": None if selected is None else selected.identity.to_dict(),
        "operation": args.operation,
        "outcome": result.outcome.value,
        "candidates": candidates,
    }
    if result.outcome is GlobalWaitOutcome.FOUND:
        payload.update(discovery.capability(result.candidate))
        return payload, 0
    return payload, 3


def _context_from_status(root: Path, entry: ExchangeStatus) -> ReviewContext:
    """Rebuild an exact context from trusted repository-relative status paths."""
    return ReviewContext(
        entry.identity,
        root / entry.reviewed_document,
        None if entry.umbrella is None else root / entry.umbrella,
        entry.implementation_step,
    )


def _candidate_payload(entry: ExchangeStatus) -> dict[str, object]:
    """Render selection evidence without exposing ownership capability material."""
    return {
        "identity": entry.identity.to_dict(),
        "document": entry.reviewed_document,
        "round": entry.round_number,
        "occurrence": entry.occurrence,
        "umbrella": entry.umbrella,
        "implementation_step": entry.implementation_step,
        "state": entry.state.value,
        "requestor_llm_nature": entry.requestor_llm_nature.value.value,
        "reviewer_llm_nature": entry.reviewer_llm_nature.value.value,
        "requestor_evidence": entry.requestor_llm_nature.evidence_dicts(),
        "reviewer_evidence": entry.reviewer_llm_nature.evidence_dicts(),
    }


def _no_op_poll() -> None:
    """Mark a fallback boundary without streaming progress or mutating evidence."""


__all__ = ["execute_resume_operation", "is_resume_operation"]


# eof
