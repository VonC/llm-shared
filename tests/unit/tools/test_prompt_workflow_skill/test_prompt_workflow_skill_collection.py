"""Collection-aware post-merge routing for ``pw skill``."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow
from tools import prompt_workflow_skill as skill
from tools.prompt_workflow_models import MemoryRecord, PromptWorkflowError, Topic

if TYPE_CHECKING:
    from pathlib import Path

_CLAUDE = {"CLAUDECODE": "1"}


def _setup_collection_tree(tmp_path: Path, *, root_routing_complete: bool = False) -> Path:
    """Create a settled two-item umbrella with its first item complete."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(exist_ok=True)
    umbrella = docs_dir / "draft.v10.0.0.sentinel.md"
    root_status = "completed" if root_routing_complete else "pending"
    root_requirement = (
        "`docs/feature-request.v10.0.0.root-routing.md`"
        if root_routing_complete
        else "-"
    )
    root_validation = (
        "`docs/plan.v10.0.0.root-routing.validation.md`"
        if root_routing_complete
        else "-"
    )
    umbrella.write_text(
        "# Sentinel\n\n"
        "- Type: collection (feature-requests and issues)\n"
        "- Draft role: umbrella\n\n"
        "## List of feature-requests and issues to create\n\n"
        "| Order | Type | Key title | Slug | Status | Requirement | Validation plan |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| 1 | Issue | Remove old routes | `route-cleanup` | completed | "
        "`docs/issue.v10.0.0.route-cleanup.md` | "
        "`docs/plan.v10.0.0.route-cleanup.validation.md` |\n"
        f"| 2 | Feature-request | Serve the root | `root-routing` | {root_status} | "
        f"{root_requirement} | {root_validation} |\n\n"
        "### Requirement details\n\n"
        '- Issue: "Remove old routes [route-cleanup]": first.\n'
        '- Feature-request: "Serve the root [root-routing]": second.\n',
        encoding="utf-8",
    )
    (docs_dir / "issue.v10.0.0.route-cleanup.md").write_text(
        "# Remove old routes\n",
        encoding="utf-8",
    )
    (docs_dir / "plan.v10.0.0.route-cleanup.md").write_text(
        "# Plan\n",
        encoding="utf-8",
    )
    (docs_dir / "plan.v10.0.0.route-cleanup.validation.md").write_text(
        "# Validation\n\nYes, it is implemented.\n",
        encoding="utf-8",
    )
    if root_routing_complete:
        (docs_dir / "feature-request.v10.0.0.root-routing.md").write_text(
            "# Serve the root\n",
            encoding="utf-8",
        )
        (docs_dir / "plan.v10.0.0.root-routing.md").write_text(
            "# Plan\n",
            encoding="utf-8",
        )
        (docs_dir / "plan.v10.0.0.root-routing.validation.md").write_text(
            "# Validation\n\nYes, it is implemented.\n",
            encoding="utf-8",
        )
    return umbrella


def test_post_merge_command_proposes_the_next_umbrella_item(tmp_path: Path) -> None:
    """A completed first item hands the ordered missing item to process-draft."""
    umbrella = _setup_collection_tree(tmp_path)

    command = skill.post_merge_command(
        tmp_path,
        "docs/draft.v10.0.0.sentinel.md",
        {"CODEX_THREAD_ID": "x"},
    )

    assert command == (
        "$llm-shared:process-draft on docs/draft.v10.0.0.sentinel.md "
        "based on root-routing"
    )
    assert umbrella.is_file()


def test_post_merge_command_prepares_release_only_after_every_item(
    tmp_path: Path,
) -> None:
    """An exhausted collection returns to the full release path."""
    _setup_collection_tree(tmp_path, root_routing_complete=True)

    command = skill.post_merge_command(
        tmp_path,
        "docs/draft.v10.0.0.sentinel.md",
        _CLAUDE,
    )

    assert command == "/prepare-release"


def test_post_merge_command_resumes_an_existing_incomplete_item(
    tmp_path: Path,
) -> None:
    """An item with a requirement resumes its workflow instead of duplicating it."""
    _setup_collection_tree(tmp_path)
    (tmp_path / "docs" / "feature-request.v10.0.0.root-routing.md").write_text(
        "# Serve the root\n\nFresh requirement.\n",
        encoding="utf-8",
    )

    command = skill.post_merge_command(
        tmp_path,
        "docs/draft.v10.0.0.sentinel.md",
        _CLAUDE,
    )

    assert command == (
        "/review-ask-questions on docs/feature-request.v10.0.0.root-routing.md"
    )


