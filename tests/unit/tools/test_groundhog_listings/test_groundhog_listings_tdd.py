"""Listings expose trustworthy group and exclusion evidence without starting runs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.groundhog import cli, exclusions, floor, redirect
from tools.groundhog.context import Deps
from tools.groundhog.models import EXIT_SETUP_ERROR

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def no_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep CLI output in pytest's capture without changing production dispatch."""
    def ignore_redirect(*_args: object) -> None:
        """Leave capture output available to test assertions."""

    monkeypatch.setattr(redirect, "activate_if_captured", ignore_redirect)


def test_groups_listing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Group listings show normalized patterns and resolved membership counts."""
    (tmp_path / ".ghog-groups").write_text("[demo]\ntests=test_*.py\nsources=module.py\n", encoding="utf-8")
    (tmp_path / "test_x.py").touch()
    (tmp_path / "module.py").touch()
    assert cli.main(["groups", "--root", str(tmp_path)], Deps()) == 0
    output = capsys.readouterr().out
    assert "demo" in output
    assert "test_*.py" in output
    assert "module.py" in output
    assert "tests=1" in output
    assert "sources=1" in output
    assert not (tmp_path / "a.ghog.status").exists()
    assert cli.main(["groups", "missing", "--root", str(tmp_path)]) == EXIT_SETUP_ERROR
    assert "unknown" in capsys.readouterr().out


def test_listing_and_semantic_comparison(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Only new or raised entries loosen the accepted duration gate."""
    exclusions.write_exclusions(tmp_path, {"tests/z.py::z": 3.0, "tests/a.py::a[x = y]": 2.0})
    args = ["exclude", "--root", str(tmp_path), "--list"]
    assert cli.main(args) == 0
    output = capsys.readouterr().out
    assert output == "tests/a.py::a[x = y] = 2.0\ntests/z.py::z = 3.0\nexclusions=2\n"
    saved = tmp_path / "listing.txt"
    saved.write_text(output, encoding="utf-8")
    exclusions.write_exclusions(tmp_path, {"tests/z.py::z": 2.0})
    assert cli.main([*args, f"--since={saved}"]) == 0
    assert capsys.readouterr().out == "exclusions=unchanged\n"
    exclusions.write_exclusions(tmp_path, {"tests/z.py::z": 4.0, "tests/new.py::n": 1.0})
    assert cli.main([*args, "--since", str(saved)]) == 0
    changed = capsys.readouterr().out
    assert "exclusions=changed" in changed
    assert "tests/z.py::z = 4.0" in changed
    assert "tests/new.py::n = 1.0" in changed


@pytest.mark.parametrize("args", [
    ["exclude"], ["exclude", "node"], ["exclude", "node", "bad"],
    ["exclude", "node", "nan"], ["exclude", "node", "-1"],
    ["exclude", "--list", "node", "1"], ["exclude", "--since=x"],
    ["exclude", "--list", "--since"], ["exclude", "--list", "--full=cov"],
    ["groups", "--full=cov"], ["groups", "--group=demo"], ["groups", "a", "b"],
    ["groups", "--root"], ["exclude", "--list", "--root"],
    ["groups", "--list=yes"], ["exclude", "--list=yes"],
])
def test_invalid_listing_arguments_exit_five(tmp_path: Path, args: list[str]) -> None:
    """Groundhog validates read-only arguments instead of argparse exiting two."""
    assert cli.main([*args, "--root", str(tmp_path)]) == EXIT_SETUP_ERROR


@pytest.mark.parametrize("body", [None, "1\n2\n"])
def test_absent_exclusions_are_empty(tmp_path: Path, capsys: pytest.CaptureFixture[str], body: str | None) -> None:
    """A missing file or missing section is a trustworthy empty listing."""
    if body is not None:
        floor.floor_path(tmp_path).write_text(body, encoding="utf-8")
    assert cli.main(["exclude", "--list", "--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out == "exclusions=0\n"


@pytest.mark.parametrize("entry", ["broken", " = 2", "node = nan", "node = inf", "node = -1", "node = bad"])
def test_malformed_entries_fail_strictly(tmp_path: Path, capsys: pytest.CaptureFixture[str], entry: str) -> None:
    """Malformed entries cannot masquerade as no exceptions."""
    floor.floor_path(tmp_path).write_text(f"1\n2\n[exclusion]\n{entry}\n", encoding="utf-8")
    assert cli.main(["exclude", "--list", "--root", str(tmp_path)]) == EXIT_SETUP_ERROR
    assert "exclusions=unreadable" in capsys.readouterr().out
    assert cli.main(["exclude", "--list", "--since=absent", "--root", str(tmp_path)]) == EXIT_SETUP_ERROR
    assert "exclusions=unverified" in capsys.readouterr().out


@pytest.mark.parametrize("body", [None, "", "exclusions=unreadable\n", "node = 1\nexclusions=0\n", "junk\nexclusions=1\n",
                                 "node = 1\nnode = 2\nexclusions=2\n"])
def test_bad_saved_listing_is_unverified(tmp_path: Path, capsys: pytest.CaptureFixture[str], body: str | None) -> None:
    """A saved listing must be complete and readable to establish unchanged."""
    saved = tmp_path / "saved.txt"
    if body is not None:
        saved.write_text(body, encoding="utf-8")
    assert cli.main(["exclude", "--list", f"--since={saved}", "--root", str(tmp_path)]) == EXIT_SETUP_ERROR
    assert "exclusions=unverified" in capsys.readouterr().out


def test_listings_preserve_live_run_and_legacy_floor(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Reading legacy evidence neither migrates artifacts nor overwrites a live run."""
    live = tmp_path / "a.ghog.status"
    live.write_text("state=running pid=123\n", encoding="utf-8")
    legacy = tmp_path / floor.FLOOR_FILE
    content = "1\n2\n[exclusion]\n# accepted call\n\nnode = 3\n"
    legacy.write_text(content, encoding="utf-8")
    assert cli.main(["exclude", "--list", "--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out == "node = 3.0\nexclusions=1\n"
    assert live.read_text(encoding="utf-8") == "state=running pid=123\n"
    assert legacy.read_text(encoding="utf-8") == content
    assert not (tmp_path / ".reviews").exists()


def test_unreadable_exclusion_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Undecodable evidence fails even before entry parsing."""
    (tmp_path / floor.FLOOR_FILE).write_bytes(b"\xff")
    assert cli.main(["exclude", "--list", "--root", str(tmp_path)]) == EXIT_SETUP_ERROR
    assert capsys.readouterr().out == "exclusions=unreadable\n"


def test_other_commands_keep_argparse_errors() -> None:
    """Listing setup errors leave the existing run-command argument contract intact."""
    with pytest.raises(SystemExit) as error:
        cli.main(["single"])
    argparse_exit = 2
    assert error.value.code == argparse_exit
