"""Keep SQLite's real SQL engine while storing scenario database bytes in memory.

Coverage still reads its schema, lines, arcs and corrupt evidence through its
normal API. Only the connection's storage is replaced; runner databases outside
the declared scratch tree retain ordinary SQLite connections.
"""

from __future__ import annotations

import builtins
import os
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any

from coverage import python as coverage_python
from coverage.misc import isolate_module

if TYPE_CHECKING:
    import pytest

    from tests.memory_filesystem import ScenarioFilesystem
    from tests.scenario_storage import Entry


class ScenarioConnection(sqlite3.Connection):
    """Persist committed SQLite pages to a scenario entry on connection close."""

    destination: Entry
    closed = False

    def close(self) -> None:
        """Preserve invalid input and close even if it cannot be serialized."""
        if self.closed:
            return
        try:
            # Native close discards an unfinished transaction. Serializing first
            # would incorrectly turn its pending writes into committed evidence.
            self.rollback()
            try:
                content = self.serialize()
            except sqlite3.Error:
                # An empty or corrupt database has no valid pages to publish.
                pass
            else:
                # The connection already owns this file observation. Reopening
                # it through pathlib on every SQL read needlessly constructs
                # streams and stat results; SQLite still owns all page changes.
                self.destination.content = content
        finally:
            self.closed = True
            super().close()


def install(patch: pytest.MonkeyPatch, filesystem: ScenarioFilesystem) -> None:
    """Route connections only when their file belongs to the scenario tree."""
    original = sqlite3.connect

    def connect(database: str, *args: Any, **kwargs: Any) -> sqlite3.Connection:  # noqa: ANN401
        if not filesystem.contains(database):
            return original(database, *args, **kwargs)
        destination = Path(database)
        storage = filesystem.filesystem
        if storage.isdir(destination) or not storage.isdir(destination.parent):
            message = "unable to open database file"
            raise sqlite3.OperationalError(message)
        connection = original(":memory:", *args, factory=ScenarioConnection, **kwargs)
        if not storage.exists(destination):
            destination.touch()
        connection.destination = storage._entry(destination)
        try:
            content = connection.destination.content
            if content:
                connection.deserialize(content)
        except BaseException:
            connection.close()
            raise
        return connection

    patch.setattr(sqlite3, "connect", connect)
    # Coverage snapshots OS functions and open before fixtures are installed.
    # Route those captured resource calls as well, retaining its parser/SQL.
    coverage_os = isolate_module(os)
    for name in ("getcwd", "stat", "listdir", "scandir", "unlink"):
        patch.setattr(coverage_os, name, getattr(os, name))
    for name in ("exists", "isfile", "isdir", "realpath", "abspath"):
        patch.setattr(coverage_os.path, name, getattr(os.path, name))
    patch.setattr(coverage_python, "open", builtins.open)


# eof
