# Design v0.12.0: Documentation layout hardening

Reference issue: [Not Every Folder Is an Effort](issue.v0.12.0.docs_layout_hardening.md)

## Context for v0.12.0 docs_layout_hardening

The issue settles ten requirement clarifications covering content-based effort
recognition, canonical-parent preference, missing-sibling fallback and ambiguity.
This design proposes how discovery and selection share those rules without
merging their different matching contracts. The proposals below are subject to
design review; they do not reopen the issue's accepted behavior.

## Scope for v0.12.0 docs_layout_hardening

The outcomes are one recognition contract at both directory-listing entry
points, explicit workflow search scopes, and actionable failures for invalid
canonical parents and competing fallback documents.

In scope are the directory-recognition boundary, filename identity matching,
candidate discovery, selection policy and error propagation. The five supported
layouts, existing directory spelling shapes and public selector signatures stay
compatible. The stricter content condition applies only to version-and-slug
directories.

Layout migration, new naming conventions, body-based document classification,
changes to local timestamp ties and changes to role/subtopic matching are out of
scope. The optional slug default and missing-slug `NewDraftError` stay unchanged.
The separate review-resume acceptance instability remains outside this effort.
Implementation steps, file splits and test execution order belong to the plan.

## Confirmed technical facts for v0.12.0 docs_layout_hardening

These facts were checked in the current source before writing this design:

- [prompt_workflow_docs.py](../../tools/prompt_workflow_docs.py) contains both
  `docs_dirs` and `docs_dirs_for_version`. The former walks below `docs/` and
  calls `_is_supported_docs_dir`; the latter enumerates version-specific paths
  and independently checks child names with `COLLECTION_SLUG_RE`.
- `COLLECTION_SLUG_RE` accepts `[a-z0-9][a-z0-9_-]*`. Both recognition sites
  currently accept a matching full-version child without inspecting its files.
- `_exact_doc_matches` already checks document type, exact version and exact
  folded slug. Its `validation-plan` selector recognizes the
  `plan.<version>.<slug>.validation.md` form and excludes that suffix from
  ordinary plan matches.
- `_doc_matches` uses workflow roles, keeps the requested filename version and
  allows exact folded topics or `<slug>_<sub>` matches. It is deliberately
  broader than exact resolution.
- `_topic_docs_dirs` searches only a recognized canonical parent, even when it
  has no requested sibling. It returns all recognized directories only when the
  parent is unrecognized. `select_document` then applies `most_recent` to the
  list returned by `find_matching_documents`.
- `most_recent` uses modification time and the existing candidate order for
  ties. `resolve_document` instead raises `PromptWorkflowError` for multiple
  exact matches and returns `None` for absence.
- [prompt_workflow_steps.py](../../tools/prompt_workflow_steps.py) uses
  `select_document` for requirements, designs and both plan roles. The CLI in
  [prompt_workflow.py](../../tools/prompt_workflow.py) reports
  `PromptWorkflowError` and `OSError` through its existing fatal-error path.
- [prompt_workflow_post_commit.py](../../tools/prompt_workflow_post_commit.py)
  builds topics from validation-plan filenames, assigning a draft path in the
  same directory without requiring that draft to exist. `plan_topics` treats
  `select_document(root, topic, "plan") is None` as a reason to skip the topic.
  That module has no exception handler.

## Current and target flows for v0.12.0 docs_layout_hardening

Today, two shape checks decide directory eligibility independently. Workflow
selection then chooses a directory set before it knows whether a requested
role has a local match. That separation makes missing-sibling fallback
impossible and loses the scope needed for different multiplicity rules.

The proposed target separates shared eligibility from contextual selection:

```text
Directory candidates -> shared eligibility -> recognized directories
                                              |
                       +----------------------+------------------+
                       |                                         |
              General exact resolution                  Workflow selection
              version-scoped directories                canonical parent check
              exact type/version/topic                   |
              zero / one / ambiguous                     +-- invalid -> error
                                                        +-- local matches
                                                        |   -> newest local
                                                        +-- no local match
                                                            -> other directories
                                                            -> zero / one / error
```

General enumeration remains version-scoped. Workflow fallback uses all other
recognized directories across supported layouts, while filename matching still
requires the requested version and existing role/subtopic rules.

