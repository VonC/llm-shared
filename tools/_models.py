"""Internal shared models and functions for the 'tools' package.

This module was created to break a circular dependency between 'inspect_api.py'
and 'dump_api.py'. It contains data classes, type definitions, and utility
functions that are used by both modules.

By centralizing these shared components, we establish a clear, one-way
dependency flow:
- `dump_api.py` depends on `_models.py`
- `inspect_api.py` depends on `_models.py` and `dump_api.py`

This resolves the import errors and improves the overall structure of the
'tools' package.

Fix (pyright): Made `_find_project_root` and `_safe_relative` public by
removing the leading underscore, as they are used by `inspect_api.py`.
Updated internal call sites to use the new public names.

Fix (splitting): Add a `COMPOSITION` layer and update `infer_layer` to
correctly classify top-level files. This allows `dump_api.py` to group
files by architectural layer instead of directory name.

Fix (splitting): Simplified layer classification by merging 'composition_root'
and 'composition' into a single 'root' layer. This ensures all top-level files
are grouped together as intended for file splitting.

Fix (splitting): Corrected layer inference to only use the top-level directory
name (e.g., 'adapters', 'domain'). This prevents sub-directories like 'inbound'
from being incorrectly merged into the layer name.

Fix (architecture): Add an opt-in adapter sublayer mode to `infer_layer()` so
guardrails can distinguish `adapters/inbound` from `adapters/outbound` without
changing the default coarse grouping used by tooling such as dump grouping.

Fix (architecture): Ignore packaging metadata directories such as `*.egg-info`
and `*.dist-info` when resolving the top-level package under `src/`. This keeps
architecture tooling working when editable-install metadata is present beside
the real package directory.

Fix (json): Add an optional `_marker` key to `JSONInspectionPayload`. This
allows a marker to be injected into the final JSON output to verify that the
file has been written completely, without causing a type error.

Fix (root): Prefer `PRJ_DIR` when it already points to a Git root so shared
tools act on the calling project before falling back to the upward scan.

"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, NotRequired, TypedDict

# ---------------------------
# Data models
# ---------------------------


@dataclass(frozen=True)
class ImportRecord:
    """Normalized representation of an import originating in '<project>/src/<project_name>/**'."""

    source_file: Path  # absolute path to the .py file
    source_module: str  # e.g. "<project_name>.domain.workflow.services.queue_manager"
    imported_module: (
        str  # e.g. "<project_name>.adapters.outbound.mappers.job_mapper" or "typing"
    )
    raw_text: str  # original textual import for logging
    imported_symbols: tuple[str, ...] = field(default_factory=tuple)  # e.g. ("A", "B")


@dataclass
class FileAnalysis:
    """Represents the analysis results of a single Python file.

    Attributes:
        file_path: Path to the analyzed Python file
        imports_text: List of import statements found in the file
        definitions: List of class and function definitions found in the file
        import_records: Structured representation of imports in the file
    """

    file_path: Path
    imports_text: list[str]
    definitions: list[ast.ClassDef | ast.FunctionDef]
    import_records: list[ImportRecord]


class Layer:
    """Constants representing different architectural layers in Domain-Driven Design (DDD).

    Used to classify modules according to the layered architecture pattern
    and to check for proper dependency direction in DDD guardrails.
    """

    ROOT = "root"
    DOMAIN = "domain"
    APPLICATION = "application"
    PORTS_IN = "ports_inbound"
    PORTS_OUT = "ports_outbound"
    ADAPTERS_IN = "adapters_inbound"
    ADAPTERS_OUT = "adapters_outbound"
    OTHER = "other"


# ---------------------------
# JSON serialization shapes
# ---------------------------


class JSONFunctionDef(TypedDict):
    """JSON-serializable representation of a function definition."""

    name: str
    decorators: list[str]
    args: list[str]
    returns: str | None
    docstring: str | None


class JSONClassDef(TypedDict):
    """JSON-serializable representation of a class definition."""

    name: str
    decorators: list[str]
    docstring: str | None
    methods: list[JSONFunctionDef]


class JSONDefinitions(TypedDict):
    """Container for JSON-serializable class and function definitions."""

    classes: list[JSONClassDef]
    functions: list[JSONFunctionDef]


class JSONImportRecord(TypedDict):
    """JSON-serializable representation of an import statement."""

    source_module: str
    imported_module: str
    raw_text: str


class JSONFileAnalysis(TypedDict):
    """JSON-serializable representation of a file analysis."""

    file: str
    imports: list[str]
    definitions: JSONDefinitions
    import_records: list[JSONImportRecord]


class JSONResults(TypedDict):
    """Container for JSON-serializable inspection results."""

    source: list[JSONFileAnalysis]
    tests: list[JSONFileAnalysis]


class JSONInspectionPayload(TypedDict):
    """JSON-serializable container for the complete inspection results."""

    project_root: str
    source_root: str
    results: JSONResults
    _marker: NotRequired[str]


# ---------------------------
# Path and project helpers
# ---------------------------

_PROJECT_ROOT_ENV_VAR: Final[str] = "PRJ_DIR"


def _project_root_from_environment() -> Path | None:
    """Return `PRJ_DIR` when it points to a Git root, otherwise None."""
    prj_dir_value = os.environ.get(_PROJECT_ROOT_ENV_VAR)
    if not prj_dir_value:
        return None

    project_root = Path(prj_dir_value).expanduser()
    if not (project_root / ".git").exists():
        return None

    return project_root.resolve()


def find_project_root(start_path: Path) -> Path:
    """Find project root, preferring `PRJ_DIR` when it points to a Git root."""
    env_project_root = _project_root_from_environment()
    if env_project_root is not None:
        return env_project_root

    current: Path = start_path.resolve()
    while current != current.parent:
        if (current / ".git").is_dir():
            return current
        current = current.parent
    if (current / ".git").is_dir():
        return current
    msg = "Could not find project root with .git directory."
    raise FileNotFoundError(msg)


_IGNORED_SRC_DIRECTORY_SUFFIXES: Final[tuple[str, ...]] = (".egg-info", ".dist-info")
_IGNORED_SRC_DIRECTORY_NAMES: Final[tuple[str, ...]] = ("__pycache__",)


def _src_package_candidates(src_dir: Path) -> tuple[Path, ...]:
    """Return non-metadata package candidates located directly under `src/`."""
    return tuple(
        path
        for path in src_dir.iterdir()
        if path.is_dir()
        and not path.name.startswith(".")
        and path.name not in _IGNORED_SRC_DIRECTORY_NAMES
        and not path.name.endswith(_IGNORED_SRC_DIRECTORY_SUFFIXES)
    )


def _detect_project_name() -> str:
    """Detect the top-level package folder name under '<project_root>/src'."""
    try:
        project_root = find_project_root(Path(__file__).parent)
        src_dir = project_root / "src"
        if not src_dir.is_dir():
            return "<unknown>"
        candidates = _src_package_candidates(src_dir)
        return candidates[0].name if len(candidates) == 1 else "<unknown>"
    except (FileNotFoundError, OSError, PermissionError, ValueError):
        return "<unknown>"


project_name: Final[str] = _detect_project_name()


def resolve_paths() -> tuple[Path, Path, Path | None, str]:
    """Resolve project paths used by the tool."""
    project_root = find_project_root(Path(__file__).parent)
    src_dir = project_root / "src"
    if not src_dir.is_dir():
        msg = f"Source folder not found: {src_dir}"
        raise FileNotFoundError(msg)

    candidates = _src_package_candidates(src_dir)
    if len(candidates) != 1:
        msg = (
            f"Expected exactly one package folder inside {src_dir}, found {len(candidates)}: "
            f"{[p.name for p in candidates]}"
        )
        raise ValueError(msg)

    top_package_dir = candidates[0]
    top_pkg_name = top_package_dir.name

    src_pkg_root = top_package_dir
    tests_path = src_pkg_root / "tests"
    tests_path = tests_path if tests_path.exists() else None
    return project_root, src_pkg_root, tests_path, top_pkg_name


# ---------------------------
# Layer classification helpers
# ---------------------------

_EMPTY_STR_TUPLE: tuple[str, ...] = ()
_ADAPTER_SUBLAYER_MIN_PARTS = 3


def safe_relative(file_path: Path, pkg_root: Path) -> Path | None:
    """Return file_path relative to pkg_root, or None if it's outside."""
    try:
        return file_path.relative_to(pkg_root)
    except ValueError:
        return None


