"""Integrated input, stream and status transport through production bootstrap.

Step 6 (2026-11-02), under the user's simulation-only test rule: every entry
kind and both tooling copies carry a relative payload resolved against the
project root while a build step changes directory, refuse invalid UTF-8
before dispatch, write non-ASCII UTF-8/LF streams and normalize a child
status 7 to the public 1. The caller's environment object is never changed.
Batch codepage, ``setlocal`` and cwd restoration stay source contracts of the
launcher tests; real cmd, PowerShell and console runs belong to the host probe.
Step 1 of v0.14.0 version-sources: a handler's status 3 (incomplete
restoration) reaches the caller unchanged, with its diagnostic, and the five
typed release observations of a handler's Git context are answered from the
sandbox's declared release history.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.acceptance_support import snapshot
from tools.release_workflow import cli
from tools.release_workflow.results import OperationResult

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.launcher_simulation import ToolingSimulation
    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox
    from tools.release_workflow.invocation import InvocationContext

_INVALID = 2
_FAILED = 1
_RESTORATION_INCOMPLETE = 3
_PAYLOAD = "Prêt pour la version 1.2.3\n"


def _selected(*, alternate: bool, launcher_tooling: ToolingSimulation, alternate_launcher_tooling: ToolingSimulation) -> ToolingSimulation:
    """Choose the designated tooling copy for one matrix row."""
    return alternate_launcher_tooling if alternate else launcher_tooling


@pytest.mark.parametrize("entry", ["explicit-native", "explicit-batch", "alias-batch"])
@pytest.mark.parametrize("alternate", [False, True])
def test_relative_payload_survives_a_build_directory_change(*, entry: str, alternate: bool,  # noqa: PLR0913 - fixture matrix
                                                            launcher_tooling: ToolingSimulation, alternate_launcher_tooling: ToolingSimulation,
                                                            git_sandbox: GitSandbox, consumers: tuple[Path, Path],
                                                            acceptance_registry: dict[str, cli.Handler]) -> None:
    """The input path is frozen against the project root before the build moves cwd."""
    root = consumers[1].resolve()
    (root / "notes").mkdir()
    (root / "notes" / "input.txt").write_bytes(_PAYLOAD.encode("utf-8"))
    arguments = ["build", "--input-file", "notes/input.txt"]
    if entry != "alias-batch":
        arguments += ["--project-root", str(root)]
    environment = dict(git_sandbox.environment)
    tooling = _selected(alternate=alternate, launcher_tooling=launcher_tooling, alternate_launcher_tooling=alternate_launcher_tooling)
    result = tooling.run(arguments, sandbox=git_sandbox, cwd=root / "sub", entry=entry, environment=environment,
                         handlers=acceptance_registry)
    assert (result.returncode, result.stdout) == (0, _PAYLOAD.encode("utf-8")), result.stderr
    assert environment == dict(git_sandbox.environment)


@pytest.mark.parametrize("entry", ["explicit-native", "explicit-batch"])
def test_invalid_utf8_payload_fails_before_dispatch(entry: str, launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                                    consumers: tuple[Path, Path], acceptance_registry: dict[str, cli.Handler]) -> None:
    """Undecodable input is a preflight failure; the locked write never starts."""
    root = consumers[0]
    (root / "input.txt").write_bytes(b"notes \xff\xfe\n")
    before = snapshot(git_sandbox.home)
    result = launcher_tooling.run(["write", "--project-root", str(root), "--input-file", "input.txt"], sandbox=git_sandbox,
                                  cwd=git_sandbox.home, entry=entry, handlers=acceptance_registry)
    assert result.returncode == _INVALID
    assert b"Release preflight failed: Cannot read input file" in result.stderr
    assert not result.stdout
    assert snapshot(git_sandbox.home) == before


@pytest.mark.parametrize(("command", "status"), [("describe", 0), ("native", _FAILED), ("publish", _INVALID)])
@pytest.mark.parametrize("entry", ["explicit-native", "explicit-batch", "alias-batch"])
def test_public_status_and_utf8_streams(*, command: str, status: int, entry: str, launcher_tooling: ToolingSimulation,  # noqa: PLR0913 - fixture matrix
                                        git_sandbox: GitSandbox, consumers: tuple[Path, Path],
                                        acceptance_registry: dict[str, cli.Handler]) -> None:
    """Only 0, 1 or 2 reach the caller; output stays UTF-8 with LF line ends."""
    root = consumers[0].resolve()
    arguments = [command] if entry == "alias-batch" else [command, "--project-root", str(root)]
    result = launcher_tooling.run(arguments, sandbox=git_sandbox, cwd=root / "sub", entry=entry, handlers=acceptance_registry)
    assert result.returncode == status, result.stderr
    assert b"\r" not in result.stdout + result.stderr
    if command == "native":
        assert result.stdout == "partial résumé\n".encode()
        assert "child build failed: échec\n".encode() in result.stderr
        assert b"native status 7; returning 1" in result.stderr
    elif command == "publish":
        assert not result.stdout


def _incomplete_restoration(_context: InvocationContext) -> OperationResult:
    """Report a restoration that kept an original copy, as status 3."""
    return OperationResult(_RESTORATION_INCOMPLETE, diagnostics=("Restoration incomplete: version.txt kept as evidence",))


@pytest.mark.parametrize("entry", ["explicit-native", "explicit-batch", "alias-batch"])
def test_incomplete_restoration_status_passes_through(entry: str, launcher_tooling: ToolingSimulation,
                                                      git_sandbox: GitSandbox, consumers: tuple[Path, Path]) -> None:
    """Status 3 is public: neither the renderer nor the bootstrap turns it into 1."""
    root = consumers[0].resolve()
    arguments = ["restore"] if entry == "alias-batch" else ["restore", "--project-root", str(root)]
    result = launcher_tooling.run(arguments, sandbox=git_sandbox, cwd=root / "sub", entry=entry,
                                  handlers={"restore": cli.Handler(_incomplete_restoration)})
    assert result.returncode == _RESTORATION_INCOMPLETE, result.stderr
    assert b"Restoration incomplete: version.txt kept as evidence\n" in result.stderr
    assert b"returning 1" not in result.stderr


def _release_observations(context: InvocationContext) -> OperationResult:
    """Print what each typed release observation of the handler's Git context answers."""
    git, root = context.git, context.project.root
    lines = (
        " ".join(tag.name for tag in git.tag_records(cwd=root, merged="HEAD")),
        " ".join(git.independent_commits(["c1", "c2"], cwd=root)),
        " ".join(git.tag_names(cwd=root, merged="HEAD", not_merged="refs/tags/v0.1.0")),
        str(git.commit_count("refs/tags/v0.1.0..HEAD", cwd=root)),
        " ".join(git.listing(cwd=root)),
    )
    return OperationResult(data="\n".join(lines) + "\n")


