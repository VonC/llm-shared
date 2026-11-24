"""Pure synthetic host, pane and session builders for resume-paused tests.

Step 1 of v0.15.0 resume-paused shares these builders with later unit and
acceptance tests. They build declared process listings, Codex release layouts
and session files, and Claude transcript records without touching a real host,
a real pane or the filesystem. Scenario assertions stay in each test.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from tools.resume_paused_claude import ClaudeLedgerProfile, TranscriptFile
from tools.resume_paused_codex import MANIFEST_NAME, SessionFile
from tools.resume_paused_profiles import Host, HostProfile, ProfileRegistry
from tools.resume_paused_windows import GLOBALROOT, ImageWalk, ProcessRecord

SHELL_PID = 10
HOST_PID = 20
CREATED = 133_000_000_000_000_000
OS_BUILD = 26200
CODEX_VERSION = "0.167.2"
CODEX_TARGET = "x86_64-pc-windows-msvc"
CODEX_DIGEST = "a" * 64
RELEASE_ROOT = f"\\Device\\Volume3\\home\\.codex\\packages\\standalone\\releases\\{CODEX_VERSION}-{CODEX_TARGET}"
CODEX_NATIVE = f"{RELEASE_ROOT}\\codex.exe"
MANIFEST_PATH = f"{GLOBALROOT}{RELEASE_ROOT}\\{MANIFEST_NAME}"
CLAUDE_VERSION = "2.1.325"
SESSION_ID = "11111111-2222-3333-4444-555555555555"
CHECKOUT = "C:/work/checkout"
STOP_COMMAND = "tuios integration hook claude-code Stop"
T0 = datetime(2026, 11, 14, 10, 0, 0, tzinfo=UTC)


def at(seconds: int) -> datetime:
    """Return the declared base instant plus whole seconds."""
    return T0.replace(minute=seconds // 60, second=seconds % 60)


def filetime(moment: datetime) -> int:
    """Return an instant as FILETIME ticks, the unit of a process creation time."""
    return int((moment - datetime(1601, 1, 1, tzinfo=UTC)).total_seconds()) * 10_000_000


def codex_manifest(**changes: Any) -> bytes:  # noqa: ANN401
    """Render the observed eight-key layout-1 manifest, with declared changes."""
    manifest: dict[str, Any] = {
        "entrypoint": "codex.exe", "execServer": "codex-exec-server.exe", "layoutVersion": 1,
        "pathDir": "path", "resourcesDir": "resources", "target": CODEX_TARGET,
        "variant": "standalone", "version": CODEX_VERSION,
    }
    manifest.update(changes)
    return json.dumps(manifest).encode()


def codex_registry() -> ProfileRegistry:
    """Pin the synthetic Codex release; the shipped registry stays empty."""
    return ProfileRegistry((HostProfile(Host.CODEX, CODEX_VERSION, frozenset({OS_BUILD}), "synthetic", CODEX_DIGEST),))


@dataclass
class FakeWindowsApi:
    """Declared Windows observations for one pane shell and its host child."""

    build: int | None = OS_BUILD
    listing: tuple[ProcessRecord, ...] | None = (
        ProcessRecord(SHELL_PID, 1, "cmd.exe"), ProcessRecord(HOST_PID, SHELL_PID, "codex.exe"),
    )
    process_handle: int | None = 1020
    created: int | None = CREATED
    native: str | None = CODEX_NATIVE
    walk: ImageWalk = field(default_factory=lambda: ImageWalk(complete=True, regions=3, mapped_names=(CODEX_NATIVE, "ntdll.dll")))
    image_handle: int | None = 7
    status: int = 0
    digest: tuple[str, int] | None = (CODEX_DIGEST, 4096)
    files: dict[str, bytes] = field(default_factory=lambda: {MANIFEST_PATH: codex_manifest()})
    closed: list[int] = field(default_factory=list[int])
    hashed: int = 0

    def os_build(self) -> int | None:
        """Return the declared build number."""
        return self.build

    def processes(self) -> tuple[ProcessRecord, ...] | None:
        """Return the declared process listing."""
        return self.listing

    def open_process(self, pid: int) -> int | None:
        """Return the declared process handle for the host child only."""
        return self.process_handle if pid == HOST_PID else None

    def creation_time(self, process: int) -> int | None:
        """Return the declared creation time."""
        return self.created if process == self.process_handle else None

    def native_image_name(self, process: int) -> str | None:
        """Return the declared native image name."""
        return self.native if process == self.process_handle else None

    def image_walk(self, process: int) -> ImageWalk:
        """Return the declared allocation walk."""
        return self.walk if process == self.process_handle else ImageWalk(complete=False, regions=0, mapped_names=())

    def open_image(self, native_name: str) -> int | None:
        """Return the declared image handle for the declared native name."""
        return self.image_handle if native_name == self.native else None

    def image_mapping_status(self, process: int, image: int) -> int:
        """Return the declared identity status for the declared handles."""
        return self.status if (process, image) == (self.process_handle, self.image_handle) else 0xC0000001

    def sha256(self, image: int) -> tuple[str, int] | None:
        """Return the declared digest and count each hashing call."""
        self.hashed += 1
        return self.digest if image == self.image_handle else None

    def read_file(self, path: str) -> bytes | None:
        """Return the declared file bytes."""
        return self.files.get(path)

    def close(self, handle: int) -> None:
        """Record each closed handle."""
        self.closed.append(handle)


def jsonl(records: list[dict[str, Any]]) -> bytes:
    """Render complete JSONL bytes with the final newline."""
    return "".join(json.dumps(record) + "\n" for record in records).encode()


def codex_session(inputs: list[tuple[str, datetime]], *, cwd: str = CHECKOUT, version: str = CODEX_VERSION) -> bytes:
    """Render one Codex session file with its metadata and typed inputs."""
    records: list[dict[str, Any]] = [
        {"type": "session_meta", "payload": {"id": SESSION_ID, "cwd": cwd, "cli_version": version}},
    ]
    records.extend(
        {
            "type": "response_item", "timestamp": moment.isoformat(),
            "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": text}]},
        }
        for text, moment in inputs
    )
    return jsonl(records)


@dataclass
class FakeSessionStore:
    """Declared Codex session files keyed by path."""

    files: dict[str, bytes | None]
    modified: dict[str, datetime] = field(default_factory=dict[str, datetime])
    complete: bool = True

    def list_files(self) -> tuple[SessionFile, ...] | None:
        """Return the declared listing, or ``None`` for an incomplete enumeration."""
        if not self.complete:
            return None
        return tuple(
            SessionFile(path, int(self.modified.get(path, at(60)).timestamp() * 1_000_000_000), len(self.files.get(path) or b""))
            for path in self.files
        )

    def read(self, path: str) -> bytes | None:
        """Return the declared bytes; a ``None`` value models a failed read."""
        return self.files[path]


def claude_profile(**changes: Any) -> ClaudeLedgerProfile:  # noqa: ANN401
    """Build a synthetic pinned ledger profile; no real version is supported."""
    values: dict[str, Any] = {
        "version": CLAUDE_VERSION,
        "record_types": frozenset({"user", "assistant", "system", "attachment", "queue-operation", "mode"}),
        "attachment_types": frozenset({"hook_success"}),
        "tool_names": frozenset({"PowerShell", "CronCreate", "CronDelete"}),
        "stop_handlers": frozenset({STOP_COMMAND}),
        "block_types": frozenset({"text", "tool_use", "tool_result"}),
        "input_parents": frozenset({"attachment:hook_success"}),
    }
    values.update(changes)
    return ClaudeLedgerProfile(**values)


def record(kind: str, uuid: str | None = None, parent: str | None = None, seconds: int | None = None, **fields: Any) -> dict[str, Any]:  # noqa: ANN401
    """Build one Claude transcript record with the pinned session linkage."""
    data: dict[str, Any] = {"type": kind, "sessionId": SESSION_ID, "version": CLAUDE_VERSION, "cwd": CHECKOUT}
    if uuid is not None:
        data.update(uuid=uuid, parentUuid=parent)
    if seconds is not None:
        data["timestamp"] = at(seconds).isoformat()
    data.update(fields)
    return data


def session_start(uuid: str = "start", seconds: int = 5, hook: str = "SessionStart:startup") -> dict[str, Any]:
    """Build the launcher's SessionStart ``hook_success`` attachment."""
    return record("attachment", uuid, None, seconds, attachment={"type": "hook_success", "hookName": hook})


