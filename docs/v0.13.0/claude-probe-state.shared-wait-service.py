"""Selected native evidence for the bounded Claude Monitor feasibility probe."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value, compact=False):
    path = Path(path)
    temporary = path.with_name(path.name + ".new")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=None if compact else 2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def native_records(path):
    """Ignore only an unfinished final JSONL record; malformed complete data fails."""
    data = Path(path).read_bytes()
    return [json.loads(line) for line in data.split(b"\n")[:-1] if line]


def timestamp(record):
    return datetime.fromisoformat(record["timestamp"]).timestamp()


def blocks(record, kind):
    content = record.get("message", {}).get("content", [])
    return [part for part in content if isinstance(part, dict) and part.get("type") == kind]


def native_state(records, config):
    """Require a successful exact Monitor call and its native normal-end chain."""
    monitor_id = None
    monitor_result = None
    final_id = None
    armed_end = None
    done_ids = set()
    final_end = None
    interruption = None
    calls = []
    notices = []
    usages = {}
    for record in records:
        # Claude writes file-history snapshots without conversation identity or
        # top-level timestamps. They are bookkeeping, never lifecycle evidence.
        if record.get("type") == "file-history-snapshot" and "sessionId" not in record:
            continue
        if record.get("sessionId") != config["thread"]:
            raise ValueError("Native session identity changed")
        at = timestamp(record) if record.get("timestamp") else None
        if at is None or at < config["prepared_at"]:
            continue
        if record.get("version") not in (None, config["build"]):
            raise ValueError("Native build changed during the smoke probe")
        if record.get("type") == "assistant":
            for call in blocks(record, "tool_use"):
                calls.append({"at": at, "name": call["name"], "id": call["id"], "input": call["input"]})
                if call["name"] == "Monitor":
                    if monitor_id is not None:
                        interruption = "multiple Monitor calls"
                    elif call["input"] == config["monitor_input"]:
                        monitor_id = call["id"]
                    else:
                        interruption = "Monitor input differs from prepared probe"
            text = "".join(part["text"] for part in blocks(record, "text"))
            if record.get("message", {}).get("stop_reason") == "end_turn":
                if text.strip() == config["armed_marker"] and monitor_result:
                    final_id = record["uuid"]
                if text.strip() == "WAIT_TEST_DONE":
                    done_ids.add(record["uuid"])
            message = record.get("message", {})
            if message.get("usage") and record.get("requestId"):
                usages[record["requestId"] + ":" + message["id"]] = {
                    "at": at, "request_id": record["requestId"], "message_id": message["id"],
                    "usage": message["usage"], "model": message.get("model"),
                }
        for result in blocks(record, "tool_result"):
            if result.get("tool_use_id") == monitor_id:
                if result.get("is_error"):
                    interruption = "Monitor returned an error"
                else:
                    monitor_result = {"at": at, "uuid": record["uuid"], "content": result.get("content")}
        if record.get("type") == "system" and record.get("subtype") == "turn_duration":
            if final_id is not None and record.get("parentUuid") == final_id and armed_end is None:
                armed_end = {"at": at, "uuid": record["uuid"], "assistant_uuid": final_id}
            if record.get("parentUuid") in done_ids and final_end is None:
                final_end = {"at": at, "uuid": record["uuid"]}
        if armed_end and at > armed_end["at"]:
            if record.get("type") == "user" and record.get("origin", {}).get("kind") == "human":
                interruption = "human input after the registering turn"
            if record.get("type") == "system" and record.get("subtype") in {"compact_boundary", "api_error"}:
                interruption = "native " + record["subtype"]
            content = record.get("message", {}).get("content")
            if isinstance(content, str) and ("task-notification" in content or "monitor" in content.lower()):
                notices.append({"at": at, "uuid": record.get("uuid"), "content": content})
            attachment = record.get("attachment", {})
            if "task" in attachment.get("type", "") or "monitor" in attachment.get("type", ""):
                notices.append({"at": at, "uuid": record.get("uuid"), "attachment": attachment})
    return {"monitor_id": monitor_id, "monitor_result": monitor_result, "armed_end": armed_end,
            "final_end": final_end, "done_messages": len(done_ids), "interruption": interruption,
            "calls": calls, "notices": notices, "usage_completions": list(usages.values())}


def capability(records):
    """Export only loaded Monitor definition and selected configuration/evidence."""
    entries = [entry for record in records
               if record.get("attachment", {}).get("type") == "deferred_tools_record"
               for entry in record["attachment"]["entries"] if entry.get("name") == "Monitor"]
    if len(entries) != 1:
        raise ValueError("Expected exactly one loaded Monitor definition")
    marker = next(record for record in records if record.get("type") == "user"
                  and isinstance(record.get("message", {}).get("content"), str)
                  and "CLAUDE_WAIT_CAPABILITY_20260916" in record["message"]["content"])
    following = records[records.index(marker) + 1:]
    next_human = next((index for index, record in enumerate(following)
                       if record.get("type") == "user" and record.get("origin", {}).get("kind") == "human"), len(following))
    answers = [record for record in following[:next_human] if record.get("type") == "assistant"
               and record.get("message", {}).get("stop_reason") == "end_turn" and blocks(record, "text")]
    answer = answers[-1]
    return {"thread": marker["sessionId"], "build": marker["version"],
            "permission_mode": marker.get("permissionMode", "unknown"),
            "model": answer["message"]["model"], "effort": answer.get("effort", "unknown"),
            "provider": "unknown", "actual_loaded_monitor_definition": entries[0],
            "answer_at": answer["timestamp"], "answer": blocks(answer, "text"),
            "scope": "Capability loaded; no Monitor execution or idle wake demonstrated yet"}

# eof
