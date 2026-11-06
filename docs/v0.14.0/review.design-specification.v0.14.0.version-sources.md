# Specification review transcript for v0.14.0

- Exchange: specification/design-specification/v0.14.0/version-sources
- Reviewed document: docs/v0.14.0/design.v0.14.0.version-sources.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-05T10:53:05+01:00
- Exchange: specification/design-specification/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for design-specification version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.version-sources.md
Review round: 1

### Requestor assessment for design-specification version-sources (round 1)

Writer assessment of the version-sources design, round 1.

The design answers the consolidated feature request
`docs/v0.14.0/feature-request.v0.14.0.version-sources.md`, whose fifteen
requirement clarifications (Q01 to Q14 option A, Q15 option B) were decided by
the user and reviewed in five rounds. It does not reopen any of them. It
settles what the requirement leaves to design: interfaces, the source model,
the write and restoration mechanism, configuration syntax, the persistent tag
eligibility evidence, the ancestry rule, output formats and exit statuses.

The confirmed-facts table was built from the current code and data before
writing: item 1's empty handler table and one-word parser, the 0/1/2 status
renderer, the schema registry families, the per-file managed writes, the
operation lock's need for a prepared artifact home, the empty `release`
dependency group, the Git observation seam used by tests, and the real tag
histories, lock formats and POM layouts of llm-shared, my-project and
workspace-halo.

Open questions: sixteen are proposed (Q01 to Q16), each with a recommended
option and a pending user decision. They cover the design choices with real
alternatives:

- tags and ranges: engine-tag evidence (Q01), strictness of the ancestry rule
  (Q02), the `versions range` entry for instruction-driven readers (Q03);
- the transition: the public status 3 for incomplete restoration (Q04), the
  plan-then-lock sequence (Q05), an interrupted `set` (Q06), evidence shared
  with item 5 (Q07);
- writing: standard-library parsing with byte-span replacement (Q08), CRLF in
  pattern sources (Q09);
- formats: allowed forms per adapter (Q10), supported npm lock formats (Q11),
  Maven internal-dependency identification (Q12);
- configuration and detection: component-root syntax (Q13), scope of form
  overrides (Q14), candidate discovery (Q15), the anchor's first line (Q16).

Q11 recommends narrowing the design text: the body currently lists npm lock
formats 1 to 3, and the writer, reviewing it, recommends dropping format 1,
because its compatibility evidence would need npm 6 and no consumer uses it.

The writer considers the question set sufficient for a design: every
remaining point is either an implementation detail for the plans (exact
signatures, module names, fixture tool versions, test organization) or already
decided by the requirement. Please assess the whole design, whether a design
question is missing, whether the options and recommendations are sound, and
whether the design contradicts the requirement, the umbrella or item 1's
foundation.

### Change summary for design-specification version-sources (round 1)

Round 1 has no preceding round. The reviewed document is new:

- `docs/v0.14.0/design.v0.14.0.version-sources.md` was written by
  `write-design` from the consolidated feature request
  `docs/v0.14.0/feature-request.v0.14.0.version-sources.md` (committed in
  `e1614b6`), the child draft and the umbrella.
- `review-ask-questions` then appended the open-questions section with Q01 to
  Q16 through `oqm`.
- The design is untracked; the feature request, the child draft and the
  umbrella are unchanged.

### Writer response for design-specification version-sources (round 1)

Writer response:

No reviewer feedback exists yet for this exchange. Three writer notes for this
first round:

- The design changes item 1's foundation in five places (operation tokens in
  the CLI, public status 3, the version schema in `SHIPPED_SCHEMAS`, a public
  lock-ownership check, typed Git observations). Each is listed in the section
  "Foundation changes required by the version domain"; please check that none
  breaks an item 1 contract that its design or tests rely on.
- The requirement lists only `version`, `versions list`, `check` and `set`. The
  design adds a read-only `versions range [<tag>]` operation to expose the
  selector to instruction-driven readers; Q03 asks whether that belongs here.
- The design files are written with CRLF line endings, because `oqm` rewrites
  every line ending when it places the questions section; this is a tooling
  matter, not part of the reviewed content.

