"""Tests for topic and document resolution in prompt_workflow.

Fix: Cover draft-name parsing, the relevant-draft detection (with and without a
fork point), the docs directory discovery, the document matching rules for every
role, most-recent selection by mtime, and open-questions detection.

v0.9.0: this test moved into the nested ``test_prompt_workflow_docs/`` form (Q08)
and gained a ``has_decisions_table`` case for the consolidated decisions sections
the skill routing reads (Q03).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_docs as docs
from tools.prompt_workflow_models import Topic

if TYPE_CHECKING:
    import pytest

# pyright: reportPrivateUsage=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false
# ruff: noqa: SLF001

_ISO = Topic(version="v9.8.0", slug="iso", draft_path=Path("d.md"))


def test_parse_draft_name_variants() -> None:
    """Draft parsing accepts a valid name and rejects the malformed ones."""
    assert docs.parse_draft_name("draft.v9.8.0.resources_isolation.md") == (
        "v9.8.0",
        "resources_isolation",
    )
    assert docs.parse_draft_name("feature.v9.8.0.iso.md") is None
    assert docs.parse_draft_name("draft.v9.8.0.iso.txt") is None
    assert docs.parse_draft_name("draft.iso.md") is None
    assert docs.parse_draft_name("draft.v9.8.0iso.md") is None
    assert docs.parse_draft_name("draft.v9.8.0..md") is None


def test_draft_relpath_topic_requires_docs_folder() -> None:
    """A draft path only counts when it lives under the docs folder."""
    assert docs._draft_relpath_topic(Path("src/draft.v1.0.0.x.md")) is None
    assert docs._draft_relpath_topic(Path("docs/draft.v1.0.0.x.md")) == ("v1.0.0", "x")


def _make_drafts(root: Path) -> None:
    docs_dir = root / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v9.8.0.iso.md").write_text("draft", encoding="utf-8")
    (docs_dir / "draft.v1.0.0.other.md").write_text("draft", encoding="utf-8")
    version_dir = docs_dir / "v9.8.0"
    version_dir.mkdir()
    (version_dir / "draft.v9.8.0.iso.md").write_text("draft", encoding="utf-8")


def test_relevant_drafts_with_fork_point(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Branch and working-tree drafts merge, skipping non-drafts and ghosts."""
    _make_drafts(tmp_path)
    monkeypatch.setattr(
        docs.git,
        "working_tree_changed_files",
        lambda _cwd: ["docs/draft.v9.8.0.iso.md", "docs/notes.md", "x/draft.v3.0.0.z.md"],
    )
    monkeypatch.setattr(docs.git, "fork_point", lambda _cwd: "base")
    monkeypatch.setattr(
        docs.git,
        "changed_files_since",
        lambda _cwd, _base: [
            "docs/draft.v9.8.0.iso.md",
            "docs/v9.8.0/draft.v9.8.0.iso.md",
            "docs/draft.v1.0.0.other.md",
            "docs/draft.v2.0.0.ghost.md",
        ],
    )

    topics = docs.relevant_drafts(tmp_path, tmp_path)

    assert [(topic.version, topic.slug) for topic in topics] == [
        ("v1.0.0", "other"),
        ("v9.8.0", "iso"),
    ]


def test_relevant_drafts_without_fork_point(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """With no fork point only the working-tree drafts are considered (Q07)."""
    _make_drafts(tmp_path)
    monkeypatch.setattr(
        docs.git,
        "working_tree_changed_files",
        lambda _cwd: ["docs/draft.v9.8.0.iso.md"],
    )
    monkeypatch.setattr(docs.git, "fork_point", lambda _cwd: None)

    topics = docs.relevant_drafts(tmp_path, tmp_path)

    assert [(topic.version, topic.slug) for topic in topics] == [("v9.8.0", "iso")]


def test_docs_dirs_empty_and_with_version_subdir(tmp_path: Path) -> None:
    """Docs discovery returns nothing without docs, then docs and version dirs."""
    assert docs.docs_dirs(tmp_path) == []

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "v9.8.0").mkdir()
    (docs_dir / "archive").mkdir()
    (docs_dir / "draft.v9.8.0.iso.md").write_text("d", encoding="utf-8")

    assert docs.docs_dirs(tmp_path) == [docs_dir, docs_dir / "v9.8.0"]


