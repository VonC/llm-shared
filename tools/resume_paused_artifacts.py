"""Exact-byte pause prompt, usage receipt and routing readers for resume-paused.

Step 2 of v0.14.0 resume-paused reads one checkout's saved pause without any
write: the artifact-home declaration through ``ReviewArtifactConfiguration.load``
(never ``prepare_home`` or a legacy-file move), the home's existing ignore
file, the prompt's exact bytes and the usage receipt. ``CheckoutSnapshot``
applies the resume-session state table (no saved prompt, unused, new since
use, used, or an error that stops this checkout) and reports the routing
separately as absent, table-only, unresolved, resolved or an error.

Prompts keep the grammar the installed ``tuitp`` reads: the heading
``# <agent-id>: Resume session: <title>`` and ``- Name: value`` metadata
lines, ``- Session role:`` included. Receipts keep their ``- Prompt:``,
``- SHA-256:`` and ``- Project root:`` lines in every schema; schema 3, which
a marked resume writes, adds ``- Launch id:``, ``- Receiving pane:`` and
``- Assignment binding:``.

Routing comes only from one top-level fenced block opened by the exact line
``ROUTING_FENCE``. The readable table rendered from that JSON, headed by
``ROUTING_TABLE_HEADER``, may follow it and must then equal the rendering;
any other routing table beside the JSON is a contradiction.

Fix (code review round 1): the snapshot's exact reads and byte account start
with the ``.review-artifacts.ini`` declaration that the configuration load
reads, both when the home resolves and when the declaration is rejected.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import StrEnum
from itertools import takewhile
from typing import TYPE_CHECKING, Final

from tools.resume_paused_models import (
    LAUNCH_ID_RE,
    PROMPT_NAME,
    RECEIPT_NAME,
    ArtifactError,
    CanonicalRoot,
    PromptDigest,
    SessionRole,
    agent_id,
    checked_text,
    checked_timestamp,
    pane_id,
    sha256_hex,
    timestamp_instant,
)
from tools.resume_paused_profiles import ReadAccount, loads_strict
from tools.resume_paused_routing import (
    ROUTING_SCHEMA,
    ROUTING_VERSION,
    NotApplicable,
    PaneIdentity,
    RoutingTarget,
    SavedExchange,
    SavedRouting,
    Unresolved,
)
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

ROUTING_FENCE: Final = "```json resume-paused-routing"
ROUTING_TABLE_HEADER: Final = "| Routing item | Value |"
_TABLE_RULE: Final = "| --- | --- |"
_LEGACY_TABLE_PREFIX: Final = "| Target | Agent host and intended role |"
_IGNORE_NAME: Final = ".gitignore"
_DECLARATION_NAME: Final = ".review-artifacts.ini"
_IGNORE_BYTES: Final = b"*\n"
_RECEIPT_TITLE: Final = "# Session resume usage receipt"
_HEADING_RE: Final = re.compile(r"# ([a-z0-9-]+): Resume session: (.*)")
_FIELD_RE: Final = re.compile(r"- (?P<name>[A-Za-z][A-Za-z0-9 -]*?): *(?P<value>.*?) *")
_FENCE_RE: Final = re.compile(r" {0,3}(?P<marker>`{3,}|~{3,}).*")
_MAX_FENCE_INDENT: Final = 3
_PROMPT_FIELDS: Final = ("Snapshot", "Project root", "Session role")
_SCHEMA_ONE: Final = ("Schema", "Prompt", "SHA-256", "Project root", "Used at", "Forced")
_SCHEMA_TWO: Final = (*_SCHEMA_ONE, "Paused by", "Resumed by", "Agent override")
_SCHEMA_THREE: Final = (*_SCHEMA_TWO, "Launch id", "Receiving pane", "Assignment binding")
_RECEIPT_SCHEMAS: Final = {"1": (1, _SCHEMA_ONE), "2": (2, _SCHEMA_TWO), "3": (3, _SCHEMA_THREE)}
_ROLE_TOKENS: Final = frozenset(role.value for role in SessionRole)
_FORCED: Final = {"true": True, "false": False}


class PromptState(StrEnum):
    """Resume-session state of one checkout's latest saved prompt."""

    NO_PROMPT = "no-saved-prompt"
    UNUSED = "unused"
    NEW_SINCE_USE = "new-since-use"
    USED = "used"
    ERROR = "error"


