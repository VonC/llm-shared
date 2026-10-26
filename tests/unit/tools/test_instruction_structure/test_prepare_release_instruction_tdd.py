"""Structural contracts for prepare-release branch-role instructions.

The version-source contract covers an npm or VS Code extension project: its
`package.json` version is derived from `version.txt` after Step 9, set to the
release `X.Y.Z` with its `package-lock.json` root, and staged in the prepare
commit, the same way `pyproject.toml` and `uv.lock` are.

Fix: the run working files contract: the `a.prepare-release.active` flag, the
planner's preview object directories, scratch copies, and the release-notes
`a.md` all live in the review artifact home, never at the project root.

Fix: the release wiki-audit, read-only planner, unsupported-path handoff and
gitworkflow contracts moved here from `test_instruction_structure_tdd.py`,
which had grown past the 650-line limit of the big-file check.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_steps as steps

if TYPE_CHECKING:
    from pathlib import Path

_INSTRUCTIONS = steps.llm_shared_dir() / "instructions"


def _read(name: str) -> str:
    """Return the text of an instruction file."""
    return (_INSTRUCTIONS / name).read_text(encoding="utf-8")


def test_prepare_release_distinguishes_branch_roles() -> None:
    """prepare-release preserves integration history and isolates feature commits."""
    content = " ".join(_read("prepare-release.md").split())
    assert "On-main release" in content
    assert "Integration release" in content
    assert "Feature completion" in content
    assert "Never rebase a published, long-lived integration branch" in content
    assert (
        'rebase --onto "<target_branch>" "<feature_base>" "<landing_branch>"'
        in content
    )
    assert "do not blindly use the oldest entry" in content
    assert "Preserve the original feature ref" in content
    assert 'There is no feature-mode "merge stale anyway" path' in content
    assert 'merge --no-ff "<source_branch>"' in content


def test_prepare_release_routes_collection_topics_to_the_umbrella_branch() -> None:
    """An umbrella association is resolved before the first planner call."""
    content = " ".join(_read("prepare-release.md").split())

    assert "umbrella slug names its integration branch" in content
    assert "folding hyphens and underscores" in content
    assert '--umbrella "<umbrella_draft>"' in content
    assert "must never fall back to `main`" in content


def test_prepare_release_documents_default_develop_variant() -> None:
    """The local variant lands topics on develop before release preparation."""
    content = " ".join(_read("prepare-release.md").split())
    assert "published long-lived hosting default" in content
    assert "umbrella slug names its integration branch" in content
    assert "generic integration branch such as `develop`" in content
    assert "standalone topic with no integration branch uses `main`" in content
    assert "Only after the umbrella is exhausted" in content


def test_prepare_release_bumps_package_json_after_version_txt() -> None:
    """package.json follows the version.txt target, like pyproject.toml."""
    content = " ".join(_read("prepare-release.md").split())
    assert (
        "`package.json`: set its `version` to the release `X.Y.Z`" in content
    )
    assert "read from the first word of `version.txt`" in content
    assert "never ahead of it" in content
    assert (
        'npm --prefix "<PRJ_DIR>" version X.Y.Z --no-git-tag-version'
        " --allow-same-version" in content
    )
    assert "`package-lock.json` root" in content
    assert "only `major.minor.patch`" in content
    assert "`package.json` and `package-lock.json`" in content


def test_prepare_release_keeps_run_files_in_the_artifact_home() -> None:
    """The flag, previews, scratch copies, and a.md live in the artifact home."""
    release = " ".join(_read("prepare-release.md").split())
    notes = " ".join(_read("prepare-release-notes.md").split())

    assert '--root "<PRJ_DIR>" --artifact-home' in release
    assert 'touch "<ARTIFACT_HOME>/a.prepare-release.active"' in release
    assert 'rm -f "<ARTIFACT_HOME>/a.prepare-release.active"' in release
    assert "`a.prepare-release-preview.<random>` in `<ARTIFACT_HOME>`" in release
    assert "Never create a working file or folder at the project root" in release
    assert "<PRJ_DIR>/a." not in release
    assert "`<ARTIFACT_HOME>/a.md`" in notes
    assert "`a.prepare-release.active` in the review artifact home" in notes
    assert "<PRJ_DIR>/a." not in notes


@pytest.mark.parametrize(
    "required",
    [
        "or an umbrella integration branch requires `ghog day --full=cov --whole-suite`",
        "group proof cannot satisfy this gate",
        "Containing the latest destination does not waive validation",
        "Run the green-gate routine on main before continuing",
        "run the green-gate routine on the integration branch",
        "switch to the target, run the green-gate routine on that destination",
        "switch to it, and run the green-gate routine before continuing to Step 6",
        "green gate even when no sync is needed",
        "if conflict resolution or any other change produced a different tree",
    ],
    ids=["umbrella", "whole-proof", "current", "main", "integration", "resume", "direct", "exhausted", "changed-tree"],
)
def test_prepare_release_gates_every_promotion_and_preparation_route(required: str) -> None:
    """Current branches and resumed umbrella work cannot bypass whole-suite proof."""
    content = " ".join(_read("prepare-release.md").split())
    assert required in content
    assert "no extra test" not in content
    assert "was not needed because the selected branch" not in content


def _assert_release_wiki_step(instruction: str) -> None:
    """Check the prepare-release instruction's wiki-audit contract."""
    content = " ".join(instruction.split())
    assert "### Step 8 — Audit and update existing Diataxis wiki roots" in instruction
    assert "`<PRJ_DIR>/wiki`" in instruction
    assert "`<PRJ_DIR>/docs/wiki`" in instruction
    assert "complete release range `<last_tag>..HEAD`" in content
    assert "`review-and-update-project-docs`" in instruction
    assert "`group-commits-msg`" in instruction
    assert instruction.index("### Step 8") < instruction.index(
        "### Step 10 — Prepare the release notes",
    )


