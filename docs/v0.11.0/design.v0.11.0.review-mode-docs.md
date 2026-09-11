# Design v0.11.0 -- Independent review-mode documentation

Reference feature request:
[feature-request.v0.11.0.review-mode-docs.md](feature-request.v0.11.0.review-mode-docs.md)

---

## Context for v0.11.0 independent review-mode documentation

The shared exchange, specification roles, and implementation-code roles are
already shipped. This design arranges their settled behavior into a connected
documentation set without turning the wiki into another policy source. It also
keeps the established self-review loop distinct from the marker-gated,
two-agent independent review mode.

## Scope for v0.11.0 independent review-mode documentation

The v0.11.0 outcomes are:

1. Readers can discover and complete one specification-review journey and one
   implementation-code-review journey.
2. Readers can identify the current owner, safe next action, returned artifact,
   and human stop for every observable exchange state.
3. Project and wiki entry points lead to one coherent set whose claims remain
   traceable to canonical instructions and shipped types.

Everything else is supporting design context for those outcomes or explicitly
deferred.

### In scope for v0.11.0 independent review-mode documentation

- one explanation page for the authority and durable-evidence model;
- two numbered, cross-linked first-use tutorials, one per review family;
- task-focused how-to pages for opt-in, reviewer invocation, returned results,
  ordinary reclaim, stopped-state recovery, and authorized continuation;
- one central reference contract for marker, identity, artifacts, states,
  operations, outcomes, exits, adapters, and policy ownership;
- concise entry-point and inventory updates plus a versioned coverage table;
- explicit comparison and cross-links with the self-review loop.

### Deferred beyond v0.11.0 independent review-mode documentation

- repository-wide Markdown-checker automation owned by umbrella item 7;
- read-only commit-plan inspection owned by umbrella item 8;
- automatic drift detection between wiki command text and launcher behavior;
- any protocol, launcher, template, state, or adapter implementation change.

---

## Confirmed technical facts for v0.11.0 review-mode documentation

**The protocol has one observable state vocabulary**:
`tools/review_exchange_models.py` defines fifteen `ArtifactState` members,
including live, abandoned, convergence, owning-action, escalation, interrupted,
repair, and inconsistent shapes. The user-visible vocabulary also includes the
launcher-only `disabled` value emitted by `tools/review_exchange_cli.py` when
the `a.review-mode` marker is absent. That result has a null round and no
coordination record. Documentation therefore derives fifteen rows from the enum
and accounts for `disabled` as a separate sixteenth row.

**Launcher results carry authority**: `bin/review_exchange.bat` is the shared
coordination boundary, and its final standard-output JSON contains the
authoritative `paths`, `state`, `outcome`, and round information. Progress on
standard error and nearby filenames are not authoritative artifact sources.

**Normal entry is skill-driven**: `bin/prompt_workflow.bat`, exposed
interactively as `pw`, routes ordinary document and implementation journeys.
Family launchers remain necessary for reference, recovery, and direct reviewer
operation, but they are not the first-use teaching surface.

**Host coverage is asymmetric**: `.agents/llm-shared/skills/` and
`.agent/workflows/` expose a shared `review-requestor` wrapper, while
`.claude/skills/` exposes the family requestors and reviewers without that
shared wrapper. The adapter table must record the gap rather than imply parity.

**The wiki already has a fixed information shape**: `wiki/README.md` presents
explanation, tutorials, how-to guides, then reference. Tutorials currently use
the numeric prefixes `01` through `08`, and existing self-review pages already
own the human-answered question loop vocabulary.

**Markdown automation is intentionally incomplete**: `.markdownlint.json`
modifies the rule set, but no shipped launcher applies it. This effort can run
project and Git gates, resolve links and paths, and manually inspect changed
Markdown, but it cannot claim a repository Markdown command exists.

---

## Current behavior for v0.11.0 review-mode documentation

Protocol facts are spread across canonical instructions, family adapters,
templates, launcher help, model enums, and older wiki pages about self-review.
A reader can reconstruct the independent exchange, but no page provides its
complete operational contract and no connected journey leads from opt-in to
the human convergence gate.

