"""Structural contracts for prepare-release branch-role instructions.

The version-source contract covers an npm or VS Code extension project: its
`package.json` version is derived from `version.txt` after Step 9, set to the
release `X.Y.Z` with its `package-lock.json` root, and staged in the prepare
commit, the same way `pyproject.toml` and `uv.lock` are.
"""

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


# eof