def test_post_merge_command_rejects_a_stale_pending_status(tmp_path: Path) -> None:
    """Complete validation cannot silently override a pending umbrella row."""
    _setup_collection_tree(tmp_path)
    docs_dir = tmp_path / "docs"
    (docs_dir / "feature-request.v10.0.0.root-routing.md").write_text(
        "# Serve the root\n",
        encoding="utf-8",
    )
    (docs_dir / "plan.v10.0.0.root-routing.validation.md").write_text(
        "# Validation\n\nYes, it is implemented.\n",
        encoding="utf-8",
    )

    with pytest.raises(PromptWorkflowError, match="implementation-check"):
        skill.post_merge_command(
            tmp_path,
            "docs/draft.v10.0.0.sentinel.md",
            _CLAUDE,
        )


def test_post_merge_command_rejects_paths_on_a_pending_row(tmp_path: Path) -> None:
    """Pending rows cannot claim evidence paths before completion."""
    umbrella = _setup_collection_tree(tmp_path)
    umbrella.write_text(
        umbrella.read_text(encoding="utf-8").replace(
            "| 2 | Feature-request | Serve the root | `root-routing` | pending | - | - |",
            "| 2 | Feature-request | Serve the root | `root-routing` | pending | "
            "`docs/feature-request.v10.0.0.root-routing.md` | - |",
        ),
        encoding="utf-8",
    )

    with pytest.raises(PromptWorkflowError, match="must use '-'"):
        skill.post_merge_command(
            tmp_path,
            "docs/draft.v10.0.0.sentinel.md",
            _CLAUDE,
        )


def test_post_merge_command_rejects_missing_completed_evidence(
    tmp_path: Path,
) -> None:
    """A completed row cannot point at a missing requirement."""
    _setup_collection_tree(tmp_path)
    (tmp_path / "docs" / "issue.v10.0.0.route-cleanup.md").unlink()

    with pytest.raises(PromptWorkflowError, match="missing requirement"):
        skill.post_merge_command(
            tmp_path,
            "docs/draft.v10.0.0.sentinel.md",
            _CLAUDE,
        )


def test_post_merge_command_requires_paths_on_a_completed_row(tmp_path: Path) -> None:
    """Completed status always carries both evidence paths."""
    umbrella = _setup_collection_tree(tmp_path)
    umbrella.write_text(
        umbrella.read_text(encoding="utf-8").replace(
            "`docs/issue.v10.0.0.route-cleanup.md`",
            "-",
        ),
        encoding="utf-8",
    )

    with pytest.raises(PromptWorkflowError, match="must name its requirement"):
        skill.post_merge_command(
            tmp_path,
            "docs/draft.v10.0.0.sentinel.md",
            _CLAUDE,
        )


def test_post_merge_command_rejects_incomplete_completed_evidence(
    tmp_path: Path,
) -> None:
    """A completed row cannot point at an incomplete validation plan."""
    _setup_collection_tree(tmp_path)
    (
        tmp_path / "docs" / "plan.v10.0.0.route-cleanup.validation.md"
    ).write_text("# Validation\n\nNo, it is not implemented.\n", encoding="utf-8")

    with pytest.raises(PromptWorkflowError, match="complete validation evidence"):
        skill.post_merge_command(
            tmp_path,
            "docs/draft.v10.0.0.sentinel.md",
            _CLAUDE,
        )


def test_post_merge_command_rejects_completed_paths_outside_root(
    tmp_path: Path,
) -> None:
    """Canonical evidence paths cannot escape the project."""
    umbrella = _setup_collection_tree(tmp_path)
    umbrella.write_text(
        umbrella.read_text(encoding="utf-8").replace(
            "`docs/issue.v10.0.0.route-cleanup.md`",
            "`../route-cleanup.md`",
        ),
        encoding="utf-8",
    )

    with pytest.raises(PromptWorkflowError, match="leaves the project root"):
        skill.post_merge_command(
            tmp_path,
            "docs/draft.v10.0.0.sentinel.md",
            _CLAUDE,
        )