```txt
README/wiki entry points
  -> established self-review documentation
  -> separate instructions, templates, launchers, and state types
  -> reader reconstructs the independent exchange unaided
```

## Target behavior for v0.11.0 review-mode documentation

The target set has one path for learning, one for completing a task, and one
for exact lookup. Entry points introduce the stable terms and link into the
set. The explanation establishes why authority is split. Separate tutorials
teach the two family journeys. How-to pages handle bounded tasks. The central
reference holds the exact contract and points back to canonical policy owners.

```txt
README.md and wiki/README.md
  -> explanation: authority, advisory review, durable evidence
  -> tutorials: specification journey | implementation-code journey
  -> how-to: opt in | invoke | interpret | reclaim/recover | continue
  -> reference: identity, artifacts, states, operations, results, adapters
  -> canonical instructions remain authoritative for agent policy
```

---

## Information architecture for v0.11.0 review-mode documentation

### Explanation and comparison boundary

A dedicated explanation page describes why requestor, reviewer, and human are
separate authorities; why recommendations remain advisory; and why versioned
transcripts are evidence rather than working context. It compares independent
review mode with the self-review loop by intent, participants, opt-in,
intermediate automation, and final human choice.

The existing self-review explanation and how-to keep their present jobs. They
gain short comparison links only where the word "review" would otherwise be
ambiguous. Neither page absorbs independent-review commands or state tables.

### First-use tutorial pair

Two tutorials use the same teaching rhythm but different family evidence:

1. activate independent review mode for an existing effort;
2. let `pw` route the requestor and publish round 1;
3. run the correct independent reviewer;
4. observe a changes-requested round and the automated writer response;
5. reach the convergence gate;
6. show that only the human choice authorizes consolidation or commit.

The specification tutorial names umbrella, reviewed specification, and round.
The implementation-code tutorial names umbrella, implementation plan, step,
round, immutable evidence, validation-state comparison, and commit boundary.
They cross-link at the point where the family-specific paths diverge.

Each tutorial depicts requestor and reviewer as two explicitly labelled agent
sessions. When the requestor enters its bounded wait, the tutorial moves to the
reviewer session, publishes the answer, then returns to the requestor session
after the wait reports the authoritative answer path. The depiction does not
suggest that switching skills inside one session creates an independent actor.

The new tutorials append to the existing numeric sequence rather than
renumbering `01` through `08`, preserving all current links. Their order places
the specification journey before the implementation-code journey.

### Task-focused how-to set

How-to coverage is split into five pages, with every required user goal assigned
to one page:

- one opt-in page covers enabling and disabling independent review mode;
- one specification page covers starting and resuming specification review;
- one implementation-code page covers starting and resuming code review;
- one result-and-continuation page covers reading returned artifacts and
  resuming an already authorized consolidation or commit action;
- one recovery page covers ordinary reclaim and stopped-state recovery in
  separate sections, with forced operations inside its marked human-decision
  section.

Ordinary procedures begin with the skill-level route. A page introduces direct
launcher operations only when the task cannot be explained truthfully without
them. Forced recovery appears inside a visually marked human-decision section
that states the required authority, accepted artifact shape, and evidence
effect before the command.

### Central reference contract

One central reference page owns the user-facing lookup contract. It contains:

- the `a.review-mode` opt-in rule and identity keys for both families;
- transient, versioned, coordination, tombstone, lock, and manifest artifacts;
- the naming grammar for orientation and returned `paths` authority;
- a state matrix with one row for every shipped `ArtifactState` member plus one
  launcher-only `disabled` row with its null round and absent coordination record;
- operation, actor, precondition, next state, outcome, and exit summaries;
- the single-final-JSON and standard-error progress contract;
- convergence choices and the human-only authority boundary;
- an adapter table with host, wrapper, prefix, delegation target, and gap;
- links to focused recovery procedures and canonical instructions.

Existing inventory pages receive links or rows only when their established
subject calls for one. They do not repeat this full contract.

The state matrix groups `disabled` and `idle` as the two not-yet-started
conditions, then groups active exchange, convergence and owning action, lease
abandonment, interrupted or repair-required, and stopped or inconsistent
conditions. Every `ArtifactState` member still appears exactly once, with the
launcher-only `disabled` row accounted for separately from enum validation.

