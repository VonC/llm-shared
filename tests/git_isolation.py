r"""Git configuration that keeps fixture-repository commits unsigned.

A developer's global ``commit.gpgsign = true`` with an SSH key command that
refuses throwaway identities made fixture commits exit 128. The root conftest
applies these variables for the whole session; they append one
``commit.gpgsign=false`` entry after any ``GIT_CONFIG_*`` entries already set.

Fix: Git for Windows' ``cmd\git.exe`` and ``bin\git.exe`` are launchers
that start ``mingw64\bin\git.exe``, so every Git call of the suite started
two processes, each scanned on access. :func:`native_git_path` puts the native
folder first on the session ``PATH``; the native executable sets up the same
``MSYSTEM`` and hook ``PATH`` as its launcher.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

# The folder of the native git.exe, relative to a Git for Windows installation.
NATIVE_GIT_FOLDER: Final = Path("mingw64", "bin")


def unsigned_commit_settings(environ: Mapping[str, str]) -> dict[str, str]:
    """Return the ``GIT_CONFIG_*`` variables that append ``commit.gpgsign=false``."""
    index = int(environ.get("GIT_CONFIG_COUNT", "0"))
    return {
        f"GIT_CONFIG_KEY_{index}": "commit.gpgsign",
        f"GIT_CONFIG_VALUE_{index}": "false",
        "GIT_CONFIG_COUNT": str(index + 1),
    }


def native_git_path(path: str, git: str | None) -> str:
    r"""Return ``path`` with the native Git folder first when ``git`` is a launcher.

    Args:
        path: The ``PATH`` value to extend.
        git: Where ``git`` resolves on that ``PATH``, or ``None``.

    Returns:
        ``path`` led by the installation's ``mingw64\bin`` when ``git`` is a
        launcher in a top-level folder (``cmd``, ``bin``) of an installation
        that has a native ``git.exe``, else ``path``.
    """
    if git is None:
        return path
    found = Path(git).resolve()
    native = found.parent.parent / NATIVE_GIT_FOLDER
    if not (native / found.name).is_file():
        return path
    return f"{native}{os.pathsep}{path}"


# eof
