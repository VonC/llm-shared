# Keep a private journal and handoff for each plan step

The code writer, the session that implements a plan step and then requests
its code review, keeps two private notes for that step. They let a crashed,
compacted, or new session resume from files instead of memory, and they hold
the details that must not reach tracked files.

This instruction applies from the first action of
[`implement-step.md`](implement-step.md) until the step is committed: the
implementation, the implementation check, `group-commits-msg`, every code
review round of [`code-review-requestor.md`](code-review-requestor.md), and
the commit. Resolve `<LLM_SHARED_DIR>` from this canonical file as described
in [`run_commands.md`](../rules/run_commands.md).

## Step note names and location

Every file of a step lives in the review artifact home: `.reviews` unless a
versioned `.review-artifacts.ini` declares another `home`. The home holds a
`.gitignore` of exactly `*`, so nothing in it is ever committed. The home
exists even when review mode is off, because the command below creates it.

| File | Name in the artifact home | Kept until |
| --- | --- | --- |
| Journal | `a.<slug>.step<x>.journal.md` | never deleted by the workflow |
| Handoff | `a.<slug>.step<x>.handoff.md` | never deleted by the workflow |
| Temporary file or folder | `a.<slug>.step<x>.tmp.<what>[.<ext>]` | `prepare-release` of the effort |

`<slug>` is the topic slug of the plan file name, `plan.vX.Y.Z.<slug>.md`.
`<x>` is the plan step id exactly as the plan writes it: `3`, `3b`, `4A`, or
`3.2`. Never invent an abbreviation for the slug: the names must be the ones
the command prints.

## Detect whether the step starts or resumes

As the first action of the step, before reading any other document, run from
the project root:

```powershell
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" step-journal <x>
```

The command creates the artifact home with its `*` ignore file when it is
missing, then prints four aligned lines:

```text
state     start
journal   C:\...\.reviews\a.dex-navigation.step3.journal.md
handoff   C:\...\.reviews\a.dex-navigation.step3.handoff.md
tmp       C:\...\.reviews\a.dex-navigation.step3.tmp.*
```

`state start` means the journal does not exist yet: this session starts the
step. `state resume` means it exists: an earlier session worked on the step.
Exit `3` means no workflow topic resolved, and exit `2` reports an invalid
step id or artifact home; stop and report the diagnostic in both cases. State
the result in one line before acting on it, such as
`step-journal: resume (a.dex-navigation.step3.journal.md)`.

Never decide start or resume from memory, from a directory listing, or from
`git status`: the home is ignored, so `git status` never shows these files.

## Start a step by writing its notes first

When the state is `start`, read the plan step, its validation plan entry, the
design, and the requirement as `implement-step` asks, and run
`pw progress` for the umbrella position. Then, before writing any code:

1. Create the journal from
   [`step-journal.template.md`](../templates/step-journal.template.md). Fill
   its objectives, main goal, and context sections: the plan path and the
   step position and title, the validation plan, design, and requirement
   paths, the umbrella draft and this topic's row (or `none, standalone
   topic`), the earlier steps this one relies on, and the next step. End it
   with the first log line, `start`.
2. Create the handoff from
   [`step-handoff.template.md`](../templates/step-handoff.template.md), with
   the first next actions of the implementation.

The objectives, goal, and context are written once. Correct them only when
they are wrong, and log the correction.

## Resume a step by reading its notes first

When the state is `resume`, read before touching any file:

1. The journal, in full: it is the authoritative record of what happened.
2. The handoff, in full.
3. Only the private references the next action needs.

Then check the disk against the handoff's verified state: `git status`, the
last commit, `pw progress`, and any run the next action depends on. When they
differ, trust the disk, append a log line that records the difference, and
update the handoff. Continue from the handoff's next actions. Never restart
the step from scratch and never rebuild its state from memory.

## Journal milestone log

The log is append-only. Add one line each time a stage changes:

```text
- <YYYY-MM-DDTHH:MM:SS+HH:MM> | <kind> | <what happened, with its evidence>
```

Use local system time with its numeric offset. `<kind>` is one of:

| Kind | When to log it |
| --- | --- |
| `start`, `resume` | the session starts or resumes the step |
| `decision` | a choice between options, with its reason |
| `gate` | a `ghog day` walk, an implementation check, or another pass or fail check ends |
| `run` | an external run starts: a build, a host run, a probe |
| `result` | that run ends, with its outcome |
| `capture` | evidence is saved, with its folder |
| `review` | a request is published, an answer consumed, or a human choice made |
| `commit`, `push` | a commit is created or pushed, with its hash |
| `blocker` | something stops the step, with what would unblock it |
| `pause` | the session ends or hands off before the step is committed |

For example:

```text
- 2026-09-26T12:54:03+02:00 | gate | ghog day exit 0 (a.ghog.log)
- 2026-09-26T13:10:41+02:00 | review | round 2 request published, waiting for the reviewer
```

Never edit or delete a past line. Correct a wrong line with a new line that
names it. Log a stage change once, not every poll of a wait.

## Handoff upkeep between milestones

Rewrite the handoff's verified state and next actions whenever a milestone
changes them, and always before: the `pw handoff check` call, publishing a
review request, the commit gate, and a `pause`. Append to its decisions
section and never rewrite it. Keep record tables there when the step repeats
runs, probes, or builds, one row per run with its revisions, command, result,
and evidence folder. List in its private references every file the next
session needs, including earlier steps' handoffs and temporary files.

## Temporary step files in the artifact home

Name every other file or folder the step creates
`a.<slug>.step<x>.tmp.<what>[.<ext>]` in the artifact home: scripts, logs,
captures, bundles, API snapshots, and evidence folders such as
`a.<slug>.step<x>.tmp.build217/`. A script derives its output paths from the
artifact home and never writes into the project root.

Never create a step file at the project root. The only root files are the
ones a tool writes there itself: `a.commit`, `a.ghog.log`, `a.ghog.status`,
`a.prompt.txt`, and `a.prompt_memory`. Review exchange inputs keep the names
[`review-requestor.md`](review-requestor.md) and the specialized role ask for,
in the same home.

A temporary file a later step still needs stays in place: that later step
lists it in its handoff's private references. `prepare-release` deletes the
effort's `a.<slug>.step*.tmp.*` files once every step is committed.

## Privacy of step notes and reviewer access

The notes may hold private details: host, service, job, and path names,
private projects, credentials locations, raw evidence. Never copy such a
detail into a tracked file, a commit message, a review request, or a review
answer. Those carry sanitized outcomes only.

The reviewer may read the notes, read-only, for context: name the journal and
handoff paths in each review request under a `Writer notes` line. The
reviewer never writes, renames, or deletes them, and never quotes a private
detail from them in its answer.

## Lifecycle of step notes

The journal and handoff stay after the step commit: later steps and later
resumes read them. The workflow never deletes them, and they are never
committed. `pw progress` prints a `journal` line with the full journal path
while a coding step has one.

## Promote lasting decisions out of the step notes

The notes are never versioned, so they can never be the only record of
something that matters beyond the step. When a decision or finding outlives
the step, such as a design choice, a constraint a later step must respect, a
changed acceptance criterion, or a limitation of the delivered code, write it
in sanitized form into the tracked document that owns it: the design, the
plan or validation plan, the requirement, or the commit message. Then log a
`decision` line in the journal naming the tracked file that now holds it. A
private detail that the tracked text cannot carry stays in the notes, and the
tracked text says only that the detail exists privately.
