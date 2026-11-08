"""Reject invalid declarations before setup, including unused fixture entries."""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import ast
from pathlib import Path, PureWindowsPath
from types import ModuleType, SimpleNamespace
from typing import cast

import llm_shared_process_audit as audit
import pytest

from tests.unit.tools.shared_lifecycle.inline_session import run_inline

_REGISTER = """
import pytest
def pytest_configure(config):
    config.addinivalue_line('markers', 'process_allowed(reason): process permission')
"""


@pytest.mark.parametrize("mark", [
    "pytest.mark.process_allowed", "pytest.mark.process_allowed()",
    "pytest.mark.process_allowed('why')", "pytest.mark.process_allowed(reason='')",
    "pytest.mark.process_allowed(reason='  ')", "pytest.mark.process_allowed(reason=3)",
    "pytest.mark.process_allowed(reason='why', extra=True)",
])
def test_malformed_test_permission_prevents_setup(tmp_path: Path, capsys: pytest.CaptureFixture[str], mark: str) -> None:
    """Malformed named-test reasons are usage errors before any setup."""
    (tmp_path / "conftest.py").write_text(_REGISTER, encoding="utf-8")
    (tmp_path / "test_case.py").write_text(f"""
import pytest
@pytest.fixture(autouse=True)
def never():
    raise AssertionError('SETUP STARTED')
@{mark}
def test_case(): pass
""", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.USAGE_ERROR
    output = capsys.readouterr()
    assert "process_allowed" in output.err
    assert "test_case" in output.err
    assert "SETUP STARTED" not in output.out


@pytest.mark.parametrize("level", ["module", "class"])
def test_inherited_permissions_are_invalid(tmp_path: Path, capsys: pytest.CaptureFixture[str], level: str) -> None:
    """A valid reason cannot turn a class or module mark into a test permission."""
    source = "pytestmark = pytest.mark.process_allowed(reason='why')\ndef test_case(): pass\n"
    if level == "class":
        source = "@pytest.mark.process_allowed(reason='why')\nclass TestCases:\n    def test_case(self): pass\n"
    (tmp_path / "conftest.py").write_text(_REGISTER, encoding="utf-8")
    (tmp_path / "test_case.py").write_text("import pytest\n" + source, encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.USAGE_ERROR
    assert level in capsys.readouterr().err


@pytest.mark.parametrize("declaration", [
    "[]", "{object(): 'why'}", "{service: ''}", "{service: 4}",
    "{service.__wrapped__: 'why'}",
    "{pytest.fixture(lambda: None): 'unregistered'}",
])
def test_all_fixture_entries_are_validated(tmp_path: Path, capsys: pytest.CaptureFixture[str], declaration: str) -> None:
    """Unused fixtures still require a dict, decorated registered keys and reasons."""
    (tmp_path / "conftest.py").write_text(_REGISTER + f"""
@pytest.fixture
def service(): pass
LLM_SHARED_PROCESS_FIXTURES = {declaration}
""", encoding="utf-8")
    (tmp_path / "test_case.py").write_text("def test_case(): pass\n", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.USAGE_ERROR
    assert "LLM_SHARED_PROCESS_FIXTURES" in capsys.readouterr().err


def test_empty_collected_module_is_validated(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A test module without items does not evade declaration validation."""
    (tmp_path / "test_empty.py").write_text("LLM_SHARED_PROCESS_FIXTURES = []\n", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.USAGE_ERROR
    assert "test_empty" in capsys.readouterr().err


@pytest.mark.parametrize("mode", ["imported", "conflicting", "ambiguous"])
def test_imported_fixture_resolution(tmp_path: Path, capsys: pytest.CaptureFixture[str], mode: str) -> None:
    """Imported decorated identity resolves once, rejects conflicts and aliases."""
    (tmp_path / "conftest.py").write_text(_REGISTER + """
@pytest.fixture(scope='session')
def service(): pass
LLM_SHARED_PROCESS_FIXTURES = {service: 'why'}
""", encoding="utf-8")
    extra = "alias = conftest.service\n" if mode == "ambiguous" else ""
    reason = "other" if mode == "conflicting" else "why"
    (tmp_path / "test_case.py").write_text(f"""
import conftest
{extra}
LLM_SHARED_PROCESS_FIXTURES = {{conftest.service: {reason!r}}}
def test_case(): pass
""", encoding="utf-8")
    code = run_inline(tmp_path, plugins=(audit,))
    assert code == (pytest.ExitCode.OK if mode == "imported" else pytest.ExitCode.USAGE_ERROR)
    if mode != "imported":
        assert "service" in capsys.readouterr().err


def test_parametrized_case_marker_is_local(tmp_path: Path) -> None:
    """One marked parameter permits its event without granting another case."""
    (tmp_path / "conftest.py").write_text(_REGISTER, encoding="utf-8")
    (tmp_path / "test_case.py").write_text("""
import pytest
from llm_shared_process_audit import get_hub
@pytest.mark.parametrize('allowed', [
    pytest.param(True, marks=pytest.mark.process_allowed(reason='case')),
    False,
])
def test_case(allowed):
    if allowed:
        get_hub().dispatch('os.system', ())
    else:
        with pytest.raises(RuntimeError, match='test_case.*os.system'):
            get_hub().dispatch('os.system', ())
""", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.OK


def test_standalone_source_contract() -> None:
    """The copied module parses on 3.10 and imports only stdlib and pytest."""
    tree = ast.parse(Path(audit.__file__).read_text(encoding="utf-8"), feature_version=(3, 10))
    assert _imports(tree) <= {"sys", "pytest", "re", "inspect", "collections", "contextlib", "dataclasses", "pathlib", "threading", "typing", "types"}
    assert _contract_versions(tree) == [1]


def _imports(tree: ast.Module) -> set[str]:
    """Collect the standalone module's declared dependencies."""
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    return imports


def _contract_versions(tree: ast.Module) -> list[object]:
    """Find literal contract versions available to source-only preparation."""
    return [node.value.value for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "LOADER_CONTRACT_VERSION" for target in node.targets)
                and isinstance(node.value, ast.Constant)]


@pytest.mark.parametrize("version", [(3, 10, 0), (3, 11, 9)])
def test_version_refusal_precedes_runtime_imports(version: tuple[int, int, int]) -> None:
    """Only sys and pytest load before refusing an unsupported interpreter."""
    source = Path(audit.__file__).read_text(encoding="utf-8")
    imported: list[str] = []

    def guarded_import(name: str, *_args: object, **_kwargs: object) -> object:
        imported.append(name)
        assert name in {"sys", "pytest"}
        return SimpleNamespace(version_info=version) if name == "sys" else pytest

    with pytest.raises(pytest.UsageError, match=r"llm_shared_process_audit.*3\.12"):
        exec(compile(source, audit.__file__, "exec"), {"__builtins__": {"__import__": guarded_import}})  # noqa: S102
    assert set(imported) == {"sys", "pytest"}


@pytest.mark.parametrize("registry", [None, {"service": 3}, {"service": [object()]}])
def test_incompatible_registry_is_identifying(tmp_path: Path, registry: object) -> None:
    """Defensive registry validation cannot silently disable unused declarations."""
    session = cast("pytest.Session", SimpleNamespace(_fixturemanager=SimpleNamespace(_arg2fixturedefs=registry)))
    with pytest.raises(pytest.UsageError, match="pytest fixture adapter"):
        audit.AuditSession(tmp_path).validate(session)


@pytest.mark.parametrize("member", ["execute", "finish", "addfinalizer"])
def test_incompatible_callables_fail_before_partial_patch(monkeypatch: pytest.MonkeyPatch, member: str) -> None:
    """Adapter attachment validates every required method before modifying any."""
    original_execute = pytest.FixtureDef[object].execute
    monkeypatch.setattr(pytest.FixtureDef, member, None)
    with pytest.raises(pytest.UsageError, match="pytest fixture adapter"):
        audit.AuditHub().attach(cast("pytest.Config", object()))
    if member != "execute":
        assert pytest.FixtureDef[object].execute is original_execute


def test_unsupported_definition_is_identifying() -> None:
    """Changed definition fields fail with the adapter name rather than later IO."""
    definition = cast("audit.Fixture", SimpleNamespace(func=None))
    with pytest.raises(pytest.UsageError, match="pytest fixture adapter"):
        audit._check_definition(definition)


def test_conflicting_test_reasons_fail_collection(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Two reasons on one function have no arbitrary winner."""
    (tmp_path / "conftest.py").write_text(_REGISTER, encoding="utf-8")
    (tmp_path / "test_case.py").write_text("""
import pytest
@pytest.mark.process_allowed(reason='one')
@pytest.mark.process_allowed(reason='two')
def test_case(): pass
""", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.USAGE_ERROR
    assert "conflicting process_allowed" in capsys.readouterr().err


def test_fixture_identity_merges_parameters_and_distinguishes_overrides(tmp_path: Path) -> None:
    """Definition identity includes source, qualified/name, registration and scope."""
    child = tmp_path / "child"
    child.mkdir()
    (tmp_path / "conftest.py").write_text(_REGISTER + """
@pytest.fixture(params=[1, 2])
def service(request): return request.param
LLM_SHARED_PROCESS_FIXTURES = {service: 'parent'}
""", encoding="utf-8")
    (child / "conftest.py").write_text("""
import pytest
@pytest.fixture
def service(): pass
LLM_SHARED_PROCESS_FIXTURES = {service: 'child'}
""", encoding="utf-8")
    (tmp_path / "test_parent.py").write_text("def test_parent(service): pass\n", encoding="utf-8")
    (child / "test_child.py").write_text("def test_child(service): pass\n", encoding="utf-8")
    states: list[audit.AuditSession] = []

    class Observe:
        """Inspect exercised state before unconfiguration detaches it."""

        def pytest_sessionfinish(self) -> None:
            states.append(audit.get_hub().sessions[-1])

    assert run_inline(tmp_path, plugins=(audit, Observe())) == pytest.ExitCode.OK
    records = list(states[0].records.values())
    expected_definitions = 2
    assert len(records) == expected_definitions
    assert {record.reason for record in records} == {"parent", "child"}
    assert all(not record.used and record.identity.endswith("|function") for record in records)
    assert all("conftest.py|service|service|" in record.identity for record in records)


def test_class_fixture_decorated_object_resolves(tmp_path: Path) -> None:
    """Class fixture binding keeps the original decorated definition identity."""
    (tmp_path / "test_case.py").write_text("""
import pytest
from llm_shared_process_audit import get_hub
class TestCases:
    @pytest.fixture
    def service(self):
        get_hub().dispatch('os.system', ())
    def test_case(self, service): pass
LLM_SHARED_PROCESS_FIXTURES = {TestCases.service: 'class fixture'}
""", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.OK


def test_legacy_registration_base_remains_in_identity(tmp_path: Path) -> None:
    """Supported registries without a registration node keep their base string."""
    definition = cast("audit.Fixture", SimpleNamespace(
        func=lambda: None, argname="declared", scope="module", baseid="child"))
    identity = audit.AuditSession(tmp_path)._identity(definition)
    assert identity.endswith("|declared|child|module")


@pytest.mark.parametrize("missing", ["registry", "unwrap", "conftests"])
def test_startup_adapter_capabilities_are_required(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, missing: str) -> None:
    """Registry and decorated-object changes are refused at session startup."""
    session = cast("pytest.Session", SimpleNamespace(
        config=SimpleNamespace(pluginmanager=SimpleNamespace(_conftest_plugins=set())),
        _fixturemanager=SimpleNamespace(_arg2fixturedefs={})))
    decorated = type(pytest.fixture(lambda: None))
    if missing == "registry":
        delattr(session, "_fixturemanager")
    elif missing == "unwrap":
        monkeypatch.setattr(decorated, "_get_wrapped_function", None)
    else:
        delattr(session.config.pluginmanager, "_conftest_plugins")
    with pytest.raises(pytest.UsageError, match="pytest fixture adapter"):
        audit.pytest_sessionstart(session)
    if missing == "unwrap":
        module = ModuleType("test_declaration")
        module.__dict__["LLM_SHARED_PROCESS_FIXTURES"] = {pytest.fixture(lambda: None): "why"}
        with pytest.raises(pytest.UsageError, match="unwrap"):
            audit.AuditSession(tmp_path)._declarations(module, {}, decorated)


def test_nonfunction_item_cannot_declare_permission(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Custom collectors cannot extend the named-test permission boundary."""
    (tmp_path / "conftest.py").write_text(_REGISTER + """
class Case(pytest.Item):
    def runtest(self): pass
class Cases(pytest.File):
    def collect(self):
        case = Case.from_parent(self, name='custom')
        case.add_marker(pytest.mark.process_allowed(reason='why'))
        yield case
def pytest_collect_file(file_path, parent):
    if file_path.suffix == '.txt':
        return Cases.from_parent(parent, path=file_path)
""", encoding="utf-8")
    (tmp_path / "test_custom.txt").write_text("", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.USAGE_ERROR
    assert "named test function" in capsys.readouterr().err


def test_missing_conftest_capability_is_usage_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A changed conftest registry refuses startup instead of omitting permissions."""
    class RemoveCapability:
        """Simulate an incompatible pytest version after configuration attaches."""

        def pytest_configure(self, config: pytest.Config) -> None:
            delattr(config.pluginmanager, "_conftest_plugins")

    (tmp_path / "test_case.py").write_text("def test_case(): pass\n", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit, RemoveCapability())) == pytest.ExitCode.USAGE_ERROR
    assert "pytest fixture adapter: missing conftest registry" in capsys.readouterr().err


def test_fixture_identity_across_windows_drives(monkeypatch: pytest.MonkeyPatch) -> None:
    """An imported plugin on another drive retains an absolute source identity."""
    class ResolvedWindowsPath(PureWindowsPath):
        """Use Windows anchors without filesystem access on any host OS."""

        def resolve(self) -> ResolvedWindowsPath:
            return self

    def plugin_source(_function: object) -> str:
        return "Z:/external/plugin.py"

    monkeypatch.setattr(audit, "Path", ResolvedWindowsPath)
    monkeypatch.setattr(audit.inspect, "getfile", plugin_source)
    definition = cast("audit.Fixture", SimpleNamespace(
        func=lambda: None, argname="service", scope="session", baseid=""))
    root = cast("Path", ResolvedWindowsPath("Y:/suite"))
    assert audit.AuditSession(root)._identity(definition).startswith("fixture:Z:/external/plugin.py|")


@pytest.mark.parametrize("invalid", [False, True])
def test_continued_collection_validates_remaining_modules(tmp_path: Path, capsys: pytest.CaptureFixture[str], *, invalid: bool) -> None:
    """Failed imports stay collection errors; other declarations validate before setup."""
    (tmp_path / "test_broken.py").write_text("raise ValueError('broken import')\n", encoding="utf-8")
    declaration = "[]" if invalid else "{}"
    (tmp_path / "test_case.py").write_text(f"""
LLM_SHARED_PROCESS_FIXTURES = {declaration}
def test_case(): print('TEST RAN')
""", encoding="utf-8")
    code = run_inline(tmp_path, "--continue-on-collection-errors", "--tb=no", plugins=(audit,))
    output = capsys.readouterr()
    assert code == (pytest.ExitCode.USAGE_ERROR if invalid else pytest.ExitCode.TESTS_FAILED)
    assert ("LLM_SHARED_PROCESS_FIXTURES" in output.err) == invalid
    assert ("TEST RAN" in output.out) != invalid
    assert "INTERNALERROR" not in output.out + output.err


# eof