def _assert_release_wiki_review_contract(review: str) -> None:
    """Check the project-doc review contract used by release preparation."""
    content = " ".join(review.split())
    assert "`wiki/` or `docs/wiki/`" in content
    assert "If a Git range was provided" in review
    assert "explanation, tutorials, how-to guides, then reference" in content
    assert "a.prepare-release.active" in review


def _assert_release_wiki_files(root: Path) -> None:
    """Check Diataxis coverage and host entry-point coverage."""
    pages = (
        root / "wiki" / "explanation" / "why-documents-before-code.md",
        root / "wiki" / "tutorials" / "05-prepare-a-release-from-develop.md",
        root / "wiki" / "how-to" / "prepare-a-release.md",
        root / "wiki" / "reference" / "skills-catalog.md",
    )
    for path in pages:
        assert "wiki" in path.read_text(encoding="utf-8").lower()

    entry_points = (
        root / ".github" / "skills" / "prepare-release" / "SKILL.md",
        root / ".claude" / "skills" / "prepare-release" / "SKILL.md",
        root / ".agents" / "llm-shared" / "skills" / "prepare-release" / "SKILL.md",
        root / ".agent" / "workflows" / "prepare-release.md",
    )
    for path in entry_points:
        assert "wiki" in path.read_text(encoding="utf-8").lower()


def test_prepare_release_audits_existing_diataxis_wikis_before_notes() -> None:
    """Release prep covers every release commit before generating its notes."""
    root = steps.llm_shared_dir()
    instruction = _read("prepare-release.md")
    review = _read("review-and-update-project-docs.md")
    _assert_release_wiki_step(instruction)
    _assert_release_wiki_review_contract(review)
    _assert_release_wiki_files(root)


def test_prepare_release_stops_historical_feature_merges() -> None:
    """prepare-release does not reword a non-tip historical feature merge."""
    content = " ".join(_read("prepare-release.md").split())
    assert "branch tip already released" in content
    assert "feature is already integrated into `<target_branch>`" in content
    assert "cannot safely invent or reword a non-tip historical merge" in content


def test_prepare_release_uses_read_only_planner_and_merge_tree_preview() -> None:
    """prepare-release plans topology and conflicts before changing branches."""
    content = " ".join(_read("prepare-release.md").split())
    assert "prepare_release_plan.bat" in content
    assert "--no-conflict-preview" in content
    assert "--feature-base" in content
    assert "git merge-tree --write-tree -z --name-only --messages" in content
    assert "isolated temporary object directory" in content
    assert "first conflict because a human resolution changes" in content


def test_prepare_release_planner_uses_package_directories() -> None:
    """Planner sources and tests live in matching prepare_release packages."""
    root = steps.llm_shared_dir()
    source = root / "tools" / "prepare_release"
    tests = root / "tests" / "unit" / "tools" / "prepare_release"
    launcher = (root / "bin" / "prepare_release_plan.bat").read_text(
        encoding="utf-8",
    )

    assert (source / "__init__.py").is_file()
    assert (source / "prepare_release_plan.py").is_file()
    assert (tests / "__init__.py").is_file()
    assert (tests / "test_prepare_release_plan_workflow.py").is_file()
    assert "tools\\prepare_release\\prepare_release_plan.py" in launcher


