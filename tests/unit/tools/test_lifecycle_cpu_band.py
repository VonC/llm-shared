"""Verify the lifecycle CPU stability band decided by the user on 2026-11-02.

A test proven at or below its ceiling on this checkout passes up to its band
top; a test never proven, or above its band top, is held to its ceiling; three
consecutive measured runs above its ceiling cost the proof. A test's ceiling is
0.1 s, or its accepted exception's CPU, and the same rule applies to both
(user answer of 2026-11-02, 10:30). The record lives in
an ignored artifact home under ``tmp_path``. Gate, hook and collector run in
process with synthetic CPU readings and reports; no process is created.
CPU within the effective band or exception limit passes even with wall excess.
"""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import TYPE_CHECKING, Literal, cast

import llm_shared_lifecycle_gate as band
import llm_shared_lifecycle_gate as policy
import pytest
from llm_shared_lifecycle_gate import (
    CpuException,
    LifecycleGate,
    LifecycleRecord,
    NodeState,
)

if TYPE_CHECKING:
    from pathlib import Path

_INI = {
    "test_lifecycle_limit": "0.1", "test_lifecycle_wall_limit": "1.0",
    "test_lifecycle_cpu_band_factor": "2.5", "test_lifecycle_cpu_drift_runs": "3",
}
_POLICY = band.BandPolicy(ceiling=0.1, factor=2.5, drift_runs=3)
_SLOW = {"cpu": 0.3, "attempted": "cached grammar", "reason": "cold import"}
_SLOW_CEILING = 0.3
_SLOW_TOP = 0.75


@pytest.mark.parametrize(("state", "cpu", "expected"), [
    (None, 0.1, NodeState(proven=True, over_runs=0, cpu=0.1, proven_cpu=0.1)),
    (None, 0.2, NodeState(proven=False, over_runs=0, cpu=0.2)),
    (NodeState(proven=False, over_runs=0, cpu=0.3), 0.05, NodeState(proven=True, over_runs=0, cpu=0.05, proven_cpu=0.05)),
    (NodeState(proven=True, over_runs=0, cpu=0.05), 0.2, NodeState(proven=True, over_runs=1, cpu=0.2, proven_cpu=0.05)),
    (NodeState(proven=True, over_runs=1, cpu=0.2, proven_cpu=0.05), 0.3, NodeState(proven=True, over_runs=2, cpu=0.3, proven_cpu=0.05)),
    (NodeState(proven=True, over_runs=2, cpu=0.3, proven_cpu=0.05), 0.2, NodeState(proven=False, over_runs=0, cpu=0.2)),
    (NodeState(proven=True, over_runs=2, cpu=0.3, proven_cpu=0.05), 0.04, NodeState(proven=True, over_runs=0, cpu=0.04, proven_cpu=0.04)),
    (NodeState(proven=True, over_runs=0, cpu=0.3, proven_cpu=0.3), 0.2, NodeState(proven=False, over_runs=0, cpu=0.2)),
    (NodeState(proven=True, over_runs=1, cpu=0.2), 0.2, NodeState(proven=False, over_runs=0, cpu=0.2)),
])
def test_a_run_proves_counts_drift_or_drops_the_proof(state: NodeState | None, cpu: float, expected: NodeState) -> None:
    """At or below the ceiling proves; above it counts toward the drift guard.

    A proof earned above the current ceiling, or one with no ``proven_cpu``
    whose last CPU is above it, no longer holds, so the run is not tolerated.
    """
    assert band.advance(state, cpu, 0.1, 3) == expected


def test_the_band_applies_only_to_proven_tests_and_exceptions_only_raise() -> None:
    """Unproven tests keep their ceiling; an exception never lowers it, and gets the band."""
    record = LifecycleRecord(
        nodes={"p": NodeState(proven=True, over_runs=0, cpu=0.05), "u": NodeState(proven=False, over_runs=0, cpu=0.2)},
        exceptions={"x": CpuException(0.3, "cached grammar", "cold import"), "y": CpuException(0.05, "a", "r")},
    )
    assert [record.limit(key, _POLICY) for key in ("p", "u", "new", "x", "y")] == [0.25, 0.1, 0.1, 0.3, 0.1]
    proven = LifecycleRecord(
        nodes={key: NodeState(proven=True, over_runs=0, cpu=0.05) for key in ("x", "y")},
        exceptions=record.exceptions,
    )
    assert [proven.limit(key, _POLICY) for key in ("x", "y")] == pytest.approx([_SLOW_TOP, 0.25])


