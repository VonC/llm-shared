"""Tests for the commit-text width enforcer.

Cover ``tools.wrap_commit``: list-item detection, greedy word wrapping,
empty-line preservation, bullet-continuation merging, the adjacent
backtick-span merge that folds a whitespace-separated run of code spans
into one span, the wrap-list pass that backticks configured string
literals loaded from ``wrap-list.backtick`` files, the paragraph-only
path-separator rule that backticks words holding a slash or backslash,
the per-block and whole-file driver, and the CLI entry point in normal,
``--check``, and ``--no-delimiters`` modes. A ``runpy`` test exercises
the ``__main__`` script path end to end.

The tool resolves the default target file under the calling project's
root through the shared ``find_project_root`` helper; the relevant test
pins that resolution with ``monkeypatch`` so it never depends on the
real checkout.
"""

from __future__ import annotations

import logging
import runpy
import sys
from typing import TYPE_CHECKING

import pytest

from tools import wrap_commit

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

_EXIT_CHANGES_PENDING = 1
_EXIT_FATAL = 2
_EXPECTED_BLOCK_COUNT = 2

# Capture the real wrap-list collector before the autouse neutralizer
# patches it, so the dedicated collector tests can still reach the real
# function.
_REAL_COLLECT_WRAP_LIST_LITERALS = wrap_commit._collect_wrap_list_literals


@pytest.fixture(autouse=True)
def _neutralize_ambient_wrap_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep ``main`` deterministic regardless of real wrap-list files.

    A ``wrap-list.backtick`` in the repo, the tool folder, or the user
    home would otherwise feed ``main`` and shift the exact-output
    assertions. The dedicated collector tests use
    ``_REAL_COLLECT_WRAP_LIST_LITERALS`` to exercise the real function.
    """
    monkeypatch.setattr(
        wrap_commit, "_collect_wrap_list_literals", lambda _start: [],
    )


class TestListItemDetection:
    r"""Validate the ``^(\s*)- `` list-item recognizer."""

    def test_detects_plain_bullet_with_empty_indent(self) -> None:
        """A bare ``- foo`` line is a list item with no indent."""
        match = wrap_commit._is_list_item("- foo")

        assert match is not None
        assert match.group(1) == ""

    def test_detects_indented_bullet(self) -> None:
        """Leading whitespace before the dash is captured as the indent."""
        match = wrap_commit._is_list_item("    - foo")

        assert match is not None
        assert match.group(1) == "    "

    def test_rejects_plain_paragraph_line(self) -> None:
        """A line without a dash marker is not a list item."""
        assert wrap_commit._is_list_item("foo bar") is None

    def test_rejects_dash_without_trailing_space(self) -> None:
        """``-foo`` does not start a list item; the dash must be followed by a space."""
        assert wrap_commit._is_list_item("-foo") is None


class TestWrapWords:
    """Validate the greedy word-wrapping helper."""

    def test_empty_words_with_no_prefix_returns_empty_list(self) -> None:
        """No words and no first prefix produce no output lines."""
        assert wrap_commit._wrap_words([], 80, "", "") == []

    def test_empty_words_with_first_prefix_keeps_prefix_alone(self) -> None:
        """A bullet prefix without content is still emitted, rstrip'd."""
        assert wrap_commit._wrap_words([], 80, "- ", "  ") == ["-"]

    def test_single_word_fits_one_line(self) -> None:
        """One word produces one line."""
        assert wrap_commit._wrap_words(["foo"], 80, "", "") == ["foo"]

    def test_multiple_words_pack_under_width(self) -> None:
        """Words that fit are joined on one line."""
        assert wrap_commit._wrap_words(["foo", "bar", "baz"], 80, "", "") == [
            "foo bar baz",
        ]

    def test_words_wrap_when_line_would_exceed_width(self) -> None:
        """A word that would push past width starts a new line."""
        result = wrap_commit._wrap_words(["foo", "bar", "baz"], 7, "", "")

        assert result == ["foo bar", "baz"]

    def test_continuation_prefix_applied_after_wrap(self) -> None:
        """Lines after the first start with the continuation prefix."""
        result = wrap_commit._wrap_words(
            ["alpha", "beta", "gamma"],
            12,
            "- ",
            "  ",
        )

        assert result == ["- alpha beta", "  gamma"]

    def test_overlong_single_word_still_emitted(self) -> None:
        """A word longer than width is kept whole on its own line."""
        long_word = "x" * 50

        assert wrap_commit._wrap_words([long_word], 10, "", "") == [long_word]


class TestReflowLines:
    """Validate the line-by-line reflow that drives each block."""

    def test_empty_input_returns_empty_output(self) -> None:
        """Reflowing an empty list of lines yields an empty list."""
        assert wrap_commit.reflow_lines([], 80) == []

    def test_preserves_consecutive_empty_lines(self) -> None:
        """Blank lines are passed through one-for-one."""
        assert wrap_commit.reflow_lines(["", ""], 80) == ["", ""]

    def test_merges_consecutive_paragraph_lines(self) -> None:
        """Two non-empty non-bullet lines collapse into one paragraph."""
        assert wrap_commit.reflow_lines(["foo bar", "baz qux"], 80) == [
            "foo bar baz qux",
        ]

    def test_wraps_long_paragraph_at_column_zero(self) -> None:
        """A paragraph that exceeds width wraps without any indent prefix."""
        assert wrap_commit.reflow_lines(["foo bar baz qux"], 7) == [
            "foo bar",
            "baz qux",
        ]

    def test_short_bullet_passes_through_unchanged(self) -> None:
        """A list item shorter than width is emitted verbatim."""
        assert wrap_commit.reflow_lines(["- foo bar"], 80) == ["- foo bar"]

    def test_long_bullet_wraps_with_two_space_continuation(self) -> None:
        """A long bullet at column 0 wraps with a two-space continuation indent."""
        assert wrap_commit.reflow_lines(["- alpha beta gamma"], 12) == [
            "- alpha beta",
            "  gamma",
        ]

    def test_indented_bullet_continuation_matches_dash_column(self) -> None:
        """A bullet indented by N spaces continues at N+2 spaces."""
        assert wrap_commit.reflow_lines(["  - alpha beta gamma"], 14) == [
            "  - alpha beta",
            "    gamma",
        ]

    def test_consecutive_bullets_stay_separated(self) -> None:
        """Each bullet line stays its own list item."""
        assert wrap_commit.reflow_lines(["- foo", "- bar"], 80) == [
            "- foo",
            "- bar",
        ]

    def test_empty_line_ends_a_list_item(self) -> None:
        """A blank line closes the current list item."""
        assert wrap_commit.reflow_lines(["- foo", "", "- bar"], 80) == [
            "- foo",
            "",
            "- bar",
        ]

    def test_bullet_continuation_line_is_merged_into_item(self) -> None:
        """Indented non-bullet lines after a bullet are merged into it."""
        assert wrap_commit.reflow_lines(
            ["- alpha", "  beta gamma"],
            80,
        ) == ["- alpha beta gamma"]

    def test_paragraph_then_bullet_keeps_both_blocks(self) -> None:
        """A bullet line ends the running paragraph block."""
        assert wrap_commit.reflow_lines(
            ["a paragraph", "- a bullet"],
            80,
        ) == ["a paragraph", "- a bullet"]


class TestProcessText:
    """Validate the per-block driver around ``reflow_lines``."""

    def test_no_delimiters_reflows_whole_text(self) -> None:
        """When both delimiters are None the whole text is reflowed."""
        result = wrap_commit.process_text("foo bar\nbaz qux\n", 80, None, None)

        assert result == "foo bar baz qux\n"

    def test_with_delimiters_reflows_only_inside_block(self) -> None:
        """Text outside the block is preserved verbatim."""
        text = (
            "before line\n"
            "```log\n"
            "foo bar\n"
            "baz qux\n"
            "```\n"
            "after line\n"
        )

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert result == (
            "before line\n"
            "```log\n"
            "foo bar baz qux\n"
            "```\n"
            "after line\n"
        )

    def test_multiple_blocks_are_each_reflowed(self) -> None:
        """Every delimited block in the file is processed independently."""
        text = (
            "```log\n"
            "alpha beta\n"
            "gamma\n"
            "```\n"
            "between\n"
            "```log\n"
            "delta\n"
            "epsilon\n"
            "```\n"
        )

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert "alpha beta gamma" in result
        assert "delta epsilon" in result
        assert result.count("```log") == _EXPECTED_BLOCK_COUNT
        assert "between" in result

    def test_no_block_in_file_returns_text_unchanged(self) -> None:
        """A file with no open delimiter is returned as-is."""
        text = "no fences here at all\n"

        assert wrap_commit.process_text(text, 80, "```log", "```") == text

    def test_unterminated_block_still_reflows_collected_content(self) -> None:
        """A block missing its close delimiter still has its content reflowed."""
        text = "```log\nfoo bar\nbaz qux\n"

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert "foo bar baz qux" in result

    def test_preserves_trailing_newline(self) -> None:
        """A trailing newline in the input is preserved on the output."""
        result = wrap_commit.process_text("foo\n", 80, None, None)

        assert result.endswith("\n")

    def test_no_trailing_newline_added_when_input_has_none(self) -> None:
        """No trailing newline is added when the input did not have one."""
        result = wrap_commit.process_text("foo", 80, None, None)

        assert not result.endswith("\n")


