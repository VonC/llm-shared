r"""Validate the Codex skill package redirects relative to their place in the clone.

Codex reads the llm-shared skills through the ``%USERPROFILE%\.agents\skills``
link to ``.agents/llm-shared/skills`` and follows that link to the clone, so
every redirect is a Markdown link relative to the adapter file in the clone:
``../../../../instructions/<name>.md`` from a ``skills/<skill>/SKILL.md``
wrapper, ``../../../instructions/<name>.md`` and ``../../../rules/<name>.md``
from the package compatibility redirects. The links resolve wherever the clone
lives.

Fix: links were relative to the installed plugin cache
(``.codex\plugins\cache\<marketplace>\llm-shared\<version>``) and assumed a
clone at ``%USERPROFILE%\git\llm-shared``. The cache base, the manifest
version lookup and the ``--installed`` check are gone: the clone is the only
place Codex reads the package from.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PACKAGE = Path(".agents") / "llm-shared"


def _relative_url(adapter: Path, target: Path) -> str:
    """Return the Markdown path from one adapter to its target."""
    return Path(os.path.relpath(target, start=adapter.parent)).as_posix()


def _redirect_body(adapter: Path) -> str:
    """Read a redirect body, excluding optional closed metadata front matter."""
    content = adapter.read_text(encoding="utf-8")
    if content.startswith("---\n"):
        _, separator, body = content[4:].partition("\n---\n")
        if separator:
            return body.lstrip("\n")
    return content


def _instruction_errors(adapter_root: Path, canonical: Path) -> list[str]:
    """Check the compatibility redirect and the skill wrapper of one instruction."""
    errors: list[str] = []
    name = canonical.name
    packaged_instruction = adapter_root / "instructions" / name
    instruction_url = _relative_url(packaged_instruction, canonical)
    expected_instruction = (
        "Read and follow the canonical instruction at "
        f"[`instructions/{name}`]({instruction_url}).\n"
    )
    if not packaged_instruction.is_file():
        errors.append(f"missing instruction redirect: {packaged_instruction}")
    elif _redirect_body(packaged_instruction) != expected_instruction:
        errors.append(
            f"wrong clone-relative redirect: {packaged_instruction} "
            f"(expected {instruction_url})",
        )

    skill_name = canonical.stem.replace("_", "-")
    packaged_skill = adapter_root / "skills" / skill_name / "SKILL.md"
    skill_url = _relative_url(packaged_skill, canonical)
    expected_suffix = f"Read and follow [the canonical instruction]({skill_url})"
    if not packaged_skill.is_file():
        errors.append(f"missing skill redirect: {packaged_skill}")
    elif not packaged_skill.read_text(encoding="utf-8").rstrip().endswith(
        expected_suffix,
    ):
        errors.append(
            f"wrong clone-relative redirect: {packaged_skill} "
            f"(expected {skill_url})",
        )
    return errors


def _validate_redirects(adapter_root: Path, canonical_root: Path) -> list[str]:
    """Return every redirect mismatch in one package, read where it lies."""
    errors: list[str] = []
    for canonical in sorted((canonical_root / "instructions").glob("*.md")):
        errors.extend(_instruction_errors(adapter_root, canonical))

    canonical_rule = canonical_root / "rules" / "docs_layout.md"
    packaged_rule = adapter_root / "rules" / "docs_layout.md"
    rule_url = _relative_url(packaged_rule, canonical_rule)
    expected_rule = (
        "Read and follow the canonical rule at "
        f"[`rules/docs_layout.md`]({rule_url}).\n"
    )
    if not packaged_rule.is_file():
        errors.append(f"missing rule redirect: {packaged_rule}")
    elif _redirect_body(packaged_rule) != expected_rule:
        errors.append(
            f"wrong clone-relative redirect: {packaged_rule} "
            f"(expected {rule_url})",
        )
    return errors


def validate_redirects(clone_root: Path) -> list[str]:
    """Return every redirect problem of the package inside one clone.

    Args:
        clone_root: The llm-shared clone holding ``instructions/``, ``rules/``
            and the ``.agents/llm-shared`` package.

    Returns:
        One message per missing or wrong redirect; empty when all are valid.
    """
    root = clone_root.resolve()
    return _validate_redirects(root / PACKAGE, root)


def main(argv: list[str] | None = None) -> int:
    """Validate the redirects of one clone, this file's clone by default."""
    parser = argparse.ArgumentParser(
        description="Validate the clone-relative redirects of the llm-shared Codex skill package.",
    )
    parser.add_argument(
        "clone_root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    args = parser.parse_args(argv)
    errors = validate_redirects(args.clone_root)
    if errors:
        for error in errors:
            sys.stderr.write(f"ERROR: {error}\n")
        return 1
    sys.stdout.write(
        f"Validated clone-relative redirects in: {args.clone_root / PACKAGE}\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
