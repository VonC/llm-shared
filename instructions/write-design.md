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
