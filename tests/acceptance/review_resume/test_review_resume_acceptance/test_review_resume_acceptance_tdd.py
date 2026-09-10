"""Cross-family acceptance for bare resume, durable gates and clean release.

These assertions inspect real launcher journeys prepared once per family. The
Release follows the workflow selected from current documents. The bare user
text drives a documented LLM simulation; provider contract tests bind
that simulation to the canonical instruction rather than claiming a model ran.
"""

# ruff: noqa: PLR2004
from __future__ import annotations

import re
from typing import Any


def _assert_automatic_trace(trace: list[Any]) -> None:
    """Require preflight, inspection and claim without a human-recovery intermediate state."""
    assert [item.payload["operation"] for item in trace] == ["migration-check", "resume-inspect", "claim"]
    assert all(item.code == 0 for item in trace)
    assert all(item.payload["outcome"] == "ready" for item in trace)


def test_bare_resume_claims_before_fresh_lease_continuation(lifecycle_journey: dict[str, Any]) -> None:
    """AC12-14: missing secrets trigger automatic pickup before either role acts."""
    journey = lifecycle_journey
    for name in ("pending", "first", "lost", "gate", "owning"):
        _assert_automatic_trace(journey[name])
    assert journey["pending"][-1].payload["action"] == "wait-exact-answer"
    assert journey["first"][-1].payload["action"] == "review-request"
    assert journey["gate"][-1].payload["action"] == "continue-requestor"


def test_fresh_lease_displacement_rejects_the_old_session(lifecycle_journey: dict[str, Any]) -> None:
    """A lost capability is replaced immediately and the displaced actor cannot publish."""
    journey = lifecycle_journey
    assert journey["lost"][-1].payload["ownership_generation"] > journey["first"][-1].payload["ownership_generation"]
    assert "ownership-superseded" in journey["stale"].stdout
    assert journey["stale"].code == 3


def test_resume_preserves_human_authority_at_convergence(lifecycle_journey: dict[str, Any]) -> None:
    """Pickup itself grants no Commit or Consolidate authorization."""
    journey = lifecycle_journey
    assert journey["answer"].payload["state"] == "convergence-gate"
    assert "owning_action_authorized" not in journey["gate"][-1].payload
    assert journey["confirmed"].payload["owning_action_authorized"] is True
    assert journey["owning"][-1].payload["action"] == "continue-requestor"
    assert journey["completion"].code == 0


def test_public_status_preserves_bytes_and_reports_both_hosts(lifecycle_journey: dict[str, Any]) -> None:
    """AC5-6,18: schema-2 JSON and human status observe both roles without mutation."""
    journey = lifecycle_journey
    assert journey["before"] == journey["after_status"]
    status = journey["status"].payload
    assert status["schema_version"] == 2
    entry = status["exchanges"][0]
    assert entry["requestor_llm_nature"] == "codex"
    assert entry["reviewer_llm_nature"] == "claude"
    assert "Requestor LLM nature: codex" in journey["human"].stdout
    assert "Reviewer LLM nature: claude" in journey["human"].stdout
    assert "Migration: unnecessary" in journey["human"].stdout


def test_every_runtime_artifact_uses_the_declared_ignored_home(lifecycle_journey: dict[str, Any]) -> None:
    """AC1-2,16: producers, consumers, status and resume agree on one ignored home."""
    journey = lifecycle_journey
    repo = journey["repo"]
    relative_home = repo.home.relative_to(repo.root).as_posix()
    for path in journey["before"]:
        assert path.startswith((relative_home + "/", "docs/"))
    assert journey["git_status"] == ""
    assert (repo.home / ".gitignore").read_bytes() == b"*\n"
    assert not tuple(repo.root.glob("a.review-*.md"))


def test_release_retains_unique_transcript_and_no_session_secrets(lifecycle_journey: dict[str, Any]) -> None:
    """AC6,13-14: release routes the requestor to its actual workflow launcher."""
    journey = lifecycle_journey
    assert journey["released"].payload["action"] == "follow-workflow"
    assert journey["final_status"].payload["state"] == "idle"
    assert journey["workflow"].returncode == 0, journey["workflow"].stderr
    assert journey["workflow"].stdout.strip() == (
        "$llm-shared:review-ask-questions on docs/v0.11.0/feature-request.v0.11.0.resume-acceptance.md"
    )
    assert "reviewer" not in journey["workflow"].stdout
    assert journey["git_status"] == ""
    _assert_no_session_secrets(journey)
    _assert_transcript_headings(journey)


def _assert_no_session_secrets(journey: dict[str, Any]) -> None:
    """Check every issued secret against retained runtime and transcript bytes."""
    evidence = b"\n".join(journey["before"].values()) + b"\n".join(journey["final_evidence"].values())
    for name in ("pending", "first", "lost", "gate", "owning"):
        assert journey[name][-1].payload["ownership_token"].encode() not in evidence
    assert b"acceptance-host-sentinel" not in evidence


def _assert_transcript_headings(journey: dict[str, Any]) -> None:
    """Retain one title and unique headings after normal publication and completion."""
    transcript = journey["repo"].paths.transcript.read_text(encoding="utf-8")
    headings = re.findall(r"^#{1,6} .+$", transcript, re.MULTILINE)
    assert sum(heading.startswith("# ") for heading in headings) == 1
    assert len(headings) == len(set(headings))


# eof
