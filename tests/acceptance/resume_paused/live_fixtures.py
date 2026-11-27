"""Build guest-local pauses from the actual TUIOS panes selected by the layout."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from tests.acceptance.resume_paused.live_cases import DUAL_CASES, PAIR_CASES
from tests.unit.tools.resume_paused_receiver_test_support import PLAN, UMBRELLA
from tests.unit.tools.test_review_exchange_lifecycle.test_review_exchange_lifecycle_tdd import (
    _harness,
)
from tests.unit.tools.test_review_resume.prepared_phase import prepare_phase
from tools.resume_paused import SavedExchanges
from tools.resume_paused_artifacts import (
    PromptState,
    read_checkout_snapshot,
    render_routing_section,
)
from tools.resume_paused_input import PaneRecord, pane_host
from tools.resume_paused_models import PROMPT_NAME, RECEIPT_NAME, SessionRole
from tools.resume_paused_profiles import Host
from tools.resume_paused_review import ExchangeObservationKind
from tools.resume_paused_routing import RoutingTarget, SavedExchange, SavedRouting
from tools.resume_paused_takeover_proof import read_exchange
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ArtifactState, ReviewFamily

if TYPE_CHECKING:
    from tools.resume_paused_artifacts import CheckoutSnapshot


SESSIONS = {
    "rp-primary": ("alpha", "project", "primary"),
    "rp-peer": ("alpha", "codex", "peer"),
    "rp-secondary": ("bravo", "claude", "secondary"),
}
LABELS = {"Codex primary": "rp-primary", "Claude primary": "rp-primary", "Codex peer": "rp-peer", "Claude secondary": "rp-secondary"}


def inventory(lab: Path, panes: tuple[PaneRecord, ...]) -> dict[str, PaneRecord]:
    """Require every expected agent and reject extra agents, duplicate identities and foreign checkouts."""
    found: dict[str, PaneRecord] = {}
    for pane in panes:
        assert pane.session in SESSIONS, f"Foreign pane {pane.name}"
        assert Path(pane.cwd).resolve() == lab / SESSIONS[pane.session][0], f"Foreign pane {pane.name}"
        host = pane_host(pane)
        if host is None:
            assert pane.name == "CMD", f"Unrecognized pane {pane.name}"
            continue
        assert LABELS.get(pane.name) == pane.session, f"Unexpected agent {pane.name}"
        assert pane.name.split()[0].lower() == host.value, f"Unexpected agent {pane.name}"
        assert pane.name not in found, f"Duplicate {pane.name}"
        found[pane.name] = pane
    _check_inventory(found, panes)
    return found


def _check_inventory(found: dict[str, PaneRecord], panes: tuple[PaneRecord, ...]) -> None:
    assert found.keys() == LABELS.keys(), f"Agents still missing: {LABELS.keys() - found.keys()}"
    assert len({pane.pane_id for pane in panes}) == len(panes), "Ambiguous pane UUID"


def _identity(pane: PaneRecord) -> dict[str, object]:
    host = pane_host(pane)
    assert host is not None
    return {"host": host.value, "session": pane.session, "pane_id": pane.pane_id, "label": pane.name}


def _target(pane: PaneRecord, role: str) -> dict[str, object]:
    return _identity(pane) | {"checkout": pane.cwd, "agent_session_id": pane.agent_session_id, "role": role, "evidence": "live guest inventory"}


def _pause_metadata(root: Path, pane: PaneRecord, case: str) -> tuple[str, str]:
    now = datetime.now(UTC).astimezone().isoformat(timespec="seconds")
    author = "chatgpt" if pane_host(pane) is Host.CODEX else "claude"
    if case == "history":
        now = (datetime.now(UTC) - timedelta(minutes=1)).astimezone().isoformat(timespec="seconds")
        if root.name == "alpha":
            author = "gemini"
    return now, author


def _prompt(root: Path, home: Path, pane: PaneRecord, other: PaneRecord | None, case: str) -> str:
    role = SessionRole.REQUESTOR if other else SessionRole.IMPLEMENTATION
    now, author = _pause_metadata(root, pane, case)
    target = _target(pane, role.value)
    absent = {"not_applicable": "single agent"}
    routing = SavedRouting.from_mapping({
        "schema": "resume-paused-routing", "version": 1,
        "pause": {"checkout": str(root), "snapshot": now, "author": author, "session_role": role.value, "pane": _identity(pane)},
        "observation": {"observed_at": now, "assignment_source": "guest scenario", "evidence": "identified by session, root, label and host"},
        "targets": {"resumed": target, "requestor": target if other else absent, "reviewer": _target(other, "reviewer") if other else absent},
        "exchange": {"family": "code", "document": PLAN, "implementation_step": "3", "umbrella": UMBRELLA, "occurrence": 1, "round": 1} if other else absent,
    })
    section = () if case == "routes" and root.name == "alpha" else render_routing_section(routing)
    objective = (f"Continue the existing requestor workflow for step 3 of {PLAN}, occurrence 1, round 1. Await its answer."
                 if other else f"Reply with RP-ACK-{root.name} and stop.")
    return "\n".join((f"# {author}: Resume session: Guest {case} {root.name}", "", f"- Snapshot: {now}", f"- Session role: {role.value}",
                      f"- Project root: `{root}`", f"- Artifact home: `{home}`", "", "## Automatic resume routing", "", *section,
                      "", "## Objective and latest user direction", "", objective, ""))


def record_prior_resume(root: Path, journal: Path | None) -> None:
    """Seed a different resuming agent in the isolated guest journal without consuming the pause."""
    assert journal, "Guest journal location unknown"
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open("a", encoding="utf-8") as stream:
        stream.write(f"\n## Resume by chatgpt at {datetime.now(UTC).isoformat()} in `{root}`\n")


def prepare_review(root: Path) -> None:
    """Publish the guest review request before saving a native or seeded pause."""
    config = ReviewArtifactConfiguration.load(root)
    config.prepare_home()
    (config.home / "a.review-mode").write_text("wait_timeout_seconds=86400\n", encoding="utf-8")
    core, _, context, clock = _harness(root)
    clock.wall = datetime.now(UTC)
    prepare_phase(core, context, clock, "request")


def _check_pair(routing: SavedRouting, reviewer: PaneRecord) -> None:
    target = routing.reviewer
    assert isinstance(target, RoutingTarget)
    assert (target.pane_id, target.session, target.host, target.role) == (reviewer.pane_id, reviewer.session, Host.CLAUDE, SessionRole.REVIEWER)
    assert routing.exchange == SavedExchange(ReviewFamily.CODE, PLAN, "3", UMBRELLA, 1, 1), "Saved pause names a different exchange"


def _write_pause(root: Path, home: Path, pane: PaneRecord, other: PaneRecord | None, case: str) -> PaneRecord:
    assert not (home / PROMPT_NAME).exists(), "Fixture already has a pause or receipt"
    assert not (home / RECEIPT_NAME).exists(), "Fixture already has a pause or receipt"
    if other:
        prepare_review(root)
        if case == "hibernate":
            (root / "docs/plan.v0.1.0.lab-waiter.md").write_text("# Separate waiter fixture\n", encoding="utf-8")
    if case == "routes" and root.name == "bravo":
        pane = replace(pane, pane_id=str(uuid4()))
    (home / PROMPT_NAME).write_text(_prompt(root, home, pane, other, case), encoding="utf-8")
    return pane


def _check_saved_target(snapshot: CheckoutSnapshot, pane: PaneRecord, case: str) -> None:
    assert snapshot.routing
    assert snapshot.routing.routing
    resumed = snapshot.routing.routing.resumed
    assert isinstance(resumed, RoutingTarget)
    role = SessionRole.REQUESTOR if case in PAIR_CASES else SessionRole.IMPLEMENTATION
    assert (resumed.pane_id, resumed.session, resumed.role, resumed.host) == (
        pane.pane_id, pane.session, role, pane_host(pane),
    ), "Saved pause targets another pane or role"


def _check_review(snapshot: CheckoutSnapshot, reviewer: PaneRecord) -> None:
    assert snapshot.routing
    assert snapshot.routing.routing
    _check_pair(snapshot.routing.routing, reviewer)
    exchange = read_exchange(snapshot.root, snapshot, SavedExchanges(lambda: datetime.now(UTC))).exchange
    assert exchange, "Guest exchange missing"
    assert exchange.kind is ExchangeObservationKind.OBSERVED, exchange
    assert exchange.state is ArtifactState.REQUEST_PENDING, exchange


def _validate_pause(root: Path, home: Path, pane: PaneRecord, panes: dict[str, PaneRecord], case: str) -> str:
    snapshot = read_checkout_snapshot(root)
    assert snapshot.state is PromptState.UNUSED, f"Invalid fixture at {root}: {snapshot.diagnostic}"
    assert snapshot.prompt, f"Invalid fixture at {root}: {snapshot.diagnostic}"
    if case != "routes" or root.name != "alpha":
        _check_saved_target(snapshot, pane, case)
    if case == "damaged" and root.name == "alpha":
        (home / RECEIPT_NAME).write_bytes(b"intentionally malformed receipt\n")
    if case in PAIR_CASES:
        _check_review(snapshot, panes["Claude primary"])
    return snapshot.prompt.digest.value


def seed(lab: Path, case: str, panes: dict[str, PaneRecord]) -> dict[str, str]:
    """Create the pre-launch state once. Capture adopts the actual pauses produced by both hosts."""
    digests: dict[str, str] = {}
    for name in (("alpha", "bravo") if case in DUAL_CASES else ("alpha",)):
        root = lab / name
        config = ReviewArtifactConfiguration.load(root)
        config.prepare_home()
        home = config.home
        pane = panes["Codex primary" if case in PAIR_CASES else ("Codex peer" if name == "alpha" else "Claude secondary")]
        if case not in {"capture", "capture-pair"}:
            other = panes["Claude primary"] if case in PAIR_CASES else None
            pane = _write_pause(root, home, pane, other, case)
        digests[name] = _validate_pause(root, home, pane, panes, case)
    return digests


# eof
