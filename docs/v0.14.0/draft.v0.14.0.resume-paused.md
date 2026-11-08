# Resume every paused agent pane in one command

- Type: feature-request
- Test group: whole suite
- Target version: v0.14.0
- Documentation layout: docs/v0.14.0/
- Slug: resume-paused
- Deferred follow-up: [senv tuitp integration](#deferred-senv-integration-after-resume-paused)

## Context for resume-paused

`pause-session` leaves one resume prompt per checkout,
`a.session-resume.local.md` in its artifact home, and `resume-session`
consumes it, writing the receipt `a.session-resume.used.local.md` with the
prompt's SHA-256. When the agents run in persistent TUIOS sessions (one
session per checkout, each shown in its own Windows Terminal tab, with a
Claude pane, a Codex pane or both), resuming after a pause means visiting
every tab, often typing a clear first, then `/resume-session` in Claude or
`$llm-shared:resume-session` in Codex, in the right pane of the right
session.

A launcher can do that for the panes it starts (senv's `tuitp` does), but
not for agents that are already running: after a night of pauses, the panes
are still open, idle, and nothing resumes them.

On 2026-11-07 an agent did it by hand from its own TUIOS pane, with the
`tuios` CLI, for six panes in six sessions (five Claude, one Codex). It
worked, and it showed what a program must handle:

This agent-run experiment is historical TUIOS evidence. The requirement's
confirmed Q16=B instead permits only a human shell launch of the delivered
command, including when an agent is asked to run it.

- From Git Bash, a text argument that starts with `/` is rewritten as a
  Windows path: `/clear` reached Claude as the Git installation folder
  followed by `/clear` (such as `C:/Program Files/Git/clear`), which Claude
  took as a prompt (one wasted turn). A program that calls `tuios` with an argument list, without a
  shell, avoids it.
- From inside a pane, `tuios ask-agent -s OTHER -w NAME` fails with `no window
  found matching <own pane id>`: `--from` defaults to the caller's pane and is
  looked up in the target session. Clearing the `TUIOS_*` pane variables is
  not an option (an agent host may refuse it as weakening security). What
  works from any pane: `tuios ask-agent --select 'session:S name:N' --yes`.
  A selector term is split on spaces and quotes do not group it, so a pane
  name with a space is matched with `*` in its place (`name:Claude*api`),
  after checking that the selector matches exactly one pane.
- A Codex pane reports no TUIOS harness: `list-agents` shows harness
  `(none)` and source `program`, from the OSC 7501 reports of llm-shared's
  own `program_status.py` (`program_status[].app` is `codex`). Its state can
  be days old (a "working" report from two days earlier was still shown), and
  `ask-agent` answers `ok` with state `idle` whether or not Codex took the
  text. Only the screen proves it: `tuios capture-pane --scrollback` shows
  `› $llm-shared:resume-session`, then `• Working`.
- A Claude pane shows that it took a command in `tuios agent-log`
  (`prompt /resume-session`), and a clear as `session started (clear)`.
  The person often clears a pane already, right after copying its
  conversation: a second clear is then useless.
- `/clear` leaves the pane's background shells running: a resumed agent
  that re-arms a background watcher then runs two of them.
- The agent running the program cannot clear itself, and typing into its own
  pane would land after its turn.
- A Codex pane that resumed may at once wait on the person (a question): it
  must never receive typed text then.

## Goal for resume-paused

User clarification on 2026-11-08: "one command and it is done". One human launch must complete the resolved pause resumption and requestor/reviewer assignments, including required author and role overrides, without asking for confirmation again. Carry the invocation's authorization into the shared resume workflows; amend those workflows before implementing this command. Q25's subsequent user amendment requires target selection from information saved by `pause-session`, without pane-selection arguments or a selection question. Unresolvable identity follows the existing skip/report rules. Preserve target protections and proof of actual role restoration.

The pause handoff must record the intended resumed agent and requestor/reviewer
assignments, including each target's host, TUIOS session and pane identity,
resolved checkout, observation time and identifying evidence. Keep the saved
pause author and current roles separate from intended roles, including any
user-directed switch. Record the exact review exchange for a pair and explicit
not-applicable values for a single-agent pause. Evolve the shared pause
instruction and template to capture this routing automatically before the
bulk command is implemented. The command validates it against live panes;
multiple panes running the same LLM require no new user selection. Missing,
stale or conflicting routing is reported without input to unresolved targets
or an interactive question, including for older handoffs without this data.

Ship a `resume_paused` command (a `bin` launcher and a `tools` module, as the
other llm-shared tools) that lists the TUIOS agent panes whose checkout holds
a resume prompt still waiting, and types the matching resume command into the
right pane of the right session, for Claude and Codex at least.

User clarification on 2026-11-07: support resuming a given tab with the LLM
roles switched. For example, when Claude was requestor and Codex reviewer,
the person can want Codex to resume as requestor and Claude as reviewer.
After identifying and resuming the requestor, check for an actual LLM
counterpart in that tab. A CMD shell is not a reviewer. If a counterpart
exists, send its native review-resume instruction to resume as reviewer,
claiming that role if needed because the requestor has just resumed.
The requirement questions must cover saved per-tab role assignments, proof
of the new requestor's takeover and a run that resumes the requestor but cannot yet
restart its reviewer. Earlier pausing-agent target rules below describe the
original default, before this explicit role-switch clarification.

```txt
resume_paused [--dry-run] [--clear] [--except NAME[,NAME...]]
```

Q27=B adds the optional `--switch-roles NAME[,NAME...]` argument; the
requirement holds the current synopsis.

### Find the agent panes

- Read `tuios list-agents --all-sessions --json`: session, pane name and id,
  folder (`cwd`), state, `ready`, harness, program status.
- A Claude pane has harness `claude-code`. A Codex pane has a
  `program_status` record whose app is `codex`; its pane name is only a
  fallback.
- The checkout of a pane is its folder, the way a launcher starts agents in
  their checkout.

### Find the prompts still waiting

- Apply the state table of `resume-session` to each checkout: the artifact
  home (`.reviews`, or the one `.review-artifacts.ini` declares), the prompt,
  its SHA-256 against the receipt, the receipt's project root.
- The prompt's first line names the agent that paused it
  (`# <agent-id>: Resume session: <task title>`): `claude` for Claude,
  `chatgpt` for Codex. Its `Session role` line says whether the pause was a
  review requestor's.
- The session journal is an index, not an authority: it can name the
  checkouts and their pause time, never replace the prompt and receipt check.

### Leave alone a checkout that is already resuming

A checkout whose prompt is already being resumed gets no resume command, in
any of its panes, even when the agent resuming it is not the agent that
paused it: the program assumes the person deliberately overrode the pauser
with a new resumer. The signs, any of which is enough:

- a valid receipt matches the prompt's bytes, whatever its `Resumed by` and
  `Agent override`;
- the session journal holds a resume entry for that checkout later than its
  pause entry;
- a pane of that checkout received `resume-session` or `review-resume` after
  the pause time: a `prompt` line in its agent log for Claude, the command on
  its screen for Codex;
- a pane of that checkout waits on the person with the resume-session
  override question ("was paused by ...; do you want to override that and
  resume it here?"), which comes before any receipt is written.

The report names the resuming pane and agent:
`SKIP api: already resuming in api/Codex api (chatgpt), paused by claude`.

### Choose the pane and the command

- Q25 supersedes the original first-pausing-agent-pane proposal: select the
  intended target from the pause handoff's routing, validated against the
  live session, pane, checkout and host. Do not ask for pane-selection arguments
  or choose a first matching pane. Use `/resume-session` for Claude and
  `$llm-shared:resume-session` for Codex.
- Each skipped pane or checkout gets one line with its reason: listed in
  `--except`; on `needs_input` or blocked on a question; mid-turn; the
  caller's own pane (`TUIOS_PANE_ID`), historically reported as "run
  resume-session here" in the agent-run experiment; Q16=B instead requires
  a human shell launch of the delivered command;
  a prompt that names no agent; no pane of the pausing agent in that
  checkout; a checkout already resuming.
- `--except` takes a comma-separated list matched against the session name,
  the pane name and the checkout folder name.

### Clear before resuming with --clear

- Claude: type `/clear`, then Enter, wait for the pane to go quiet, and
  confirm `session started (clear)` in its agent log. Skip the clear when
  the log already shows one after the pause time.
- Codex: the command that starts a new conversation (to confirm on the Codex
  version in use: `/new` or `/clear`), confirmed on the screen.
- A clear that cannot be confirmed stops that pane: no resume command
  follows it.

### Type the command and prove it was taken

User-relayed observation on 2026-11-07: a command can be typed into Codex's
input box without being submitted. The reported screen shows the command
with no `Ask Codex to do anything` line below it, while `ask-agent` reports
`ok` and the pane remains idle. Readiness before typing and submission after
typing are separate checks. The requirement's confirmed Q11=C permits one
Enter for this run's proven unsubmitted command, followed by another check
for `Working`. It protects the person's draft and forbids retyping or repeated
Enter when submission is uncertain; the requirement defines the evidence and
pane-targeted delivery for independent review.

- Type with the call already proven:
  `tuios ask-agent --select 'session:S name:N' --yes --stall-timeout 60000
  --timeout 100000 --lines 1 --json -- <command>`, one worker per pane, all
  panes at once.
- Claude: taken when the agent log shows the `prompt` line of the command.
- Codex: taken when the screen shows the command, then `• Working`.
- Call `tuios` with argument lists, never through a shell.

### Preview with --dry-run

`--dry-run` types nothing and prints what a run would do, one line per checkout
holding a prompt (Q15=A):

```txt
RESUME api/Claude api: /resume-session for 'Fix the parser', paused by claude at 2026-11-07 00:06
RESUME web/Codex web: clear, then $llm-shared:resume-session for 'Review step 4', paused by chatgpt at 2026-11-07 01:05
RESUME docs/Claude docs: already cleared at 00:42, /resume-session for 'Update the guide', paused by claude at 2026-11-07 00:30
SKIP lib: already resuming in lib/Codex lib (chatgpt), paused by claude
HISTORICAL agent-run example: SKIP senv/Claude senv: this pane, run resume-session here
```

### Constraints for resume-paused

- Never type into a pane on `needs_input`, nor into a pane that holds a
  draft.
- The program only reads prompts, receipts and the journal: `resume-session`
  stays the only writer of a receipt and a resume journal entry.
- No dependency on senv or its launcher: Windows Terminal tab titles, when a
  launcher records them, are an optional extra.
- Python 3.12 compatible; the tests run with a fake `tuios` runner, no live
  TUIOS needed.
- Exit status follows the requirement's Q10=A and Q23=A rules, with one
  result line per checkout holding a prompt under Q15=A.

## Deferred senv integration after resume-paused

Q05 was confirmed as Option A on 2026-11-07: deliver the command for existing
panes first. Integration means changing senv's `tuitp` launcher to reuse the
shared command for its launch-time resume handling, instead of maintaining
a separate waiting-prompt check.

- [ ] After the shared command is implemented and validated, open a separate
  senv effort for `tuitp` integration. Revisit it at the resume-paused completion
  handoff and when next changing senv's launch-time resume behavior.

The [requirement's deferred-work checklist](feature-request.v0.14.0.resume-paused.md#deferred-senv-integration-follow-up)
is the detailed record. Carry that link into the design, implementation plan
and completion handoff; retain it when consolidating questions. No target
version or calendar reminder has been assigned to this later work.

## Notes for resume-paused

The original draft questions below are resolved in the requirement:

- Reviewer panes: when the pause was a review requestor's, a launcher that
  starts the panes also sends `review-resume as reviewer` to the other
  agent. For running panes, send it only to a reviewer pane that `--clear`
  cleared too (a reviewer not cleared keeps its context), always, or never?
  Resolved by Q01=D: activate an eligible actual LLM counterpart after requestor
  takeover, without requiring a clear. Q22=A never clears the counterpart.
- Mid-turn panes: Q02=A skips them immediately.
- Codex at rest: since its state can be stale, decide from the screen (an
  empty `›` prompt line with no `• Working`) rather than from `list-agents`?
  Resolved by Q03=A, subject to the requirement's current screen and input checks.
- Background shells left by `/clear`: report them (`N shells` on the status
  line) so the person can stop the old ones? Q04=A reports the indicator and
  leaves those shells running.
- Should senv's `tuitp` later call this program for the panes it starts,
  instead of keeping its own copy of the waiting-prompt check
  (`bin\tuitp_resume.py`, `waiting_prompt`)? Q05=A defers this to the tracked
  follow-up above.
