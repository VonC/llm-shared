# Automation and direct invocation

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 The ownership contract for llm-shared skills, launchers, and lower-level
tools. "Automated" means the AI owns the next command after the user starts a
workflow; it does not remove the human approval points documented by that
workflow.

## Invocation model

This page is a read-only ownership map rather than an executable procedure. Use
it before invoking a command directly to determine which surrounding checks and
human validation gates the normal AI-orchestrated workflow would provide.

## User starts, AI orchestrates

| Workflow | Normal invocation | What the AI calls | Human role |
| --- | --- | --- | --- |
| Document pipeline | Ask for `process-draft` or the required writing skill | writing, explicit `pw skill --after-write` review handoffs, consolidation, then state-based bare `pw skill` | approve an umbrella-derived child, answer structured questions, and validate settled documents |
| Implementation step | Ask for `implement-step N` | Groundhog, implementation check, missing-work repair, and grouped-commit preparation | validate decisions and approve commit replay |
| Independent review mode | Start the normal writing or implementation skill with `a.review-mode` present | `pw`, the family requestor, the shared exchange, and bounded waits | start the independent reviewer separately; decide at convergence or a marked human-recovery decision |
| Release preparation | Ask for `prepare-release` with release intent | planner, conflict previews, synchronization, merges, notes, version updates, and preparation commit | approve topology and notes; run `brel` later |
| History sanitization | Ask for `sanitize-git-history` | contextual scan, rule validation, fresh-clone rewrite, and re-audit | approve replacement rules and destructive phase; push later if desired |
| Reports and maintenance skills | Ask for the named skill | activity/dashboard builders, doc review, file split, or slow-test workflow | validate the requested output |
| Session continuity | Ask for `list-session` to see every folder's paused session, `status-session` to inspect one, `pause-session` to save, or `resume-session` to continue | read-only list and status; snapshot, note and session journal updates on pause; context reconciliation, usage receipt and session journal entry on resume | choose when to inspect, stop and return; explicitly use `--force` to reread a consumed prompt; resolve any still-pending decision |

The user should not be told to run an internal prerequisite merely because it
has a command-line interface. The owning skill calls it and reports the
evidence.

Review roles remain isolated: a requestor never starts or messages a reviewer,
and a reviewer never starts or messages a requestor. Durable state naming the
next actor does not authorize the other automated role to launch it.

`list-session`, `status-session`, `pause-session` and `resume-session` are LLM
commands, not launcher names or `pw` subcommands. List and status report the
waiting prompts or latest recorded work without modifying artifacts or
continuing tasks.
Resuming preserves applicable authorization and pending gates.
Its usage receipt confirms context recovery before task execution; it grants
no new approval. The [session guide](../how-to/pause-and-resume-a-session.md)
also distinguishes checkpoint recovery from the review-specific bare `resume`.

## Commands normally called inside automation

| Command or tool | Normal owner | Call it directly when |
| --- | --- | --- |
| `prepare_release_plan.bat` | `prepare-release` | developing the planner or diagnosing one topology without preparing a release |
| `sensitive_history_scan.bat` / `shscan` | `sanitize-git-history` | performing an ad hoc read-only audit or developing replacement rules |
| `ghog day` and subcommands | implementation and fix skills | learning the loop, diagnosing locally, or running the same quality gate without an AI session |
| `pw handoff` / `pw skill` | workflow skills | debugging state routing, reproducing an explicit `--after-write` handoff, resuming a known phase, or using the interactive menu |
| `review_exchange.bat` and family renderers | review requestors and reviewers | diagnosing one exact exchange or carrying out a documented recovery operation |
| `gcba.bat` | grouped-commit approval flow | replaying a reviewed `a.commit` plan from a console |
| release-note scripts and changelog tools | `prepare-release` | developing or diagnosing the release-note half independently |

Direct use is supported, but it narrows the contract: the caller must supply
the context, ordering, validation, and follow-up that the owning skill normally
provides.

## Commands intentionally run by a human

| Command or tool | Why it stays direct |
| --- | --- |
| `brel` | it finalizes the version and creates the release tag after preparation review |
| plugin/workflow registration commands | they change the user's AI-host configuration |
| local wiki server | it owns a foreground browser/server session stopped with Ctrl-C |
| `git_history_diagrams.bat` / `ghdiag` | it is a documentation-maintenance generator, not part of release execution |
| presentation rebuild | it creates reviewable presentation artifacts on demand |

An AI may execute a direct maintenance command when the user asks for that
maintenance task. The distinction is about the normal workflow owner, not a
technical restriction.

## Release foundation invocation

