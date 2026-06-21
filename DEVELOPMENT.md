# Development workflow with IA

This workflow takes one raw topic from draft notes to reviewed documents,
implemented plan steps, and grouped commits. It uses the skills in
`.github\skills` (Copilot) and `.claude\skills` (Claude Code) together
with the local helper scripts in `bin\` and `tools\`. Both folders
delegate to the same markdown bodies under `instructions\`, so the same
slash command produces the same output regardless of the agent.

This is geared toward Python projects, but the general flow and some of
the helpers can be adapted to other languages and ecosystems.

## Agent prerequisites

The workflow itself is agent-agnostic; only the prerequisites differ.

### Copilot in VS Code — prerequisites

Make sure the setting "Chat Permissions Default" is set to "Bypass Approval".  
And "chat.notifyWindowOnConfirmation" is set to "always".  
And "chat.notifyWindowOnResponseReceived" is set to "always".

### Claude Code — prerequisites

Run Claude Code in a permission mode that does not block every tool
call (for example `claude --permission-mode acceptEdits`, or
`bypassPermissions` when the worktree is disposable). Configure a
`Stop` hook in `~/.claude/settings.json` if you want the desktop to
chime when a long prompt completes, which is the Claude-side equivalent
of the VS Code `chat.notifyWindowOnResponseReceived` setting.

### Any other LLM — prerequisites

The slash-command names used below map one-to-one to markdown bodies in
`instructions\<name>.md`. An LLM that does not auto-discover those
files can still run the same step by being handed the matching
instruction file as part of its context, together with the input files
the body expects (a draft, a requirement, a plan, etc.).

## Goal: avoid vibe-coding

Vibe-coding is the shortcut some developers take with an AI assistant:
"I got an idea, here it is, now generate me some code for it, I will
figure out the details later." The code lands fast, runs against an
unspoken set of assumptions, and then breaks on the first real-world
case the author never wrote down.

This workflow keeps the creative spark — the draft is still raw natural
language, the author still picks the topic and direction — but spends
real time turning that spark into a defined requirement, a reviewed
design with explicit acceptance scenarios, and a plan that drives the
code in a known order. Each skill exists to do one of those jobs:

- **Capture and (optionally) split** the idea: write
  `docs\draft.vX.Y.Z.<topic>.md` in free form, then run
  `/split-and-define` only if the draft carries several items. A
  single-requirement draft skips straight to the next step.
- **Define each requirement** in its own document with
  `/write-requirement`.
- **Refine each document** through the review loop
  (`/review-ask-questions` then `/consolidate-then-review-ask-questions`),
  until no open question remains.
- **Design the solution**, including acceptance scenarios that describe
  what "done" looks like from the user side, with `/write-design`.
- **Plan the implementation** as a numbered list of steps with
  `/write-plans`. The plan starts with one or more gate-test steps that
  add failing tests against the target behavior, continues with steps
  that make those gate tests pass piece by piece, and ends with an
  acceptance-test step that closes the loop on the requirement.
- **Implement and check each step** in isolation with
  `/implement-step N` then `/implementation-check N`, updating the
  validation document and committing in small grouped commits.

What this workflow refuses to do:

- Skip the requirement document because "we both know what I mean".
- Skip the design document because "the code will tell us".
- Skip the gate tests because "I'll add them after".
- Skip the acceptance tests because "I tested it manually once".

What this workflow keeps:

- Natural-language drafts with no constraint on style.
- Author judgement on what is one requirement versus several.
- A short path when the draft is genuinely one self-contained
  requirement (see
  [Requirement breakdown from the draft](#requirement-breakdown-from-the-draft)).

The cost is up-front: a few extra documents before any code is written.
The payoff is that the code that does get written has a known target, a
written acceptance bar, and tests that already exist when the
implementation starts.

### Trail left by the workflow

A long-running benefit: every phase leaves an artifact, so the workflow
doubles as documentation of the development process itself.

What ends up in the repository:

- The original draft, with the author's raw framing.
- The requirement document(s), with the decision table that captures
  every resolved open question (the option that was picked and the
  alternatives that were rejected).
- The design document, with its own decision table and the acceptance
  scenarios.
- The plan, with one entry per numbered step, and the validation plan
  that records what each step actually shipped.
- One grouped commit per logical change, each with a conventional commit
  message written for the matching diff.
- A merge commit with a rewritten conventional message that points to
  the documents that landed with the branch.

This trail is useful to two kinds of future readers:

- A human reader (the original author six months later, or a new
  contributor) who needs to understand why a piece of code looks the
  way it does, not just what it does.
- An LLM that is asked to extend, debug, or refactor the code in a later
  session. The model gets context that is missing from the code alone:
  the question that was being answered, the alternatives that were ruled
  out, and the acceptance bar that was negotiated. The richer the
  history, the better the suggestions the model can produce.

Code without that trail forces every future reader — human or model —
to reverse-engineer the intent from the implementation. Code with the
trail short-circuits that reverse-engineering, which is the same reason
this workflow exists in the first place.

### Why LLM self-review matters

Two phases in this workflow exist specifically because the LLM should
review its own output, never ship its first pass:

- The review loop (`/review-ask-questions` followed by
  `/consolidate-then-review-ask-questions`) challenges the requirement
  document and the design document before any code is written.
- The implementation check (`/implementation-check`) challenges the code
  produced by `/implement-step` against the plan and the design's
  acceptance scenarios.

Trusting the first pass blindly is exactly what these phases protect
against. A first-pass document usually reads well, and a first-pass
step usually compiles and passes the tests it shipped with — which is
the reason a separate review pass is needed in the first place. The
same model that wrote the artifact gets a fresh chance, with the
surrounding documents as context, to spot contradictions, ambiguity,
missing acceptance criteria, or gaps between what was planned and what
was actually written.

What the review loop on a document catches:

- Contradictions inside the requirement, for example two paragraphs
  that imply different behavior for the same input.
- Open questions the author did not see, because the draft assumed a
  shared context that is not written down.
- Acceptance criteria that sound obvious in English but turn out to be
  untestable when phrased as a scenario.
- Cases where the model only understood the requirement on the
  surface: the open questions it raises (or fails to raise) are a
  visible signal of how deep the model actually went.

What the implementation check catches:

- Code that compiles, passes its own tests, and still does not match
  the plan: a sub-step skipped, a side condition not handled, a test
  that proves the wrong claim.
- Architecture smells, dependency issues, and hot-path performance
  risks that are easier to spot from outside the step than from inside
  it.
- Gaps between the acceptance scenarios captured in the design and
  what the code actually demonstrates.

When the implementation check reports gaps, the next move is to iterate
on `/implement-step N` (and on the tests) until a fresh check comes
back clean. The validation document keeps the trace of what each
iteration changed, so a later reader (human or model) can see not just
the final state but the corrections that produced it.

The pattern is the same on both sides: ask the model to look again at
work it just produced, with the surrounding artifacts as context, and
treat the first pass as a draft, not a deliverable.

## Shell setup for the IA workflow

Before you use the aliases below, load the project shell with `senv.bat`.
That script switches to the project Python version, adds `bin\` to `PATH`,
and loads the Doskey macros declared in `senv.bat` and `senv.doskey`.

The rest of this document assumes those macros are available.

The Doskey macros and the `senv.bat` wrapper are Windows-only. The
Python entry points they call (`tools\group_commit_message_prompt.py`,
`tools\git_batch_commit.py`, `tools\coverage_gap_functions.py`,
`tools\git_command.py`, `tools\groundhog\cli.py`) run on Linux and macOS
as well; wire them into bash functions or shell aliases as needed. The
slash commands and the skill bodies in `instructions\` do not depend on
Windows at all.

## Local command reference for this workflow

- `gcmp`: Doskey alias to `bin\gcmp.bat`. It runs
  `tools\group_commit_message_prompt.py`, reads the staged Git state, writes
  `a.diff`, clears `a.commit`, builds a `/group-commits-msg` prompt from the
  staged files, copies that prompt to the clipboard, and prints a ready line.
- `gcba`: Doskey alias to `bin\gcba.bat --root-a-commit`. It runs
  `tools\git_batch_commit.py --root-a-commit`, validates `a.commit`, and then
  replays the grouped commits when the file is valid. The aliases `gcb`,
  `gbc`, `gcbr`, `gbcr`, `gcab`, and `gbca` are the same family of helpers.
- `ruffc`: Doskey alias to `ruff check`. Use it right after code generation
  or manual edits.
- `ghog`: Doskey alias to `bin\ghog.bat`, the groundhog pytest reset tool that
  backs every pytest alias below. `ghog day` walks the whole chain — check,
  affected tests, full suite with coverage — stopping at the first non-green
  step; `ghog init` registers the LLM fixing loop in a consuming project. The
  manual is [GROUNDHOG.md](GROUNDHOG.md).
- `ptanc`: Doskey alias to `ghog affected --no-cov`. It reruns only the tests
  affected by the current changes (testmon) and reports pass or fail, coverage
  off, so the run stays fast and never fails on the 100% gate. Use it to
  confirm the focused tests are green, not to read a coverage report.
- `pta`: Doskey alias to `ghog affected`. Same testmon selection, with
  appended coverage: this is how a coverage gap is re-verified after adding
  tests, without paying a full run; when it reports the gate is reached, no
  `ptr` is needed.
- `pts`: Doskey alias to `ghog single <test files>`. Runs the named test
  files in focus, coverage off, and compares the result with the failing
  tests of the last full run (`a.ghog.failures`), splitting plain failures
  from test-interaction suspects.
- `ptr`: Doskey alias to `ghog full`. It resets `.testmondata` and reruns the
  suite with the coverage report measured against the gate. Still the slow,
  authoritative pass — but its output is now budgeted (progress lines and a
  final report instead of raw pytest output), so the LLM fixing loop can run
  it through `ghog day` instead of leaving it to the user only.
- `covg`: alias to
  `python "tools\coverage_gap_functions.py" $*`.
  It maps uncovered coverage lines to the enclosing function or method, adds
  branch context when possible, logs the report, and copies a ready-to-paste
  test coverage prompt to the clipboard. On a coverage gap (`exit=3`), ghog
  replays the term-missing rows whose `Missing` column is exactly the covg
  input.

## Groundhog: the test loop behind the pytest aliases

All the pytest aliases above are one tool, groundhog, and `ghog day` is the
single command that walks them in order, gating each step on the previous
one:

```txt
   +---------------------------------+
   |  ghog day                       |
   +-------+-------------------------+
           |
           |  check.bat              (exit 0, no ERROR lines)
           |  ptanc                  (affected tests green)
           |  ptr                    (full suite green, cov at gate)
           v
   +---------------------------------+
   |  exit 0: objective reached      |
   |  (else: stop at the first       |
   |   non-green step, with the      |
   |   exact fix to apply)           |
   +---------------------------------+
