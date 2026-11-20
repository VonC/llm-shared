"""Example tests of the budget-bounded proof readers of resume-paused.

Step 6 of v0.14.0 resume-paused, code review round 3: each reader asks the
send's remaining-time source at the moment of its own call. With time left
it reads, a capture bounded by what is left (at most the 30-second call
bound); once the budget is spent it reads nothing and reports the evidence
unavailable. Every wrapped port is declared and records its calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from tools.resume_paused_budget import (
    BoundedCapture,
    BoundedSessionStore,
    BoundedTranscriptSource,
    BoundedVersions,
)
from tools.resume_paused_claude import TranscriptFile
from tools.resume_paused_codex import CodexPaneProfile, SessionFile
from tools.resume_paused_input import PaneRecord

PANE = PaneRecord("2fd92f30-1111-4222-8333-444455556666", "work", "Codex api", "C:\\work\\api", "", ("codex",), None)
PROFILE = CodexPaneProfile("> ", r"Working.*")
SESSION = SessionFile("C:/codex/sessions/s.jsonl", 1, 2)
TRANSCRIPT = TranscriptFile("C:/claude/projects/p/t.jsonl", datetime(2026, 11, 20, tzinfo=UTC))


@dataclass
class Left:
    """Declared remaining seconds, read at each call."""

    seconds: float

    def __call__(self) -> float:
        """Return the declared remaining seconds."""
        return self.seconds


@dataclass
class Recorder:
    """Every wrapped port at once, recording each call it receives."""

    calls: list[str] = field(default_factory=list[str])

    def capture(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Record the bounded capture."""
        self.calls.append(f"capture {pane.name} {timeout}")
        return ("captured",)

    def evidence(self, pane: PaneRecord) -> tuple[str, CodexPaneProfile] | None:
        """Record the version read."""
        self.calls.append(f"evidence {pane.name}")
        return ("0.167.2", PROFILE)

    def list_files(self) -> tuple[SessionFile, ...] | None:
        """Record the session listing."""
        self.calls.append("list")
        return (SESSION,)

    def read(self, path: str) -> bytes | None:
        """Record the read."""
        self.calls.append(f"read {path}")
        return b"{}"


@dataclass
class Transcripts:
    """Declared transcript source recording each call."""

    calls: list[str] = field(default_factory=list[str])

    def list_files(self) -> tuple[TranscriptFile, ...] | None:
        """Record the transcript listing."""
        self.calls.append("list")
        return (TRANSCRIPT,)

    def read(self, path: str) -> bytes | None:
        """Record the read."""
        self.calls.append(f"read {path}")
        return b"{}"


@pytest.mark.parametrize(("left", "bound"), [(45.0, 30.0), (12.5, 12.5), (0.2, 0.2)])
def test_a_capture_with_time_left_is_bounded_by_what_is_left(left: float, bound: float) -> None:
    """The bound is the time left at the moment of the capture, at most the call bound."""
    recorder = Recorder()
    assert BoundedCapture(recorder.capture, Left(left)).capture(PANE) == ("captured",)
    assert recorder.calls == [f"capture Codex api {bound}"]


def test_the_bound_is_read_at_each_call_not_when_the_reader_is_built() -> None:
    """A reader built with half a second left grants only what remains when it finally captures."""
    recorder, left = Recorder(), Left(0.5)
    capture = BoundedCapture(recorder.capture, left)
    left.seconds = 0.2
    capture.capture(PANE)
    assert recorder.calls == ["capture Codex api 0.2"]


@pytest.mark.parametrize("left", [0.0, -1.5])
def test_no_reader_reads_once_the_budget_is_spent(left: float) -> None:
    """Every wrapped reader reports its evidence unavailable and calls nothing."""
    recorder, transcripts = Recorder(), Transcripts()
    remaining = Left(left)
    store, source = BoundedSessionStore(recorder, remaining), BoundedTranscriptSource(transcripts, remaining)

    assert BoundedCapture(recorder.capture, remaining).capture(PANE) is None
    assert BoundedVersions(recorder, remaining).evidence(PANE) is None
    assert (store.list_files(), store.read(SESSION.path)) == (None, None)
    assert (source.list_files(), source.read(TRANSCRIPT.path)) == (None, None)
    assert (recorder.calls, transcripts.calls) == ([], [])


def test_every_reader_reads_while_time_is_left() -> None:
    """With time left, versions, sessions and transcripts are read unchanged."""
    recorder, transcripts = Recorder(), Transcripts()
    remaining = Left(1.0)
    store, source = BoundedSessionStore(recorder, remaining), BoundedTranscriptSource(transcripts, remaining)

    assert BoundedVersions(recorder, remaining).evidence(PANE) == ("0.167.2", PROFILE)
    assert (store.list_files(), store.read(SESSION.path)) == ((SESSION,), b"{}")
    assert (source.list_files(), source.read(TRANSCRIPT.path)) == ((TRANSCRIPT,), b"{}")
    assert recorder.calls == ["evidence Codex api", "list", f"read {SESSION.path}"]
    assert transcripts.calls == ["list", f"read {TRANSCRIPT.path}"]


# eof
