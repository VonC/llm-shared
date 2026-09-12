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

## Consequences of the unsettled layout contract

Shape-based recognition does not distinguish an effort from an ordinary
directory whose name happens to look like a slug. It therefore leaves the
meaning of a recognized effort directory implicit.

The two selection entry points can also produce different results for the same
duplicate documents. The draft explicitly leaves open whether this distinction
is correct: strict ambiguity detection and preference for the canonical draft's
own directory are both existing behaviors. The missing contract and regression
coverage allow the distinction to change accidentally.

Finally, changing umbrella-row slug validation could also change which effort
directories are recognized, even though these are separate responsibilities.

Hardening recognition changes an existing tested behavior. Both
`test_docs_dirs_supports_all_layouts` and
`test_docs_dirs_includes_version_slug_layout` create an empty slug directory
under a version directory and expect it to be discoverable. A content
requirement would deliberately replace those empty-directory expectations.

## Expected documentation-discovery contract

The effort must establish an explicit rule for recognizing
`docs/vX.Y.Z/<slug>/` as an effort directory. That rule must describe what happens
to ordinary directories such as `images` and `sub`, including whether they are
excluded or accepted under a documented naming constraint.

For this issue's recognition questions, an effort document means a canonical
draft, feature-request or issue, design, implementation plan, or validation plan
for an effort, identified by its workflow document filename. Review transcripts,
ignored `a.*` scratch files, and unrelated files do not count as effort documents.
Under a content-based recognition rule, those files alone would not qualify a
directory. The rule for matching the enclosing version and slug is proposed in
Q03, including equivalence of hyphens and underscores. This vocabulary does not
require interpreting the document body to decide its kind.

Duplicate handling must have a stated expected result for both
`resolve_document` and `select_document`. The issue does not presume that their
results must become identical or that the existing preference for the canonical
draft's parent is defective.

The issue settles directory eligibility, directory preference and fallback, and
the result when several documents match. The existing difference in name-match
breadth remains: exact type and folded slug for general resolution, versus role
types and subtopic matches for workflow selection. Q05, Q06, Q09 and Q10 separate
these selection cases and distinguish retained behavior from proposed changes.

Directory recognition must have its own contract so that changing umbrella-row
slug validation does not silently change documentation discovery. The draft's
candidate recognition mechanisms and the organization of validation patterns
remain matters for the design.

The supported nested layout must continue to expose an accepted effort's sibling
documents. Hardening must not recreate the v0.11.0 discovery gap.

## Confirmed boundaries for docs_layout_hardening

- Keep all three documentation-layout concerns in this single issue.
- Preserve the `slug: str | None = None` default on `docs_relative_dir`.
- Preserve the `NewDraftError` raised when `version-slug` is requested without
  a slug. The existing in-tree callers already supply a slug.
- Keep the intermittent `migration_journey[former-default]` failures under
  `tests/acceptance/review_resume/` outside this effort. They concern review
  acceptance stability and require separate work.
- Do not treat a proposed recognition mechanism or duplicate-resolution policy
  as a confirmed decision before the corresponding behavior is settled.

## Acceptance criteria for the layout contract

1. The recognition rule explicitly states the accepted and rejected directory
   cases, including the five shapes reproduced below and the treatment of
   ordinary directories.
2. Tests pin those accepted and rejected outcomes against the settled
   rule. The examples below describe the source draft's current observations,
   not predetermined target outcomes.
3. The expected behavior of both document-selection entry points is documented
   and tested for a document duplicated between the version directory and its
   slug subdirectory.
4. Every call site deciding whether a `docs/vX.Y.Z/<slug>/` directory is an
   effort applies the settled recognition contract, agrees on the same directory,
   and is independent of changes made only to umbrella-row slug validation.
5. The existing layout tests are extended to meet any new conditions imposed on
   an effort directory. Only the version-and-slug expectation changes: an empty
   `docs/vX.Y/`, `docs/vX.Y.Z/` or `docs/vX.Y/vX.Y.Z/` directory stays
   discoverable. Coverage continues to verify discovery of the effort's sibling
   documents.
6. The optional-slug default and the missing-slug error described above remain
   covered without changing their contract.
7. Selection outcomes are documented and tested when a recognized canonical
   parent lacks the requested sibling: one match elsewhere, several competing
   matches, and no match anywhere in the permitted fallback set.