The v0.14.0 release foundation is reachable through `bin\release_workflow.bat`,
`bin\release_alias.bat` and the native bootstrap entry; their syntax is in
[Aliases and launchers](aliases-and-launchers.md#-release-foundation-launchers).
This section is the contract an automation relies on.

### Availability boundary of the foundation

This version ships the foundation (runtime readiness, project and Git
identity, strict configuration, read-only artifact resolution, managed writes,
the project operation lock, input transport and result rendering) and two
operations: `version` and `versions`, described in
[Version sources](version-sources.md). Any other operation name ends with
status 2, `Release operation '<name>' is unavailable in this tooling checkout`.
Changelog generation, release transactions, installation and upgrades, the
move of existing build and `senv` callers, alias installation and consumer
cutover belong to later items of the sibling release tooling effort.

### Runtime readiness and its repair

Each launcher reads `venvs\release-runtime.v1.txt`, which this checkout's setup
publishes after preparing its environment (`senv.bat` calls
`bin\release_runtime_record.bat`). The bootstrap then checks that the running
interpreter and prefix are the recorded ones, that the platform is Windows x64,
and that the release dependency group is installed. A missing or invalid
record, another checkout's interpreter or a missing dependency ends with
`Release readiness failed: ... Run this checkout's setup` and status 2. The
repair is to run that checkout's setup again; nothing is written to the
consumer project or the tooling checkout on the way.

### Selector variables in PowerShell

A selector names a variable instead of carrying a value, so a path with `%`,
`^`, `!` or `"` reaches the engine unchanged. In PowerShell, assign the
variable fresh for each call and remove it in `finally`; the launcher reads it
once, and a later change has no effect on a running operation:

```powershell
$env:RELEASE_PROJECT = 'C:\work\project 100%'
try {
    & "<llm-shared>\bin\release_workflow.bat" <operation> --project-root-env RELEASE_PROJECT
} finally {
    Remove-Item Env:RELEASE_PROJECT
}
```

The variable belongs to the PowerShell session, not to the call. On Ctrl+C,
Windows PowerShell 5.1 waits for the launcher, then stops the script: the
line after the call never runs, but `finally` does. Without `finally`, Ctrl+C
or a terminating error leaves the variable set in the session, where the next
call that names it would read the old value.

When the call's output is captured, as in `$out = & ...`, Ctrl+C makes
Windows PowerShell 5.1 end the launcher itself: `$LASTEXITCODE` is `-1`, cmd
asks no question and the console stays on codepage 65001. The engine still
reports `interrupted`; a lock record left by an engine that was ended is
recovered by the next call as a dead owner.

From Windows PowerShell 5.1, pass input with `--input-file` or
`--input-file-env`, not through a pipe. Its pipe to a native command adds a
byte-order mark and a trailing line break, and it can replace non-ASCII
characters even when `$OutputEncoding` is set to UTF-8.

### Native automation without the batch question

On Ctrl+C, the running operation ends with status 1 and releases its project
lock, but cmd then asks `Terminate batch job (Y/N)?`, in the console's
language, before a batch launcher returns, also when Windows PowerShell started
it. Answering no lets the launcher return 1 and restore the caller's codepage.
Answering yes ends the batch at once: the launcher's status is lost (a
`cmd /c` caller sees 255) and the console stays on codepage 65001. With
standard input redirected from `NUL`, cmd still prints the question, reads the
end of input and lets the launcher return 1. An automation
that must not meet that question calls the recorded
interpreter directly with `-I -X utf8 tools\release_workflow\bootstrap.py
--entry-kind explicit-native -- <operation> ...`. The native entry is also the
only one that accepts `--text`.

### Statuses and streams

| Status | Meaning |
| --- | --- |
| `0` | the operation succeeded |
| `1` | the operation failed or was interrupted; any other child status becomes 1, with the original status in a diagnostic |
| `2` | the invocation, the preflight or the runtime readiness failed; no operation ran |
| `3` | a version transition's restoration is incomplete: a stop that requires recovery, never a failure to retry ([Version sources](version-sources.md#statuses-of-the-version-commands)) |

Standard output carries operation data, standard error carries diagnostics;
both are UTF-8 with LF line endings. The batch launchers switch the console
to codepage 65001 for the call and restore the caller's codepage on exit. When
no input source is given and standard input is not a console, the call is
non-interactive and never prompts. On a console without `--non-interactive`,
an operation that requires input asks `Release input:` on standard error and
reads one line; with `--non-interactive` it ends with status 2 instead.

Inherited `PRJ_DIR` and the other legacy location variables have no
authority: the project comes only from the explicit root or, for the alias
launcher, the current directory. A disagreeing `PRJ_DIR` produces a warning,
and none of those variables reaches Git.

Related: [Where the human stays in the loop](../explanation/where-the-human-stays-in-the-loop.md),
[Independent review mode contract](independent-review-mode-contract.md),
[Skills catalog](skills-catalog.md), and [Aliases and launchers](aliases-and-launchers.md).