```

An LLM can drive the same walk in a fixing loop — run `ghog day`, apply the
fix the report names, run it again — registered per project with `ghog init`
for both Claude Code (`/groundhog`) and ChatGPT Codex. The exit codes, the
report grammar, the coverage-gap flow with `covg`, and the registration are
all detailed in [GROUNDHOG.md](GROUNDHOG.md).

In that LLM loop, no ghog output reaches the conversation: the instruction
file routes every ghog call through `> a.ghog.log 2>&1` at the project root.
The exit code alone drives the branching; the model then reads only the log
tail (5 lines on green, 100 on a stop), so the chat context carries bounded
tail reads instead of full reports. The log is overwritten by each run and
never deleted — watch it from a second console to follow a run live. The
redirect belongs to the LLM invocation only: ghog itself writes to stdout,
and console runs (`ghog day`, `ptr`, `pta`, ...) are untouched.

Run completion is a file contract, not a log guess: every run brackets
itself in `a.ghog.status` (`state=running pid=` then `state=done exit=`),
`ghog status` replays it without starting anything, and a harness whose
tool timeouts kill long calls runs the walk with `ghog day --detach` — a
survivor process the timeout cannot reach, polled through `ghog status`
(see GROUNDHOG.md, Q32).

## Draft capture for a feature or fix

```txt
   +---------------------------------+
   | raw notes / discussion          |
   | missing or broken behavior      |
   | desired outcome                 |
   +-------+-------------------------+
           |
           |  capture
           v
   +---------------------------------+
   |                                 |----+
   |  docs\draft.vX.Y.Z.<topic>.md   |    |  edit + refine
   |                                 |<---+  in natural language
   +-------+-------------------------+
           |
           |  stable enough to split
           v
   +---------------------------------+
   |   draft ready for breakdown     |
   +---------------------------------+
