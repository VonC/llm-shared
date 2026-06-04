"""Read and write the ``a.prompt_memory`` file for prompt_workflow.

The memory file persists the workflow context as ``key=value`` lines under a
single ``[topic]`` section (Q03): the branch, the version, the topic slug, the
current step number, and the chosen instruction. The step is stored as a number
because the same instruction recurs at different steps. Parsing uses the
standard-library ``configparser`` so the file stays easy to read and hand-edit.

The cycle's ``plan_step`` id is read back as a raw string, not an int, because it
may carry a letter suffix such as ``4A`` for a sub-step (Q41); only the workflow
``step`` is parsed as an int.
"""

from __future__ import annotations

import configparser
from typing import TYPE_CHECKING

from tools.prompt_workflow_models import MemoryRecord, PromptWorkflowError

if TYPE_CHECKING:
    from pathlib import Path

# Name of the memory file kept at the project root.
MEMORY_FILENAME = "a.prompt_memory"
# The single section holding the workflow context.
MEMORY_SECTION = "topic"
# Required keys that every memory file must carry.
_REQUIRED_KEYS = ("branch", "version", "topic")


def memory_path(root: Path) -> Path:
    """Return the path to the memory file at the project root."""
    return root / MEMORY_FILENAME


def _parse_step(raw: str | None) -> int | None:
    """Return the step number parsed from its stored text, or None when absent."""
    if raw is None or not raw.strip():
        return None
    try:
        return int(raw.strip())
    except ValueError as err:
        msg = f"Invalid step value in memory file: {raw!r}"
        raise PromptWorkflowError(msg) from err


def read_memory(root: Path) -> MemoryRecord | None:
    """Return the persisted memory record, or None when the file is absent.

    Args:
        root: The project root holding the memory file.

    Returns:
        The parsed MemoryRecord, or None when no memory file exists yet.

    Raises:
        PromptWorkflowError: When the file exists but lacks the section or a
            required key, or carries a non-integer step.
    """
    path = memory_path(root)
    if not path.is_file():
        return None

    parser = configparser.ConfigParser()
    parser.read_string(path.read_text(encoding="utf-8"))
    if not parser.has_section(MEMORY_SECTION):
        msg = f"Memory file has no [{MEMORY_SECTION}] section: {path}"
        raise PromptWorkflowError(msg)

    section = parser[MEMORY_SECTION]
    missing = [key for key in _REQUIRED_KEYS if key not in section]
    if missing:
        msg = f"Memory file is missing keys {missing}: {path}"
        raise PromptWorkflowError(msg)

    instruction = section.get("instruction") or None
    return MemoryRecord(
        branch=section["branch"],
        version=section["version"],
        topic=section["topic"],
        step=_parse_step(section.get("step")),
        instruction=instruction,
        plan_step=(section.get("plan_step") or "").strip() or None,
    )


def write_memory(root: Path, record: MemoryRecord) -> None:
    """Write the memory record to the project root as a single-section file."""
    parser = configparser.ConfigParser()
    parser[MEMORY_SECTION] = {
        "branch": record.branch,
        "version": record.version,
        "topic": record.topic,
        "step": "" if record.step is None else str(record.step),
        "instruction": record.instruction or "",
        "plan_step": "" if record.plan_step is None else str(record.plan_step),
    }
    with memory_path(root).open("w", encoding="utf-8") as handle:
        parser.write(handle)


# eof
