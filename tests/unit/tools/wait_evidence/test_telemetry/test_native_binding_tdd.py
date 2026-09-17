"""Verify selected native headers and keep local timing outside usage authority."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    lifecycle,
    manifest_data,
)
from tools.wait_evidence.collector import Collector
from tools.wait_evidence.models import StreamSpec, TrialManifest
from tools.wait_evidence.probe_driver import capture_stream
from tools.wait_evidence.telemetry import Telemetry

if TYPE_CHECKING:
    from pathlib import Path

    from tools.wait_evidence.models import JsonObject

pytestmark = pytest.mark.timeout(10)


def selected(root: Path, host: str = "codex", role: str = "telemetry") -> tuple[JsonObject, Path, JsonObject]:
    """Create a selected file whose identity header precedes the measured offset."""
    data = manifest_data(root)
    build = "0.154.0" if host == "codex" else "2.1.272"
    data.update(host=host, home=str(root), build=build, schema=f"{host}-native-{build}")
    path = root / "a.shared-wait-service" / "run" / "events.jsonl"
    path.parent.mkdir(parents=True)
    header: JsonObject
    if role == "probe":
        header = {key: data[key] for key in ("schema", "host", "build", "thread", "profile", "source_id")}
        header["type"] = "probe_meta"
    elif host == "codex":
        header = {"type": "session_meta", "payload": {"id": data["thread"], "cli_version": build}}
    else:
        header = {"type": "user", "sessionId": data["thread"], "version": build}
    path.write_text(json.dumps(header) + "\n", encoding="utf-8")
    data["streams"] = [{**capture_stream(path), "role": role}]
    return data, path, header


class TestNativeBinding:
    """Keep native gaps explicit while accepting local A-arm timing boundaries."""

    def test_classic_pending_return_restores_timing_without_coverage(self, tmp_path: Path) -> None:
        """A real probe journal supplies wait timing, never request authority."""
        data, path, header = selected(tmp_path, role="probe")
        data["arm"] = "A"
        rows = lifecycle()[:-1]
        with path.open("a", encoding="utf-8") as stream:
            for row in rows:
                if row["kind"] == "normal_turn_end":
                    row["kind"] = "pending_return"
                stream.write(json.dumps({**row, **header, "type": "probe_event"}) + "\n")
        manifest = TrialManifest.from_dict(data)
        collector = Collector(manifest)
        for record in Telemetry(manifest).read(486):
            collector.ingest(record)
        report = collector.report(486)
        assert (report["quiet_duration"], report["source_duration"], report["logical_consumptions"]) == (243 - 5, 243 - 3, 1)
        assert report["gaps"] == []
        assert report["request_coverage"] == "incomplete"
        assert report["strict_zero_inference"] is False
        assert report["status"] == "inconclusive"

    @pytest.mark.parametrize(("host", "fault"), [("codex", "wrong-thread"), ("claude", "wrong-build"),
        ("codex", "empty"), ("codex", "non-header"), ("codex", "bad-json"), ("codex", "outside-home")])
    def test_header_errors_survive_pre_prompt_offsets(self, tmp_path: Path, host: str, fault: str) -> None:
        """Skipping seed bytes never skips verification of their native identity."""
        data, path, header = selected(tmp_path, host)
        if fault == "wrong-thread":
            header["payload"] = {"id": "other", "cli_version": data["build"]}
        if fault == "wrong-build":
            header["version"] = "uninspected"
        if fault == "non-header":
            header = {"type": "not-a-header"}
        contents = json.dumps(header) + "\n"
        if fault in {"empty", "bad-json"}:
            contents = "" if fault == "empty" else "invalid\n"
        path.write_text(contents, encoding="utf-8")
        data["streams"] = [capture_stream(path)]
        if fault == "outside-home":
            data["home"] = str(tmp_path / "another-home")
        records = Telemetry(TrialManifest.from_dict(data)).read(30)
        assert len(records) == 1
        assert records[0].kind == "gap"

    @pytest.mark.parametrize("fault", ["missing-header", "identity", "outside-evidence", "certificate", "event-identity"])
    def test_probe_measurements_cannot_forge_native_coverage(self, tmp_path: Path, fault: str) -> None:
        """Local markers bind the whole run and admit only measurement kinds."""
        data, path, header = selected(tmp_path, role="probe")
        if fault == "outside-evidence":
            target = tmp_path / "outside.jsonl"
            path.replace(target)
            path = target
        if fault == "missing-header":
            header["type"] = "other"
        if fault == "identity":
            header["thread"] = "other"
        path.write_text(json.dumps(header) + "\n", encoding="utf-8")
        data["streams"] = [{**capture_stream(path), "role": "probe"}]
        row = {**header, "type": "probe_event", "kind": "coverage" if fault == "certificate" else "source_ready",
               "at": 20, "data": {}, "event_id": "measurement"}
        if fault == "event-identity":
            row["thread"] = "unrelated"
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row) + "\n")
        records = Telemetry(TrialManifest.from_dict(data)).read(30)
        assert records[0].kind == "gap"

    def test_probe_record_in_native_stream_and_unknown_role_are_rejected(self, tmp_path: Path) -> None:
        """Local events belong to the selected measurement journal only."""
        data, path, _header = selected(tmp_path)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"type": "probe_event"}) + "\n")
        assert Telemetry(TrialManifest.from_dict(data)).read(30)[0].kind == "gap"
        with pytest.raises(ValueError, match="Unknown stream role"):
            StreamSpec.from_dict({"path": str(path), "offset": 0, "role": "coverage"})

    def test_claude_header_and_non_usage_observation(self, tmp_path: Path) -> None:
        """A valid current-build transcript binds even without a usage record."""
        data, path, header = selected(tmp_path, "claude")
        header["timestamp"] = "1970-01-01T00:00:20Z"
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(header) + "\n")
        adapter = Telemetry(TrialManifest.from_dict(data))
        assert adapter.read(30)[0].kind == "native_observation"
        header["sessionId"] = "other"
        assert adapter.normalize(header, "selected:123", 30).kind == "gap"
        header["sessionId"] = data["thread"]
        header["timestamp"] = "1970-01-01T00:00:20"
        assert adapter.normalize(header, "selected:124", 30).kind == "gap"


# eof