```

1. Start with `docs\draft.vX.Y.Z.<topic>.md`.
2. Keep `X.Y.Z` as the working version for the current effort, even if the
  final merge target changes later.
3. Keep `<topic>` short, stable, and descriptive.
4. Write the draft in natural language, preferably English. Cover the desired
  behavior, missing behavior, broken behavior, constraints, examples, and the
  expected outcome.

## Requirement breakdown from the draft

```txt
                +---------------------------------+
                |  docs\draft.vX.Y.Z.<topic>.md   |
                +----------------+----------------+
                                 |
                  +--------------+--------------+
                  |                             |
        single requirement?            multiple items?
        skip /split-and-define         /split-and-define
                  |                             |
                  |                             v
                  |             +---------------------------------+
                  |             |  draft + appended section:      |
                  |             |  "List of feature-requests      |
                  |             |   and issues to create"         |
                  |             |   - item 1   [topic-slug]       |
                  |             |   - item 2   [topic-slug]       |
                  |             |   - ...                         |
                  |             |   - item N   [topic-slug]       |
                  |             +----------------+----------------+
                  |                              |
                  |                  /write-requirement
                  |                  <type> vX.Y.Z <topic>
                  |                  (one call per item)
                  |                              |
                  +--------------+---------------+
                                 |
                /write-requirement <type> vX.Y.Z <topic>
                (single call, author picks the type)
                                 v
                +---------------------------------+
                | docs\feature-request.vX.Y.Z.    |
                |       <topic-slug>.md           |
                |  or                             |
                | docs\issue.vX.Y.Z.              |
                |       <topic-slug>.md           |
                +---------------------------------+
