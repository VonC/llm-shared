"""Session journal writes keep every other entry, or refuse and write nothing.

The journal is replaced only by ``apply``, after a ``plan`` whose checks pass
again on the bytes ``apply`` reads. Every test works in a scratch home:
USERPROFILE and HOME point there, so no test can reach the real journal.

Fix: the entry model names import from ``tools.session_journal_entries`` since
the module split, and the run-as-script test restores ``sys.path`` after the
module adds the llm-shared root to it.
"""

from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path

import pytest

from tools import session_journal
from tools.session_journal import apply_plan, default_journal, main, plan_update
from tools.session_journal_entries import (
    Journal,
    JournalRefusedError,
    checkout_key,
    render,
    validate,
)

PREAMBLE = "# Session journal\n\nPrivate index.\n"
REFUSED = 2
UNVERIFIED = 3


def _entry(kind: str, stamp: str, checkout: str, note: str) -> str:
    """Build one entry in the template's form."""
    return f"## {kind} by claude at {stamp} in `{checkout}`\n\n- Host: test\n- Summary: {note}\n"


A_PAUSE = _entry("Pause", "2026-11-08T10:00:00+01:00", "C:/work/app", "app paused")
B_PAUSE = _entry("Pause", "2026-11-08T11:00:00+01:00", "C:/work/lib", "lib paused")
A_RESUME = _entry("Resume", "2026-11-08T12:00:00.1234567+01:00", "C:/work/app", "app resumed")
A_PAUSE_NEW = _entry("Pause", "2026-11-09T09:00:00+01:00", "C:/work/./app", "app paused again")
A_PAUSE_OLD = _entry("Pause", "2026-11-07T09:00:00+01:00", "C:/work/app", "app paused long ago")
LIVE = PREAMBLE + "\n" + A_PAUSE + "\n" + B_PAUSE + "\n" + A_RESUME
AFTER_NEW_PAUSE = PREAMBLE + "\n" + B_PAUSE + "\n" + A_RESUME + "\n" + A_PAUSE_NEW


