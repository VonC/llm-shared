# Design v0.9.0 -- Automated workflow handoffs

Reference feature-request: [feature-request.v0.9.0.handoff_automation.md](feature-request.v0.9.0.handoff_automation.md)

---

## Context for v0.9.0 handoff automation

The feature-request asks for two linked changes. First, the instruction bodies
that should chain to the next step must do so on their own, calling the next
skill with the right document name and not waiting for a user review or
go-ahead. Second, `pw` (prompt_workflow) gains a `pw skill` subcommand that returns
the bare next-step command the LLM runs, instead of the user-facing prompt it writes
today. The eight review clarifications (Q01 to Q08, recorded in the
feature-request) settle the scope; this design turns them into target behavior,
confirmed facts, and the major design areas, without dropping to a file-by-file
plan.

## Scope for v0.9.0 handoff automation

The v0.9.0 outcomes are:

1. The writing and consolidation instructions chain automatically: `write-requirement`, `write-design`, and `write-plans` call `/review-ask-questions` on the document just written, and `consolidate-then-review-ask-questions` calls the next workflow instruction once the document is settled, all without a go-ahead.
2. `pw skill` returns the bare next-step command (or commands), host-prefixed and free of the user-facing wrapper, derived from the documents on disk.
3. The two splitting instructions (`process-draft`, `split-and-define`) and the review instruction (`review-ask-questions`) present a multi-choice list or a next-step hint, each carrying the real document name.

Everything else is either supporting design context for those outcomes or explicitly deferred.

### In scope for v0.9.0 handoff automation

- Automated `## Handoff` sections on `write-requirement.md`, `write-design.md`, `write-plans.md`, and `consolidate-then-review-ask-questions.md`, mirroring the existing `implement-step.md` handoff shape.
- A next-step hint on `review-ask-questions.md` and multi-choice lists on `process-draft.md` and `split-and-define.md`, each closing with an LLM-supplied "Type something else" entry.
- A `pw skill` output mode: bare command strings, host-aware prefix with an override, single or multi-line, derived from on-disk state.
- The "stop here" opt-out (Q01) honored at the writing skill, the consolidate trigger (Q03), the artifact precedence (Q04), and the consolidated-versus-open-questions split that decides review against advance.

### Deferred from v0.9.0 handoff automation to v0.10.0 and beyond

- The reliable mechanism that renders the review hint as a gray, Tab-completable prompt on Claude and on Codex (Q06): plain text is the committed baseline, the gray affordance is a later study.
- Any change to the interactive `pw` menu or to the existing `pw handoff` implement cycle beyond what the `pw skill` mode reuses.

---

## Confirmed technical facts for v0.9.0 handoff automation

These facts were confirmed by inspecting the current codebase before writing this design.

**The pw hub already routes a menu-less subcommand**: `tools/prompt_workflow.py` builds an argparse parser with a shared parent (`--root`, `--debug`) that parses on either side of the subcommand, a top-level `--pick`, and a `handoff` subcommand (`pw handoff <task> <x>`); `main()` dispatches to `run_handoff` or the interactive `run`. A new `pw skill` subcommand attaches at this hub, beside `handoff`.

**The current next-step message is a three-part prompt**: `steps.build_prompt` assembles a header (`Follow the instructions from {prefix}/{instruction} and do the following:`), the per-step body, and a `Context: this is about {version} {slug}. Read {...}.` line; `deliver_prompt` writes it to `a.prompt.txt`, copies it to the clipboard, and records the step in `a.prompt_memory`. The `pw skill` mode returns a bare command in place of this three-part text and its delivery side effects.

**The workflow state is already derived from on-disk documents**: `steps.compute_state` calls `docs.select_document` for the requirement, design, plan, and validation-plan roles (scanning `docs/` and `docs/vX.Y.Z/`), and `docs.has_open_questions` detects the `## Open questions` marker. `steps.next_step_numbers` walks requirement, then design, then plan, routing by presence and the open-questions flag, which already realizes the "most advanced artifact wins" precedence (Q04).

**Topics come from the branch drafts**: `docs.relevant_drafts` reads the drafts changed or committed on the branch, `parse_draft_name` parses `draft.vX.Y.Z.<slug>.md`, and slug matching folds `-` and `_`, so a draft slug resolves the hyphenated or underscored documents and the reverse.

