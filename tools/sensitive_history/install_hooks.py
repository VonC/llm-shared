#!/usr/bin/env python3
"""Install composable Git dispatchers for pending sensitive-content checks."""

from __future__ import annotations

import argparse
import stat
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

DISPATCHER_MARKER = "# llm-shared managed hook dispatcher v1"
ENTRY_MARKER = "# llm-shared managed sensitive hook v1"
HOOK_LAUNCHERS = {
    "pre-commit": "sensitive_pre_commit.py",
    "commit-msg": "sensitive_commit_msg.py",
}
SHARED_RULES_CONFIG = "sensitive.sharedRulesFile"


class HookInstallError(RuntimeError):
    """Report a hook installation that cannot safely continue."""


def _git_path(repo: Path, name: str) -> Path:
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "rev-parse", "--git-path", name],  # noqa: S607
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as error:
        message = f"cannot resolve Git {name!r} path for {repo}"
        raise HookInstallError(message) from error
    path = Path(result.stdout.strip())
    return (path if path.is_absolute() else repo / path).resolve()


def _configure_shared_rules(repo: Path, shared_rules: Path) -> bool:
    """Point one repository at the common sensitive replacement rules."""
    resolved = shared_rules.resolve()
    if not resolved.is_file():
        message = f"shared sensitive rules file not found: {resolved}"
        raise HookInstallError(message)
    try:
        current = subprocess.run(  # noqa: S603
            ["git", "config", "--path", "--get", SHARED_RULES_CONFIG],  # noqa: S607
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        current_path = Path(current.stdout.strip()) if current.returncode == 0 else None
        if current_path is not None:
            current_path = current_path if current_path.is_absolute() else repo / current_path
            if current_path.resolve() == resolved:
                return False
        subprocess.run(  # noqa: S603
            [  # noqa: S607
                "git",
                "config",
                "--local",
                SHARED_RULES_CONFIG,
                resolved.as_posix(),
            ],
            cwd=repo,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        message = f"cannot configure shared sensitive rules for {repo}"
        raise HookInstallError(message) from error
    return True


def _dispatcher() -> str:
    return f"""#!/bin/sh
{DISPATCHER_MARKER}
hook_dir=${{0%/*}}
[ "$hook_dir" != "$0" ] || hook_dir=.
hook_name=${{0##*/}}
for hook in "$hook_dir/$hook_name.d/"*; do
    [ -f "$hook" ] || continue
    "$hook" "$@" || exit $?
done
exit 0
"""


def _shell_quote(path: Path) -> str:
    return "'" + path.as_posix().replace("'", "'\"'\"'") + "'"


def _entry(python_executable: Path, launcher: Path) -> str:
    return f"""#!/bin/sh
{ENTRY_MARKER}
exec {_shell_quote(python_executable)} {_shell_quote(launcher)} "$@"
"""


def _write_executable(path: Path, content: str) -> bool:
    encoded = content.encode("utf-8")
    if path.is_file() and path.read_bytes() == encoded:
        return False
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(encoded)
    temporary.chmod(
        temporary.stat().st_mode
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IXOTH,
    )
    temporary.replace(path)
    return True


def _adopt_existing_hook(hook: Path, chain_dir: Path) -> None:
    if not hook.exists() or DISPATCHER_MARKER.encode() in hook.read_bytes():
        return
    preserved = chain_dir / "50-existing"
    if preserved.exists():
        message = f"cannot preserve {hook}: {preserved} already exists"
        raise HookInstallError(message)
    hook.replace(preserved)


def install_hooks(
    repo: Path,
    shared_root: Path,
    shared_rules: Path | None = None,
) -> tuple[str, ...]:
    """Install or verify both sensitive pending-commit hook chains."""
    resolved_repo = repo.resolve()
    hooks_dir = _git_path(resolved_repo, "hooks")
    hooks_dir.mkdir(parents=True, exist_ok=True)
    changes: list[str] = []
    if shared_rules is not None and _configure_shared_rules(resolved_repo, shared_rules):
        changes.append("configured shared sensitive rules")
    for hook_name, launcher_name in HOOK_LAUNCHERS.items():
        hook = hooks_dir / hook_name
        chain_dir = hooks_dir / f"{hook_name}.d"
        chain_dir.mkdir(exist_ok=True)
        had_unmanaged_hook = hook.exists() and DISPATCHER_MARKER.encode() not in hook.read_bytes()
        _adopt_existing_hook(hook, chain_dir)
        if had_unmanaged_hook:
            changes.append(f"preserved existing {hook_name}")
        if _write_executable(hook, _dispatcher()):
            changes.append(f"installed {hook_name} dispatcher")
        entry = chain_dir / "90-sensitive"
        launcher = shared_root.resolve() / "tools" / "sensitive_history" / launcher_name
        if _write_executable(entry, _entry(Path(sys.executable).resolve(), launcher)):
            changes.append(f"installed {hook_name} sensitive check")
    return tuple(changes)


def main(argv: Sequence[str] | None = None) -> int:
    """Install hooks for one repository."""
    parser = argparse.ArgumentParser(prog="install-sensitive-hooks")
    parser.add_argument("repo", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument(
        "--shared-root",
        type=Path,
        default=Path(__file__).parent.parent.parent,
    )
    parser.add_argument("--shared-rules", type=Path)
    args = parser.parse_args(argv)
    try:
        changes = install_hooks(args.repo, args.shared_root, args.shared_rules)
    except (HookInstallError, OSError) as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return 1
    if changes:
        for change in changes:
            sys.stdout.write(f"HOOK: {change}\n")
    else:
        sys.stdout.write("HOOK: sensitive hooks already installed\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