8. Selection behavior is documented and tested when the canonical draft's
   parent does not satisfy the settled effort-directory rule.
9. The rule for several matching documents inside the recognized canonical
   parent is documented and tested separately from fallback ambiguity.
10. Recognition coverage includes matching and mismatched versions and slugs,
    hyphen/underscore equivalence, accepted document kinds, transcript-only and
    scratch-only directories, and the unsupported
    `docs/vX.Y/vX.Y.Z/<slug>/` shape, according to the settled answers.

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

## Open questions for the v0.12.0 docs_layout_hardening issue

### Q01: Must ordinary directories be excluded from effort discovery?

The issue permits either excluding ordinary directories or documenting a naming
constraint. What observable distinction must discovery make between a real
effort and a lowercase directory containing only assets or unrelated files?
The expected-contract section defines effort documents as canonical drafts,
requirements, designs, implementation plans, and validation plans; review
transcripts, scratch files and unrelated files do not count. This question
settles the required behavior; the recognition mechanism belongs in the design.

#### BBQ for Q01

A barbecue organizer should decide whether every labeled box belongs on the
serving table or whether boxes containing only decorations stay off it. In this
picture: the organizer is documentation discovery, the serving table is the set
of recognized effort directories, and the decoration boxes are ordinary folders.

#### Options for Q01

- Option A: Exclude directories that contain no effort documents.
  - pro: Ordinary assets folders do not become efforts solely because of their names.
  - con: An empty directory prepared for a future effort is not yet discoverable.
    Recognition becomes content-dependent as documents are added, renamed or
    removed, and replaces two current tests' empty-directory expectations.
- Option B: Keep recognizing every directory with an accepted name and document
  that this namespace is reserved for efforts.
  - pro: Preserves current recognition without imposing a content requirement.
  - con: Correct behavior depends on authors keeping ordinary folders elsewhere.

#### Recommended option for Q01 (with arguments for this choice)

Option A: Require an observable distinction between effort content and ordinary
folders. This directly addresses the recognition concern without choosing how
the implementation makes that distinction.

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: Accept exclusion of directories without effort documents because an
ordinary folder should not enter effort discovery merely through its spelling.

### Q02: Must existing effort documents remain discoverable without a draft?

If directory recognition requires effort content, should a directory containing
the effort's requirement, design, implementation plan, or validation plan still
qualify when its draft is absent? This concerns the supported document lifecycle,
not the choice of a detection algorithm. It is conditional on Q01 option A.

#### BBQ for Q02

A cook may still have the menu and cooking instructions after losing the
original shopping note. In this picture: the shopping note is the draft, the
menu and cooking instructions are later effort documents, and recognizing the
cook's station is recognizing their effort directory.

#### Options for Q02

- Option A: Allow later effort documents to keep the directory discoverable
  without a draft.
  - pro: Existing requirements and plans do not disappear when a draft is absent.
  - con: Directory recognition alone cannot guarantee canonical-draft context
    for every later workflow command.
- Option B: Require a draft for the directory to qualify as an effort.
  - pro: Every recognized directory supplies the workflow's canonical starting context.
  - con: Otherwise valid effort documents become invisible if the draft is removed.

#### Recommended option for Q02 (with arguments for this choice)

Option A: Preserve discovery of later documents independently of whether a
particular workflow also needs a draft. This avoids repeating the original
symptom of sibling documents becoming invisible.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: Accept discovery without a draft because retaining a requirement or
plan should not depend on retaining its initial working notes. Commands that
need a canonical draft may still enforce that separate prerequisite.

### Q03: Must effort content match the enclosing version and slug?

A directory can contain an effort document copied from another effort. Should
such content qualify `docs/v1.2.3/topic/` when it belongs only to another version
or another slug? This question defines the recognition boundary, without
settling the parsing or validation mechanism. It is conditional on Q01 option A.

#### BBQ for Q03

A serving station labeled for one dish might contain only the recipe for a
different dish. In this picture: the station label is the directory's version
and slug, the recipe is an effort document, and the recipe's dish is the
document's version and topic.

#### Options for Q03

- Option A: Require at least one effort document matching both the enclosing
  version and slug, treating hyphens and underscores as equivalent in the slug;
  unrelated content alone does not qualify the directory.
  - pro: A copied document cannot make a differently named folder appear to be
    the intended effort.
  - con: A directory containing only mismatched documents needs correction
    before it becomes discoverable.
