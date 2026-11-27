"""Run one acceptance story through the installed tuitp and production resume_paused wrappers in a disposable Windows VM."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, TypedDict

from tests.acceptance.resume_paused.live_cases import CASES, OBSERVATIONS, Row, Step
from tests.acceptance.resume_paused.live_checks import (
    Observation,
    check_delta,
    check_receiver,
    check_reports,
    observe,
)
from tests.acceptance.resume_paused.live_faults import run_fault
from tests.acceptance.resume_paused.live_fixtures import (
    inventory,
    prepare_review,
    record_prior_resume,
    seed,
)
from tests.acceptance.resume_paused.live_guest import (
    REPO,
    check_namespace,
    executable,
    guest,
    layout,
    run,
)
from tests.acceptance.resume_paused.live_power import check_power, start_waiter
from tools.resume_paused_evidence import journal_path
from tools.resume_paused_input import LIST_AGENTS, parse_agents
from tools.resume_paused_marker import marker_in_command
from tools.resume_paused_models import PROMPT_NAME
from tools.resume_paused_terminal import result_lines

if TYPE_CHECKING:
    from pathlib import Path

    from tools.resume_paused_input import PaneRecord


class Manifest(TypedDict):
    """Identity of the guest case pinned before its first launch."""

    case: str
    boot: str
    panes: dict[str, str]
    digests: dict[str, str]


def _save(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)


def _panes(lab: Path) -> dict[str, PaneRecord]:
    return inventory(lab, parse_agents(run(LIST_AGENTS).stdout))


def _logs(folder: Path, label: str, args: tuple[str, ...], env: dict[str, str] | None = None) -> tuple[int, str]:
    """Preserve diagnostics even after a timeout. Never retry a failed launch."""
    with (folder / f"{label}.stdout").open("xb") as stdout, (folder / f"{label}.stderr").open("xb") as stderr:
        result = subprocess.run(args, cwd=REPO, stdout=stdout, stderr=stderr, env=env, timeout=900, check=False)  # noqa: S603
    output = (folder / f"{label}.stdout").read_text(encoding="utf-8", errors="replace")
    _save(folder / f"{label}.exit.json", result.returncode)
    return result.returncode, output


def _launcher(lab: Path, label: str) -> None:
    folder = lab / label
    folder.mkdir()
    code, _ = _logs(folder, "tuitp", (str(executable("tuitp.bat")), "--list", str(lab / "tuitp.list")))
    assert code == 0, f"tuitp exited {code}; see {folder}"


def _draft(pane: PaneRecord) -> None:
    capture = run(["tuios", "capture-pane", "-s", pane.session, "-w", pane.pane_id, "--trim"]).stdout
    assert "RP-UNSENT-472" in capture, "Leave the sentinel draft in the Codex peer editor"


def _journal_hash(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _copied(lab: Path, index: int, panes: dict[str, PaneRecord], before: Observation) -> None:
    """Check a real receiver's refusal of the most recent preview, including on the same-host decoy."""
    previous = lab / f"step-{index}"
    report = (previous / "launch-1.stdout").read_text(encoding="utf-8")
    marker = marker_in_command(report)
    pane = panes["Codex peer" if index == 1 else "Codex primary"]
    capture = run(["tuios", "capture-pane", "-s", pane.session, "-w", pane.pane_id, "--trim"]).stdout
    assert f"resume-paused {marker.launch_id} failed" in result_lines(tuple(capture.splitlines())), f"Wait for the marked refusal in {pane.name}"
    baseline = json.loads((previous / "after-alpha.json").read_text(encoding="utf-8"))
    assert asdict(before) == baseline, "The copied preview changed the checkout"


def _after(root: Path, journal: Path, before: Observation, row: Row) -> Observation:
    # Receivers append the journal after the receipt. Allow the receiver to finish without sending anything.
    deadline = time.monotonic() + 60
    observation = observe(root, journal)
    while "resume" in row.phases and row.status != "FAIL" and observation.resumes == before.resumes and time.monotonic() < deadline:
        time.sleep(1)
        observation = observe(root, journal)
    return observation


def _launch(folder: Path, case: str, index: int, step: Step, panes: dict[str, PaneRecord]) -> list[tuple[int, str]]:
    if case in {"stall", "recovery"} and index == 0:
        return [run_fault(folder, case, panes["Codex peer"])]
    args = (str(REPO / "bin/resume_paused.bat"), *step.args)
    env = None
    if case == "caller":
        env = dict(os.environ, **({"CLAUDECODE": "1"} if index else {"CODEX_THREAD_ID": "guest-caller"}))
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(_logs, folder, f"launch-{number + 1}", args, env) for number in range(2 if step.concurrent else 1)]
        return [future.result() for future in futures]


