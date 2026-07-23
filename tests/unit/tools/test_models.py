"""Tests for shared model helpers and serialization branches.

Fix: Cover project-root detection, src package discovery, layer inference,
and JSON serialization helpers in `tools._models`.

Fix: Cover the `PRJ_DIR` branch where the environment points at a path that
is not a Git root.

Fix: the no-git-root test walks a `_FakePath` ancestor chain instead of a
real temp directory, so it stays hermetic: the real walk climbs to the
filesystem root, and a Git repository above the pytest temp directory (the
user's home, say) would otherwise satisfy it and break the expected raise.
The fake path classes are hoisted to module level and gain a parent link so
both upward-walk tests share them.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from tools import _models

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

if TYPE_CHECKING:
    from collections.abc import Callable


def _return_project_root(project_root: Path) -> Callable[[Path], Path]:
    def fake_find_project_root(_start_path: Path) -> Path:
        return project_root

    return fake_find_project_root


def _raise_missing_root(_start_path: Path) -> Path:
    msg = "missing root"
    raise FileNotFoundError(msg)


class _FakeGitDir:
    """A `.git` probe stub returning a fixed `is_dir` answer."""

    def __init__(self, *, is_dir_result: bool) -> None:
        self._is_dir_result = is_dir_result

    def is_dir(self) -> bool:
        return self._is_dir_result


class _FakePath:
    """A minimal Path stand-in for hermetic upward-walk tests.

    `find_project_root` only resolves, climbs to `parent`, and probes
    `<dir> / ".git"`; this stub answers those three, so a test can model any
    ancestor chain without touching the real filesystem, whose ancestors
    above the pytest temp directory may hold a real Git root. A node without
    an explicit parent is its own parent, the walk's filesystem-root stop.
    """

    __hash__ = object.__hash__

    def __init__(self, *, has_git: bool, parent: _FakePath | None = None) -> None:
        self._has_git = has_git
        self._parent: _FakePath = parent if parent is not None else self

    def resolve(self) -> _FakePath:
        return self

    @property
    def parent(self) -> _FakePath:
        return self._parent

    def __truediv__(self, other: str) -> _FakeGitDir:
        assert other == ".git"
        return _FakeGitDir(is_dir_result=self._has_git)

    def __eq__(self, other: object) -> bool:
        return self is other


def test_project_root_from_environment_returns_none_without_prj_dir(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The environment helper should return None when `PRJ_DIR` is unset."""
    monkeypatch.delenv("PRJ_DIR", raising=False)

    assert _models._project_root_from_environment() is None