def typed(uuid: str, parent: str | None, seconds: int, text: str = "hello") -> dict[str, Any]:
    """Build a human-typed input record."""
    return record("user", uuid, parent, seconds, promptSource="typed", origin={"kind": "human"}, message={"content": text})


def closing(prefix: str, parent: str, seconds: int, command: str = STOP_COMMAND) -> list[dict[str, Any]]:
    """Build the Stop summary and final duration records that close a turn."""
    return [
        record("system", f"{prefix}-stop", parent, seconds, subtype="stop_hook_summary", hookInfos=[{"command": command}]),
        record("system", f"{prefix}-end", f"{prefix}-stop", seconds, subtype="turn_duration"),
    ]


def tool_call(  # noqa: PLR0913 - one declared field per argument keeps scenarios readable
    uuid: str, parent: str, seconds: int, call: str, name: str = "PowerShell", command: str | None = None,
) -> dict[str, Any]:
    """Build an assistant record carrying one tool call, with its command when declared."""
    block: dict[str, Any] = {"type": "tool_use", "id": call, "name": name}
    if command is not None:
        block["input"] = {"command": command}
    return record("assistant", uuid, parent, seconds, message={"content": [block]})


def tool_result(uuid: str, parent: str, seconds: int, call: str, **result: Any) -> dict[str, Any]:  # noqa: ANN401
    """Build the user record answering one tool call, with its structured result."""
    content = [{"type": "tool_result", "tool_use_id": call}]
    return record("user", uuid, parent, seconds, message={"content": content}, toolUseResult=result)


