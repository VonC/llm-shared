# Document review mode from opt-in to recovery

## CDC revision that introduces review-mode documentation

The review-mode umbrella separates functional delivery from user
documentation. Its first five requirements implement the shared exchange,
specification requestor and reviewer, and implementation-code requestor and
reviewer. Ordered item 6, `review-mode-docs`, follows those settled behaviors
and asks for one coherent operational account without making the functional
requirements depend on prose that was still changing.

The documentation must cover the shared requestor role, both reviewer roles,
their canonical instructions and LLM-specific adapters, the opt-in marker,
transient and versioned artifacts, automated intermediate rounds, the
convergence-only human gate, mandatory identity, timeouts, disagreements,
recovery, escalation, templates, launchers, and supporting tools.

## User story for review-mode documentation

As a user running AI-assisted specification or implementation review, I want
the project documentation to explain the complete review-mode workflow and its
recovery paths, so that I can start the correct role, interpret every durable
state and artifact, and know exactly when the LLM may continue and when a human
decision is required.

## Current behavior in v0.11.0

- The shared exchange and all four specification and implementation roles are
  implemented through canonical instructions, host adapters, templates,
  launchers, typed states, and durable transcripts.
- `README.md` and the existing `wiki/` Diataxis tree describe the established
  writer self-review cycle and general human checkpoints, but they do not give
  users a complete operational path through the new independent review-mode
  exchange.
- No connected documentation set currently explains the `a.review-mode`
  marker, exact request and answer identities, automated intermediate rounds,
  convergence confirmation, lease reclaim, stopped-state recovery, and role
  authority together.
- Existing reference pages list general artifacts, launchers, templates, and
  skills without defining the complete review-mode command, state, outcome,
  and exit contract.

## Gap to close for review-mode documentation

1. Add an entry point from the project documentation to a review-mode
   Diataxis set that covers explanation, tutorials, how-to guides, and
   reference in that order.
2. Explain why requestor, reviewer, and human authority are separate, why
   reviewer recommendations remain advisory, and why the transcript is
   append-only rather than working context.
3. Provide complete first-use tutorials for specification review and
   implementation-code review, including intermediate change rounds and the
   final human gate.
4. Provide task-focused procedures for enabling review mode, invoking each
   reviewer, reading the returned artifact paths, handling lease expiry,
   recovering or escalating stopped exchanges, and resuming a durably
   authorized owning action.
5. Define the exact marker, artifact locations, identity fields, roles,
   states, transitions, commands, outcomes, exit behavior, validation
   evidence, and transcript rules in reference documentation.
6. Document how `.agents`, `.claude`, and `.agent` adapters locate canonical
   shared instructions without copying the workflow policy.
7. Connect the new pages to the existing wiki navigation and related project
   pages without mixing explanation, tutorial, how-to, and reference purposes
   on one page.

## Required workflow coverage

### Opt-in and identity

- Review mode is active only when the project-root `a.review-mode` marker is
  present.
- Specification summaries name the umbrella or state `none`, the exact
  reviewed specification, and a positive round number.
- Implementation-code summaries name the umbrella, exact implementation
  plan, implementation step, and round.
- Human-readable fields must agree with the machine-readable exchange
  identity; nearby filenames are never substitutes for the returned exact
  artifact path.

### Artifacts and dialogue lifecycle

- Transient `a.review-requested.*` and `a.review-answer.*` artifacts stay at
  the project root under the existing `a.*` ignore rule.
- Versioned `review.*` transcripts stay beside the reviewed specification or
  implementation plan. Agents append durable entries and do not reread the
  transcript as working context.
- Requestors publish identity-bearing requests. Reviewers read only the exact
  returned request, publish an advisory answer through the shared exchange,
  and consume the request only when the answer is ready.
- Changes-requested answers lead to automated writer correction and another
  round. Specification consolidation and code commit readiness alone enter
  the convergence gate.

### Human authority and recovery

- At specification convergence, only the human may choose `Consolidate` or
  `Revise and review again`. At code convergence, only the human may choose
  `Commit` or `Rework and review again`.
- The documentation distinguishes a live lease, an abandoned request or
  answer, an artifact-free abandoned mid-round, convergence, durable owning
  authorization, escalation, inconsistent evidence, and interrupted repair.
- Recovery procedures identify the owning role and the difference between an
  ordinary guarded reclaim, human-authorized forced reclaim or completion,
  repair, resolution, archival, cancellation, and a fresh round.
- Timeouts, repeated no-progress, disagreement, identity mismatch, missing
  mandatory evidence, and unusable artifact shapes state when automation must
  stop for human intervention.

## Diataxis documentation boundaries

- Explanation pages describe the authority model, durable state, and reasons
  for file-based coordination.
- Tutorials walk through a complete first specification-review exchange and a
  complete first implementation-code exchange.
- How-to guides give bounded procedures for activation, reviewer invocation,
  artifact interpretation, reclaim, recovery, escalation, and continuation.
- Reference pages define exact files, fields, commands, states, outcomes,
  validation evidence, and exit codes.
