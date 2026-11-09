"""Guarded writer for the llm-shared session journal.

pause-session and resume-session keep one private index of the sessions
paused and resumed across checkouts: ``sessions.journal.md`` in the user's
``.llm-shared`` folder. Every update rewrites the whole file, so a faulty
rewrite can silently drop every other entry. This tool is the only writer, and
it updates the journal in two commands, each run as its own shell call and
never chained with the command that wrote the new entry:

``plan``
    Re-read the journal and build the new content in memory from entry files
    (``--add``, appended after the live entries) and, for a restore, from older
    entries (``--recover``, put back before them) or an older full copy
    (``--base``). Check it, then write the candidate and a JSON manifest to a
    new plan folder beside the journal, or to ``--out-dir``. The journal is not
    touched.
``apply``
    Replace the journal with a planned candidate only when the journal still
    has the SHA-256 the plan read and the candidate still passes every check:
    a timestamped backup first, then a temporary file beside the journal,
    flushed to disk and read back, an atomic replace and a final read-back.
    Once the journal reads back, only the newest 50 of the tool's own backups
    are kept; a pruning failure is reported as a warning, never as an error.

The entry rules and checks live in ``tools/session_journal_entries.py``; this
module keeps the files, the two commands and the command line.

Exit codes: 0 done, 2 refused (the journal is unchanged), 3 the journal was
replaced but does not read back as the candidate (restore the printed backup).
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import secrets
import sys
from pathlib import Path
from typing import TYPE_CHECKING, cast

if __name__ == "__main__":
    # bin\session_journal.bat runs this file in isolated mode (-I), which puts
    # neither the current folder nor this file's folder on sys.path: add the
    # llm-shared root so the entries module imports as part of tools.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.session_journal_entries import (
    TITLE,
    Journal,
    JournalRefusedError,
    Sources,
    decode,
    merge,
    parse_journal,
    render,
    validate,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from tools.session_journal_entries import Entry

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "session-journal.template.md"
CANDIDATE_NAME = "sessions.journal.candidate.md"
MANIFEST_NAME = "sessions.journal.manifest.json"
SUMMARY_KEYS = ("before_count", "after_count", "removed", "added")
BACKUPS_KEPT = 50
EXIT_REFUSED = 2
EXIT_UNVERIFIED = 3


class JournalUnverifiedError(Exception):
    """The journal was replaced, but it does not read back as the candidate."""


def default_journal() -> Path:
    """Return the journal path: under USERPROFILE, or HOME only where USERPROFILE is unset."""
    home = os.environ.get("USERPROFILE") or os.environ.get("HOME")
    if not home:
        msg = "neither USERPROFILE nor HOME is set: pass --journal"
        raise JournalRefusedError(msg)
    return Path(home) / ".llm-shared" / "sessions.journal.md"


def sha256(data: bytes) -> str:
    """Return the hexadecimal SHA-256 of some bytes."""
    return hashlib.sha256(data).hexdigest()


def _read_optional(path: Path) -> bytes | None:
    """Read a file's bytes, or return None when it does not exist."""
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def _entries_from_files(paths: Iterable[Path]) -> tuple[Entry, ...]:
    """Read entry files: each holds one or more entries and nothing before them."""
    entries: list[Entry] = []
    for path in paths:
        origin = str(path)
        journal = parse_journal(decode(path.read_bytes(), origin, entry_file=True), origin)
        if journal.preamble.strip():
            msg = f"{origin}: text before the first entry heading"
            raise JournalRefusedError(msg)
        if not journal.entries:
            msg = f"{origin}: no entry"
            raise JournalRefusedError(msg)
        entries.extend(journal.entries)
    return tuple(entries)


