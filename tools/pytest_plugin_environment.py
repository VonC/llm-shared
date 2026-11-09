"""Compute atomic pytest activation without importing selected policy modules.

The environment builder is shared by shell preparation and child runners.
Only a verified, immutable loader is cached; policies always stay live in the
bound checkout. No caller environment or consumer project file is modified.
"""

from __future__ import annotations

import ast
import hashlib
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

SELECTION = "LLM_SHARED_PYTEST_PLUGINS"
ROOT = "LLM_SHARED_PYTEST_ROOT"
POLICY_DIR = "LLM_SHARED_PYTEST_POLICY_DIR"
LOADER = "llm_shared_pytest_loader"
POLICIES = {"lifecycle": "llm_shared_lifecycle_gate", "process": "llm_shared_process_audit"}
CONTRACT_VERSION = 1
_OPTION_TOKEN = re.compile(r"""(?:[^\s'"\\]|\\.|'[^']*'|"(?:[^"\\]|\\.)*")+""")
_HASH = re.compile(r"[0-9a-f]{64}")


class PreparationError(ValueError):
    """Reject incomplete sources/cache state before publishing activation."""


def normalize_selection(raw: str) -> tuple[str, ...]:
    """Normalize duplicate named tokens while rejecting malformed declarations."""
    if not raw.strip():
        return ()
    tokens = {token.strip() for token in raw.split(",")}
    if tokens - POLICIES.keys():
        message = f"{SELECTION}={raw!r}: select only lifecycle and process"
        raise PreparationError(message)
    return tuple(name for name in POLICIES if name in tokens)


def _path_key(value: str) -> str:
    """Compare whole lexical path entries using this platform's path rules."""
    return os.path.normcase(os.path.normpath(value))


def clean_paths(paths: Sequence[str], owned: set[str]) -> list[str]:
    """Remove owned entries in one pass while preserving unrelated ordering."""
    keys = {_path_key(value) for value in owned}
    return [value for value in paths if _path_key(value) not in keys]


def clean_options(options: str) -> str:
    """Remove just the injected loader option, preserving other option spelling."""
    tokens = list(_OPTION_TOKEN.finditer(options))
    pieces: list[str] = []
    end = 0
    index = 0
    while index < len(tokens):
        token = tokens[index]
        last = token
        owned = token[0] in (f"-p{LOADER}", f"-p={LOADER}")
        if token[0] == "-p" and index + 1 < len(tokens) and tokens[index + 1][0] == LOADER:
            index += 1
            last = tokens[index]
            owned = True
        if owned:
            pieces.append(options[end:token.start()])
            end = last.end() + (options[last.end():last.end() + 1] == " ")
        index += 1
    return "".join((*pieces, options[end:]))


def _contract(source: bytes, path: Path) -> None:
    """Validate exactly one module-level literal without executing source code."""
    try:
        tree = ast.parse(source, filename=str(path))
        declarations = _contract_values(tree)
        valid = len(declarations) == 1 and isinstance(declarations[0], ast.Constant) and type(declarations[0].value) is int and declarations[0].value == CONTRACT_VERSION
    except (SyntaxError, ValueError) as error:
        message = f"{path.stem}: invalid source for {SELECTION}; prepare the shell again: {error}"
        raise PreparationError(message) from error
    if not valid:
        message = f"{path.stem}: loader contract mismatch for {SELECTION}; prepare the shell again"
        raise PreparationError(message)


def _is_contract(target: ast.expr) -> bool:
    """Identify the one public declaration name without evaluating it."""
    return isinstance(target, ast.Name) and target.id == "LOADER_CONTRACT_VERSION"


def _contract_values(tree: ast.Module) -> list[ast.expr]:
    """Collect ordinary and annotated module-level assignments in source order."""
    return [statement.value for statement in tree.body if isinstance(statement, (ast.Assign, ast.AnnAssign)) and statement.value is not None and (any(_is_contract(target) for target in statement.targets) if isinstance(statement, ast.Assign) else _is_contract(statement.target))]


def _source(path: Path) -> bytes:
    """Read and validate one named source exactly once for this preparation."""
    try:
        source = path.read_bytes()
    except OSError as error:
        message = f"{path.stem}: cannot read selected source for {SELECTION}: {error}"
        raise PreparationError(message) from error
    _contract(source, path)
    return source


