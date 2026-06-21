"""Tests for the wrap-list collection of the commit-text width enforcer.

Cover ``tools.wrap_commit_wraplist``: the directory search order and its
de-duplication, the ``wrap-list.backtick`` reader, and the collector across the
search roots.

The collector resolves the project root through the shared
``find_project_root`` helper; these tests pin that resolution with
``monkeypatch`` so they never depend on the real checkout.

Fix (split): extracted from ``test_wrap_commit.py`` so each test file stays
under the repo line budget; the backtick-pass classes stay there.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.unit.tools.wrap_commit_test_support import fixed_project_root
from tools import wrap_commit_wraplist

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001


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
