# v0.11.0 specification review requestor implementation tracking and validation

Yes, it is implemented.

All four steps are implemented and validated: paired rendering, specialized
writer orchestration, durable workflow routing, and end-to-end acceptance now
form one complete specification review requestor path.

> Initial-skeleton note: each not-yet-checked section uses the literal empty
> placeholder required by the validation workflow. Implementation checks replace
> those placeholders with evidence and add a missing-work section only when a
> checked step is incomplete.

---

## File-based IO cost clarification for v0.11.0 specification review requestor implementation

All implementation work must preserve these plan constraints:

- Resolve one effort and inspect only its bounded exact document and
  coordination paths.
- Read each feedback or guidance input once and render paired outputs without
  reparsing generated Markdown.
- Publish, wait, reclaim, and complete through shared exact-path atomic
  operations.
- Never load sibling transcript history as routing or working context.

## Complexity bound clarification for v0.11.0 specification review requestor implementation

- **O(1) per render or protocol action** over a constant exact-path set.
- **O(n) per authored input** for feedback and guidance rendering.
- **O(k) per workflow resolution with constant k** for the bounded current
  effort candidates.

Every implementation check must reject documentation-tree scans, transcript
history reads, or repeated generated-Markdown parsing.

---

## Step 1. Add paired specification request rendering

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The repository now provides one frozen, validated specification-round input,
one paired request and transcript-summary render result, a strict ignored-file
CLI and self-locating launcher, a canonical specialized template, public
exports, and focused tests covering every supported type and failure boundary.

### Goal for Step 1

Add one validated specification-round input that produces coherent complete
request content and substantive transcript-summary content for all supported
specification types.

### Step 1 improvement expectations

- Shared identity and Markdown validation are reused rather than copied.
- Request and summary identity, round, assessment, and changes cannot diverge.
- Guided replacement rounds emit the literal `Human guidance:` label and a
  separate writer response.
- Rendering performs one linear pass over caller-authored inputs and one write
  per output.

### What was implemented for Step 1

- **Paired renderer**: added `tools/spec_review_request.py` with exact filename
  identity derivation, the `design` to `design-specification` mapping, shared
  envelope rendering and parsing, and independent request and transcript
  composition from one immutable input.
- **Authored request boundary**: added
  `templates/spec-review-request.template.md` with unique round-qualified H2
  sections, the prescribed reviewer conclusion, and an exact answer artifact.
  The transcript summary uses H3 sections and excludes fixed conclusion
  boilerplate.
- **File command contract**: added `bin/spec_review_request.bat` and CLI flags
  for exact context and round, separate assessment, change-summary,
  writer-response, and optional-guidance inputs, plus two explicit output
  paths. Every caller-owned path must be an effectively ignored root `a.*`
  file, and all paths are validated before either output is written.
- **Guided override behavior**: preserved the literal `Human guidance:` value
  and a separately labeled writer response in both paired artifacts.
- **Package surface**: exported `SpecificationRoundInput`,
  `SpecificationRequestRender`, `specification_context`, and
  `render_specification_request` from `tools/__init__.py`.
- **Validation evidence**: the focused renderer suite, lifecycle split suite,
  and sensitive-commit suite pass. The final `ghog day` completed with 1,486
  passing tests, 100% coverage, zero outliers, zero exclusions, and `exit=0`.

### Step 1 implementation-to-plan variances

`tools/spec_review_request.py` finished at 413 lines rather than the advisory
240-340 estimate, and its focused test finished at 477 rather than 300-420.
Both remain below the plan's 550-line safe threshold and 650-line ceiling. The
extra lines provide strict caller-path, UTF-8, Git-ignore, template, shared
validation, and IO failure coverage without creating another production
module.

The existing 683-line lifecycle test was split into a 501-line transition
module and a 225-line recovery module so the repository-wide line ceiling
remains green. No lifecycle assertion was removed.

The Groundhog duration gate identified one unrelated real-Git unit test at
5.19 seconds. Its unborn-branch Git protocol was replaced by typed exact-output
doubles while preserving and strengthening its empty-tree, finding-location,
and no-pending assertions; its isolated call phase is now below 0.01 seconds.

### New types or classes introduced for Step 1

