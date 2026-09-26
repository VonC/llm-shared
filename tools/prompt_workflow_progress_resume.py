"""Build the `pw progress` prompts that resume an abnormal review exchange.

A review exchange in a normal state needs no help: the round waits for its
counterpart, for the human choice, or for the authorized owning action, and
the condensed `review` line says so. An abandoned, interrupted, escalated, or
inconsistent exchange stops the cycle until someone pastes the right prompt
into the right session. For each such exchange this module renders one line
for the role instruction that recovers it:

    /code-review-requestor on docs/plan.v10.0.0.x.md step 3: escalated, ... (claude)

An abandoned or interrupted exchange goes to the role `rwst` names to continue
it, since only that role can reclaim its round or rerun its own operation. An
escalated or inconsistent exchange goes to the requestor, which owns the
recovery commands; escalation stays a human decision, so its prompt asks for
the reason and the choice rather than choosing. `review-resume` is not used
here: its typed inspection blocks escalated, interrupted, and inconsistent
exchanges.

The prefix and the trailing name come from the target role's recorded LLM
nature; an unrecorded or conflicting nature falls back to the detected host
prefix and names the role instead.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from tools import prompt_workflow_render as rendering
from tools import prompt_workflow_skill_review as role_names
from tools.llm_nature import LlmNature
from tools.review_exchange_models import ReviewFamily, ReviewRole
from tools.review_status_models import ExchangeStatus, NextAction

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tools.review_status_models import ReviewStatusResult

_INSTRUCTION: Final[dict[tuple[ReviewFamily, ReviewRole], str]] = {
    (ReviewFamily.CODE, ReviewRole.REQUESTOR): role_names.CODE_REVIEW_REQUESTOR,
    (ReviewFamily.CODE, ReviewRole.REVIEWER): role_names.CODE_REVIEWER,
    (ReviewFamily.SPECIFICATION, ReviewRole.REQUESTOR): role_names.SPEC_REVIEW_REQUESTOR,
    (ReviewFamily.SPECIFICATION, ReviewRole.REVIEWER): role_names.SPEC_REVIEWER,
}
_REQUESTOR_ACTIONS: Final[frozenset[NextAction]] = frozenset(
    {NextAction.RESOLVE_ESCALATION, NextAction.NO_SAFE_ACTION},
)
_RESUME_TASK: Final[dict[NextAction, str]] = {
    NextAction.RECLAIM: "reclaim the abandoned round and continue it",
    NextAction.REPAIR: (
        "rerun the interrupted operation with the same content to complete it, then continue"
    ),
    NextAction.RESOLVE_ESCALATION: (
        "show me the escalation reason, then ask me to choose reclaim --force, "
        "resolve, or archive to restart the cycle"
    ),
    NextAction.NO_SAFE_ACTION: (
        "explain the inconsistent evidence and propose a repair "
        "without editing review artifacts"
    ),
}


def target_role(exchange: ExchangeStatus) -> ReviewRole:
    """Return the role a resume prompt addresses for an abnormal exchange."""
    if exchange.next_action in _REQUESTOR_ACTIONS:
        return ReviewRole.REQUESTOR
    return exchange.continuing_role


def _host(
    exchange: ExchangeStatus,
    role: ReviewRole,
    env: Mapping[str, str],
    override: str | None,
) -> tuple[str, str]:
    """Return the command prefix and the trailing name for the target role."""
    status = (
        exchange.requestor_llm_nature
        if role is ReviewRole.REQUESTOR
        else exchange.reviewer_llm_nature
    )
    nature = status.value
    if isinstance(nature, LlmNature) and nature is not LlmNature.UNKNOWN:
        return rendering.HOST_PREFIXES[nature.value], nature.value
    return rendering.host_prefix(env, override), role.value


def resume_prompt(
    exchange: ExchangeStatus,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Return the one-line prompt that resumes an abnormal exchange.

    Args:
        exchange: One active exchange from the collected review status.
        env: The process environment, read for the fallback host prefix.
        override: An optional host token forcing the fallback prefix.

    Returns:
        `<prefix><role instruction> on <document>[ step N][ with umbrella U]:
        <state>, <task> (<name>)`, or None when the exchange is in a normal
        state.
    """
    task = _RESUME_TASK.get(exchange.next_action)
    if task is None:
        return None
    role = target_role(exchange)
    prefix, name = _host(exchange, role, env, override)
    instruction = f"{_INSTRUCTION[exchange.identity.family, role]}{rendering.MD_SUFFIX}"
    command = rendering.render_command(prefix, instruction, exchange.reviewed_document)
    if exchange.implementation_step:
        command += f" step {exchange.implementation_step}"
    if exchange.umbrella:
        command += f" with umbrella {exchange.umbrella}"
    return f"{command}: {exchange.state.value}, {task} ({name})"


def resume_prompts(
    result: ReviewStatusResult,
    env: Mapping[str, str],
    override: str | None = None,
) -> list[str]:
    """Return one resume prompt per abnormal exchange, in status order.

    Args:
        result: The collected repository review status.
        env: The process environment, read for the fallback host prefix.
        override: An optional host token forcing the fallback prefix.

    Returns:
        The prompts of `resume_prompt`; empty when every exchange is normal
        or no review is in progress.
    """
    prompts = (
        resume_prompt(entry, env, override)
        for entry in result.exchanges
        if isinstance(entry, ExchangeStatus)
    )
    return [prompt for prompt in prompts if prompt is not None]


# eof
