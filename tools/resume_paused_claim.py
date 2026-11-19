"""Marked claim adaptation for the resume-paused receiving workflows.

Step 4 of v0.14.0 resume-paused connects a marked resume to the existing
locked selected claim (design Q04=A). ``marked_claim_verifier`` returns the
callable that ``claim_selected`` runs under the transition lock, before any
backfill or ownership write. It parses the raw marker again, requires the
claimed role to be the marker's role and, for a Codex claimant, the session
identity and launch id carried from its first validation, with the launch id
equal to the marker's. It then rereads the checkout's saved pause, rebuilds the
assignment from the current prompt, saved routing and the locked exchange round
and occurrence, and requires the same exact exchange, the claimant host and
the marker binding. The receipt must show consumption: the requestor's own
schema 3 receipt for this launch, pane and binding, or for a reviewer the
requestor's schema 3 receipt for the prompt's bytes.

A refusal raises before anything is written, naming one reason code. The
verifier returns only non-secret evidence for the coordination record. It
reads no host session file and needs no TUIOS: the separate fresh validator
call before the claim supplies the pane and complete-input proof.

Fix (code review round 1): an error checkout snapshot, such as one whose
receipt names another checkout, keeps the prompt, routing and receipt it parsed
before failing. The verifier refuses it as ``checkout-unreadable`` before using
any of them, and the receipt-consumption checks never read an error snapshot.
"""

# ruff: noqa: EM101

from __future__ import annotations

import os
from typing import TYPE_CHECKING, cast

from tools.llm_nature import LlmNature
from tools.resume_paused_artifacts import (
    PromptState,
    RoutingState,
    read_checkout_snapshot,
)
from tools.resume_paused_input import CarriedIdentity
from tools.resume_paused_marker import (
    Assignment,
    LiveExchange,
    Marker,
    resolve_assignment,
)
from tools.resume_paused_models import ArtifactError, SessionRole
from tools.resume_paused_profiles import Host
from tools.review_exchange_models import ReviewExchangeError, ReviewRole
from tools.review_exchange_models_coordination import MarkedClaimEvidence

if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path

    from tools.resume_paused_artifacts import CheckoutSnapshot, UsageReceipt
    from tools.resume_paused_marker import AssignedExchange
    from tools.review_exchange_models import ReviewContext
    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_resume_identity import MarkedClaimVerifier

_HOSTS = {LlmNature.CLAUDE: Host.CLAUDE, LlmNature.CODEX: Host.CODEX}
_MARKED_SCHEMA = 3


def _refused(code: str) -> ReviewExchangeError:
    """Build the typed refusal one marked claim reports."""
    return ReviewExchangeError(f"marked claim refused: {code}")


def _require_carried(host: Host, marker: Marker, carried: CarriedIdentity | None) -> None:
    """Require a Codex claimant's carried identity and refuse any other launch id."""
    if host is Host.CODEX and (carried is None or not carried.session_id or not carried.launch_id):
        raise ArtifactError("carried-identity-missing")
    if carried is not None and carried.launch_id and carried.launch_id != marker.launch_id:
        raise ArtifactError("carried-launch-id-mismatch")


def _assignment(snapshot: CheckoutSnapshot, marker: Marker, record: CoordinationRecord, occurrence: int) -> Assignment:
    """Rebuild the assignment from the current saved pause and the locked exchange.

    An error snapshot keeps the fields it parsed before failing, such as a
    receipt naming another checkout; it is refused before any of them is used.
    """
    if snapshot.state is PromptState.ERROR:
        raise ArtifactError("checkout-unreadable")
    prompt, routing = snapshot.prompt, snapshot.routing
    if prompt is None or routing is None:
        raise ArtifactError("prompt-unavailable")
    if routing.state is not RoutingState.RESOLVED or routing.routing is None:
        raise ArtifactError("routing-unresolved")
    live = LiveExchange(occurrence, record.round_number)
    return resolve_assignment(routing.routing, prompt.digest, marker.pane_id, marker.role, live)


def _same_path(root: Path, relative: str | None, absolute: Path | None) -> bool:
    """Compare a saved checkout-relative path with a context path by the filesystem's rules."""
    if relative is None or absolute is None:
        return relative is None and absolute is None
    return os.path.normcase(os.path.normpath(root / relative)) == os.path.normcase(os.path.normpath(absolute))


