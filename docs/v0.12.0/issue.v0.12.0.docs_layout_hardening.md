# Not Every Folder Is an Effort

- Type: issue
- Target version: v0.12.0
- Topic: docs_layout_hardening
- Source: [Canonical documentation-layout draft](draft.v0.12.0.docs_layout_hardening.md)

## Background of the documentation-layout hardening issue

v0.11.0 added the `docs/vX.Y.Z/<slug>/` documentation layout. Extending
`_is_supported_docs_dir` to recognize that layout also closed an older discovery
gap: `relevant_drafts` could resolve a nested draft while `docs_dirs` rejected
its parent, leaving the draft's sibling documents invisible.

The source draft identifies three remaining concerns about the layout contract:
recognition of ordinary directories as efforts, different behavior when two
document-selection entry points encounter duplicates, and coupling between
directory-name validation and umbrella-row slug validation. They form one issue
for v0.12.0. The draft reports no current repository breakage from these concerns.

## Current directory recognition and document selection

1. `_is_supported_docs_dir` accepts a directory two levels below `docs/` when
   the first component is a full version and the second matches the accepted
   slug shape. Recognition does not require an effort document in the directory.
2. A lowercase assets or images directory can therefore be scanned by consumers
   of `docs_dirs` as though it were an effort directory. The draft reports that
   no such ordinary directory exists under a version directory in this repository.
3. `resolve_document` and `select_document` differ on three axes. Resolution
   searches supported directories for the requested version; selection searches
   the recognized canonical draft's parent alone, or all supported directories
   when that parent is not recognized. Resolution matches an exact document
   type and folded slug; selection matches the types belonging to a document
   role and also accepts `<slug>_<sub>` subtopics. Resolution reports multiple
   matches as ambiguous; selection returns the most recently modified match.
4. The directory-name check reuses `COLLECTION_SLUG_RE`, which was introduced
   for slug validation in umbrella collection tables. Both the general layout
   predicate behind `docs_dirs` and the independent version-scoped listing
   `docs_dirs_for_version` apply it to version-and-slug directories.
5. When the canonical draft's parent is recognized but lacks the requested
   sibling document, selection currently returns no match. Its existing broad
   directory fallback applies when the parent is not recognized, not when a
   recognized parent has no matching document. Name matching still requires the
   requested document version even when the directory search is broad.

## Consequences of the current layout contract

Shape-based recognition does not distinguish an effort from an ordinary
directory whose name happens to look like a slug. It therefore leaves the
meaning of a recognized effort directory implicit.

The two selection entry points can also produce different results for the same
duplicate documents. Strict ambiguity detection and preference for the canonical
draft's own directory are both existing behaviors. The accepted contract below
preserves that distinction and defines the missing-sibling and invalid-parent
cases so they cannot change accidentally.

Finally, changing umbrella-row slug validation could also change which effort
directories are recognized, even though these are separate responsibilities.

Hardening recognition changes an existing tested behavior. Both
`test_docs_dirs_supports_all_layouts` and
`test_docs_dirs_includes_version_slug_layout` create an empty slug directory
under a version directory and expect it to be discoverable. A content
requirement deliberately replaces those empty-directory expectations.

## Expected documentation-discovery contract

### Recognition of version-and-slug effort directories

A `docs/vX.Y.Z/<slug>/` directory is recognized only when its existing path
shape is valid and it contains at least one qualifying effort document. Empty
directories and ordinary asset directories do not qualify through spelling
alone. Adding, renaming or removing documents can change eligibility.

An effort document is a canonical draft, feature-request or issue, design,
implementation plan, or validation plan, identified by its workflow document
filename. Review transcripts, ignored `a.*` scratch files and unrelated files do
not count. Recognition does not require interpreting document bodies.

A qualifying document must match the enclosing full version exactly and the
directory slug with hyphens and underscores treated as equivalent. A subtopic
prefix match alone is insufficient. For example,
`docs/v1.2.3/my-effort/issue.v1.2.3.my_effort.md` qualifies. Documents for a
different version or slug alone do not qualify the directory; accompanying
unrelated files do not disqualify a directory that has a matching document.

An existing requirement, design or plan is sufficient without a canonical draft.
Commands that require a draft retain that separate prerequisite. Common names
such as `images` and `sub` are valid effort names when their directories contain
qualifying documents; there is no reserved-name list.

Every recognition path, including general and version-scoped discovery, must
apply this same contract. Changes made only to umbrella-row slug validation must
not change directory eligibility. The recognition mechanism and organization of
validation patterns remain design choices.

### Resolution and workflow selection outcomes

General resolution retains strict ambiguity detection across recognized
directories for the requested version. It does not use canonical-draft context
to select among duplicate matches.