class RoutingState(StrEnum):
    """Whether bulk launch can use a prompt's saved routing."""

    ABSENT = "absent"
    TABLE_ONLY = "table-only"
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    ERROR = "error"


@dataclass(frozen=True)
class PromptMetadata:
    """Exact digest and header fields of one saved prompt."""

    digest: PromptDigest
    size: int
    author: str | None
    title: str
    session_role: str
    snapshot: str
    project_root: CanonicalRoot


@dataclass(frozen=True)
class RoutingReading:
    """The saved routing of one prompt, or the reasons bulk launch cannot use it."""

    state: RoutingState
    routing: SavedRouting | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class UsageReceipt:
    """One validated usage receipt; later schemas only add fields."""

    schema: int
    digest: PromptDigest
    project_root: CanonicalRoot
    used_at: str
    forced: bool
    paused_by: str | None = None
    resumed_by: str | None = None
    agent_override: str | None = None
    launch_id: str | None = None
    receiving_pane: str | None = None
    assignment_binding: str | None = None


@dataclass(frozen=True)
class CheckoutSnapshot:
    """One canonical checkout's saved pause, with the exact files read to obtain it."""

    root: CanonicalRoot
    home: Path | None
    state: PromptState
    prompt: PromptMetadata | None = None
    receipt: UsageReceipt | None = None
    routing: RoutingReading | None = None
    diagnostic: str = ""
    reads: tuple[Path, ...] = ()
    account: ReadAccount = field(default_factory=ReadAccount)


def _lines(data: bytes, label: str) -> list[str]:
    """Decode strict UTF-8, drop a byte-order mark and split CRLF or LF lines."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ArtifactError(f"{label} is not UTF-8") from error
    return text.removeprefix("\N{ZERO WIDTH NO-BREAK SPACE}").splitlines()


def _header(lines: Sequence[str]) -> list[str]:
    """Return the lines above the first level-two section."""
    return list(takewhile(lambda line: not line.startswith("## "), lines))


def _single_field(lines: Sequence[str], name: str) -> str:
    """Return one header field's value, read the way the installed launcher reads it."""
    pattern = re.compile(rf"- {re.escape(name)}: *(.*?) *")
    values = [match[1] for line in lines if (match := pattern.fullmatch(line)) is not None]
    if not values:
        raise ArtifactError(f"resume prompt is incomplete: missing {name}")
    if len(values) > 1:
        raise ArtifactError(f"resume prompt repeats {name}")
    return values[0]


def _unquote(value: str) -> str:
    """Drop one pair of backticks around a header path value."""
    return value[1:-1] if len(value) > 1 and value.startswith("`") and value.endswith("`") else value


def parse_prompt(data: bytes, root: CanonicalRoot) -> tuple[PromptMetadata, RoutingReading]:
    """Parse exact prompt bytes for one checkout; routing problems stay in the reading."""
    lines = _lines(data, "resume prompt")
    if not any(line.strip() for line in lines):
        raise ArtifactError("resume prompt is empty")
    first = lines[0].strip()
    heading = _HEADING_RE.fullmatch(first)
    values = {name: _single_field(_header(lines[1:]), name) for name in _PROMPT_FIELDS}
    project_root = CanonicalRoot.parse(_unquote(values["Project root"]), "prompt project root")
    if project_root != root:
        raise ArtifactError("resume prompt names another checkout")
    metadata = PromptMetadata(
        PromptDigest.of(data),
        len(data),
        heading[1] if heading else None,
        (heading[2] if heading else first.lstrip("# ")).strip(),
        checked_text(values["Session role"], "prompt session role"),
        checked_timestamp(values["Snapshot"], "prompt snapshot"),
        project_root,
    )
    return metadata, read_routing(lines, metadata)


