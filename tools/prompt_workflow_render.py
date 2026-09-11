"""Render host-prefixed prompt-workflow commands.

Step 2 delegates host identity to the shared detector, preserving explicit
unknown and Gemini results instead of silently defaulting to Claude.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.llm_nature import LlmNature, LlmNatureDetector

if TYPE_CHECKING:
    from collections.abc import Mapping

HOST_CLAUDE = LlmNature.CLAUDE.value
HOST_CODEX = LlmNature.CODEX.value
HOST_GEMINI = LlmNature.GEMINI.value
HOST_UNKNOWN = LlmNature.UNKNOWN.value
HOST_PREFIXES = {
    HOST_CLAUDE: "/",
    HOST_CODEX: "$",
    HOST_GEMINI: "/",
    HOST_UNKNOWN: "<command-prefix>",
}
DEFAULT_HOST = HOST_UNKNOWN
MD_SUFFIX = ".md"
CODEX_SKILL_NAMESPACE = "llm-shared:"


def detect_host(
    env: Mapping[str, str],
    trusted_hint: str | None = None,
) -> str:
    """Return the shared detector's closed host token."""
    return LlmNatureDetector().detect(env, trusted_hint=trusted_hint).nature.value


def host_prefix(env: Mapping[str, str], override: str | None = None) -> str:
    """Return the command prefix for the detected or explicitly selected host."""
    host = detect_host(env, override)
    return HOST_PREFIXES[host]


def render_command(prefix: str, instruction: str, document: str) -> str:
    """Render one bare host-prefixed next-step command line."""
    name = instruction.removesuffix(MD_SUFFIX)
    if prefix == HOST_PREFIXES[HOST_CODEX] and ":" not in name:
        name = f"{CODEX_SKILL_NAMESPACE}{name}"
    return f"{prefix}{name} on {document}"


def render_step_command(
    prefix: str,
    instruction: str,
    document: str,
    implementation_step: str,
) -> str:
    """Append the explicit implementation-step token to an ordinary command."""
    return f"{render_command(prefix, instruction, document)} step {implementation_step}"


def render_umbrella_command(
    prefix: str,
    instruction: str,
    document: str,
    umbrella: str | None,
) -> str:
    """Append the umbrella a review role must carry in its exchange context.

    A reviewer builds its core context from this line. Omitting the umbrella
    there while the published request and the coordination record both carry
    one makes every exchange operation report `inconsistent` with the opaque
    "artifact context differs from core context", naming neither the umbrella
    nor the missing flag. Naming it here is what lets the reviewer discover it.

    Args:
        prefix: The host command prefix.
        instruction: The instruction or role name, with or without its suffix.
        document: The repository-relative reviewed document.
        umbrella: The repository-relative umbrella draft, or None when the
            effort has none.

    Returns:
        The ordinary command when there is no umbrella, and the same command
        followed by ``with umbrella <path>`` when there is one.
    """
    command = render_command(prefix, instruction, document)
    if umbrella is None:
        return command
    return f"{command} with umbrella {umbrella}"


# eof
