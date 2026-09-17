"""Keep home selection explicit and startup bounded without real sleeps."""

# ruff: noqa: PLR2004 - Exact call counts and exit codes are test expectations.

from __future__ import annotations

import contextlib
import io
import json
import runpy
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier, Lock
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from tools.wait_service import runtime
from tools.wait_service.models import WaitError
from tools.wait_service.protocol import Frame, Hello, decode_frame, encode_frame
from tools.wait_service.runtime import (
    Authority,
    RuntimeOptions,
    ensure_started,
    request,
    resolve_home,
    run_authority,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Generator


class FakeResource:
    """Record cleanup order, including resources opened before a startup failure."""

    def __init__(self, events: list[str], name: str) -> None:
        """Use a shared ledger instead of real files or OS handles."""
        self.events, self.name = events, name

    def close(self) -> None:
        """Record exactly the release requested by the lifecycle owner."""
        self.events.append(self.name)


class FakeConnection:
    """Already-authenticated bounded bytes, independent of native pipe testing."""

    def __init__(self, frames: list[Frame], sid: str) -> None:
        """Predeclare peer bytes; application writes remain independently visible."""
        self.stream = io.BytesIO(b"".join(encode_frame(frame) for frame in frames))
        self.verified_sid = sid
        self.writes: list[Frame] = []
        self.closed = False

    def read(self, count: int) -> bytes:
        """Return only requested bytes, including EOF for a truncated exchange."""
        return self.stream.read(count)

    def write(self, data: bytes) -> None:
        """Retain exactly the frames sent to the peer."""
        self.writes.append(decode_frame(data))

    def close(self) -> None:
        """Mark connection cleanup for refusal and successful exchanges alike."""
        self.closed = True


class FakeListener(FakeResource):
    """Serve one deterministic connection while retaining singleton ownership."""

    def __init__(self, events: list[str]) -> None:
        """Expose a connection only when the test explicitly supplies one."""
        super().__init__(events, "pipe")
        self.connection: FakeConnection | None = None

    @contextlib.contextmanager
    def accept(self, _timeout: float) -> Generator[FakeConnection]:
        """Mirror native listener cleanup without owning its borrowed handle."""
        assert self.connection is not None
        try:
            yield self.connection
        finally:
            self.connection.close()


class FakeTransport:
    """Inject lock contention, discovery and authenticated endpoint availability."""

    def __init__(self) -> None:
        """No process is reachable until a test provides its hello."""
        self.events: list[str] = []
        self.lock = Lock()
        self.listener = FakeListener(self.events)
        self.remote: Hello | None = None
        self.connection: FakeConnection | None = None
        self.error = "endpoint-unavailable"
        self.timeouts: list[float] = []

    def current_sid(self) -> str:
        """The synthetic OS user is explicit and stable."""
        return "S-1-5-21-1"

    def secure_home(self, home: Path, _sid: str) -> None:
        """Only the isolated temporary directory may be created."""
        home.mkdir(parents=True, exist_ok=True)
        self.events.append("secure")

    def try_lock(self, _home: Path, _sid: str) -> MagicMock | None:
        """A real in-process mutex permits a deterministic concurrent-starter test."""
        if not self.lock.acquire(blocking=False):
            return None
        resource = MagicMock()

        def close() -> None:
            self.events.append("lock")
            self.lock.release()

        resource.close.side_effect = close
        return resource

    def listen(self, _endpoint: str, _sid: str) -> FakeListener:
        """Return the retained first-instance fixture."""
        return self.listener

    def connect(self, _endpoint: str, sid: str, timeout: float) -> FakeConnection:
        """Discovery hint files have no influence on this actual endpoint probe."""
        self.timeouts.append(timeout)
        if self.connection is not None:
            return self.connection
        if self.remote is None:
            raise WaitError(self.error)
        return FakeConnection([Frame("hello", self.remote.payload()), Frame("result", self.remote.payload())], sid)


def authority(tmp_path: Path, transport: FakeTransport | None = None) -> Authority:
    """Bind fixtures to an isolated home and an injected default location."""
    return Authority(tmp_path / "isolated", transport or FakeTransport(), RuntimeOptions(default_home=tmp_path / "default"))


class TestRuntime:
    """Development discovery must fail before creating any default resources."""

    def test_default_guard_and_explicit_aliases(self, tmp_path: Path) -> None:
        """Omitted/default/relative homes cannot silently choose an authority."""
        default = tmp_path / "default"
        for candidate in [None, default, default / ".." / "default"]:
            with pytest.raises(WaitError, match="explicit-home-required"):
                resolve_home(candidate, default=default)
        with pytest.raises(WaitError, match="invalid-home"):
            resolve_home(type(tmp_path)("relative"), default=default)
        selected = tmp_path / "isolated"
        assert resolve_home(selected / ".." / "isolated", default=default) == selected.resolve()
        assert not default.exists()
        assert not selected.exists()

    def test_aliases_and_distinct_authorities(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Physical aliases converge while different explicit homes stay separate."""
        default = tmp_path / "default"
        chosen = tmp_path / "isolated"
        original = Path.resolve

        def resolve(path: Path) -> Path:
            if path.name == "default-alias":
                return default
            if path.name == "alias":
                return chosen
            return original(path)

        monkeypatch.setattr(Path, "resolve", resolve)
        assert resolve_home(tmp_path / "alias", default=default) == chosen
        with pytest.raises(WaitError, match="explicit-home-required"):
            resolve_home(tmp_path / "default-alias", default=default)
        first = authority(tmp_path)
        second = authority(tmp_path / "other")
        assert first.endpoint != second.endpoint
        assert runtime.endpoint_for(first.home, "different-sid") != first.endpoint

    def test_environment_and_resolution_failures(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Failed overrides and missing default identity never trigger fallback."""
        monkeypatch.delenv("LOCALAPPDATA", raising=False)
        with pytest.raises(WaitError, match="invalid-home"):
            resolve_home(tmp_path)
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "appdata"))
        assert resolve_home(tmp_path / "isolated") == tmp_path / "isolated"
        with pytest.raises(WaitError, match="invalid-home"):
            resolve_home(tmp_path, default=Path("relative"))
        with monkeypatch.context() as context:
            context.setattr(Path, "resolve", MagicMock(side_effect=OSError("inaccessible")))
            with pytest.raises(WaitError, match="invalid-home"):
                resolve_home(tmp_path)
        with pytest.raises(WaitError, match="invalid-home"):
            resolve_home(Path("\\\\remote\\share\\home"))

    @pytest.mark.timeout(5)
    def test_simultaneous_starters_select_one_store_owner(self, tmp_path: Path) -> None:
        """Two contenders can race, but only one opens the durable store."""
        transport = FakeTransport()
        candidates = [authority(tmp_path, transport), authority(tmp_path, transport)]
        gate = Barrier(2)
        store = MagicMock(return_value=FakeResource(transport.events, "store"))

        def start(candidate: Authority) -> bool:
            gate.wait(timeout=2)
            return candidate.open(store)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(start, candidate) for candidate in candidates]
            results = [future.result(timeout=3) for future in futures]
        assert results.count(True) == 1
        assert store.call_count == 1
        winner = candidates[results.index(True)]
        assert winner.open(store)
        hint = json.loads((winner.home / "discovery.json").read_text(encoding="utf-8"))
        assert hint["instance"] == winner.identity.instance
        winner.close()
        winner.close()
        assert transport.events[-3:] == ["pipe", "store", "lock"]

    def test_startup_failures_release_resources_before_lock(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Store recovery, pipe conflicts and discovery failure never publish ready."""
        for boundary in ("store", "pipe", "discovery"):
            transport = FakeTransport()
            candidate = authority(tmp_path / boundary, transport)
            store = MagicMock(return_value=FakeResource(transport.events, "store"))
            with monkeypatch.context() as context:
                if boundary == "store":
                    store.side_effect = WaitError("schema-incompatible")
                elif boundary == "pipe":
                    context.setattr(transport, "listen", MagicMock(side_effect=WaitError("endpoint-conflict")))
                else:
                    context.setattr(Path, "replace", MagicMock(side_effect=OSError("disk full")))
                with pytest.raises((WaitError, OSError)):
                    candidate.open(store)
            assert not candidate.ready
            assert not transport.lock.locked()
            assert transport.events[-1] == "lock"
            assert not list(candidate.home.glob("*.tmp"))

    @pytest.mark.timeout(5)
    def test_offline_reader_retries_then_hidden_start(self, tmp_path: Path) -> None:
        """A temporary offline reader is allowed to finish within the readiness bound."""
        transport = FakeTransport()
        clock = [0.0]
        transport.lock.acquire()

        def delay(seconds: float) -> None:
            clock[0] += seconds
            if transport.lock.locked():
                transport.lock.release()

        candidate = authority(tmp_path, transport)
        candidate.options = replace(candidate.options, monotonic=lambda: clock[0], delay=delay)
        launches: list[float] = []

        def launch() -> int:
            launches.append(clock[0])
            transport.remote = candidate.identity
            return 123

        result = ensure_started(candidate, launch)
        assert result.operation == "result"
        assert len(launches) == 1
        assert launches[0] > 0
        assert clock[0] < runtime.STARTUP_SECONDS

    @pytest.mark.parametrize("held", [True, False])
    def test_startup_deadline_no_duplicate_launch_or_owner_kill(self, tmp_path: Path, *, held: bool) -> None:
        """An unavailable owner times out at exactly 15 injected seconds."""
        transport = FakeTransport()
        if held:
            transport.lock.acquire()
        candidate = authority(tmp_path, transport)
        clock = [0.0]

        def delay(seconds: float) -> None:
            clock[0] += seconds

        candidate.options = replace(candidate.options, monotonic=lambda: clock[0], delay=delay)
        launch = MagicMock(return_value=123)
        with pytest.raises(WaitError, match="startup-timeout"):
            ensure_started(candidate, launch)
        assert clock[0] == runtime.STARTUP_SECONDS
        assert launch.call_count == (0 if held else 1)
        assert transport.lock.locked() is held
        assert max(transport.timeouts) <= 1

    def test_stale_discovery_is_not_ownership_or_authentication(self, tmp_path: Path) -> None:
        """A stale arbitrary hint cannot replace the live endpoint's identity."""
        transport = FakeTransport()
        candidate = authority(tmp_path, transport)
        candidate.home.mkdir()
        (candidate.home / "discovery.json").write_text('{"pid":1,"endpoint":"evil"}', encoding="utf-8")
        transport.remote = candidate.identity
        launch = MagicMock()
        assert ensure_started(candidate, launch).operation == "result"
        launch.assert_not_called()
        transport.remote = replace(candidate.identity, major=2)
        with pytest.raises(WaitError, match="protocol-incompatible"):
            ensure_started(candidate, launch)
        transport.remote = None
        transport.error = "peer-refused"
        with pytest.raises(WaitError, match="peer-refused"):
            ensure_started(candidate, launch)

    @pytest.mark.parametrize("reply", [Frame("error", {"code": "protocol-incompatible"}), Frame("result", {})])
    def test_client_refusal_before_application_frame(self, tmp_path: Path, reply: Frame) -> None:
        """Invalid negotiation never transmits the requested mutation."""
        transport = FakeTransport()
        candidate = authority(tmp_path, transport)
        connection = FakeConnection([reply], candidate.sid)
        transport.connection = connection
        with pytest.raises(WaitError):
            request(candidate, Frame("stop", {}))
        assert [frame.operation for frame in connection.writes] == (["hello", "ack"] if reply.operation == "error" else ["hello"])
        assert connection.closed

    def test_client_rejects_foreign_and_missing_required_feature(self, tmp_path: Path) -> None:
        """Foreign peers get no bytes; missing server features get no application frame."""
        transport = FakeTransport()
        candidate = authority(tmp_path, transport)
        connection = FakeConnection([], "foreign")
        transport.connection = connection
        with pytest.raises(WaitError, match="peer-refused"):
            request(candidate, Frame("stop", {}))
        assert connection.writes == []
        transport.connection = None
        transport.remote = replace(candidate.identity, features=())
        with pytest.raises(WaitError, match="unsupported-feature"):
            request(candidate, Frame("stop", {}, ("stop",)))

    def test_invalid_application_reply_and_status_refusal(self, tmp_path: Path) -> None:
        """Transport acknowledgement precedes typed rejection of invalid replies."""
        transport = FakeTransport()
        candidate = authority(tmp_path, transport)
        for reply, code in [(Frame("hello", {}), "invalid-frame"), (Frame("error", {"code": "busy"}), "service-unavailable")]:
            connection = FakeConnection([Frame("hello", candidate.identity.payload()), reply], candidate.sid)
            transport.connection = connection
            with pytest.raises(WaitError, match=code):
                ensure_started(candidate, MagicMock())
            assert connection.writes[-1] == Frame("ack", {})

    def test_probe_consuming_deadline_does_not_sleep_past_it(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Retry delay is omitted when the last bounded probe exhausted the budget."""
        candidate = authority(tmp_path)
        clock = [0.0]
        delay = MagicMock()
        candidate.options = replace(candidate.options, monotonic=lambda: clock[0], delay=delay)
        failure = WaitError("ipc-timeout")

        def probe(*_args: object, **_kwargs: object) -> Frame:
            clock[0] = runtime.STARTUP_SECONDS
            raise failure

        monkeypatch.setattr(runtime, "request", probe)
        launch = MagicMock(return_value=123)
        with pytest.raises(WaitError, match="startup-timeout"):
            ensure_started(candidate, launch)
        delay.assert_not_called()
        launch.assert_not_called()

    def test_server_dispatch_and_orderly_stop(self, tmp_path: Path) -> None:
        """A compatible hello precedes the single request and resource release."""
        transport = FakeTransport()
        candidate = authority(tmp_path, transport)
        with pytest.raises(WaitError, match="service-unavailable"):
            candidate.serve_once(candidate.lifecycle)
        assert candidate.open(lambda _path: FakeResource(transport.events, "store"))
        connection = FakeConnection([Frame("hello", candidate.identity.payload()), Frame("stop", {}), Frame("ack", {})], candidate.sid)
        transport.listener.connection = connection
        candidate.serve_once(candidate.lifecycle)
        assert candidate.stopping
        assert [frame.operation for frame in connection.writes] == ["hello", "result"]
        assert connection.closed
        assert connection.stream.read() == b""
        candidate.close()

    def test_server_invalid_frame_never_reaches_handler(self, tmp_path: Path) -> None:
        """A typed negotiation error is returned and no useful work occurs."""
        transport = FakeTransport()
        candidate = authority(tmp_path, transport)
        candidate.open(lambda _path: FakeResource(transport.events, "store"))
        connection = FakeConnection([Frame("stop", {}), Frame("status", {})], candidate.sid)
        transport.listener.connection = connection
        handler = MagicMock()
        candidate.serve_once(handler)
        assert connection.writes == [Frame("error", {"code": "hello-required"})]
        handler.assert_not_called()
        assert candidate.lifecycle(Frame("status", {})).payload["status"] == "ready"
        with pytest.raises(WaitError, match="invalid-frame"):
            candidate.lifecycle(Frame("status", {"unexpected": True}))
        with pytest.raises(WaitError, match="unsupported-feature"):
            candidate.lifecycle(Frame("register", {}))
        candidate.close()

    def test_run_loop_closes_on_loss_stop_and_fatal_error(self) -> None:
        """A losing starter exits; transient idle/peer errors cannot kill the owner."""
        candidate = MagicMock()
        candidate.open.return_value = False
        run_authority(candidate, MagicMock())
        candidate.serve_once.assert_not_called()
        candidate.close.assert_called_once()
        candidate.reset_mock()
        candidate.open.return_value = True
        candidate.stopping = False
        errors = iter([WaitError("ipc-timeout"), WaitError("peer-refused"), None])

        def serve(_handler: object) -> None:
            error = next(errors)
            if error:
                raise error
            candidate.stopping = True

        candidate.serve_once.side_effect = serve
        run_authority(candidate, MagicMock())
        assert candidate.serve_once.call_count == 3
        candidate.stopping = False
        candidate.serve_once.side_effect = WaitError("unexpected")
        with pytest.raises(WaitError, match="unexpected"):
            run_authority(candidate, MagicMock())

    def test_entrypoint_uses_exact_interpreter_root_and_home(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Internal startup resolves an absolute invocation and supports hidden serving."""
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "appdata"))
        ipc = MagicMock(return_value=FakeTransport())
        monkeypatch.setattr("tools.wait_service.windows_ipc.WindowsIPC", ipc)
        run = MagicMock()
        monkeypatch.setattr(runtime, "run_authority", run)
        assert runtime.main(["--home", str(tmp_path / "isolated"), "--serve"]) == 0
        run.assert_called_once()
        launch = MagicMock(return_value=123)
        monkeypatch.setattr("tools.wait_service.windows_ipc.launch_hidden", launch)

        def start(_authority: Authority, callback: Callable[[], int]) -> Frame:
            callback()
            return Frame("result", {})

        monkeypatch.setattr(runtime, "ensure_started", start)
        assert runtime.main(["--home", str(tmp_path / "isolated")]) == 0
        assert launch.call_args.args[0][0] == sys.executable
        assert launch.call_args.args[0][-1] == "--serve"
        ipc.reset_mock()
        assert runtime.main([]) == 2
        ipc.assert_not_called()

    def test_module_main_guard_without_default_home_effects(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The actual module entrypoint rejects omitted home before native setup."""
        monkeypatch.delitem(sys.modules, "tools.wait_service.runtime")
        monkeypatch.setattr(sys, "argv", ["runtime"])
        with pytest.raises(SystemExit) as error:
            runpy.run_module("tools.wait_service.runtime", run_name="__main__")
        assert error.value.code == 2


# eof
