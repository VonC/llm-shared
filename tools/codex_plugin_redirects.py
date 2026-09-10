"""Validate Codex plugin redirects from their installed cache locations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _relative_url(adapter: Path, target: Path) -> str:
    """Return the Markdown path from one cached adapter to its target."""
    return Path(os.path.relpath(target, start=adapter.parent)).as_posix()


def _validate_redirects(
    adapter_root: Path,
    canonical_root: Path,
    cache_root: Path,
) -> list[str]:
    """Return every redirect mismatch in one plugin package."""
    errors: list[str] = []
    instructions = canonical_root / "instructions"
    for canonical in sorted(instructions.glob("*.md")):
        name = canonical.name
        cached_instruction = cache_root / "instructions" / name
        instruction_url = _relative_url(cached_instruction, canonical)
        expected_instruction = (
            "Read and follow the canonical instruction at "
            f"[`instructions/{name}`]({instruction_url}).\n"
        )
        packaged_instruction = adapter_root / "instructions" / name
        if not packaged_instruction.is_file():
            errors.append(f"missing instruction redirect: {packaged_instruction}")
        elif packaged_instruction.read_text(encoding="utf-8") != expected_instruction:
            errors.append(
                f"wrong cache-relative redirect: {packaged_instruction} "
                f"(expected {instruction_url})",
            )

        skill_name = canonical.stem.replace("_", "-")
        cached_skill = cache_root / "skills" / skill_name / "SKILL.md"
        skill_url = _relative_url(cached_skill, canonical)
        packaged_skill = adapter_root / "skills" / skill_name / "SKILL.md"
        expected_suffix = (
            "Read and follow [the canonical instruction]"
            f"({skill_url})"
        )
        if not packaged_skill.is_file():
            errors.append(f"missing skill redirect: {packaged_skill}")
        elif not packaged_skill.read_text(encoding="utf-8").rstrip().endswith(
            expected_suffix,
        ):
            errors.append(
                f"wrong cache-relative redirect: {packaged_skill} "
                f"(expected {skill_url})",
            )

    canonical_rule = canonical_root / "rules" / "docs_layout.md"
    cached_rule = cache_root / "rules" / "docs_layout.md"
    rule_url = _relative_url(cached_rule, canonical_rule)
    packaged_rule = adapter_root / "rules" / "docs_layout.md"
    expected_rule = (
        "Read and follow the canonical rule at "
        f"[`rules/docs_layout.md`]({rule_url}).\n"
    )
    if not packaged_rule.is_file():
        errors.append(f"missing rule redirect: {packaged_rule}")
    elif packaged_rule.read_text(encoding="utf-8") != expected_rule:
        errors.append(
            f"wrong cache-relative redirect: {packaged_rule} "
            f"(expected {rule_url})",
        )
    return errors


def _plugin_version(plugin_root: Path) -> str:
    """Read the cache directory name from the source plugin manifest."""
    manifest = plugin_root / ".codex-plugin" / "plugin.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    version = data.get("version")
    if not isinstance(version, str) or not version:
        message = f"missing plugin version in {manifest}"
        raise ValueError(message)
    return version


def main() -> int:
    """Validate source redirects or their installed cache copy."""
    parser = argparse.ArgumentParser()
    parser.add_argument("plugin_root", type=Path)
    parser.add_argument("canonical_root", type=Path)
    parser.add_argument("cache_base", type=Path)
    parser.add_argument("--installed", action="store_true")
    args = parser.parse_args()

    cache_root = args.cache_base / _plugin_version(args.plugin_root)
    adapter_root = cache_root if args.installed else args.plugin_root
    errors = _validate_redirects(
        adapter_root.resolve(),
        args.canonical_root.resolve(),
        cache_root.resolve(),
    )
    if errors:
        for error in errors:
            sys.stderr.write(f"ERROR: {error}\n")
        return 1
    location = "installed cache" if args.installed else "plugin source"
    sys.stdout.write(
        f"Validated cache-relative redirects in {location}: {adapter_root}\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
