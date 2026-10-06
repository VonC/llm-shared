"""Structural contracts for prepare-release branch-role instructions.

The version-source contract covers an npm or VS Code extension project: its
`package.json` version is derived from `version.txt` after Step 9, set to the
release `X.Y.Z` with its `package-lock.json` root, and staged in the prepare
commit, the same way `pyproject.toml` and `uv.lock` are.

Fix: the run working files contract: the `a.prepare-release.active` flag, the
planner's preview object directories, scratch copies, and the release-notes
`a.md` all live in the review artifact home, never at the project root.
"""

import pytest

from tools import prompt_workflow_steps as steps

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


# eof
