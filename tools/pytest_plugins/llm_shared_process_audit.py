"""Standalone process audit with session-local declarations and fixture ownership.

One process-lifetime dispatcher survives reload and alias imports. A bounded
pytest adapter delimits actual setup and finalization without changing caching.
Thread-local, live operation tokens prevent a fixture permission escaping its
own work. Nested collection remains subject to the innermost active test.
Workers validate before announcing collection; the controller stops on missing
or inconsistent evidence and combines exercised permissions exactly once.
"""

import sys

import pytest

if sys.version_info < (3, 12):
    raise pytest.UsageError("llm_shared_process_audit requires Python 3.12 or later")  # noqa: EM101, TRY003 - approved pre-refusal boundary

LOADER_CONTRACT_VERSION = 1

import inspect  # noqa: E402
import re  # noqa: E402
from collections.abc import Callable, Generator  # noqa: E402
from contextlib import contextmanager  # noqa: E402
from dataclasses import asdict, dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402
from threading import local  # noqa: E402
from types import ModuleType  # noqa: E402
from typing import cast  # noqa: E402

_EVENTS = frozenset({
    "subprocess.Popen", "_winapi.CreateProcess", "os.system", "os.posix_spawn",
    "os.spawn", "os.fork", "os.forkpty", "os.startfile", "os.exec",
})
_GUARD = "_llm_shared_process_audit_contract_1"
_GROUP_SUFFIX = re.compile(r"@[A-Za-z0-9._-]+$")
_DECLARATION = "LLM_SHARED_PROCESS_FIXTURES"
_ADAPTER = "pytest fixture adapter"
_CONFTESTS = "_conftest_plugins"
_RECORDS = "llm_shared_process_permissions"
_ERROR = "llm_shared_process_error"
_WORKER_RECORDS = "worker permission records"
_COLLECTION = "validated collection"
Fixture = pytest.FixtureDef[object]
FixtureCall = Callable[..., object]


def _usage(subject: str, detail: str) -> pytest.UsageError:
    """Build an identifying declaration or capability error."""
    return pytest.UsageError(f"llm_shared_process_audit: {subject}: {detail}")


def _reason(value: object, subject: str) -> str:
    """Accept only a nonempty textual reason."""
    if not isinstance(value, str) or not value.strip():
        raise _usage(subject, "requires a non-empty reason string")
    return value


@dataclass
class Permission:
    """One exercised test or fixture definition and its exclusive event credit."""

    kind: str
    identity: str
    reason: str
    used: bool = False


