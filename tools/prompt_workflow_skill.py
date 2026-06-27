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
target document, then renders. For the implementation cycle, an available
validation plan also contributes the plan step id so ``implement-step`` receives
the argument it needs.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_docs as docs
from tools import prompt_workflow_git as git
from tools import prompt_workflow_handoff as handoff
from tools import prompt_workflow_memory as memory
from tools import prompt_workflow_plan as plan
from tools import prompt_workflow_steps as steps
from tools.prompt_workflow_models import VALIDATION_SUFFIX, MemoryRecord, Topic

if TYPE_CHECKING:
    from collections.abc import Mapping

    from tools.prompt_workflow_models import WorkflowState

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
# Workflow step number that hands execution to the plan implementation cycle.
IMPLEMENT_STEP = 10


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
    prefix = host_prefix(env, override)
    if step == IMPLEMENT_STEP:
        plan_step = _plan_step_to_implement(root, state)
        command = render_command(prefix, instruction, document)
        return command if plan_step is None else f"{command} step {plan_step}"
    return render_command(prefix, instruction, document)


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


def _plan_step_to_implement(root: Path, state: WorkflowState) -> str | None:
    """Return the validation-plan step for an ``implement-step`` command.

    Args:
        root: The project root, used for commit-history checks.
        state: The workflow state holding the validation plan path.

    Returns:
        The plan step id to append, or None when no validation plan can provide
        one.
    """
    if state.validation_plan is None:
        return None
    plan_steps = plan.parse_validation_steps(state.validation_plan.read_text(encoding="utf-8"))
    if not plan_steps:
        return None
    branch_start = git.fork_point(root)

    def _has_commit(number: str) -> bool:
        return git.has_step_commit(root, number, branch_start)

    step, _verified, _terminal = plan.derive_x(plan_steps, _has_commit)
    return step


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


# Exit code when the skill mode has no command to emit (a forced skill that is not
# yet applicable, or no resolvable topic): stdout stays empty so the caller never
# reads the signal as a command (Q03).
EXIT_NOT_APPLICABLE = 3
# The document role a forced skill targets; the skill is emitted only when that
# document exists (Q04). Review and consolidate are not forceable here, since they
# read whichever document is current rather than a single owned one.
FORCED_ROLE = {
    "process-draft": "draft",
    "write-requirement": "requirement",
    "write-design": "design",
    "write-plans": "plan",
    "implement-step": "plan",
}


def run_skill(
    root: Path,
    skill_name: str | None,
    host_override: str | None,
    after_commit: str | None = None,
) -> int:
    """Print the bare next-step command for the current topic, or a forced skill.

    With ``after_commit`` set, prints the post-commit next action for that
    just-committed plan step instead (Step 7). Otherwise resolves the topic
    without a menu (the single draft, or the branch-locked one), then prints the
    disk-derived next command, or - with a skill name - that skill's command when
    its document exists. When nothing applies (no resolvable topic, a forced skill
    whose document is absent, or no next step after the commit) it writes a
    one-line note to stderr, leaves stdout empty, and returns
    ``EXIT_NOT_APPLICABLE`` so the caller never reads the signal as a command (Q03).

    Args:
        root: The project root.
        skill_name: A forced skill name, or None for the derived next step.
        host_override: A host token forcing the prefix, or None to detect it.
        after_commit: A just-committed plan step to derive the post-commit action
            for, or None for the normal next-step or forced-skill behavior.

    Returns:
        0 when a command is printed, ``EXIT_NOT_APPLICABLE`` otherwise.
    """
    if after_commit is not None:
        return _emit(
            post_commit_command(root, after_commit, os.environ, host_override),
            f"pw skill: no next step after committing {after_commit}.\n",
        )
    branch = git.current_branch(root)
    topic = handoff.resolve_topic(
        docs.relevant_drafts(root, root),
        memory.read_memory(root),
        branch,
    )
    if topic is None:
        return _emit(None, "pw skill: no topic resolved on this branch.\n")
    if skill_name is not None:
        return _emit(
            forced_command(root, topic, skill_name, os.environ, host_override),
            f"pw skill: {skill_name} is not applicable here.\n",
        )
    return _emit(next_command(root, topic, branch, os.environ, host_override), "")


def _emit(command: str | None, not_applicable_note: str) -> int:
    """Print a command to stdout and return 0, or note its absence on stderr.

    Args:
        command: The command to print, or None when nothing applies.
        not_applicable_note: The stderr line written when command is None.

    Returns:
        0 when a command is printed; ``EXIT_NOT_APPLICABLE`` when it is None.
    """
    if command is None:
        sys.stderr.write(not_applicable_note)
        return EXIT_NOT_APPLICABLE
    sys.stdout.write(f"{command}\n")
    return 0


