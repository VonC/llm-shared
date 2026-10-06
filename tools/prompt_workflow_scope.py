"""Print the current requirement's scope in pw commands and progress reports.

The workflow boundary resolves the topic and documents. The shared reader
owns metadata and group validation; this adapter only rejects caller scope
overrides and renders the result, never inferring full-suite proof from it.
"""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

from tools import effort_scope
from tools import prompt_workflow_git as git
from tools import prompt_workflow_handoff as handoff
from tools import prompt_workflow_memory as memory
from tools import prompt_workflow_steps as steps
from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_scope import bound_scope_payload
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from tools.prompt_workflow_models import Topic, WorkflowState


def run_scope(root: Path, ghog_args: Sequence[str]) -> int:
    """Print an explicit selector, or a completed ghog command.

    Returns:
        0 with a command; 2 for invalid scope or a caller selector; 3 when
        menu-less topic resolution is not applicable.
    """
    for argument in ghog_args:
        if argument.split("=", maxsplit=1)[0] in {"--group", "--scope-file", "--whole-suite"}:
            sys.stderr.write(f"pw scope: ghog arguments already carry a scope selector: {argument}\n")
            return 2
    topic = handoff.resolve_current_topic(root, git.current_branch(root), memory.read_memory(root))
    if topic is None:
        sys.stderr.write("pw scope: no workflow topic resolved.\n")
        return 3
    state = steps.compute_state(root, topic, None)
    try:
        resolved = effort_scope.read_effort_scope(root, state.requirement)
    except effort_scope.EffortScopeError as error:
        sys.stderr.write(f"pw scope: {error}\n")
        return 2
    command = ["ghog", *ghog_args] if ghog_args else []
    command.append(resolved.scope.selector())
    sys.stdout.write(subprocess.list2cmdline(command) + "\n")
    return 0


def scope_lines(root: Path, topic: Topic, state: WorkflowState) -> list[tuple[str, str]]:
    """Report current effort scope and the independently validated round capture."""
    try:
        resolved = effort_scope.read_effort_scope(root, state.requirement)
    except effort_scope.EffortScopeError as error:
        return [("scope", f"error: {error}")]
    label = resolved.scope.label().removeprefix("the ")
    lines = [("scope", f"{label} ({resolved.reason})")]
    if state.plan is None:
        return lines
    context = ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", topic.version, topic.slug), state.plan,
        umbrella_path=None, implementation_step="scope-display",
    )
    paths = derive_artifact_paths(root, context)
    try:
        record = ReviewExchangeStore(paths).read_coordination()
    except ReviewExchangeError:
        return [*lines, ("bound", "missing")]
    if record is not None:
        bound = bound_scope_payload(paths, record)
        value = "missing"
        if isinstance(bound, dict):
            value = f"group {bound['group']}" if bound["group"] else "whole suite"
            if (bound["scope"], bound["fingerprint"]) != (resolved.scope.key(), resolved.scope.fingerprint):
                value += f"; pending change to {label}"
        lines.append(("bound", value))
    return lines


# eof