Workflow selection first checks whether the canonical draft's parent is a
recognized documentation directory, then applies the following outcomes:

| Canonical-parent state | Required selection outcome |
| --- | --- |
| Recognized, with one matching document | Return that local document, regardless of copies in other layouts. |
| Recognized, with several matching documents | Return the most recently modified local match, retaining the existing timestamp-tie behavior. |
| Recognized, with no matching sibling | Search all other recognized documentation directories across the supported layouts; return the sole matching document, report ambiguity for several matches, or return no match when none exists. |
| Unrecognized | Report the unrecognized canonical directory explicitly; do not widen the search to other directories. |

The missing-sibling fallback is a new behavior: today a recognized parent with
no matching sibling yields no match. The unrecognized-parent result also changes
behavior: today that condition triggers broad fallback. Branch-relevant drafts
can already be discovered in unsupported locations under `docs/`; stricter
version-and-slug eligibility adds further possible rejected-parent cases.

Existing name-match breadth remains unchanged. General resolution matches an
exact document type and folded slug. Workflow selection matches the types for
the requested role and accepts its existing `<slug>_<sub>` subtopic matches.
Both local selection and fallback still require the exact requested document
version, even when the fallback searches directories from other versions.

### Compatibility of existing documentation layouts

Stricter content recognition applies only to `docs/vX.Y.Z/<slug>/`. Preserve
the existing flat, minor, full-version and minor-and-full-version layouts,
including discovery of empty directories in those layouts. Preserve the current
accepted spelling shapes; do not introduce new layouts or relocate documents.
The deeper `docs/vX.Y/vX.Y.Z/<slug>/` shape remains unsupported.

Accepted version-and-slug efforts must continue to expose their sibling
documents. Hardening must not recreate the v0.11.0 discovery gap.

## Confirmed boundaries for docs_layout_hardening

- Keep all three documentation-layout concerns in this single issue.
- Preserve the `slug: str | None = None` default on `docs_relative_dir`.
- Preserve the `NewDraftError` raised when `version-slug` is requested without
  a slug. The existing in-tree callers already supply a slug.
- Keep the intermittent `migration_journey[former-default]` failures under
  `tests/acceptance/review_resume/` outside this effort. They concern review
  acceptance stability and require separate work.
- Preserve the existing name-match breadth of each selection entry point and
  the timestamp-tie behavior within a recognized canonical parent.
- Leave recognition mechanisms, pattern organization and implementation
  structure to the design; this issue specifies observable behavior.

## Acceptance criteria for the layout contract

1. A version-and-slug directory is accepted only with a qualifying effort
   document. Empty, asset-only, transcript-only and scratch-only directories are
   rejected. Adding, renaming and removing the qualifying document updates the
   eligibility result.
2. Recognition tests cover every accepted document kind, including a directory
   containing a later effort document without a canonical draft. Matching effort
   documents allow common directory names such as `images` and `sub`; those names
   receive no reserved-name exception.
3. For a document duplicated between a version directory and its recognized slug
   subdirectory, general resolution reports ambiguity while workflow selection
   returns the match in its recognized canonical draft's parent.
4. Every call site deciding whether a `docs/vX.Y.Z/<slug>/` directory is an
   effort applies the recognition contract, agrees on the same directory,
   and is independent of changes made only to umbrella-row slug validation.
5. The two existing empty-slug-directory tests are updated for content-based
   eligibility. Only the version-and-slug expectation changes: empty `docs/`,
   `docs/vX.Y/`, `docs/vX.Y.Z/` and `docs/vX.Y/vX.Y.Z/` directories stay
   discoverable. Tests continue to verify the effort's sibling discovery and
   reject `docs/vX.Y/vX.Y.Z/<slug>/` without expanding accepted spellings.
6. The optional-slug default and the missing-slug error described above remain
   covered without changing their contract.
7. When a recognized canonical parent lacks the requested sibling, selection
   searches every other recognized documentation directory. Tests verify the
   sole-match result, ambiguity for competing matches and absence when none
   exists, retaining the exact requested version and existing role/subtopic
   matching rules throughout fallback.
8. When a discovered canonical draft has an unrecognized parent, selection
   reports that directory explicitly and does not search elsewhere. Coverage
   includes an unsupported location and a parent rejected by the stricter rule.
9. Several matching documents inside a recognized canonical parent still select
   its most recently modified match. Test this separately from fallback
   ambiguity, without changing the existing local timestamp-tie behavior.
10. Recognition tests verify exact enclosing-version equality and slug equality
    with hyphen/underscore folding. Different versions, different slugs and mere
    subtopic prefix matches do not qualify a directory by themselves; unrelated
    accompanying files do not disqualify a matching effort document.

## Observed examples from the source draft

