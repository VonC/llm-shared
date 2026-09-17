"""Reject untrusted frames and gate dispatch on a compatible hello."""

from __future__ import annotations

import json
import struct
from dataclasses import replace
from uuid import uuid4

import pytest

from tools.wait_service.models import WaitError
from tools.wait_service.protocol import (
    MAX_FRAME,
    Frame,
    Hello,
    Session,
    decode_frame,
    encode_frame,
    read_frame,
)


def hello() -> Hello:
    """An explicit synthetic authority independent of the user's home."""
    return Hello(1, 0, "test-build", ("synthetic",), ("status",), str(uuid4()), "C:/isolated", "S-1-5-21-1", 1, "ready")


class TestProtocol:
    """Bound wire bytes, reject malformed shapes, and negotiate before dispatch."""

    @pytest.mark.parametrize("size", [0, 1, 8191, 8192])
    def test_inline_utf8_boundary(self, size: int) -> None:
        """The limit counts encoded data bytes, including multibyte text."""
        frame = Frame("result", {"inline_result": "x" * size})
        assert decode_frame(encode_frame(frame)) == frame
        with pytest.raises(WaitError, match="inline-result-too-large"):
            encode_frame(Frame("result", {"inline_result": "é" * 4097}))

    @pytest.mark.parametrize("offset", [-1, 0, 1])
    def test_frame_limit_before_body_read(self, offset: int) -> None:
        """A declared oversize is rejected without reading the body."""
        base = encode_frame(Frame("result", {"data": ""}))
        frame = Frame("result", {"data": "x" * (MAX_FRAME - len(base) + 4 + offset)})
        if offset > 0:
            with pytest.raises(WaitError, match="frame-too-large"):
                encode_frame(frame)
        else:
            assert len(encode_frame(frame)) == MAX_FRAME + 4 + offset
        reads: list[int] = []

        def read(count: int) -> bytes:
            reads.append(count)
            return struct.pack("!I", MAX_FRAME + 1)

        with pytest.raises(WaitError, match="frame-too-large"):
            read_frame(read)
        assert reads == [4]

    @pytest.mark.parametrize("body", [b"", b"[1]", b"{", b"\xff", b'{"operation":"status","payload":[],"required_features":[]}', b'{"operation":"mystery","payload":{},"required_features":[]}', b'{"operation":"status","payload":{},"required_features":[],"extra":0}', b'{"operation":"status","payload":{"x":NaN},"required_features":[]}', b'{"operation":"status","operation":"stop","payload":{},"required_features":[]}'])
    def test_invalid_json_and_fields(self, body: bytes) -> None:
        """No executable decoding, ambiguous keys, NaN or unknown envelope fields."""
        with pytest.raises(WaitError):
            decode_frame(struct.pack("!I", len(body)) + body)

    @pytest.mark.parametrize("raw", [b"", b"\x00", struct.pack("!I", 9) + b"{}", encode_frame(Frame("status", {})) + b"extra"])
    def test_truncation_and_trailing_data(self, raw: bytes) -> None:
        """Exactly one bounded frame must be present."""
        with pytest.raises(WaitError, match="invalid-frame"):
            decode_frame(raw)

    def test_fragmented_stream_and_eof(self) -> None:
        """Chunked reads use bounded accumulation and terminate on EOF."""
        frame = Frame("status", {})
        chunks = iter(bytes([value]) for value in encode_frame(frame))
        assert read_frame(lambda _count: next(chunks, b"")) == frame
        with pytest.raises(WaitError, match="invalid-frame"):
            read_frame(lambda _count: b"")

    @pytest.mark.parametrize("payload", [{"inline_result": 1}, {"inline_result": "\ud800"}, {"data": object()}, {"data": float("nan")}])
    def test_unserializable_payload_is_typed(self, payload: dict[str, object]) -> None:
        """Malformed text, nonfinite numbers and non-JSON values cannot escape raw."""
        with pytest.raises(WaitError, match="invalid-frame"):
            encode_frame(Frame("result", payload))

    def test_oversized_header_and_feature_list(self) -> None:
        """Direct decoding and trusted callers obey the same bounded contract."""
        with pytest.raises(WaitError, match="frame-too-large"):
            decode_frame(struct.pack("!I", MAX_FRAME + 1))
        with pytest.raises(WaitError, match="invalid-frame"):
            encode_frame(Frame("status", {}, ("x",) * 33))

    def test_handshake_gates_handler(self) -> None:
        """Only a verified same-user peer with a compatible hello can dispatch."""
        identity = hello()
        calls: list[Frame] = []

        def handle(frame: Frame) -> Frame:
            calls.append(frame)
            return Frame("result", {})

        session = Session(identity, identity.sid)
        with pytest.raises(WaitError, match="hello-required"):
            session.dispatch(Frame("stop", {}), handle)
        response = session.dispatch(Frame("hello", identity.payload()), handle)
        assert response == Frame("hello", identity.payload())
        assert calls == []
        assert session.dispatch(Frame("status", {}), handle).operation == "result"
        assert calls == [Frame("status", {})]
        with pytest.raises(WaitError, match="unexpected-hello"):
            session.dispatch(Frame("hello", identity.payload()), handle)
        with pytest.raises(WaitError, match="peer-refused"):
            Session(identity, "S-1-5-21-foreign")
        for operation in ("result", "error", "ack"):
            with pytest.raises(WaitError, match="unknown-operation"):
                session.dispatch(Frame(operation, {}), handle)

    @pytest.mark.parametrize(("change", "code"), [({"major": 2}, "protocol-incompatible"), ({"schema": 2}, "schema-incompatible"), ({"home": "C:/other"}, "authority-conflict"), ({"sid": "S-1-5-21-other"}, "authority-conflict"), ({"status": "starting"}, "service-unavailable")])
    def test_incompatible_hello(self, change: dict[str, object], code: str) -> None:
        """Version or authority conflicts never call an application handler."""
        identity = hello()
        payload = identity.payload() | change
        session = Session(identity, identity.sid)
        with pytest.raises(WaitError, match=code):
            session.dispatch(Frame("hello", payload), lambda frame: pytest.fail(str(frame)))

    def test_minor_features_and_hello_validation(self) -> None:
        """Minor versions are compatible only when all required features exist."""
        identity = hello()
        identity.compatible(replace(identity, minor=99), ("status",))
        with pytest.raises(WaitError, match="unsupported-feature"):
            identity.compatible(identity, ("absent",))
        for key, value in [("major", True), ("minor", -1), ("build", ""), ("instance", "bad"), ("features", [5]), ("ports", "bad"), ("extra", 1)]:
            with pytest.raises(WaitError, match="invalid-hello"):
                Hello.parse(identity.payload() | {key: value})
        with pytest.raises(WaitError, match="invalid-hello"):
            Hello.parse({})
        assert json.loads(encode_frame(Frame("hello", identity.payload()))[4:])["operation"] == "hello"


# eof
