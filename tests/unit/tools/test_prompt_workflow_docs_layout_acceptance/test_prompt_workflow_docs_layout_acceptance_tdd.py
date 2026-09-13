"""Exercise layout discovery through real Git, CLI and post-commit resolution.

Step 4 proves canonical preference, current-content fallback and fatal errors
across the real modules. No layout, selection, state or Git helper is stubbed.
The script entry point supplies its actual exit-2 boundary; explicit host
arguments keep successful skill commands independent of the test host.
"""

from __future__ import annotations

import os
import runpy
import sys
from typing import TYPE_CHECKING

import pytest

from tools import new_draft_models, prompt_workflow
from tools import prompt_workflow_git as git
from tools import prompt_workflow_post_commit as post_commit
from tools.prompt_workflow_models import PromptWorkflowError, Topic

if TYPE_CHECKING:
    from pathlib import Path

_VERSION = "v1.2.3"
_SLUG = "my_effort"
_PARENT = "docs/v1.2.3/my-effort"
_DRAFT = f"draft.{_VERSION}.{_SLUG}.md"
_ISSUE = f"issue.{_VERSION}.{_SLUG}.md"
_PLAN = f"plan.{_VERSION}.{_SLUG}.md"
_VALIDATION = f"plan.{_VERSION}.{_SLUG}.validation.md"
_FATAL = 2
_ABSENT = 3
_VALIDATION_FIRST = (
    "# Validation\n\n### Analysis of Step 1 implementation state\n\n"
    "Yes. Step 1 is fully implemented.\n"
)
_VALIDATION_NEXT = (
    _VALIDATION_FIRST
    + "\n### Analysis of Step 2 implementation state\n\nNot started.\n"
)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    """Create an isolated Git history with a real branch and no inherited hooks."""
    git.run_git(["init", "--initial-branch=main"], cwd=tmp_path)
    hooks = tmp_path / ".git" / "empty-hooks"
    hooks.mkdir()
    git.run_git(["config", "core.hooksPath", str(hooks)], cwd=tmp_path)
    git.run_git(
        [
            "-c", "user.name=Layout acceptance",
            "-c", "user.email=layout@example.invalid",
            "-c", "commit.gpgSign=false",
            "commit", "--allow-empty", "-m", "Initial fixture",
        ],
        cwd=tmp_path,
    )
    git.run_git(["checkout", "-b", _SLUG], cwd=tmp_path)
    return tmp_path


def _write(root: Path, relative: str, body: str = "# Effort\n") -> Path:
    """Write a real effort file and return its absolute path."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _skill(root: Path, *arguments: str) -> int:
    """Run the public parser and real skill router with an explicit host."""
    return prompt_workflow.main(
        ["skill", *arguments, "--host", "codex", "--root", str(root)],
    )


def _assert_command(capsys: pytest.CaptureFixture[str], command: str) -> None:
    """Require exactly the expected command and no not-applicable diagnostic."""
    output = capsys.readouterr()
    assert output.out == f"{command}\n"
    assert output.err == ""


def _assert_document(
    root: Path, capsys: pytest.CaptureFixture[str], *, present: bool,
) -> None:
    """Check the document CLI's exact path or explicit absence after a mutation."""
    code = prompt_workflow.main(
        ["document", _VERSION, _SLUG, "issue", "--root", str(root)],
    )
    output = capsys.readouterr()
    assert code == (0 if present else _ABSENT)
    assert output.out == (f"{_PARENT}/{_ISSUE}\n" if present else "")
    assert output.err == (
        "" if present else f"pw document: no issue document for {_VERSION} {_SLUG}.\n"
    )


