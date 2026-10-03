"""Prove pw scope dispatch, live requirement changes and progress ordering.

Git and review discovery are stubbed; document selection, metadata reading,
group resolution, parser dispatch and the rendered scope use the real modules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.groundhog_group_support import group_project
from tools import prompt_workflow
from tools import prompt_workflow_progress as progress
from tools import prompt_workflow_scope as scope
from tools.prompt_workflow_models import Topic
from tools.prompt_workflow_progress_review import ReviewReport

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

_INVALID_SCOPE = 2
_NO_TOPIC = 3


@pytest.fixture
def topic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Topic:
    """Build a stale grouped draft and select it without spawning Git."""
    group_project(tmp_path)
    docs = tmp_path / "docs"
    docs.mkdir()
    draft = docs / "draft.v1.0.0.topic.md"
    draft.write_text("# Draft\n- Test group: sentinel\n", encoding="utf-8")
    selected = Topic("v1.0.0", "topic", draft)
    monkeypatch.setattr(scope.git, "current_branch", lambda _root: "topic")
    monkeypatch.setattr(scope.handoff, "resolve_current_topic", lambda *_args: selected)
    monkeypatch.setattr(progress.git, "fork_point", lambda _root: None)
    monkeypatch.setattr(progress.git, "has_step_commit", lambda *_args: False)
    monkeypatch.setattr(progress.progress_review, "review_report", lambda *_args: ReviewReport((), None))
    monkeypatch.setattr(progress.review_history, "last_requestor_nature", lambda *_args: None)
    monkeypatch.setattr(progress, "next_line", lambda *_args: "next command")
    return selected


def _requirement(topic: Topic, value: str | None) -> Path:
    """Rewrite only the current requirement scope declaration."""
    path = topic.draft_path.with_name("feature-request.v1.0.0.topic.md")
    body = "# Requirement\n" + ("" if value is None else f"- Test group: {value}\n")
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.parametrize(("value", "arguments", "expected"), [
    ("sentinel", [], "--group=sentinel"),
    (None, [], "--whole-suite"),
    ("whole suite", ["day"], "ghog day --whole-suite"),
    ("sentinel", ["day", "--full=speed"], "ghog day --full=speed --group=sentinel"),
    (None, ["day", "--full=cov"], "ghog day --full=cov --whole-suite"),
    ("sentinel", ["single", "tests/a file.py"], 'ghog single "tests/a file.py" --group=sentinel'),
])
def test_cli_prints_explicit_scope_independent_of_environment(  # noqa: PLR0913
    tmp_path: Path, topic: Topic, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str], value: str | None, arguments: list[str], expected: str,
) -> None:
    """CLI dispatch preserves ghog arguments and defeats ambient or stale draft groups."""
    _requirement(topic, value)
    monkeypatch.setenv("GHOG_GROUP", "other")
    assert prompt_workflow.main(["--root", str(tmp_path), "scope", *arguments]) == 0
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"
    assert not captured.err


def test_no_requirement_prints_whole_suite(tmp_path: Path, topic: Topic, capsys: pytest.CaptureFixture[str]) -> None:
    """A draft group is not used before the requirement exists."""
    assert topic.draft_path.exists()
    assert scope.run_scope(tmp_path, []) == 0
    assert capsys.readouterr().out == "--whole-suite\n"


@pytest.mark.parametrize("selector", [
    ["--group=x"], ["--group", "x"], ["--scope-file=f"], ["--scope-file", "f"], ["--whole-suite"],
])
def test_existing_selector_is_refused(
    tmp_path: Path, topic: Topic, capsys: pytest.CaptureFixture[str], selector: list[str],
) -> None:
    """A caller cannot override the effort scope with either selector spelling."""
    _requirement(topic, "sentinel")
    assert prompt_workflow.main(["--root", str(tmp_path), "scope", "day", *selector]) == _INVALID_SCOPE
    captured = capsys.readouterr()
    assert not captured.out
    assert selector[0] in captured.err


def test_bad_group_prints_only_a_diagnostic(tmp_path: Path, topic: Topic, capsys: pytest.CaptureFixture[str]) -> None:
    """An invalid group exits 2 without printing a runnable selector."""
    _requirement(topic, "unknown")
    assert scope.run_scope(tmp_path, ["day"]) == _INVALID_SCOPE
    captured = capsys.readouterr()
    assert not captured.out
    assert "feature-request.v1.0.0.topic.md" in captured.err
    assert "unknown group: unknown" in captured.err


def test_unresolved_topic_prints_no_selector(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Menu-less ambiguity preserves the existing not-applicable exit code."""
    monkeypatch.setattr(scope.git, "current_branch", lambda _root: "topic")
    monkeypatch.setattr(scope.handoff, "resolve_current_topic", lambda *_args: None)
    assert scope.run_scope(tmp_path, []) == _NO_TOPIC
    captured = capsys.readouterr()
    assert not captured.out
    assert "no workflow topic resolved" in captured.err


