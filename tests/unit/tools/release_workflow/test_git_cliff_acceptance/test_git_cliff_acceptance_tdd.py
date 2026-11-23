"""Integrated acceptance of git-cliff provisioning against the shipped manifest: the rows Step 8 owns outside the gcliff ones.

Step 8 of v0.14.0 git-cliff-provisioning (design "Acceptance cases for the
git-cliff provisioning design", plan "Acceptance ownership map", requirement
acceptance criteria AC1 to AC3, AC5 and AC6). The rows run the production
bootstrap, configuration reader, launcher and provisioning service through
the launcher simulation, with the provisioning world as the cache, the
Windows layer and the children. A repair that downloads uses a synthetic
2.14.2 pin table whose archive the fake worker delivers.

- `.release.ini` without `[git-cliff]` and a valid cached 2.14.2: reused with
  nothing printed, no lock, no network.
- `version = 2.15.0`, `v2.14.2`, `latest` or `2.7.0` (the evidence baseline):
  a configuration error before any other work, listing the tested pins.
- A truncated executable or a missing `entry.json`: the entry is invalid
  without running it, then provisioned again online, or a diagnostic offline;
  a read-only checkout with a valid entry runs normally and writes nothing.
- Windows older than the baseline: the platform diagnostic before any child.
- An engine caller (a test-only handler calling `provision`, as `uc` or
  `brel` will) whose provisioning fails: status 2 with the stage diagnostic,
  the project unchanged.
- `version`, `versions check` and an ordinary configuration load import no
  `git_cliff` module but `manifest` and never read the budget variable. Since
  code review round 1, the command entry points and the modules they import
  lazily are imported once, at collection, from an unloaded release package
  (about 0.09 s of CPU, more than a test may spend), so an eager import below
  them is seen; each operation runs on those fresh modules, so a lazy import
  loads anew; and the budget variable's name is watched in the command
  environment and in `os.environ`, so even a lookup whose result is discarded
  is seen. A control proves that the watch sees a budget resolution and both
  lookups. Since code review round 2, `os.environ` is also watched during the
  collection-time import, and a control module that looks the variable up
  while it is imported proves that this watch records it too.
- A fresh checkout's first provisioning writes only below the ignored
  `.tools/git-cliff/`, so `git status` stays clean; checked on the produced
  paths and the root `.gitignore` rule, without Git.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import io
import os
import sys
from collections.abc import MutableMapping
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.acceptance_support import snapshot
from tests.unit.tools.release_workflow.gcliff_simulation import (
    GcliffScenario,
    gcliff_scenario,
)
from tests.unit.tools.release_workflow.git_cliff_children_fake import failed
from tests.unit.tools.release_workflow.git_cliff_support import (
    STAND_IN_EXECUTABLE,
    VERSION,
    deny_writes,
    synthetic_pin,
)
from tests.unit.tools.release_workflow.launcher_simulation import patch_git
from tests.unit.tools.release_workflow.version_support import (
    command_project,
    project_identity,
    version_txt,
)
from tools.release_workflow import cli
from tools.release_workflow.git_cliff.budget import (
    DOWNLOAD_BUDGET_VARIABLE,
    BudgetSettingError,
    resolve_budget,
)
from tools.release_workflow.git_cliff.manifest import ADMITTED_PINS, admitted
from tools.release_workflow.git_cliff.messages import ProvisioningError
from tools.release_workflow.git_cliff.provisioning import (
    configured_pin,
    provision,
    provisioning_budget,
)
from tools.release_workflow.results import OperationResult
from tools.release_workflow.runtime_identity import RuntimeIdentity
from tools.release_workflow.windows_child import PlatformError

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator, Mapping
    from types import ModuleType

    from tests.unit.tools.release_workflow.repository_simulation import GitSandbox
    from tools.release_workflow.invocation import InvocationContext

_UNAVAILABLE = 69
_SETUP = 2
_REPOSITORY = Path(__file__).resolve().parents[5]
_RELEASE_PACKAGE = "tools.release_workflow"
_PACKAGE = "tools.release_workflow.git_cliff"
_ALLOWED = frozenset({_PACKAGE, f"{_PACKAGE}.manifest"})
# The command entry points, and the modules they import lazily, imported fresh for the operations below.
_ENTRY_POINTS = (f"{_RELEASE_PACKAGE}.cli", f"{_RELEASE_PACKAGE}.invocation", f"{_RELEASE_PACKAGE}.configuration",
                 f"{_RELEASE_PACKAGE}.sources.model")


@pytest.fixture
def scenario(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, git_sandbox: GitSandbox) -> GcliffScenario:
    """A tooling checkout whose cache is still empty, with the shipped 2.14.2 as the pin."""
    return gcliff_scenario(tmp_path, monkeypatch, git_sandbox)


def _repairable(scenario: GcliffScenario) -> GcliffScenario:
    """Select from a synthetic 2.14.2 table, so a repair can download an archive the fake worker delivers."""
    scenario.world.pin = synthetic_pin(VERSION)
    scenario.pins = (scenario.world.pin,)
    return scenario


def test_a_valid_default_entry_is_reused_with_nothing_printed_no_lock_and_no_network(scenario: GcliffScenario) -> None:
    """`.release.ini` without `[git-cliff]` takes the manifest default and reuses its valid entry lock-free."""
    scenario.world.install()
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert (result.returncode, result.stderr, scenario.world.lines) == (0, b"", [])
    assert [launched.role for launched in scenario.world.children.launched] == ["probe", "run"]
    assert (scenario.world.mutex.entries, scenario.world.lock_record(), scenario.world.renames) == ([], None, [])


@pytest.mark.parametrize(("declared", "reason"), [
    ("2.15.0", b"not a tested git-cliff pin; tested: 2.14.2"),
    ("v2.14.2", b"expected an exact git-cliff version X.Y.Z"),
    ("latest", b"expected an exact git-cliff version X.Y.Z"),
    ("2.7.0", b"not a tested git-cliff pin; tested: 2.14.2"),
])
def test_an_untested_or_malformed_pin_is_a_configuration_error_before_any_work(declared: str, reason: bytes,
                                                                                scenario: GcliffScenario) -> None:
    """Only tested pins are accepted, the evidence-only 2.7.0 included; nothing is guarded, started or written."""
    scenario.world.install()
    files = scenario.world.tree()
    root = scenario.sandbox.home / "B"
    (root / ".release.ini").write_text(f"[git-cliff]\nversion = {declared}\n", encoding="utf-8")
    result = scenario.run("--version", cwd=root)
    assert result.returncode == _UNAVAILABLE
    assert f"[git-cliff] version={declared!r}".encode() in result.stderr
    assert reason in result.stderr
    assert (scenario.world.opener.opened, scenario.world.children.launched, scenario.world.tree()) == ([], [], files)


@pytest.mark.parametrize("damage", ["truncated", "record-missing"])
def test_a_damaged_entry_is_invalid_without_running_it_and_provisioned_again(damage: str, scenario: GcliffScenario) -> None:
    """No probe runs the damaged entry; the repair downloads, verifies, publishes and runs a whole executable."""
    world = _repairable(scenario).world
    world.install()
    if damage == "truncated":
        world.executable.write_bytes(STAND_IN_EXECUTABLE[:16])
    else:
        world.layout.record(world.pin).unlink()
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert result.returncode == 0
    assert [launched.role for launched in world.children.launched] == ["worker", "probe", "run"]
    assert world.children.of("probe")[0].request.executable != world.executable
    assert world.executable.read_bytes() == STAND_IN_EXECUTABLE


def test_a_damaged_entry_offline_is_the_download_diagnostic(scenario: GcliffScenario) -> None:
    """Offline, the repair fails at the download stage with its remedy, and git-cliff is not started."""
    world = _repairable(scenario).world
    world.install()
    world.executable.write_bytes(STAND_IN_EXECUTABLE[:16])
    world.children.script("worker", failed("fatal", "URLError: <urlopen error [Errno 11001] getaddrinfo failed>"))
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert result.returncode == _UNAVAILABLE
    assert b"(download stage)" in result.stderr
    assert b"HTTPS_PROXY" in result.stderr
    assert scenario.runs == []


def test_a_read_only_checkout_with_a_valid_entry_runs_normally_and_writes_nothing(scenario: GcliffScenario,
                                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """Reuse writes nothing: every write-capable call is refused and none is attempted."""
    scenario.world.install()
    denial = deny_writes(monkeypatch)
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert (result.returncode, denial.attempts) == (0, [])
    assert len(scenario.runs) == 1


def test_an_older_windows_is_the_platform_diagnostic_before_any_child(scenario: GcliffScenario) -> None:
    """Below Windows 10 or Windows Server 2016 x64, nothing is guarded, downloaded or started."""
    scenario.world.install()
    scenario.world.platform_error = PlatformError("Windows 6.3.9600 is below Windows 10")
    result = scenario.run("--version", cwd=scenario.sandbox.home / "B")
    assert result.returncode == _UNAVAILABLE
    assert b"(platform stage)" in result.stderr
    assert (scenario.world.opener.opened, scenario.world.children.launched) == ([], [])


def test_an_engine_caller_whose_provisioning_fails_returns_2_and_leaves_the_project_unchanged(scenario: GcliffScenario) -> None:
    """A test-only handler calling `provision`, as `uc` or `brel` will, maps the failure to status 2 with its stage."""
    world = _repairable(scenario).world
    world.children.script("worker", failed("fatal", "URLError: <urlopen error [Errno 11001] getaddrinfo failed>"))

    def render(context: InvocationContext) -> OperationResult:
        version = configured_pin(context.configuration)
        try:
            pin = None if version is None else admitted(version, scenario.pins)
            budget = provisioning_budget({}, tooling_root=context.runtime.root, pin=pin)
            invocation = provision(context.runtime.root, pin, budget, seams=world.seams(), caller="engine")
        except ProvisioningError as error:
            return OperationResult(error.exit_code, diagnostics=(f"render failed: {error}",))
        invocation.close()
        return OperationResult(0)

    root = scenario.sandbox.home / "B"
    before = snapshot(root)
    result = scenario.simulation.run(["render", "--project-root", str(root)], sandbox=scenario.sandbox, cwd=scenario.sandbox.home,
                                     handlers={"render": cli.Handler(render)})
    assert result.returncode == _SETUP
    assert b"render failed: git-cliff 2.14.2 unavailable at" in result.stderr
    assert b"(download stage)" in result.stderr
    assert snapshot(root) == before


def _modules_of(modules: Mapping[str, object], package: str) -> list[str]:
    """Name the modules of a package among named modules, the package included."""
    return [name for name in modules if name == package or name.startswith(f"{package}.")]


def _modules(package: str) -> list[str]:
    """Name the loaded modules of a package, the package included."""
    return _modules_of(sys.modules, package)


def _watched_name(name: str, reads: list[str]) -> str:
    """Spell a variable name that records every comparison with the budget variable's name, upper-cased or not.

    A lookup by that name compares it with the stored name, and the case-insensitive lookup of the release engine
    compares the stored name's `upper()` with it, so both are recorded, even when the looked-up value is discarded.
    """
    class _Watched(str):
        """The watched name; its reads are the closure's list."""

        __slots__ = ()

        def __eq__(self, other: object) -> bool:
            """Compare as a string, recording a comparison with the budget variable's name."""
            if isinstance(other, str) and str.upper(other) == DOWNLOAD_BUDGET_VARIABLE:
                reads.append(f"name compared with {other}")
            return str.__eq__(self, other)

        def __ne__(self, other: object) -> bool:
            """Compare as a string, recording like `==`."""
            return not self.__eq__(other)

        __hash__ = str.__hash__

        def upper(self) -> str:  # ty: ignore[invalid-method-override] - the watched spelling of a case-insensitive lookup
            """Keep watching the upper-case spelling a case-insensitive lookup compares."""
            return _Watched(str.upper(self))

    return _Watched(name)


