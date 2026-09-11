"""Tests for one-pass Markdown parsing and pure document classification."""

# ruff: noqa: PLR2004

from tools.markdown_check.classifier import DocumentKind, classify_document
from tools.markdown_check.source import fenced_line_numbers, parse_markdown


def test_source_model_records_structural_tokens_once_outside_fences() -> None:
    """The parser records source locations and ignores structural fence content."""
    markdown = """---
description: "Example adapter"
---
# Visible Résumé title

[Guide](../rules/guide.md#usage)

- first item
- second item

`inline`
`multi
line`
<img src="logo.png">
<div>body</div>

```markdown
## Hidden heading
- hidden item
<span>hidden</span>
```

~~~text
### Also hidden
~~~

## Visible section
"""

    source = parse_markdown("docs/example.md", markdown)

    assert source.frontmatter is not None
    assert source.frontmatter.description == "Example adapter"
    assert [(heading.line, heading.level, heading.title) for heading in source.headings] == [
        (4, 1, "Visible Résumé title"),
        (27, 2, "Visible section"),
    ]
    assert [(link.line, link.target) for link in source.links] == [
        (6, "../rules/guide.md#usage"),
    ]
    assert [(block.start_line, block.end_line) for block in source.list_blocks] == [
        (8, 9),
    ]
    assert [element.name for element in source.raw_html] == ["img", "div", "div"]
    assert [span.value for span in source.inline_code] == ["inline", "multi line"]
    assert source.inline_code[1].line == 12
    assert source.fenced_lines == frozenset({17, 18, 19, 20, 21, 23, 24, 25})


def test_fence_scanner_preserves_existing_review_heading_boundaries() -> None:
    """Backtick and tilde fences close only with a long-enough matching marker."""
    lines = ["lead", "````python", "```", "## literal", "````", "## visible"]

    assert fenced_line_numbers(lines) == frozenset({2, 3, 4, 5})


def test_source_model_handles_unclosed_frontmatter_and_inline_delimiters() -> None:
    """Malformed frontmatter stays visible and stale backtick runs are discarded."""
    source = parse_markdown(
        "docs/edge.md",
        "---\ndescription: unclosed\n# Visible\n\n`a``b``c`d``\n",
    )

    assert source.frontmatter is None
    assert [heading.title for heading in source.headings] == ["Visible"]
    assert [span.raw_content for span in source.inline_code] == ["a``b``c"]


def test_source_model_hides_list_indented_fenced_code() -> None:
    """Backticks inside a nested fenced block never become inline-code spans."""
    source = parse_markdown(
        "docs/nested.md",
        "- item\n\n    ```bash\n    echo ` padded `\n    ```\n",
    )

    assert source.inline_code == ()
    assert source.fenced_lines == frozenset({3, 4, 5})


def test_source_model_extends_lists_across_blank_indented_content() -> None:
    """A continued list may cross blanks and may end with trailing blanks."""
    source = parse_markdown(
        "docs/lists.md",
        "Lead.\n\n- first\n\n  continued\n\n- trailing\n\n",
    )

    assert [(block.start_line, block.end_line) for block in source.list_blocks] == [
        (3, 7),
    ]


def test_classifier_recognizes_each_bounded_adapter_shape() -> None:
    """Frontmatter, canonical pointers, and template fragments are adapters."""
    frontmatter = parse_markdown(
        ".claude/skills/example/SKILL.md",
        "---\ndescription: adapter identity\n---\nBody.\n",
    )
    pointer = parse_markdown(
        ".agents/llm-shared/instructions/example.md",
        "Read [the canonical rule](../../../instructions/example.md).\n",
    )
    cache_pointer = parse_markdown(
        ".agents/llm-shared/instructions/example.md",
        "Read [the canonical rule]"
        "(../../../../../../../git/llm-shared/instructions/example.md).\n",
    )
    fragment = parse_markdown("templates/example.md", "## Substituted section\n")

    assert classify_document(frontmatter).kind is DocumentKind.ADAPTER
    assert classify_document(pointer).kind is DocumentKind.ADAPTER
    assert classify_document(cache_pointer).kind is DocumentKind.ADAPTER
    assert classify_document(fragment).kind is DocumentKind.ADAPTER


def test_classifier_rejects_unlinked_or_escaping_pointer_candidates() -> None:
    """A short file is structured unless its Markdown link stays in the repository."""
    unlinked = parse_markdown(
        ".github/prompts/example.md",
        "Canonical instructions live elsewhere.\n",
    )
    escaping = parse_markdown(
        ".github/prompts/example.md",
        "Read [outside](../../../outside.md).\n",
    )
    too_long = parse_markdown(
        ".github/prompts/example.md",
        "[Rule](../../instructions/example.md)\n1\n2\n3\n4\n5\n",
    )

    assert classify_document(unlinked).kind is DocumentKind.STRUCTURED
    assert classify_document(escaping).kind is DocumentKind.STRUCTURED
    assert classify_document(too_long).kind is DocumentKind.STRUCTURED


def test_classifier_rejects_external_empty_and_non_markdown_links() -> None:
    """Pointer classification requires a relative path to a Markdown file."""
    source = parse_markdown(
        ".github/prompts/example.md",
        "[external](https://example.test/rule.md)\n"
        "[empty](#fragment)\n"
        "[text](../../instructions/example.txt)\n",
    )

    assert classify_document(source).kind is DocumentKind.STRUCTURED


# eof
