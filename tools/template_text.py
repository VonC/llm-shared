"""Read one shipped Markdown template as text.

Every renderer reads its template through this single function. Production
commands still read the file each time they render; a host that renders many
artifacts in one process, such as the test suite, can reuse the immutable text
by replacing this one function instead of five inline reads.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def read_template(path: Path) -> str:
    """Return the UTF-8 text of one template file.

    Args:
        path: The template file to read.

    Returns:
        The file's text. OS and decoding errors propagate unchanged, so each
        caller keeps its own error translation.
    """
    return path.read_text(encoding="utf-8")


# eof