@dataclass(frozen=True)
class _RoutingLayout:
    """Line positions of routing blocks and tables outside every other fence."""

    blocks: tuple[tuple[int, int], ...]
    tables: tuple[int, ...]
    legacy: tuple[int, ...]


def _closes(line: str, marker: str) -> bool:
    """Return whether one line closes the fence that ``marker`` opened."""
    stripped = line.strip()
    indent = len(line) - len(line.lstrip(" "))
    return indent <= _MAX_FENCE_INDENT and len(stripped) >= len(marker) and set(stripped) == {marker[0]}


def _scan_routing(lines: Sequence[str]) -> _RoutingLayout:
    """Locate top-level routing blocks and tables; quoted fences hide their content."""
    blocks: list[tuple[int, int]] = []
    tables: list[int] = []
    legacy: list[int] = []
    marker, start = "", None
    for index, line in enumerate(lines):
        if marker:
            if _closes(line, marker):
                if start is not None:
                    blocks.append((start, index))
                marker, start = "", None
            continue
        opening = _FENCE_RE.fullmatch(line)
        if opening is not None:
            marker, start = opening["marker"], index + 1 if line == ROUTING_FENCE else None
        elif line == ROUTING_TABLE_HEADER:
            tables.append(index)
        elif line.startswith(_LEGACY_TABLE_PREFIX):
            legacy.append(index)
    if start is not None:
        raise ArtifactError("routing JSON block is not closed")
    return _RoutingLayout(tuple(blocks), tuple(tables), tuple(legacy))


def parse_routing_json(text: str) -> SavedRouting:
    """Parse one routing block's JSON text, refusing duplicate keys."""
    try:
        data = loads_strict(text)
    except (ValueError, RecursionError) as error:
        raise ArtifactError(f"invalid routing JSON: {error}") from error
    return SavedRouting.from_mapping(data)


def _require_rendered_table(lines: Sequence[str], routing: SavedRouting) -> None:
    """Require the table starting at ``lines`` to equal the rendering of the JSON."""
    table = tuple(takewhile(lambda line: line.startswith("|"), lines))
    if table != render_routing_table(routing):
        raise ArtifactError("routing table contradicts the routing JSON block")


def _require_agreement(routing: SavedRouting, prompt: PromptMetadata) -> None:
    """Reject routing whose pause identity contradicts the prompt header."""
    pause = routing.pause
    if pause.checkout != prompt.project_root:
        raise ArtifactError("routing checkout contradicts the prompt project root")
    if timestamp_instant(pause.snapshot) != timestamp_instant(prompt.snapshot):
        raise ArtifactError("routing snapshot contradicts the prompt snapshot")
    if pause.author != (prompt.author or "unknown"):
        raise ArtifactError("routing author contradicts the prompt heading")
    role = prompt.session_role.lower()
    if role in _ROLE_TOKENS and role != pause.session_role.value:
        raise ArtifactError("routing session role contradicts the prompt")


def _classify_routing(lines: Sequence[str], prompt: PromptMetadata) -> RoutingReading:
    """Read the routing block, compare its rendered table, and classify the result."""
    layout = _scan_routing(lines)
    blocks = layout.blocks
    if len(blocks) > 1:
        raise ArtifactError("resume prompt holds more than one routing JSON block")
    if not blocks:
        state = RoutingState.TABLE_ONLY if layout.tables or layout.legacy else RoutingState.ABSENT
        return RoutingReading(state, None, ())
    if layout.legacy:
        raise ArtifactError("routing table is not rendered from the routing JSON block")
    if len(layout.tables) > 1:
        raise ArtifactError("resume prompt repeats the routing table")
    start, end = next(iter(blocks))
    routing = parse_routing_json("\n".join(lines[start:end]))
    if layout.tables:
        _require_rendered_table(lines[layout.tables[0]:], routing)
    _require_agreement(routing, prompt)
    reasons = routing.unresolved
    return RoutingReading(RoutingState.UNRESOLVED if reasons else RoutingState.RESOLVED, routing, reasons)


