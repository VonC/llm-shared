"""Bounded real-process scenarios with setup charged to each requesting test.

Link the immutable prepared interpreter redirector and copy its configuration into a
disposable checkout. No machine setup, downloads, or external switchpy runs.
Each scenario retains its real launch without charging the first test for an
entire matrix. Record-consuming cases seed the prior record as fixture data;
the successful producer case starts without a record and proves publication.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from tests.unit.tools.release_workflow.test_support import metadata

_REPOSITORY = Path(__file__).resolve().parents[3]
_DRIVER = """import json, pathlib, runpy, sys
root = pathlib.Path(sys.argv[1])
assert "tools" not in sys.modules
namespace = runpy.run_path(str(root / "tools/release_workflow/bootstrap.py"))
status = namespace["main"](["probe"])
print(json.dumps({"status": status, "tools": "tools" in sys.modules,
                  "isolated": sys.flags.isolated, "utf8": sys.flags.utf8_mode,
                  "bytecode": sys.dont_write_bytecode}))
"""


def run(arguments: list[str], root: Path, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Run a fixture-owned executable with bounded capture and no shell."""
    return subprocess.run(  # noqa: S603 - fixture builds every executable and argument
        arguments, cwd=root, env=environment, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False, timeout=30,
    )


def _prepare_checkout(root: Path) -> None:
    """Build a disposable checkout with one prepared interpreter and CLI probe."""
    helper_dir = root / "tools/release_workflow"
    helper_dir.mkdir(parents=True)
    for name in ("bootstrap", "runtime_identity", "readiness", "markers", "__init__"):
        shutil.copyfile(_REPOSITORY / f"tools/release_workflow/{name}.py", helper_dir / f"{name}.py")
    (root / "tools/__init__.py").write_text("", encoding="utf-8")
    cli = helper_dir / "cli.py"
    cli.write_text("def main(argv):\n    assert argv == ['probe']\n    return 0\n", encoding="utf-8")
    prefix = root / "venvs/prepared"
    executable = prefix / "Scripts/python.exe"
    executable.parent.mkdir(parents=True)
    try:
        executable.hardlink_to(sys.executable)
    except OSError:
        # A different temporary volume may not support linking the redirector.
        shutil.copyfile(sys.executable, executable)
    (prefix / "pyvenv.cfg").write_text(
        f"home = {sys.base_prefix}\ninclude-system-site-packages = false\n", encoding="utf-8",
    )
    metadata(root)
    entry = root / "record.bat"
    shutil.copyfile(_REPOSITORY / "bin/release_runtime_record.bat", entry)
    driver = root / "driver.py"
    driver.write_text(_DRIVER, encoding="utf-8")


def _setup_cleanup(home: Path, command: str, scenario: str) -> subprocess.CompletedProcess[str]:
    """Execute the real senv preparation block with bounded batch collaborators."""
    root = home / "setup-cleanup"
    (root / "bin").mkdir(parents=True)
    (root / "tools/batcolors").mkdir(parents=True)
    (root / "switchpy.bat").write_text("@exit /b %FAKE_SETUP_STATUS%\n", encoding="ascii")
    (root / "tools/batcolors/echos_macros.bat").write_text("@exit /b 0\n", encoding="ascii")
    (root / "bin/release_runtime_record.bat").write_text(
        '@if not "%~2"=="0" exit /b %~2\n@exit /b %FAKE_PRODUCER_STATUS%\n', encoding="ascii",
    )
    source = (_REPOSITORY / "senv.bat").read_text(encoding="utf-8")
    start = source.index('pushd "%PRJ_DIR%"\ncall switchpy')
    stop = source.index("REM Install composable hooks", start)
    (root / "section.bat").write_text(
        "@echo off\n" + source[start:stop] + "echo SETUP_CONTINUED\nexit /b 0\n", encoding="ascii",
    )
    driver = root / "driver.bat"
    driver.write_text(
        '@echo off\ncall .\\section.bat\nset "OBSERVED=%ERRORLEVEL%"\n'
        'if defined RELEASE_SETUP_STATUS exit /b 99\n'
        'if defined RELEASE_RUNTIME_STATUS exit /b 98\n'
        'echo STATUS_CLEAN\nexit /b %OBSERVED%\n', encoding="ascii",
    )
    setup, producer = {"clean_success": ("0", "0"), "clean_setup_failure": ("7", "0"),
                       "clean_producer_failure": ("0", "2")}[scenario]
    environment = {**os.environ, "PRJ_DIR": str(root), "_ok": "rem", "PYTHON_VERSION": "fixture",
                   "FAKE_SETUP_STATUS": setup, "FAKE_PRODUCER_STATUS": producer,
                   "PATH": str(root) + os.pathsep + os.environ["PATH"]}
    return run([command, "/d", "/c", str(driver)], root, environment)


