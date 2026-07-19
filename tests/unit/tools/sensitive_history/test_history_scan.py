"""Tests for case-insensitive Git history scanning."""

from __future__ import annotations

import re
import subprocess
from typing import TYPE_CHECKING

import pytest

from tools.sensitive_history.history_scan import (
    GitRepository,
    HistoryScanError,
    ScanReport,
    _display_line,
    merge_patterns,
    patterns_from_replacement_file,
    patterns_from_terms,
    patterns_from_terms_file,
    scan_repository,
)

if TYPE_CHECKING:
    from pathlib import Path

EXPECTED_BLOB_MATCHES = 3
MATCHING_TEXT_LINE = 2


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


@pytest.fixture
def history_repo(tmp_path: Path) -> Path:
    """Create history with message, tag, path, text, and binary matches."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Scanner Tests")
    _git(repo, "config", "user.email", "scanner@example.invalid")
    (repo / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (repo / "SecretCorp-notes.txt").write_text(
        "first line\nSecretCorp appears here\n", encoding="utf-8",
    )
    (repo / "binary.dat").write_bytes(b"prefix\0SECRETCORP binary suffix")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: mention secretcorp", "-m", "body SecretCorp")
    _git(repo, "tag", "-a", "v1", "-m", "SecretCorp release")
    (repo / "SecretCorp-notes.txt").write_text(
        "replacement\nsecretcorp second version\n", encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "docs: update notes")
    return repo


def test_pattern_inputs_are_case_insensitive_and_deduplicated(tmp_path: Path) -> None:
    """Terms and both replacement syntaxes form one stable pattern list."""
    terms_file = tmp_path / "terms.txt"
    terms_file.write_text("# names\nAcme\n\n", encoding="utf-8")
    rules_file = tmp_path / "rules.txt"
    rules_file.write_text(
        "regex:(?i)_secretproject_==>_my_project_\n"
        "literal:Other.Co==>company\n"
        "BareName==>replacement\n",
        encoding="utf-8",
    )
    patterns = merge_patterns(
        patterns_from_terms(["SecretProject"]),
        patterns_from_terms_file(terms_file),
        patterns_from_replacement_file(rules_file),
        patterns_from_terms(["secretproject"]),
    )

    assert [pattern.label for pattern in patterns] == [
        "SecretProject",
        "Acme",
        "_secretproject_",
        "Other.Co",
        "BareName",
    ]
    assert patterns[0].regex.search("secretproject")
    assert patterns[2].regex.search("x_secretproject_y")
    assert patterns[3].regex.search("other.co")
    assert patterns[4].regex.search("barename")


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("\n", "blank"),
        ("glob:secret*==>x\n", "glob"),
        ("regex:[==>x\n", "invalid pattern"),
    ],
)
def test_replacement_file_rejects_unsafe_or_unsupported_rules(
    tmp_path: Path,
    content: str,
    message: str,
) -> None:
    """Malformed replacement rules stop before scanning."""
    path = tmp_path / "rules.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(HistoryScanError, match=message):
        patterns_from_replacement_file(path)


def test_missing_and_empty_inputs_are_reported(tmp_path: Path) -> None:
    """Unreadable files and empty merged inputs have clear errors."""
    with pytest.raises(HistoryScanError, match="cannot read terms file"):
        patterns_from_terms_file(tmp_path / "missing.txt")
    with pytest.raises(HistoryScanError, match="cannot read replacement file"):
        patterns_from_replacement_file(tmp_path / "missing-rules.txt")
    with pytest.raises(HistoryScanError, match="must not be empty"):
        patterns_from_terms([" "])
    with pytest.raises(HistoryScanError, match="provide terms"):
        merge_patterns([])


@pytest.fixture
def history_report(history_repo: Path) -> ScanReport:
    """Scan the shared history fixture once per dependent test."""
    return scan_repository(
        history_repo,
        patterns_from_terms(["secretcorp"]),
        max_line_chars=None,
        validation_term="replacement",
    )


def test_scan_reports_every_source_kind(history_report: ScanReport) -> None:
    """One batch scan reports counts for every historical source kind."""
    report = history_report
    assert report.object_count > report.blob_count > 0
    assert report.validation_blob_count == 1
    assert report.kind_counts("secretcorp") == {
        "commit": 2,
        "tag": 1,
        "path": 2,
        "blob": 3,
    }
    assert report.blob_counts("secretcorp") == EXPECTED_BLOB_MATCHES
    assert report.casing_counts("secretcorp") == {
        "SecretCorp": 5,
        "secretcorp": 2,
        "SECRETCORP": 1,
    }


def test_scan_reports_exact_context(history_report: ScanReport) -> None:
    """Blob results retain lines, binary flags, paths, and serialization."""
    blob_matches = [match for match in history_report.matches if match.kind == "blob"]
    assert any(
        match.line_number == MATCHING_TEXT_LINE and "appears here" in match.line
        for match in blob_matches
    )
    assert any(match.binary and "binary suffix" in match.line for match in blob_matches)
    assert any("SecretCorp-notes.txt" in match.paths for match in blob_matches)
    assert history_report.to_dict()["terms"] == ["secretcorp"]
    assert blob_matches[0].to_dict()["kind"] == "blob"


def test_scan_truncates_long_lines_and_validates_known_content(history_repo: Path) -> None:
    """Long lines become centered excerpts and a bad validation term fails."""
    long_file = history_repo / "long.txt"
    long_file.write_text(f"{'a' * 80}SecretCorp{'z' * 80}\n", encoding="utf-8")
    _git(history_repo, "add", "long.txt")
    _git(history_repo, "commit", "-m", "test: long line")
    report = scan_repository(
        history_repo,
        patterns_from_terms(["secretcorp"]),
        max_line_chars=40,
    )
    long_match = next(
        match
        for match in report.matches
        if match.kind == "blob" and "long.txt" in match.paths
    )
    assert long_match.truncated
    assert long_match.line.startswith("…")
    assert long_match.line.endswith("…")
    with pytest.raises(HistoryScanError, match="scanner validation failed"):
        scan_repository(
            history_repo,
            patterns_from_terms(["secretcorp"]),
            validation_term="definitely absent",
        )


def test_non_repository_is_rejected(tmp_path: Path) -> None:
    """Scanning stops outside a Git working tree."""
    with pytest.raises(HistoryScanError, match="git rev-parse"):
        scan_repository(tmp_path, patterns_from_terms(["secret"]))

    bare = tmp_path / "bare.git"
    subprocess.run(  # noqa: S603
        ["git", "init", "--bare", str(bare)],  # noqa: S607
        check=True,
        capture_output=True,
    )
    with pytest.raises(HistoryScanError, match="not a Git working tree"):
        GitRepository(bare)


def test_empty_batch_inputs_and_unmatched_excerpt(history_repo: Path) -> None:
    """Empty object batches are no-ops and the excerpt helper has a fallback."""
    repository = GitRepository(history_repo)
    assert repository.blob_ids([]) == []
    assert list(repository.iter_blobs([])) == []
    assert _display_line("x" * 60, re.compile("absent"), 40) == ("x" * 40, True)


# eof
