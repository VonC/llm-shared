"""Check the provisional native transport and durable failure boundaries."""

# ruff: noqa: PLR2004 - Explicit protocol examples and fake timestamps.

from __future__ import annotations

from pathlib import Path
from queue import Empty
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from tests.unit.tools.wait_evidence.test_codex_proxy import ProxyPeer
from tests.unit.tools.wait_evidence.test_collector.test_collector_tdd import (
    manifest_data,
)
from tests.unit.tools.wait_evidence.test_prototype.test_prototype_tdd import (
    registration,
)
from tools.wait_evidence.models import TrialManifest
from tools.wait_evidence.prototype import CodexQueue, Prototype, Route, run_directory

if TYPE_CHECKING:
    from tools.wait_evidence.models import JsonObject

pytestmark = pytest.mark.timeout(10)


def native(tmp_path: Path, *, profile: str = "default") -> CodexQueue:
    """Select an inspected build and an exact native UUID with no real host calls."""
    data = manifest_data(tmp_path)
    data.update(host="codex", build="0.154.0", profile=profile, thread="00000000-0000-4000-8000-000000000001")
    return CodexQueue(tmp_path / "codex.exe", TrialManifest.from_dict(data))


class TestDurableFailures:
    """Invalid input and transport exceptions cannot create a second wake."""

    @pytest.mark.parametrize("path", [Path("relative"), Path("C:/elsewhere/run")])
    def test_implicit_or_unignored_state_is_rejected(self, path: Path) -> None:
        """State can only be created under an explicit ignored evidence root."""
        with pytest.raises(ValueError, match="absolute run path"):
            run_directory(path)

    def test_invalid_registration_and_premature_actions(self, tmp_path: Path) -> None:
        """Reject impossible timing, overwritten runs and unearned receipts."""
        data = registration(tmp_path)
        data["due_at"] = 99
        directory = tmp_path / "a.shared-wait-service" / "run"
        with pytest.raises(ValueError, match="due time"):
            Prototype.create(directory, data)
        prototype = Prototype.create(directory, registration(tmp_path))
        with pytest.raises(FileExistsError):
            Prototype.create(directory, registration(tmp_path))
        with pytest.raises(ValueError, match="precedes registration"):
            prototype.normal_end(90, "direct-turn-evidence")
        with pytest.raises(ValueError, match="Unknown suppression"):
            prototype.suppress("unknown", 100)
        with pytest.raises(ValueError, match="send intent"):
            prototype.receipt("unexpected")
        with pytest.raises(ValueError, match="precedes readiness"):
            prototype.consume("event-one", "thread-one", 110)

    def test_exception_after_send_intent_survives_restart(self, tmp_path: Path) -> None:
        """A lost transport response cannot be retried by reopening state."""
        prototype = Prototype.create(tmp_path / "a.shared-wait-service" / "run", registration(tmp_path))
        prototype.normal_end(110, "direct-turn-evidence")
        prototype.normal_end(120, "host-gated-turn-end")
        sender = Mock(side_effect=OSError("lost connection"))
        route = Route("direct-turn-evidence", lambda: "idle", sender)
        with pytest.raises(OSError, match="lost connection"):
            prototype.advance(340, route)
        assert Prototype(prototype.directory).advance(341, route) == "receipt-unknown"
        assert sender.call_count == 1
        assert prototype.snapshot()["normal_end_at"] == 110


class TestCodexQueue:
    """Require WebSocket proxy framing, read-only checks and exact queue arguments."""

    @pytest.mark.parametrize(("status", "expected"), [("idle", "idle"), ("active", "busy"),
                                                      ("notLoaded", "closed"), ("systemError", "bridge-failed")])
    def test_recipient_status(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                              status: str, expected: str) -> None:
        """Translate the installed protocol's recipient status conservatively."""
        host = native(tmp_path)
        result: JsonObject = {"thread": {"id": host.manifest.thread, "cliVersion": "0.154.0", "status": {"type": status}}}
        monkeypatch.setattr(host, "_read_thread", Mock(return_value=result))
        assert host.status() == expected

    def test_unrelated_recipient_and_unavailable_backend(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Stale recipients and missing backend responses block delivery."""
        host = native(tmp_path)
        monkeypatch.setattr(host, "_read_thread", Mock(return_value={"thread": {"id": "other"}}))
        assert host.status() == "stale"
        monkeypatch.setattr(host, "_read_thread", Mock(side_effect=Empty))
        assert host.status() == "bridge-failed"

    def test_wrong_build_and_noncanonical_uuid_fail_closed(self, tmp_path: Path) -> None:
        """Names and uninspected builds cannot reach the queue command."""
        data = manifest_data(tmp_path)
        with pytest.raises(ValueError, match="inspected executable"):
            CodexQueue(tmp_path / "codex.exe", TrialManifest.from_dict(data))
        data.update(host="codex", build="0.154.0", thread="00000000000040008000000000000001")
        with pytest.raises(ValueError, match="exact thread UUID"):
            CodexQueue(tmp_path / "codex.exe", TrialManifest.from_dict(data))

    def test_initialized_proxy_reads_metadata_without_resuming(self, tmp_path: Path,
                                                              monkeypatch: pytest.MonkeyPatch) -> None:
        """A real WebSocket peer accepts initialization and a metadata read only."""
        host = native(tmp_path)
        response: JsonObject = {"thread": {"id": host.manifest.thread, "cliVersion": "0.154.0", "status": {"type": "idle"}}}
        peer = ProxyPeer(response)
        spawn = Mock(return_value=peer.process)
        monkeypatch.setattr("tools.wait_evidence.prototype.subprocess.Popen", spawn)
        assert host.status() == "idle"
        sent = peer.requests
        assert [row["method"] for row in sent] == ["initialize", "initialized", "thread/read"]
        assert sent[-1]["params"] == {"threadId": host.manifest.thread, "includeTurns": False}
        assert spawn.call_args.args[0][-4:] == ["app-server", "proxy", "--sock", str(host.socket)]
        assert spawn.call_args.kwargs["env"]["CODEX_HOME"] == str(host.manifest.home)
        peer.process.terminate.assert_called_once()

    @pytest.mark.parametrize(("exit_code", "stdout", "receipt"), [(0, "accepted\n", "accepted"),
                                                                  (0, "", "queue-exit-0"), (1, "", None)])
    def test_queue_preserves_profile_home_and_acceptance_only(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                                            exit_code: int, stdout: str, receipt: str | None) -> None:  # noqa: PLR0913 - Three protocol result cases.
        """Use frozen routing settings and distinguish acceptance from uncertainty."""
        host = native(tmp_path, profile="selected")
        invoke = Mock(return_value=Mock(returncode=exit_code, stdout=stdout))
        monkeypatch.setattr("tools.wait_evidence.prototype.subprocess.run", invoke)
        assert host.send("exact message") == receipt
        assert invoke.call_args.args[0] == [str(tmp_path / "codex.exe"), "-p", "selected", "queue",
                                            "--remote", f"unix://{host.socket}",
                                            "--thread", host.manifest.thread, "--message", "exact message"]
        assert invoke.call_args.kwargs["env"]["CODEX_HOME"] == str(host.manifest.home)


# eof
