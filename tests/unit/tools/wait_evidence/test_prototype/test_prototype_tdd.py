"""Prove durable prototype lifecycle without model calls or real timer waits."""

# ruff: noqa: PLR2004 - Protocol timestamps and counters are assertion examples.

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.wait_evidence.probe_driver import SEEDS, Experiment
from tools.wait_evidence.prototype import Prototype, Route

if TYPE_CHECKING:
    from tools.wait_evidence.models import JsonObject, JsonValue

pytestmark = pytest.mark.timeout(10)


def registration(root: Path) -> JsonObject:
    """Use explicit synthetic identities in an isolated ignored run directory."""
    return {"thread": "thread-one", "profile": str(root / "profile"),
            "source_id": "source-one", "wait_id": "wait-one", "event_id": "event-one",
            "source_start": 100.0, "due_at": 340.0}


class TestPrototype:
    """Exercise normal-end gates, cancellation during host I/O and receipt recovery."""

    def test_status_io_allows_cancellation_before_send(self, tmp_path: Path) -> None:
        """Host status does not lock out writers, and a concurrent cancel wins."""
        path = tmp_path / "a.shared-wait-service" / "status-cancel"
        prototype = Prototype.create(path, registration(tmp_path))
        prototype.normal_end(110, "direct-turn-evidence")

        def status() -> str:
            # Prove the host callback can acquire a write lock without waiting.
            with sqlite3.connect(prototype.database, timeout=0) as connection:
                connection.execute("BEGIN IMMEDIATE")
            connection.close()
            Prototype(path).suppress("cancel", 340)
            return "idle"

        route = Route("direct-turn-evidence", status, lambda _: pytest.fail("cancelled send"))
        assert prototype.advance(340, route) == "suppressed"
        assert Prototype(path).snapshot()["delivery"] == "not-attempted"

    def test_timer_survives_restart_and_delivers_once(self, tmp_path: Path) -> None:
        """A reopened harness keeps its exact outcome and send attempt identity."""
        path = tmp_path / "a.shared-wait-service" / "series" / "run"
        prototype = Prototype.create(path, registration(tmp_path))
        sent: list[str] = []
        route = Route("direct-turn-evidence", lambda: "idle", lambda message: sent.append(message) or "receipt-1")
        prototype.normal_end(110, "direct-turn-evidence")
        assert prototype.advance(339, route) == "waiting"
        assert Prototype(path).advance(340, route) == "accepted"
        assert Prototype(path).advance(341, route) == "accepted"
        assert len(sent) == 1
        assert "WAIT_TEST_DONE" in sent[0]

    def test_consumption_is_durable_and_duplicate_is_rejected(self, tmp_path: Path) -> None:
        """The exact event can be usefully consumed once across process restarts."""
        prototype = Prototype.create(tmp_path / "a.shared-wait-service" / "consume", registration(tmp_path))
        prototype.advance(340, Route("unavailable", lambda: "idle", lambda _: None))
        assert prototype.consume("event-one", "thread-one", 342) is True
        assert prototype.consume("event-one", "thread-one", 343) is False
        state = prototype.snapshot()
        assert state["event_id"] == "event-one"
        assert state["consumed_at"] == 342
        assert state["duplicate_consumptions"] == 1

    @pytest.mark.parametrize("gate", ["direct-turn-evidence", "host-gated-turn-end"])
    def test_early_outcome_waits_for_proven_normal_end(self, tmp_path: Path, gate: str) -> None:
        """Readiness is durable before arming and operator markers never arm."""
        path = tmp_path / "a.shared-wait-service" / "series" / gate
        prototype = Prototype.create(path, registration(tmp_path))
        route = Route(gate, lambda: "idle", lambda _: "receipt")
        prototype.mark_normal_end(350)
        assert prototype.advance(351, route) == "retained-result-only"
        assert prototype.snapshot()["ready_at"] == 351
        prototype.normal_end(352, gate)
        assert Prototype(path).advance(353, route) == "accepted"

    @pytest.mark.parametrize("reason", ["stop", "cancel", "interrupted", "closed", "stale", "bridge-failed"])
    def test_suppression_retains_outcome(self, tmp_path: Path, reason: str) -> None:
        """Stop, Cancel and broken recipients cannot cause an automatic send."""
        prototype = Prototype.create(tmp_path / "a.shared-wait-service" / reason, registration(tmp_path))
        prototype.normal_end(110, "direct-turn-evidence")
        prototype.suppress(reason, 120)
        route = Route("direct-turn-evidence", lambda: "idle", lambda _: pytest.fail("suppressed send"))
        assert prototype.advance(340, route) == "suppressed"
        assert prototype.snapshot()["ready_at"] == 340
        with pytest.raises(ValueError, match="suppressed"):
            prototype.consume("event-one", "thread-one", 341)

    @pytest.mark.parametrize("status", ["busy", "closed", "stale", "bridge-failed"])
    def test_host_status_blocks_send(self, tmp_path: Path, status: str) -> None:
        """Recipient validation happens before any native invocation."""
        prototype = Prototype.create(tmp_path / "a.shared-wait-service" / status, registration(tmp_path))
        prototype.normal_end(110, "direct-turn-evidence")
        route = Route("direct-turn-evidence", lambda: status, lambda _: pytest.fail("invalid send"))
        assert prototype.advance(340, route) == status

    def test_lost_acknowledgement_is_not_automatically_retried(self, tmp_path: Path) -> None:
        """A persisted send intent prevents fresh CLI IDs from duplicating a wake."""
        prototype = Prototype.create(tmp_path / "a.shared-wait-service" / "lost", registration(tmp_path))
        prototype.normal_end(110, "direct-turn-evidence")
        calls: list[str] = []
        route = Route("direct-turn-evidence", lambda: "idle", lambda message: calls.append(message) or None)
        assert prototype.advance(340, route) == "receipt-unknown"
        assert Prototype(prototype.directory).advance(350, route) == "receipt-unknown"
        assert len(calls) == 1
        prototype.receipt("receipt-late")
        assert prototype.snapshot()["delivery"] == "accepted"

    def test_invalid_gate_and_identity_fail_closed(self, tmp_path: Path) -> None:
        """Unavailable capabilities and unrelated receipt consumers remain explicit."""
        prototype = Prototype.create(tmp_path / "a.shared-wait-service" / "invalid", registration(tmp_path))
        route = Route("unavailable", lambda: "idle", lambda _: pytest.fail("unavailable send"))
        assert prototype.advance(340, route) == "retained-result-only"
        with pytest.raises(ValueError, match="normal-end"):
            prototype.normal_end(341, "operator-marker")
        with pytest.raises(ValueError, match="identity"):
            prototype.consume("different-event", "thread-one", 342)
        with pytest.raises(ValueError, match="identity"):
            prototype.consume("event-one", "different-thread", 342)


