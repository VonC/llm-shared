# Agent instructions

## Running shell commands

Before the first shell command, read and follow:

```txt
rules/run_commands.md
```

Treat that file as the authoritative shell-execution policy. Do not duplicate or improvise alternate quoting, wrapper, retry, or output-handling rules.

## Execution permissions

This repository's review and groundhog workflows are intended to run unattended.

Its project-local Codex configuration is expected to provide:

```txt
Full access / never
```

* Do not request interactive approval or escalation.
* Do not switch the approval policy to `on-request`.
* If an operation that should be available is unexpectedly blocked, distinguish a genuine permission problem from a command, quoting, environment, Git, or test failure.
* If the effective permissions do not match the repository's expected configuration, report the mismatch rather than weakening global configuration or repeatedly retrying the blocked command.
* Ordinary clarification questions to the user remain allowed when useful.

## Review role isolation

Whenever acting in a review exchange, follow:

```txt
instructions/review-requestor.md
```

A requestor publishes and then waits. It must never spawn, start, delegate, invoke, or message a reviewer agent or session.

A reviewer reviews or waits. It must never spawn, start, delegate, invoke, or message a requestor agent or session.

Each role rejects a task initiated by the automated counterpart.

When waiting for the counterpart, follow the global long-running-work and quota-hygiene instructions. Do not busy-poll merely to check whether the other role has progressed.

## groundhog (pytest reset loop)

When the user asks to run groundhog, `ghog`, or to fix tests and coverage, read and follow:

```txt
instructions/groundhog.md
```

Treat that file as the authoritative groundhog workflow.

In particular:

* There is no standalone `groundhog` executable or alias.
* Do not infer completion merely from a growing log.
* Do not launch a duplicate walk that may still be running.
* Use the workflow's status and detached-execution mechanisms as documented there.
* Follow the global quota-hygiene instructions when waiting for long-running work.

Do not copy or invent an alternate groundhog lifecycle in this file.

## Diataxis documentation order

Whenever a task creates or maintains a Diataxis documentation set, present and link its categories in this order:

1. explanation
2. tutorials
3. how-to guides
4. reference

Keep every page focused on exactly one Diataxis purpose.

## LLM-specific Markdown adapters

When adding or modifying an LLM-specific skill, prompt, workflow, or other Markdown adapter, follow:

```txt
rules/llm-specific-adapters.md
```
