"""Record which tests proved the lifecycle CPU ceiling on this checkout.

User decision of 2026-11-02, the CPU stability band: CPU-load variation must
stop costing extra walks while the ceiling stays enforced. One rule holds for
every test. Its ceiling is ``test_lifecycle_limit``, or the measured CPU of its
accepted exception when that is higher. A test is proven once a measured run
saw its setup-through-teardown CPU at or below its ceiling. A proven test
passes up to its band top, ``test_lifecycle_cpu_band_factor`` times its
ceiling, without a rerun. A test that was never proven, or lands above its band
top, is held to its ceiling. A proven test measured above its ceiling on
``test_lifecycle_cpu_drift_runs`` consecutive runs, in the band or above it,
loses its proof, so a real slowdown cannot stay in the band. A later run at or
below its ceiling proves it again. A proof holds only while the CPU that earned
it stays at or below the test's current ceiling, so lowering a ceiling, in
``pyproject.toml`` or with ``-o`` for one run, never keeps a looser proof. Only
a lifecycle whose call passed with no other failure is a measured run.

The record is untracked and per checkout: ``a.test-lifecycle-cpu.local.json``
in the review artifact home. Its ``nodes`` object belongs to the gate, which
updates it once per run on the controller. Its ``exceptions`` object belongs to
whoever accepts a slow test, as ``ghog exclude`` accepts a slow call: each entry
gives the measured CPU, the improvement already attempted and the reason the
cost stays, and raises that test's ceiling to the measured CPU; the band and
the drift guard then apply to that ceiling. The gate keeps that object as
written, rejects an entry without all three fields, and lists every exception
at the end of a run. A fresh clone has no record and starts strict. The
wall-clock limit is not part of the band.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Final, cast

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Mapping
    from pathlib import Path

    import pytest

RECORD_NAME: Final = "a.test-lifecycle-cpu.local.json"
_SCHEMA: Final = 1
_IGNORE_BYTES: Final = b"*\n"
_GROUP_SUFFIX: Final = re.compile(r"@[A-Za-z0-9._-]+$")
_NO_HOME: Final = "no ignored artifact home; nothing recorded"
_ABOUT: Final = (
    "nodes: written by tests/simulation_policy.py after each measured run. "
    "exceptions: kept as written, one entry per accepted slow test: "
    '"<node id>": {"cpu": <measured seconds>, "attempted": "<improvement tried>", '
    '"reason": "<why the cost stays>"}.'
)


def record_key(nodeid: str) -> str:
    """Return the node id without the xdist ``loadgroup`` suffix.

    Args:
        nodeid: A pytest node id, possibly ending in ``@<group>``.

    Returns:
        The id a test keeps across serial and distributed runs.
    """
    return _GROUP_SUFFIX.sub("", nodeid)


@dataclass(frozen=True, slots=True)
class NodeState:
    """One test's proof, its consecutive runs above the ceiling and last CPU.

    ``proven_cpu`` is the CPU of the run that earned the proof. The proof holds
    only while it stays at or below the test's current ceiling, so a proof
    earned under a looser ceiling, set for one run with ``-o`` or lowered in
    the project since, grants no band. A record written without it falls back
    to the last CPU.
    """

    proven: bool
    over_runs: int
    cpu: float
    proven_cpu: float | None = None

    @property
    def earned(self) -> float:
        """Return the CPU that earned the proof, or the last CPU in an older record."""
        return self.cpu if self.proven_cpu is None else self.proven_cpu

    def holds(self, ceiling: float) -> bool:
        """Tell whether the proof still holds under this ceiling."""
        return self.proven and self.earned <= ceiling


@dataclass(frozen=True, slots=True)
class CpuException:
    """One accepted slow test: measured CPU, attempted improvement, reason."""

    cpu: float
    attempted: str
    reason: str


@dataclass(frozen=True, slots=True)
class BandPolicy:
    """The default ceiling, the band factor for proven tests, and the drift guard."""

    ceiling: float
    factor: float
    drift_runs: int

    @classmethod
    def from_ini(cls, getini: Callable[[str], object]) -> BandPolicy:
        """Read the policy from the visible pytest configuration.

        Args:
            getini: The pytest ini reader.

        Returns:
            The configured ceiling, band factor and drift run count.
        """
        ceiling = setting(getini, "test_lifecycle_limit", lambda value: value > 0, "seconds above 0")
        factor = setting(getini, "test_lifecycle_cpu_band_factor", lambda value: value >= 1, "a multiple of at least 1")
        drift_runs = setting(
            getini, "test_lifecycle_cpu_drift_runs",
            lambda value: value >= 1 and value.is_integer(), "a whole number of runs, at least 1",
        )
        return cls(ceiling, factor, int(drift_runs))

    def band_top(self, ceiling: float) -> float:
        """Return what a proven test with this ceiling may use."""
        return ceiling * self.factor


def setting(getini: Callable[[str], object], key: str, valid: Callable[[float], bool], expected: str) -> float:
    """Read one lifecycle limit a project sets, refusing a value that switches it off.

    Args:
        getini: The pytest ini reader; ``pyproject.toml`` or ``-o`` sets the value.
        key: The ini key.
        valid: Whether a finite number is acceptable for this key.
        expected: What an acceptable value is, for the refusal.

    Returns:
        The configured number.

    Raises:
        ValueError: When the value is not a finite number ``valid`` accepts.
    """
    raw = cast("str", getini(key))
    try:
        value = float(raw)
    except ValueError:
        value = math.nan
    if not (math.isfinite(value) and valid(value)):
        message = f"{key} = {raw!r} in the pytest configuration: expected {expected}"
        raise ValueError(message)
    return value


def advance(state: NodeState | None, cpu: float, ceiling: float, drift_runs: int) -> NodeState:
    """Return a test's proof after one measured run.

    Args:
        state: The recorded proof, ``None`` for a test never recorded.
        cpu: The measured lifecycle CPU seconds.
        ceiling: The test's ceiling, raised only by an accepted exception.
        drift_runs: Consecutive runs above the ceiling that cost the proof.

    Returns:
        The proof the next run starts from.
    """
    if cpu <= ceiling:
        return NodeState(proven=True, over_runs=0, cpu=cpu, proven_cpu=cpu)
    if state is None or not state.holds(ceiling):
        return NodeState(proven=False, over_runs=0, cpu=cpu)
    over_runs = state.over_runs + 1
    if over_runs >= drift_runs:
        return NodeState(proven=False, over_runs=0, cpu=cpu)
    return NodeState(proven=True, over_runs=over_runs, cpu=cpu, proven_cpu=state.earned)


@dataclass(frozen=True, slots=True)
class LifecycleRecord:
    """Recorded proofs and accepted exceptions, keyed by :func:`record_key`."""

    nodes: Mapping[str, NodeState] = field(default_factory=dict[str, NodeState])
    exceptions: Mapping[str, CpuException] = field(default_factory=dict[str, CpuException])
    rejected: tuple[str, ...] = ()

    def ceiling(self, key: str, policy: BandPolicy) -> float:
        """Return the test's ceiling; an exception may raise it, never lower it."""
        exception = self.exceptions.get(key)
        return policy.ceiling if exception is None else max(policy.ceiling, exception.cpu)

    def proven(self, key: str, policy: BandPolicy) -> bool:
        """Tell whether the test holds a proof under its current ceiling."""
        state = self.nodes.get(key)
        return state is not None and state.holds(self.ceiling(key, policy))

    def limit(self, key: str, policy: BandPolicy) -> float:
        """Return the CPU a run may use: its band top only for a proven test."""
        ceiling = self.ceiling(key, policy)
        return policy.band_top(ceiling) if self.proven(key, policy) else ceiling

    def advanced(self, measured: Mapping[str, float], policy: BandPolicy) -> LifecycleRecord:
        """Return the record after one run's measured lifecycles."""
        nodes = dict(self.nodes)
        for key, cpu in measured.items():
            nodes[key] = advance(nodes.get(key), cpu, self.ceiling(key, policy), policy.drift_runs)
        return replace(self, nodes=nodes)