## Authority and content reuse for v0.11.0 review-mode documentation

### User contract versus agent policy

Wiki pages state observable user behavior in their own words. Whenever a page
summarizes a policy-owned rule, it names the canonical instruction that owns
agent behavior and links to it. Pages never copy an instruction body or imply
that wiki wording overrides a launcher or typed state.

Reference tables are assembled from shipped sources at implementation time:

- fifteen states from `ArtifactState` and the launcher-only `disabled` state
  from the absent-marker branch in `tools/review_exchange_cli.py`;
- dispositions from `ReviewDisposition` and confirmation outcomes from
  `ConfirmationOutcome`;
- operation outcome strings from `tools/review_exchange_cli.py`, recorded as
  the one contract column with inline string sources rather than typed backing
  and therefore given an explicit source and drift-risk note;
- operations and arguments from launcher help and adapters;
- ownership from canonical requestor and reviewer instructions;
- artifact shapes from templates and store models.

### Command and path examples

Tutorials and ordinary how-to pages show host-prefixed skill commands and
repository-relative context paths. Reference and recovery pages may show the
full `bin/*.bat` form. JSON examples include only fields needed to teach the
contract, use illustrative paths, and label the returned `paths` object as the
source to follow.

Examples do not reconstruct exact protocol filenames, edit protocol artifacts,
or treat standard-error diagnostics as final results. Exit `0` means the
operation completed and grants its reported next action, exit `3` is an
expected protocol stop, and exit `2` is invalid input or a fatal error.

The canonical final-result example is pinned to `_success_payload` in
`tools/review_exchange_cli.py`. It always shows `diagnostic`, `identity`,
`operation`, `outcome`, `paths`, `round`, and `state`. Observable additions such
as `exchange_occurrence` or an owning-action authorization flag are labelled
conditional rather than part of the mandatory payload.

### Visual identity boundary

New independent-review-mode pages use
`wiki/assets/logo-llm-shared-transparent.png`. The existing
`wiki/assets/logo-llm-shared-review-transparent.png` remains the visual marker
for self-review pages. This avoids recreating the terminology collision through
shared imagery and requires no new asset.

## Discovery and coverage evidence for v0.11.0 review-mode documentation

### Entry points and category navigation

`README.md` adds one concise pointer that distinguishes independent review mode
from the self-review loop. `wiki/README.md` adds the new pages under their
existing categories and keeps the mandated order: explanation, tutorials,
how-to guides, then reference.

The six candidate inventory pages are assessed individually. A candidate gets
a link or row only when it helps a reader find an artifact, template, launcher,
skill, or repository location already in that page's scope. An omission is
recorded rather than hidden.

### Versioned acceptance-to-page table

A versioned coverage table under `docs/v0.11.0/` is effort evidence, not a wiki
page. It maps acceptance criteria 1 through 9 to exact delivered pages. It
records criteria 10 through 12 as validation or scope evidence and records the
disposition of every candidate inventory page.

Each row names the criterion, evidence type, exact path or command, and result.
The table therefore answers both "which page carries this contract?" and "why
was this candidate left unchanged?" without forcing non-Diataxis material into
the wiki.

