"""Tests for the word-level rules of the commit-text width enforcer.

Cover ``tools.wrap_commit_backticks`` at the single-word level:
backtick-region detection, the wrap-exception whitelist, every
individual backtick-wrap rule (dash-prefixed tokens, ``=`` and ``_``
mixed-content tokens, dots, parens, CamelCase), the backtick-aware
tokenizer, the outer-punctuation splitter, the custom-predicate form of
the word backticker, and the paragraph-only path-separator predicate.

Fix: split for the repo line budget -- the word-rule classes moved here
from ``test_wrap_commit.py``, which keeps the backtick-pass and
wrap-list config tests; the targets now live in the split
``tools.wrap_commit_backticks`` module.
"""

from __future__ import annotations

from tools import wrap_commit_backticks

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001


class TestBacktickRegionDetection:
    """Validate detection of existing inline backtick spans."""

    def test_no_backticks_returns_empty_list(self) -> None:
        """Text without backticks reports no spans."""
        assert wrap_commit_backticks._find_backtick_regions("foo bar") == []

    def test_one_pair_returns_one_region_covering_both_ticks(self) -> None:
        """A single pair returns one span covering both backticks."""
        assert wrap_commit_backticks._find_backtick_regions("`foo`") == [(0, 5)]

    def test_multiple_pairs_each_reported(self) -> None:
        """Each pair of backticks is reported as its own span."""
        text = "use `foo` and `bar`"

        assert wrap_commit_backticks._find_backtick_regions(text) == [
            (4, 9),
            (14, 19),
        ]

    def test_unmatched_trailing_backtick_is_ignored(self) -> None:
        """An unmatched trailing backtick produces no span."""
        assert wrap_commit_backticks._find_backtick_regions("`foo") == []


class TestWordMatchesWrapException:
    r"""Validate the ``v\d+\.`` and ``[Oo]\(`` whitelist exemptions."""

    def test_version_literal_matches(self) -> None:
        """``v1.0`` matches the version-literal exemption."""
        assert wrap_commit_backticks._word_matches_wrap_exception("v1.0")

    def test_multi_part_version_literal_matches(self) -> None:
        """``v2.5.3`` matches the version-literal exemption."""
        assert wrap_commit_backticks._word_matches_wrap_exception("v2.5.3")

    def test_version_literal_with_trailing_punct_matches(self) -> None:
        """``v1.0,`` still matches -- the regex anchors at the start only."""
        assert wrap_commit_backticks._word_matches_wrap_exception("v1.0,")

    def test_uppercase_v_does_not_match(self) -> None:
        """The regex is lowercase-only: ``V1.0`` is not exempted."""
        assert not wrap_commit_backticks._word_matches_wrap_exception("V1.0")

    def test_v_without_digits_does_not_match(self) -> None:
        r"""A leading ``v`` without ``\d+\.`` is not exempted."""
        assert not wrap_commit_backticks._word_matches_wrap_exception("v.x")
        assert not wrap_commit_backticks._word_matches_wrap_exception("v")

    def test_v_with_digits_but_no_dot_does_not_match(self) -> None:
        """``v1`` lacks the trailing dot and is not exempted."""
        assert not wrap_commit_backticks._word_matches_wrap_exception("v1")

    def test_uppercase_big_o_matches(self) -> None:
        """``O(n)`` matches the big-O exemption."""
        assert wrap_commit_backticks._word_matches_wrap_exception("O(n)")

    def test_lowercase_o_open_paren_matches(self) -> None:
        """``o(log)`` matches the big-O exemption."""
        assert wrap_commit_backticks._word_matches_wrap_exception("o(log)")

    def test_o_without_open_paren_does_not_match(self) -> None:
        """A leading ``O``/``o`` without ``(`` is not exempted."""
        assert not wrap_commit_backticks._word_matches_wrap_exception("OK(foo)")
        assert not wrap_commit_backticks._word_matches_wrap_exception("octopus")

    def test_plain_word_does_not_match(self) -> None:
        """A word that does not start with either pattern is not exempted."""
        assert not wrap_commit_backticks._word_matches_wrap_exception("foo_bar")