def test_release_observations_reach_the_declared_history(launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                                         consumers: tuple[Path, Path]) -> None:
    """Through the real bootstrap, no observation starts Git: the sandbox history answers each one."""
    history = git_sandbox.verified_git.facts.history
    first = history.commit("c1")
    history.head = history.commit("c2", first)
    history.tag("v0.1.0", first, "Release 0.1.0\n")
    history.tag("v0.2.0", history.head)
    history.names = ("version.txt",)
    root = consumers[0].resolve()
    result = launcher_tooling.run(["releases", "--project-root", str(root)], sandbox=git_sandbox, cwd=root / "sub",
                                  handlers={"releases": cli.Handler(_release_observations)})
    assert result.returncode == 0, result.stderr
    assert result.stdout == b"v0.1.0 v0.2.0\nc2\nv0.2.0\n1\nversion.txt\n"
    assert [call[0] for call in history.calls] == ["tag_records", "independent_commits", "tag_names", "commit_count", "listing"]


def test_process_environment_is_left_alone(launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                           consumers: tuple[Path, Path], acceptance_registry: dict[str, cli.Handler]) -> None:
    """The engine reads a frozen copy; the process environment keeps every entry."""
    before = dict(os.environ)
    result = launcher_tooling.run(["describe", "--project-root", str(consumers[0])], sandbox=git_sandbox,
                                  cwd=git_sandbox.home, environment=dict(git_sandbox.environment, PRJ_DIR=str(consumers[1])),
                                  handlers=acceptance_registry)
    assert result.returncode == 0, result.stderr
    assert dict(os.environ) == before


# eof
