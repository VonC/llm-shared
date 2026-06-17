"""Tests for the driver and CLI of the commit-text width enforcer.

Cover ``tools.wrap_commit`` as the script hub: the per-block and
whole-file ``process_text`` driver (including the block-leading commit
subject skip, the subject-wrap backtick strip on later subject lines,
and the wrap-list pass on block bodies), the target-file resolution, and
the CLI entry point in normal, ``--check``, and ``--no-delimiters``
modes. A ``runpy`` test exercises the ``__main__`` script path end to
end.

The tool resolves the default target file under the calling project's
root through the shared ``find_project_root`` helper; the relevant test
pins that resolution with ``monkeypatch`` so it never depends on the
real checkout.

Fix: split for the repo line budget -- the driver and CLI classes moved
here from ``test_wrap_commit.py``, which keeps the backtick-pass and
wrap-list config tests; the monkeypatch lambdas became typed helpers
from ``wrap_commit_test_support`` so pyright strict accepts the
``monkeypatch.setattr`` values.
"""

from __future__ import annotations

import logging
import runpy
import sys
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wrap_commit_test_support import (
    fixed_project_root,
    fixed_wrap_list_literals,
)
from tools import wrap_commit

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

_EXIT_CHANGES_PENDING = 1
_EXIT_FATAL = 2
_EXPECTED_BLOCK_COUNT = 2


@pytest.fixture(autouse=True)
def neutralize_ambient_wrap_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep ``main`` deterministic regardless of real wrap-list files.

    A ``wrap-list.backtick`` in the repo, the tool folder, or the user
    home would otherwise feed ``main`` and shift the exact-output
    assertions. The dedicated collector tests exercise the real function
    through ``tools.wrap_commit_wraplist`` directly, which this fixture
    leaves untouched.
    """
    monkeypatch.setattr(
        wrap_commit, "_collect_wrap_list_literals", fixed_wrap_list_literals([]),
    )


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
        """A second subject-shaped line is wrapped, then bared by the strip."""
        text = (
            "```log\n"
            "feat(tools): one\n"
            "fix(io): two\n"
            "```\n"
        )

        result = wrap_commit.process_text(text, 80, "```log", "```")

        assert "feat(tools): one" in result
        # ``fix(io):`` is not the first line, so the word pass wraps it
        # via the open-paren rule; the final subject-wrap strip then
        # removes the two backticks, leaving the opener bare.
        assert "fix(io): two" in result
        assert "`fix(io)`" not in result

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
        """``--no-delimiters`` skips the verbatim rule, but the strip still bares it."""
        text = "feat(tools): add cert-aware uv launcher\n"

        result = wrap_commit.process_text(text, 80, None, None)

        # Without delimiters there is no "block", so the verbatim
        # first-line rule never fires and the word pass wraps the opener
        # via the open-paren rule. The final subject-wrap strip then
        # removes the two backticks, so the subject reads bare.
        assert "feat(tools): add cert-aware uv launcher" in result
        assert "`feat(tools)`" not in result

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
        monkeypatch.setattr(
            wrap_commit, "find_project_root", fixed_project_root(tmp_path),
        )
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
        monkeypatch.setattr(
            wrap_commit, "find_project_root", fixed_project_root(tmp_path),
        )

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
            fixed_wrap_list_literals(["make better"]),
        )

        exit_code = wrap_commit.main(["--file", str(target)])

        assert exit_code == 0
        assert target.read_text(encoding="utf-8") == (
            "```log\nwe `make better` cars\n```\n"
        )


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