def _assert_no_post_commit_topic(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Require topic omission and the CLI's not-applicable result together."""
    assert post_commit.plan_topics(root) == []
    assert _skill(root, "--after-commit", "1") == _ABSENT
    output = capsys.readouterr()
    assert output.out == ""
    assert "no next step" in output.err


def _fatal_cli(
    root: Path,
    arguments: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> str:
    """Require a stdout fatal diagnostic without a success command or prompt."""
    script = prompt_workflow.__file__
    monkeypatch.setattr(sys, "argv", [script, *arguments, "--root", str(root)])
    with pytest.raises(SystemExit) as caught:
        runpy.run_path(script, run_name="__main__")
    assert caught.value.code == _FATAL
    output = capsys.readouterr()
    assert output.out.startswith("ERROR: ")
    assert "$" not in output.out
    assert " ready" not in output.out
    assert not (root / "a.prompt.txt").exists()
    return output.out + output.err


def test_document_ambiguity_keeps_workflow_canonical_preference(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Exact duplicates fail in document mode while skill mode uses its parent."""
    _write(repository, f"{_PARENT}/{_DRAFT}")
    local = _write(repository, f"{_PARENT}/{_ISSUE}")
    fallback = _write(repository, f"docs/v1.2.3/{_ISSUE}")
    diagnostic = _fatal_cli(
        repository, ["document", _VERSION, _SLUG, "issue"],
        monkeypatch, capsys,
    )
    for fragment in ("Ambiguous", _VERSION, _SLUG, _PARENT, f"docs/v1.2.3/{_ISSUE}"):
        assert fragment in diagnostic
    assert _skill(repository) == 0
    _assert_command(capsys, f"$llm-shared:review-ask-questions on {_PARENT}/{_ISSUE}")

    # Removing the local sibling immediately exposes the sole eligible fallback.
    local.unlink()
    assert _skill(repository) == 0
    _assert_command(
        capsys, f"$llm-shared:review-ask-questions on {fallback.relative_to(repository).as_posix()}",
    )


def test_skill_keeps_newest_local_match_ahead_of_newer_fallback(
    repository: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Local subtopics keep newest-file selection without mixing fallback mtimes."""
    _write(repository, f"{_PARENT}/{_DRAFT}")
    older = _write(repository, f"{_PARENT}/{_ISSUE}")
    newer = _write(repository, f"{_PARENT}/issue.{_VERSION}.{_SLUG}_detail.md")
    fallback = _write(repository, f"docs/{_ISSUE}")
    for path, timestamp in ((older, 100), (newer, 200), (fallback, 300)):
        os.utime(path, (timestamp, timestamp))
    assert _skill(repository) == 0
    _assert_command(
        capsys, f"$llm-shared:review-ask-questions on {newer.relative_to(repository).as_posix()}",
    )


def test_skill_fallback_ambiguity_is_fatal_and_refreshes_after_removal(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Competing fallback paths reach exit 2, and removing one restores routing."""
    _write(repository, f"{_PARENT}/{_DRAFT}")
    first = _write(repository, f"docs/{_ISSUE}")
    second = _write(repository, f"docs/v9.8.7/{_ISSUE}")
    diagnostic = _fatal_cli(
        repository, ["skill", "--host", "codex"], monkeypatch, capsys,
    )
    paths = [path.relative_to(repository).as_posix() for path in (first, second)]
    for fragment in ("fallback", "requirement", _VERSION, _SLUG, _PARENT, *paths):
        assert fragment in diagnostic
    assert diagnostic.index(paths[0]) < diagnostic.index(paths[1])
    second.unlink()
    assert _skill(repository) == 0
    _assert_command(capsys, f"$llm-shared:review-ask-questions on {paths[0]}")


@pytest.mark.parametrize("parent", ["docs/assets/topic", "docs/v1.2.3/wrong_slug"])
def test_branch_relevant_draft_with_invalid_parent_reaches_fatal_cli(
    repository: Path,
    parent: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Real Git finds the draft even though layout discovery rejects its parent."""
    _write(repository, f"{parent}/{_DRAFT}")
    _write(repository, f"docs/{_ISSUE}")
    diagnostic = _fatal_cli(
        repository, ["skill", "--host", "codex"], monkeypatch, capsys,
    )
    for fragment in ("canonical parent", parent, _VERSION, _SLUG):
        assert fragment in diagnostic


def test_document_mode_observes_added_renamed_and_removed_evidence(
    repository: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Later documents qualify without a draft and are rediscovered every call."""
    _write(repository, f"{_PARENT}/asset.txt")
    _assert_document(repository, capsys, present=False)
    evidence = _write(repository, f"{_PARENT}/{_ISSUE}")
    _assert_document(repository, capsys, present=True)
    renamed = evidence.rename(evidence.with_name(f"issue.{_VERSION}.other.md"))
    _assert_document(repository, capsys, present=False)
    renamed.rename(evidence)
    _assert_document(repository, capsys, present=True)
    evidence.unlink()
    _assert_document(repository, capsys, present=False)


def test_post_commit_missing_draft_routes_unique_plan_and_validation_changes(
    repository: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A validation-only parent uses a fallback plan until its last file disappears."""
    validation = _write(repository, f"{_PARENT}/{_VALIDATION}", _VALIDATION_NEXT)
    expected = Topic(_VERSION, _SLUG, repository / _PARENT / _DRAFT)
    assert not expected.draft_path.exists()
    _assert_no_post_commit_topic(repository, capsys)

    fallback = _write(repository, f"docs/{_PLAN}")
    assert post_commit.plan_topics(repository) == [expected]
    assert _skill(repository, "--after-commit", "1") == 0
    _assert_command(capsys, f"$implement-step on docs/{_PLAN} step 2")
    validation.write_text(_VALIDATION_FIRST, encoding="utf-8")
    assert _skill(repository, "--after-commit", "1") == 0
    _assert_command(capsys, "$prepare-release")

    # Removing the plan skips the topic; restoring it re-includes the topic.
    fallback.unlink()
    _assert_no_post_commit_topic(repository, capsys)
    _write(repository, f"docs/{_PLAN}")
    assert post_commit.plan_topics(repository) == [expected]
    validation.unlink()
    _assert_no_post_commit_topic(repository, capsys)


def test_post_commit_competing_plans_propagate_to_fatal_cli(
    repository: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A missing-draft topic never becomes absent when fallback plans compete."""
    _write(repository, f"{_PARENT}/{_VALIDATION}", _VALIDATION_NEXT)
    first = _write(repository, f"docs/{_PLAN}")
    second = _write(repository, f"docs/v1.2.3/{_PLAN}")
    with pytest.raises(PromptWorkflowError, match="Ambiguous fallback plan"):
        post_commit.plan_topics(repository)
    diagnostic = _fatal_cli(
        repository, ["skill", "--after-commit", "1", "--host", "codex"],
        monkeypatch, capsys,
    )
    paths = [path.relative_to(repository).as_posix() for path in (first, second)]
    for fragment in ("fallback plan", _VERSION, _SLUG, _PARENT, *paths):
        assert fragment in diagnostic
    assert diagnostic.index(paths[0]) < diagnostic.index(paths[1])
    second.unlink()
    assert _skill(repository, "--after-commit", "1") == 0
    _assert_command(capsys, f"$implement-step on {paths[0]} step 2")


@pytest.mark.parametrize(
    ("layout", "expected"),
    [
        ("flat", "docs"), ("minor", "docs/v1.2"),
        ("version", "docs/v1.2.3"), ("minor-version", "docs/v1.2/v1.2.3"),
    ],
)
def test_older_layouts_keep_optional_slug_default(layout: str, expected: str) -> None:
    """The original four layout callers can still omit the slug argument."""
    version = new_draft_models.SemanticVersion(1, 2, 3)
    assert new_draft_models.docs_relative_dir(version, layout).as_posix() == expected


# eof
