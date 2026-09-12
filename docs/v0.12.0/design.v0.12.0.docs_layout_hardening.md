# Design v0.12.0: Documentation layout hardening

Reference issue: [Not Every Folder Is an Effort](issue.v0.12.0.docs_layout_hardening.md)

## Context for v0.12.0 docs_layout_hardening

The issue settles ten requirement clarifications covering content-based effort
recognition, canonical-parent preference, missing-sibling fallback and ambiguity.
This design defines how discovery and selection share those rules without
merging their different matching contracts. The seven accepted design decisions
below preserve the issue's accepted behavior and provide the basis for planning.

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

The target separates shared eligibility from contextual selection:

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

Use one shared predicate for supported directory eligibility. General and
version-scoped discovery retain their present enumeration strategies and
ordering, but neither may decide version-and-slug eligibility independently.
The flat root remains an explicit accepted layout; the other older layouts
retain their existing shape-only conditions, including empty directories.

For a full-version child, eligibility combines an independent directory-slug
pattern with a qualifying immediate file. The directory pattern initially has
the same accepted language as `COLLECTION_SLUG_RE`, but is owned by layout
recognition and has no dependency on umbrella-row validation. No reserved-name
list is introduced.

### Filename evidence for an effort directory

Reuse exact document matching as the filename evidence rule, across draft,
feature-request, issue, design, plan and validation-plan kinds. Keep those six
kinds explicit; the `requirement` selector alias does not add another kind. Check
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

Evaluate current directory entries on each discovery invocation with
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

Use a shared internal candidate result containing the ordered matching paths
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
not resolve multiplicity. Under the shared validation boundary, an
unrecognized parent raises `PromptWorkflowError` from both this list-returning
helper and `select_document`; it is not represented by an empty list. Design
Q07 records this placement of the check. `select_document` consumes the same
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

Use `PromptWorkflowError` for both an unrecognized canonical parent
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

## Design decisions

All seven reviewed choices are accepted as option A. No further design
question blocks implementation planning.

| Question | Decision and reason | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Share one eligibility predicate while retaining separate enumeration. This removes the duplicated rule while keeping version-scoped discovery narrow. | [One eligibility boundary with independent enumeration](#one-eligibility-boundary-with-independent-enumeration) | Filtering a general inventory would scan unrelated directories and require preserving version-scoped ordering through another projection. |
| Q02 | Reuse exact filename matching across draft, feature-request, issue, design, plan and validation-plan. It already expresses exact version, folded slug and validation-suffix handling. | [Filename evidence for an effort directory](#filename-evidence-for-an-effort-directory) | A new shared filename parser would expand the grammar and compatibility work beyond the content check. |
| Q03 | Carry ordered paths and search scope in one internal result, adapting it to the existing public return shapes. Selection needs this provenance and should not rediscover it. | [Candidate discovery retains its search scope](#candidate-discovery-retains-its-search-scope) | Inferring scope from a plain list or repeating discovery complicates empty results and duplicates filesystem work. |
| Q04 | Use contextual `PromptWorkflowError` diagnostics for invalid parents and fallback ambiguity. Existing callers report failures; absence remains distinct, including in post-commit lookup. | [Error information and caller boundaries](#error-information-and-caller-boundaries) | Dedicated public error subclasses would add unused recovery interfaces. Future structured recovery should use a typed interface rather than message parsing. |
| Q05 | Read current entries on every discovery invocation without an eligibility cache. This observes content changes without adding snapshot lifetime or invalidation rules, accepting repeated reads. | [Freshness and file access during recognition](#freshness-and-file-access-during-recognition) | An operation-scoped immutable inventory would expand caller interfaces and observe concurrent changes only after a rebuild. |
| Q06 | Preserve surfaced filesystem-error propagation. Failure must remain observable instead of being treated as absent content. | [Freshness and file access during recognition](#freshness-and-file-access-during-recognition) | A bounded retry for concurrent removal would add classification and repeated reads without providing atomic discovery. |
| Q07 | Validate the canonical parent in shared candidate discovery. Both public entry points depend on a valid scope and report an invalid parent; a missing draft file alone does not invalidate the directory. | [Candidate discovery retains its search scope](#candidate-discovery-retains-its-search-scope) | Selector-only validation would let candidate listing conflate an invalid scope with absence and force later consumers to repeat the check. |
