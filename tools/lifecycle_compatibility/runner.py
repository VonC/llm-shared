"""Run bounded real-xdist barrier probes outside the audited unit suite.

The caller supplies a fresh private evidence directory. Every project is
isolated from parent conftests, plugin autoload and inherited policy bindings.
The explicit --all mode also validates executable policy behaviors and actual
interpreter/dependency observations. Each runtime retains separate evidence.
Failed probes print their observations and bounded controller output before
the automatic preflight removes its temporary evidence directory.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import signal
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING

from tools.lifecycle_compatibility import scenarios

if TYPE_CHECKING:
    from collections.abc import Sequence

_TIMEOUT = 30
_WORKERS = 2
_USAGE_EXIT = 4


def alive(pid: int) -> bool:
    """Probe an observed worker without Windows os.kill(pid, 0) side effects."""
    if sys.platform == "win32":
        result = subprocess.run(  # noqa: S603 - fixed operating-system command
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],  # noqa: S607
            capture_output=True, text=True, check=True, timeout=5,
        )
        return any(len(row) > 1 and row[1] == str(pid) for row in csv.reader(result.stdout.splitlines()))
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def kill_tree(pid: int, *, group: bool = True) -> None:
    """Bound failure cleanup, including children of a hung controller."""
    if sys.platform == "win32":
        subprocess.run(  # noqa: S603 - fixed operating-system command
            ["taskkill", "/T", "/F", "/PID", str(pid)],  # noqa: S607
            capture_output=True, check=False, timeout=5,
        )
    else:
        try:
            if group:
                os.killpg(pid, signal.SIGKILL)
            else:
                os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def isolated_environment() -> dict[str, str]:
    """Remove inherited policy selection and expose only the standalone files."""
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith("LLM_SHARED_PYTEST_")
                   and key not in {"PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTHONPATH"}}
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "pytest_plugins")
    return environment


def run_smoke(evidence: Path, scenario: str = "invalid") -> dict[str, object]:
    """Retain actual announcement, no-start, exit and worker-cleanup evidence."""
    root = evidence / "project"
    if root.exists():
        message = "Compatibility evidence requires a fresh project directory"
        raise ValueError(message)
    scenarios.write_project(root, scenario)
    command = [sys.executable, "-m", "pytest", "-c", str(root / "pytest.ini"),
               "--rootdir", str(root), "--confcutdir", str(root),
               "-p", "xdist.plugin", "-p", "llm_shared_process_audit",
               "-n", "2", "--max-worker-restart=0", "-q", str(root)]
    child = subprocess.Popen(  # noqa: S603 - fixed executable and generated project
        command, cwd=root, env=isolated_environment(), stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, start_new_session=sys.platform != "win32",
    )
    timed_out = False
    try:
        output, _ = child.communicate(timeout=_TIMEOUT)
    except subprocess.TimeoutExpired:
        timed_out = True
        kill_tree(child.pid)
        output, _ = child.communicate(timeout=5)
    (evidence / "controller.log").write_text(output, encoding="utf-8")
    pids = [int(path.read_text(encoding="utf-8")) for path in root.glob("worker.*.pid")]
    remaining = [pid for pid in pids if alive(pid)]
    for pid in remaining:
        kill_tree(pid, group=False)
    result: dict[str, object] = {
        "scenario": scenario, "returncode": child.returncode, "timed_out": timed_out,
        "valid_peer_announced": (root / "announced").exists(),
        "test_started": (root / "started").exists(), "worker_pids": pids,
        "workers_reaped": not remaining and len(pids) == _WORKERS,
        "diagnostic": scenarios.DIAGNOSTICS[scenario] in output,
    }
    result["passed"] = all((not timed_out, child.returncode == _USAGE_EXIT,
                            result["valid_peer_announced"], not result["test_started"],
                            result["workers_reaped"], result["diagnostic"]))
    (evidence / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def _all_cases(evidence: Path) -> list[dict[str, object]]:
    """Verify the runtime before barriers and policy behavior contracts."""
    from tools.lifecycle_compatibility import (  # noqa: PLC0415 - avoid circular runner transport import
        behavior_runner,
        behavior_scenarios,
        environment,
    )

    environment.verify(Path(__file__).resolve().parents[2], Path(sys.executable), sys.version_info[:2])
    results = [run_smoke(evidence / name, name) for name in scenarios.NAMES]
    results.extend(behavior_runner.run_case(evidence / case.name, case) for case in behavior_scenarios.cases())
    return results


def _report(evidence: Path, results: list[dict[str, object]]) -> None:
    """Expose bounded failure diagnostics before temporary logs are removed."""
    for result in results:
        sys.stdout.write(f'Compatibility {result.get("scenario", "probe")}: {"passed" if result["passed"] else "FAILED"}\n')
        if not result["passed"]:
            sys.stdout.write(json.dumps(result, sort_keys=True) + "\n")
            log = evidence / str(result.get("scenario", "probe")) / "controller.log"
            if log.is_file():
                sys.stdout.write("\n".join(log.read_text(encoding="utf-8").splitlines()[-40:]) + "\n")
        sys.stdout.flush()


def main(argv: Sequence[str] | None = None) -> int:
    """Record actual environment versions and fail if any barrier probe fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--all", action="store_true", help="Run all standalone policy compatibility contracts")
    arguments = parser.parse_args(argv)
    evidence = Path(arguments.evidence).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    results = _all_cases(evidence) if arguments.all else [run_smoke(evidence / name, name) for name in scenarios.NAMES]
    summary = {"python": sys.version, "pytest": version("pytest"),
               "xdist": version("pytest-xdist"), "scenarios": results}
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _report(evidence, results)
    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())


# eof
