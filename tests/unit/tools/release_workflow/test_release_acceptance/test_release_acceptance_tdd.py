"""Integrated acceptance of the release foundation through production bootstrap.

Step 6 (2026-11-02), under the user's simulation-only test rule: projects A
and B, linked and nested worktrees, selected and alternate tooling, stale
inherited environments, current-directory shadows and readiness failures run
through bootstrap, readiness, dispatch and invocation with data-only
interpreter and repository ports. Every failed or read-only call leaves the
consumer and tooling trees byte-identical; a mutation writes only its managed
target and the prepared artifact home. Real launcher, console and process
evidence comes from the separate host probe, outside pytest.

Step 9 of v0.14.0 version-sources ships exactly `version` and `versions`; the
acceptance handler names stay unavailable through production bootstrap, and
an installed launcher's `version` on a project without `version.txt` returns
its status 2 without any fallback.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, cast

import pytest

from tests.unit.tools.release_workflow.acceptance_support import (
    TARGET,
    VERSION,
    CallerOutcome,
    build_caller,
    consumer,
    handlers,
    snapshot,
)
from tests.unit.tools.release_workflow.launcher_simulation import (
    HANDLERS,
    ToolingSimulation,
    decoded,
)
from tools.release_workflow import bootstrap, cli

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from tests.unit.tools.release_workflow.acceptance_support import LockFacts
    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox

_INVALID = 2
_FAILED = 1
_LEGACY = ("PRJ_DIR", "PRJ_DIR_UNIX", "PRJ_DIR_NAME", "VERSION_TXT_FILE", "POM_FILE",
           "PACKAGE_JSON_FILE", "HEADER_CHANGELOG_FILE", "DEV_WORKFLOW_DIR")
_ACCEPTANCE_NAMES = ("build", "describe", "native", "write", "write-interrupted")


@pytest.mark.parametrize("project", ["A", "B", "A/nested", "linked"])
@pytest.mark.parametrize("entry", ["explicit-native", "explicit-batch", "alias-batch"])
def test_every_root_derives_its_own_locations(project: str, entry: str, launcher_tooling: ToolingSimulation,
                                              git_sandbox: GitSandbox, acceptance_registry: dict[str, cli.Handler]) -> None:
    """Explicit and alias entries reach the same physical root and its six locations."""
    if project == "linked":
        git_sandbox.linked_worktree()
    root = consumer(git_sandbox.home / project).resolve()
    if entry == "alias-batch":
        arguments, cwd = ["describe"], root / "build"
    else:
        arguments, cwd = ["describe", "--project-root", str(root)], git_sandbox.home
    value = decoded(launcher_tooling.run(arguments, sandbox=git_sandbox, cwd=cwd, entry=entry,
                                         handlers=acceptance_registry))
    assert (value["root"], value["posix"], value["name"], value["version"]) == (str(root), root.as_posix(), root.name, VERSION)
    assert (value["pom"], value["package"], value["changelog"], value["workflow"]) == (
        str(root / "pom.xml"), str(root / "package.json"), str(root / "changelog-header.md"),
        str(root / "tools" / "dev_workflow"),
    )
    assert value["tooling"] == str(launcher_tooling.root)


@pytest.mark.parametrize("alternate", [False, True])
def test_stale_inherited_environment_has_no_authority(*, alternate: bool, launcher_tooling: ToolingSimulation,  # noqa: PLR0913 - fixture matrix
                                                      alternate_launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                                      consumers: tuple[Path, Path], acceptance_registry: dict[str, cli.Handler]) -> None:
    """Legacy locations naming A never redirect B, reach Git or change either tree."""
    stale, selected = (path.resolve() for path in consumers)
    (stale / "version.txt").write_text("9.9.9-stale\n", encoding="utf-8")
    environment = dict(git_sandbox.environment, RELEASE_PROJECT=str(selected), PYTHONPATH=str(stale),
                       VIRTUAL_ENV=str(stale / "venvs" / "other"),
                       **{name: str(stale / name.lower()) for name in _LEGACY})
    environment["PRJ_DIR"] = str(stale)
    tooling = alternate_launcher_tooling if alternate else launcher_tooling
    before = snapshot(git_sandbox.home), snapshot(tooling.root)
    value = decoded(tooling.run(["describe", "--project-root-env", "RELEASE_PROJECT"], sandbox=git_sandbox,
                                cwd=stale / "sub", environment=environment, handlers=acceptance_registry))
    assert (value["root"], value["version"], value["tooling"]) == (str(selected), VERSION, str(tooling.root))
    diagnostics, child_environment = cast("list[str]", value["diagnostics"]), cast("list[str]", value["child_environment"])
    assert f"Ignored stale PRJ_DIR={stale}; validated project root is {selected}" in diagnostics
    assert not set(_LEGACY).intersection(child_environment)
    assert (snapshot(git_sandbox.home), snapshot(tooling.root)) == before


def test_stale_interpreter_is_refused_without_writes(launcher_tooling: ToolingSimulation,
                                                     alternate_launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                                     consumers: tuple[Path, Path], acceptance_registry: dict[str, cli.Handler]) -> None:
    """Another checkout's interpreter cannot run this checkout's engine."""
    stale = ToolingSimulation(launcher_tooling.root, alternate_launcher_tooling.identity)
    before = snapshot(git_sandbox.home), snapshot(launcher_tooling.root), snapshot(alternate_launcher_tooling.root)
    result = stale.run(["write", "--project-root", str(consumers[0]), "--input-stdin"], sandbox=git_sandbox,
                       cwd=git_sandbox.home, payload=b"never written", handlers=acceptance_registry)
    assert result.returncode == _INVALID
    assert b"Release readiness failed" in result.stderr
    assert not result.stdout
    assert (snapshot(git_sandbox.home), snapshot(launcher_tooling.root), snapshot(alternate_launcher_tooling.root)) == before


def test_current_directory_shadows_are_never_loaded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                    bootstrap_state: None) -> None:
    """Helpers load from the bootstrap's own directory, whatever cwd and sys.path hold."""
    del bootstrap_state
    shipped = {name: bootstrap.helper(name).__file__ for name in ("runtime_identity", "markers", "readiness")}
    shadow = tmp_path / "shadow"
    for directory in (shadow, shadow / "tools" / "release_workflow"):
        directory.mkdir(parents=True, exist_ok=True)
        for name in shipped:
            (directory / f"{name}.py").write_text("raise RuntimeError('shadow imported')\n", encoding="utf-8")
    monkeypatch.chdir(shadow)
    monkeypatch.setattr(sys, "path", [str(shadow), *sys.path])
    assert {name: bootstrap.helper(name).__file__ for name in shipped} == shipped


