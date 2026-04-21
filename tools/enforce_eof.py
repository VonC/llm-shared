"""A tool to enforce a consistent '# eof' marker at the end of Python files.

This script scans all *.py files in the 'src/' and 'tools/' directories,
ignoring '__pycache__' folders. For each file, it checks if it ends with
the required sequence: two empty lines, '# eof', and a final newline.

If a file does not conform, it is automatically updated.

Fix (ruff): Replace all `print` calls with a configured logger to resolve T201
errors. Change broad `except Exception` to more specific `IOError` and `OSError`
to resolve BLE001. Restructure a `try` block with an `else` to fix TRY300.

Fix (ruff): Replace `IOError` with `OSError` (UP024). Use `logging.exception`
in except blocks (TRY400). Use lazy %-formatting for logs (G004).

Fix: Update the EOF sequence to ensure two empty lines are present before the
'# eof' marker, not just one.

Fix: Remove all existing '# eof' markers from the end of a file before
appending the new, correct sequence. This prevents duplicate markers.

Fix (root): Reuse the shared `find_project_root` helper so EOF enforcement
honors `PRJ_DIR` and follows the same project-root logic as the other tools.
"""

from __future__ import annotations

import contextlib
import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

if __name__ == "__main__":
    with contextlib.suppress(Exception):
        _project_root = Path(__file__).parent.parent.resolve()
        sys.path.insert(0, str(_project_root))
        sys.path.insert(0, str((_project_root / "src").resolve()))

from tools import find_project_root

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def _iter_python_files(roots: list[Path]) -> Iterable[Path]:
    """Yield Python files under a list of root directories, skipping __pycache__."""
    for root in roots:
        if not root.is_dir():
            continue
        for dirpath, _, filenames in os.walk(root):
            if "__pycache__" in Path(dirpath).parts:
                continue
            for file in filenames:
                if file.endswith(".py"):
                    yield Path(dirpath) / file


def _process_file(file_path: Path) -> bool:
    """Check and enforce the '# eof' sequence at the end of a file.

    Args:
        file_path: The path to the Python file to process.

    Returns:
        True if the file was modified, False otherwise.
    """
    eof_sequence = "\n\n\n# eof\n"
    try:
        original_content = file_path.read_text(encoding="utf-8")
        content = original_content

        # Repeatedly strip any existing '# eof' sections from the end.
        while content.rstrip().endswith("# eof"):
            last_eof_pos = content.rfind("# eof")
            content = content[:last_eof_pos].rstrip()

        # Normalize by stripping all trailing whitespace and newlines,
        # then append the required sequence.
        updated_content = content.rstrip() + eof_sequence

        if updated_content == original_content:
            return False

        file_path.write_text(updated_content, encoding="utf-8")
    except OSError:
        logger.exception("Error processing file %s", file_path)
        return False
    else:
        return True


def main() -> None:
    """Main function to find and process all relevant Python files."""
    try:
        project_root = find_project_root(Path(__file__).parent)
        logger.info("Project root found at: %s", project_root)

        scan_dirs = [project_root / "src", project_root / "tools"]
        logger.info("Scanning directories: %s", [str(d) for d in scan_dirs])

        modified_files_count = 0
        total_files_count = 0

        for file_path in _iter_python_files(scan_dirs):
            total_files_count += 1
            if _process_file(file_path):
                logger.info("Updated: %s", file_path.relative_to(project_root))
                modified_files_count += 1

        logger.info("\n--- Summary ---")
        logger.info("Total Python files scanned: %d", total_files_count)
        logger.info("Files updated: %d", modified_files_count)
        logger.info("Scan complete.")

    except FileNotFoundError:
        logger.exception("Error finding project root")
    except OSError:
        logger.exception("An unexpected file system error occurred")


if __name__ == "__main__":
    main()


# eof
