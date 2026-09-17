"""Guard semantic ports against accidental persistence or workflow coupling."""

from __future__ import annotations

import builtins
import importlib
from typing import TYPE_CHECKING, Any

from tools.wait_service import ports

if TYPE_CHECKING:
    from types import ModuleType

    import pytest


class TestWaitPorts:
    """Port declarations must load without importing infrastructure adapters."""

    def test_ports_do_not_load_sqlite_or_production_workflows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A guarded reload catches forbidden imports even if already cached."""
        original = builtins.__import__

        def guarded(name: str, *args: Any, **kwargs: Any) -> ModuleType:  # noqa: ANN401 - Match the import hook's opaque arguments.
            forbidden = ("sqlite3", "tools.groundhog", "tools.review", "win32", "ctypes")
            assert not name.startswith(forbidden), f"Port depends on infrastructure: {name}"
            return original(name, *args, **kwargs)

        with monkeypatch.context() as context:
            context.setattr(builtins, "__import__", guarded)
            importlib.reload(ports)

# eof
