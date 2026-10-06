"""Resolve request scopes once and report only the walk's currently valid proof.

The renderer supplies its validated plan identity for effort lookup and change
disclosure; capture validation and proof validity remain shared with groundhog
and the exchange respectively.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools import effort_scope
from tools import prompt_workflow_steps as steps
from tools.groundhog import snapshot
from tools.prompt_workflow_models import PromptWorkflowError, Topic
from tools.review_exchange_models import ReviewExchangeError
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_scope import bound_scope_payload
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from tools.effort_scope import EffortScope
    from tools.review_exchange_models import ExchangeIdentity, ReviewContext


def resolve_request_scope(root: Path, plan: Path, identity: ExchangeIdentity) -> EffortScope:
    """Read the requirement using the renderer's already validated plan identity."""
    draft = plan.with_name(f"draft.{identity.version}.{identity.slug}.md")
    try:
        state = steps.compute_state(root, Topic(identity.version, identity.slug, draft), None)
    except PromptWorkflowError as error:
        raise ReviewExchangeError(str(error)) from error
    return effort_scope.read_effort_scope(root, state.requirement)


def scope_evidence(root: Path, scope: EffortScope) -> dict[str, str | None]:
    """Project the exact resolution and shared effective proof into request JSON."""
    resolved = scope.scope
    proof = snapshot.effective_proof(root, resolved.key(), resolved.fingerprint).proof
    return {
        "scope": resolved.key(),
        "group": resolved.name or None,
        "fingerprint": resolved.fingerprint,
        "requirement": None if scope.source_path is None else scope.source_path.relative_to(root).as_posix(),
        "proof": "missing" if proof is None else proof.token,
    }


def bound_capture(root: Path, context: ReviewContext) -> dict[str, str | None] | None:
    """Read the active round's validated capture without resolving its group."""
    paths = derive_artifact_paths(root, context)
    record = ReviewExchangeStore(paths).read_coordination()
    payload = bound_scope_payload(paths, record)
    return payload if isinstance(payload, dict) else None


def scope_change_block(
    previous: Mapping[str, str | None] | None,
    current: Mapping[str, str | None],
    reason: str | None,
) -> str:
    """Require disclosure when replacement changes the bound scope identity."""
    if previous is None or (previous["scope"], previous["fingerprint"]) == (
        current["scope"], current["fingerprint"],
    ):
        return ""
    before = f"{previous['scope']} ({previous['fingerprint']})"
    after = f"{current['scope']} ({current['fingerprint']})"
    if reason is None or not reason.strip():
        message = f"scope change from {before} to {after} requires --scope-change-file"
        raise ReviewExchangeError(message)
    return f"Scope change:\n\nPrevious scope: {before}\n\nNew scope: {after}\n\nReason: {reason.strip()}"


# eof
