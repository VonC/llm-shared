"""Canonical authority identity, singleton lifetime and bounded hidden startup.

Lifecycle policy depends on narrow resource ports. The executable composition
is deliberately limited to readiness/status and orderly stop until Step 7.
Development requires an explicit nondefault home before any discovery or I/O.
"""

# ruff: noqa: EM101 - Public typed errors, not free-form exception messages.

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast
from uuid import uuid4

from tools.wait_service.models import WaitError
from tools.wait_service.protocol import Frame, Hello, Session, encode_frame, read_frame

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager

STARTUP_SECONDS = 15.0
RETRY_SECONDS = 0.05


class Resource(Protocol):
    """An owned handle or recovered store with an explicit lifetime."""

    def close(self) -> None:
        """Release once when startup fails or shutdown completes."""
        ...


class Connection(Resource, Protocol):
    """Transport must authenticate before exposing any frame I/O."""

    @property
    def verified_sid(self) -> str:
        """Return OS-verified peer provenance."""
        ...

    def read(self, count: int) -> bytes:
        """Read within the connection's finite deadline."""
        ...

    def write(self, data: bytes) -> None:
        """Write within the connection's finite deadline."""
        ...


class Listener(Resource, Protocol):
    """Retain the first pipe instance while accepting authenticated connections."""

    def accept(self, timeout: float, /) -> AbstractContextManager[Connection]:
        """Yield one verified peer, then disconnect without dropping ownership."""
        ...


class Transport(Protocol):
    """Platform resource operations kept outside lifecycle policy."""

    def current_sid(self) -> str:
        """Resolve the current OS token user."""
        ...

    def secure_home(self, home: Path, sid: str, /) -> None:
        """Prepare local, user-private state before the store opens."""
        ...

    def try_lock(self, home: Path, sid: str, /) -> Resource | None:
        """Acquire the OS singleton nonblocking, or report an existing owner."""
        ...

    def listen(self, endpoint: str, sid: str, /) -> Listener:
        """Reserve the authenticated first pipe instance."""
        ...

    def connect(self, endpoint: str, sid: str, timeout: float, /) -> Connection:
        """Verify the server OS user before returning a connection."""
        ...


def resolve_home(home: Path | None, *, default: Path | None = None) -> Path:
    """Canonicalize physical aliases without cwd fallback or resource creation."""
    if home is None:
        raise WaitError("explicit-home-required", "development requires an isolated state home")
    if default is None:
        appdata = os.environ.get("LOCALAPPDATA", "")
        if not appdata or not Path(appdata).is_absolute():
            raise WaitError("invalid-home", "LOCALAPPDATA must identify the default home")
        default = Path(appdata) / "llm-shared" / "wait-service"
    if not home.is_absolute() or not default.is_absolute():
        raise WaitError("invalid-home", "absolute local homes required")
    try:
        resolved = Path(os.path.normcase(str(home.resolve())))
        default_resolved = Path(os.path.normcase(str(default.resolve())))
    except (OSError, RuntimeError) as error:
        raise WaitError("invalid-home", "physical home resolution failed") from error
    # Temporary Q07 rollout guard. Step 8 removes this check only after its
    # isolated live acceptance and explicit compatibility/rollout record.
    if resolved == default_resolved:
        raise WaitError("explicit-home-required", "default-home aliases are disabled before rollout")
    if str(resolved).startswith("\\\\"):
        raise WaitError("invalid-home", "network homes are unsupported")
    return resolved


def endpoint_for(home: Path, sid: str) -> str:
    """Derive a local endpoint solely from verified SID and canonical home."""
    digest = hashlib.sha256(f"{sid}\0{home}".encode()).hexdigest()
    return "\\\\.\\pipe\\llm-shared-wait-" + digest


@dataclass(frozen=True)
class RuntimeOptions:
    """Explicit build/port/schema identity, injectable clocks and development home."""

    build: str = "v0.13.0-core"
    ports: tuple[str, ...] = ("synthetic",)
    features: tuple[str, ...] = ("status", "stop")
    schema: int = 1
    default_home: Path | None = None
    monotonic: Callable[[], float] = time.monotonic
    delay: Callable[[float], None] = time.sleep