@pytest.fixture(autouse=True)
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point USERPROFILE and HOME at a scratch folder, never at the real journal."""
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


@pytest.fixture
def journal(home: Path) -> Path:
    """Write a live journal holding three entries for two checkouts."""
    path = home / ".llm-shared" / "sessions.journal.md"
    path.parent.mkdir()
    path.write_bytes(LIVE.encode())
    return path


def _file(folder: Path, name: str, text: str) -> Path:
    """Write a UTF-8 file and return its path."""
    path = folder / name
    path.write_bytes(text.encode())
    return path


def _heading(entry: str) -> str:
    """Return the heading line of an entry."""
    return entry.split("\n", 1)[0]


def _headings(text: str) -> list[str]:
    """Return the entry heading lines of a journal, in order."""
    return [line for line in text.split("\n") if line.startswith("## ")]


def _planned(journal: Path, home: Path, entry: str = A_PAUSE_NEW) -> dict[str, object]:
    """Plan the addition of one entry file to the journal."""
    return plan_update(journal, add=[_file(home, "entry.md", entry)])


def _tamper(manifest_path: Path, candidate: bytes, **fields: object) -> None:
    """Swap the planned candidate and fix its digest, as a careless rewrite would."""
    manifest = json.loads(manifest_path.read_bytes())
    Path(manifest["candidate"]).write_bytes(candidate)
    manifest["candidate_sha256"] = session_journal.sha256(candidate)
    manifest.update(fields)
    manifest_path.write_bytes(json.dumps(manifest).encode())


def test_cli_plan_then_apply_replaces_only_that_checkout_older_pause(
    journal: Path,
    home: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The plan only reads; apply drops that checkout's older pause and keeps the rest."""
    entry = _file(home, "entry.md", A_PAUSE_NEW)
    assert main(["plan", "--add", str(entry)]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert journal.read_bytes() == LIVE.encode()
    assert (plan["removed"], plan["added"]) == ([_heading(A_PAUSE)], [_heading(A_PAUSE_NEW)])
    assert main(["apply", "--manifest", plan["manifest"]]) == 0
    assert journal.read_bytes() == AFTER_NEW_PAUSE.encode()


def test_apply_keeps_a_backup_of_the_previous_journal_and_drops_the_plan(journal: Path, home: Path) -> None:
    """The backup holds the exact previous bytes; the default plan folder goes away."""
    result = apply_plan(Path(str(_planned(journal, home)["manifest"])))
    backups = list((journal.parent / "sessions.journal.backups").iterdir())
    assert [backup.read_bytes() for backup in backups] == [LIVE.encode()]
    assert result["backup"] == str(backups[0])
    assert list((journal.parent / "sessions.journal.plans").iterdir()) == []


def _old_backups(journal: Path, year: int, count: int) -> list[str]:
    """Write backups named as the tool names them, all dated early in ``year``."""
    folder = journal.parent / "sessions.journal.backups"
    folder.mkdir(exist_ok=True)
    names = [f"{journal.name}.{year:04d}0101T{index:06d}-{index:08x}.bak" for index in range(count)]
    for name in names:
        (folder / name).write_bytes(b"old\n")
    return names


def test_apply_keeps_the_newest_fifty_backups_and_ignores_other_files(journal: Path, home: Path) -> None:
    """Backups beyond the newest 50 go, oldest first; files the tool did not name stay."""
    old = _old_backups(journal, 2000, 52)
    folder = journal.parent / "sessions.journal.backups"
    strangers = [_file(folder, name, "keep\n").name for name in ("notes.txt", "sessions.journal.md.manual.bak")]
    result = apply_plan(Path(str(_planned(journal, home)["manifest"])))
    assert (result["pruned_backups"], result["warnings"]) == (3, [])
    remaining = sorted(path.name for path in folder.iterdir())
    assert remaining == sorted([*old[3:], Path(str(result["backup"])).name, *strangers])


def test_pruning_never_deletes_the_backup_just_written(journal: Path, home: Path) -> None:
    """Fifty backups dated after the new one still leave the new one in place."""
    later = _old_backups(journal, 2999, session_journal.BACKUPS_KEPT)
    result = apply_plan(Path(str(_planned(journal, home)["manifest"])))
    assert result["pruned_backups"] == 0
    assert Path(str(result["backup"])).read_bytes() == LIVE.encode()
    remaining = sorted(path.name for path in (journal.parent / "sessions.journal.backups").iterdir())
    assert remaining == sorted([*later, Path(str(result["backup"])).name])


def test_a_pruning_failure_is_a_warning_and_the_apply_still_succeeds(
    journal: Path,
    home: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A backup that cannot be deleted leaves the replaced journal and exit 0."""
    _old_backups(journal, 2000, 50)
    report = _planned(journal, home)
    unlink = Path.unlink

    def unlink_except_backups(path: Path, *, missing_ok: bool = False) -> None:
        if path.suffix == ".bak":
            raise PermissionError(13, "in use", str(path))
        unlink(path, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", unlink_except_backups)
    assert main(["apply", "--manifest", str(report["manifest"])]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["pruned_backups"] == 0
    assert "not fully pruned" in result["warnings"][0]
    assert journal.read_bytes() == AFTER_NEW_PAUSE.encode()


def test_apply_keeps_an_explicit_plan_folder_and_only_empties_it(journal: Path, home: Path) -> None:
    """A folder named by --out-dir belongs to the caller: only the plan files go."""
    out_dir = home / "plan"
    report = plan_update(journal, add=[_file(home, "entry.md", A_PAUSE_NEW)], out_dir=out_dir)
    apply_plan(Path(str(report["manifest"])))
    assert list(out_dir.iterdir()) == []


def test_an_older_added_entry_is_superseded_and_never_removes_the_newer_one(journal: Path, home: Path) -> None:
    """An entry older than the live one of its kind is reported, not written."""
    report = _planned(journal, home, A_PAUSE_OLD)
    assert (report["added"], report["removed"], report["superseded"]) == ([], [], [_heading(A_PAUSE_OLD)])
    apply_plan(Path(str(report["manifest"])))
    assert _headings(journal.read_text(encoding="utf-8")) == _headings(LIVE)


def test_apply_refuses_when_the_journal_changed_after_the_plan(
    journal: Path,
    home: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Another writer's entry is never overwritten: apply asks for a new plan."""
    report = _planned(journal, home)
    changed = (LIVE + "\n" + _entry("Pause", "2026-11-08T13:00:00+01:00", "C:/work/cli", "cli paused")).encode()
    journal.write_bytes(changed)
    assert main(["apply", "--manifest", str(report["manifest"])]) == REFUSED
    assert "changed since the plan" in capsys.readouterr().err
    assert journal.read_bytes() == changed
    assert not (journal.parent / "sessions.journal.backups").exists()


def test_apply_refuses_a_candidate_that_drops_live_entries(
    journal: Path,
    home: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The 2026-11-09 failure: a candidate holding only the new entry is refused."""
    manifest = Path(str(_planned(journal, home)["manifest"]))
    _tamper(manifest, (PREAMBLE + "\n" + A_PAUSE_NEW).encode())
    assert main(["apply", "--manifest", str(manifest)]) == REFUSED
    assert "would be lost" in capsys.readouterr().err
    assert journal.read_bytes() == LIVE.encode()
    assert sorted(path.name for path in journal.parent.iterdir()) == ["sessions.journal.md", "sessions.journal.plans"]


def test_apply_refuses_a_candidate_edited_after_the_plan(journal: Path, home: Path) -> None:
    """The candidate must still have the SHA-256 the plan recorded."""
    report = _planned(journal, home)
    Path(str(report["candidate"])).write_bytes(LIVE.encode())
    with pytest.raises(JournalRefusedError, match="candidate changed"):
        apply_plan(Path(str(report["manifest"])))
    assert journal.read_bytes() == LIVE.encode()


def test_apply_refuses_a_manifest_whose_report_no_longer_matches(journal: Path, home: Path) -> None:
    """Apply recomputes the report and compares it with the planned one."""
    report = _planned(journal, home)
    manifest = Path(str(report["manifest"]))
    _tamper(manifest, Path(str(report["candidate"])).read_bytes(), added=[])
    with pytest.raises(JournalRefusedError, match="no longer matches"):
        apply_plan(manifest)
    assert journal.read_bytes() == LIVE.encode()


def test_apply_refuses_when_the_journal_changes_during_apply(
    journal: Path,
    home: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A write landing between the temporary file and the swap keeps its bytes."""
    report = _planned(journal, home)
    changed = LIVE.encode() + b"\n"
    write = session_journal._write_synced

    def write_then_change(path: Path, data: bytes) -> None:
        write(path, data)
        if path.suffix == ".tmp":
            journal.write_bytes(changed)

    monkeypatch.setattr(session_journal, "_write_synced", write_then_change)
    with pytest.raises(JournalRefusedError, match="during apply"):
        apply_plan(Path(str(report["manifest"])))
    assert journal.read_bytes() == changed
    assert [path.name for path in journal.parent.iterdir() if path.suffix == ".tmp"] == []


def test_a_journal_that_does_not_read_back_exits_3_and_names_the_backup(
    journal: Path,
    home: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """After the swap, a differing read-back is reported with the backup path."""
    report = _planned(journal, home)
    replace = Path.replace

    def replace_then_damage(source: Path, target: Path) -> Path:
        result = replace(source, target)
        target.write_bytes(b"damaged\n")
        return result

    monkeypatch.setattr(Path, "replace", replace_then_damage)
    assert main(["apply", "--manifest", str(report["manifest"])]) == UNVERIFIED
    error = capsys.readouterr().err
    assert "does not read back" in error
    assert "sessions.journal.backups" in error


def test_a_write_that_does_not_read_back_is_removed_and_refused(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Backups, temporary files and plan files are read back before use."""
    read_bytes = Path.read_bytes

    def read_altered(path: Path) -> bytes:
        return read_bytes(path) + b"!"

    monkeypatch.setattr(Path, "read_bytes", read_altered)
    target = tmp_path / "copy.bak"
    with pytest.raises(JournalRefusedError, match="read-back differs"):
        session_journal._write_synced(target, b"data")
    assert not target.exists()


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        (b"", "no entry"),
        (A_PAUSE_NEW.replace("again", "\bagain").encode(), "control characters"),
        (b"## Pause by claude at soon in `C:/work/app`\n", "bad timestamp"),
        (b"## Pause by claude at 2026-11-09T09:00:00 in `C:/work/app`\n", "without offset"),
        (b"## Notes\n", "unrecognized heading"),
        (("note\n" + A_PAUSE_NEW).encode(), "text before the first entry"),
        (A_PAUSE_NEW.replace("test\n", "test\r").encode(), "carriage return"),
        (b"\xff" + A_PAUSE_NEW.encode(), "not UTF-8"),
    ],
)
def test_plan_refuses_a_broken_entry_file_before_writing_anything(
    journal: Path,
    home: Path,
    content: bytes,
    reason: str,
) -> None:
    """Empty, damaged or unrecognized entry files stop the plan at once."""
    entry = home / "entry.md"
    entry.write_bytes(content)
    with pytest.raises(JournalRefusedError, match=reason):
        plan_update(journal, add=[entry])
    assert journal.read_bytes() == LIVE.encode()
    assert not (journal.parent / "sessions.journal.plans").exists()


def test_plan_needs_an_entry_file_or_a_restore_source(journal: Path) -> None:
    """A plan without --add, --recover or --base has nothing to merge."""
    with pytest.raises(JournalRefusedError, match="nothing to plan"):
        plan_update(journal)


def test_restore_merges_an_older_copy_recovered_entries_and_the_live_ones(journal: Path, home: Path) -> None:
    """A damaged journal gets back its title and the latest entry of each kind."""
    base = _file(home, "base.md", PREAMBLE + "\n" + A_PAUSE_OLD + "\n" + B_PAUSE)
    journal.write_bytes(("\n" + A_PAUSE_NEW).encode())
    recovered = _file(home, "recovered.md", A_RESUME)
    apply_plan(Path(str(plan_update(journal, base=base, recover=[recovered])["manifest"])))
    text = journal.read_text(encoding="utf-8")
    assert text.startswith(PREAMBLE)
    assert _headings(text) == [_heading(B_PAUSE), _heading(A_RESUME), _heading(A_PAUSE_NEW)]


def test_a_missing_journal_is_created_under_the_template_title_in_a_private_folder(home: Path) -> None:
    """First use: the folder gets its .gitignore, the journal the template's title."""
    folder = home / ".llm-shared"
    report = plan_update(default_journal(), add=[_file(home, "entry.md", A_PAUSE_NEW)])
    assert (folder / ".gitignore").read_bytes() == b"*\n"
    assert not (folder / "sessions.journal.md").exists()
    assert apply_plan(Path(str(report["manifest"])))["backup"] is None
    text = (folder / "sessions.journal.md").read_text(encoding="utf-8")
    assert text.startswith("# Session journal\n\nPrivate index of the sessions paused and resumed")
    assert _headings(text) == [_heading(A_PAUSE_NEW)]


def test_an_entry_file_with_a_byte_order_mark_and_crlf_lines_is_stored_lf_only(journal: Path, home: Path) -> None:
    """An entry written by a Windows shell is accepted and normalized."""
    entry = home / "entry.md"
    entry.write_bytes(("\ufeff" + A_PAUSE_NEW.replace("\n", "\r\n")).encode())
    candidate = Path(str(plan_update(journal, add=[entry])["candidate"])).read_bytes()
    assert candidate.endswith(A_PAUSE_NEW.encode())
    assert b"\r" not in candidate


def test_two_different_entries_with_one_timestamp_are_refused(journal: Path, home: Path) -> None:
    """Entries of one kind for one checkout with equal timestamps cannot be ordered."""
    with pytest.raises(JournalRefusedError, match="share one timestamp"):
        _planned(journal, home, A_PAUSE.replace("app paused", "app paused twice"))


@pytest.mark.parametrize(
    ("live", "candidate", "reason"),
    [
        (LIVE, LIVE + "\n" + A_PAUSE_NEW, "two entries of one kind"),
        (LIVE, LIVE.replace("Private index.", "Another index."), "changes the journal preamble"),
        (LIVE, LIVE.replace("# Session journal", "# Notes"), "journal title"),
        (PREAMBLE + "\n" + A_PAUSE + "\n" + A_PAUSE, PREAMBLE + "\n" + A_PAUSE, "count mismatch"),
    ],
)
def test_validate_refuses_a_candidate_that_breaks_the_journal_shape(live: str, candidate: str, reason: str) -> None:
    """Duplicate keys, another preamble, no title or a wrong count are refused."""
    with pytest.raises(JournalRefusedError, match=reason):
        validate(live, candidate)


def test_plan_refuses_a_live_journal_without_its_title(journal: Path, home: Path) -> None:
    """Text before the entries that is not the title is never replaced silently."""
    journal.write_bytes(LIVE.replace("# Session journal", "Notes").encode())
    with pytest.raises(JournalRefusedError, match="no journal title"):
        _planned(journal, home)


def test_default_journal_prefers_userprofile_and_falls_back_to_home(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """USERPROFILE wins; HOME counts only where USERPROFILE is unset."""
    monkeypatch.setenv("HOME", str(tmp_path / "posix"))
    assert default_journal() == tmp_path / ".llm-shared" / "sessions.journal.md"
    monkeypatch.delenv("USERPROFILE")
    assert default_journal() == tmp_path / "posix" / ".llm-shared" / "sessions.journal.md"
    monkeypatch.delenv("HOME")
    with pytest.raises(JournalRefusedError, match="pass --journal"):
        default_journal()


def test_checkout_paths_compare_by_the_filesystem_rules() -> None:
    """Spellings of one folder share one key, case-folded where Windows folds case."""
    spellings = ["C:/work/app", "C:/work/./app", "C:/work/lib/../app"]
    if os.name == "nt":
        spellings.append("c:\\WORK\\App")
    assert len({checkout_key(path) for path in spellings}) == 1


def test_an_explicit_plan_folder_never_overwrites_an_earlier_plan(
    journal: Path,
    home: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A second plan into the same --out-dir is refused, keeping the first one."""
    entry = _file(home, "entry.md", A_PAUSE_NEW)
    command = ["plan", "--journal", str(journal), "--add", str(entry), "--out-dir", str(home / "plan")]
    assert main(command) == 0
    manifest = Path(json.loads(capsys.readouterr().out)["manifest"])
    first = manifest.read_bytes()
    assert main(command) == REFUSED
    assert manifest.read_bytes() == first


@pytest.mark.parametrize(
    ("manifest", "reason"),
    [
        ([], "not a JSON object"),
        ({"journal": 1}, "'journal' is missing or not a string"),
        ({"journal": "j", "candidate": "c", "journal_sha256": 5}, "'journal_sha256' is not a string or null"),
    ],
)
def test_apply_refuses_a_manifest_with_missing_or_mistyped_fields(home: Path, manifest: object, reason: str) -> None:
    """Only a JSON object with the planned string fields is applied."""
    with pytest.raises(JournalRefusedError, match=reason):
        apply_plan(_file(home, "manifest.json", json.dumps(manifest)))


def test_a_journal_without_entries_renders_as_its_preamble_and_one_newline() -> None:
    """No blank lines are left after the preamble when no entry follows."""
    assert render(Journal("# Session journal", ())) == "# Session journal\n"


def test_running_the_module_file_delegates_to_main(
    home: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Running the module file, as the launcher does, reports through main."""
    monkeypatch.setattr(sys, "path", [*sys.path])
    monkeypatch.setattr(sys, "argv", ["session_journal.py", "apply", "--manifest", str(home / "missing.json")])
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(session_journal.__file__, run_name="__main__")
    assert raised.value.code == REFUSED
    assert "refused, the journal is unchanged" in capsys.readouterr().err


# eof