def experiment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Experiment:
    """Freeze representative complete Git blobs without an external repository setup."""
    def read_git(_repository: Path, revision: str) -> bytes:
        return b"a" * 40 if ":" not in revision else b"full draft\nlast line\n"

    monkeypatch.setattr("tools.wait_evidence.probe_driver.git_bytes", read_git)
    settings: JsonObject = {"series_id": "series-one", "host": "codex", "build": "0.154.0",
                            "schema": "codex-native-0.154.0", "model": "model-one", "profile": "profile-one",
                            "home": str(tmp_path), "configuration": {"model": "model-one", "effort": "high"}}
    return Experiment.freeze(tmp_path / "a.shared-wait-service" / "series", tmp_path, "HEAD", settings)


def request(experiment: Experiment, run: str = "run-one") -> JsonObject:
    """Describe an operator-confirmed fresh READY before capturing a trial."""
    return {"run_id": run, "thread": "00000000-0000-4000-8000-000000000001", "arm": "A", "pair_id": "pair-1",
            "ready_at": 10, "context_tokens": 10000, "complete_reads": True,
            "ready_marker": "READY", "seed_hashes": experiment.settings["seed_hashes"],
            "streams": [], "mode": "trial"}


def native_stream(path: Path, thread: str = "00000000-0000-4000-8000-000000000001") -> str:
    """Retain a selected native file with its inspected exact-thread header."""
    path.write_text(json.dumps({"type": "session_meta", "payload": {"id": thread, "cli_version": "0.154.0"}}) + "\n",
                    encoding="utf-8")
    return str(path)


