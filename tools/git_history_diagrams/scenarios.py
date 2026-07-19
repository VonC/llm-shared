"""Canonical prepare-release history scenarios."""

from __future__ import annotations

from tools.git_history_diagrams.models import Commit, Edge, Lane, Scenario

MAIN = "#2563eb"
DEVELOP = "#d97706"
FEATURE = "#15803d"
PROMOTION = "#7c3aed"


def _feature_to_develop() -> Scenario:
    lanes = (
        Lane("main", "main (release)", 110, MAIN),
        Lane("develop", "develop (integration)", 210, DEVELOP),
        Lane("feature", "feature/A", 310, FEATURE),
    )
    commits = (
        Commit("m0", "M0", 190, "main"),
        Commit("d0", "D0", 310, "develop"),
        Commit("d1", "D1", 470, "develop"),
        Commit("f0", "A1", 470, "feature"),
        Commit("f1", "A2", 630, "feature"),
        Commit("rf0", "A1'", 690, "feature"),
        Commit("rf1", "A2'", 830, "feature"),
        Commit("dm", "merge A", 990, "develop"),
    )
    edges = (
        Edge("m0", "d0"),
        Edge("d0", "d1"),
        Edge("d0", "f0"),
        Edge("f0", "f1"),
        Edge("f0", "rf0", "rebase", "rebase onto develop"),
        Edge("d1", "rf0"),
        Edge("rf0", "rf1"),
        Edge("d1", "dm"),
        Edge("rf1", "dm", "merge", "merge --no-ff"),
    )
    return Scenario(
        "feature-to-develop",
        "Integrate one feature into develop",
        "The rebased commits get new identities; the merge records integration.",
        lanes,
        commits,
        edges,
    )


def _feature_direct_to_main() -> Scenario:
    lanes = (
        Lane("main", "main (release)", 130, MAIN),
        Lane("feature", "feature/A", 250, FEATURE),
        Lane("promotion", "promotion copy", 350, PROMOTION),
    )
    commits = (
        Commit("m0", "M0", 190, "main"),
        Commit("m1", "M1", 470, "main"),
        Commit("f0", "A1", 390, "feature"),
        Commit("f1", "A2", 580, "feature"),
        Commit("p0", "A1'", 650, "promotion"),
        Commit("p1", "A2'", 800, "promotion"),
        Commit("mm", "merge A", 990, "main"),
    )
    edges = (
        Edge("m0", "m1"),
        Edge("m0", "f0"),
        Edge("f0", "f1"),
        Edge("f0", "p0", "rebase", "rebase exact range onto main"),
        Edge("m1", "p0"),
        Edge("p0", "p1"),
        Edge("m1", "mm"),
        Edge("p1", "mm", "merge", "merge --no-ff"),
    )
    return Scenario(
        "feature-direct-to-main",
        "Select one stale feature directly for main",
        "A temporary copy is rebased; the original feature branch is unchanged.",
        lanes,
        commits,
        edges,
    )


def _feature_from_develop_to_main() -> Scenario:
    lanes = (
        Lane("main", "main (release)", 100, MAIN),
        Lane("develop", "develop (integration)", 205, DEVELOP),
        Lane("feature", "feature/A", 310, FEATURE),
        Lane("promotion", "promotion copy", 415, PROMOTION),
    )
    commits = (
        Commit("m0", "M0", 180, "main"),
        Commit("m1", "M1", 500, "main"),
        Commit("d0", "D0", 300, "develop"),
        Commit("f0", "A1", 460, "feature"),
        Commit("f1", "A2", 620, "feature"),
        Commit("dm", "merge A", 760, "develop"),
        Commit("p0", "A1'", 690, "promotion"),
        Commit("p1", "A2'", 835, "promotion"),
        Commit("mm", "merge A", 1010, "main"),
    )
    edges = (
        Edge("m0", "m1"),
        Edge("m0", "d0"),
        Edge("d0", "f0"),
        Edge("f0", "f1"),
        Edge("d0", "dm"),
        Edge("f1", "dm", "merge", "integration merge --no-ff"),
        Edge("f0", "p0", "rebase", "isolate A1..A2; replay onto main"),
        Edge("m1", "p0"),
        Edge("p0", "p1"),
        Edge("m1", "mm"),
        Edge("p1", "mm", "merge", "release merge --no-ff"),
    )
    return Scenario(
        "feature-from-develop-to-main",
        "Promote only one feature already tested on develop",
        "Only the confirmed feature range is replayed; unrelated develop work stays out.",
        lanes,
        commits,
        edges,
    )


def _develop_to_main() -> Scenario:
    lanes = (
        Lane("main", "main (release)", 125, MAIN),
        Lane("develop", "develop (integration)", 255, DEVELOP),
        Lane("features", "validated topics", 375, FEATURE),
    )
    commits = (
        Commit("m0", "M0", 180, "main"),
        Commit("d0", "D0", 300, "develop"),
        Commit("a", "A", 430, "features"),
        Commit("ma", "merge A", 570, "develop"),
        Commit("b", "B", 660, "features"),
        Commit("mb", "merge B", 800, "develop"),
        Commit("mm", "merge develop", 1010, "main"),
    )
    edges = (
        Edge("m0", "d0"),
        Edge("d0", "a"),
        Edge("d0", "ma"),
        Edge("a", "ma", "merge", "--no-ff"),
        Edge("ma", "b"),
        Edge("ma", "mb"),
        Edge("b", "mb", "merge", "--no-ff"),
        Edge("m0", "mm"),
        Edge("mb", "mm", "merge", "merge develop --no-ff"),
    )
    return Scenario(
        "develop-to-main",
        "Release every feature validated on develop",
        "Develop is never rebased; one merge selects its complete tested history.",
        lanes,
        commits,
        edges,
    )


def prepare_release_scenarios() -> tuple[Scenario, ...]:
    """Return the stable diagram set in documentation order."""
    return (
        _feature_to_develop(),
        _feature_direct_to_main(),
        _feature_from_develop_to_main(),
        _develop_to_main(),
    )


# eof
