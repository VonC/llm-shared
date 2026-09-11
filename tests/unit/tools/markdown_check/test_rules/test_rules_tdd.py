"""Tests for supported Markdown and repository-local rule behavior."""

# ruff: noqa: PLR2004

from collections.abc import Callable

import pytest

from tools.markdown_check.classifier import DocumentClassification, DocumentKind
from tools.markdown_check.models import Finding, MarkdownSource
from tools.markdown_check.rules import (
    check_ls001,
    check_ls002,
    check_ls003,
    check_md001,
    check_md009,
    check_md012,
    check_md024,
    check_md025,
    check_md032,
    check_md033,
    check_md034,
    check_md038,
    check_md040,
    check_md050,
    evaluate_rules,
)
from tools.markdown_check.source import parse_markdown

Rule = Callable[[MarkdownSource], tuple[Finding, ...]]


def test_heading_list_html_and_code_rules_return_located_findings() -> None:
    """Every catalog evaluator reports its own stable identifier and source line."""
    source = parse_markdown(
        "docs/broken.md",
        """# Title
### Jump
# Other title
## Repeated
## Repeated
Prose.
- item
Following prose.
<div>raw</div>
` padded `
__strong__
""",
    )
    classification = DocumentClassification(DocumentKind.STRUCTURED, "default")

    findings = evaluate_rules(source, classification, allowed_html=frozenset({"img"}))

    rules = {finding.rule for finding in findings}
    assert rules == {
        "MD001",
        "MD024",
        "MD025",
        "MD032",
        "MD033",
        "MD038",
        "MD050",
        "LS003",
    }
    assert any(finding.rule == "MD001" and finding.line == 2 for finding in findings)
    assert any(finding.rule == "MD032" and finding.line == 7 for finding in findings)
    assert any(finding.rule == "MD033" and finding.line == 9 for finding in findings)


def test_structured_outline_rules_and_adapter_exemptions_are_separate() -> None:
    """Only LS001 and LS002 honor adapter classification."""
    source = parse_markdown("docs/outline.md", "## Only section\n")
    structured = DocumentClassification(DocumentKind.STRUCTURED, "default")
    adapter = DocumentClassification(DocumentKind.ADAPTER, "frontmatter")

    assert [finding.rule for finding in check_ls001(source, structured)] == ["LS001"]
    assert [finding.rule for finding in check_ls002(source, structured)] == ["LS002"]
    assert check_ls001(source, adapter) == ()
    assert check_ls002(source, adapter) == ()


def test_md001_allows_a_fragment_to_start_below_level_one() -> None:
    """MD001 compares consecutive headings and leaves first-heading policy to MD041."""
    source = parse_markdown("templates/fragment.md", "## Fragment\n### Child\n")

    assert check_md001(source) == ()


@pytest.mark.parametrize(
    ("markdown", "has_finding"),
    [
        ("` leading`", True),
        ("`trailing `", True),
        ("` padded `", True),
        ("`  genuine  `", False),
        ("`   `", False),
        ("`` `literal` ``", False),
        ("`plain`", False),
    ],
)
def test_md038_distinguishes_padding_from_genuine_code_space(
    markdown: str,
    *,
    has_finding: bool,
) -> None:
    """MD038 preserves parsed boundary spaces and required backtick padding."""
    source = parse_markdown("docs/code.md", markdown)

    assert bool(check_md038(source)) is has_finding


@pytest.mark.parametrize(
    ("markdown", "has_finding"),
    [
        ("__strong__", True),
        ("- tests/unit/__init__.py", True),
        ("**strong**", False),
        ("`__init__.py`", False),
        ("```text\n__strong__\n```", False),
        (r"\__strong__", False),
    ],
)
def test_md050_requires_asterisk_strong_style_only_in_prose(
    markdown: str,
    *,
    has_finding: bool,
) -> None:
    """MD050 ignores code and escapes while rejecting underscore strong style."""
    source = parse_markdown("docs/strong.md", markdown)

    assert bool(check_md050(source)) is has_finding


def test_individual_rules_cover_clean_and_configured_paths() -> None:
    """Clean sources and the configured img element produce no findings."""
    source = parse_markdown(
        "docs/clean.md",
        """# Title

## First section

Text with <img src="logo.png"> and `code`.

## Second section
""",
    )

    rules: tuple[Rule, ...] = (
        check_md001,
        check_md009,
        check_md012,
        check_md024,
        check_md025,
        check_md032,
        check_md038,
        check_md040,
        check_md050,
        check_ls003,
    )
    assert all(rule(source) == () for rule in rules)
    assert check_md033(source, allowed_elements=frozenset({"img"})) == ()


def test_md032_accepts_a_list_with_blank_boundaries() -> None:
    """A list separated from surrounding prose satisfies MD032."""
    source = parse_markdown("docs/list.md", "Lead.\n\n- item\n\nTail.\n")

    assert check_md032(source) == ()


@pytest.mark.parametrize(
    ("markdown", "expected"),
    [
        ("```text\ncode\n```\n", ()),
        ("~~~bash\ncode\n~~~\n", ()),
        ("```\ncode\n```\n", (1,)),
        ("```   \ncode\n```\n", (1,)),
        ("Lead.\n\n```\na\n```\n\n```py\nb\n```\n", (3,)),
        ("```text\n```\nprose\n```\n", (4,)),
    ],
)
def test_md040_requires_a_language_on_every_opening_fence(
    markdown: str,
    expected: tuple[int, ...],
) -> None:
    """MD040 reads the opener's info string and ignores closing markers."""
    source = parse_markdown("docs/fences.md", markdown)

    findings = check_md040(source)

    assert all(
        finding.rule == "MD040" and finding.reason == "fenced code block has no language"
        for finding in findings
    )
    assert tuple(finding.line for finding in findings) == expected


