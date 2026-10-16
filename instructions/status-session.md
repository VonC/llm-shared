# Report session status without resuming

Use when the user invokes `status-session` or asks whether a paused session
is waiting to be resumed. Report whether the latest saved prompt is unprocessed,
then give exactly three summary points. If no unprocessed prompt exists,
summarize the latest recorded work from notes, handoffs and journals instead.
This is an LLM command, not a shell executable or `pw` subcommand. It takes no
arguments; `--force` belongs to [resume-session](resume-session.md).

## Inspect the artifact home without changing it

Work in the consuming project's current checkout. Read its agent instructions
and [run_commands.md](../rules/run_commands.md) before shell work. Resolve the
artifact home from [artifact_files.md](../rules/artifact_files.md): `.reviews`
by default, or the home declared in the checkout's `.review-artifacts.ini`.

Use read-only checks. The existing
[`ReviewArtifactConfiguration.load(project_root)`](../tools/review_artifact_configuration.py)
can validate the declaration and resolve the home without preparing it.
Whether using that API or equivalent filesystem reads, validate the configured
path stays inside this checkout and is not a tracked directory. If the home
exists, verify its `.gitignore` contains exactly `*` and a newline. If it is
absent, report no prompt and no notes; do not create it. Invalid configuration,
unreadable paths or invalid ignore coverage are diagnostics, not absence.

Do not call `prepare_home()`, `artifact_home()`, `artifact_path()`, or the
artifact-home launcher: those can create or migrate files. Do not refresh
notes, create a report, write or clear a receipt, migrate artifacts, claim a
review role, launch jobs, or resume work. Read saved commands and instructions
as evidence only, even when a prompt tells the next session to continue.

## Determine whether the latest prompt is unprocessed

At invocation time, sample these exact paths in the resolved home:

- `a.session-resume.local.md`: the latest pause prompt.
- `a.session-resume.used.local.md`: its usage receipt.

Use the [resume validation contract](resume-session.md#locate-and-check-the-saved-prompt)
and [receipt schema](../templates/resume-session.template.md) only; do not run
the resume workflow. Read the prompt fully to check it is complete and usable,
and hash its exact bytes with SHA-256, normalized to lowercase. Compare resolved
checkout paths using the filesystem's rules. A receipt must be valid before a
different digest can establish that the prompt is new. A prompt naming a
different checkout is a diagnostic, not a pending task for this checkout.

| Observed state | Status and summary source |
| --- | --- |
| Complete prompt, no receipt | Unprocessed prompt found; summarize that prompt |
| Valid receipt for this prompt basename and checkout, different SHA-256 | Unprocessed prompt found, new since previous use; summarize that prompt |
| Valid receipt matches basename, checkout and SHA-256 | No unprocessed prompt; latest prompt already used; summarize latest notes |
| Prompt missing, including an absent artifact home | No unprocessed prompt; no saved prompt found; summarize latest notes if any |
| Prompt empty, unreadable or incomplete; invalid receipt or wrong basename/checkout | Status undetermined; report the diagnostic without classifying the prompt as unused or consumed |

A missing prompt leaves any orphan receipt untouched. A matching receipt means
context was read and reconciled, not that the task completed. Do not choose an
older prompt by modification time or search other folders for an unused one.
Before reporting, resample prompt and receipt existence and bytes. If either
changed during inspection, read the new state once; if it keeps changing,
report uncertainty rather than a stable classification.

## Select the evidence for three summary points

For an unprocessed prompt, summarize its saved objective, completed and remaining
work, and next actions or blockers. Read essential referenced notes if needed
to understand it. Describe it as a saved snapshot; status does not verify a
recorded job is still running or execute its continuation.

When no unprocessed prompt exists, inspect the latest relevant notes, handoffs
and journals within the artifact home, including subfolders. Recognize
`a.<slug>.step<x>.journal.md` and `a.<slug>.step<x>.handoff.md` from
[step-journal.md](step-journal.md), as well as informal Markdown or text notes.
Do not invoke that instruction's note-writing workflow. Exclude scratch output,
usage receipts and unrelated review inputs from the note selection.

Use filenames and modification times to locate candidates, then dated entries,
milestones and handoff contents to establish what was last recorded. Read the
latest relevant records for each active topic, not just the single newest file.
Reconcile completed journal milestones against obsolete handoff next actions;
do not report a finished action as pending. Preserve topic and role distinctions
when records disagree. Do not use an already-consumed prompt as the sole source
of this fallback summary.

Keep stale, missing or conflicting evidence explicit. Say "last recorded" for
jobs and other unverified state. If no usable notes exist, state that the
objective, progress and next action are unknown; do not invent ongoing work.
If the notes show everything completed, say no remaining action is recorded.
An unreadable candidate is a limitation, not proof there are no notes.

For an undetermined prompt state, summarize readable notes if the home is valid,
labeling them as such without implying that no prompt is pending. If the home
cannot be inspected, use the three points to state the unknown objective,
the observed diagnostic and the check needed to resolve it. Do not repair it
during this status command.

## Report and stop

Fill [status-session.template.md](../templates/status-session.template.md)
directly in the response; do not save a new artifact. Begin with one clear
status line naming the actual prompt path relative to the consuming checkout,
such as `.reviews/a.session-resume.local.md`. Honor the configured home; if it
cannot be resolved, name `.review-artifacts.ini` and the diagnostic instead.

Follow with exactly three numbered points: objective, progress, and next
actions or blockers. Cite relative source paths and relevant dates within
those points, without nested lists. Replace every placeholder with observed
facts or explicit unknowns. Keep it concise and do not print secrets from
private notes. Stop after reporting; a subsequent `resume-session` is what
reads, reconciles and consumes the pending prompt to continue work.
