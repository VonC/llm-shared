"""Register the groundhog skill in a consuming repository (Q23).

``ghog init`` writes the per-harness pointers of Q13 into the project:
a Claude skill at ``.claude/skills/groundhog/SKILL.md`` and a section in
``AGENTS.md`` for Codex, both referencing the single instruction file
``instructions/groundhog.md`` of llm-shared by relative path. The skill
pointer is fully owned by groundhog and rewritten on every init; the
AGENTS.md content of the project is preserved, the section is appended
once and recognized on later runs.

Fix: both generated texts now name the Q32 lifecycle — completion is
``a.ghog.status`` reading ``state=done``, polled with ``ghog status``,
and ``ghog day --detach`` covers harnesses that kill long calls — so a
consumer registered (or refreshed) after Q32 routes the timeout case
correctly instead of replaying a killed walk.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from tools.groundhog.models import GroundhogError

# The Codex-facing file at the project root.
AGENTS_FILE_NAME: Final = "AGENTS.md"
# The user-level Codex pieces: config folder, prompts folder, /groundhog
# prompt file (Q25).
CODEX_DIR_NAME: Final = ".codex"
CODEX_PROMPTS_DIR: Final = "prompts"
CODEX_PROMPT_FILE: Final = "groundhog.md"
# The heading that marks (and detects) the groundhog AGENTS.md section.
AGENTS_MARKER: Final = "## groundhog"
# The Claude skill pointer location, relative to the project root.
SKILL_DIR_PARTS: Final = (".claude", "skills", "groundhog")
SKILL_FILE_NAME: Final = "SKILL.md"
# The single instruction source, relative to the llm-shared root (Q13).
_INSTRUCTION_PARTS: Final = ("instructions", "groundhog.md")
# The heading of a freshly created AGENTS.md.
_AGENTS_TITLE: Final = "# Agent instructions"


def llm_shared_root() -> Path:
    """Return the llm-shared root, the grandparent of this package.

    Returns:
        The llm-shared repository root.
    """
    return Path(__file__).resolve().parents[2]


def instruction_path() -> Path:
    """Return the groundhog instruction file path (Q13).

    Returns:
        The ``instructions/groundhog.md`` path under llm-shared.
    """
    return llm_shared_root().joinpath(*_INSTRUCTION_PARTS)


def write_skill_pointer(root: Path) -> Path:
    """Write the Claude skill pointer of the consuming project.

    Args:
        root: The consuming project root.

    Returns:
        The written ``SKILL.md`` path.
    """
    skill_dir = root.joinpath(*SKILL_DIR_PARTS)
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = skill_dir / SKILL_FILE_NAME
    path.write_text(_skill_text(skill_dir), encoding="utf-8")
    return path


def update_agents_md(root: Path) -> tuple[Path, bool]:
    """Add the groundhog section to AGENTS.md, once.

    The project's existing AGENTS.md content is never rewritten: when
    the section heading is already there the file is not even opened
    for writing, and an unreadable file aborts before any write.

    Args:
        root: The consuming project root.

    Returns:
        The AGENTS.md path, and whether the section was added (False
        when a groundhog section is already there).

    Raises:
        GroundhogError: When an existing AGENTS.md is not UTF-8
            readable; the file is left untouched.
    """
    path = root / AGENTS_FILE_NAME
    existing = ""
    if path.is_file():
        try:
            existing = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            msg = f"{AGENTS_FILE_NAME} is not UTF-8 readable, left untouched: {path}"
            raise GroundhogError(msg) from exc
    if _has_groundhog_section(existing):
        return path, False
    if existing:
        prefix = existing if existing.endswith("\n") else f"{existing}\n"
        content = f"{prefix}\n{_agents_section(root)}"
    else:
        content = f"{_AGENTS_TITLE}\n\n{_agents_section(root)}"
    path.write_text(content, encoding="utf-8")
    return path, True


def write_codex_prompt(home: Path) -> Path | None:
    """Write the user-level Codex ``/groundhog`` prompt (Q25).

    The prompt is project-agnostic (it routes through the project's
    AGENTS.md section), so one user-level copy serves every repository.

    Args:
        home: The user home directory.

    Returns:
        The written prompt path, or ``None`` when ``~/.codex`` does not
        exist (Codex not set up for this user).
    """
    codex_dir = home / CODEX_DIR_NAME
    if not codex_dir.is_dir():
        return None
    prompts_dir = codex_dir / CODEX_PROMPTS_DIR
    prompts_dir.mkdir(exist_ok=True)
    path = prompts_dir / CODEX_PROMPT_FILE
    path.write_text(_codex_prompt_text(), encoding="utf-8")
    return path


def run_init(root: Path, home: Path | None = None) -> list[str]:
    """Register the groundhog skill pointers in a project (Q23, Q25).

    Args:
        root: The consuming project root.
        home: The user home directory, ``Path.home()`` when ``None``.

    Returns:
        The report lines naming the written files and the triggers.

    Raises:
        GroundhogError: When the llm-shared instruction file is absent,
            or when an existing AGENTS.md is not UTF-8 readable.
    """
    instruction = instruction_path()
    if not instruction.is_file():
        msg = f"instruction file not found: {instruction}"
        raise GroundhogError(msg)
    skill = write_skill_pointer(root)
    agents, added = update_agents_md(root)
    agents_line = (
        f"AGENTS.md section added: {agents}"
        if added
        else f"AGENTS.md already references groundhog: {agents}"
    )
    codex = write_codex_prompt(home if home is not None else Path.home())
    codex_line = (
        f"Codex /groundhog prompt written: {codex}"
        if codex is not None
        else "Codex not detected (no ~/.codex), /groundhog prompt skipped."
    )
    return [
        f"Skill pointer written: {skill}",
        agents_line,
        codex_line,
        'Trigger from your LLM: "run groundhog" (Claude Code and Codex: /groundhog).',
    ]


def _skill_text(skill_dir: Path) -> str:
    """Build the SKILL.md content for one project layout.

    Args:
        skill_dir: The skill folder the relative link starts from.

    Returns:
        The SKILL.md text, frontmatter plus the instruction pointer.
    """
    link = _relative_link(instruction_path(), skill_dir)
    return (
        "---\n"
        "name: groundhog\n"
        "description: Drive the test suite to its global objective - every "
        "test passing and coverage at the project gate - by looping ghog day "
        "and fixes. Use when the user asks to run groundhog, ghog, fix tests "
        "and coverage, or reach 100% coverage.\n"
        "---\n"
        "\n"
        f"Follow the instructions from [groundhog.md]({link}).\n"
    )


def _agents_section(root: Path) -> str:
    """Build the AGENTS.md groundhog section for one project layout.

    The wording is trigger-first and names the two known misreadings
    (running ``groundhog`` as a command, running senv.bat first), the
    failure modes a real Codex session showed (Q25).

    Args:
        root: The consuming project root the relative link starts from.

    Returns:
        The section text, opened by ``AGENTS_MARKER``.
    """
    link = _relative_link(instruction_path(), root)
    return (
        f"{AGENTS_MARKER} (pytest reset loop)\n"
        "\n"
        "When the user asks to run groundhog, ghog, or to fix tests and "
        "coverage: there is no `groundhog` executable or alias to run, and "
        "senv.bat must never be run as a separate step. Read and follow "
        f"`{link}` instead; it drives the test suite to its global objective "
        "(every test passing, coverage at the project gate) through the ghog "
        "wrapper, which loads senv.bat itself. A walk is finished only when "
        "`a.ghog.status` at the project root reads `state=done` - a growing "
        "`a.ghog.log` proves nothing. Poll with `ghog status` (never "
        "redirected: exit 6 while the walk is live, 7 when it was killed), "
        "and when the harness can kill long calls, run the walk detached "
        "(`ghog day --detach`, no redirect) as that instruction describes - "
        "never size a timeout around a walk, never rerun one that may still "
        "be alive.\n"
    )


def _codex_prompt_text() -> str:
    """Build the user-level Codex ``/groundhog`` prompt text (Q25).

    Returns:
        The project-agnostic prompt routing through AGENTS.md.
    """
    return (
        "Run the groundhog pytest reset loop for the current project: read "
        'AGENTS.md at the project root, find its "## groundhog" section, and '
        "follow the llm-shared instruction file it references "
        "(instructions/groundhog.md). There is no `groundhog` executable or "
        "alias to run, and senv.bat must never be run as a separate step - "
        "the ghog wrapper named in the instruction loads it itself. A walk "
        "is finished only when `a.ghog.status` reads `state=done`: poll it "
        "with `ghog status` (exit 6 while the walk is live, 7 when it was "
        "killed) instead of watching the log or the processes, and prefer "
        "`ghog day --detach` when your tool calls can time out - never "
        "rerun a walk while `ghog status` answers 6.\n"
    )


def _has_groundhog_section(content: str) -> bool:
    """Detect the groundhog section heading, anchored at a line start.

    Args:
        content: The current AGENTS.md content.

    Returns:
        True when a line opens with the section marker; a mid-line
        mention of the marker does not count.
    """
    return any(line.startswith(AGENTS_MARKER) for line in content.splitlines())


def _relative_link(target: Path, start: Path) -> str:
    """Build a forward-slash relative link between two paths.

    Args:
        target: The file the link points at.
        start: The folder the link starts from.

    Returns:
        The relative path with forward slashes.
    """
    return os.path.relpath(target, start).replace("\\", "/")


# eof
