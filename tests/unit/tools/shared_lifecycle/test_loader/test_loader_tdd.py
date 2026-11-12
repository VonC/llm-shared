"""Exercise live-source preflight without installing synthetic audit dispatchers."""

from __future__ import annotations

import ast
import importlib.machinery
import os
import runpy
import shutil
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import cast

import llm_shared_pytest_loader as loader
import pytest


@pytest.fixture
def prepared(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict[str, str], list[str]]:
    """Declare live policies and observe canonical imports through their seam."""
    policy = tmp_path / "shared"
    policy.mkdir()
    root = tmp_path / "project"
    root.mkdir()
    for name in loader.POLICIES.values():
        (policy / f"{name}.py").write_text("LOADER_CONTRACT_VERSION = 1\n", encoding="utf-8")
    calls: list[str] = []
    def import_policy(name: str) -> ModuleType:
        calls.append(name)
        module = ModuleType(name)
        module.__file__ = str(policy / f"{name}.py")
        setattr(module, "LOADER_CONTRACT_VERSION", 1)
        return module
    def find(name: str) -> importlib.machinery.ModuleSpec:
        return importlib.machinery.ModuleSpec(name, None, origin=str(policy / f"{name}.py"))
    monkeypatch.setattr(loader.importlib, "import_module", import_policy)
    monkeypatch.setattr(loader.importlib.util, "find_spec", find)
    values = {loader.SELECTION: "lifecycle,process", loader.ROOT: str(root), loader.POLICY_DIR: str(policy)}
    return values, calls


def test_all_source_contracts_precede_any_import(prepared: tuple[dict[str, str], list[str]]) -> None:
    """A bad second policy prevents importing even the valid first policy."""
    values, calls = prepared
    (Path(values[loader.POLICY_DIR]) / "llm_shared_process_audit.py").write_text("LOADER_CONTRACT_VERSION = 2", encoding="utf-8")
    with pytest.raises(pytest.UsageError, match=r"llm_shared_process_audit.*prepare"):
        loader.preflight(values, [])
    assert calls == []


@pytest.mark.parametrize(("selection", "names"), [("", []), ("lifecycle", ["llm_shared_lifecycle_gate"]), ("process", ["llm_shared_process_audit"]), ("process,lifecycle,process", ["llm_shared_lifecycle_gate", "llm_shared_process_audit"])])
def test_only_selected_canonical_names_are_imported(prepared: tuple[dict[str, str], list[str]], selection: str, names: list[str]) -> None:
    """Independent selection leaves the unselected policy completely unimported."""
    values, calls = prepared
    values[loader.SELECTION] = selection
    modules = loader.preflight(values, [])
    assert [module.__name__ for module in modules] == names
    assert calls == names


@pytest.mark.parametrize("failure", ["unknown", "empty_token", "binding", "relative", "missing", "syntax", "contract", "computed", "duplicate", "blocked"])
def test_startup_failures_identify_opt_in_before_execution(prepared: tuple[dict[str, str], list[str]], failure: str) -> None:
    """Every selected source/import failure becomes identifying exit-4 semantics."""
    values, calls = prepared
    path = Path(values[loader.POLICY_DIR]) / "llm_shared_lifecycle_gate.py"
    args: list[str] = []
    if failure in {"unknown", "empty_token"}:
        values[loader.SELECTION] = "bad" if failure == "unknown" else "lifecycle,,process"
    elif failure == "binding":
        del values[loader.ROOT]
    elif failure == "relative":
        values[loader.POLICY_DIR] = "relative"
    elif failure == "missing":
        path.unlink()
    elif failure in {"syntax", "contract", "computed", "duplicate"}:
        path.write_text({"syntax": "def ?", "contract": "x = 1", "computed": "LOADER_CONTRACT_VERSION = int('1')", "duplicate": "LOADER_CONTRACT_VERSION = 1\nLOADER_CONTRACT_VERSION = 1"}[failure], encoding="utf-8")
    elif failure == "blocked":
        args = ["-p", "no:llm_shared_lifecycle_gate"]
    with pytest.raises(pytest.UsageError, match=loader.SELECTION):
        loader.preflight(values, args)
    assert calls == []