- `SpecificationRoundInput`: frozen exact context, positive round, timestamp,
  authored assessment, change summary, writer response, and optional literal
  human guidance.
- `SpecificationRequestRender`: frozen complete request content and substantive
  transcript summary pair.
- `_ArgumentParser`: internal command adapter that converts parse failures into
  the shared fail-closed validation error.

### Architecture check for Step 1

- **Domain boundary**: the two public dataclasses hold validated review content
  and depend on shared exchange value objects, not persistence or workflow
  orchestration.
- **Rendering boundary**: the pure paired renderer uses shared `Envelope`,
  `render_envelope_markdown`, and `parse_envelope_markdown` contracts. It does
  not derive one generated artifact by reparsing the other.
- **Adapter boundary**: Git-ignore checks, caller-owned file IO, argument
  parsing, and process exit handling remain in the thin command portion of the
  focused renderer module; publication stays delegated to the shared exchange.
- **Dependency direction**: the package root exports stable renderer values,
  while the renderer imports shared model and envelope modules directly and
  introduces no dependency on higher workflow layers.
- **Maintainability**: every modified or split Python file is below 550 lines,
  and no production file approaches the 650-line ceiling.

No, there is nothing that needs to be addressed for Step 1.

### Performance check for Step 1

- **Linear authored content**: request and summary composition each traverse
  the bounded authored strings once, so work is `O(n)` in supplied content.
- **Constant path set**: the CLI validates four authored inputs, optional
  guidance, and two outputs without a directory scan. Git ignore checks use a
  fixed command per supplied root path.
- **One-write result**: both output paths are validated before rendering, and
  each rendered artifact is written once.
- **No generated-output parsing for composition**: shared parsing validates the
  complete request envelope only; the transcript summary is composed directly
  from the frozen source input.

No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **Supported identities**: parameterized tests cover feature requests, issues,
  designs mapped to `design-specification`, and plans, with and without an
  umbrella.
- **Model and Markdown contract**: tests cover frozen values, positive rounds,
  required authored content, H1 and JSON-first structure, H2 request sections,
  paired identity fields, guidance preservation, and boilerplate exclusion.
- **CLI and filesystem boundary**: tests cover exact flags, missing and
  malformed UTF-8 inputs, non-root, tracked, duplicate, wrongly named, and
  directory paths, Git absence and failure, output errors, template failure,
  and shared-validation mismatch.
- **Coverage evidence**: the full suite reports 100% coverage, including every
  mapped defensive branch in `tools/spec_review_request.py`.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Shared exchange compatibility**: existing envelope and context validation
  remain the source of truth, and publication behavior is unchanged.
- **Lifecycle preservation**: the lifecycle-test split moved recovery cases
  without removing assertions; both focused modules pass.
- **Test reliability**: the sensitive-commit optimization replaces only slow
  subprocess setup with exact protocol doubles and retains the behavior under
  test. The full suite reports zero failures and zero duration warnings.
- **Adapter integrity**: the launcher follows the established self-locating
  `llm-shared` batch pattern, and the canonical template contains no
  provider-specific fork.

No, no existing feature or reporting capability appears impaired by Step 1.

---

## Step 2. Add the specialized requestor instruction and adapters

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The canonical specialized role now registers the fixed specification policy,
coordinates every lifecycle transition through the shared requestor, and
gates consolidation on durable authorization. Thin workflow, Codex, and Claude
adapters expose that role without copying its policy, and focused contract tests
cover the instruction and adapter boundaries.

### Goal for Step 2

Add one discoverable specification requestor that owns assessment, edits, and
authorized consolidation while delegating every durable transition to the
shared requestor and exchange launcher.

### Step 2 improvement expectations

- The exact specification family policy is registered on every operation.
- Intermediate rounds, convergence, reclaim, escalation, and owning-action
  replay follow the shared protocol without manual artifact mutation.
- Canonical consolidation runs only after durable `Consolidate` authorization.
- The `.agent/workflows`, `.agents/llm-shared/instructions`,
  `.agents/llm-shared/skills`, and `.claude/skills` Markdown files redirect to
  the canonical instruction in the form each host loader resolves.

### What was implemented for Step 2

