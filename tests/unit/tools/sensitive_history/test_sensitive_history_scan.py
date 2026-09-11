"""CLI and Markdown rendering tests for the sensitive history scanner.

The scanner engine has dedicated repository contracts. These CLI tests use a
typed report at that seam so argument handling, output safety, JSON, Markdown,
and exit codes do not rebuild and rescan Git history for every assertion.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tools.sensitive_history import sensitive_history_scan as scan_cli
from tools.sensitive_history.history_scan import HistoryMatch, PatternSpec, ScanReport

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

ERROR_EXIT = 2
SOURCE_SECTION_COUNT = 4


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (repo / "file.txt").write_text("one SecretWord two\n", encoding="utf-8")
    (repo / "binary.dat").write_bytes(b"prefix\0SecretWord binary")
    (repo / "long.txt").write_text(
        f"{'x' * 520}SecretWord{'y' * 20}\n", encoding="utf-8",
    )
    (repo / "a.sensitive.replacements.local.txt").write_text(
        "regex:(?i)secretword==>replacement\n", encoding="utf-8",
    )
    return repo


@pytest.fixture(autouse=True)
def scanner_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return representative typed history without launching Git."""
    def fake_scan(
        root: Path,
        patterns: Sequence[PatternSpec],
        *,
        max_line_chars: int | None,
        validation_term: str | None,
    ) -> ScanReport:
        labels = tuple(pattern.label for pattern in patterns)
        if not labels or all("absent" in label for label in labels):
            matches: tuple[HistoryMatch, ...] = ()
        else:
            term = labels[0]
            long_line = f"{'x' * 520}SecretWord{'y' * 20}"
            rendered_line = long_line if max_line_chars is None else long_line[:max_line_chars]
            matches = (
                HistoryMatch(term, "commit", "c" * 40, None, (), 1, "feat: SecretWord", ("SecretWord",)),
                HistoryMatch(term, "tag", "t" * 40, "v1", (), 1, "SecretWord release", ("SecretWord",)),
                HistoryMatch(term, "path", "p" * 40, None, ("SecretWord.txt",), None, "SecretWord.txt", ("SecretWord",)),
                HistoryMatch(
                    term,
                    "blob",
                    "b" * 40,
                    None,
                    ("binary.dat",),
                    1,
                    rendered_line,
                    ("SecretWord",),
                    binary=True,
                    truncated=max_line_chars is not None and len(long_line) > max_line_chars,
                ),
            )
        return ScanReport(
            root=str(root),
            object_count=4,
            blob_count=1,
            terms=labels,
            matches=matches,
            validation_term=validation_term,
            validation_blob_count=1 if validation_term else None,
        )

    class FakeRepository:
        """Model the ignored-output check used by the CLI."""

        def __init__(self, root: Path) -> None:
            self.root = root.resolve()

        @staticmethod
        def is_ignored(path: Path) -> bool:
            return path.name.startswith("a.")

    monkeypatch.setattr(scan_cli, "scan_repository", fake_scan)
    monkeypatch.setattr(scan_cli, "GitRepository", FakeRepository)

    def repository_patterns(
        root: Path,
        *,
        allow_empty: bool = False,
    ) -> list[PatternSpec]:
        rules = root / "a.sensitive.replacements.local.txt"
        if not rules.is_file():
            if allow_empty:
                return []
            message = "provide terms or a replacement rules file"
            raise scan_cli.HistoryScanError(message)
        if allow_empty and not rules.read_text(encoding="utf-8").strip():
            return []
        return scan_cli.patterns_from_replacement_file(rules)

    monkeypatch.setattr(scan_cli, "patterns_from_repository_rules", repository_patterns)


@pytest.fixture
def sensitive_cli_repo(tmp_path: Path) -> Path:
    """Build scanner history outside the measured CLI assertion call."""
    return _repo(tmp_path)


def test_cli_defaults_to_rules_and_writes_ignored_markdown(
    sensitive_cli_repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No explicit terms uses the conventional rules file."""
    repo = sensitive_cli_repo
    output = repo / "a.scan.local.md"

    assert (
        scan_cli.main(
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

    assert scan_cli.main(
        ["--root", str(repo), "--json", "--fail-on-match", "secretword"],
    ) == 1

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
        scan_cli.main(
            ["--root", str(repo), "--output", str(repo / "report.md"), "secretword"],
        )
        == ERROR_EXIT
    )
    assert "must be Git-ignored" in capsys.readouterr().err
    assert (
        scan_cli.main(["--root", str(repo), "--max-line-chars", "20", "secretword"])
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
    assert scan_cli.main(["--root", str(repo)]) == ERROR_EXIT
    assert "provide terms" in capsys.readouterr().err


def test_cli_markdown_renders_empty_sections(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A clean Markdown scan explicitly marks every empty result section."""
    repo = _repo(tmp_path)
    assert scan_cli.main(["--root", str(repo), "definitely-absent"]) == 0
    assert capsys.readouterr().out.count("None.") == SOURCE_SECTION_COUNT


# eof
