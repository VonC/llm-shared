"""Observe real record reads across standalone bootstrap and public dispatch."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tests.unit.tools.release_workflow.launcher_simulation import decoded

if TYPE_CHECKING:
    import pytest

    from tests.unit.tools.release_workflow.launcher_simulation import ToolingSimulation
    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox


def test_runtime_record_read_once(launcher_tooling: ToolingSimulation, git_template: GitSandbox,
                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """Public identity normalization does not reload the private helper's record."""
    reads: list[Path] = []
    read = Path.read_text

    def observe(path: Path, encoding: str | None = None, errors: str | None = None, newline: str | None = None) -> str:
        if path.name == "release-runtime.v1.txt":
            reads.append(path)
        return read(path, encoding=encoding, errors=errors, newline=newline)

    monkeypatch.setattr(Path, "read_text", observe)
    result = launcher_tooling.run(["probe", "--project-root", str(git_template.home / "B")],
                                  sandbox=git_template, cwd=git_template.home)
    value = decoded(result)
    assert value["entry"] == "explicit-native"
    assert value["runtime_public"] is True
    assert value["runtime_equal"] is True
    assert reads == [launcher_tooling.root / "venvs/release-runtime.v1.txt"]


# eof