class _WatchedEnvironment(MutableMapping[str, str]):
    """`os.environ` as Windows reads it, by upper-case names, recording each lookup of the budget variable."""

    def __init__(self, source: Mapping[str, str], reads: list[str]) -> None:
        """Copy the process environment and share the list of recorded reads."""
        self._values = {name.upper(): value for name, value in source.items()}
        self._reads = reads

    def __getitem__(self, name: str) -> str:
        """Look a name up as Windows does, recording the budget variable; `get` and `in` come here too."""
        if name.upper() == DOWNLOAD_BUDGET_VARIABLE:
            self._reads.append(f"os.environ lookup of {name}")
        return self._values[name.upper()]

    def __setitem__(self, name: str, value: str) -> None:
        """Set a variable."""
        self._values[name.upper()] = value

    def __delitem__(self, name: str) -> None:
        """Unset a variable."""
        del self._values[name.upper()]

    def __iter__(self) -> Iterator[str]:
        """Name every variable."""
        return iter(self._values)

    def __len__(self) -> int:
        """Count the variables."""
        return len(self._values)

    def copy(self) -> dict[str, str]:
        """Copy the variables, as `os.environ.copy()` does."""
        return dict(self._values)


def _watched_imports(names: tuple[str, ...], reads: list[str]) -> None:
    """Import modules while `os.environ` is the watch, so a budget lookup made at import time is recorded; restore it after."""
    environment = os.environ
    os.__dict__["environ"] = _WatchedEnvironment(environment, reads)
    try:
        for name in names:
            importlib.import_module(name)
    finally:
        os.__dict__["environ"] = environment