- Added `instructions/spec-review-requestor.md` with the fixed specification
  family, convergence signal, choice labels, shared lifecycle commands, paired
  renderer invocation, exact answer-path reading, replay behavior, and
  authorized consolidation flow.
- Added redirect-only adapters for the workflow, packaged Codex instruction,
  Codex skill, and Claude skill discovery surfaces. The junctioned workflow
  wrapper reuses the repository-wide locate steps so the body resolves when
  llm-shared is the workspace, a sibling clone, or a submodule, while the
  Codex and Claude hosts keep their loader-relative canonical links.
- Added focused instruction-contract tests for fixed policy, lifecycle states,
  renderer inputs, writer-owned wording changes, durable authorization, and
  post-consolidation completion.
- Added adapter-structure tests that keep host files to metadata plus one direct
  canonical redirect and pin the repository-wide Codex redirect forms.
- Reached the Groundhog objective with 1,494 passing tests, 100% coverage, no
  warnings, no duration outliers, and no exclusions.

### New types or classes introduced for Step 2

No production types or classes were introduced. This step adds canonical
Markdown orchestration and redirect adapters only.

### Architecture check for Step 2

- **Role boundary**: the specialized instruction owns specification assessment,
  writer edits, and the authorized consolidation decision while delegating
  durable state transitions to `instructions/review-requestor.md`.
- **Protocol boundary**: status, activation, publication, waiting, answer
  consumption, continuation, confirmation, reclaim, and completion remain
  shared exchange operations; the instruction forbids manual artifact changes.
- **Rendering boundary**: the role invokes the paired renderer using exact
  caller-owned inputs and outputs and reads only the authoritative answer path.
- **Adapter boundary**: all four host adapters contain only discovery metadata
  where needed and one redirect to the canonical instruction, each in the form
  its own loader resolves.
- **Dependency direction**: provider adapters point inward to canonical prose;
  canonical prose references the shared role and launcher contracts without
  duplicating their implementation.

No, there is nothing that needs to be addressed for Step 2.

### Performance check for Step 2

- **Bounded paths**: the role uses exact document, coordination, answer, and
  caller-owned render paths without a documentation-tree scan.
- **Single authoritative answer**: each assessment reads the exact answer path
  once and never reloads the sibling transcript as working context.
- **Linear authored content**: paired rendering remains linear in supplied
  feedback, writer response, and optional guidance; no nested collection work
  is introduced.
- **Static adapters**: host redirects add no runtime computation or repeated IO.

No, there is no performance issue that needs to be addressed for Step 2.

### Unit test coverage check for Step 2

- **Instruction policy**: focused tests cover the exact family, convergence
  signal, choice labels, command sequence, answer-path rule, reclaim boundary,
  wording gate, consolidation authorization, and completion route.
- **Adapter structure**: focused tests cover every requested host, reject copied
  lifecycle policy, require discovery metadata, and assert exact Codex plugin
  redirects. A regression test pins the workflow wrapper to the shared
  `review-requestor` locate body with only the instruction name substituted, so
  it cannot drift back to a clone-relative link that a junctioned project
  cannot resolve.
- **Class coverage**: this Markdown-only step introduces no class file requiring
  a class-specific unit-test package.
- **Coverage evidence**: the full suite reports 100% project coverage and all
  focused instruction and structure tests pass.

No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Shared lifecycle preservation**: the specialized role explicitly delegates
  state authority to the existing exchange and shared requestor contracts.
- **Provider consistency**: redirects follow established workflow, Codex, and
  Claude adapter shapes, including the global Codex plugin format checks.
- **Writer ownership**: assessment edits and convergence wording remain with the
  writer before the human gate; no automated consolidation bypass is added.
- **Regression evidence**: the complete Groundhog walk passes with no failures,
  warnings, duration outliers, or excluded tests.

No, no existing feature or reporting capability appears impaired by Step 2.

---

## Step 3. Route new questions and resume live exchanges through pw

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

Both question workflows now delegate marker-enabled new questions through
`pw`, while a focused exact-path adapter gives one matching live specification
exchange precedence over ordinary routing. Forced delegation, ambiguity
handling, explicit holds, no-question behavior, and replay states are covered
without adding exchange parsing to the main skill router.

