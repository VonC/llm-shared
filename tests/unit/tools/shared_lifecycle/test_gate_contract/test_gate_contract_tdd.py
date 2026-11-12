"""Standalone gate contracts with synthetic records and isolated pytest sessions.

The legacy assertions remain in their original modules. These cases cover the
new import boundary, configuration ownership and copied artifact lookup.
"""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import llm_shared_lifecycle_gate as gate
import pytest

from tests.unit.tools.shared_lifecycle.inline_session import run_inline

_DEFAULTS = {
    "test_lifecycle_limit": "0.1", "test_lifecycle_wall_limit": "1.0",
    "test_lifecycle_cpu_band_factor": "2.5", "test_lifecycle_cpu_drift_runs": "3",
}
_CEILING = 0.1
_SNIPPET = """
def pytest_addoption(parser, pluginmanager):
    if not pluginmanager.has_plugin("llm_shared_lifecycle_gate"):
        for key in ("test_lifecycle_limit", "test_lifecycle_wall_limit",
                    "test_lifecycle_cpu_band_factor", "test_lifecycle_cpu_drift_runs"):
            parser.addini(key, "Project lifecycle setting")
"""


def _home(root: Path, relative: str = ".reviews", ignore: bytes = b"*\n") -> Path:
    """Declare an existing ignored home without invoking shared helpers."""
    home = root / relative
    home.mkdir(parents=True)
    (home / ".gitignore").write_bytes(ignore)
    return home


@pytest.mark.parametrize("declaration", [
    "", "[other]\nhome=.reviews", "[review-artifacts]\n",
    "[review-artifacts]\nhome=.reviews\nextra=yes",
    "[review-artifacts]\nhome=.reviews\nhome=again",
    "[review-artifacts]\nhome=.reviews\n[other]\nhome=other",
    "[review-artifacts]\nhome=.reviews\n[review-artifacts]\nhome=again",
    "[DEFAULT]\nextra=yes\n[review-artifacts]\nhome=.reviews",
])
def test_invalid_declaration_never_falls_back(tmp_path: Path, declaration: str) -> None:
    """A present invalid declaration cannot silently authorize the default."""
    _home(tmp_path)
    (tmp_path / ".review-artifacts.ini").write_text(declaration, encoding="utf-8")
    loaded = gate.LifecycleGate.load(tmp_path, _DEFAULTS.__getitem__)
    assert loaded.path is None
    assert loaded.cpu_limit("t") == _CEILING
    assert loaded.save({"t": 0.05}).problem == "no ignored artifact home; nothing recorded"
    assert not (tmp_path / ".reviews" / gate.RECORD_NAME).exists()


@pytest.mark.parametrize("value", ["", ".", "../escape", "a/../..", "/absolute", "C:relative", "C:/absolute", "\\server", "~user", "$HOME/x", "x%VAR%"])
def test_home_spelling_and_containment_are_strict(tmp_path: Path, value: str) -> None:
    """Both Windows and native absolute/expanded or escaping paths are unsafe."""
    (tmp_path / ".review-artifacts.ini").write_text(f"[review-artifacts]\nhome={value}\n", encoding="utf-8")
    assert gate.artifact_record_path(tmp_path) is None


@pytest.mark.parametrize("inherited", [False, True])
def test_custom_home_preserves_strict_configparser_semantics(tmp_path: Path, *, inherited: bool) -> None:
    """Backslashes normalize and DEFAULT inheritance matches the existing parser."""
    home = _home(tmp_path, "private/evidence")
    text = "[DEFAULT]\nhome=private\\evidence\n[review-artifacts]\n" if inherited else "[review-artifacts]\nhome=private\\evidence\n"
    (tmp_path / ".review-artifacts.ini").write_text(text, encoding="utf-8")
    assert gate.artifact_record_path(tmp_path) == home / gate.RECORD_NAME