@dataclass
class AuditSession:
    """Isolate nested permissions and require every initial worker's evidence."""

    root: Path
    active: pytest.Item | None = None
    tests: dict[pytest.Item, str] = field(default_factory=dict[pytest.Item, str])
    fixtures: dict[Fixture, tuple[str, str]] = field(default_factory=dict[Fixture, tuple[str, str]])
    records: dict[str, Permission] = field(default_factory=dict[str, Permission])
    collectors: list[pytest.Module | pytest.Class] = field(default_factory=list[pytest.Module | pytest.Class])
    failed_collectors: set[str] = field(default_factory=set[str])
    expected_workers: int = 0
    announced: set[int] = field(default_factory=set[int])
    collection: list[str] | None = None
    barrier_complete: bool = False

    def exercise(self, kind: str, identity: str, reason: str) -> Permission:
        """Record entry once without marking a permission used before an event."""
        previous = self.records.get(identity)
        if previous is not None:
            if previous.kind != kind or previous.reason != reason:
                raise _usage(identity, "conflicting permission definition or reason")
            return previous
        permission = Permission(kind, identity, reason)
        self.records[identity] = permission
        return permission

    def merge(self, payload: object) -> None:
        """Validate transported records and OR usage without losing definitions."""
        if not isinstance(payload, list):
            raise _usage(_WORKER_RECORDS, "missing or invalid list")
        for entry in cast("list[object]", payload):
            if not isinstance(entry, dict):
                raise _usage(_WORKER_RECORDS, "invalid entry")
            record = cast("dict[str, object]", entry)
            kind, identity = record.get("kind"), record.get("identity")
            reason, used = record.get("reason"), record.get("used")
            if (kind not in ("test", "fixture") or not isinstance(identity, str)
                    or not identity.startswith(f"{kind}:") or not isinstance(reason, str)
                    or not reason.strip() or type(used) is not bool):
                raise _usage(_WORKER_RECORDS, "invalid definition or usage")
            permission = self.exercise(cast("str", kind), identity, reason)
            permission.used |= used

    def test_permission(self) -> Permission | None:
        """Return the carrying test's exercised permission, if declared."""
        if self.active is None or self.active not in self.tests:
            return None
        identity = "test:" + _GROUP_SUFFIX.sub("", self.active.nodeid)
        return self.exercise("test", identity, self.tests[self.active])

    def fixture_permission(self, fixture: Fixture) -> Permission | None:
        """Return an entered fixture definition's declared permission."""
        declaration = self.fixtures.get(fixture)
        return None if declaration is None else self.exercise("fixture", *declaration)

    def validate(self, session: pytest.Session) -> None:
        """Index registered definitions once and validate every collected declaration."""
        index = _fixture_index(session)
        decorated_type = type(pytest.fixture(lambda: None))
        for module in self._modules(session):
            self._declarations(module, index, decorated_type)
        self._test_marks(session.items)

    def _modules(self, session: pytest.Session) -> list[ModuleType]:
        """Collect declaration sources once, preserving original marker levels."""
        modules = {id(module): module for module in
                   cast("set[object]", getattr(session.config.pluginmanager, _CONFTESTS))
                   if isinstance(module, ModuleType)}
        for collector in self.collectors:
            if collector.nodeid in self.failed_collectors:
                continue
            if any(mark.name == "process_allowed" for mark in collector.own_markers):
                level = "module" if isinstance(collector, pytest.Module) else "class"
                raise _usage(collector.nodeid, f"process_allowed is invalid at {level} level")
            if isinstance(collector, pytest.Module):
                module = collector.obj
                modules[id(module)] = module
        return list(modules.values())

    def _test_marks(self, items: list[pytest.Item]) -> None:
        """Validate function/case reasons after rejecting inherited permissions."""
        for item in items:
            reasons: set[str] = set()
            for mark in item.own_markers:
                if mark.name == "process_allowed":
                    if mark.args or set(mark.kwargs) != {"reason"}:
                        raise _usage(item.nodeid, "malformed process_allowed(reason=...)")
                    reasons.add(_reason(mark.kwargs["reason"], item.nodeid + " process_allowed"))
            if len(reasons) > 1:
                raise _usage(item.nodeid, "conflicting process_allowed reasons")
            if reasons:
                if not isinstance(item, pytest.Function):
                    raise _usage(item.nodeid, "process_allowed requires a named test function")
                self.tests[item] = reasons.pop()

    def _declarations(self, module: ModuleType, index: dict[int, list[Fixture]], decorated_type: type) -> None:
        """Resolve decorated object identities in linear time, including unused entries."""
        if not hasattr(module, _DECLARATION):
            return
        subject = f"{module.__name__} {_DECLARATION}"
        declaration: object = getattr(module, _DECLARATION)
        if type(declaration) is not dict:
            raise _usage(subject, "requires a plain dictionary")
        for key, value in cast("dict[object, object]", declaration).items():
            if not isinstance(key, decorated_type):
                raise _usage(subject, "key must be an actual decorated fixture object")
            unwrap = getattr(key, "_get_wrapped_function", None)
            if not callable(unwrap):
                raise _usage(_ADAPTER, "missing decorated fixture unwrap capability")
            matches = index.get(_callable_key(unwrap()), [])
            name = str(getattr(key, "name", "<fixture>"))
            subject_key = f"{subject} {name}"
            if len(matches) != 1:
                raise _usage(subject_key, "fixture must resolve to exactly one registered definition")
            reason = _reason(value, subject_key)
            fixture = matches[0]
            previous = self.fixtures.get(fixture)
            if previous is not None and previous[1] != reason:
                raise _usage(subject_key, "conflicting fixture reasons")
            self.fixtures[fixture] = (self._identity(fixture), reason)

    def _identity(self, fixture: Fixture) -> str:
        """Keep overrides distinct and all parameter instances under one identity."""
        filename = inspect.getfile(fixture.func)
        source_path = Path(filename).resolve()
        try:
            source = source_path.relative_to(self.root.resolve(), walk_up=True).as_posix()
        except ValueError:
            source = source_path.as_posix()
        registration = getattr(fixture, "node", None)
        base = getattr(registration, "nodeid", None)
        if not isinstance(base, str):
            base = cast("str", getattr(fixture, "baseid", ""))
        qualified = str(getattr(fixture.func, "__qualname__", ""))
        return f"fixture:{source}|{qualified}|{fixture.argname}|{base}|{fixture.scope}"


