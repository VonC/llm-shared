"""Build executable standalone-policy contracts in isolated temporary projects.

Generated tests use only the supported interpreter, stdlib and pytest. Real
process starts and CPU work belong here, outside the audited carrying suite.
Prepared selection and distributed fixture usage retain separate verdicts.
Worker cases explicitly load xdist because the harness disables plugin autoload.
Empty process probes skip site initialization while retaining real child starts.
Consumer package construction keeps collision checks separate from execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def write_consumer_packages(root: Path) -> None:
    """Build consumer-owned packages and verify their identities in the child."""
    for name in ("tools", "tests"):
        package = root / name
        package.mkdir()
        (package / "__init__.py").write_text("CONSUMER_PACKAGE = True\n", encoding="utf-8")
    with (root / "test_behavior.py").open("a", encoding="utf-8") as source:
        source.write("""
def test_consumer_packages():
    import tools, tests
    from pathlib import Path
    for package in (tools, tests):
        assert package.CONSUMER_PACKAGE is True
        assert Path(package.__file__).resolve().parent.parent == Path(__file__).resolve().parent
""")


GATE = "llm_shared_lifecycle_gate"
AUDIT = "llm_shared_process_audit"
LOADER = "llm_shared_pytest_loader"
_KEYS = {"test_lifecycle_limit": "0.1", "test_lifecycle_wall_limit": "1.0",
         "test_lifecycle_cpu_band_factor": "2.5", "test_lifecycle_cpu_drift_runs": "3"}
_REGISTER = """import pytest
def pytest_addoption(parser, pluginmanager):
    if not pluginmanager.has_plugin("llm_shared_lifecycle_gate"):
        for key, value in {keys!r}.items():
            parser.addini(key, "lifecycle setting", default=value)
"""
_BASIC = """def test_configuration(pytestconfig):
    expected = {expected!r}
    for key, value in expected.items():
        assert pytestconfig.getini(key) == value
"""
_START = """import subprocess
import sys
import pytest

def start():
    return subprocess.run([sys.executable, "-I", "-S", "-c", "pass"], check=True, timeout=5)
"""
_PROCESS = _START + """
@pytest.mark.process_allowed(reason="executable permission probe")
def test_allowed():
    assert start().returncode == 0

def test_rejected():
    with pytest.raises(RuntimeError, match="not permitted"):
        start()
"""
_FIXTURES = _START + """
from threading import Thread

@pytest.fixture(scope="module")
def owner(request):
    assert start().returncode == 0
    errors = []
    def foreign_thread():
        try:
            start()
        except RuntimeError:
            errors.append("rejected")
    worker = Thread(target=foreign_thread)
    worker.start()
    worker.join(timeout=5)
    assert not worker.is_alive()
    assert errors == ["rejected"]
    request.addfinalizer(lambda: start())
    yield
    assert start().returncode == 0

LLM_SHARED_PROCESS_FIXTURES = {owner: "fixture operation probe"}

@pytest.fixture
def unrelated(owner):
    with pytest.raises(RuntimeError, match="not permitted"):
        start()
    yield
    with pytest.raises(RuntimeError, match="not permitted"):
        start()

def test_fixture_ownership(owner, unrelated):
    with pytest.raises(RuntimeError, match="not permitted"):
        start()
"""
_NESTED = _START + """
from pathlib import Path

@pytest.mark.process_allowed(reason="outer permission must not escape")
def test_nested(tmp_path):
    inner = tmp_path / "inner"
    inner.mkdir()
    (inner / "pytest.ini").write_text("[pytest]\\n")
    (inner / "test_inner.py").write_text(
        "import sys, subprocess, pytest\\n"
        "def test_denied():\\n"
        "    with pytest.raises(RuntimeError, match='not permitted'):\\n"
        "        subprocess.run([sys.executable, '-I', '-c', 'pass'])\\n")
    assert pytest.main(["-c", str(inner / "pytest.ini"), "--rootdir", str(inner),
                        "--confcutdir", str(inner), "-p", "llm_shared_process_audit", str(inner)]) == 0
    assert start().returncode == 0
"""
_BUDGET = """from time import process_time
def test_cpu_rejection():
    deadline = process_time() + 0.03
    while process_time() < deadline:
        pass