def forced_command(
    root: Path,
    topic: Topic,
    skill_name: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Return a forced skill's command when its document exists, else None (Q04).

    Args:
        root: The project root, used to make the document path relative.
        topic: The resolved topic.
        skill_name: The forced skill name (a key of ``FORCED_ROLE``).
        env: The process environment, read for the host prefix.
        override: A host token forcing the prefix, or None to detect it.

    Returns:
        The host-prefixed command naming the skill's document when that document
        exists; None when the skill is unknown or its document is absent.
    """
    role = FORCED_ROLE.get(skill_name)
    if role is None:
        return None
    state = steps.compute_state(root, topic, None)
    doc = (
        topic.draft_path
        if role == "draft"
        else {
            "requirement": state.requirement,
            "design": state.design,
            "plan": state.plan,
        }[role]
    )
    if doc is None:
        return None
    instruction = f"{skill_name}{MD_SUFFIX}"
    return render_command(host_prefix(env, override), instruction, _relpath(root, doc))


def post_commit_command(
    root: Path,
    committed_step: str,
    env: Mapping[str, str],
    override: str | None = None,
) -> str | None:
    """Return the command to chain after committing ``committed_step`` (Step 7).

    Told the plan step the commit completes, this names the step after it for
    ``implement-step``; once that step was the last, ``prepare-release``; and when
    no validation plan is resolved (a standalone commit, no effort) or the step is
    not in the plan, None.

    Args:
        root: The project root.
        committed_step: The plan step id the commit just completed.
        env: The process environment, read for the host prefix.
        override: A host token forcing the prefix, or None to detect it.

    Returns:
        The host-prefixed command for the next action, or None when there is no
        plan in play or the committed step is not one of its steps.
    """
    branch = git.current_branch(root)
    record = memory.read_memory(root)
    topic = handoff.resolve_topic(docs.relevant_drafts(root, root), record, branch)
    if topic is None:
        topic = _resolve_post_commit_topic(root, record, branch)
    if topic is None:
        return None
    state = steps.compute_state(root, topic, None)
    if state.validation_plan is None:
        return None
    numbers = [
        plan_step.number
        for plan_step in plan.parse_validation_steps(
            state.validation_plan.read_text(encoding="utf-8"),
        )
    ]
    if committed_step not in numbers:
        return None
    prefix = host_prefix(env, override)
    index = numbers.index(committed_step)
    if index + 1 < len(numbers):
        plan_doc = _document(root, topic, "plan", state)
        return f"{prefix}implement-step on {plan_doc} step {numbers[index + 1]}"
    return f"{prefix}prepare-release"


def _resolve_post_commit_topic(
    root: Path,
    record: MemoryRecord | None,
    branch: str,
) -> Topic | None:
    """Resolve a plan topic when the original draft is no longer discoverable."""
    candidates = _plan_topics(root)
    if not candidates:
        return None
    if record is not None:
        matching = [
            topic
            for topic in candidates
            if topic.version == record.version and topic.slug == record.topic
        ]
        if len(matching) == 1:
            return matching[0]
    branch_key = _slug_key(branch.rsplit("/", maxsplit=1)[-1])
    branch_matches = [
        topic for topic in candidates if branch_key.endswith(_slug_key(topic.slug))
    ]
    if len(branch_matches) == 1:
        return branch_matches[0]
    return None


def _plan_topics(root: Path) -> list[Topic]:
    """Return unique topics that have both a plan and a validation plan."""
    topics: list[Topic] = []
    seen: set[tuple[str, str]] = set()
    for directory in docs.docs_dirs(root):
        for entry in sorted(directory.iterdir()):
            topic = _topic_from_validation_plan(root, entry)
            if topic is None:
                continue
            key = (topic.version, topic.slug)
            if key in seen or docs.select_document(root, topic, "plan") is None:
                continue
            seen.add(key)
            topics.append(topic)
    return topics


def _topic_from_validation_plan(root: Path, path: Path) -> Topic | None:
    """Parse a Topic from ``plan.<version>.<slug>.validation.md``."""
    name = path.name
    if (
        not path.is_file()
        or not name.startswith("plan.")
        or not name.endswith(VALIDATION_SUFFIX)
    ):
        return None
    core = name[len("plan.") : -len(VALIDATION_SUFFIX)]
    match = docs.VERSION_RE.match(core)
    if match is None:
        return None
    version = match.group(0)
    rest = core[len(version) :]
    if not rest.startswith(".") or not rest[1:]:
        return None
    slug = rest[1:]
    draft = root / DOCS_DIR / f"draft.{version}.{slug}{MD_SUFFIX}"
    return Topic(version=version, slug=slug, draft_path=draft.resolve())


def _slug_key(value: str) -> str:
    """Canonicalize branch and topic slugs for fallback matching."""
    return value.replace("-", "_")


# eof
