"""Describe calling-shell contracts and assess complete before/after snapshots.

These decisions stay process-free; shell_runner supplies actual cmd evidence.
Refused preparations must preserve every owned key, including missing values.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from tools.pytest_plugin_shell import OWNED_KEYS

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

PUNCTUATION = 'spaces %percent% !bang! ^caret &amp "quotes"'
DUMPER = """import json, os, sys
from pathlib import Path
keys = {keys!r}
Path(os.environ["PROBE_OUTPUT"] + "." + sys.argv[1] + ".json").write_text(
    json.dumps({{key: os.environ.get(key) for key in keys}}, ensure_ascii=False), encoding="utf-8")
""".format(keys=(*OWNED_KEYS, "PROBE_EXIT"))


@dataclass(frozen=True)
class ShellCase:
    """Carry one named caller state, expected exit and environment suffixes."""

    name: str
    delayed: str
    cwd: Path
    extra: dict[str, str]
    code: int = 0


def cases(project: Path, drive: Path) -> tuple[ShellCase, ...]:
    """Keep all eight sequential and two concurrent preparation contracts."""
    result: list[ShellCase] = []
    common = {"LLM_SHARED_PYTEST_PLUGINS": "lifecycle,process", "PYTHONPATH": PUNCTUATION, "PYTEST_ADDOPTS": PUNCTUATION}
    for delayed in ("off", "on"):
        result.extend((
            ShellCase("preserve-" + delayed, delayed, project, common),
            ShellCase("atomic-invalid-" + delayed, delayed, project, dict(common, LLM_SHARED_PYTEST_PLUGINS="invalid"), 4),
            ShellCase("atomic-unrepresentable-" + delayed, delayed, project, dict(common, PYTEST_ADDOPTS="emoji \U0001f642"), 4),
            ShellCase("drive-root-" + delayed, delayed, drive, common),
        ))
    result.extend(ShellCase("concurrent-" + delayed, delayed, project, {"LLM_SHARED_PYTEST_PLUGINS": "lifecycle,process"})
                  for delayed in ("off", "on"))
    return tuple(result)


def verdict(case: ShellCase, code: int, before: Mapping[str, str | None], after: Mapping[str, str | None]) -> bool:
    """Reject bad exits, partial application and lost punctuation suffixes."""
    if code != case.code or after.get("PROBE_EXIT") != str(case.code):
        return False
    old = {key: before.get(key) for key in OWNED_KEYS}
    new = {key: after.get(key) for key in OWNED_KEYS}
    if case.code:
        return new == old
    return all((
        new["LLM_SHARED_PYTEST_ROOT"] == str(case.cwd.resolve()),
        new["LLM_SHARED_PYTEST_PLUGINS"] == "lifecycle,process",
        bool(new["LLM_SHARED_PYTEST_POLICY_DIR"]),
        (new["PYTHONPATH"] or "").endswith(case.extra.get("PYTHONPATH", "")),
        (new["PYTEST_ADDOPTS"] or "").endswith(case.extra.get("PYTEST_ADDOPTS", "")),
    ))


def read_snapshot(path: Path) -> dict[str, str | None]:
    """Missing or malformed output cannot establish successful preparation."""
    value: object = json.loads(path.read_text(encoding="utf-8"))
    snapshot = cast("dict[str, object]", value)
    if not isinstance(value, dict) or set(snapshot) != {*OWNED_KEYS, "PROBE_EXIT"}:
        message = "Incomplete shell snapshot"
        raise ValueError(message)
    result: dict[str, str | None] = {}
    for key, item in snapshot.items():
        if not isinstance(item, (str, type(None))):
            message = "Invalid shell snapshot value"
            raise ValueError(message)  # noqa: TRY004 - malformed external JSON is an invalid value
        result[str(key)] = item
    return result


# eof
