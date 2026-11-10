"""Build executable standalone-policy contracts in isolated temporary projects.

Generated tests use only the supported interpreter, stdlib and pytest. Real
process starts and CPU work belong here, outside the audited carrying suite.
"""

from __future__ import annotations

from dataclasses import dataclass

GATE = "llm_shared_lifecycle_gate"
AUDIT = "llm_shared_process_audit"
LOADER = "llm_shared_pytest_loader"
_KEYS = {"test_lifecycle_limit": "0.1", "test_lifecycle_wall_limit": "1.0",
         "test_lifecycle_cpu_band_factor": "2.5", "test_lifecycle_cpu_drift_runs": "3"}
_REGISTER = """import pytest
def pytest_addoption(parser):
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
    return subprocess.run([sys.executable, "-I", "-c", "pass"], check=True, timeout=5)
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
    """One executable verdict, including identifying diagnostics and summaries."""

    name: str
    plugins: tuple[str, ...]
    source: str
    ini: str = ""
    conftest: str = ""
    options: tuple[str, ...] = ()
    code: int = 0
    contains: tuple[str, ...] = ()
    summaries: tuple[tuple[str, int], ...] = ()
    prepared: str = ""
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
    return (*matrix,
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
