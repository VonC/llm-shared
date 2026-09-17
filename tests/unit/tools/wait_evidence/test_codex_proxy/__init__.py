"""Provide an in-memory WebSocket peer for the raw Codex proxy regression."""

from __future__ import annotations

import json
from queue import Queue
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from wsproto import ConnectionType, WSConnection
from wsproto.events import AcceptConnection, Event, Request, TextMessage

from tools.wait_evidence.models import JsonObject, object_value

if TYPE_CHECKING:
    from tools.wait_evidence.codex_proxy import PipeItem


class ProxyPeer:
    """Require HTTP Upgrade and masked WebSocket requests, as the real socket does."""

    def __init__(self, result: JsonObject) -> None:
        """Answer metadata requests only; never access a real host."""
        self.result = result
        self.connection = WSConnection(ConnectionType.SERVER)
        self.output: Queue[PipeItem] = Queue()
        self.requests: list[JsonObject] = []
        self.controls: list[Event] = []
        self.process = MagicMock()
        self.process.__enter__.return_value = self.process
        self.process.stdin.write.side_effect = self.write
        self.process.stdout.read1.side_effect = self.read
        self.process.terminate.side_effect = lambda: self.output.put(b"")

    def read(self, _size: int) -> bytes:
        """Wake the transport reader when the fake peer emits wire bytes."""
        data = self.output.get(timeout=1)
        if isinstance(data, Exception):
            raise data
        return data

    def write(self, data: bytes) -> int:
        """Decode actual wire bytes, rejecting the old plain-JSONL transport."""
        assert isinstance(data, bytes), "The Unix proxy requires binary WebSocket transport"
        self.connection.receive_data(data)
        for event in self.connection.events():
            if isinstance(event, Request):
                self.output.put(self.connection.send(AcceptConnection()))
            elif isinstance(event, TextMessage):
                row = object_value(json.loads(event.data))
                self.requests.append(row)
                if "id" in row:
                    result = {} if row["method"] == "initialize" else self.result
                    self.output.put(self.connection.send(TextMessage(data=json.dumps({"id": row["id"],
                                                                                      "result": result}))))
            else:
                self.controls.append(event)
        return len(data)


# eof