- Each page has one Diataxis purpose. Navigation and handoff lists present
  categories in the order explanation, tutorials, how-to guides, then
  reference.

## Concrete artifact examples

- `a.review-requested.feature-request.vX.Y.Z.slug.md` is a transient
  specification request at the project root.
- `a.review-answer.code.vX.Y.Z.slug.md` is a transient implementation-review
  answer at the project root.
- `review.feature-request.vX.Y.Z.slug.md` is a durable specification transcript
  beside the reviewed requirement.
- `review.code.vX.Y.Z.slug.md` is a durable code-review transcript beside the
  implementation plan.
- `a.review-active.<identity>.md`, consumed tombstones, transition locks, and
  retained validation manifests are protocol-owned evidence whose exact paths
  come from launcher results rather than filename discovery.

## Code and documentation references

- `instructions/review-requestor.md`: shared requestor sequence, artifact
  authorship, convergence, and recovery rules.
- `instructions/spec-reviewer.md`: independent specification-review behavior
  and authority boundary.
- `instructions/code-reviewer.md`: independent implementation-review
  assessment, evidence, repair, and publication sequence.
- `instructions/spec-review-requestor.md` and
  `instructions/code-review-requestor.md`: writer-side specialization of the
  shared requestor sequence.
- `templates/review-request.template.md`,
  `templates/review-answer.template.md`,
  `templates/spec-review-request.template.md`,
  `templates/spec-review-answer.template.md`,
  `templates/code-review-request.template.md`,
  `templates/code-review-answer.template.md`,
  `templates/review-specification-transcript.template.md`, and
  `templates/review-code-transcript.template.md`: shared, family-specific,
  and transcript rendering contracts.
- `bin/review_exchange.bat`, `bin/spec_review_request.bat`,
  `bin/spec_review_answer.bat`, `bin/code_review_request.bat`,
  `bin/code_review_evidence.bat`, `bin/code_review_answer.bat`, and
  `bin/prompt_workflow.bat`: stable exchange, renderer, evidence, and `pw`
  routing boundaries users and adapters call.
- `wiki/reference/pw-launcher.md`: existing `pw` routing reference that the
  independent review-mode journeys must extend or cross-link.
- `wiki/how-to/answer-a-review-round.md` and
  `wiki/explanation/why-the-llm-reviews-its-own-work.md`: existing self-review
  pages whose terminology must be distinguished from independent review mode.
- `wiki/README.md`, `wiki/explanation/`, `wiki/tutorials/`, `wiki/how-to/`, and
  `wiki/reference/`: existing Diataxis navigation and target roots.

## Acceptance criteria for review-mode documentation

1. `README.md` and `wiki/README.md` lead users to a connected independent
   review-mode documentation set, distinguish it from the existing self-review
   loop, and preserve the required Diataxis category order.
2. The independent review-mode explanation states the requestor, reviewer, and
   human authority boundaries and explains why convergence recommendations
   never authorize consolidation or commit.
3. Exactly one cross-linked first-use tutorial walks through specification
   review and exactly one walks through implementation-code review from opt-in
   to the human gate.
4. How-to coverage gives executable procedures for enabling review mode,
   running each reviewer, interpreting artifacts, reclaiming an expired live
   exchange, and escalating or resolving a stopped exchange. Human-only forced
   operations appear only inside a marked human-decision section that states
   their precondition and the evidence each operation preserves or removes.
5. Reference coverage defines the exact marker, transient and durable artifact
   paths, identity fields, roles, states, commands, outcomes, and exit
   behavior without directing users to edit protocol artifacts by hand.
6. The docs use `self-review loop` for the human-answered open-question cycle
   and `independent review mode` for the marker-gated two-agent exchange,
   distinguish automated intermediate rounds from convergence, and list the
   exact human choices for both review families.
7. Timeout, abandonment, no-progress, disagreement, inconsistent artifacts,
   interrupted transitions, ordinary reclaim, forced human recovery, and
   durable owning-action resumption are each documented with their owner and
   stopping rule. Forced recovery is never presented as an ordinary automated
   procedure.
8. A new or changed page that summarizes a policy-owned rule states that rule
   in its own words, names the canonical instruction that owns it as
   authoritative for agent policy, and does not copy that policy body. A page
   that only gains a cross-link or an inventory row carries no such obligation.
   The adapter table records wrapper location, command prefix, delegation
   boundary, and per-host coverage, including an absent wrapper.
9. Each new or changed wiki page serves one Diataxis purpose, and navigation
   presents explanation, tutorials, how-to guides, then reference.
10. `ghog day`, `git diff --check`, and `git diff --cached --check` pass; every
    added or changed local link and named repository path resolves; and the
    changed Markdown is manually checked against `.markdownlint.json`, with
    MD024 and MD025 explicitly kept active. No repository-wide Markdown checker
    is created by this effort.
11. This effort documents settled review-mode behavior only; it does not add
    the repository-wide Markdown checker from umbrella item 7 or the
    read-only commit-plan launcher from item 8.