def _check_digests(before: dict[str, Observation], digests: dict[str, str]) -> None:
    for name, observation in before.items():
        assert observation.files.get(PROMPT_NAME) == digests.get(name), f"Changed or unexpected pause in {name}"


@dataclass
class StepEvidence:
    """The checkout observations for a single human launch."""

    folder: Path
    journal: Path
    rows: dict[str, Row]
    before: dict[str, Observation]

    def launch(self, case: str, index: int, step: Step, panes: dict[str, PaneRecord]) -> None:
        """Lock the attempt and retain observations even when the child fails."""
        self.folder.mkdir()  # Exclusive checkpoint before the first possible input, also across simultaneous operators.
        _save(self.folder / "before.json", {name: asdict(value) for name, value in self.before.items()})
        try:
            results = _launch(self.folder, case, index, step, panes)
        finally:
            for name in self.rows:
                _save(self.folder / f"immediate-{name}.json", asdict(observe(self.folder.parent / name, self.journal)))
        check_reports(step, results)

    def check_readonly_journal(self, original_hash: str | None) -> None:
        """A read-only command must preserve even journal entries for unrelated checkouts."""
        if not any(row.phases for row in self.rows.values()):
            assert _journal_hash(self.journal) == original_hash, "A read-only launch changed the journal"

    def check_outcomes(self, case: str, digests: dict[str, str], panes: dict[str, PaneRecord]) -> None:
        """Keep the final evidence for both roots before checking their receipts."""
        lab = self.folder.parent
        after = {name: _after(lab / name, self.journal, self.before[name], row) for name, row in self.rows.items()}
        for name, observation in after.items():
            _save(self.folder / f"after-{name}.json", asdict(observation))
        for name, row in self.rows.items():
            root = lab / name
            observation = after[name]
            agent = "claude" if name == "bravo" or case == "switch" else "chatgpt"
            check_delta(self.before[name], observation, row, agent)
            if name in digests:
                check_receiver(root, case, digests[name], row, panes)


def _step(lab: Path, case: str, index: int, digests: dict[str, str], panes: dict[str, PaneRecord]) -> None:
    step = CASES[case][index]
    folder = lab / f"step-{index + 1}"
    journal = journal_path(os.environ)
    assert journal is not None
    rows = {"alpha": step.alpha, "bravo": step.bravo or Row("SKIP")}
    before = {name: observe(lab / name, journal) for name in rows}
    _check_digests(before, digests)
    journal_before = _journal_hash(journal)
    if case == "draft":
        _draft(panes["Codex peer"])
    if case == "copied" and index:
        _copied(lab, index, panes, before["alpha"])
    evidence = StepEvidence(folder, journal, rows, before)
    evidence.launch(case, index, step, panes)
    evidence.check_outcomes(case, digests, panes)
    evidence.check_readonly_journal(journal_before)
    if case == "draft":
        _draft(panes["Codex peer"])
    _save(folder / "passed.json", {"case": case, "step": index + 1, "args": step.args})


def _next_index(lab: Path, case: str) -> int:
    for index in range(len(CASES[case])):
        folder = lab / f"step-{index + 1}"
        if not (folder / "passed.json").exists():
            assert not folder.exists(), f"Interrupted or failed step. Keep evidence at {folder} and revert the guest snapshot to repeat."
            return index
    return len(CASES[case])


def _overall(lab: Path, case: str) -> None:
    question = OBSERVATIONS.get(case)
    if question:
        path = lab / "observation.json"
        if not path.exists():
            sys.stdout.write(f"Awaiting operator observation. {question} Run lab.bat verdict.\n")
            return
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record["verdict"] == "pass", f"FAIL {case}. {record['note']}"
    sys.stdout.write(f"PASS {case}. Evidence at {lab}\n")


def _verdict(lab: Path) -> None:
    case = json.loads((lab / "case.json").read_text(encoding="utf-8"))["case"]
    assert case in OBSERVATIONS, "This case has only automated checks"
    assert _next_index(lab, case) == len(CASES[case]), "Complete the command steps first"
    path = lab / "observation.json"
    if not path.exists():
        sys.stdout.write(OBSERVATIONS[case] + "\n")
        verdict = input("Observed outcome (pass/fail): ").strip().lower()
        assert verdict in {"pass", "fail"}, "Enter pass or fail"
        note = input("Record what you saw in the pane(s): ").strip()
        assert note, "Include the observed result"
        _save(path, {"case": case, "verdict": verdict, "note": note})
    _overall(lab, case)


