"""Protect isolation and real SQLite behavior at the simulation boundary."""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

import pytest

from tests.scenario_storage import ScenarioStorage

if TYPE_CHECKING:
    from pathlib import Path


def test_discard_keeps_shared_seed_and_link_target(tmp_path: Path) -> None:
    """Fixture retirement removes only its own tree, including stale link cache."""
    storage = ScenarioStorage(str(tmp_path))
    seed, scratch = tmp_path / "seed", tmp_path / "scratch"
    storage.create_dir(seed)
    storage.create_dir(scratch / "nested")
    storage.symlink(seed, scratch / "link", target_is_directory=True)
    assert storage.realpath(scratch / "link") == str(seed)

    storage.discard_tree(scratch)

    assert storage.isdir(seed)
    assert not storage.exists(scratch)
    assert not storage.exists(scratch / "nested")
    assert not storage.exists(scratch / "link")
    assert storage.listdir(tmp_path) == ["seed"]


def test_sqlite_close_retains_commit_and_discards_pending_write(tmp_path: Path) -> None:
    """Reconnecting reads real SQL pages and cannot resurrect a rolled-back row."""
    path = tmp_path / "evidence.db"
    connection = sqlite3.connect(str(path))
    connection.execute("create table evidence (value text)")
    connection.execute("insert into evidence values ('committed')")
    connection.commit()
    connection.execute("insert into evidence values ('pending')")
    connection.close()
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("select 1")

    restored = sqlite3.connect(str(path))
    try:
        assert restored.execute("select value from evidence").fetchall() == [("committed",)]
    finally:
        restored.close()

    assert path.read_bytes().startswith(b"SQLite format 3\x00")


# eof
