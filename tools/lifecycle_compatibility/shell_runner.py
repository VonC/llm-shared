"""Run eleven real Windows caller contracts outside the audited unit suite.

Each probe owns private fresh evidence. Process transport is bounded and
replaceable in tests; concurrent transfer files are read only after close.
Non-Windows hosts explicitly report that these contracts were not run.
"""

from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

from tools.lifecycle_compatibility import runner, scenarios, shell_scenarios
from tools.pytest_plugin_shell import publish_result

_TIMEOUT = 30
_TRANSFERS = 4


def oem_code_page() -> int:
    """Observe the real caller's OEM encoding only on the Windows path."""
    return int(ctypes.windll.kernel32.GetOEMCP())


def caller_environment(evidence: Path, extra: dict[str, str]) -> dict[str, str]:
    """Clear inherited activation and select this matrix runtime on PATH."""
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith("LLM_SHARED_PYTEST_")
                   and key not in {"PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTHONPATH", "PROBE_EXIT"}}
    environment.update(PYTHONDONTWRITEBYTECODE="1", PROBE_DUMPER=str(evidence / "dump.py"),
                       PROBE_LAUNCHER=str(Path(__file__).resolve().parents[2] / "bin/prepare_pytest_plugins.bat"))
    environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
    environment.update(extra)
    return environment


def run_case(evidence: Path, case: shell_scenarios.ShellCase) -> dict[str, object]:
    """Observe actual exit and owned values, killing a timed-out caller tree."""
    home = evidence / case.name
    home.mkdir()
    environment = caller_environment(evidence, case.extra)
    environment["PROBE_OUTPUT"] = str(home / "snapshot")
    child = subprocess.Popen(  # noqa: S603 - fixed cmd and generated private caller
        ["cmd", "/d", "/v:" + case.delayed, "/c", str(evidence / "caller.bat")],  # noqa: S607
        cwd=case.cwd, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    timed_out = False
    try:
        output, _ = child.communicate(timeout=_TIMEOUT)
    except subprocess.TimeoutExpired:
        timed_out = True
        runner.kill_tree(child.pid)
        output, _ = child.communicate(timeout=5)
    (home / "controller.log").write_bytes(output)
    result: dict[str, object] = {"scenario": case.name, "returncode": child.returncode, "timed_out": timed_out,
                                 "passed": False, "log": str(home / "controller.log")}
    try:
        before = shell_scenarios.read_snapshot(home / "snapshot.before.json")
        after = shell_scenarios.read_snapshot(home / "snapshot.after.json")
        result["passed"] = not timed_out and shell_scenarios.verdict(case, child.returncode, before, after)
    except (OSError, ValueError) as error:
        result["diagnostic"] = str(error)
    (home / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def transfer_case(evidence: Path, code_page: int) -> dict[str, object]:
    """Publish concurrently, require four distinct complete files and clean ours."""
    def publish(_index: int) -> Path:
        return publish_result({"LLM_SHARED_PYTEST_PLUGINS": "process"}, delayed_expansion=False,
                              code_page=code_page, directory=evidence)
    with ThreadPoolExecutor(max_workers=_TRANSFERS) as pool:
        files = list(pool.map(publish, range(_TRANSFERS)))
    try:
        complete = all(path.read_text(encoding=f"cp{code_page}").startswith("LLM_SHARED_PYTEST_PLUGINS=process\n") for path in files)
        return {"scenario": "concurrent-exclusive-transfer", "count": len(files),
                "passed": len(set(files)) == _TRANSFERS and complete}
    finally:
        for path in files:
            path.unlink(missing_ok=True)


def run_all(evidence: Path) -> list[dict[str, object]]:
    """Retain shell cases in --all, with an explicit platform-specific absence."""
    if sys.platform != "win32":
        return [{"scenario": "windows-shell", "passed": None, "status": "not run", "reason": "requires Windows cmd.exe"}]
    evidence.mkdir(parents=True)
    code_page = oem_code_page()
    (evidence / "dump.py").write_text(shell_scenarios.DUMPER, encoding="utf-8")
    (evidence / "caller.bat").write_text(f"@echo off\nchcp {code_page} >nul\n" + scenarios.windows_caller(), encoding="ascii")
    project = evidence / "projet é % ! ^ & spaces"
    project.mkdir()
    cases = shell_scenarios.cases(project, Path(evidence.anchor))
    results = [run_case(evidence, case) for case in cases[:8]]
    results.append(transfer_case(evidence, code_page))
    with ThreadPoolExecutor(max_workers=2) as pool:
        results.extend(pool.map(partial(run_case, evidence), cases[8:]))
    return results


# eof