**A non-interactive handoff and plan parsing already exist**: `tools/prompt_workflow_handoff.py` resolves a topic without a menu and reads a named plan step from the validation plan (`find_plan_step` over `plan.parse_validation_steps`), and `plan.derive_x` picks the current step. The consolidate-to-implement routing reuses this to name the first plan step.

**The handoff prose pattern is set by implement-step**: `instructions/implement-step.md` carries a `## Handoff` section that runs a `pw` command, tells the LLM to confirm the first line of `a.prompt.txt` names the next instruction, and to run the returned prompt straight away, stating that a handoff is the go-ahead and not to stop for confirmation. The new automated handoffs mirror this shape and wording.

**There is no host detection today**: the generated prompt is host-neutral text with no `/` or `$` prefix, so host-aware prefixing (Q08) is new behavior.

---

## Current behavior for v0.9.0 handoff automation

Only the implement cycle chains on its own (`pw handoff check|after-check|...`). Every step before it stops on a prose next-step note, and `pw` (interactive) writes the three-part prompt to the clipboard for the user to paste back:

```txt
write-requirement -> (manual paste) -> review-ask-questions -> (manual paste) -> consolidate -> (manual paste) -> write-design -> ...
pw run -> a.prompt.txt + clipboard: "Follow the instructions from .../<instruction> ... Context: this is about vX.Y.Z <slug>. Read ..."
```

## Target behavior for v0.9.0 handoff automation

The writing and consolidation steps chain without a paste, and `pw skill` feeds the next command directly:

```txt
write-requirement --(## Handoff)--> /review-ask-questions on feature-request.vX.Y.Z.<slug>.md   (runs straight away)
review-ask-questions --(hint)--> /consolidate-then-review-ask-questions on <doc>            (human review between)
consolidate (settled) --(## Handoff)--> /write-design from design source | /write-plans | /implement-step <first step>
pw skill -> stdout: "<prefix>write-design on the design.vX.Y.Z.<slug>.md"   (bare command, no header, no Context, no backticks)
```

The "stop here" signal, passed to the writing skill at invocation, holds the chain at that step instead of firing the handoff.

---

## Design area 1 for v0.9.0: the automated handoff contract in the instructions

### Shape of an automated handoff section

`write-requirement.md`, `write-design.md`, `write-plans.md`, and
`consolidate-then-review-ask-questions.md` each gain a `## Handoff` section in the
shape `implement-step.md` already uses: run the `pw skill` command from the
project root, read the bare command it returns, and run that command straight
away, with the explicit statement that a handoff is the go-ahead and the LLM does
not pause for confirmation. The handoff names the exact document just written, so
the next skill starts on the right file. `write-plans` hands off only the plain
plan, never the validation plan.

### The "stop here" gate at the writing skill

The opt-out from Q01 lives at the writing skill, not at the next skill: the author
passes a "stop here" signal when invoking `write-requirement`, `write-design`, or
`write-plans`, and that skill then writes its document and skips its handoff. The
signal is never passed to the next skill, and never after the handoff has begun,
so the gate is a property of the step that produces the document.

### The review hint, not a handoff

`review-ask-questions.md` keeps a human review between itself and the
consolidation, so it emits a next-step hint rather than an automatic call. The
hint is plain text carrying the reviewed document name as the committed baseline;
where a host can render a gray, Tab-completable prompt, it is shown that way (the
reliable trigger is deferred, Q06).

### Multi-choice lists and the free-text entry

`process-draft.md` and `split-and-define.md` present a multi-choice next-step
list. `split-and-define` lists one `/write-requirement` entry per slug it defined,
with no cap and in split order (Q05). Every list closes with a "Type something
else" entry that the instruction body adds, not `pw`; selecting it passes the
typed text through unchanged as the next call, with no name check and no required
document, because the author may state a need that names no document (Q07).

## Design area 2 for v0.9.0: the pw skill output mode

### Command surface and output channel

