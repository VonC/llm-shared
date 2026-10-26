"""Unit tests for groundhog's atomic side-file publication.

Cover a transient lock that clears after two refused attempts, a lock that
never clears (raised after every attempt, with doubling waits), and another
``OSError`` that is raised at once, without a retry.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.groundhog import atomic


def _refusing(monkeypatch: pytest.MonkeyPatch, refusals: int, error: OSError) -> list[Path]:
    """Make ``Path.replace`` raise ``error`` for the first ``refusals`` calls."""
    calls: list[Path] = []
    real = Path.replace

    def replace(side: Path, target: Path) -> Path:
        calls.append(target)
        if len(calls) <= refusals:
            raise error
        return real(side, target)

    monkeypatch.setattr(Path, "replace", replace)
    return calls


def test_a_transient_lock_is_retried_until_the_side_file_lands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two refused attempts wait, then the third publishes the content."""
    side, target = tmp_path / "a.side.tmp", tmp_path / "a.target"
    side.write_text("done\n", encoding="utf-8")
    calls = _refusing(monkeypatch, 2, PermissionError(13, "Access is denied"))
    pauses: list[float] = []
    atomic.replace(side, target, pauses.append)
    assert len(calls) == 3  # noqa: PLR2004
    assert pauses == [atomic.FIRST_DELAY_SECONDS, atomic.FIRST_DELAY_SECONDS * 2]
    assert target.read_text(encoding="utf-8") == "done\n"


def test_a_lasting_lock_is_raised_after_every_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The caller still sees the error once the attempts are spent."""
    side = tmp_path / "a.side.tmp"
    side.write_text("x", encoding="utf-8")
    calls = _refusing(monkeypatch, atomic.ATTEMPTS, PermissionError(13, "Access is denied"))
    pauses: list[float] = []
    with pytest.raises(PermissionError):
        atomic.replace(side, tmp_path / "a.target", pauses.append)
    assert len(calls) == atomic.ATTEMPTS
    assert len(pauses) == atomic.ATTEMPTS - 1


def test_another_os_error_is_never_retried(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Only the transient lock is retried."""
    calls = _refusing(monkeypatch, 1, FileNotFoundError(2, "missing"))
    pauses: list[float] = []
    with pytest.raises(FileNotFoundError):
        atomic.replace(tmp_path / "a.side.tmp", tmp_path / "a.target", pauses.append)
    assert len(calls) == 1
    assert pauses == []


# eof
