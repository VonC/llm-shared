"""Validate a live command against its declared rows and independent receiver artifacts."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from tests.acceptance.resume_paused.live_cases import PAIR_CASES, Row
from tools.resume_paused import SavedExchanges
from tools.resume_paused_artifacts import read_checkout_snapshot
from tools.resume_paused_delivery_model import Phase
from tools.resume_paused_dispatch import read_dispatch
from tools.resume_paused_evidence import read_session_journal
from tools.resume_paused_input import pane_host
from tools.resume_paused_marker import (
    LiveExchange,
    marker_in_command,
    resolve_assignment,
)
from tools.resume_paused_models import CanonicalRoot, SessionRole
from tools.resume_paused_takeover_proof import (
    ProofState,
    consumption,
    read_exchange,
    takeover,
)
from tools.resume_paused_terminal import COMMANDS
from tools.review_artifact_configuration import ReviewArtifactConfiguration

if TYPE_CHECKING:
    from pathlib import Path

    from tests.acceptance.resume_paused.live_cases import Step
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_marker import Marker
    from tools.resume_paused_profiles import Host
    from tools.resume_paused_takeover_proof import Durable


@dataclass(frozen=True)
class Observation:
    """Hashes, scoped journal entries and phase names. Raw conversations and ownership tokens stay in the guest."""

    files: dict[str, str]
    phases: dict[str, str]
    resumes: list[str]


def observe(root: Path, journal: Path) -> Observation:
    """Record every private artifact by digest, including malformed receipts."""
    home = ReviewArtifactConfiguration.load(root).home
    files = {p.relative_to(home).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in home.rglob("*") if p.is_file()}
    phases = {name: digest for name, digest in files.items() if re.fullmatch(r"a\.resume-paused\.[a-f0-9]{64}\.\w+\.local\.json", name)}
    entries = read_session_journal(journal).resumes(CanonicalRoot.from_path(root))
    assert entries is not None, "Guest journal unreadable"
    return Observation(files, phases, [f"{entry.agent} {entry.at.isoformat()}" for entry in entries])


def _matches(line: str, row: Row) -> bool:
    # A pause title is user text. Only match evidence in the verdict and actions.
    _, _, body = line.partition(": ")
    if "; " in body and row.status != "REFUSED":
        body = body.partition("; ")[2]
    return line.startswith(row.status + " ") and all(word in body for word in row.words)


def _report_lines(output: str, rows: dict[str, Row]) -> dict[str, str]:
    seen: dict[str, str] = {}
    for line in output.splitlines():
        match = re.match(r"^(?:REFUSED|PLAN|DONE|PENDING|SKIP|ERROR|FAIL) (.+?): ", line)
        if not match:
            assert not line.startswith(("REFUSED ", "PLAN ", "DONE ", "PENDING ", "SKIP ", "ERROR ", "FAIL ")), f"Malformed report: {line}"
            continue
        name = match[1]
        assert name in rows, f"Unexpected report: {line}"
        assert name not in seen, f"Unexpected report: {line}"
        seen[name] = line
    assert seen.keys() == rows.keys(), f"Missing checkout reports: {rows.keys() - seen.keys()}"
    return seen


def _check_concurrent_skip(step: Step, row: Row, line: str) -> None:
    assert step.concurrent, f"Expected {row}, received {line}"
    assert line.startswith("SKIP ")
    assert any(s in line for s in ("guard held", "already-resuming", "already-used")), f"Unexpected concurrent result: {line}"


def check_reports(step: Step, results: list[tuple[int, str]]) -> None:
    """Every launch must report exactly its expected roots, with only one winner per concurrent checkout."""
    assert len(results) == (2 if step.concurrent else 1)
    rows = {"run" if step.alpha.status == "REFUSED" else "alpha": step.alpha}
    if step.bravo:
        rows["bravo"] = step.bravo
    winners = dict.fromkeys(rows, 0)
    for code, output in results:
        assert code == step.code, f"Unexpected exit {code}; expected {step.code}"
        for name, line in _report_lines(output, rows).items():
            if _matches(line, rows[name]):
                winners[name] += 1
            else:
                _check_concurrent_skip(step, rows[name], line)
    assert all(count == 1 for count in winners.values()), f"Expected one matching report per root: {winners}"


def _check_journal(before: list[str], after: list[str], row: Row, agent: str) -> None:
    consumed = "resume" in row.phases and row.status != "FAIL"
    assert after[:len(before)] == before, "Earlier journal entries changed"
    new_entries = after[len(before):]
    assert len(new_entries) == int(consumed), "Unexpected number of guest journal resumes"
    if consumed:
        assert new_entries[0].split()[0] == agent, "Journal names a different resuming agent"


def check_delta(before: Observation, after: Observation, row: Row, agent: str) -> None:
    """Reject extra sends, mutated reservations, missing journal entries and changes to skipped roots."""
    added = sorted(name.split(".")[-3] for name in after.phases.keys() - before.phases.keys())
    assert added == sorted(row.phases), f"New dispatch phases {added}; expected {row.phases}"
    assert all(after.phases.get(key) == value for key, value in before.phases.items()), "A prior reservation changed"
    _check_journal(before.resumes, after.resumes, row, agent)
    if not row.phases:
        assert before.files == after.files, "A protected checkout changed"


def _reviewer_claim(durable: Durable, marker: Marker, host: Host, generation: int | None) -> None:
    exchange = durable.exchange
    assert exchange
    assert exchange.marked_claim
    assert exchange.owner
    assert exchange.owner.value == "reviewer"
    binding = exchange.marked_claim
    claim = binding.evidence
    assert (binding.issued_generation, claim.launch_id, claim.assignment_binding, claim.pane_id, claim.host, claim.round_number, claim.occurrence) == (
        exchange.ownership_generation, marker.launch_id, marker.binding, marker.pane_id, host.value, 1, 1,
    ), "Wrong reviewer generation, exchange or receiver"
    assert generation is not None
    assert binding.issued_generation == generation + 1, "Claim did not follow the reserved generation"


def _target(case: str, root: Path, phase: Phase) -> tuple[str, SessionRole]:
    if case not in PAIR_CASES:
        return ("Codex peer" if root.name == "alpha" else "Claude secondary"), SessionRole.IMPLEMENTATION
    if phase is Phase.REVIEWER:
        return ("Codex primary" if case == "switch" else "Claude primary"), SessionRole.REVIEWER
    return ("Claude primary" if case == "switch" else "Codex primary"), SessionRole.REQUESTOR


def _reserved(durable: Durable, phase: Phase, pane: PaneRecord, role: SessionRole, host: Host) -> tuple[Marker, int | None]:
    record = read_dispatch(durable.snapshot, phase)
    assert record, f"Missing {phase} reservation"
    marker = marker_in_command(record.command)
    live = None if role is SessionRole.IMPLEMENTATION else LiveExchange(1, 1)
    assert durable.routing
    assert durable.snapshot.prompt
    assignment = resolve_assignment(durable.routing, durable.snapshot.prompt.digest, pane.pane_id, role, live)
    assert (marker.pane_id, marker.role, marker.binding) == (pane.pane_id, role, assignment.digest()), "Wrong receiving pane, role or binding"
    native = COMMANDS[host].reviewer if phase is Phase.REVIEWER else COMMANDS[host].resume
    assert record.command.split()[0] == native
    return marker, record.generation


def _check_phase(durable: Durable, phase: Phase, pane: PaneRecord, role: SessionRole, row: Row) -> None:
    host = pane_host(pane)
    assert host
    marker, generation = _reserved(durable, phase, pane, role, host)
    if row.status == "FAIL":
        assert durable.snapshot.receipt is None, "Supposedly stalled launch consumed the prompt"
    elif phase is Phase.REVIEWER:
        _reviewer_claim(durable, marker, host, generation)
    elif phase is Phase.RESUME:
        _check_consumed(durable, marker, host, row)


def _check_consumed(durable: Durable, marker: Marker, host: Host, row: Row) -> None:
    assert durable.snapshot.prompt
    assert consumption(durable, marker, host, durable.snapshot.prompt.digest).state is ProofState.PROVED, "Matching schema 3 receipt missing"
    if marker.role is SessionRole.REQUESTOR and "reviewer" not in row.phases:
        assert takeover(durable, marker, host).state is ProofState.PROVED, "Requestor did not claim the exchange"


def check_receiver(root: Path, case: str, digest: str, row: Row, panes: dict[str, PaneRecord]) -> None:
    """Verify each reserved command, receipt and claim against the expected guest pane and saved digest."""
    if not row.phases:
        return
    snapshot = read_checkout_snapshot(root)
    assert snapshot.prompt, "Saved pause changed"
    assert snapshot.prompt.digest.value == digest, "Saved pause changed"
    durable = read_exchange(snapshot.root, snapshot, SavedExchanges(lambda: datetime.now(UTC)))
    for phase_name in row.phases:
        phase = Phase(phase_name)
        label, role = _target(case, root, phase)
        _check_phase(durable, phase, panes[label], role, row)


# eof
