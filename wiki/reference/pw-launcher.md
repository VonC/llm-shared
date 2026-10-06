# pw launcher

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🔁 The prompt-workflow launcher: `bin\prompt_workflow.bat`, wrapping
`tools\prompt_workflow.py`, aliased `pw` in an interactive `cmd`. It
answers one question — what is the next step of this effort? — in three
workflow modes, and also exposes one stateless document locator.

## Invocation model

Other skills normally let the AI call this launcher as an internal handoff.
Humans call it directly to use the interactive menu, debug dispatch, or resume a
specific known phase without restarting the parent workflow.

## 🧠 Shared core of every mode

All modes resolve the topic from the branch and the `docs\` tree (locked
per branch in `a.prompt_memory`), read the same workflow state (which of
draft, requirement, design, plan, validation exist; open questions or
settled decision table; which plan steps are done), and know the host:
`CLAUDECODE` emits `/skill`, while `CODEX_THREAD_ID` emits the installed
plugin form `$llm-shared:skill`.

The menu-less `pw skill` and `pw handoff` modes call one shared topic resolver.
Normal resolution uses relevant changed drafts and branch memory. If it finds
no topic, the shared resolver has a safe fallback for a requirement split from
an unchanged collection draft:

1. normalize only the branch leaf, treating `-` and `_` as equivalent,
2. require exactly one feature-request or issue filename with that version and
   normalized slug,
3. use exactly one direct same-version, same-slug draft when present,
4. otherwise require exactly one same-version draft marked
   `- Draft role: umbrella` whose canonical requirement table contains the
   complete normalized slug.

Missing and ambiguous relationships return no topic. A same-version draft that
does not mention the item is never borrowed as context, and the umbrella draft
is not renamed to the item slug.

A clean umbrella branch has no changed draft or item requirement to feed those
routes. In that case, bare `pw skill` matches the normalized branch leaf to
exactly one canonical umbrella carrying a nonempty collection table. It then
returns the first valid pending row through `process-draft ... based on
<slug>`. No match or more than one match remains not applicable rather than
selecting an unrelated umbrella.

When a caller already knows a version, slug, and document type, it does not
need branch state, a draft path, or `a.prompt_memory`. The stateless form
`pw document <version> <slug> <type>` searches recognized directories across
the five supported layouts for that version and prints the unique
repository-relative path.

The collection checkpoint uses the same canonical table more strictly.
`pw skill --after-merge <umbrella-draft>` reads rows in numeric order. A
`completed` row must name an existing requirement and a validation plan whose
first non-title line is exactly `Yes, it is implemented.`. A `pending` row with
complete validation evidence is stale and fails closed. The first valid pending
row starts or resumes its workflow; only an exhausted table emits
`prepare-release`.

## 🎛️ The three modes side by side

| Mode | Step chosen by | Emits | Channel |
| --- | --- | --- | --- |
| `pw` | a human, from a menu | a full next-step prompt | `a.prompt.txt` + clipboard + `a.prompt_memory` |
| `pw handoff <task> <x>` | the caller (the step is given) | a full, assembled cycle prompt | `a.prompt.txt` + clipboard + `a.prompt_memory` |
| `pw skill [name] [--after-write role] [--after-merge umbrella]` | disk state, forced name, writer event, or collection checkpoint | one bare command line | stdout |

## 📍 Where the topic stands

`pw progress` resolves the topic like bare `pw skill` and prints the same next
command, preceded by where the topic stands and how far along it is. The next
command may be rendered for the topic's requestor, as described below:

```text
branch    shared-wait-service
topic     v0.13.0 shared-wait-service
umbrella  no_polling, topic 1/9: Run one durable monitoring service (0/9 topics completed)
phase     implementation (5/5)
step      6/8: Implement delivery, cancellation and consumption settlement (6/8 verified)
review    round 2 for step 6: wait for the human choice: Commit, or Rework and review again
next      /code-review-requestor on docs/v0.13.0/plan.v0.13.0.shared-wait-service.md step 6 (claude)
```

Positions are counted in document order, not read from ids. The step list is
the validation plan's `Analysis of Step <id>` headings, so a plan listing `0`,
`1`, `2`, `3.1`, `3.2` reports its fifth step as `step 3.2 (5/5)`; an id equal
to its position prints compactly, as `step 6/8`. The phases are `draft`,
`requirement`, `design`, `plan`, and `implementation`. Before the
implementation phase the step line only counts planned and verified steps.

The umbrella comes from the child draft's `- Umbrella:` line, from the umbrella
draft a requirement resolved through, or from the one same-version umbrella
whose status table lists the slug. Otherwise the line reads
`none, standalone topic`. On the umbrella integration branch, the report shows
the completed rows and the next pending topic instead of a phase and a step.

The `review` lines condense the repository review status that `rvw_status`
(alias `rwst`) reports in full: `no review in progress`, or one line per active
exchange with its round, the reviewed step (code) or document type
(specification), and whose move it is, such as
`wait for code reviewer (codex) response` or
`wait for spec requestor (claude) update`. The role nature comes from the
exchange's recorded evidence and reads `unrecorded` when none exists. An
exchange of another topic names its slug. Damaged candidates and an
unavailable status point back to `rwst`.

When the topic's requestor, the code or document writer, is clearly known, the
`next` command is rendered for that host and names it at the end of the line:
`/` for Claude, `$llm-shared:` for Codex, then `(claude)` or `(codex)`:

```text
next      $llm-shared:implement-step on docs/plan.v10.0.0.dex-navigation.md step 3 (codex)
```

The requestor comes from the topic's active exchanges when they all record the
same Claude or Codex requestor. Once an exchange completes, `rwst` reports
`no review in progress`, so the report then reads the topic's committed review
transcripts, `review.<type>.<version>.<slug>.md`, and takes the requestor of
the most recently recorded entry. An unrecorded or disagreeing requestor, or no
transcript, leaves the command as bare `pw skill` prints it. A reviewer handoff
(`code-reviewer`, `spec-reviewer`) is also left as is, since the requestor does
not run it.

An exchange in an abnormal state adds one `resume` line after the `review`
lines: a one-line prompt to paste so the review cycle can restart. No review in
progress, or reviews waiting normally for a counterpart, the human choice, or
the authorized `Commit` or `Consolidate`, add no such line.

```text
review    round 2 for step 3: resolve-escalation: Resolve the escalation before continuing.
resume    /code-review-requestor on docs/plan.v10.0.0.dex-navigation.md step 3: escalated, show me the escalation reason, then ask me to choose reclaim --force, resolve, or archive to restart the cycle (claude)
```

The prompt calls the role instruction that recovers the exchange, with the
reviewed document, the step, and the umbrella when there is one:

| State | Pasted to | Asks the role to |
| --- | --- | --- |
| `abandoned-*` | the role `rwst` names to continue | reclaim the abandoned round and continue it |
| interrupted or repair pending | the role `rwst` names to continue | rerun the interrupted operation with the same content |
| `escalated` | the requestor | show the reason and ask for `reclaim --force`, `resolve`, or `archive` |
| `inconsistent` | the requestor | explain the evidence and propose a repair, editing nothing |

The escalation choice stays with the human, as the recovery commands require.
The prompt is not a `review-resume` call: that inspection blocks escalated,
interrupted, and inconsistent exchanges. Its prefix and trailing name come from
the target role's recorded nature: `/` and `(claude)`, or `$llm-shared:` and
`(codex)`. An unrecorded nature uses the detected host prefix and ends with the
role, `(requestor)` or `(reviewer)`, instead.

During the coding steps, a `journal` line follows the `step` line once the
code writer has created the current step's private journal:

```text
step      3/8: Wire the navigation index (2/8 verified)
journal   C:\src\app\.reviews\a.dex-navigation.step3.journal.md
```

`pw progress` reads the documents and Git without changing them. The review
status collection runs the same bounded migration preflight as `rwst`, which
only moves review artifacts of an old layout into the artifact home. The
command exits `0` with a resolved topic, and `3` with `topic none resolved`
otherwise.

## Effort test scope

`pw scope` prints one explicit ghog selector. `pw scope day --full=speed`
prints a complete command such as `ghog day --full=speed --group=parser`;
it does not execute tests. The requirement or issue header, before its first
level-two heading, is the sole declaration:

```markdown
- Test group: parser
```

Use `whole suite` to select the whole suite. A missing line or requirement
defaults to whole suite. Empty, duplicate, invalid, or unresolved declarations
fail closed. Draft metadata and `GHOG_GROUP` do not select effort scope.
Named groups must resolve through the project-root `.ghog-groups`.

`pw scope` rejects caller-supplied `--group`, `--whole-suite`, or `--scope-file`
with exit 2. An unresolved topic exits 3; valid output exits 0. `pw progress`
shows the current scope and its provenance, plus the validated bound scope of
the current code-review round. A changed requirement is shown as a pending
change; missing captures read `bound missing` and never imply proof.

## 📓 Private step journal and handoff

```text
pw step-journal 3
```

The code writer runs this command as the first action of a plan step, as
`instructions/step-journal.md` requires. It creates the review artifact home
with its `*` ignore file when missing, then prints whether the step starts (no
journal yet) or resumes (journal present), with the exact note paths:

```text
state     start
journal   C:\src\app\.reviews\a.dex-navigation.step3.journal.md
handoff   C:\src\app\.reviews\a.dex-navigation.step3.handoff.md
tmp       C:\src\app\.reviews\a.dex-navigation.step3.tmp.*
```

The journal opens with the step's objectives, main goal, and plan and umbrella
context, then keeps an append-only milestone log. The handoff holds the
verified state, next actions, decisions, and record tables a new session
resumes from. Every other file of the step is a `tmp` file in the same home,
which `prepare-release` deletes. The command exits `3` without a resolved
topic and `2` for an invalid step id or artifact home.

## 🔎 Stateless document lookup

```text
pw document v10.0.0 route-cleanup design
```

The three selector values are sufficient. Supported types are `draft`,
`requirement`, `feature-request`, `issue`, `design`, `plan`, and
`validation-plan`. `requirement` resolves either a feature request or an issue.
Slug hyphens and underscores are equivalent.

The lookup checks `docs/`, `docs/vX.Y/`, `docs/vX.Y.Z/`,
`docs/vX.Y/vX.Y.Z/`, and qualifying `docs/vX.Y.Z/<slug>/` directories for the
supplied full version. See [effort-directory recognition](artifact-files.md#effort-directory-recognition)
for the matching immediate-file requirement. It prints nothing and exits `3`
when no document exists. Multiple exact matches are a fatal error, including
copies in both a version directory and its qualifying slug child. Canonical
preference and newest-file selection do not apply to this stateless command.

## Workflow document selection

Workflow selection validates the canonical draft path's parent as a recognized
directory before choosing any document. The draft file itself need not exist.
An unrecognized parent is fatal; selection does not broaden the search to
compensate for it.

For each requested role, selection uses these rules:

| Matches | Result |
| --- | --- |
| One or more in the canonical parent | Select the newest local file; equal timestamps retain existing candidate order. Other directories cannot override it. |
| None locally, one across other recognized directories | Select that unique fallback. |
| None locally or elsewhere | Report the role absent. |
| None locally, several across other recognized directories | Fatal ambiguity listing the role, version, slug, canonical parent, and all competing paths. |

Fallback searches all other recognized directories across supported layouts.
Matching preserves the requested role and version, hyphen/underscore
equivalence, and existing workflow subtopic matching. Exact `pw document`
lookup does not include subtopics. Directory eligibility is rechecked on every
call; local success avoids fallback document matching, while directory
eligibility checks can still inspect other folders.

Post-commit discovery uses the validation plan's parent as the location of a
synthesized draft path. A local or unique fallback ordinary plan includes the
topic; no ordinary plan skips it. Competing fallback plans and invalid parents
propagate a fatal CLI error with exit code `2`, without a success command or
new success prompt. Existing validation state determines the continuation for
an included topic.

## 🤝 pw handoff tasks

| Call | When | Prompt written |
| --- | --- | --- |
| `pw handoff check <x>` | after `/implement-step <x>` or `/implement-missing-step <x>` ends green | the `implementation-check.md` prompt for step `<x>` |
| `pw handoff after-check <x>` | after `/implementation-check <x>` records its verdict | routed: `implement-missing-step.md` on `No`, `group-commits-msg.md` (`git add -A` form) on `Yes` |

`after-check` is neutral on purpose: `pw` reads the `Analysis of Step x`
status line the check wrote, so the caller cannot pick the wrong branch.

## 🗂️ What pw skill derives from disk

| State on disk | Printed command |
| --- | --- |
| fresh draft, no requirement | `/process-draft on docs\draft...md` |
| doc still carrying `## Open questions` | `/consolidate-then-review-ask-questions on ...` |
| current doc fresh: no open questions, no consolidated decisions | `/review-ask-questions on ...` |
| settled requirement | `/write-design` |
| settled design | `/write-plans` |
| settled plan, uncommitted validation work | `/implement-step <x>` |
| settled plan, final step committed | `/prepare-release` |