def test_the_record_key_drops_only_the_loadgroup_suffix() -> None:
    """A node keeps one key across serial and ``--dist loadgroup`` runs."""
    assert band.record_key("t.py::test[a@b]@resume-concurrency") == "t.py::test[a@b]"
    assert band.record_key("t.py::test[a@b]") == "t.py::test[a@b]"


def test_rendering_keeps_the_human_part_and_round_trips_the_proofs() -> None:
    """The gate rewrites ``nodes`` only, one sorted line per test."""
    exceptions = {"slow": {"cpu": 0.3, "attempted": "cached grammar", "reason": "cold import"}}
    nodes = {
        "b": NodeState(proven=True, over_runs=1, cpu=0.2, proven_cpu=0.0625),
        "a": NodeState(proven=False, over_runs=0, cpu=0.125),
    }
    text = band.render_record({"exceptions": exceptions, "note": "kept", "nodes": {}}, nodes)
    record, document = band.parse_record(text)
    assert record.nodes == nodes
    assert record.exceptions == {"slow": CpuException(0.3, "cached grammar", "cold import")}
    assert (document["note"], document["exceptions"], document["schema"]) == ("kept", exceptions, 1)
    assert text.index('"a": {') < text.index('"b": {')
    assert band.render_record({}, {}).endswith('"nodes": {}\n}\n')


@pytest.mark.parametrize("entry", [
    {"cpu": 0.3, "reason": "r"},
    {"cpu": 0.3, "attempted": " ", "reason": "r"},
    {"cpu": 0, "attempted": "a", "reason": "r"},
    {"cpu": "0.3", "attempted": "a", "reason": "r"},
    {"cpu": True, "attempted": "a", "reason": "r"},
    "0.3",
])
def test_an_exception_without_its_evidence_is_rejected(entry: object) -> None:
    """Measured CPU, the attempted improvement and the reason are all required."""
    record, _ = band.parse_record(json.dumps({"exceptions": {"slow": entry}}))
    assert (record.exceptions, record.rejected) == ({}, ("slow",))


@pytest.mark.parametrize(("text", "error"), [
    ("{", ValueError),
    ("[]", TypeError),
    ('{"nodes": []}', TypeError),
    ('{"exceptions": []}', TypeError),
    ('{"nodes": {"a": {"proven": 1, "over_runs": 0, "cpu": 0.1}}}', TypeError),
    ('{"nodes": {"a": {"proven": true, "over_runs": true, "cpu": 0.1}}}', TypeError),
    ('{"nodes": {"a": {"proven": true, "over_runs": -1, "cpu": 0.1}}}', TypeError),
    ('{"nodes": {"a": {"proven": true, "over_runs": 0, "cpu": NaN}}}', TypeError),
    ('{"nodes": {"a": {"proven": true, "over_runs": 0, "cpu": 0.1, "proven_cpu": "0.1"}}}', TypeError),
])
def test_a_damaged_record_is_refused(text: str, error: type[Exception]) -> None:
    """The gate never guesses a proof from a damaged record."""
    with pytest.raises(error):
        band.parse_record(text)


def _home(root: Path, ignore: bytes = b"*\n") -> Path:
    """Create an artifact home with the given ignore file."""
    home = root / ".reviews"
    home.mkdir()
    (home / ".gitignore").write_bytes(ignore)
    return home


def _load(root: Path) -> LifecycleGate:
    """Load the gate as each pytest process does."""
    return LifecycleGate.load(root, _INI.__getitem__)


def test_the_gate_records_proofs_and_the_drift_guard_drops_them(tmp_path: Path) -> None:
    """A first run proves, the band tolerates two runs above, the third drops it."""
    home = _home(tmp_path)
    first = _load(tmp_path)
    assert (first.path, first.cpu_limit("t"), first.problem) == (home / band.RECORD_NAME, 0.1, None)
    assert first.save({}) == band.SaveOutcome(first.path)
    assert first.save({"t": 0.05, "s": 0.2}).problem is None
    assert (_load(tmp_path).cpu_limit("t"), _load(tmp_path).cpu_limit("s")) == (0.25, 0.1)
    outcomes = [_load(tmp_path).save({"t": 0.2}) for _ in range(3)]
    assert [outcome.lost for outcome in outcomes] == [(), (), ("t",)]
    assert _load(tmp_path).cpu_limit("t") == _POLICY.ceiling