def test_prepare_release_treats_later_versions_as_notes() -> None:
    """The invocation branch selects content while the lowest new version labels it."""
    content = " ".join(_read("prepare-release.md").split())
    assert "Choose the lowest version strictly greater than the last" in content
    assert "feature-request" in content
    assert "forward-looking notes for later efforts" in content
    assert "Drafts never trigger Step 2" in content
    assert "selecting the invocation branch selects its content" in content
    assert "Later-version plans are forward-looking notes" in content


def test_prepare_release_owns_planner_invocation_end_to_end() -> None:
    """The caller supplies context; the skill runs every planner command itself."""
    content = " ".join(_read("prepare-release.md").split())
    assert "The user only has to invoke `$llm-shared:prepare-release`" in content
    assert "Never ask the user to run `prepare_release_plan.bat`" in content
    assert "Do not depend on the user's current shell having `LLM_SHARED_DIR`" in content
    assert "automatically rerun the release planner" in content

    root = steps.llm_shared_dir()
    tutorial = (root / "wiki/tutorials/05-prepare-a-release-from-develop.md").read_text(
        encoding="utf-8",
    )
    how_to = (root / "wiki/how-to/prepare-a-release.md").read_text(encoding="utf-8")
    for page in (tutorial, how_to):
        assert "$llm-shared:prepare-release" in page
        assert "$env:LLM_SHARED_DIR" not in page


def test_prepare_release_gives_actionable_unsupported_path_handoffs() -> None:
    """Unsupported planner paths stop safely with commands and a re-entry point."""
    content = " ".join(_read("prepare-release.md").split())

    assert "Unsupported planner handoffs" in content
    assert "Every unsupported result must end with an actionable block" in content
    assert "git revert -m 1 <excluded_merge_oid>" in content
    assert "git cherry-pick --abort" in content
    assert "Re-enter prepare-release" in content
    assert "no combined planner run can model an evolving main" in content
    assert "do not claim that the planner accepts an explicit commit list" in content
    assert "Independently count `main..<integration_branch>`" in content


def test_prepare_release_wiki_marks_planner_capability_boundaries() -> None:
    """Diátaxis pages distinguish supported paths from actionable stops."""
    root = steps.llm_shared_dir()
    scenarios = (root / "wiki/reference/prepare-release-scenarios.md").read_text(
        encoding="utf-8",
    )
    planner = (root / "wiki/reference/prepare-release-planner.md").read_text(
        encoding="utf-8",
    )
    how_to = (root / "wiki/how-to/prepare-a-release.md").read_text(encoding="utf-8")
    tutorial = (root / "wiki/tutorials/05-prepare-a-release-from-develop.md").read_text(
        encoding="utf-8",
    )

    assert "Required unsupported-path output" in scenarios
    assert "Supported and unsupported planning paths" in planner
    assert "git switch -c prepare-release/exclude-<topic>" in how_to
    assert "git switch -c prepare-release/<feature>-clean main" in how_to
    assert "The `main..develop` scope must contain at least one commit" in tutorial


def test_prepare_release_names_and_applies_gitworkflow_precisely() -> None:
    """Topic graduation is gitworkflow, while bulk develop promotion is explicit."""
    content = " ".join(_read("prepare-release.md").split())
    assert "Workflow model: gitworkflow topic graduation" in content
    assert 'Do not call this generic "Git flow"' in content
    assert "oldest integration branch it may eventually enter" in content
    assert "all-topics-ready bulk exception" in content
    assert "GitFlow-style recovery shortcut, not normal gitworkflow" in content
    assert "does not preview this revert path" in content
    assert "https://git-scm.com/docs/gitworkflows" in content
    assert "https://github.com/rocketraman/gitworkflow" in content


def test_gitworkflow_explanation_links_the_primary_context() -> None:
    """The explanation distinguishes the named workflow and cites its context."""
    explanation = (
        steps.llm_shared_dir() / "wiki/explanation/why-release-branch-roles-matter.md"
    ).read_text(encoding="utf-8")
    assert "The model is gitworkflow, one word" in explanation
    assert "This is not a spelling variant of generic" in explanation
    assert "https://stackoverflow.com/a/44470240/6309" in explanation
    assert "https://stackoverflow.com/a/216228/6309" in explanation
    assert "https://stackoverflow.com/a/53405887/6309" in explanation


# eof