## Shared directory eligibility for v0.12.0 docs_layout_hardening

### One eligibility boundary with independent enumeration

Propose one shared predicate for supported directory eligibility. General and
version-scoped discovery may keep their present enumeration strategies and
ordering, but neither may decide version-and-slug eligibility independently.
The flat root remains an explicit accepted layout; the other older layouts
retain their existing shape-only conditions, including empty directories.

For a full-version child, eligibility combines an independent directory-slug
pattern with a qualifying immediate file. The directory pattern initially has
the same accepted language as `COLLECTION_SLUG_RE`, but is owned by layout
recognition and has no dependency on umbrella-row validation. No reserved-name
list is introduced.

### Filename evidence for an effort directory

Propose reusing exact document matching as the filename evidence rule, across
draft, feature-request, issue, design, plan and validation-plan kinds. Check
immediate regular-file candidates with the enclosing full version and directory
slug. Existing `Path.is_file()` behavior is retained; this effort does not add a
new symbolic-link policy. No recursive content search or body read is needed.

The check succeeds as soon as one supported document filename exactly matches
that version and the folded slug. It must not reuse the workflow role matcher,
whose subtopic acceptance would weaken the requirement. Review transcripts,
scratch files and unrelated filenames are outside the accepted type prefixes.
The validation suffix is interpreted as a document-kind suffix, not as part of
the effort slug.

Directory recognition remains independent of canonical-draft discovery. A
matching later document is sufficient, and the predicate must not call a
resolver that itself enumerates recognized directories. This avoids a circular
dependency between recognizing an effort and finding its first document.

### Freshness and file access during recognition

Propose evaluating current directory entries on each discovery invocation with
no process-wide or persistent eligibility cache. An added, renamed or removed
qualifying file can therefore change the next discovery result without explicit
invalidation. Repeated scans are acceptable for the existing short-lived local
workflow; a new indexing service is unnecessary.

Retain existing file-access failure propagation. A filesystem exception that
surfaces during enumeration is an operational failure, not evidence that an
effort is absent. Do not catch and silently convert such an exception into an
ineligible directory or an empty fallback result. No transactional filesystem
snapshot or retry lifecycle is introduced.

## Scope-aware selection for v0.12.0 docs_layout_hardening

### Candidate discovery retains its search scope

Propose a shared internal candidate result containing the ordered matching paths
and their scope, either canonical-parent or fallback. The internal discovery
operation accepts the root, topic and requested role, validates the canonical
parent against recognized directories, and searches that parent first.

Here the canonical parent means the directory holding the topic's draft path.
Validate that directory against the recognized set without requiring the draft
file to exist or discovering it again. Post-commit topics rely on paths to
drafts that were removed or never written. Existing path normalization for
directory comparison is retained; it does not add a draft-existence check.

Any local matches terminate discovery for the role. Only an empty local result
permits scanning all other recognized directories. Parent comparison retains
the current resolved-path comparison, and the parent is excluded from fallback
using that same comparison. Preserve current enumeration order within each
scope so local timestamp ties do not change accidentally.

`find_matching_documents` keeps its public list return shape by exposing the
paths from this result. It returns all matches in the selected scope and does
not resolve multiplicity. Under the proposed shared validation boundary, an
unrecognized parent raises `PromptWorkflowError` from both this list-returning
helper and `select_document`; it is not represented by an empty list. Design
Q07 reviews this placement of the check. `select_document` consumes the same
internal result directly, so it does not need a second discovery pass to
reconstruct provenance.

The exact private type and helper names remain plan details.

### Selection applies the policy appropriate to the scope

For canonical-parent matches, retain `most_recent`. For fallback, return `None`
for zero matches, the sole path for one match, and an error for multiple
matches. Both paths reuse existing role/version/subtopic matching.

General `find_documents` and `resolve_document` keep their current exact-match
and strict-ambiguity contracts. They benefit from shared directory eligibility
without adopting workflow fallback or canonical-parent preference.

### Error information and caller boundaries

Propose using `PromptWorkflowError` for both an unrecognized canonical parent
and ambiguous workflow fallback, preserving existing selector return types and
CLI error handling. Absence remains `None`; it must not represent either error.