class TestWordNeedsBackticks:
    """Validate each individual backtick-wrap rule."""

    def test_underscore_anywhere_qualifies(self) -> None:
        """A word containing ``_`` qualifies."""
        assert wrap_commit_backticks._word_needs_backticks("foo_bar")

    def test_dot_in_middle_qualifies(self) -> None:
        """A non-trailing dot qualifies."""
        assert wrap_commit_backticks._word_needs_backticks("foo.bar")

    def test_dot_at_end_only_does_not_qualify(self) -> None:
        """A trailing-only dot (sentence punctuation) does not qualify."""
        assert not wrap_commit_backticks._word_needs_backticks("machines.")

    def test_open_paren_in_middle_qualifies(self) -> None:
        """A non-leading open paren qualifies."""
        assert wrap_commit_backticks._word_needs_backticks("foo(bar)")

    def test_open_paren_at_start_only_does_not_qualify(self) -> None:
        """A leading-only open paren does not qualify."""
        assert not wrap_commit_backticks._word_needs_backticks("(foo")

    def test_single_uppercase_does_not_qualify(self) -> None:
        """``Xyz`` (one uppercase) does not qualify under the CamelCase rule."""
        assert not wrap_commit_backticks._word_needs_backticks("Xyz")

    def test_two_uppercase_qualifies(self) -> None:
        """``XyzUvw`` (two uppercase + lowercase) qualifies under CamelCase."""
        assert wrap_commit_backticks._word_needs_backticks("XyzUvw")

    def test_all_lowercase_does_not_qualify(self) -> None:
        """A plain lowercase word does not qualify."""
        assert not wrap_commit_backticks._word_needs_backticks("paragraph")

    def test_empty_word_does_not_qualify(self) -> None:
        """Empty input does not qualify."""
        assert not wrap_commit_backticks._word_needs_backticks("")

    def test_pure_acronym_does_not_qualify(self) -> None:
        """A pure acronym (no lowercase) is not CamelCase and stays bare."""
        assert not wrap_commit_backticks._word_needs_backticks("PBT")
        assert not wrap_commit_backticks._word_needs_backticks("URL")

    def test_acronym_with_trailing_close_paren_does_not_qualify(self) -> None:
        """``PBT)`` is an acronym followed by punctuation; no lowercase, stays bare."""
        assert not wrap_commit_backticks._word_needs_backticks("PBT)")

    def test_close_paren_alone_does_not_qualify(self) -> None:
        """A single uppercase + ``)`` does not qualify -- closing paren is irrelevant."""
        assert not wrap_commit_backticks._word_needs_backticks("X)")

    def test_open_paren_with_close_paren_still_qualifies(self) -> None:
        """``x(r)`` qualifies via the open-paren rule despite the trailing ``)``."""
        assert wrap_commit_backticks._word_needs_backticks("x(r)")

    def test_pypi_qualifies_under_camelcase(self) -> None:
        """``PyPI`` has 3 uppercase + 1 lowercase, so it is CamelCase."""
        assert wrap_commit_backticks._word_needs_backticks("PyPI")

    def test_version_literal_short_circuits_to_false(self) -> None:
        """``v1.0`` is exempt even though it has a non-trailing dot."""
        assert not wrap_commit_backticks._word_needs_backticks("v1.0")

    def test_big_o_notation_short_circuits_to_false(self) -> None:
        """``O(n)`` is exempt even though it has a non-leading ``(``."""
        assert not wrap_commit_backticks._word_needs_backticks("O(n)")

    def test_dash_prefixed_tokens_qualify(self) -> None:
        """Tokens that start with ``-`` and have non-dash content qualify."""
        assert wrap_commit_backticks._word_needs_backticks("-x")
        assert wrap_commit_backticks._word_needs_backticks("--foo")
        assert wrap_commit_backticks._word_needs_backticks("--no-backticks")
        assert wrap_commit_backticks._word_needs_backticks("---bar")

    def test_all_dash_tokens_do_not_qualify(self) -> None:
        """Bare separators like ``-``, ``--``, ``---`` are not wrapped."""
        assert not wrap_commit_backticks._word_needs_backticks("-")
        assert not wrap_commit_backticks._word_needs_backticks("--")
        assert not wrap_commit_backticks._word_needs_backticks("---")

    def test_dashed_token_helper_directly(self) -> None:
        """Direct check of the dashed-token helper."""
        assert wrap_commit_backticks._word_is_dashed_token("-x")
        assert wrap_commit_backticks._word_is_dashed_token("--foo")
        assert not wrap_commit_backticks._word_is_dashed_token("--")
        assert not wrap_commit_backticks._word_is_dashed_token("foo")
        assert not wrap_commit_backticks._word_is_dashed_token("foo-bar")

    def test_equals_anywhere_qualifies(self) -> None:
        """A token with ``=`` mixed with other chars qualifies."""
        assert wrap_commit_backticks._word_needs_backticks("KEY=value")
        assert wrap_commit_backticks._word_needs_backticks("foo=bar")
        assert wrap_commit_backticks._word_needs_backticks("=leading")
        assert wrap_commit_backticks._word_needs_backticks("trailing=")

    def test_bare_equals_does_not_qualify(self) -> None:
        """``=`` and ``==`` are only ``=`` chars, so the rule does not fire."""
        assert not wrap_commit_backticks._word_needs_backticks("=")
        assert not wrap_commit_backticks._word_needs_backticks("==")
        assert not wrap_commit_backticks._word_needs_backticks("===")

    def test_bare_underscore_does_not_qualify(self) -> None:
        """``_`` and ``__`` are only ``_`` chars, so the rule does not fire."""
        assert not wrap_commit_backticks._word_needs_backticks("_")
        assert not wrap_commit_backticks._word_needs_backticks("__")
        assert not wrap_commit_backticks._word_needs_backticks("___")

    def test_helper_word_has_other_chars_than(self) -> None:
        """Direct check of the mixed-char helper for both ``=`` and ``_``."""
        # The char must be present.
        assert not wrap_commit_backticks._word_has_other_chars_than("foo", "=")
        # The char must be mixed with at least one other character.
        assert not wrap_commit_backticks._word_has_other_chars_than("==", "=")
        assert not wrap_commit_backticks._word_has_other_chars_than("__", "_")
        # Mixed cases qualify.
        assert wrap_commit_backticks._word_has_other_chars_than("=x", "=")
        assert wrap_commit_backticks._word_has_other_chars_than("a_b", "_")

    def test_camelcase_helper_directly(self) -> None:
        """The CamelCase helper requires 2+ upper AND 1+ lower."""
        assert wrap_commit_backticks._word_is_camelcase("XyzUvw")
        assert not wrap_commit_backticks._word_is_camelcase("Xyz")
        assert not wrap_commit_backticks._word_is_camelcase("URL")


