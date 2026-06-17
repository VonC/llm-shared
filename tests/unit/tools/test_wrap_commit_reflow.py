"""Tests for the reflow stage of the commit-text width enforcer.

Cover ``tools.wrap_commit_reflow``: list-item detection, greedy word
wrapping, empty-line preservation, bullet-continuation merging, the
backtick pass flowing through ``reflow_lines`` (including the adjacent
span merge and the indivisible-span width wrap), the wrap-list literal
pass, the paragraph-only path-separator rule that backticks words
holding a slash or backslash, the final subject-wrap strip that bares a
backticked ``type(scope):`` line opener, the conventional-commit subject
recognizer, and the per-block reflow that keeps a leading commit
subject verbatim.

Fix: split for the repo line budget -- the reflow classes moved here
from ``test_wrap_commit.py``, which keeps the backtick-pass and
wrap-list config tests; the targets now live in the split
``tools.wrap_commit_reflow`` module.
"""

from __future__ import annotations

from tools import wrap_commit_reflow

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001


class TestListItemDetection:
    r"""Validate the ``^(\s*)- `` list-item recognizer."""

    def test_detects_plain_bullet_with_empty_indent(self) -> None:
        """A bare ``- foo`` line is a list item with no indent."""
        match = wrap_commit_reflow._is_list_item("- foo")

        assert match is not None
        assert match.group(1) == ""

    def test_detects_indented_bullet(self) -> None:
        """Leading whitespace before the dash is captured as the indent."""
        match = wrap_commit_reflow._is_list_item("    - foo")

        assert match is not None
        assert match.group(1) == "    "

    def test_rejects_plain_paragraph_line(self) -> None:
        """A line without a dash marker is not a list item."""
        assert wrap_commit_reflow._is_list_item("foo bar") is None

    def test_rejects_dash_without_trailing_space(self) -> None:
        """``-foo`` does not start a list item; the dash must be followed by a space."""
        assert wrap_commit_reflow._is_list_item("-foo") is None


class TestWrapWords:
    """Validate the greedy word-wrapping helper."""

    def test_empty_words_with_no_prefix_returns_empty_list(self) -> None:
        """No words and no first prefix produce no output lines."""
        assert wrap_commit_reflow._wrap_words([], 80, "", "") == []

    def test_empty_words_with_first_prefix_keeps_prefix_alone(self) -> None:
        """A bullet prefix without content is still emitted, rstrip'd."""
        assert wrap_commit_reflow._wrap_words([], 80, "- ", "  ") == ["-"]

    def test_single_word_fits_one_line(self) -> None:
        """One word produces one line."""
        assert wrap_commit_reflow._wrap_words(["foo"], 80, "", "") == ["foo"]

    def test_multiple_words_pack_under_width(self) -> None:
        """Words that fit are joined on one line."""
        assert wrap_commit_reflow._wrap_words(["foo", "bar", "baz"], 80, "", "") == [
            "foo bar baz",
        ]

    def test_words_wrap_when_line_would_exceed_width(self) -> None:
        """A word that would push past width starts a new line."""
        result = wrap_commit_reflow._wrap_words(["foo", "bar", "baz"], 7, "", "")

        assert result == ["foo bar", "baz"]

    def test_continuation_prefix_applied_after_wrap(self) -> None:
        """Lines after the first start with the continuation prefix."""
        result = wrap_commit_reflow._wrap_words(
            ["alpha", "beta", "gamma"],
            12,
            "- ",
            "  ",
        )

        assert result == ["- alpha beta", "  gamma"]

    def test_overlong_single_word_still_emitted(self) -> None:
        """A word longer than width is kept whole on its own line."""
        long_word = "x" * 50

        assert wrap_commit_reflow._wrap_words([long_word], 10, "", "") == [long_word]


