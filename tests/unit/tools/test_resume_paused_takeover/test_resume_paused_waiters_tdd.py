"""Check the live reviewer census against declared OS processes."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import psutil
import pytest

from tools.resume_paused_models import CanonicalRoot
from tools.resume_paused_waiters import waiter_reason

if TYPE_CHECKING:
    from pathlib import Path


def process(cwd: Path, verb: str = "wait-request") -> Mock:
    """Declare the exact script invocation a shared reviewer waiter uses."""
    waiter = Mock(spec=psutil.Process)
    waiter.name.return_value = "python.exe"
    waiter.cmdline.return_value = ["python", "review_exchange_cli.py", verb]
    waiter.cwd.return_value = str(cwd)
    waiter.environ.return_value = {}
    return waiter


@pytest.mark.parametrize("verb", ["wait-request", "wait-any-request"])
def test_surviving_and_ended_waiters(tmp_path: Path, verb: str) -> None:
    """A hibernated process remains active. A process that exits during observation disappears."""
    root = CanonicalRoot.from_path(tmp_path)
    waiter = process(tmp_path / "src", verb)
    assert waiter_reason(root, lambda: [waiter]) == "reviewer-wait-active"
    waiter.cmdline.side_effect = psutil.NoSuchProcess(100)
    assert waiter_reason(root, lambda: [waiter]) == ""
    assert waiter_reason(root, list) == ""


def test_waiter_from_a_different_directory(tmp_path: Path) -> None:
    """The configured project root can select the checkout even with a different working directory."""
    checkout = tmp_path / "target"
    checkout.mkdir()
    root = CanonicalRoot.from_path(checkout)
    other = tmp_path / "other"
    (other / ".git").mkdir(parents=True)
    waiter = process(other)
    waiter.environ.return_value = {"PRJ_DIR": str(checkout)}
    assert waiter_reason(root, lambda: [waiter]) == "reviewer-wait-active"
    waiter.environ.return_value = {}
    assert waiter_reason(root, lambda: [waiter]) == ""


def test_unreadable_process_and_unrelated_command(tmp_path: Path) -> None:
    """Unobservable Python arguments leave the reviewer pending. A wait-answer belongs to the requestor."""
    root = CanonicalRoot.from_path(tmp_path)
    waiter = process(tmp_path, "wait-answer")
    assert waiter_reason(root, lambda: [waiter]) == ""
    waiter.cmdline.side_effect = psutil.AccessDenied(100)
    assert waiter_reason(root, lambda: [waiter]) == "reviewer-wait-unknown"


def test_waiter_without_a_checkout_or_readable_command(tmp_path: Path) -> None:
    """Unknown Python waiters keep activation pending while other processes are ignored."""
    root = CanonicalRoot.from_path(tmp_path / "target")
    waiter = process(tmp_path / "elsewhere")
    with patch("tools.resume_paused_waiters.Path.exists", return_value=False):
        assert waiter_reason(root, lambda: [waiter]) == "reviewer-wait-unknown"
    waiter.cmdline.return_value = []
    assert waiter_reason(root, lambda: [waiter]) == "reviewer-wait-unknown"
    waiter.name.return_value = "editor.exe"
    assert waiter_reason(root, lambda: [waiter]) == ""


# eof