def _seconds(value: object, *, positive: bool = False) -> float | None:
    """Return a finite, non-negative JSON number, or ``None``."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    number = float(value)
    if not math.isfinite(number) or number < 0 or (positive and number == 0):
        return None
    return number


def _text(value: object) -> str | None:
    """Return a non-blank JSON string, or ``None``."""
    return value if isinstance(value, str) and value.strip() else None


def _object(value: object, what: str) -> dict[str, object]:
    """Return a JSON object or refuse the record naming what was wrong."""
    if not isinstance(value, dict):
        message = f"{what} is not a JSON object"
        raise TypeError(message)
    return cast("dict[str, object]", value)


def _count(value: object) -> int | None:
    """Return a non-negative JSON integer, or ``None``."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _node(key: str, value: object) -> NodeState:
    """Return one recorded proof or refuse the record."""
    fields = _object(value, f"node {key}")
    proven, over_runs, cpu = fields.get("proven"), _count(fields.get("over_runs")), _seconds(fields.get("cpu"))
    earned = fields.get("proven_cpu")
    proven_cpu = None if earned is None else _seconds(earned)
    if not isinstance(proven, bool) or over_runs is None or cpu is None or (earned is not None and proven_cpu is None):
        message = f"node {key} needs proven, over_runs and cpu, and a valid proven_cpu when present"
        raise TypeError(message)
    return NodeState(proven, over_runs, cpu, proven_cpu)


