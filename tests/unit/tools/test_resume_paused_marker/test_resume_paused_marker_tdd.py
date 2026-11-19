"""Marker grammar, assignment binding and compact result tests.

Step 4 of v0.14.0 resume-paused: a marked resume command carries one compact
versioned marker, launch id first, then the receiving pane UUID, its resolved
role and the SHA-256 of the canonical UTF-8 JSON assignment. The receiver
rebuilds that assignment from its prompt digest, saved routing, its own pane
and role, and the live exchange round and occurrence; any change moves the
digest. A pair pane given the opposite pair role is a swap, allowed only for
a saved requestor pause. The compact result names the launch id, the outcome
and an optional claim generation in at most 100 characters.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    SESSION,
    THIRD_PANE,
    mutated,
    part,
    routing_mapping,
    single_agent,
)
from tools.resume_paused_marker import (
    MARKER_FLAG,
    RESULT_LIMIT,
    AssignedPane,
    LiveExchange,
    Marker,
    ResultLine,
    marker_in_command,
    new_launch_id,
    resolve_assignment,
)
from tools.resume_paused_models import (
    LAUNCH_ID_RE,
    ArtifactError,
    CanonicalRoot,
    PromptDigest,
    SessionRole,
)
from tools.resume_paused_profiles import Host
from tools.resume_paused_routing import SavedRouting

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT = Path("C:\\work\\checkout")
LAUNCH = "0123456789abcdef0123456789abcdef"
BINDING = "a" * 64
PROMPT = PromptDigest("b" * 64)
LIVE = LiveExchange(occurrence=1, round_number=3)


def marker_text(launch: str = LAUNCH, version: str = "rp1", pane: str = REQUESTOR_PANE, role: str = "requestor", binding: str = BINDING) -> str:
    """Join the five marker fields."""
    return f"{launch}.{version}.{pane}.{role}.{binding}"


def routing(change: Callable[[dict[str, object]], None] | None = None) -> SavedRouting:
    """Return the Step 2 paired routing, optionally changed."""
    return SavedRouting.from_mapping(mutated(ROOT, change) if change else routing_mapping(ROOT))


def test_marker_renders_launch_id_first_and_parses_back() -> None:
    """The launch id leads, then the version, pane, role and binding."""
    marker = Marker(LAUNCH, REQUESTOR_PANE, SessionRole.REQUESTOR, BINDING)
    assert marker.render() == marker_text()
    assert marker.render().startswith(LAUNCH)
    assert Marker.parse(marker_text()) == marker


@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("", "marker-malformed"),
        (marker_text(launch=LAUNCH.upper()), "marker-malformed"),
        (marker_text(launch=LAUNCH[:-1]), "marker-malformed"),
        (marker_text(version="rp2"), "marker-version-unsupported"),
        (marker_text(pane=REQUESTOR_PANE.upper()), "marker-malformed"),
        (marker_text(pane=REQUESTOR_PANE[:-1]), "marker-malformed"),
        (marker_text(role="owner"), "marker-malformed"),
        (marker_text(role="r\N{LATIN SMALL LETTER E WITH ACUTE}viewer"), "marker-malformed"),
        (marker_text(binding=BINDING[:-1]), "marker-malformed"),
        (f" {marker_text()}", "marker-malformed"),
        (f"{marker_text()} ", "marker-malformed"),
        (f"{marker_text()}.extra", "marker-too-long"),
        (f"{LAUNCH}.rp1.{REQUESTOR_PANE}.{BINDING}", "marker-malformed"),
    ],
    ids=[
        "empty", "upper launch", "short launch", "other version", "upper pane", "short pane", "unknown role",
        "non-ascii role", "short binding", "leading space", "trailing space", "extra field", "missing role",
    ],
)
def test_marker_refuses_malformed_text(text: str, code: str) -> None:
    """Unknown versions, wrong lengths, spellings and fields are refused, never repaired."""
    with pytest.raises(ArtifactError, match=rf"^{code}$"):
        Marker.parse(text)


def test_command_holds_exactly_one_marker_after_its_flag() -> None:
    """The marker is the whole token following the single marker flag."""
    assert marker_in_command(f"/resume-session {MARKER_FLAG} {marker_text()}") == Marker.parse(marker_text())


@pytest.mark.parametrize(
    "command",
    [
        "/resume-session",
        f"/resume-session {MARKER_FLAG}",
        f"/resume-session {MARKER_FLAG} {marker_text()} {MARKER_FLAG} {marker_text()}",
        f"/resume-session {MARKER_FLAG}={marker_text()}",
        f"/resume-session {MARKER_FLAG} {marker_text()}x",
        f"/resume-session {marker_text()}",
    ],
    ids=["no flag", "no marker", "two flags", "glued value", "longer token", "marker without flag"],
)
def test_command_without_exactly_one_marker_is_refused(command: str) -> None:
    """A missing, repeated, glued or extended marker grants nothing."""
    with pytest.raises(ArtifactError, match=r"^marker-"):
        marker_in_command(command)


def test_assignment_json_is_canonical_utf8_and_hashed() -> None:
    """Sorted keys, compact separators and UTF-8 text give one digest."""
    resolved = resolve_assignment(routing(_accented), PROMPT, REQUESTOR_PANE, SessionRole.REQUESTOR, LIVE)
    data = resolved.canonical_json()
    assert data == json.dumps(resolved.to_mapping(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    assert "\N{LATIN SMALL LETTER E WITH ACUTE}quipe".encode() in data
    assert data.startswith(b'{"checkout":')
    assert resolved.digest() == hashlib.sha256(data).hexdigest()


def _rename_session(mapping: dict[str, object], session: str) -> None:
    """Give every routed target one TUIOS session name."""
    for name in ("resumed", "requestor", "reviewer"):
        part(part(mapping, "targets"), name)["session"] = session


def _accented(mapping: dict[str, object]) -> None:
    """Name the TUIOS session with a non-ASCII letter."""
    _rename_session(mapping, "\N{LATIN SMALL LETTER E WITH ACUTE}quipe")


def _unknown_reviewer(mapping: dict[str, object]) -> None:
    """Record the reviewer target as unknown."""
    part(mapping, "targets").update(reviewer={"unknown": "closed"})


def test_assignment_binds_every_field() -> None:
    """Changing the prompt, pane, role, round, occurrence or checkout changes the digest."""
    base = resolve_assignment(routing(), PROMPT, REQUESTOR_PANE, SessionRole.REQUESTOR, LIVE).digest()
    variants = [
        resolve_assignment(routing(), PromptDigest("c" * 64), REQUESTOR_PANE, SessionRole.REQUESTOR, LIVE),
        resolve_assignment(routing(), PROMPT, REVIEWER_PANE, SessionRole.REVIEWER, LIVE),
        resolve_assignment(routing(), PROMPT, REQUESTOR_PANE, SessionRole.REVIEWER, LIVE),
        resolve_assignment(routing(), PROMPT, REQUESTOR_PANE, SessionRole.REQUESTOR, LiveExchange(1, 4)),
        resolve_assignment(routing(), PROMPT, REQUESTOR_PANE, SessionRole.REQUESTOR, LiveExchange(2, 3)),
    ]
    other_root = Path("C:\\work\\other")
    moved = SavedRouting.from_mapping(routing_mapping(other_root))
    variants.append(resolve_assignment(moved, PROMPT, REQUESTOR_PANE, SessionRole.REQUESTOR, LIVE))
    assert len({base, *(variant.digest() for variant in variants)}) == len(variants) + 1


def test_single_agent_assignment_has_no_pair_or_exchange() -> None:
    """A single implementation pause binds its own pane and role only."""
    resolved = resolve_assignment(routing(single_agent), PROMPT, REQUESTOR_PANE, SessionRole.IMPLEMENTATION, None)
    assert (resolved.pair, resolved.exchange, resolved.role) == (None, None, SessionRole.IMPLEMENTATION)
    assert resolved.receiver == AssignedPane(Host.CLAUDE, SESSION, REQUESTOR_PANE)
    assert resolved.to_mapping()["pair"] is None


@pytest.mark.parametrize(
    ("pane", "role", "host", "swapped"),
    [
        (REQUESTOR_PANE, SessionRole.REQUESTOR, Host.CLAUDE, False),
        (REVIEWER_PANE, SessionRole.REVIEWER, Host.CODEX, False),
        (REQUESTOR_PANE, SessionRole.REVIEWER, Host.CLAUDE, True),
        (REVIEWER_PANE, SessionRole.REQUESTOR, Host.CODEX, True),
    ],
    ids=["requestor", "reviewer", "requestor pane swapped", "reviewer pane swapped"],
)
def test_pair_assignment_follows_the_marker_role(pane: str, role: SessionRole, host: Host, swapped: bool) -> None:  # noqa: FBT001
    """The pair keeps its saved order unless the marker gives a pair pane the other role."""
    resolved = resolve_assignment(routing(), PROMPT, pane, role, LIVE)
    requestor = AssignedPane(Host.CLAUDE, SESSION, REQUESTOR_PANE)
    reviewer = AssignedPane(Host.CODEX, SESSION, REVIEWER_PANE)
    assert resolved.receiver.host is host
    assert resolved.pair == ((reviewer, requestor) if swapped else (requestor, reviewer))
    assert resolved.exchange is not None
    assert (resolved.exchange.occurrence, resolved.exchange.round_number) == (1, 3)


def _reviewer_pause(mapping: dict[str, object]) -> None:
    """Record the pause as the reviewer's."""
    part(mapping, "pause")["session_role"] = "reviewer"
    part(mapping, "targets")["resumed"] = dict(part(part(mapping, "targets"), "reviewer"))


