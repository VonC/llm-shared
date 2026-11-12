"""Join preparation, runner isolation, canonical loading and policy records.

The process factory executes a generated consumer in process, retaining the
runner's real environment boundary and result parser. Scratch resources use
the suite's memory filesystem; a local source adapter feeds generated Python
to the real import loader without native file opens or bytecode discovery.
Earlier unit/property suites own malformed declarations and finite branches.
The consumer declares the exact ignored-home contract used by real records.
An explicit configuration path and --noconftest avoid repeated discovery.
The supplied consumer hook registers strict settings; executable cases own
real conftest discovery. Generated test fixtures still run through pytest.
Separate project construction and record assertions keep the journey focused.
Environment assertions independently verify binding and parent restoration.
"""

from __future__ import annotations

import json
import os
from dataclasses import replace
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from tests.unit.tools.groundhog_acceptance_support import (
    FakeProcess,
    QueueSpawns,
    make_deps,
)
from tests.unit.tools.shared_lifecycle.inline_session import run_inline
from tools import pytest_plugin_environment as activation
from tools.groundhog import commands
from tools.groundhog.context import Invocation
from tools.groundhog.models import Mode
from tools.lifecycle_compatibility.scenarios import windows_caller
from tools.pytest_plugins import llm_shared_pytest_loader as loader

if TYPE_CHECKING:
    import subprocess
    from collections.abc import Mapping
    from types import CodeType

_CPU_LIMIT = 0.1
_UNUSED_PERMISSIONS = 2

_PROJECT = """import pytest

@pytest.fixture(scope="module")
def service(request):
    request.addfinalizer(lambda: None)
    yield "ready"

LLM_SHARED_PROCESS_FIXTURES = {service: "synthetic unused fixture permission"}

@pytest.mark.process_allowed(reason="synthetic unused test permission")
def test_consumer(service, pytestconfig):
    assert service == "ready"
    assert pytestconfig.getini("test_lifecycle_limit") == "0.1"
"""


