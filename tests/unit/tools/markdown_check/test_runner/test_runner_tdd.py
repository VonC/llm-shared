"""TDD contracts for inventory, evaluation, and stable runner diagnostics."""

# ruff: noqa: S603, S607

from __future__ import annotations

import json
import subprocess
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Never

import pytest

from tools.markdown_check import runner as runner_module
from tools.markdown_check.runner import (
    CheckerRunner,
    InventoryError,
    tracked_markdown_paths,
)

if TYPE_CHECKING:
    from pathlib import Path


def _policy(tmp_path: Path) -> None:
    (tmp_path / ".markdownlint.json").write_text(
        json.dumps({"MD013": False, "MD033": {"allowed_elements": ["img"]}}),
        encoding="utf-8",
    )
    (tmp_path / ".markdownlint-baseline.json").write_text(
        json.dumps({"version": 1, "allowances": []}),
        encoding="utf-8",
    )


@pytest.fixture
def tracked_repository(tmp_path: Path) -> Path:
    """Build a real tracked inventory outside the measured test call."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "note.MD").write_text("# Note\n", encoding="utf-8")
    (tmp_path / "skip.txt").write_text("skip\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "."],
        check=True,
    )
    return tmp_path


def test_runner_sorts_growth_findings_and_normalizes_paths(tmp_path: Path) -> None:
    """One fixed inventory yields ordered path:line diagnostics and failure."""
    _policy(tmp_path)
    documents = {
        "docs/a.md": "## Only section\n",
        "docs/b.MD": "# Title\n\n## One\n\n## Two\n",
    }
    runner = CheckerRunner(
        tmp_path,
        inventory_loader=lambda _root: ("docs\\b.MD", "docs/a.md"),
        source_reader=lambda path: documents[path.as_posix()],
    )

    result = runner.run()

    assert result.exit_code == 1
    assert result.stdout == (
        "docs/a.md:1: LS001: structured document needs a title",
        "docs/a.md:1: LS002: structured document needs multiple sections",
    )
    assert result.stderr == ()


def test_runner_refines_pointer_links_against_tracked_inventory(tmp_path: Path) -> None:
    """A syntactic pointer is an adapter only when its normalized target exists."""
    _policy(tmp_path)
    pointer = "Read [rule](../../../instructions/rule.md).\n"
    documents = {
        ".agents/llm-shared/instructions/pointer.md": pointer,
        "instructions/rule.md": "# Rule\n\n## One\n\n## Two\n",
    }
    present = CheckerRunner(
        tmp_path,
        inventory_loader=lambda _root: tuple(documents),
        source_reader=lambda path: documents[path.as_posix()],
    ).run()
    missing = CheckerRunner(
        tmp_path,
        inventory_loader=lambda _root: (".agents/llm-shared/instructions/pointer.md",),
        source_reader=lambda path: documents[path.as_posix()],
    ).run()

    assert present.exit_code == 0
    assert missing.stdout == (
        ".agents/llm-shared/instructions/pointer.md:1: LS001: structured document needs a title",
        ".agents/llm-shared/instructions/pointer.md:1: LS002: structured document needs multiple sections",
    )


def test_runner_reports_inventory_and_decoding_failures(tmp_path: Path) -> None:
    """Operational failures stay on stderr and stop evaluation."""
    _policy(tmp_path)

    def failed_inventory(_root: Path) -> Never:
        message = "git ls-files failed"
        raise InventoryError(message)

    inventory_result = CheckerRunner(tmp_path, inventory_loader=failed_inventory).run()
    decode_result = CheckerRunner(
        tmp_path,
        inventory_loader=lambda _root: ("docs/a.md",),
        source_reader=lambda _path: (_ for _ in ()).throw(
            UnicodeDecodeError("utf-8", b"x", 0, 1, "invalid"),
        ),
    ).run()

    assert inventory_result.stderr == ("markdown-check: git ls-files failed",)
    assert decode_result.stderr[0].startswith("markdown-check: cannot read docs/a.md:")


def test_tracked_inventory_uses_git_and_filters_markdown(
    tracked_repository: Path,
) -> None:
    """The production inventory queries Git once and filters suffixes case-insensitively."""
    assert tracked_markdown_paths(tracked_repository) == ("note.MD",)


def test_tracked_inventory_fails_closed_on_git_and_path_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing Git, command failures, decoding, and escaping paths are operational errors."""
    def missing_git(_name: str) -> None:
        return None

    monkeypatch.setattr(runner_module.shutil, "which", missing_git)
    with pytest.raises(InventoryError, match="not found"):
        tracked_markdown_paths(tmp_path)

    def found_git(_name: str) -> str:
        return "git"

    monkeypatch.setattr(runner_module.shutil, "which", found_git)

    def completed_with(stdout: bytes, *, returncode: int = 0) -> object:
        def run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
            return subprocess.CompletedProcess([], returncode, stdout, b"git failed")

        return run

    monkeypatch.setattr(runner_module.subprocess, "run", completed_with(b"", returncode=1))
    with pytest.raises(InventoryError, match="git failed"):
        tracked_markdown_paths(tmp_path)

    for raw in (b"\xff", b"../outside.md\0"):
        monkeypatch.setattr(runner_module.subprocess, "run", completed_with(raw))
        with pytest.raises(InventoryError, match="invalid git ls-files inventory"):
            tracked_markdown_paths(tmp_path)


def test_default_source_reader_reads_utf8_and_rejects_escape(tmp_path: Path) -> None:
    """The production reader remains rooted and uses strict UTF-8."""
    path = tmp_path / "note.md"
    path.write_text("# Note\n\n## One\n\n## Two\n", encoding="utf-8")
    runner = CheckerRunner(tmp_path)

    assert runner._read_source(PurePosixPath("note.md")).startswith("# Note")  # noqa: SLF001
    with pytest.raises(OSError, match="escapes repository"):
        runner._read_source(PurePosixPath("../outside.md"))  # noqa: SLF001


# eof