def test_an_exception_ceiling_gets_the_band_and_the_drift_guard(tmp_path: Path) -> None:
    """An exception at 0.3 s passes up to 0.75 s once proven, until 3 runs above 0.3 s."""
    path = _home(tmp_path) / band.RECORD_NAME
    path.write_text(json.dumps({"exceptions": {"x": _SLOW}}), encoding="utf-8")
    assert _load(tmp_path).cpu_limit("x") == _SLOW_CEILING
    assert _load(tmp_path).save({"x": 0.28}).problem is None
    proven = _load(tmp_path)
    assert proven.cpu_limit("x") == pytest.approx(_SLOW_TOP)
    assert proven.describe("x") == "accepted exception 0.300s, proven here, band applies, band top 0.750s"
    outcomes = [_load(tmp_path).save({"x": 0.31}) for _ in range(3)]
    assert [outcome.lost for outcome in outcomes] == [(), (), ("x",)]
    assert _load(tmp_path).cpu_limit("x") == _SLOW_CEILING


def test_a_project_sets_its_own_ceiling_band_factor_and_drift_runs(tmp_path: Path) -> None:
    """The ini keys, not the defaults, decide the ceiling, the band top and the drift guard."""
    _home(tmp_path)
    ini = {**_INI, "test_lifecycle_limit": "0.2", "test_lifecycle_cpu_band_factor": "2", "test_lifecycle_cpu_drift_runs": "2"}

    def load() -> LifecycleGate:
        return LifecycleGate.load(tmp_path, ini.__getitem__)

    assert load().cpu_limit("t") == pytest.approx(0.2)
    assert load().save({"t": 0.15}).problem is None
    assert load().cpu_limit("t") == pytest.approx(0.4)
    assert [load().save({"t": 0.3}).lost for _ in range(2)] == [(), ("t",)]


def test_a_proof_earned_under_a_looser_ceiling_grants_no_band(tmp_path: Path) -> None:
    """A run with ``-o test_lifecycle_limit=0.5`` cannot prove a test for the 0.1 s ceiling."""
    _home(tmp_path)
    loose = {**_INI, "test_lifecycle_limit": "0.5"}
    assert LifecycleGate.load(tmp_path, loose.__getitem__).save({"t": 0.3}).problem is None
    assert LifecycleGate.load(tmp_path, loose.__getitem__).cpu_limit("t") == pytest.approx(1.25)
    strict = _load(tmp_path)
    assert (strict.cpu_limit("t"), strict.describe("t")) == (0.1, "ceiling 0.100s, not proven here, band top 0.250s")
    assert strict.save({"t": 0.08}).lost == ()
    assert _load(tmp_path).cpu_limit("t") == _POLICY.band_top(_POLICY.ceiling)


@pytest.mark.parametrize(("key", "value"), [
    ("test_lifecycle_limit", "0"),
    ("test_lifecycle_limit", "fast"),
    ("test_lifecycle_cpu_band_factor", "0.5"),
    ("test_lifecycle_cpu_band_factor", "nan"),
    ("test_lifecycle_cpu_drift_runs", "0"),
    ("test_lifecycle_cpu_drift_runs", "1.5"),
    ("test_lifecycle_wall_limit", "inf"),
])
def test_a_setting_that_would_switch_the_gate_off_is_refused(tmp_path: Path, key: str, value: str) -> None:
    """A zero, negative, infinite or partial value is a usage error naming its key."""
    ini = {**_INI, key: value}
    with pytest.raises(ValueError, match=key):
        LifecycleGate.load(tmp_path, ini.__getitem__)
    config = SimpleNamespace(rootpath=tmp_path, getini=ini.__getitem__, stash=pytest.Stash())
    with pytest.raises(pytest.UsageError, match=key):
        policy.pytest_configure(cast("pytest.Config", config))


@pytest.mark.parametrize("ignore", [None, b"", b"*\nkeep\n"])
def test_without_an_ignored_home_the_gate_is_strict_and_writes_nothing(tmp_path: Path, ignore: bytes | None) -> None:
    """No home, or a home Git may track, never receives the record."""
    if ignore is not None:
        _home(tmp_path, ignore)
    gate = _load(tmp_path)
    assert (gate.path, gate.cpu_limit("t")) == (None, 0.1)
    assert gate.save({"t": 0.05}).problem == "no ignored artifact home; nothing recorded"
    assert not (tmp_path / ".reviews" / band.RECORD_NAME).exists()