class TestTokenizeKeepingBackticks:
    """Validate the tokenizer that treats backtick spans as indivisible."""

    def test_plain_text_splits_on_whitespace(self) -> None:
        """Without backticks, the tokenizer is a regular whitespace split."""
        assert wrap_commit_backticks.tokenize_keeping_backticks("a b c") == [
            "a",
            "b",
            "c",
        ]

    def test_collapses_consecutive_whitespace(self) -> None:
        """Multiple-space gaps still collapse to a single token boundary."""
        assert wrap_commit_backticks.tokenize_keeping_backticks("a  b") == ["a", "b"]

    def test_leading_and_trailing_whitespace_ignored(self) -> None:
        """Outer whitespace does not create empty tokens."""
        assert wrap_commit_backticks.tokenize_keeping_backticks("  abc  ") == ["abc"]

    def test_backtick_span_with_internal_space_kept_as_one_token(self) -> None:
        r"""A ``\`xx yyy zzz\``` span is returned as a single token."""
        assert wrap_commit_backticks.tokenize_keeping_backticks(
            "a `xx yyy zzz` b",
        ) == [
            "a",
            "`xx yyy zzz`",
            "b",
        ]

    def test_multiple_backtick_spans_each_kept_intact(self) -> None:
        """Each span is its own indivisible token."""
        assert wrap_commit_backticks.tokenize_keeping_backticks(
            "see `a b` and `c d e` here",
        ) == ["see", "`a b`", "and", "`c d e`", "here"]

    def test_backtick_span_without_internal_space_is_one_token(self) -> None:
        r"""A no-space ``\`foo\``` is naturally a single token."""
        assert wrap_commit_backticks.tokenize_keeping_backticks("a `foo` b") == [
            "a",
            "`foo`",
            "b",
        ]

    def test_empty_input_returns_empty_list(self) -> None:
        """An empty string yields no tokens."""
        assert wrap_commit_backticks.tokenize_keeping_backticks("") == []


