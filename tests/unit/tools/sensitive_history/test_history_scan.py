"""Tests for case-insensitive Git history scanning.

Fix: the ``subprocess.run`` stand-ins are fully typed (``object`` parameters
and an explicit return), so the strict pyright gate no longer flags unknown
parameter or argument types on the monkeypatched doubles.

Repository scanning uses an in-memory Git boundary with representative object,
message, path, text, binary, and long-line records. Configuration tests inject
the exact Git config results they parse, avoiding process startup while keeping
the scanner algorithms and failure paths intact.
"""

from __future__ import annotations

import re
import subprocess
from types import SimpleNamespace
from typing import TYPE_CHECKING, NoReturn

import pytest

from tools.sensitive_history import history_scan
from tools.sensitive_history.history_scan import (
    GitRepository,
    HistoryScanError,
    ScanReport,
    _display_line,
    configured_shared_replacement_file,
    merge_patterns,
    patterns_from_replacement_file,
    patterns_from_repository_rules,
    patterns_from_terms,
    patterns_from_terms_file,
    repository_replacement_files,
    scan_repository,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

EXPECTED_BLOB_MATCHES = 3
MATCHING_TEXT_LINE = 2


class _HistoryRepository:
    """Representative reachable history served without Git subprocesses."""

    def __init__(self, root: Path, *, include_long: bool = False) -> None:
        self.root = root
        self._blobs = {
            "1" * 40: b"first line\nSecretCorp appears here\n",
            "2" * 40: b"prefix\0SECRETCORP binary suffix",
            "3" * 40: b"replacement\nsecretcorp second version\n",
        }
        if include_long:
            self._blobs["4" * 40] = f"{'a' * 80}SecretCorp{'z' * 80}\n".encode()

    def object_inventory(self) -> tuple[list[str], dict[str, tuple[str, ...]]]:
        paths: dict[str, tuple[str, ...]] = {
            "1" * 40: ("SecretCorp-notes.txt",),
            "2" * 40: ("binary.dat",),
            "3" * 40: ("SecretCorp-notes.txt",),
        }
        if "4" * 40 in self._blobs:
            paths["4" * 40] = ("long.txt",)
        return [*self._blobs, "c" * 40, "t" * 40], paths

    def blob_ids(self, _object_ids: list[str]) -> list[str]:
        return list(self._blobs)

    def iter_blobs(self, blob_ids: list[str]) -> Iterator[tuple[str, bytes]]:
        return ((oid, self._blobs[oid]) for oid in blob_ids)

    @staticmethod
    def commit_messages() -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                oid="c" * 40,
                ref=None,
                text="feat: mention secretcorp\nbody SecretCorp",
            ),
        ]

    @staticmethod
    def tag_messages() -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                oid="t" * 40,
                ref="v1",
                text="SecretCorp release",
            ),
        ]


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


