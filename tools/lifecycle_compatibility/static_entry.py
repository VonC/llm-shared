"""Check whole-file Python 3.10 syntax and the exact inert refusal prefix.

Ruff supplies target-aware grammar validation, including a PEP 701 negative
control that ast.parse(feature_version=...) alone misses on Python 3.13.
The AST check independently constrains all execution before version refusal.
An empty standalone policy set fails validation instead of silently passing.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

_PREFIX = """import sys
import pytest
if sys.version_info < (3, 12):
    raise pytest.UsageError({message!r})
"""
_PEP701 = 'value = f"{dict(x=1)["x"]}"\n'


def check_structure(source: str, name: str) -> None:
    """Allow only sys/pytest imports and an identifying version-refusal guard."""
    body = ast.parse(source).body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    expected = ast.parse(_PREFIX.format(message=f"{name} requires Python 3.12 or later")).body
    if [ast.dump(node) for node in body[:3]] != [ast.dump(node) for node in expected]:
        message = f"{name}: unsafe pre-refusal structure"
        raise ValueError(message)


def syntax(source: str, filename: str) -> subprocess.CompletedProcess[str]:
    """Run only Ruff's grammar checks with an explicit Python 3.10 target."""
    return subprocess.run(  # noqa: S603 - fixed syntax-check tool and input, no shell
        ["ruff", "check", "--isolated", "--target-version", "py310", "--select", "E9",  # noqa: S607
         "--stdin-filename", filename, "-"], input=source, capture_output=True,
        text=True, timeout=30, check=False,
    )


def _check_files() -> None:
    """Check the negative control and every shipped standalone entry file."""
    control = syntax(_PEP701, "pep701_negative_control.py")
    if control.returncode != 1 or "Python 3.12" not in control.stdout:
        message = "Python 3.10 syntax checker failed to reject the PEP 701 negative control"
        raise ValueError(message)
    directory = Path(__file__).resolve().parents[1] / "pytest_plugins"
    paths = tuple(directory.glob("llm_shared_*.py"))
    if not paths:
        message = "No standalone policy files found for static compatibility validation"
        raise ValueError(message)
    for path in paths:
        source = path.read_text(encoding="utf-8")
        check_structure(source, path.stem)
        result = syntax(source, str(path))
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)


def main() -> int:
    """Run static checks and their grammar regression without policy execution."""
    try:
        _check_files()
    except (OSError, ValueError, SyntaxError, subprocess.SubprocessError) as error:
        sys.stderr.write(f"Static compatibility failed: {error}\n")
        return 1
    sys.stdout.write("Python 3.10 syntax/refusal boundary and PEP 701 negative control passed\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
