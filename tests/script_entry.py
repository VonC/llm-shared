"""Exercise real script guards without reloading an application's definitions."""

from __future__ import annotations

import ast
import importlib
import sys
from functools import cache
from pathlib import Path
from types import CodeType, ModuleType


@cache
def _guard(path: str) -> CodeType:
    """Compile the actual guard with its original filename and line numbers."""
    source = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=path)
    guards: list[ast.stmt] = [node for node in tree.body if isinstance(node, ast.If)
              and ast.unparse(node.test) == "__name__ == '__main__'"]
    if not guards:
        message = f"Expected script guards in {path}"
        raise ValueError(message)
    return compile(ast.Module(body=guards, type_ignores=[]), path, "exec")


def run_main(source: str | Path | ModuleType) -> None:
    """Run the real guard against the existing module's functions and globals."""
    if isinstance(source, ModuleType):
        module = source
    elif str(source).endswith(".py"):
        path = Path(source).resolve()
        root = Path(__file__).resolve().parents[1]
        module = importlib.import_module(".".join(path.relative_to(root).with_suffix("").parts))
    else:
        module = importlib.import_module(str(source))
    assert module.__file__ is not None
    namespace = dict(vars(module), __name__="__main__")
    original_path = sys.path[:]
    try:
        exec(_guard(module.__file__), namespace)  # noqa: S102 - exact checked-in guard, no generated source
    finally:
        sys.path[:] = original_path


# eof