- Option B: Accept any effort document regardless of its version and slug.
  - pro: Discovery tolerates partially renamed or reorganized document collections.
  - con: Recognition can report an effort identity unsupported by its contents.
- Option C: Require the enclosing version and a literally identical slug,
  distinguishing hyphens from underscores.
  - pro: Directory and document names have exactly the same topic spelling.
  - con: Rejects separator variants already treated as equivalent by document matching.

#### Recommended option for Q03 (with arguments for this choice)

Option A: Align the recognized effort with the identity expressed by its
directory. Additional unrelated files need not disqualify a directory that also
contains matching effort content. For example, `docs/v1.2.3/my-effort/` with
`issue.v1.2.3.my_effort.md` qualifies; a different version or a merely prefixed
subtopic alone does not. The version must match exactly.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: Accept matching version and slug as the boundary because the directory
should represent the effort it names, while still allowing accompanying files
and the existing hyphen/underscore equivalence.

### Q04: Can an actual effort use a common folder name such as images?

The draft uses `images` and `sub` as examples of ordinary folders, but those
spellings also satisfy the current slug shape. If a directory contains the
required effort content, should its common name still prevent recognition?
This content-based distinction is conditional on Q01 option A.

#### BBQ for Q04

A box labeled "supplies" may hold real food despite sounding like a storage
box. In this picture: the box label is a common directory name, the food is
qualifying effort content, and admitting the box to the serving table is
recognizing the directory as an effort.

#### Options for Q04

- Option A: Allow common names when the directory otherwise qualifies as an effort.
  - pro: Legitimate effort topics are not rejected through an arbitrary reserved name.
  - con: The directory's name alone cannot tell a reader whether it holds assets
    or effort documents.
- Option B: Reserve common assets-folder names and reject them as effort slugs.
  - pro: Those names consistently indicate ordinary supporting folders.
  - con: Existing valid effort names can become unusable, and the reserved set
    needs an explicit scope.

#### Recommended option for Q04 (with arguments for this choice)

Option A: The concern is mistaking ordinary contents for an effort, not the words
`images` or `sub` themselves. Recognition should follow the settled effort rule.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: Accept a qualifying effort with a common name because the hardening
should distinguish directory purpose without introducing reserved topic names.

### Q05: Should canonical-draft context justify different duplicate results?

For copies of the same document in the version directory and its slug
subdirectory, the draft reports ambiguity from `resolve_document` and a selected
copy from `select_document`. The entry points differ today in directory set,
name-match breadth, and treatment of several matches. This question settles the
directory preference alone. Name matching retains its current breadth; Q09
addresses several matches inside the chosen directory. The shared layout rule
already favors the canonical draft's parent for workflow discovery. Should that
contextual distinction remain the explicit acceptance contract?

#### BBQ for Q05

Two tables may display the same dish card. A guest assigned to one table can use
that table's card, while an unassigned guest cannot tell which card applies. In
this picture: the tables are documentation directories, the cards are duplicate
documents, the table assignment is canonical-draft context, and the unassigned
guest is resolution without that preference.

#### Options for Q05

- Option A: Keep strict ambiguity in general resolution and let workflow
  selection resolve within the canonical draft's parent alone when that
  directory is recognized.
  - pro: Makes the existing contextual distinction explicit and preserves the
    documented effort-directory preference.
  - con: Callers must understand the different results. What happens when that
    parent holds no match is settled by Q06, and several matches inside it by Q09.
- Option B: Require both entry points to reject cross-directory duplicates even
  when the canonical draft identifies the effort directory.
  - pro: Gives both entry points the same ambiguity rule.
  - con: Changes the documented workflow preference and can block an otherwise
    unambiguous effort in its own directory.

#### Recommended option for Q05 (with arguments for this choice)

Option A: Preserve the meaning of canonical-draft context and make the existing
difference intentional and testable. The acceptance case must apply whichever
of the two layouts contains the canonical draft.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: Accept context-sensitive selection because the canonical draft already
identifies the effort's directory, while a general resolver still needs to
report competing matches.

### Q06: What happens when the requested document is missing beside the draft?

When the recognized canonical draft's parent lacks the requested document,
workflow selection currently returns no match. `_topic_docs_dirs` widens to all
supported directories only when that parent is not recognized; that separate
case is covered by Q10. Should missing siblings also permit a fallback?

