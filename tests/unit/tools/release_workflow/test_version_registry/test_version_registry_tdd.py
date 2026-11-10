"""The explicit adapter tuple lists every adapter module exactly once.

Step 2 of v0.14.0 version-sources: the modules of `tools.release_workflow.sources`,
minus the declared support modules, each contribute one entry to `ADAPTERS`,
named after the module; a synthetic listing with an unregistered or a
duplicated adapter breaks the check. Step 3 appends `pattern` and declares
`settings` and `detection` as support modules. Step 5 inserts `python` before
`pattern` and declares the `toml_scan` support module. Step 6 inserts `npm`
after `python` and declares the `json_scan` support module. Step 7 inserts
`maven` after `npm` and declares the `xml_scan` and `maven_references` support
modules: the final order `("anchor", "python", "npm", "maven", "pattern")` is
now pinned.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections import Counter
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow import sources
from tools.release_workflow.sources import anchor, maven, npm, pattern, python

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from tools.release_workflow.sources.model import Adapter


def _registry_problems(modules: Iterable[str], support: frozenset[str], adapters: Sequence[Adapter]) -> list[str]:
    """List adapter modules missing from the tuple, duplicated or without a module."""
    expected = set(modules) - support
    counts = Counter(adapter.name for adapter in adapters)
    problems = [f"missing from ADAPTERS: {name}" for name in sorted(expected - set(counts))]
    problems += [f"listed {count} times: {name}" for name, count in sorted(counts.items()) if count > 1]
    problems += [f"no adapter module: {name}" for name in sorted(set(counts) - expected)]
    return problems


def _modules() -> list[str]:
    """Name the modules of the sources package."""
    return [info.name for info in pkgutil.iter_modules(sources.__path__)]


def test_every_adapter_module_is_registered_once() -> None:
    """The real package and tuple agree, and each entry is its module's `ADAPTER`."""
    modules = _modules()
    assert _registry_problems(modules, sources.SUPPORT_MODULES, sources.ADAPTERS) == []
    for name in sorted(set(modules) - sources.SUPPORT_MODULES):
        module = importlib.import_module(f"tools.release_workflow.sources.{name}")
        assert module.ADAPTER in sources.ADAPTERS


def test_detection_order() -> None:
    """The anchor comes first and `pattern` last, with every format adapter between them in the final order."""
    assert tuple(adapter.name for adapter in sources.ADAPTERS) == ("anchor", "python", "npm", "maven", "pattern")
    assert frozenset({"model", "settings", "detection", "toml_scan", "json_scan", "xml_scan", "maven_references"}) == sources.SUPPORT_MODULES


@pytest.mark.parametrize(("modules", "adapters", "problem"), [
    (["anchor", "maven", "model", "npm", "pattern", "python", "extra"],
     (anchor.ADAPTER, python.ADAPTER, npm.ADAPTER, maven.ADAPTER, pattern.ADAPTER), "missing from ADAPTERS: extra"),
    (["anchor", "model", "pattern"], (anchor.ADAPTER, pattern.ADAPTER, anchor.ADAPTER), "listed 2 times: anchor"),
    (["model", "pattern"], (anchor.ADAPTER, pattern.ADAPTER), "no adapter module: anchor"),
])
def test_synthetic_listing_breaks_the_check(modules: list[str], adapters: tuple[Adapter, ...], problem: str) -> None:
    """An unregistered module, a duplicate entry or an entry without a module is reported."""
    assert _registry_problems(modules, sources.SUPPORT_MODULES, adapters) == [problem]


# eof