@pytest.mark.parametrize(("case", "status"), [
    ("read-only", 0), ("unavailable", _INVALID), ("missing-input", _INVALID),
    ("absent-root", _INVALID), ("non-repository", _INVALID),
])
def test_failed_and_read_only_calls_write_nothing(case: str, status: int, launcher_tooling: ToolingSimulation,  # noqa: PLR0913 - fixture matrix
                                                  git_sandbox: GitSandbox, consumers: tuple[Path, Path],
                                                  acceptance_registry: dict[str, cli.Handler]) -> None:
    """Consumers, ignored output, legacy scratch and tooling stay byte-identical."""
    project = consumers[0]
    outside = git_sandbox.home / "outside"
    outside.mkdir()
    arguments = {
        "read-only": ["describe", "--project-root", str(project)],
        "unavailable": ["publish", "--project-root", str(project)],
        "missing-input": ["write", "--project-root", str(project)],
        "absent-root": ["write", "--project-root", str(git_sandbox.home / "absent"), "--input-stdin"],
        "non-repository": ["write", "--project-root", str(outside), "--input-stdin"],
    }[case]
    before = snapshot(git_sandbox.home), snapshot(launcher_tooling.root)
    result = launcher_tooling.run(arguments, sandbox=git_sandbox, cwd=git_sandbox.home, payload=b"never written",
                                  handlers=acceptance_registry)
    assert result.returncode == status, result.stderr
    assert (snapshot(git_sandbox.home), snapshot(launcher_tooling.root)) == before