def _sources(add: Sequence[Path], recover: Sequence[Path], base: Path | None) -> Sources:
    """Read every source a plan merges, refusing a plan with nothing to merge."""
    if not (add or recover or base):
        msg = "nothing to plan: give --add, --recover or --base"
        raise JournalRefusedError(msg)
    older = parse_journal(decode(base.read_bytes(), str(base)), str(base)) if base else Journal("", ())
    return Sources(older, _entries_from_files(recover), _entries_from_files(add))


def _template_preamble() -> str:
    """Return the title and first paragraph of the shipped journal template."""
    return TEMPLATE.read_text(encoding="utf-8").split("\n## ", 1)[0].strip("\n")


def build_candidate(live: Journal, sources: Sources) -> str:
    """Return the new journal text: the merged entries under the kept preamble.

    The preamble is the live one, else the base copy's, else the template's
    title and first paragraph, as for a journal that does not exist yet.
    """
    preamble = live.preamble or sources.base.preamble or _template_preamble()
    if not preamble.startswith(TITLE):
        msg = "no journal title in the live journal or the base copy"
        raise JournalRefusedError(msg)
    entries = merge([*sources.base.entries, *sources.recovered, *live.entries, *sources.added])
    return render(Journal(preamble, tuple(entries)))


def _stamp() -> str:
    """Return a sortable local timestamp with a random suffix, for new file names."""
    return f"{dt.datetime.now(dt.UTC).astimezone():%Y%m%dT%H%M%S}-{secrets.token_hex(4)}"


def _plans_root(journal: Path) -> Path:
    """Return the folder that holds the default plan folders of a journal."""
    return journal.with_name(f"{journal.stem}.plans")


def _backups_root(journal: Path) -> Path:
    """Return the folder that holds the timestamped backups of a journal."""
    return journal.with_name(f"{journal.stem}.backups")


def _ensure_private_folder(folder: Path) -> None:
    """Create a missing journal folder with a .gitignore that ignores all of it."""
    if not folder.exists():
        folder.mkdir(parents=True)
        (folder / ".gitignore").write_bytes(b"*\n")


def _plan_folder(journal: Path, out_dir: Path | None) -> Path:
    """Return the plan folder: the given one, or a new one beside the journal."""
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir.absolute()
    _ensure_private_folder(journal.parent)
    folder = _plans_root(journal) / _stamp()
    folder.mkdir(parents=True)
    return folder


def _write_synced(path: Path, data: bytes) -> None:
    """Create a new file with these bytes, flush it to disk, and read it back.

    Raises:
        JournalRefusedError: the read-back differs; the new file is removed.
    """
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    if path.read_bytes() != data:
        path.unlink()
        msg = f"{path}: read-back differs from the bytes written"
        raise JournalRefusedError(msg)


def plan_update(
    journal: Path,
    *,
    add: Sequence[Path] = (),
    recover: Sequence[Path] = (),
    base: Path | None = None,
    out_dir: Path | None = None,
) -> dict[str, object]:
    """Build and check a candidate journal and write it with its manifest.

    The journal itself is only read. The returned report names the manifest
    that ``apply`` takes, the removed and added entry headings, and the
    requested entries left out because a newer one already exists.
    """
    sources = _sources(add, recover, base)
    journal = journal.absolute()
    live_bytes = _read_optional(journal)
    live_text = decode(live_bytes or b"", "live journal")
    candidate_text = build_candidate(parse_journal(live_text, "live journal"), sources)
    report = validate(live_text, candidate_text, sources.requested)
    folder = _plan_folder(journal, out_dir)
    candidate = folder / CANDIDATE_NAME
    candidate_bytes = candidate_text.encode("utf-8")
    _write_synced(candidate, candidate_bytes)
    manifest: dict[str, object] = {
        "journal": str(journal),
        "journal_sha256": None if live_bytes is None else sha256(live_bytes),
        "candidate": str(candidate),
        "candidate_sha256": sha256(candidate_bytes),
        **report.summary(),
        "superseded": list(report.superseded),
    }
    manifest_path = folder / MANIFEST_NAME
    _write_synced(manifest_path, json.dumps(manifest, indent=2).encode("utf-8"))
    return {"manifest": str(manifest_path), **manifest}