class TestReflowLines:
    """Validate the line-by-line reflow that drives each block."""

    def test_empty_input_returns_empty_output(self) -> None:
        """Reflowing an empty list of lines yields an empty list."""
        assert wrap_commit_reflow.reflow_lines([], 80) == []

    def test_preserves_consecutive_empty_lines(self) -> None:
        """Blank lines are passed through one-for-one."""
        assert wrap_commit_reflow.reflow_lines(["", ""], 80) == ["", ""]

    def test_merges_consecutive_paragraph_lines(self) -> None:
        """Two non-empty non-bullet lines collapse into one paragraph."""
        assert wrap_commit_reflow.reflow_lines(["foo bar", "baz qux"], 80) == [
            "foo bar baz qux",
        ]

    def test_wraps_long_paragraph_at_column_zero(self) -> None:
        """A paragraph that exceeds width wraps without any indent prefix."""
        assert wrap_commit_reflow.reflow_lines(["foo bar baz qux"], 7) == [
            "foo bar",
            "baz qux",
        ]

    def test_short_bullet_passes_through_unchanged(self) -> None:
        """A list item shorter than width is emitted verbatim."""
        assert wrap_commit_reflow.reflow_lines(["- foo bar"], 80) == ["- foo bar"]

    def test_long_bullet_wraps_with_two_space_continuation(self) -> None:
        """A long bullet at column 0 wraps with a two-space continuation indent."""
        assert wrap_commit_reflow.reflow_lines(["- alpha beta gamma"], 12) == [
            "- alpha beta",
            "  gamma",
        ]

    def test_indented_bullet_continuation_matches_dash_column(self) -> None:
        """A bullet indented by N spaces continues at N+2 spaces."""
        assert wrap_commit_reflow.reflow_lines(["  - alpha beta gamma"], 14) == [
            "  - alpha beta",
            "    gamma",
        ]

    def test_consecutive_bullets_stay_separated(self) -> None:
        """Each bullet line stays its own list item."""
        assert wrap_commit_reflow.reflow_lines(["- foo", "- bar"], 80) == [
            "- foo",
            "- bar",
        ]

    def test_empty_line_ends_a_list_item(self) -> None:
        """A blank line closes the current list item."""
        assert wrap_commit_reflow.reflow_lines(["- foo", "", "- bar"], 80) == [
            "- foo",
            "",
            "- bar",
        ]

    def test_bullet_continuation_line_is_merged_into_item(self) -> None:
        """Indented non-bullet lines after a bullet are merged into it."""
        assert wrap_commit_reflow.reflow_lines(
            ["- alpha", "  beta gamma"],
            80,
        ) == ["- alpha beta gamma"]

    def test_paragraph_then_bullet_keeps_both_blocks(self) -> None:
        """A bullet line ends the running paragraph block."""
        assert wrap_commit_reflow.reflow_lines(
            ["a paragraph", "- a bullet"],
            80,
        ) == ["a paragraph", "- a bullet"]


class TestReflowLinesBackticks:
    """Validate the backtick pass through ``reflow_lines``."""

    def test_paragraph_gets_code_like_words_backticked_by_default(self) -> None:
        """The default reflow wraps code-like tokens before the width wrap."""
        assert wrap_commit_reflow.reflow_lines(
            ["use foo_bar here"],
            80,
        ) == ["use `foo_bar` here"]

    def test_add_backticks_false_disables_the_pass(self) -> None:
        """``add_backticks=False`` skips the wrap step."""
        assert wrap_commit_reflow.reflow_lines(
            ["use foo_bar here"],
            80,
            add_backticks=False,
        ) == ["use foo_bar here"]

    def test_bullet_content_also_gets_backticked(self) -> None:
        """List-item content is passed through the backtick wrap too."""
        assert wrap_commit_reflow.reflow_lines(
            ["- run foo_bar today"],
            80,
        ) == ["- run `foo_bar` today"]

    def test_backtick_span_with_internal_space_is_not_split(self) -> None:
        r"""A ``\`xx yyy zzz\``` span survives the width wrap as one piece."""
        # Width 12 forces a wrap; the 12-char ``\`xx yyy zzz\``` span
        # must land on its own line, never split mid-span.
        result = wrap_commit_reflow.reflow_lines(
            ["alpha `xx yyy zzz` beta"],
            12,
            add_backticks=False,
        )

        assert result == ["alpha", "`xx yyy zzz`", "beta"]

    def test_backtick_span_in_bullet_is_not_split(self) -> None:
        r"""Inside a list item, a backtick span also stays intact."""
        # Width 12 forces a wrap; the span ``\`xx yyy zzz\``` must stay
        # whole on its own continuation line, never torn at an inner space.
        result = wrap_commit_reflow.reflow_lines(
            ["- a `xx yyy zzz` b"],
            12,
            add_backticks=False,
        )

        assert result == ["- a", "  `xx yyy zzz`", "  b"]

    def test_adjacent_spans_merge_in_paragraph(self) -> None:
        """Code spans the backtick pass wraps side by side fold into one."""
        # ``--testmon`` and ``--no-cov`` each get backticked, then the
        # merge folds the pair into a single span.
        assert wrap_commit_reflow.reflow_lines(
            ["run --testmon --no-cov here"],
            80,
        ) == ["run `--testmon --no-cov` here"]

    def test_adjacent_spans_merge_in_bullet(self) -> None:
        """The merge runs on list-item content too."""
        assert wrap_commit_reflow.reflow_lines(
            ["- pass --testmon --no-cov today"],
            80,
        ) == ["- pass `--testmon --no-cov` today"]

    def test_spans_split_across_input_lines_merge(self) -> None:
        """Spans the source split across two lines merge after the collapse."""
        # The two paragraph lines collapse into one first, so the spans
        # land side by side and fold into a single span.
        assert wrap_commit_reflow.reflow_lines(
            ["existing `--a`", "`--b` tail"],
            80,
        ) == ["existing `--a --b` tail"]

    def test_no_backticks_flag_skips_the_merge(self) -> None:
        """``add_backticks=False`` leaves existing adjacent spans apart."""
        assert wrap_commit_reflow.reflow_lines(
            ["use `--a` `--b` now"],
            80,
            add_backticks=False,
        ) == ["use `--a` `--b` now"]