@pytest.mark.parametrize(
    ("change", "pane", "role", "live", "code"),
    [
        (None, THIRD_PANE, SessionRole.REQUESTOR, LIVE, "marker-pane-not-routed"),
        (single_agent, REQUESTOR_PANE, SessionRole.REQUESTOR, None, "marker-role-mismatch"),
        (None, REQUESTOR_PANE, SessionRole.IMPLEMENTATION, LIVE, "marker-role-mismatch"),
        (_reviewer_pause, REVIEWER_PANE, SessionRole.REQUESTOR, LIVE, "marker-switch-not-applicable"),
        (_unknown_reviewer, REQUESTOR_PANE, SessionRole.REQUESTOR, LIVE, "routing-unresolved"),
        (None, REQUESTOR_PANE, SessionRole.REQUESTOR, None, "exchange-not-observed"),
        (single_agent, REQUESTOR_PANE, SessionRole.IMPLEMENTATION, LIVE, "exchange-not-applicable"),
    ],
    ids=["unrouted pane", "single role mismatch", "pair role mismatch", "swap on reviewer pause", "unresolved", "no live exchange", "live exchange for single"],
)
def test_assignment_refuses_what_routing_does_not_bind(
    change: Callable[[dict[str, object]], None] | None, pane: str, role: SessionRole, live: LiveExchange | None, code: str,
) -> None:
    """Unrouted panes, wrong roles, illegal swaps and missing evidence never resolve."""
    with pytest.raises(ArtifactError, match=rf"^{code}$"):
        resolve_assignment(routing(change), PROMPT, pane, role, live)


