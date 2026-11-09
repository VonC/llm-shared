# Session journal command reference

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

🤖 `bin\session_journal.bat` runs `tools\session_journal.py` with llm-shared's
own Python. It is the only writer of the private session journal that
pause-session and resume-session keep and list-session reads:
`%USERPROFILE%\.llm-shared\sessions.journal.md`, or
`$HOME/.llm-shared/sessions.journal.md` where `USERPROFILE` is unset. The
rules for the journal itself are in
[pause-session](../../instructions/pause-session.md#session-journal-across-checkouts).

## Invocation model

pause-session and resume-session run it to add their entry. Run it directly
only to restore a damaged journal from an older copy. A plan and its apply are
always two separate shell calls, never chained with each other or with the
command that wrote the entry file, so a failed step can never feed the next
one.

## ⌨️ Commands

| Command | Effect |
| --- | --- |
| `session_journal.bat plan --add FILE [--add FILE ...]` | Re-read the journal, append the entries of each file after the live ones, check the result, and write it with its manifest to a new plan folder; the journal is only read |
| `session_journal.bat plan --base FILE [--recover FILE ...]` | Restore: merge an older full copy, and files of older entries put back before the live ones |
| `session_journal.bat apply --manifest FILE` | Replace the journal with the planned candidate once every check passes again |

`plan` also takes `--journal FILE` (default: the path above) and
`--out-dir DIR` (default: a new folder under `sessions.journal.plans` beside
the journal). An entry file holds one or more entries in the form of the
[journal template](../../templates/session-journal.template.md) and nothing
before them; a byte order mark and CRLF line ends are accepted and dropped.
Where the Windows launcher does not apply, run
`python3 -I <LLM_SHARED_DIR>/tools/session_journal.py` with the same
arguments.

## 🔢 Exit codes of plan and apply

| Exit | Meaning |
| --- | --- |
| `0` | Done; a JSON report on stdout |
| `1` | Launcher setup error: no llm-shared Python environment |
| `2` | Refused, reason on stderr; the journal is unchanged |
| `3` | The journal was replaced but does not read back as the candidate; stderr names the backup that holds the previous content |

## 🛡️ Checks before any write

- Per checkout and per kind (pause, resume), only the entry with the latest
  timestamp survives. Checkout paths compare by the filesystem's rules.
- Every other entry keeps its exact text, and the new journal counts exactly
  the entries before, minus the removed ones, plus the added ones.
- An entry is removed only when a newer entry of the same kind for the same
  checkout replaces it. Two different entries of one kind for one checkout
  with the same timestamp are refused.
- The text before the first entry stays as it is. A missing journal gets the
  template's title and first paragraph, and a missing folder a `.gitignore`
  holding `*`.
- The journal is strict UTF-8 with LF line ends, without control characters
  other than tabs, and every level-two heading is an entry heading.

`apply` runs the same checks again on the bytes it reads. It also refuses when
the journal no longer has the SHA-256 the plan read, when the candidate no
longer has the SHA-256 the plan recorded, or when the change no longer matches
the planned report.

## 📄 Plan report fields

| Field | Meaning |
| --- | --- |
| `manifest` | The path to pass to `apply --manifest` |
| `journal`, `journal_sha256` | The journal path and the SHA-256 the plan read, null for a missing journal |
| `candidate`, `candidate_sha256` | The planned journal and its SHA-256 |
| `before_count`, `after_count` | Entry counts before and after the change |
| `removed`, `added` | Headings of the entries the change removes and adds |
| `superseded` | Headings of requested entries left out because a newer entry of the same kind exists |

`apply` prints `applied` (the journal path), `backup` (null when there was no
journal yet), the same counts and headings, `pruned_backups` (the number of
older backups deleted) and `warnings` (empty unless pruning failed).

## 🗂️ Files beside the journal

| Path | Content | Removed |
| --- | --- | --- |
| `sessions.journal.backups\sessions.journal.md.<time>-<random>.bak` | The previous journal, one copy per apply | By a successful apply, beyond the newest 50 |
| `sessions.journal.plans\<time>-<random>\` | The candidate and the manifest of one plan | By a successful apply |
| `sessions.journal.md.<time>-<random>.tmp` | The new content before the atomic replace | By apply, whatever its outcome |

Only after the journal is replaced and read back does `apply` prune the
backups: it orders them by the time in their name and keeps the newest 50,
always including the one it just wrote. A file in that folder whose name does
not follow the pattern above is never deleted. A pruning failure leaves the
apply successful, with exit `0` and the reason in `warnings`.

A leftover `.tmp` file comes from an interrupted apply and can be deleted.
Every file the tool writes is created as a new file, so a second plan never
overwrites an earlier one.
