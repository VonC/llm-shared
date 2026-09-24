"""Preserve rendering options, Unicode navigation and independently usable hooks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.serve_docs import render_contract, serve_docs

if TYPE_CHECKING:
    from pathlib import Path


def test_compatibility_import_uses_the_shared_contract() -> None:
    """Keep existing callers on the authoritative extracted implementation."""
    assert serve_docs.write_config is render_contract.write_config
    assert serve_docs.HOOK_TEMPLATE == render_contract.HOOK_TEMPLATE


def test_contract_preserves_complete_scaffold(tmp_path: Path) -> None:
    """Characterize theme settings and the hook before extracting their owner."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Home\n", encoding="utf-8")
    (docs / "plain-name.md").write_text("No heading\n", encoding="utf-8")
    for section in ("reference", "how-to", "tutorials", "explanation", "extras"):
        folder = docs / section
        folder.mkdir()
        (folder / "page.md").write_text(f"# {section} guide\n", encoding="utf-8")
    (docs / "empty").mkdir()
    work = tmp_path / "work"
    work.mkdir()

    config = serve_docs.write_config(docs, 'A "quoted" guide', work).read_text(encoding="utf-8")

    assert 'site_name: "A \\"quoted\\" guide"' in config
    assert '"Plain Name": "plain-name.md"' in config
    assert "Empty" not in config
    labels = ("Explanation", "Tutorials", "How-to guides", "Reference", "Extras")
    positions = [config.index(f'  - "{label}"') for label in labels]
    assert positions == sorted(positions)
    _assert_material_scaffold(config, work)


def _assert_material_scaffold(config: str, work: Path) -> None:
    """Check the fixed rendering settings and fullscreen integration."""
    assert "use_directory_urls: false" in config
    assert "font: false" in config
    assert "content.code.copy" in config
    assert "pymdownx.superfences.fence_code_format" in config
    hook = (work / "fullscreen_hook.py").read_text(encoding="utf-8")
    assert "Element.prototype.attachShadow" in hook
    assert "on_post_page" in hook
    assert "</body>" in hook


def test_empty_navigation_and_separate_navigation_root(tmp_path: Path) -> None:
    """Keep explicitly selected navigation independent from mounted includes."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "included.md").write_text("# Included\n", encoding="utf-8")
    navigation = tmp_path / "navigation"
    navigation.mkdir()
    config = serve_docs.write_config(docs, "Guide", tmp_path, navigation).read_text(encoding="utf-8")
    assert "Included" not in config
    assert "nav:\n" in config


# eof