An invalid-parent diagnostic identifies the canonical directory and its topic
version and slug. A fallback-ambiguity diagnostic identifies the requested role,
version and slug, canonical parent, and every competing document path in a
stable order. Render repository-relative paths where applicable. The design
requires that diagnostic information, not an exact sentence or a new public
error-code scheme.

The shared discovery operation validates the parent before any fallback, and
errors propagate through both public entry points to their callers. Callers
must not downgrade these failures to a missing document or
continue choosing a later workflow phase from partial results.

`plan_topics` in post-commit topic resolution is another caller of selection.
It builds topics from directories returned by `docs_dirs`, so with an unchanged
tree those parents are recognized even when their draft files do not exist.
If a validation plan has no ordinary plan beside it, the topic is currently
skipped. The accepted missing-sibling fallback now includes that topic when one
matching plan exists elsewhere, retains the skip when no plan exists anywhere,
and raises for competing fallback plans. Post-commit resolution propagates that
error instead of downgrading it to a missing plan. This is the same selection
contract applied to an existing caller, not a separate post-commit policy.

## Acceptance cases for v0.12.0 docs_layout_hardening

| Scenario | Expected outcome | Requirement basis |
| --- | --- | --- |
| Empty `docs/v1.2.3/topic/`, or one containing only assets, scratch files or review transcripts | Neither directory-listing entry point recognizes it. | Issue Q01, Q08 |
| `docs/v1.2.3/my-effort/issue.v1.2.3.my_effort.md` without a draft | Both listings recognize it. | Issue Q02, Q03 |
| Matching design, ordinary plan or validation plan is the only effort file | The directory qualifies through that document kind. | Issue Q02 |
| Only another version, another slug or a subtopic-prefix filename is present | The version-and-slug directory does not qualify. | Issue Q03 |
| Qualifying effort named `images`, with unrelated assets beside its documents | The directory qualifies without a reserved-name exception. | Issue Q04 |
| Empty flat, minor, full-version or minor-and-full-version directory | Older layout recognition is retained. | Issue Q07 |
| Uppercase or dotted slug directory, or a slug below minor-and-full-version nesting | The currently unsupported shape stays rejected. | Issue Q07 |
| Document duplicated between a version directory and its recognized slug child | General resolution reports ambiguity; workflow selection prefers its canonical parent. | Issue Q05 |
| Several matches in a recognized canonical parent | Workflow selection returns the existing newest local result. | Issue Q09 |
| No local sibling, with one eligible match elsewhere | Workflow selection returns that fallback match. | Issue Q06, Q09 |
| No local sibling, with multiple eligible fallback matches | Workflow selection reports ambiguity with the competing paths. | Issue Q09 |
| No local sibling and no eligible fallback match | Workflow selection returns `None`. | Issue Q06 |
| Topic whose parent directory is unsupported or identity-mismatched | Selection reports the parent and never widens its search. | Issue Q10 |
| Qualifying file added, renamed or removed between discovery calls | The next call observes the resulting eligibility. | Issue Q01; Design Q05 |
| Topic built from a validation plan whose draft file does not exist | Its directory is checked as the canonical parent without requiring the draft file. | Issue Q02, Q10; Design Q07 |
| Post-commit validation-plan topic has no local ordinary plan | A sole fallback plan includes the topic, no fallback plan skips it, and competing fallback plans raise. | Issue Q06, Q09 |

The implementation plan will map these outcomes to regression coverage and
check the optional-slug interface. This design does not prescribe a file-by-file
change sequence or reopen the issue's compatibility boundaries.

## Open questions for the v0.12.0 docs_layout_hardening design

### Q01: Where should the two directory listings share eligibility?

The issue requires both recognition paths to agree. Should they share the
eligibility predicate while retaining their enumeration strategies, or should
version-scoped discovery filter a single general directory inventory?

#### BBQ for Q01

Two organizers can use the same admission check on different guest lists, or
both start with the full list. In this picture: the organizers are the directory
listings, admission is eligibility, and guest lists are candidate directories.

#### Options for Q01

- Option A: Share one eligibility predicate and retain separate enumeration.
  - pro: Keeps version-scoped discovery narrow while removing the duplicated rule.
  - con: Enumeration order and scope still have two callers to maintain.
- Option B: Build one general inventory and filter it for version-scoped calls.
  - pro: Centralizes directory enumeration as well as eligibility.
  - con: Exact resolution must scan unrelated version directories and preserve
    existing version-scoped ordering through an additional projection.

