"""Tests for the open-questions document tool.

The tool manages the ``## Open questions`` section of a
``docs/<type>.vX.Y.Z.<topic>.md`` document and its
``a.<base>.open.questions.md`` companion kept at the project root, across three
mutually exclusive modes: ``--create``, ``--strip`` and ``--append``.

These tests cover the pure helpers (version extraction, companion naming,
section strip/extract/append), the document lookup under ``docs`` and
``docs/<vX.Y.Z>``, and the three CLI modes including their fatal preconditions.
The shared ``find_project_root`` helper is monkeypatched to a temporary project
root so the tool stays self-contained, mirroring the EOF tool tests. The
``__main__`` script guard is run with ``runpy`` for both the success exit and the
fatal exit through ``_log_fatal``, and the append helper is covered for a section
with no trailing newline.
"""

from __future__ import annotations

import runpy
import sys
from typing import TYPE_CHECKING

import pytest

from tools import find_project_root as shared_find_project_root
from tools import open_questions_md

if TYPE_CHECKING:
    from pathlib import Path


def _patch_root(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    """Point the tool's project-root helper at a temporary root."""

    def fake_find_project_root(_start: Path) -> Path:
        return root

    monkeypatch.setattr(open_questions_md, "find_project_root", fake_find_project_root)


def _patch_shared_root(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    """Point the package-level helper the script re-imports under runpy at a root."""

    def fake_find_project_root(_start: Path) -> Path:
        return root

    monkeypatch.setattr("tools.find_project_root", fake_find_project_root)


def _write_doc(
    root: Path,
    name: str,
    content: str,
    *,
    subdir: str | None = None,
) -> Path:
    """Create a document under ``<root>/docs`` (optionally a version subdir)."""
    docs_dir = root / "docs"
    target_dir = docs_dir / subdir if subdir else docs_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    doc_path = target_dir / name
    doc_path.write_text(content, encoding="utf-8")
    return doc_path


# ---------------------------
# Shared root helper reuse
# ---------------------------


def test_reuses_shared_find_project_root_symbol() -> None:
    """The tool should reuse the shared project-root helper."""
    assert open_questions_md.find_project_root is shared_find_project_root


# ---------------------------
# Pure helpers
# ---------------------------


def test_extract_version_three_parts() -> None:
    """A three-part version token is extracted from the document name."""
    # Act / Assert
    assert open_questions_md._extract_version("design.v1.2.3.cdc-gap.md") == "v1.2.3"


def test_extract_version_two_parts() -> None:
    """A two-part version token is extracted from the document name."""
    # Act / Assert
    assert open_questions_md._extract_version("plan.v8.11.perf.md") == "v8.11"


def test_extract_version_absent_returns_none() -> None:
    """A name without a version token yields None."""
    # Act / Assert
    assert open_questions_md._extract_version("notes.md") is None


def test_companion_name_format() -> None:
    """The companion name wraps the base with the a.*.open.questions.md form."""
    # Act
    companion = open_questions_md._companion_name("design.v1.2.3.cdc-gap")

    # Assert
    assert companion == "a.design.v1.2.3.cdc-gap.open.questions.md"


def test_strip_open_questions_truncates_at_marker() -> None:
    """Stripping returns the text before the marker line and a changed flag."""
    # Arrange
    text = "x\n## Open questions for v1\ny\n"

    # Act
    new_text, changed = open_questions_md._strip_open_questions(text)

    # Assert
    assert new_text == "x\n"
    assert changed is True


def test_strip_open_questions_no_marker_is_unchanged() -> None:
    """Stripping a marker-less text returns it unchanged with changed=False."""
    # Arrange
    text = "x\ny\n"

    # Act
    new_text, changed = open_questions_md._strip_open_questions(text)

    # Assert
    assert new_text == text
    assert changed is False


def test_extract_section_returns_from_marker() -> None:
    """Extraction returns the marker line and everything after it."""
    # Act
    section = open_questions_md._extract_section("pre\n## Open questions z\nq\n")

    # Assert
    assert section == "## Open questions z\nq\n"


def test_extract_section_without_marker_returns_none() -> None:
    """Extraction returns None when no marker line is present."""
    # Act / Assert
    assert open_questions_md._extract_section("no marker here\n") is None


def test_append_section_inserts_one_empty_line() -> None:
    """Appending separates the body and the section by exactly one empty line."""
    # Act
    combined = open_questions_md._append_section("a\n", "## Open questions\nbody\n")

    # Assert: between "a" and "## Open questions" there is exactly one empty line.
    assert combined == "a\n\n## Open questions\nbody\n"
    assert combined.splitlines() == ["a", "", "## Open questions", "body"]


def test_append_section_collapses_trailing_blank_lines() -> None:
    """Trailing blank/whitespace lines collapse to a single empty line."""
    # Act
    combined = open_questions_md._append_section("a\n   \n\n\n", "## Open questions\n")

    # Assert: only one empty line survives before the section.
    assert combined == "a\n\n## Open questions\n"


def test_append_section_adds_trailing_newline() -> None:
    """A section with no trailing newline gets exactly one appended."""
    # Act
    combined = open_questions_md._append_section("a\n", "## Open questions\nbody")

    # Assert: the missing trailing newline is added.
    assert combined == "a\n\n## Open questions\nbody\n"


# ---------------------------
# Document lookup
# ---------------------------


def test_resolve_doc_in_docs_root(tmp_path: Path) -> None:
    """A document directly under docs/ is located."""
    # Arrange
    doc = _write_doc(tmp_path, "design.v1.2.3.topic.md", "# Body\n")

    # Act
    resolved = open_questions_md._resolve_doc(tmp_path, "design.v1.2.3.topic.md")

    # Assert
    assert resolved == doc


def test_resolve_doc_in_version_subdir(tmp_path: Path) -> None:
    """A document under docs/<vX.Y.Z>/ is located via the version token."""
    # Arrange
    doc = _write_doc(tmp_path, "design.v1.2.3.topic.md", "# Body\n", subdir="v1.2.3")

    # Act
    resolved = open_questions_md._resolve_doc(tmp_path, "design.v1.2.3.topic.md")

    # Assert
    assert resolved == doc


def test_resolve_doc_missing_raises(tmp_path: Path) -> None:
    """A missing document fails early with a fatal error."""
    # Act / Assert
    with pytest.raises(open_questions_md.OpenQuestionsError, match="not found"):
        open_questions_md._resolve_doc(tmp_path, "design.v1.2.3.topic.md")


def test_resolve_doc_empty_raises(tmp_path: Path) -> None:
    """An empty document fails early with a fatal error."""
    # Arrange
    _write_doc(tmp_path, "design.v1.2.3.topic.md", "   \n")

    # Act / Assert
    with pytest.raises(open_questions_md.OpenQuestionsError, match="empty"):
        open_questions_md._resolve_doc(tmp_path, "design.v1.2.3.topic.md")


# ---------------------------
# --create mode
# ---------------------------


def test_create_makes_empty_companion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--create writes an empty companion at the project root."""
    # Arrange
    _patch_root(monkeypatch, tmp_path)
    _write_doc(tmp_path, "design.v1.2.3.topic.md", "# Body\n")

    # Act
    exit_code = open_questions_md.main(["design.v1.2.3.topic.md", "--create"])

    # Assert
    companion = tmp_path / "a.design.v1.2.3.topic.open.questions.md"
    assert exit_code == 0
    assert companion.is_file()
    assert companion.read_text(encoding="utf-8") == ""


def test_create_is_no_op_when_companion_already_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--create leaves an already-empty companion in place."""
    # Arrange
    _patch_root(monkeypatch, tmp_path)
    _write_doc(tmp_path, "design.v1.2.3.topic.md", "# Body\n")
    companion = tmp_path / "a.design.v1.2.3.topic.open.questions.md"
    companion.write_text("", encoding="utf-8")

    # Act
    exit_code = open_questions_md.main(["design.v1.2.3.topic.md", "-c"])

    # Assert
    assert exit_code == 0
    assert companion.read_text(encoding="utf-8") == ""


def test_create_empties_existing_non_empty_companion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--create truncates a companion that already holds content."""
    # Arrange
    _patch_root(monkeypatch, tmp_path)
    _write_doc(tmp_path, "design.v1.2.3.topic.md", "# Body\n")
    companion = tmp_path / "a.design.v1.2.3.topic.open.questions.md"
    companion.write_text("## Open questions\ndrop me\n", encoding="utf-8")

    # Act
    exit_code = open_questions_md.main(["design.v1.2.3.topic.md", "--create"])

    # Assert
    assert exit_code == 0
    assert companion.read_text(encoding="utf-8") == ""


# ---------------------------
# --strip mode
# ---------------------------


def test_strip_truncates_document_at_marker(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--strip removes the marker line and everything after it."""
    # Arrange
    _patch_root(monkeypatch, tmp_path)
    content = "# Design\n\nBody line.\n\n## Open questions for v1.2.3\n\n### Q01: foo\n"
    doc = _write_doc(tmp_path, "design.v1.2.3.topic.md", content)

    # Act
    exit_code = open_questions_md.main(["design.v1.2.3.topic.md", "--strip"])

    # Assert
    assert exit_code == 0
    assert doc.read_text(encoding="utf-8") == "# Design\n\nBody line.\n\n"


def test_strip_without_marker_leaves_document_untouched(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--strip is a no-op when the document has no open-questions section."""
    # Arrange
    _patch_root(monkeypatch, tmp_path)
    content = "# Design\n\nBody only.\n"
    doc = _write_doc(tmp_path, "design.v1.2.3.topic.md", content)

    # Act
    exit_code = open_questions_md.main(["design.v1.2.3.topic.md", "-s"])

    # Assert
    assert exit_code == 0
    assert doc.read_text(encoding="utf-8") == content


# ---------------------------
# --append mode
# ---------------------------


def test_append_adds_section_after_one_empty_line(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--append concatenates the companion section after one empty line.

    The document here already ends with trailing blank lines (as --strip would
    leave it); those collapse so a single empty line separates the body from
    the appended section.
    """
    # Arrange
    _patch_root(monkeypatch, tmp_path)
    doc = _write_doc(tmp_path, "design.v1.2.3.topic.md", "# Design\n\nSome body.\n\n")
    companion = tmp_path / "a.design.v1.2.3.topic.open.questions.md"
    companion.write_text(
        "intro junk\n## Open questions for v1.2.3\n\n### Q01: foo\n",
        encoding="utf-8",
    )

    # Act
    exit_code = open_questions_md.main(["design.v1.2.3.topic.md", "--append"])

    # Assert
    expected = (
        "# Design\n\nSome body.\n\n## Open questions for v1.2.3\n\n### Q01: foo\n"
    )
    assert exit_code == 0
    assert doc.read_text(encoding="utf-8") == expected


def test_append_missing_companion_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--append fails when the companion file is absent."""
    # Arrange
    _patch_root(monkeypatch, tmp_path)
    _write_doc(tmp_path, "design.v1.2.3.topic.md", "# Design\n")

    # Act / Assert
    with pytest.raises(open_questions_md.OpenQuestionsError, match="not found"):
        open_questions_md.main(["design.v1.2.3.topic.md", "-a"])


def test_append_companion_without_marker_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """--append fails when the companion has no open-questions section."""
    # Arrange
    _patch_root(monkeypatch, tmp_path)
    _write_doc(tmp_path, "design.v1.2.3.topic.md", "# Design\n")
    companion = tmp_path / "a.design.v1.2.3.topic.open.questions.md"
    companion.write_text("just notes, no section\n", encoding="utf-8")

    # Act / Assert
    with pytest.raises(open_questions_md.OpenQuestionsError, match="No '## Open"):
        open_questions_md.main(["design.v1.2.3.topic.md", "--append"])


# ---------------------------
# Shared precondition
# ---------------------------


def test_main_rejects_non_md_document_name(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A document name without a .md suffix fails early."""
    # Arrange
    _patch_root(monkeypatch, tmp_path)

    # Act / Assert
    with pytest.raises(open_questions_md.OpenQuestionsError, match="Expected a"):
        open_questions_md.main(["design.v1.2.3.topic.txt", "--create"])


# ---------------------------
# __main__ script guard
# ---------------------------


def test_script_runs_as_main_and_creates_companion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Running as __main__ executes a mode and exits 0 through the script guard."""
    # Arrange
    _patch_shared_root(monkeypatch, tmp_path)
    _write_doc(tmp_path, "design.v1.2.3.topic.md", "# Body\n")
    script_path = open_questions_md.__file__
    monkeypatch.setattr(sys, "argv", [script_path, "design.v1.2.3.topic.md", "--create"])

    # Act
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(script_path, run_name="__main__")

    # Assert
    assert excinfo.value.code == 0
    assert (tmp_path / "a.design.v1.2.3.topic.open.questions.md").is_file()


def test_script_logs_fatal_on_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A fatal error in __main__ exits with EXIT_FATAL through _log_fatal."""
    # Arrange
    _patch_shared_root(monkeypatch, tmp_path)
    script_path = open_questions_md.__file__
    monkeypatch.setattr(sys, "argv", [script_path, "not-a-doc-name", "--create"])

    # Act
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(script_path, run_name="__main__")

    # Assert
    assert excinfo.value.code == open_questions_md.EXIT_FATAL


# eof