The mode is a `pw skill` subcommand beside the existing `handoff` subcommand. It
refines the flag form considered at review (Q01) because it takes optional
arguments. It returns the bare next-step command on stdout for the LLM to read, in
place of the three-part prompt `build_prompt` produces and the clipboard and
`a.prompt.txt` delivery `deliver_prompt` performs. The string is a command such as
`<prefix>write-design on the design.vX.Y.Z.<slug>.md`, with no "Follow the
instructions... Context..." wrapper and no backticks around the skill name, so the
LLM reads it as a command rather than as quoted text.

### Forcing a specific skill, and the host override

`pw skill` takes two optional arguments, neither meant for automation. With a skill
name, `pw skill <name>` emits that skill's command when its target document exists,
even when it is no longer the current next step, and returns `-1` when the skill is
not yet applicable (its document does not exist), so the author can re-invoke a
valid earlier skill by hand. The host override forces the command prefix and
short-circuits host detection (design area 4). With no argument, `pw skill` emits
the next step derived from disk.

### Single and multi-line output

When one next step applies, `pw skill` prints one line. When several disk-derivable
next steps apply, it prints one command per line; the instruction body, not `pw`,
appends the "Type something else" entry and, for the split fork, the per-slug list
(design area 1). The subcommand is a distinct output path on the hub, leaving the
interactive `pw` and the existing `pw handoff` cycle unchanged.

## Design area 3 for v0.9.0: deriving the next step from on-disk state

### Reusing the existing state machine

`pw skill` reads the same `compute_state` and `next_step_numbers` the interactive
flow uses, so the next step it names comes from the documents on disk, not a new
parser. Because that walk already orders requirement, then design, then plan, the
Q04 "most advanced artifact wins" precedence falls out of the existing rules: with
a draft, a requirement, a design, and a plan all present, the reported step is the
one after the plan.

### A consolidated document is read from disk, not from a parameter

`docs.has_open_questions` already detects the `## Open questions` marker, the
"review pending" signal: a requirement or issue still carrying that section maps to
`/review-ask-questions`. A document whose questions are consolidated (the section
stripped and a decisions table such as `## Requirement clarifications` present) is
settled, so `pw skill` advances to the next phase. The fork is read from the
document alone, with no LLM-passed parameter, because the consolidate step's own
output (strip the section, write the table) records the state on disk (Q03).

To keep that signal unambiguous in the rare case the review round raises no
question, `review-ask-questions` writes a minimal decisions table (a single row such
as "No open questions, all decisions made") instead of leaving the document with no
section at all. From that settled state `pw skill` routes straight to the next phase
(`/write-design` for a requirement, `/write-plans` for a design), skipping both a
further review and a consolidate round.

### A fresh draft maps to process-draft

A new draft on `main`, or on a branch not named after the slug, with no other
`vX.Y.Z.<slug>` document, maps to `/process-draft` on that draft, building on the
existing `relevant_drafts` topic detection. A `draft.vX.Y.Z.<slug>.md` alone on the
slug branch maps to `/write-requirement` on the matching requirement.

## Design area 4 for v0.9.0: host-aware command prefix

`pw skill` prefixes each command with `/` for a Claude session and `$` for a Codex
session. The host is read from the process environment, confirmed on a live session:
Claude Code sets `CLAUDECODE` (value `1`), and a Codex session sets
`CODEX_THREAD_ID`. `pw skill` keys on those: `CLAUDECODE` present means Claude (`/`),
`CODEX_THREAD_ID` present means Codex (`$`). An explicit host override wins and
short-circuits detection: when the override is given, `pw skill` does not probe the
environment at all. The override also covers the undecidable case, where neither
marker is present (a plain terminal), so a command never ships with a guessed
prefix. The environment read and the override are the only host-specific parts of
the mode; the rest of the command string is host-neutral.

## Design area 5 for v0.9.0: consolidate auto-advance and routing

`consolidate-then-review-ask-questions` auto-advances only once every open question
carries an accepted answer and the latest round raises no new question (Q03); one
unanswered question holds the chain. On that settled outcome it calls the next
workflow instruction by source type: `/write-design` for a feature-request or
issue, `/write-plans` for a design, and `/implement-step` for a plan. For a plan,
`pw` names the first step to implement, reusing the validation-plan parsing
(`parse_validation_steps`, `derive_x`) the existing handoff already relies on, so
the first-step id appears in the emitted command.

---