def _require_exchange(assignment: Assignment, context: ReviewContext, root: Path) -> None:
    """Require the saved exchange to be exactly the locked exchange.

    The assignment was resolved with the locked live exchange, which
    ``resolve_assignment`` refuses for a single-agent pause, so it names one.
    """
    saved = cast("AssignedExchange", assignment.exchange).saved
    same = (
        saved.identity() == context.identity
        and _same_path(root, saved.document, context.document_path)
        and saved.implementation_step == context.implementation_step
        and _same_path(root, saved.umbrella, context.umbrella_path)
    )
    if not same:
        raise ArtifactError("exchange-mismatch")


def _marked_receipt(snapshot: CheckoutSnapshot) -> UsageReceipt | None:
    """Return the schema 3 receipt that consumed the current prompt bytes, if any; never from an error snapshot."""
    receipt, prompt = snapshot.receipt, snapshot.prompt
    if snapshot.state is PromptState.ERROR or receipt is None or prompt is None:
        return None
    return receipt if receipt.schema == _MARKED_SCHEMA and receipt.digest == prompt.digest else None


def consumed_by(snapshot: CheckoutSnapshot, marker: Marker) -> bool:
    """Return whether this marker's own schema 3 receipt consumed the current prompt."""
    receipt = _marked_receipt(snapshot)
    return receipt is not None and (receipt.launch_id, receipt.receiving_pane, receipt.assignment_binding) == (
        marker.launch_id,
        marker.pane_id,
        marker.binding,
    )


def requestor_consumed(snapshot: CheckoutSnapshot, assignment: Assignment) -> bool:
    """Return whether the assignment's requestor pane consumed the current prompt."""
    receipt = _marked_receipt(snapshot)
    return receipt is not None and assignment.pair is not None and receipt.receiving_pane == assignment.pair[0].pane_id


def _require_receipt(snapshot: CheckoutSnapshot, marker: Marker, assignment: Assignment) -> None:
    """Require the receipt that consumed this prompt for the claimed role."""
    if marker.role is SessionRole.REVIEWER:
        if not requestor_consumed(snapshot, assignment):
            raise ArtifactError("requestor-receipt-missing")
    elif not consumed_by(snapshot, marker):
        raise ArtifactError("receipt-not-bound")


def _evidence(  # noqa: PLR0913 - the locked record, its occurrence and the four claim inputs
    project_root: Path, raw_marker: str, role: ReviewRole, host: Host, carried: CarriedIdentity | None,
    record: CoordinationRecord, occurrence: int,
) -> MarkedClaimEvidence:
    """Verify one marked claim against current evidence and return what it records."""
    marker = Marker.parse(raw_marker)
    if marker.role.value != role.value:
        raise ArtifactError("marker-role-mismatch")
    _require_carried(host, marker, carried)
    snapshot = read_checkout_snapshot(project_root)
    assignment = _assignment(snapshot, marker, record, occurrence)
    _require_exchange(assignment, record.context, project_root)
    if assignment.receiver.host is not host:
        raise ArtifactError("host-mismatch")
    if assignment.digest() != marker.binding:
        raise ArtifactError("binding-mismatch")
    _require_receipt(snapshot, marker, assignment)
    return MarkedClaimEvidence(marker.launch_id, marker.pane_id, host.value, marker.binding, record.round_number, occurrence)


def marked_claim_verifier(
    project_root: Path, raw_marker: str, role: ReviewRole, host: Host, carried: CarriedIdentity | None,
) -> MarkedClaimVerifier:
    """Return the verifier ``claim_selected`` runs under the transition lock."""

    def verify(record: CoordinationRecord, occurrence: int) -> MarkedClaimEvidence:
        """Refuse with one reason code, or return the non-secret claim evidence."""
        try:
            return _evidence(project_root, raw_marker, role, host, carried, record, occurrence)
        except ArtifactError as error:
            raise _refused(str(error)) from error

    return verify


def verifier_from_arguments(args: Namespace, project_root: Path, role: ReviewRole, nature: LlmNature) -> MarkedClaimVerifier | None:
    """Build the verifier from the claim command's marked arguments, or ``None`` for a manual claim."""
    raw_marker: str | None = getattr(args, "resume_paused_marker", None)
    if raw_marker is None:
        return None
    host = _HOSTS.get(nature)
    if host is None:
        raise _refused("host-unsupported")
    session: str | None = getattr(args, "carried_session", None)
    launch: str | None = getattr(args, "carried_launch_id", None)
    carried = None if session is None and launch is None else CarriedIdentity(session or "", launch or "")
    return marked_claim_verifier(project_root, raw_marker, role, host, carried)


__all__ = ["consumed_by", "marked_claim_verifier", "requestor_consumed", "verifier_from_arguments"]


# eof