```

`/split-and-define` is optional. The choice depends on the draft:

- Run `/split-and-define` first when the draft mixes several distinct
  items, when those items have a non-trivial dependency order, or when
  the author wants the skill to propose a `[topic-slug]` per item and
  decide which item is a `feature-request` and which is an `issue`.
- Skip `/split-and-define` and call `/write-requirement` directly when
  the draft already describes a single, self-contained requirement and
  the author already knows the type (`feature-request` or `issue`),
  version, and topic. This shorter path keeps the focus on writing one
  clear requirement instead of running a split that would return only
  one item.

When `/split-and-define` is used:

1. Run `/split-and-define` with the draft document in context.
2. That skill updates the draft itself by appending a
  `List of feature-requests and issues to create` section.
3. The generated list groups related draft items, gives each item a key title
  plus a short `[topic-slug]`, and orders the items from the most independent
  one to the most dependent one.
4. For each item in that list, run `/write-requirement` with the draft and the
  selected item in context.
5. Use the actual skill name `/write-requirement` and pass the type, version,
  and topic, for example `issue v9.3.0 sentinels`.
6. The skill writes `docs\<type>.vX.Y.Z.<topic>.md`.

When `/split-and-define` is skipped:

1. Decide the type directly: `feature-request` for new behavior, `issue`
  for a bug or missing behavior already present in the draft.
2. Run `/write-requirement <type> vX.Y.Z <topic>` with the draft in
  context, picking a stable `<topic>` slug yourself.
3. The skill writes the same `docs\<type>.vX.Y.Z.<topic>.md` file and
  the next phase (review loop) is identical.

You can decide if you need to isolate each identified features or issues in their
own development branch (`git switch -c <topic-slug>`) or if you can keep multiple
related items in the

## Review loop for each requirement document

The same loop is used later on the design document and, if needed, on the plan
document. Only the input document changes.

This loop is the document-side half of LLM self-review (see
[Why LLM self-review matters](#why-llm-self-review-matters)): each
pass gives the model a fresh chance to find contradictions or missing
context in a document it just helped to shape, and to point those out
as open questions before they become code.

```txt
   +---------------------------------+
   |  document under review          |
   |  (requirement, design, or plan) |
   +-------+-------------------------+
           |
           |  /review-ask-questions
           |  (appends Qxx blocks: options,
           |   pros, cons, recommended choice)
           v
   +---------------------------------+
   |  doc with open questions        |
   +-------+-------------------------+
           |
           |  user picks one answer per Qxx
           v
   +---------------------------------+
   |  answered doc                   |
   +-------+-------------------------+
           |
           |  /consolidate-then-review-ask-questions
           |  (folds answers into a decision table,
           |   removes resolved Qxx,
           |   appends new Qxx only if needed)
           v
   +---------------------------------+
   |  consolidated doc               |----+  new open questions?
   |                                 |    |  yes -> /review-ask-questions
   |                                 |<---+  (loop)
   +-------+-------------------------+
           |
           |  no more open questions
           v
   +---------------------------------+
   |  doc approved for next phase    |
   +---------------------------------+
```

1. Run `/review-ask-questions` on the requirement document, with the related
  markdown files in context.
2. That skill appends open questions with options, pros and cons, a
  recommended choice, and an explicit answer format.
3. Once answers are settled, run `/consolidate-then-review-ask-questions`.
4. That skill folds resolved questions back into the document, removes old
  question blocks, and asks new questions only when more clarification is
  still needed.
5. Repeat the two skills until the requirement is clear enough to design and
  plan.

## Design and planning flow for each approved requirement

```txt
   +---------------------------------+
   |  approved requirement doc       |
   +-------+-------------------------+
           |
           |  /write-design
           v
   +---------------------------------+
   |                                 |----+
   |  docs\design.vX.Y.Z.<topic>.md  |    |  /review-ask-questions
   |  (scope, constraints, target    |    |  /consolidate-then-review-...
   |   behavior, design areas)       |<---+  (loop until stable)
   +-------+-------------------------+
           |
           |  /write-plans
           v
   +---------------------------------+
   |  docs\plan.vX.Y.Z.<topic>.md    |
   |    (execution plan)             |----+
   |  docs\plan.vX.Y.Z.<topic>.      |    |  /review-ask-questions
   |       validation.md             |    |  /consolidate-then-review-...
   |    (validation template)        |<---+  (optional, if open Qs remain)
   +-------+-------------------------+
           |
           |  plan ready for step-by-step execution
           v
   +---------------------------------+
   |  ready to /implement-step       |
   +---------------------------------+
```

1. Run `/write-design` with the requirement document in context.
2. The skill writes `docs\design.vX.Y.Z.<topic>.md` and keeps the output at
  design level: scope, constraints, confirmed facts, target behavior, and
  major design areas, not file-by-file implementation steps.
3. Run `/review-ask-questions` on the design document.
4. Run `/consolidate-then-review-ask-questions` after the design answers are
  chosen.
5. Repeat that review loop until the design is stable.
6. Run `/write-plans` with the design document in context.
7. That skill creates `docs\plan.vX.Y.Z.<topic>.md`, which is the execution
  plan: step order, file lists, rollout notes, line-budget checkpoints,
  command checklists, and acceptance-test expectations.
8. The same skill also creates
  `docs\plan.vX.Y.Z.<topic>.validation.md`, which is the implementation
  validation document updated later by the execution and checking steps.
9. If the plan still has open implementation questions, run the same
  review-and-consolidation loop on the plan document before coding.

## Conventional commit message template: why and what beyond changelog

The grouped commit loop below builds on the
[Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
spec. The spec covers the title line only:
`<type>[optional scope]: <description>`. That title is the input that
changelog generators read, and it is the only part of the message
the spec defines.

This repository extends the spec with a body template,
[`templates/group-commits-msg.template.md`](templates/group-commits-msg.template.md),
that captures the rationale and the change list under the title.

### Body template structure for a single commit

```log
type(scope): subject

Why:

A detailed reason for the change. Multiple sentences. Use specific
terms, not generalities.

A detailed description of the "now" state that this commit produces.
Multiple sentences. Use specific terms, not generalities.

What:

