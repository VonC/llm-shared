"""Navigation and root-mount tests for the local documentation server."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

import pytest

from tools.serve_docs.serve_docs import (
    build_root_snapshot,
    read_docs_config,
    resolve_settings,
    write_config,
)

if TYPE_CHECKING:
    from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_generated_navigation_uses_diataxis_order(tmp_path: Path) -> None:
    """The left sidebar follows explanation, tutorial, how-to, reference."""
    docs = tmp_path / "wiki"
    _write(docs / "README.md", "# Home\n")
    for section in ("reference", "how-to", "tutorials", "explanation"):
        _write(docs / section / "page.md", f"# {section}\n")
    work = tmp_path / "work"
    work.mkdir()

    config = write_config(docs, "Test", work).read_text(encoding="utf-8")

    positions = [config.index(f'  - "{label}"') for label in (
        "Explanation",
        "Tutorials",
        "How-to guides",
        "Reference",
    )]
    assert positions == sorted(positions)
    assert '- "Home": "README.md"' in config


def test_generated_navigation_preserves_emoji_in_h1_title(tmp_path: Path) -> None:
    """A non-BMP emoji remains valid UTF-8 in the rendered navigation title."""
    docs = tmp_path / "wiki"
    _write(docs / "README.md", "# Home\n")
    _write(docs / "explanation" / "page.md", "# 📚 Unicode guide\n")
    work = tmp_path / "work"
    work.mkdir()

    config = write_config(docs, "Test", work).read_text(encoding="utf-8")

    assert '      - "📚 Unicode guide": "explanation/page.md"' in config
    assert "\\ud83d\\udcda" not in config
    config.encode("utf-8")


def test_root_snapshot_rewrites_escaping_links_without_expanding_nav(
    tmp_path: Path,
) -> None:
    """Flattened wiki links reach mounted docs without adding nav sections."""
    wiki = tmp_path / "wiki"
    deck = tmp_path / "docs" / "deck.html"
    rules = tmp_path / "rules"
    _write(wiki / "README.md", "# Wiki\n[Deck](../docs/deck.html)\n")
    _write(
        wiki / "how-to" / "page.md",
        "# Guide\n[Rule](../../rules/example.md)\n"
        "[Reference](../reference/page.md)\n",
    )
    _write(wiki / "reference" / "page.md", "# Reference\n")
    _write(deck, "<h1>Deck</h1>\n")
    _write(rules / "example.md", "# Rule\n")

    work = tmp_path / "work"
    combined = build_root_snapshot(wiki, [deck, rules], work)
    config = write_config(
        combined,
        "Test",
        work,
        navigation_root=wiki,
    ).read_text(encoding="utf-8")

    assert "[Deck](docs/deck.html)" in (combined / "README.md").read_text(
        encoding="utf-8",
    )
    guide = (combined / "how-to" / "page.md").read_text(encoding="utf-8")
    assert "[Rule](../rules/example.md)" in guide
    assert "[Reference](../reference/page.md)" in guide
    assert (combined / "docs" / "deck.html").read_text(encoding="utf-8") == "<h1>Deck</h1>\n"
    assert '  - "How-to guides":' in config
    assert '  - "Rules":' not in config


def test_folder_config_loads_and_validates_root_includes(tmp_path: Path) -> None:
    """A short alias can mount presentation assets through serve_docs.ini."""
    wiki = tmp_path / "wiki"
    deck = tmp_path / "docs" / "deck.html"
    _write(wiki / "README.md", "# Wiki\n")
    _write(deck, "deck\n")
    _write(
        wiki / "serve_docs.ini",
        "[serve_docs]\nname = Wiki\nport = 8123\nroot_include = ../docs/deck.html\n",
    )
    name, port, includes, root_includes = read_docs_config(wiki)
    assert (name, port, includes, root_includes) == ("Wiki", 8123, [], [deck])

    args = argparse.Namespace(
        name=None,
        port=None,
        include=[],
        root_include=[],
    )
    assert resolve_settings(args, wiki) == ("Wiki", 8123, [], [deck])


def test_resolver_rejects_conflicting_or_escaping_mounts(tmp_path: Path) -> None:
    """Snapshot modes cannot mix or copy a root mount from outside the project."""
    wiki = tmp_path / "project" / "wiki"
    sibling = tmp_path / "project" / "docs" / "deck.html"
    outside = tmp_path / "outside.html"
    _write(wiki / "README.md", "# Wiki\n")
    _write(sibling, "deck\n")
    _write(outside, "outside\n")
    conflict = argparse.Namespace(
        name=None,
        port=8000,
        include=[str(sibling)],
        root_include=[str(sibling)],
    )
    with pytest.raises(SystemExit, match="cannot be combined"):
        resolve_settings(conflict, wiki)
    escaping = argparse.Namespace(
        name=None,
        port=8000,
        include=[],
        root_include=[str(outside)],
    )
    with pytest.raises(SystemExit, match="must stay below"):
        resolve_settings(escaping, wiki)