def default_cache_root(environment: Mapping[str, str]) -> Path:
    """Use user-local storage independent of either project or artifact home."""
    base = Path(environment["LOCALAPPDATA"]) if environment.get("LOCALAPPDATA") else Path.home() / ".cache"
    return base / "llm-shared" / "pytest-loader"


def _verify_entry(entry: Path, digest: str) -> None:
    """Reject immutable-entry corruption without repairing a shell's live code."""
    try:
        valid = hashlib.sha256((entry / f"{LOADER}.py").read_bytes()).hexdigest() == digest
    except OSError:
        valid = False
    if not valid:
        message = f"Corrupt loader cache entry {entry}; explicitly remove this entry and prepare the shell again"
        raise PreparationError(message)


def _publish_loader(cache: Path, source: bytes) -> Path:
    """Atomically publish one complete directory, or verify a racing winner."""
    digest = hashlib.sha256(source).hexdigest()
    entry = cache / digest
    if entry.exists():
        _verify_entry(entry, digest)
        return entry
    cache.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".publishing-", dir=cache))
    try:
        (temporary / f"{LOADER}.py").write_bytes(source)
        try:
            temporary.rename(entry)
        except OSError:
            if not entry.exists():
                raise
        _verify_entry(entry, digest)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return entry


def _owned_paths(environment: Mapping[str, str], cache: Path) -> set[str]:
    """Recognize old bound policy and loader entries without extra public state."""
    owned: set[str] = {environment[POLICY_DIR]} if environment.get(POLICY_DIR) else set()
    for value in environment.get("PYTHONPATH", "").split(os.pathsep):
        path = Path(value)
        if _HASH.fullmatch(path.name) and (path.parent == cache or (path.parent.name == "pytest-loader" and path.parent.parent.name == "llm-shared")):
            owned.add(value)
    return owned


def _set_or_remove(environment: dict[str, str], key: str, value: str) -> None:
    """Avoid manufacturing empty variables when owned entries are removed."""
    if value:
        environment[key] = value
    else:
        environment.pop(key, None)


def _activation_paths(project: Path, shared: Path, selected: tuple[str, ...], cache: Path) -> tuple[Path, Path]:
    """Preflight all sources before publishing a checkout-independent bootstrap."""
    if cache.is_relative_to(project) or cache.is_relative_to(shared):
        message = f"Loader cache {cache} must be outside project {project} and shared checkout {shared}"
        raise PreparationError(message)
    policy = shared / "tools" / "pytest_plugins"
    source = _source(policy / f"{LOADER}.py")
    for name in selected:
        _source(policy / f"{POLICIES[name]}.py")
    try:
        entry = _publish_loader(cache, source)
    except OSError as error:
        message = f"Cannot publish loader cache for {SELECTION}={','.join(selected)}: {error}"
        raise PreparationError(message) from error
    return entry, policy


def prepare_environment(
    project_root: Path,
    shared_root: Path,
    environment: Mapping[str, str],
    *,
    cache_root: Path | None = None,
) -> dict[str, str]:
    """Return a complete independent environment, publishing no partial result.

    Selected sources and contracts are read before any cache publication.
    Unselected preparation only removes prior owned activation. Directory
    publication uses a same-parent rename and verifies any concurrent winner.
    """
    selected = normalize_selection(environment.get(SELECTION, ""))
    project, shared = project_root.resolve(), shared_root.resolve()
    cache = (cache_root if cache_root is not None else default_cache_root(environment)).resolve()
    result = dict(environment)
    owned = _owned_paths(environment, cache)
    paths = environment["PYTHONPATH"].split(os.pathsep) if environment.get("PYTHONPATH") else []
    options = clean_options(environment.get("PYTEST_ADDOPTS", ""))
    for key in (SELECTION, ROOT, POLICY_DIR):
        result.pop(key, None)
    if not selected and not owned and options == environment.get("PYTEST_ADDOPTS", ""):
        return result
    if selected:
        entry, policy = _activation_paths(project, shared, selected, cache)
        owned.update((str(entry), str(policy)))
        paths = [str(entry), str(policy), *clean_paths(paths, owned)]
        options = f"-p {LOADER}" + (f" {options}" if options else "")
        result.update({SELECTION: ",".join(selected), ROOT: str(project), POLICY_DIR: str(policy)})
    else:
        paths = clean_paths(paths, owned)
    _set_or_remove(result, "PYTHONPATH", os.pathsep.join(paths))
    _set_or_remove(result, "PYTEST_ADDOPTS", options)
    return result


# eof