def _read_manifest(path: Path) -> dict[str, object]:
    """Read a plan manifest, refusing anything but a JSON object."""
    data: object = json.loads(path.read_bytes())
    if not isinstance(data, dict):
        msg = f"{path}: the manifest is not a JSON object"
        raise JournalRefusedError(msg)
    return cast("dict[str, object]", data)


def _text(manifest: Mapping[str, object], key: str) -> str:
    """Return a manifest string field, refusing a missing or mistyped one."""
    value = manifest.get(key)
    if not isinstance(value, str):
        msg = f"manifest field {key!r} is missing or not a string"
        raise JournalRefusedError(msg)
    return value


def _optional_text(manifest: Mapping[str, object], key: str) -> str | None:
    """Return a manifest string field that may be null, as for a missing journal."""
    value = manifest.get(key)
    if value is not None and not isinstance(value, str):
        msg = f"manifest field {key!r} is not a string or null"
        raise JournalRefusedError(msg)
    return value


def _check_unchanged(live: bytes | None, expected: str | None, moment: str) -> None:
    """Refuse when the journal's SHA-256 is no longer the one the plan read."""
    actual = None if live is None else sha256(live)
    if actual != expected:
        msg = f"the journal changed {moment}: run plan again"
        raise JournalRefusedError(msg)


def _backup(journal: Path, live: bytes | None) -> Path | None:
    """Keep a timestamped copy of the live journal; a missing journal has none."""
    if live is None:
        return None
    folder = _backups_root(journal)
    folder.mkdir(exist_ok=True)
    backup = folder / f"{journal.name}.{_stamp()}.bak"
    _write_synced(backup, live)
    return backup


def _backups_newest_first(journal: Path) -> list[Path]:
    """Return the tool's own backups of a journal, newest name timestamp first.

    Only names the tool writes count: the journal name, a ``YYYYMMDDTHHMMSS``
    timestamp, an eight-digit hexadecimal suffix and ``.bak``. Any other file
    in the backups folder is ignored, never pruned.
    """
    pattern = re.compile(re.escape(journal.name) + r"\.(\d{8}T\d{6})-[0-9a-f]{8}\.bak")
    stamped = [
        (match[1], path.name, path)
        for path in _backups_root(journal).iterdir()
        if (match := pattern.fullmatch(path.name))
    ]
    return [path for _stamp_text, _name, path in sorted(stamped, reverse=True)]


def _prune_backups(journal: Path, kept: Path | None) -> tuple[int, list[str]]:
    """Delete the tool's backups beyond the newest ``BACKUPS_KEPT``, never ``kept``.

    Returns the number of backups deleted and the warnings to report. Called
    only after the journal was replaced and read back, so a failure here never
    turns that apply into an error. A journal created by this apply had no
    backup, so nothing is pruned.
    """
    pruned = 0
    if kept is None:
        return pruned, []
    try:
        for path in _backups_newest_first(journal)[BACKUPS_KEPT:]:
            if path.name != kept.name:
                path.unlink()
                pruned += 1
    except OSError as error:
        return pruned, [f"older backups not fully pruned: {error}"]
    return pruned, []


def _replace(journal: Path, candidate: bytes, expected: str | None, backup: Path | None) -> None:
    """Write a temporary file beside the journal, then swap it in atomically.

    Raises:
        JournalRefusedError: the journal changed meanwhile; it is left as is.
        JournalUnverifiedError: the replaced journal does not read back as
            the candidate.
    """
    _ensure_private_folder(journal.parent)
    temp = journal.with_name(f"{journal.name}.{_stamp()}.tmp")
    try:
        _write_synced(temp, candidate)
        _check_unchanged(_read_optional(journal), expected, "during apply")
        temp.replace(journal)
    finally:
        temp.unlink(missing_ok=True)
    written: bytes | None = None
    with contextlib.suppress(OSError):
        written = journal.read_bytes()
    if written != candidate:
        msg = f"{journal} does not read back as the candidate; the previous content is in {backup}"
        raise JournalUnverifiedError(msg)


