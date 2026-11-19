"""Requestor answer-wait transport contract for marked review continuation.

Step 4 of v0.14.0 resume-paused applies confirmed design Q25=A: every Claude
requestor starts each ``wait-answer`` through a host background mechanism, as
one recognized invocation form, ends its turn and resumes from the completion
notification, on every requestor route. A foreground or moved wait stays in
scope and leaves the reviewer pending. Codex keeps its attached wait. The
shared rule lives in ``rules/run_commands.md``; the three requestor
instructions refer to it instead of copying it. The existing reviewer waits
keep their host-specific transports: Claude background completion, Codex
attached waiting and no detaching launcher.
"""

from __future__ import annotations

from functools import cache

import pytest

from tools import prompt_workflow_steps as steps

ROOT = steps.llm_shared_dir()
RULE = "Claude requestors wait for answers in the background"
RULE_LINK = "](../rules/run_commands.md#claude-requestors-wait-for-answers-in-the-background)"
REQUESTORS = (
    "instructions/review-requestor.md",
    "instructions/spec-review-requestor.md",
    "instructions/code-review-requestor.md",
)
REVIEWER_WAITS = (
    ("instructions/review-resume.md", "Claude may return chat control with a background watcher and resume through its supported completion notification."),
    ("instructions/spec-reviewer.md", "Claude may return control of the chat with its background watcher active and resume on the completion notification."),
    ("instructions/code-reviewer.md", "Claude may return control of the chat with its background watcher active and resume on the completion notification."),
)
DETACHING_LAUNCHERS = ("start /b", "Start-Process", "--detach")


@cache
def folded(relative: str) -> str:
    """Return one shipped instruction with line breaks folded into single spaces."""
    return " ".join((ROOT / relative).read_text(encoding="utf-8").split())


def rule_section() -> str:
    """Return the shared Claude requestor wait rule, below its heading."""
    text = (ROOT / "rules/run_commands.md").read_text(encoding="utf-8")
    return " ".join(text.split(f"\n### {RULE}\n", 1)[1].split("\n#", 1)[0].split())


@pytest.mark.parametrize(
    "required",
    [
        "Every Claude requestor starts each `wait-answer` through a host background mechanism, on every requestor route:",
        "a first round, a replacement round, a resumed exchange and a marked resume",
        "one recognized invocation form: the shared launcher by its full path with `wait-answer` and the exact context arguments, alone on one line",
        "never chained, piped, wrapped in another shell or combined with another operation",
        "end the turn, and resume from its completion notification to read the final JSON",
        "A foreground `wait-answer`, or one moved into the background after it started, stays in scope for reviewer activation and leaves the reviewer pending with that reason.",
        "Codex keeps its attached wait; this rule does not apply to it.",
    ],
)
def test_shared_rule_requires_the_claude_background_answer_wait(required: str) -> None:
    """The shared rule makes the background start mandatory, not merely permitted."""
    assert required in rule_section()


@pytest.mark.parametrize("relative", REQUESTORS)
def test_requestor_instructions_refer_to_the_shared_rule(relative: str) -> None:
    """Each requestor instruction points at the one rule rather than copying it."""
    text = folded(relative)
    assert RULE_LINK in text
    assert "Every Claude requestor starts each `wait-answer` through a host background mechanism" not in text


@pytest.mark.parametrize(("relative", "claude"), REVIEWER_WAITS)
def test_reviewer_waits_keep_their_host_specific_transports(relative: str, claude: str) -> None:
    """Reviewer waits stay background-notified in Claude, attached in Codex, never detached."""
    text = folded(relative)
    assert claude in text
    assert "Codex must use an attached wait" in text
    assert not any(launcher in text for launcher in DETACHING_LAUNCHERS)


# eof
