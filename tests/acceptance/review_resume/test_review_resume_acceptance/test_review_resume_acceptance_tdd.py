"""Independent cross-family scenarios for resume, durable gates and release.

Each case creates its own repository and executes only its prerequisite
transitions. Setup is measured; no test depends on another case's execution.
The driver invokes production Python against declared repository observations.
Lost-owner recovery retains public CLI integration for both families; other
phase variants invoke the same production dispatcher with parsed arguments.
"""

# ruff: noqa: PLR2004
from __future__ import annotations

import os
import re
from argparse import Namespace
from typing import TYPE_CHECKING, Any

import pytest

from tests.acceptance.review_resume.cli_support import run_inline
from tests.acceptance.review_resume.conftest import (
    SHARED_ROOT,
    ReviewRepository,
)
from tests.acceptance.review_resume.prepared_request import (
    prepare_convergence,
    prepare_request,
)
from tests.unit.tools.review_exchange_test_support import session_environment
from tools.review_exchange_cli_resume import execute_resume_operation
from tools.review_exchange_models import Actor, ReviewFamily, ReviewRole

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tests.acceptance.review_resume.conftest import ProcessResult


class Journey:
    """Retain issued capabilities solely to check that publication omits them."""

    def __init__(self, repo: ReviewRepository) -> None:
        """Retain the independently declared repository for one measured test."""
        self.repo = repo
        self.capabilities: list[dict[str, Any]] = []

    def prepare(self, phase: str = "request") -> None:
        """Declare only the prerequisite phase consumed by this test."""
        if phase in {"gate", "owning"}:
            capability = prepare_convergence(self.repo, authorized=phase == "owning")
        else:
            capability = prepare_request(self.repo, "codex", owner=Actor.REVIEWER if phase == "lost" else Actor.REQUESTOR,
                                         reviewer_nature="claude" if phase == "lost" else None)
        self.capabilities.append(capability)

    def claim(self, *, reviewer: bool = False, inspect: bool = True,
              infer_role: bool = False) -> list[ProcessResult]:
        """Exercise orchestration, or claim a known prerequisite directly."""
        nature = "claude" if reviewer else "codex"
        if inspect:
            trace = self.repo.resume_selected(role="reviewer" if reviewer and not infer_role else None, nature=nature)
        else:
            trace = [self.repo.claim_known(role="reviewer" if reviewer else "requestor", nature=nature)]
        assert [item.payload["operation"] for item in trace] == (
            ["resume-inspect", "claim"] if inspect else ["claim"]
        )
        assert all(item.code == 0 and item.payload["outcome"] == "ready" for item in trace)
        self.capabilities.append(trace[-1].payload)
        self.assert_no_secrets()
        return trace

    def answer(self) -> ProcessResult:
        """Reach convergence by a real reviewer claim and publication."""
        reviewer = self.repo.prepare_reviewer()
        self.capabilities.append(reviewer)
        self.assert_no_secrets()
        answer = self.repo.publish(ReviewRole.REVIEWER, reviewer, ready=True, nature="claude")
        assert answer.code == 3  # Publication succeeds but waits at the human gate.
        assert answer.payload["outcome"] == "published"
        assert answer.payload["state"] == "convergence-gate"
        self.assert_no_secrets()
        return answer

    def dispatch_selected(self, *, reviewer: bool = False) -> dict[str, Any]:
        """Check phase variants at the real dispatcher, preserving fresh selection.

        The lost-owner case below retains the public inspect/claim CLI journey
        for each family, including inferred role and renewed ownership.
        """
        nature = "claude" if reviewer else "codex"
        args = Namespace(operation="resume-inspect", document=str(self.repo.context.document_path),
                         implementation_step=self.repo.context.implementation_step,
                         role="reviewer" if reviewer else None, trusted_host_hint=nature,
                         override=False, ownership_generation=None, ownership_token=None)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(os, "environ", session_environment(os.environ, nature))
            inspected, code = execute_resume_operation(args, self.repo.root)
            assert code == 0
            assert inspected["operation"] == "resume-inspect"
            assert inspected["outcome"] == "ready"
            candidate = inspected["candidates"][0]
            args.operation, args.role = "claim", inspected["role"]
            args.round_number, args.occurrence = candidate["round"], candidate["occurrence"]
            claimed, code = execute_resume_operation(args, self.repo.root)
            assert code == 0
            assert claimed["operation"] == "claim"
            assert claimed["outcome"] == "ready"
        self.capabilities.append(claimed)
        self.assert_no_secrets()
        return claimed

    def authorize(self, *, resume: bool = True) -> list[ProcessResult]:
        """Require a separate human choice before the owning action resumes."""
        gate = self.claim(inspect=False)
        assert gate[-1].payload["action"] == "continue-requestor"
        assert "owning_action_authorized" not in gate[-1].payload
        label = "Commit" if self.repo.context.identity.family is ReviewFamily.CODE else "Consolidate"
        confirmed = self.repo.exchange("confirm", "--choice-label", label, capability=gate[-1].payload)
        assert confirmed.code == 3  # The separately authorized owning action is still pending.
        assert confirmed.payload["owning_action_authorized"] is True
        return self.claim() if resume else gate

    def assert_no_secrets(self) -> None:
        """Every issued secret stays out of runtime and transcript bytes."""
        evidence = b"\n".join(self.repo.evidence().values())
        assert all(capability["ownership_token"].encode() not in evidence for capability in self.capabilities)
        assert b"acceptance-host-sentinel" not in evidence