class Authority:
    """Own the singleton through recovery, readiness, serving and orderly cleanup."""

    def __init__(self, home: Path | None, transport: Transport, options: RuntimeOptions | None = None) -> None:
        """Refuse unsafe homes before reading discovery or requesting OS resources."""
        options = options or RuntimeOptions()
        self.home = resolve_home(home, default=options.default_home)
        self.transport, self.options = transport, options
        self.sid = transport.current_sid()
        self.endpoint = endpoint_for(self.home, self.sid)
        self.identity = Hello(1, 0, options.build, options.ports, options.features, str(uuid4()), str(self.home), self.sid, options.schema, "ready")
        self._resources = contextlib.ExitStack()
        self.listener: Listener | None = None
        self.ready = False
        self.stopping = False

    def open(self, store_factory: Callable[[Path], Resource]) -> bool:
        """Recover the store and enforce IPC before atomically publishing readiness."""
        if self.ready:
            return True
        self.transport.secure_home(self.home, self.sid)
        lock = self.transport.try_lock(self.home, self.sid)
        if lock is None:
            return False
        self._resources.callback(lock.close)
        try:
            store = store_factory(self.home / "store.sqlite3")
            self._resources.callback(store.close)
            self.listener = self.transport.listen(self.endpoint, self.sid)
            self._resources.callback(self.listener.close)
            self._publish()
            self.ready = True
        except BaseException:
            self.close()
            raise
        return True

    def _publish(self) -> None:
        # Hints are never read for authentication or ownership. Unique temporary
        # files plus replace make discovery atomic while the singleton is held.
        hint = self.identity.payload() | {"endpoint": self.endpoint}
        temporary = self.home / f"discovery.{self.identity.instance}.tmp"
        try:
            temporary.write_text(json.dumps(hint), encoding="utf-8")
            temporary.replace(self.home / "discovery.json")
        except OSError as error:
            raise WaitError("storage-unavailable", "cannot publish discovery") from error
        finally:
            temporary.unlink(missing_ok=True)

    def serve_once(self, handler: Callable[[Frame], Frame], timeout: float = 1.0) -> None:
        """Serve one finite negotiated request; malformed peers cannot call handlers."""
        if not self.ready or self.listener is None:
            raise WaitError("service-unavailable", "authority not ready")
        with self.listener.accept(timeout) as connection:
            session = Session(self.identity, connection.verified_sid)
            try:
                connection.write(encode_frame(session.dispatch(read_frame(connection.read), handler)))
                connection.write(encode_frame(session.dispatch(read_frame(connection.read), handler)))
            except WaitError as error:
                connection.write(encode_frame(Frame("error", {"code": error.code})))
            # DisconnectNamedPipe discards unread output. A transport-only ack
            # confirms the reply was read, within the existing I/O deadline;
            # it never acknowledges a delivery or changes durable state.
            with contextlib.suppress(WaitError):
                if read_frame(connection.read) != Frame("ack", {}):
                    raise WaitError("invalid-frame", "reply acknowledgement required")

    def lifecycle(self, frame: Frame) -> Frame:
        """Expose only core readiness and explicit orderly stop until composition grows."""
        if frame.payload:
            raise WaitError("invalid-frame", "core lifecycle takes no fields")
        if frame.operation == "status":
            return Frame("result", self.identity.payload())
        if frame.operation == "stop":
            self.stopping = True
            return Frame("result", {"status": "stopping"})
        raise WaitError("unsupported-feature", "operation requires later service composition")

    def close(self) -> None:
        """Release pipe/store before singleton; stale discovery remains only a hint."""
        self.ready = False
        self.listener = None
        self._resources.close()


def request(authority: Authority, frame: Frame, timeout: float = 1.0) -> Frame:
    """Perform reciprocal hello checks before sending an application request."""
    with contextlib.closing(authority.transport.connect(authority.endpoint, authority.sid, timeout)) as connection:
        if connection.verified_sid != authority.sid:
            raise WaitError("peer-refused", "foreign server")
        connection.write(encode_frame(Frame("hello", authority.identity.payload(), frame.required_features)))
        response = read_frame(connection.read)
        if response.operation == "error":
            connection.write(encode_frame(Frame("ack", {})))
            raise WaitError(str(response.payload.get("code", "invalid-frame")), "hello refused")
        if response.operation != "hello":
            raise WaitError("invalid-hello", "server did not answer hello")
        peer = Hello.parse(response.payload)
        authority.identity.compatible(peer)
        peer.compatible(authority.identity, frame.required_features)
        connection.write(encode_frame(frame))
        response = read_frame(connection.read)
        connection.write(encode_frame(Frame("ack", {})))
        if response.operation not in {"result", "error"}:
            raise WaitError("invalid-frame", "application response required")
        return response


def ensure_started(authority: Authority, launch: Callable[[], int]) -> Frame:
    """Retry an offline-reader lock within 15 seconds; never kill an existing owner."""
    deadline = authority.options.monotonic() + STARTUP_SECONDS
    launched = False
    authority.transport.secure_home(authority.home, authority.sid)
    while (remaining := deadline - authority.options.monotonic()) > 0:
        try:
            result = request(authority, Frame("status", {}), timeout=min(1.0, remaining))
        except WaitError as error:
            if error.code not in {"endpoint-unavailable", "ipc-timeout", "ipc-unavailable"}:
                raise
        else:
            if result.operation != "result":
                raise WaitError("service-unavailable", "authority status refused")
            return result
        if authority.options.monotonic() >= deadline:
            break
        if not launched:
            lock = authority.transport.try_lock(authority.home, authority.sid)
            if lock is not None:
                lock.close()
                launch()
                launched = True
        remaining = deadline - authority.options.monotonic()
        if remaining > 0:
            authority.options.delay(min(RETRY_SECONDS, remaining))
    raise WaitError("startup-timeout", "no ready authority within 15 seconds")


def run_authority(authority: Authority, store_factory: Callable[[Path], Resource]) -> None:
    """A losing starter exits; the winner holds resources until explicit stop."""
    try:
        if not authority.open(store_factory):
            return
        while not authority.stopping:
            try:
                authority.serve_once(authority.lifecycle)
            except WaitError as error:
                if error.code not in {"ipc-timeout", "ipc-unavailable", "peer-refused"}:
                    raise
    finally:
        authority.close()


def main(argv: list[str] | None = None) -> int:
    """Internal absolute-interpreter entry point; the user CLI belongs to Step 7."""
    from tools.wait_service.store import (  # noqa: PLC0415 - Entrypoint composition is lazy.
        WaitStore,
    )
    from tools.wait_service.windows_ipc import (  # noqa: PLC0415
        WindowsIPC,
        launch_hidden,
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path)
    parser.add_argument("--serve", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        home = resolve_home(cast("Path | None", arguments.home))
        authority = Authority(home, WindowsIPC())
        if arguments.serve:
            run_authority(authority, WaitStore)
        else:
            root = Path(__file__).resolve().parents[2]
            command = [sys.executable, "-m", "tools.wait_service.runtime", "--home", str(home), "--serve"]
            ensure_started(authority, lambda: launch_hidden(command, root))
    except WaitError as error:
        sys.stderr.write(error.code + "\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
