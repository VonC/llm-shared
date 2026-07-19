"""Scenario, SVG renderer, and CLI tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.git_history_diagrams.generate_git_history_diagrams import main
from tools.git_history_diagrams.models import Commit, Edge, Lane, Scenario
from tools.git_history_diagrams.scenarios import prepare_release_scenarios
from tools.git_history_diagrams.svg_renderer import render_svg

if TYPE_CHECKING:
    from pathlib import Path

SCENARIO_COUNT = 4


def test_scenario_set_is_stable() -> None:
    """The documented scenario collection has stable unique slugs."""
    scenarios = prepare_release_scenarios()
    assert len(scenarios) == SCENARIO_COUNT
    assert len({scenario.slug for scenario in scenarios}) == len(scenarios)


@pytest.mark.parametrize("scenario", prepare_release_scenarios(), ids=lambda item: item.slug)
def test_scenario_topology_is_complete(scenario: Scenario) -> None:
    """Every documented scenario has valid commits and a merge decision."""
    commit_keys = {commit.key for commit in scenario.commits}
    assert len(commit_keys) == len(scenario.commits)
    assert all(edge.start in commit_keys and edge.end in commit_keys for edge in scenario.edges)
    assert any(edge.kind == "merge" for edge in scenario.edges)


def test_bulk_develop_scenario_never_rebases() -> None:
    """The all-ready integration path is a merge-only operation."""
    scenarios = prepare_release_scenarios()
    bulk = next(item for item in scenarios if item.slug == "develop-to-main")
    assert not any(edge.kind == "rebase" for edge in bulk.edges)


def test_replayed_commits_keep_their_new_base_and_branch_role() -> None:
    """Replayed commits descend from the target while staying off it until merge."""
    scenarios = {item.slug: item for item in prepare_release_scenarios()}
    integration = scenarios["feature-to-develop"]
    commit_lanes = {commit.key: commit.lane for commit in integration.commits}
    assert commit_lanes["rf0"] == "feature"
    assert commit_lanes["rf1"] == "feature"
    assert Edge("d1", "rf0") in integration.edges
    for slug in ("feature-direct-to-main", "feature-from-develop-to-main"):
        assert Edge("m1", "p0") in scenarios[slug].edges


def test_renderer_is_accessible_escaped_and_styled() -> None:
    """SVG carries accessible text, escaped labels, colors, and both arrow styles."""
    scenario = Scenario(
        "escape",
        "A < B",
        "safe & clear",
        (Lane("main", "main", 100, "#123456"),),
        (Commit("a", "A", 100, "main"), Commit("b", "B", 300, "main")),
        (Edge("a", "b", "rebase", "x < y"),),
    )
    rendered = render_svg(scenario)
    assert 'role="img"' in rendered
    assert "A &lt; B" in rendered
    assert "safe &amp; clear" in rendered
    assert "x &lt; y" in rendered
    assert "stroke-dasharray" in rendered
    assert "solid arrow = merge --no-ff" in rendered
    assert "#123456" in rendered


@pytest.mark.parametrize(
    ("scenario", "message"),
    [
        (
            Scenario("x", "x", "x", (Lane("a", "a", 1, "#000"), Lane("a", "b", 2, "#111")), (), ()),
            "lane keys",
        ),
        (
            Scenario("x", "x", "x", (Lane("a", "a", 1, "#000"),), (Commit("c", "c", 1, "missing"),), ()),
            "unknown lane",
        ),
        (
            Scenario("x", "x", "x", (Lane("a", "a", 1, "#000"),), (Commit("c", "c", 1, "a"), Commit("c", "d", 2, "a")), ()),
            "commit keys",
        ),
        (
            Scenario("x", "x", "x", (Lane("a", "a", 1, "#000"),), (Commit("c", "c", 1, "a"),), (Edge("c", "missing"),)),
            "unknown commit",
        ),
    ],
)
def test_renderer_rejects_invalid_topology(scenario: Scenario, message: str) -> None:
    """Broken declarative scenarios fail with an actionable error."""
    with pytest.raises(ValueError, match=message):
        render_svg(scenario)


def test_cli_writes_lists_checks_and_detects_stale(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The CLI supports generation, discovery, freshness checks, and drift detection."""
    output = tmp_path / "diagrams"
    assert main(["--output-dir", str(output)]) == 0
    assert len(list(output.glob("*.svg"))) == SCENARIO_COUNT
    assert "Wrote" in capsys.readouterr().out
    assert main(["--output-dir", str(output), "--check"]) == 0
    assert main(["--list"]) == 0
    assert "develop-to-main" in capsys.readouterr().out
    (output / "develop-to-main.svg").write_text("stale", encoding="utf-8")
    assert main(["--output-dir", str(output), "--check"]) == 1
    assert "Missing or stale diagrams" in capsys.readouterr().err