def test_scope_changes_take_effect_after_step_two(
    tmp_path: Path, topic: Topic, capsys: pytest.CaptureFixture[str],
) -> None:
    """Activation, switching and removal re-read the requirement without changing groups."""
    validation = topic.draft_path.with_name("plan.v1.0.0.topic.validation.md")
    validation.write_text("## Step 2. Done\n\n### Analysis of Step 2\n\nYes\n", encoding="utf-8")
    groups_before = (tmp_path / ".ghog-groups").read_bytes()
    for value, expected in ((None, "--whole-suite"), ("sentinel", "--group=sentinel"),
                            ("other", "--group=other"), (None, "--whole-suite")):
        _requirement(topic, value)
        assert scope.run_scope(tmp_path, ["day"]) == 0
        assert capsys.readouterr().out == f"ghog day {expected}\n"
    assert (tmp_path / ".ghog-groups").read_bytes() == groups_before


@pytest.mark.parametrize(("value", "expected"), [
    (None, "whole suite (no Test group line in docs/feature-request.v1.0.0.topic.md)"),
    ("sentinel", "group sentinel (docs/feature-request.v1.0.0.topic.md)"),
    ("whole suite", "whole suite (docs/feature-request.v1.0.0.topic.md)"),
    ("unknown", "error: docs/feature-request.v1.0.0.topic.md: unknown group: unknown"),
])
def test_progress_scope_after_phase_without_step(tmp_path: Path, topic: Topic, value: str | None, expected: str) -> None:
    """Every source and validation error is visible without claiming saved proof."""
    _requirement(topic, value)
    lines = progress.progress_lines(tmp_path, topic, "topic", {})
    labels = [label for label, _value in lines]
    assert labels.index("scope") == labels.index("phase") + 1
    assert dict(lines)["scope"] == expected


def test_progress_without_requirement(tmp_path: Path, topic: Topic) -> None:
    """No requirement reports its reason rather than resurrecting the draft group."""
    lines = progress.progress_lines(tmp_path, topic, "topic", {})
    assert dict(lines)["scope"] == "whole suite (no requirement yet)"


@pytest.mark.parametrize("journal", [False, True])
def test_progress_scope_follows_step_and_optional_journal(tmp_path: Path, topic: Topic, *, journal: bool) -> None:
    """The scope row stays adjacent to the step context, before review and next."""
    _requirement(topic, "sentinel")
    design = topic.draft_path.with_name("design.v1.0.0.topic.md")
    design.write_text("# Design\n", encoding="utf-8")
    plan = topic.draft_path.with_name("plan.v1.0.0.topic.md")
    plan.write_text(
        "### Step 2. Select scope\n\n## Implementation decisions\n\n| Q01 | Settled |\n",
        encoding="utf-8",
    )
    validation = topic.draft_path.with_name("plan.v1.0.0.topic.validation.md")
    validation.write_text("## Step 2. Select scope\n\n### Analysis of Step 2\n\nNo\n", encoding="utf-8")
    if journal:
        home = tmp_path / ".reviews"
        home.mkdir()
        (home / "a.topic.step2.journal.md").write_text("notes", encoding="utf-8")
    lines = progress.progress_lines(tmp_path, topic, "topic", {})
    labels = [label for label, _value in lines]
    assert labels.index("scope") == labels.index("journal" if journal else "step") + 1


# eof
