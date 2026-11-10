"""Observe every pytest launch with finite selections and no real processes.

Preparation refreshes live sources without importing policies, preserves the
consumer interpreter and restores the parent before output is consumed.
"""

from __future__ import annotations

import os
import sys
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.groundhog_acceptance_support import (
    QueueSpawns,
    make_deps,
    passing_transcript,
)
from tools import pytest_plugin_environment as env
from tools.groundhog import (
    commands,
    group_coverage,
    pytest_environment,
    runner,
    selection,
)
from tools.groundhog.context import Deps, Invocation
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import EXIT_SETUP_ERROR, Mode
from tools.scope_capture import WHOLE_SCOPE, ScopeKind

if TYPE_CHECKING:
    import subprocess
    from collections.abc import Mapping

_PROBE_COUNT = 2


def _consumer_pytest(_name: str) -> str:
    """Keep interpreter lookup independent of shared launcher activation."""
    return "consumer/venv/pytest"


def _assert_activation(child: Mapping[str, str], expected: Mapping[str, str], project: Path, shared: Path, selected: str) -> None:
    """Compare the child activation with the shared builder's exact result."""
    for key in (env.SELECTION, env.ROOT, env.POLICY_DIR, "PYTHONPATH", "PYTEST_ADDOPTS"):
        assert child.get(key) == expected.get(key)
    if selected:
        assert child[env.ROOT] == str(project.resolve())
        assert child[env.POLICY_DIR] == str(shared / "tools" / "pytest_plugins")


def _activation_parent(monkeypatch: pytest.MonkeyPatch, incoming: Mapping[str, str]) -> dict[str, str]:
    """Supply a clean activation boundary and retain the exact parent state."""
    for key in (env.SELECTION, env.ROOT, env.POLICY_DIR, "PYTHONPATH", "PYTEST_ADDOPTS"):
        monkeypatch.delenv(key, raising=False)
    for key, value in incoming.items():
        monkeypatch.setenv(key, value)
    return dict(os.environ)


def _run_stage(stage: str, project: Path, deps: Deps) -> None:
    """Exercise one actual command or both actual collection boundaries."""
    sub = "full" if stage == "parallel" else stage
    if stage == "parallel":
        (project / runner.PARALLEL_MARKER).touch()
    invocation = Invocation(sub, ("focus.py",), no_cov=True, mode=Mode.LLM, root=project, level=FullLevel.PASS)
    if stage == "probes":
        assert selection.counts(invocation, deps) == (1, 2)
    else:
        assert commands.run_tests_outcome(invocation, deps).code == 0


def _assert_stage_children(stage: str, observed: list[dict[str, str]], prepared: list[dict[str, str]], spawns: QueueSpawns) -> None:
    """Verify spawn count and the full-run worker limit separately from activation."""
    assert len(prepared) == len(observed) == (_PROBE_COUNT if stage == "probes" else 1)
    if stage == "parallel":
        assert int(observed[0][runner.AUTO_WORKERS_VARIABLE]) <= runner.MAX_AUTO_WORKERS
        assert "-n" in spawns.commands[0]