## Acceptance cases for v0.9.0 handoff automation

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| `write-requirement finishes, no "stop here" phrase` | `the ## Handoff emits /review-ask-questions on that feature-request and runs it at once` | default auto-advance |
| `write-requirement invoked with the "stop here" phrase` | `the document is written and the handoff does not fire` | opt-out phrase at the writing skill (Q06) |
| `pw skill on a branch with only a new draft` | `prints <prefix>process-draft on that draft` | new-draft case, relevant_drafts |
| `pw skill with requirement, design and plan present` | `prints the step after the plan` | most-advanced precedence via next_step_numbers |
| `pw skill on a feature-request still carrying ## Open questions` | `prints <prefix>review-ask-questions on it` | open-questions marker = review pending |
| `pw skill on a consolidated feature-request (decisions table, no open questions)` | `prints <prefix>write-design from it` | settled read from disk, no LLM parameter (Q03) |
| `review-ask-questions raises no question` | `it writes a one-row decisions table, and pw skill then prints <prefix>write-design, skipping consolidate` | unambiguous settled signal (Q03) |
| `pw skill <name> where that skill's document exists but is not the next step` | `prints that skill's command` | force a valid earlier skill by hand (Q01) |
| `pw skill <name> where that skill is not yet applicable` | `returns -1` | the skill's document does not exist (Q01) |
| `pw skill in a Codex session` | `the command prefix is $` | CODEX_THREAD_ID present (Q04) |
| `pw skill in a Claude session` | `the command prefix is /` | CLAUDECODE present (Q04) |
| `pw skill with a host override` | `the override sets the prefix and detection is skipped` | override wins, short-circuits detection (Q04) |
| `consolidate on a design, all answered and none new` | `the handoff emits <prefix>write-plans from that design` | settled trigger and routing |
| `consolidate on a plan, all answered` | `the handoff emits <prefix>implement-step on the first unimplemented step, naming it` | derive_x over the validation plan (Q07) |
| `split-and-define defined three requirements` | `the instruction lists one /write-requirement per slug plus "Type something else"` | instruction owns the split fork (Q05) |
| `author picks "Type something else" and types an instruction with no document` | `the typed text passes through unchanged as the next call` | pass-through, no name check (feature-request Q07) |

## File-based IO cost clarification for v0.9.0 handoff automation

The `pw skill` derivation is a bounded index-read, not a metadata-loading delay:

- It reuses the existing `docs_dirs` scan (one directory listing) and reads only the open-questions and decisions-table marker lines on matched documents.
- Host detection reads `CLAUDECODE` and `CODEX_THREAD_ID` from the environment; it touches no file.
- `pw skill` writes nothing and prints to stdout only.

## Design decisions for v0.9.0 handoff automation

These rows record the design choices settled in review (Q01 to Q07); each names the
question that settled it, the design area where it is integrated, and the options
that were turned down.

| Area | Decision | Question | Integrated in | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Command surface | A `pw skill` subcommand taking an optional skill-name argument and a host override; returns -1 when a forced skill is not yet applicable | Q01 | Design area 2 | A bare `--skill` flag; a subcommand with no arguments |
| State source | Stateless: derive every fork from disk, never from `a.prompt_memory`, which the automated flow does not refresh | Q02 | Design areas 2 and 3 | Read the memory for the tiebreak; read and write it |
| Consolidate-against-advance fork | Read from disk (open-questions marker against decisions table); `review-ask-questions` writes a one-row table when it has no question, so the settled signal is always present | Q03 | Design area 3 | An LLM-passed parameter; a hybrid disk-or-parameter path |
| Host signal | Read the process environment (`CLAUDECODE` for Claude, `CODEX_THREAD_ID` for Codex); a host override wins and short-circuits detection | Q04 | Design area 4 | A required per-call argument; a persisted per-machine config |
| Split fork ownership | The instruction body lists the split slugs; `pw skill` answers only disk-derivable next steps | Q05 | Design areas 1 and 2 | pw formats a passed slug list; pw derives slugs from disk |
| "Stop here" form | A recognized phrase in the writing skill's argument | Q06 | Design area 1 | A marker file; a pw-level flag |
| First plan step | The first not-yet-implemented step via `derive_x` over the validation plan | Q07 | Design area 5 | Literally step 1; the first step in the plain plan |
