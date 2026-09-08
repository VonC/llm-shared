"""Unit tests for Step 5 resume CLI support operations and terminal output."""
# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

from __future__ import annotations

import json
from argparse import Namespace
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from tools import review_exchange_cli as launcher
from tools import review_exchange_cli_resume as subject
from tools.llm_nature import LlmNature
from tools.review_exchange_models import Actor, ArtifactState, ReviewExchangeError
from tools.review_exchange_ownership import OwnershipFailure, OwnershipRejectedError
from tools.review_resume import ResumeAction

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_status_models import ExchangeStatus

_SUCCESS_EXIT = 0
_MIGRATION_BLOCKED_EXIT = 2
_STOP_EXIT = 3


class FakeEntry:
    """Provide the minimal trusted status facts used by the resume CLI."""

    def __init__(self, state: ArtifactState = ArtifactState.REQUEST_PENDING) -> None:
        """Build one request-pending candidate with stable selection details."""
        self.state = state
        self.identity = SimpleNamespace(to_dict=lambda: {"slug": "resume"})
        self.reviewed_document = "docs/plan.v0.11.0.resume.md"
        self.umbrella = None
        self.implementation_step = "5"
        self.round_number = 1
        self.occurrence = 1
        self.requestor_llm_nature = SimpleNamespace(value=LlmNature.CODEX, evidence_dicts=list)
        self.reviewer_llm_nature = SimpleNamespace(value=LlmNature.CLAUDE, evidence_dicts=list)


def _args(operation: str, **values: object) -> Namespace:
    """Return one parser-shaped namespace for a support operation."""
    return Namespace(operation=operation, role=None, trusted_host_hint=None,
                     poll_interval=1.0, **values)