class TestSplitOuterPunctuation:
    """Validate the (leading, core, trailing) outer-punctuation splitter."""

    def test_no_outer_punctuation_returns_empty_outer(self) -> None:
        """A word without any outer punctuation returns empty leading and trailing."""
        assert wrap_commit_backticks._split_outer_punctuation("foo_bar") == (
            "",
            "foo_bar",
            "",
        )

    def test_trailing_colon_is_split_off(self) -> None:
        """A single trailing ``:`` is extracted as the suffix."""
        assert wrap_commit_backticks._split_outer_punctuation("foo_bar:") == (
            "",
            "foo_bar",
            ":",
        )

    def test_multiple_trailing_sentence_chars_extracted(self) -> None:
        """A run of trailing sentence-punctuation is fully extracted."""
        assert wrap_commit_backticks._split_outer_punctuation("foo.,") == (
            "",
            "foo",
            ".,",
        )

    def test_unbalanced_trailing_close_paren_extracted(self) -> None:
        """A lone trailing ``)`` (no matching ``(``) is extracted."""
        assert wrap_commit_backticks._split_outer_punctuation("foo_bar)") == (
            "",
            "foo_bar",
            ")",
        )

    def test_unbalanced_trailing_close_paren_with_sentence_run(self) -> None:
        """A trailing ``).,`` is fully extracted (unbalanced ``)`` plus sentence run)."""
        assert wrap_commit_backticks._split_outer_punctuation("foo).,") == (
            "",
            "foo",
            ").,",
        )

    def test_balanced_close_paren_stays_inside_core(self) -> None:
        """``foo(bar)`` is balanced; ``)`` stays in the core."""
        assert wrap_commit_backticks._split_outer_punctuation("foo(bar)") == (
            "",
            "foo(bar)",
            "",
        )

    def test_balanced_close_paren_with_trailing_colon(self) -> None:
        """``feat(tools):`` keeps the balanced parens and extracts the ``:``."""
        assert wrap_commit_backticks._split_outer_punctuation("feat(tools):") == (
            "",
            "feat(tools)",
            ":",
        )

    def test_unbalanced_leading_open_paren_extracted(self) -> None:
        """A lone leading ``(`` (no matching ``)``) is extracted."""
        assert wrap_commit_backticks._split_outer_punctuation(
            "(FlagValidationStatus,",
        ) == (
            "(",
            "FlagValidationStatus",
            ",",
        )

    def test_balanced_leading_open_paren_stays_inside_core(self) -> None:
        """``(foo_bar)`` is balanced; both parens stay in the core."""
        assert wrap_commit_backticks._split_outer_punctuation("(foo_bar)") == (
            "",
            "(foo_bar)",
            "",
        )

    def test_multiple_unbalanced_leading_parens(self) -> None:
        """Multiple unbalanced leading ``(`` chars are all extracted."""
        assert wrap_commit_backticks._split_outer_punctuation("((FlagX,") == (
            "((",
            "FlagX",
            ",",
        )

    def test_multiple_unbalanced_trailing_close_parens(self) -> None:
        """Multiple unbalanced trailing ``)`` chars are all extracted."""
        assert wrap_commit_backticks._split_outer_punctuation("read_flag))") == (
            "",
            "read_flag",
            "))",
        )

    def test_only_outer_punct_yields_empty_core(self) -> None:
        """All-punctuation input produces an empty core."""
        assert wrap_commit_backticks._split_outer_punctuation(".,;:") == (
            "",
            "",
            ".,;:",
        )

    def test_empty_input_returns_three_empty_strings(self) -> None:
        """An empty word returns three empty strings."""
        assert wrap_commit_backticks._split_outer_punctuation("") == ("", "", "")


