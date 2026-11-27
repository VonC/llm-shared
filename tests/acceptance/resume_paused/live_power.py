"""Stage and verify the human-operated Windows hibernate and restart checkpoints."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import psutil

from tests.acceptance.resume_paused.live_guest import POWERSHELL, REPO, executable, run
from tools.resume_paused_models import CanonicalRoot
from tools.resume_paused_waiters import waiter_reason

if TYPE_CHECKING:
    from pathlib import Path


WAITER_STOPPED_STEP = 2


def waiter_arguments(root: Path) -> list[str]:
    """Wait on an independent, unpublished document so pickup cannot claim the scenario exchange."""
    document = root / "docs/plan.v0.1.0.lab-waiter.md"
    return [sys.executable, "-m", "tools.review_exchange_cli", "wait-request", "--family", "code",
            "--document", str(document), "--implementation-step", "1", "--convergence-signal", "commit-ready",
            "--another-round-label", "Another round", "--continue-owning-workflow-label", "Commit", "--timeout-seconds", "3600"]


def start_waiter(lab: Path) -> None:
    """Keep the real waiter attached to the operator's second terminal until interrupted."""
    root = lab / "alpha"
    args = waiter_arguments(root)
    identity = lab / "waiter.json"
    env = dict(os.environ, PRJ_DIR=str(root), PYTHONPATH=str(REPO))
    with identity.open("x", encoding="utf-8") as stream, subprocess.Popen(  # noqa: S603
        args, cwd=root, env=env, stdout=subprocess.DEVNULL,
    ) as child:
        try:
            process = psutil.Process(child.pid)
            json.dump({"pid": child.pid, "created": process.create_time()}, stream)
            stream.flush()
            sys.stdout.write("Keep this terminal open through hibernation. After step 2 press Ctrl+C here.\n")
            code = child.wait()
            assert code == 0, f"Waiter exited {code} before cancellation"
        finally:
            if child.poll() is None:
                child.terminate()


def _same_waiter(lab: Path, index: int) -> None:
    identity = json.loads((lab / "waiter.json").read_text(encoding="utf-8"))
    root = CanonicalRoot.from_path(lab / "alpha")
    try:
        process = psutil.Process(identity["pid"])
        same = process.create_time() == identity["created"] and waiter_reason(root, lambda: (process,)) == "reviewer-wait-active"
    except psutil.NoSuchProcess:
        same = False
    assert same == (index < WAITER_STOPPED_STEP), "Check the original guest waiter in the second human terminal"
    expected = "reviewer-wait-active" if index < WAITER_STOPPED_STEP else ""
    assert waiter_reason(root) == expected, "Unexpected checkout waiter census"


def check_power(case: str, index: int, lab: Path, boot: str, first_boot: str) -> None:
    """Verify the current waiter, boot identity and a guest power event since the first step."""
    if case == "hibernate":
        _same_waiter(lab, index)
    if index != 1 or case not in {"hibernate", "reboot"}:
        return
    since = int((lab / "step-1/passed.json").stat().st_mtime)
    if case == "reboot":
        assert boot != first_boot, "Perform a full guest restart and restore the layout"
        provider, event, field, expected = "Microsoft-Windows-Kernel-Boot", 27, "BootType", 0
    else:
        assert boot == first_boot, "Hibernation must preserve the boot and waiter"
        provider, event, field, expected = "Microsoft-Windows-Kernel-Power", 42, "EffectiveState", 5
    query = (f"$e=Get-WinEvent -FilterHashtable @{{LogName='System'; ProviderName='{provider}';Id={event};"
             f"StartTime=[DateTimeOffset]::FromUnixTimeSeconds({since}).LocalDateTime}} -MaxEvents 1 -ErrorAction Stop;"
             f"(([xml]$e.ToXml()).Event.EventData.Data | Where-Object Name -eq '{field}').'#text'")
    value = run([str(executable(POWERSHELL)), "-NoProfile", "-Command", query]).stdout.strip()
    assert int(value, 0) == expected, f"Unexpected {provider} event {event} {field}: {value}"
    (lab / "power.json").write_text(json.dumps({"boot": boot, "event": event, field: value}), encoding="utf-8")


# eof