### Goal for Step 3

Connect both question workflows to one specialized requestor and make an exact
matching live exchange authoritative over ordinary disk-derived routing without
growing the at-risk workflow module beyond 650 lines.

### Step 3 improvement expectations

- Marker absence, no-question passes, and direct holds preserve existing
  behavior and create no exchange state.
- Marker-present new questions delegate through `pw` to the exact current
  requirement, design, or plan.
- Current, reclaimable, escalated, convergence, and owning-action states route
  according to the shared contract.
- Routing checks a constant candidate set with no tree scan or transcript read.

### What was implemented for Step 3

- Added `tools/prompt_workflow_review.py` to derive at most the resolved
  requirement, design, and plan contexts, map designs to
  `design-specification`, resolve the declared umbrella, and classify exact
  exchanges through the shared observer.
- Added forced `spec-review-requestor` targeting for one question-bearing
  document and ordinary `pw skill` precedence for one non-idle live exchange.
- Added fail-closed diagnostics containing every exact identity, document, and
  state when more than one specification exchange is live for a topic.
- Added matching marker-gated delegation blocks to both canonical question
  workflows after question placement and after the explicit hold decision.
- Added focused routing, skill integration, and instruction contract tests,
  including every defensive routing branch required for 100% coverage.
- Reached the Groundhog objective with 1,515 passing tests, 100% coverage, no
  warnings, no duration outliers, and no exclusions.

### Step 3 implementation-to-plan variances

`tools/prompt_workflow_skill.py` finished at exactly 650 lines rather than the
advisory count at or below 645. It remains at, not above, the repository
ceiling, so the plan's split guidance was not triggered. The module now has no
headroom: the single blank line between `SPEC_REVIEW_REQUESTOR` and
`next_command` cannot be restored to the two-blank-line form used by the other
eighteen top-level definitions without exceeding 650 lines. Move the existing
forced-skill resolution into a responsibility-focused sibling before any later
change adds a line to this module.

`test_prompt_workflow_skill_spec_review_tdd.py` finished at 128 lines rather
than the advisory 180-280 estimate. Its four cases replace the focused adapter
calls directly, so the smaller count reflects delegation to
`test_prompt_workflow_review_tdd.py` rather than missing coverage.
`tools/prompt_workflow_review.py` at 192 lines and its focused test at 298
lines both land inside their advisory ranges.

### New types or classes introduced for Step 3

- `SpecificationReviewRoutingError`: prompt-workflow error that carries exact
  fail-closed ambiguity or context diagnostics to the command adapter.
- `_LiveRoute`: private frozen pairing of one validated `ReviewContext` with
  its observed `ArtifactState` during bounded candidate selection.

### Architecture check for Step 3

- **Routing boundary**: `prompt_workflow_review` owns specification candidate
  derivation and shared observer construction; `prompt_workflow_skill` only
  asks for a forced or live target and renders the resulting command.
- **Exchange boundary**: state classification remains in `ReviewExchangeCore`
  and its observer, so the new router neither parses coordination nor mutates
  protocol artifacts.
- **Writer boundary**: both question instructions retain question detection,
  explicit holds, and existing non-review handoffs while delegating all round
  work to the specialized role.
- **Dependency direction**: the adapter depends inward on prompt state and the
  shared exchange surface; the shared exchange has no dependency on `pw`.
- **File size**: the focused adapter remains below 550 lines, while
  `prompt_workflow_skill.py` sits at exactly the 650-line repository ceiling
  with no remaining headroom.

Yes, `tools/prompt_workflow_skill.py` sits at the 650-line ceiling with no
headroom; run the plan's split guidance for that module before any later change
adds a line to it.

### Performance check for Step 3

- **Constant candidates**: routing checks only `state.requirement`,
  `state.design`, and `state.plan`; it uses no glob, recursive scan, or
  directory enumeration.
- **Exact artifacts**: each candidate delegates classification to the shared
  fixed-path observer and never reads a versioned transcript.
- **Linear draft marker**: the child draft is read once to resolve its optional
  umbrella declaration, with work linear only in that bounded document text.
- **No nested traversal**: live and question-bearing selections are single
  passes over at most three candidates, so no `O(n log n)` or `O(n^2)` path is
  introduced.

