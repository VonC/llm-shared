"""TDD contracts for strict repository-local artifact-home configuration."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from tools import review_artifact_configuration as configuration_module
from tools.review_artifact_configuration import (
    ReviewArtifactConfiguration,
    caller_file_parents,
)
from tools.review_exchange_models import ReviewExchangeError


def test_absent_declaration_uses_portable_default(tmp_path: Path) -> None:
    """An absent declaration resolves to the repository-local `.reviews` home."""
    configuration = ReviewArtifactConfiguration.load(tmp_path)

    assert configuration.project_root == tmp_path.resolve()
    assert configuration.home == tmp_path.resolve() / ".reviews"
    assert configuration.relative_home == ".reviews"
    assert configuration.declared is False
    assert configuration.declaration_path == tmp_path / ".review-artifacts.ini"


def test_valid_declaration_normalizes_separators_and_dot_segments(
    tmp_path: Path,
) -> None:
    """One valid home is normalized into portable relative output."""
    (tmp_path / ".review-artifacts.ini").write_text(
        "[review-artifacts]\nhome = runtime\\./reviews\n",
        encoding="utf-8",
    )

    configuration = ReviewArtifactConfiguration.load(tmp_path)

    assert configuration.home == tmp_path.resolve() / "runtime" / "reviews"
    assert configuration.relative_home == "runtime/reviews"
    assert configuration.declared is True


@pytest.mark.parametrize(
    "value",
    ["", ".", "..", "../outside", "C:relative", "C:/absolute", "//server/share", "$HOME/reviews", "%TEMP%/reviews", "~/reviews"],
)
def test_invalid_path_classes_are_rejected(tmp_path: Path, value: str) -> None:
    """Absolute, external, expanded, root, and empty values fail closed."""
    (tmp_path / ".review-artifacts.ini").write_text(
        f"[review-artifacts]\nhome = {value}\n",
        encoding="utf-8",
    )

    with pytest.raises(ReviewExchangeError, match="artifact home"):
        ReviewArtifactConfiguration.load(tmp_path)


@pytest.mark.parametrize(
    "content",
    [
        "[review-artifacts]\nhome=.reviews\nhome=other\n",
        "[review-artifacts]\nhome=.reviews\nextra=value\n",
        "[other]\nhome=.reviews\n",
        "[review-artifacts]\nhome=.reviews\n[other]\nx=y\n",
    ],
)
def test_duplicate_and_unsupported_declaration_shape_is_rejected(
    tmp_path: Path,
    content: str,
) -> None:
    """Only one named section containing one home property is accepted."""
    (tmp_path / ".review-artifacts.ini").write_text(content, encoding="utf-8")

    with pytest.raises(ReviewExchangeError, match="artifact-home declaration"):
        ReviewArtifactConfiguration.load(tmp_path)


def test_existing_tracked_directory_is_rejected(tmp_path: Path) -> None:
    """A configured directory containing tracked evidence cannot be reused."""
    home = tmp_path / "tracked"
    home.mkdir()
    (tmp_path / ".review-artifacts.ini").write_text(
        "[review-artifacts]\nhome=tracked\n",
        encoding="utf-8",
    )

    with pytest.raises(ReviewExchangeError, match="tracked directory"):
        ReviewArtifactConfiguration.load(
            tmp_path,
            tracked_directory=lambda _root, _relative: True,
        )


def test_existing_symlink_escape_is_rejected(tmp_path: Path) -> None:
    """Physical link resolution cannot redirect the home outside the repository."""
    external = tmp_path.parent / f"{tmp_path.name}-external"
    external.mkdir()
    link = tmp_path / "linked"
    try:
        link.symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks are unavailable")
    (tmp_path / ".review-artifacts.ini").write_text(
        "[review-artifacts]\nhome=linked/reviews\n",
        encoding="utf-8",
    )

    with pytest.raises(ReviewExchangeError, match="outside repository"):
        ReviewArtifactConfiguration.load(tmp_path)


def test_declaration_directory_and_home_file_are_rejected(tmp_path: Path) -> None:
    """Configuration paths must have their one declared filesystem kind."""
    declaration = tmp_path / ".review-artifacts.ini"
    declaration.mkdir()
    with pytest.raises(ReviewExchangeError, match="not a file"):
        ReviewArtifactConfiguration.load(tmp_path)
    declaration.rmdir()
    declaration.write_text("[review-artifacts]\nhome=.reviews\n", encoding="utf-8")
    (tmp_path / ".reviews").write_text("not a directory", encoding="utf-8")
    with pytest.raises(ReviewExchangeError, match="not a directory"):
        ReviewArtifactConfiguration.load(tmp_path)


def test_existing_home_requires_exact_portable_ignore_bytes(tmp_path: Path) -> None:
    """A CRLF or otherwise modified catch-all file blocks silent repair."""
    home = tmp_path / ".reviews"
    home.mkdir()
    (home / ".gitignore").write_bytes(b"*\r\n")
    configuration = ReviewArtifactConfiguration.load(tmp_path)

    with pytest.raises(ReviewExchangeError, match="coverage is invalid"):
        configuration.prepare_home()


def test_home_creation_failure_rolls_back_and_cleanup_failure_is_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Creation reports write errors while best-effort rollback never masks them."""
    configuration = ReviewArtifactConfiguration.load(tmp_path)
    original_write = Path.write_bytes

    def fail_ignore_write(path: Path, content: bytes) -> int:
        if path == configuration.ignore_path:
            message = "write denied"
            raise OSError(message)
        return original_write(path, content)

    monkeypatch.setattr(Path, "write_bytes", fail_ignore_write)
    with pytest.raises(ReviewExchangeError, match="cannot create"):
        configuration.prepare_home()
    assert not configuration.home.exists()

    configuration.home.mkdir()

    def fail_unlink(path: Path, *, missing_ok: bool = False) -> None:
        del path, missing_ok
        message = "cleanup denied"
        raise OSError(message)

    monkeypatch.setattr(Path, "unlink", fail_unlink)
    configuration.rollback_prepared_home()
    assert configuration.home.exists()


def test_git_tracking_query_failure_is_reported(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An index-shaped but invalid repository cannot prove home safety."""
    home = tmp_path / ".reviews"
    home.mkdir()
    git = tmp_path / ".git"
    git.mkdir()
    (git / "index").write_bytes(b"not an index")
    failed_query = subprocess.CompletedProcess(
        ["git", "ls-files"],
        128,
        "",
        "invalid index",
    )
    runner = Mock(return_value=failed_query)
    monkeypatch.setattr(configuration_module.subprocess, "run", runner)

    with pytest.raises(ReviewExchangeError, match=r"cannot validate.*tracking"):
        ReviewArtifactConfiguration.load(tmp_path)
    runner.assert_called_once_with(
        ["git", "ls-files", "--", ".reviews"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )


def test_caller_files_are_accepted_only_in_the_artifact_home(
    tmp_path: Path,
) -> None:
    """Caller scratch belongs in the home and never at the repository root."""
    accepted = caller_file_parents(tmp_path)

    assert accepted == frozenset({tmp_path / ".reviews"})


def test_caller_file_parents_fail_closed_for_a_broken_declaration(
    tmp_path: Path,
) -> None:
    """An unusable declaration accepts no caller-owned path."""
    (tmp_path / ".review-artifacts.ini").write_text("not ini\n", encoding="utf-8")

    assert caller_file_parents(tmp_path) == frozenset()


# eof
