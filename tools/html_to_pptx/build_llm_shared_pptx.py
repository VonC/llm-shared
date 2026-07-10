"""Rebuild docs/llm-shared_presentation.html as an editable PowerPoint.

This worked example builds the deck with the primitives of pptx_helpers.py.
Run it from anywhere:

    python tools/html_to_pptx/build_llm_shared_pptx.py

It writes docs/llm-shared_presentation.pptx (16 slides, text and vector
shapes only -- no images). Every pixel coordinate is read from the matching
slide in the HTML source; the Theme maps 1280x720 px onto a 13.333in x 7.5in
16:9 slide, so the numbers transfer without re-layout.

Treat this folder as the pattern to copy for any other HTML deck: keep the
generic drawing in pptx_helpers.py, and keep one entry script like this one
per presentation, with its palette in deck_theme.py, its repeated patterns
in deck_parts.py and its slides in the slides_*.py modules.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Running this file directly (python build_llm_shared_pptx.py) starts with
# no importable package root: put the repository root on sys.path first, so
# the `tools.html_to_pptx` package imports below resolve from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.html_to_pptx.deck_theme import OUT, THEME
from tools.html_to_pptx.pptx_helpers import make_presentation
from tools.html_to_pptx.slides_intro import add_intro_slides
from tools.html_to_pptx.slides_main import add_main_slides

LOGGER = logging.getLogger("build_llm_shared_pptx")


def main() -> int:
    """Build the 16-slide deck and write it next to the HTML source."""
    prs = make_presentation(THEME)
    add_intro_slides(prs)
    add_main_slides(prs)
    prs.save(str(OUT))
    LOGGER.info("Saved %s with %s slides, %s KB", OUT, len(prs.slides),
                OUT.stat().st_size // 1024)
    return 0


def _configure_logging() -> None:
    """Configure stdout logging with message-only formatting."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


if __name__ == "__main__":
    _configure_logging()
    raise SystemExit(main())


# eof