def task_ended(seconds: int, task: str, status: str = "completed") -> dict[str, Any]:
    """Build the terminal queue enqueue of a background task."""
    content = f"<task-notification><task-id>{task}</task-id><status>{status}</status></task-notification>"
    return record("queue-operation", None, None, seconds, operation="enqueue", content=content)


def reply(uuid: str, parent: str | None, seconds: int) -> dict[str, Any]:
    """Build an assistant text reply."""
    return record("assistant", uuid, parent, seconds, message={"content": [{"type": "text", "text": "ok"}]})


def closed_turn(*tools: tuple[Any, ...], text: str = "hello") -> list[dict[str, Any]]:
    """Build a started session with one closed turn running the declared tools.

    Each tool is its name, the structured result its call returned and,
    optionally, the command it ran. The input is typed at second 10; tool
    ``i`` is called at second ``20 + 2 * i`` and answered one second later;
    the reply comes at second 40 and the turn closes at second 41.
    """
    records = [record("mode"), session_start(), typed("in", "start", 10, text)]
    tail = "in"
    for index, (name, result, *command) in enumerate(tools):
        records.append(tool_call(f"call{index}", tail, 20 + 2 * index, f"c{index}", name, *command))
        records.append(tool_result(f"res{index}", f"call{index}", 21 + 2 * index, f"c{index}", **result))
        tail = f"res{index}"
    return [*records, reply("reply", tail, 40), *closing("t1", "reply", 41)]


@dataclass
class FakeTranscriptSource:
    """Declared Claude transcripts keyed by path."""

    files: dict[str, bytes | None]
    modified: dict[str, datetime] = field(default_factory=dict[str, datetime])
    complete: bool = True

    def list_files(self) -> tuple[TranscriptFile, ...] | None:
        """Return the declared listing, or ``None`` for an incomplete enumeration."""
        if not self.complete:
            return None
        return tuple(TranscriptFile(path, self.modified.get(path, at(60))) for path in self.files)

    def read(self, path: str) -> bytes | None:
        """Return the declared bytes; a ``None`` value models a failed read."""
        return self.files[path]


# eof
