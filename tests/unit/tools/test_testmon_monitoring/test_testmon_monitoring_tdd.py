"""Dependency hashes retain source evidence without Testmon's Git shortcut."""

from pathlib import Path

import pytest
from testmon import process_code, testmon_core

from tests.testmon_monitoring import source_sha


def test_dependency_hash_reads_source_without_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The live Testmon binding uses its source fallback, never a child process."""
    source = tmp_path / "sample.py"
    source.write_text("answer = 42\n", encoding="utf-8")
    expected = process_code.read_source_sha(str(source))

    def reject_git(*_args: object, **_kwargs: object) -> None:
        pytest.fail("dependency hashing must not start Git")

    monkeypatch.setattr(process_code, "run", reject_git)

    assert testmon_core.get_source_sha is source_sha
    assert testmon_core.get_source_sha(str(tmp_path), "sample.py") == expected
    assert testmon_core.get_source_sha(str(tmp_path), "missing.py") == (None, None)
