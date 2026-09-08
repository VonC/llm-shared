"""Structural checks for the packaged Codex plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_steps as steps
from tools.llm_nature import LlmNature, LlmNatureDetector

if TYPE_CHECKING:
    from pathlib import Path

PluginSnapshot = tuple[
    set[str],
    set[str],
    tuple[tuple[str, str, str, bytes], ...],
]


def _markdown_bodies_by_path(
    root: Path,
    folders: tuple[str, ...],
) -> dict[Path, bytes]:
    """Read each Markdown body below the selected roots exactly once."""
    return {
        path.relative_to(root): path.read_bytes()
        for folder in folders
        for path in (root / folder).rglob("*.md")
    }


def _matching_canonical_bodies(
    root: Path,
    folders: tuple[str, ...],
    adapter_bodies: set[bytes],
) -> dict[bytes, Path]:
    """Read only canonical files whose sizes could match an adapter body."""
    adapter_sizes = {len(content) for content in adapter_bodies}
    canonical: dict[bytes, Path] = {}
    for folder in folders:
        for path in (root / folder).rglob("*.md"):
            if path.stat().st_size not in adapter_sizes:
                continue
            content = path.read_bytes()
            if content in adapter_bodies:
                canonical[content] = path.relative_to(root)
    return canonical


@pytest.fixture(scope="session")
def duplicate_markdown_bodies() -> dict[Path, Path]:
    """Scan provider and canonical Markdown once outside measured call time."""
    root = steps.llm_shared_dir()
    canonical_roots = (
        "instructions",
        "rules",
        "scripts",
        "templates",
        "bin",
        "tools",
        "docs",
        "wiki",
    )
    adapter_roots = (".agent", ".agents", ".claude", ".github")
    adapter_contents = _markdown_bodies_by_path(root, adapter_roots)
    adapter_bodies = set(adapter_contents.values())
    canonical = _matching_canonical_bodies(root, canonical_roots, adapter_bodies)
    return {
        path: canonical[content]
        for path, content in adapter_contents.items()
        if content in canonical
    }


@pytest.fixture(scope="session")
def codex_plugin_snapshot() -> PluginSnapshot:
    """Read the Codex package once, outside the measured test-call phase."""
    root = steps.llm_shared_dir()
    instructions = root / "instructions"
    plugin = root / ".agents" / "llm-shared"
    instruction_names = {path.name for path in instructions.glob("*.md")}
    expected_skill_names = {
        name.removesuffix(".md").replace("_", "-") for name in instruction_names
    }
    packaged_skill_names = {
        path.name for path in (plugin / "skills").iterdir() if path.is_dir()
    }
    rows = tuple(
        (
            name,
            (
                plugin
                / "skills"
                / name.removesuffix(".md").replace("_", "-")
                / "SKILL.md"
            ).read_text(encoding="utf-8"),
            (plugin / "instructions" / name).read_text(encoding="utf-8"),
            (instructions / name).read_bytes(),
        )
        for name in instruction_names
    )
    return expected_skill_names, packaged_skill_names, rows


def test_codex_plugin_redirects_every_instruction(
    codex_plugin_snapshot: PluginSnapshot,
) -> None:
    """Every shared instruction has matching Codex redirects, never a copy."""
    expected_skill_names, packaged_skill_names, rows = codex_plugin_snapshot
    assert packaged_skill_names == expected_skill_names
    for instruction_name, skill, packaged, source in rows:
        skill_redirect = (
            "Read and follow [the canonical instruction]"
            f"(../../../../../../../../git/llm-shared/instructions/{instruction_name})"
        )
        packaged_redirect = (
            "Read and follow the canonical instruction at "
            f"[`instructions/{instruction_name}`]"
            f"(../../../../../../../git/llm-shared/instructions/{instruction_name}).\n"
        )
        assert skill.rstrip().endswith(skill_redirect)
        packaged_body = packaged
        if packaged.startswith("---\n"):
            assert LlmNatureDetector.adapter_nature(packaged) is LlmNature.CODEX
            packaged_body = packaged.split("---\n", 2)[2].lstrip("\n")
        assert packaged_body == packaged_redirect
        assert packaged.encode("utf-8") != source


def test_codex_plugin_redirects_to_the_docs_layout_rule() -> None:
    """The packaged layout path redirects to the canonical root rule."""
    root = steps.llm_shared_dir()
    source = (root / "rules" / "docs_layout.md").read_text(encoding="utf-8")
    packaged = (
        root / ".agents" / "llm-shared" / "rules" / "docs_layout.md"
    ).read_text(encoding="utf-8")

    assert packaged == (
        "Read and follow the canonical rule at "
        "[`rules/docs_layout.md`](../../../../../../../git/llm-shared/rules/docs_layout.md).\n"
    )
    assert packaged != source


def test_llm_specific_markdown_never_copies_canonical_markdown(
    duplicate_markdown_bodies: dict[Path, Path],
) -> None:
    """Provider adapters cannot duplicate a canonical Markdown body."""
    assert duplicate_markdown_bodies == {}


def _assert_llmup_launcher(doskeys: str, launcher: str) -> None:
    """Check the alias and launcher validation pipeline."""
    assert 'llmup="%LLM_SHARED_DIR%\\bin\\update_llm_shared_plugin.bat"' in doskeys
    assert "--isolated --no-project --with PyYAML" in launcher
    assert "validate_plugin.py" in launcher
    assert "update_plugin_cachebuster.py" in launcher


def _assert_llmup_installation(launcher: str) -> None:
    """Check redirect generation and marketplace replacement commands."""
    assert "read_marketplace_name.py" in launcher
    assert "codex_plugin_redirects.py" in launcher
    assert "--installed" in launcher
    assert "plugin add llm-shared@%MARKETPLACE_NAME%" in launcher


def _assert_llmup_documentation(root: Path, pages: tuple[Path, ...]) -> None:
    """Check the shortcut remains discoverable in each user-facing page."""
    layout = (root / "wiki" / "reference" / "repository-layout.md").read_text(
        encoding="utf-8",
    )
    assert all("llmup" in path.read_text(encoding="utf-8") for path in pages)
    assert "update_llm_shared_plugin" in layout


def test_llmup_alias_refreshes_the_personal_codex_plugin() -> None:
    """The console shortcut keeps the documented plugin update loop together."""
    root = steps.llm_shared_dir()
    doskeys = (root / "senv.doskey").read_text(encoding="utf-8")
    launcher = (root / "bin" / "update_llm_shared_plugin.bat").read_text(
        encoding="utf-8",
    )
    wiki = root / "wiki"
    pages = (
        wiki / "how-to" / "pick-up-skill-edits-without-restarting.md",
        wiki / "how-to" / "register-skills-as-a-codex-plugin.md",
        wiki / "reference" / "aliases-and-launchers.md",
    )
    _assert_llmup_launcher(doskeys, launcher)
    _assert_llmup_installation(launcher)
    assert 'findstr /I /C:"llm-shared@%MARKETPLACE_NAME%"' in launcher
    _assert_llmup_documentation(root, pages)