For the fallback alternatives below, the search covers every other recognized
documentation directory across supported layouts. Matches must still have the
requested version, role and topic under the existing name-match rules; scanning
a directory does not permit selecting a different document version.

#### BBQ for Q06

A guest's assigned table may have no dish card, leaving one or several cards at
other tables. In this picture: the assigned table is the canonical draft's
directory, the missing card is the requested sibling document, the other tables
are alternative documentation directories, and competing cards are ambiguous
fallback matches.

#### Options for Q06

- Option A: Allow a fallback to other recognized documentation directories,
  with the multiplicity rule settled by Q09 and absence reported when nothing
  matches.
  - pro: Supports a recoverable partial layout instead of a dead end.
  - con: Introduces fallback where a recognized parent currently yields absence,
    and lets an effort draw a missing document from another directory.
- Option B: Treat absence in the canonical draft's parent as absence for the
  effort, even if another directory contains a matching document, as today.
  - pro: Enforces complete effort co-location.
  - con: A matching document elsewhere remains unavailable to the effort.
- Option C: Introduce missing-sibling fallback and apply the current selection
  rule of returning the most recently modified match among its alternatives.
  - pro: Reuses the existing timestamp selection behavior without duplicate cleanup.
  - con: Adds a new fallback trigger and silently chooses by timestamps rather
    than resolving effort identity.

#### Recommended option for Q06 (with arguments for this choice)

Option A: Introduce an explicit fallback rather than a dead end, under the
multiplicity rule Q09 settles. This changes current behavior when the recognized
canonical parent lacks the requested sibling; it is not just clarification of
an existing fallback trigger.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: Accept a fallback for a missing sibling because it supports recovery
of a partial layout, and leave to Q09 how many candidates that fallback
tolerates.

### Q07: Should stricter recognition be confined to the slug subdirectory layout?

The motivating recognition concern applies to `docs/vX.Y.Z/<slug>/`. Should
this effort preserve the other four supported layouts and the current accepted
name shapes, apart from any duplicate policy settled above, or apply new
recognition requirements more broadly?

#### BBQ for Q07

Adding a label check to individual serving stations need not change the rules
for the shared dining area. In this picture: individual stations are slug
subdirectories, their label check is the new recognition rule, and the shared
dining area represents the four existing documentation layouts.

#### Options for Q07

- Option A: Confine stricter directory recognition to the version-and-slug
  layout; preserve the other layouts and current slug spelling constraints.
  - pro: Keeps the issue focused and avoids requiring unrelated document relocation.
  - con: Recognition conditions remain different across layout kinds.
- Option B: Apply new content requirements to all supported layout kinds.
  - pro: Offers a broader uniform recognition contract.
  - con: Expands the issue beyond the described gap and can affect existing efforts.
- Option C: Also broaden accepted slug spellings, including currently rejected names.
  - pro: Supports more directory naming conventions.
  - con: Adds a naming-policy change unrelated to distinguishing effort content.

#### Recommended option for Q07 (with arguments for this choice)

Option A: Harden the newly supported slug directory without expanding naming
rules or changing recognition of the four established layouts. The duplicate
contract remains a separate acceptance concern covered by Q05 and Q06.

#### Answer to Q07: option A (with reason why it must be accepted as the answer)

Option A: Accept the limited compatibility scope because the source identifies
three specific contract gaps, not a general documentation-layout migration.
In particular, `docs/vX.Y/vX.Y.Z/<slug>/` remains unsupported: adding a slug
below the minor-and-full-version layout is not part of this effort.

### Q08: Must all directory-recognition paths apply the same effort rule?

The general listing used by `docs_dirs` and the version-scoped listing
`docs_dirs_for_version` independently decide whether a version-and-slug
directory is an effort. Must both apply the same settled eligibility rule for
that directory? The question concerns observable agreement, not how the two
paths share or organize their implementation.

#### BBQ for Q08

Two organizers checking the same serving station should agree whether it
belongs at the barbecue. In this picture: the organizers are the general and
version-scoped directory listings, the station is the same slug directory, and
admission is recognition under the settled effort rule.

#### Options for Q08

- Option A: Require the settled recognition rule at every directory-recognition path.
  - pro: General discovery and version-scoped resolution agree about each
    version-and-slug directory and are both independent of umbrella-row changes.
  - con: More than the originally named recognition path must be addressed.
