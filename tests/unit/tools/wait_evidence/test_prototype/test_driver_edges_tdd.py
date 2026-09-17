"""Check immutable preparation, bounded reservation work and command boundaries."""

# ruff: noqa: PLR2004 - Fixed benchmark controls and exact test identities.

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from tests.unit.tools.wait_evidence.test_prototype.test_prototype_tdd import (
    experiment,
    native_stream,
    request,
)
from tools.wait_evidence import probe_cli
from tools.wait_evidence.models import object_value
from tools.wait_evidence.probe_driver import (
    ORDER,
    Experiment,
    capture_stream,
    git_bytes,
)

if TYPE_CHECKING:
    from tools.wait_evidence.models import JsonValue

pytestmark = pytest.mark.timeout(10)


class TestDriverBoundaries:
    """Retain invalid attempts and bound reservation work as prior trials accumulate."""

    def test_reservation_work_is_bounded_with_retained_trials(self, tmp_path: Path,
                                                            monkeypatch: pytest.MonkeyPatch) -> None:
        """A SQLite instruction budget rejects history scans without wall-clock timing."""
        series = experiment(tmp_path, monkeypatch)
        connect = sqlite3.connect
        database = series.directory / "trials.sqlite3"
        with connect(database) as connection:
            connection.executemany("INSERT INTO trials VALUES (?, ?, ?, ?, ?, ?, ?)",
                ((f"old-{index}", f"thread-{index}", f"pair-{index // 2}", ORDER[index % 6],
                  "trial", 10000, index) for index in range(6000)))
            connection.execute("INSERT INTO trials VALUES ('baseline', 'baseline', 'baseline', 'A', 'baseline', 10000, 6000)")
        connection.close()

        def budgeted_connect(path: str | Path, *, uri: bool = False) -> sqlite3.Connection:
            result = connect(path, uri=uri)
            if "trials.sqlite3" in str(path):
                result.set_progress_handler(lambda: 1, 2000)
            return result

        monkeypatch.setattr("tools.wait_evidence.probe_driver.sqlite3.connect", budgeted_connect)
        data = request(series)
        data.update(pair_id="new-pair", streams=[native_stream(tmp_path / "fresh.jsonl")])
        directory = series.prepare(data, 11)
        assert (directory / "benchmark.txt").is_file()
        with connect(database) as connection:
            assert connection.execute("SELECT ordinal FROM trials WHERE run='run-one'").fetchone() == (6000,)
        connection.close()

    def test_git_reads_full_blobs_and_resolves_commit(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Git commands use argument vectors and keep complete stdout bytes."""
        invoke = Mock(return_value=Mock(stdout=b"complete\nblob\n"))
        monkeypatch.setattr("tools.wait_evidence.probe_driver.subprocess.run", invoke)
        assert git_bytes(tmp_path, "HEAD") == b"complete\nblob\n"
        assert "--end-of-options" in invoke.call_args.args[0]
        assert git_bytes(tmp_path, "a" * 40 + ":docs/draft.md").endswith(b"blob\n")
        assert invoke.call_args.args[0][3] == "show"

    def test_freeze_rejects_relative_repository_and_bad_commit(self, tmp_path: Path,
                                                            monkeypatch: pytest.MonkeyPatch) -> None:
        """A seed revision must resolve before any series directory is published."""
        series = experiment(tmp_path, monkeypatch)
        target = tmp_path / "a.shared-wait-service" / "other"
        with pytest.raises(ValueError, match="Repository must be absolute"):
            Experiment.freeze(target, Path("relative"), "HEAD", series.settings)
        monkeypatch.setattr("tools.wait_evidence.probe_driver.git_bytes", Mock(return_value=b"invalid"))
        with pytest.raises(ValueError, match="full commit"):
            Experiment.freeze(target, tmp_path, "HEAD", series.settings)
        with pytest.raises(ValueError, match="Telemetry paths"):
            capture_stream(Path("relative"))

    @pytest.mark.parametrize(("field", "value", "message"), [("run_id", "../escape", "directory component"),
        ("thread", "00000000000040008000000000000001", "canonical"), ("arm", "B-service", "Only A"),
        ("mode", "unknown", "Unknown trial mode"), ("streams", [], "Explicit native")])
    def test_invalid_controls_fail_before_prompt(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                field: str, value: JsonValue, message: str) -> None:  # noqa: PLR0913 - Boundary case table.
        """Malformed identities and unsupported arms cannot become a benchmark."""
        series = experiment(tmp_path, monkeypatch)
        data = request(series)
        stream = tmp_path / "rollout.jsonl"
        stream.touch()
        data["streams"] = [str(stream)]
        data[field] = value
        with pytest.raises(ValueError, match=message):
            series.prepare(data, 11)

    def test_modified_seed_and_implementing_thread_are_rejected(self, tmp_path: Path,
                                                             monkeypatch: pytest.MonkeyPatch) -> None:
        """Changing frozen bytes or measuring the implementation session is invalid."""
        series = experiment(tmp_path, monkeypatch)
        data = request(series)
        (series.directory / "seeds/draft.v0.13.0.no_polling.md").write_bytes(b"changed")
        with pytest.raises(ValueError, match="Frozen seed bytes"):
            series.prepare(data, 11)
        data["run_id"] = "implementing"
        monkeypatch.setenv("CODEX_THREAD_ID", str(data["thread"]))
        with pytest.raises(ValueError, match="implementing conversation"):
            series.prepare(data, 12)

    def test_fixed_order_and_duplicate_pair_rejection(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """All six fresh trials retain fixed controls and respect A/B, B/A, A/B."""
        series = experiment(tmp_path, monkeypatch)
        stream = tmp_path / "rollout.jsonl"
        stream.touch()
        data = request(series)
        for index, arm in enumerate(ORDER):
            data = request(series, f"run-{index}")
            thread = f"00000000-0000-4000-8000-{index + 1:012d}"
            data.update(thread=thread, arm=arm,
                        pair_id=f"pair-{index // 2}", streams=[native_stream(tmp_path / f"{index}.jsonl", thread)])
            directory = series.prepare(data, 11)
            manifest = object_value(json.loads((directory / "manifest.json").read_text(encoding="utf-8")))
            assert (manifest["wake_bound"], manifest["duplicate_window"], manifest["drain_bound"]) == (60, 120, 120)
        duplicate = {**data, "run_id": "duplicate", "thread": "00000000-0000-4000-8000-000000000010", "arm": "A"}
        duplicate["streams"] = [native_stream(tmp_path / "duplicate.jsonl", str(duplicate["thread"]))]
        with pytest.raises(ValueError, match="Pair already"):
            series.prepare(duplicate, 12)

    def test_cli_freeze_prepare_and_register(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """The CLI produces reviewable paths and registers only a prepared run."""
        series = experiment(tmp_path, monkeypatch)
        settings = tmp_path / "settings.json"
        settings.write_text(json.dumps(series.settings), encoding="utf-8")
        second = tmp_path / "a.shared-wait-service" / "second"
        assert probe_cli.main(["freeze", "--directory", str(second), "--repository", str(tmp_path),
                               "--commit", "HEAD", "--settings", str(settings)]) == 0
        data = request(Experiment(second))
        data["mode"] = "baseline"
        stream = tmp_path / "rollout.jsonl"
        data["streams"] = [native_stream(stream)]
        path = tmp_path / "request.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        monkeypatch.setattr("tools.wait_evidence.probe_cli.time.time", Mock(return_value=11.0))
        assert probe_cli.main(["prepare", "--directory", str(second), "--request", str(path)]) == 0
        assert probe_cli.main(["register", "--directory", str(second / "run-one")]) == 0
        assert "600 seconds" in (second / "run-one/benchmark.txt").read_text(encoding="utf-8")

    @pytest.mark.parametrize("fault", ["unrelated", "empty", "outside-home", "order"])
    def test_native_binding_precedes_prompt(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str) -> None:
        """Wrong native files or trial ordering leave a retained invalid attempt."""
        series = experiment(tmp_path, monkeypatch)
        data = request(series)
        path = tmp_path / "rollout.jsonl"
        data["streams"] = [native_stream(path, "unrelated" if fault == "unrelated" else str(data["thread"]))]
        if fault == "empty":
            path.write_bytes(b"")
        if fault == "outside-home":
            series.settings["home"] = str(tmp_path / "another-home")
        if fault == "order":
            data["arm"] = "B-prototype"
        with pytest.raises(ValueError, match=r"Native|Initial trial order"):
            series.prepare(data, 11)
        assert not (series.directory / "run-one/benchmark.txt").exists()


# eof