def test_symlink_escape_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A declared symlink resolution outside the root cannot authorize a home."""
    outside = tmp_path.parent / "outside"
    home = _home(tmp_path)
    original = Path.resolve

    def resolve(path: Path, *, strict: bool = False) -> Path:
        return outside if path == home else original(path, strict=strict)

    monkeypatch.setattr(Path, "resolve", resolve)
    assert gate.artifact_record_path(tmp_path) is None


@pytest.mark.parametrize("ignore", [b"", b"*", b"*\r\n", b"*\n\n", b"*\nkeep\n"])
def test_ignore_bytes_must_match_exactly(tmp_path: Path, ignore: bytes) -> None:
    """No equivalent-looking or partial ignore file grants write permission."""
    _home(tmp_path, ignore=ignore)
    assert gate.artifact_record_path(tmp_path) is None


@pytest.mark.parametrize("kind", ["missing", "file", "declaration-directory", "bad-utf8"])
def test_unavailable_home_is_read_only(tmp_path: Path, kind: str) -> None:
    """The gate never creates a home or repairs a declaration."""
    if kind == "file":
        (tmp_path / ".reviews").write_text("file", encoding="utf-8")
    elif kind == "declaration-directory":
        (tmp_path / ".review-artifacts.ini").mkdir()
    elif kind == "bad-utf8":
        (tmp_path / ".review-artifacts.ini").write_bytes(b"\xff")
    assert gate.artifact_record_path(tmp_path) is None
    assert not (tmp_path / ".reviews" / gate.RECORD_NAME).exists()


@pytest.mark.parametrize("method", ["resolve", "read_text", "read_bytes"])
def test_artifact_io_failure_is_strict(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, method: str) -> None:
    """Unreadable roots, declarations and ignore files produce no writable path."""
    _home(tmp_path)
    (tmp_path / ".review-artifacts.ini").write_text("[review-artifacts]\nhome=.reviews\n", encoding="utf-8")

    def refuse(*_args: object, **_kwargs: object) -> object:
        message = "denied"
        raise OSError(message)

    monkeypatch.setattr(Path, method, refuse)
    assert gate.artifact_record_path(tmp_path) is None


def test_existing_record_round_trip_keeps_human_fields(tmp_path: Path) -> None:
    """Synthetic schema-1 continuity retains exceptions, notes and eligible proofs."""
    path = _home(tmp_path) / gate.RECORD_NAME
    exception = {"cpu": 0.3, "attempted": "cached", "reason": "intrinsic", "ticket": 7}
    original_loose = {"proven": True, "over_runs": 0, "cpu": 0.3, "proven_cpu": 0.3}
    document = {
        "schema": 1, "extra": {"future": True}, "exceptions": {"slow": exception},
        "nodes": {
            "valid": {"proven": True, "over_runs": 1, "cpu": 0.2, "proven_cpu": 0.05},
            "loose": original_loose,
        },
    }
    path.write_text(json.dumps(document), encoding="utf-8")
    loaded = gate.LifecycleGate.load(tmp_path, _DEFAULTS.__getitem__)
    assert (loaded.cpu_limit("valid"), loaded.cpu_limit("loose"), loaded.cpu_limit("slow")) == (0.25, 0.1, 0.3)
    assert loaded.save({"valid": 0.07}).problem is None
    updated = json.loads(path.read_text(encoding="utf-8"))
    assert (updated["schema"], updated["extra"], updated["exceptions"]) == (1, document["extra"], document["exceptions"])
    assert updated["nodes"]["loose"] == original_loose
    assert not path.with_name(f"{gate.RECORD_NAME}.tmp").exists()


@pytest.mark.parametrize("operation", ["read_text", "write_text", "replace"])
def test_record_io_failure_preserves_original(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str) -> None:
    """An unreadable or unwritable record cannot change the test verdict or file."""
    path = _home(tmp_path) / gate.RECORD_NAME
    original = '{"schema": 1, "nodes": {}}'
    path.write_text(original, encoding="utf-8")
    loaded = gate.LifecycleGate.load(tmp_path, _DEFAULTS.__getitem__)
    with monkeypatch.context() as patch:
        def refuse(*_args: object, **_kwargs: object) -> object:
            message = "locked"
            raise OSError(message)

        patch.setattr(Path, operation, refuse)
        assert "locked" in str(loaded.save({"t": 0.05}).problem)
        if operation == "read_text":
            strict = gate.LifecycleGate.load(tmp_path, _DEFAULTS.__getitem__)
            assert strict.cpu_limit("t") == _CEILING
            assert "unusable" in str(strict.problem)
    assert path.read_text(encoding="utf-8") == original


@pytest.mark.parametrize("order", ["early", "late"])
@pytest.mark.parametrize("source", ["default", "project", "override"])
def test_guarded_consumer_settings_in_both_registration_orders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, order: str, source: str,
) -> None:
    """Gate registration supplies defaults; project and CLI values take precedence."""
    expected = list(_DEFAULTS.values()) if source == "default" else ["0.2", "2.0", "3.0", "4"]
    (tmp_path / "conftest.py").write_text(_SNIPPET + ('\npytest_plugins = ["llm_shared_lifecycle_gate"]\n' if order == "late" else ""), encoding="utf-8")
    config = "[pytest]\n"
    if source == "project":
        config += "\n".join(f"{key}={value}" for key, value in zip(_DEFAULTS, expected, strict=True))
    (tmp_path / "pytest.ini").write_text(config, encoding="utf-8")
    (tmp_path / "test_sample.py").write_text(
        f"def test_settings(pytestconfig):\n    assert [pytestconfig.getini(k) for k in {list(_DEFAULTS)!r}] == {expected!r}\n", encoding="utf-8",
    )
    arguments = ["--strict-config", "-W", "error"]
    if order == "early":
        arguments += ["-p", "llm_shared_lifecycle_gate"]
    if source == "override":
        for key, value in zip(_DEFAULTS, expected, strict=True):
            arguments += ["-o", f"{key}={value}"]
    monkeypatch.setattr(gate, "process_time", lambda: 0.0)
    assert run_inline(tmp_path, *arguments) == pytest.ExitCode.OK


def test_guarded_settings_remain_usable_without_gate(tmp_path: Path) -> None:
    """Tracked keys remain valid with strict configuration and warnings."""
    (tmp_path / "conftest.py").write_text(_SNIPPET, encoding="utf-8")
    (tmp_path / "pytest.ini").write_text("[pytest]\n" + "\n".join(f"{k}={v}" for k, v in _DEFAULTS.items()), encoding="utf-8")
    (tmp_path / "test_sample.py").write_text('def test_absent(pytestconfig):\n    assert not pytestconfig.pluginmanager.has_plugin("llm_shared_lifecycle_gate")\n', encoding="utf-8")
    assert run_inline(tmp_path, "--strict-config", "-W", "error") == pytest.ExitCode.OK


@pytest.mark.parametrize("key", list(_DEFAULTS))
@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "-inf", "word"])
def test_invalid_settings_name_the_key(tmp_path: Path, key: str, value: str) -> None:
    """Each setting refuses nonfinite, malformed and disabled values."""
    with pytest.raises(ValueError, match=key):
        gate.LifecycleGate.load(tmp_path, {**_DEFAULTS, key: value}.__getitem__)


def test_invalid_setting_exits_four_before_collection(tmp_path: Path) -> None:
    """A selected invalid policy is a usage error rather than a test failure."""
    (tmp_path / "test_sample.py").write_text('raise AssertionError("must not collect")\n', encoding="utf-8")
    assert run_inline(tmp_path, "-p", "llm_shared_lifecycle_gate", "-o", "test_lifecycle_cpu_drift_runs=1.5") == pytest.ExitCode.USAGE_ERROR


def _imports(tree: ast.Module) -> set[str]:
    """Collect root import names for the standalone dependency assertion."""
    imports = {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
    imports |= {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    return imports


def test_source_boundary_is_python310_and_stdlib_only() -> None:
    """The complete source parses at 3.10 with only allowed imports and no audit."""
    source = Path(gate.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source, feature_version=(3, 10))
    assert _imports(tree) <= sys.stdlib_module_names | {"pytest"}
    assert "addaudithook" not in source


def _contracts(tree: ast.Module) -> list[ast.Assign]:
    """Locate top-level literal-contract declarations without importing the policy."""
    return [node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "LOADER_CONTRACT_VERSION" for t in node.targets)]


def test_loader_contract_is_a_module_level_integer_literal() -> None:
    """Preparation can inspect exactly one stable declaration after the guard."""
    tree = ast.parse(Path(gate.__file__).read_text(encoding="utf-8"))
    contracts = _contracts(tree)
    assert len(contracts) == 1
    assert isinstance(contracts[0].value, ast.Constant)
    assert type(contracts[0].value.value) is int
    assert gate.LOADER_CONTRACT_VERSION == 1


@pytest.mark.parametrize("version", [(3, 10, 0), (3, 11, 9)])
def test_version_refusal_precedes_other_imports(version: tuple[int, int, int]) -> None:
    """Only sys/pytest imports execute before the identifying refusal."""
    source = Path(gate.__file__).read_text(encoding="utf-8")
    imported: list[str] = []

    def guarded_import(name: str, *_args: object, **_kwargs: object) -> object:
        imported.append(name)
        assert name in {"sys", "pytest"}
        return SimpleNamespace(version_info=version) if name == "sys" else pytest

    namespace = {"__builtins__": {"__import__": guarded_import}}
    with pytest.raises(pytest.UsageError, match=r"llm_shared_lifecycle_gate.*3\.12"):
        exec(compile(source, gate.__file__, "exec"), namespace)  # noqa: S102
    assert set(imported) == {"sys", "pytest"}


# eof
