"""Bounded JSON framing and mutual compatibility before application dispatch.

OS authentication belongs to the transport. This module only accepts the SID
verified by that transport; claimed frame identity never substitutes for it.
"""

# ruff: noqa: EM101 - WaitError codes are the public machine-readable contract.

from __future__ import annotations

import json
import struct
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, cast
from uuid import UUID

from tools.wait_service.models import WaitError

if TYPE_CHECKING:
    from collections.abc import Callable

MAX_FRAME = 64 * 1024
MAX_INLINE = 8 * 1024
MAX_FEATURES = 32
MAX_FEATURE_NAME = 128
MAX_IDENTITY_TEXT = 2048
HEADER_SIZE = 4
OPERATIONS = frozenset({"hello", "status", "register", "cancel", "retry", "rearm", "rebind", "stop", "restart", "purge", "result", "error", "ack"})


def _strings(value: object) -> bool:
    if not isinstance(value, (list, tuple)):
        return False
    items = cast("list[object] | tuple[object, ...]", value)
    return len(items) <= MAX_FEATURES and all(isinstance(item, str) and 0 < len(item) <= MAX_FEATURE_NAME for item in items)


def _identity_fields(payload: dict[str, object]) -> None:
    for field in ("major", "minor", "schema"):
        if type(payload[field]) is not int or cast("int", payload[field]) < 0:
            raise WaitError("invalid-hello", "nonnegative version required")
    for field in ("build", "instance", "home", "sid", "status"):
        if not isinstance(payload[field], str) or not 0 < len(cast("str", payload[field])) <= MAX_IDENTITY_TEXT:
            raise WaitError("invalid-hello", "bounded identity text required")
    if not _strings(payload["ports"]) or not _strings(payload["features"]):
        raise WaitError("invalid-hello", "invalid ports or features")


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise WaitError("invalid-frame", "duplicate JSON key")
        result[key] = value
    return result


def _constant(_value: str) -> None:
    raise WaitError("invalid-frame", "nonfinite JSON number")


@dataclass(frozen=True)
class Frame:
    """One bounded envelope; operation handlers own domain payload validation."""

    operation: str
    payload: dict[str, object]
    required_features: tuple[str, ...] = ()

    def validate(self) -> None:
        """Reject unknown operations, malformed fields and oversized inline data."""
        if self.operation not in OPERATIONS:
            raise WaitError("unknown-operation", str(self.operation))
        if not _strings(self.required_features):
            raise WaitError("invalid-frame", "bounded feature list required")
        inline = self.payload.get("inline_result", "")
        if not isinstance(inline, str):
            raise WaitError("invalid-frame", "inline_result must be text")
        try:
            size = len(inline.encode("utf-8"))
        except UnicodeError as error:
            raise WaitError("invalid-frame", "inline_result must be UTF-8 text") from error
        if size > MAX_INLINE:
            raise WaitError("inline-result-too-large", "use a validated result reference")


