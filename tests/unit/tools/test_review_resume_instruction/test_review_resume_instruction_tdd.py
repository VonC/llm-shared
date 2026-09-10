"""Check the public resume entry, validated provider hints and role boundaries."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import prompt_workflow_skill as skill
from tools.llm_nature import InvalidLlmNatureError, LlmNature, LlmNatureDetector
from tools.prompt_workflow_models import Topic

_ROOT = Path(__file__).resolve().parents[4]
_ADAPTERS = (
    (".agent/workflows/review-resume.md", LlmNature.GEMINI),
    (".agents/llm-shared/instructions/review-resume.md", LlmNature.CODEX),
    (".agents/llm-shared/skills/review-resume/SKILL.md", LlmNature.CODEX),
    (".claude/skills/review-resume/SKILL.md", LlmNature.CLAUDE),
    (".github/skills/review-resume/SKILL.md", LlmNature.UNKNOWN),
)


@pytest.mark.parametrize(("path", "nature"), _ADAPTERS)
def test_provider_is_a_validated_direct_pointer(path: str, nature: LlmNature) -> None:
    """Every resume adapter validates its hint and delegates directly to canonical prose."""
    content = (_ROOT / path).read_text(encoding="utf-8")
    assert LlmNatureDetector.adapter_nature(content) is nature
    body = content.split("---", 2)[2].strip()
    assert "instructions/review-resume.md" in body
    assert "read and follow" in body.lower()
    assert "wait-any-request" not in body
    assert "ownership" not in body
    assert "../.agents" not in body
    assert "../.claude" not in body


@pytest.mark.parametrize("metadata", [
    "", "---\nllm_nature: codex\n", "---\nname: resume\n---\n",
    "---\nllm_nature: codex\nllm_nature: claude\n---\n",
    "---\nllm_nature: requestor\n---\n",
])
def test_provider_rejects_missing_duplicate_and_invalid_nature(metadata: str) -> None:
    """Unvalidated host metadata cannot influence role selection."""
    with pytest.raises((InvalidLlmNatureError, ValueError)):
        LlmNatureDetector.adapter_nature(metadata)


def test_bare_resume_orders_gates_and_automatic_claim() -> None:
    """A human needs no ownership vocabulary and claims precede role mutation."""
    content = (_ROOT / "instructions/review-resume.md").read_text(encoding="utf-8")
    normalized = " ".join(content.split())
    assert "bare user request `resume` authorizes automatic ownership pickup" in normalized
    assert content.index("migration-check") < content.index("resume-inspect") < content.index("automatic `claim`")
    for phrase in ("Do not ask for a token", "lease-independent pickup", "only in the session",
                   "pass it to every later", "Override", "Stop", "wait-exact-answer",
                   "follow-workflow", "After exchange release, run and follow `pw skill` immediately"):
        assert phrase in normalized
    assert not (_ROOT / "rvw_resume.bat").exists()
    assert not (_ROOT / "bin/rvw_resume.bat").exists()


@pytest.mark.parametrize("family", ["spec", "code"])
def test_roles_keep_exact_requestor_and_global_reviewer_continuations(family: str) -> None:
    """Both families use automatic pickup, persistent global waiting and owning-role release."""
    reviewer = " ".join((_ROOT / f"instructions/{family}-reviewer.md").read_text(encoding="utf-8").split())
    requestor = " ".join((_ROOT / f"instructions/{family}-review-requestor.md").read_text(encoding="utf-8").split())
    for content in (reviewer, requestor):
        assert "bare user `resume`" in content
        assert "automatic `claim`" in content
    assert "After any answer, wait globally with `wait-any-request`" in reviewer
    assert "Never run `pw skill" in reviewer
    assert "After exchange release, run and follow `pw skill` immediately" in requestor


@pytest.mark.parametrize("name", ["resume", "review-resume"])
@pytest.mark.parametrize(("environment", "expected"), [
    ({"CODEX_THREAD_ID": "test-host"}, "$llm-shared:review-resume"),
    ({"CLAUDECODE": "1"}, "/review-resume"),
])
def test_router_emits_a_bare_resume_skill_without_a_document(
    tmp_path: Path, name: str, environment: dict[str, str], expected: str,
) -> None:
    """Resume routing needs no document lookup and cannot emit a dangling on argument."""
    topic = Topic("v0.11.0", "resume", tmp_path / "draft.v0.11.0.resume.md")
    assert skill.forced_command(tmp_path, topic, name, environment) == expected


# eof
