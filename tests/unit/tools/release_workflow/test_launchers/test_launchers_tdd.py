"""Exercise Python entry contracts with argument vectors and explicit facts."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.launcher_simulation import decoded
from tools.release_workflow.cli import SHIPPED_HANDLERS

if TYPE_CHECKING:
    from tests.unit.tools.release_workflow.launcher_simulation import ToolingSimulation
    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox

_PAYLOAD = 'Prêt %PATH% ^ ! & "quoted" 🐍\r\nsecond line'


@pytest.mark.parametrize("entry", ["explicit-batch", "explicit-native"])
@pytest.mark.parametrize("transport", ["file", "stdin"])
@pytest.mark.parametrize("alternate", [False, True])
def test_entry_payload(*, entry: str, transport: str, alternate: bool, launcher_tooling: ToolingSimulation,  # noqa: PLR0913 - fixture matrix
                       alternate_launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox) -> None:
    """Python preserves payload and selects the designated tooling checkout."""
    sandbox = git_sandbox
    root = sandbox.home / "B"
    payload = root / "input é % ^ ! &.txt"
    payload.write_bytes(_PAYLOAD.encode("utf-8"))
    environment = dict(sandbox.environment, RELEASE_PROJECT=str(root), RELEASE_INPUT=str(payload),
                       PRJ_DIR=str(sandbox.home / "A"))
    selected = alternate_launcher_tooling if alternate else launcher_tooling
    arguments = ["probe", "--project-root-env", "RELEASE_PROJECT"]
    arguments += ["--input-stdin"] if transport == "stdin" else ["--input-file-env", "RELEASE_INPUT"]
    result = selected.run(arguments, sandbox=sandbox, cwd=sandbox.home, environment=environment,
                          entry=entry, payload=_PAYLOAD.encode("utf-8"))
    value = decoded(result)
    assert (value["root"], value["tooling"], value["payload"]) == (str(root), str(selected.root), _PAYLOAD)
    assert value["non_interactive"] is True
    assert str(root).encode() in result.stderr


def test_native_text(launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox) -> None:
    """Native argument text reaches production dispatch without a shell parser."""
    root = git_sandbox.home / "B"
    result = launcher_tooling.run(["probe", "--project-root", str(root), "--text", _PAYLOAD],
                                  sandbox=git_sandbox, cwd=root)
    assert decoded(result)["payload"] == _PAYLOAD


def test_fixture_registry_is_not_shipped() -> None:
    """No production operation or environment setting activates test handlers."""
    assert not {"probe", "required", "fail", "wait"}.intersection(SHIPPED_HANDLERS)


# eof