- list of changes...
- ... done for that commit
```

Title line rules (the spec part):

- 52 characters max, including the type, the optional scope, the
  colon, and the space.
- `type` is one of `feat`, `fix`, `docs`, `chore`, `refactor`,
  `test`, `build`, `ci`, `perf`, `style`, or any other type the
  project declares.
- `(scope)` is optional and names the area touched (a module name,
  a feature slug, etc.).
- `subject` is a short imperative description.

Body and footer rules (the extension on top of the spec):

- Body and footer lines wrap at 80 characters and are never
  indented.
- The `Why:` section is two paragraphs separated by an empty line:
  the reason for the change first, the "now" state second.
- The `What:` section is a dash-prefixed list, one item per
  modification.
- Words listed in [`rules/blacklist.md`](rules/blacklist.md) are
  forbidden in the body, same as in any other prose in the project.

### Why the body extension matters beyond changelog generation

The Conventional Commits spec only standardizes the title. That is
enough to generate a changelog from a git log, which is the spec's
stated goal. It is not enough for the other readers of the commit
history:

- The original author, six months later, looking at why a function
  looks the way it does.
- A new contributor trying to follow the order in which decisions
  were made.
- An LLM asked to extend, refactor, or debug the code, with only the
  current files and the git history as context.

Those readers need the `Why:` section. The diff already tells them
what changed; the title tells them what kind of change it was; only
the body tells them what the change was for and how the code reads
better afterwards.

### Why automating the grouping matters at commit time

By the time a slice of work is ready to commit, the working tree
usually contains several distinct changes:

- The code change that was the goal of the slice.
- One or more small fixes the author noticed along the way.
- Test updates that pair with one of the above.
- A documentation tweak or a configuration change.

Two real problems show up at that point:

- The author often no longer remembers every change they made,
  especially the small fixes picked up along the way. Squashing the
  whole working tree into one "WIP" commit hides those changes from
  the history for good.
- The order in which changes are committed matters: a commit that
  modifies a file used by a later commit must land first, or the
  intermediate state of the repository becomes incoherent (tests
  fail at a midway commit, bisect lands on a broken state, etc.).

The `/group-commits-msg` skill handles both problems. It reads
`git diff --cached`, groups files from the least dependent group to
the most dependent one, and writes one commit message per group
into `a.commit`. The author reviews and edits `a.commit`, then
`gcba` replays the file as a sequence of real commits in that order.

The skill does more than save typing. It rebuilds the change story
from the diff itself, so the resulting commits read like the author
made them carefully, even when the author no longer remembers every
detail. The grouping pass also catches changes that should not have
been mixed: an unrelated fix that landed in the same slice gets its
own commit, instead of being absorbed silently into a feature
commit.

### Trade-off worth knowing for the grouping skill

The skill is only as good as the staged diff. If the staged set
mixes a feature with an unrelated refactor, the skill produces two
well-formed commits, but the split is the only one the diff
supports. When the diff itself is incoherent, edit `a.commit` by
hand before running `gcba`, or stage in two passes (commit one
slice, then stage the rest).

## Grouped commit loop for documents and code

```txt
   +---------------------------------+
   |  staged files (current slice)   |
   +-------+-------------------------+
           |
           |  gcmp
           v
   +---------------------------------+
   |  a.diff (snapshot of the diff)  |
   |  clipboard:                     |
   |    /group-commits-msg           |
   |    ... Context: <topic>         |
   +-------+-------------------------+
           |
           |  paste the prompt into Copilot / Claude
           v
   +---------------------------------+
   |  a.commit                       |----+  edit if grouping
   |  (groups + messages,            |    |  or wording is off
   |   one block per group)          |<---+  (rerun /group-commits-msg
   +-------+-------------------------+       only if needed)
           |
           |  approved a.commit
           |  gcba
           v
   +---------------------------------+
   |  commits replayed, from least   |
   |  dependent group to most        |
   |  dependent group                |
   +---------------------------------+
```

1. Stage only the files that belong to the current slice. Use `git add .` only
  if the worktree contains nothing unrelated.
2. Run `gcmp`.
3. Paste the generated clipboard prompt into your agent (Copilot, Claude
  Code, or another LLM that can write files in the workspace). The
  prompt already starts with `/group-commits-msg ...` and ends with
  `Context:`. Add the topic at the end of that `Context:` line.
4. Review the generated `a.commit` file. `a.diff` is the staged diff snapshot
  used to justify the groups, and `a.commit` is the grouped commit plan that
  will be replayed later.
5. If the grouping or wording is off, edit `a.commit`.
  Rerun the `gcmp` -> `/group-commits-msg` generation pass only if you need
  your agent to regroup files or rewrite the commit messages again. If
  your manual edits are enough, do not rerun that pass; go straight to
  `gcba`.
6. When `a.commit` is ready, either say `go ahead` in the same chat flow or
  run `gcba` directly.
7. `gcba` validates `a.commit` and creates the commits from the least
  dependent group to the most dependent group.

Use this commit loop once after the documents are ready, then again after each
fully completed implementation step.

## Step execution loop from the plan

```txt
                +---------------------------------+
                |  docs\plan.vX.Y.Z.<topic>.md    |
                |  pick next unchecked step N     |
                +-------+-------------------------+
                        |
                        |  /implement-step N   (starts the chain)
                        v
   +===================================================================+
   |  Automated implement chain  --  one /implement-step N starts it,  |
   |  then pw handoff hands each step to the next with no menu and no  |
   |  "go ahead" until a.commit is written.                            |
   |                                                                   |
   |        +-----------------------+                                  |
   |        | /implement-step N     |                                  |
   |        | code + tests, ghog day|                                  |
   |        +-----------+-----------+                                  |
   |                    |  ghog day exit=0                             |
   |                    |  pw handoff check <x>                        |
   |                    v                                              |
   |        +-----------------------+                                  |
   |        | /implementation-check |----+  No: validation reads       |
   |        | writes Yes/No verdict |    |  No -> /implement-missing-  |
   |        +-----------+-----------+<---+  step, ghog day, then       |
   |                    |  pw handoff       pw handoff check <x>       |
   |                    |  after-check <x>  (re-check the gap)         |
   |                    v  (Yes branch)                                |
   |        +-----------------------+                                  |
   |        | /group-commits-msg    |                                  |
   |        | writes a.commit       |                                  |
   |        | (git add -A variant)  |                                  |
   |        +-----------+-----------+                                  |
   +==================== ==============================================+
                        |  chain ends: a.commit holds the grouped
                        |  commit messages, ready for review
                        v
                +---------------------------------+
                |  a.commit reviewed, "go ahead"  |
                |  gcba replays the commits, gp   |
                +-------+-------------------------+
                        |
                        v
                +---------------------------------+
                |  step N committed and pushed    |----+  more steps?
                |                                 |    |  yes -> /implement-
                |                                 |<---+  step (loop)
                +-------+-------------------------+
                        |
                        |  last step done
                        v
                +---------------------------------+
                |  branch ready to merge          |
                +---------------------------------+