## Design decisions for v0.11.0 review-mode documentation

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Use one central reference, one explanation, two tutorials, and a bounded goal-organized how-to set. | Information architecture | One omnibus page mixes Diataxis purposes; many tiny pages fragment one exchange. |
| Q02 | Append specification and code tutorials as `09` and `10`, with navigation carrying conceptual order. | First-use tutorial pair | Renumbering breaks existing links; unnumbered files break the tutorial convention. |
| Q03 | Use two stages of one fictional effort, with each tutorial independently completable. | First-use tutorial pair | Unrelated examples weaken comparison; one generic exchange hides family differences. |
| Q04 | Use five how-to pages for opt-in, two family starts, shared results and continuation, and shared recovery. | Task-focused how-to set | One branching guide is hard to follow; duplicated family recovery copies shared policy. |
| Q05 | Keep ordinary and stopped-state recovery in one guide, with forced actions inside a marked human-decision section. | Task-focused how-to set | An uninterrupted procedure weakens authority; a separate forced guide disconnects diagnosis from action. |
| Q06 | Group all typed states by lifecycle, add the launcher-only `disabled` row separately, and place `disabled` with `idle` as not-yet-started. | Central reference contract | Enum order is poor for diagnosis; common-state-only coverage omits recovery cases. |
| Q07 | Show missing host wrappers as `absent` and name the existing family-specific route. | Central reference contract | Silent omission hides gaps; adding wrappers changes behavior outside scope. |
| Q08 | Show one `_success_payload` example with seven mandatory fields and label every additional field conditional. | Command and path examples | Full snapshots freeze incidental fields; path-only examples omit the result contract. |
| Q09 | Create `coverage.v0.11.0.review-mode-docs.md` with criterion, evidence type, exact path or command, result, and notes. | Versioned acceptance-to-page table | Plan-only evidence mixes concerns; per-page metadata loses one scope view. |
| Q10 | Record each inventory candidate as `update`, `already covered`, or `unaffected`, with a target or reason. | Entry points and category navigation | Updating every candidate adds noise; silent omission cannot be reviewed. |
| Q11 | Add reciprocal comparison callouts to the two self-review pages and keep full comparison on the new explanation page. | Explanation and comparison boundary | Rewriting old pages changes their purpose; no cross-links preserve ambiguity. |
| Q12 | Attribute canonical sources once per reference section and add row-level notes only for exceptions. | User contract versus agent policy | Per-row links overwhelm tables; one bottom source list obscures ownership. |
| Q13 | Mark forced actions with a `Human decision required` heading and a blockquote naming authority, precondition, and evidence effect. | Task-focused how-to set | HTML styling is renderer-dependent; ordinary prose is too easy to miss. |
| Q14 | Depict requestor and reviewer as two labelled sessions, including the bounded-wait handoff and returned answer path. | First-use tutorial pair | One session makes independence cosmetic; abstract commands hide the actor boundary. |
| Q15 | Use the generic llm-shared logo on new independent-review pages and retain the review logo for self-review pages. | Visual identity boundary | Reusing the logo recreates the collision; a new asset expands this effort. |

No open questions remain; all design decisions are settled and the
implementation-plan phase has enough information to proceed.

---

## Acceptance cases for v0.11.0 review-mode documentation

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| A new user wants specification review | The entry points lead to the specification tutorial, which reaches the `Consolidate` or `Revise and review again` gate. | The first-use path stays linear and family-specific. |
| A new user wants implementation-code review | The entry points lead to the implementation-code tutorial, which includes immutable evidence and reaches the `Commit` or `Rework and review again` gate. | Code review has a different evidence and authority boundary. |
| A live request lease expires | The relevant how-to identifies the reviewer as owner and uses ordinary reclaim, which renews the lease in place, preserves the round and artifacts, and remains idempotent while the round is live. | Expiry is recovery, not a new exchange. |
| An exchange is escalated | The recovery guide stops automation and places forced or resolving actions inside a human-decision section. | Reviewer or requestor roles cannot invent human authority. |
| A page mentions an exact artifact path | It tells the reader to follow the final JSON `paths` member rather than infer a neighboring filename. | Launcher output is authoritative. |
| A host lacks a shared requestor wrapper | The adapter table marks the wrapper absent and points to the family adapter that exists. | Documentation records real host coverage without inventing parity. |
| An inventory page gains only a row | It links to the central reference and does not restate policy. | Link-only edits carry no contract-definition obligation. |
| Documentation validation runs after staging | Both Git whitespace checks run, links and named paths resolve, and manual markdownlint review keeps MD024 and MD025 active. | Staged and unstaged changes both receive evidence. |

## File-based IO cost clarification for v0.11.0 review-mode documentation

The delivered pages use explicit links and fixed inventories. Opening a normal
journey therefore reads only the selected page and the links the reader follows;
it does not scan the repository for exchange metadata. Authoring and acceptance
validation may read the finite page set, declared local targets, typed state
model, and launcher contract once, for linear `O(n)` work in those bounded
inputs. No production response path or exchange persistence behavior changes.