def _fixture_index(session: pytest.Session) -> dict[int, list[Fixture]]:
    """Traverse the registry once; declaration lookups never rescan definitions."""
    manager = getattr(session, "_fixturemanager", None)
    registry = getattr(manager, "_arg2fixturedefs", None)
    if not isinstance(registry, dict):
        raise _usage(_ADAPTER, "missing fixture registry")
    index: dict[int, list[Fixture]] = {}
    seen: set[int] = set()
    for definitions in cast("dict[object, object]", registry).values():
        if not isinstance(definitions, (tuple, list)):
            raise _usage(_ADAPTER, "invalid fixture registry definitions")
        for definition in cast("list[object]", definitions):
            fixture = cast("Fixture", definition)
            if not isinstance(definition, pytest.FixtureDef):
                raise _usage(_ADAPTER, "invalid fixture definition")
            _check_definition(fixture)
            if id(fixture) not in seen:
                index.setdefault(_callable_key(fixture.func), []).append(fixture)
                seen.add(id(fixture))
    return index


def _callable_key(function: object) -> int:
    """Match pytest's bound class fixture to its decorated underlying function."""
    return id(getattr(function, "__func__", function))


def _check_definition(fixture: Fixture) -> None:
    """Refuse a changed pytest object before any test setup."""
    if (not callable(fixture.func) or not isinstance(getattr(fixture, "argname", None), str)
            or fixture.scope not in {"function", "class", "module", "package", "session"}
            or not hasattr(fixture, "cached_result")):
        raise _usage(_ADAPTER, "unsupported fixture definition capabilities")


@dataclass
class _Operation:
    """Bind one fixture operation to a session and a live thread-local token."""

    state: AuditSession | None
    fixture: Fixture | None
    live: bool = True


