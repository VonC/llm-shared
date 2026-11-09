"""Assert declaration announcement ordering, cancellation and combined reporting.

Transport events are explicit observations of xdist's real hook order; the
external compatibility runner separately proves scheduling and worker cleanup.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import cast

import llm_shared_process_audit as audit
import pytest

from tests.unit.tools.shared_lifecycle.inline_session import run_inline


@pytest.fixture
def controller(monkeypatch: pytest.MonkeyPatch) -> tuple[pytest.Config, audit.AuditSession]:
    """Supply isolated controller state without patching the carrying adapter."""
    def no_plugin(_name: str) -> None:
        return None
    config = cast("pytest.Config", type("Config", (), {
        "pluginmanager": SimpleNamespace(getplugin=no_plugin),
    })())
    state = audit.AuditSession(Path())
    hub = audit.AuditHub()
    hub.configs[config] = state
    monkeypatch.setattr(audit, "get_hub", lambda: hub)
    audit.pytest_xdist_setupnodes(config, [object(), object()])
    return config, state


def test_all_workers_must_announce_identical_validated_collection(
    controller: tuple[pytest.Config, audit.AuditSession],
) -> None:
    """The first announcement cannot complete the all-worker barrier."""
    config, state = controller
    nodes = [SimpleNamespace(config=config), SimpleNamespace(config=config)]
    audit.pytest_xdist_node_collection_finished(nodes[0], ["a", "b"])
    assert len(state.announced) == 1 < state.expected_workers
    audit.pytest_xdist_node_collection_finished(nodes[1], ["a", "b"])
    assert len(state.announced) == state.expected_workers == len(nodes)
    assert state.barrier_complete
    for node in nodes:
        node.workeroutput = {audit._RECORDS: []}
        audit.pytest_testnodedown(node, None)


@pytest.mark.parametrize("announced", [False, True])
@pytest.mark.parametrize("error", [None, "cancelled"])
def test_early_exit_never_waits_for_missing_worker(
    controller: tuple[pytest.Config, audit.AuditSession], *, announced: bool, error: str | None,
) -> None:
    """Even a valid peer exiting before the full barrier stops the controller."""
    config, _state = controller
    node = SimpleNamespace(config=config, workeroutput={})
    if announced:
        audit.pytest_xdist_node_collection_finished(node, ["a"])
    with pytest.raises(pytest.UsageError, match="validated collection"):
        audit.pytest_testnodedown(node, error)


@pytest.mark.parametrize("records", [False, True])
def test_post_barrier_crash_preserves_xdist_replacement_handling(
    controller: tuple[pytest.Config, audit.AuditSession], *, records: bool,
) -> None:
    """A crashed worker may omit output; transported usage is still retained."""
    config, state = controller
    nodes = [SimpleNamespace(config=config, workeroutput={}) for _ in range(2)]
    for node in nodes:
        audit.pytest_xdist_node_collection_finished(node, ["a"])
    if records:
        nodes[0].workeroutput[audit._RECORDS] = [
            {"kind": "test", "identity": "test:a", "reason": "caller", "used": True},
        ]
    audit.pytest_testnodedown(nodes[0], "worker crashed")
    assert bool(state.records) is records
    replacement = SimpleNamespace(config=config, workeroutput={audit._RECORDS: []})
    audit.pytest_xdist_node_collection_finished(replacement, ["a"])
    assert len(state.announced) > state.expected_workers
    assert state.barrier_complete
    audit.pytest_testnodedown(replacement, None)
    nodes[1].workeroutput[audit._RECORDS] = []
    audit.pytest_testnodedown(nodes[1], None)


@pytest.mark.parametrize("barrier_complete", [False, True])
@pytest.mark.parametrize("records", [False, True])
def test_keyboard_interrupt_preserves_both_xdist_down_notifications(
    controller: tuple[pytest.Config, audit.AuditSession], *, barrier_complete: bool, records: bool,
) -> None:
    """Xdist reports finish before errordown for a worker keyboard interrupt."""
    config, state = controller
    node = SimpleNamespace(config=config, workeroutput={"exitstatus": pytest.ExitCode.INTERRUPTED})
    if barrier_complete:
        for peer in (node, SimpleNamespace(config=config)):
            audit.pytest_xdist_node_collection_finished(peer, ["a"])
    if records:
        node.workeroutput[audit._RECORDS] = [
            {"kind": "test", "identity": "test:a", "reason": "caller", "used": True},
        ]
    audit.pytest_testnodedown(node, None)
    audit.pytest_testnodedown(node, "keyboard-interrupt")
    assert bool(state.records) is records


@pytest.mark.parametrize("stop_field", ["shouldstop", "shuttingdown"])
def test_controller_shutdown_before_barrier_preserves_original_stop(
    controller: tuple[pytest.Config, audit.AuditSession], monkeypatch: pytest.MonkeyPatch,
    stop_field: str,
) -> None:
    """Collection maxfail can stop xdist before it forwards announcements."""
    config, state = controller
    distributed = SimpleNamespace(**{stop_field: "stopping after 1 failures"})
    def get_distributed(_name: str) -> SimpleNamespace:
        return distributed
    monkeypatch.setattr(config.pluginmanager, "getplugin", get_distributed)
    node = SimpleNamespace(config=config, workeroutput={audit._RECORDS: []})
    audit.pytest_testnodedown(node, None)
    audit.pytest_testnodedown(SimpleNamespace(config=config), "cancelled during shutdown")
    assert not state.barrier_complete
    assert not state.announced
    assert not state.records


def test_replacement_collection_must_still_match_initial_collection(
    controller: tuple[pytest.Config, audit.AuditSession],
) -> None:
    """Completing the initial barrier never waives replacement validation."""
    config, state = controller
    nodes = [SimpleNamespace(config=config) for _ in range(2)]
    for node in nodes:
        audit.pytest_xdist_node_collection_finished(node, ["a"])
    with pytest.raises(pytest.UsageError, match="inconsistent worker collection"):
        audit.pytest_xdist_node_collection_finished(SimpleNamespace(config=config), ["b"])
    assert state.barrier_complete
    assert len(state.announced) == state.expected_workers


def test_invalid_worker_preserves_identifying_usage_error(
    controller: tuple[pytest.Config, audit.AuditSession],
) -> None:
    """An invalid worker terminates with its declaration diagnostic, exit four."""
    config, state = controller
    peer = SimpleNamespace(config=config)
    audit.pytest_xdist_node_collection_finished(peer, ["a"])
    bad = SimpleNamespace(config=config, workeroutput={audit._ERROR: "bad_fixture: empty reason"})
    with pytest.raises(pytest.UsageError, match="bad_fixture: empty reason"):
        audit.pytest_testnodedown(bad, None)
    assert len(state.announced) == 1


def test_inconsistent_collection_fails_before_scheduler_hook_returns(
    controller: tuple[pytest.Config, audit.AuditSession],
) -> None:
    """Xdist calls this hook before add_node_collection or scheduling."""
    config, state = controller
    audit.pytest_xdist_node_collection_finished(SimpleNamespace(config=config), ["a"])
    with pytest.raises(pytest.UsageError, match="inconsistent worker collection"):
        audit.pytest_xdist_node_collection_finished(SimpleNamespace(config=config), ["b"])
    assert len(state.announced) == 1


def test_worker_failure_is_recorded_before_announcement(
    controller: tuple[pytest.Config, audit.AuditSession], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Validation failure retains evidence and cannot reach xdist's announcement."""
    config, _state = controller
    output: dict[str, object] = {}
    monkeypatch.setattr(config, "workeroutput", output, raising=False)
    def invalid(_self: audit.AuditSession, _session: pytest.Session) -> None:
        message = "invalid unused fixture"
        raise pytest.UsageError(message)
    monkeypatch.setattr(audit.AuditSession, "validate", invalid)
    with pytest.raises(pytest.UsageError, match="invalid unused fixture"):
        audit.pytest_collection_finish(cast("pytest.Session", SimpleNamespace(config=config)))
    assert "invalid unused fixture" in str(output[audit._ERROR])
    metadata = cast("dict[str, object]", getattr(audit.pytest_collection_finish, "pytest_impl", {}))
    assert metadata["tryfirst"] is True