"Settled" means consolidated, not merely titled: the document must carry a
decisions section (`Requirement clarifications`, `Design decisions`, or
`Implementation decisions`) holding at least one row opening with a question id
(`| Qxx`) or the "No open questions" row a no-question review writes. A
decisions heading alone does not count.

Bare `pw skill` treats a complete settled marker as state and advances. Writers
therefore do not use bare inference: `pw skill --after-write
requirement|design|plan` names the artifact just created and always prints its
`/review-ask-questions`, even if its text already resembles a settled document.
The `<x>` of `/implement-step` comes from the validation plan's own step list:
the last verified step, or the plan's first step when none is verified, which
is not always `1` (a plan may open on a step 0). Whether the settled-plan
command is run at once (the default) or shown and held (`stop here` in the
consolidation invocation, or an explicit human instruction) is decided by the
skill instructions, not by `pw`.

## 🚩 Flags and special forms

| Form | Effect |
| --- | --- |
| `pw skill --after-write requirement\|design\|plan` | reviews the named artifact just written, ignoring settled-looking markers; prints nothing and exits not-applicable when it is absent |
| `pw skill --after-commit <x>` | told the plan step the pending commit completes, prints the contextual next action (next `/implement-step`, `/prepare-release`, or nothing) — read-only, used to build the commit-gate labels |
| `pw skill --after-merge <umbrella-draft>` | verifies the ordered umbrella status table; emits `process-draft ... based on <slug>`, resumes an existing pending effort, or emits `prepare-release` only when all rows are complete |
| `pw skill --host claude\|codex` | forces the command prefix |
| `pw skill <skill-name>` | prints a specific earlier phase's command, to re-run it by hand |
| `pw document <version> <slug> <type>` | prints the unique document path without branch or memory resolution |
| `pw progress [--host claude\|codex]` | prints branch, topic, umbrella position or standalone, phase, step position, and condensed review status above the bare next command |
| `pw --pick` | reopens the topic menu when the branch lock is wrong |
| `pw scope [ghog arguments]` | prints the requirement's explicit scope selector, or a completed ghog command |
| `--root`, `--debug` | shared flags, accepted before or after the subcommand |

## 🚦 Exit and error behavior

Skill mode exits `3` with empty stdout when no topic or requested artifact is
applicable, so a caller cannot mistake an error note for a command. The tool
exits `2` on fatal errors (`EXIT_FATAL`). A launcher error naming `No python_3*
directory found in "\venvs"` means a stale copy of
`prompt_workflow.bat` outside the real checkout.

Related: [One launcher, three modes](../explanation/one-launcher-three-modes.md),
[Run pw from any shell](../how-to/run-pw-from-any-shell.md), and
[Artifact files and naming conventions](artifact-files.md).
