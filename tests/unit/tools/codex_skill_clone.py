"""Lay out a minimal llm-shared clone whose Codex skill package is valid.

The redirect validator and the ``llmup`` link tool both read the package where
it lies in the clone, so their tests share one layout: one canonical
instruction, the docs layout rule, and the package manifest, wrapper and
compatibility redirects with clone-relative links.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

PACKAGE_FILES = {
    ".agents/llm-shared/.codex-plugin/plugin.json": json.dumps(
        {"version": "0.1.0", "name": "llm-shared", "skills": "./skills/"},
    ),
    ".agents/llm-shared/skills/sample/SKILL.md": (
        "---\nname: sample\ndescription: Run the sample workflow.\n---\n\n"
        "Read and follow [the canonical instruction](../../../../instructions/sample.md)\n"
    ),
    ".agents/llm-shared/instructions/sample.md": (
        "Read and follow the canonical instruction at "
        "[`instructions/sample.md`](../../../instructions/sample.md).\n"
    ),
    ".agents/llm-shared/rules/docs_layout.md": (
        "Read and follow the canonical rule at "
        "[`rules/docs_layout.md`](../../../rules/docs_layout.md).\n"
    ),
}
CANONICAL_FILES = {
    "instructions/sample.md": "# Sample\n",
    "rules/docs_layout.md": "# Layout\n",
}
COMPATIBILITY_REDIRECTS = (
    ".agents/llm-shared/instructions/sample.md",
    ".agents/llm-shared/rules/docs_layout.md",
)


def write_clone(root: Path, *, frontmatter: str = "") -> Path:
    """Write the clone under ``root``; ``frontmatter`` prefixes the two redirects."""
    for relative, text in (CANONICAL_FILES | PACKAGE_FILES).items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        prefix = frontmatter if relative in COMPATIBILITY_REDIRECTS else ""
        path.write_text(prefix + text, encoding="utf-8")
    return root


# eof
