"""Saved-routing schema tests: strict parsing, explicit unknowns and contradictions.

Step 2 of v0.14.0 resume-paused: the versioned routing object parses into typed
targets and one exact exchange, renders back to the same canonical JSON, keeps
an explicit unknown as an unresolved part without failing the pause, and
refuses contradictions between its parts. The builders here also serve the
artifact and observation tests of the same step.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from tools.resume_paused_models import ArtifactError, CanonicalRoot, SessionRole
from tools.resume_paused_profiles import Host
from tools.resume_paused_routing import (
    ROUTING_SCHEMA,
    NotApplicable,
    RoutingTarget,
    SavedExchange,
    SavedRouting,
    Unresolved,
)
from tools.review_exchange_models import ExchangeIdentity, ReviewFamily

if TYPE_CHECKING:
    from collections.abc import Callable

SNAPSHOT = "2026-11-17T17:37:18+01:00"
OBSERVED = "2026-11-17T17:36:00+01:00"
SESSION = "llm-shared_resume-paused"
REQUESTOR_PANE = "77e5f39c-0536-4cbb-a057-f4a1f5c715b0"
REVIEWER_PANE = "2fd92f30-1111-4222-8333-444455556666"
THIRD_PANE = "5b1c0d2e-3f40-4a5b-8c6d-7e8f90a1b2c3"
PLAN = "docs/v0.14.0/plan.v0.14.0.resume-paused.md"
ROOT = Path("C:\\work\\checkout")


def target(root: Path, role: str = "requestor", pane: str = REQUESTOR_PANE, host: str = "claude") -> dict[str, object]:
    """Return one full routing target object."""
    return {
        "role": role, "host": host, "session": SESSION, "pane_id": pane, "label": f"{role} | pane",
        "checkout": str(root), "agent_session_id": None, "evidence": f"{role} role from the exchange state",
    }


def routing_mapping(root: Path) -> dict[str, object]:
    """Return one valid paired-requestor routing object."""
    requestor = target(root)
    return {
        "schema": ROUTING_SCHEMA,
        "version": 1,
        "pause": {
            "checkout": str(root), "snapshot": SNAPSHOT, "author": "claude", "session_role": "requestor",
            "pane": {"host": "claude", "session": SESSION, "pane_id": REQUESTOR_PANE, "label": "requestor | pane"},
        },
        "observation": {"observed_at": OBSERVED, "assignment_source": "verified current assignment", "evidence": "own pane listing"},
        "targets": {"resumed": requestor, "requestor": dict(requestor), "reviewer": target(root, "reviewer", REVIEWER_PANE, "codex")},
        "exchange": {"family": "code", "document": PLAN, "implementation_step": "2", "umbrella": None, "occurrence": 1, "round": 1},
    }


def part(mapping: dict[str, object], key: str) -> dict[str, object]:
    """Return one nested mutable routing object."""
    return cast("dict[str, object]", mapping[key])


def slot(mapping: dict[str, object], name: str) -> dict[str, object]:
    """Return one mutable target slot of a routing mapping."""
    return part(part(mapping, "targets"), name)


def mutated(root: Path, change: Callable[[dict[str, object]], None]) -> dict[str, object]:
    """Return the valid routing object after one in-place change."""
    mapping = routing_mapping(root)
    change(mapping)
    return mapping


def single_agent(mapping: dict[str, object]) -> None:
    """Turn the pair into a single implementation pause with no exchange."""
    absent = {"not_applicable": "single-agent pause"}
    part(mapping, "targets").update(resumed={**slot(mapping, "resumed"), "role": "implementation"}, requestor=absent, reviewer=absent)
    mapping["exchange"] = absent


def test_valid_routing_parses_into_typed_parts_and_renders_back() -> None:
    """A complete pair parses into typed targets and renders the same canonical JSON."""
    mapping = routing_mapping(ROOT)
    routing = SavedRouting.from_mapping(mapping)
    resumed = routing.resumed
    assert isinstance(resumed, RoutingTarget)
    assert (resumed.role, resumed.host, resumed.pane_id, resumed.checkout) == (SessionRole.REQUESTOR, Host.CLAUDE, REQUESTOR_PANE, CanonicalRoot.from_path(ROOT))
    assert routing.exchange == SavedExchange(ReviewFamily.CODE, PLAN, "2", None, 1, 1)
    assert (routing.unresolved, routing.to_mapping()) == ((), mapping)


KEPT_ROUTINGS: list[tuple[Callable[[dict[str, object]], None], tuple[str, ...]]] = [
    (lambda m: part(m, "targets").update(resumed={"unknown": "no pane evidence"}), ("resumed target unknown: no pane evidence",)),
    (lambda m: part(m, "targets").update(reviewer={"unknown": "pane closed"}), ("reviewer target unknown: pane closed",)),
    (lambda m: m.update(exchange={"unknown": "no live exchange"}), ("review exchange unknown: no live exchange",)),
    (lambda m: part(m, "pause").update(pane={"unknown": "shared daemon"}), ()),
    (single_agent, ()),
    (lambda m: part(m, "targets").update(resumed={**slot(m, "requestor"), "role": "documentation", "pane_id": THIRD_PANE}), ()),
]


@pytest.mark.parametrize(("change", "reasons"), KEPT_ROUTINGS)
def test_unknown_and_not_applicable_parts_keep_the_routing(change: Callable[[dict[str, object]], None], reasons: tuple[str, ...]) -> None:
    """An explicit unknown stays unresolved; a single-agent pause needs no pair."""
    routing = SavedRouting.from_mapping(mutated(ROOT, change))
    assert routing.unresolved == reasons
    assert SavedRouting.from_mapping(routing.to_mapping()) == routing


def test_explicit_parts_keep_their_reasons() -> None:
    """Unknown and not-applicable parts carry the pauser's reason."""
    routing = SavedRouting.from_mapping(mutated(ROOT, single_agent))
    assert (routing.requestor, routing.exchange) == (NotApplicable("single-agent pause"), NotApplicable("single-agent pause"))
    unknown = SavedRouting.from_mapping(mutated(ROOT, lambda m: part(m, "pause").update(pane={"unknown": "shared daemon"})))
    assert unknown.pause.pane == Unresolved("shared daemon")