```

The giant box in the diagram is the automated part: one `/implement-step N`
starts it, and `pw handoff` chains the check, any implement-missing pass,
and the `a.commit` group-commit step with no menu and no go-ahead between
them (see [Automated implement chain with pw handoff](#automated-implement-chain-with-pw-handoff)
below). The numbered steps that follow are the underlying actions that
chain runs, and the helper commands you can still call by hand when you
drive a step yourself.

1. Pick the next unchecked step from `docs\plan.vX.Y.Z.<topic>.md`.
2. Run `/implement-step <step-number>` with the plan, design, and related
  requirement documents in context.
3. Run `ruffc`.
4. Run `ptanc` to confirm the focused tests (created, modified, or impacted by
  the step) pass. It prints no coverage, so it stays fast and leaves the
  recorded `.coverage` untouched.
5. Run `pts <test path>` when you want a single test, class, or file on its
  own. It is coverage-off too, and it compares the result with the failing
  tests of the last full run.
6. `ptr` (or the whole `ghog day` walk) is the full coverage pass. It is still
  the slow step, but its output is budgeted — progress lines and a final
  report instead of raw pytest output — so an LLM can run it too. On a
  coverage gap it replays the uncovered lines; `covg` maps them to the
  enclosing functions and builds a clipboard prompt for the smallest tests
  still needed, re-verified with `pta` only (see [GROUNDHOG.md](GROUNDHOG.md)).
7. Once the code and tests are green, run `/implementation-check` with the
  step number, version, topic, relevant markdown docs, and `a.diff` when
  available.
8. That skill updates `docs\plan.vX.Y.Z.<topic>.validation.md` and checks
  whether the step is actually complete, including architecture smells,
  dependency issues, and hot-path performance risks.
9. If a file is getting too large or is doing too many unrelated things, use
  `/split-large-file` before the next step grows it further.
10. Stage the finished slice and reuse the grouped commit loop. When the
  chain drives it, `pw handoff after-check` reaches this step on its own
  and writes `a.commit` for you.
11. Do not start the next step until the current one is implemented, tested,
  checked, and committed. And pushed. (use `gp` for `git push`)

The `/implementation-check` call in step 7 is the code-side half of LLM
self-review (see [Why LLM self-review matters](#why-llm-self-review-matters)):
the model that just wrote the step gets a fresh pass, with the plan, the
design, and `a.diff` in context, to confirm or refute that the code
actually implements the plan and meets the acceptance scenarios. When
the check reports gaps, iterate on the step until a fresh check is
clean — that is the moment the step can be committed and pushed.

### Automated implement chain with pw handoff

The giant box in the diagram above runs without a menu and without a
go-ahead between steps. `pw` is the prompt-workflow launcher (the `pw`
Doskey alias to `bin\prompt_workflow.bat`); its `pw handoff <task> <x>`
subcommand writes the prompt for the next cycle step and skips the
interactive menu. The model reads that prompt from `a.prompt.txt` and
keeps going.

Three calls chain the cycle, each run from the project root once the
current step is done:

- after `/implement-step <x>` ends with a green `ghog day` walk:
  `pw handoff check <x>` writes the `implementation-check.md` prompt.
- after `/implementation-check <x>` records its `Analysis of Step x`
  verdict: `pw handoff after-check <x>`. The task is neutral; `pw` reads
  that verdict line and routes the branch itself, so the caller cannot
  pick the wrong next step:
  - a `No` verdict  --  the `implement-missing-step.md` prompt, to fill
    the `Missing work for Step x` list, then back to the check.
  - a `Yes` verdict  --  the `group-commits-msg.md` prompt in its
    `git add -A` form, which stages every change and writes one grouped
    commit message per group into `a.commit`.
- after `/implement-missing-step <x>` ends with a green walk:
  `pw handoff check <x>` again, so the filled gap is re-checked.

The chain stops at `a.commit`. Writing the grouped messages is the last
automatic step; replaying them is not. `gcba` runs only after you review
`a.commit` and say "go ahead", the gate `group-commits-msg.md` keeps. So
the model writes the messages on its own, then waits before any commit
lands; after that `gp` pushes and the cycle loops to the next step.

Each `pw handoff` call also copies the prompt to the clipboard and records
the step in `a.prompt_memory`, so a later interactive `pw` run sees a
consistent state. The calls are wired in by the `## Handoff` section of
`implement-step.md`, `implement-missing-step.md`, and
`implementation-check.md`; without those sections the subcommand exists
but nothing triggers it.

