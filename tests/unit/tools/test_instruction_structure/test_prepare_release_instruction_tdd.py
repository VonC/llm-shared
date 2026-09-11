"""Structural contracts for prepare-release branch-role instructions."""

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


# eof
