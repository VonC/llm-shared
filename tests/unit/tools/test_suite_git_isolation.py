"""The suite's fixture repositories commit even where signing is mandatory.

A developer's global ``commit.gpgsign = true`` with an SSH key command that
refuses throwaway identities made fixture commits exit 128. The root conftest
appends ``commit.gpgsign=false`` through ``GIT_CONFIG_COUNT``; these tests pin
the appended entries and the active session environment without spawning Git,
since a forced-signing commit fixture cost 3.45s alone and 12.47s under load.

The native Git folder goes first on the session ``PATH`` only when ``git``
resolves to a Git for Windows launcher; the cases use fake installation
layouts, so they hold on any platform.
"""

from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING

import pytest

from tests.git_isolation import (
    NATIVE_GIT_FOLDER,
    native_git_path,
    unsigned_commit_settings,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_settings_start_at_the_first_entry_without_existing_configuration() -> None:
    """An environment without GIT_CONFIG_COUNT receives entry 0."""
    assert unsigned_commit_settings({}) == {
        "GIT_CONFIG_KEY_0": "commit.gpgsign",
        "GIT_CONFIG_VALUE_0": "false",
        "GIT_CONFIG_COUNT": "1",
    }


def test_settings_append_after_existing_entries() -> None:
    """Entries a caller already set keep their slots; signing goes after them."""
    existing = {
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "core.autocrlf",
        "GIT_CONFIG_VALUE_0": "false",
    }
    assert unsigned_commit_settings(existing) == {
        "GIT_CONFIG_KEY_1": "commit.gpgsign",
        "GIT_CONFIG_VALUE_1": "false",
        "GIT_CONFIG_COUNT": "2",
    }


def test_session_environment_disables_commit_signing() -> None:
    """Every Git child process of this session inherits commit.gpgsign=false."""
    index = int(os.environ["GIT_CONFIG_COUNT"]) - 1
    assert os.environ[f"GIT_CONFIG_KEY_{index}"] == "commit.gpgsign"
    assert os.environ[f"GIT_CONFIG_VALUE_{index}"] == "false"


def _installation(root: Path, *, native: bool) -> Path:
    """Lay out a fake Git for Windows installation and return its launcher."""
    launcher = root / "cmd" / "git.exe"
    launcher.parent.mkdir(parents=True)
    launcher.write_bytes(b"")
    if native:
        (root / NATIVE_GIT_FOLDER).mkdir(parents=True)
        (root / NATIVE_GIT_FOLDER / "git.exe").write_bytes(b"")
    return launcher


def test_a_launcher_puts_its_native_folder_first(tmp_path: Path) -> None:
    """A launcher beside an installed native git.exe leads PATH with its folder."""
    launcher = _installation(tmp_path, native=True)
    native = launcher.resolve().parent.parent / NATIVE_GIT_FOLDER
    assert native_git_path("rest", str(launcher)) == f"{native}{os.pathsep}rest"


@pytest.mark.parametrize("case", ["missing", "no-native-folder", "already-native"])
def test_other_git_locations_leave_the_path_unchanged(tmp_path: Path, case: str) -> None:
    """No Git, a lone git.exe, or the native one itself keep PATH as given."""
    launcher = _installation(tmp_path, native=case == "already-native")
    git = {"missing": None, "no-native-folder": str(launcher),
           "already-native": str(tmp_path / NATIVE_GIT_FOLDER / "git.exe")}[case]
    assert native_git_path("rest", git) == "rest"


def test_session_path_already_leads_with_the_native_git() -> None:
    """The root conftest applied the rule: applying it again changes nothing."""
    path = os.environ["PATH"]
    assert native_git_path(path, shutil.which("git", path=path)) == path


# eof