#### Recommended option for Q01 (with arguments for this choice)

Option A: The defect is duplicated eligibility. Sharing that boundary preserves
the useful narrow search without coupling exact resolution to a full tree scan.

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: Accept a common predicate because it satisfies agreement across both
entry points while preserving their distinct enumeration purposes.

### Q02: How should recognition match a qualifying document filename?

The accepted identity rule is exact version and folded slug equality, including
the validation-plan suffix. Should recognition reuse existing exact matching
or use a new filename parser shared with the resolvers?

#### BBQ for Q02

Admission can reuse the existing recipe-label checker or replace the label
system before checking anything. In this picture: admission is directory
recognition, recipe labels are document filenames, and the checker is exact
document matching.

#### Options for Q02

- Option A: Reuse exact document matching across the accepted document kinds.
  - pro: Retains existing type prefixes, separator folding and validation suffix
    handling without creating another interpretation of filename identity.
  - con: Recognition depends on the exact matcher continuing to serve both
    discovery and explicit resolution; accepted kinds must remain explicit.
- Option B: Introduce a shared parsed document identity for recognition and resolution.
  - pro: Makes type, version and slug available as reusable structured data.
  - con: Requires broader parser changes and compatibility review beyond adding
    the content check, especially for legacy names and validation suffixes.

#### Recommended option for Q02 (with arguments for this choice)

Option A: Existing exact matching already expresses the required identity rule.
Using it avoids a wider parser change and keeps role/subtopic matching separate.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: Accept exact matcher reuse because the issue needs a shared identity
test, without introducing a new filename grammar or parsing abstraction. The
accepted kinds are draft, feature-request, issue, design, plan and
validation-plan; the `requirement` selector alias does not add another kind.

### Q03: How should candidate discovery carry the selected search scope?

Local matches use the newest timestamp, while fallback must be unique. The
selector therefore needs the scope as well as the paths. Should internal
discovery return both, or should selection infer the scope from a public list?

#### BBQ for Q03

Collected recipe cards can carry a note saying which table they came from,
or the cook can walk back to identify their table afterward. In this picture:
cards are matching documents, tables are local and fallback scopes, the note is
scope metadata, and the cook is the selector.

#### Options for Q03

- Option A: Return ordered paths and scope internally, preserving public list
  and single-document interfaces through adapters.
  - pro: One discovery pass supplies enough context for both public operations.
  - con: Introduces a small internal result shape that the implementation must maintain.
- Option B: Keep only a list result and infer local versus fallback from the
  candidate parents or a repeated canonical-parent check.
  - pro: Avoids introducing a separate candidate-result abstraction.
  - con: Reconstructs information discovery already had, complicates empty
    results and can require repeated filesystem work.

#### Recommended option for Q03 (with arguments for this choice)

Option A: Preserve provenance at the point where scope is chosen. Public callers
can keep their current result shapes without losing the policy distinction.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: Accept an internal scoped result because local versus fallback is
required selection context and should not have to be rediscovered afterward.

### Q04: How should new selection failures reach existing callers?

An unrecognized parent and ambiguous fallback must be reported, while absence
remains `None`. Should the design use existing `PromptWorkflowError` diagnostics
or introduce dedicated public error subclasses with structured fields?

#### BBQ for Q04

An organizer can report a seating problem through the existing help desk with
the relevant names, or create a new form for each problem. In this picture: the
help desk is the existing error path, names are diagnostic paths and topic
identity, and forms are dedicated error subclasses.

#### Options for Q04

- Option A: Raise `PromptWorkflowError` with contextual diagnostic text.
  - pro: Fits current caller and CLI handling while distinguishing errors from absence.
  - con: Post-commit topic lookup currently uses `None` to skip missing plans
    and will now propagate fallback ambiguity. Programmatic recovery would need
    a typed interface rather than depending on message parsing.
- Option B: Add dedicated subclasses with structured directory and candidate fields.
  - pro: Gives future callers a stable way to distinguish and inspect each failure.
  - con: Adds public error contracts when current callers only report fatal failures.

#### Recommended option for Q04 (with arguments for this choice)

