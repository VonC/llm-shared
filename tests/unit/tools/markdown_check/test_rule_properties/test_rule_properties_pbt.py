"""Heading and title properties with a bounded MD001 example budget.

The heading property keeps its complete input domain and assertion while
limiting example generation to leave margin below the duration gate.

Fix: the LS003 word generator excludes the document's own "Root" title.
Hypothesis eventually drew "ROOT", which collides with the fixed opening
heading and yields two findings, so the property failed on a document that was
never the duplicate case it describes.
"""

# ruff: noqa: PLR2004

from itertools import pairwise

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.markdown_check.rules import check_ls003, check_md001
from tools.markdown_check.source import parse_markdown

_LEVELS = st.lists(st.integers(min_value=1, max_value=6), min_size=1, max_size=30)
_WORDS = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    min_size=1,
    max_size=20,
    # The LS003 document below opens with a fixed "# Root" title, so a word
    # that normalizes to it makes three colliding titles and two findings
    # rather than the one duplicate the property is about.
).filter(lambda word: word.casefold() != "root")


@given(_LEVELS)
@settings(max_examples=40)
def test_md001_matches_every_invalid_heading_increment(levels: list[int]) -> None:
    """A finding exists exactly when an ordered heading jumps by two or more."""
    markdown = "\n".join(
        f"{'#' * level} Heading {index}" for index, level in enumerate(levels)
    )
    expected = sum(current > previous + 1 for previous, current in pairwise(levels))

    assert len(check_md001(parse_markdown("docs/headings.md", markdown))) == expected


@given(_WORDS)
@settings(max_examples=100)
def test_ls003_collides_case_and_inline_formatting_variants(word: str) -> None:
    """Case, emphasis markers, and punctuation do not hide a repeated title."""
    markdown = f"# Root\n\n## {word}\n\n### *{word.upper()}*!\n"

    findings = check_ls003(parse_markdown("docs/titles.md", markdown))

    assert len(findings) == 1
    assert findings[0].line == 5


# eof
