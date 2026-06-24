"""prompt_workflow_skill.py Skill-mode rendering for prompt_workflow (pw skill).

The ``pw skill`` subcommand prints the bare next-step command the LLM runs,
instead of the three-part prompt the interactive flow writes. This module holds
the pieces that mode is built on: the host-prefix detection and the command
rendering (Step 1), and the disk-derived next-step routing (Step 2) of
``docs/plan.v0.9.0.handoff_automation.md``.

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

Next-step routing (Q02, Q03): ``next_command`` reads the workflow state from disk
only (never ``a.prompt_memory``), reuses ``steps.next_step_numbers`` for the base
step, and advances past a review step when the document it reads carries a
consolidated decisions table. The resolved step maps to an instruction and a
target document, then renders.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_docs as docs
from tools import prompt_workflow_steps as steps

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tools.prompt_workflow_models import Topic, WorkflowState

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
    name = instruction.removesuffix(MD_SUFFIX)
    return f"{prefix}{name} on {document}"


# The docs folder the skill commands name, relative to the project root.
DOCS_DIR = "docs"
# The instruction named before the workflow proper, when only a new draft exists.
PROCESS_DRAFT = "process-draft.md"
# The instruction each resolved workflow step names (step 1 on the slug branch writes).
STEP_INSTRUCTION = {
    1: "write-requirement.md",
    2: "review-ask-questions.md",
    3: "consolidate-then-review-ask-questions.md",
    4: "write-design.md",
    5: "review-ask-questions.md",
    6: "consolidate-then-review-ask-questions.md",
    7: "write-plans.md",
    8: "review-ask-questions.md",
    9: "consolidate-then-review-ask-questions.md",
    10: "implement-step.md",
}
# The artifact role each step reads or produces.
STEP_ROLE = {
    1: "requirement",
    2: "requirement",
    3: "requirement",
    4: "design",
    5: "design",
    6: "design",
    7: "plan",
    8: "plan",
    9: "plan",
    10: "plan",
}
# A review step whose current document, once it carries a decisions table, advances
# past the review to the next write or implement step (the Q02 post-process).
ADVANCE_PAST_REVIEW = {2: 4, 5: 7, 8: 10}
# The document type a write step produces for each artifact role.
PRODUCED_TYPE = {"requirement": "feature-request", "design": "design", "plan": "plan"}


def next_command(
    root: Path,
    topic: Topic,
    branch: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str:
    """Return the bare next-step command derived from the documents on disk.

    The next step is read from the tree only (never ``a.prompt_memory``): the
    state comes from ``compute_state`` with no memory step, ``next_step_numbers``
    picks the base step, and a current document carrying a decisions table
    advances past its review step (Q02). The resolved step maps to an instruction
    and a target document, which ``render_command`` turns into one host-prefixed
    line.

    Args:
        root: The project root the documents live under.
        topic: The resolved topic (version, slug, draft path).
        branch: The current branch name, used to tell a new draft (process-draft)
            from a draft already on its slug branch (write-requirement).
        env: The process environment, read for the host prefix.
        override: An optional host token forcing the prefix (see ``host_prefix``).

    Returns:
        One bare ``<prefix><name> on <document>`` command line.
    """
    state = steps.compute_state(root, topic, None)
    step = _resolve_step(state)
    instruction, document = _instruction_and_document(step, root, topic, branch, state)
    return render_command(host_prefix(env, override), instruction, document)


def _resolve_step(state: WorkflowState) -> int:
    """Return the base step, advanced past its review when the current doc is settled.

    Args:
        state: The workflow state read from disk.

    Returns:
        The first ``next_step_numbers`` step, advanced past its review step when
        the document that review step reads carries a decisions table (Q02). A
        step with no review document (everything but 2, 5, and 8) is returned as
        is.
    """
    step = steps.next_step_numbers(state)[0]
    review_doc = {2: state.requirement, 5: state.design, 8: state.plan}.get(step)
    if review_doc is not None and docs.has_decisions_table(review_doc):
        return ADVANCE_PAST_REVIEW[step]
    return step


def _instruction_and_document(
    step: int,
    root: Path,
    topic: Topic,
    branch: str,
    state: WorkflowState,
) -> tuple[str, str]:
    """Return the instruction and the target document for a resolved step.

    Step 1 is special: off the slug branch a new draft is still to be processed;
    on the slug branch the requirement is written. Every other step names the
    document of its artifact role through ``_document``.

    Args:
        step: The resolved step number.
        root: The project root, used to make document paths relative.
        topic: The resolved topic.
        branch: The current branch name (the step-1 process-draft case).
        state: The workflow state, holding the existing document paths.

    Returns:
        An ``(instruction, document)`` pair for ``render_command``.
    """
    if step == 1 and branch != topic.slug:
        return PROCESS_DRAFT, _relpath(root, topic.draft_path)
    return STEP_INSTRUCTION[step], _document(root, topic, STEP_ROLE[step], state)


def _document(root: Path, topic: Topic, role: str, state: WorkflowState) -> str:
    """Return the document for a role: the existing one, or the one to produce.

    Args:
        root: The project root, used to make an existing path relative.
        topic: The resolved topic, used to name a document still to be produced.
        role: The artifact role (``requirement``, ``design``, or ``plan``).
        state: The workflow state holding the existing document paths.

    Returns:
        The relative path of the existing document for the role when present,
        otherwise the relative path of the document a write step produces.
    """
    existing = {
        "requirement": state.requirement,
        "design": state.design,
        "plan": state.plan,
    }[role]
    if existing is not None:
        return _relpath(root, existing)
    return f"{DOCS_DIR}/{PRODUCED_TYPE[role]}.{topic.version}.{topic.slug}.md"


def _relpath(root: Path, path: Path) -> str:
    """Return ``path`` as a posix string relative to the project root."""
    return Path(os.path.relpath(Path(path).resolve(), root)).as_posix()


# eof