## Decision rule for architecture and performance findings

- If `/implementation-check` finds an architecture smell (or violation, or
  girth too big, or anything else), ask for the pros
  and cons of fixing it now versus documenting an exemption and creating a
  follow-up issue. Fix it immediately when the change stays small and within
  the current step scope.
- If it finds a hot-path performance issue, fix it before moving on. Do not
  defer it to a later step unless the current fix is blocked by missing design
  work.

Repeat this sequence until every planned step is committed in your branch.

## Merge your development branch

```txt
   +---------------------------------+
   |  development branch             |
   |  (all steps committed)          |
   +-------+-------------------------+
           |
           |  git fetch
           |  git rebase origin/main
           |  ghog day (check + ptanc + ptr)
           v
   +---------------------------------+
   |  branch rebased and green       |
   +-------+-------------------------+
           |
           |  git switch main
           |  git pull
           |  git merge --no-ff <branch>
           v
   +---------------------------------+
   |  merge commit on main           |
   |  (default Git message)          |
   +-------+-------------------------+
           |
           |  /update-merge-commit-msg
           |    (git-extract-merge-docs.sh
           |     -> a.docs;
           |     skill -> a.commit)
           |  grmc
           |    (rewrites the merge commit)
           v
   +---------------------------------+
   |  merge commit with              |
   |  conventional message           |
   +-------+-------------------------+
           |
           |  gp / git push
           v
   +---------------------------------+
   |                                 |----+  next requirement?
   |  main published                 |    |  yes -> new branch,
   |                                 |<---+  back to /implement-step
   +-------+-------------------------+
           |
           |  after several merges
           |  /prepare_release_notes
           |  brel
           v
   +---------------------------------+
   |  release                        |
   +---------------------------------+
```

### Rebase your branch on top of main

Do this while you are still on your development branch. The goal is to replay
your work on top of the latest `origin/main`, resolve conflicts before the
merge commit exists, and rerun the same checks you used during step execution.

1. Run `git fetch` to refresh your remote references.
2. Run `git rebase origin/main` and resolve any conflict before continuing.
3. Run `ghog day`: it walks the compile check (check.bat), the affected tests
  without coverage, and the full suite with the coverage report — stopping at
  the first non-green step with the fix to apply. This is the one place the
  100% gate from `pyproject.toml` is checked before the merge; the individual
  aliases (`c`, `ptanc`, `ptr`) remain available to re-run a single step (see
  [GROUNDHOG.md](GROUNDHOG.md)).

### Create the merge commit on main

Switch back to `main` only after your rebased branch is clean. This keeps the
merge commit focused on a branch that already passed checks on top of the
current main line.

1. Run `git switch main`.
2. Run `git pull` to make sure your local `main` matches the remote branch.
3. Run `git merge --no-ff <your-branch>` so Git creates an explicit merge
  commit for the branch.

### Reword the merge commit from the branch docs

Do not keep the default merge message. At this point the merge commit exists,
so you can derive a proper conventional commit message from the documents that
landed with the branch.

1. Run `/update-merge-commit-msg`.
2. That skill calls the merge-doc extraction script, writes the merged branch
  documents to `a.docs`, then writes one conventional commit message to
  `a.commit` for you to review and edit if needed.
3. Once `a.commit` is ready, run `grmc`, which is the local Doskey alias to
  `scripts\update-merge-commit-msg\git-reword-merge.sh`.
4. `grmc` rewrites the current merge commit so its message matches the final
  content of `a.commit`.

### Push the updated main branch

Publish only after the merge commit message has been rewritten.

1. Run `gp` if your shell defines it as your `git push` shortcut.
2. If `gp` is not defined in your shell, run `git push` directly to update
  `main`.

## Prepare release notes and create the release

A release on `main` takes two moves. First `/prepare_release_notes`
turns the commit history into release notes; then `brel` runs the build
that creates the tag. The skill never tags anything itself.

```txt
   +---------------------------------+
   |  main with several merge        |
   |  commits                        |
   +-------+-------------------------+
           |
           |  /prepare_release_notes  (step 1)
           |  runs scripts\prepare_release_notes.sh
           v
   +---------------------------------+
   |  a.md - release-preparation     |
   |  notes                          |
   |  - commit titles grouped by type|
   |  - full commit list since tag   |
   +-------+-------------------------+
           |
           |  step 2: summary written into
           |  version.txt (main theme, key
           |  changes, three title pairs)
           v
   +---------------------------------+
   |  version.txt - release-notes    |
   |  summary draft                  |
   +-------+-------------------------+
           |
           |  step 3: author picks one title pair
           |  step 4: version.txt rewritten with title
           v
   +---------------------------------+
   |  version.txt finalized          |
   +-------+-------------------------+
           |
           |  step 5: tools\dev_workflow\update-changelog.bat
           v
   +---------------------------------+
   |  CHANGELOG.md updated with      |
   |  vX.Y.Z and the summary         |
   +-------+-------------------------+
           |
           |  brel  ->  tools\dev_workflow\t_build.bat rel
           |        ->  update-version.bat drops -SNAPSHOT
           |        ->  git tag vX.Y.Z, marked [valid] on success
           v
   +---------------------------------+
   |  tagged release on main         |
   +---------------------------------+
```