class TestResolveTargetFile:
    """Validate the file-resolution rules used by ``main``."""

    def test_explicit_file_arg_is_used_directly(self, tmp_path: Path) -> None:
        """A user-supplied ``--file`` path is returned verbatim (resolved)."""
        target = tmp_path / "explicit.txt"
        args = wrap_commit._parse_args(["--file", str(target)])

        resolved = wrap_commit._resolve_target_file(args)

        assert resolved == target.resolve()

    def test_default_falls_back_to_project_root_a_commit(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Without ``--file`` the tool targets ``<project_root>/a.commit``."""

        def fake_find_project_root(_start: Path) -> Path:
            return tmp_path

        monkeypatch.setattr(wrap_commit, "find_project_root", fake_find_project_root)
        args = wrap_commit._parse_args([])

        resolved = wrap_commit._resolve_target_file(args)

        assert resolved == tmp_path / wrap_commit.DEFAULT_FILE_NAME


class TestMain:
    """Validate the CLI entry point end to end."""

    def test_main_processes_default_a_commit_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """With no flags the tool rewrites ``<project_root>/a.commit`` in place."""
        commit_file = tmp_path / wrap_commit.DEFAULT_FILE_NAME
        commit_file.write_text(
            "before\n```log\nfoo bar\nbaz qux\n```\nafter\n",
            encoding="utf-8",
        )

        def fake_find_project_root(_start: Path) -> Path:
            return tmp_path

        monkeypatch.setattr(wrap_commit, "find_project_root", fake_find_project_root)

        exit_code = wrap_commit.main([])

        assert exit_code == 0
        assert commit_file.read_text(encoding="utf-8") == (
            "before\n```log\nfoo bar baz qux\n```\nafter\n"
        )

    def test_main_with_explicit_file_overrides_default(
        self,
        tmp_path: Path,
    ) -> None:
        """``--file`` redirects the tool to a different path."""
        custom = tmp_path / "custom.txt"
        custom.write_text(
            "```log\nfoo bar\nbaz qux\n```\n",
            encoding="utf-8",
        )

        exit_code = wrap_commit.main(["--file", str(custom)])

        assert exit_code == 0
        assert custom.read_text(encoding="utf-8") == (
            "```log\nfoo bar baz qux\n```\n"
        )

    def test_main_with_smaller_width_wraps_content(
        self,
        tmp_path: Path,
    ) -> None:
        """``--width`` controls the maximum line width inside the block."""
        custom = tmp_path / "custom.txt"
        custom.write_text(
            "```log\nalpha beta gamma delta\n```\n",
            encoding="utf-8",
        )

        exit_code = wrap_commit.main(["--file", str(custom), "--width", "12"])

        assert exit_code == 0
        assert custom.read_text(encoding="utf-8") == (
            "```log\nalpha beta\ngamma delta\n```\n"
        )

    def test_main_no_delimiters_flag_reflows_whole_file(
        self,
        tmp_path: Path,
    ) -> None:
        """``--no-delimiters`` ignores the open/close markers."""
        custom = tmp_path / "plain.txt"
        custom.write_text("foo bar\nbaz qux\n", encoding="utf-8")

        exit_code = wrap_commit.main(["--file", str(custom), "--no-delimiters"])

        assert exit_code == 0
        assert custom.read_text(encoding="utf-8") == "foo bar baz qux\n"

    def test_main_custom_open_and_close_delimiters(
        self,
        tmp_path: Path,
    ) -> None:
        """``--open`` and ``--close`` override the default markers."""
        custom = tmp_path / "custom.txt"
        custom.write_text(
            "<<<\nfoo bar\nbaz\n>>>\n",
            encoding="utf-8",
        )

        exit_code = wrap_commit.main(
            ["--file", str(custom), "--open", "<<<", "--close", ">>>"],
        )

        assert exit_code == 0
        assert custom.read_text(encoding="utf-8") == (
            "<<<\nfoo bar baz\n>>>\n"
        )

    def test_main_check_mode_with_no_changes_needed_returns_zero(
        self,
        tmp_path: Path,
    ) -> None:
        """``--check`` returns 0 and leaves the file alone when no change is needed."""
        custom = tmp_path / "custom.txt"
        original = "```log\nfoo bar\n```\n"
        custom.write_text(original, encoding="utf-8")

        exit_code = wrap_commit.main(["--file", str(custom), "--check"])

        assert exit_code == 0
        assert custom.read_text(encoding="utf-8") == original

    def test_main_check_mode_with_pending_changes_returns_one(
        self,
        tmp_path: Path,
    ) -> None:
        """``--check`` returns 1 without writing when changes would be made."""
        custom = tmp_path / "custom.txt"
        original = "```log\nfoo bar\nbaz qux\n```\n"
        custom.write_text(original, encoding="utf-8")

        exit_code = wrap_commit.main(["--file", str(custom), "--check"])

        assert exit_code == _EXIT_CHANGES_PENDING
        assert custom.read_text(encoding="utf-8") == original

    def test_main_missing_file_raises_wrap_commit_error(
        self,
        tmp_path: Path,
    ) -> None:
        """A missing target file is surfaced as a ``WrapCommitError``."""
        missing = tmp_path / "missing.txt"

        with pytest.raises(wrap_commit.WrapCommitError, match="File not found"):
            wrap_commit.main(["--file", str(missing)])


class TestBacktickRegionDetection:
    """Validate detection of existing inline backtick spans."""

    def test_no_backticks_returns_empty_list(self) -> None:
        """Text without backticks reports no spans."""
        assert wrap_commit._find_backtick_regions("foo bar") == []

    def test_one_pair_returns_one_region_covering_both_ticks(self) -> None:
        """A single pair returns one span covering both backticks."""
        assert wrap_commit._find_backtick_regions("`foo`") == [(0, 5)]

    def test_multiple_pairs_each_reported(self) -> None:
        """Each pair of backticks is reported as its own span."""
        text = "use `foo` and `bar`"

        assert wrap_commit._find_backtick_regions(text) == [(4, 9), (14, 19)]

    def test_unmatched_trailing_backtick_is_ignored(self) -> None:
        """An unmatched trailing backtick produces no span."""
        assert wrap_commit._find_backtick_regions("`foo") == []


class TestWordMatchesWrapException:
    r"""Validate the ``v\d+\.`` and ``[Oo]\(`` whitelist exemptions."""

    def test_version_literal_matches(self) -> None:
        """``v1.0`` matches the version-literal exemption."""
        assert wrap_commit._word_matches_wrap_exception("v1.0")

    def test_multi_part_version_literal_matches(self) -> None:
        """``v2.5.3`` matches the version-literal exemption."""
        assert wrap_commit._word_matches_wrap_exception("v2.5.3")

    def test_version_literal_with_trailing_punct_matches(self) -> None:
        """``v1.0,`` still matches -- the regex anchors at the start only."""
        assert wrap_commit._word_matches_wrap_exception("v1.0,")

    def test_uppercase_v_does_not_match(self) -> None:
        """The regex is lowercase-only: ``V1.0`` is not exempted."""
        assert not wrap_commit._word_matches_wrap_exception("V1.0")

    def test_v_without_digits_does_not_match(self) -> None:
        r"""A leading ``v`` without ``\d+\.`` is not exempted."""
        assert not wrap_commit._word_matches_wrap_exception("v.x")
        assert not wrap_commit._word_matches_wrap_exception("v")

    def test_v_with_digits_but_no_dot_does_not_match(self) -> None:
        """``v1`` lacks the trailing dot and is not exempted."""
        assert not wrap_commit._word_matches_wrap_exception("v1")

    def test_uppercase_big_o_matches(self) -> None:
        """``O(n)`` matches the big-O exemption."""
        assert wrap_commit._word_matches_wrap_exception("O(n)")

    def test_lowercase_o_open_paren_matches(self) -> None:
        """``o(log)`` matches the big-O exemption."""
        assert wrap_commit._word_matches_wrap_exception("o(log)")

    def test_o_without_open_paren_does_not_match(self) -> None:
        """A leading ``O``/``o`` without ``(`` is not exempted."""
        assert not wrap_commit._word_matches_wrap_exception("OK(foo)")
        assert not wrap_commit._word_matches_wrap_exception("octopus")

    def test_plain_word_does_not_match(self) -> None:
        """A word that does not start with either pattern is not exempted."""
        assert not wrap_commit._word_matches_wrap_exception("foo_bar")


class TestWordNeedsBackticks:
    """Validate each individual backtick-wrap rule."""

    def test_underscore_anywhere_qualifies(self) -> None:
        """A word containing ``_`` qualifies."""
        assert wrap_commit._word_needs_backticks("foo_bar")

    def test_dot_in_middle_qualifies(self) -> None:
        """A non-trailing dot qualifies."""
        assert wrap_commit._word_needs_backticks("foo.bar")

    def test_dot_at_end_only_does_not_qualify(self) -> None:
        """A trailing-only dot (sentence punctuation) does not qualify."""
        assert not wrap_commit._word_needs_backticks("machines.")

    def test_open_paren_in_middle_qualifies(self) -> None:
        """A non-leading open paren qualifies."""
        assert wrap_commit._word_needs_backticks("foo(bar)")

    def test_open_paren_at_start_only_does_not_qualify(self) -> None:
        """A leading-only open paren does not qualify."""
        assert not wrap_commit._word_needs_backticks("(foo")

    def test_single_uppercase_does_not_qualify(self) -> None:
        """``Xyz`` (one uppercase) does not qualify under the CamelCase rule."""
        assert not wrap_commit._word_needs_backticks("Xyz")

    def test_two_uppercase_qualifies(self) -> None:
        """``XyzUvw`` (two uppercase + lowercase) qualifies under CamelCase."""
        assert wrap_commit._word_needs_backticks("XyzUvw")

    def test_all_lowercase_does_not_qualify(self) -> None:
        """A plain lowercase word does not qualify."""
        assert not wrap_commit._word_needs_backticks("paragraph")

    def test_empty_word_does_not_qualify(self) -> None:
        """Empty input does not qualify."""
        assert not wrap_commit._word_needs_backticks("")

    def test_pure_acronym_does_not_qualify(self) -> None:
        """A pure acronym (no lowercase) is not CamelCase and stays bare."""
        assert not wrap_commit._word_needs_backticks("PBT")
        assert not wrap_commit._word_needs_backticks("URL")

    def test_acronym_with_trailing_close_paren_does_not_qualify(self) -> None:
        """``PBT)`` is an acronym followed by punctuation; no lowercase, stays bare."""
        assert not wrap_commit._word_needs_backticks("PBT)")

    def test_close_paren_alone_does_not_qualify(self) -> None:
        """A single uppercase + ``)`` does not qualify -- closing paren is irrelevant."""
        assert not wrap_commit._word_needs_backticks("X)")

    def test_open_paren_with_close_paren_still_qualifies(self) -> None:
        """``x(r)`` qualifies via the open-paren rule despite the trailing ``)``."""
        assert wrap_commit._word_needs_backticks("x(r)")

    def test_pypi_qualifies_under_camelcase(self) -> None:
        """``PyPI`` has 3 uppercase + 1 lowercase, so it is CamelCase."""
        assert wrap_commit._word_needs_backticks("PyPI")

    def test_version_literal_short_circuits_to_false(self) -> None:
        """``v1.0`` is exempt even though it has a non-trailing dot."""
        assert not wrap_commit._word_needs_backticks("v1.0")

    def test_big_o_notation_short_circuits_to_false(self) -> None:
        """``O(n)`` is exempt even though it has a non-leading ``(``."""
        assert not wrap_commit._word_needs_backticks("O(n)")

    def test_dash_prefixed_tokens_qualify(self) -> None:
        """Tokens that start with ``-`` and have non-dash content qualify."""
        assert wrap_commit._word_needs_backticks("-x")
        assert wrap_commit._word_needs_backticks("--foo")
        assert wrap_commit._word_needs_backticks("--no-backticks")
        assert wrap_commit._word_needs_backticks("---bar")

    def test_all_dash_tokens_do_not_qualify(self) -> None:
        """Bare separators like ``-``, ``--``, ``---`` are not wrapped."""
        assert not wrap_commit._word_needs_backticks("-")
        assert not wrap_commit._word_needs_backticks("--")
        assert not wrap_commit._word_needs_backticks("---")

    def test_dashed_token_helper_directly(self) -> None:
        """Direct check of the dashed-token helper."""
        assert wrap_commit._word_is_dashed_token("-x")
        assert wrap_commit._word_is_dashed_token("--foo")
        assert not wrap_commit._word_is_dashed_token("--")
        assert not wrap_commit._word_is_dashed_token("foo")
        assert not wrap_commit._word_is_dashed_token("foo-bar")

    def test_equals_anywhere_qualifies(self) -> None:
        """A token with ``=`` mixed with other chars qualifies."""
        assert wrap_commit._word_needs_backticks("KEY=value")
        assert wrap_commit._word_needs_backticks("foo=bar")
        assert wrap_commit._word_needs_backticks("=leading")
        assert wrap_commit._word_needs_backticks("trailing=")

    def test_bare_equals_does_not_qualify(self) -> None:
        """``=`` and ``==`` are only ``=`` chars, so the rule does not fire."""
        assert not wrap_commit._word_needs_backticks("=")
        assert not wrap_commit._word_needs_backticks("==")
        assert not wrap_commit._word_needs_backticks("===")

    def test_bare_underscore_does_not_qualify(self) -> None:
        """``_`` and ``__`` are only ``_`` chars, so the rule does not fire."""
        assert not wrap_commit._word_needs_backticks("_")
        assert not wrap_commit._word_needs_backticks("__")
        assert not wrap_commit._word_needs_backticks("___")

    def test_helper_word_has_other_chars_than(self) -> None:
        """Direct check of the mixed-char helper for both ``=`` and ``_``."""
        # The char must be present.
        assert not wrap_commit._word_has_other_chars_than("foo", "=")
        # The char must be mixed with at least one other character.
        assert not wrap_commit._word_has_other_chars_than("==", "=")
        assert not wrap_commit._word_has_other_chars_than("__", "_")
        # Mixed cases qualify.
        assert wrap_commit._word_has_other_chars_than("=x", "=")
        assert wrap_commit._word_has_other_chars_than("a_b", "_")

    def test_camelcase_helper_directly(self) -> None:
        """The CamelCase helper requires 2+ upper AND 1+ lower."""
        assert wrap_commit._word_is_camelcase("XyzUvw")
        assert not wrap_commit._word_is_camelcase("Xyz")
        assert not wrap_commit._word_is_camelcase("URL")


class TestTokenizeKeepingBackticks:
    """Validate the tokenizer that treats backtick spans as indivisible."""

    def test_plain_text_splits_on_whitespace(self) -> None:
        """Without backticks, the tokenizer is a regular whitespace split."""
        assert wrap_commit._tokenize_keeping_backticks("a b c") == ["a", "b", "c"]

    def test_collapses_consecutive_whitespace(self) -> None:
        """Multiple-space gaps still collapse to a single token boundary."""
        assert wrap_commit._tokenize_keeping_backticks("a  b") == ["a", "b"]

    def test_leading_and_trailing_whitespace_ignored(self) -> None:
        """Outer whitespace does not create empty tokens."""
        assert wrap_commit._tokenize_keeping_backticks("  abc  ") == ["abc"]

    def test_backtick_span_with_internal_space_kept_as_one_token(self) -> None:
        r"""A ``\`xx yyy zzz\``` span is returned as a single token."""
        assert wrap_commit._tokenize_keeping_backticks("a `xx yyy zzz` b") == [
            "a",
            "`xx yyy zzz`",
            "b",
        ]

    def test_multiple_backtick_spans_each_kept_intact(self) -> None:
        """Each span is its own indivisible token."""
        assert wrap_commit._tokenize_keeping_backticks(
            "see `a b` and `c d e` here",
        ) == ["see", "`a b`", "and", "`c d e`", "here"]

    def test_backtick_span_without_internal_space_is_one_token(self) -> None:
        r"""A no-space ``\`foo\``` is naturally a single token."""
        assert wrap_commit._tokenize_keeping_backticks("a `foo` b") == [
            "a",
            "`foo`",
            "b",
        ]

    def test_empty_input_returns_empty_list(self) -> None:
        """An empty string yields no tokens."""
        assert wrap_commit._tokenize_keeping_backticks("") == []


class TestSplitOuterPunctuation:
    """Validate the (leading, core, trailing) outer-punctuation splitter."""

    def test_no_outer_punctuation_returns_empty_outer(self) -> None:
        """A word without any outer punctuation returns empty leading and trailing."""
        assert wrap_commit._split_outer_punctuation("foo_bar") == (
            "",
            "foo_bar",
            "",
        )

    def test_trailing_colon_is_split_off(self) -> None:
        """A single trailing ``:`` is extracted as the suffix."""
        assert wrap_commit._split_outer_punctuation("foo_bar:") == (
            "",
            "foo_bar",
            ":",
        )

    def test_multiple_trailing_sentence_chars_extracted(self) -> None:
        """A run of trailing sentence-punctuation is fully extracted."""
        assert wrap_commit._split_outer_punctuation("foo.,") == (
            "",
            "foo",
            ".,",
        )

    def test_unbalanced_trailing_close_paren_extracted(self) -> None:
        """A lone trailing ``)`` (no matching ``(``) is extracted."""
        assert wrap_commit._split_outer_punctuation("foo_bar)") == (
            "",
            "foo_bar",
            ")",
        )

    def test_unbalanced_trailing_close_paren_with_sentence_run(self) -> None:
        """A trailing ``).,`` is fully extracted (unbalanced ``)`` plus sentence run)."""
        assert wrap_commit._split_outer_punctuation("foo).,") == (
            "",
            "foo",
            ").,",
        )

    def test_balanced_close_paren_stays_inside_core(self) -> None:
        """``foo(bar)`` is balanced; ``)`` stays in the core."""
        assert wrap_commit._split_outer_punctuation("foo(bar)") == (
            "",
            "foo(bar)",
            "",
        )

    def test_balanced_close_paren_with_trailing_colon(self) -> None:
        """``feat(tools):`` keeps the balanced parens and extracts the ``:``."""
        assert wrap_commit._split_outer_punctuation("feat(tools):") == (
            "",
            "feat(tools)",
            ":",
        )

    def test_unbalanced_leading_open_paren_extracted(self) -> None:
        """A lone leading ``(`` (no matching ``)``) is extracted."""
        assert wrap_commit._split_outer_punctuation("(FlagValidationStatus,") == (
            "(",
            "FlagValidationStatus",
            ",",
        )

    def test_balanced_leading_open_paren_stays_inside_core(self) -> None:
        """``(foo_bar)`` is balanced; both parens stay in the core."""
        assert wrap_commit._split_outer_punctuation("(foo_bar)") == (
            "",
            "(foo_bar)",
            "",
        )

    def test_multiple_unbalanced_leading_parens(self) -> None:
        """Multiple unbalanced leading ``(`` chars are all extracted."""
        assert wrap_commit._split_outer_punctuation("((FlagX,") == (
            "((",
            "FlagX",
            ",",
        )

    def test_multiple_unbalanced_trailing_close_parens(self) -> None:
        """Multiple unbalanced trailing ``)`` chars are all extracted."""
        assert wrap_commit._split_outer_punctuation("read_flag))") == (
            "",
            "read_flag",
            "))",
        )

    def test_only_outer_punct_yields_empty_core(self) -> None:
        """All-punctuation input produces an empty core."""
        assert wrap_commit._split_outer_punctuation(".,;:") == (
            "",
            "",
            ".,;:",
        )

    def test_empty_input_returns_three_empty_strings(self) -> None:
        """An empty word returns three empty strings."""
        assert wrap_commit._split_outer_punctuation("") == ("", "", "")


class TestAddBackticksToWords:
    """Validate the whole-text backtick-wrap pass."""

    def test_no_matching_words_leaves_text_unchanged(self) -> None:
        """A plain sentence with no rule hits is returned verbatim."""
        assert wrap_commit._add_backticks_to_words("foo bar baz") == "foo bar baz"

    def test_wraps_an_underscore_word(self) -> None:
        """A bare ``foo_bar`` token is wrapped in backticks."""
        assert wrap_commit._add_backticks_to_words(
            "use foo_bar here",
        ) == "use `foo_bar` here"

    def test_wraps_a_dot_word(self) -> None:
        """A bare ``senv.bat`` token is wrapped in backticks."""
        assert wrap_commit._add_backticks_to_words(
            "edit senv.bat now",
        ) == "edit `senv.bat` now"

    def test_wraps_a_camelcase_word(self) -> None:
        """A two-uppercase token is wrapped in backticks."""
        assert wrap_commit._add_backticks_to_words(
            "the PyPI mirror",
        ) == "the `PyPI` mirror"

    def test_skips_word_already_in_backtick_region(self) -> None:
        """An already-backticked code span is not double-wrapped."""
        assert wrap_commit._add_backticks_to_words(
            "use `foo_bar` here",
        ) == "use `foo_bar` here"

    def test_skips_word_overlapping_a_backtick_region(self) -> None:
        """A token that touches a backtick span is left alone."""
        # ``use_`foo` `` overlaps the backtick span around ``foo`` so it
        # must not get a second backtick pair around the whole token.
        assert wrap_commit._add_backticks_to_words(
            "use_`foo`",
        ) == "use_`foo`"

    def test_skips_sentence_ending_word(self) -> None:
        """``machines.`` is sentence punctuation and stays bare."""
        assert wrap_commit._add_backticks_to_words(
            "satisfy both machines.",
        ) == "satisfy both machines."

    def test_preserves_whitespace_runs(self) -> None:
        """Multi-space runs between tokens are preserved verbatim."""
        assert wrap_commit._add_backticks_to_words("a  b") == "a  b"

    def test_combines_multiple_matches_in_one_pass(self) -> None:
        """Every matching token in one string is wrapped in one pass."""
        result = wrap_commit._add_backticks_to_words(
            "use foo_bar and senv.bat with PyPI",
        )

        assert result == "use `foo_bar` and `senv.bat` with `PyPI`"

    def test_skips_acronym_with_trailing_close_paren(self) -> None:
        """A token like ``PBT)`` is a prose acronym; it is not wrapped."""
        result = wrap_commit._add_backticks_to_words(
            "tested with PBT) for safety",
        )

        assert result == "tested with PBT) for safety"

    def test_trailing_colon_kept_outside_backticks(self) -> None:
        r"""``foo_bar:`` wraps as ``\`foo_bar\`:`` with the colon outside."""
        assert wrap_commit._add_backticks_to_words(
            "set foo_bar: value",
        ) == "set `foo_bar`: value"

    def test_trailing_comma_kept_outside_backticks(self) -> None:
        """``foo_bar,`` keeps the comma outside the closing backtick."""
        assert wrap_commit._add_backticks_to_words(
            "use foo_bar, then baz",
        ) == "use `foo_bar`, then baz"

    def test_trailing_semicolon_kept_outside_backticks(self) -> None:
        """``foo_bar;`` keeps the semicolon outside."""
        assert wrap_commit._add_backticks_to_words(
            "first foo_bar; then",
        ) == "first `foo_bar`; then"

    def test_trailing_period_kept_outside_backticks(self) -> None:
        """``foo_bar.`` keeps the period outside the closing backtick."""
        assert wrap_commit._add_backticks_to_words(
            "use foo_bar.",
        ) == "use `foo_bar`."

    def test_multiple_trailing_punct_chars_all_go_outside(self) -> None:
        """A run of trailing punctuation is fully extracted outside."""
        assert wrap_commit._add_backticks_to_words(
            "see foo_bar.,",
        ) == "see `foo_bar`.,"

    def test_unbalanced_trailing_close_paren_is_moved_outside(self) -> None:
        r"""``foo_bar)`` wraps as ``\`foo_bar\`)`` -- lone ``)`` goes outside."""
        assert wrap_commit._add_backticks_to_words(
            "wrap foo_bar) here",
        ) == "wrap `foo_bar`) here"

    def test_balanced_close_paren_stays_inside_the_backticks(self) -> None:
        """``foo(bar)`` keeps both parens inside -- the parens are balanced."""
        # ``foo(bar)`` qualifies via the open-paren rule; the trailing
        # ``)`` matches the ``(`` so it stays inside the backticks.
        assert wrap_commit._add_backticks_to_words(
            "call foo(bar) here",
        ) == "call `foo(bar)` here"

    def test_unbalanced_leading_open_paren_is_moved_outside(self) -> None:
        r"""``(FlagValidationStatus,`` wraps as ``(\`FlagValidationStatus\`,``."""
        assert wrap_commit._add_backticks_to_words(
            "see (FlagValidationStatus, here",
        ) == "see (`FlagValidationStatus`, here"

    def test_balanced_leading_open_paren_stays_inside(self) -> None:
        """``(foo_bar)`` keeps both parens inside -- they are balanced."""
        assert wrap_commit._add_backticks_to_words(
            "see (foo_bar) here",
        ) == "see `(foo_bar)` here"

    def test_question_mark_stays_inside(self) -> None:
        """``?`` is neither sentence-trailing nor a paren -- stays inside."""
        assert wrap_commit._add_backticks_to_words(
            "is foo_bar? maybe",
        ) == "is `foo_bar?` maybe"

    def test_typed_scoped_subject_in_paragraph_keeps_colon_outside(self) -> None:
        r"""``feat(tools):`` wraps as ``\`feat(tools)\`:`` in paragraph text."""
        # The parens are balanced so they stay inside; only the
        # trailing ``:`` is extracted.
        assert wrap_commit._add_backticks_to_words(
            "the feat(tools): commit",
        ) == "the `feat(tools)`: commit"

    def test_version_literal_is_not_wrapped(self) -> None:
        """``v1.0`` and ``v2.5.3`` stay bare in paragraph text."""
        assert wrap_commit._add_backticks_to_words(
            "ship v1.0 today and v2.5.3 next",
        ) == "ship v1.0 today and v2.5.3 next"

    def test_big_o_notation_is_not_wrapped(self) -> None:
        """``O(n)`` and ``o(log n)`` stay bare in paragraph text."""
        assert wrap_commit._add_backticks_to_words(
            "complexity is O(n) here and o(log) there",
        ) == "complexity is O(n) here and o(log) there"

    def test_dash_prefixed_long_option_is_wrapped(self) -> None:
        """``--no-backticks`` wraps via the dash-prefix rule."""
        assert wrap_commit._add_backticks_to_words(
            "pass --no-backticks today",
        ) == "pass `--no-backticks` today"

    def test_dash_prefixed_short_option_is_wrapped(self) -> None:
        """``-x`` also wraps -- one dash plus non-dash content qualifies."""
        assert wrap_commit._add_backticks_to_words(
            "pass -x today",
        ) == "pass `-x` today"

    def test_bare_dash_separators_are_not_wrapped(self) -> None:
        """``-``, ``--``, ``---`` are bare separators and stay unwrapped."""
        assert wrap_commit._add_backticks_to_words(
            "before -- after --- end",
        ) == "before -- after --- end"

    def test_equals_assignment_is_wrapped(self) -> None:
        """``KEY=value`` wraps via the ``=`` rule."""
        assert wrap_commit._add_backticks_to_words(
            "set KEY=value here",
        ) == "set `KEY=value` here"

    def test_long_option_with_equals_is_wrapped_once(self) -> None:
        """``--width=80`` wraps as a single backticked token."""
        assert wrap_commit._add_backticks_to_words(
            "use --width=80 now",
        ) == "use `--width=80` now"

    def test_bare_equals_operator_is_not_wrapped(self) -> None:
        """``a == b`` and ``a = b`` keep the bare operator unwrapped."""
        assert wrap_commit._add_backticks_to_words(
            "check a == b here",
        ) == "check a == b here"
        assert wrap_commit._add_backticks_to_words(
            "set a = b now",
        ) == "set a = b now"

    def test_bare_underscore_placeholder_is_not_wrapped(self) -> None:
        """A bare ``_`` token (Python ignore placeholder) is not wrapped."""
        assert wrap_commit._add_backticks_to_words(
            "use _ for ignored",
        ) == "use _ for ignored"

    def test_degenerate_all_punctuation_token_is_left_alone(self) -> None:
        """An all-outer-punctuation token has nothing to wrap; it stays bare.

        ``.,`` qualifies under the ``.`` not-at-end rule (the leading
        dot is not the last char), but stripping the trailing run
        leaves an empty core, so the helper falls back to emitting the
        token unchanged.
        """
        assert wrap_commit._add_backticks_to_words("a .,") == "a .,"


class TestMergeAdjacentBacktickSpans:
    """Validate the adjacent backtick-span merge helper."""

    def test_text_without_spans_is_unchanged(self) -> None:
        """Plain text with no backtick spans is returned verbatim."""
        assert wrap_commit._merge_adjacent_backtick_spans(
            "foo bar baz",
        ) == "foo bar baz"

    def test_single_span_is_unchanged(self) -> None:
        """A lone backtick span has nothing to merge."""
        assert wrap_commit._merge_adjacent_backtick_spans(
            "use `foo` here",
        ) == "use `foo` here"

    def test_two_spans_one_space_merge(self) -> None:
        """Two spans separated by one space fold into one span."""
        assert wrap_commit._merge_adjacent_backtick_spans("`a` `b`") == "`a b`"

    def test_three_spans_collapse_to_one(self) -> None:
        """A run of three spans collapses in the fixpoint loop."""
        assert wrap_commit._merge_adjacent_backtick_spans(
            "`zone 1` `zone 2` `zone 3`",
        ) == "`zone 1 zone 2 zone 3`"

    def test_spans_with_prose_between_do_not_merge(self) -> None:
        """Spans with words between them are left apart."""
        assert wrap_commit._merge_adjacent_backtick_spans(
            "`a` and `b`",
        ) == "`a` and `b`"

    def test_spans_across_single_newline_merge(self) -> None:
        """A span pair split across one newline with indent merges."""
        assert wrap_commit._merge_adjacent_backtick_spans(
            "`--no-cov`\n  `-rxX`",
        ) == "`--no-cov -rxX`"

    def test_spans_across_blank_line_do_not_merge(self) -> None:
        """A blank line (paragraph break) keeps the spans apart."""
        assert wrap_commit._merge_adjacent_backtick_spans(
            "`a`\n\n`b`",
        ) == "`a`\n\n`b`"

    def test_spans_across_bullet_marker_do_not_merge(self) -> None:
        """A following ``- `` bullet marker keeps the spans apart."""
        assert wrap_commit._merge_adjacent_backtick_spans(
            "`a`\n- `b`",
        ) == "`a`\n- `b`"

    def test_tab_between_spans_merges(self) -> None:
        """A tab counts as inter-span whitespace and merges."""
        assert wrap_commit._merge_adjacent_backtick_spans("`a`\t`b`") == "`a b`"

    def test_directly_adjacent_spans_do_not_merge(self) -> None:
        """Spans with no whitespace between them stay as-is."""
        # ``\`a\`\`b\``` has no separator, so the rule (which needs
        # inter-span whitespace) does not fire.
        assert wrap_commit._merge_adjacent_backtick_spans("`a``b`") == "`a``b`"

    def test_surrounding_prose_is_preserved(self) -> None:
        """Prose around a merged run stays intact."""
        assert wrap_commit._merge_adjacent_backtick_spans(
            "run `--a` `--b` now",
        ) == "run `--a --b` now"


class TestReflowLinesBackticks:
    """Validate the backtick pass through ``reflow_lines``."""

    def test_paragraph_gets_code_like_words_backticked_by_default(self) -> None:
        """The default reflow wraps code-like tokens before the width wrap."""
        assert wrap_commit.reflow_lines(
            ["use foo_bar here"],
            80,
        ) == ["use `foo_bar` here"]

    def test_add_backticks_false_disables_the_pass(self) -> None:
        """``add_backticks=False`` skips the wrap step."""
        assert wrap_commit.reflow_lines(
            ["use foo_bar here"],
            80,
            add_backticks=False,
        ) == ["use foo_bar here"]

    def test_bullet_content_also_gets_backticked(self) -> None:
        """List-item content is passed through the backtick wrap too."""
        assert wrap_commit.reflow_lines(
            ["- run foo_bar today"],
            80,
        ) == ["- run `foo_bar` today"]

    def test_backtick_span_with_internal_space_is_not_split(self) -> None:
        r"""A ``\`xx yyy zzz\``` span survives the width wrap as one piece."""
        # Width 12 forces a wrap; the 12-char ``\`xx yyy zzz\``` span
        # must land on its own line, never split mid-span.
        result = wrap_commit.reflow_lines(
            ["alpha `xx yyy zzz` beta"],
            12,
            add_backticks=False,
        )

        assert result == ["alpha", "`xx yyy zzz`", "beta"]

    def test_backtick_span_in_bullet_is_not_split(self) -> None:
        r"""Inside a list item, a backtick span also stays intact."""
        # Width 12 forces a wrap; the span ``\`xx yyy zzz\``` must stay
        # whole on its own continuation line, never torn at an inner space.
        result = wrap_commit.reflow_lines(
            ["- a `xx yyy zzz` b"],
            12,
            add_backticks=False,
        )

        assert result == ["- a", "  `xx yyy zzz`", "  b"]

    def test_adjacent_spans_merge_in_paragraph(self) -> None:
        """Code spans the backtick pass wraps side by side fold into one."""
        # ``--testmon`` and ``--no-cov`` each get backticked, then the
        # merge folds the pair into a single span.
        assert wrap_commit.reflow_lines(
            ["run --testmon --no-cov here"],
            80,
        ) == ["run `--testmon --no-cov` here"]

    def test_adjacent_spans_merge_in_bullet(self) -> None:
        """The merge runs on list-item content too."""
        assert wrap_commit.reflow_lines(
            ["- pass --testmon --no-cov today"],
            80,
        ) == ["- pass `--testmon --no-cov` today"]

    def test_spans_split_across_input_lines_merge(self) -> None:
        """Spans the source split across two lines merge after the collapse."""
        # The two paragraph lines collapse into one first, so the spans
        # land side by side and fold into a single span.
        assert wrap_commit.reflow_lines(
            ["existing `--a`", "`--b` tail"],
            80,
        ) == ["existing `--a --b` tail"]

    def test_no_backticks_flag_skips_the_merge(self) -> None:
        """``add_backticks=False`` leaves existing adjacent spans apart."""
        assert wrap_commit.reflow_lines(
            ["use `--a` `--b` now"],
            80,
            add_backticks=False,
        ) == ["use `--a` `--b` now"]


class TestProcessTextBacktickFlag:
    """Validate that ``process_text`` forwards ``add_backticks``."""

    def test_process_text_default_wraps_backticks(self) -> None:
        """By default ``process_text`` wraps code-like tokens inside blocks."""
        text = "```log\nuse foo_bar here\n```\n"

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert result == "```log\nuse `foo_bar` here\n```\n"

    def test_process_text_add_backticks_false_disables_the_pass(self) -> None:
        """``add_backticks=False`` is forwarded to ``reflow_lines``."""
        text = "```log\nuse foo_bar here\n```\n"

        result = wrap_commit.process_text(
            text,
            80,
            "```log",
            "```",
            add_backticks=False,
        )

        assert result == "```log\nuse foo_bar here\n```\n"

    def test_process_text_unterminated_block_still_runs_backtick_pass(
        self,
    ) -> None:
        """An unterminated block still gets its content backticked."""
        text = "```log\nuse foo_bar here\n"

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert "`foo_bar`" in result

    def test_process_text_no_delimiters_runs_backtick_pass(self) -> None:
        """Whole-file mode also forwards ``add_backticks``."""
        text = "use foo_bar here\n"

        result = wrap_commit.process_text(text, 80, None, None)

        assert result == "use `foo_bar` here\n"

    def test_process_text_merges_adjacent_spans_in_block(self) -> None:
        """The default run folds adjacent code spans inside a block."""
        text = "```log\nrun --testmon --no-cov now\n```\n"

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert result == "```log\nrun `--testmon --no-cov` now\n```\n"