@pytest.mark.parametrize("failure", ["origin", "import", "runtime_contract"])
def test_selected_import_errors_are_usage_errors(prepared: tuple[dict[str, str], list[str]], monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    """Origin resolution and runtime failures retain the selected opt-in context."""
    values, calls = prepared
    path = Path(values[loader.POLICY_DIR]) / "llm_shared_lifecycle_gate.py"
    if failure == "origin":
        def missing_spec(_name: str) -> None:
            return None
        monkeypatch.setattr(loader.importlib.util, "find_spec", missing_spec)
    else:
        def broken(name: str) -> ModuleType:
            if failure == "import":
                message = "missing dependency"
                raise ImportError(message)
            module = ModuleType(name)
            module.__file__ = str(path)
            setattr(module, "LOADER_CONTRACT_VERSION", 3)
            return module
        monkeypatch.setattr(loader.importlib, "import_module", broken)
    with pytest.raises(pytest.UsageError, match=loader.SELECTION):
        loader.preflight(values, [])
    assert calls == []


def test_import_failure_has_no_registration(prepared: tuple[dict[str, str], list[str]], monkeypatch: pytest.MonkeyPatch) -> None:
    """Importing a second selected module cannot register the first prematurely."""
    values, _calls = prepared
    original = loader.importlib.import_module
    def second_failure(name: str) -> ModuleType:
        if name.endswith("audit"):
            message = "broken import"
            raise RuntimeError(message)
        return original(name)
    monkeypatch.setattr(loader.importlib, "import_module", second_failure)
    with pytest.raises(pytest.UsageError, match="llm_shared_process_audit"):
        loader.preflight(values, [])


def test_roots_accept_descendants_but_not_siblings(prepared: tuple[dict[str, str], list[str]]) -> None:
    """Containment compares whole paths, including Windows case normalization."""
    values, _calls = prepared
    root = Path(values[loader.ROOT])
    loader.check_root(values, root)
    loader.check_root(values, root / "nested")
    with pytest.raises(pytest.UsageError, match=str(root.name)):
        loader.check_root(values, root.with_name(root.name + "-other"))
    if os.name == "nt":
        loader.check_root(values, Path(str(root).swapcase()))


def test_hook_reuses_canonical_registration(prepared: tuple[dict[str, str], list[str]], monkeypatch: pytest.MonkeyPatch) -> None:
    """Pytest's canonical mechanism owns deduplication, including explicit loading."""
    values, _calls = prepared
    modules = loader.preflight(values, [])
    manager = pytest.PytestPluginManager()
    manager.register(modules[0], modules[0].__name__)
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(loader, "_PREFLIGHTED", modules)
    config = cast("pytest.Config", SimpleNamespace(rootpath=Path(values[loader.ROOT]), pluginmanager=manager))
    loader.pytest_load_initial_conftests(config, [])
    loader.pytest_load_initial_conftests(config, [])
    assert manager.get_plugin(modules[0].__name__) is modules[0]
    assert manager.get_plugin(modules[1].__name__) is modules[1]
    manager.set_blocked(modules[1].__name__)
    with pytest.raises(pytest.UsageError, match="blocked"):
        loader.pytest_load_initial_conftests(config, [])


def test_empty_hook_is_inert(monkeypatch: pytest.MonkeyPatch) -> None:
    """Loading an unselected bootstrap alone does not require a binding."""
    monkeypatch.setattr(loader, "_PREFLIGHTED", ())
    loader.pytest_load_initial_conftests(cast("pytest.Config", None), [])


def test_version_refusal_runs_before_newer_definitions(monkeypatch: pytest.MonkeyPatch) -> None:
    """The standalone bootstrap retains the same old-interpreter refusal path."""
    monkeypatch.setattr(sys, "version_info", (3, 10))
    with pytest.raises(pytest.UsageError, match=r"llm_shared_pytest_loader requires Python 3\.12"):
        runpy.run_path(str(Path(loader.__file__)))


def test_initial_preflight_precedes_explicit_policy_loading(prepared: tuple[dict[str, str], list[str]], monkeypatch: pytest.MonkeyPatch) -> None:
    """Importing the bootstrap rejects a missing selection before later -p work."""
    values, calls = prepared
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("PYTEST_ADDOPTS", "-p llm_shared_pytest_loader")
    monkeypatch.setattr(sys, "argv", ["pytest", "-p", "llm_shared_lifecycle_gate"])
    (Path(values[loader.POLICY_DIR]) / "llm_shared_process_audit.py").unlink()
    with pytest.raises(pytest.UsageError, match="llm_shared_process_audit"):
        runpy.run_path(str(Path(loader.__file__)))
    assert calls == []


def test_initial_preflight_parses_options_only_when_selected(prepared: tuple[dict[str, str], list[str]], monkeypatch: pytest.MonkeyPatch) -> None:
    """Unselected bootstrap imports ignore unrelated malformed option text."""
    values, calls = prepared
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("PYTEST_ADDOPTS", '"unterminated')
    with pytest.raises(pytest.UsageError, match="No closing quotation"):
        loader._initial_preflight()
    monkeypatch.setenv(loader.SELECTION, "")
    assert loader._initial_preflight() == ()
    assert calls == []


def test_annotated_contract_is_accepted(prepared: tuple[dict[str, str], list[str]]) -> None:
    """Both supported module-level literal declaration forms preflight."""
    values, calls = prepared
    (Path(values[loader.POLICY_DIR]) / "llm_shared_process_audit.py").write_text("LOADER_CONTRACT_VERSION: int = 1", encoding="utf-8")
    assert [module.__name__ for module in loader.preflight(values, [])] == list(loader.POLICIES.values())
    assert calls == list(loader.POLICIES.values())


def test_conflicting_registration_is_rejected_before_any_registration(prepared: tuple[dict[str, str], list[str]], monkeypatch: pytest.MonkeyPatch) -> None:
    """A foreign canonical identity cannot silently replace selected enforcement."""
    values, _calls = prepared
    modules = loader.preflight(values, [])
    manager = pytest.PytestPluginManager()
    manager.register(ModuleType(modules[1].__name__), modules[1].__name__)
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(loader, "_PREFLIGHTED", modules)
    config = cast("pytest.Config", SimpleNamespace(rootpath=Path(values[loader.ROOT]), pluginmanager=manager))
    with pytest.raises(pytest.UsageError, match="different identity"):
        loader.pytest_load_initial_conftests(config, [])
    assert manager.get_plugin(modules[0].__name__) is None


def test_loader_is_independent_and_refusal_boundary_is_inspectable() -> None:
    """The entire source parses at 3.10 and only sys/pytest precede refusal."""
    tree = ast.parse(Path(loader.__file__).read_text(encoding="utf-8"), feature_version=(3, 10))
    assert _imports(tree) <= sys.stdlib_module_names | {"pytest"}
    boundary = tree.body[1:4]
    assert isinstance(boundary[0], ast.Import)
    assert boundary[0].names[0].name == "sys"
    assert isinstance(boundary[1], ast.Import)
    assert boundary[1].names[0].name == "pytest"
    assert isinstance(boundary[2], ast.If)
    assert len(boundary[2].body) == 1
    assert isinstance(boundary[2].body[0], ast.Raise)


def _imports(tree: ast.Module) -> set[str]:
    """Collect dependency roots without importing anything from the source."""
    names = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    names.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return names


@pytest.mark.parametrize("removed", ["cache", "checkout"])
def test_each_loader_copy_handles_independent_removal(prepared: tuple[dict[str, str], list[str]], monkeypatch: pytest.MonkeyPatch, tmp_path: Path, removed: str) -> None:
    """Cache removal uses live bootstrap; checkout removal still refuses policies."""
    values, calls = prepared
    source = Path(loader.__file__).read_bytes()
    policy = Path(values[loader.POLICY_DIR])
    live = policy / "llm_shared_pytest_loader.py"
    live.write_bytes(source)
    cache = tmp_path / "cache"
    cache.mkdir()
    cached = cache / live.name
    cached.write_bytes(source)
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("PYTEST_ADDOPTS", "-p llm_shared_pytest_loader")
    monkeypatch.setattr(sys, "argv", ["pytest"])
    if removed == "checkout":
        shutil.rmtree(policy)
        with pytest.raises(pytest.UsageError, match="llm_shared_lifecycle_gate"):
            exec(compile(cached.read_bytes(), str(cached), "exec"), {})  # noqa: S102 - execute copied bootstrap in process
        assert calls == []
    else:
        shutil.rmtree(cache)
        loaded: dict[str, object] = {}
        exec(compile(live.read_bytes(), str(live), "exec"), loaded)  # noqa: S102 - execute live bootstrap in process
        modules = cast("tuple[ModuleType, ...]", loaded["_PREFLIGHTED"])
        assert [module.__name__ for module in modules] == list(loader.POLICIES.values())
        assert calls == list(loader.POLICIES.values())


def test_real_canonical_imports_preserve_consumer_packages(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Actual selected imports retain the caller's tools/tests and path entries."""
    consumer_tools = ModuleType("tools")
    consumer_tests = ModuleType("tests")
    monkeypatch.setitem(sys.modules, "tools", consumer_tools)
    monkeypatch.setitem(sys.modules, "tests", consumer_tests)
    policy = Path(loader.__file__).parent
    values = {loader.SELECTION: "lifecycle,process", loader.ROOT: str(tmp_path), loader.POLICY_DIR: str(policy)}
    before = sys.path[:]
    modules = loader.preflight(values, [])
    assert [module.__name__ for module in modules] == list(loader.POLICIES.values())
    assert all(module is sys.modules[module.__name__] for module in modules)
    assert loader.importlib.import_module("tools") is consumer_tools
    assert loader.importlib.import_module("tests") is consumer_tests
    assert sys.path == before
