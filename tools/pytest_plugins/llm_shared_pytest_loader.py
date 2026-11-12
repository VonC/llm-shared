"""Independent prepared-run bootstrap with all-selected live policy preflight.

Only stdlib and pytest are dependencies. This source is copied into an
immutable user cache; the environment binds each shell to its live policies.
No policy is registered until every selected source and import has passed.
"""

import sys

import pytest

if sys.version_info < (3, 12):
    raise pytest.UsageError("llm_shared_pytest_loader requires Python 3.12 or later")  # noqa: EM101, TRY003 - approved pre-refusal boundary

LOADER_CONTRACT_VERSION = 1

import ast  # noqa: E402
import importlib  # noqa: E402
import importlib.util  # noqa: E402
import os  # noqa: E402
import shlex  # noqa: E402
from collections.abc import Mapping, Sequence  # noqa: E402
from pathlib import Path  # noqa: E402
from types import ModuleType  # noqa: E402

SELECTION = "LLM_SHARED_PYTEST_PLUGINS"
ROOT = "LLM_SHARED_PYTEST_ROOT"
POLICY_DIR = "LLM_SHARED_PYTEST_POLICY_DIR"
LOADER = "llm_shared_pytest_loader"
POLICIES = {"lifecycle": "llm_shared_lifecycle_gate", "process": "llm_shared_process_audit"}


def _error(name: str, selection: str, detail: str) -> pytest.UsageError:
    """Identify selected enforcement and its opt-in on every startup failure."""
    return pytest.UsageError(f"{name}: {SELECTION}={selection!r}: {detail}; prepare the shell again")


def _blocked(args: Sequence[str], name: str) -> bool:
    """Recognize both pytest short-option spellings without parsing other flags."""
    return any(arg in (f"-pno:{name}", f"-p=no:{name}") or (arg == "-p" and index + 1 < len(args) and args[index + 1] == f"no:{name}") for index, arg in enumerate(args))


def _check_source(path: Path, selection: str) -> None:
    """Reject missing or nonliteral live contracts before importing any policy."""
    try:
        tree = ast.parse(path.read_bytes(), filename=str(path))
        values = _contract_values(tree)
        valid = len(values) == 1 and isinstance(values[0], ast.Constant) and type(values[0].value) is int and values[0].value == LOADER_CONTRACT_VERSION
    except (OSError, SyntaxError, ValueError) as error:
        raise _error(path.stem, selection, f"cannot preflight live source {path}: {error}") from error
    if not valid:
        raise _error(path.stem, selection, "loader contract mismatch")


def _is_contract(target: ast.expr) -> bool:
    """Identify the public declaration name without evaluating it."""
    return isinstance(target, ast.Name) and target.id == "LOADER_CONTRACT_VERSION"


def _contract_values(tree: ast.Module) -> list[ast.expr]:
    """Collect module-level literal candidates, including annotated assignments."""
    return [statement.value for statement in tree.body if isinstance(statement, (ast.Assign, ast.AnnAssign)) and statement.value is not None and (any(_is_contract(target) for target in statement.targets) if isinstance(statement, ast.Assign) else _is_contract(statement.target))]


def _live_module(name: str, policy: Path, selection: str) -> ModuleType:
    """Refuse installed or previously imported alternatives to the bound source."""
    spec = importlib.util.find_spec(name)
    expected = (policy / f"{name}.py").resolve()
    if spec is None or spec.origin is None or Path(spec.origin).resolve() != expected:
        raise _error(name, selection, f"canonical import does not resolve to live policy {expected}")
    module = importlib.import_module(name)
    version = getattr(module, "LOADER_CONTRACT_VERSION", None)
    if Path(module.__file__ or "").resolve() != expected or type(version) is not int or version != LOADER_CONTRACT_VERSION:
        raise _error(name, selection, "imported policy contract or source mismatch")
    return module


def _import_policy(name: str, policy: Path, selection: str) -> ModuleType:
    """Convert all selected import exceptions to identifying usage errors."""
    try:
        return _live_module(name, policy, selection)
    except Exception as error:
        raise _error(name, selection, f"selected import failed: {error}") from error


def _selected_names(raw: str) -> list[str]:
    """Normalize only the documented tokens in stable policy order."""
    tokens = {name.strip() for name in raw.split(",")}
    if tokens - POLICIES.keys():
        raise _error(LOADER, raw, "select only lifecycle and process")
    return [module for token, module in POLICIES.items() if token in tokens]


def preflight(environment: Mapping[str, str], args: Sequence[str]) -> tuple[ModuleType, ...]:
    """Import only selected canonical modules, after checking all live sources."""
    raw = environment.get(SELECTION, "")
    if not raw.strip():
        return ()
    names = _selected_names(raw)
    policy = Path(environment.get(POLICY_DIR, ""))
    root = Path(environment.get(ROOT, ""))
    if not policy.is_absolute() or not root.is_absolute():
        raise _error(names[0], raw, f"missing absolute {ROOT} or {POLICY_DIR}")
    for name in names:
        if _blocked(args, name):
            raise _error(name, raw, "selected plugin is blocked")
        _check_source(policy / f"{name}.py", raw)
    return tuple(_import_policy(name, policy, raw) for name in names)


def check_root(environment: Mapping[str, str], rootpath: Path) -> None:
    """Accept the bound project and descendants; reject whole-path outsiders."""
    bound = Path(environment[ROOT]).resolve()
    actual = rootpath.resolve()
    if not actual.is_relative_to(bound):
        raise _error(LOADER, environment.get(SELECTION, ""), f"pytest root {actual} lies outside bound project {bound}")


def _initial_preflight() -> tuple[ModuleType, ...]:
    """Run during early -p import, before later explicit command-line plugins."""
    if not os.environ.get(SELECTION, "").strip():
        return ()
    try:
        args = [*shlex.split(os.environ.get("PYTEST_ADDOPTS", "")), *sys.argv[1:]]
    except ValueError as error:
        raise _error(LOADER, os.environ.get(SELECTION, ""), str(error)) from error
    return preflight(os.environ, args)


_PREFLIGHTED = _initial_preflight()


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config: pytest.Config, args: list[str]) -> None:
    """Validate binding and blocked plugins before initial conftest discovery."""
    if not _PREFLIGHTED:
        return
    check_root(os.environ, early_config.rootpath)
    manager = early_config.pluginmanager
    for module in _PREFLIGHTED:
        if manager.is_blocked(module.__name__) or _blocked(args, module.__name__):
            raise _error(module.__name__, os.environ.get(SELECTION, ""), "selected plugin is blocked")
        registered = manager.get_plugin(module.__name__)
        if registered is not None and registered is not module:
            raise _error(module.__name__, os.environ.get(SELECTION, ""), "canonical registration has a different identity")
    for module in _PREFLIGHTED:
        if not manager.hasplugin(module.__name__):
            manager.register(module, module.__name__)


# eof
