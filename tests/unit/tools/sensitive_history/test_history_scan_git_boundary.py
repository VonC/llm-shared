"""Fast protocol tests for the sensitive-history Git repository adapter.

Recorded byte streams preserve the exact Git parsing and failure contracts
without creating repositories or launching one process per assertion.
"""

from __future__ import annotations

import subprocess
from io import BytesIO
from typing import TYPE_CHECKING

import pytest

from tools.sensitive_history.history_scan import GitRepository, HistoryScanError

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


def test_repository_parses_git_inventory_messages_and_ignore_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise all non-streaming Git protocols through recorded results."""
    blob_oid = "1" * 40
    tree_oid = "2" * 40
    commit_oid = "c" * 40
    tag_oid = "t" * 40
    calls: list[tuple[str, ...]] = []

    def recorded_run(
        command: Sequence[str],
        **_kwargs: object,
    ) -> subprocess.CompletedProcess[bytes]:
        calls.append(tuple(command))
        operation = command[1]
        outputs = {
            "rev-parse": (0, b"true\n", b""),
            "rev-list": (0, f"{blob_oid} notes.txt\n{tree_oid}\n".encode(), b""),
            "cat-file": (0, f"{blob_oid} blob\n{tree_oid} tree\n".encode(), b""),
            "log": (0, f"{commit_oid}\0subject\nbody\0".encode(), b""),
            "for-each-ref": (0, f"v1\0{tag_oid}\0release notes\0".encode(), b""),
            "check-ignore": (0, b"", b""),
            "broken": (1, b"", b"fatal detail"),
        }
        try:
            return_code, stdout, stderr = outputs[operation]
        except KeyError as error:
            raise AssertionError(command) from error
        return subprocess.CompletedProcess(command, return_code, stdout, stderr)

    monkeypatch.setattr(subprocess, "run", recorded_run)
    repository = GitRepository(tmp_path)

    object_ids, paths = repository.object_inventory()
    assert object_ids == [blob_oid, tree_oid]
    assert paths == {blob_oid: ("notes.txt",)}
    assert repository.blob_ids(object_ids) == [blob_oid]
    assert repository.blob_ids([]) == []
    assert repository.is_ignored(tmp_path / "a.report.json") is True

    commits = repository.commit_messages()
    assert [(record.oid, record.ref, record.text) for record in commits] == [
        (commit_oid, None, "subject\nbody"),
    ]
    tags = repository.tag_messages()
    assert [(record.oid, record.ref, record.text) for record in tags] == [
        (tag_oid, "v1", "release notes"),
    ]

    with pytest.raises(HistoryScanError, match="git broken failed: fatal detail"):
        repository._run("broken")  # noqa: SLF001

    assert ("git", "check-ignore", "--quiet", "--", "a.report.json") in calls


class _BlobProcess:
    """Popen-shaped byte pipes for one cat-file batch exchange."""

    def __init__(self, stdout: bytes) -> None:
        self.stdin = BytesIO()
        self.stdout = BytesIO(stdout)
        self.stderr = BytesIO()

    @staticmethod
    def wait() -> int:
        return 0


def test_repository_streams_recorded_batch_blobs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cover the feeder thread, batch framing, process finish, and yields."""
    first_oid = "1" * 40
    second_oid = "2" * 40
    output = (
        f"{first_oid} blob 5\n".encode()
        + b"first\n"
        + f"{second_oid} blob 6\n".encode()
        + b"second\n"
    )
    process = _BlobProcess(output)

    def recorded_popen(
        command: Sequence[str],
        **_kwargs: object,
    ) -> _BlobProcess:
        assert tuple(command) == ("git", "cat-file", "--batch")
        return process

    monkeypatch.setattr(subprocess, "Popen", recorded_popen)
    repository = object.__new__(GitRepository)
    repository.root = tmp_path.resolve()

    assert list(repository.iter_blobs([first_oid, second_oid])) == [
        (first_oid, b"first"),
        (second_oid, b"second"),
    ]
    assert list(repository.iter_blobs([])) == []
