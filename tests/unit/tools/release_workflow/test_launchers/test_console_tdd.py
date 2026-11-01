"""Console decisions and cancellation injected at production Python boundaries."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.launcher_simulation import decoded

if TYPE_CHECKING:
    from tests.unit.tools.release_workflow.launcher_simulation import ToolingSimulation
    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox


@pytest.mark.parametrize("override", [False, True])
def test_alias_origin(*, override: bool, launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox) -> None:
    """Alias origin discovers the caller's repository with declared console stdin."""
    (git_sandbox.home / "B/input.txt").write_text("Bonjour", encoding="utf-8")
    arguments = ["probe", "--input-file", "input.txt"]
    if override:
        arguments.append("--non-interactive")
    result = launcher_tooling.run(arguments, sandbox=git_sandbox, cwd=git_sandbox.home / "B/sub",
                                  entry="alias-batch", console=True)
    value = decoded(result)
    assert (value["root"], value["entry"], value["non_interactive"]) == (str(git_sandbox.home / "B"), "alias-batch", override)
    assert value["payload"] == "Bonjour"


@pytest.mark.parametrize("entry", ["explicit-native", "explicit-batch", "alias-batch"])
@pytest.mark.parametrize("console", [False, True])
@pytest.mark.parametrize("alternate", [False, True])
def test_cancellation(*, entry: str, console: bool, alternate: bool, launcher_tooling: ToolingSimulation,  # noqa: PLR0913 - fixture matrix
                      alternate_launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox) -> None:
    """KeyboardInterrupt becomes status 1 with diagnostics at every Python entry."""
    selected = alternate_launcher_tooling if alternate else launcher_tooling
    result = selected.run(["wait", "--project-root", str(git_sandbox.home / "B")],
                           sandbox=git_sandbox, cwd=git_sandbox.home, entry=entry, console=console)
    assert result.returncode == 1
    assert b"interrupted" in result.stderr
    assert not result.stdout


@pytest.mark.parametrize("entry", ["explicit-native", "explicit-batch"])
@pytest.mark.parametrize("case", ["eof", "file", "explicit"])
def test_redirected_stdin(entry: str, case: str, launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox) -> None:
    """Dispatch consumes a declared non-console stream or explicit policy."""
    payload = 'Prêt %PATH% ^!& "quoted"\r\n'
    arguments = ["probe", "--project-root", str(git_sandbox.home / "B")]
    arguments += {"eof": [], "file": ["--input-stdin"], "explicit": ["--non-interactive"]}[case]
    result = launcher_tooling.run(arguments, sandbox=git_sandbox, cwd=git_sandbox.home,
                                  entry=entry, payload=payload.encode("utf-8"), console=case == "explicit")
    value = decoded(result)
    assert value["non_interactive"] is True
    assert value["payload"] == (payload if case == "file" else None)


# eof
