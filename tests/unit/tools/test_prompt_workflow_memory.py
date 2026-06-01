"""Tests for the a.prompt_memory read/write helpers of prompt_workflow.

Fix: Cover the absent-file case, a full round trip, the empty-instruction
normalization, and the three malformed-file errors (no section, missing key,
non-integer step).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_memory as memory
from tools.prompt_workflow_models import MemoryRecord, PromptWorkflowError

if TYPE_CHECKING:
    from pathlib import Path


def test_read_memory_absent_returns_none(tmp_path: Path) -> None:
    """No memory file yields None."""
    assert memory.read_memory(tmp_path) is None


def test_write_then_read_round_trip(tmp_path: Path) -> None:
    """A written record reads back with the same fields."""
    record = MemoryRecord(
        branch="feature/iso",
        version="v9.8.0",
        topic="resources_isolation",
        step=4,
        instruction="write-design.md",
    )

    memory.write_memory(tmp_path, record)

    assert memory.read_memory(tmp_path) == record


def test_read_memory_empty_instruction_becomes_none(tmp_path: Path) -> None:
    """An empty instruction value normalizes to None on read."""
    memory.write_memory(
        tmp_path,
        MemoryRecord(branch="main", version="v9.8.0", topic="iso"),
    )

    loaded = memory.read_memory(tmp_path)

    assert loaded is not None
    assert loaded.step is None
    assert loaded.instruction is None


def test_read_memory_without_section_errors(tmp_path: Path) -> None:
    """A file lacking the [topic] section is a fatal error."""
    memory.memory_path(tmp_path).write_text("[other]\nx=1\n", encoding="utf-8")

    with pytest.raises(PromptWorkflowError, match="no \\[topic\\] section"):
        memory.read_memory(tmp_path)


def test_read_memory_missing_key_errors(tmp_path: Path) -> None:
    """A file missing a required key is a fatal error."""
    memory.memory_path(tmp_path).write_text(
        "[topic]\nbranch=main\n",
        encoding="utf-8",
    )

    with pytest.raises(PromptWorkflowError, match="missing keys"):
        memory.read_memory(tmp_path)


def test_read_memory_invalid_step_errors(tmp_path: Path) -> None:
    """A non-integer step value is a fatal error."""
    memory.memory_path(tmp_path).write_text(
        "[topic]\nbranch=main\nversion=v9.8.0\ntopic=iso\nstep=abc\n",
        encoding="utf-8",
    )

    with pytest.raises(PromptWorkflowError, match="Invalid step value"):
        memory.read_memory(tmp_path)


# eof