def test_repository_rules_merge_shared_then_project_local(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Conventional scans use central rules plus repository-specific rules."""
    repo = tmp_path / "repo"
    repo.mkdir()
    shared = tmp_path / "shared.rules"
    shared.write_text("literal:CommonTerm==>redacted\n", encoding="utf-8")
    local = repo / "a.sensitive.replacements.local.txt"
    local.write_text("literal:LocalTerm==>redacted\n", encoding="utf-8")

    def shared_config(
        *_args: object,
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            [],
            0,
            stdout=f"{shared}\n".encode(),
            stderr=b"",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        shared_config,
    )

    assert configured_shared_replacement_file(repo) == shared.resolve()
    assert repository_replacement_files(repo) == (shared.resolve(), local.resolve())
    assert [pattern.label for pattern in patterns_from_repository_rules(repo)] == [
        "CommonTerm",
        "LocalTerm",
    ]

    local.write_text("", encoding="utf-8")
    assert [pattern.label for pattern in patterns_from_repository_rules(repo)] == [
        "CommonTerm",
    ]


def test_repository_rules_handle_absent_empty_relative_and_failed_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Shared rule config is optional, path-aware, and fails closed on errors."""
    absent = tmp_path / "absent"
    absent.mkdir()
    empty = tmp_path / "empty"
    empty.mkdir()
    relative = tmp_path / "relative"
    relative.mkdir()
    rules = relative / "relative.rules"
    rules.write_text("literal:RelativeTerm==>redacted\n", encoding="utf-8")

    def config_result(
        *_args: object,
        cwd: Path,
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[bytes]:
        if cwd == absent:
            return subprocess.CompletedProcess([], 1, stdout=b"", stderr=b"")
        output = b"\n" if cwd == empty else b"relative.rules\n"
        return subprocess.CompletedProcess([], 0, stdout=output, stderr=b"")

    monkeypatch.setattr(subprocess, "run", config_result)
    assert configured_shared_replacement_file(absent) is None
    assert configured_shared_replacement_file(empty) is None
    assert configured_shared_replacement_file(relative) == rules.resolve()

    def missing_git(*_args: object, **_kwargs: object) -> NoReturn:
        message = "missing"
        raise FileNotFoundError(message)

    monkeypatch.setattr(subprocess, "run", missing_git)
    with pytest.raises(HistoryScanError, match="cannot read Git config"):
        configured_shared_replacement_file(relative)


def test_repository_rules_reject_failed_git_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A nonstandard Git config failure is not mistaken for an absent key."""
    repo = tmp_path / "repo"
    repo.mkdir()

    def failed_git(
        *_args: object,
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess([], 2, stdout=b"", stderr=b"config failed")

    monkeypatch.setattr(subprocess, "run", failed_git)
    with pytest.raises(HistoryScanError, match="config failed"):
        configured_shared_replacement_file(repo)


@pytest.fixture
def history_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> ScanReport:
    """Scan representative in-memory history through the production algorithm."""
    repository = _HistoryRepository(tmp_path)

    def repository_factory(_root: Path) -> _HistoryRepository:
        return repository

    monkeypatch.setattr(history_scan, "GitRepository", repository_factory)
    return scan_repository(
        tmp_path,
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


def test_scan_truncates_long_lines_and_validates_known_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Long lines become centered excerpts while known content validates."""
    repository = _HistoryRepository(tmp_path, include_long=True)

    def repository_factory(_root: Path) -> _HistoryRepository:
        return repository

    monkeypatch.setattr(history_scan, "GitRepository", repository_factory)
    report = scan_repository(
        tmp_path,
        patterns_from_terms(["secretcorp"]),
        max_line_chars=40,
        validation_term="SecretCorp",
    )
    long_match = next(
        match
        for match in report.matches
        if match.kind == "blob" and "long.txt" in match.paths
    )
    assert long_match.truncated
    assert long_match.line.startswith("…")
    assert long_match.line.endswith("…")
    assert report.validation_blob_count == EXPECTED_BLOB_MATCHES + 1


class _EmptyHistoryRepository:
    """In-memory repository for the missing-validation branch."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def object_inventory(self) -> tuple[list[str], dict[str, tuple[str, ...]]]:
        return [], {}

    def blob_ids(self, _object_ids: list[str]) -> list[str]:
        return []

    def iter_blobs(self, _blob_ids: list[str]) -> list[tuple[str, bytes]]:
        return []

    def commit_messages(self) -> list[object]:
        return []

    def tag_messages(self) -> list[object]:
        return []


def test_scan_rejects_a_validation_term_absent_from_history(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A missing positive control still fails without a second real scan."""
    repository = _EmptyHistoryRepository(tmp_path)

    def repository_factory(_root: Path) -> _EmptyHistoryRepository:
        return repository

    monkeypatch.setattr(history_scan, "GitRepository", repository_factory)
    with pytest.raises(HistoryScanError, match="scanner validation failed"):
        scan_repository(
            tmp_path,
            patterns_from_terms(["secretcorp"]),
            validation_term="definitely absent",
        )


def test_non_repository_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Scanning stops outside a Git working tree."""
    real_repository = GitRepository

    def reject_repository(_root: Path) -> NoReturn:
        message = "git rev-parse failed"
        raise HistoryScanError(message)

    monkeypatch.setattr(history_scan, "GitRepository", reject_repository)
    with pytest.raises(HistoryScanError, match="git rev-parse"):
        scan_repository(tmp_path, patterns_from_terms(["secret"]))

    bare = tmp_path / "bare.git"
    bare.mkdir()

    def bare_result(
        *_args: object,
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            [],
            0,
            stdout=b"false\n",
            stderr=b"",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        bare_result,
    )
    with pytest.raises(HistoryScanError, match="not a Git working tree"):
        real_repository(bare)


def test_empty_batch_inputs_and_unmatched_excerpt(tmp_path: Path) -> None:
    """Empty object batches are no-ops and the excerpt helper has a fallback."""
    repository = object.__new__(GitRepository)
    repository.root = tmp_path
    assert repository.blob_ids([]) == []
    assert list(repository.iter_blobs([])) == []
    assert _display_line("x" * 60, re.compile("absent"), 40) == ("x" * 40, True)


# eof
