"""Speak WebSocket JSON-RPC through Codex's raw Unix-socket proxy.

The proxy is a byte tunnel, not the app-server stdio JSONL transport. wsproto
owns HTTP Upgrade, masking and frame parsing. Reads have absolute deadlines
and a total byte budget; only this connection's child proxy is terminated.
"""

from __future__ import annotations

import json
import subprocess
import time
from collections import deque
from contextlib import contextmanager
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, cast

from wsproto import ConnectionType, WSConnection
from wsproto.events import AcceptConnection, Ping, Request, TextMessage
from wsproto.utilities import ProtocolError

from .models import JsonObject, object_value, reject

if TYPE_CHECKING:
    from collections.abc import Generator
    from io import BufferedReader
    from typing import IO

    from wsproto.events import Event

MAX_BYTES = 1_048_576
RESPONSE_SECONDS = 10
type PipeItem = bytes | OSError | ValueError


def read_pipe(stream: BufferedReader, output: Queue[PipeItem]) -> None:
    """Forward available bytes, errors and EOF without unbounded buffering."""
    total = 0
    try:
        while data := stream.read1(65_536):
            total += len(data)
            if total > MAX_BYTES:
                reject("Codex proxy byte budget exceeded")
            output.put(data)
    except (OSError, ValueError) as error:
        output.put(error)
    else:
        output.put(b"")


class CodexProxy:
    """Perform bounded WebSocket exchanges instead of sending JSONL to the tunnel."""

    def __init__(self, stream: IO[bytes], output: Queue[PipeItem]) -> None:
        """Bind one binary writer and the bounded pipe reader's output."""
        self.stream, self.output = stream, output
        self.connection = WSConnection(ConnectionType.CLIENT)
        self.events: deque[Event] = deque()
        self.request_id = 0

    def _send(self, event: Event) -> None:
        self.stream.write(self.connection.send(event))
        self.stream.flush()

    def _event(self, deadline: float) -> Event:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                reject("Codex proxy response deadline exceeded")
            if self.events:
                return self.events.popleft()
            data = self.output.get(timeout=remaining)
            if isinstance(data, Exception):
                raise data
            if not data:
                reject("Codex proxy closed before response")
            self.connection.receive_data(data)
            self.events.extend(self.connection.events())

    def initialize(self) -> None:
        """Complete HTTP Upgrade before sending the app-server initialization."""
        self._send(Request(host="localhost", target="/"))
        if not isinstance(self._event(time.monotonic() + RESPONSE_SECONDS), AcceptConnection):
            reject("Codex proxy WebSocket upgrade rejected")
        self.request("initialize", {"clientInfo": {"name": "wait-prototype", "version": "0.13.0"}})
        self._send(TextMessage(data=json.dumps({"method": "initialized"})))

    def request(self, method: str, params: JsonObject) -> JsonObject:
        """Send one RPC; notifications and fragments cannot reset its deadline."""
        self.request_id += 1
        self._send(TextMessage(data=json.dumps({"id": self.request_id, "method": method, "params": params})))
        deadline = time.monotonic() + RESPONSE_SECONDS
        while True:
            row = self._message(deadline)
            if row.get("id") == self.request_id:
                if "error" in row:
                    reject("Codex proxy RPC error")
                return object_value(row.get("result"))

    def _message(self, deadline: float) -> JsonObject:
        parts: list[str] = []
        while True:
            event = self._event(deadline)
            if isinstance(event, Ping):
                self._send(event.response())
            elif isinstance(event, TextMessage):
                parts.append(event.data)
                if event.message_finished:
                    return object_value(json.loads("".join(parts)))
            else:
                reject("Codex proxy closed or sent an unexpected WebSocket event")


@contextmanager
def connect(argv: list[str], environment: dict[str, str]) -> Generator[CodexProxy]:
    """Attach to an existing backend without starting or resuming a conversation."""
    with subprocess.Popen(  # noqa: S603 - Explicit inspected executable; never a shell.
            argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env=environment) as process:
        assert process.stdout is not None  # noqa: S101 - PIPE contract.
        assert process.stdin is not None  # noqa: S101 - PIPE contract.
        output: Queue[PipeItem] = Queue()
        reader = Thread(target=read_pipe, args=(cast("BufferedReader", process.stdout), output), daemon=True)
        reader.start()
        try:
            client = CodexProxy(process.stdin, output)
            client.initialize()
            yield client
        except ProtocolError:
            reject("Codex proxy WebSocket protocol error")
        finally:
            process.terminate()
            process.wait(timeout=10)
            reader.join(timeout=10)


# eof