def _infer_adapter_sublayer(parts: tuple[str, ...]) -> str | None:
    """Return the adapter sublayer when the path clearly identifies one."""
    if len(parts) < _ADAPTER_SUBLAYER_MIN_PARTS or parts[0] != "adapters":
        return None

    if parts[1] == "inbound":
        return Layer.ADAPTERS_IN
    if parts[1] == "outbound":
        return Layer.ADAPTERS_OUT
    return None


def infer_layer(
    file_path: Path,
    pkg_root: Path,
    _: str,
    *,
    split_adapters: bool = False,
) -> str:
    """Infer the layer from the path under src/<project_name>.

    The layer is determined by the top-level directory within the package root.
    For example:
    - `.../src/pdfss/domain/workflow/a.py` -> 'domain'
    - `.../src/pdfss/adapters/inbound/b.py` -> 'adapters'
    - `.../src/pdfss/composition.py` -> 'root'

    When `split_adapters=True`, adapter paths can be refined to
    `Layer.ADAPTERS_IN` or `Layer.ADAPTERS_OUT` for guardrail checks while the
    default behavior stays coarse for other tooling.
    """
    rel = safe_relative(file_path, pkg_root)
    parts: tuple[str, ...] = tuple(rel.parts) if rel is not None else _EMPTY_STR_TUPLE

    # Any file at the top-level of the package is part of the 'root' layer.
    # This includes __main__.py, __init__.py, composition.py, etc.
    if len(parts) <= 1:
        return Layer.ROOT

    if split_adapters:
        adapter_sublayer = _infer_adapter_sublayer(parts)
        if adapter_sublayer is not None:
            return adapter_sublayer

    # The first part of the relative path is the layer name.
    return parts[0]


