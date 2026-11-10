"""The day shortcut retains selection boundaries, prepared probes and truthful proof."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, NoReturn

import pytest

from tests.unit.tools.groundhog_acceptance_support import (
    QueueSpawns,
    make_deps,
    passing_transcript,
)
from tools import pytest_plugin_environment as env
from tools.groundhog import cli, selection, snapshot
from tools.groundhog.context import Deps, Invocation
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import Mode
from tools.scope_capture import WHOLE_SCOPE

if TYPE_CHECKING:
    from pathlib import Path

type Transcript = tuple[list[str], int]


@pytest.mark.parametrize(("raw", "expected"), [(None, 75), ("0", 0), ("75.5", 75.5),
                                          ("100", 100), ("bad", None), ("nan", None),
                                          ("inf", None), ("-1", None), ("101", None)])
def test_threshold(raw: str | None, expected: float | None) -> None:
    """Accept finite percentages and reject malformed configuration."""
    deps = make_deps(QueueSpawns([]), {} if raw is None else {selection.ENV_PERCENT: raw})
    assert selection.threshold(deps) == expected


@pytest.mark.parametrize(("affected", "skip"), [(74, False), (75, False), (76, True), (100, True), (0, False)])
def test_day_skips_only_above_threshold(tmp_path: Path, capsys: pytest.CaptureFixture[str], affected: int, *, skip: bool) -> None:
    """Only a strictly greater selection skips execution and full earns proof."""
    children = [] if skip else [(passing_transcript(affected, None), 0)]
    children.append((passing_transcript(100, "TOTAL 100 0 100%"), 0))
    spawns = QueueSpawns(children)
    def counts(_i: Invocation, _d: Deps) -> tuple[int, int]:
        return affected, 100

    deps = replace(make_deps(spawns), selection_counts=counts)
    assert cli.main(["day", "--full=cov", "--root", str(tmp_path)], deps) == 0
    assert len(spawns.commands) == (1 if skip else 2)
    marker = snapshot.read_proof_marker(snapshot.marker_path(tmp_path))
    assert marker is not None
    assert marker.proof is FullLevel.COV
    assert ("execution skipped" in capsys.readouterr().out) is skip


@pytest.mark.parametrize(("raw", "level"), [("100", "cov"), ("bad", "cov"), ("75", "none")])
def test_disabled_or_no_full_never_probes(tmp_path: Path, raw: str, level: str) -> None:
    """No collection cost is added when probing is disabled or irrelevant."""
    children = [(passing_transcript(1, None), 0)]
    if level != "none":
        children.append((passing_transcript(1, "TOTAL 1 0 100%"), 0))
    deps = make_deps(QueueSpawns(children), {selection.ENV_PERCENT: raw})

    def forbidden(_i: Invocation, _d: Deps) -> NoReturn:
        pytest.fail("selection probe must not run")

    options = [] if level == "none" else [f"--full={level}"]
    assert cli.main(["day", *options, "--root", str(tmp_path)],
                    replace(deps, selection_counts=forbidden)) == 0


def test_failed_full_after_skip_does_not_claim_affected_pass(tmp_path: Path) -> None:
    """A skipped execution supplies no proof when the full tests fail."""
    spawns = QueueSpawns([(["collected 1 item", "tests/test_x.py::test_x FAILED [100%]",
                           "=== 1 failed in 0.01s ==="], 1)])
    def counts(_i: Invocation, _d: Deps) -> tuple[int, int]:
        return 1, 1

    deps = replace(make_deps(spawns), selection_counts=counts)
    assert cli.main(["day", "--full=cov", "--root", str(tmp_path)], deps) != 0
    assert snapshot.read_proof_marker(snapshot.marker_path(tmp_path)) is None


@pytest.mark.parametrize(("full", "affected", "expected"), [
    ((["collected 120 items / 20 deselected / 100 selected"], 0),
     (["collected 90 items / 10 deselected / 80 selected"], 0), (80, 100)),
    ((["collected 1 item"], 0), (["collected 0 items"], 5), (0, 1)),
    ((["collected 1 item"], 0), (["collected 2 items"], 0), None),
    ((["collected 1 item"], 0), (["collected 1 item"], 2), None),
    ((["collected 0 items"], 5), None, None),
    ((["collected 1 item"], 2), None, None),
    ((["unrecognized output"], 0), None, None),
])
def test_collection_counts_only_successful_selected_cases(
    tmp_path: Path, full: Transcript, affected: Transcript | None, expected: tuple[int, int] | None,
) -> None:
    """Use selected counts, accepting empty affected but no failed probe."""
    children = [full] + ([] if affected is None else [affected])
    spawns = QueueSpawns(children)
    invocation = Invocation("day", (), no_cov=False, mode=Mode.LLM, root=tmp_path)
    assert selection.counts(invocation, make_deps(spawns)) == expected
    assert all("--collect-only" in c and "--no-cov" in c for c in spawns.commands)
    assert "--no-testmon" in spawns.commands[0]
    if affected is not None:
        assert "--testmon-nocollect" in spawns.commands[1]


@pytest.mark.parametrize("missing", ["pytest", "project", "spawn"])
def test_unavailable_collection_falls_back(tmp_path: Path, missing: str) -> None:
    """Missing tooling or failed spawning retains the ordinary sequence."""
    deps = make_deps(QueueSpawns([]))
    def absent(_name: str) -> None:
        return None

    def non_project(_root: Path) -> bool:
        return False

    if missing == "pytest":
        deps = replace(deps, which=absent)
    elif missing == "project":
        deps = replace(deps, pytest_project=non_project)
    else:
        def broken(_command: list[str], _cwd: Path) -> NoReturn:
            message = "cannot spawn"
            raise OSError(message)
        deps = replace(deps, popen_factory=broken)
    assert selection.counts(Invocation("day", (), no_cov=False, mode=Mode.LLM, root=tmp_path), deps) is None


def test_both_probes_preserve_bound_test_files(tmp_path: Path) -> None:
    """Compare the same explicit file selection in both collection processes."""
    scope = replace(WHOLE_SCOPE, test_files=("tests/test_a.py", "tests/test_b.py"))
    spawns = QueueSpawns([(["collected 2 items"], 0), (["collected 1 item"], 0)])
    invocation = Invocation("day", (), no_cov=False, mode=Mode.LLM, root=tmp_path, scope=scope)
    assert selection.counts(invocation, make_deps(spawns)) == (1, 2)
    assert all(tuple(command[-2:]) == scope.test_files for command in spawns.commands)


def test_missing_tooling_cannot_hide_foreign_binding(tmp_path: Path) -> None:
    """Binding validation precedes the collection availability fallback."""
    spawns = QueueSpawns([])
    def missing(_name: str) -> None:
        return None

    deps = replace(make_deps(spawns, {env.ROOT: str(tmp_path / "other")}), which=missing)
    with pytest.raises(env.PreparationError):
        selection.counts(Invocation("day", (), no_cov=True, mode=Mode.LLM, root=tmp_path), deps)
    assert spawns.commands == []


# eof