def _status(lab: Path) -> None:
    manifest = lab / "case.json"
    if not manifest.is_file():
        state = "Seeding interrupted" if (lab / "seeding").exists() else "No case seeded"
        if (lab / "pair-ready").is_file() and not (lab / "adopting").exists():
            state = "Review prepared. Save the native paired pause, then seed capture-pair"
        sys.stdout.write(f"{state}. Guest evidence at {lab}\n")
        return
    case = json.loads(manifest.read_text(encoding="utf-8"))["case"]
    for index, step in enumerate(CASES[case], start=1):
        folder = lab / f"step-{index}"
        if not (folder / "passed.json").is_file():
            state = "Locked after launch" if folder.exists() else "Next"
            sys.stdout.write(f"{state}: {case} step {index}/{len(CASES[case])} ({' '.join(step.args) or 'normal launch'}). Evidence at {folder}\n")
            return
    _overall(lab, case)


def _seed_case(lab: Path, selected: str | None, boot: str) -> None:
    if selected is None:
        (lab / "seeding").touch(exist_ok=False)
        prepare_review(lab / "alpha")
        (lab / "pair-ready").touch(exist_ok=False)
        sys.stdout.write("Review prepared. Save the native paired pause, then seed capture-pair.\n")
        return
    panes = _panes(lab)
    if selected == "capture-pair":
        assert (lab / "pair-ready").is_file(), "Run prepare-pair before the native paired pause"
        (lab / "adopting").touch(exist_ok=False)
    else:
        (lab / "seeding").touch(exist_ok=False)
    digests = seed(lab, selected, panes)
    if selected == "history":
        record_prior_resume(lab / "bravo", journal_path(os.environ))
    _save(lab / "case.json", {"case": selected, "boot": boot, "digests": digests, "panes": {name: p.pane_id for name, p in panes.items()}})
    sys.stdout.write(f"Seeded {selected}. Follow its staging instructions, then run next.\n")


def _operate(action: str, selected: str | None) -> None:
    lab, ledger, boot = guest()
    os.environ.update(LLM_SHARED_DIR=str(REPO), TUITP_RESUME="0", PYTHONUTF8="1")
    if action == "open":
        check_namespace(lab, ledger, fresh=True)
        layout(lab)
        _launcher(lab, "open")
        check_namespace(lab, ledger, fresh=False)
        sys.stdout.write(f"Lab opened at {lab}. Finish host setup and snapshot the VM before seeding.\n")
        return
    if action == "status":
        _status(lab)
        return
    if action == "verdict":
        _verdict(lab)
        return
    check_namespace(lab, ledger, fresh=False, restoring=action == "restore")
    if action in {"prepare-pair", "seed"}:
        _seed_case(lab, selected, boot)
        return
    _advance(lab, action, boot)


def _advance(lab: Path, action: str, boot: str) -> None:
    manifest: Manifest = json.loads((lab / "case.json").read_text(encoding="utf-8"))
    case = manifest["case"]
    index = _next_index(lab, case)
    if action == "waiter":
        assert case == "hibernate", "Start the waiter before the first hibernation step"
        assert index == 0, "Start the waiter before the first hibernation step"
        start_waiter(lab)
        return
    if action == "restore":
        assert case == "reboot", "Restore is only for the reboot checkpoint"
        assert index == 1, "Restore is only for the reboot checkpoint"
        assert boot != manifest["boot"], "Restore is only for the reboot checkpoint"
        _launcher(lab, "restore")
        return
    _run_next(lab, case, index, manifest, boot)


def _run_next(lab: Path, case: str, index: int, manifest: Manifest, boot: str) -> None:
    if index == len(CASES[case]):
        _overall(lab, case)
        return
    sys.stdout.write(f"{case} step {index + 1}/{len(CASES[case])}: resume_paused {' '.join(CASES[case][index].args)}\n")
    panes = _panes(lab)
    assert {label: pane.pane_id for label, pane in panes.items()} == manifest["panes"], "Saved UUIDs changed; the original route cannot be restored"
    check_power(case, index, lab, boot, manifest["boot"])
    _step(lab, case, index, manifest["digests"], panes)
    sys.stdout.write(f"PASS {case} step {index + 1}/{len(CASES[case])}. Evidence at {lab}\n")
    if index + 1 == len(CASES[case]):
        _overall(lab, case)


def main() -> int:
    """Dispatch only explicitly requested human operations. Listing cases never touches live hosts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("cases", "open", "prepare-pair", "seed", "next", "status", "verdict", "restore", "waiter"), nargs="?", default="cases")
    parser.add_argument("case", choices=sorted(CASES), nargs="?")
    args = parser.parse_args()
    if not __debug__:
        parser.error("The acceptance verifier requires Python assertions enabled")
    if (args.action == "seed") != bool(args.case):
        parser.error("Supply a case name only with seed")
    if args.action == "cases":
        sys.stdout.write("\n".join(f"{name} ({len(steps)} {'step' if len(steps) == 1 else 'steps'})" for name, steps in CASES.items()) + "\n")
        return 0
    try:
        _operate(args.action, args.case)
    except (AssertionError, EOFError, OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        sys.stderr.write(f"Acceptance check failed: {type(error).__name__}: {error}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


# eof