def test_mutation_writes_only_its_target_and_home(launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                                  consumers: tuple[Path, Path], acceptance_registry: dict[str, cli.Handler]) -> None:
    """A locked write adds the managed file and prepared home, and nothing else."""
    project, other = consumers
    before, other_before, tooling_before = snapshot(project), snapshot(other), snapshot(launcher_tooling.root)
    result = launcher_tooling.run(["write", "--project-root", str(project), "--input-stdin"], sandbox=git_sandbox,
                                  cwd=git_sandbox.home, payload="Notes é\n".encode(), handlers=acceptance_registry)
    assert (result.returncode, result.stdout) == (0, f"wrote {TARGET}\n".encode())
    after = snapshot(project)
    assert {key: value for key, value in after.items() if key not in before} == {
        ".reviews": None, ".reviews/.gitignore": b"*\n", TARGET: "Notes é\n".encode(),
    }
    assert {key: after[key] for key in before} == before
    assert (snapshot(other), snapshot(launcher_tooling.root)) == (other_before, tooling_before)


@pytest.mark.parametrize("name", _ACCEPTANCE_NAMES)
def test_shipped_registry_rejects_acceptance_names(name: str, launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox,
                                                   lock_facts: LockFacts) -> None:
    """Only in-process injection reaches the acceptance handlers; production ships the version pair only."""
    assert set(handlers(lock_facts)) == set(_ACCEPTANCE_NAMES)
    assert set(cli.SHIPPED_HANDLERS) == {"version", "versions"}
    result = launcher_tooling.run([name, "--project-root", str(git_sandbox.home / "B")], sandbox=git_sandbox,
                                  cwd=git_sandbox.home, handlers=None)
    assert result.returncode == _INVALID
    assert b"unavailable in this tooling checkout" in result.stderr


@pytest.mark.parametrize(("installed", "arguments", "expected"), [
    (False, ("package",), CallerOutcome(0, VERSION, ("release_workflow.bat is missing; using the local version",))),
    (False, ("package", "--mode", "SNAPSHOT"), CallerOutcome(_FAILED, warnings=(
        "release_workflow.bat is missing; release and snapshot need the release tooling",))),
    (False, ("Release",), CallerOutcome(_FAILED, warnings=(
        "release_workflow.bat is missing; release and snapshot need the release tooling",))),
    (True, ("version",), CallerOutcome(_INVALID)),
    (True, ("fail",), CallerOutcome(_FAILED)),
    (True, ("probe",), CallerOutcome(0)),
])
def test_missing_launcher_caller_contract(*, installed: bool, arguments: tuple[str, ...], expected: CallerOutcome,  # noqa: PLR0913 - fixture matrix
                                          tmp_path: Path, launcher_tooling: ToolingSimulation, git_sandbox: GitSandbox) -> None:
    """Absence is the launcher file, never a status; an installed 1 or 2 propagates."""
    launcher = tmp_path / "bin" / "release_workflow.bat"
    if installed:
        launcher.parent.mkdir()
        launcher.write_text("@echo off\n", encoding="ascii")
    calls: list[tuple[str, ...]] = []

    def run(_launcher: Path, supplied: Sequence[str]) -> int:
        calls.append(tuple(supplied))
        registry = None if supplied[0] == "version" else HANDLERS
        return launcher_tooling.run([*supplied, "--project-root", str(git_sandbox.home / "B")], sandbox=git_sandbox,
                                    cwd=git_sandbox.home, handlers=registry).returncode

    outcome = build_caller(launcher, arguments, run=run, local_version=lambda: VERSION)
    assert outcome == expected
    assert calls == ([arguments] if installed else [])


# eof
