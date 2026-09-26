# Working files live in the artifact home

Every `a.*` working file lives in the project's review artifact home: `.reviews`
unless a versioned `.review-artifacts.ini` declares another `home`. The home
holds a `.gitignore` of exactly `*`, so nothing in it is ever committed. This
covers every file a tool writes and every file an agent creates: scratch
notes, helper scripts and their captured output, logs, JSON snapshots,
evidence folders, bundles, rendered review inputs, reports, and private notes.

Never create an `a.*` file or folder at the project root. The root keeps only
these six files, each a human-facing handoff point or a configuration read at
the root on purpose:

| Root file | Why it stays at the root |
| --- | --- |
| `a.ghog.log` | groundhog report the agent and the human read after each walk |
| `a.ghog.status` | groundhog run state, read through `ghog status` |
| `a.commit` | commit plan the human reviews and edits before the go-ahead |
| `a.prompt.txt` | next prompt `pw handoff` writes for the human to paste |
| `a.prompt_memory` | step memory `pw` reads to resolve the current topic |
| `a.sensitive.replacements.local.txt` | project rules the sensitive commit hooks read |

Any other root file needs the human's confirmation first; ask before creating
it, and name the reason it cannot live in the home.

## Names inside the artifact home

Name each file so its owner and lifetime are clear:

| Scope | Name | Deleted |
| --- | --- | --- |
| One plan step | `a.<slug>.step<x>.tmp.<what>[.<ext>]` | by `prepare-release` |
| One effort, no single step | `a.<slug>.tmp.<what>[.<ext>]` | by `prepare-release` |
| No effort | `a.tmp.<what>[.<ext>]` | by hand, once no longer needed |
| Step journal and handoff | see [`step-journal.md`](../instructions/step-journal.md) | never by the workflow |
| Private notes kept across efforts | `a.<what>.local.md` | never by the workflow |

A helper script and its captured output share one stem, such as
`a.<slug>.step3.tmp.probe.sh` and `a.<slug>.step3.tmp.probe.raw.txt`. A script
computes its output paths from the artifact home and never writes into the
project root, even when it runs there.

## Resolve the artifact home from tools and launchers

Python tools call `tools.artifact_home.artifact_path(root, name)`, which
prepares the home and moves a legacy root copy of the same name into it once.
Batch launchers call `bin\artifact_home.bat "<project-root>"`, which sets
`ARTIFACT_HOME`. A shell caller can print one path with
`python -m tools.artifact_home <project-root> <file-name>`.