def test_assignment_checkout_uses_the_canonical_key() -> None:
    """Separator and case spellings of one checkout bind the same digest."""
    spelled = SavedRouting.from_mapping(routing_mapping(Path("c:/WORK/checkout/")))
    plain = resolve_assignment(routing(), PROMPT, REQUESTOR_PANE, SessionRole.REQUESTOR, LIVE)
    assert resolve_assignment(spelled, PROMPT, REQUESTOR_PANE, SessionRole.REQUESTOR, LIVE).digest() == plain.digest()
    assert plain.to_mapping()["checkout"] == CanonicalRoot.from_path(ROOT).key


def test_result_line_names_launch_outcome_and_generation() -> None:
    """The compact result is short, non-secret and parses back."""
    line = ResultLine(LAUNCH, "claimed", 7).render()
    assert line == f"resume-paused {LAUNCH} claimed g7"
    assert ResultLine.parse(line) == ResultLine(LAUNCH, "claimed", 7)
    assert ResultLine.parse(ResultLine(LAUNCH, "resumed").render()) == ResultLine(LAUNCH, "resumed")
    longest = ResultLine(LAUNCH, "f" * 32, 9_999_999_999).render()
    assert len(longest) <= RESULT_LIMIT


@pytest.mark.parametrize(
    "line",
    [
        f"resume-paused {LAUNCH} Claimed",
        f"resume-paused {LAUNCH} {'f' * 33}",
        f"resume-paused {LAUNCH} claimed g0",
        f"resume-paused {LAUNCH} claimed g12345678901",
        f"resume-paused {LAUNCH[:-1]} claimed",
        f"resume-paused {LAUNCH} claimed g7 t-secret",
        f"resume {LAUNCH} claimed",
    ],
    ids=["upper outcome", "long outcome", "zero generation", "long generation", "short launch", "extra field", "other prefix"],
)
def test_result_line_refuses_other_shapes(line: str) -> None:
    """Anything beyond launch id, outcome and generation is not a result line."""
    with pytest.raises(ArtifactError, match=r"^result-malformed$"):
        ResultLine.parse(line)


def test_result_line_refuses_to_render_a_bad_outcome() -> None:
    """Rendering validates the same grammar the parser enforces."""
    with pytest.raises(ArtifactError, match=r"^result-malformed$"):
        ResultLine(LAUNCH, "two words").render()


@pytest.mark.parametrize(("occurrence", "round_number"), [(0, 1), (1, 0)], ids=["zero occurrence", "zero round"])
def test_live_exchange_needs_a_positive_occurrence_and_round(occurrence: int, round_number: int) -> None:
    """A live exchange without a positive occurrence and round was not observed."""
    with pytest.raises(ArtifactError, match=r"^exchange-not-observed$"):
        LiveExchange(occurrence, round_number)


def test_new_launch_ids_are_fresh_lowercase_hex() -> None:
    """Each launch draws a new 128-bit identifier."""
    first, second = new_launch_id(), new_launch_id()
    assert LAUNCH_ID_RE.fullmatch(first)
    assert first != second


# eof