def _break_readiness(root: Path, scenario: str, environment: dict[str, str], command: str) -> None:
    """Prepare one failure while retaining a real junction for physical escape."""
    record = root / "venvs/release-runtime.v1.txt"
    if scenario == "missing_engine":
        (root / "tools/release_workflow/cli.py").unlink()
    elif scenario == "escaped_record":
        outside = root.parent / "outside"
        (outside / "Scripts").mkdir(parents=True)
        (outside / "Scripts/python.exe").write_bytes(b"not an interpreter")
        junction = root / "venvs/escaped"
        linked = run([command, "/d", "/c", "mklink", "/J", str(junction), str(outside)], root.parent, environment)
        assert linked.returncode == 0, linked.stdout + linked.stderr
        record.write_text("1\nvenvs/escaped\n", encoding="utf-8")
    elif scenario == "missing_record":
        record.unlink()


def process_scenario(home: Path, scenario: str) -> dict[str, object]:
    """Run one real scenario, including its own complete fixture cost."""
    command = str(Path(os.environ["SYSTEMROOT"]) / "System32/cmd.exe")
    if scenario.startswith("clean_"):
        return {scenario: _setup_cleanup(home, command, scenario)}
    root = home / "tooling space"
    _prepare_checkout(root)
    consumer = home / "consumer"
    consumer.mkdir()
    (consumer / "keep.txt").write_text("consumer content", encoding="utf-8")
    (consumer / "tools.py").write_text("raise AssertionError('ambient import')\n", encoding="utf-8")
    before_consumer = {path.name: path.read_bytes() for path in consumer.iterdir()}
    prefix = root / "venvs/prepared"
    executable = prefix / "Scripts/python.exe"
    entry = root / "record.bat"
    driver = root / "driver.py"
    environment = {**os.environ, "VIRTUAL_ENV": str(prefix), "PYTHONPATH": str(consumer)}
    producer = [command, "/d", "/c", "call", str(entry), str(root)]
    result: dict[str, object] = {}
    record = root / "venvs/release-runtime.v1.txt"
    before = b"1\nvenvs/prepared\n"
    if scenario != "success":
        record.write_bytes(before)
    if scenario in {"success", "failed_setup", "no_environment", "missing_python", "foreign_python"}:
        environment["VIRTUAL_ENV"] = {"no_environment": "", "missing_python": str(home / "absent"),
                                      "foreign_python": sys.prefix}.get(scenario, str(prefix))
        status = "7" if scenario == "failed_setup" else "0"
        result[scenario] = run([*producer, status], consumer, environment)
        result["record"] = record.read_text(encoding="utf-8")
        result["preserved"] = record.read_bytes() == before
        result["nonlocal_preserved"] = record.read_bytes() == before
        return result
    isolated = [str(executable), "-I", "-X", "utf8", str(driver), str(root)]
    _break_readiness(root, scenario, environment, command)
    result[scenario] = run(isolated, consumer, environment)
    result["cache_files"] = list(root.rglob("*.pyc"))
    result["consumer_unchanged"] = before_consumer == {path.name: path.read_bytes() for path in consumer.iterdir()}
    return result


def import_closure(root: Path) -> subprocess.CompletedProcess[str]:
    """Prove the actual eager tools closure imports with all site packages off."""
    driver = root / "closure.py"
    driver.write_text(
        "import importlib, json, sys\n"
        f"sys.path.insert(0, {str(_REPOSITORY)!r})\n"
        "importlib.import_module('tools.release_workflow')\n"
        "print(json.dumps([name for name in sys.modules if name.startswith('tools')]))\n",
        encoding="utf-8",
    )
    return run([sys.executable, "-I", "-S", "-B", "-X", "utf8", str(driver)], root, dict(os.environ))

def empty_uv_lock(home: Path, *, dev_edges: bool) -> Path:
    """Generate one real offline lock, charging its process to its own test."""
    local = home / "local-only"
    local.mkdir()
    (local / "pyproject.toml").write_text(
        '[project]\nname="local-only"\nversion="1.0"\n[tool.uv]\npackage=false\n', encoding="utf-8",
    )
    root = home / "project"
    uv = str(Path(sys.prefix) / "Scripts/uv.exe")
    root.mkdir()
    metadata(root)
    (root / "uv.lock").unlink()
    if dev_edges:
        project = root / "pyproject.toml"
        project.write_text(
            project.read_text(encoding="utf-8").replace(
                'dev = [{include-group = "release"}]',
                'dev = [{include-group = "release"}, "local-only"]',
            ) + '\n[tool.uv.sources]\nlocal-only = {path="../local-only"}\n', encoding="utf-8",
        )
    result = run([uv, "lock", "--offline", "--no-config"], root, dict(os.environ))
    assert result.returncode == 0, result.stdout + result.stderr
    lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    package = next(value for value in lock["package"] if value["source"] == {"virtual": "."})
    assert ("dev-dependencies" in package) == dev_edges
    return root

# eof
