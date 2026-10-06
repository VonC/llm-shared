"""Acceptance tests of the saved proof of a walk (v0.13.0 full_suite_levels).

Step 2: one test per proof row of the design's "Acceptance Cases", driven
through ``cli.main`` on a ``tmp_path`` project with the process boundary
faked: a noop on stronger saved proof; an upgrade reusing check and affected;
a proof kept below a higher-gate failure and capped by a contradicted lower
gate, the timing pass included; a legacy one-line marker read as no proof; a
detached walk keeping its level and evidence in ``ghog status``; and the
timing fingerprint capping a saved ``speed`` proof at ``cov`` while a Python
file change invalidates the whole proof. Setup errors (exit 5), a project
without a pytest suite (exit 9) and an affected, full or timing child
interrupted before any failure (each of pytest's interruption banners, a
``pytest.exit`` returning 0 or 1 included) judge no gate and leave the saved
marker byte for byte as it was. Such a child crashes its step and earns no
proof, in a walk without a saved marker as in a direct ``ghog full``. A
failure reported before the interruption still caps the proof. A source check.bat fixes is
the one the walk proves, and a saved proof of the sources before the fix does
not survive it.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.groundhog_acceptance_support import (
    QueueSpawns,
    closing_line_of,
    make_deps,
    passing_transcript,
)
from tests.unit.tools.test_groundhog_acceptance_levels.support import (
    AFFECTED_OK,
    CHECK_OK,
    CRASHING,
    FAILED_THEN_INTERRUPTED,
    FULL_GAP,
    FULL_GREEN,
    INTERRUPTED_CHILDREN,
    INTERRUPTION_IDS,
    TESTS_FAILING,
    TIMINGS_GREEN,
    project,
    run,
    save,
    saved,
    slow_transcript,
)
from tools.groundhog import cli, exclusions, floor, reporting_nextstep, snapshot, status
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_NOT_PYTEST_PROJECT,
    EXIT_OBJECTIVE_MET,
    EXIT_RUN_LIVE,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
)

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

    from tests.unit.tools.test_groundhog_acceptance_levels.support import Child

# The parallel speed chain up to a green covered worker run.
_PARALLEL_FULL_GREEN = [CHECK_OK, AFFECTED_OK, FULL_GREEN]


def test_stronger_saved_proof_is_a_noop(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Saved speed on unchanged sources meets a default walk: nothing runs."""
    save(project(tmp_path), FullLevel.SPEED)
    code, spawns = run(tmp_path, ["day"], [])
    assert code == EXIT_OBJECTIVE_MET
    assert spawns.commands == []
    out = capsys.readouterr().out
    assert reporting_nextstep.noop_line(FullLevel.NONE, FullLevel.SPEED) in out
    assert closing_line_of(out).endswith("full=none src=default proof=speed reused=all scope=whole")


