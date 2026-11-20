"""Budget-bounded readers for the acceptance proofs of the guarded delivery.

Step 6 of v0.14.0 resume-paused, code review round 3: every send of the
delivery has a fixed 100-second budget, and an acceptance proof reads several
pieces of evidence in turn (Codex: the pane's version evidence, a pane
capture, the session files; Claude: the transcript listing and the
transcript). Each reader here wraps one Step 1 or Step 4 port and asks the
send's ``Remaining`` callable, at the moment of its own call, how many seconds
are left:

- with time left, it reads; a capture is bounded by what is left at that
  moment (at most ``CALL_BOUND_SECONDS``), never by a figure computed before
  an earlier, slower read;
- once the budget is spent, it reads nothing and reports the evidence
  unavailable, so the proof fails closed and the checkout guard is not held
  for further work.

The Step 8 composition builds each proof's prover from these wrappers inside
the delivery's ``ProverFactory``. Nothing here writes or sends input.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.resume_paused_delivery_model import CALL_BOUND_SECONDS

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.resume_paused_claude import TranscriptFile, TranscriptSource
    from tools.resume_paused_codex import CodexPaneProfile, SessionFile, SessionStore
    from tools.resume_paused_delivery_model import Remaining
    from tools.resume_paused_input import CodexVersions, PaneRecord


class BoundedCapture:
    """``PaneCapture`` bounded by the seconds left at the moment of the capture; none once they are spent."""

    def __init__(self, capture: Callable[[PaneRecord, float], tuple[str, ...] | None], remaining: Remaining) -> None:
        """Keep the bounded transport capture and the send's remaining-time source."""
        self._capture = capture
        self._remaining = remaining

    def capture(self, pane: PaneRecord) -> tuple[str, ...] | None:
        """Capture with the time left, at most the call bound, or report no capture."""
        seconds = self._remaining()
        return None if seconds <= 0 else self._capture(pane, min(CALL_BOUND_SECONDS, seconds))


class BoundedVersions:
    """``CodexVersions`` that reads the pane's version evidence only while time is left."""

    def __init__(self, versions: CodexVersions, remaining: Remaining) -> None:
        """Keep the version source and the send's remaining-time source."""
        self._versions = versions
        self._remaining = remaining

    def evidence(self, pane: PaneRecord) -> tuple[str, CodexPaneProfile] | None:
        """Return the evidence, or ``None`` once the budget is spent."""
        return None if self._remaining() <= 0 else self._versions.evidence(pane)


class BoundedSessionStore:
    """``SessionStore`` that lists and reads Codex session files only while time is left."""

    def __init__(self, store: SessionStore, remaining: Remaining) -> None:
        """Keep the session store and the send's remaining-time source."""
        self._store = store
        self._remaining = remaining

    def list_files(self) -> tuple[SessionFile, ...] | None:
        """List the session files, or report an incomplete enumeration once the budget is spent."""
        return None if self._remaining() <= 0 else self._store.list_files()

    def read(self, path: str) -> bytes | None:
        """Read one session file, or report it unreadable once the budget is spent."""
        return None if self._remaining() <= 0 else self._store.read(path)


class BoundedTranscriptSource:
    """``TranscriptSource`` that lists and reads Claude transcripts only while time is left."""

    def __init__(self, source: TranscriptSource, remaining: Remaining) -> None:
        """Keep the transcript source and the send's remaining-time source."""
        self._source = source
        self._remaining = remaining

    def list_files(self) -> tuple[TranscriptFile, ...] | None:
        """List the transcripts, or report an incomplete enumeration once the budget is spent."""
        return None if self._remaining() <= 0 else self._source.list_files()

    def read(self, path: str) -> bytes | None:
        """Read one transcript, or report it unreadable once the budget is spent."""
        return None if self._remaining() <= 0 else self._source.read(path)


__all__ = [
    "BoundedCapture",
    "BoundedSessionStore",
    "BoundedTranscriptSource",
    "BoundedVersions",
]


# eof
