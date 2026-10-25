"""Probe native process creation time and distinguish PID reuse from live ownership."""

from __future__ import annotations

import os
from dataclasses import replace
from unittest.mock import MagicMock

import pytest

from tools.release_workflow import windows_process
from tools.release_workflow.windows_process import (
    ProcessIdentity,
    ProcessState,
    current_identity,
    process_state,
    transition_mutex,
)


def test_current_native_process_identity_and_reused_pid() -> None:
    """A real creation timestamp identifies this process, not merely its PID."""
    owner = current_identity()
    assert owner.pid == os.getpid()
    assert owner.created > 0
    assert process_state(owner) is ProcessState.ALIVE
    assert process_state(replace(owner, created=owner.created + 1)) is ProcessState.DEAD


@pytest.mark.parametrize(("opened", "wait", "error", "expected"), [
    (False, 0, 87, ProcessState.DEAD),
    (False, 0, 5, ProcessState.UNKNOWN),
    (True, 0, 0, ProcessState.DEAD),
    (True, 0xFFFFFFFF, 0, ProcessState.UNKNOWN),
    (True, 0x102, 0, ProcessState.UNKNOWN),
])
def test_native_probe_failures_are_conservative(
    monkeypatch: pytest.MonkeyPatch, *, opened: bool, wait: int, error: int, expected: ProcessState,
) -> None:
    """Only missing/signalled processes prove death; permissions are uncertainty."""
    api = MagicMock()
    api.OpenProcess.return_value = int(opened)
    api.WaitForSingleObject.return_value = wait
    api.GetProcessTimes.return_value = 0
    monkeypatch.setattr(windows_process, "_kernel", lambda: api)
    monkeypatch.setattr(windows_process.ctypes, "get_last_error", lambda: error)
    assert process_state(ProcessIdentity(123, 456)) is expected
    assert api.CloseHandle.call_count == int(opened)


def test_invalid_identity_and_unavailable_current_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid identities cannot authorize acquisition or automatic recovery."""
    assert process_state(ProcessIdentity(0, 1)) is ProcessState.UNKNOWN
    assert process_state(ProcessIdentity(1, 0)) is ProcessState.UNKNOWN
    def unavailable(_pid: int) -> tuple[ProcessState, int]:
        return ProcessState.UNKNOWN, 0
    monkeypatch.setattr(windows_process, "_probe", unavailable)
    with pytest.raises(OSError, match="creation time"):
        current_identity()


@pytest.mark.parametrize("wait", [0, 0x80])
def test_mutex_acquisition_and_abandonment_close_handles(monkeypatch: pytest.MonkeyPatch, wait: int) -> None:
    """An abandoned transition mutex is usable and always released after errors."""
    api = MagicMock()
    api.CreateMutexW.return_value = 1
    api.WaitForSingleObject.return_value = wait
    monkeypatch.setattr(windows_process, "_kernel", lambda: api)
    msg = "body"
    with pytest.raises(ValueError, match="body"), transition_mutex("fixture"):
        raise ValueError(msg)
    timeout = api.WaitForSingleObject.call_args.args[1]
    maximum_wait_ms = 5000
    assert 0 < timeout <= maximum_wait_ms
    api.ReleaseMutex.assert_called_once_with(1)
    api.CloseHandle.assert_called_once_with(1)


@pytest.mark.parametrize("opened", [False, True])
def test_mutex_failure_never_enters_transition(monkeypatch: pytest.MonkeyPatch, *, opened: bool) -> None:
    """A denied creation or busy mutex fails closed without releasing another owner."""
    api = MagicMock()
    api.CreateMutexW.return_value = int(opened)
    api.WaitForSingleObject.return_value = 0x102
    monkeypatch.setattr(windows_process, "_kernel", lambda: api)
    with pytest.raises(OSError, match="mutex"), transition_mutex("fixture"):
        pytest.fail("A denied transition must not run")
    api.ReleaseMutex.assert_not_called()
    assert api.CloseHandle.call_count == int(opened)


# eof