"""


@dataclass(frozen=True)
class Case:
    """One executable verdict, with optional preparation and summary counts."""

    name: str
    plugins: tuple[str, ...]
    source: str
    ini: str = ""
    conftest: str = ""
    options: tuple[str, ...] = ()
    code: int = 0
    contains: tuple[str, ...] = ()
    summaries: tuple[tuple[str, int], ...] = ()
    prepared: str | None = None
    optional_absent: bool = False


def cases() -> tuple[Case, ...]:
    """Enumerate finite policy, configuration, ownership and loading contracts."""
    matrix = tuple(
        Case("policies-" + str(index), plugins, _BASIC.format(expected=_KEYS),
             conftest="" if GATE in plugins else _REGISTER.format(keys=_KEYS),
             options=("--strict-config", "--strict-markers"),
             summaries=(("lifecycle CPU band", int(GATE in plugins)),))
        for index, plugins in enumerate(((), (GATE,), (AUDIT,), (GATE, AUDIT)))
    )
    configured = dict(_KEYS, test_lifecycle_limit="0.5", test_lifecycle_wall_limit="2.0",
                      test_lifecycle_cpu_band_factor="3.0", test_lifecycle_cpu_drift_runs="4")
    config = "".join(f"{key} = {value}\n" for key, value in configured.items())
    prepared = tuple(
        Case("prepared-" + str(index), (LOADER,), _BASIC.format(expected=_KEYS),
             conftest=_REGISTER.format(keys=_KEYS), prepared=selection,
             options=("--strict-config", "--strict-markers"),
             summaries=(("lifecycle CPU band", int("lifecycle" in selection)),))
        for index, selection in enumerate(("", "lifecycle", "process", "lifecycle,process"))
    )
    return (*matrix, *prepared,
            Case("guard-late", (), _BASIC.format(expected=_KEYS),
                 conftest=_REGISTER.format(keys=_KEYS) + f"pytest_plugins = [{GATE!r}]\n"),
            Case("prepared-explicit", (LOADER, GATE, AUDIT), _PROCESS, prepared="lifecycle,process",
                 ini="test_lifecycle_limit = 1.0\ntest_lifecycle_wall_limit = 10.0\n",
                 summaries=(("process permissions", 1), ("lifecycle CPU band", 1))),
            Case("workers-aggregate", (GATE, AUDIT, "xdist.plugin"), _PROCESS, options=("-n", "2"),
                 ini="test_lifecycle_limit = 1.0\ntest_lifecycle_wall_limit = 10.0\n",
                 contains=("[used]",), summaries=(("process permissions", 1), ("lifecycle CPU band", 1))),
            Case("workers-fixtures", (AUDIT, "xdist.plugin"), _FIXTURES.replace(
                "def test_fixture_ownership(owner, unrelated):",
                '@pytest.mark.parametrize("item", [0, 1, 2, 3])\ndef test_fixture_ownership(owner, unrelated, item):'),
                 options=("-n", "2"), contains=("[used]",),
                 summaries=(("Fixture permissions (1)", 1), ("process permissions", 1))),
            Case("gate-process-only", (GATE,), _START + "\ndef test_start():\n    assert start().returncode == 0\n",
                 ini="test_lifecycle_limit = 1.0\ntest_lifecycle_wall_limit = 10.0\n",
                 summaries=(("lifecycle CPU band", 1), ("process permissions", 0))),
            Case("tracked", (GATE,), _BASIC.format(expected=configured), ini=config),
            Case("override", (GATE,), _BASIC.format(expected=_KEYS), ini=config,
                 options=tuple(arg for key, value in _KEYS.items() for arg in ("-o", f"{key}={value}"))),
            Case("process", (AUDIT,), _PROCESS, summaries=(("process permissions", 1),), contains=("[used]",)),
            Case("fixtures", (AUDIT,), _FIXTURES, summaries=(("process permissions", 1),), contains=("[used]",)),
            Case("nested", (AUDIT,), _NESTED, summaries=(("process permissions", 1),)),
            Case("budget", (GATE,), _BUDGET, ini="test_lifecycle_limit = 0.001\n", code=1,
                 contains=("lifecycle", "CPU="), summaries=(("lifecycle CPU band", 1),)),
            Case("prepared-both", (LOADER,), _PROCESS, prepared="lifecycle,process",
                 ini="test_lifecycle_limit = 1.0\ntest_lifecycle_wall_limit = 10.0\n",
                 summaries=(("process permissions", 1), ("lifecycle CPU band", 1))),
            Case("optional-absent", (GATE, AUDIT), _PROCESS, optional_absent=True,
                 ini="test_lifecycle_limit = 1.0\ntest_lifecycle_wall_limit = 10.0\n",
                 summaries=(("process permissions", 1), ("lifecycle CPU band", 1))),
            Case("invalid-declaration", (AUDIT,), 'import pytest\n@pytest.mark.process_allowed(reason="")\ndef test_bad(): pass\n',
                 conftest="", code=4, contains=("requires a non-empty reason string",)),
            )


# eof
