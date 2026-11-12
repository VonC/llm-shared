"""Verify checkout-local Python 3.12 prerequisites before executable validation.

Provisioning belongs to the explicit launcher --setup branch. This module
never installs or imports the main project's dependencies. Both default and
absolute override executables must match this checkout's pinned manifest.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, cast

from tools.lifecycle_compatibility import runner

if TYPE_CHECKING:
    from collections.abc import Sequence

OVERRIDE = "LLM_SHARED_LIFECYCLE_PYTHON"
_DEFAULT = "python_3.12_lifecycle_compatibility"
_PROBE = """import json, sys
from importlib.metadata import version, PackageNotFoundError
dependencies = {}
for name in sys.argv[1:]:
    try:
        dependencies[name] = version(name)
    except PackageNotFoundError:
        dependencies[name] = None
print(json.dumps(dict(python=list(sys.version_info[:2]), dependencies=dependencies)))
"""


def interpreter(root: Path, override: str | None) -> Path:
    """Resolve an explicit absolute override or the target checkout's default."""
    if override is not None:
        selected = Path(override)
        if not selected.is_absolute():
            message = f"{OVERRIDE} must name an absolute interpreter path"
            raise ValueError(message)
        return selected
    return root / "venvs" / _DEFAULT / "Scripts" / "python.exe"


def requirements(root: Path) -> dict[str, str]:
    """Read exact pins rather than importing a shared project dependency graph."""
    path = root / "tools" / "lifecycle_compatibility" / "requirements-py312.txt"
    pins: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_-]+)==([A-Za-z0-9.]+)", line)
        if match is None or match[1] in pins:
            message = f"Invalid independent compatibility pin: {line!r}"
            raise ValueError(message)
        pins[match[1]] = match[2]
    if not {"pytest", "pytest-xdist"} <= pins.keys():
        message = f"Missing mandatory compatibility dependencies in {path}"
        raise ValueError(message)
    return pins


def _probe(root: Path, executable: Path, expected: tuple[int, int]) -> dict[str, object]:
    """Compare actual executable observations with this checkout's exact pins."""
    if expected not in ((3, 12), (3, 13)):
        message = "executable compatibility requires Python 3.12 or 3.13"
        raise ValueError(message)
    if not executable.is_absolute() or not executable.is_file():
        raise FileNotFoundError(str(executable))
    pins = requirements(root)
    result = subprocess.run(  # noqa: S603 - explicit absolute interpreter and fixed probe
        [str(executable), "-I", "-c", _PROBE, *pins], capture_output=True,
        text=True, timeout=10, check=True,
    )
    observed: object = json.loads(result.stdout)
    if observed != {"python": list(expected), "dependencies": pins}:
        message = f"unsuitable executable or dependency set: {result.stdout.strip()}"
        raise ValueError(message)
    return cast("dict[str, object]", observed)


def verify(root: Path, executable: Path, expected: tuple[int, int] = (3, 12)) -> dict[str, object]:
    """Probe real prerequisites and attach explicit setup help to failures."""
    try:
        return _probe(root, executable, expected)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        message = (f'lifecycle compatibility prerequisites: {error}. Run '
                   f'{root / "bin" / "lifecycle_compatibility.bat"} --setup '
                   f'or set {OVERRIDE} to an absolute prepared Python 3.12 executable')
        raise ValueError(message) from error


def _validate(root: Path, evidence: Path | None) -> int:
    """Require the selected executable and clean automatic scenario roots."""
    selected = interpreter(root, os.environ.get(OVERRIDE))
    versions = verify(root, selected)
    if selected.resolve() != Path(sys.executable).resolve():
        message = "launcher did not execute the selected compatibility interpreter"
        raise ValueError(message)
    sys.stdout.write(f"Compatibility interpreter: {selected}; verified {versions}\n")
    sys.stdout.flush()
    if evidence is not None:
        return runner.main([str(evidence), "--all"])
    with tempfile.TemporaryDirectory(prefix="lifecycle-compatibility-") as temporary:
        return runner.main([temporary, "--all"])


def main(argv: Sequence[str] | None = None) -> int:
    """Verify this interpreter and run fresh projects, cleaning temporary roots."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path)
    arguments = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    try:
        return _validate(root, arguments.evidence)
    except (OSError, ValueError) as error:
        sys.stderr.write(f"Compatibility setup failed: {error}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


# eof