Option A: Current callers need an actionable failure, and the existing exception
boundary already supports it. Require useful diagnostic data without fixing an
exact message string or adding unused recovery interfaces.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: Accept the existing error type because it carries both failures to
the established CLI boundary without altering the selector return contract.

### Q05: Should discovery introduce an eligibility snapshot for repeated role lookups?

Workflow state resolves several roles in succession. Content-based recognition
adds directory-entry reads to those calls. Should discovery remain uncached, or
should an explicit inventory snapshot be passed through one workflow operation?

#### BBQ for Q05

An organizer can check the serving stations each time a guest asks, or prepare
one list for a single seating round. In this picture: stations are effort
directories, guest requests are role lookups, and the round list is an explicit
operation-scoped inventory snapshot.

#### Options for Q05

- Option A: Read current entries on each discovery invocation with no eligibility cache.
  - pro: Added, renamed and removed documents are reflected on the next call
    without cache lifetime or invalidation rules.
  - con: Several role lookups can repeat directory-entry reads.
- Option B: Pass an explicit immutable inventory through one workflow operation,
  rebuilding it for every subsequent discovery operation.
  - pro: Shares recognition work across the operation's role lookups.
  - con: Expands caller interfaces and requires a defined snapshot lifetime;
    changes during that operation are observed only after rebuilding it.

#### Recommended option for Q05 (with arguments for this choice)

Option A: The current workflow is short-lived, and no measured need justifies
snapshot plumbing. Direct reads keep the accepted freshness rule straightforward.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: Accept uncached discovery because it preserves current invocation
boundaries and observes document changes without additional state management.

### Q06: Should recognition add recovery for filesystem errors during enumeration?

Eligibility now inspects directory entries. If an enumeration operation raises
an `OSError`, should discovery retain existing error propagation or perform one
bounded retry when a concurrent removal can explain the failure?

#### BBQ for Q06

If an organizer cannot read a station's label, they can report the problem or
walk around once more to check whether the station moved. In this picture: the
label read is filesystem enumeration, the report is error propagation, and the
second walk is a bounded retry after a concurrent removal.

#### Options for Q06

- Option A: Propagate surfaced filesystem errors through the existing caller boundary.
  - pro: Does not silently turn inaccessible content into an absent effort and
    preserves existing operational failure handling.
  - con: A concurrent deletion can require the user to repeat the workflow command.
- Option B: Retry enumeration once for a recognized concurrent-removal failure,
  then propagate any remaining error.
  - pro: Can recover from a transient tree change without repeating the whole command.
  - con: Adds retry classification and multiple reads without an atomic view;
    it does not solve other concurrent mutations.

#### Recommended option for Q06 (with arguments for this choice)

Option A: This design needs content evidence, not a new filesystem recovery
lifecycle. Retaining surfaced errors is explicit and keeps absence meaningful.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: Accept existing error propagation because a recognition failure must
remain observable and the issue does not require transactional discovery.

### Q07: Where should the canonical-parent check be enforced?

The issue requires an unrecognized parent to be reported without fallback.
Should the shared candidate-discovery operation enforce that check for both
public entry points, or should only single-document selection enforce it?
The check concerns the topic's directory, not existence of its draft file.

#### BBQ for Q07

An organizer can check a station before handing out any recipe cards, or leave
that check to the cook who chooses a card. In this picture: the station is the
topic's parent directory, handing out cards is candidate discovery, and choosing
one card is single-document selection.

#### Options for Q07

- Option A: Validate the parent in shared candidate discovery; both
  `find_matching_documents` and `select_document` report an unrecognized parent.
  - pro: Every consumer receives candidates only after the search scope has
    been validated, with one place enforcing the parent check.
  - con: The list-returning helper gains an invalid-parent exception that its
    tests and any future callers must account for.
- Option B: Validate only in `select_document`; the list-returning helper
  returns an empty list for an unrecognized parent.
  - pro: Avoids adding this exception to the list-returning helper.
  - con: The list helper conflates an invalid scope with absence, and any future
    selector must repeat validation before interpreting its candidates.

#### Recommended option for Q07 (with arguments for this choice)

Option A: An unrecognized parent invalidates the scope choice itself. Check it
where scope is formed so no adapter can quietly interpret an invalid scope as
an empty match set.

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: Accept validation in shared discovery because both candidate listing
and selection depend on the same valid parent. A missing draft file alone does
not invalidate that directory.