| Directory | Current recognition |
| --- | --- |
| `docs/v1.2.3/topic` | Accepted |
| `docs/v1.2.3/images` | Accepted |
| `docs/v1.2.3/sub` | Accepted |
| `docs/v1.2.3/My_Slug` | Rejected because of uppercase characters |
| `docs/v1.2.3/a.scratch` | Rejected because of the dot |

With the same feature-request document under both `docs/v1.2.3/` and
`docs/v1.2.3/my_slug/`, the source draft reports:

| Entry point | Current result in the reported example |
| --- | --- |
| `resolve_document(...)` | Raises `Ambiguous feature-request document for ...` |
| `select_document(...)` | Returns the most recently modified match within its selected directory set; the draft reports the copy under `docs/v1.2.3/` |

The code confirms the timestamp rule, but the draft does not record the probe's
timestamps. Canonical-parent preference restricts the candidates before that
rule is applied.

## Code responsibilities identified by the draft and review

- `_is_supported_docs_dir`: decides whether a documentation directory is
  supported.
- `relevant_drafts`: discovers the canonical draft, including the nested layout.
- `docs_dirs`: supplies documentation directories to downstream consumers.
- `docs_dirs_for_version`: lists supported directories for a version and applies
  an independent `COLLECTION_SLUG_RE` check to full-version subdirectories.
- `resolve_document`: detects ambiguous document matches.
- `select_document` and `_topic_docs_dirs`: select documents with preference for
  the canonical draft's directory.
- `most_recent`: selects the matching document with the latest modification time.
- `_slug_key`: makes hyphens and underscores equivalent when comparing slugs.
- `COLLECTION_SLUG_RE`: validates umbrella collection-row slugs and is currently
  reused for effort-directory names.
- `docs_relative_dir` and `NewDraftError`: retain the established optional-slug
  interface and the rejection of `version-slug` without a slug.

The reviewed discovery and selection functions are in
`tools/prompt_workflow_docs.py`. The two empty-directory tests identified above
are in
`tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py`.

## File-based IO cost clarification for v0.12.0 requirements

The qualifying-content rule uses current immediate filenames and existing
file-type checks without reading document bodies. Existing enumeration,
ordering and downstream document reads remain. The accepted behavior requires
fresh results after file changes, not an index, a cache or a latency target.

## Requirement clarifications

| Question | Decision and rationale | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | A: Require an effort document so an ordinary directory cannot qualify through its spelling alone. | Recognition of version-and-slug effort directories; criterion 1 | Recognizing every valid slug name and reserving the namespace for efforts. |
| Q02 | A: A later effort document qualifies without a draft because retaining requirements or plans must not depend on retaining initial notes. | Recognition of version-and-slug effort directories; criterion 2 | Requiring a canonical draft for directory discovery. |
| Q03 | A: Require the enclosing version and folded slug to match, so the directory represents the effort it names while keeping separator equivalence. | Recognition of version-and-slug effort directories; criterion 10 | Any effort document regardless of identity; literal separator equality. |
| Q04 | A: Accept qualifying efforts named `images` or `sub`; purpose comes from matching content. | Recognition of version-and-slug effort directories; criterion 2 | Reserving common assets-folder names. |
| Q05 | A: Preserve strict general resolution and canonical-parent preference in workflow selection because only the latter has that context. | Resolution and workflow selection outcomes; criterion 3 | One global duplicate policy that ignores canonical-parent context. |
| Q06 | A: Add fallback when a recognized parent lacks a sibling, supporting recovery of a partial layout; Q09 controls multiplicity. | Resolution and workflow selection outcomes; criterion 7 | Keeping absence without fallback; choosing the newest among fallback alternatives. |
| Q07 | A: Limit stricter recognition to version-and-slug directories because this effort closes specific contract gaps without a layout migration. | Compatibility of existing documentation layouts; criterion 5 | Applying content restrictions to older layouts or broadening accepted slug spellings. |
| Q08 | A: Apply one eligibility contract at every recognition path, independent of umbrella validation, so listing choice cannot change discovery. | Recognition of version-and-slug effort directories; criterion 4 | Fixing only the general recognition path and leaving version-scoped discovery inconsistent. |
| Q09 | C: Retain local newest-match selection but require a unique fallback match; canonical context justifies the former, while competitors outside it remain ambiguous. | Resolution and workflow selection outcomes; criteria 7 and 9 | Strict ambiguity for local matches too; silently choosing the newest fallback match. |
| Q10 | A: Explicitly report an unrecognized canonical parent without fallback so stricter eligibility cannot silently broaden selection. | Resolution and workflow selection outcomes; criterion 8 | Retaining broad fallback for an unrecognized parent. |

All ten issue questions are settled. No additional requirement clarification is
needed before design.
