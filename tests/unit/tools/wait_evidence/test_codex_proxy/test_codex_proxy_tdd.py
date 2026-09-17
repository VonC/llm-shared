"""Exercise real WebSocket framing and bounded failures without host processes."""

# ruff: noqa: PLR2004 - Explicit wire sizes and fake deadlines.

from __future__ import annotations

import io
import json
from queue import Empty, Queue
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from wsproto.events import BytesMessage, CloseConnection, Ping, Pong, TextMessage
from wsproto.utilities import ProtocolError

from tests.unit.tools.wait_evidence.test_codex_proxy import ProxyPeer
from tools.wait_evidence.codex_proxy import CodexProxy, PipeItem, connect, read_pipe

if TYPE_CHECKING:
    from wsproto.events import Event

pytestmark = pytest.mark.timeout(10)


def connected() -> tuple[CodexProxy, ProxyPeer]:
    """Complete the real HTTP Upgrade against an in-memory server."""
    peer = ProxyPeer({})
    # Transfer responses synchronously: only connect() needs a pipe reader.
    client = CodexProxy(peer.process.stdin, peer.output)
    client.initialize()
    return client, peer


class TestWebSocketExchange:
    """Cover fragmentation, control frames and failures hidden by JSONL fakes."""

    def test_fragmented_unicode_response_and_ping(self) -> None:
        """Byte and message fragmentation preserve Unicode while answering ping."""
        client, peer = connected()
        wire = peer.connection.send(TextMessage(data='{"result": "caf', message_finished=False))
        wire += peer.connection.send(Ping(payload=b"alive"))
        wire += peer.connection.send(TextMessage(data='é"}'))
        for value in wire:
            peer.output.put(bytes([value]))
        assert client._message(float("inf")) == {"result": "café"}
        assert peer.controls == [Pong(payload=b"alive")]

    def test_unrelated_messages_do_not_replace_rpc_result(self) -> None:
        """Notifications and another request's result cannot satisfy this request."""
        client, peer = connected()
        for row in ({"method": "notification"}, {"id": -1, "result": {"wrong": True}}):
            peer.output.put(peer.connection.send(TextMessage(data=json.dumps(row))))
        assert client.request("thread/loaded/list", {}) == {}

    @pytest.mark.parametrize("payload", ['{"id":2,"error":{"message":"unavailable"}}',
                                        '{"id":2,"result":null}', "[]", "invalid"])
    def test_rpc_errors_and_malformed_results_fail(self, payload: str) -> None:
        """An RPC failure or invalid JSON object never looks like metadata."""
        client, peer = connected()
        peer.output.put(peer.connection.send(TextMessage(data=payload)))
        with pytest.raises(ValueError, match=r"RPC error|JSON object|Expecting value"):
            client.request("thread/read", {})

    @pytest.mark.parametrize("event", [CloseConnection(code=1000), BytesMessage(data=b"binary"), Pong(payload=b"unsolicited")])
    def test_closure_and_unexpected_events_fail(self, event: Event) -> None:
        """Only expected text messages and server pings enter the RPC channel."""
        client, peer = connected()
        peer.output.put(peer.connection.send(event))
        with pytest.raises(ValueError, match="closed or sent an unexpected"):
            client._message(float("inf"))

    @pytest.mark.parametrize("wire", [b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n",
                                     b"HTTP/1.1 101 Switching Protocols\r\n\r\n"])
    def test_rejected_or_invalid_upgrade_fails(self, wire: bytes) -> None:
        """A rejection and invalid acceptance cannot precede JSON-RPC traffic."""
        output: Queue[PipeItem] = Queue()
        output.put(wire)
        client = CodexProxy(io.BytesIO(), output)
        with pytest.raises((ValueError, ProtocolError)):
            client.initialize()

    def test_noisy_peer_cannot_extend_absolute_deadline(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Buffered notifications still consume the same finite response window."""
        client, peer = connected()
        peer.output.put(peer.connection.send(TextMessage(data='{"method":"notification"}')))
        monkeypatch.setattr("tools.wait_evidence.codex_proxy.time.monotonic", Mock(side_effect=[0.0, 1.0, 2.0, 11.0]))
        with pytest.raises(ValueError, match="deadline"):
            client.request("thread/read", {})


class TestPipeBounds:
    """Bound buffered wire bytes and surface EOF, read errors and timeouts."""

    def test_reader_forwards_bytes_and_eof(self) -> None:
        """The reader consumes available bytes without waiting for a full buffer."""
        output: Queue[PipeItem] = Queue()
        read_pipe(io.BufferedReader(io.BytesIO(b"wire bytes")), output)
        assert [output.get_nowait(), output.get_nowait()] == [b"wire bytes", b""]

    def test_reader_rejects_oversized_input(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The total byte cap bounds notifications and incomplete frames alike."""
        monkeypatch.setattr("tools.wait_evidence.codex_proxy.MAX_BYTES", 4)
        output: Queue[PipeItem] = Queue()
        read_pipe(io.BufferedReader(io.BytesIO(b"oversized")), output)
        assert isinstance(output.get_nowait(), ValueError)
        assert output.empty()

    def test_reader_preserves_os_failure(self) -> None:
        """A broken pipe wakes the RPC caller with the original exception."""
        failure = OSError("pipe failed")
        output: Queue[PipeItem] = Queue()
        read_pipe(Mock(read1=Mock(side_effect=failure)), output)
        client = CodexProxy(io.BytesIO(), output)
        with pytest.raises(OSError, match="pipe failed"):
            client._event(float("inf"))

    def test_eof_and_missing_response_fail_promptly(self) -> None:
        """Closure and queue timeout cannot be mistaken for an idle thread."""
        output: Queue[PipeItem] = Queue()
        output.put(b"")
        client = CodexProxy(io.BytesIO(), output)
        with pytest.raises(ValueError, match="closed"):
            client._event(float("inf"))
        client.output = Mock(get=Mock(side_effect=Empty))
        with pytest.raises(Empty):
            client._event(float("inf"))

    @pytest.mark.parametrize("rejected", ["", "forbidden", "malformed"])
    def test_owned_proxy_exits_after_success_or_failed_upgrade(self, monkeypatch: pytest.MonkeyPatch,
                                                              rejected: str) -> None:
        """Close the owned binary tunnel on both acceptance and handshake failure."""
        peer = ProxyPeer({"data": []})
        spawn = Mock(return_value=peer.process)
        monkeypatch.setattr("tools.wait_evidence.codex_proxy.subprocess.Popen", spawn)
        if rejected:
            peer.output.put(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n" if rejected == "forbidden"
                            else b"HTTP/1.1 101 Switching Protocols\r\n\r\n")
            with pytest.raises(ValueError, match="Codex proxy WebSocket"), connect(["exact-proxy"], {}):
                pytest.fail("Rejected upgrade must not expose an initialized client")
        else:
            with connect(["exact-proxy"], {}) as client:
                assert client.request("thread/loaded/list", {}) == {"data": []}
        assert "text" not in spawn.call_args.kwargs
        peer.process.terminate.assert_called_once()
        peer.process.wait.assert_called_once_with(timeout=10)


# eof