def read_routing(lines: Sequence[str], prompt: PromptMetadata) -> RoutingReading:
    """Classify a prompt's saved routing; a routing error never hides the rest of the pause."""
    try:
        reading = _classify_routing(lines, prompt)
    except ArtifactError as error:
        reading = RoutingReading(RoutingState.ERROR, None, (str(error),))
    return reading


def _cell(value: str) -> str:
    """Escape the table cell separator."""
    return value.replace("|", "\\|")


def _pane_text(pane: PaneIdentity | Unresolved) -> str:
    """Describe the historical pausing pane."""
    if isinstance(pane, Unresolved):
        return f"unknown: {pane.reason}"
    return f"{pane.host} in TUIOS session {pane.session}, pane {pane.pane_id}, label {pane.label or 'none'}"


def _slot_text(slot: RoutingTarget | Unresolved | NotApplicable) -> str:
    """Describe one target slot."""
    if isinstance(slot, Unresolved):
        return f"unknown: {slot.reason}"
    if isinstance(slot, NotApplicable):
        return f"not applicable: {slot.reason}"
    return (
        f"{slot.role.value} on {slot.host.value} in TUIOS session {slot.session}, pane {slot.pane_id}, "
        f"label {slot.label or 'none'}, checkout {slot.checkout.display}, "
        f"agent session {slot.agent_session_id or 'none'}; evidence: {slot.evidence}"
    )


def _exchange_text(exchange: SavedExchange | Unresolved | NotApplicable) -> str:
    """Describe the saved exchange or why none applies."""
    if not isinstance(exchange, SavedExchange):
        return _slot_text(exchange)
    return (
        f"{exchange.family.value} review of {exchange.document}, "
        f"implementation step {exchange.implementation_step or 'not applicable'}, "
        f"umbrella {exchange.umbrella or 'none'}, occurrence {exchange.occurrence}, "
        f"round at pause {exchange.round_number or 'none'}"
    )


def render_routing_table(routing: SavedRouting) -> tuple[str, ...]:
    """Render the readable routing table derived from the JSON object."""
    pause, observation = routing.pause, routing.observation
    rows = (
        ("Routing schema", f"{ROUTING_SCHEMA} version {ROUTING_VERSION}"),
        ("Pause checkout", pause.checkout.display),
        ("Pause snapshot", pause.snapshot),
        ("Pause author", pause.author),
        ("Saved session role", pause.session_role.value),
        ("Pausing pane", _pane_text(pause.pane)),
        ("Observed at", observation.observed_at),
        ("Assignment source", observation.assignment_source),
        ("Observation evidence", observation.evidence),
        ("Resumed agent", _slot_text(routing.resumed)),
        ("Requestor", _slot_text(routing.requestor)),
        ("Reviewer", _slot_text(routing.reviewer)),
        ("Review exchange", _exchange_text(routing.exchange)),
    )
    return (ROUTING_TABLE_HEADER, _TABLE_RULE, *(f"| {name} | {_cell(value)} |" for name, value in rows))


def render_routing_section(routing: SavedRouting) -> tuple[str, ...]:
    """Render the routing JSON block, then its readable table, as a pause writes them."""
    body = json.dumps(routing.to_mapping(), indent=2, ensure_ascii=False).splitlines()
    return (ROUTING_FENCE, *body, "```", "", *render_routing_table(routing))