def _exception(value: object) -> CpuException | None:
    """Return one accepted exception, or ``None`` when its evidence is missing."""
    if not isinstance(value, dict):
        return None
    fields = cast("dict[str, object]", value)
    cpu = _seconds(fields.get("cpu"), positive=True)
    attempted, reason = _text(fields.get("attempted")), _text(fields.get("reason"))
    if cpu is None or attempted is None or reason is None:
        return None
    return CpuException(cpu, attempted, reason)


def parse_record(text: str) -> tuple[LifecycleRecord, dict[str, object]]:
    """Read a record and keep the whole document it came from.

    Args:
        text: The record file content.

    Returns:
        The record, and the parsed document whose other keys a write keeps.

    Raises:
        ValueError: When the text is not JSON; the gate then stays strict.
        TypeError: When the JSON is not a record; the gate then stays strict.
    """
    document = _object(json.loads(text), "record")
    nodes = {key: _node(key, value) for key, value in _object(document.get("nodes", {}), "nodes").items()}
    exceptions: dict[str, CpuException] = {}
    rejected: list[str] = []
    for key, value in _object(document.get("exceptions", {}), "exceptions").items():
        accepted = _exception(value)
        if accepted is None:
            rejected.append(key)
        else:
            exceptions[key] = accepted
    return LifecycleRecord(nodes, exceptions, tuple(rejected)), document


def render_record(document: Mapping[str, object], nodes: Mapping[str, NodeState]) -> str:
    """Write the proofs into the document, one sorted line per test.

    Args:
        document: The document read before the update; its other keys stay.
        nodes: The proofs to write.

    Returns:
        The complete record text.
    """
    head = {key: value for key, value in document.items() if key != "nodes"}
    head.setdefault("schema", _SCHEMA)
    head.setdefault("about", _ABOUT)
    head.setdefault("exceptions", {})
    lines = [f"{json.dumps(key)}: {json.dumps(_node_fields(state))}" for key, state in sorted(nodes.items())]
    body = "{}" if not lines else "{\n    " + ",\n    ".join(lines) + "\n  }"
    return f'{json.dumps(head, indent=2)[:-2]},\n  "nodes": {body}\n}}\n'


