"""Exercise actual pytest fixture boundaries with synthetic process events.

Nested-session checks reuse the carrying pytest config as their outer session,
avoiding a redundant generated parent project while retaining real child hooks.
The fixture-scope matrix keeps declarations in its collected test module and
uses explicit configuration, avoiding a second import and config discovery.
"""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import importlib
import importlib.util
import sys
from typing import TYPE_CHECKING, cast

import llm_shared_process_audit as audit
import pytest

from tests.unit.tools.shared_lifecycle.inline_session import run_inline

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

_PRELUDE = """
import pytest
from llm_shared_process_audit import get_hub
def event(): get_hub().dispatch('subprocess.Popen', ())
def pytest_configure(config):
    config.addinivalue_line('markers', 'process_allowed(reason): process permission')
"""


@pytest.mark.parametrize("scope", ["function", "class", "module", "package", "session"])
@pytest.mark.parametrize("fixture_allowed", [False, True])
@pytest.mark.parametrize("test_allowed", [False, True])
def test_fixture_precedence_and_credit(tmp_path: Path, scope: str, *, fixture_allowed: bool, test_allowed: bool) -> None:
    """The most specific owner applies during setup, finalizer and yield cleanup."""
    permitted = fixture_allowed or (test_allowed and scope == "function")
    body = "event()" if permitted else "with pytest.raises(RuntimeError, match='subprocess.Popen'):\n        event()"
    declaration = "LLM_SHARED_PROCESS_FIXTURES = {service: 'fixture'}" if fixture_allowed else ""
    mark = "@pytest.mark.process_allowed(reason='test')\n" if test_allowed else ""
    configuration = tmp_path / "pytest.ini"
    configuration.write_text("[pytest]\nmarkers =\n    process_allowed(reason): process permission\n", encoding="utf-8")
    (tmp_path / "test_case.py").write_text(_PRELUDE + f"""
def check():
    {body}
@pytest.fixture(scope={scope!r})
def service(request):
    check()
    request.addfinalizer(check)
    yield
    check()
{declaration}
{mark}def test_case(service): pass
""", encoding="utf-8")
    states: list[audit.AuditSession] = []

    class Observe:
        """Retain detached state to inspect exclusive permission credit."""

        def pytest_sessionfinish(self) -> None:
            states.append(audit.get_hub().sessions[-1])

    assert run_inline(tmp_path, "-c", str(configuration), "--noconftest", plugins=(audit, Observe())) == pytest.ExitCode.OK
    _assert_credit(states[0], (fixture_allowed, test_allowed, permitted))
    assert audit.get_hub().sessions == []


def _assert_credit(state: audit.AuditSession, expected: tuple[bool, bool, bool]) -> None:
    """Check exclusive test/fixture credit separately from constructing a session."""
    fixture_allowed, test_allowed, permitted = expected
    records = list(state.records.values())
    fixtures = [record for record in records if record.kind == "fixture"]
    tests = [record for record in records if record.kind == "test"]
    assert len(fixtures) == int(fixture_allowed)
    assert len(tests) == int(test_allowed)
    assert all(record.used for record in fixtures)
    assert all(record.used == (permitted and not fixture_allowed) for record in tests)


