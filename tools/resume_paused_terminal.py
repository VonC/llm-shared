"""Public terminal contracts used by the human bulk launcher."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.resume_paused_delivery_model import CALL_BOUND_SECONDS, DeliveryProfile
from tools.resume_paused_evidence import ScreenVerdict
from tools.resume_paused_input import pane_host
from tools.resume_paused_pane_guard import ClaudeScreen
from tools.resume_paused_profiles import Host

if TYPE_CHECKING:
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_transport import TuiosTransport

_SGR = re.compile(r"\x1b\[([0-9;]*)m")
_CLAUDE_BORDER = re.compile(r"─{4,}")
_SHORTCUTS = re.compile(r"^ *(?:← for agents · )?\? (?:for )?shortcuts(?:\s+.*)?$")
_MAX_FOOTER_ROWS = 5
_RGB = 2
_DIM = 2
_MODAL = re.compile(r"esc(?:ape)? to (?:cancel|close)|enter to (?:select|confirm)", re.IGNORECASE)
_CLEAR_BANNERS = {"Conversation cleared", "Conversation cleared.", "New conversation started", "New conversation started.", "Context cleared"}


@dataclass(frozen=True)
class HostCommands:
    """Native skills, clear command and visible editor prefix."""

    resume: str
    reviewer: str
    clear: str
    editor: str


COMMANDS: Final = {
    Host.CLAUDE: HostCommands("/resume-session", "/review-resume", "/clear", "\u276f"),
    Host.CODEX: HostCommands("$llm-shared:resume-session", "$llm-shared:review-resume", "/new", "\u203a"),
}


def plain(row: str) -> str:
    """Remove SGR styling and terminal padding while retaining editor indentation."""
    return _SGR.sub("", row).rstrip(" ")


def _dim_after(codes: str, *, dim: bool) -> bool:
    """Apply intensity changes, skipping the numeric arguments of SGR colors."""
    values = iter(int(part or 0) for part in codes.split(";"))
    for code in values:
        if code in {38, 48, 58}:
            count = 3 if next(values, None) == _RGB else 1
            for _ in range(count):
                next(values, None)
        elif code == _DIM:
            dim = True
        elif code in {0, 22}:
            dim = False
    return dim


def _suggestion(row: str, prefix: str) -> bool:
    """Require every visible character after the prompt to have dim intensity."""
    # A typed space before a ghost suggestion is a draft too. Padding after
    # the suggestion is part of the terminal grid.
    content = _SGR.sub("", row)
    if not content.startswith((prefix + " ", prefix + "\xa0")) or not content[len(prefix) + 1:].strip():
        return False
    if content[len(prefix) + 1].isspace():
        return False
    dim = False
    position = 0
    visible = ""
    for match in _SGR.finditer(row):
        chunk = row[position:match.start()]
        if not dim:
            visible += chunk
        position = match.end()
        dim = _dim_after(match[1], dim=dim)
    if not dim:
        visible += row[position:]
    return visible.strip() == prefix


def _claude_footer(line: str) -> bool:
    """Recognize an indented status line and reject modal hints."""
    return not line or (line.startswith("  ") and not _MODAL.search(line))


def _chrome(host: Host, above: str, below: tuple[str, ...]) -> bool:
    """Distinguish the editable prompt from history, wrapped drafts and dialogs."""
    if not below or len(below) > _MAX_FOOTER_ROWS + 1:
        return False
    if host is Host.CODEX:
        return not below[0] and bool(_SHORTCUTS.fullmatch(below[-1])) and all(line.startswith("  ") for line in below[1:-1])
    if not _CLAUDE_BORDER.fullmatch(above) or above != below[0]:
        return False
    return all(_claude_footer(line) for line in below[1:])


def _editor(host: Host, rows: tuple[str, ...]) -> str | None:
    """Locate the one physical editor row relative to its host's bottom chrome."""
    lines = tuple(plain(row) for row in rows)
    prefix = COMMANDS[host].editor
    for index in range(len(lines) - 1, -1, -1):
        if not lines[index].startswith(prefix):
            continue
        above = lines[index - 1] if index else ""
        return rows[index] if _chrome(host, above, lines[index + 1:]) else None
    return None


def editor_state(host: Host, rows: tuple[str, ...], command: str = "") -> ScreenVerdict:
    """Recognize an empty editor, or the exact command in a recovery check."""
    row = _editor(host, rows)
    if row is None:
        return ScreenVerdict.UNSUPPORTED
    prefix = COMMANDS[host].editor
    line = plain(row)
    if command:
        owned = line == f"{prefix} {command}" and sum(plain(item).count(command) for item in rows) == 1
        return ScreenVerdict.IDLE_EMPTY if owned else ScreenVerdict.DRAFT
    body = line.removeprefix(prefix).strip()
    if _suggestion(row, prefix) and (host is Host.CLAUDE or body == "Ask Codex to do anything"):
        return ScreenVerdict.IDLE_EMPTY
    return ScreenVerdict.DRAFT


def clear_observed(host: Host, before: tuple[str, ...], after: tuple[str, ...] | None, original: PaneRecord, current: PaneRecord) -> bool:
    """Confirm an empty editor and a new session identity or an additional clear banner."""
    if not after or editor_state(host, after) is not ScreenVerdict.IDLE_EMPTY:
        return False
    if original.agent_session_id and current.agent_session_id and original.agent_session_id != current.agent_session_id:
        return True
    return sum(plain(row).strip() in _CLEAR_BANNERS for row in after) > sum(plain(row).strip() in _CLEAR_BANNERS for row in before)


def result_lines(rows: tuple[str, ...] | None) -> tuple[str, ...]:
    """Remove terminal styling and the host's leading response bullet from result candidates."""
    candidates = (re.sub(r"^[•⏺●] +", "", plain(row).strip()) for row in rows or ())
    return tuple(line for line in candidates if line.startswith("resume-paused "))


@dataclass(frozen=True)
class TerminalScreens:
    """Read the editor with TUIOS and report exact compact failure lines."""

    transport: TuiosTransport
    recovery_pane: str | None = None
    require_empty = True

    def probe(self, pane: PaneRecord) -> ScreenVerdict:
        """Classify a fresh physical-row capture."""
        if pane.pane_id == self.recovery_pane:
            return ScreenVerdict.IDLE_EMPTY
        rows = self.transport.capture(pane, CALL_BOUND_SECONDS)
        host = pane_host(pane)
        return editor_state(host, rows) if host and rows else ScreenVerdict.UNSUPPORTED

    def read(self, pane: PaneRecord, lines: tuple[str, ...]) -> ClaudeScreen:
        """Classify a Claude pane in the checkout-wide reviewer guard."""
        del pane
        return ClaudeScreen.IDLE if editor_state(Host.CLAUDE, lines) is ScreenVerdict.IDLE_EMPTY else ClaudeScreen.UNKNOWN

    def profile(self, pane: PaneRecord) -> DeliveryProfile | None:
        """Select the native commands of a recognized host."""
        host = pane_host(pane)
        return DeliveryProfile(host, COMMANDS[host].clear) if host is not None else None

    def results(self, pane: PaneRecord, timeout: float) -> tuple[str, ...]:
        """Expose only compact result-line candidates from the visible terminal."""
        return result_lines(self.transport.capture(pane, timeout))


# eof