class PreparedStartup:
    """Supply consumer settings and real bootstrap without conftest discovery."""

    def __init__(self, environment: Mapping[str, str], patch: pytest.MonkeyPatch) -> None:
        """Retain prepared values and the caller's scoped restoration helper."""
        self.environment = environment
        self.patch = patch

    def pytest_addoption(self, parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
        """Keep the documented consumer guard and all four registrations real."""
        if not pluginmanager.has_plugin("llm_shared_lifecycle_gate"):
            for key, default in {
                "test_lifecycle_limit": "0.1", "test_lifecycle_wall_limit": "1.0",
                "test_lifecycle_cpu_band_factor": "2.5", "test_lifecycle_cpu_drift_runs": "3",
            }.items():
                parser.addini(key, "lifecycle setting", default=default)

    @pytest.hookimpl(tryfirst=True)
    def pytest_load_initial_conftests(self, early_config: pytest.Config, args: list[str]) -> None:
        """Restore prepared values cleared by the generic embedded test helper."""
        for key in (activation.SELECTION, activation.ROOT, activation.POLICY_DIR):
            if key in self.environment:
                # run_inline owns restoration of the keys it cleared. A second
                # patch here would undo that restoration in the wrong order.
                os.environ[key] = self.environment[key]
        modules = loader.preflight(self.environment, args)
        self.patch.setattr(loader, "_PREFLIGHTED", modules)
        loader.pytest_load_initial_conftests(early_config, args)


def consumer_project(tmp_path: Path) -> Path:
    """Declare consumer resources without moving work outside the lifecycle."""
    project = tmp_path / "consumer"
    project.mkdir()
    for package in ("tools", "tests"):
        directory = project / package
        directory.mkdir()
        (directory / "__init__.py").write_text("raise AssertionError('consumer package imported')\n", encoding="utf-8")
    (project / "pytest.ini").write_text(
        "[pytest]\nmarkers =\n    process_allowed(reason): process permission\n", encoding="utf-8",
    )
    # Unused declarations must work even when neither policy is selected.
    (project / "test_consumer.py").write_text(_PROJECT, encoding="utf-8")
    home = project / ".reviews"
    home.mkdir()
    (home / ".gitignore").write_bytes(b"*\n")
    return project


def assert_consumer_record(home: Path, selected: str) -> None:
    """Only the selected gate writes a valid proof into the consumer home."""
    record = home / "a.test-lifecycle-cpu.local.json"
    assert record.exists() == ("lifecycle" in selected)
    if record.exists():
        node = json.loads(record.read_text(encoding="utf-8"))["nodes"]["test_consumer.py::test_consumer"]
        assert node["proven"]
        assert node["proven_cpu"] <= _CPU_LIMIT


def assert_consumer_environment(
    parent: Mapping[str, str], observed: Mapping[str, str], selected: str, project: Path, shared: Path,
) -> None:
    """Keep the parent's values intact and bind selected children to this root."""
    changed_keys = {key for key in parent.keys() | os.environ.keys() if parent.get(key) != os.environ.get(key)}
    assert not changed_keys
    if selected:
        assert observed[activation.ROOT] == str(project.resolve())
        assert observed[activation.POLICY_DIR] == str(shared / "tools" / "pytest_plugins")
        assert str(shared) not in observed["PYTHONPATH"].split(os.pathsep)


@pytest.mark.parametrize("selected", ["", "lifecycle", "process", "lifecycle,process"])
def test_prepared_groundhog_consumer_contract(
    tmp_path: Path, selected: str, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """All opt-ins preserve consumer packages, strict settings and parent state."""
    project = consumer_project(tmp_path)
    shared = Path(__file__).resolve().parents[4]
    observed: list[dict[str, str]] = []
    for key in (activation.SELECTION, activation.ROOT, activation.POLICY_DIR, "PYTHONPATH", "PYTEST_ADDOPTS"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv(activation.SELECTION, selected)
    parent = dict(os.environ)

    def prepare(root: Path, environment: Mapping[str, str]) -> dict[str, str]:
        return activation.prepare_environment(root, shared, environment, cache_root=tmp_path / "cache")

    def execute(_command: list[str], cwd: Path) -> subprocess.Popen[str]:
        observed.append(dict(os.environ))
        with pytest.MonkeyPatch.context() as patch:
            original_code = SourceFileLoader.get_code

            def consumer_code(source_loader: SourceFileLoader, fullname: str) -> CodeType | None:
                if Path(source_loader.path).is_relative_to(cwd):
                    return compile(Path(source_loader.path).read_bytes(), source_loader.path, "exec")
                return original_code(source_loader, fullname)

            patch.setattr(SourceFileLoader, "get_code", consumer_code)
            patch.setenv("PYTEST_CURRENT_TEST", os.environ["PYTEST_CURRENT_TEST"])
            code = run_inline(cwd, "-c", str(cwd / "pytest.ini"), "--noconftest", "--strict-config", "--strict-markers",
                              "-p", "no:monkeypatch", "-p", "no:recwarn", "-p", "no:stepwise",
                              "-p", "no:setupplan", "-p", "no:setuponly", "-p", "no:threadexception", "-p", "no:subtests",
                              plugins=(PreparedStartup(observed[-1], patch),))
        output = capsys.readouterr().out
        assert output.count("lifecycle CPU band") == int("lifecycle" in selected)
        assert output.count("process permissions") == int("process" in selected)
        if "process" in selected:
            assert output.count("WARNING unused") == _UNUSED_PERMISSIONS
        return cast("subprocess.Popen[str]", FakeProcess(output.splitlines(), code))

    deps = replace(make_deps(QueueSpawns([]), {activation.SELECTION: selected}),
                   prepare_pytest=prepare, popen_factory=execute)
    invocation = Invocation("single", (), no_cov=True, mode=Mode.LLM, root=project)
    assert commands.run_tests_outcome(invocation, deps).code == 0
    assert len(observed) == 1
    assert_consumer_environment(parent, observed[0], selected, project, shared)
    assert_consumer_record(project / ".reviews", selected)


def test_windows_probe_preserves_the_caller_boundary() -> None:
    """Executable probes observe both snapshots and the launcher's own verdict."""
    source = windows_caller()
    assert source.index("before") < source.index('call "%PROBE_LAUNCHER%"') < source.index("after")
    assert "setlocal" not in source
    assert 'set "PROBE_EXIT=%errorlevel%"' in source


# eof