def test_lower_saved_proof_is_upgraded(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Saved none and --full=cov: check and affected reused, the full run only."""
    save(project(tmp_path), FullLevel.NONE)
    code, spawns = run(tmp_path, ["day", "--full=cov"], [FULL_GREEN])
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == 1
    out = capsys.readouterr().out
    assert "== ghog check == reused from snapshot (saved proof=none)" in out
    assert "== ghog affected --no-cov == reused from snapshot (saved proof=none)" in out
    assert closing_line_of(out).endswith("full=cov src=param proof=cov reused=check+affected scope=whole")
    assert saved(tmp_path) is FullLevel.COV


def test_higher_gate_failure_keeps_the_lower_proof(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Saved pass and a coverage gap at cov: exit 3, proof stays pass."""
    save(project(tmp_path), FullLevel.PASS)
    code, _ = run(tmp_path, ["day", "--full=cov"], [FULL_GAP])
    assert code == EXIT_COVERAGE_GAP
    assert "proof=pass" in closing_line_of(capsys.readouterr().out)
    assert saved(tmp_path) is FullLevel.PASS


def test_full_failure_caps_the_saved_proof(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Saved pass and a full failure at cov: proof none; --full=pass walks again."""
    save(project(tmp_path), FullLevel.PASS)
    code, _ = run(tmp_path, ["day", "--full=cov"], [TESTS_FAILING])
    assert code == EXIT_TEST_FAILURES
    assert "proof=none" in closing_line_of(capsys.readouterr().out)
    assert saved(tmp_path) is FullLevel.NONE
    code, spawns = run(tmp_path, ["day", "--full=pass"], [FULL_GREEN])
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == 1


def _timing_pass(root: Path, timings: Child, *options: str) -> int:
    """Run a parallel speed walk whose timing pass ends with one child."""
    code, _ = run(root, ["day", "--full=speed", *options], [*_PARALLEL_FULL_GREEN, timings])
    return code


def test_timing_pass_failure_caps_the_earned_proof(tmp_path: Path) -> None:
    """A failing timing pass after a green full run leaves proof none."""
    root = project(tmp_path, parallel=True)
    assert _timing_pass(root, TESTS_FAILING) == EXIT_TEST_FAILURES
    assert saved(root) is FullLevel.NONE
    code, spawns = run(root, ["day", "--full=cov"], [FULL_GREEN])
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == 1


def test_timing_pass_crash_caps_the_earned_proof(tmp_path: Path) -> None:
    """A crashing timing pass contradicts pass: proof none, --full=pass walks."""
    root = project(tmp_path, parallel=True)
    assert _timing_pass(root, CRASHING) == EXIT_SUITE_CRASH
    assert saved(root) is FullLevel.NONE


def test_forced_timing_failure_caps_the_saved_proof(tmp_path: Path) -> None:
    """--force over saved speed and a failing timing pass: proof none."""
    root = project(tmp_path, parallel=True)
    save(root, FullLevel.SPEED)
    code, spawns = run(root, ["day", "--full=speed", "--force"], [*_PARALLEL_FULL_GREEN, TESTS_FAILING])
    assert code == EXIT_TEST_FAILURES
    assert len(spawns.commands) == len(("check", "affected", "full", "timings"))
    assert saved(root) is FullLevel.NONE


def test_timing_outliers_keep_the_cov_proof(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Outliers only in the timing pass: exit 8, proof cov."""
    root = project(tmp_path, parallel=True)
    assert _timing_pass(root, (slow_transcript(None), 0)) == EXIT_DURATION_OUTLIERS
    assert "proof=cov" in closing_line_of(capsys.readouterr().out)
    assert saved(root) is FullLevel.COV
    assert _timing_pass(root, TIMINGS_GREEN, "--force") == EXIT_OBJECTIVE_MET
    assert saved(root) is FullLevel.SPEED


def test_legacy_marker_is_no_proof(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A one-line digest marker proves nothing: the default walk runs, proof none."""
    root = project(tmp_path)
    snapshot.marker_path(root).write_text(f"{snapshot.source_digest(root)}\n", encoding="utf-8")
    code, spawns = run(root, ["day"], [CHECK_OK, AFFECTED_OK])
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == len(("check", "affected"))
    assert "reused=none" in closing_line_of(capsys.readouterr().out)
    assert saved(root) is FullLevel.NONE


def test_detached_walk_keeps_its_level_and_evidence(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """--detach --full=cov: the survivor runs at cov; ghog status shows its evidence."""
    root = project(tmp_path)
    running: list[str] = []

    def _survivor(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        del log_path, preamble, cwd
        walk_deps = make_deps(_RecordingSpawns(root, running))
        assert cli.main(command[2:], walk_deps) == EXIT_OBJECTIVE_MET
        return 1

    deps = cli.Deps(detach_factory=_survivor, sleep=lambda _seconds: None)
    code = cli.main(["day", "--detach", "--full=cov", "--root", str(root), "--llm"], deps)
    assert code == EXIT_RUN_LIVE
    assert "full=cov src=param scope=whole proof=pending" in running[0]
    capsys.readouterr()
    assert cli.main(["status", "--root", str(root), "--llm"]) == EXIT_OBJECTIVE_MET
    done = status.read_status(root)
    assert done is not None
    assert "full=cov src=param proof=cov reused=none scope=whole exit=0" in done.line


class _RecordingSpawns(QueueSpawns):
    """A green three-step walk recording the status line at each spawn."""

    def __init__(self, root: Path, lines: list[str]) -> None:
        """Script the walk and the status recording.

        Args:
            root: The project root holding the status file.
            lines: Receives the status line seen at each spawn.
        """
        super().__init__([CHECK_OK, AFFECTED_OK, FULL_GREEN])
        self._root = root
        self._lines = lines

    def __call__(self, command: list[str], cwd: Path) -> subprocess.Popen[str]:
        """Record the status, then return the next canned child.

        Args:
            command: The child command line.
            cwd: The child working directory.

        Returns:
            The canned process, seen as a Popen.
        """
        recorded = status.read_status(self._root)
        self._lines.append("" if recorded is None else recorded.line)
        return super().__call__(command, cwd)


def test_timing_change_keeps_a_lower_saved_proof(tmp_path: Path) -> None:
    """Saved cov and only line 2 or an exclusion changed: --full=cov is a noop."""
    root = project(tmp_path)
    save(root, FullLevel.COV)
    floor.write_floor(root, 0.4, 2.0)
    code, spawns = run(root, ["day", "--full=cov"], [])
    assert (code, spawns.commands) == (EXIT_OBJECTIVE_MET, [])
    exclusions.write_exclusions(root, {"tests/test_slow.py::test_freak": 2.5})
    code, spawns = run(root, ["day", "--full=cov"], [])
    assert (code, spawns.commands) == (EXIT_OBJECTIVE_MET, [])


def test_timing_change_caps_a_saved_speed_proof(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Saved speed and only an exclusion changed: --full=speed upgrades."""
    root = project(tmp_path)
    save(root, FullLevel.SPEED)
    exclusions.write_exclusions(root, {"tests/test_slow.py::test_freak": 2.5})
    code, spawns = run(root, ["day", "--full=speed"], [FULL_GREEN])
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == 1
    assert "reused=check+affected" in closing_line_of(capsys.readouterr().out)


def test_setup_errors_judge_no_gate(tmp_path: Path) -> None:
    """Exit 5 in the full step or the timing pass writes nothing: saved proof stays."""
    root = project(tmp_path, parallel=True)
    save(root, FullLevel.COV)
    no_total = (passing_transcript(4, None), 0)
    code, _ = run(root, ["day", "--full=cov", "--force"], [CHECK_OK, AFFECTED_OK, no_total])
    assert code == EXIT_SETUP_ERROR
    assert saved(root) is FullLevel.COV
    empty = (["no tests ran in 0.01s"], 5)
    code, _ = run(root, ["day", "--full=speed", "--force"], [*_PARALLEL_FULL_GREEN, empty])
    assert code == EXIT_SETUP_ERROR
    assert saved(root) is FullLevel.COV


def test_project_without_a_suite_writes_no_proof(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Exit 9 after check.bat judges no gate: the saved proof is reported and kept."""
    root = project(tmp_path)
    save(root, FullLevel.PASS)

    def _no_suite(_root: Path) -> bool:
        return False

    deps = replace(make_deps(QueueSpawns([CHECK_OK])), pytest_project=_no_suite)
    code = cli.main(["day", "--force", "--root", str(root), "--llm"], deps)
    assert code == EXIT_NOT_PYTEST_PROJECT
    assert saved(root) is FullLevel.PASS
    assert "proof=pass reused=none" in closing_line_of(capsys.readouterr().out)


@pytest.mark.parametrize("interrupted", INTERRUPTED_CHILDREN, ids=INTERRUPTION_IDS)
def test_interrupted_children_keep_the_saved_proof(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    interrupted: Child,
) -> None:
    """An affected, full or timing child interrupted before any failure judges no gate.

    Each of pytest's interruption banners (a bare or messaged
    KeyboardInterrupt, an explicit pytest.exit with its interrupted, failing
    or even zero return code) crashes the step and leaves the saved marker
    byte for byte as it was.
    """
    root = project(tmp_path, parallel=True)
    save(root, FullLevel.SPEED)
    marker = snapshot.marker_path(root).read_bytes()
    for children in (
        [CHECK_OK, interrupted],
        [CHECK_OK, AFFECTED_OK, interrupted],
        [*_PARALLEL_FULL_GREEN, interrupted],
    ):
        code, spawns = run(root, ["day", "--full=speed", "--force"], children)
        assert (code, len(spawns.commands)) == (EXIT_SUITE_CRASH, len(children))
        assert snapshot.marker_path(root).read_bytes() == marker
        assert "proof=speed reused=none" in closing_line_of(capsys.readouterr().out)


@pytest.mark.parametrize("interrupted", INTERRUPTED_CHILDREN, ids=INTERRUPTION_IDS)
def test_interrupted_suite_earns_no_proof(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    interrupted: Child,
) -> None:
    """An interrupted full child crashes and earns nothing, whatever its return code.

    A walk without a saved marker writes none, so the next walk runs again,
    and a direct ghog full at pass claims no proof.
    """
    root = project(tmp_path)
    code, _ = run(root, ["day", "--full=pass"], [CHECK_OK, AFFECTED_OK, interrupted])
    assert (code, snapshot.marker_path(root).exists()) == (EXIT_SUITE_CRASH, False)
    assert closing_line_of(capsys.readouterr().out).endswith("proof=unproven reused=none scope=whole")
    code, _ = run(root, ["full", "--full=pass"], [interrupted])
    assert code == EXIT_SUITE_CRASH
    assert closing_line_of(capsys.readouterr().out).endswith("full=pass src=param proof=unproven scope=whole")


def test_failure_before_an_interruption_still_caps_the_proof(tmp_path: Path) -> None:
    """A failing test reported before the interruption contradicts the full tests."""
    root = project(tmp_path)
    save(root, FullLevel.SPEED)
    code, _ = run(root, ["day", "--full=cov", "--force"], [CHECK_OK, AFFECTED_OK, FAILED_THEN_INTERRUPTED])
    assert code == EXIT_SUITE_CRASH
    assert saved(root) is FullLevel.NONE


def test_python_change_invalidates_the_saved_proof(tmp_path: Path) -> None:
    """Saved speed and a changed Python file: --full=cov walks the whole chain."""
    root = project(tmp_path)
    save(root, FullLevel.SPEED)
    (root / "src" / "mod.py").write_text("VALUE = 2  # changed size\n", encoding="utf-8")
    code, spawns = run(root, ["day", "--full=cov"], [CHECK_OK, AFFECTED_OK, FULL_GREEN])
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == len(("check", "affected", "full"))


class _FixingCheck(QueueSpawns):
    """A recording factory whose check.bat child fixes a source, as a ruff auto-fix does."""

    def __init__(self, root: Path, children: list[Child]) -> None:
        """Script the children and the source the check child rewrites.

        Args:
            root: The project root.
            children: One canned child per expected spawn, check.bat first.
        """
        super().__init__(children)
        self._source = root / "src" / "mod.py"

    def __call__(self, command: list[str], cwd: Path) -> subprocess.Popen[str]:
        """Rewrite the source on the first spawn, then return the next child.

        Args:
            command: The child command line.
            cwd: The child working directory.

        Returns:
            The canned process, seen as a Popen.
        """
        if not self.commands:
            self._source.write_text("VALUE = 1  # fixed by check.bat\n", encoding="utf-8")
        return super().__call__(command, cwd)


def _fixing_walk(root: Path, *flags: str) -> int:
    """Run a green cov walk whose check.bat fixes a source.

    Args:
        root: The project root.
        flags: The extra walk flags.

    Returns:
        The walk exit code.
    """
    spawns = _FixingCheck(root, [CHECK_OK, AFFECTED_OK, FULL_GREEN])
    return cli.main(["day", "--full=cov", *flags, "--root", str(root), "--llm"], make_deps(spawns))


def test_check_fix_proves_the_fixed_sources(tmp_path: Path) -> None:
    """The proof records the sources check.bat fixed: the same walk again is a noop."""
    root = project(tmp_path)
    assert _fixing_walk(root) == EXIT_OBJECTIVE_MET
    assert saved(root) is FullLevel.COV
    code, spawns = run(root, ["day", "--full=cov"], [])
    assert (code, spawns.commands) == (EXIT_OBJECTIVE_MET, [])


def test_check_fix_drops_the_proof_of_the_old_sources(tmp_path: Path) -> None:
    """A saved speed matched before check.bat fixed a source does not survive the fix."""
    root = project(tmp_path)
    save(root, FullLevel.SPEED)
    assert _fixing_walk(root, "--force") == EXIT_OBJECTIVE_MET
    marker = snapshot.read_proof_marker(snapshot.marker_path(root))
    assert marker is not None
    assert (marker.proof, marker.digest) == (FullLevel.COV, snapshot.source_digest(root))


# eof
