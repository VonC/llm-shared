"""Example tests of the shell-free TUIOS transport of resume-paused.

Step 6 of v0.14.0 resume-paused: the ask and the recovery Enter are exact
argument lists, the marked command stays one inert argument after ``--``,
spaces in live names become the documented ``*`` wildcard, and the selector
must resolve to exactly the validated pane UUID among every listed pane. No
process starts: the runners are declared. Code review round 1: every call
runs on a runner bounded by the seconds its caller grants.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pytest

from tools.resume_paused_input import PaneRecord
from tools.resume_paused_profiles import CommandResult
from tools.resume_paused_transport import (
    ASK_TIMEOUT_MS,
    STALL_TIMEOUT_MS,
    AskOutcome,
    Selection,
    TuiosTransport,
    ask_arguments,
    enter_arguments,
    resolve_selector,
    selector_value,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

TARGET = "77e5f39c-0536-4cbb-a057-f4a1f5c715b0"
OTHER = "2fd92f30-1111-4222-8333-444455556666"
SESSION = "llm-shared_resume-paused"
METACHARACTERS = '/resume-session --resume-paused x & del * | "q" ^%PATH%! > out; $(id) `id`'


def pane(pane_id: str = TARGET, name: str = "Claude api", session: str = SESSION) -> PaneRecord:
    """Declare one live record."""
    return PaneRecord(pane_id, session, name, "C:\\work\\api", "claude-code", (), None)


@dataclass
class FakeRunner:
    """Declared command results, recording every argument list."""

    result: CommandResult = field(default_factory=lambda: CommandResult(0, ""))
    calls: list[tuple[str, ...]] = field(default_factory=list[tuple[str, ...]])

    def run(self, arguments: Sequence[str]) -> CommandResult:
        """Record the call and return the declared result."""
        self.calls.append(tuple(arguments))
        return self.result


def test_ask_arguments_are_the_proven_selector_form_with_the_command_last() -> None:
    """The flags are fixed and the command follows ``--`` as one unchanged argument."""
    arguments = ask_arguments("session:S name:Claude*api", METACHARACTERS)

    assert arguments == (
        "tuios", "ask-agent", "--select", "session:S name:Claude*api", "--yes",
        "--stall-timeout", "60000", "--timeout", "100000", "--lines", "1", "--json", "--", METACHARACTERS,
    )
    assert (STALL_TIMEOUT_MS, ASK_TIMEOUT_MS) == (60_000, 100_000)


def test_enter_arguments_target_the_full_pane_uuid() -> None:
    """The recovery Enter names the session and the full UUID, never a label."""
    assert enter_arguments(SESSION, TARGET) == ("tuios", "send-keys", "-s", SESSION, "-w", TARGET, "Enter")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Claude api", "Claude*api"),
        (SESSION, SESSION),
        ("requestor | pane", "requestor*|*pane"),
        ("api/Claude", "api/Claude"),
        ("Café  ü", "Café**ü"),
        ("", None),
        ("a*b", None),
        ("a?b", None),
        ("a[b]", None),
        ("a\\b", None),
        ("a\tb", None),
        ("a\nb", None),
        ("a\u00a0b", None),
        ("bell\x07", None),
    ],
)
def test_selector_values_wildcard_spaces_and_refuse_every_other_glob_or_blank(text: str, expected: str | None) -> None:
    """Only a plain space has a documented wildcard; a name with another glob character has no exact glob."""
    assert selector_value(text) == expected


def test_a_unique_target_resolves_to_its_live_session_and_name() -> None:
    """Other sessions and other names do not collide."""
    panes = (pane(), pane(OTHER, "Claude web"), pane("5b1c0d2e-3f40-4a5b-8c6d-7e8f90a1b2c3", "Claude api", "other"))

    assert resolve_selector(panes, pane()) == Selection(f"session:{SESSION} name:Claude*api")


@pytest.mark.parametrize(
    ("listed", "reason"),
    [
        ((pane(), pane(OTHER, "Claude-big-api")), "selector-ambiguous"),
        ((pane(), pane(OTHER, "claude API")), "selector-ambiguous"),
        ((pane(), pane(OTHER, "Claudeapi")), "selector-ambiguous"),
        ((pane(), pane()), "selector-ambiguous"),
        ((pane(OTHER, "Claude web"),), "selector-unresolved"),
    ],
)
def test_wildcard_collisions_and_an_unlisted_target_refuse_the_selector(listed: tuple[PaneRecord, ...], reason: str) -> None:
    """Any second pane the wildcard could reach, in any letter case, is an error before input."""
    assert resolve_selector(listed, pane()) == Selection(None, reason)


def test_a_session_name_with_a_space_is_wildcarded_too() -> None:
    """Both selector terms use the wildcard form."""
    target = pane(session="my session")

    assert resolve_selector((target, pane(OTHER, session="my-session")), target).reason == "selector-ambiguous"
    assert resolve_selector((target,), target).selector == "session:my*session name:Claude*api"


def test_a_target_name_without_an_exact_glob_is_unsupported() -> None:
    """A glob character in the live name refuses the selector."""
    target = pane(name="Claude*")

    assert resolve_selector((target,), target) == Selection(None, "selector-unsupported")


@dataclass
class RunnerFactory:
    """Hand out the declared runner for every bound, recording each bound granted."""

    runner: FakeRunner
    bounds: list[float] = field(default_factory=list[float])

    def __call__(self, timeout: float) -> FakeRunner:
        """Record the bound and return the declared runner."""
        self.bounds.append(timeout)
        return self.runner


def test_transport_runs_discovery_capture_and_enter_within_the_granted_bounds() -> None:
    """Discovery, capture and the Enter are argument lists, each on a runner bounded as the caller grants."""
    listing = {"agents": [{"window_id": TARGET, "session": SESSION, "name": "Claude api", "cwd": "C:\\work\\api", "state": "idle", "ready": True}]}
    factory = RunnerFactory(FakeRunner(CommandResult(0, json.dumps(listing))))
    transport = TuiosTransport(factory)

    observation = transport.observe(30.0)
    captured = transport.capture(pane(), 12.5)
    entered = transport.enter(SESSION, TARGET, 7.0)

    assert transport.select((pane(), pane(OTHER, "Claude-api")), pane()) == Selection(None, "selector-ambiguous")
    assert observation is not None
    assert [record.pane_id for record in observation.panes] == [TARGET]
    assert captured == (json.dumps(listing),)
    assert entered is True
    assert factory.runner.calls == [
        ("tuios", "list-agents", "--all-sessions", "--json"),
        ("tuios", "capture-pane", "-s", SESSION, "-w", TARGET, "--unwrap", "--trim"),
        ("tuios", "send-keys", "-s", SESSION, "-w", TARGET, "Enter"),
    ]
    assert factory.bounds == [30.0, 12.5, 7.0]


def test_transport_asks_within_the_granted_bound_and_reports_only_its_exit_code() -> None:
    """The ask runs on a runner bounded by the send's budget; its exit code is report-only, a refused Enter is not sent."""
    factory = RunnerFactory(FakeRunner(CommandResult(3, '{"ok": true}')))
    transport = TuiosTransport(factory)

    assert transport.ask("session:S name:N", METACHARACTERS, 100.0) == AskOutcome(3)
    assert transport.enter(SESSION, TARGET, 5.0) is False
    assert factory.runner.calls[0] == ask_arguments("session:S name:N", METACHARACTERS)
    assert factory.bounds == [100.0, 5.0]


# eof