class TestMainNoBackticksFlag:
    """Validate the ``--no-backticks`` CLI flag."""

    def test_main_default_wraps_code_like_words(self, tmp_path: Path) -> None:
        """Default CLI run wraps code-like tokens inside the block."""
        target = tmp_path / "custom.txt"
        target.write_text(
            "```log\nuse foo_bar here\n```\n",
            encoding="utf-8",
        )

        exit_code = wrap_commit.main(["--file", str(target)])

        assert exit_code == 0
        assert target.read_text(encoding="utf-8") == (
            "```log\nuse `foo_bar` here\n```\n"
        )

    def test_main_no_backticks_flag_skips_the_pass(self, tmp_path: Path) -> None:
        """``--no-backticks`` makes the tool skip the backtick wrap."""
        target = tmp_path / "custom.txt"
        target.write_text(
            "```log\nuse foo_bar here\n```\n",
            encoding="utf-8",
        )

        exit_code = wrap_commit.main(["--file", str(target), "--no-backticks"])

        # No reflow either, since nothing else needed changing.
        assert exit_code == 0
        assert target.read_text(encoding="utf-8") == (
            "```log\nuse foo_bar here\n```\n"
        )


class TestCommitSubjectPattern:
    r"""Validate the ``^\S+\(.*?\):\s`` conventional-subject recognizer."""

    def test_matches_typed_and_scoped_subject(self) -> None:
        """``feat(tools): add ...`` matches the pattern."""
        assert wrap_commit.COMMIT_SUBJECT_PATTERN.match(
            "feat(tools): add cert-aware uv launcher",
        ) is not None

    def test_does_not_match_subject_without_scope(self) -> None:
        """A subject without parens (``feat: x``) does not match."""
        assert wrap_commit.COMMIT_SUBJECT_PATTERN.match("feat: xxx") is None

    def test_does_not_match_plain_paragraph(self) -> None:
        """A regular sentence does not match the subject pattern."""
        assert wrap_commit.COMMIT_SUBJECT_PATTERN.match("regular line") is None


