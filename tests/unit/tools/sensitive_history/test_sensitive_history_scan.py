"""CLI and Markdown rendering tests for the sensitive history scanner."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from tools.sensitive_history.sensitive_history_scan import main

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

ERROR_EXIT = 2
SOURCE_SECTION_COUNT = 4


def _git(repo: Path, *args: str) -> None:
    subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
    )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "CLI Tests")
    _git(repo, "config", "user.email", "cli@example.invalid")
    (repo / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (repo / "file.txt").write_text("one SecretWord two\n", encoding="utf-8")
    (repo / "binary.dat").write_bytes(b"prefix\0SecretWord binary")
    (repo / "long.txt").write_text(
        f"{'x' * 520}SecretWord{'y' * 20}\n", encoding="utf-8",
    )
    (repo / "a.sensitive.replacements.local.txt").write_text(
        "regex:(?i)secretword==>replacement\n", encoding="utf-8",
    )
    _git(repo, "add", ".gitignore", "file.txt", "binary.dat", "long.txt")
    _git(repo, "commit", "-m", "feat: SecretWord")
    _git(repo, "tag", "-a", "v1", "-m", "SecretWord release")
    return repo


def test_cli_defaults_to_rules_and_writes_ignored_markdown(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No explicit terms uses the conventional rules file."""
    repo = _repo(tmp_path)
    output = repo / "a.scan.local.md"

    assert (
        main(
            [
                "--root",
                str(repo),
                "--output",
                str(output),
                "--full-lines",
                "--validation-term",
                "SecretWord",
            ],
        )
        == 0
    )

    stdout = capsys.readouterr().out
    content = output.read_text(encoding="utf-8")
    assert "Wrote" in stdout
    assert content.startswith("<!-- markdownlint-disable-file -->\n\n")
    assert "## Commit-message lines" in content
    assert "SecretWord" in content
    assert "Scanner validation" in content
    assert "binary" in content
    assert "excerpt" not in content


def test_cli_json_and_fail_on_match(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """JSON is machine-readable and the optional match gate returns one."""
    repo = _repo(tmp_path)

    assert main(["--root", str(repo), "--json", "--fail-on-match", "secretword"]) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["terms"] == ["secretword"]
    assert payload["matches"]


def test_cli_rejects_unignored_output_and_tiny_excerpt(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A sensitive report cannot land in a tracked location or use tiny excerpts."""
    repo = _repo(tmp_path)
    assert (
        main(["--root", str(repo), "--output", str(repo / "report.md"), "secretword"])
        == ERROR_EXIT
    )
    assert "must be Git-ignored" in capsys.readouterr().err
    assert (
        main(["--root", str(repo), "--max-line-chars", "20", "secretword"])
        == ERROR_EXIT
    )
    assert "at least 40" in capsys.readouterr().err


def test_cli_requires_an_input_when_default_rules_are_absent(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No terms and no conventional rules file returns a usage error."""
    repo = _repo(tmp_path)
    (repo / "a.sensitive.replacements.local.txt").unlink()
    assert main(["--root", str(repo)]) == ERROR_EXIT
    assert "provide terms" in capsys.readouterr().err


def test_cli_markdown_renders_empty_sections(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A clean Markdown scan explicitly marks every empty result section."""
    repo = _repo(tmp_path)
    assert main(["--root", str(repo), "definitely-absent"]) == 0
    assert capsys.readouterr().out.count("None.") == SOURCE_SECTION_COUNT


# eof
