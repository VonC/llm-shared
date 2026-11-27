"""Guest isolation and namespace checks for the operator-run acceptance lab."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, cast

from tests.acceptance.resume_paused.live_fixtures import SESSIONS
from tools.resume_paused import process_ancestry
from tools.resume_paused_profiles import CallerOrigin, classify_caller

if TYPE_CHECKING:
    from collections.abc import Sequence

REPO = Path(__file__).resolve().parents[3]
LAYOUT = "--- resume-lab\n=== Acceptance\n" + "".join(f"+ {root}|{name}|{kind}|{label}\n" for name, (root, kind, label) in SESSIONS.items())
POWERSHELL = "powershell.exe"
FACTS = """
$ErrorActionPreference='Stop'
$c=Get-CimInstance Win32_ComputerSystem
$os=Get-CimInstance Win32_OperatingSystem
$disk=Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3'
[pscustomobject]@{name=$c.Name;model=$c.Model;profile=[Environment]::GetFolderPath('UserProfile');
local=[Environment]::GetFolderPath('LocalApplicationData');drives=@($disk.DeviceID);
boot=$os.LastBootUpTime.ToUniversalTime().ToString('o')} | ConvertTo-Json -Compress
"""


def run(args: Sequence[str], *, cwd: Path = REPO, timeout: int = 40, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Use bounded native commands, keeping their real exit status and both output streams."""
    return subprocess.run(args, cwd=cwd, capture_output=True, check=check, timeout=timeout, encoding="utf-8", errors="replace")  # noqa: S603


def executable(name: str) -> Path:
    """Resolve installed guest tools before using them."""
    path = shutil.which(name)
    assert path, f"Missing from the guest terminal PATH: {name}"
    return Path(path).resolve(strict=True)


def guest_paths(facts: dict[str, object]) -> tuple[Path, Path]:
    """Require a named VM and guest-local storage for all mutable resources."""
    assert str(facts["name"]).upper() == "RP-LAB", "Requires disposable VM RP-LAB"
    assert re.search(r"Virtual Machine|VMware|VirtualBox", str(facts["model"]), re.IGNORECASE), "Requires disposable VM RP-LAB"
    profile, local = Path(str(facts["profile"])).resolve(), Path(str(facts["local"])).resolve()
    assert Path(os.environ["USERPROFILE"]).resolve() == profile
    assert Path(os.environ["LOCALAPPDATA"]).resolve() == local
    drives = cast("list[str]", facts["drives"])
    for path in (profile, local, REPO, executable("tuitp.bat"), executable("tuios")):
        assert path.drive.upper() in drives, f"Use a local disk and batch-safe path: {path}"
        assert re.fullmatch(r"[\w .:\\/()-]+", str(path)), f"Use a local disk and batch-safe path: {path}"
    for link, folder in ((profile / ".agents/skills", REPO / ".agents/llm-shared/skills"), (profile / ".claude/skills", REPO / ".claude/skills")):
        assert link.resolve(strict=True) == folder.resolve(strict=True), f"Point {link} to {folder} in the guest"
    return local / "resume-paused-acceptance", local / "tuitp/state.json"


def guest() -> tuple[Path, Path, str]:
    """Refuse before launcher access when running outside the dedicated human terminal."""
    assert os.name == "nt", "Requires Windows"
    ancestry = process_ancestry()
    assert ancestry, "Open a human Windows Terminal"
    assert classify_caller(os.environ, ancestry).origin is not CallerOrigin.AGENT, "Open a human Windows Terminal"
    assert not os.environ.get("TUIOS_PANE_ID"), "Use a separate human terminal outside TUIOS"
    facts = json.loads(run([str(executable(POWERSHELL)), "-NoProfile", "-NonInteractive", "-Command", FACTS]).stdout)
    lab, ledger = guest_paths(facts)
    for path in (lab, ledger, lab / "alpha", lab / "bravo", Path(os.environ["USERPROFILE"]) / ".llm-shared"):
        assert path.resolve() == path, f"Guest directories must be local and unredirected: {path}"
    return lab, ledger, facts["boot"]