@pytest.fixture(params=(ReviewFamily.CODE, ReviewFamily.SPECIFICATION))
def journey(tmp_path: Path, request: pytest.FixtureRequest, stable_review_inputs: Callable[[], None]) -> Journey:
    """Build independent data and request state inside this case's lifecycle."""
    family = request.param
    repo = ReviewRepository(tmp_path / "caller", family=family,
                            home=".reviews" if family is ReviewFamily.CODE else "runtime/reviews")
    stable_review_inputs()
    return Journey(repo)


@pytest.mark.parametrize("phase", ["pending", "first", "lost", "gate", "owning"])
def test_bare_resume_claims_before_fresh_lease_continuation(journey: Journey, phase: str) -> None:
    """AC12-14: current-layout pickup inspects and claims before acting.

    The migration suite separately asserts the complete preflight trace.
    """
    journey.prepare(phase)
    prior_generation = journey.capabilities[-1]["ownership_generation"]
    # Keep public argument parsing and inspect-to-claim integration for each
    # family in the lost-owner case; exercise the remaining phase decisions
    # through the same production dispatcher without redundant CLI setup.
    claimed = (journey.claim(reviewer=True, infer_role=True)[-1].payload if phase == "lost"
               else journey.dispatch_selected(reviewer=phase == "first"))
    expected = {"pending": "wait-exact-answer", "first": "review-request", "lost": "review-request",
                "gate": "continue-requestor", "owning": "continue-requestor"}
    assert claimed["action"] == expected[phase]
    if phase == "lost":
        # Recover with neither role nor capability supplied by this host.
        assert claimed["ownership_generation"] > prior_generation


@pytest.mark.parametrize("publisher", ["displaced", "current"])
def test_fresh_lease_displacement_rejects_the_old_session(journey: Journey, publisher: str) -> None:
    """Publication rejects a displaced capability and accepts the current one."""
    journey.prepare("lost")
    first = journey.capabilities[-1]
    # The lost-phase case above asserts CLI discovery, role inference, claim
    # and generation advancement. Publication needs only that real ownership
    # transition as a prerequisite, not another replay of discovery.
    current = journey.repo.prepare_reviewer()
    journey.capabilities.append(current)
    assert current["ownership_generation"] > first["ownership_generation"]
    if publisher == "displaced":
        stale = journey.repo.publish(ReviewRole.REVIEWER, first, nature="claude")
        assert "ownership-superseded" in stale.stdout
        assert stale.code == 3
    else:
        answer = journey.repo.publish(ReviewRole.REVIEWER, current, ready=True, nature="claude")
        assert answer.code == 3
        assert answer.payload["outcome"] == "published"
    journey.assert_no_secrets()


def test_resume_preserves_human_authority_at_convergence(journey: Journey) -> None:
    """Pickup itself grants no Commit or Consolidate authorization."""
    journey.prepare("gate")
    owning = journey.authorize(resume=False)
    assert owning[-1].payload["action"] == "continue-requestor"
    assert journey.repo.exchange("complete", capability=owning[-1].payload).code == 0
    journey.assert_no_secrets()


def test_reviewer_publication_reaches_convergence(journey: Journey) -> None:
    """Retain the real publication and secrecy contract independently of pickup."""
    journey.prepare()
    journey.answer()


def test_public_status_preserves_bytes_and_reports_both_hosts(journey: Journey) -> None:
    """AC5-6,18: schema-2 JSON and human status observe both roles without mutation."""
    journey.prepare("gate")
    repo = journey.repo
    before = repo.evidence()
    status = repo.run("--format", "json", launcher=SHARED_ROOT / "rvw_status.bat").payload
    human = run_inline((), repo.root, session_environment(os.environ, "codex"), entry="status")
    assert before == repo.evidence()
    assert status["schema_version"] == 2
    entry = status["exchanges"][0]
    assert entry["requestor_llm_nature"] == "codex"
    assert entry["reviewer_llm_nature"] == "claude"
    assert "Requestor LLM nature: codex" in human.stdout
    assert "Reviewer LLM nature: claude" in human.stdout
    assert "Migration: unnecessary" in human.stdout


def test_every_runtime_artifact_uses_the_declared_ignored_home(journey: Journey) -> None:
    """AC1-2,16: producers, consumers, status and resume agree on one ignored home."""
    journey.prepare("gate")
    journey.claim(inspect=False)
    repo = journey.repo
    assert repo.exchange("status").payload["state"] == "convergence-gate"
    relative_home = repo.home.relative_to(repo.root).as_posix()
    for path in repo.evidence():
        assert path.startswith((relative_home + "/", "docs/"))
    assert repo.facts.changes() == {}
    assert (repo.home / ".gitignore").read_bytes() == b"*\n"
    assert not tuple(repo.root.glob("a.review-*.md"))


def test_release_retains_unique_transcript_and_no_session_secrets(journey: Journey) -> None:
    """AC6,13-14: release routes the requestor to its actual workflow launcher."""
    journey.prepare("owning")
    repo = journey.repo
    assert repo.exchange("complete", capability=journey.capabilities[-1]).code == 0
    assert repo.run("resume-inspect", "--role", "requestor").payload["action"] == "follow-workflow"
    assert repo.exchange("status").payload["state"] == "idle"
    workflow = run_inline(("skill",), repo.root, session_environment(os.environ, "codex"), entry="workflow")
    assert workflow.returncode == 0, workflow.stderr
    assert workflow.stdout.strip() == (
        "$llm-shared:review-ask-questions on docs/v0.11.0/feature-request.v0.11.0.resume-acceptance.md"
    )
    assert "reviewer" not in workflow.stdout
    assert repo.facts.changes() == {}
    journey.assert_no_secrets()
    transcript = repo.paths.transcript.read_text(encoding="utf-8")
    headings = re.findall(r"^#{1,6} .+$", transcript, re.MULTILINE)
    assert sum(heading.startswith("# ") for heading in headings) == 1
    assert len(headings) == len(set(headings))


# eof
