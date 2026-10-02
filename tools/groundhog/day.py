"""The ghog day walk: check, affected --no-cov, then the full step(s) of a level.

Split out of ``commands.py`` so that module stays under the repo line budget
(Q22): the walk orchestration and its per-step timestamp headers live here,
while the individual step executors (check and the pytest runs) stay in
``commands.py``. ``status.py`` dispatches the ``day`` subcommand to
:func:`walk`.

Each step is bracketed by a ``started``/``ended`` header carrying a full local
timestamp and, on the end header, the step duration measured on the injected
monotonic clock. The headers land in ``a.ghog.log`` (and the mirrored
envelope), so a stale log read after a silent no-op shows old timestamps
instead of passing as a fresh green result.

Fix (v0.13.0 full_suite_levels, Step 2): the walk runs by level, with saved
proof. It first reads the whole-suite proof marker
(``snapshot.effective_proof``) and asks ``proof.decide``:

- a noop when the valid saved proof meets the requested level: nothing runs,
  not even check.bat, and the noop line names both levels;
- an upgrade when the saved proof is below it: check.bat and the affected
  step are reused (their headers say so), and only the full step runs;
- otherwise the whole chain: check.bat, the affected tests, then, above the
  default level ``none``, the full step at the level. At ``none`` the walk
  stops after a green affected step with the skip success line. At ``speed``
  in a parallel project a green full step is followed by a timed sequential
  ``timings`` step, whose exit becomes the walk's.

The walk records each gate it judged: a failure contradicts the level that
gate guards (check.bat or the affected tests: ``none``; the full tests or the
timing pass: ``pass``; the coverage gate: ``cov``; the duration outliers:
``speed``). It then accumulates the proof (``proof.accumulate``) and rewrites
the marker, or removes it when nothing is proven. The marker records the
digest the test steps ran on, taken again after a green check.bat, whose
auto-fixes may move it; a saved proof matched on the earlier digest then no
longer counts. A step that judged no gate
(``proof.judges_gate``: a setup error, a project without a pytest suite, or a
pytest child interrupted before it reported any failure) stops the walk and
writes nothing, nor does an interruption of the walk itself, so the saved
proof stays as it was. The walk ends with its own ``ghog day`` closing line,
which repeats the last step's counters and appends the ``full=``, ``src=``,
``proof=``, ``reused=`` and ``scope=`` keys. :func:`walk` returns that
outcome and replaces the former code-only ``run_day``, since the lifecycle
bracket records the evidence too.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Final

from tools.groundhog import (
    commands,
    evidence,
    progress,
    reporting,
    reporting_nextstep,
    runner,
    snapshot,
)
from tools.groundhog.evidence import Reused, RunOutcome
from tools.groundhog.levels import FullLevel, effective_level
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    RunStats,
)
from tools.groundhog.proof import (
    Decision,
    Gate,
    accumulate,
    decide,
    earned_by_direct_full,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.groundhog.context import Deps, Invocation
    from tools.groundhog.snapshot import EffectiveProof

# The gate a failing full step or timing pass contradicts, by exit code.
_FULL_GATES: Final = {
    EXIT_TEST_FAILURES: Gate.FULL_TESTS,
    EXIT_SUITE_CRASH: Gate.FULL_TESTS,
    EXIT_COVERAGE_GAP: Gate.COVERAGE,
    EXIT_DURATION_OUTLIERS: Gate.DURATIONS,
}
# The step labels of the walk headers.
_CHECK_LABEL: Final = "check"
_AFFECTED_LABEL: Final = "affected --no-cov"


@dataclass
class _Walk:
    """The running record of one walk: what it earned, contradicted and ran.

    Attributes:
        invocation: The day invocation.
        deps: The injectable seams.
        level: The level the walk is asked to prove.
        state: The digest the test steps run on and the saved proof valid on
            it, moved after a green check.bat.
        earned: The highest level the walk fully established, ``None`` while
            it established nothing.
        contradicted: The gates that failed anywhere in the walk.
        judged: False once a step stopped the walk without judging a gate.
        last: The outcome of the last pytest step, for the closing line.
    """

    invocation: Invocation
    deps: Deps
    level: FullLevel
    state: EffectiveProof
    earned: FullLevel | None = None
    contradicted: list[Gate] = field(default_factory=list[Gate])
    judged: bool = True
    last: RunOutcome | None = None

    @property
    def project(self) -> str:
        """Return the consuming project name, the report prefix."""
        return self.invocation.root.name

    def step(self, sub: str, *, no_cov: bool = False) -> Invocation:
        """Derive the invocation of one walk step, carrying the level.

        Args:
            sub: The step subcommand.
            no_cov: Whether the step disables coverage, the check step's
                value being irrelevant.

        Returns:
            The step invocation, flagged as inside the walk.
        """
        return replace(self.invocation, sub=sub, no_cov=no_cov, in_walk=True)

    def run_pytest_step(self, label: str, sub: str, *, no_cov: bool) -> int:
        """Run one timed pytest step and keep its outcome for the closing line.

        Args:
            label: The step header label.
            sub: The step subcommand.
            no_cov: Whether the step disables coverage.

        Returns:
            The step exit code.
        """
        step = self.step(sub, no_cov=no_cov)
        self.last = _timed_step(
            self.project,
            label,
            self.deps,
            lambda: commands.run_tests_outcome(step, self.deps),
        )
        if not self.last.judged:
            self.judged = False
        return self.last.code


def walk(invocation: Invocation, deps: Deps) -> RunOutcome:
    """Walk the chain at the invocation's level, with saved proof.

    The walk stops at the first non-green step, whose report already names
    the fix to apply; the fixing, and the loop around it, stay with the
    caller. A missing check.bat skips to the test steps (Q10). Each step is
    bracketed by timestamped start/end headers (:func:`_timed_step`).

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        The walk outcome: the exit code of the first non-green step, or of
        the last step; the evidence of the closing and done lines.
    """
    level = effective_level(invocation.level, runner.SUB_DAY)
    state = snapshot.effective_proof(
        invocation.root,
        snapshot.WHOLE_SCOPE_KEY,
        snapshot.WHOLE_SCOPE_FINGERPRINT,
    )
    # effective_proof already matched the digest and capped a timing change.
    decision = decide(
        state.proof,
        level,
        digest_matches=True,
        timing_matches=True,
        force=invocation.force,
    )
    saved = state.proof
    if saved is not None and decision is Decision.NOOP:
        commands.emit_summary(["", reporting_nextstep.noop_line(level, saved)])
        return _close(invocation, EXIT_OBJECTIVE_MET, _evidence(invocation, saved, Reused.ALL), None)
    record = _Walk(invocation, deps, level, state)
    if saved is not None and decision is Decision.UPGRADE:
        for label in (_CHECK_LABEL, _AFFECTED_LABEL):
            commands.emit_summary(["", reporting.step_reused_line(record.project, label, saved)])
        record.earned = FullLevel.NONE
        code = _full_steps(record)
        reused = Reused.CHECK_AFFECTED
    else:
        code = _whole_chain(record)
        reused = Reused.NONE
    proof = _record_proof(record)
    return _close(invocation, code, _evidence(invocation, proof, reused), record.last)


def _whole_chain(record: _Walk) -> int:
    """Run check.bat, the affected tests, then the full step(s) above ``none``.

    Args:
        record: The walk record.

    Returns:
        The exit code of the first non-green step, or of the last step.
    """
    check = record.step(runner.SUB_CHECK)
    code = _timed_step(
        record.project,
        _CHECK_LABEL,
        record.deps,
        lambda: commands.run_check(check, record.deps),
    )
    if code != EXIT_OBJECTIVE_MET:
        record.contradicted.append(Gate.CHECK_OR_AFFECTED)
        return code
    # check.bat may have fixed sources: the test steps judge the fixed ones.
    record.state = record.state.on_sources(snapshot.source_digest(record.invocation.root))
    code = record.run_pytest_step(_AFFECTED_LABEL, runner.SUB_AFFECTED, no_cov=True)
    if not record.judged:
        return code
    if code != EXIT_OBJECTIVE_MET:
        record.contradicted.append(Gate.CHECK_OR_AFFECTED)
        return code
    record.earned = FullLevel.NONE
    if record.level is FullLevel.NONE:
        commands.emit_summary(["", reporting_nextstep.success_line(FullLevel.NONE)])
        return code
    return _full_steps(record)


def _full_steps(record: _Walk) -> int:
    """Run the full step at the walk's level, then the timing pass at parallel speed.

    Args:
        record: The walk record, its check and affected steps green or reused.

    Returns:
        The exit code of the full step, or of the timing pass after it.
    """
    parallel = runner.parallel_enabled(record.invocation.root)
    code = record.run_pytest_step(runner.SUB_FULL, runner.SUB_FULL, no_cov=False)
    if not record.judged:
        return code
    _judge(record, code, earned_by_direct_full(record.level, code, parallel=parallel))
    if code != EXIT_OBJECTIVE_MET or not (record.level is FullLevel.SPEED and parallel):
        return code
    code = record.run_pytest_step(runner.SUB_TIMINGS, runner.SUB_TIMINGS, no_cov=True)
    if record.judged:
        _judge(record, code, FullLevel.SPEED if code == EXIT_OBJECTIVE_MET else None)
    return code


def _judge(record: _Walk, code: int, earned: FullLevel | None) -> None:
    """Record what one full step or timing pass established and contradicted.

    Args:
        record: The walk record.
        code: The step exit code.
        earned: The level the step fully established, ``None`` for nothing.
    """
    if earned is not None:
        record.earned = earned
    gate = _FULL_GATES.get(code)
    if gate is not None:
        record.contradicted.append(gate)


def _record_proof(record: _Walk) -> FullLevel | None:
    """Accumulate the walk's proof and rewrite or remove the marker.

    Args:
        record: The finished walk record, with the digest its test steps ran
            on and the saved proof valid on it.

    Returns:
        The proof valid after the walk; the saved proof valid on that digest
        when the walk judged no gate, in which case nothing is written.
    """
    if not record.judged:
        return record.state.proof
    proof = accumulate(record.earned, record.state.proof, record.contradicted)
    snapshot.save_proof(
        record.invocation.root,
        snapshot.WHOLE_SCOPE_KEY,
        snapshot.WHOLE_SCOPE_FINGERPRINT,
        record.state.digest,
        proof,
    )
    return proof


def _evidence(
    invocation: Invocation,
    proof: FullLevel | None,
    reused: Reused,
) -> evidence.RunEvidence:
    """Build the walk's evidence: level, source, proof, reuse and scope.

    Args:
        invocation: The day invocation.
        proof: The proof valid after the walk, ``None`` for ``unproven``.
        reused: What the walk took from the snapshot.

    Returns:
        The evidence of the closing and done lines.
    """
    return replace(evidence.for_invocation(invocation, proof), reused=reused)


def _close(
    invocation: Invocation,
    code: int,
    walk_evidence: evidence.RunEvidence,
    last: RunOutcome | None,
) -> RunOutcome:
    """Print the walk's own closing line and return its outcome.

    Args:
        invocation: The day invocation.
        code: The walk exit code.
        walk_evidence: The walk's level, proof, reuse and scope.
        last: The last pytest step's outcome, whose counters and closing
            values the line repeats; ``None`` when no pytest step ran.

    Returns:
        The walk outcome, with the closing values it printed.
    """
    stats, metrics = RunStats(), reporting.ClosingMetrics(reporting.COV_SKIPPED)
    if last is not None and last.metrics is not None:
        stats, metrics = last.stats, last.metrics
    metrics = replace(metrics, evidence=walk_evidence.closing_keys())
    closing = reporting.closing_line(
        invocation.root.name,
        progress.sub_label(invocation),
        stats,
        code,
        metrics,
    )
    commands.emit_summary(["", closing])
    return RunOutcome(code, walk_evidence, stats, metrics)


def _timed_step[T](
    project: str,
    label: str,
    deps: Deps,
    run: Callable[[], T],
) -> T:
    """Run one day-walk step framed by a separator rule and timestamp headers.

    A dashed rule and a start header are emitted before the step, an end
    header and a closing rule after it; each header carries the local
    wall-clock time, and the end header also carries the step duration
    measured on the injected monotonic clock.

    Args:
        project: The consuming project name, the report prefix.
        label: The step label (``check``, ``affected --no-cov``, ``full``,
            ``timings``).
        deps: The injectable seams, for the monotonic duration clock.
        run: The step thunk returning its exit code or outcome.

    Returns:
        The step result, unchanged.
    """
    commands.emit_summary(
        [
            reporting.step_open_banner(project),
            reporting.step_started_line(project, label, reporting.now_local()),
            reporting.step_rule(project),
        ],
    )
    start = deps.clock()
    result = run()
    duration = max(0.0, deps.clock() - start)
    commands.emit_summary(
        [
            reporting.step_rule(project),
            reporting.step_ended_line(project, label, reporting.now_local(), duration),
            reporting.step_close_banner(project),
        ],
    )
    return result


# eof