def _sessions() -> dict[str, bool]:
    result = run([str(executable("tuios")), "ls", "--json"], check=False)
    json_rows: object = json.loads(result.stdout)
    assert isinstance(json_rows, list)
    rows = cast("list[object]", json_rows)
    assert result.returncode in {0, 1, 3}
    sessions: dict[str, bool] = {}
    for item in rows:
        assert isinstance(item, dict), "Invalid TUIOS session list"
        row = cast("dict[str, object]", item)
        name = row.get("name")
        assert isinstance(name, str), "Invalid TUIOS session name"
        sessions[name] = bool(row.get("saved"))
    assert len(sessions) == len(rows)
    assert (not result.returncode or all(sessions.values()))
    return sessions


def check_namespace(lab: Path, ledger: Path, *, fresh: bool, restoring: bool = False) -> None:
    """Reject foreign live or saved sessions and foreign tabs before tuitp can reconcile."""
    sessions = _sessions()
    if fresh:
        assert not sessions, "Open requires a fresh guest without a launcher ledger or live/saved sessions"
        assert not ledger.exists(), "Open requires a fresh guest without a launcher ledger or live/saved sessions"
        launcher = executable("tuitp.bat").parent
        assert not any((launcher / item).exists() for item in ("tuitp.legacy.json", "tuitp-legacy")), "Use a clean guest launcher installation"
        return
    expected = SESSIONS.keys()
    assert sessions.keys() <= expected, f"Foreign sessions: {sessions.keys() - expected}"
    if not restoring:
        assert sessions.keys() == expected, f"Missing sessions: {expected - sessions.keys()}"
        assert not any(sessions.values()), "Expected running sessions, found a saved session"
    _check_ledger(lab, ledger)


def _check_ledger(lab: Path, ledger: Path) -> None:
    state = json.loads(ledger.read_text(encoding="utf-8-sig"))
    assert state["version"] == 1, "Foreign or incomplete session ledger"
    assert state["sessions"].keys() == SESSIONS.keys(), "Foreign or incomplete session ledger"
    for name, (root, kind, label) in SESSIONS.items():
        entry = state["sessions"][name]
        assert (entry["name"], Path(entry["folder"]).resolve(), entry["kind"], entry["id"], entry["status"]) == (name, lab / root, kind, label, "ready")
    assert len(state["tabs"]) == 1, "Expected only the Acceptance tab"
    (tab,) = state["tabs"].values()
    spec = tab["spec"]
    assert "legacy" not in tab
    assert (spec["kind"], spec["window"], spec["title"], spec["sessions"]) == ("tuios", "resume-lab", "Acceptance", list(SESSIONS))
    assert (lab / "tuitp.list").read_text(encoding="utf-8") == LAYOUT


def layout(lab: Path) -> None:
    """Create two fresh Git checkouts and the alternate layout in the guest."""
    lab.mkdir()
    for name in ("alpha", "bravo"):
        root = lab / name
        root.mkdir()
        run(["git", "init", "-q", "-b", "main"], cwd=root)
        (root / "senv.bat").write_text(
            f'@echo off\ncall "%USERPROFILE%\\senv.bat" global\nif errorlevel 1 exit /b %errorlevel%\n'
            f'cd /d "%~dp0"\nset "PRJ_DIR={root}"\nset "LLM_SHARED_DIR={REPO}"\nset "PATH={REPO}\\bin;%PATH%"\nexit /b 0\n', encoding="utf-8",
        )
        if name == "bravo":
            (root / ".review-artifacts.ini").write_text("[review-artifacts]\nhome = .lab-reviews\n", encoding="utf-8")
        run(["git", "add", "."], cwd=root)
        run(["git", "-c", "user.name=Acceptance", "-c", "user.email=lab@example.invalid", "commit", "-qm", "Create guest fixture"], cwd=root)
    (lab / "tuitp.list").write_text(LAYOUT, encoding="utf-8")


# eof
