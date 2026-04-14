---
name: write-design
description: 'Write a design document named `docs\design.vX.Y.Z.<topic>.md`, in markdown format, from a user story, a bug report, or a feature request included in your context. The generated document should be clear and concise, and should include all relevant information for the development team to understand the need and implement a solution.'
user-invocable: true
metadata:
  - "This skill is used to write a design document named `docs\design.vX.Y.Z.<topic>.md`, in markdown format, from a user story, a bug report, or a feature request included in your context. The generated document should be clear and concise, and should include all relevant information for the development team to understand the need and implement a solution."
  - "The argument hint for this skill is 'Provide the version vX.Y.Z and topic, for example "v9.3.0 sentinels".'"
argument-hint: 'Provide the version vX.Y.Z and topic, for example "v9.3.0 sentinels".'
---

Check your prompt for version vX.Y.Z and topic (for instance "v9.3.0 sentinels")

Write a design document named `docs\design.vX.Y.Z.<topic>.md`, in markdown format, from a user story, a bug report, or a feature request included in your context. The generated document should stay at design level: describe scope, confirmed facts, constraints, target behavior, and major design areas. Do not turn the document into an implementation plan.

Follow the template from #file:./design.template.md to write the design document, and adapt it as needed if some sections are not relevant for the specific design you are writing.

Notes for the writer:

- Keep section titles specific to the topic and version; do not reuse generic repeated titles.
- Use the current-behavior and target-behavior sections only when the design depends on comparing flows.
- Put facts already confirmed from the codebase in the confirmed-facts section.
- Put implementation steps, file-by-file task lists, and rollout steps in the later implementation plan, not in the design.
- Do not add the open-questions section in this skill output; It will be addressed by `.github\skills\review-ask-questions\SKILL.md` in a later follow-up review step.
