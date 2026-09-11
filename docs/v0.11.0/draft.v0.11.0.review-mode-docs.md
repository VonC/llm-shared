# Document the review-mode workflows

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

## Selected umbrella item

This draft continues ordered item 6, `review-mode-docs`, from the review-mode
umbrella. It documents the settled behavior delivered by
`review-exchange-core`, `spec-review-requestor`, `spec-reviewer`,
`code-review-requestor`, and `code-reviewer`; it does not redefine those
functional requirements.

The documentation must cover the shared requestor role, the `spec-reviewer`
and `code-reviewer` skills, their templates and scripts, the opt-in marker,
artifacts, automated intermediate rounds, the convergence-only human gate,
mandatory summary identity, dialogue lifecycle, timeouts, disagreement
handling, and supporting tools.

## Operational behavior to document

Review mode is enabled by the project-root `a.review-mode` marker. Transient
request and answer artifacts stay at the project root under the existing
`a.*` ignore rule, while each versioned `review.*` transcript stays beside the
specification or implementation plan it records. Agents append to that
transcript as durable history and do not reread it as working context.

Specification-review summaries identify the umbrella or state that none
exists, the exact reviewed specification, and the positive round number.
Implementation-code summaries identify the umbrella, exact implementation
plan, implementation step, and round. Human-readable identity must agree with
the machine-readable exchange identity.

Ordinary intermediate rounds are automated. A requestor consumes a
changes-requested answer, applies or assesses the feedback, and publishes the
next round. The responder reads only the exact pending request artifact,
publishes its answer through the shared exchange, and leaves consolidation or
commit authority with the requestor and human.

Convergence occurs only when a specification reviewer recommends
consolidation or a code reviewer recommends commit readiness. The durable
human gate then offers `Consolidate` or `Revise and review again` for
specification work, and `Commit` or `Rework and review again` for code work.
Reviewer recommendations remain advisory. Human guidance and overrides are
recorded in the transcript, and another-round choices reset the no-progress
counters.

The documentation must distinguish lease expiry and guarded reclaim from
timeouts, abandonment, no-progress, disagreement, inconsistent artifacts,
escalation, repair, and human-authorized recovery. It must explain when
automation stops, which role owns each recovery action, and when a human must
intervene.

## Roles, adapters, and artifacts to document

The shared requestor documentation must explain how specification and code
writers activate an exchange, publish identity-bearing summaries, process
intermediate answers, present convergence, and resume a human-authorized
owning action. Reviewer documentation must explain how `spec-reviewer` and
`code-reviewer` wait for their exact request, assess only their permitted
scope, publish an advisory answer, and avoid writer or human authority.

Document the LLM-specific wrappers under `.agents`, `.claude`, and `.agent`
that locate canonical shared instructions instead of copying workflow policy.
Cover the request and answer templates, launchers, state and evidence tools,
transcript behavior, retained validation manifests, and recovery commands
needed to inspect or repair an exchange without editing protocol artifacts by
hand.

Use concrete artifact examples such as
`a.review-requested.code.vX.Y.Z.slug.md`,
`a.review-answer.feature-request.vX.Y.Z.slug.md`,
`review.code.vX.Y.Z.slug.md`, and
`review.feature-request.vX.Y.Z.slug.md`. Explain that answer publication
consumes the matching request and that convergence evidence is retained until
the human choice is durably recorded.

## Documentation structure and constraints

Update the project documentation and the appropriate existing Diataxis wiki
pages so users have one coherent operational view. Keep each page focused on
one purpose and present the categories in this order: explanation, tutorials,
how-to guides, then reference.

Explanation covers the role and authority model. Tutorials provide a complete
first specification-review or code-review dialogue. How-to guides cover
enabling review mode, running each reviewer, interpreting artifacts, resuming
an expired exchange, and escalating to a human. Reference pages define exact
markers, paths, identities, states, commands, outcomes, and exit behavior.

The documentation follows the settled behavior of the five prerequisite
requirements. It must not make those requirements depend on prose still being
written, pull in the repository-wide Markdown checker from item 7, or add the
read-only commit-plan launcher from item 8.