def test_a_damaged_record_keeps_the_gate_strict_and_the_file_untouched(tmp_path: Path) -> None:
    """A damaged record is reported, not overwritten, and grants no band."""
    path = _home(tmp_path) / band.RECORD_NAME
    path.write_text('{"nodes": {"t": {"proven": true}}}', encoding="utf-8")
    gate = _load(tmp_path)
    assert gate.cpu_limit("t") == _POLICY.ceiling
    assert gate.problem is not None
    assert "not updated" in str(gate.save({"t": 0.05}).problem)
    assert path.read_text(encoding="utf-8") == '{"nodes": {"t": {"proven": true}}}'


def test_a_failed_write_is_reported_not_raised(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The run's verdict never depends on writing the record."""
    _home(tmp_path)
    gate = _load(tmp_path)

    def refuse(_path: object, _text: object) -> None:
        message = "locked"
        raise OSError(message)

    monkeypatch.setattr(band, "_write", refuse)
    assert "not written: locked" in str(gate.save({"t": 0.05}).problem)


def _gate(nodes: dict[str, NodeState]) -> LifecycleGate:
    """Return a gate with a record and no file."""
    return LifecycleGate(_POLICY, 1.0, LifecycleRecord(nodes=nodes), None)


def _judge(gate: LifecycleGate, cpu: float, *, call: Literal["passed", "failed"] = "passed", wall: float = 0.03) -> pytest.TestReport:
    """Run one lifecycle's reports through the real accounting hook."""
    config = SimpleNamespace(stash=pytest.Stash())
    config.stash[policy._GATE] = gate
    item = cast("pytest.Item", SimpleNamespace(stash=pytest.Stash(), config=config, nodeid="t.py::test@group"))
    item.stash[policy._CPU] = cpu
    phases: tuple[tuple[Literal["setup", "call", "teardown"], Literal["passed", "failed"]], ...] = (
        ("setup", "passed"), ("call", call), ("teardown", "passed"),
    )
    reports = [
        pytest.TestReport(item.nodeid, ("t.py", 0, "test"), {}, outcome, None, when, duration=wall / 3)
        for when, outcome in phases
    ]
    for report in reports:
        hook = policy.pytest_runtest_makereport(item, cast("pytest.CallInfo[None]", None))
        next(hook)
        with pytest.raises(StopIteration):
            hook.send(report)
    return reports[-1]


@pytest.mark.parametrize("wall", [0.03, 1.0, 6.0])
@pytest.mark.parametrize(("proven", "cpu", "outcome", "limit"), [
    (True, 0.2, "passed", 0.25),
    (True, 0.25, "passed", 0.25),
    (True, 0.3, "failed", 0.25),
    (False, 0.2, "failed", 0.1),
    (False, 0.1, "passed", 0.1),
])
def test_the_hook_judges_each_lifecycle_by_its_own_limit(proven: bool, cpu: float, outcome: str, limit: float, wall: float) -> None:  # noqa: FBT001
    """The band top applies regardless of wall time; diagnostics retain both."""
    report = _judge(_gate({"t.py::test": NodeState(proven=proven, over_runs=0, cpu=0.05)}), cpu, wall=wall)
    properties = dict(report.user_properties)
    assert (report.outcome, properties["test_lifecycle_cpu_limit"], properties["test_lifecycle_measured"]) == (outcome, limit, True)
    if outcome == "failed":
        assert "band top 0.250s" in str(report.longrepr)


@pytest.mark.parametrize("proven", [False, True])
@pytest.mark.parametrize("offset", [-0.01, 0.0, 0.01])
def test_exception_limit_and_drift_survive_wall_excess(offset: float, *, proven: bool) -> None:
    """Exceptions keep their effective limit and CPU observations with slow wall."""
    key = "t.py::test"
    gate = LifecycleGate(_POLICY, 1.0, LifecycleRecord(
        nodes={key: NodeState(proven=proven, over_runs=0, cpu=0.05)},
        exceptions={key: CpuException(0.3, "cached grammar", "cold import")},
    ), None)
    limit = _SLOW_TOP if proven else _SLOW_CEILING
    cpu = limit + offset
    report = _judge(gate, cpu, wall=6.0)
    assert report.outcome == ("failed" if offset > 0 else "passed")
    properties = dict(report.user_properties)
    assert properties["test_lifecycle_cpu_limit"] == pytest.approx(limit)
    assert properties["test_lifecycle_seconds"] == pytest.approx(6.0)
    collector = band.BandCollector(gate)
    collector.pytest_runtest_logreport(report)
    assert collector._measured == {key: cpu}


def test_a_failed_call_is_not_a_measured_run() -> None:
    """Only a lifecycle whose call passed can prove or drift a test."""
    report = _judge(_gate({}), 0.05, call="failed")
    assert dict(report.user_properties)["test_lifecycle_measured"] is False


def _teardown(nodeid: str, cpu: float, *, measured: bool) -> pytest.TestReport:
    """Return a teardown report shaped as xdist forwards it to the controller."""
    properties = [["test_lifecycle_cpu_seconds", cpu], ["test_lifecycle_measured", measured]]
    return pytest.TestReport(nodeid, ("t.py", 0, "t"), {}, "passed", None, "teardown", duration=0.01, user_properties=cast("list[tuple[str, object]]", properties))


def test_the_controller_records_measured_runs_and_reports_the_band(tmp_path: Path) -> None:
    """Measured teardown reports update the record; the summary lists the band."""
    path = _home(tmp_path) / band.RECORD_NAME
    path.write_text(json.dumps({
        "nodes": {"t.py::slow": {"proven": True, "over_runs": 0, "cpu": 0.05}},
        "exceptions": {"t.py::kept": {"cpu": 0.3, "attempted": "cached grammar", "reason": "cold import"}, "t.py::bare": {"cpu": 0.3}},
    }), encoding="utf-8")
    collector = band.BandCollector(_load(tmp_path))
    collector.pytest_runtest_logreport(_teardown("t.py::slow@group", 0.2, measured=True))
    collector.pytest_runtest_logreport(_teardown("t.py::failed", 0.05, measured=False))
    call = pytest.TestReport("t.py::call", ("t.py", 0, "c"), {}, "passed", None, "call", duration=0.01)
    collector.pytest_runtest_logreport(call)
    collector.pytest_sessionfinish()
    lines: list[str] = []

    def write_sep(_sep: str, title: str) -> None:
        lines.append(title)

    reporter = SimpleNamespace(write_sep=write_sep, write_line=lines.append)
    collector.pytest_terminal_summary(cast("pytest.TerminalReporter", reporter))
    assert lines[0] == "lifecycle CPU band"
    assert lines[1] == f"record {path}: 1 measured, 1 in the band, 0 lost proof"
    assert lines[2].startswith("band pass: t.py::slow CPU=0.200000s, ceiling 0.100s, proven here")
    assert lines[3:] == [
        "accepted exception: t.py::kept CPU=0.300000s; attempted: cached grammar; reason: cold import",
        "rejected exception, needs cpu, attempted and reason: t.py::bare",
    ]
    assert band.parse_record(path.read_text(encoding="utf-8"))[0].nodes["t.py::slow"].over_runs == 1


def test_the_summary_names_lost_proofs_and_record_problems() -> None:
    """A lost proof and a missing home are both visible at the end of a run."""
    collector = band.BandCollector(LifecycleGate(_POLICY, 1.0, LifecycleRecord(), None, "no ignored artifact home; nothing recorded"))
    collector.pytest_sessionfinish()
    assert collector.summary_lines() == ["record none: 0 measured, 0 in the band, 0 lost proof", "no ignored artifact home; nothing recorded"]
    assert list(band._problem_lines("damaged", None, "damaged")) == ["record problem: damaged"]
    lost = band.BandCollector(_gate({}))
    lost._outcome = band.SaveOutcome(None, ("t.py::slow",))
    assert lost.summary_lines()[1] == "proof lost after 3 runs above the ceiling: t.py::slow"


@pytest.mark.parametrize("worker", [False, True])
def test_only_the_controller_collects(tmp_path: Path, *, worker: bool) -> None:
    """Every process loads the gate; only the controller registers the collector."""
    registered: list[str] = []

    def register(_plugin: object, name: str) -> None:
        registered.append(name)

    config = SimpleNamespace(
        rootpath=tmp_path, getini=_INI.__getitem__, stash=pytest.Stash(),
        pluginmanager=SimpleNamespace(register=register),
    )
    if worker:
        config.workerinput = {}
    policy.pytest_configure(cast("pytest.Config", config))
    assert config.stash[policy._GATE].cpu_limit("t") == _POLICY.ceiling
    assert registered == ([] if worker else ["lifecycle-cpu-band"])


# eof