def _remove_plan(journal: Path, manifest: Path, candidate: Path) -> None:
    """Remove an applied plan's files, and its folder when it is a default one.

    Fix: both sides of the folder comparison are resolved, so a short (8.3)
    and a long spelling of the same Windows folder still match.
    """
    with contextlib.suppress(OSError):
        folder = manifest.resolve().parent
        candidate.unlink(missing_ok=True)
        manifest.unlink(missing_ok=True)
        if folder.parent == _plans_root(journal).resolve():
            folder.rmdir()


def apply_plan(manifest_path: Path) -> dict[str, object]:
    """Replace the journal with a planned candidate after every check passes again."""
    manifest = _read_manifest(manifest_path)
    journal = Path(_text(manifest, "journal"))
    candidate_path = Path(_text(manifest, "candidate"))
    expected = _optional_text(manifest, "journal_sha256")
    live = _read_optional(journal)
    _check_unchanged(live, expected, "since the plan")
    candidate = candidate_path.read_bytes()
    if sha256(candidate) != _text(manifest, "candidate_sha256"):
        msg = "the candidate changed since the plan: run plan again"
        raise JournalRefusedError(msg)
    report = validate(decode(live or b"", "live journal"), decode(candidate, "candidate"))
    if report.summary() != {key: manifest.get(key) for key in SUMMARY_KEYS}:
        msg = "the candidate no longer matches the plan report: run plan again"
        raise JournalRefusedError(msg)
    backup = _backup(journal, live)
    _replace(journal, candidate, expected, backup)
    pruned, warnings = _prune_backups(journal, backup)
    _remove_plan(journal, manifest_path, candidate_path)
    return {
        "applied": str(journal),
        "backup": None if backup is None else str(backup),
        **report.summary(),
        "pruned_backups": pruned,
        "warnings": warnings,
    }


def _parser() -> argparse.ArgumentParser:
    """Build the two-command parser."""
    parser = argparse.ArgumentParser(
        prog="session_journal",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="build and check a candidate; the journal is only read")
    plan.add_argument("--journal", type=Path, help="journal path (default: the user's .llm-shared folder)")
    plan.add_argument("--add", type=Path, action="append", default=[], metavar="FILE", help="new entries, appended after the live ones")
    plan.add_argument("--recover", type=Path, action="append", default=[], metavar="FILE", help="older entries, put back before the live ones")
    plan.add_argument("--base", type=Path, metavar="FILE", help="older full journal copy to restore from")
    plan.add_argument("--out-dir", type=Path, metavar="DIR", help="plan folder (default: a new folder beside the journal)")
    apply = commands.add_parser("apply", help="replace the journal with a planned candidate")
    apply.add_argument("--manifest", type=Path, required=True, metavar="FILE", help="manifest printed by plan")
    return parser


def _run(args: argparse.Namespace) -> dict[str, object]:
    """Run the parsed command and return its JSON report."""
    if args.command == "plan":
        return plan_update(
            args.journal or default_journal(),
            add=args.add,
            recover=args.recover,
            base=args.base,
            out_dir=args.out_dir,
        )
    return apply_plan(args.manifest)


def main(argv: Sequence[str] | None = None) -> int:
    """Run plan or apply; print a JSON report, or the reason on stderr."""
    args = _parser().parse_args(argv)
    try:
        result = _run(args)
    except JournalUnverifiedError as error:
        sys.stderr.write(f"session_journal: unverified: {error}\n")
        return EXIT_UNVERIFIED
    except (JournalRefusedError, OSError, ValueError) as error:
        sys.stderr.write(f"session_journal: refused, the journal is unchanged: {error}\n")
        return EXIT_REFUSED
    sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# eof
