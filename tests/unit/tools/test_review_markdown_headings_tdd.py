"""Tests for nesting and qualifying caller-authored review headings."""

from tools.review_markdown_headings import qualify_round_headings, wrap_bare_urls


def test_headings_shift_as_one_outline_and_keep_code_fences_literal() -> None:
    """The shallowest heading moves below its parent without flattening children."""
    markdown = """Lead.

## Evidence

### Detail ###

```markdown
## Literal sample
~~~
```

###### Deep detail
"""

    rendered = qualify_round_headings(
        markdown,
        minimum_level=4,
        qualifier="step 2 relocation-force-rpath",
        round_number=3,
    )

    assert "#### Evidence for step 2 relocation-force-rpath (round 3)" in rendered
    assert "##### Detail for step 2 relocation-force-rpath (round 3) ###" in rendered
    assert "###### Deep detail for step 2 relocation-force-rpath (round 3)" in rendered
    assert "```markdown\n## Literal sample\n~~~\n```" in rendered
    assert rendered.endswith("\n")


def test_existing_round_context_is_replaced_and_rendering_is_idempotent() -> None:
    """A caller's older suffix is replaced by the canonical step-round suffix."""
    markdown = "## Test evidence for step 2 relocation-force-rpath round 3"

    rendered = qualify_round_headings(
        markdown,
        minimum_level=3,
        qualifier="step 2 relocation-force-rpath",
        round_number=3,
    )

    assert rendered == "### Test evidence for step 2 relocation-force-rpath (round 3)"
    assert (
        qualify_round_headings(
            rendered,
            minimum_level=3,
            qualifier="step 2 relocation-force-rpath",
            round_number=3,
        )
        == rendered
    )


def test_legacy_reviewer_exchange_suffix_is_replaced_once() -> None:
    """The old round-before-exchange suffix does not survive migration."""
    markdown = (
        "### Findings for step 2 relocation-force-rpath round 3 (exchange 1)"
    )

    rendered = qualify_round_headings(
        markdown,
        minimum_level=3,
        qualifier="step 2 relocation-force-rpath (exchange 1)",
        round_number=3,
    )

    assert rendered == (
        "### Findings for step 2 relocation-force-rpath (exchange 1) (round 3)"
    )


def test_specification_qualifier_is_idempotent() -> None:
    """A specification heading keeps one identity suffix across re-rendering."""
    rendered = "### Evidence for feature-request review-status-command (round 2)"

    assert (
        qualify_round_headings(
            rendered,
            minimum_level=3,
            qualifier="feature-request review-status-command",
            round_number=2,
        )
        == rendered
    )


def test_plain_markdown_and_tilde_fences_are_unchanged() -> None:
    """Content without authored headings returns byte-for-byte equivalent text."""
    markdown = "Lead.\n\n~~~text\n## Literal sample\n```\n~~~"

    assert (
        qualify_round_headings(
            markdown,
            minimum_level=4,
            qualifier="step 1 topic",
            round_number=1,
        )
        == markdown
    )


def test_bare_urls_are_wrapped_and_addressed_ones_are_left_alone() -> None:
    """MD034 is fixed at the input boundary, without touching an existing link."""
    markdown = (
        "These constraints follow the guidance:\n"
        "https://docs.python.org/3.12/library/multiprocessing.html#x\n"
        "and see [terminate](https://docs.python.org/3.12/y) or <https://z.test/a>.\n"
    )

    rendered = wrap_bare_urls(markdown)

    assert "<https://docs.python.org/3.12/library/multiprocessing.html#x>" in rendered
    assert "[terminate](https://docs.python.org/3.12/y)" in rendered
    assert "<https://z.test/a>" in rendered
    assert "<<" not in rendered


def test_wrapping_leaves_sentence_punctuation_and_fenced_urls_outside() -> None:
    """A trailing full stop is prose, and a fenced or spanned URL is a sample."""
    markdown = (
        "Read https://example.test/a.\n"
        "Call `https://example.test/b` directly.\n"
        "```text\n"
        "https://example.test/c\n"
        "```\n"
        "[ref]: https://example.test/d\n"
        "Balanced https://example.test/Foo_(bar) stays whole.\n"
    )

    rendered = wrap_bare_urls(markdown)

    assert "<https://example.test/a>.\n" in rendered
    assert "`https://example.test/b`" in rendered
    assert "\nhttps://example.test/c\n" in rendered
    assert "[ref]: https://example.test/d" in rendered
    assert "<https://example.test/Foo_(bar)>" in rendered


def test_wrapping_is_idempotent_and_runs_inside_heading_qualification() -> None:
    """A second pass changes nothing, and the round renderer applies the same fix."""
    markdown = "## Evidence\n\nSee https://example.test/a for the contract.\n"

    rendered = qualify_round_headings(
        markdown,
        minimum_level=3,
        qualifier="step 1 topic",
        round_number=1,
    )

    assert "See <https://example.test/a> for the contract." in rendered
    assert "### Evidence for step 1 topic (round 1)" in rendered
    assert wrap_bare_urls(rendered) == rendered


def test_an_unclosed_code_span_does_not_swallow_the_rest_of_the_line() -> None:
    """A stray backtick run with no partner leaves later URLs still wrappable."""
    markdown = "``unclosed ` run https://example.test/a end\n"

    rendered = wrap_bare_urls(markdown)

    assert "<https://example.test/a>" in rendered


def test_unmatched_run_does_not_hide_a_later_code_spanned_url() -> None:
    """A later valid span stays protected after an unmatched earlier run."""
    markdown = "``unclosed `https://example.test/x` end\n"

    assert wrap_bare_urls(markdown) == markdown