def test_indented_code_is_treated_as_code_by_every_rule() -> None:
    """An indented transcript yields no raw-HTML, bare-URL, or trailing-space finding."""
    source = parse_markdown(
        "docs/transcript.md",
        "Now recall the diagnostic:\n"
        "\n"
        "    75 | #include_next <stdlib.h>\n"
        "    see https://example.com for the report \n"
        "\n"
        "Prose resumes here.\n",
    )

    assert source.indented_code_lines == frozenset({3, 4})
    assert check_md033(source) == ()
    assert check_md034(source) == ()
    assert check_md009(source) == ()


def test_indented_continuation_of_a_list_is_not_code() -> None:
    """List continuation indentation stays prose, so its markup is still checked."""
    source = parse_markdown(
        "docs/list.md",
        "Lead.\n\n- item\n\n    <div>raw</div>\n\nTail.\n",
    )

    assert 5 not in source.indented_code_lines
    assert [finding.line for finding in check_md033(source)] == [5, 5]


@pytest.mark.parametrize(
    ("markdown", "expected"),
    [
        ("Clean line.\n", ()),
        ("Hard break.  \n", ()),
        ("One space. \n", ((1, 1),)),
        ("Three spaces.   \n", ((1, 3),)),
        ("Trailing tab.\t\n", ((1, 1),)),
        ("   \n", ((1, 3),)),
        ("```text\ncode. \n```\n", ()),
        ("```text \ncode\n``` \n", ((1, 1), (3, 1))),
    ],
)
def test_md009_allows_only_the_hard_break_pair_outside_fenced_content(
    markdown: str,
    expected: tuple[tuple[int, int], ...],
) -> None:
    """MD009 exempts fenced content lines but still checks both fence markers."""
    source = parse_markdown("docs/spaces.md", markdown)

    findings = check_md009(source)

    assert all(finding.rule == "MD009" for finding in findings)
    assert tuple((finding.line, finding.reason) for finding in findings) == tuple(
        (line, f"trailing spaces [Expected: 0 or 2; Actual: {count}]")
        for line, count in expected
    )


@pytest.mark.parametrize(
    ("markdown", "expected"),
    [
        ("See https://example.com now.\n", (5,)),
        ("- https://example.com\n", (3,)),
        ("Wrapped <https://example.com> here.\n", ()),
        ("A [link](https://example.com) here.\n", ()),
        ("An ![image](https://example.com) here.\n", ()),
        ("[label]: https://example.com\n", ()),
        ("Code `https://example.com` here.\n", ()),
        ("```text\nhttps://example.com\n```\n", ()),
        ('A <a href="https://example.com">x</a> tag.\n', ()),
        ("Prefixed view-source:https://example.com here.\n", (22,)),
        ("Wrapped <view-source:https://example.com> here.\n", ()),
        ("Glued xhttps://example.com here.\n", ()),
        ("Two https://a.example and https://b.example lines.\n", (5, 27)),
        ("Also ftp://files.example/pub here.\n", ()),
    ],
)
def test_md034_reports_only_unwrapped_absolute_urls(
    markdown: str,
    expected: tuple[int, ...],
) -> None:
    """MD034 skips autolinks, link targets, definitions, code, and HTML attributes."""
    source = parse_markdown("docs/urls.md", markdown)

    findings = check_md034(source)

    assert all(finding.rule == "MD034" for finding in findings)
    assert tuple(finding.reason for finding in findings) == tuple(
        f"bare URL at column {column}" for column in expected
    )


@pytest.mark.parametrize(
    ("markdown", "expected"),
    [
        ("Lead.\n\nTail.\n", ()),
        ("Lead.\n\n\nTail.\n", ((3, 2),)),
        ("Lead.\n\n\n\nTail.\n", ((4, 3),)),
        ("Lead.\n\n\t\nTail.\n", ((3, 2),)),
        ("A.\n\n\nB.\n\n\nC.\n", ((3, 2), (6, 2))),
        ("```text\n\n\ncode\n```\n", ()),
        ("Lead.\n\n```text\n\n\ncode\n```\n\nTail.\n", ()),
        ("---\ndescription: x\n\n\nname: y\n---\n\nBody.\n", ()),
        ("Lead.\n\n\n", ((3, 2),)),
    ],
)
def test_md012_reports_only_blank_runs_outside_fenced_code(
    markdown: str,
    expected: tuple[tuple[int, int], ...],
) -> None:
    """MD012 counts each blank run once, at its last line, and skips code and frontmatter."""
    source = parse_markdown("docs/blanks.md", markdown)

    findings = check_md012(source)

    assert all(finding.rule == "MD012" for finding in findings)
    assert tuple(finding.line for finding in findings) == tuple(
        line for line, _ in expected
    )
    assert tuple(
        f"multiple consecutive blank lines [Expected: 1; Actual: {count}]"
        for _, count in expected
    ) == tuple(finding.reason for finding in findings)


# eof
