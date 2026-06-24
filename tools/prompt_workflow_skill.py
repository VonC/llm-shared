"""prompt_workflow_skill.py Skill-mode rendering for prompt_workflow (pw skill).

The ``pw skill`` subcommand prints the bare next-step command the LLM runs,
instead of the three-part prompt the interactive flow writes. This module is the
foundation that mode is built on (Step 1 of
``docs/plan.v0.9.0.handoff_automation.md``): the host-prefix detection and the
command rendering. The disk-derived routing and the subcommand wiring build on
it in the later steps.

Host prefix (Q04): a command is prefixed with ``/`` in a Claude session and
``$`` in a Codex session. The host is read from the process environment - Claude
Code sets ``CLAUDECODE``, a Codex session sets ``CODEX_THREAD_ID`` - and an
explicit override short-circuits that read, so the caller can force the prefix
even where detection cannot decide. When neither marker is present and no
override is given, the prefix falls back to the Claude default, so a command
always carries a usable prefix.

Command rendering: ``render_command`` turns an instruction file name and a target
document into a bare ``<prefix><name> on <document>`` line, dropping the ``.md``
suffix and using no backticks, so the LLM reads it as a command rather than as
quoted text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

# Host tokens used as the keys of the prefix lookup.
HOST_CLAUDE = "claude"
HOST_CODEX = "codex"
# Environment markers that identify the host (confirmed live on a session, Q04).
CLAUDE_ENV_VAR = "CLAUDECODE"
CODEX_ENV_VAR = "CODEX_THREAD_ID"
# Command prefix per host: a slash for Claude, a dollar for Codex.
HOST_PREFIXES = {HOST_CLAUDE: "/", HOST_CODEX: "$"}
# Host used when no marker and no override decide it, so a command always gets a prefix.
DEFAULT_HOST = HOST_CLAUDE
# Markdown suffix dropped from an instruction file name to form the skill name.
MD_SUFFIX = ".md"


def detect_host(env: Mapping[str, str]) -> str:
    """Return the host token read from the process environment (Q04).

    Args:
        env: The process environment mapping to read the host markers from.

    Returns:
        ``HOST_CLAUDE`` when the Claude marker is set, ``HOST_CODEX`` when the
        Codex marker is set, otherwise ``DEFAULT_HOST``. The Claude marker is
        checked first, so it wins if both are somehow present.
    """
    if env.get(CLAUDE_ENV_VAR):
        return HOST_CLAUDE
    if env.get(CODEX_ENV_VAR):
        return HOST_CODEX
    return DEFAULT_HOST


def host_prefix(env: Mapping[str, str], override: str | None = None) -> str:
    """Return the command prefix for the host, honoring an override (Q04).

    Args:
        env: The process environment mapping, read only when no override is given.
        override: An explicit host token (``HOST_CLAUDE`` or ``HOST_CODEX``). When
            present it short-circuits the environment read, so the caller can force
            the prefix even where detection cannot decide.

    Returns:
        ``/`` for the Claude host and ``$`` for the Codex host.

    Raises:
        KeyError: When ``override`` is not a known host token.
    """
    host = override if override is not None else detect_host(env)
    return HOST_PREFIXES[host]


def render_command(prefix: str, instruction: str, document: str) -> str:
    """Render one bare next-step command line (no wrapper, no backticks).

    Args:
        prefix: The host prefix (``/`` or ``$``) from ``host_prefix``.
        instruction: The instruction file name, such as ``write-design.md``; its
            ``.md`` suffix is dropped to form the emitted skill name.
        document: The target document the skill runs on.

    Returns:
        A line of the form ``<prefix><name> on <document>``, which the LLM reads
        as a command rather than as quoted text.
    """
    name = (
        instruction.removesuffix(MD_SUFFIX)
    )
    return f"{prefix}{name} on {document}"


# eof