def _node_fields(state: NodeState) -> dict[str, object]:
    """Return one proof as its record fields; ``proven_cpu`` only once earned."""
    fields: dict[str, object] = {"proven": state.proven, "over_runs": state.over_runs, "cpu": state.cpu}
    if state.proven_cpu is not None:
        fields["proven_cpu"] = state.proven_cpu
    return fields


def _unignored_home(root: Path, relative: str) -> bool:
    """Treat a home without its exact catch-all ignore file as unsafe.

    ``ReviewArtifactConfiguration`` asks Git whether the home is tracked. Every
    xdist worker loads the gate, so this check reads the home's ``.gitignore``
    instead of starting one Git process per worker.
    """
    try:
        return (root / relative / ".gitignore").read_bytes() != _IGNORE_BYTES
    except OSError:
        return True


def artifact_record_path(root: Path) -> Path | None:
    """Return the record path in an existing, ignored artifact home.

    Args:
        root: The project root.

    Returns:
        The record path, or ``None`` when no ignored home exists yet.
    """
    try:
        home = ReviewArtifactConfiguration.load(root, tracked_directory=_unignored_home).home
    except (ReviewExchangeError, OSError):
        return None
    return home / RECORD_NAME if home.is_dir() else None


def _read(path: Path) -> tuple[LifecycleRecord, dict[str, object]]:
    """Read the record; a missing file is an empty record."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return LifecycleRecord(), {}
    return parse_record(text)


def _write(path: Path, text: str) -> None:
    """Replace the record through a side file, so a reader never sees half."""
    side = path.with_name(f"{path.name}.tmp")
    side.write_text(text, encoding="utf-8")
    side.replace(path)


@dataclass(frozen=True, slots=True)
class SaveOutcome:
    """Where a run's proofs went, which tests lost theirs, and any problem."""

    path: Path | None
    lost: tuple[str, ...] = ()
    problem: str | None = None


@dataclass(frozen=True, slots=True)
class LifecycleGate:
    """The per-process CPU and wall limits, read once when pytest starts."""

    policy: BandPolicy
    wall_limit: float
    record: LifecycleRecord
    path: Path | None
    problem: str | None = None

    @classmethod
    def load(cls, root: Path, getini: Callable[[str], object]) -> LifecycleGate:
        """Read the policy and this checkout's record; a damaged record is strict.

        Args:
            root: The project root.
            getini: The pytest ini reader.

        Returns:
            The gate every lifecycle of this process is judged by.
        """
        policy = BandPolicy.from_ini(getini)
        wall_limit = setting(getini, "test_lifecycle_wall_limit", lambda value: value > 0, "seconds above 0")
        path = artifact_record_path(root)
        if path is None:
            return cls(policy, wall_limit, LifecycleRecord(), None, _NO_HOME)
        try:
            record, _ = _read(path)
        except (OSError, ValueError, TypeError) as error:
            return cls(policy, wall_limit, LifecycleRecord(), path, f"{path.name} unusable, strict limits apply: {error}")
        return cls(policy, wall_limit, record, path)

    @classmethod
    def strict(cls, ceiling: float, wall_limit: float) -> LifecycleGate:
        """Return a gate with no record: every test is held to the ceiling."""
        return cls(BandPolicy(ceiling, 1.0, 1), wall_limit, LifecycleRecord(), None)

    def cpu_limit(self, key: str) -> float:
        """Return the CPU seconds this run of the test may use."""
        return self.record.limit(key, self.policy)

    def describe(self, key: str) -> str:
        """Explain the CPU limit chosen for one test, for its failure message."""
        exception = self.record.exceptions.get(key)
        basis = "accepted exception" if exception is not None else "ceiling"
        proof = "proven here, band applies" if self.record.proven(key, self.policy) else "not proven here"
        ceiling = self.record.ceiling(key, self.policy)
        return f"{basis} {ceiling:.3f}s, {proof}, band top {self.policy.band_top(ceiling):.3f}s"

    def save(self, measured: Mapping[str, float]) -> SaveOutcome:
        """Advance the proofs of one run's measured tests and replace the record.

        Args:
            measured: CPU seconds of every measured lifecycle, by record key.

        Returns:
            The record path, the tests that lost their proof, and any problem.
        """
        if self.path is None:
            return SaveOutcome(None, problem=self.problem or _NO_HOME)
        if not measured:
            return SaveOutcome(self.path)
        try:
            current, document = _read(self.path)
        except (OSError, ValueError, TypeError) as error:
            return SaveOutcome(self.path, problem=f"{self.path.name} not updated: {error}")
        updated = current.advanced(measured, self.policy)
        policy = self.policy
        lost = tuple(sorted(key for key in measured if current.proven(key, policy) and not updated.proven(key, policy)))
        try:
            _write(self.path, render_record(document, updated.nodes))
        except OSError as error:
            return SaveOutcome(self.path, lost, f"{self.path.name} not written: {error}")
        return SaveOutcome(self.path, lost)


