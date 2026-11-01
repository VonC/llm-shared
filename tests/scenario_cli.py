"""Reuse immutable CLI grammar while retaining fresh parse and runtime state.

Construction remains lazy inside the first invoking test's measured lifecycle.
Each parse creates a new Namespace; production dispatch and command state are
never cached. Direct parser-construction tests retain the original factory.
Stable review-input caching also supports scoped journey builders; each cache
starts empty inside the measured fixture and is restored on leaving it.
Shipped template text is immutable like the grammars: its first read per path
stays in the first rendering test, later renders reuse it, and missing paths
still raise because failures are never cached.
"""

from __future__ import annotations

import argparse
import logging
import os
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools import (
    code_review_request,
    prompt_workflow_parser,
    review_exchange_cli,
    review_exchange_cli_parser,
    spec_review_answer_cli,
    spec_review_request,
    template_text,
)
from tools.groundhog import cli as groundhog_cli
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import ReviewConfiguration

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


def _english(message: str) -> str:
    """Use the declared scenario locale without native catalog discovery."""
    return message


def _english_plural(singular: str, plural: str, count: int) -> str:
    """Retain argparse's English singular/plural diagnostics."""
    return singular if count == 1 else plural


@pytest.fixture(scope="session", autouse=True)
def scenario_command_grammar() -> Iterator[None]:
    """Install a lazy grammar cache, counting construction in the calling test."""
    clear_caches: list[Callable[[], None]] = []
    with pytest.MonkeyPatch.context() as patch:
        # Scenario diagnostics have a declared English locale. Argparse's
        # default gettext lookup probes native locale catalogs per argument.
        patch.setattr(argparse, "_", _english)
        patch.setattr(argparse, "ngettext", _english_plural)
        # Use argparse's supported terminal dimensions instead of probing the
        # native console for every formatter during cold parser construction.
        patch.setenv("COLUMNS", "80")
        patch.setenv("LINES", "24")
        for module, name in ((review_exchange_cli, "_parser"),
                             (review_exchange_cli, "_parser_for"),
                             (review_exchange_cli_parser, "_common_arguments"),
                             (code_review_request, "_parser"),
                             (spec_review_answer_cli, "_parser"),
                             (spec_review_request, "_parser"),
                             (groundhog_cli, "_build_arg_parser"),
                             (prompt_workflow_parser, "build_arg_parser"),
                             (template_text, "read_template")):
            factory = cache(getattr(module, name))
            clear_caches.append(factory.cache_clear)
            patch.setattr(module, name, factory)
        yield
    for clear in clear_caches:
        clear()


@pytest.fixture(autouse=True)
def scenario_logging() -> Iterator[None]:
    """Restore CLI logging before pytest closes the current capture streams."""
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    try:
        yield
    finally:
        for handler in root.handlers:
            if handler not in handlers:
                handler.close()
        root.handlers[:] = handlers
        root.setLevel(level)


@pytest.fixture
def stable_review_inputs(monkeypatch: pytest.MonkeyPatch) -> Callable[[], None]:
    """Install lazy stable observations for one function-scoped scenario."""
    return cache_review_inputs(monkeypatch)


def cache_review_inputs(monkeypatch: pytest.MonkeyPatch) -> Callable[[], None]:
    """Reuse immutable observations only in journeys with fixed configuration.

    These opt-in scenarios never change symlinks or the artifact declaration.
    Their first observation still executes production code inside the measured
    lifecycle. The returned callback freezes review-mode configuration only
    after activation; protocol records and CLI runtime state remain live.
    """
    original_resolve = Path.resolve

    @cache
    def resolved(path: str) -> Path:
        # pathlib 3.13 repeatedly normalizes and hashes Path keys. These
        # scenarios already have stable absolute spelling; key by that text
        # and construct a Path only on the first real observation.
        return original_resolve(Path(path))

    def resolve(path: Path, strict: bool = False) -> Path:  # noqa: FBT001, FBT002
        # Relative paths are caller-dependent, and strict existence is mutable.
        if strict:
            return original_resolve(path, strict=True)
        spelling = str(path)
        # Inspect the existing string without reparsing a pathlib object.
        return resolved(spelling if os.path.isabs(spelling) else str(Path.cwd() / path))  # noqa: PTH117

    # Path already memoizes its parsed components. Wrapping the cheap lexical
    # predicates in functools.cache adds normalized Path hashing on every call
    # and retains duplicate path objects for no filesystem work saved.
    monkeypatch.setattr(Path, "resolve", resolve)
    monkeypatch.setattr(ReviewArtifactConfiguration, "load", cache(ReviewArtifactConfiguration.load))

    def freeze_review_mode() -> None:
        """Begin lazy configuration reuse after all activation mutations."""
        monkeypatch.setattr(ReviewConfiguration, "load", cache(ReviewConfiguration.load))

    return freeze_review_mode


# eof