@pytest.fixture
def layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Supply literal contracts whose executable bodies must never run here."""
    project, shared, cache = (tmp_path / name for name in ("project", "shared", "cache"))
    project.mkdir()
    policy = shared / "tools" / "pytest_plugins"
    policy.mkdir(parents=True)
    for name in (env.LOADER, *env.POLICIES.values()):
        (policy / f"{name}.py").write_text("LOADER_CONTRACT_VERSION = 1\nraise RuntimeError('policy imported')\n", encoding="utf-8")
    return project, shared, cache


@pytest.mark.parametrize("selected", ["", "lifecycle", "process", "lifecycle,process"])
@pytest.mark.parametrize("stage", ["affected", "single", "timings", "full", "parallel", "probes"])
def test_every_stage_prepares_its_child(
    layout: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch, selected: str, stage: str,
) -> None:
    """The real builder shapes each observed child and never alters its parent."""
    project, shared, cache = layout
    incoming = {env.SELECTION: selected, "PYTHONPATH": "consumer", "PYTEST_ADDOPTS": "-q"}
    parent = _activation_parent(monkeypatch, incoming)
    prepared: list[dict[str, str]] = []
    observed: list[dict[str, str]] = []

    def prepare(root: Path, environment: Mapping[str, str]) -> dict[str, str]:
        assert root == project
        assert dict(os.environ) == parent
        result = env.prepare_environment(root, shared, environment, cache_root=cache)
        prepared.append(result)
        return result

    children = [(["collected 2 items"], 0), (["collected 1 item"], 0)] if stage == "probes" else [(passing_transcript(1, None), 0)]
    spawns = QueueSpawns(children)

    def factory(command: list[str], cwd: Path) -> subprocess.Popen[str]:
        assert command[0] == "consumer/venv/pytest"
        observed.append(dict(os.environ))
        return spawns(command, cwd)

    deps = replace(make_deps(spawns, incoming), popen_factory=factory, prepare_pytest=prepare,
                   which=_consumer_pytest)
    modules = set(sys.modules)
    _run_stage(stage, project, deps)
    _assert_stage_children(stage, observed, prepared, spawns)
    for child, expected in zip(observed, prepared, strict=True):
        _assert_activation(child, expected, project, shared, selected)
    assert dict(os.environ) == parent
    assert not (set(env.POLICIES.values()) & (set(sys.modules) - modules))


@pytest.mark.parametrize("selected", ["lifecycle", ""])
def test_same_root_refresh_and_deselection(
    layout: tuple[Path, Path, Path], selected: str,
) -> None:
    """Same-root stale activation is rebuilt, including complete removals."""
    project, shared, cache = layout
    old = env.prepare_environment(project, shared, {env.SELECTION: "process"}, cache_root=cache)
    old[env.SELECTION] = selected
    old[env.POLICY_DIR] = str(shared / "old-policies")
    old["PYTHONPATH"] = old["PYTHONPATH"].replace(str(shared / "tools" / "pytest_plugins"), str(shared / "old-policies"))

    def prepare(root: Path, environment: Mapping[str, str]) -> dict[str, str]:
        return env.prepare_environment(root, shared, environment, cache_root=cache)

    invocation = Invocation("single", (), no_cov=True, mode=Mode.LLM, root=project)
    delta = pytest_environment.child_environment(invocation, replace(make_deps(QueueSpawns([]), old), prepare_pytest=prepare))
    refreshed = {key: value for key, value in {**old, **delta}.items() if value is not None}
    if selected:
        assert refreshed[env.POLICY_DIR] == str(shared / "tools" / "pytest_plugins")
        assert refreshed[env.SELECTION] == selected
        assert str(shared / "old-policies") not in refreshed["PYTHONPATH"]
    else:
        assert all(delta[key] is None for key in (env.SELECTION, env.ROOT, env.POLICY_DIR, "PYTEST_ADDOPTS", "PYTHONPATH"))


@pytest.mark.parametrize("sub", ["affected", "single", "timings", "full"])
def test_stage_rechecks_binding_before_spawn(tmp_path: Path, sub: str) -> None:
    """Direct stage calls cannot use another project's activation."""
    spawns = QueueSpawns([])
    deps = make_deps(spawns, {env.ROOT: str(tmp_path / "other")})
    invocation = Invocation(sub, (), no_cov=True, mode=Mode.LLM, root=tmp_path)
    assert commands.run_tests_outcome(invocation, deps).code == EXIT_SETUP_ERROR
    assert spawns.commands == []


@pytest.mark.parametrize("failed_probe", [0, 1])
@pytest.mark.parametrize("failure", ["binding", "preparation", "io"])
def test_probe_setup_errors_never_fall_back(tmp_path: Path, failed_probe: int, failure: str) -> None:
    """Either probe fails closed even when ordinary unavailable evidence falls back."""
    variables: dict[str, str] = {}
    spawns = QueueSpawns([(["collected 2 items"], 0)])
    calls = 0

    def prepare(_root: Path, environment: Mapping[str, str]) -> dict[str, str]:
        nonlocal calls
        if calls == failed_probe and failure != "binding":
            message = "preparation failed"
            raise (OSError(message) if failure == "io" else env.PreparationError(message))
        calls += 1
        if failure == "binding":
            variables[env.ROOT] = str(tmp_path / "other")
        return dict(environment)

    if failure == "binding" and failed_probe == 0:
        variables[env.ROOT] = str(tmp_path / "other")
    deps = replace(make_deps(spawns), environ=variables.get, prepare_pytest=prepare)
    invocation = Invocation("day", (), no_cov=True, mode=Mode.LLM, root=tmp_path)
    with pytest.raises(env.PreparationError):
        selection.counts(invocation, deps)
    assert len(spawns.commands) == failed_probe


def test_default_adapter_uses_its_own_checkout(tmp_path: Path) -> None:
    """The default preparation resolves the implementation sources locally."""
    project = tmp_path / "project"
    project.mkdir()
    result = pytest_environment.prepare(project, {env.SELECTION: "process", "LOCALAPPDATA": str(tmp_path / "local")})
    assert result[env.POLICY_DIR] == str(Path(pytest_environment.__file__).resolve().parents[2] / "tools" / "pytest_plugins")