class BandCollector:
    """Gather measured lifecycles on the controller and update the record once.

    xdist forwards each teardown report, with its ``user_properties``, to the
    controller, so only this process writes the record and workers never race.
    """

    def __init__(self, gate: LifecycleGate) -> None:
        """Start with the gate this session's workers loaded."""
        self._gate = gate
        self._measured: dict[str, float] = {}
        self._outcome: SaveOutcome | None = None

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Keep the CPU of every measured lifecycle, by record key."""
        if report.when != "teardown":
            return
        properties = dict(report.user_properties)
        if properties.get("test_lifecycle_measured") is True:
            self._measured[record_key(report.nodeid)] = float(cast("float", properties["test_lifecycle_cpu_seconds"]))

    def pytest_sessionfinish(self) -> None:
        """Write the run's proofs before the terminal summary reports them."""
        self._outcome = self._gate.save(self._measured)

    def pytest_terminal_summary(self, terminalreporter: pytest.TerminalReporter) -> None:
        """Show the record, band passes, lost proofs and every exception."""
        terminalreporter.write_sep("-", "lifecycle CPU band")
        for line in self.summary_lines():
            terminalreporter.write_line(line)

    def summary_lines(self) -> list[str]:
        """Return the summary, so a run shows what the band tolerated."""
        outcome = self._outcome or SaveOutcome(self._gate.path)
        band = self._band_passes()
        drift_runs = self._gate.policy.drift_runs
        return [
            f"record {outcome.path or 'none'}: {len(self._measured)} measured, {len(band)} in the band, {len(outcome.lost)} lost proof",
            *(f"band pass: {key} CPU={cpu:.6f}s, {self._gate.describe(key)}" for key, cpu in band),
            *(f"proof lost after {drift_runs} runs above the ceiling: {key}" for key in outcome.lost),
            *_exception_lines(self._gate.record),
            *_problem_lines(self._gate.problem, outcome.problem),
        ]

    def _band_passes(self) -> list[tuple[str, float]]:
        """Return the measured tests above their ceiling that the band let pass."""
        gate = self._gate
        return [
            (key, cpu) for key, cpu in sorted(self._measured.items())
            if gate.record.ceiling(key, gate.policy) < cpu <= gate.cpu_limit(key)
        ]


def _exception_lines(record: LifecycleRecord) -> Iterator[str]:
    """Yield every accepted and every rejected exception."""
    for key, exception in sorted(record.exceptions.items()):
        yield f"accepted exception: {key} CPU={exception.cpu:.6f}s; attempted: {exception.attempted}; reason: {exception.reason}"
    for key in record.rejected:
        yield f"rejected exception, needs cpu, attempted and reason: {key}"


def _problem_lines(*problems: str | None) -> Iterator[str]:
    """Yield each distinct record problem once."""
    for problem in dict.fromkeys(problems):
        if problem == _NO_HOME:
            yield problem
        elif problem is not None:
            yield f"record problem: {problem}"


# eof
