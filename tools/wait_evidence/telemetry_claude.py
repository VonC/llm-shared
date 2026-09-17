"""Inspected Claude 2.1.273 content blocks and native completion ancestry.

Completed response usage repeats across native content records. Count identical
usage once, preserve each tool block, and reject conflicting repeated totals.
Known sessionless history and versionless queue bookkeeping carry no request or
normal-end authority. Parent resolution is incremental and linear in records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from .models import (
    EvidenceRecord,
    JsonObject,
    identity_digest,
    object_value,
    reject,
    text_value,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from .models import TrialManifest

BOOKKEEPING = frozenset({"custom-title", "agent-name", "mode", "permission-mode", "atis-latch",
                         "last-prompt", "ai-title", "cost-state"})


@dataclass
class ClaudeTelemetry:
    """Normalize exact-session content and allow only inspected normal-end links."""

    manifest: TrialManifest
    usage: Callable[[JsonObject, str, str], JsonObject]
    turns: dict[str, str] = field(default_factory=dict[str, str])
    finals: dict[str, JsonObject] = field(default_factory=dict[str, JsonObject])
    responses: dict[str, JsonObject] = field(default_factory=dict[str, JsonObject])

    def normalize(self, raw: JsonObject, location: str, ingested_at: float) -> list[EvidenceRecord]:
        """Fan out native records without inventing unobserved request attempts."""
        kind = text_value(raw, "type")
        at = self._envelope(raw, kind, ingested_at)
        if kind in BOOKKEEPING or (kind == "file-history-snapshot" and "sessionId" not in raw):
            data: JsonObject = {"native_type": kind, "time_basis": "ingestion-only"}
            data.update({key: raw[key] for key in ("permissionMode", "mode") if key in raw})
            return [EvidenceRecord("claude:bookkeeping:" + identity_digest(location), "native_observation",
                                   at, ingested_at, location, data, synthetic=False)]
        events = self._events(raw, kind, location)
        return [EvidenceRecord("claude:" + event_id, normalized, at, ingested_at,
                               location, payload, synthetic=False) for event_id, normalized, payload in events]

    def _envelope(self, raw: JsonObject, kind: str, ingested_at: float) -> float:
        if kind == "file-history-snapshot" and "sessionId" not in raw:
            return ingested_at
        if raw.get("sessionId") != self.manifest.thread:
            reject("Native thread identity mismatch")
        if kind in BOOKKEEPING and "version" not in raw and "timestamp" not in raw:
            return ingested_at
        return self._versioned(raw, kind)

    def _versioned(self, raw: JsonObject, kind: str) -> float:
        if raw.get("version") != self.manifest.build and not (kind == "queue-operation" and "version" not in raw):
            reject("Native build identity mismatch")
        timestamp = datetime.fromisoformat(text_value(raw, "timestamp"))
        if timestamp.tzinfo is None:
            reject("Native timestamp requires an explicit timezone")
        if kind not in {"assistant", "user", "system", "attachment", "progress", "queue-operation", "file-history-snapshot"}:
            reject("Uninspected Claude record type")
        return timestamp.timestamp()

    def _events(self, raw: JsonObject, kind: str, location: str) -> list[tuple[str, str, JsonObject]]:
        identity = str(raw.get("uuid") or identity_digest(location))
        parent = str(raw.get("parentUuid") or "")
        turn = self.turns.get(parent, "")
        message = object_value(raw.get("message", {}))
        content = message.get("content", [])
        blocks = [object_value(block) for block in content] if isinstance(content, list) else []
        origin = object_value(raw.get("origin", {})).get("kind")
        if kind == "user" and origin in {"human", "task-notification"}:
            turn = identity
        self.turns[identity] = turn
        data: JsonObject = {"native_uuid": identity, "parent_uuid": parent, "turn_id": turn, "native_type": kind}
        for setting in ("permissionMode", "effortValue"):
            if setting in raw:
                data[setting] = raw[setting]
        events = self._content(raw, message, blocks, identity, data)
        if not events:
            events.append((identity, "native_observation", data))
        return events

    def _content(self, raw: JsonObject, message: JsonObject, blocks: list[JsonObject],
                 identity: str, data: JsonObject) -> list[tuple[str, str, JsonObject]]:
        kind = data["native_type"]
        if kind == "assistant":
            return self._assistant(raw, message, blocks, identity, data)
        if kind == "user":
            return self._user(raw, blocks, message.get("content", []), identity, data)
        parent = text_value(data, "parent_uuid") if data["parent_uuid"] else ""
        if kind == "system":
            return self._system(raw, identity, parent, data)
        if kind == "attachment":
            attachment = object_value(raw.get("attachment"))
            data["attachment"] = attachment
            if attachment.get("type") == "deferred_tools_record" and parent in self.finals:
                self.finals[identity] = self.finals[parent]
        return []

    def _assistant(self, raw: JsonObject, message: JsonObject, blocks: list[JsonObject],
                   identity: str, data: JsonObject) -> list[tuple[str, str, JsonObject]]:
        if message.get("model") != self.manifest.model:
            reject("Native model identity mismatch")
        response = text_value(raw, "requestId") + ":" + text_value(message, "id")
        measured = self.usage(object_value(message.get("usage")), "claude", response)
        events = self._response_usage(response, measured)
        text = "".join(text_value(block, "text") for block in blocks if block.get("type") == "text")
        data.update(text=text, stop_reason=message.get("stop_reason"), response_id=response)
        events.append((identity, "native_assistant", data))
        if message.get("stop_reason") == "end_turn" and text:
            self.finals[identity] = {**data, "assistant_uuid": identity, "last_agent_message": text}
        for block in blocks:
            if block.get("type") == "tool_use":
                call_id = text_value(block, "id")
                events.append(("call:" + call_id, "tool_call", {
                    **data, "call_id": call_id, "attempt_id": response, "name": text_value(block, "name"),
                    "input": object_value(block.get("input")),
                }))
        return events

    def _response_usage(self, response: str, measured: JsonObject) -> list[tuple[str, str, JsonObject]]:
        previous = self.responses.get(response)
        if previous is not None:
            if previous != measured:
                reject("Conflicting repeated Claude response usage")
            return []
        self.responses[response] = measured
        return [(response, "usage_completion", measured)]

    @staticmethod
    def _user(raw: JsonObject, blocks: list[JsonObject], content: object, identity: str,
              data: JsonObject) -> list[tuple[str, str, JsonObject]]:
        events: list[tuple[str, str, JsonObject]] = []
        for block in blocks:
            if block.get("type") == "tool_result":
                call_id = text_value(block, "tool_use_id")
                events.append(("result:" + call_id, "tool_result", {
                    **data, "call_id": call_id, "is_error": block.get("is_error", False),
                    "content": block.get("content"), "native_result": raw.get("toolUseResult", {}),
                }))
        if isinstance(content, str):
            data.update(text=content, origin=object_value(raw.get("origin", {})).get("kind"))
            events.append((identity, "native_user", data))
        result = raw.get("toolUseResult", {})
        interrupted = isinstance(result, dict) and result.get("interrupted") is True
        if interrupted or (isinstance(content, str) and content.startswith("[Request interrupted by user")):
            events.append((identity + ":interruption", "native_interruption", {**data, "reason": "user/tool interruption"}))
        return events

    def _system(self, raw: JsonObject, identity: str, parent: str,
                data: JsonObject) -> list[tuple[str, str, JsonObject]]:
        subtype = text_value(raw, "subtype")
        data["subtype"] = subtype
        if subtype == "turn_duration":
            final = self.finals.get(parent)
            if final is None:
                reject("Native normal-end parent chain unavailable")
            return [(identity, "native_turn_complete", {**final, "native_uuid": identity})]
        if subtype in {"compact_boundary", "api_error", "turn_aborted"}:
            events = [(identity, "native_interruption", {**data, "reason": subtype})]
            if subtype == "compact_boundary":
                events.append((identity + ":compaction", "compaction", data))
            return events
        return []


# eof