class TestWordHasPathSeparator:
    """Validate the path-separator word predicate."""

    def test_forward_slash_word_qualifies(self) -> None:
        """A word with a forward slash and other chars qualifies."""
        assert wrap_commit_backticks._word_has_path_separator("src/pdfss")

    def test_backslash_word_qualifies(self) -> None:
        """A word with a backslash and other chars qualifies."""
        assert wrap_commit_backticks._word_has_path_separator(r"C:\Users\vonc")

    def test_and_or_qualifies(self) -> None:
        """A prose token like ``and/or`` qualifies."""
        assert wrap_commit_backticks._word_has_path_separator("and/or")

    def test_bare_forward_slash_does_not_qualify(self) -> None:
        """A lone ``/`` separator stays bare."""
        assert not wrap_commit_backticks._word_has_path_separator("/")

    def test_bare_backslash_does_not_qualify(self) -> None:
        r"""A lone ``\`` separator stays bare."""
        assert not wrap_commit_backticks._word_has_path_separator("\\")

    def test_repeated_separators_do_not_qualify(self) -> None:
        """Runs made only of separators stay bare."""
        assert not wrap_commit_backticks._word_has_path_separator("//")
        assert not wrap_commit_backticks._word_has_path_separator("\\\\")

    def test_plain_word_does_not_qualify(self) -> None:
        """A word without a separator does not qualify."""
        assert not wrap_commit_backticks._word_has_path_separator("paragraph")


class TestAddBackticksToWordsPredicate:
    """Validate the custom-predicate form of the word backticker."""

    def test_default_predicate_is_code_like(self) -> None:
        """With no predicate, the code-like rules apply."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "use foo_bar",
        ) == "use `foo_bar`"

    def test_path_predicate_wraps_slash_words(self) -> None:
        """A custom predicate can target path-separator words."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "see src/pdfss here",
            wrap_commit_backticks._word_has_path_separator,
        ) == "see `src/pdfss` here"

    def test_path_predicate_leaves_plain_words(self) -> None:
        """A custom predicate leaves non-matching words alone."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "plain words here",
            wrap_commit_backticks._word_has_path_separator,
        ) == "plain words here"


class TestWordNeedsBackticksInParagraph:
    """Validate the paragraph predicate (code-like plus path-separator)."""

    def test_code_like_word_qualifies(self) -> None:
        """A code-like word qualifies via the regular rules."""
        assert wrap_commit_backticks.word_needs_backticks_in_paragraph("foo_bar")

    def test_path_separator_word_qualifies(self) -> None:
        """A slash word qualifies via the path-separator rule."""
        assert wrap_commit_backticks.word_needs_backticks_in_paragraph("src/pdfss")

    def test_plain_word_does_not_qualify(self) -> None:
        """A plain word qualifies under neither rule."""
        assert not wrap_commit_backticks.word_needs_backticks_in_paragraph(
            "paragraph",
        )


# eof
