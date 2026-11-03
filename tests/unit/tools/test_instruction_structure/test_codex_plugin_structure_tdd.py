"""Structural checks for the packaged Codex plugin.

Fix: the Grok adapters (``.grok``) are scanned for canonical copies too, and
``llmup`` validates and bumps the plugin with llm-shared's own package tool,
since Codex no longer installs the plugin-creator helper scripts.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_steps as steps
from tools.llm_nature import LlmNature, LlmNatureDetector

if TYPE_CHECKING:
    from collections.abc import Iterator

ROOT = steps.llm_shared_dir()
INSTRUCTION_NAMES = tuple(sorted(path.name for path in (ROOT / "instructions").glob("*.md")))
CANONICAL_ROOTS = ("instructions", "rules", "scripts", "templates", "bin", "tools", "docs", "wiki")
ADAPTER_ROOTS = (".agent", ".agents", ".claude", ".github", ".grok")


def _markdown_entries(folder: Path) -> Iterator[os.DirEntry[str]]:
    """Reuse directory metadata instead of statting every canonical file."""
    with os.scandir(folder) as entries:
        for entry in entries:
            if entry.is_dir(follow_symlinks=False):
                yield from _markdown_entries(Path(entry.path))
            elif entry.name.endswith(".md"):
                yield entry


def _duplicate_candidates() -> tuple[tuple[Path, tuple[Path, ...]], ...]:
    """Discover test inputs by size; every content read stays in its test."""
    canonical_by_size: dict[int, list[Path]] = {}
    for folder in CANONICAL_ROOTS:
        for entry in _markdown_entries(ROOT / folder):
            canonical_by_size.setdefault(entry.stat().st_size, []).append(Path(entry.path))
    return tuple(
        (Path(entry.path), tuple(canonical_by_size.get(entry.stat().st_size, ())))
        for folder in ADAPTER_ROOTS
        for entry in _markdown_entries(ROOT / folder)
    )


def test_codex_plugin_inventory_matches_every_instruction() -> None:
    """Missing and extra skill directories are both rejected."""
    plugin = ROOT / ".agents" / "llm-shared"
    expected_skill_names = {
        name.removesuffix(".md").replace("_", "-") for name in INSTRUCTION_NAMES
    }
    packaged_skill_names = {
        path.name for path in (plugin / "skills").iterdir() if path.is_dir()
    }
    assert packaged_skill_names == expected_skill_names


@pytest.mark.parametrize("instruction_name", INSTRUCTION_NAMES)
def test_codex_plugin_redirects_every_instruction(instruction_name: str) -> None:
    """Every shared instruction has matching Codex redirects, never a copy."""
    plugin = ROOT / ".agents" / "llm-shared"
    skill_name = instruction_name.removesuffix(".md").replace("_", "-")
    skill = (plugin / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
    packaged = (plugin / "instructions" / instruction_name).read_text(encoding="utf-8")
    source = (ROOT / "instructions" / instruction_name).read_bytes()
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


@pytest.mark.parametrize(("adapter", "candidates"), _duplicate_candidates(),
                         ids=lambda value: value.relative_to(ROOT).as_posix() if isinstance(value, Path) else None)
def test_llm_specific_markdown_never_copies_canonical_markdown(adapter: Path, candidates: tuple[Path, ...]) -> None:
    """Provider adapters cannot duplicate a canonical Markdown body."""
    content = adapter.read_bytes()
    assert all(content != candidate.read_bytes() for candidate in candidates), adapter


def _assert_llmup_launcher(doskeys: str, launcher: str) -> None:
    """Check the alias and launcher validation pipeline.

    The launcher runs llm-shared's own package tool with the llm-shared Python:
    Codex no longer installs the plugin-creator helper scripts it used to call.
    """
    assert 'llmup="%LLM_SHARED_DIR%\\bin\\update_llm_shared_plugin.bat"' in doskeys
    assert "codex_plugin_package.py" in launcher
    assert 'python "%PACKAGE_TOOL%" validate "%PLUGIN_ROOT%"' in launcher
    assert 'python "%PACKAGE_TOOL%" bump-version "%PLUGIN_ROOT%"' in launcher
    assert "plugin-creator\\scripts" not in launcher
    assert "uv.exe" not in launcher


def _assert_llmup_installation(launcher: str) -> None:
    """Check redirect generation and marketplace replacement commands."""
    assert 'marketplace-name "%MARKETPLACE_FILE%"' in launcher
    assert "codex_plugin_redirects.py" in launcher
    assert "--installed" in launcher
    assert "plugin add llm-shared@%MARKETPLACE_NAME%" in launcher


@pytest.mark.parametrize(("page", "expected"), [
    ("how-to/pick-up-skill-edits-without-restarting.md", "llmup"),
    ("how-to/register-skills-as-a-codex-plugin.md", "llmup"),
    ("reference/aliases-and-launchers.md", "llmup"),
    ("reference/repository-layout.md", "update_llm_shared_plugin"),
])
def test_llmup_documentation(page: str, expected: str) -> None:
    """Check each independently editable page against its shortcut contract."""
    assert expected in (steps.llm_shared_dir() / "wiki" / page).read_text(encoding="utf-8")


def test_llmup_alias_refreshes_the_personal_codex_plugin() -> None:
    """The console shortcut keeps the documented plugin update loop together."""
    root = steps.llm_shared_dir()
    doskeys = (root / "senv.doskey").read_text(encoding="utf-8")
    launcher = (root / "bin" / "update_llm_shared_plugin.bat").read_text(
        encoding="utf-8",
    )
    _assert_llmup_launcher(doskeys, launcher)
    _assert_llmup_installation(launcher)
    assert 'findstr /I /C:"llm-shared@%MARKETPLACE_NAME%"' in launcher