def test_post_merge_command_rejects_invalid_or_empty_umbrellas(
    tmp_path: Path,
) -> None:
    """The lookup never guesses outside the root or from a malformed collection."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v10.0.0.empty.md").write_text("# Empty\n", encoding="utf-8")
    (docs_dir / "not-a-draft.md").write_text("# Nope\n", encoding="utf-8")

    assert skill.post_merge_command(tmp_path, "../outside.md", _CLAUDE) is None
    assert skill.post_merge_command(tmp_path, "docs/missing.md", _CLAUDE) is None
    assert skill.post_merge_command(tmp_path, "docs/not-a-draft.md", _CLAUDE) is None
    assert skill.post_merge_command(
        tmp_path,
        "docs/draft.v10.0.0.empty.md",
        _CLAUDE,
    ) is None


def test_run_skill_after_merge_emits_the_collection_command(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """run_skill handles --after-merge before ordinary topic resolution."""
    _setup_collection_tree(tmp_path)

    code = skill.run_skill(
        tmp_path,
        None,
        skill.HOST_CLAUDE,
        after_merge="docs/draft.v10.0.0.sentinel.md",
    )

    assert code == 0
    assert capsys.readouterr().out == (
        "/process-draft on docs/draft.v10.0.0.sentinel.md "
        "based on root-routing\n"
    )


def test_run_skill_routes_an_exact_umbrella_branch_without_after_merge(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Generic skill lookup reads an umbrella branch's ordered current status."""
    umbrella = _setup_collection_tree(tmp_path)
    child = tmp_path / "docs" / "draft.v10.0.0.route-cleanup.md"
    child.write_text("# Child topic\n", encoding="utf-8")
    topics = [
        Topic(version="v10.0.0", slug="route-cleanup", draft_path=child),
        Topic(version="v10.0.0", slug="sentinel", draft_path=umbrella),
    ]
    stale = MemoryRecord(
        branch="route-cleanup",
        version="v10.0.0",
        topic="route-cleanup",
    )

    def current_branch(_root: Path) -> str:
        return "sentinel"

    def relevant_drafts(
        _root: Path,
        _cwd: Path,
        _branch: str | None,
    ) -> list[Topic]:
        return topics

    def read_memory(_root: Path) -> MemoryRecord:
        return stale

    monkeypatch.setattr(skill.git, "current_branch", current_branch)
    monkeypatch.setattr(
        skill.docs,
        "relevant_drafts",
        relevant_drafts,
    )
    monkeypatch.setattr(skill.memory, "read_memory", read_memory)

    code = skill.run_skill(tmp_path, None, skill.HOST_CODEX)

    assert code == 0
    assert capsys.readouterr().out == (
        "$llm-shared:process-draft on docs/draft.v10.0.0.sentinel.md "
        "based on root-routing\n"
    )


def test_run_skill_routes_a_clean_integration_umbrella_branch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A branch-matched umbrella remains resolvable after its merge diff is clean."""
    umbrella = _setup_collection_tree(tmp_path)
    review_umbrella = umbrella.with_name("draft.v10.0.0.review-mode.md")
    umbrella.rename(review_umbrella)
    (tmp_path / "docs" / "draft.v9.0.0.review_mode.md").write_text(
        "# A focused draft with the same normalized slug\n",
        encoding="utf-8",
    )

    def current_branch(_root: Path) -> str:
        return "review_mode"

    def relevant_drafts(
        _root: Path,
        _cwd: Path,
        _branch: str | None,
    ) -> list[Topic]:
        return []

    def read_memory(_root: Path) -> MemoryRecord | None:
        return None

    monkeypatch.setattr(skill.git, "current_branch", current_branch)
    monkeypatch.setattr(skill.docs, "relevant_drafts", relevant_drafts)
    monkeypatch.setattr(skill.memory, "read_memory", read_memory)

    code = skill.run_skill(tmp_path, None, skill.HOST_CODEX)

    assert code == 0
    assert capsys.readouterr().out == (
        "$llm-shared:process-draft on docs/draft.v10.0.0.review-mode.md "
        "based on root-routing\n"
    )


def test_main_dispatches_the_skill_after_merge(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The hub passes the umbrella path through --after-merge."""
    captured: dict[str, object] = {}

    def fake_run_skill(  # noqa: PLR0913
        root: Path,
        skill_name: str | None,
        host_override: str | None,
        after_commit: str | None,
        after_write: str | None,
        after_merge: str | None,
    ) -> int:
        captured["call"] = (
            root,
            skill_name,
            host_override,
            after_commit,
            after_write,
            after_merge,
        )
        return 0

    monkeypatch.setattr(prompt_workflow.skill, "run_skill", fake_run_skill)

    code = prompt_workflow.main(
        [
            "skill",
            "--after-merge",
            "docs/draft.v10.0.0.sentinel.md",
            "--root",
            str(tmp_path),
        ],
    )

    assert code == 0
    assert captured["call"] == (
        tmp_path.resolve(),
        None,
        None,
        None,
        None,
        "docs/draft.v10.0.0.sentinel.md",
    )