No, there is no performance issue that needs to be addressed for Step 3.

### Unit test coverage check for Step 3

- **Context derivation**: tests cover requirement, design, and plan mapping,
  standalone and umbrella drafts, invalid umbrella markers, missing or outside
  umbrellas, and topic mismatches.
- **State routing**: tests cover current, abandoned, escalated, and
  owning-action states, marker absence, live precedence, forced selection, and
  all ambiguity branches.
- **Integration contracts**: tests cover forced and ordinary `pw` commands,
  unchanged fallback, exact error propagation, and both question instructions.
- **Coverage evidence**: the new routing module and the full project report
  100% coverage in the final Groundhog walk.

No, there is no unit-tested class below 100% that needs completing for Step 3.

### Feature integrity for Step 3

- **Ordinary routing**: marker absence or no live exchange returns the exact
  pre-existing disk-derived command.
- **Question workflow behavior**: no-question passes, direct holds, and absent
  review mode retain their existing human or settled-document handoffs.
- **Durable resumption**: all non-idle states, including escalation and
  owning-action replay, return to the one specialized role rather than being
  bypassed by document phase routing.
- **Regression evidence**: all 1,515 tests pass with no warning, exclusion, or
  duration finding.

No, no existing feature or reporting capability appears impaired by Step 3.

---

## Step 4. Prove the full specification requestor workflow

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

The acceptance suite now composes real Git-backed activation, exact `pw`
routing, paired request rendering, shared publication, every specification
identity, repeated rounds, literal human guidance, reclaim, convergence,
durable `Consolidate`, canonical owning-action completion, failure stops, and
bounded IO. Groundhog completed 1,535 tests with 100% coverage and no warning,
xfail, duration outlier, or exclusion.

### Goal for Step 4

Validate the complete opt-in requestor behavior across every specification
type, repeated rounds, session recovery, transcript aggregation, convergence,
durable authorization, canonical consolidation, and completion.

### Step 4 improvement expectations

- Public launchers and canonical contracts compose without private state
  mutation or specialized transport exceptions.
- Every supported artifact identity and failure boundary is exercised.
- Transcript aggregation remains append-only evidence and is never read as
  working context.
- Acceptance IO checks prove bounded exact-path behavior and the repository
  coverage gate remains green.

### What was implemented for Step 4

- Added activation acceptance for marker absence, no-question routing, explicit
  hold ordering, marker-present forced routing, and live-exchange precedence.
- Added paired rendering and publication coverage for `feature-request`,
  `issue`, `design-specification`, and `plan` identities.
- Added a complete writer lifecycle covering a change-request round,
  replacement publication, transcript prefix preservation, convergence
  retention, durable `Consolidate`, canonical document settlement, ordered
  transcript evidence, and completion cleanup.
- Added literal `Human guidance:` override coverage with a separate writer
  response and replacement round.
- Added expired-lease reclaim coverage that proves the request, transcript,
  identity, and round stay byte-for-byte unchanged.
- Added failure and IO acceptance for mismatched identity, duplicate live
  exchange, unsupported type, tracked root input, escalation, bounded exact
  artifact checks, and transcript-read rejection.
- Moved real Git journeys into fixtures after profiling showed subprocess
  validation dominated measured call time. The representative lifecycle call
  dropped from 10.00 seconds to below the one-second duration floor without
  removing any assertion.
- Applied the same fixture boundary to the existing branch-draft workflow
  integration test after Groundhog reported its call at 6.55 seconds. The next
  full run reported no duration outlier.

### Step 4 implementation-to-plan variances

- Added
  `test_spec_review_requestor_acceptance_activation_tdd.py` under the plan's
  split guidance after the combined acceptance file reached 626 lines. The
  resulting activation, lifecycle, and IO files finish at 161, 486, and 265
  lines, each below the 550-line safe threshold.
- The lifecycle file finishes six lines above its 360-480 advisory estimate,
  and the IO file finishes 25 lines above its 160-240 advisory estimate. Both
  remain responsibility-focused and below 550; the difference records the
  public-adapter fixtures and failure instrumentation required by the plan.
