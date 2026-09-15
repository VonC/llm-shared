"""Reject ambiguous identities, invalid baselines and unbounded trial inputs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    manifest_data,
)
from tools.wait_evidence.models import TrialManifest, identity_digest, usage_value

if TYPE_CHECKING:
    from pathlib import Path

    from tools.wait_evidence.models import JsonObject, JsonValue

pytestmark = pytest.mark.timeout(10)


class TestModels:
    """Validate every independent manifest control and preserve unknown counts."""

    @pytest.mark.parametrize(("field", "value"), [
        ("run_id", ""), ("thread", None), ("arm", "prototype-renamed-service"),
        ("repository", "relative"), ("home", "relative"),
        ("seed_hashes", {}), ("seed_hashes", {"seed": "x" * 64}),
        ("seed_hashes", []), ("configuration_hash", "short"),
        ("context_tokens", 0), ("context_tokens", True), ("context_tokens", "10"),
        ("ready_at", 2), ("wake_bound", 0), ("duplicate_window", float("inf")),
        ("drain_bound", 1), ("created_at", True), ("created_at", "now"),
        ("streams", []), ("streams", None),
        ("streams", [{"path": "relative", "offset": 0}]),
        ("cached_input_included", "unknown"), ("reasoning_included", 1),
        ("baselines", {"epoch": {"input": -1}}),
    ])
    def test_invalid_manifest_rejected(self, tmp_path: Path, field: str, value: JsonValue) -> None:
        """Each invalid control fails before reading telemetry or publishing output."""
        data = manifest_data(tmp_path)
        data[field] = value
        with pytest.raises(ValueError, match=r".+"):
            TrialManifest.from_dict(data)

    @pytest.mark.parametrize("offset", [-1, True, "0", None])
    def test_invalid_stream_offset(self, tmp_path: Path, offset: JsonValue) -> None:
        """A cursor cannot start at an implicit or invalid byte position."""
        data = manifest_data(tmp_path)
        data["streams"] = [{"path": str(tmp_path / "events.jsonl"), "offset": offset}]
        with pytest.raises(ValueError, match="offset"):
            TrialManifest.from_dict(data)

    def test_duplicate_paths_rejected(self, tmp_path: Path) -> None:
        """Two aliases of the same declared path cannot double-count a stream."""
        data = manifest_data(tmp_path)
        stream: JsonObject = {"path": str(tmp_path / "events.jsonl"), "offset": 0}
        data["streams"] = [stream, stream]
        with pytest.raises(ValueError, match="Duplicate"):
            TrialManifest.from_dict(data)

    @pytest.mark.parametrize(("file_id", "anchor"), [
        (None, "a" * 64), ("id", "a" * 64), ([1], "a" * 64),
        ([True, 1], "a" * 64), ([1, -1], "a" * 64),
        ([1, "2"], "a" * 64), ([1, 2], None), ([1, 2], "short"), ([1, 2], "x" * 64),
    ])
    def test_invalid_stream_identity_rejected(self, tmp_path: Path, file_id: JsonValue, anchor: JsonValue) -> None:
        """Incomplete or malformed identity evidence cannot establish continuity."""
        data = manifest_data(tmp_path)
        data["streams"] = [{"path": str(tmp_path / "events.jsonl"), "offset": 0,
                            "file_id": file_id, "anchor_sha256": anchor}]
        with pytest.raises(ValueError, match=r"identity|anchor"):
            TrialManifest.from_dict(data)

    def test_unknown_semantics_remain_unknown(self, tmp_path: Path) -> None:
        """No absent inclusion flag is interpreted as known cached token semantics."""
        data = manifest_data(tmp_path)
        data.pop("cached_input_included")
        data.pop("reasoning_included")
        manifest = TrialManifest.from_dict(data)
        assert manifest.cached_input_included is None
        assert manifest.reasoning_included is None
        assert usage_value({}) == dict.fromkeys(("input", "cached_input", "output", "reasoning"))

    def test_identity_fingerprints_preserve_field_boundaries(self) -> None:
        """Private fields compare consistently without concatenation ambiguity."""
        assert identity_digest("ab", "c") != identity_digest("a", "bc")
        assert identity_digest("ab", "c") == identity_digest("ab", "c")

# eof