### Six steps of /prepare_release_notes

`/prepare_release_notes` resolves to the mutualized body
[`instructions/prepare-release-notes.md`](instructions/prepare-release-notes.md).
Run it from the project directory once the `-SNAPSHOT` development cycle
is over and the release is ready to cut. The skill works in six steps:

1. **Generate `a.md`.** The skill runs
  [`scripts/prepare_release_notes.sh`](scripts/prepare_release_notes.sh),
  which reads the `X.Y.Z-SNAPSHOT` version from the first line of
  `version.txt`, finds the last git tag, and writes `a.md` with the
  conventional-commit titles since that tag grouped by type, plus the
  full commit list. The script stops with a fatal error when the version
  is not a `-SNAPSHOT`, or when the last tag already matches `X.Y.Z`
  (the notes are already prepared).
2. **Write the summary into `version.txt`.** The skill reads `a.md` and
  writes a release-notes summary following
  [`templates/prepare-release-notes.version-txt.template.txt`](templates/prepare-release-notes.version-txt.template.txt):
  a first line `X.Y.Z-SNAPSHOT -- <title>`, three witty title / subtitle
  pairs, a main theme paragraph, an optional secondary theme, and a
  `Key changes` list of three items.
3. **Pause for a title choice.** The skill stops and shows the three
  title / subtitle pairs, then asks the author to pick one.
4. **Finalize `version.txt`.** The chosen title becomes the release
  title on the first line; the two other pairs stay in the list below.
5. **Update the changelog.** The skill calls
  `tools\dev_workflow\update-changelog.bat`, which folds the
  `version.txt` summary into `CHANGELOG.md` under the new version.
6. **Report and hand off.** The skill confirms `version.txt` and
  `CHANGELOG.md` are written, and points the author at the next step:
  `brel`.

### Create the release with brel

`/prepare_release_notes` stops before the tag on purpose. To cut the
release, the author runs `brel`, which drives the project build with the
`rel` parameter:

1. `brel` calls `tools\dev_workflow\t_build.bat rel`.
2. `t_build.bat` reads `rel` as an update-version argument and calls
  `update-version.bat`, which drops the `-SNAPSHOT` suffix, commits the
  release version, and creates the `vX.Y.Z` git tag.
3. When the build succeeds, `t_build.bat` marks the `vX.Y.Z` tag with a
  `[valid]` marker. When it fails, `t_build.bat` resets the pre-release
  state and deletes the tag, so a failed release leaves no half-tagged
  `main` behind.

### Dependency on the senv_dev_workflow build tooling

Step 5 above and the whole `brel` path are not part of `llm-shared`.
They depend on the project carrying the build tooling from
[`senv_dev_workflow`](https://github.com/VonC/senv_dev_workflow) under
its own `tools\dev_workflow\` directory:

- `update-changelog.bat`  --  called in step 5 to write `CHANGELOG.md`.
- `t_build.bat`  --  called by `brel`; the `rel` parameter selects the
  release path of the build.
- `update-version.bat`  --  called by `t_build.bat` to turn the
  `-SNAPSHOT` version into the release version and tag it.

The split of ownership is clean. `llm-shared` owns the release-notes
side: the `prepare_release_notes` skill, its instruction body, the
`prepare_release_notes.sh` script, and the `version.txt` summary
template. `senv_dev_workflow` owns the build side: `t_build.bat`,
`update-version.bat`, `update-changelog.bat`, and the `senv.bat` wiring
that `brel` runs through. A project that uses the release stage of this
workflow needs both repositories wired into its `tools\` directory.

## License rationale: why MIT fits llm-shared

`llm-shared` is released under the MIT License ([LICENSE.md](LICENSE.md)).
The reasons MIT was picked, rather than a copyleft license such as the
GPL:

- **The repository exists to be copied into other projects.** The
  README section "How to use llm-shared from another project" tells the
  reader to copy or symlink `.claude/skills/` into `~/.claude/skills/`,
  or to hand a single `instructions/<skill>.md` file to another LLM as
  context. MIT puts no condition on those copies beyond keeping the
  copyright notice, so a downstream project can take one skill without
  having to think about license terms.
- **No copyleft reach into downstream documents.** Running these skills
  produces drafts, requirements, designs, plans, and commit messages
  inside someone else's repository. A copyleft license would raise an
  unclear question about whether those generated documents inherit the
  license. MIT removes that question: the workflow artifacts belong to
  the project that ran the workflow.
- **It matches the code already in the tree.** The bundled
  `tools\batcolors` helper already ships under the MIT License with the
  same copyright holder. Using MIT for the whole repository keeps one
  license across the tree and avoids any compatibility check between
  `batcolors` and the rest of the files.
- **The content is small, adaptable parts.** Most files are prompts,
  markdown instructions, templates, and short helper scripts meant to be
  forked and edited per project. A short, widely understood, attribution-only
  license fits a toolbox whose value is in being reused, not in
  restricting what people build from it.

The MIT choice covers only `llm-shared` itself. The build tooling from
`senv_dev_workflow` (see the section above) lives in its own repository
under its own license terms, and is not affected by this decision.
