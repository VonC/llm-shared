"""Contracts for placing tool files in the review artifact home.

`artifact_path` prepares the home with its `*` ignore file, returns the file
path inside it, and moves a legacy root copy of the same name into the home
once, never overwriting a home copy. The shell entry prints that path.
"""

from __future__ import annotations

import runpy
import sys
from typing import TYPE_CHECKING

import pytest

from tools import artifact_home
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from pathlib import Path


def test_artifact_home_prepares_the_default_home(tmp_path: Path) -> None:
    """Without a declaration the home is `.reviews`, created with `*`."""
    home = artifact_home.artifact_home(tmp_path)

    assert home == tmp_path.resolve() / ".reviews"
    assert (home / ".gitignore").read_bytes() == b"*\n"
    assert artifact_home.artifact_home(tmp_path) == home


def test_artifact_path_follows_a_declared_home(tmp_path: Path) -> None:
    """A declared home wins, and the path is only prepared, not created."""
    (tmp_path / ".review-artifacts.ini").write_text(
        "[review-artifacts]\nhome = .private/work\n", encoding="utf-8",
    )

    path = artifact_home.artifact_path(tmp_path, "a.ghog.outliers")

    assert path == tmp_path.resolve() / ".private" / "work" / "a.ghog.outliers"
    assert not path.exists()


def test_artifact_path_moves_a_legacy_root_copy_once(tmp_path: Path) -> None:
    """A root copy moves into the home; a home copy is never overwritten."""
    (tmp_path / "a.ghog.outliers").write_text("kept\n", encoding="utf-8")

    moved = artifact_home.artifact_path(tmp_path, "a.ghog.outliers")

    assert moved.read_text(encoding="utf-8") == "kept\n"
    assert not (tmp_path / "a.ghog.outliers").exists()

    (tmp_path / "a.ghog.outliers").write_text("stale\n", encoding="utf-8")
    assert artifact_home.artifact_path(tmp_path, "a.ghog.outliers") == moved
    assert moved.read_text(encoding="utf-8") == "kept\n"
    assert (tmp_path / "a.ghog.outliers").read_text(encoding="utf-8") == "stale\n"


@pytest.mark.parametrize("name", ["", ".", "..", "sub/a.x", "..\\a.x"])
def test_artifact_path_rejects_anything_but_a_plain_name(tmp_path: Path, name: str) -> None:
    """Only a plain file name can be placed in the home."""
    with pytest.raises(ValueError, match="plain name"):
        artifact_home.artifact_path(tmp_path, name)


def test_artifact_home_surfaces_an_invalid_home(tmp_path: Path) -> None:
    """An existing home with the wrong ignore bytes is refused, not repaired."""
    (tmp_path / ".reviews").mkdir()
    (tmp_path / ".reviews" / ".gitignore").write_text("*.log\n", encoding="utf-8")

    with pytest.raises(ReviewExchangeError, match="ignore coverage is invalid"):
        artifact_home.artifact_home(tmp_path)


def test_main_prints_the_path_or_reports_usage(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """The shell entry prints one path, or exits 2 with a diagnostic."""
    assert artifact_home.main([str(tmp_path), "a.diff"]) == artifact_home.EXIT_OK
    assert capsys.readouterr().out == f"{tmp_path.resolve() / '.reviews' / 'a.diff'}\n"

    assert artifact_home.main([str(tmp_path)]) == artifact_home.EXIT_USAGE
    assert "usage:" in capsys.readouterr().err

    assert artifact_home.main([str(tmp_path), "../a.diff"]) == artifact_home.EXIT_USAGE
    assert "plain name" in capsys.readouterr().err


def test_main_reads_the_process_arguments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Without explicit arguments the entry reads `sys.argv`."""
    monkeypatch.setattr(artifact_home.sys, "argv", ["artifact_home", str(tmp_path), "a.md"])

    assert artifact_home.main() == artifact_home.EXIT_OK
    assert capsys.readouterr().out.strip().endswith("a.md")


@pytest.mark.filterwarnings("ignore:'tools.artifact_home' found in sys.modules:RuntimeWarning")
def test_module_entry_exits_with_the_main_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`python -m tools.artifact_home` exits with the status of `main`."""
    monkeypatch.setattr(sys, "argv", ["artifact_home", str(tmp_path), "a.md"])

    with pytest.raises(SystemExit) as raised:
        runpy.run_module("tools.artifact_home", run_name="__main__")

    assert raised.value.code == artifact_home.EXIT_OK


# eof