class TestReflowBlockSubjectSkip:
    """Validate ``_reflow_block`` keeps a leading commit subject verbatim."""

    def test_subject_line_is_emitted_verbatim(self) -> None:
        """A first-line commit subject is returned untouched."""
        result = wrap_commit._reflow_block(
            ["feat(tools): add cert-aware uv launcher"],
            80,
            add_backticks=True,
        )

        assert result == ["feat(tools): add cert-aware uv launcher"]

    def test_subject_line_skips_backtick_pass(self) -> None:
        """No backticks are added to the subject line."""
        result = wrap_commit._reflow_block(
            ["feat(tools): add foo_bar today"],
            80,
            add_backticks=True,
        )

        assert result == ["feat(tools): add foo_bar today"]

    def test_subject_line_skips_width_wrap(self) -> None:
        """An overlong subject line is preserved even past the width."""
        long_subject = "feat(tools): " + ("x" * 100)

        result = wrap_commit._reflow_block(
            [long_subject],
            80,
            add_backticks=True,
        )

        assert result == [long_subject]

    def test_remaining_lines_still_reflowed_after_subject(self) -> None:
        """Lines after the subject still go through the normal reflow."""
        result = wrap_commit._reflow_block(
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
        result = wrap_commit._reflow_block(
            ["use foo_bar here"],
            80,
            add_backticks=True,
        )

        assert result == ["use `foo_bar` here"]

    def test_empty_block_returns_empty_list(self) -> None:
        """An empty block produces no output."""
        assert wrap_commit._reflow_block([], 80, add_backticks=True) == []


class TestProcessTextSubjectSkip:
    """Validate that ``process_text`` preserves block-leading commit subjects."""

    def test_block_with_subject_keeps_subject_verbatim(self) -> None:
        """The subject line inside a block is preserved through ``process_text``."""
        text = (
            "```log\n"
            "feat(tools): add cert-aware uv launcher\n"
            "\n"
            "Use foo_bar today\n"
            "```\n"
        )

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert "feat(tools): add cert-aware uv launcher" in result
        assert "`feat(tools):`" not in result
        # The non-subject content still gets the backtick pass.
        assert "`foo_bar`" in result

    def test_subject_match_only_applies_to_first_line_of_block(self) -> None:
        """A second subject-shaped line inside the block is still backticked."""
        text = (
            "```log\n"
            "feat(tools): one\n"
            "fix(io): two\n"
            "```\n"
        )

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert "feat(tools): one" in result
        # ``fix(io):`` is not first, so the open-paren rule kicks in;
        # the trailing colon sits outside the closing backtick.
        assert "`fix(io)`: two" in result

    def test_overlong_subject_line_is_not_wrapped(self) -> None:
        """An overlong subject line is preserved verbatim even past the width."""
        long_subject = "feat(tools): " + " ".join(["word"] * 30)
        text = f"```log\n{long_subject}\n```\n"

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert long_subject in result

    def test_unterminated_block_still_preserves_subject(self) -> None:
        """An unterminated block at EOF also preserves the subject line."""
        text = (
            "```log\n"
            "feat(tools): add foo_bar\n"
            "more content here\n"
        )

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert "feat(tools): add foo_bar" in result

    def test_no_delimiters_mode_does_not_apply_subject_skip(self) -> None:
        """``--no-delimiters`` mode skips the subject-line rule."""
        text = "feat(tools): add cert-aware uv launcher\n"

        result = wrap_commit.process_text(text, 80, None, None)

        # Without delimiters there is no "block", so the subject line
        # is processed normally and the open-paren rule wraps it; the
        # trailing colon sits outside the closing backtick.
        assert "`feat(tools)`: add" in result

    def test_subject_skip_works_with_no_backticks_flag(self) -> None:
        """``add_backticks=False`` still keeps the subject line verbatim."""
        text = (
            "```log\n"
            "feat(tools): xxx foo_bar\n"
            "more foo_bar\n"
            "```\n"
        )

        result = wrap_commit.process_text(
            text, 80, "```log", "```", add_backticks=False,
        )

        assert "feat(tools): xxx foo_bar" in result
        # Content lines have no backticks added either, by the flag.
        assert "`foo_bar`" not in result


class TestAddBackticksToLiterals:
    """Validate the wrap-list literal backticking pass."""

    def test_no_literals_leaves_text_unchanged(self) -> None:
        """An empty literal list returns the text verbatim."""
        assert wrap_commit._add_backticks_to_literals("foo bar", []) == "foo bar"

    def test_single_word_literal_is_wrapped(self) -> None:
        """A configured single-word literal gets backticked."""
        assert wrap_commit._add_backticks_to_literals(
            "please optimize this",
            ["optimize"],
        ) == "please `optimize` this"

    def test_multi_word_literal_is_wrapped_as_one_span(self) -> None:
        """A multi-word literal is wrapped as a single span."""
        assert wrap_commit._add_backticks_to_literals(
            "we make better cars",
            ["make better"],
        ) == "we `make better` cars"

    def test_literal_inside_larger_word_is_not_matched(self) -> None:
        """A literal embedded in a larger word is left alone."""
        # ``cat`` must not match inside ``concatenate``.
        assert wrap_commit._add_backticks_to_literals(
            "concatenate the cat",
            ["cat"],
        ) == "concatenate the `cat`"

    def test_literal_already_in_backtick_zone_is_skipped(self) -> None:
        """An occurrence already inside a backtick span is not re-wrapped."""
        assert wrap_commit._add_backticks_to_literals(
            "use `foo` and foo",
            ["foo"],
        ) == "use `foo` and `foo`"

    def test_longer_literal_wins_over_shorter_substring(self) -> None:
        """A multi-word literal is wrapped before a shorter overlapping one."""
        # ``del .testmondata`` is wrapped first; the standalone ``del``
        # literal then only matches the separate trailing ``del``.
        assert wrap_commit._add_backticks_to_literals(
            "run del .testmondata then del",
            ["del", "del .testmondata"],
        ) == "run `del .testmondata` then `del`"

    def test_literal_with_punctuation_keeps_punct_outside(self) -> None:
        """Trailing punctuation stays outside the wrapped literal."""
        assert wrap_commit._add_backticks_to_literals(
            "edit a.commit, then go",
            ["a.commit"],
        ) == "edit `a.commit`, then go"

    def test_blank_literal_entries_are_ignored(self) -> None:
        """Empty-string literals wrap nothing."""
        assert wrap_commit._add_backticks_to_literals(
            "leave it be",
            [""],
        ) == "leave it be"


class TestApplyInlineBackticks:
    """Validate the combined wrap-list, code-like, and merge pass."""

    def test_add_backticks_false_returns_text_unchanged(self) -> None:
        """With backticks off, the segment is returned verbatim."""
        assert wrap_commit._apply_inline_backticks(
            "use foo_bar and make better",
            add_backticks=False,
            literals=["make better"],
        ) == "use foo_bar and make better"

    def test_runs_literal_then_code_then_merge(self) -> None:
        """Literals and code-like tokens are wrapped, then spans merge."""
        # ``--a`` and ``--b`` are code-like and adjacent, so they merge;
        # ``make better`` is wrapped from the wrap-list.
        assert wrap_commit._apply_inline_backticks(
            "run --a --b for make better",
            add_backticks=True,
            literals=["make better"],
        ) == "run `--a --b` for `make better`"

    def test_paragraph_predicate_wraps_slash_word(self) -> None:
        """The paragraph predicate backticks a path-separator word."""
        assert wrap_commit._apply_inline_backticks(
            "see a/b now",
            add_backticks=True,
            literals=[],
            needs_backticks=wrap_commit._word_needs_backticks_in_paragraph,
        ) == "see `a/b` now"


class TestWrapListSearchDirs:
    """Validate the wrap-list directory search order and de-duplication."""

    def test_includes_tool_calling_root_and_home_in_order(
        self,
        tmp_path: Path,
    ) -> None:
        """The four roles appear in tool, calling, root, home order."""
        tool = tmp_path / "tool"
        root = tmp_path / "proj"
        sub = root / "a" / "b"
        home = tmp_path / "home"
        for directory in (tool, sub, home):
            directory.mkdir(parents=True)

        dirs = wrap_commit._wrap_list_search_dirs(tool, sub, root, home)

        assert dirs[0] == tool
        assert dirs[1] == sub
        assert root in dirs
        assert dirs[-1] == home
        # The walk from sub stops at root: nothing above root is scanned.
        assert root.parent not in dirs

    def test_deduplicates_repeated_roles(self, tmp_path: Path) -> None:
        """A directory that plays several roles is listed once."""
        only = tmp_path / "only"
        only.mkdir()

        dirs = wrap_commit._wrap_list_search_dirs(only, only, only, only)

        assert dirs == [only]

    def test_walk_stops_at_filesystem_root_when_root_not_ancestor(
        self,
        tmp_path: Path,
    ) -> None:
        """When the project root is not an ancestor, the walk reaches fs root."""
        start = tmp_path / "x" / "y"
        start.mkdir(parents=True)
        unrelated_root = tmp_path / "other"
        unrelated_root.mkdir()
        home = tmp_path / "home"
        home.mkdir()

        dirs = wrap_commit._wrap_list_search_dirs(
            tmp_path / "tool",
            start,
            unrelated_root,
            home,
        )

        # The walk climbed all the way to the filesystem root.
        anchor = start
        while anchor != anchor.parent:
            anchor = anchor.parent
        assert anchor in dirs


class TestLoadWrapListLiterals:
    """Validate reading ``wrap-list.backtick`` files across directories."""

    def test_missing_files_yield_no_literals(self, tmp_path: Path) -> None:
        """Directories without the file contribute nothing."""
        assert wrap_commit._load_wrap_list_literals([tmp_path]) == []

    def test_reads_non_blank_lines_as_literals(self, tmp_path: Path) -> None:
        """Each non-blank, stripped line becomes one literal."""
        (tmp_path / wrap_commit.WRAP_LIST_FILE_NAME).write_text(
            "make better\n\n  know your fleet  \n",
            encoding="utf-8",
        )

        assert wrap_commit._load_wrap_list_literals([tmp_path]) == [
            "make better",
            "know your fleet",
        ]

    def test_concatenates_across_directories_in_order(
        self,
        tmp_path: Path,
    ) -> None:
        """Literals from several files are concatenated in directory order."""
        first = tmp_path / "first"
        second = tmp_path / "second"
        first.mkdir()
        second.mkdir()
        (first / wrap_commit.WRAP_LIST_FILE_NAME).write_text(
            "alpha\n", encoding="utf-8",
        )
        (second / wrap_commit.WRAP_LIST_FILE_NAME).write_text(
            "beta\n", encoding="utf-8",
        )

        assert wrap_commit._load_wrap_list_literals([first, second]) == [
            "alpha",
            "beta",
        ]

    def test_unreadable_file_is_skipped(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A file that raises OSError on read is skipped, not fatal."""
        (tmp_path / wrap_commit.WRAP_LIST_FILE_NAME).write_text(
            "x\n", encoding="utf-8",
        )

        def boom(*_args: object, **_kwargs: object) -> str:
            raise OSError

        monkeypatch.setattr(wrap_commit.Path, "read_text", boom)

        assert wrap_commit._load_wrap_list_literals([tmp_path]) == []

    def test_directory_named_like_file_is_skipped(self, tmp_path: Path) -> None:
        """A ``wrap-list.backtick`` that is a directory is not read."""
        (tmp_path / wrap_commit.WRAP_LIST_FILE_NAME).mkdir()

        assert wrap_commit._load_wrap_list_literals([tmp_path]) == []


class TestCollectWrapListLiterals:
    """Validate the wrap-list collector across the search roots."""

    def test_collects_from_start_dir_when_root_resolves(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A wrap-list in the calling folder is collected."""
        (tmp_path / wrap_commit.WRAP_LIST_FILE_NAME).write_text(
            "frobnicate widget\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(wrap_commit, "find_project_root", lambda _s: tmp_path)
        # Point HOME at an empty folder so the real home is not scanned.
        monkeypatch.setenv("HOME", str(tmp_path / "empty_home"))

        result = _REAL_COLLECT_WRAP_LIST_LITERALS(tmp_path)

        assert "frobnicate widget" in result

    def test_falls_back_when_project_root_not_found(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A missing project root falls back to the calling folder."""
        (tmp_path / wrap_commit.WRAP_LIST_FILE_NAME).write_text(
            "frobnicate gadget\n",
            encoding="utf-8",
        )

        def no_root(_s: Path) -> Path:
            raise FileNotFoundError

        monkeypatch.setattr(wrap_commit, "find_project_root", no_root)
        monkeypatch.setenv("HOME", str(tmp_path / "empty_home"))

        result = _REAL_COLLECT_WRAP_LIST_LITERALS(tmp_path)

        assert "frobnicate gadget" in result

    def test_reads_the_home_env_folder(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The ``HOME`` env folder is scanned, matching ``%HOME%``/``$HOME``."""
        home = tmp_path / "myhome"
        home.mkdir()
        (home / wrap_commit.WRAP_LIST_FILE_NAME).write_text(
            "frobnicate from home\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setattr(wrap_commit, "find_project_root", lambda _s: tmp_path)

        result = _REAL_COLLECT_WRAP_LIST_LITERALS(tmp_path)

        assert "frobnicate from home" in result

    def test_uses_os_home_when_home_env_unset(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """With ``HOME`` unset, the OS home (``Path.home()``) is used."""
        fake_home = tmp_path / "oshome"
        fake_home.mkdir()
        (fake_home / wrap_commit.WRAP_LIST_FILE_NAME).write_text(
            "frobnicate os home\n",
            encoding="utf-8",
        )
        monkeypatch.delenv("HOME", raising=False)
        monkeypatch.setattr(
            wrap_commit.Path, "home", classmethod(lambda _cls: fake_home),
        )
        monkeypatch.setattr(wrap_commit, "find_project_root", lambda _s: tmp_path)

        result = _REAL_COLLECT_WRAP_LIST_LITERALS(tmp_path)

        assert "frobnicate os home" in result


class TestReflowLinesWrapList:
    """Validate wrap-list literals flowing through ``reflow_lines``."""

    def test_paragraph_literal_is_backticked(self) -> None:
        """A configured literal in a paragraph is wrapped."""
        assert wrap_commit.reflow_lines(
            ["we make better cars today"],
            80,
            literals=["make better"],
        ) == ["we `make better` cars today"]

    def test_bullet_literal_is_backticked(self) -> None:
        """A configured literal in a bullet is wrapped too."""
        assert wrap_commit.reflow_lines(
            ["- we make better cars"],
            80,
            literals=["make better"],
        ) == ["- we `make better` cars"]

    def test_no_backticks_flag_skips_literals(self) -> None:
        """With backticks off, wrap-list literals are left alone."""
        assert wrap_commit.reflow_lines(
            ["we make better cars"],
            80,
            add_backticks=False,
            literals=["make better"],
        ) == ["we make better cars"]

    def test_no_literals_matches_prior_behaviour(self) -> None:
        """Without literals, output matches the no-wrap-list behaviour."""
        assert wrap_commit.reflow_lines(
            ["we make better cars"],
            80,
        ) == ["we make better cars"]


class TestProcessTextWrapList:
    """Validate wrap-list literals applied to block bodies only."""

    def test_literal_wrapped_in_body_not_in_subject(self) -> None:
        """A literal is backticked in the body but never in the subject."""
        text = (
            "```log\n"
            "feat(x): make better today\n"
            "\n"
            "we make better cars\n"
            "```\n"
        )

        result = wrap_commit.process_text(
            text,
            80,
            "```log",
            "```",
            literals=["make better"],
        )

        assert "feat(x): make better today" in result
        assert "we `make better` cars" in result

    def test_no_literals_leaves_block_unchanged(self) -> None:
        """Without literals the block body keeps its plain words."""
        text = "```log\nwe make better cars\n```\n"

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert result == "```log\nwe make better cars\n```\n"


class TestMainWrapList:
    """Validate ``main`` applies collected wrap-list literals."""

    def test_main_applies_collected_literals(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Literals from the collector are backticked in the body."""
        target = tmp_path / "custom.txt"
        target.write_text(
            "```log\nwe make better cars\n```\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(
            wrap_commit,
            "_collect_wrap_list_literals",
            lambda _s: ["make better"],
        )

        exit_code = wrap_commit.main(["--file", str(target)])

        assert exit_code == 0
        assert target.read_text(encoding="utf-8") == (
            "```log\nwe `make better` cars\n```\n"
        )


class TestWordHasPathSeparator:
    """Validate the path-separator word predicate."""

    def test_forward_slash_word_qualifies(self) -> None:
        """A word with a forward slash and other chars qualifies."""
        assert wrap_commit._word_has_path_separator("src/pdfss")

    def test_backslash_word_qualifies(self) -> None:
        """A word with a backslash and other chars qualifies."""
        assert wrap_commit._word_has_path_separator(r"C:\Users\vonc")

    def test_and_or_qualifies(self) -> None:
        """A prose token like ``and/or`` qualifies."""
        assert wrap_commit._word_has_path_separator("and/or")

    def test_bare_forward_slash_does_not_qualify(self) -> None:
        """A lone ``/`` separator stays bare."""
        assert not wrap_commit._word_has_path_separator("/")

    def test_bare_backslash_does_not_qualify(self) -> None:
        r"""A lone ``\`` separator stays bare."""
        assert not wrap_commit._word_has_path_separator("\\")

    def test_repeated_separators_do_not_qualify(self) -> None:
        """Runs made only of separators stay bare."""
        assert not wrap_commit._word_has_path_separator("//")
        assert not wrap_commit._word_has_path_separator("\\\\")

    def test_plain_word_does_not_qualify(self) -> None:
        """A word without a separator does not qualify."""
        assert not wrap_commit._word_has_path_separator("paragraph")


class TestWordNeedsBackticksInParagraph:
    """Validate the paragraph predicate (code-like plus path-separator)."""

    def test_code_like_word_qualifies(self) -> None:
        """A code-like word qualifies via the regular rules."""
        assert wrap_commit._word_needs_backticks_in_paragraph("foo_bar")

    def test_path_separator_word_qualifies(self) -> None:
        """A slash word qualifies via the path-separator rule."""
        assert wrap_commit._word_needs_backticks_in_paragraph("src/pdfss")

    def test_plain_word_does_not_qualify(self) -> None:
        """A plain word qualifies under neither rule."""
        assert not wrap_commit._word_needs_backticks_in_paragraph("paragraph")


class TestAddBackticksToWordsPredicate:
    """Validate the custom-predicate form of the word backticker."""

    def test_default_predicate_is_code_like(self) -> None:
        """With no predicate, the code-like rules apply."""
        assert wrap_commit._add_backticks_to_words(
            "use foo_bar",
        ) == "use `foo_bar`"

    def test_path_predicate_wraps_slash_words(self) -> None:
        """A custom predicate can target path-separator words."""
        assert wrap_commit._add_backticks_to_words(
            "see src/pdfss here",
            wrap_commit._word_has_path_separator,
        ) == "see `src/pdfss` here"

    def test_path_predicate_leaves_plain_words(self) -> None:
        """A custom predicate leaves non-matching words alone."""
        assert wrap_commit._add_backticks_to_words(
            "plain words here",
            wrap_commit._word_has_path_separator,
        ) == "plain words here"


class TestReflowLinesPathSeparator:
    """Validate the paragraph-only path-separator backticking."""

    def test_paragraph_wraps_forward_slash_word(self) -> None:
        """A paragraph backticks a forward-slash path word."""
        assert wrap_commit.reflow_lines(
            ["edit src/pdfss/tests today"],
            80,
        ) == ["edit `src/pdfss/tests` today"]

    def test_paragraph_wraps_backslash_word(self) -> None:
        """A paragraph backticks a backslash path word."""
        assert wrap_commit.reflow_lines(
            [r"open C:\Users\vonc now"],
            80,
        ) == [r"open `C:\Users\vonc` now"]

    def test_bullet_does_not_wrap_slash_word(self) -> None:
        """The item list keeps the regular rules, so a slash word stays bare."""
        assert wrap_commit.reflow_lines(
            ["- edit src/pdfss/tests today"],
            80,
        ) == ["- edit src/pdfss/tests today"]

    def test_no_backticks_flag_skips_the_slash_rule(self) -> None:
        """With backticks off, slash words are left alone."""
        assert wrap_commit.reflow_lines(
            ["edit src/pdfss/tests today"],
            80,
            add_backticks=False,
        ) == ["edit src/pdfss/tests today"]

    def test_slash_word_already_in_span_is_not_rewrapped(self) -> None:
        """A slash word already inside a span is left as-is."""
        assert wrap_commit.reflow_lines(
            ["edit `src/pdfss` today"],
            80,
        ) == ["edit `src/pdfss` today"]

    def test_slash_words_merge_after_wrapping(self) -> None:
        """Adjacent slash words wrap, then the merge folds them into one span."""
        assert wrap_commit.reflow_lines(
            ["paths a/b c/d here"],
            80,
        ) == ["paths `a/b c/d` here"]


class TestScriptExecution:
    """Validate the ``__main__`` script entry point."""

    def test_script_runs_as_main_and_exits_zero_on_success(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Running the script end to end rewrites the target file and exits 0."""
        commit_file = tmp_path / wrap_commit.DEFAULT_FILE_NAME
        commit_file.write_text(
            "```log\nfoo bar baz\n```\n",
            encoding="utf-8",
        )
        (tmp_path / ".git").mkdir()
        monkeypatch.setenv("PRJ_DIR", str(tmp_path))
        monkeypatch.setattr(sys, "argv", ["wrap_commit.py"])

        with pytest.raises(SystemExit) as excinfo:
            runpy.run_path(wrap_commit.__file__, run_name="__main__")

        assert excinfo.value.code == 0

    def test_script_logs_fatal_when_main_raises(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """A ``WrapCommitError`` raised by ``main`` produces exit code 2."""
        missing = tmp_path / "missing.txt"
        monkeypatch.setattr(sys, "argv", ["wrap_commit.py", "--file", str(missing)])
        caplog.set_level(logging.ERROR)

        with pytest.raises(SystemExit) as excinfo:
            runpy.run_path(wrap_commit.__file__, run_name="__main__")

        assert excinfo.value.code == _EXIT_FATAL


# eof
