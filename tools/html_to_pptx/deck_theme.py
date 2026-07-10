"""Palette, theme, branding and output location of the llm-shared deck.

The colors are the :root variables of docs/llm-shared_presentation.html, so
the rebuilt PowerPoint matches the HTML rendering. Import THEME plus the
named colors from here in every slide module; keep anything reusable across
decks in pptx_helpers.py instead.
"""

from __future__ import annotations

import os
from pathlib import Path

from tools.html_to_pptx.pptx_helpers import Theme, rgb

HERE = Path(__file__).resolve().parent
OUT = (HERE / ".." / ".." / "docs" / "llm-shared_presentation.pptx").resolve()

# --- palette (the HTML :root variables) ------------------------------------
BLUE = rgb("00566f")
ORANGE = rgb("ec6608")
GREEN = rgb("95c11f")
GRAY = rgb("717e86")
LGRAY = rgb("aaaaaa")
LIGHTBLUE = rgb("e6f0f3")
WARM = rgb("fff3e6")
LIGHT = rgb("f0f4f6")
TEAL = rgb("006d67")
DARK = rgb("1a2a30")
WHITE = rgb("ffffff")
TEXT = rgb("333333")
MUTED = rgb("666666")
MUTED2 = rgb("555555")
TSOFT = rgb("c4d8de")
TMUTED = rgb("8eb2bb")
CODE = rgb("8eb2bb")

THEME = Theme(primary=BLUE, accent=ORANGE, muted=GRAY, faint=LGRAY,
              white=WHITE, extra={"light": LIGHT, "muted": MUTED,
                                  "muted2": MUTED2, "text": TEXT})

# Brand placeholders. Like the HTML deck (which swaps them at render time
# through llm-shared_presentation.local.js), the build reads LLM_SHARED_BRAND
# and LLM_SHARED_BRAND_SUB from the environment and keeps the placeholders
# when they are not set.
BRAND = os.environ.get("LLM_SHARED_BRAND", "Organization name")
BRAND_SUB = os.environ.get("LLM_SHARED_BRAND_SUB", "ORGANIZATION SUBTITLE")


# eof