ROUTING_ERRORS: list[tuple[Callable[[dict[str, object]], None], str]] = [
    (lambda m: m.update(version=2), "unsupported routing schema or version"),
    (lambda m: m.update(version=True), "unsupported routing schema or version"),
    (lambda m: m.update(schema="other"), "unsupported routing schema or version"),
    (lambda m: m.update(extra=1), "unexpected extra"),
    (lambda m: m.update(pause=[]), "invalid routing pause: expected an object"),
    (lambda m: slot(m, "reviewer").update(colour="red"), "unexpected colour"),
    (lambda m: slot(m, "reviewer").update(role="captain"), "invalid reviewer target role: captain"),
    (lambda m: slot(m, "reviewer").update(host=7), "invalid reviewer target host: expected a string"),
    (lambda m: part(m, "targets").update(resumed={"not_applicable": "x"}), "invalid resumed target"),
    (lambda m: part(m, "pause").update(pane={"not_applicable": "x"}), "invalid pausing pane"),
    (lambda m: part(m, "exchange").update(occurrence=True), "invalid exchange occurrence"),
    (lambda m: part(m, "exchange").update(umbrella="../draft.md"), "invalid exchange umbrella"),
    (lambda m: m.update(exchange={"not_applicable": "single agent"}), "pair contradicts its exchange"),
    (lambda m: part(m, "targets").update(requestor={"not_applicable": "x"}), "pair contradicts its exchange"),
    (lambda m: slot(m, "reviewer").update(role="requestor"), "reviewer slot names a requestor target"),
    (lambda m: slot(m, "reviewer").update(checkout="C:\\other"), "contradicts the pause checkout"),
    (lambda m: slot(m, "reviewer").update(pane_id=REQUESTOR_PANE), "one pane to different targets"),
    (lambda m: slot(m, "requestor").update(pane_id=REVIEWER_PANE.replace("2fd9", "3fd9")), "resumed target contradicts its pair slot"),
]


@pytest.mark.parametrize(("change", "diagnostic"), ROUTING_ERRORS)
def test_malformed_or_contradictory_routing_is_refused(change: Callable[[dict[str, object]], None], diagnostic: str) -> None:
    """Malformed records and contradictions between routing parts are parse errors."""
    with pytest.raises(ArtifactError, match=diagnostic):
        SavedRouting.from_mapping(mutated(ROOT, change))


@pytest.mark.parametrize(
    ("exchange", "identity"),
    [
        (SavedExchange(ReviewFamily.CODE, PLAN, "2", None, 1, 1), ExchangeIdentity(ReviewFamily.CODE, "code", "v0.14.0", "resume-paused")),
        (SavedExchange(ReviewFamily.SPECIFICATION, "docs/design.v0.14.0.x.md", None, "docs/draft.md", 2, None), ExchangeIdentity(ReviewFamily.SPECIFICATION, "design-specification", "v0.14.0", "x")),
    ],
)
def test_saved_exchange_derives_its_identity(exchange: SavedExchange, identity: ExchangeIdentity) -> None:
    """The reviewed document names the complete exchange identity."""
    assert exchange.identity() == identity
    assert SavedExchange.from_mapping(exchange.to_mapping()) == exchange


@pytest.mark.parametrize(
    ("document", "family", "step", "occurrence"),
    [
        ("docs/design.v0.14.0.x.md", ReviewFamily.CODE, "2", 1),
        (PLAN, ReviewFamily.CODE, None, 1),
        (PLAN, ReviewFamily.CODE, "2 b", 1),
        (PLAN, ReviewFamily.SPECIFICATION, "2", 1),
        ("docs/../plan.v0.14.0.x.md", ReviewFamily.CODE, "2", 1),
        ("/docs/plan.v0.14.0.x.md", ReviewFamily.CODE, "2", 1),
        ("docs/notes.md", ReviewFamily.SPECIFICATION, None, 1),
        (PLAN, ReviewFamily.CODE, "2", 0),
    ],
)
def test_saved_exchange_rejects_inexact_selections(document: str, family: ReviewFamily, step: str | None, occurrence: int) -> None:
    """A wrong document type, step, path or occurrence names no exact exchange."""
    with pytest.raises(ArtifactError):
        SavedExchange(family, document, step, None, occurrence, None)


def test_saved_exchange_rejects_a_zero_round() -> None:
    """A recorded round at pause, when present, is a positive round number."""
    with pytest.raises(ArtifactError, match="invalid exchange round"):
        SavedExchange(ReviewFamily.CODE, PLAN, "2", None, 1, 0)


# eof