# ---------------------------
# JSON serialization helpers
# ---------------------------


def _unparse_arg(a: ast.arg) -> str:
    """Return a string for an argument including its annotation if present."""
    return ast.unparse(a)


def _collect_args_for_json(a: ast.arguments) -> list[str]:
    """Collect arguments for JSON output without '*' and '/' markers."""
    out: list[str] = []
    out.extend(_unparse_arg(x) for x in getattr(a, "posonlyargs", []))
    out.extend(_unparse_arg(x) for x in a.args)
    if a.vararg is not None:
        name = a.vararg.arg
        out.append("*" + name)
    out.extend(_unparse_arg(x) for x in a.kwonlyargs)
    if a.kwarg is not None:
        out.append("**" + a.kwarg.arg)
    return out


def _serialize_function_def(node: ast.FunctionDef) -> JSONFunctionDef:
    """Serialize a function/method definition to a JSON-friendly dict."""
    decorator_list: list[str] = [ast.unparse(d) for d in node.decorator_list]
    args: list[str] = _collect_args_for_json(node.args)
    return_annotation: str | None = ast.unparse(node.returns) if node.returns else None
    result: JSONFunctionDef = {
        "name": node.name,
        "decorators": decorator_list,
        "args": args,
        "returns": return_annotation,
        "docstring": ast.get_docstring(node),
    }
    return result


def _serialize_class_def(node: ast.ClassDef) -> JSONClassDef:
    """Serialize a class definition (with its direct methods) to a JSON-friendly dict."""
    methods: list[JSONFunctionDef] = [
        _serialize_function_def(b) for b in node.body if isinstance(b, ast.FunctionDef)
    ]
    decorators: list[str] = [ast.unparse(d) for d in node.decorator_list]
    result: JSONClassDef = {
        "name": node.name,
        "decorators": decorators,
        "docstring": ast.get_docstring(node),
        "methods": methods,
    }
    return result


def _serialize_definitions(
    defs: list[ast.ClassDef | ast.FunctionDef],
) -> JSONDefinitions:
    """Split and serialize definitions into classes and functions."""
    classes: list[JSONClassDef] = []
    functions: list[JSONFunctionDef] = []
    for d in defs:
        if isinstance(d, ast.ClassDef):
            classes.append(_serialize_class_def(d))
        else:
            functions.append(_serialize_function_def(d))
    result: JSONDefinitions = {"classes": classes, "functions": functions}
    return result


def _serialize_import_records(recs: list[ImportRecord]) -> list[JSONImportRecord]:
    """Serialize ImportRecord list to JSON-friendly dicts."""
    out: list[JSONImportRecord] = [
        {
            "source_module": r.source_module,
            "imported_module": r.imported_module,
            "raw_text": r.raw_text,
        }
        for r in recs
    ]
    return out


def serialize_file_analysis(
    fa: FileAnalysis,
    project_root: Path,
) -> JSONFileAnalysis:
    """Convert a FileAnalysis object into a JSON-friendly dict."""
    try:
        rel = fa.file_path.relative_to(project_root)
    except ValueError:
        rel = fa.file_path
    result: JSONFileAnalysis = {
        "file": rel.as_posix(),
        "imports": sorted(fa.imports_text),
        "definitions": _serialize_definitions(fa.definitions),
        "import_records": _serialize_import_records(fa.import_records),
    }
    return result


# eof
