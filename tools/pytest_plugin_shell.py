"""Transfer one complete environment result to a prepared Windows caller.

FOR substitution reads data after cmd's command/percent parsing. When the
caller enables delayed expansion, escape its subsequent caret/exclamation
scan. Selection and cache computation remain owned by the shared builder.
Exclusive transfer files use the caller's console code page and are disclosed
only after a complete write; unrepresentable values fail before application.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.pytest_plugin_environment import (
    POLICY_DIR,
    ROOT,
    SELECTION,
    PreparationError,
    prepare_environment,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

OWNED_KEYS = (SELECTION, ROOT, POLICY_DIR, "PYTHONPATH", "PYTEST_ADDOPTS")
_MAX_RECORD = 8000


def serialize_result(environment: Mapping[str, str], *, delayed_expansion: bool) -> str:
    """Serialize all owned keys as data; empty assignments explicitly remove keys.

    Values enter ``set "%%V"`` through FOR substitution, so percent signs,
    quotes and command metacharacters are never reparsed as command text.
    Cmd skips the delayed scan for tokens without an exclamation mark.
    """
    lines: list[str] = []
    for key in OWNED_KEYS:
        value = environment.get(key, "")
        if any(char in value for char in "\r\n\0"):
            message = f"Windows transport cannot represent a multiline/NUL value for {key}"
            raise PreparationError(message)
        if delayed_expansion and "!" in value:
            value = value.replace("^", "^^").replace("!", "^!")
        line = f"{key}={value}"
        if len(line) > _MAX_RECORD:
            message = f"Windows transport record exceeds cmd's line limit for {key}"
            raise PreparationError(message)
        lines.append(line)
    return "\n".join(lines) + "\n"


def publish_result(environment: Mapping[str, str], *, delayed_expansion: bool, code_page: int, directory: Path | None = None) -> Path:
    """Return an exclusive, complete transfer file in the caller's code page.

    The caller learns the unique filename only after its contents are closed.
    Encoding failures happen before file creation; IO failures remove only the
    file owned by this invocation, never another preparation's result.
    """
    content = serialize_result(environment, delayed_expansion=delayed_expansion)
    try:
        encoded = content.encode(f"cp{code_page}")
    except (UnicodeError, LookupError) as error:
        message = f"Windows transport cannot represent the complete result in code page {code_page}: {error}"
        raise PreparationError(message) from error
    descriptor, name = tempfile.mkstemp(prefix="llm-shared-pytest-", suffix=".env", dir=directory)
    output = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
        # The filename also crosses FOR /F, so it must be representable.
        str(output).encode(f"cp{code_page}")
    except (OSError, UnicodeError):
        output.unlink(missing_ok=True)
        raise
    return output


def main(argv: Sequence[str] | None = None) -> int:
    """Compute using the one shared builder; leave no applicable result on error."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--shared-root", type=Path, required=True)
    parser.add_argument("--code-page", type=int, required=True)
    parser.add_argument("--delayed-expansion", choices=("on", "off"), required=True)
    args = parser.parse_args(argv)
    output: Path | None = None
    try:
        environment = prepare_environment(args.project_root, args.shared_root, os.environ)
        output = publish_result(environment, delayed_expansion=args.delayed_expansion == "on", code_page=args.code_page)
        sys.stdout.buffer.write((str(output) + "\n").encode(f"cp{args.code_page}"))
        sys.stdout.buffer.flush()
    except (PreparationError, OSError, UnicodeError) as error:
        if output is not None:
            output.unlink(missing_ok=True)
        sys.stderr.write(f"pytest preparation failed: {error}\n")
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())


# eof