def _fresh_release_package(reads: list[str]) -> dict[str, ModuleType]:
    """Import the command entry points from a release package unloaded first, keep those fresh modules, restore the originals.

    It runs once, at collection: a fresh import costs about as much as a whole test may (about 0.09 s of CPU for 27
    modules), and every git-cliff module it loads is an eager import of the command path. Since code review round 2,
    `os.environ` is watched during that import, so a budget lookup at module import is recorded in `reads`.
    """
    tools = importlib.import_module("tools")
    package = importlib.import_module(_RELEASE_PACKAGE)
    original = {name: sys.modules[name] for name in _modules(_RELEASE_PACKAGE)}
    for name in original:
        del sys.modules[name]
    try:
        _watched_imports(_ENTRY_POINTS, reads)
        return {name: sys.modules[name] for name in _modules(_RELEASE_PACKAGE)}
    finally:
        for name in _modules(_RELEASE_PACKAGE):
            del sys.modules[name]
        sys.modules.update(original)
        vars(tools)["release_workflow"] = package


_IMPORT_READS: list[str] = []
_FRESH = _fresh_release_package(_IMPORT_READS)


@contextmanager
def _fresh_modules_installed(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """Run a block on the fresh release package in place of the loaded one; restore the loaded one at teardown.

    Modules a block imports for the first time are fresh too, and are dropped on exit.
    """
    tools = importlib.import_module("tools")
    monkeypatch.setattr(tools, "release_workflow", _FRESH[_RELEASE_PACKAGE])
    loaded = set(_modules(_RELEASE_PACKAGE))
    for name in loaded:
        monkeypatch.delitem(sys.modules, name)
    for name, module in _FRESH.items():
        monkeypatch.setitem(sys.modules, name, module)
    try:
        yield
    finally:
        for name in set(_modules(_RELEASE_PACKAGE)) - loaded - set(_FRESH):
            del sys.modules[name]


def _operate(operation: str, root: Path, sandbox: GitSandbox, environment: Mapping[str, str], monkeypatch: pytest.MonkeyPatch) -> int:
    """Run one operation from the freshly imported release package and return its status."""
    if operation == "configuration load":
        importlib.import_module(f"{_RELEASE_PACKAGE}.configuration").load_configuration(project_identity(root))
        return 0
    fresh_cli = importlib.import_module(f"{_RELEASE_PACKAGE}.cli")
    patch_git(monkeypatch, sandbox, importlib.import_module(f"{_RELEASE_PACKAGE}.git").GitExecutionContext)
    monkeypatch.setattr(fresh_cli, "stdin_is_console", lambda: False)
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return fresh_cli.main([*operation.split(), "--project-root", str(root)], entry_kind="explicit-native",
                              original_cwd=sandbox.home, runtime=RuntimeIdentity(sandbox.home, "venvs/prepared"),
                              environment=environment)


@pytest.mark.parametrize("operation", ["version", "versions check", "configuration load"])
def test_an_operation_without_git_cliff_imports_no_provisioning_and_never_looks_up_the_budget(
        operation: str, git_sandbox: GitSandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    """On a freshly imported release package, the operation loads only the manifest and never looks up the budget.

    Code review round 1 of Step 8: the command entry points and the modules they import lazily were imported again
    from an unloaded release package, so their eager imports are the git-cliff modules of that fresh package, and the
    operation runs on it, so a lazy import loads anew. The budget variable's name is watched in the command
    environment and in `os.environ`, so a lookup whose result is discarded is seen too.
    """
    root = command_project(git_sandbox, {"version.txt": version_txt("0.13.0")})
    reads: list[str] = []
    environment = {**git_sandbox.environment, _watched_name(DOWNLOAD_BUDGET_VARIABLE, reads): "-1"}
    monkeypatch.setattr(os, "environ", _WatchedEnvironment(os.environ, reads))
    with _fresh_modules_installed(monkeypatch):
        status = _operate(operation, root, git_sandbox, environment, monkeypatch)
        loaded = set(_modules(_PACKAGE))
    assert (set(_modules_of(_FRESH, _PACKAGE)), _IMPORT_READS) == (set(_ALLOWED), [])
    assert (status, loaded, reads) == (0, set(_ALLOWED), [])


class _ReadingModule(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Serve one in-memory module that looks the budget variable up, discarding the value, while it is imported."""

    name = "a_module_reading_the_budget_at_import"

    def find_spec(self, fullname: str, path: object, target: object = None) -> importlib.machinery.ModuleSpec | None:
        """Find only the reading module."""
        del path, target
        return importlib.util.spec_from_loader(fullname, self) if fullname == self.name else None

    def exec_module(self, module: ModuleType) -> None:
        """Run the module body: one discarded lookup of the budget variable."""
        del module
        os.environ.get(DOWNLOAD_BUDGET_VARIABLE)


def test_the_import_watch_sees_a_discarded_lookup_made_at_import(monkeypatch: pytest.MonkeyPatch) -> None:
    """Code review round 2: a module that looks the budget variable up and discards it while it is imported is recorded."""
    reading = _ReadingModule()
    monkeypatch.setattr(sys, "meta_path", [reading, *sys.meta_path])
    reads: list[str] = []
    try:
        _watched_imports((reading.name,), reads)
    finally:
        sys.modules.pop(reading.name, None)
    assert reads == [f"os.environ lookup of {DOWNLOAD_BUDGET_VARIABLE}"]
    assert not isinstance(os.environ, _WatchedEnvironment)


def test_the_budget_watch_sees_a_resolution_and_every_kind_of_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    """The control of the watch: a budget resolution, a discarded lookup by name and an `os.environ` lookup are each recorded."""
    reads: list[str] = []
    environment = {"PATH": "C:/Windows", _watched_name(DOWNLOAD_BUDGET_VARIABLE, reads): "-1"}
    monkeypatch.setattr(os, "environ", _WatchedEnvironment({"Path": "C:/Windows"}, reads))
    with pytest.raises(BudgetSettingError):
        resolve_budget(environment)
    environment.get(DOWNLOAD_BUDGET_VARIABLE)
    assert DOWNLOAD_BUDGET_VARIABLE.lower() not in os.environ
    assert os.environ.get("PATH") == "C:/Windows"
    assert reads == [f"name compared with {DOWNLOAD_BUDGET_VARIABLE}", f"name compared with {DOWNLOAD_BUDGET_VARIABLE}",
                     f"os.environ lookup of {DOWNLOAD_BUDGET_VARIABLE.lower()}"]


def test_a_fresh_checkouts_first_provisioning_writes_only_below_the_ignored_cache(scenario: GcliffScenario) -> None:
    """Every produced path is below `.tools/git-cliff/`, which the root `.gitignore` ignores before the first write."""
    _repairable(scenario)
    tooling = scenario.simulation.root
    before = snapshot(tooling)
    assert scenario.run("--version", cwd=scenario.sandbox.home / "B").returncode == 0
    produced = sorted(set(snapshot(tooling)) - set(before))
    assert produced
    assert all(path == ".tools" or path.startswith(".tools/git-cliff") for path in produced)
    assert {path: content for path, content in snapshot(tooling).items() if path in before} == before
    assert "/.tools/git-cliff/" in (_REPOSITORY / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_the_shipped_manifest_is_the_pin_table_of_these_rows() -> None:
    """The rows that need no download select from the shipped manifest, whose default is the admitted 2.14.2."""
    assert [(pin.version, pin.default) for pin in ADMITTED_PINS] == [(VERSION, True)]


# eof
