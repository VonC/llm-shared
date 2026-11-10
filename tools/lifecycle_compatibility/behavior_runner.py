"""Run real-policy cases with bounded cleanup and optional packages absent.

The dependency-free variant uses -S and a temporary directory containing only
pytest's mandatory packages. Neither xdist nor pytest-cov is on that child's
import path; this is actual import isolation rather than a fake module.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from tools.lifecycle_compatibility import behavior_scenarios, runner


def mandatory_packages(destination: Path) -> None:
    """Copy only pytest's mandatory import packages for a site-free child."""
    destination.mkdir()
    for name in ("pytest", "_pytest", "py", "pluggy", "packaging", "iniconfig", "pygments", "colorama"):
        spec = importlib.util.find_spec(name)
        if spec is None or spec.origin is None:
            message = f"Mandatory pytest package unavailable: {name}"
            raise ValueError(message)
        origin = Path(spec.origin)
        if origin.name == "__init__.py":
            shutil.copytree(origin.parent, destination / name, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copyfile(origin, destination / origin.name)


def run_case(evidence: Path, case: behavior_scenarios.Case) -> dict[str, object]:
    """Interpret real exit/diagnostic/summary observations from a fresh project."""
    root = evidence / "project"
    root.mkdir(parents=True)
    (root / "pytest.ini").write_text("[pytest]\nmarkers =\n    process_allowed(reason): permission\n" + case.ini, encoding="utf-8")
    (root / "test_behavior.py").write_text(case.source, encoding="utf-8")
    (root / "conftest.py").write_text(case.conftest, encoding="utf-8")
    environment = runner.isolated_environment()
    if case.prepared:
        environment.update(LLM_SHARED_PYTEST_PLUGINS=case.prepared, LLM_SHARED_PYTEST_ROOT=str(root),
                           LLM_SHARED_PYTEST_POLICY_DIR=environment["PYTHONPATH"])
    command = [sys.executable]
    if case.optional_absent:
        vendor = evidence / "mandatory"
        mandatory_packages(vendor)
        environment["PYTHONPATH"] += os.pathsep + str(vendor)
        command.append("-S")
        source = (root / "test_behavior.py").read_text(encoding="utf-8")
        (root / "test_behavior.py").write_text(source + """
def test_optional_dependencies_absent():
    import importlib.util
    assert importlib.util.find_spec("xdist") is None
    assert importlib.util.find_spec("pytest_cov") is None
""", encoding="utf-8")
    command.extend(["-m", "pytest", "-c", str(root / "pytest.ini"), "--rootdir", str(root),
                    "--confcutdir", str(root), "-q", *case.options])
    for plugin in case.plugins:
        command.extend(["-p", plugin])
    command.append(str(root))
    child = subprocess.Popen(  # noqa: S603 - fixed interpreter and generated isolated project
        command, cwd=root, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, start_new_session=sys.platform != "win32",
    )
    timed_out = False
    try:
        output, _ = child.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        timed_out = True
        runner.kill_tree(child.pid)
        output, _ = child.communicate(timeout=5)
    (evidence / "controller.log").write_text(output, encoding="utf-8")
    passed = (not timed_out and child.returncode == case.code
              and all(text in output for text in case.contains)
              and all(output.count(text) == count for text, count in case.summaries))
    result: dict[str, object] = {"scenario": case.name, "returncode": child.returncode, "timed_out": timed_out, "passed": passed}
    (evidence / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


# eof
