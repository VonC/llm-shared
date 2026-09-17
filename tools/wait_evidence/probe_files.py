"""Exclusive durable JSON artifacts shared by the synthetic probe drivers."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from pathlib import Path

    from .models import JsonValue


def save(path: Path, data: JsonValue) -> None:
    """Publish a durable exclusive JSON artifact; previous evidence is immutable."""
    temporary = path.with_name(path.name + "." + uuid4().hex + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


# eof
