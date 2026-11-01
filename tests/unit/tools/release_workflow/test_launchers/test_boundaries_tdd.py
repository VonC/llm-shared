"""Real Python failure boundaries with data-only interpreter/repository ports."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.launcher_simulation import tooling

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.launcher_simulation import ToolingSimulation
    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox

_INVALID = 2
_RECORDS = {
    "missing-executable": "1\nvenvs/absent\n",
    "parent-path": "1\nvenvs/../prepared\n",
    "version-injection": '1" & echo injected>injected.txt & rem "\nvenvs/prepared\n',
    "path-injection": '1\nvenvs/prepared" & echo injected>injected.txt & rem "\n',
    "colon": "1\nvenvs/C:prepared\n",
    "backslash": "1\nvenvs/prepared\\child\n",
    "prefix": "1\nelsewhere/prepared\n",
    "literal-metacharacters": "1\nvenvs/absent!%PATH%^& space\n",
}


@pytest.mark.parametrize("entry", ["explicit-native", "explicit-batch"])
@pytest.mark.parametrize(("command", "status", "detail"), [
    ("fail", 1, b"status 23"), ("required", 2, b"required input"), ("missing", 2, b"unavailable"),
])
def test_operation_failure(entry: str, command: str, status: int, detail: bytes,  # noqa: PLR0913 - fixture matrix
                           launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox) -> None:
    """Failure normalization retains detail and never silently prompts."""
    result = launcher_tooling.run([command, "--project-root", str(git_sandbox.home / "B")],
                                  sandbox=git_sandbox, cwd=git_sandbox.home, entry=entry)
    assert result.returncode == status
    assert detail in result.stderr
    assert b"Release input:" not in result.stderr
    assert not result.stdout
    if command == "fail":
        assert b"original child failure" in result.stderr


@pytest.mark.parametrize(("entry", "detail"), [
    ("explicit-batch", b"Unsupported batch argument"), ("explicit-native", b"Cannot read"),
])
def test_argument_grammar(entry: str, detail: bytes, launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox) -> None:
    """The production parser distinguishes batch grammar from native paths."""
    result = launcher_tooling.run(["probe", "--project-root", str(git_sandbox.home / "B"),
                                   "--input-file", "surviving!value"], sandbox=git_sandbox,
                                  cwd=git_sandbox.home, entry=entry)
    assert result.returncode == _INVALID
    assert detail in result.stderr


@pytest.mark.parametrize("kind", ["missing", "unreadable", *_RECORDS])
def test_unusable_runtime(kind: str, tmp_path: Path, git_template: GitSandbox) -> None:
    """Bootstrap rejects unusable designations before dispatch; data is never code."""
    selected = tooling(tmp_path / "tooling")
    record = selected.root / "venvs/release-runtime.v1.txt"
    record.unlink()
    if kind == "unreadable":
        record.mkdir()
    elif kind != "missing":
        record.write_text(_RECORDS[kind], encoding="utf-8")
    result = selected.run(["probe"], sandbox=git_template, cwd=tmp_path)
    assert result.returncode == _INVALID
    assert b"Release readiness failed" in result.stderr
    assert not result.stdout
    assert not (tmp_path / "injected.txt").exists()


def test_no_production_fixture_handler(launcher_tooling: ToolingSimulation, git_template: GitSandbox) -> None:
    """The production registry cannot reach a test-only operation."""
    result = launcher_tooling.run(["probe"], sandbox=git_template, cwd=git_template.home, handlers=None)
    assert result.returncode == _INVALID
    assert b"unavailable" in result.stderr


# eof