def test_worker_records_merge_usage_and_keep_definitions_distinct(
    controller: tuple[pytest.Config, audit.AuditSession],
) -> None:
    """Parameters and workers share identity, but fixture overrides stay distinct."""
    config, state = controller
    nodes = [SimpleNamespace(config=config), SimpleNamespace(config=config)]
    for node in nodes:
        audit.pytest_xdist_node_collection_finished(node, ["a"])
    for used, node in zip((False, True), nodes, strict=True):
        node.workeroutput = {audit._RECORDS: [
            {"kind": "fixture", "identity": "fixture:a", "reason": "service", "used": used},
            {"kind": "test", "identity": "test:a", "reason": "caller", "used": False},
        ]}
        audit.pytest_testnodedown(node, None)
    state.exercise("fixture", "fixture:override", "override")
    assert set(state.records) == {"fixture:a", "test:a", "fixture:override"}
    assert state.records["fixture:a"].used is True
    assert state.records["test:a"].used is False


@pytest.mark.parametrize("payload", [None, {}, [1], [{"kind": "test"}], [
    {"kind": "test", "identity": "test:a", "reason": "r", "used": 1},
], [
    {"kind": "other", "identity": "test:a", "reason": "r", "used": False},
]])
def test_missing_or_malformed_worker_records_fail_identifiably(
    controller: tuple[pytest.Config, audit.AuditSession], payload: object,
) -> None:
    """Missing usage evidence cannot silently become an empty successful report."""
    config, _state = controller
    node = SimpleNamespace(config=config, workeroutput={audit._RECORDS: payload})
    for peer in (node, SimpleNamespace(config=config)):
        audit.pytest_xdist_node_collection_finished(peer, [])
    with pytest.raises(pytest.UsageError, match="worker permission records"):
        audit.pytest_testnodedown(node, None)