class TestCommitSubjectPattern:
    r"""Validate the ``^\S+\(.*?\):\s`` conventional-subject recognizer."""

    def test_matches_typed_and_scoped_subject(self) -> None:
        """``feat(tools): add ...`` matches the pattern."""
        assert wrap_commit_reflow.COMMIT_SUBJECT_PATTERN.match(
            "feat(tools): add cert-aware uv launcher",
        ) is not None

    def test_does_not_match_subject_without_scope(self) -> None:
        """A subject without parens (``feat: x``) does not match."""
        assert wrap_commit_reflow.COMMIT_SUBJECT_PATTERN.match("feat: xxx") is None

    def test_does_not_match_plain_paragraph(self) -> None:
        """A regular sentence does not match the subject pattern."""
        assert wrap_commit_reflow.COMMIT_SUBJECT_PATTERN.match("regular line") is None


class TestReflowBlockSubjectSkip:
    """Validate ``_reflow_block`` keeps a leading commit subject verbatim."""

    def test_subject_line_is_emitted_verbatim(self) -> None:
        """A first-line commit subject is returned untouched."""
        result = wrap_commit_reflow._reflow_block(
            ["feat(tools): add cert-aware uv launcher"],
            80,
            add_backticks=True,
        )

        assert result == ["feat(tools): add cert-aware uv launcher"]

    def test_subject_line_skips_backtick_pass(self) -> None:
        """No backticks are added to the subject line."""
        result = wrap_commit_reflow._reflow_block(
            ["feat(tools): add foo_bar today"],
            80,
            add_backticks=True,
        )

        assert result == ["feat(tools): add foo_bar today"]

    def test_subject_line_skips_width_wrap(self) -> None:
        """An overlong subject line is preserved even past the width."""
        long_subject = "feat(tools): " + ("x" * 100)

        result = wrap_commit_reflow._reflow_block(
            [long_subject],
            80,
            add_backticks=True,
        )

        assert result == [long_subject]

    def test_remaining_lines_still_reflowed_after_subject(self) -> None:
        """Lines after the subject still go through the normal reflow."""
        result = wrap_commit_reflow._reflow_block(
            [
                "feat(tools): add launcher",
                "",
                "Use foo_bar today",
            ],
            80,
            add_backticks=True,
        )

        assert result == [
            "feat(tools): add launcher",
            "",
            "Use `foo_bar` today",
        ]

    def test_non_subject_first_line_processed_normally(self) -> None:
        """Without a subject match, the whole block is reflowed."""
        result = wrap_commit_reflow._reflow_block(
            ["use foo_bar here"],
            80,
            add_backticks=True,
        )

        assert result == ["use `foo_bar` here"]

    def test_empty_block_returns_empty_list(self) -> None:
        """An empty block produces no output."""
        assert wrap_commit_reflow._reflow_block([], 80, add_backticks=True) == []


class TestReflowLinesWrapList:
    """Validate wrap-list literals flowing through ``reflow_lines``."""

    def test_paragraph_literal_is_backticked(self) -> None:
        """A configured literal in a paragraph is wrapped."""
        assert wrap_commit_reflow.reflow_lines(
            ["we make better cars today"],
            80,
            literals=["make better"],
        ) == ["we `make better` cars today"]

    def test_bullet_literal_is_backticked(self) -> None:
        """A configured literal in a bullet is wrapped too."""
        assert wrap_commit_reflow.reflow_lines(
            ["- we make better cars"],
            80,
            literals=["make better"],
        ) == ["- we `make better` cars"]

    def test_no_backticks_flag_skips_literals(self) -> None:
        """With backticks off, wrap-list literals are left alone."""
        assert wrap_commit_reflow.reflow_lines(
            ["we make better cars"],
            80,
            add_backticks=False,
            literals=["make better"],
        ) == ["we make better cars"]

    def test_no_literals_matches_prior_behaviour(self) -> None:
        """Without literals, output matches the no-wrap-list behaviour."""
        assert wrap_commit_reflow.reflow_lines(
            ["we make better cars"],
            80,
        ) == ["we make better cars"]


