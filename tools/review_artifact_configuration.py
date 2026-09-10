"""Strict repository-local configuration for review runtime artifacts.

Step 1 introduces one optional versioned declaration and one prepared artifact
home. Parsing is side-effect free; home preparation is explicit so callers can
validate Git ignore coverage before exposing any protocol evidence.
"""

# ruff: noqa: EM101, EM102, S607, TRY003

from __future__ import annotations

import configparser
import subprocess
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING, Final

from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from collections.abc import Callable

_DECLARATION_NAME: Final = ".review-artifacts.ini"
_SECTION: Final = "review-artifacts"
_HOME_KEY: Final = "home"
_DEFAULT_HOME: Final = ".reviews"
_IGNORE_NAME: Final = ".gitignore"
_IGNORE_BYTES: Final = b"*\n"


def _tracked_directory(root: Path, relative: str) -> bool:
    """Return whether Git tracks any path below one existing directory."""
    git_metadata = root / ".git"
    if not git_metadata.exists():
        return False
    if git_metadata.is_dir() and not (git_metadata / "index").exists():
        return False
    completed = subprocess.run(  # noqa: S603
        ["git", "ls-files", "--", relative],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        diagnostic = completed.stderr.strip() or "git ls-files failed"
        raise ReviewExchangeError(
            f"cannot validate artifact home tracking: {diagnostic}",
        )
    return bool(completed.stdout.strip())


def _declaration_value(path: Path) -> tuple[str, bool]:
    """Read one strict declaration or return the default home."""
    if not path.exists():
        return _DEFAULT_HOME, False
    if not path.is_file():
        raise ReviewExchangeError("invalid artifact-home declaration: not a file")
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        content = path.read_text(encoding="utf-8")
        parser.read_string(content)
    except (OSError, UnicodeError, configparser.Error) as error:
        raise ReviewExchangeError(
            f"invalid artifact-home declaration: {error}",
        ) from error
    if parser.sections() != [_SECTION]:
        raise ReviewExchangeError(
            "invalid artifact-home declaration: expected one review-artifacts section",
        )
    properties = set(parser[_SECTION])
    if properties != {_HOME_KEY}:
        raise ReviewExchangeError(
            "invalid artifact-home declaration: expected only the home property",
        )
    return parser[_SECTION][_HOME_KEY].strip(), True


def _resolve_home(root: Path, value: str) -> tuple[Path, str]:
    """Normalize one portable path and enforce the physical root boundary."""
    if not value:
        raise ReviewExchangeError("artifact home must be a non-empty relative path")
    windows = PureWindowsPath(value)
    if (
        Path(value).is_absolute()
        or windows.is_absolute()
        or bool(windows.drive)
        or value.startswith(("~", "\\", "/"))
        or "$" in value
        or "%" in value
    ):
        raise ReviewExchangeError("artifact home must be repository-relative")
    candidate = (root / value.replace("\\", "/")).resolve(strict=False)
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise ReviewExchangeError("artifact home resolves outside repository") from error
    if relative == Path():
        raise ReviewExchangeError("artifact home cannot be the repository root")
    return candidate, relative.as_posix()


@dataclass(frozen=True)
class ReviewArtifactConfiguration:
    """Validated physical and portable paths for one artifact home."""

    project_root: Path
    home: Path
    relative_home: str
    declared: bool

    @classmethod
    def load(
        cls,
        project_root: Path,
        *,
        tracked_directory: Callable[[Path, str], bool] = _tracked_directory,
    ) -> ReviewArtifactConfiguration:
        """Load and validate the optional root declaration without writing."""
        root = project_root.resolve(strict=True)
        value, declared = _declaration_value(root / _DECLARATION_NAME)
        home, relative = _resolve_home(root, value)
        if home.exists():
            if not home.is_dir():
                raise ReviewExchangeError("artifact home is not a directory")
            if tracked_directory(root, relative):
                raise ReviewExchangeError("artifact home names an existing tracked directory")
        return cls(root, home, relative, declared)

    @property
    def declaration_path(self) -> Path:
        """Return the sole versioned artifact-home declaration path."""
        return self.project_root / _DECLARATION_NAME

    @property
    def ignore_path(self) -> Path:
        """Return the home-local catch-all ignore path."""
        return self.home / _IGNORE_NAME

    def prepare_home(self) -> bool:
        """Create a new catch-all home or validate an existing one's bytes."""
        if self.home.exists():
            try:
                content = self.ignore_path.read_bytes()
            except OSError as error:
                raise ReviewExchangeError(
                    f"artifact home ignore coverage is unreadable: {self.ignore_path}",
                ) from error
            if content != _IGNORE_BYTES:
                raise ReviewExchangeError(
                    f"artifact home ignore coverage is invalid: {self.ignore_path}",
                )
            return False
        try:
            self.home.mkdir(parents=True)
            self.ignore_path.write_bytes(_IGNORE_BYTES)
        except OSError as error:
            self.rollback_prepared_home()
            raise ReviewExchangeError(f"cannot create artifact home: {error}") from error
        return True

    def rollback_prepared_home(self) -> None:
        """Remove only a newly prepared empty home and its catch-all file."""
        try:
            self.ignore_path.unlink(missing_ok=True)
            self.home.rmdir()
        except OSError:
            return


def caller_file_parents(project_root: Path) -> frozenset[Path]:
    """Return the configured home for caller-owned review files."""
    root = project_root.resolve()
    try:
        home = ReviewArtifactConfiguration.load(root).home
    except ReviewExchangeError:
        return frozenset()
    return frozenset({home})


__all__ = ["ReviewArtifactConfiguration", "caller_file_parents"]


# eof