def test_successful_worker_cannot_omit_permission_records(
    controller: tuple[pytest.Config, audit.AuditSession],
) -> None:
    """A normal finish must supply usage evidence even when it exercised none."""
    config, state = controller
    node = SimpleNamespace(config=config, workeroutput={})
    for peer in (node, SimpleNamespace(config=config)):
        audit.pytest_xdist_node_collection_finished(peer, [])
    assert state.barrier_complete
    with pytest.raises(pytest.UsageError, match="worker permission records"):
        audit.pytest_testnodedown(node, None)


def test_conflicting_reason_is_not_overwritten(
    controller: tuple[pytest.Config, audit.AuditSession],
) -> None:
    """Two workers must agree about a permission's definition and reason."""
    config, state = controller
    state.exercise("test", "test:a", "first")
    node = SimpleNamespace(config=config, workeroutput={audit._RECORDS: [
        {"kind": "test", "identity": "test:a", "reason": "other", "used": False},
    ]})
    for peer in (node, SimpleNamespace(config=config)):
        audit.pytest_xdist_node_collection_finished(peer, [])
    with pytest.raises(pytest.UsageError, match="conflicting permission"):
        audit.pytest_testnodedown(node, None)
    assert state.records["test:a"].reason == "first"


def test_worker_publishes_detached_permission_records(
    controller: tuple[pytest.Config, audit.AuditSession], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Publish exercised usage before xdist sends output, with no live references."""
    config, state = controller
    permission = state.exercise("fixture", "fixture:service", "worker service")
    permission.used = True
    output: dict[str, object] = {}
    monkeypatch.setattr(config, "workeroutput", output, raising=False)
    audit.pytest_sessionfinish(cast("pytest.Session", SimpleNamespace(config=config)))
    permission.used = False
    assert output[audit._RECORDS] == [{
        "kind": "fixture", "identity": "fixture:service", "reason": "worker service", "used": True,
    }]


def test_audit_only_summary_reports_only_exercised_own_scope_permissions(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """One report separates tests/fixtures, warns unused and omits unentered work."""
    (tmp_path / "conftest.py").write_text("""
import pytest
def pytest_configure(config):
    config.addinivalue_line('markers', 'process_allowed(reason): permission')
@pytest.fixture(params=[1, 2])
def service():
    from llm_shared_process_audit import get_hub
    get_hub().dispatch('os.system', ())
@pytest.fixture
def unentered(): pass
LLM_SHARED_PROCESS_FIXTURES = {service: 'fixture reason', unentered: 'hidden'}
""", encoding="utf-8")
    (tmp_path / "test_case.py").write_text("""
import pytest
@pytest.mark.process_allowed(reason='caller reason')
def test_case(service): pass
""", encoding="utf-8")
    assert run_inline(tmp_path, plugins=(audit,)) == 0
    output = capsys.readouterr().out
    assert output.count("process permissions") == 1
    assert "Test permissions (2)" in output
    assert "Fixture permissions (1)" in output
    assert "fixture reason [used]" in output
    expected_cases = 2
    assert output.count("caller reason [WARNING unused]") == expected_cases
    assert "hidden" not in output
    assert "lifecycle CPU band" not in output
    assert not (tmp_path / ".reviews").exists()


# eof