class TestResumeCliSupport:
    """Exercise migration, inspection, discovery, claim, and wait result paths."""

    def test_operation_membership_and_migration_results(self, monkeypatch: pytest.MonkeyPatch,
                                                         tmp_path: Path) -> None:
        """Migration operations render ready, blocked, and unsupported results."""
        ready = SimpleNamespace(state=SimpleNamespace(value="ready"), diagnostics=(),
                                configuration=SimpleNamespace(relative_home=".reviews"))
        blocked = SimpleNamespace(state=SimpleNamespace(value="blocked"), diagnostics=("bad",),
                                  configuration=SimpleNamespace(relative_home=".reviews"))
        migration = SimpleNamespace(migration_check=lambda: ready, migrate=lambda _: ready)
        monkeypatch.setattr(subject, "ReviewArtifactMigration", lambda **_: migration)
        assert subject.is_resume_operation("migration-check")
        assert not subject.is_resume_operation("status")
        assert subject.execute_resume_operation(_args("migration-check"), tmp_path)[1] == _SUCCESS_EXIT
        assert subject.execute_resume_operation(_args("migrate-artifacts"), tmp_path)[1] == _SUCCESS_EXIT
        monkeypatch.setattr(subject, "_wait_any_request", lambda _args, _root: ({"outcome": "idle"}, _SUCCESS_EXIT))
        assert subject.execute_resume_operation(_args("wait-any-request"), tmp_path)[1] == _SUCCESS_EXIT
        migration.migration_check = lambda: blocked
        assert subject.execute_resume_operation(_args("migrate-artifacts"), tmp_path)[1] == _MIGRATION_BLOCKED_EXIT
        with pytest.raises(ReviewExchangeError):
            subject.execute_resume_operation(_args("unknown"), tmp_path)

    def test_inspection_maps_status_and_role_decision(self, monkeypatch: pytest.MonkeyPatch,
                                                       tmp_path: Path) -> None:
        """Inspection reports the pure reviewer route from trusted status evidence."""
        entry = FakeEntry()
        status = SimpleNamespace(outcome=subject.ReviewStatusOutcome.TRUSTWORTHY,
                                 exchanges=(entry,))
        monkeypatch.setattr(subject, "ExchangeStatus", FakeEntry)
        monkeypatch.setattr(subject, "collect_review_status", lambda *_: status)
        monkeypatch.setattr(subject.LlmNatureDetector, "detect",
                            lambda *_args, **_kwargs: SimpleNamespace(nature=LlmNature.CLAUDE,
                                                                        diagnostic=None))
        payload, code = subject.execute_resume_operation(_args("resume-inspect"), tmp_path)
        assert code == 0
        assert payload["action"] == ResumeAction.REVIEW_REQUEST.value
        assert "ownership_generation" not in payload
        status.outcome = subject.ReviewStatusOutcome.UNTRUSTWORTHY
        with pytest.raises(ReviewExchangeError):
            subject.execute_resume_operation(_args("resume-inspect"), tmp_path)

    def test_discovery_handles_status_and_claim_boundaries(self, monkeypatch: pytest.MonkeyPatch,
                                                           tmp_path: Path) -> None:
        """Discovery filters requests and retains only a successful claim capability."""
        entry = FakeEntry()
        status = SimpleNamespace(outcome=subject.ReviewStatusOutcome.TRUSTWORTHY,
                                 exchanges=(entry, FakeEntry(ArtifactState.ANSWER_PENDING)))
        monkeypatch.setattr(subject, "ExchangeStatus", FakeEntry)
        monkeypatch.setattr(subject, "collect_ready_review_requests", lambda *_: status)
        discovery = subject._RequestDiscovery(tmp_path)
        assert discovery.rescan() == (entry,)
        status.outcome = subject.ReviewStatusOutcome.UNTRUSTWORTHY
        with pytest.raises(ReviewExchangeError):
            discovery.rescan()
        status.exchanges = (entry, FakeEntry(ArtifactState.ABANDONED_ANSWER))
        assert discovery.rescan() == (entry,)
        entry.state = ArtifactState.ABANDONED_REQUEST
        assert discovery.rescan() == (entry,)
        status.exchanges = (entry, object())
        with pytest.raises(ReviewExchangeError):
            discovery.rescan()
        with pytest.raises(ReviewExchangeError):
            discovery.claim(object())
        with pytest.raises(ReviewExchangeError):
            discovery.capability(entry)

    def test_discovery_claim_retains_capability_and_loses_races(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        """The waiting adapter uses the normal claim seam and keeps its secret local."""
        entry = FakeEntry()
        record = SimpleNamespace(expected_next_actor=Actor.REVIEWER, policy=object())
        store = SimpleNamespace(read_coordination=lambda **_: record)

        class Core:
            """Small deterministic core substitute for the CLI integration seam."""

            def __init__(self, *_: object) -> None:
                self.ownership_capability = object()

            def reclaim(self) -> None:
                """Model the successful locked reviewer claim."""

        monkeypatch.setattr(subject, "ExchangeStatus", FakeEntry)
        monkeypatch.setattr(subject, "_context_from_status", lambda *_: object())
        monkeypatch.setattr(subject.ReviewArtifactConfiguration, "load", lambda *_: object())
        monkeypatch.setattr(subject, "load_review_configuration", lambda *_args, **_kwargs: object())
        monkeypatch.setattr(subject, "derive_artifact_paths", lambda *_args, **_kwargs: object())
        monkeypatch.setattr(subject, "ReviewExchangeStore", lambda _: store)
        monkeypatch.setattr(subject, "ReviewExchangeCore", Core)
        def claim(core: Core, _round: int, _occurrence: int) -> object:
            """Drive the test core's scripted claim outcome."""
            core.reclaim()
            return core.ownership_capability

        monkeypatch.setattr(subject, "claim_discovered_request", claim)
        monkeypatch.setattr(subject, "capability_payload", lambda _: {"ownership_generation": 1})
        discovery = subject._RequestDiscovery(tmp_path)

        assert discovery.claim(entry)
        assert discovery.capability(entry) == {"ownership_generation": 1}

        record.expected_next_actor = Actor.REQUESTOR
        assert not discovery.claim(entry)

        class ClaimedCore(Core):
            """Model a competing reviewer that won the compare-and-swap claim."""

            def reclaim(self) -> None:
                """Raise the non-fatal competing claim signal."""
                raise OwnershipRejectedError(OwnershipFailure("already-claimed", "taken", 1))

        record.expected_next_actor = Actor.REVIEWER
        monkeypatch.setattr(subject, "ReviewExchangeCore", ClaimedCore)
        assert not discovery.claim(entry)

        class FailedCore(Core):
            """Model a claim failure which is not a harmless competing claim."""

            def reclaim(self) -> None:
                """Raise the fatal ownership error unchanged."""
                raise OwnershipRejectedError(OwnershipFailure("invalid", "broken", 1))

        monkeypatch.setattr(subject, "ReviewExchangeCore", FailedCore)
        with pytest.raises(OwnershipRejectedError, match="broken"):
            discovery.claim(entry)

        class NoCapabilityCore(Core):
            """Model a broken core that reports a successful claim without a capability."""

            def __init__(self, *_: object) -> None:
                self.ownership_capability = None

        monkeypatch.setattr(subject, "ReviewExchangeCore", NoCapabilityCore)
        assert not discovery.claim(entry)

    def test_wait_result_and_helpers_cover_terminal_rendering(self, monkeypatch: pytest.MonkeyPatch,
                                                              tmp_path: Path) -> None:
        """Wait rendering keeps capability data on found results only."""
        entry = FakeEntry()
        monkeypatch.setattr(subject, "ExchangeStatus", FakeEntry)
        monkeypatch.setattr(subject.GlobalReviewerWait, "wait",
                            lambda _self: SimpleNamespace(outcome=subject.GlobalWaitOutcome.CANCELLED,
                                                           candidate=None, candidates=(), diagnostic="stop"))
        payload, code = subject._wait_any_request(_args("wait-any-request"), tmp_path)
        assert code == _STOP_EXIT
        assert payload["outcome"] == "cancelled"
        assert subject._known_nature("legacy") is None
        assert subject._candidate_payload(cast("ExchangeStatus", entry))["round"] == 1

    def test_wait_found_and_context_helpers(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        """A found request returns only the selected capability and stable evidence."""
        entry = FakeEntry()
        context_values: list[tuple[object, ...]] = []

        class Discovery:
            """Minimal result seam for terminal wait output."""

            def __init__(self, _root: object) -> None:
                pass

            def rescan(self) -> tuple[object, ...]:
                """Provide the waiter dependency."""
                return ()

            def claim(self, _candidate: object) -> bool:
                """Provide the waiter dependency."""
                return True

            def capability(self, _candidate: object) -> dict[str, object]:
                """Return session-only capability fields."""
                return {"ownership_generation": 1}

        monkeypatch.setattr(subject, "ExchangeStatus", FakeEntry)
        monkeypatch.setattr(subject, "_RequestDiscovery", Discovery)
        monkeypatch.setattr(subject.GlobalReviewerWait, "wait",
                            lambda _self: SimpleNamespace(outcome=subject.GlobalWaitOutcome.FOUND,
                                                           candidate=entry, candidates=(entry,), diagnostic=None))
        def capture_context(*values: object) -> object:
            """Retain the constructor inputs without requiring on-disk review artifacts."""
            context_values.append(values)
            return object()

        monkeypatch.setattr(subject, "ReviewContext", capture_context)
        payload, code = subject._wait_any_request(_args("wait-any-request"), tmp_path)

        assert code == 0
        assert payload["ownership_generation"] == 1
        subject._context_from_status(tmp_path, cast("ExchangeStatus", entry))
        assert context_values[0][1] == tmp_path / entry.reviewed_document
        assert subject._known_nature(LlmNature.CODEX) is LlmNature.CODEX
        assert subject._wall_clock().tzinfo is not None

    def test_main_prints_resume_adapter_terminal_payload(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path,
    ) -> None:
        """The shared launcher delegates resume operations before normal runtime setup."""
        args = _args("resume-inspect")
        monkeypatch.setattr(launcher, "_parser", lambda: SimpleNamespace(parse_args=lambda _: args))
        monkeypatch.setattr(launcher, "find_project_root", lambda _: tmp_path)
        monkeypatch.setattr(launcher, "is_resume_operation", lambda _: True)
        monkeypatch.setattr(launcher, "execute_resume_operation", lambda *_: ({"outcome": "ready"}, 0))

        assert launcher.main(["resume-inspect"]) == _SUCCESS_EXIT
        assert '"outcome": "ready"' in capsys.readouterr().out

@pytest.mark.parametrize(("error", "outcome", "code"), [
    (KeyboardInterrupt(), "cancelled", 3),
    (OSError("disk unavailable"), "operational-failure", 2),
    (RuntimeError("observer unavailable"), "operational-failure", 2),
])
def test_wait_failure_is_one_quiet_terminal_result(  # noqa: PLR0913 - terminal scenarios and isolated IO fixtures
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str],
    error: BaseException, outcome: str, code: int,
) -> None:
    """Host interruption and operational errors leave no waiter artifact or capability."""

    def fail(_args: object, _root: object) -> None:
        """Inject the failure at the real terminal adapter boundary."""
        raise error

    monkeypatch.setattr(subject, "_wait_any_request", fail)
    monkeypatch.setattr(launcher, "find_project_root", lambda _: tmp_path)
    assert launcher.main(["wait-any-request"]) == code
    output = capsys.readouterr()
    payload = json.loads(output.out)
    assert payload["outcome"] == outcome
    assert {"operation", "outcome", "identity", "candidates", "diagnostic"} <= payload.keys()
    assert "ownership_token" not in payload
    assert not output.err
    assert not tuple(tmp_path.iterdir())
