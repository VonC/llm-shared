# Write design document

ultrathink: take the time to reason through the user story, bug report, or feature request deeply before drafting the design document, so you can identify all the relevant information and constraints, and provide a clear and concise design that addresses the need.

Check your prompt for version vX.Y.Z and topic (for instance "v9.3.0 sentinels").

Read [`../rules/docs_layout.md`](../rules/docs_layout.md). Resolve the effort
directory from the parent of the requirement or canonical draft named in the
prompt. Write `design.vX.Y.Z.<topic>.md` beside that source document. Do not add
a topic subdirectory. The generated document should stay at design level:
describe scope, confirmed facts, constraints, target behavior, major design
areas, and security architecture with threat surface. Do not turn the document
into an implementation plan.

Follow the template from [`write-design.template.md`](../templates/write-design.template.md) to write the design document, and adapt it as needed if some sections are not relevant for the specific design you are writing.

Notes for the writer:

- Keep section titles specific to the topic and version; do not reuse generic repeated titles.
- Use the current-behavior and target-behavior sections only when the design depends on comparing flows.
- Put facts already confirmed from the codebase in the confirmed-facts section.
- Address trust boundaries, untrusted input handling, and threat vectors in the dedicated security architecture section, applying least privilege, fail-safe defaults, and secret protection.
- Put implementation steps, file-by-file task lists, and rollout steps in the later implementation plan, not in the design.
- Do not add the open-questions section in this skill output; it will be addressed by the `review-ask-questions` skill (see [`review-ask-questions.md`](review-ask-questions.md)) in a later follow-up review step.

## Handoff

Before using or showing a host-prefixed workflow command, read
[`../rules/command_prefix_char.md`](../rules/command_prefix_char.md) and use its
prefix rule.

When `<effort-dir>\design.vX.Y.Z.<slug>.md` is written, hand the cycle on to
its review, with no menu and no go-ahead. From the project root, in a PowerShell
shell, run the explicit post-write form through the `pw skill` launcher (see
[`run-pw.md`](run-pw.md) for the non-interactive invocation; the bare `pw`
alias does not resolve in a tool shell):

- `pw skill --after-write design`

The explicit post-write form prints the exact
`<command-prefix>review-ask-questions on <design-path>` line (with the prefix
selected by `command_prefix_char.md`) even if the new design already contains
text that resembles a settled decision marker. Read that line and run it
straight away: a handoff is the go-ahead to perform the next step now, so do not
stop to ask whether to proceed, and do not compose the next prompt yourself.

To hold the chain here instead — to read the design before the review runs — pass the literal phrase `stop here` in this skill's argument when you invoke it. With `stop here` in the argument, write the design and skip this handoff.