class TestReflowLinesPathSeparator:
    """Validate the paragraph-only path-separator backticking."""

    def test_paragraph_wraps_forward_slash_word(self) -> None:
        """A paragraph backticks a forward-slash path word."""
        assert wrap_commit_reflow.reflow_lines(
            ["edit src/pdfss/tests today"],
            80,
        ) == ["edit `src/pdfss/tests` today"]

    def test_paragraph_wraps_backslash_word(self) -> None:
        """A paragraph backticks a backslash path word."""
        assert wrap_commit_reflow.reflow_lines(
            [r"open C:\Users\vonc now"],
            80,
        ) == [r"open `C:\Users\vonc` now"]

    def test_bullet_does_not_wrap_slash_word(self) -> None:
        """The item list keeps the regular rules, so a slash word stays bare."""
        assert wrap_commit_reflow.reflow_lines(
            ["- edit src/pdfss/tests today"],
            80,
        ) == ["- edit src/pdfss/tests today"]

    def test_no_backticks_flag_skips_the_slash_rule(self) -> None:
        """With backticks off, slash words are left alone."""
        assert wrap_commit_reflow.reflow_lines(
            ["edit src/pdfss/tests today"],
            80,
            add_backticks=False,
        ) == ["edit src/pdfss/tests today"]

    def test_slash_word_already_in_span_is_not_rewrapped(self) -> None:
        """A slash word already inside a span is left as-is."""
        assert wrap_commit_reflow.reflow_lines(
            ["edit `src/pdfss` today"],
            80,
        ) == ["edit `src/pdfss` today"]

    def test_slash_words_merge_after_wrapping(self) -> None:
        """Adjacent slash words wrap, then the merge folds them into one span."""
        assert wrap_commit_reflow.reflow_lines(
            ["paths a/b c/d here"],
            80,
        ) == ["paths `a/b c/d` here"]


class TestReflowLinesSubjectWrapStrip:
    r"""Validate the final ``\`type(scope)\`:`` opener strip in ``reflow_lines``."""

    def test_paragraph_subject_opener_is_unwrapped(self) -> None:
        r"""A body line that wraps to ``\`feat(tools)\`:`` is stripped bare."""
        # The word pass wraps ``feat(tools):`` via the open-paren rule;
        # the final strip removes the two backticks again.
        assert wrap_commit_reflow.reflow_lines(
            ["feat(tools): add launcher"],
            80,
        ) == ["feat(tools): add launcher"]

    def test_second_subject_line_is_unwrapped(self) -> None:
        """A second subject-shaped paragraph line is also bared."""
        assert wrap_commit_reflow.reflow_lines(
            ["fix(io): two"],
            80,
        ) == ["fix(io): two"]

    def test_bullet_subject_keeps_its_backticks(self) -> None:
        r"""A bullet opens with ``- ``, so its ``\`fix(io)\`:`` head stays wrapped."""
        # The strip is anchored at the line start; a bullet line opens
        # with ``- ``, never a backtick, so its head is preserved.
        assert wrap_commit_reflow.reflow_lines(
            ["- fix(io): two"],
            80,
        ) == ["- `fix(io)`: two"]

    def test_no_backticks_flag_skips_the_strip(self) -> None:
        """With backticks off, an existing wrapped opener is left untouched."""
        assert wrap_commit_reflow.reflow_lines(
            ["`feat(tools)`: add launcher"],
            80,
            add_backticks=False,
        ) == ["`feat(tools)`: add launcher"]

    def test_rest_of_subject_line_still_backticked(self) -> None:
        """The opener is bared while later code-like words still wrap."""
        # ``feat(tools):`` is unwrapped by the strip, but ``foo_bar`` in
        # the same line still gets the regular code-like backticks.
        assert wrap_commit_reflow.reflow_lines(
            ["feat(tools): tweak foo_bar today"],
            80,
        ) == ["feat(tools): tweak `foo_bar` today"]


# eof