### Reviewer focus for design-specification version-sources (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.design-specification.v0.14.0.version-sources.md`
- `.reviews/a.review-requested.design-specification.v0.14.0.version-sources.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-05T11:02:52+01:00
- Exchange: specification/design-specification/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification version-sources round 1

Recommend changes-requested and another automated review round. The design has a sound overall shape, and I agree with the proposed choices A for Q01–Q10 and Q12–Q16, and B for Q11. All sixteen user decisions remain pending. Agreement with those choices does not cover the substantive gaps below or authorize consolidation.

I assessed the complete current design against the consolidated requirement, the relevant umbrella contracts, and the existing CLI, Git, path, managed-write and operation-lock implementation. The confirmed requirement decisions, including Q15 B, remain settled. This is a design assessment, not implementation validation.

#### F1: Validate tag conflicts before excluding the target boundary for design-specification version-sources (round 1)

The deterministic ancestry rule, steps 3–4 (design lines 560–566), removes the target's own version/commit before detecting conflicts. Consider commit A tagged `1.0.0`, followed by commit B tagged `v1.0.0`, both historical and eligible. `versions range v1.0.0` removes B first, then accepts A as its predecessor. It silently accepts the different-commit alias conflict that requirement AC14 explicitly forbids. Two different stable versions on the target commit can likewise lose their conflict when one is removed.

Validate and group all reachable relevant stable boundaries, including the tag target, before excluding the target's one validated boundary from predecessor candidates. Exclusion must remove same-commit aliases together, and must not erase a conflict. Add both counterexamples to acceptance cases. Q02 A remains my choice.

Also make the typed observations sufficient for step 6: a set of commits reachable from the target plus independent eligible tips does not establish whether an ambiguous tag is before or after the selected baseline. Return the needed ancestry information, or add a bounded query relative to the baseline. A fixed call count can remain a goal; it must supply the information the rule uses.

#### F2: Specify Python workspace and cross-component local-link rejection for design-specification version-sources (round 1)

The Python section (lines 299–315) recognizes a workspace only through a member list in `uv.lock`; it gives no Python local-link detection rule. The npm section's dependency checks do not cover Python. A participating Python root with `[tool.uv.workspace]` and no optional lock can therefore pass these rules. Two declared Python components connected through a `[tool.uv.sources]` path can also be synchronized while the unsupported reference is ignored.

Requirement Q08 and AC9 require rejection of every participating npm or uv workspace arrangement and local link between participating components before writes. Define manifest-side uv workspace detection even with no lock, supported lock-side workspace indicators, and Python path/editable/local-reference detection. Resolve references against the declaring root and compare physical destinations with all participating roots. Specify the treatment of `workspace = true` rather than attempting to interpret it as a filesystem path. Preserve external references and participation filtering, including tool-only pairs. Add no-lock workspace and Python cross-component path-link acceptance cases.

#### F3: Reject overlapping byte ownership as well as duplicate field identifiers for design-specification version-sources (round 1)

The combining rule (lines 251–259) rejects only duplicate `(physical path, field)` claims. A pattern source can capture the same bytes as `[project].version` under a different field identifier; two differently named patterns can do the same. Different forms can then propose different replacements for the same bytes. Distinct field identifiers do not establish disjoint ownership.

Before mutation, group edits by physical file, validate span bounds and reject overlapping claimed spans, naming both claimants, including when the replacement happens to agree. Keep disjoint owned fields in one file supported and compose their edits from one captured original without offset drift. This is a completion of Q08 A, not a reason to replace its parser-and-span approach. Add built-in/pattern and pattern/pattern overlap cases.

#### F4: Check interrupted evidence before the clean-plan return for design-specification version-sources (round 1)

The ownership section (lines 433–443) returns `unchanged` immediately when the locked plan is empty, then describes the leftover-evidence stop. A process killed after its last replacement but before verification/cleanup leaves a fully synchronized set plus unfinished evidence. Repeating the same target follows the empty-plan return and can bypass the required recovery stop.

Under the lock, check for unfinished evidence before every success path, including `unchanged`. State that ordering explicitly and add this interruption point as an acceptance case. Distinguish evidence currently owned by a supplied lifecycle transaction from unrelated unfinished evidence, so legitimate lifecycle reuse is not rejected. This preserves Q05 A and Q06 A.

#### F5: Define finalization separately from deleting recovery originals for design-specification version-sources (round 1)

The write section deletes evidence after verification (line 463), while the restoration section promises rollback on any failure after the first replacement (line 467). If deletion removes some originals and then fails, that rule attempts rollback with originals already missing. The status-3 promise to name every retained original can no longer hold. Lock-release failure after evidence deletion has the same undefined rollback boundary.

Add a missing design question about the completion boundary and cleanup failures. I recommend a durable, verified-complete state before destructive evidence cleanup. Before that boundary, failures restore using the complete originals; after it, cleanup or lock-release failures report that the new source state was applied and cleanup failed, without attempting rollback from partially deleted evidence. Keep the completion marker until the other evidence cleanup finishes, distinguish completed residue from interrupted mutation on the next invocation, and define the nonzero result and retained diagnostics. An alternative is deliberately retaining complete evidence for later explicit cleanup, with its storage and operational costs stated. Neither alternative permits deleting originals and then promising unconditional rollback.

Give the new question distinct options, pros/cons, a recommendation and a pending user decision. Suggested Q17: "When is a verified version transition complete, and what does a cleanup failure report?" Suggested A is the durable completion boundary above; suggested B retains complete evidence until explicit cleanup. I choose A. Public status 3 remains reserved for incomplete restoration; a completed transition with cleanup failure needs an explicitly described execution outcome.

Also bind lifecycle reuse to the same physical project: checking that a supplied handle owns some operation is insufficient if it belongs to another project. The public ownership check and transaction-directory authorization must establish the current invocation's project and managed artifact boundary. The existing private `_require_owned` checks record ownership, not equality with another invocation's project.

#### F6: Bound Maven version inheritance to a synchronized owner for design-specification version-sources (round 1)

The Maven section (lines 330–348) allows an absent project version inherited from its parent and leaves external parents unchanged. A participating root POM with an external parent at `1.0.0` and no own version has an effective project version of `1.0.0`. Setting the anchor to `2.0.0` cannot synchronize that project by the listed edits: there is no own version span and the external parent must stay unchanged.

State that inherited project versions are supported when their effective version is supplied by a participating internal parent chain that the transition updates. Reject an inheritance chain ending in an unchanged external parent when there is no owned project version, before writing, with the remedy to declare a literal project version. This preserves requirement Q15's inheritance exception without silently reporting an unsynchronized Maven project as successful. Include a supported internal-parent chain and the unsupported external-parent-root example. Retain the rule that external parent versions are never edited.

#### F7: Make the lock-compatibility evidence prove locked acceptance for design-specification version-sources (round 1)

The evidence section (lines 506–517) compares owned fields against a real tool's version-change fixture while requiring all other bytes to remain unchanged. That establishes field fidelity, but does not establish requirement Q10/AC8's stronger claim that a previously current pair remains accepted by a locked install without rejection or rewrite.

Specify that recorded compatibility evidence includes the real supported tool accepting the before pair and accepting the adapter-edited after pair in its locked/frozen mode without changing the manifest or lock. Record tool/version, relevant schema and root-source layout, command outcome and before/after file hashes. These are fixture-generation/compatibility checks, not opportunistic tool execution in `set`, and exact tool versions and fixture paths may still be selected in the plans. Cover each supported uv root layout and npm lock format, or explicitly reject an unproved combination. State how the supported uv schema/revision boundary is registered rather than leaving an unconstrained "schema this adapter supports" promise.

#### Wording corrections that do not require new scope for design-specification version-sources (round 1)

- The sentence "Each change keeps item 1's existing contracts and tests intact" (line 608) contradicts Q04 and the documented 0/1/2 foundation normalization. Describe the five deliberate extensions and the relevant contract/test updates, while preserving unrelated foundation guarantees. The five extensions themselves are justified; adding `versions range` stays within selector exposure.
- Qualify the claim that every failure before the first write leaves the artifact home unchanged. Preparing the home, taking the lock and writing evidence already mutate it before a source overwrite. Distinguish artifact-free initial validation, source-unchanged pre-overwrite failures and explicit artifact cleanup/retention.
- A file view may cache once per phase, not once per entire `set` invocation. Replanning under lock, comparing before replacement, verification and restoration verification deliberately reread files. Correct both the common model and read-count statements.
- Q05 A's claim about every rejected command being artifact-free overstates the requirement and its own second locked preflight. Q05 B need not prepare artifacts for a malformed target either: the proposed argument validator already rejects that target before project validation. Compare the alternatives using valid input that later fails source validation, not a typo already rejected by both.

### Question verdicts for design-specification version-sources round 1

All entries below assess proposed answers. No design answer has been confirmed by the user, and this review does not record any human decision.

| Question | Independent verdict and choice |
| --- | --- |
| Q01 | In scope, with distinct annotation-marker and external-evidence alternatives. Choose A: the required trailer plus later standalone `[valid]` supplies clone-visible evidence without a second marker. Keep the explicit ambiguous cases. Define matching as a standalone trailer line, consistently with the umbrella, rather than a substring found anywhere in release notes. C cannot meet ordinary-clone evidence requirements without an additional fetch contract. |
| Q02 | In scope; stopping, highest-version preference and date preference have materially different consequences. Choose A: strict conflicts protect every range consumer. Correct F1 so exclusion does not hide an explicit alias conflict, and provide the ancestry observation needed to classify evidence relative to the baseline. The current implementation sketch does not yet deliver the proposed answer. |
| Q03 | In scope, not a reopening of the requirement's ownership. Choose A: an existing `versions` handler is a reasonable home for the required command-facing selector. B is feasible but adds a top-level command; C defers a useful shared entry to its consumer. Adoption remains with item 7. |
| Q04 | Necessary foundation extension. Choose A: public 3 gives CLI and in-process callers the distinct incomplete-restoration result. B and C should be labeled as failing the requirement's public distinction, rather than equivalent compliant alternatives. Update the inherited status contract and corresponding tests explicitly. |
| Q05 | A valid design tradeoff, but the advantages currently overclaim artifact-free failures. Choose A: the authoritative capture and plan are under the operation lock, including no-edit runs. Correct the comparison with B and the per-phase read claims. Ensure F4's evidence check precedes the empty-plan result. C permits success without observing another operation's ownership. |
| Q06 | Necessary interruption policy, with distinct manual, automatic and command-driven recovery options. Choose A within this item's scope, provided F4 is fixed and diagnostics make the originals/manifest usable for manual recovery. This policy does not answer F5's separate completed-transition cleanup case. |
| Q07 | In scope; the three alternatives materially change capture ownership and retention. Choose A: caller-local retained evidence and one restoration routine fit lifecycle reuse. Bind the supplied lock and directory to the same project, distinguish owned lifecycle evidence from abandoned evidence, and define failure retention consistently with F5. Item 5 still owns encompassing transaction retention. |
| Q08 | In scope with materially different dependency and fidelity costs. Choose A: parsed values plus format-aware byte spans preserve the requirement's bytes without expanding the runtime closure. Add the cross-adapter overlap rejection in F3. A span's equal text alone must not substitute for identifying the actual owned syntactic field. |
| Q09 | A useful explicit regex behavior choice. Choose A: an LF matching view makes the existing anchored pattern work on CRLF while byte mapping preserves the file. The options clearly expose deliberate raw-CR behavior as a tradeoff. |
| Q10 | In scope, with meaningful Maven publication-risk alternatives. Choose A: Python core, npm all three, Maven snapshot and explicitly declared pattern forms cover the confirmed defaults and npm exception. Nothing in the confirmed requirement forces a Maven core override. Keep external versions and unsupported property expressions outside the write set. |
| Q11 | In scope because the design owns supported lock schemas and evidence. Choose B, supporting npm lock 2/3 and rejecting 1 with an actionable remedy. The body 1/2/3 versus proposed B difference is disclosed in the request and is a pending human choice, not an undisclosed inconsistency to consolidate now. Avoid calling npm 7/8 "current"; evidence may legitimately use explicitly supported older tool versions. Apply F7 regardless of the selected formats. |
| Q12 | In scope and meaningfully different from literal-only skipping or general property resolution. Choose A: resolve literals and exact `${project.groupId}`, reject potentially internal unresolved groups rather than silently treating them as external. Preserve requirement Q15's exact `${project.version}` exception only in internal dependency/dependency-management version fields. Add F6's inheritance boundary without broadening property resolution. |
| Q13 | In scope; individual managed paths, a list and path-as-section have distinct validation costs. Choose A: `[component:<id>] root = ...` reuses the shipped schema and managed-path rules. Existing managed-path authorization already rejects nested repository boundaries. No new executable project configuration is warranted. |
| Q14 | In scope, with distinct global/per-component costs. Choose A: one override per adapter across participating roots fits the one-project-version scope and known consumers. No current evidence justifies adding per-component overrides. |
| Q15 | In scope; tracked-only, tracked plus untracked and a walk expose different candidates and costs. Choose A: one Git inventory includes new components and respects exclusions. Be precise that tracked files stay visible even if a later ignore rule matches them; ignored untracked files are omitted. Preserve the existing managed-path/nested-repository boundary. |
| Q16 | In scope grammar clarification; lenient-title and ignored-trailing-text alternatives have clear silent-error risks. Choose A: reject non-whitespace trailing text without the `--` separator. Retain empty title/notes and token-only anchors as the confirmed requirement permits. |

The question set is not yet complete: add Q17 for the completion boundary and cleanup failure outcome described in F5. The other findings complete existing rules or enforce already confirmed boundaries; they do not require reopening requirement questions or automatically creating more human decisions for routine implementation details.

### Requested changes for design-specification version-sources round 1

Requested changes:

Changes requested; the remaining work exceeds wording polish.

- F1: validate reachable tag conflicts before removing the tag target's validated boundary, and supply ancestry information for evidence between baseline and target.
- F2: reject uv workspace declarations without a lock and Python local links between participating components, under the confirmed participation rules.
- F3: reject overlapping claimed byte spans even when field identifiers differ; retain support for disjoint edits to one file.
- F4: check unfinished evidence before the locked no-edit success path, with an explicit exception for current caller-owned lifecycle evidence.
- F5: add the missing completion/cleanup question and define a safe finalization boundary, cleanup failure status, residue classification and project-bound lifecycle ownership.
- F6: permit inherited Maven project versions only through a synchronized internal owner; reject an external-parent root lacking its own version rather than reporting successful synchronization.
- F7: define compatibility evidence that observes actual locked/frozen acceptance without rewrites for supported tool/schema/layout combinations.

Revise and review again. All proposed design decisions, including the new cleanup question, remain for the human; the reviewer has authorized neither consolidation nor implementation.

### Writer instructions for design-specification version-sources round 1

Revise the reviewed design and publish another automated review request. Do not consolidate the open questions or mark any answer as a user decision.

1. Repair F1–F7 in the design body and add their concrete counterexamples to the acceptance cases.
2. Add Q17 about finalization/cleanup, with distinct alternatives, pros and cons, a recommendation and a pending user decision. I recommend the durable-completion alternative in F5.
3. Preserve Q01–Q16 identifiers and the confirmed requirement. Carry forward the recommended A choices and Q11 B as proposals only. Refine the Q04 and Q05 arguments as described in the verdicts.
4. Correct the foundation-contract, artifact-home and per-phase read-count claims. Name deliberate changes to existing contracts and tests instead of claiming all are untouched.
5. In the next request, map each finding to the revised section and report any remaining disagreement or evidence limitation. Exact implementation signatures, module layout, fixture tool versions and test organization can remain plan work; the behavioral and recovery boundaries cannot.

### Final reviewer decision for design-specification version-sources round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-05T11:17:29+01:00
- Exchange: specification/design-specification/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification version-sources (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.version-sources.md
Review round: 2

### Requestor assessment for design-specification version-sources (round 2)

Writer assessment of the version-sources design, round 2.

Every round 1 finding and wording correction was accepted and applied; none was
declined. The questions now hold Q01 to Q17, each with a recommended option
and a pending user decision; no decision is recorded or inferred. Q17 is new,
as requested.

Mapping of findings to the revised design:

| Finding | Where it is now handled |
| --- | --- |
| F1, tag conflicts before excluding the target | "The deterministic ancestry rule": steps reordered so all reachable stable tags, the target's included, are grouped and checked for conflicts before the target's boundary is removed as a whole; step 6 classifies tags between baseline and target. "Git queries of the selector": a table of four queries, each named with the step it serves, including tags reachable from the target and not from the baseline |
| F2, uv workspaces and Python local links | "Python with uv": manifest-side `[tool.uv.workspace]` rejection with or without a lock, root workspace members matched against participating roots even when the root is tool-only, lock-side member lists, `workspace = true` rejected as a workspace reference, `path` sources and `file:` direct references resolved against the declaring root and compared physically with participating roots, external references unchanged |
| F3, overlapping byte ownership | "Combining all detectors": claims grouped by physical file, span bounds checked, any overlap rejected whatever the field identifier or replacement, disjoint edits composed from one captured original. "Locating values with the standard library": the scanner identifies the syntactic field; text equality is only a cross-check |
| F4, evidence before the clean result | "Ownership and the authoritative plan": ordered steps, the evidence check first and before every success path including `unchanged`; owner recorded in the manifest so the supplied lifecycle transaction's evidence is accepted and any other unfinished evidence stops `set` |
| F5, completion boundary and project binding | New "Completion boundary and cleanup failures" (proposed in Q17 A); "Restoration and its distinct failure" restores only before the boundary and states the `writing`/`complete` handling after a kill; "Reuse by a lifecycle caller" binds the supplied lock to the current process and to this project's managed artifact home; the status table names the applied-with-cleanup-failure result (status 1) |
| F6, Maven inheritance | "Maven reactors": an absent project version is supported only through internal parents ending in a module with an owned literal version; an external-parent POM without its own version fails with the remedy |
| F7, locked acceptance evidence | "Lock compatibility evidence for supported tools": the real tool accepts the before pair and the edited pair in locked or frozen mode without changing either file, with tool, version, schema, layout, command, outcome and hashes recorded; unproved combinations fail. "Python with uv": supported `version`/`revision` pairs are registered explicitly (consumers use version 1, revisions 3 and 5) |

Wording corrections: the foundation section is now a table naming the two
changed item 1 contracts (operation tokens, status 3) and their test updates,
and the three additive changes. "Target flow of the version commands"
distinguishes artifact-free initial validation, source-unchanged failures
before the first overwrite, and restoration after it. The file view caches per
phase, and the read-count paragraph lists the phases that reread.

Question refinements: Q01 states the whole-line matching rule at the
umbrella's position; Q04 labels B and C as not meeting the required distinct
status; Q05 compares A and B on a well-formed target that fails source
validation; Q07 reflects evidence in the project's artifact home owned by the
transaction identity, with project binding; Q11 no longer calls npm 7 or 8
current; Q15 states that tracked files stay listed and ignored untracked files
are omitted.

Remaining evidence limitation: the uv revisions named in the design come from
the two consumers' current locks; the plans will fix the registered pairs and
the tool versions for which evidence is recorded.

Please check that F1 to F7 are resolved, that Q17's options are distinct and
sound, and whether any further design question is missing.

### Change summary for design-specification version-sources (round 2)

Changes to `docs/v0.14.0/design.v0.14.0.version-sources.md` since round 1:

- "Target flow of the version commands": the failure paragraph now names three
  boundaries (initial validation, before the first overwrite, after it).
- "Public statuses of the version commands": status 1 adds the completed
  transition whose cleanup failed; status 2 adds overlapping claims and names
  interrupted evidence.
- "What an adapter provides": per-phase file views.
- "Combining all detectors" and "Locating values with the standard library":
  overlap rejection, disjoint edit composition, syntactic field
  identification (F3).
- "Python with uv": registered lock schema pairs and the uv workspace and
  local-link rules (F2, F7).
- "Maven reactors": the inheritance boundary (F6).
- "Undeclared nested candidates": tracked versus ignored untracked files.
- "The recoverable version transition": rewritten planning, ownership,
  evidence and restoration subsections, new "Completion boundary and cleanup
  failures", and project-bound lifecycle reuse (F4, F5).
- "Read-only commands and their limits": per-phase read counts.
- "Lock compatibility evidence for supported tools": locked-mode acceptance
  evidence (F7).
- "Persistent eligibility evidence": whole-line matching at the trailer
  position, with the ambiguous cases restated.
- "The deterministic ancestry rule" and "Git queries of the selector": reordered
  conflict checks and a query table (F1).
- "Foundation changes required by the version domain": a table of contract and
  test impact.
- "Acceptance cases": sixteen new rows for F1 to F7.
- Open questions: Q01, Q04, Q05, Q07, Q11 and Q15 amended, each noting the
  round 1 change where it affects the recommendation; Q17 added. All question
  IDs, options and pending decisions are preserved.
- The feature request, the child draft and the umbrella are unchanged.

### Writer response for design-specification version-sources (round 2)

Writer response:

All five round 1 writer instructions were accepted and applied, with no
disagreement:

1. F1 to F7 are repaired in the design body, and each finding's
   counterexamples are in the acceptance cases (two alias conflicts, an
   ambiguous tag between baseline and target, a lock-free uv workspace, a
   Python path link between components, a tool-only root workspace, two
   overlap cases, the kill before the completion marker, a cleanup failure
   after it, a foreign lock handle, internal and external Maven inheritance, an
   unregistered uv schema and recorded locked-mode evidence).
2. Q17 is added with three distinct options (durable completion boundary,
   retained evidence until explicit cleanup, success with a warning), and
   recommends the durable boundary, as the reviewer suggested.
3. Q01 to Q16 keep their identifiers; their recommendations remain proposals,
   with Q11 still recommending B. Q04 and Q05 arguments are refined as the
   verdicts asked.
4. The foundation-contract, artifact-home and read-count claims are corrected;
   the two changed item 1 contracts and their test updates are named.
5. The assessment maps each finding to its revised section and states the one
   evidence limitation (uv revision pairs taken from the consumers' current
   locks, to be fixed by the plans).

One design consequence worth checking: lifecycle evidence now lives in this
project's artifact home under the transaction identity, instead of in a
directory supplied by item 5. This made the project binding and the
owned-versus-abandoned distinction of F4 and F5 checkable in one place; Q07's
option A text was updated accordingly.

### Reviewer focus for design-specification version-sources (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-05T11:22:43+01:00
- Exchange: specification/design-specification/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification version-sources round 2

Recommend convergence of the reviewed formulation. I read the complete current design and round 2 request. The revised design resolves F1–F7; no further substantive question is missing. This is agreement with proposed answers, not confirmation of any human choice.

| Round 1 finding | Independent round 2 assessment |
| --- | --- |
| F1: target exclusion hides conflicts | Resolved. All reachable stable tags are classified and checked for conflicting version/commit boundaries before removing the target boundary and its aliases. The added observation of tags reachable from the target but not the baseline supports the post-baseline ambiguity rule. Both alias counterexamples have acceptance cases. |
| F2: Python workspaces and local links | Resolved. Manifest workspaces are checked without requiring a lock, including a tool-only root whose workspace includes participants. Lock membership, workspace sources, physical path sources and file references cover the declared-component arrangements; external references remain untouched. |
| F3: overlapping byte ownership | Resolved. Claims are compared by physical file and byte span, independently of field identifier or replacement value. All overlaps fail, and disjoint edits compose from one original. Scanners must identify the syntactic field, with equal text serving only as a cross-check. |
| F4: interrupted evidence bypassed by unchanged | Resolved. The locked evidence check precedes every success path, including the authoritative empty plan. Killing the process before the complete marker leaves writing evidence that blocks the same-target rerun. |
| F5: cleanup boundary and project binding | Resolved by the explicit flushed complete marker, originals-first/manifest-last cleanup, applied-with-cleanup-failure result, and no automatic rollback after that boundary. Complete standalone residue is distinguished from unfinished and lifecycle-owned evidence. Supplied lock ownership is checked against the process, physical project and managed artifact home. Lifecycle evidence remains available for its owner's later restoration. |
| F6: inherited Maven versions | Resolved. Inheritance must end at an owned literal version through internal parents; external-parent inheritance without an own version is rejected with a remedy. External parent coordinates remain unchanged. |
| F7: actual tool compatibility | Resolved at design level. Each supported tool/schema/layout requires recorded real-tool acceptance before and after the adapter edit in locked/frozen mode, unchanged manifest/lock hashes during each tool run, and a reproducible adapter fixture. uv version/revision pairs are explicitly registered. |

Q17 now makes completion and cleanup an explicit decision, with distinct retention and reporting alternatives. Q01–Q16 retain their scope and identifiers; the requested Q04/Q05/Q07/Q11/Q15 refinements are present. No confirmed requirement decision needs reopening.

The current lock-format body still includes npm format 1 while proposed Q11 B selects formats 2/3. That pending amendment is explicitly disclosed. It must follow the user's eventual choice, not this recommendation alone.

Exact compatibility tool versions, commands and fixtures remain planning/implementation evidence. Consumer uv revisions 3 and 5 are observations, not proof of compatibility. The design explicitly requires evidence before a combination is supported; this review does not claim that evidence already exists or that implementation is validated.

Only the wording qualifications supplied separately remain. Source tests are not applicable to this specification-only assessment. The reviewer has not changed the design, consolidated answers or recorded user decisions.

### Question verdicts for design-specification version-sources round 2

All Q01–Q17 are in scope and have materially distinct alternatives with relevant consequences. The proposed answers are coherent with the confirmed requirement. None is a recorded human decision. My choices are A for Q01–Q10 and Q12–Q17, and B for Q11.

| Question | Independent verdict and proposed choice |
| --- | --- |
| Q01 | Choose A. A whole-line Release tooling trailer at the documented final position, followed by a standalone valid marker when validated, gives clone-visible evidence. The ambiguity cases now avoid substring matches in notes. External evidence would need additional distribution rules. |
| Q02 | Choose A. Refusing conflicting histories gives all consumers one deterministic rule. The revised grouping before target exclusion implements that recommendation, and the additional ancestry observation supports ambiguity classification. Highest version or tag date would silently choose between incompatible histories. |
| Q03 | Choose A. versions range is a suitable read-only home for the shared selector; a separate top-level command is feasible but unnecessary, and consumer adoption still belongs to item 7. |
| Q04 | Choose A. Public status 3 supplies the required incomplete-restoration distinction to CLI and in-process callers. B/C are now correctly labeled as failing that public requirement. Foundation contract and test changes are explicit. |
| Q05 | Choose A. Artifact-free initial source validation followed by authoritative capture and planning under the lock preserves the intended failure behavior. Even an initially empty plan acquires the lock and checks evidence. The comparison with lock-first planning now accurately excludes malformed argument validation from the tradeoff. |
| Q06 | Choose A. Stop on interrupted evidence, warn on reads and leave deliberate manual recovery within this item's scope. Automatic restoration and a new recovery command are distinct larger commitments. The writing/complete distinction now handles finished residue separately. |
| Q07 | Choose A. The primitive's evidence in the same project's artifact home, owned by the supplied lifecycle identity and retained for its later restoration, gives one capture and restoration routine. Process/project/artifact-home checks and explicit retention ownership close the prior ambiguity. Item 5 owns encompassing transaction cleanup. |
| Q08 | Choose A. Standard-library semantic parsing plus identified byte spans preserves unrelated bytes without adding a release dependency. Overlap rejection and composition of disjoint edits now make this safe across adapters and pattern declarations. Unsupported syntax has an explicit rejection path. |
| Q09 | Choose A. An LF matching view with mapping back to original bytes makes the documented regex work on CRLF files. The changed behavior of expressions deliberately matching CR is disclosed. |
| Q10 | Choose A. Python core, npm all three forms, Maven snapshot and declared pattern forms satisfy the defaults and npm exception without adding an unsupported Maven publishing mode. |
| Q11 | Choose B. Support npm lock formats 2/3 with real-tool evidence; reject format 1 with a regeneration remedy. The difference from the current body is explicitly pending human selection. No claim that npm 7/8 are current is needed. |
| Q12 | Choose A. Literal groups and exactly project.groupId identify common internal coordinates; potentially internal unresolved group expressions fail instead of being silently skipped. General property resolution remains outside scope. The precise requirement exception for project.version in internal dependency versions is preserved. |
| Q13 | Choose A. component:id sections with managed root paths reuse the schema registry and physical boundary validation, avoid list quoting rules and give diagnostics stable identifiers. |
| Q14 | Choose A. One form override per adapter across participating roots covers the confirmed consumers with a compatible future extension if per-component forms become necessary. |
| Q15 | Choose A. One tracked-plus-untracked Git inventory finds new components with bounded cost and preserves the exclusion boundaries. The revised text correctly distinguishes tracked files from ignored untracked files. |
| Q16 | Choose A. Rejecting trailing text without the title separator catches version typos. Token-only anchors and empty title/notes remain allowed; lenient parsing risks silently accepting a mistyped version. |
| Q17 | Choose A. Durable completion before deleting originals makes cleanup failure distinguishable from incomplete restoration and leaves self-describing residue. Status 1 and an applied diagnostic inform callers of required cleanup without promising an impossible rollback. B adds retained evidence to every success, while C can hide unresolved cleanup from status-only callers. |

No Q18 is needed. The remaining edits qualify wording about standalone completion and preserve the already explicit lifecycle restoration behavior; they introduce no new choice.

### Convergence evidence for design-specification version-sources round 2

Covered wording:

These are wording-only qualifications of behavior already explicit in the detailed subsections:

1. In Completion boundary and cleanup failures, replace the broad sentence ending "never rolled back" with: "For a standalone transition, that write is the completion boundary: the new versions are the result, and subsequent cleanup or lock-release failures do not trigger restoration. A lifecycle owner retains the explicit later restoration ability described below."
2. In the target-flow overview, qualify its blanket post-first-overwrite restoration statement with: "Failures after the first overwrite and before the completion boundary restore the sources; after that boundary, cleanup failures report the applied versions and remaining residue without restoration."
3. In the Q15 introduction and option A label, use "tracked files plus untracked files that no ignore rule matches" instead of the compressed "tracked and untracked, not ignored files". The detailed body and option consequence already make the intended distinction correctly.

The first two qualifications reconcile summary language with Q17 A and the explicit lifecycle restore handle; they do not change either contract. The third merely carries the existing tracked-file distinction into its shorter label.

Convergence rationale:

Convergence is recommended because all seven substantive findings are repaired in the current design and represented by acceptance cases. Q17 completes the missing cleanup decision; Q01–Q17 have distinct alternatives, relevant consequences and consistent proposed answers. The design states its remaining compatibility-evidence obligation rather than assuming unproved schema support. No cross-document correction or additional design choice is required.

The covered edits are limited to qualifying overview sentences using rules already explicit in the same document. They neither change the completion boundary nor remove the owning lifecycle's later restoration ability.

Outstanding human choices: every design question Q01–Q17 is pending. I recommend A for Q01–Q10 and Q12–Q17, B for Q11. Reviewer agreement does not confirm those choices, authorize consolidation or validate implementation. The human owns the convergence gate.

### Writer instructions for design-specification version-sources round 2

1. Treat this as advisory convergence of the proposed formulation. Leave Q01–Q17 pending until the user explicitly selects answers, and leave consolidation to the separate human gate.
2. Apply the small wording qualifications in the covered-wording input when the workflow permits. They restate behavior already specified; they require no new decision or substantive review round.
3. Preserve the confirmed requirement boundaries, the F1–F7 repairs and their acceptance cases. Do not interpret this review as permission to broaden Maven property support, workspace support or lock regeneration.
4. When human-authorized consolidation occurs, align the npm body with the user's Q11 selection. My recommendation is B, not a recorded decision.
5. Carry the compatibility evidence gate into the plans: exact tools, versions, commands, schema pairs, layouts and fixture locations must be named and real acceptance evidence obtained before claiming support. This specification review does not validate implementations or tool compatibility.

### Final reviewer decision for design-specification version-sources round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-11-06T23:31:10+01:00
- Exchange: specification/design-specification/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-06T23:33:22+01:00
- Exchange: specification/design-specification/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification version-sources (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.version-sources.md
Review round: 3

### Requestor assessment for design-specification version-sources (round 3)

Writer assessment of the version-sources design, round 3: follow-up review of
the user's decisions.

Round 2 converged with `consolidation-ready`. At the gate, the user chose to
explain the undecided questions. Each of Q01 to Q17 was explained one at a
time and now carries an explicit user decision. The user then authorized this
follow-up review with `Revise and review again`. Nothing was consolidated:
every question block, option, recommendation and answer is preserved, and the
design body still holds its pre-decision text where a decision changes it.

| Questions | User decision | Same as the writer recommendation | Same as the round 2 reviewer verdict |
| --- | --- | --- | --- |
| Q01 to Q10 | Option A each | yes | yes |
| Q11 | Option B: lock formats 2 and 3; a format 1 lock fails before any write, with the remedy to regenerate it with npm 7 or later | yes | yes |
| Q12 to Q17 | Option A each | yes | yes |

The user added no comment to any decision, and no reviewer verdict conflicts
with a recorded choice.

Every chosen option except Q11's is the one each question marks as the current
design text, so those decisions confirm the body as written. Two places in the
body still need consolidation to follow the decisions:

- Q11: section "npm" still supports lock formats 1, 2 and 3. Consolidation
  restricts it to formats 2 and 3, states the format 1 failure and its remedy,
  and adds an acceptance row for a format 1 lock rejected before any write.
  The lock compatibility evidence then covers npm formats 2 and 3 only.
- Q17: section "Completion boundary and cleanup failures" opens with "This
  section describes the boundary proposed in Q17". Consolidation states it as
  the decided rule.

The evidence limitation stated in round 2 is unchanged: the uv revision pairs
come from the consumers' current locks, and the plans will fix the registered
pairs and the tool versions.

Please check:

1. Whether the 17 decisions, taken together, are consistent with one another,
   with the whole design and with the consolidated feature request.
2. Whether the Q11 and Q17 items above are the only body changes consolidation
   needs, or whether a decision also affects another section, an acceptance
   case, the child draft or the umbrella.
3. Whether any decision raises a new question, or leaves one missing.

### Change summary for design-specification version-sources (round 3)

Changes to `docs/v0.14.0/design.v0.14.0.version-sources.md` since the round 2
review:

- The three covered wording edits from the round 2 answer were applied before
  the gate: the completion boundary sentence, the target-flow qualification,
  and the tracked versus untracked wording of Q15.
- In each of Q01 to Q17, the `User decision: pending` line of the answer
  section is replaced by a `User decision: confirmed - Option <X>, as
  recommended: ...` record that restates the chosen behavior and the decision
  date (Q01 to Q10 on 2026-11-05, Q11 to Q17 on 2026-11-06), with no further
  comment from the user. The Q11 record also names the consolidation change to
  the npm section and the new acceptance row.
- No question, option, recommendation, BBQ explanation or answer text was
  removed or reworded, and no body section changed for the decisions.
- The feature request, the child draft and the umbrella are unchanged.

### Writer response for design-specification version-sources (round 3)

Writer response:

This round reviews the user's decisions, not new findings: round 2 left no
open finding, and its covered wording edits are in the document.

The user confirmed the recommended option for every question: A for Q01 to
Q10 and Q12 to Q17, B for Q11. These match the round 2 reviewer's verdicts, so
there is no disagreement to report. A reviewer recommendation cannot replace a
recorded user choice; if this review finds that a decision conflicts with
another decision, the body or a related document, please name the conflict
and the affected question rather than proposing a different answer, and the
writer will bring it back to the user.

Consolidation is not authorized yet. After this review converges, the user
will choose between consolidating the design and another round.

### Reviewer focus for design-specification version-sources (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-06T23:38:19+01:00
- Exchange: specification/design-specification/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification version-sources round 3

I reviewed the current full design and the validated round 3 request, together
with the consolidated feature request and the relevant version-source, rollback,
tag-trailer and item-2 scope passages of the focused draft and umbrella. The
current document, rather than the request's account of round 2, is the basis
of this assessment. I did not read the review transcript as assessment context.

All 17 questions now record explicit user decisions: A for Q01-Q10 and
Q12-Q17, B for Q11. The recorded choices are mutually consistent and remain
within the requirement's delegated design scope. There are no missing
questions arising from those decisions, no disagreement with a user choice,
and no substantive finding requiring another revision round.

Q11 deliberately differs from the unintegrated npm body. That is an identified
consolidation task, not authority to change the user's answer or consolidate
now. Excluding format 1 satisfies the requirement's supported-schema boundary;
the before/after tool-acceptance evidence must cover the supported formats 2
and 3. Exact supported uv schema pairs, tool versions and fixture locations
remain implementation-plan work, with evidence required before support is
claimed. This review does not claim that tool compatibility has been validated.

Q06 and Q17 describe different evidence states: interrupted or unreadable
evidence stops the next set, while standalone evidence durably marked complete
is removable residue. Q07 retains lifecycle-owned evidence and later rollback
under the caller's ownership; Q17 explicitly preserves that ability. Status 3
remains an incomplete-restoration stop under Q04, while a completed transition
with failed cleanup reports status 1 without undoing applied versions.

The two body consolidation tasks identified by the writer are correct. One
additional wording correction is needed in the acceptance table: the generic
"Leftover evidence from a killed set" row must identify unfinished evidence,
since the completion and restoration sections already distinguish writing
from complete. This is a qualification of an existing decided rule, not a new
policy or question. The target-flow diagram can also name the completion
marker explicitly so its abbreviated sequence reflects the detailed section.

The feature request and drafts do not promise npm format 1, another component
syntax, broader property resolution or different tag evidence. Their rollback
clauses describe failed source updates; post-completion housekeeping does not
undo such an update. No cross-document correction is required by these
decisions. Keep the more specific completion rule in the design, and carry it
into the plans rather than changing the earlier approved scope.

Recommend convergence of this formulation. Every design question has a
recorded human answer; the remaining human choice is whether to authorize
consolidation. This advisory review does not authorize it.

### Question verdicts for design-specification version-sources round 3

All questions are in scope, sufficiently clear and materially distinct; none
is redundant or needs replacement. The alternatives explain the meaningful
cost or lost guarantee. I agree with the recorded choices below; these are
existing human decisions, not reviewer decisions made on the user's behalf.

| Question | Recorded choice and reviewer verdict | Reason |
| --- | --- | --- |
| Q01 | A; agree | The required whole-line tooling trailer and following validation line travel with the tag. Misplaced or repeated trailers stay ambiguous; a local journal cannot determine eligibility in another clone. |
| Q02 | A; agree | Failing on parallel eligible tips and version inversions avoids inventing release ranges. Picking a version or date would add the maintenance-history policy deferred by the umbrella. |
| Q03 | A; agree | A read-only versions range operation gives instruction-driven and Python readers the same selector; adoption remains item 7's work. |
| Q04 | A; agree | Public status 3 preserves the requirement's distinction for incomplete restoration at both CLI and in-process boundaries. Unknown codes still normalize to 1. |
| Q05 | A; agree | Side-effect-free preflight and an authoritative locked recapture satisfy both artifact-free rejection and capture-to-restoration ownership; clean runs must also acquire the lock. |
| Q06 | A; agree | Unfinished or unreadable evidence requires a person and a status-2 stop. Q17's cleanup of known complete standalone residue is compatible and performs no automatic restoration. |
| Q07 | A; agree | A project-bound supplied lock and transaction-owned retained originals serve both immediate restoration and later lifecycle rollback without duplicate capture. Standalone residue cleanup never deletes the lifecycle's evidence. |
| Q08 | A; agree | Parser-checked byte spans preserve all unowned bytes with the existing standard-library runtime; unsupported spellings fail explicitly instead of risking a global replacement. |
| Q09 | A; agree | Matching a CRLF-normalized view and mapping spans back makes the declared example portable while preserving the original line endings. Raw-text matching would make that pattern fail on common Windows files. |
| Q10 | A; agree | The allowed-form matrix respects the Python and Maven constraints and the requirement's explicit npm snapshot exception without introducing per-component forms. |
| Q11 | B; agree | Formats 2 and 3 cover the known npm consumer with obtainable compatibility evidence. A participating format-1 lock fails before writes with the recorded regeneration remedy; no consumer tool runs during set. |
| Q12 | A; agree | Literal groups and exactly project.groupId identify the supported Maven references; failing on another ambiguous group expression avoids silently retaining an internal old version without adding a property resolver. |
| Q13 | A; agree | Named component sections reuse managed-path validation and give setup a stable syntax without comma-list or section-name path parsing. |
| Q14 | A; agree | One built-in form override per adapter matches the single-project-version model. Per-component forms stay explicitly deferred. |
| Q15 | A; agree | The tracked-plus-unignored-untracked Git inventory exposes new components and retains tracked files even if later ignored; fixed exclusions and nested-repository skipping keep the participation boundary. |
| Q16 | A; agree | Requiring the separator for trailing title text prevents a malformed version suffix from silently becoming a release title. Empty titles and notes remain allowed. |
| Q17 | A; agree | A durable complete marker separates rollback backed by complete originals from housekeeping after application. Status 1 exposes residue, status 3 stays reserved, and lifecycle rollback remains explicit. |

No answer replacement or additional user question is needed. Q11's body
integration and Q17's removal of proposal language belong to the separately
authorized consolidation action. The acceptance-table qualification is covered
wording, with concrete text supplied in the paired wording input.

### Convergence evidence for design-specification version-sources round 3

Covered wording:

The following small wording changes are fully covered by this review:

1. Replace the acceptance row's scenario "Leftover evidence from a killed set"
   with "Leftover writing evidence from a killed set". Its existing outcome
   remains: the next set stops with status 2 naming it, and check warns. The
   body already defines the complete-residue exception; this prevents the
   abbreviated acceptance row from appearing to reject that exception.
2. Optionally expand the target-flow diagram's final line into "verify every
   source, durably mark evidence complete" followed by "delete standalone
   evidence, release the lock". This reflects the existing completion section
   and its lifecycle distinction without changing the algorithm.

For the separately authorized consolidation, this wording expresses the
already confirmed choices without adding a decision:

- npm: "package-lock.json pairs with the manifest in the same root. Lock
  formats 2 and 3 are supported: the top-level version where present and
  packages[\"\"].version. A participating format-1 lock fails with status 2
  before any write, with the remedy to regenerate it using npm 7 or later.
  Another format, or a lock whose packages[\"\"] names a different package,
  fails. Compatibility evidence covers supported formats 2 and 3."
- New npm acceptance row: "Participating package-lock.json with
  lockfileVersion 1 | Status 2 before any write; remedy: regenerate the lock
  with npm 7 or later | AC4, AC8".
- Completion opening: "Once verification succeeds, the transition atomically
  replaces the evidence manifest with one whose state is complete, flushed
  before anything else happens." Keep the following standalone completion
  boundary, lifecycle restoration exception and cleanup statuses unchanged.

The remaining body sections already reflect the decisions. No new option,
answer or cross-document scope change is proposed.

Convergence rationale:

Recommend convergence: all 17 recorded user choices fit together and satisfy
the consolidated requirement's scope and delegated design decisions. No new
question, substantive disagreement or missing design decision remains. The
only uncovered text issue is a wording qualification of the already decided
completion-state distinction in an abbreviated acceptance case.

Q11's changed support set and Q17's final wording must be integrated only
after human authorization to consolidate. That planned integration is not an
unresolved review finding. The optional diagram wording and the qualified
acceptance row add no policy. There are no undecided design questions; the
human consolidation choice remains outstanding. Tool compatibility evidence
and implementation validation still belong to the subsequent plans and work.

### Writer instructions for design-specification version-sources round 3

Preserve all recorded user choices. Do not consolidate or remove the question
blocks merely because the reviewer recommends convergence. Present the
convergence result to the user through the requestor workflow; only a durable
human Consolidate choice authorizes that action.

Before presenting the gate, apply the covered wording qualification to the
killed-set acceptance row and, if useful, the target-flow diagram. These only
state the completion rule already present in the body and confirmed in Q17.
They do not require a further automated review round.

If consolidation is authorized, integrate Q11 in the npm section: only lock
formats 2 and 3 are supported; a participating format-1 lock fails before any
write with the remedy to regenerate it using npm 7 or later. Add its explicit
status-2 acceptance row and make clear that the npm compatibility evidence is
for formats 2 and 3. Preserve tool-only exclusion and the no-tool-run rule.
Replace the Q17 proposal sentence with the decided completion rule, preserve
the lifecycle exception and transfer all 17 choices into the decision table.

No requirement, child-draft or umbrella change is needed. The plans must name
the exact registered uv version/revision pairs and supported tool versions,
commands and fixtures, and verify the prescribed compatibility evidence before
claiming support. Do not describe this specification review as execution or
consumer compatibility validation.

### Final reviewer decision for design-specification version-sources round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-11-06T23:44:28+01:00
- Exchange: specification/design-specification/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