def test_nested_dynamic_dependencies_and_cached_access(tmp_path: Path) -> None:
    """Requested dependency setup/finalization replaces and restores its owner."""
    (tmp_path / "conftest.py").write_text(_PRELUDE + """
@pytest.fixture(scope='session')
def dependency():
    with pytest.raises(RuntimeError): event()
    yield
    with pytest.raises(RuntimeError): event()
@pytest.fixture(scope='session')
def service(request):
    event()
    request.getfixturevalue('dependency')
    event()
    request.getfixturevalue('dependency')
    event()
    yield
    event()
LLM_SHARED_PROCESS_FIXTURES = {service: 'own only'}
""", encoding="utf-8")
    (tmp_path / "test_case.py").write_text("def test_case(service): pass\n", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.OK


@pytest.mark.parametrize("failure", ["setup", "yield", "finalizer"])
def test_failed_fixture_operation_unwinds(tmp_path: Path, failure: str) -> None:
    """Setup and both cleanup failures cannot leave the next test exempt."""
    (tmp_path / "conftest.py").write_text(_PRELUDE + f"""
def fail():
    event()
    raise ValueError('expected fixture failure')
@pytest.fixture
def service(request):
    event()
    if {failure!r} == 'setup': fail()
    if {failure!r} == 'finalizer': request.addfinalizer(fail)
    yield
    if {failure!r} == 'yield': fail()
LLM_SHARED_PROCESS_FIXTURES = {{service: 'own only'}}
""", encoding="utf-8")
    (tmp_path / "test_case.py").write_text("""
import pytest
from llm_shared_process_audit import get_hub
def test_first(service): pass
def test_second():
    with pytest.raises(RuntimeError): get_hub().dispatch('os.fork', ())
""", encoding="utf-8")
    original_execute, original_finish = pytest.FixtureDef[object].execute, pytest.FixtureDef[object].finish
    assert run_inline(tmp_path, "--tb=no", plugins=(audit,)) == pytest.ExitCode.TESTS_FAILED
    assert pytest.FixtureDef[object].execute is original_execute
    assert pytest.FixtureDef[object].finish is original_finish
    assert audit.get_hub().sessions == []
    audit.get_hub().dispatch("os.fork", ())


def test_thread_and_copied_context_do_not_inherit_fixture_permission(tmp_path: Path) -> None:
    """Another thread and a deferred copied context use the current lifecycle."""
    (tmp_path / "conftest.py").write_text(_PRELUDE + """
from contextvars import copy_context
from threading import Thread
@pytest.fixture
def service():
    context = copy_context()
    failures = []
    def background():
        try: context.run(event)
        except RuntimeError: failures.append('rejected')
    thread = Thread(target=background)
    thread.start()
    thread.join()
    assert failures == ['rejected']
    event()
    return context
LLM_SHARED_PROCESS_FIXTURES = {service: 'own only'}
""", encoding="utf-8")
    (tmp_path / "test_case.py").write_text("""
import pytest
from llm_shared_process_audit import get_hub
def test_case(service):
    with pytest.raises(RuntimeError): service.run(get_hub().dispatch, 'os.exec', ())
""", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.OK


def test_reload_preserves_dispatcher() -> None:
    """Reloading the standalone module retains its process-lifetime hub."""
    hub = audit.get_hub()
    assert importlib.reload(audit).get_hub() is hub


def test_alias_preserves_dispatcher() -> None:
    """An arbitrary module alias retains the same process-lifetime hub."""
    hub = audit.get_hub()
    spec = importlib.util.spec_from_file_location("audit_alias", audit.__file__)
    assert spec is not None
    assert spec.loader is not None
    alias = importlib.util.module_from_spec(spec)
    sys.modules["audit_alias"] = alias
    try:
        spec.loader.exec_module(alias)
        assert alias.get_hub() is hub
    finally:
        sys.modules.pop("audit_alias")


@pytest.mark.parametrize("allowed", [False, True])
def test_nested_sessions_preserve_outer_owner(tmp_path: Path, capsys: pytest.CaptureFixture[str], request: pytest.FixtureRequest, *, allowed: bool) -> None:
    """Inactive children use the active outer test; active children own their work."""
    hub = audit.get_hub()
    child = tmp_path
    item = request._pyfuncitem
    collection = "get_hub().dispatch('os.system', ())" if allowed else f"""
with pytest.raises(RuntimeError) as caught:
    get_hub().dispatch('os.system', ())
assert {item.nodeid!r} in str(caught.value)
"""
    (child / "test_child.py").write_text(f"""
import pytest
from llm_shared_process_audit import get_hub
{collection}
def test_child():
    with pytest.raises(RuntimeError, match='test_child.py::test_child'):
        get_hub().dispatch('os.system', ())
""", encoding="utf-8")
    state = hub.attach(request.config)
    # Synthetic permission state; no process permission is declared for the suite.
    if allowed:
        state.tests[item] = "outer"
    protocol = audit.pytest_runtest_protocol(item)
    next(protocol)
    try:
        assert len(hub.sessions) == 1
        _assert_outer_event(hub, item, allowed=allowed)
        # Profiled startup support is unrelated to ownership; retain the reporter.
        code = run_inline(child, "-p", "no:debugging", "-p", "no:terminalprogress", plugins=(audit,))
        output = capsys.readouterr()
        assert code == pytest.ExitCode.OK, output.out + output.err
        assert len(hub.sessions) == 1
        _assert_outer_event(hub, item, allowed=allowed)
    finally:
        protocol.close()
        hub.detach(request.config)
    assert hub.sessions == []
    assert hub.active_sessions == []


def _assert_outer_event(hub: audit.AuditHub, item: pytest.Item, *, allowed: bool) -> None:
    """Check carrying attribution before and after an embedded session."""
    if allowed:
        hub.dispatch("os.system", ())
    else:
        with pytest.raises(RuntimeError) as caught:
            hub.dispatch("os.system", ())
        assert item.nodeid in str(caught.value)


@pytest.mark.parametrize("event", [
    "subprocess.Popen", "_winapi.CreateProcess", "os.system", "os.posix_spawn",
    "os.spawn", "os.fork", "os.forkpty", "os.startfile", "os.exec",
])
def test_all_process_events_cover_entire_protocol(tmp_path: Path, event: str) -> None:
    """Collection is inactive; setup, call and teardown reject carrying events."""
    (tmp_path / "conftest.py").write_text(_PRELUDE + f"""
get_hub().dispatch({event!r}, ())
@pytest.fixture(autouse=True)
def phases():
    with pytest.raises(RuntimeError, match='test_case'): get_hub().dispatch({event!r}, ())
    yield
    with pytest.raises(RuntimeError, match='test_case'): get_hub().dispatch({event!r}, ())
""", encoding="utf-8")
    (tmp_path / "test_case.py").write_text(f"""
import pytest
from llm_shared_process_audit import get_hub
def test_case():
    get_hub().dispatch('unrelated.event', ())
    with pytest.raises(RuntimeError, match='test_case'): get_hub().dispatch({event!r}, ())
""", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == pytest.ExitCode.OK


def test_dispatcher_is_installed_only_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """The sys-owned guard, rather than a module flag, owns hook installation."""
    installed: list[object] = []
    monkeypatch.setattr(sys, audit._GUARD, None)
    monkeypatch.setattr(sys, "addaudithook", installed.append)
    hub = audit.get_hub()
    assert audit.get_hub() is hub
    assert installed == [hub.dispatch]


def test_detach_preserves_replacement_and_is_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A later third-party wrapper belongs to that party after audit detaches."""
    original = pytest.FixtureDef[object].execute

    def replacement(*args: object, **kwargs: object) -> object:
        return cast("Callable[..., object]", original)(*args, **kwargs)

    class Replace:
        """Replace only at session finish, after the audit has executed tests."""

        def pytest_sessionfinish(self, session: pytest.Session) -> None:
            assert audit.get_hub().attach(session.config) is audit.get_hub().sessions[-1]
            monkeypatch.setattr(pytest.FixtureDef, "execute", replacement)

    (tmp_path / "test_case.py").write_text("def test_case(): pass\n", encoding="utf-8")
    # Register restoration before the adapter is installed, so undo restores the original.
    monkeypatch.setattr(pytest.FixtureDef, "execute", original)
    assert run_inline(tmp_path, plugins=(audit, Replace())) == pytest.ExitCode.OK
    assert pytest.FixtureDef[object].execute is replacement
    audit.get_hub().detach(cast("pytest.Config", object()))
    monkeypatch.undo()
    assert pytest.FixtureDef[object].execute is original


# eof
