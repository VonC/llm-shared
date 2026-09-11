"""Final Step 5 acceptance for independent review-mode documentation.

This sibling keeps final coverage, inventory, and connected-set contracts
separate from the incremental Steps 1 through 4 assertions. Review-resume Step 6
also checks the connected public pages for shipped resumption and waiting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .conftest import (
    _CODE_TUTORIAL,
    _COVERAGE,
    _EXPLANATION,
    _HOW_TO_GUIDES,
    _INVENTORY_CANDIDATES,
    _REFERENCE,
    _SELF_REVIEW_EXPLANATION,
    _SELF_REVIEW_HOW_TO,
    _SPEC_TUTORIAL,
    assert_contains,
    assert_local_links,
    assert_named_paths,
    markdown_table_row,
    read_declared,
)

if TYPE_CHECKING:
    from pathlib import Path

_CONNECTED_DOCUMENTATION = (
    "README.md",
    "wiki/README.md",
    _EXPLANATION,
    _SELF_REVIEW_EXPLANATION,
    _SELF_REVIEW_HOW_TO,
    _SPEC_TUTORIAL,
    _CODE_TUTORIAL,
    *_HOW_TO_GUIDES,
    _REFERENCE,
    *_INVENTORY_CANDIDATES,
)
_PAGE_CRITERION_COUNT = 9
_EVIDENCE_CRITERION_TYPES = {
    "AC10": "Validation evidence",
    "AC11": "Scope evidence",
    "AC12": "Coverage evidence",
}
_FORBIDDEN_EVIDENCE_REFERENCES = ("a.reviewtool", "bin/mdlint")


def _assert_complete_criterion_rows(coverage: str) -> None:
    """Assert every acceptance criterion has one complete row."""
    for number in range(1, 13):
        row = markdown_table_row(coverage, f"AC{number:02d}")
        assert "| Complete |" in row


def _assert_page_criterion_rows(coverage: str) -> None:
    """Assert page criteria retain at least one exact Markdown path."""
    for number in range(1, _PAGE_CRITERION_COUNT + 1):
        assert ".md`" in markdown_table_row(coverage, f"AC{number:02d}")


def _assert_evidence_criterion_rows(coverage: str) -> None:
    """Assert non-page criteria retain their exact evidence types."""
    for criterion, evidence_type in _EVIDENCE_CRITERION_TYPES.items():
        row = markdown_table_row(coverage, criterion)
        assert f"| {evidence_type} |" in row
        assert ".md`" not in row


def _assert_forbidden_evidence_is_absent(coverage: str) -> None:
    """Assert provisional helpers and nonexistent launchers are not evidence."""
    for reference in _FORBIDDEN_EVIDENCE_REFERENCES:
        assert reference not in coverage


def test_step_5_coverage_finalizes_every_criterion(
    docs_root: Path,
) -> None:
    """Step 5 evidence: every criterion has one final result."""
    coverage = read_declared(docs_root, _COVERAGE)

    _assert_complete_criterion_rows(coverage)
    _assert_page_criterion_rows(coverage)
    _assert_evidence_criterion_rows(coverage)
    assert "Pending" not in coverage
    assert "Partial" not in coverage
    _assert_forbidden_evidence_is_absent(coverage)
    assert_contains(
        coverage,
        (
            "`ghog day`",
            "`git diff --check`",
            "`git diff --cached --check`",
            "MD024",
            "MD025",
            "## Step 5 executable evidence",
        ),
    )


def test_step_5_coverage_finalizes_every_inventory_candidate(docs_root: Path) -> None:
    """Step 5 inventory: every candidate keeps one final linked result."""
    coverage = read_declared(docs_root, _COVERAGE)
    for candidate in _INVENTORY_CANDIDATES:
        row = markdown_table_row(coverage, f"`{candidate}`")
        assert "| Update |" in row
        assert "independent-review-mode-contract.md" in row


def test_step_5_connected_set_closes_links_terms_logos_and_gates(
    docs_root: Path,
) -> None:
    """Step 5 acceptance: the bounded connected set retains its contracts."""
    assert_named_paths(docs_root, (*_CONNECTED_DOCUMENTATION, _COVERAGE))
    assert_local_links(docs_root, _CONNECTED_DOCUMENTATION)

    independent_pages = (
        _EXPLANATION,
        _SPEC_TUTORIAL,
        _CODE_TUTORIAL,
        *_HOW_TO_GUIDES,
        _REFERENCE,
    )
    for path in independent_pages:
        markdown = read_declared(docs_root, path)
        assert "logo-llm-shared-transparent.png" in markdown
    terminology = "\n".join(
        read_declared(docs_root, path)
        for path in (_EXPLANATION, _SPEC_TUTORIAL, _CODE_TUTORIAL, _REFERENCE)
    )
    assert "independent review mode" in terminology
    assert "self-review loop" in terminology
    assert "Consolidate" in read_declared(docs_root, _SPEC_TUTORIAL)
    assert "Revise and review again" in read_declared(docs_root, _SPEC_TUTORIAL)
    assert "Commit" in read_declared(docs_root, _CODE_TUTORIAL)
    assert "Rework and review again" in read_declared(docs_root, _CODE_TUTORIAL)


def test_reviewer_rounds_use_reciprocal_active_waits_across_the_docs(
    docs_root: Path,
) -> None:
    """README and each Diataxis purpose present automatic intermediate rounds."""
    readme = read_declared(docs_root, "README.md")
    wiki_home = read_declared(docs_root, "wiki/README.md")
    explanation = read_declared(docs_root, _EXPLANATION)
    spec_tutorial = read_declared(docs_root, _SPEC_TUTORIAL)
    code_tutorial = read_declared(docs_root, _CODE_TUTORIAL)
    spec_how_to = read_declared(
        docs_root,
        "wiki/how-to/run-specification-review.md",
    )
    code_how_to = read_declared(
        docs_root,
        "wiki/how-to/run-implementation-code-review.md",
    )
    reference = read_declared(docs_root, _REFERENCE)

    assert "automatic requestor-reviewer exchange" in readme
    assert "main goal is the automatic" in wiki_home
    assert "reciprocal waiting is the default" in explanation
    assert "Without another command from you" in spec_tutorial
    assert "Without another command from you" in code_tutorial
    assert "do not invoke the reviewer" in spec_how_to
    assert "do not invoke the reviewer" in code_how_to
    assert "reciprocal waiting" in reference


def test_resume_public_docs_describe_shipped_waiting_and_automatic_pickup(docs_root: Path) -> None:
    """Review-resume AC15: every connected page describes the shipped role split."""
    paths = (
        "README.md", "wiki/README.md", _EXPLANATION, _SPEC_TUTORIAL, _CODE_TUTORIAL,
        *_HOW_TO_GUIDES, _REFERENCE,
    )
    for path in paths:
        text = read_declared(docs_root, path)
        assert "has not shipped" not in text
        assert "not shipped yet" not in text
        assert "planned for Step 5" not in text
    readme = read_declared(docs_root, "README.md")
    assert_contains(readme, (".review-artifacts.ini", "home = .reviews", "automatic pickup",
                            "wait-any-request", "wait-answer", "pw skill"))
    recovery = read_declared(docs_root, "wiki/how-to/recover-an-independent-review.md")
    assert "enter `resume`" in recovery
    assert "automatic pickup" in recovery
    assert "force requestor ownership pickup" not in recovery
    reference = read_declared(docs_root, _REFERENCE)
    assert_contains(reference, ("migration-check", "resume-inspect", "claim",
                               "wait-any-request", "cancelled", "already-claimed"))


# eof
