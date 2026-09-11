"""Git IO, validation-state, commit-plan, and authority acceptance."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.code_review_evidence import (
    capture_index_tree,
    capture_validation_state,
    compare_validation_state,
)
from tools.git_batch_commit_models import CommitBlock
from tools.git_batch_commit_validation import validate_commit_plan

from .fixtures import git, make_effort, staged_paths

_MINIMUM_PUBLISH_REFERENCES = 2


@pytest.fixture
def ignored_validation_artifact(tmp_path: Path) -> None:
    """Classify one ignored command artifact outside call timing."""
    effort = make_effort(tmp_path / "ignored")
    paths = ("reviewed.py", "a.validation-result.json")
    before = capture_validation_state(effort.root, paths)
    (effort.root / "a.validation-result.json").write_text("{}\n", encoding="utf-8")
    after = capture_validation_state(effort.root, paths)
    comparison = compare_validation_state(before, after)
    assert comparison.acceptable
    assert comparison.ignored_paths == ("a.validation-result.json",)


def test_validation_changes_only_ignored_paths_are_acceptable(
    ignored_validation_artifact: None,
) -> None:
    """Design case 10: ignored validation output does not block readiness."""
    assert ignored_validation_artifact is None


@pytest.fixture
def tracked_validation_artifact(tmp_path: Path) -> None:
    """Classify a tracked command side effect without staging or reverting it."""
    effort = make_effort(tmp_path / "tracked")
    before_tree = capture_index_tree(effort.root)
    before = capture_validation_state(effort.root, ("reviewed.py",))
    effort.source.write_text("VALUE = 99\n", encoding="utf-8")
    after = capture_validation_state(effort.root, ("reviewed.py",))
    comparison = compare_validation_state(before, after)
    assert not comparison.acceptable
    assert comparison.tracked_paths == ("reviewed.py",)
    assert capture_index_tree(effort.root) == before_tree
    assert effort.source.read_text(encoding="utf-8") == "VALUE = 99\n"


def test_validation_changes_tracked_file_blocks_without_staging_or_revert(
    tracked_validation_artifact: None,
) -> None:
    """Design case 11: tracked validation side effects remain visible."""
    assert tracked_validation_artifact is None


@pytest.fixture
def literal_explicit_path_set(tmp_path: Path, real_git_commands: object) -> None:
    """Capture one metacharacter path without repository discovery."""
    del real_git_commands
    effort = make_effort(tmp_path / "literal")
    literal = effort.root / "literal[1].txt"
    decoy = effort.root / "literal1.txt"
    literal.write_text("selected\n", encoding="utf-8")
    decoy.write_text("decoy\n", encoding="utf-8")
    git(effort.root, "add", "literal[1].txt", "literal1.txt")
    state = capture_validation_state(effort.root, ("literal[1].txt",))
    assert state.paths == ("literal[1].txt",)
    assert tuple(item.path for item in state.tracked_files) == ("literal[1].txt",)


def test_validation_capture_uses_literal_explicit_paths_only(
    literal_explicit_path_set: None,
) -> None:
    """IO boundary: Git pathspec metacharacters cannot widen the path set."""
    assert literal_explicit_path_set is None


@pytest.fixture
def side_effect_free_commit_plan(tmp_path: Path) -> None:
    """Validate typed commit membership without touching the index."""
    effort = make_effort(tmp_path / "commit-plan")
    before = capture_index_tree(effort.root)
    block = CommitBlock(
        ["git add -A reviewed.py"],
        "test(code-reviewer): prove acceptance\n",
        "test(code-reviewer): prove acceptance",
    )
    result = validate_commit_plan([block], list(staged_paths(effort.root)))
    assert result.diagnostics == ()
    assert result.groups[0].paths == ("reviewed.py",)
    assert capture_index_tree(effort.root) == before


def test_commit_plan_validation_is_typed_and_side_effect_free(
    side_effect_free_commit_plan: None,
) -> None:
    """Readiness floor: commit grouping uses the shared pure validator."""
    assert side_effect_free_commit_plan is None


def test_reviewer_instruction_denies_requestor_human_and_commit_authority() -> None:
    """Requirement AC03: the responder cannot acquire owning operations."""
    content = Path("instructions/code-reviewer.md").read_text(encoding="utf-8")
    normalized = " ".join(content.split())
    assert (
        "Never call `consume-answer`, `continue`, `confirm`, `complete`, "
        "`escalate`, `cancel`, `resolve`, or `archive`."
    ) in normalized
    assert "invoke batch commit" in normalized
    assert "never complete an umbrella row" in normalized
    assert "The reviewer may call only" in content
    assert content.count("`publish-answer`") >= _MINIMUM_PUBLISH_REFERENCES
    assert "one bounded `wait-request` per round" in content
    assert "same reviewer session" in content