class AuditHub:
    """Own the lifetime dispatcher and restore only adapter-owned pytest methods."""

    def __init__(self) -> None:
        """Create no active state until a pytest configuration attaches."""
        self.sessions: list[AuditSession] = []
        self.active_sessions: list[AuditSession] = []
        self.configs: dict[pytest.Config, AuditSession] = {}
        self.threads = local()
        self.originals: dict[str, FixtureCall] = {}
        self.wrappers: dict[str, FixtureCall] = {}

    def attach(self, config: pytest.Config) -> AuditSession:
        """Attach once per config even if the plugin was imported under two names."""
        existing = self.configs.get(config)
        if existing is not None:
            return existing
        if not self.sessions:
            self._install_adapter()
        state = AuditSession(config.rootpath)
        self.configs[config] = state
        self.sessions.append(state)
        return state

    def detach(self, config: pytest.Config) -> None:
        """Restore on last detach while preserving a nested caller's live state."""
        state = self.configs.pop(config, None)
        if state is None:
            return
        self.sessions = [entry for entry in self.sessions if entry is not state]
        self.active_sessions = [entry for entry in self.active_sessions if entry is not state]
        if not self.sessions:
            for name, wrapper in self.wrappers.items():
                if getattr(pytest.FixtureDef, name) is wrapper:
                    setattr(pytest.FixtureDef, name, self.originals[name])
            self.wrappers.clear()
            self.originals.clear()

    def dispatch(self, event: str, _arguments: tuple[object, ...]) -> None:
        """Reject unpermitted starts without any IO or scan of declarations."""
        if event not in _EVENTS or not self.active_sessions:
            return
        state = self.active_sessions[-1]
        item = cast("pytest.Item", state.active)
        fixture = self._owner(state)
        permission = state.fixture_permission(fixture) if fixture is not None else None
        if permission is None and (fixture is None or fixture.scope == "function"):
            permission = state.test_permission()
        if permission is None:
            message = f"{item.nodeid}: process event {event} is not permitted"
            raise RuntimeError(message)
        permission.used = True

    def _owner(self, state: AuditSession) -> Fixture | None:
        """Use only a live operation on this thread and in the active session."""
        operations = cast("list[_Operation]", getattr(self.threads, "operations", []))
        operation = operations[-1] if operations else None
        if operation is not None and operation.live and operation.state is state:
            return operation.fixture
        return None

    @contextmanager
    def operation(self, state: AuditSession | None, fixture: Fixture | None) -> Generator[None, None, None]:
        """Replace a requesting owner and unwind every failure path."""
        operations = cast("list[_Operation]", getattr(self.threads, "operations", []))
        self.threads.operations = operations
        token = _Operation(state, fixture)
        operations.append(token)
        if state is not None and fixture is not None and state.active is not None:
            state.fixture_permission(fixture)
        try:
            yield
        finally:
            token.live = False
            operations.pop()

    def _install_adapter(self) -> None:
        """Validate and patch exactly the bounded execution/finalization surface."""
        for name in ("execute", "finish"):
            method = getattr(pytest.FixtureDef, name, None)
            if not callable(method) or tuple(inspect.signature(method).parameters) != ("self", "request"):
                raise _usage(_ADAPTER, f"unsupported FixtureDef.{name}(self, request)")
        if not callable(getattr(pytest.FixtureDef, "addfinalizer", None)):
            raise _usage(_ADAPTER, "missing FixtureDef.addfinalizer")
        originals = {name: cast("FixtureCall", getattr(pytest.FixtureDef, name)) for name in ("execute", "finish")}

        def execute(fixture: Fixture, request: pytest.FixtureRequest) -> object:
            state = self.configs.get(request.config)
            # Cache/dependency resolution cannot borrow the requester's permission.
            with self.operation(state, None):
                return originals["execute"](fixture, request)

        def finish(fixture: Fixture, request: pytest.FixtureRequest) -> object:
            state = self.configs.get(request.config)
            owner = fixture if fixture.cached_result is not None else None
            with self.operation(state, owner):
                return originals["finish"](fixture, request)

        self.originals = originals
        self.wrappers = {"execute": execute, "finish": finish}
        for name, wrapper in self.wrappers.items():
            setattr(pytest.FixtureDef, name, wrapper)


def get_hub() -> AuditHub:
    """Return the process-wide hub across reloads and arbitrary module aliases."""
    hub = cast("AuditHub | None", getattr(sys, _GUARD, None))
    if hub is None:
        hub = AuditHub()
        sys.addaudithook(hub.dispatch)
        setattr(sys, _GUARD, hub)
    return hub


def pytest_configure(config: pytest.Config) -> None:
    """Attach audit state independently of the timing gate."""
    get_hub().attach(config)


def pytest_unconfigure(config: pytest.Config) -> None:
    """Remove this session even after collection or execution errors."""
    get_hub().detach(config)


def pytest_collectstart(collector: pytest.Collector) -> None:
    """Remember modules without tests and original class/module marker levels."""
    if isinstance(collector, (pytest.Module, pytest.Class)):
        get_hub().configs[collector.config].collectors.append(collector)


def pytest_collectreport(report: pytest.CollectReport) -> None:
    """Avoid retrying failed collector objects when validating remaining sources."""
    if report.failed:
        get_hub().sessions[-1].failed_collectors.add(report.nodeid)