def _make_topic_docs(root: Path) -> None:
    docs_dir = root / "docs"
    docs_dir.mkdir()
    names = [
        "feature-request.v9.8.0.iso.md",
        "issue.v9.8.0.iso.md",
        "design.v9.8.0.iso.md",
        "design.v9.8.0.iso_sub.md",
        "design.v9.8.0.other.md",
        "plan.v9.8.0.iso.md",
        "plan.v9.8.0.iso.validation.md",
        "notes.txt",
    ]
    for name in names:
        (docs_dir / name).write_text("body", encoding="utf-8")


def test_find_matching_documents_per_role(tmp_path: Path) -> None:
    """Matching honors the role prefixes, the validation suffix, and sub-topics."""
    _make_topic_docs(tmp_path)

    def names(role: str) -> list[str]:
        return [path.name for path in docs.find_matching_documents(tmp_path, _ISO, role)]

    assert names("requirement") == [
        "feature-request.v9.8.0.iso.md",
        "issue.v9.8.0.iso.md",
    ]
    assert names("design") == ["design.v9.8.0.iso.md", "design.v9.8.0.iso_sub.md"]
    assert names("plan") == ["plan.v9.8.0.iso.md"]
    assert names("validation_plan") == ["plan.v9.8.0.iso.validation.md"]


def test_find_matching_documents_folds_hyphen_and_underscore(tmp_path: Path) -> None:
    """A ``_`` draft slug resolves the hyphenated documents for every role."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    names = [
        "feature-request.v0.8.0.git-history-report.md",
        "design.v0.8.0.git-history-report.md",
        "plan.v0.8.0.git-history-report.md",
        "plan.v0.8.0.git-history-report.validation.md",
    ]
    for name in names:
        (docs_dir / name).write_text("body", encoding="utf-8")
    underscore = Topic(
        version="v0.8.0",
        slug="git_history_report",
        draft_path=Path("d.md"),
    )

    def names_for(role: str) -> list[str]:
        return [
            path.name
            for path in docs.find_matching_documents(tmp_path, underscore, role)
        ]

    assert names_for("requirement") == ["feature-request.v0.8.0.git-history-report.md"]
    assert names_for("design") == ["design.v0.8.0.git-history-report.md"]
    assert names_for("plan") == ["plan.v0.8.0.git-history-report.md"]
    assert names_for("validation_plan") == [
        "plan.v0.8.0.git-history-report.validation.md",
    ]


def test_doc_matches_reverse_separators_and_subtopic() -> None:
    """A hyphen slug resolves an underscore document, including a sub-topic key."""
    version, slug = "v0.8.0", "git-history-report"

    # An underscore document name is matched by the hyphen slug.
    assert docs._doc_matches("design.v0.8.0.git_history_report.md", "design", version, slug)
    # A mixed-separator sub-topic under the umbrella slug still matches.
    assert docs._doc_matches(
        "design.v0.8.0.git-history-report_extra.md", "design", version, slug,
    )
    # A different topic does not match.
    assert not docs._doc_matches("design.v0.8.0.other.md", "design", version, slug)


def test_most_recent_and_select_document(tmp_path: Path) -> None:
    """The most recent match wins on modification time; empty yields None."""
    assert docs.most_recent([]) is None

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    older = docs_dir / "design.v9.8.0.iso.md"
    newer = docs_dir / "design.v9.8.0.iso_sub.md"
    older.write_text("old", encoding="utf-8")
    newer.write_text("new", encoding="utf-8")
    os.utime(older, (1_000, 1_000))
    os.utime(newer, (2_000, 2_000))

    assert docs.select_document(tmp_path, _ISO, "design") == newer


def test_has_open_questions(tmp_path: Path) -> None:
    """Open-questions detection matches the section marker line."""
    with_oq = tmp_path / "design.md"
    without_oq = tmp_path / "plan.md"
    with_oq.write_text("# Title\n\n## Open questions\n\n### Q1\n", encoding="utf-8")
    without_oq.write_text("# Title\n\nNo questions here.\n", encoding="utf-8")

    assert docs.has_open_questions(with_oq) is True
    assert docs.has_open_questions(without_oq) is False


def test_has_decisions_table(tmp_path: Path) -> None:
    """Decisions detection matches the three consolidated section titles, else False."""
    for title in (
        "## Requirement clarifications",
        "## Design decisions",
        "## Implementation decisions",
    ):
        doc = tmp_path / "doc.md"
        doc.write_text(f"# Title\n\n{title}\n\n| a | b |\n", encoding="utf-8")
        assert docs.has_decisions_table(doc) is True

    without = tmp_path / "plain.md"
    without.write_text("# Title\n\n## Open questions\n\n### Q1\n", encoding="utf-8")
    assert docs.has_decisions_table(without) is False


# eof