def test_project_root_from_environment_returns_none_without_git_marker(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The environment helper should reject `PRJ_DIR` values that are not Git roots."""
    monkeypatch.setenv("PRJ_DIR", str(tmp_path))

    assert _models._project_root_from_environment() is None


def test_find_project_root_returns_current_git_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The root finder should accept the starting directory when it has `.git`."""
    monkeypatch.delenv("PRJ_DIR", raising=False)
    (tmp_path / ".git").mkdir()

    assert _models.find_project_root(tmp_path) == tmp_path.resolve()


def test_find_project_root_raises_when_no_git_root_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The root finder should fail when no ancestor contains a `.git` directory."""
    # A three-level fake chain with no `.git` anywhere, ending at a
    # self-parented filesystem root: hermetic, so a real Git repository above
    # the pytest temp directory (the user's home, say) cannot satisfy the walk.
    fs_root = _FakePath(has_git=False)
    nested = _FakePath(has_git=False, parent=fs_root)
    start_path = _FakePath(has_git=False, parent=nested)
    monkeypatch.delenv("PRJ_DIR", raising=False)

    with pytest.raises(FileNotFoundError, match="Could not find project root"):
        _models.find_project_root(cast("Path", start_path))


def test_find_project_root_accepts_a_root_path_after_the_parent_walk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The root finder should still return a Git root after the upward walk ends."""
    fake_root = _FakePath(has_git=True)
    monkeypatch.delenv("PRJ_DIR", raising=False)

    assert _models.find_project_root(cast("Path", fake_root)) is fake_root


def test_src_package_candidates_filter_hidden_metadata_and_cache_dirs(
    tmp_path: Path,
) -> None:
    """Only real package directories under `src/` should be returned."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "pkg").mkdir()
    (src_dir / ".hidden").mkdir()
    (src_dir / "__pycache__").mkdir()
    (src_dir / "demo.egg-info").mkdir()
    (src_dir / "demo.dist-info").mkdir()
    (src_dir / "README.md").write_text("ignore me", encoding="utf-8")

    assert _models._src_package_candidates(src_dir) == (src_dir / "pkg",)


def test_detect_project_name_uses_single_src_candidate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Project-name detection should return the lone package under `src/`."""
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    monkeypatch.setattr(_models, "find_project_root", _return_project_root(tmp_path))

    assert _models._detect_project_name() == "pkg"


def test_detect_project_name_returns_unknown_without_src_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Project-name detection should return `<unknown>` when `src/` is absent."""
    monkeypatch.setattr(_models, "find_project_root", _return_project_root(tmp_path))

    assert _models._detect_project_name() == "<unknown>"


def test_detect_project_name_returns_unknown_for_multiple_src_candidates(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Project-name detection should return `<unknown>` when `src/` is ambiguous."""
    (tmp_path / "src" / "first").mkdir(parents=True)
    (tmp_path / "src" / "second").mkdir(parents=True)
    monkeypatch.setattr(_models, "find_project_root", _return_project_root(tmp_path))

    assert _models._detect_project_name() == "<unknown>"


def test_detect_project_name_returns_unknown_when_root_lookup_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Project-name detection should return `<unknown>` when root lookup fails."""
    monkeypatch.setattr(
        _models,
        "find_project_root",
        _raise_missing_root,
    )

    assert _models._detect_project_name() == "<unknown>"


def test_resolve_paths_returns_project_and_tests_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Path resolution should return the project root, package, tests, and name."""
    package_dir = tmp_path / "src" / "pkg"
    tests_dir = package_dir / "tests"
    tests_dir.mkdir(parents=True)
    monkeypatch.setattr(_models, "find_project_root", _return_project_root(tmp_path))

    assert _models.resolve_paths() == (tmp_path, package_dir, tests_dir, "pkg")


def test_resolve_paths_raises_when_src_dir_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Path resolution should fail when the project has no `src/` directory."""
    monkeypatch.setattr(_models, "find_project_root", _return_project_root(tmp_path))

    with pytest.raises(FileNotFoundError, match="Source folder not found"):
        _models.resolve_paths()


def test_resolve_paths_raises_when_src_has_multiple_packages(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Path resolution should reject ambiguous package roots under `src/`."""
    (tmp_path / "src" / "first").mkdir(parents=True)
    (tmp_path / "src" / "second").mkdir(parents=True)
    monkeypatch.setattr(_models, "find_project_root", _return_project_root(tmp_path))

    with pytest.raises(ValueError, match="Expected exactly one package folder"):
        _models.resolve_paths()


def test_safe_relative_returns_relative_path_and_none(tmp_path: Path) -> None:
    """Relative-path handling should return None for paths outside the package."""
    pkg_root = tmp_path / "src" / "pkg"
    inside = pkg_root / "domain" / "service.py"
    outside = tmp_path / "outside.py"
    inside.parent.mkdir(parents=True)
    inside.touch()
    outside.touch()

    assert _models.safe_relative(inside, pkg_root) == Path("domain") / "service.py"
    assert _models.safe_relative(outside, pkg_root) is None


def test_infer_layer_handles_root_split_and_default_cases(tmp_path: Path) -> None:
    """Layer inference should cover root files, adapter splits, and fallbacks."""
    pkg_root = tmp_path / "src" / "pkg"

    assert _models._infer_adapter_sublayer(("domain", "service.py")) is None
    assert (
        _models._infer_adapter_sublayer(("adapters", "outbound", "client.py"))
        == _models.Layer.ADAPTERS_OUT
    )
    assert (
        _models._infer_adapter_sublayer(("adapters", "sideways", "client.py")) is None
    )
    assert (
        _models.infer_layer(pkg_root / "__init__.py", pkg_root, "pkg")
        == _models.Layer.ROOT
    )
    assert (
        _models.infer_layer(
            pkg_root / "adapters" / "inbound" / "handler.py",
            pkg_root,
            "pkg",
            split_adapters=True,
        )
        == _models.Layer.ADAPTERS_IN
    )
    assert (
        _models.infer_layer(pkg_root / "domain" / "service.py", pkg_root, "pkg")
        == _models.Layer.DOMAIN
    )
    assert (
        _models.infer_layer(tmp_path / "external.py", pkg_root, "pkg")
        == _models.Layer.ROOT
    )


def test_serialization_helpers_cover_args_functions_classes_and_imports(
    tmp_path: Path,
) -> None:
    """Serialization helpers should preserve decorators, args, docs, and imports."""
    module = ast.parse(
        """
@outer.decorator
def sample(a, /, b: int, *args, c: str, **kwargs) -> bool:
    \"\"\"Function doc.\"\"\"
    return True

@class_decorator
class Example:
    \"\"\"Class doc.\"\"\"
    value = 1

    @staticmethod
    def method(item: int) -> str:
        \"\"\"Method doc.\"\"\"
        return str(item)
""",
    )

    function_node = module.body[0]
    class_node = module.body[1]

    assert isinstance(function_node, ast.FunctionDef)
    assert isinstance(class_node, ast.ClassDef)
    assert _models._unparse_arg(function_node.args.posonlyargs[0]) == "a"
    assert _models._collect_args_for_json(function_node.args) == [
        "a",
        "b: int",
        "*args",
        "c: str",
        "**kwargs",
    ]

    serialized_function = _models._serialize_function_def(function_node)
    assert serialized_function == {
        "name": "sample",
        "decorators": ["outer.decorator"],
        "args": ["a", "b: int", "*args", "c: str", "**kwargs"],
        "returns": "bool",
        "docstring": "Function doc.",
    }

    serialized_class = _models._serialize_class_def(class_node)
    assert serialized_class == {
        "name": "Example",
        "decorators": ["class_decorator"],
        "docstring": "Class doc.",
        "methods": [
            {
                "name": "method",
                "decorators": ["staticmethod"],
                "args": ["item: int"],
                "returns": "str",
                "docstring": "Method doc.",
            },
        ],
    }

    assert _models._serialize_definitions([class_node, function_node]) == {
        "classes": [serialized_class],
        "functions": [serialized_function],
    }

    import_record = _models.ImportRecord(
        source_file=tmp_path / "src" / "pkg" / "module.py",
        source_module="pkg.module",
        imported_module="typing",
        raw_text="import typing",
    )
    assert _models._serialize_import_records([import_record]) == [
        {
            "source_module": "pkg.module",
            "imported_module": "typing",
            "raw_text": "import typing",
        },
    ]


def test_serialize_file_analysis_uses_relative_and_absolute_paths(
    tmp_path: Path,
) -> None:
    """File-analysis serialization should prefer a project-relative path when possible."""
    inside = _models.FileAnalysis(
        file_path=tmp_path / "src" / "pkg" / "module.py",
        imports_text=["import b", "import a"],
        definitions=[],
        import_records=[],
    )
    outside_path = tmp_path.parent / "external.py"
    outside = _models.FileAnalysis(
        file_path=outside_path,
        imports_text=[],
        definitions=[],
        import_records=[],
    )

    assert _models.serialize_file_analysis(inside, tmp_path) == {
        "file": "src/pkg/module.py",
        "imports": ["import a", "import b"],
        "definitions": {"classes": [], "functions": []},
        "import_records": [],
    }
    assert _models.serialize_file_analysis(outside, tmp_path)["file"] == (
        outside_path.as_posix()
    )


# eof