class TestExperiment:
    """Freeze seeds, reserve fresh identities and retain invalid matched-trial attempts."""

    def test_frozen_bytes_manifest_and_prompt_order(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A manifest captures complete seeds and telemetry positions before prompt publication."""
        series = experiment(tmp_path, monkeypatch)
        stream = tmp_path / "rollout.jsonl"
        data = request(series)
        data["streams"] = [native_stream(stream)]
        directory = series.prepare(data, 11)
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["seed_commit"] == "a" * 40
        assert set(manifest["seed_hashes"]) == set(SEEDS)
        assert all((series.directory / "seeds" / Path(name).name).read_bytes().endswith(b"last line\n") for name in SEEDS)
        assert manifest["streams"][0]["offset"] == stream.stat().st_size
        assert manifest["ready_at"] < manifest["created_at"]
        assert "60000" in (directory / "benchmark.txt").read_text(encoding="utf-8")
        with pytest.raises(FileExistsError):
            series.prepare(data, 12)

    @pytest.mark.parametrize(("field", "value"), [("complete_reads", False), ("ready_marker", "almost"),
                                           ("ready_at", 12), ("arm", "B-prototype"),
                                           ("thread", "session-name"), ("seed_hashes", {})])
    def test_invalid_trials_are_retained(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                         field: str, value: JsonValue) -> None:
        """Validation failure preserves the original request and creates no benchmark prompt."""
        series = experiment(tmp_path, monkeypatch)
        data = request(series)
        data[field] = value
        with pytest.raises(ValueError, match=r".+"):
            series.prepare(data, 11)
        result = json.loads((series.directory / "run-one" / "invalid.json").read_text(encoding="utf-8"))
        assert result["status"] == "invalid"
        assert not (series.directory / "run-one" / "benchmark.txt").exists()

    def test_thread_reuse_and_context_mismatch_stay_invalid(self, tmp_path: Path,
                                                          monkeypatch: pytest.MonkeyPatch) -> None:
        """A second arm needs a fresh thread and context within five percent."""
        series = experiment(tmp_path, monkeypatch)
        stream = tmp_path / "rollout.jsonl"
        first = request(series)
        first["streams"] = [native_stream(stream)]
        series.prepare(first, 11)
        reused = {**first, "run_id": "reused", "arm": "B-prototype"}
        with pytest.raises(ValueError, match="fresh"):
            series.prepare(reused, 12)
        mismatch: JsonObject = {**reused, "run_id": "mismatch", "thread": "00000000-0000-4000-8000-000000000002",
                    "context_tokens": 20000,
                    "streams": [native_stream(tmp_path / "second.jsonl", "00000000-0000-4000-8000-000000000002")]}
        with pytest.raises(ValueError, match="context"):
            series.prepare(mismatch, 12)

    @pytest.mark.parametrize("other_cwd", [False, True])
    def test_absolute_cli_imports_from_physical_checkout(self, tmp_path: Path, *, other_cwd: bool) -> None:
        """The standalone script starts in either cwd with no PYTHONPATH setup."""
        repository = Path(__file__).resolve().parents[5]
        script = repository / "docs/v0.13.0/probe.shared-wait-service.py"
        directory = tmp_path / "a.shared-wait-service" / "smoke"
        directory.mkdir(parents=True)
        data = {**registration(tmp_path), "source_seconds": 240, "mode": "trial"}
        (directory / "manifest.json").write_text(json.dumps(data), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(script), "register", "--directory", str(directory)],  # noqa: S603 - Verified interpreter and physical script.
                                   cwd=tmp_path if other_cwd else repository,
                                   capture_output=True, text=True, check=False, timeout=5)
        assert completed.returncode == 0, completed.stderr
        assert json.loads(completed.stdout)["thread"] == "thread-one"
        assert Prototype(directory).snapshot()["source_id"] == "source-one"


# eof
