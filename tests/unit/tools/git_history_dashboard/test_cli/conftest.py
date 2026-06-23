"""Shared fixtures for the git-history dashboard CLI tests.

Step 3 (v0.8.0): ``cli.run`` builds the report through ``write_dashboard``, which
converts the analysis markdown through the ``uv``-backed ``convert_markdown``
seam. This autouse fixture stubs that seam so every CLI test stays fast and needs
neither ``uv`` nor the ``markdown`` package; the real seam is covered directly in
``test_analysis``.
"""
# pytest invokes the autouse fixture, which pyright cannot see as used.
# pyright: reportUnusedFunction=false

from __future__ import annotations

import pytest

from tools.git_history_dashboard import analysis


def _fake_convert(markdown_text: str) -> str:
    """Return the markdown wrapped in a div, standing in for the uv seam."""
    return f'<div class="analysis">{markdown_text}</div>'


@pytest.fixture(autouse=True)
def _stub_markdown_conversion(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the uv-backed markdown seam with a fast inline stub."""
    monkeypatch.setattr(analysis, "convert_markdown", _fake_convert)


# eof
