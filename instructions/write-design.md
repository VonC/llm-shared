# Write design document

ultrathink: take the time to reason through the user story, bug report, or feature request deeply before drafting the design document, so you can identify all the relevant information and constraints, and provide a clear and concise design that addresses the need.

Check your prompt for version vX.Y.Z and topic (for instance "v9.3.0 sentinels").

Write a design document named `docs\design.vX.Y.Z.<topic>.md`, in markdown format, from a user story, a bug report, or a feature request included in your context. The generated document should stay at design level: describe scope, confirmed facts, constraints, target behavior, and major design areas. Do not turn the document into an implementation plan.

Follow the template from [`write-design.template.md`](../templates/write-design.template.md) to write the design document, and adapt it as needed if some sections are not relevant for the specific design you are writing.

Notes for the writer:

- Keep section titles specific to the topic and version; do not reuse generic repeated titles.
- Use the current-behavior and target-behavior sections only when the design depends on comparing flows.
- Put facts already confirmed from the codebase in the confirmed-facts section.
- Put implementation steps, file-by-file task lists, and rollout steps in the later implementation plan, not in the design.
- Do not add the open-questions section in this skill output; it will be addressed by the `review-ask-questions` skill (see [`review-ask-questions.md`](review-ask-questions.md)) in a later follow-up review step.

## Handoff

When the `design.vX.Y.Z.<slug>.md` is written, hand the cycle on to its review, with no menu and no go-ahead. From the project root, in a PowerShell shell, run the `pw` launcher (`<llm-shared>\bin\prompt_workflow.bat`, the `pw` alias of the project environment) in skill mode:

- `pw skill`

`pw skill` prints one bare next-step command, derived from the documents on disk — here `/review-ask-questions on docs/design.vX.Y.Z.<slug>.md` (a `/` prefix in a Claude session, a `$` prefix in a Codex session). Read that line and run it straight away: a handoff is the go-ahead to perform the next step now, so do not stop to ask whether to proceed, and do not compose the next prompt yourself.

To hold the chain here instead — to read the design before the review runs — pass the literal phrase `stop here` in this skill's argument when you invoke it. With `stop here` in the argument, write the design and skip this handoff.
