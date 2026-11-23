"""Canonical checkout root, digest, id, timestamp and text value tests.

Step 2 of v0.15.0 resume-paused: checkout roots compare by Windows rules and
refuse ambiguous spellings, digests and pane UUIDs normalize their case, agent
ids keep the grammar pauses write, timestamps carry an offset, and routing
text stays on one line.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from tools.resume_paused_models import (
    ArtifactError,
    CanonicalRoot,
    PromptDigest,
    agent_id,
    checked_text,
    checked_timestamp,
    host_for_agent,
    pane_id,
    sha256_hex,
    timestamp_instant,
)
from tools.resume_paused_profiles import Host

PANE = "77e5f39c-0536-4cbb-a057-f4a1f5c715b0"
SHA_OF_EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


@pytest.mark.parametrize(
    "alias",
    ["C:/Work/Repo/", "c:\\work\\repo", "\\\\?\\C:\\WORK\\repo", "C:\\work\\\\repo\\"],
)
def test_canonical_roots_compare_by_windows_rules(alias: str) -> None:
    """Case, separators, repeated or trailing separators and the extended prefix do not matter."""
    assert CanonicalRoot.parse(alias) == CanonicalRoot.parse("C:\\Work\\Repo")
    assert CanonicalRoot.parse(alias).key == "c:\\work\\repo"


def test_unc_and_drive_roots_keep_their_canonical_display() -> None:
    """A share, its extended spelling and a bare drive canonicalize predictably."""
    assert CanonicalRoot.parse("//srv/share/x") == CanonicalRoot.parse("\\\\?\\UNC\\srv\\share\\X")
    assert (CanonicalRoot.parse("c:/").display, CanonicalRoot.parse("//srv/share").display) == ("C:\\", "\\\\srv\\share")
    assert CanonicalRoot.from_path(Path("C:/work/x")).display == "C:\\work\\x"


@pytest.mark.parametrize(
    "value",
    ["relative\\root", "C:relative", "\\\\srv", "C:\\a\\..\\b", "C:\\a\\.\\b", "C:\\a.", "C:\\a \\b", "C:\\a|b", "", "C:\\a\nb", 5],
)
def test_ambiguous_roots_are_rejected(value: object) -> None:
    """Relative, dotted, trailing-dot, reserved-character and control spellings fail."""
    with pytest.raises(ArtifactError):
        CanonicalRoot.parse(value)


def test_digests_and_pane_ids_normalize_their_case() -> None:
    """Recorded hexadecimal and UUID spellings compare in lowercase."""
    assert PromptDigest.of(b"") == PromptDigest.parse(SHA_OF_EMPTY.upper())
    assert (sha256_hex("A" * 64, "binding"), pane_id(PANE.upper(), "pane")) == ("a" * 64, PANE)
    for value in ("a" * 63, "g" * 64, 64):
        with pytest.raises(ArtifactError, match="invalid digest"):
            sha256_hex(value, "digest")
    with pytest.raises(ArtifactError, match="invalid pane: expected a full pane UUID"):
        pane_id(PANE[:8], "pane")


def test_agent_ids_and_recognized_hosts() -> None:
    """Agent ids keep the pause grammar; only claude and chatgpt name a supported host."""
    assert agent_id("claude-2", "author") == "claude-2"
    with pytest.raises(ArtifactError, match="invalid author: expected lowercase letters"):
        agent_id("Claude", "author")
    assert [host_for_agent(agent) for agent in ("claude", "chatgpt", "gemini", None)] == [Host.CLAUDE, Host.CODEX, None, None]


def test_timestamps_require_a_numeric_offset() -> None:
    """Only offset-bearing timestamps validate, and they compare by instant."""
    assert checked_timestamp("2026-11-18T07:25:09+01:00", "time") == "2026-11-18T07:25:09+01:00"
    assert timestamp_instant("2026-11-18T07:25:09+01:00") == datetime(2026, 11, 18, 6, 25, 9, tzinfo=UTC)
    for value in ("2026-11-18T07:25:09", "2026-13-18T07:25:09+01:00"):
        with pytest.raises(ArtifactError, match="invalid time"):
            checked_timestamp(value, "time")


def test_text_is_trimmed_single_line_and_bounded() -> None:
    """Empty text needs an explicit allowance; controls, separators and padding fail."""
    assert checked_text("", "label", empty=True) == ""
    for value in ("", " padded", "next\x85line", "split\u2028line", "x" * 1001, None):
        with pytest.raises(ArtifactError, match="invalid text"):
            checked_text(value, "text")


# eof
