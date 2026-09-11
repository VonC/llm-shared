"""Detect the current LLM host without retaining host-owned secrets.

Step 2 centralizes trusted adapter hints and known environment signals in one
closed detector. Missing or contradictory evidence is explicit ``unknown``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping


class LlmNature(StrEnum):
    """LLM hosts that may act in one review protocol role."""

    CLAUDE = "claude"
    CODEX = "codex"
    GEMINI = "gemini"
    UNKNOWN = "unknown"


class InvalidLlmNatureError(ValueError):
    """Raised when a trusted provider hint is outside the closed enum."""


@dataclass(frozen=True)
class LlmNatureDetection:
    """One non-secret detected nature with its stable evidence category."""

    nature: LlmNature
    source: str
    diagnostic: str | None = None


class LlmNatureDetector:
    """Validate provider metadata and resolve hints before host environment signals."""

    @staticmethod
    def adapter_nature(markdown: str) -> LlmNature:
        """Validate the single non-secret nature field in provider front matter."""
        lines = markdown.splitlines()
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            message = "adapter requires closed front matter"
            raise InvalidLlmNatureError(message)
        end = lines.index("---", 1)
        values = [line.partition(":")[2].strip() for line in lines[1:end] if line.startswith("llm_nature:")]
        if len(values) != 1:
            message = "adapter requires exactly one llm_nature"
            raise InvalidLlmNatureError(message)
        return LlmNature(values[0])

    _ENVIRONMENT_SIGNALS: Final = (
        ("CLAUDECODE", LlmNature.CLAUDE),
        ("CODEX_THREAD_ID", LlmNature.CODEX),
    )

    def detect(
        self,
        environment: Mapping[str, str],
        *,
        trusted_hint: str | LlmNature | None = None,
    ) -> LlmNatureDetection:
        """Return a nature without copying environment names or values."""
        if trusted_hint is not None:
            try:
                nature = LlmNature(trusted_hint)
            except ValueError as error:
                msg = f"unsupported LLM nature: {trusted_hint}"
                raise InvalidLlmNatureError(msg) from error
            return LlmNatureDetection(nature, "trusted-host-hint")

        detected: list[LlmNature] = []
        for variable, nature in self._ENVIRONMENT_SIGNALS:
            if environment.get(variable) and nature not in detected:
                detected.append(nature)
        if not detected:
            return LlmNatureDetection(
                LlmNature.UNKNOWN,
                "no-host-evidence",
                "no known host signal was detected",
            )
        if len(detected) == 1:
            return LlmNatureDetection(detected[0], "host-environment")
        names = ", ".join(nature.value for nature in detected)
        return LlmNatureDetection(
            LlmNature.UNKNOWN,
            "conflicting-host-signals",
            f"conflicting detected natures: {names}",
        )


__all__ = [
    "InvalidLlmNatureError",
    "LlmNature",
    "LlmNatureDetection",
    "LlmNatureDetector",
]


# eof