def encode_frame(frame: Frame) -> bytes:
    """Serialize a validated frame with a network-order four-byte byte length."""
    frame.validate()
    try:
        body = json.dumps(asdict(frame), ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise WaitError("invalid-frame", "payload is not bounded UTF-8 JSON") from error
    if len(body) > MAX_FRAME:
        raise WaitError("frame-too-large", "maximum 64 KiB")
    return struct.pack("!I", len(body)) + body


def decode_frame(data: bytes) -> Frame:
    """Decode one complete frame, rejecting ambiguous and malformed JSON."""
    if len(data) < HEADER_SIZE:
        raise WaitError("invalid-frame", "truncated length")
    length = struct.unpack("!I", data[:4])[0]
    if length > MAX_FRAME:
        raise WaitError("frame-too-large", "maximum 64 KiB")
    if len(data) != length + 4:
        raise WaitError("invalid-frame", "truncated or trailing bytes")
    try:
        value: object = json.loads(data[4:].decode("utf-8"), object_pairs_hook=_object, parse_constant=_constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise WaitError("invalid-frame", "invalid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise WaitError("invalid-frame", "invalid envelope fields")
    fields = cast("dict[str, object]", value)
    if set(fields) != {"operation", "payload", "required_features"}:
        raise WaitError("invalid-frame", "invalid envelope fields")
    if not isinstance(fields["operation"], str) or not isinstance(fields["payload"], dict) or not _strings(fields["required_features"]):
        raise WaitError("invalid-frame", "invalid envelope types")
    frame = Frame(fields["operation"], cast("dict[str, object]", fields["payload"]), tuple(cast("list[str]", fields["required_features"])))
    frame.validate()
    return frame


def read_frame(read: Callable[[int], bytes]) -> Frame:
    """Read only the advertised bounded body, with linear chunk accumulation."""
    def exact(count: int) -> bytes:
        chunks: list[bytes] = []
        remaining = count
        while remaining:
            chunk = read(remaining)
            if not chunk or len(chunk) > remaining:
                raise WaitError("invalid-frame", "truncated or oversized transport read")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    header = exact(4)
    length = struct.unpack("!I", header)[0]
    if length > MAX_FRAME:
        raise WaitError("frame-too-large", "maximum 64 KiB")
    return decode_frame(header + exact(length))


@dataclass(frozen=True)
class Hello:
    """Explicit wire/build/schema/instance identity for one canonical authority."""

    major: int
    minor: int
    build: str
    ports: tuple[str, ...]
    features: tuple[str, ...]
    instance: str
    home: str
    sid: str
    schema: int
    status: str

    def payload(self) -> dict[str, object]:
        """Return plain wire fields without serializing executable objects."""
        return asdict(self)

    @classmethod
    def parse(cls, payload: dict[str, object]) -> Hello:
        """Validate all identity fields before compatibility can be trusted."""
        if set(payload) != set(cls.__dataclass_fields__):
            raise WaitError("invalid-hello", "identity fields differ")
        _identity_fields(payload)
        try:
            UUID(cast("str", payload["instance"]))
        except ValueError as error:
            raise WaitError("invalid-hello", "invalid instance UUID") from error
        return cls(cast("int", payload["major"]), cast("int", payload["minor"]), cast("str", payload["build"]), tuple(cast("list[str]", payload["ports"])), tuple(cast("list[str]", payload["features"])), cast("str", payload["instance"]), cast("str", payload["home"]), cast("str", payload["sid"]), cast("int", payload["schema"]), cast("str", payload["status"]))

    def compatible(self, peer: Hello, required: tuple[str, ...] = ()) -> None:
        """Refuse mismatched authority or schema; minor compatibility is feature based."""
        if (self.sid, self.home) != (peer.sid, peer.home):
            raise WaitError("authority-conflict", "SID or physical home differs")
        if self.major != peer.major:
            raise WaitError("protocol-incompatible", "protocol major differs")
        if self.schema != peer.schema:
            raise WaitError("schema-incompatible", "store schema differs")
        if peer.status != "ready":
            raise WaitError("service-unavailable", "peer is not ready")
        if not set(required).issubset(self.features):
            raise WaitError("unsupported-feature", "required feature unavailable")


class Session:
    """Gate each connection on OS-verified identity and one compatible hello."""

    def __init__(self, identity: Hello, verified_sid: str) -> None:
        """Never accept claimed peer identity in place of the transport's SID."""
        if verified_sid != identity.sid:
            raise WaitError("peer-refused", "foreign OS user")
        self.identity = identity
        self.ready = False

    def dispatch(self, frame: Frame, handler: Callable[[Frame], Frame]) -> Frame:
        """Handshake first, then enforce required features before every request."""
        frame.validate()
        if not self.ready:
            if frame.operation != "hello":
                raise WaitError("hello-required", "compatibility has not been established")
            self.identity.compatible(Hello.parse(frame.payload), frame.required_features)
            self.ready = True
            return Frame("hello", self.identity.payload())
        if frame.operation == "hello":
            raise WaitError("unexpected-hello", "already negotiated")
        self.identity.compatible(self.identity, frame.required_features)
        if frame.operation in {"result", "error", "ack"}:
            raise WaitError("unknown-operation", "response cannot be dispatched")
        return handler(frame)


# eof
