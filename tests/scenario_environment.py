"""Restore complete CLI environments while writing only changed variables."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping


@contextmanager
def environment(values: Mapping[str, str]) -> Generator[None]:
    """Retain patch.dict restoration semantics without rewriting every OS key."""
    original = dict(os.environ)
    try:
        for key, value in values.items():
            if os.environ.get(key) != value:
                os.environ[key] = value
        yield
    finally:
        for key in os.environ.keys() - original.keys():
            del os.environ[key]
        for key, value in original.items():
            if os.environ.get(key) != value:
                os.environ[key] = value


# eof
