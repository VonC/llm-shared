"""Version source adapters in detection order, and the modules supporting them.

Step 2 of v0.14.0 version-sources registers the `anchor` adapter. Step 3
appends `pattern` and adds the `settings` and `detection` support modules.
Step 5 inserts `python` before `pattern` and adds the `toml_scan` support
module. Step 6 inserts `npm` after `python` and adds the `json_scan` support
module. Step 7 inserts `maven` after `npm` and adds the `xml_scan` and
`maven_references` support modules, completing the design's order. Every
other module of this package is a support module and declares no adapter; the
registry test checks that each adapter module appears once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.release_workflow.sources import anchor, maven, npm, pattern, python

if TYPE_CHECKING:
    from tools.release_workflow.sources.model import Adapter

ADAPTERS: tuple[Adapter, ...] = (anchor.ADAPTER, python.ADAPTER, npm.ADAPTER, maven.ADAPTER, pattern.ADAPTER)
SUPPORT_MODULES = frozenset({"model", "settings", "detection", "toml_scan", "json_scan", "xml_scan", "maven_references"})


# eof