def _receipt_values(lines: Sequence[str]) -> dict[str, str]:
    """Read the receipt's ``- Name: value`` block, refusing other or repeated lines."""
    values: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        match = _FIELD_RE.fullmatch(line)
        if match is None:
            raise ArtifactError("usage receipt has a malformed line above its first section")
        name = match["name"]
        if name in values:
            raise ArtifactError(f"usage receipt repeats {name}")
        values[name] = match["value"]
    return values


def _agent_fields(values: dict[str, str]) -> dict[str, str | None]:
    """Validate the schema 2 agent fields when the schema carries them."""
    if "Paused by" not in values:
        return {}
    return {
        "paused_by": agent_id(values["Paused by"], "receipt Paused by"),
        "resumed_by": agent_id(values["Resumed by"], "receipt Resumed by"),
        "agent_override": checked_text(values["Agent override"], "receipt Agent override"),
    }


def _binding_fields(values: dict[str, str]) -> dict[str, str | None]:
    """Validate the schema 3 marked-resume binding fields when the schema carries them."""
    if "Launch id" not in values:
        return {}
    if LAUNCH_ID_RE.fullmatch(values["Launch id"]) is None:
        raise ArtifactError("invalid receipt Launch id: expected 32 lowercase hexadecimal characters")
    return {
        "launch_id": values["Launch id"],
        "receiving_pane": pane_id(values["Receiving pane"], "receipt Receiving pane"),
        "assignment_binding": sha256_hex(values["Assignment binding"], "receipt Assignment binding"),
    }


def _receipt_schema(values: dict[str, str]) -> int:
    """Return the receipt schema after checking it carries exactly that schema's fields."""
    schema = _RECEIPT_SCHEMAS.get(values.get("Schema", ""))
    if schema is None:
        raise ArtifactError(f"unsupported usage receipt schema: {values.get('Schema')}")
    number, expected = schema
    unexpected = sorted(set(values) - set(expected))
    missing = [name for name in expected if name not in values]
    if unexpected or missing:
        raise ArtifactError(
            f"usage receipt has unexpected {', '.join(unexpected) or 'nothing'}; missing {', '.join(missing) or 'nothing'}",
        )
    return number


def _forced(values: dict[str, str]) -> bool:
    """Check the canonical prompt basename, then return the recorded force flag."""
    if values["Prompt"] != PROMPT_NAME:
        raise ArtifactError("usage receipt names another prompt")
    forced = _FORCED.get(values["Forced"])
    if forced is None:
        raise ArtifactError("invalid receipt Forced: expected true or false")
    return forced


def parse_receipt(data: bytes) -> UsageReceipt:
    """Parse one strict usage receipt of schema 1, 2 or 3."""
    lines = _lines(data, "usage receipt")
    if not lines or lines[0].strip() != _RECEIPT_TITLE:
        raise ArtifactError("usage receipt has no receipt title")
    values = _receipt_values(_header(lines[1:]))
    schema = _receipt_schema(values)
    return UsageReceipt(
        schema,
        PromptDigest.parse(values["SHA-256"]),
        CanonicalRoot.parse(values["Project root"], "receipt project root"),
        checked_timestamp(values["Used at"], "receipt use time"),
        _forced(values),
        **_agent_fields(values),
        **_binding_fields(values),
    )


def classify_usage(prompt: PromptMetadata, receipt: UsageReceipt | None, root: CanonicalRoot) -> PromptState:
    """Apply the resume-session reuse table to one valid prompt and receipt."""
    if receipt is None:
        return PromptState.UNUSED
    if receipt.project_root != root:
        raise ArtifactError("usage receipt names another checkout")
    return PromptState.USED if receipt.digest == prompt.digest else PromptState.NEW_SINCE_USE


def _declaration_read(path: Path) -> tuple[list[Path], ReadAccount]:
    """Account for the declaration, which ``ReviewArtifactConfiguration.load`` reads when it is a file."""
    if not path.is_file():
        return [], ReadAccount()
    return [path], ReadAccount().plus(path.stat().st_size)


