"""One workflow journey covers scope, review-off comparisons and release gates."""

from __future__ import annotations

import shlex
from typing import TYPE_CHECKING

from tools import prompt_workflow
from tools.groundhog import cli, exclusions, floor
from tools.prepare_release.prepare_release_plan_workflow import build_release_plan

if TYPE_CHECKING:
    import pytest

    from tests.unit.tools.test_full_suite_levels_acceptance.conftest import Effort


def test_review_off_scope_comparison_and_release(
    effort: Effort, release_base: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Ambient selection cannot narrow the requirement or release; tightening is unchanged."""
    monkeypatch.setenv("GHOG_GROUP", "sentinel")
    effort.set_group(None)
    capsys.readouterr()
    assert prompt_workflow.main(["--root", str(effort.root), "scope", "day", "--full=speed"]) == 0
    command = shlex.split(capsys.readouterr().out.strip())
    assert command == ["ghog", "day", "--full=speed", "--whole-suite"]
    _assert_exclusion_comparisons(effort, command, capsys)
    (effort.root / "src/sentinel/core.py").write_text("value = 2\n", encoding="utf-8")
    effort.set_group("sentinel")
    _assert_release_gates(effort, release_base, capsys)


def _assert_exclusion_comparisons(
    effort: Effort, command: list[str], capsys: pytest.CaptureFixture[str],
) -> None:
    """A speed walk tightens the baseline, while a newly accepted entry changes policy."""
    node = "tests/old/test_core.py::test_ok"
    floor.write_floor(effort.root, 10.0, 1.0)
    exclusions.write_exclusions(effort.root, {node: 4.0})
    listing = ["exclude", "--list", "--root", str(effort.root)]
    assert cli.main(listing) == 0
    saved = effort.home / "a.exclusions.txt"
    saved.write_text(capsys.readouterr().out, encoding="utf-8")
    assert effort.walk(*command[1:], environment={"GHOG_GROUP": "sentinel"}, seconds=1.5)[0] == 0
    assert exclusions.read_exclusions(effort.root) == {node: 1.5}
    assert floor.floor_path(effort.root).read_text(encoding="utf-8").splitlines()[0] != "10.0"
    capsys.readouterr()
    comparison = [*listing, f"--since={saved}"]
    assert cli.main(comparison) == 0
    assert capsys.readouterr().out == "exclusions=unchanged\n"
    assert cli.main(["exclude", "tests/new/test_core.py::test_new", "2.0", "--root", str(effort.root)]) == 0
    capsys.readouterr()
    assert cli.main(comparison) == 0
    assert "exclusions=changed" in capsys.readouterr().out


def _assert_release_gates(effort: Effort, base: str, capsys: pytest.CaptureFixture[str]) -> None:
    """Main preparation and divergent promotions require whole-suite coverage."""
    for branch in ("main", "topic", "develop"):
        plan = build_release_plan(effort.root, main_branch="main", integration_branch="develop", branch=branch,
                                  feature_base=base, feature_parent="develop", preview_conflicts=False)
        gates = [operation for operation in plan.operations if "ghog day" in operation]
        assert len(gates) == 1
        assert "ghog day --full=cov --whole-suite" in gates[0]
    capsys.readouterr()
    arguments = shlex.split(gates[0].split("ghog ", 1)[1])
    code, spawns = effort.walk(*arguments, environment={"GHOG_GROUP": "sentinel"})
    assert code == 0
    assert "tests/old/test_core.py" not in spawns.commands[-1]
    assert "scope=whole" in capsys.readouterr().out
