"""Tests for the backtick passes of the commit-text width enforcer.

Cover ``tools.wrap_commit_backticks`` at the text level -- the
whole-text backtick-wrap pass, the adjacent backtick-span merge that
folds a whitespace-separated run of code spans into one span, the
wrap-list literal pass, the combined wrap-list/code-like/merge segment
pass, and the subject-wrap backtick stripper that bares a backticked
``type(scope):`` line opener -- plus ``tools.wrap_commit_wraplist``:
the directory
search order, the ``wrap-list.backtick`` reader, and the collector
across the search roots.

The collector resolves the project root through the shared
``find_project_root`` helper; the relevant tests pin that resolution
with ``monkeypatch`` so they never depend on the real checkout.

Fix: split for the repo line budget -- the word-rule classes moved to
``test_wrap_commit_words.py``, the reflow classes to
``test_wrap_commit_reflow.py``, and the driver plus CLI classes to
``test_wrap_commit_cli.py``; the targets now live in the split
``tools.wrap_commit_backticks`` and ``tools.wrap_commit_wraplist``
modules, so the collector tests reach the real function directly and
no longer need to capture it ahead of an autouse neutralizer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.unit.tools.wrap_commit_test_support import fixed_project_root
from tools import wrap_commit_backticks, wrap_commit_wraplist

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001


class TestAddBackticksToWords:
    """Validate the whole-text backtick-wrap pass."""

    def test_no_matching_words_leaves_text_unchanged(self) -> None:
        """A plain sentence with no rule hits is returned verbatim."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "foo bar baz",
        ) == "foo bar baz"

    def test_wraps_an_underscore_word(self) -> None:
        """A bare ``foo_bar`` token is wrapped in backticks."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "use foo_bar here",
        ) == "use `foo_bar` here"

    def test_wraps_a_dot_word(self) -> None:
        """A bare ``senv.bat`` token is wrapped in backticks."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "edit senv.bat now",
        ) == "edit `senv.bat` now"

    def test_wraps_a_camelcase_word(self) -> None:
        """A two-uppercase token is wrapped in backticks."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "the PyPI mirror",
        ) == "the `PyPI` mirror"

    def test_skips_word_already_in_backtick_region(self) -> None:
        """An already-backticked code span is not double-wrapped."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "use `foo_bar` here",
        ) == "use `foo_bar` here"

    def test_skips_word_overlapping_a_backtick_region(self) -> None:
        """A token that touches a backtick span is left alone."""
        # ``use_`foo` `` overlaps the backtick span around ``foo`` so it
        # must not get a second backtick pair around the whole token.
        assert wrap_commit_backticks._add_backticks_to_words(
            "use_`foo`",
        ) == "use_`foo`"

    def test_skips_sentence_ending_word(self) -> None:
        """``machines.`` is sentence punctuation and stays bare."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "satisfy both machines.",
        ) == "satisfy both machines."

    def test_preserves_whitespace_runs(self) -> None:
        """Multi-space runs between tokens are preserved verbatim."""
        assert wrap_commit_backticks._add_backticks_to_words("a  b") == "a  b"

    def test_combines_multiple_matches_in_one_pass(self) -> None:
        """Every matching token in one string is wrapped in one pass."""
        result = wrap_commit_backticks._add_backticks_to_words(
            "use foo_bar and senv.bat with PyPI",
        )

        assert result == "use `foo_bar` and `senv.bat` with `PyPI`"

    def test_skips_acronym_with_trailing_close_paren(self) -> None:
        """A token like ``PBT)`` is a prose acronym; it is not wrapped."""
        result = wrap_commit_backticks._add_backticks_to_words(
            "tested with PBT) for safety",
        )

        assert result == "tested with PBT) for safety"

    def test_trailing_colon_kept_outside_backticks(self) -> None:
        r"""``foo_bar:`` wraps as ``\`foo_bar\`:`` with the colon outside."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "set foo_bar: value",
        ) == "set `foo_bar`: value"

    def test_trailing_comma_kept_outside_backticks(self) -> None:
        """``foo_bar,`` keeps the comma outside the closing backtick."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "use foo_bar, then baz",
        ) == "use `foo_bar`, then baz"

    def test_trailing_semicolon_kept_outside_backticks(self) -> None:
        """``foo_bar;`` keeps the semicolon outside."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "first foo_bar; then",
        ) == "first `foo_bar`; then"

    def test_trailing_period_kept_outside_backticks(self) -> None:
        """``foo_bar.`` keeps the period outside the closing backtick."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "use foo_bar.",
        ) == "use `foo_bar`."

    def test_multiple_trailing_punct_chars_all_go_outside(self) -> None:
        """A run of trailing punctuation is fully extracted outside."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "see foo_bar.,",
        ) == "see `foo_bar`.,"

    def test_unbalanced_trailing_close_paren_is_moved_outside(self) -> None:
        r"""``foo_bar)`` wraps as ``\`foo_bar\`)`` -- lone ``)`` goes outside."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "wrap foo_bar) here",
        ) == "wrap `foo_bar`) here"

    def test_balanced_close_paren_stays_inside_the_backticks(self) -> None:
        """``foo(bar)`` keeps both parens inside -- the parens are balanced."""
        # ``foo(bar)`` qualifies via the open-paren rule; the trailing
        # ``)`` matches the ``(`` so it stays inside the backticks.
        assert wrap_commit_backticks._add_backticks_to_words(
            "call foo(bar) here",
        ) == "call `foo(bar)` here"

    def test_unbalanced_leading_open_paren_is_moved_outside(self) -> None:
        r"""``(FlagValidationStatus,`` wraps as ``(\`FlagValidationStatus\`,``."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "see (FlagValidationStatus, here",
        ) == "see (`FlagValidationStatus`, here"

    def test_balanced_leading_open_paren_stays_inside(self) -> None:
        """``(foo_bar)`` keeps both parens inside -- they are balanced."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "see (foo_bar) here",
        ) == "see `(foo_bar)` here"

    def test_question_mark_stays_inside(self) -> None:
        """``?`` is neither sentence-trailing nor a paren -- stays inside."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "is foo_bar? maybe",
        ) == "is `foo_bar?` maybe"

    def test_typed_scoped_subject_in_paragraph_keeps_colon_outside(self) -> None:
        r"""``feat(tools):`` wraps as ``\`feat(tools)\`:`` in paragraph text."""
        # The parens are balanced so they stay inside; only the
        # trailing ``:`` is extracted.
        assert wrap_commit_backticks._add_backticks_to_words(
            "the feat(tools): commit",
        ) == "the `feat(tools)`: commit"

    def test_version_literal_is_not_wrapped(self) -> None:
        """``v1.0`` and ``v2.5.3`` stay bare in paragraph text."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "ship v1.0 today and v2.5.3 next",
        ) == "ship v1.0 today and v2.5.3 next"

    def test_big_o_notation_is_not_wrapped(self) -> None:
        """``O(n)`` and ``o(log n)`` stay bare in paragraph text."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "complexity is O(n) here and o(log) there",
        ) == "complexity is O(n) here and o(log) there"

    def test_dash_prefixed_long_option_is_wrapped(self) -> None:
        """``--no-backticks`` wraps via the dash-prefix rule."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "pass --no-backticks today",
        ) == "pass `--no-backticks` today"

    def test_dash_prefixed_short_option_is_wrapped(self) -> None:
        """``-x`` also wraps -- one dash plus non-dash content qualifies."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "pass -x today",
        ) == "pass `-x` today"

    def test_bare_dash_separators_are_not_wrapped(self) -> None:
        """``-``, ``--``, ``---`` are bare separators and stay unwrapped."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "before -- after --- end",
        ) == "before -- after --- end"

    def test_equals_assignment_is_wrapped(self) -> None:
        """``KEY=value`` wraps via the ``=`` rule."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "set KEY=value here",
        ) == "set `KEY=value` here"

    def test_long_option_with_equals_is_wrapped_once(self) -> None:
        """``--width=80`` wraps as a single backticked token."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "use --width=80 now",
        ) == "use `--width=80` now"

    def test_bare_equals_operator_is_not_wrapped(self) -> None:
        """``a == b`` and ``a = b`` keep the bare operator unwrapped."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "check a == b here",
        ) == "check a == b here"
        assert wrap_commit_backticks._add_backticks_to_words(
            "set a = b now",
        ) == "set a = b now"

    def test_bare_underscore_placeholder_is_not_wrapped(self) -> None:
        """A bare ``_`` token (Python ignore placeholder) is not wrapped."""
        assert wrap_commit_backticks._add_backticks_to_words(
            "use _ for ignored",
        ) == "use _ for ignored"

    def test_degenerate_all_punctuation_token_is_left_alone(self) -> None:
        """An all-outer-punctuation token has nothing to wrap; it stays bare.

        ``.,`` qualifies under the ``.`` not-at-end rule (the leading
        dot is not the last char), but stripping the trailing run
        leaves an empty core, so the helper falls back to emitting the
        token unchanged.
        """
        assert wrap_commit_backticks._add_backticks_to_words("a .,") == "a .,"


class TestMergeAdjacentBacktickSpans:
    """Validate the adjacent backtick-span merge helper."""

    def test_text_without_spans_is_unchanged(self) -> None:
        """Plain text with no backtick spans is returned verbatim."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "foo bar baz",
        ) == "foo bar baz"

    def test_single_span_is_unchanged(self) -> None:
        """A lone backtick span has nothing to merge."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "use `foo` here",
        ) == "use `foo` here"

    def test_two_spans_one_space_merge(self) -> None:
        """Two spans separated by one space fold into one span."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "`a` `b`",
        ) == "`a b`"

    def test_three_spans_collapse_to_one(self) -> None:
        """A run of three spans collapses in the fixpoint loop."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "`zone 1` `zone 2` `zone 3`",
        ) == "`zone 1 zone 2 zone 3`"

    def test_spans_with_prose_between_do_not_merge(self) -> None:
        """Spans with words between them are left apart."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "`a` and `b`",
        ) == "`a` and `b`"

    def test_spans_across_single_newline_merge(self) -> None:
        """A span pair split across one newline with indent merges."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "`--no-cov`\n  `-rxX`",
        ) == "`--no-cov -rxX`"

    def test_spans_across_blank_line_do_not_merge(self) -> None:
        """A blank line (paragraph break) keeps the spans apart."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "`a`\n\n`b`",
        ) == "`a`\n\n`b`"

    def test_spans_across_bullet_marker_do_not_merge(self) -> None:
        """A following ``- `` bullet marker keeps the spans apart."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "`a`\n- `b`",
        ) == "`a`\n- `b`"

    def test_tab_between_spans_merges(self) -> None:
        """A tab counts as inter-span whitespace and merges."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "`a`\t`b`",
        ) == "`a b`"

    def test_directly_adjacent_spans_do_not_merge(self) -> None:
        """Spans with no whitespace between them stay as-is."""
        # ``\`a\`\`b\``` has no separator, so the rule (which needs
        # inter-span whitespace) does not fire.
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "`a``b`",
        ) == "`a``b`"

    def test_surrounding_prose_is_preserved(self) -> None:
        """Prose around a merged run stays intact."""
        assert wrap_commit_backticks._merge_adjacent_backtick_spans(
            "run `--a` `--b` now",
        ) == "run `--a --b` now"


class TestAddBackticksToLiterals:
    """Validate the wrap-list literal backticking pass."""

    def test_no_literals_leaves_text_unchanged(self) -> None:
        """An empty literal list returns the text verbatim."""
        assert wrap_commit_backticks._add_backticks_to_literals(
            "foo bar",
            [],
        ) == "foo bar"

    def test_single_word_literal_is_wrapped(self) -> None:
        """A configured single-word literal gets backticked."""
        assert wrap_commit_backticks._add_backticks_to_literals(
            "please optimize this",
            ["optimize"],
        ) == "please `optimize` this"

    def test_multi_word_literal_is_wrapped_as_one_span(self) -> None:
        """A multi-word literal is wrapped as a single span."""
        assert wrap_commit_backticks._add_backticks_to_literals(
            "we make better cars",
            ["make better"],
        ) == "we `make better` cars"

    def test_literal_inside_larger_word_is_not_matched(self) -> None:
        """A literal embedded in a larger word is left alone."""
        # ``cat`` must not match inside ``concatenate``.
        assert wrap_commit_backticks._add_backticks_to_literals(
            "concatenate the cat",
            ["cat"],
        ) == "concatenate the `cat`"

    def test_literal_already_in_backtick_zone_is_skipped(self) -> None:
        """An occurrence already inside a backtick span is not re-wrapped."""
        assert wrap_commit_backticks._add_backticks_to_literals(
            "use `foo` and foo",
            ["foo"],
        ) == "use `foo` and `foo`"

    def test_longer_literal_wins_over_shorter_substring(self) -> None:
        """A multi-word literal is wrapped before a shorter overlapping one."""
        # ``del .testmondata`` is wrapped first; the standalone ``del``
        # literal then only matches the separate trailing ``del``.
        assert wrap_commit_backticks._add_backticks_to_literals(
            "run del .testmondata then del",
            ["del", "del .testmondata"],
        ) == "run `del .testmondata` then `del`"

    def test_literal_with_punctuation_keeps_punct_outside(self) -> None:
        """Trailing punctuation stays outside the wrapped literal."""
        assert wrap_commit_backticks._add_backticks_to_literals(
            "edit a.commit, then go",
            ["a.commit"],
        ) == "edit `a.commit`, then go"

    def test_blank_literal_entries_are_ignored(self) -> None:
        """Empty-string literals wrap nothing."""
        assert wrap_commit_backticks._add_backticks_to_literals(
            "leave it be",
            [""],
        ) == "leave it be"


class TestApplyInlineBackticks:
    """Validate the combined wrap-list, code-like, and merge pass."""

    def test_add_backticks_false_returns_text_unchanged(self) -> None:
        """With backticks off, the segment is returned verbatim."""
        assert wrap_commit_backticks.apply_inline_backticks(
            "use foo_bar and make better",
            add_backticks=False,
            literals=["make better"],
        ) == "use foo_bar and make better"

    def test_runs_literal_then_code_then_merge(self) -> None:
        """Literals and code-like tokens are wrapped, then spans merge."""
        # ``--a`` and ``--b`` are code-like and adjacent, so they merge;
        # ``make better`` is wrapped from the wrap-list.
        assert wrap_commit_backticks.apply_inline_backticks(
            "run --a --b for make better",
            add_backticks=True,
            literals=["make better"],
        ) == "run `--a --b` for `make better`"

    def test_paragraph_predicate_wraps_slash_word(self) -> None:
        """The paragraph predicate backticks a path-separator word."""
        assert wrap_commit_backticks.apply_inline_backticks(
            "see a/b now",
            add_backticks=True,
            literals=[],
            needs_backticks=wrap_commit_backticks.word_needs_backticks_in_paragraph,
        ) == "see `a/b` now"


class TestStripSubjectWrapBackticks:
    r"""Validate the ``\`type(scope)\`:`` opener backtick stripper."""

    def test_strips_wrapped_subject_opener(self) -> None:
        r"""``\`feat(tools)\`: rest`` loses the two wrap backticks."""
        assert wrap_commit_backticks.strip_subject_wrap_backticks(
            "`feat(tools)`: add launcher",
        ) == "feat(tools): add launcher"

    def test_keeps_rest_of_line_after_colon(self) -> None:
        """Only the two backticks go; text after the colon is untouched."""
        assert wrap_commit_backticks.strip_subject_wrap_backticks(
            "`fix(io)`: two `still_code` here",
        ) == "fix(io): two `still_code` here"

    def test_non_opener_match_is_left_alone(self) -> None:
        """A backticked subject mid-line (not at the start) is not stripped."""
        assert wrap_commit_backticks.strip_subject_wrap_backticks(
            "the `feat(tools)`: commit",
        ) == "the `feat(tools)`: commit"

    def test_bullet_line_is_not_stripped(self) -> None:
        """A ``- `` bullet opener does not match the line-start pattern."""
        assert wrap_commit_backticks.strip_subject_wrap_backticks(
            "- `feat(tools)`: add launcher",
        ) == "- `feat(tools)`: add launcher"

    def test_indented_line_is_not_stripped(self) -> None:
        """Leading whitespace breaks the ``^`` anchor, so nothing is stripped."""
        assert wrap_commit_backticks.strip_subject_wrap_backticks(
            "  `feat(tools)`: add launcher",
        ) == "  `feat(tools)`: add launcher"

    def test_bare_subject_without_backticks_is_unchanged(self) -> None:
        """An already-bare ``feat(tools):`` opener has nothing to strip."""
        assert wrap_commit_backticks.strip_subject_wrap_backticks(
            "feat(tools): add launcher",
        ) == "feat(tools): add launcher"

    def test_subject_without_scope_is_not_matched(self) -> None:
        r"""``\`feat\`:`` has no ``(scope)`` group, so it is left alone."""
        assert wrap_commit_backticks.strip_subject_wrap_backticks(
            "`feat`: no scope",
        ) == "`feat`: no scope"

    def test_pattern_matches_typed_scoped_opener(self) -> None:
        """The compiled pattern matches the wrapped opener at line start."""
        assert wrap_commit_backticks.SUBJECT_WRAP_BACKTICKS_PATTERN.match(
            "`feat(tools)`: rest",
        ) is not None


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

        dirs = wrap_commit_wraplist._wrap_list_search_dirs(tool, sub, root, home)

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

        dirs = wrap_commit_wraplist._wrap_list_search_dirs(only, only, only, only)

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

        dirs = wrap_commit_wraplist._wrap_list_search_dirs(
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
        assert wrap_commit_wraplist._load_wrap_list_literals([tmp_path]) == []

    def test_reads_non_blank_lines_as_literals(self, tmp_path: Path) -> None:
        """Each non-blank, stripped line becomes one literal."""
        (tmp_path / wrap_commit_wraplist.WRAP_LIST_FILE_NAME).write_text(
            "make better\n\n  know your fleet  \n",
            encoding="utf-8",
        )

        assert wrap_commit_wraplist._load_wrap_list_literals([tmp_path]) == [
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
        (first / wrap_commit_wraplist.WRAP_LIST_FILE_NAME).write_text(
            "alpha\n", encoding="utf-8",
        )
        (second / wrap_commit_wraplist.WRAP_LIST_FILE_NAME).write_text(
            "beta\n", encoding="utf-8",
        )

        assert wrap_commit_wraplist._load_wrap_list_literals([first, second]) == [
            "alpha",
            "beta",
        ]

    def test_unreadable_file_is_skipped(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A file that raises OSError on read is skipped, not fatal."""
        (tmp_path / wrap_commit_wraplist.WRAP_LIST_FILE_NAME).write_text(
            "x\n", encoding="utf-8",
        )

        def boom(*_args: object, **_kwargs: object) -> str:
            raise OSError

        monkeypatch.setattr(wrap_commit_wraplist.Path, "read_text", boom)

        assert wrap_commit_wraplist._load_wrap_list_literals([tmp_path]) == []

    def test_directory_named_like_file_is_skipped(self, tmp_path: Path) -> None:
        """A ``wrap-list.backtick`` that is a directory is not read."""
        (tmp_path / wrap_commit_wraplist.WRAP_LIST_FILE_NAME).mkdir()

        assert wrap_commit_wraplist._load_wrap_list_literals([tmp_path]) == []


class TestCollectWrapListLiterals:
    """Validate the wrap-list collector across the search roots."""

    def test_collects_from_start_dir_when_root_resolves(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A wrap-list in the calling folder is collected."""
        (tmp_path / wrap_commit_wraplist.WRAP_LIST_FILE_NAME).write_text(
            "frobnicate widget\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(
            wrap_commit_wraplist,
            "find_project_root",
            fixed_project_root(tmp_path),
        )
        # Point HOME at an empty folder so the real home is not scanned.
        monkeypatch.setenv("HOME", str(tmp_path / "empty_home"))

        result = wrap_commit_wraplist.collect_wrap_list_literals(tmp_path)

        assert "frobnicate widget" in result

    def test_falls_back_when_project_root_not_found(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A missing project root falls back to the calling folder."""
        (tmp_path / wrap_commit_wraplist.WRAP_LIST_FILE_NAME).write_text(
            "frobnicate gadget\n",
            encoding="utf-8",
        )

        def no_root(_s: Path) -> Path:
            raise FileNotFoundError

        monkeypatch.setattr(wrap_commit_wraplist, "find_project_root", no_root)
        monkeypatch.setenv("HOME", str(tmp_path / "empty_home"))

        result = wrap_commit_wraplist.collect_wrap_list_literals(tmp_path)

        assert "frobnicate gadget" in result

    def test_reads_the_home_env_folder(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The ``HOME`` env folder is scanned, matching ``%HOME%``/``$HOME``."""
        home = tmp_path / "myhome"
        home.mkdir()
        (home / wrap_commit_wraplist.WRAP_LIST_FILE_NAME).write_text(
            "frobnicate from home\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setattr(
            wrap_commit_wraplist,
            "find_project_root",
            fixed_project_root(tmp_path),
        )

        result = wrap_commit_wraplist.collect_wrap_list_literals(tmp_path)

        assert "frobnicate from home" in result

    def test_uses_os_home_when_home_env_unset(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """With ``HOME`` unset, the OS home (``Path.home()``) is used."""
        fake_home = tmp_path / "oshome"
        fake_home.mkdir()
        (fake_home / wrap_commit_wraplist.WRAP_LIST_FILE_NAME).write_text(
            "frobnicate os home\n",
            encoding="utf-8",
        )

        def fake_os_home() -> Path:
            """Return the test's stand-in OS home folder."""
            return fake_home

        monkeypatch.delenv("HOME", raising=False)
        monkeypatch.setattr(wrap_commit_wraplist.Path, "home", fake_os_home)
        monkeypatch.setattr(
            wrap_commit_wraplist,
            "find_project_root",
            fixed_project_root(tmp_path),
        )

        result = wrap_commit_wraplist.collect_wrap_list_literals(tmp_path)

        assert "frobnicate os home" in result


# eof
