#!/usr/bin/env python3
"""new_draft.py Scaffold a new development effort.

Interactively asks for a slug, proposes a patch/minor/major bump of the current
`pyproject.toml` version, checks the slug against local branches and every
declared remote, creates the branch (optionally inside a sibling
`<project>_<slug>` worktree), and writes a `docs/draft.vX.Y.Z.<slug>.md`
skeleton so the effort starts already isolated. The chosen version only labels
the draft and its filename; `pyproject.toml` is left untouched.

The non-interactive `--from-draft` mode, used by the `process-draft`
instruction, skips the prompts: it takes an existing draft, a slug, a version,
and a layout, then creates the branch and renames the draft into the chosen
tree.

Usage:
    python new_draft.py [--root <repo-root>]
    python new_draft.py --from-draft <draft.md> --slug <slug>
        [--version X.Y.Z] (--worktree | --in-place) [--root <repo-root>]

This file is the thin script hub: it bootstraps the import path and delegates to
`tools.new_draft_workflow`, which holds the workflow logic.
"""

from __future__ import annotations

import contextlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))

with contextlib.suppress(Exception):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools.new_draft_models import NewDraftError, SemanticVersion
from tools.new_draft_workflow import main as _workflow_main

if TYPE_CHECKING:
    from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """Delegate CLI execution to the workflow module."""
    return _workflow_main(argv)


__all__ = [
    "NewDraftError",
    "SemanticVersion",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())


# eof
