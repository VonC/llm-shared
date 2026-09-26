"""Place tool and scratch files in the review artifact home, never at the root.

Every `a.*` working file a tool or an agent creates belongs in the artifact
home (`.reviews` unless `.review-artifacts.ini` declares another home), which
holds a `.gitignore` of exactly `*`. Only a few human-facing files stay at the
project root; see `rules/artifact_files.md` for the list.

This module is the one place tools resolve such a path. `artifact_path`
prepares the home and returns the file path inside it. When the file still
exists at the project root under the same name, from before a tool moved it,
the root copy is moved into the home first, so a tool keeps its state (for
example groundhog's recorded outlier exclusions) across the move.

Usage from a shell, printing the resolved path::

    python -m tools.artifact_home <project-root> <file-name>
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tools.review_artifact_configuration import ReviewArtifactConfiguration

if TYPE_CHECKING:
    from collections.abc import Sequence

EXIT_OK = 0
EXIT_USAGE = 2


def artifact_home(root: Path) -> Path:
    """Return the prepared artifact home of a project.

    Args:
        root: The project root.

    Returns:
        The artifact home, created with its `*` ignore file when missing.

    Raises:
        ReviewExchangeError: When the declaration or the existing home is invalid.
    """
    configuration = ReviewArtifactConfiguration.load(root)
    configuration.prepare_home()
    return configuration.home


def artifact_path(root: Path, name: str) -> Path:
    """Return the home path of one tool file, moving a legacy root copy first.

    Args:
        root: The project root.
        name: The plain file name, such as `a.ghog.outliers`.

    Returns:
        The file path inside the prepared artifact home.

    Raises:
        ValueError: When the name is not a plain file name.
        ReviewExchangeError: When the artifact home is invalid.
    """
    if not name or Path(name).name != name or name in {".", ".."}:
        message = f"artifact file name must be a plain name: {name!r}"
        raise ValueError(message)
    target = artifact_home(root) / name
    legacy = root / name
    if legacy.exists() and not target.exists():
        legacy.replace(target)
    return target


def main(argv: Sequence[str] | None = None) -> int:
    """Print the home path of one file for a shell caller.

    Args:
        argv: `<project-root> <file-name>`; defaults to the process arguments.

    Returns:
        0 with the path printed, 2 on a usage error or an invalid home.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:  # noqa: PLR2004 - root and name
        sys.stderr.write("usage: python -m tools.artifact_home <project-root> <file-name>\n")
        return EXIT_USAGE
    try:
        path = artifact_path(Path(args[0]).resolve(), args[1])
    except (OSError, ValueError) as error:
        sys.stderr.write(f"artifact_home: {error}\n")
        return EXIT_USAGE
    sys.stdout.write(f"{path}\n")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())


# eof