12. A versioned acceptance-to-page coverage table maps criteria 1 through 9 to
    the exact pages that satisfy them and records criteria 10 through 12 as
    evidence entries rather than page mappings. It also records the disposition
    of the candidate inventory pages: `wiki/reference/skills-catalog.md`,
    `wiki/reference/artifact-files.md`,
    `wiki/reference/aliases-and-launchers.md`,
    `wiki/reference/templates.md`,
    `wiki/reference/automation-and-direct-invocation.md`, and
    `wiki/reference/repository-layout.md`. Implementation may omit a candidate
    only when the table records why that page is unaffected. The table is
    effort documentation under `docs/v0.11.0/` rather than a wiki Diataxis page,
    so criterion 9 does not apply to it.

## Requirement clarifications

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Use dedicated Diataxis pages for complete journeys and contracts, with concise links from existing entry points. | Gap to close; Diataxis documentation boundaries; criteria 1 and 9 | One large page would mix purposes; extending only existing pages would leave incomplete coverage. |
| Q02 | Provide exactly one cross-linked first-use tutorial for each review family. | Gap to close; Diataxis documentation boundaries; criterion 3 | One branching tutorial would lose linear first use; one tutorial plus reference would leave the other family without a complete journey. |
| Q03 | Keep tutorials and ordinary how-to pages at skill-command level, and put the complete launcher contract in reference and recovery material. | Gap to close; Code and documentation references; criteria 4 and 5 | Launcher-only documentation is too low-level for first use; skill-only documentation cannot define recovery or exit behavior. |
| Q04 | Derive a complete state, owner, action, and result matrix from shipped typed states and outcomes, with focused procedures for multi-step recovery. | Human authority and recovery; criteria 4, 5, and 7 | A small common-state list omits recovery; prose alone is hard to scan and easier to drift. |
| Q05 | Use artifact naming grammar only for orientation; the `paths` object in the launcher's final standard-output JSON is authoritative. | Opt-in and identity; Concrete artifact examples; criterion 5 | Filename inference can select nearby artifacts; treating standard-error progress as authoritative conflicts with the launcher contract. |
| Q06 | Document one canonical workflow plus an adapter table covering wrapper location, command prefix, delegation boundary, and per-host gaps. | Gap to close; Code and documentation references; criteria 6 and 8 | Per-host copies duplicate policy; a canonical-only account hides missing wrappers and invocation differences. |
| Q07 | Keep the self-review loop and independent review mode, compare them explicitly, and cross-link where opt-in and human stops differ. | Current behavior; Required workflow coverage; criteria 1, 2, and 6 | Replacing the established loop breaks existing guidance; leaving the concepts unrelated preserves ambiguous terminology. |
| Q08 | Update the two top-level entry points and assess the six named inventory pages, recording every disposition in the coverage table. | Code and documentation references; criteria 1 and 12 | Updating only top-level navigation leaves discovery gaps; updating every inventory page without assessment creates redundant edits. |
| Q09 | Validate with `ghog day`, both Git whitespace checks, link and path resolution, and manual markdownlint-rule review while deferring checker automation. | Criterion 10 | Depending on umbrella item 7 breaks ordering; manual review alone gives weak executable evidence. |
| Q10 | Use `self-review loop` and `independent review mode` as stable display names while retaining existing filenames. | Current behavior; criteria 1, 2, and 6 | Renaming files breaks links; continuing to call both concepts review mode leaves the authority boundary ambiguous. |
| Q11 | Make the acceptance-to-page coverage table a versioned deliverable. | Criterion 12 | An implementation-plan-only map is too late for requirement verification; prose claims provide no auditable mapping. |
| Q12 | Let wiki pages define the user-facing contract in their own words while canonical instructions remain authoritative for agent policy. | Criterion 8 | Copying instruction bodies creates a second policy source; linking without a user-facing contract makes reference pages incomplete. |
| Q13 | Present forced recovery only in marked human-decision sections that state authority, preconditions, and evidence effects. | Human authority and recovery; criteria 4 and 7 | Omitting forced operations leaves recovery incomplete; presenting them as ordinary steps weakens the human boundary. |

No open questions remain; all requirement clarifications are settled and the
design phase has enough information to proceed.

## Dependencies and scope boundary

This feature depends on the completed `review-exchange-core`,
`spec-review-requestor`, `spec-reviewer`, `code-review-requestor`, and
`code-reviewer` efforts. Those requirements continue to own protocol behavior,
state transitions, templates, launchers, reviewer assessment, writer
continuation, and human authority. `review-mode-docs` owns the project and
Diataxis documentation that teaches and defines that settled behavior.

## File-based IO cost clarification for review-mode documentation

- Normal readers follow explicit entry-point and page links; independent review
  mode does not add a metadata crawl or directory scan to a requestor or
  reviewer response path.
- Reference construction reads the named canonical instructions, launchers,
  templates, and typed models once during documentation authoring rather than
  adding runtime discovery.
- Acceptance validation traverses only the delivered documentation set and its
  declared local links, so its filesystem cost stays linear in the bounded set
  of changed pages and evidence rows.