- Updated `test_prompt_workflow_integration.py`, which was outside the listed
  Step 4 files, because Groundhog's mandatory duration gate named its existing
  branch-draft call during the Step 4 walk. Only test setup timing changed; its
  assertions and production behavior remain the same.
- Used `ReviewExchangeCore` directly beyond the plan's counterpart-answer
  allowance in three journeys. The reclaim test injects a wall clock to expire
  a lease without a real sleep, which the launcher cannot express and which a
  real wait would turn back into a duration outlier. The identity-mismatch and
  escalation tests assert exact `ReviewExchangeError` types that the command
  adapter converts into JSON exit codes. Every other requestor step in the
  suite runs through the public renderer, exchange adapter, or `pw` routing.

### New types or classes introduced for Step 4

- No production type or class was introduced.
- `CliResult` is a frozen test-support result for the public exchange adapter.
- `Effort` is a frozen test-support context binding the temporary root, topic,
  shared review context, exact document, and umbrella.

### Architecture check for Step 4

- **Public boundary**: requestor journeys use the public renderer, exchange
  command adapter, and `pw` routing surface rather than private coordination
  mutation.
- **Deferred reviewer boundary**: counterpart answer publication calls
  `ReviewExchangeCore` directly, as the plan permits until the independent
  reviewer role exists. Three tests also drive requestor-side operations
  through the same public core rather than the launcher: the reclaim journey
  needs an injected wall clock to expire a lease without a real sleep, and the
  identity-mismatch and escalation journeys assert `ReviewExchangeError` types
  that the command adapter converts into exit codes. All other requestor work
  goes through the public renderer, exchange adapter, and `pw` routing.
- **Responsibility split**: activation and identity, repeated lifecycle, and IO
  failure instrumentation live in separate files below 550 lines.
- **Dependency direction**: test modules depend on prompt-workflow adapters and
  the shared exchange application surface; production layers gained no reverse
  dependency on acceptance code.
- **Canonical owning action**: the lifecycle proves durable authorization
  precedes the canonical consolidation boundary and that completion follows a
  settled decision marker.

Yes, direct `ReviewExchangeCore` use in the reclaim, identity-mismatch, and
escalation journeys reaches past the plan's counterpart-answer allowance; each
case is justified above and recorded as a variance, and the later code-review
umbrella item should revisit whether the launcher needs a clock or typed-error
seam that would remove the exception.

### Performance check for Step 4

- **Constant candidate set**: the IO acceptance fixture exercises exactly the
  resolved requirement, design, and plan contexts and rejects `glob`, `rglob`,
  and `iterdir` calls.
- **Transcript boundary**: guarded reads fail on any versioned transcript
  access during routing, while exact request and coordination paths remain
  available to the shared observer.
- **Linear work**: request rendering and transcript assertions operate on one
  bounded artifact at a time; no `O(n log n)` or `O(n^2)` computation was
  added.
- **Duration result**: real Git subprocess work now runs in fixture setup, so
  call-phase checks remain below the one-second floor. The final full suite
  reports `outliers=0` and `excluded=0`.

No, there is no performance issue that needs to be addressed for Step 4.

### Unit test coverage check for Step 4

- Step 4 changes acceptance and integration tests only; it modifies no
  production class requiring a new class-focused unit test folder.
- The shared renderer, exchange, routing, and workflow modules retain their
  existing unit suites and report 100% project coverage in the final Groundhog
  walk.
- A property-based test is not needed for these finite orchestration journeys;
  the shared exchange state invariants remain covered by the existing property
  suites.

No, there is no unit-tested class below 100% that needs completing for Step 4.

### Feature integrity for Step 4

- Marker absence, explicit holds, and no-question passes retain their existing
  non-review handoffs and create no coordination artifact.
- Every registered specification type publishes the exact shared identity,
  including the `design` to `design-specification` mapping.
- Intermediate answers, human overrides, reclaim, convergence, canonical
  settlement, escalation, and cleanup preserve their shared lifecycle rules.
- The pre-existing branch-draft workflow integration keeps all prior assertions
  while moving only its expensive setup out of call timing.
- Groundhog passes all 1,535 tests with 100% coverage and no warning, xfail,
  outlier, or exclusion.

No, no existing feature or reporting capability appears impaired by Step 4.