@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    """Refuse a missing registry or decorated-object adapter before collection."""
    manager = getattr(session, "_fixturemanager", None)
    if not isinstance(getattr(manager, "_arg2fixturedefs", None), dict):
        raise _usage(_ADAPTER, "missing fixture registry")
    if not callable(getattr(pytest.fixture(lambda: None), "_get_wrapped_function", None)):
        raise _usage(_ADAPTER, "missing decorated fixture unwrap capability")
    if not isinstance(getattr(session.config.pluginmanager, _CONFTESTS, None), set):
        raise _usage(_ADAPTER, "missing conftest registry")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_finish(session: pytest.Session) -> None:
    """Withhold xdist's announcement until declarations have been validated."""
    try:
        get_hub().configs[session.config].validate(session)
    except pytest.UsageError as error:
        output = getattr(session.config, "workeroutput", None)
        if isinstance(output, dict):
            output[_ERROR] = str(error)
        raise


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_setupnodes(config: pytest.Config, specs: list[object]) -> None:
    """Count initial workers before any collection announcement can arrive."""
    get_hub().configs[config].expected_workers = len(specs)


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_node_collection_finished(node: object, ids: list[str]) -> None:
    """Refuse mismatches before xdist adds this collection to its scheduler."""
    state = get_hub().configs[cast("pytest.Config", getattr(node, "config", None))]
    if state.collection is not None and state.collection != ids:
        raise _usage(_COLLECTION, "inconsistent worker collection")
    state.collection = ids
    state.announced.add(id(node))
    state.barrier_complete |= len(state.announced) == state.expected_workers


@pytest.hookimpl(optionalhook=True)
def pytest_testnodedown(node: object, error: object) -> None:
    """Stop on early exit rather than waiting for evidence that cannot arrive."""
    config = cast("pytest.Config", getattr(node, "config", None))
    state = get_hub().configs[config]
    output = cast("dict[str, object]", getattr(node, "workeroutput", {}))
    diagnostic = output.get(_ERROR)
    if diagnostic:
        subject = "worker declaration"
        raise _usage(subject, str(diagnostic))
    interrupted = output.get("exitstatus") == pytest.ExitCode.INTERRUPTED
    if not state.barrier_complete and not interrupted:
        controller = config.pluginmanager.getplugin("dsession")
        if not (getattr(controller, "shouldstop", False) or getattr(controller, "shuttingdown", False)):
            raise _usage(_COLLECTION, "worker exited before all validated collection evidence arrived")
    # A crash may have no session-finish output. Let xdist report/restart it;
    # successful workers still owe records, and any records sent are validated.
    if _RECORDS in output or (error is None and not interrupted):
        state.merge(output.get(_RECORDS))


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Publish records before xdist's outer session-finish wrapper sends them."""
    output = getattr(session.config, "workeroutput", None)
    if isinstance(output, dict):
        state = get_hub().configs[session.config]
        output[_RECORDS] = [asdict(permission) for permission in state.records.values()]


def pytest_terminal_summary(terminalreporter: "pytest.TerminalReporter", config: pytest.Config) -> None:
    """Print one serial or controller report, omitting unexercised declarations."""
    records = get_hub().configs[config].records
    if not records or hasattr(config, "workerinput"):
        return
    groups: dict[str, list[Permission]] = {"test": [], "fixture": []}
    for permission in records.values():
        groups[permission.kind].append(permission)
    terminalreporter.section("process permissions")
    for kind, entries in groups.items():
        terminalreporter.write_line(f"{kind.title()} permissions ({len(entries)})")
        for permission in entries:
            status = "used" if permission.used else "WARNING unused"
            terminalreporter.write_line(f"  {permission.identity}: {permission.reason} [{status}]")


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_protocol(item: pytest.Item) -> Generator[None, object, object]:
    """Enforce setup through teardown with the carrying test identity."""
    hub = get_hub()
    state = hub.configs[item.config]
    previous = state.active
    state.active = item
    hub.active_sessions.append(state)
    state.test_permission()
    try:
        return (yield)
    finally:
        hub.active_sessions.pop()
        state.active = previous


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_fixture_setup(fixturedef: Fixture, request: pytest.FixtureRequest) -> Generator[None, object, object]:
    """Enter only actual own setup; cached accesses never enter this hook."""
    hub = get_hub()
    with hub.operation(hub.configs.get(request.config), fixturedef):
        return (yield)


# eof
