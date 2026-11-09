r"""Structural checks for the Codex skill package.

Fix: the Grok adapters (``.grok``) are scanned for canonical copies too, and
``llmup`` validates the package with llm-shared's own package tool, since
Codex no longer installs the plugin-creator helper scripts.

Fix: Codex reads the skills through the ``%USERPROFILE%\.agents\skills``
link to the clone, so every wrapper and compatibility redirect links relative
to its own file in the clone and must resolve there. ``llmup`` became
``bin\codex_skills_link.bat``, a read-only check of that link: no version
bump, no plugin install, no installed cache.
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
        f"(../../../../instructions/{instruction_name})"
    )
    packaged_redirect = (
        "Read and follow the canonical instruction at "
        f"[`instructions/{instruction_name}`]"
        f"(../../../instructions/{instruction_name}).\n"
    )
    assert skill.rstrip().endswith(skill_redirect)
    assert (plugin / "skills" / skill_name / "../../../../instructions" / instruction_name).is_file()
    assert (plugin / "instructions" / "../../../instructions" / instruction_name).is_file()
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
        "[`rules/docs_layout.md`](../../../rules/docs_layout.md).\n"
    )
    assert packaged != source


@pytest.mark.parametrize(("adapter", "candidates"), _duplicate_candidates(),
                         ids=lambda value: value.relative_to(ROOT).as_posix() if isinstance(value, Path) else None)
def test_llm_specific_markdown_never_copies_canonical_markdown(adapter: Path, candidates: tuple[Path, ...]) -> None:
    """Provider adapters cannot duplicate a canonical Markdown body."""
    content = adapter.read_bytes()
    assert all(content != candidate.read_bytes() for candidate in candidates), adapter


@pytest.mark.parametrize(("page", "expected"), [
    ("how-to/pick-up-skill-edits-without-restarting.md", "llmup"),
    ("how-to/link-the-skills-into-codex.md", "llmup --create"),
    ("how-to/link-the-skills-into-codex.md", "codex plugin remove llm-shared@personal"),
    ("reference/aliases-and-launchers.md", "llmup"),
    ("reference/repository-layout.md", "codex_skills_link"),
])
def test_llmup_documentation(page: str, expected: str) -> None:
    """Check each independently editable page against its shortcut contract."""
    assert expected in (steps.llm_shared_dir() / "wiki" / page).read_text(encoding="utf-8")


def test_llmup_alias_only_checks_the_codex_skills_link() -> None:
    """The console shortcut runs the self-locating link check, never a plugin install."""
    root = steps.llm_shared_dir()
    doskeys = (root / "senv.doskey").read_text(encoding="utf-8")
    launcher = (root / "bin" / "codex_skills_link.bat").read_text(encoding="utf-8")

    assert 'llmup="%LLM_SHARED_DIR%\\bin\\codex_skills_link.bat" $*' in doskeys
    assert "update_llm_shared_plugin" not in doskeys
    assert not (root / "bin" / "update_llm_shared_plugin.bat").exists()
    assert 'set "CLONE_DIR=%~dp0.."' in launcher
    assert '-I "%CLONE_DIR%\\tools\\codex_skills_link.py" %*' in launcher
    for removed in ("bump-version", "plugin add", "marketplace", "%LLM_SHARED_DIR%", "uv.exe"):
        assert removed not in launcher