- Option B: Change only the general recognition path named by the draft.
  - pro: Limits the change to the initially identified location.
  - con: Version-scoped resolution can keep scanning ordinary folders that
    general discovery rejects.

#### Recommended option for Q08 (with arguments for this choice)

Option A: One directory must have one eligibility result, even when callers use
different search scopes. This avoids creating a new discovery disagreement
while repairing the layout contract.

#### Answer to Q08: option A (with reason why it must be accepted as the answer)

Option A: Accept consistent recognition at every path because directory
eligibility must not depend on which listing a caller happens to use.

### Q09: Which match wins when several documents remain in the chosen scope?

Workflow selection currently returns the most recently modified match, both
inside the recognized canonical parent's directory and in its existing broad
fallback set. Q05 preserves the parent preference, and Q06 proposes a fallback
when a recognized parent lacks the requested sibling. Which multiplicity rule
should apply inside that parent and in a permitted fallback?

#### BBQ for Q09

Several dish cards may be revisions kept at one assigned table or competing
cards collected from different tables. In this picture: the cards are matching
documents, their revision times are file modification times, the assigned table
is the canonical parent's directory, and the other tables form the fallback set.

#### Options for Q09

- Option A: Report several matches as ambiguous in every selection scope.
  - pro: Removes silent duplicate selection throughout the workflow.
  - con: Retires timestamp selection even inside an effort's own directory and
    can block roles that currently match several subtopics or document types.
- Option B: Keep most-recent selection in every permitted scope.
  - pro: Preserves the existing multiplicity rule.
  - con: A permitted fallback can silently choose among competing locations.
- Option C: Keep most-recent selection inside the recognized canonical parent;
  require a unique match in a permitted fallback.
  - pro: Preserves selection within the effort while avoiding silent choices
    between fallback alternatives, consistently with Q05 and Q06 option A.
  - con: The local and fallback scopes have different multiplicity rules to explain.

#### Recommended option for Q09 (with arguments for this choice)

Option C: Canonical-parent context justifies preserving its current timestamp
rule. Outside that context, several candidates remain ambiguous. This retains
the existing handling of role and subtopic matches inside the effort and changes
only the multiplicity rule of a permitted fallback.

#### Answer to Q09: option C (with reason why it must be accepted as the answer)

Option C: Accept local most-recent selection and unique fallback selection
because they respect the difference between an identified effort directory and
unresolved alternatives. Existing timestamp-tie behavior inside the canonical
parent remains outside this hardening scope.

### Q10: What if the canonical draft's parent fails the effort rule?

Canonical-parent preference currently depends on that parent appearing in the
recognized directory set. If it does not, selection searches all supported
directories. Content-based recognition can introduce this case when the draft
and enclosing directory have different identities or the available documents
change. Should failing eligibility widen selection or produce an explicit
unrecognized-directory result?

This case also exists today, before any recognition change: a relevant draft
can be discovered anywhere under `docs/`, so a draft in an unsupported directory
such as `docs/archive/` or below the accepted depth already leaves its parent
out of the recognized set and already widens selection to every supported
directory.

#### BBQ for Q10

A guest assigned to a station that fails admission should not silently receive
cards from every other station. In this picture: the assignment is canonical-draft
context, failed admission is an unrecognized parent directory, and collecting
other cards is widening document selection to the fallback set.

#### Options for Q10

- Option A: Report the unrecognized canonical effort directory without widening.
  - pro: Stricter recognition cannot silently produce a broader document search.
  - con: A mismatched or incomplete effort must be corrected before selection
    proceeds, and a draft already sitting in an unsupported directory stops
    resolving siblings instead of searching every supported directory.
- Option B: Retain the current broad fallback when the parent is unrecognized.
  - pro: Preserves the existing fallback trigger.
  - con: Failing the effort rule can silently expand selection to other directories.

#### Recommended option for Q10 (with arguments for this choice)

Option A: An invalid effort location is different from a missing sibling in an
otherwise recognized effort. Report that location problem directly; Q06's
proposed fallback remains available only for a recognized parent.

#### Answer to Q10: option A (with reason why it must be accepted as the answer)

Option A: Accept an explicit unrecognized-directory result because directory
hardening should not cause selection to become less constrained. This deliberately
replaces the existing fallback trigger for an unrecognized canonical parent.