class _CheckoutReader:
    """Read one home's exact files, keeping what parsed for the error report."""

    def __init__(self, root: CanonicalRoot, home: Path, declaration: tuple[list[Path], ReadAccount]) -> None:
        """Bind the canonical root, the declared home and the declaration already read."""
        self._root = root
        self._home = home
        self._reads, self._account = declaration
        self._prompt: PromptMetadata | None = None
        self._routing: RoutingReading | None = None
        self._receipt: UsageReceipt | None = None

    def read(self) -> CheckoutSnapshot:
        """Validate the existing ignore file, then read the prompt and its receipt."""
        if not self._home.exists():
            return self.snapshot(PromptState.NO_PROMPT, "artifact home does not exist")
        ignore = self._home / _IGNORE_NAME
        if not ignore.exists():
            raise ArtifactError("artifact home has no ignore file")
        if self._read(ignore, "artifact home ignore file") != _IGNORE_BYTES:
            raise ArtifactError("artifact home ignore coverage is invalid")
        prompt = self._home / PROMPT_NAME
        if not prompt.exists():
            return self.snapshot(PromptState.NO_PROMPT, "")
        self._prompt, self._routing = parse_prompt(self._read(prompt, "resume prompt"), self._root)
        receipt = self._home / RECEIPT_NAME
        if receipt.exists():
            self._receipt = parse_receipt(self._read(receipt, "usage receipt"))
        return self.snapshot(classify_usage(self._prompt, self._receipt, self._root), "")

    def _read(self, path: Path, label: str) -> bytes:
        """Read one exact existing file and account for its bytes."""
        if not path.is_file():
            raise ArtifactError(f"{label} is not a file")
        try:
            data = path.read_bytes()
        except OSError as error:
            raise ArtifactError(f"{label} is unreadable: {error.strerror or error}") from error
        self._reads.append(path)
        self._account = self._account.plus(len(data))
        return data

    def snapshot(self, state: PromptState, diagnostic: str) -> CheckoutSnapshot:
        """Return the snapshot of everything read so far."""
        return CheckoutSnapshot(
            self._root, self._home, state, self._prompt, self._receipt, self._routing,
            diagnostic, tuple(self._reads), self._account,
        )


def read_checkout_snapshot(
    project_root: Path,
    *,
    tracked_directory: Callable[[Path, str], bool] | None = None,
) -> CheckoutSnapshot:
    """Read one checkout's saved pause without preparing, migrating or writing anything."""
    try:
        configuration = ReviewArtifactConfiguration.load(project_root, tracked_directory=tracked_directory)
    except (OSError, ReviewExchangeError) as error:
        reads, account = _declaration_read(project_root / _DECLARATION_NAME)
        return CheckoutSnapshot(
            CanonicalRoot.from_path(project_root.absolute()), None, PromptState.ERROR,
            diagnostic=f"artifact home is unusable: {error}", reads=tuple(reads), account=account,
        )
    declaration = _declaration_read(configuration.declaration_path)
    reader = _CheckoutReader(CanonicalRoot.from_path(configuration.project_root), configuration.home, declaration)
    try:
        snapshot = reader.read()
    except ArtifactError as error:
        snapshot = reader.snapshot(PromptState.ERROR, str(error))
    return snapshot


__all__ = [
    "ROUTING_FENCE",
    "ROUTING_TABLE_HEADER",
    "CheckoutSnapshot",
    "PromptMetadata",
    "PromptState",
    "RoutingReading",
    "RoutingState",
    "UsageReceipt",
    "classify_usage",
    "parse_prompt",
    "parse_receipt",
    "parse_routing_json",
    "read_checkout_snapshot",
    "read_routing",
    "render_routing_section",
    "render_routing_table",
]


# eof
