# Agent instructions

## Running shell commands

Before any tool call that runs a shell command, follow `rules/run_commands.md`.

* Read and search files with the harness file tools, never through an environment wrapper.
* When a wrapper is required, chain exactly one simple command with no nested shell quoting.
* Read targeted slices, never whole-document dumps.
* When a command fails with a quoting or parse error, rewrite it more simply instead of re-running the same command or changing permissions.

## Execution permissions

This repository's review and groundhog workflows are designed to run unattended.

The active Codex configuration is expected to permit the repository operations required by those workflows, including writes to Git metadata when staging or committing is part of the task.

* Do not request interactive approval or escalation.
* Do not switch an approval policy to `on-request`.
* Do not repeatedly retry an operation that has already failed because of a sandbox restriction.
* If an operation that is required by the workflow is unexpectedly sandbox-blocked, first distinguish that from a command, quoting, environment, or test failure.
* If it is genuinely blocked by the active Codex permissions, report the specific blocked operation and the effective permission mismatch. Do not attempt to work around the restriction by weakening user or global configuration on your own.
* Ordinary clarification questions to the user remain allowed when they are useful.

## Long-running commands and quota hygiene

Do not turn long-running work into frequent model polling.

* Avoid repeated short polling of long-running commands, processes, or agents.
* When an execution is healthy and still running, do not repeatedly re-enter the model merely to check whether it has completed.
* For code-mode `wait`, prefer `yield_time_ms = 60000` for long-running work.
* Do not use 1000 ms or 10000 ms polling intervals unless there is a concrete reason to expect useful output that soon.
* If a 60000 ms wait returns while a process is still healthy and running, wait again rather than duplicating, restarting, or re-investigating the same work.
* For delegated agents, prefer long `wait_agent` waits and avoid unnecessary `list_agents` or other status-only polling.
* If a delegated agent remains healthy after a wait timeout, wait again rather than interrupting, replacing, or duplicating it.
* Do not interrupt or duplicate healthy background work merely because a wait interval expired.

## Review role isolation

Whenever acting in a review exchange, follow the role-session isolation rules in `instructions/review-requestor.md`.

A requestor publishes and then waits. It must never spawn, start, delegate, invoke, or message a reviewer agent or session.

A reviewer reviews or waits. It must never spawn, start, delegate, invoke, or message a requestor agent or session.

Each role rejects a task initiated by the automated counterpart.

Waiting for the counterpart must follow the long-running-work rules above: avoid frequent status-only polling and use long waits where supported.

## groundhog (pytest reset loop)

To drive the test suite to its global objective, with every test passing and coverage at the project gate, follow `instructions/groundhog.md`.

Trigger this whenever the user asks to run groundhog, `ghog`, or to fix tests and coverage.

A walk is finished only when `a.ghog.status` at the project root reads:

```txt
state=done
```

A growing `a.ghog.log` proves nothing.

Poll with:

```txt
ghog status
```

Never redirect `ghog status`.

Never replace it with a direct read of `a.ghog.status`; only the command probes the recorded PID.

Interpret its status as follows:

* Exit 6: the walk is still live. Start nothing else and check again later.
* Exit 7: the walk was killed. Relaunch it according to `instructions/groundhog.md`.
* Any other exit code: treat it as the walk's own verdict.

When the harness can kill long calls, run the walk detached:

```txt
ghog day --detach
```

Do not redirect that detached launch.

Never size a timeout around a full walk.

Never rerun a walk that may still be alive.

Never monitor a live walk with repeated process listings, direct status-file reads, sleeps followed immediately by another poll, or other busy-polling mechanisms.

Space status checks at least 60 seconds apart. For a full walk, prefer intervals of several minutes when no useful state change is expected sooner.

If `ghog` or its prerequisite Git operations are genuinely blocked by the active Codex permissions, follow the execution-permissions section above. Do not request an approval that the active policy cannot provide and do not repeatedly replay the blocked command.

## Diataxis documentation order

Whenever a task creates or maintains a Diataxis documentation set, present and link its categories in this order:

1. explanation
2. tutorials
3. how-to guides
4. reference

Keep every page focused on exactly one Diataxis purpose.

## LLM-specific Markdown adapters

When adding or modifying an LLM-specific skill, prompt, workflow, or other Markdown adapter, follow `rules/llm-specific-adapters.md`.
