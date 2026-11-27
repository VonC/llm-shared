"""Optional Claude clear evidence from the public TUIOS pane event tail."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from tools.resume_paused_delivery_model import CALL_BOUND_SECONDS, LogEvent, LogKind
from tools.resume_paused_profiles import as_items, as_mapping, loads_strict

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_profiles import CommandRunner


def _clear_time(entry: dict[str, object]) -> datetime | None:
    """Recognize the daemon's typed clear reason and nanosecond epoch time."""
    at = entry.get("at")
    if entry.get("kind") != "session_start" or entry.get("text") != "clear" or type(at) is not int or at <= 0:
        return None
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(microseconds=at // 1000)


def _latest_clear(payload: dict[str, object], pane: PaneRecord) -> datetime | None:
    """Walk backwards from the reported head. Only trailing status and turn-end events preserve proof."""
    if payload.get("success") is not True or (payload.get("window"), payload.get("session")) != (pane.pane_id, pane.session):
        return None
    expected = payload.get("last_seq")
    if type(expected) is not int:
        return None
    for raw in reversed(as_items(payload.get("entries"))):
        entry = as_mapping(raw)
        seq = entry.get("seq")
        if type(seq) is not int or seq != expected or seq < 1:
            return None
        if entry.get("kind") not in ("state", "turn_end"):
            return _clear_time(entry)
        expected -= 1
    return None


@dataclass(frozen=True)
class TerminalClearLog:
    """Read the current pane's bounded event tail only when a Claude clear was requested."""

    runner_for: Callable[[float], CommandRunner]

    def events(self, pane: PaneRecord) -> tuple[LogEvent, ...] | None:
        """An unsupported response, missing provenance or uncertain tail requires a fresh clear."""
        result = self.runner_for(CALL_BOUND_SECONDS).run(("tuios", "agent-log", "-s", pane.session, "-w", pane.pane_id, "--limit", "256", "--json"))
        if result.exit_code:
            return None
        try:
            at = _latest_clear(as_mapping(loads_strict(result.stdout)), pane)
        except (ValueError, RecursionError, OverflowError):
            return None
        return (LogEvent(LogKind.CLEAR, at),) if at else ()


# eof
