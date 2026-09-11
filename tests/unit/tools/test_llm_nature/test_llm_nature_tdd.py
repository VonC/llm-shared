"""Tests for trusted and environment-backed LLM-nature detection."""

from __future__ import annotations

import pytest

from tools.llm_nature import (
    InvalidLlmNatureError,
    LlmNature,
    LlmNatureDetector,
)


def test_trusted_hint_takes_precedence_over_environment_conflicts() -> None:
    """An installed adapter hint is authoritative without persisting secrets."""
    detection = LlmNatureDetector().detect(
        {"CLAUDECODE": "claude-secret", "CODEX_THREAD_ID": "codex-secret"},
        trusted_hint="gemini",
    )

    assert detection.nature is LlmNature.GEMINI
    assert detection.source == "trusted-host-hint"
    assert "secret" not in repr(detection)


@pytest.mark.parametrize(
    ("environment", "expected"),
    [
        ({"CLAUDECODE": "1"}, LlmNature.CLAUDE),
        ({"CODEX_THREAD_ID": "thread"}, LlmNature.CODEX),
        ({}, LlmNature.UNKNOWN),
    ],
)
def test_environment_detection_has_no_silent_default(
    environment: dict[str, str],
    expected: LlmNature,
) -> None:
    """Known signals map directly and missing evidence stays unknown."""
    assert LlmNatureDetector().detect(environment).nature is expected


def test_conflicting_environment_signals_return_unknown() -> None:
    """Contradictory known hosts produce one non-secret conflict result."""
    detection = LlmNatureDetector().detect(
        {"CLAUDECODE": "claude-secret", "CODEX_THREAD_ID": "codex-secret"},
    )

    assert detection.nature is LlmNature.UNKNOWN
    assert detection.source == "conflicting-host-signals"
    assert detection.diagnostic == "conflicting detected natures: claude, codex"
    assert "secret" not in repr(detection)


def test_invalid_trusted_hint_is_rejected() -> None:
    """Provider hints are validated against the closed enum."""
    with pytest.raises(InvalidLlmNatureError, match="unsupported LLM nature"):
        LlmNatureDetector().detect({}, trusted_hint="other")