def test_coverage_and_explicit_worker_settings_survive_preparation(tmp_path: Path) -> None:
    """Activation composes with coverage isolation and a caller's worker limit."""
    variables = {runner.AUTO_WORKERS_VARIABLE: "1"}
    deps = make_deps(QueueSpawns([]), variables)
    invocation = Invocation("full", (), no_cov=False, mode=Mode.LLM, root=tmp_path)
    coverage = tmp_path / "group.coverage"
    delta = pytest_environment.child_environment(invocation, deps, (coverage, 0.0), parallel=True)
    assert delta["COVERAGE_FILE"] == str(coverage)
    assert runner.AUTO_WORKERS_VARIABLE not in delta


def test_binding_normalizes_same_root_and_non_pytest_commands_ignore_it(tmp_path: Path) -> None:
    """Whole-root equality accepts lexical normalization and Windows casing."""
    spelling = str(tmp_path / "child" / "..")
    pytest_environment.validate_binding(tmp_path, {env.ROOT: spelling.upper() if os.name == "nt" else spelling}.get)
    deps = make_deps(QueueSpawns([]), {env.ROOT: str(tmp_path / "other")})
    for sub in ("check", "status", "init", "exclude", "groups"):
        pytest_environment.validate_invocation(Invocation(sub, (), no_cov=True, mode=Mode.LLM, root=tmp_path), deps)
    unbound = Invocation("affected", (), no_cov=True, mode=Mode.LLM, root=tmp_path)
    assert pytest_environment.child_environment(unbound, make_deps(QueueSpawns([]))) == {}


@pytest.mark.parametrize("sub", ["affected", "single", "timings", "full"])
def test_selected_preparation_failure_stops_before_spawn(tmp_path: Path, sub: str) -> None:
    """Invalid selection cannot reach any pytest child or mutate the parent."""
    spawns = QueueSpawns([])
    deps = make_deps(spawns, {env.SELECTION: "unknown"})
    before = dict(os.environ)
    invocation = Invocation(sub, (), no_cov=True, mode=Mode.LLM, root=tmp_path)
    assert commands.run_tests_outcome(invocation, deps).code == EXIT_SETUP_ERROR
    assert spawns.commands == []
    assert dict(os.environ) == before


@pytest.mark.parametrize("grouped", [False, True])
def test_full_preparation_failure_preserves_existing_evidence(tmp_path: Path, *, grouped: bool) -> None:
    """A setup refusal preserves dependency and group coverage data before spawn."""
    dependency_map = tmp_path / runner.TESTMON_DATA_FILE
    coverage_data = group_coverage.data_file(tmp_path, "activation")
    for path in (dependency_map, coverage_data):
        path.write_bytes(b"existing evidence")
    scope = replace(WHOLE_SCOPE, kind=ScopeKind.GROUP, name="activation") if grouped else WHOLE_SCOPE
    invocation = Invocation("full", (), no_cov=False, mode=Mode.LLM, root=tmp_path, level=FullLevel.COV, scope=scope)
    spawns = QueueSpawns([])
    deps = make_deps(spawns, {env.SELECTION: "unknown"})

    assert commands.run_tests_outcome(invocation, deps).code == EXIT_SETUP_ERROR

    assert spawns.commands == []
    for path in (dependency_map, coverage_data):
        assert path.read_bytes() == b"existing evidence"


def test_unavailable_probe_cannot_skip_later_preparation(tmp_path: Path) -> None:
    """An ordinary probe spawn failure leaves the actual stage preflight intact."""
    preparations = 0
    launches = 0

    def prepare(_root: Path, inherited: Mapping[str, str]) -> dict[str, str]:
        nonlocal preparations
        preparations += 1
        if preparations > 1:
            message = "source changed after unavailable probe"
            raise env.PreparationError(message)
        return dict(inherited)

    def unavailable(_command: list[str], _cwd: Path) -> subprocess.Popen[str]:
        nonlocal launches
        launches += 1
        message = "unavailable probe"
        raise OSError(message)

    deps = replace(make_deps(QueueSpawns([])), prepare_pytest=prepare, popen_factory=unavailable)
    invocation = Invocation("affected", (), no_cov=True, mode=Mode.LLM, root=tmp_path)
    assert selection.counts(invocation, deps) is None
    assert commands.run_tests_outcome(invocation, deps).code == EXIT_SETUP_ERROR
    assert preparations == _PROBE_COUNT
    assert launches == 1


# eof
