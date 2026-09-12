# Specification review transcript for v0.12.0

- Exchange: specification/issue/v0.12.0/docs_layout_hardening
- Reviewed document: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-12T13:41:51+02:00
- Exchange: specification/issue/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for issue docs_layout_hardening (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
Review round: 1

### Requestor assessment for issue docs_layout_hardening (round 1)

#### Assessment of the documentation-layout issue for issue docs_layout_hardening (round 1)

The user selected one issue requirement followed by review of its questions.
The reviewed document is derived from
`docs/v0.12.0/draft.v0.12.0.docs_layout_hardening.md`, with settled type `issue`,
version `v0.12.0`, and slug `docs_layout_hardening`. There is no umbrella.

The requirement retains all three source concerns: effort-directory
recognition, duplicate-document selection, and independence from umbrella-row
slug validation. It preserves the optional-slug contract and excludes the
unrelated review-resume acceptance instability.

Seven open questions cover the observable recognition boundary, discovery
without a draft, version and slug identity, common folder names, selection with
canonical-draft context, fallback selection, and compatibility scope. Each has
distinct options with pros and cons, a recommendation, and a proposed answer.
The options and answers appear sufficient for those cases. No further issue-level
question is apparent to the writer; independent review should check for missing
behavior or acceptance boundaries and any accidental design-level prescription.

Q02 and Q03 are conditional on Q01 option A. Recommendations are proposals,
not confirmed requirements. Q05 preserves the documented preference for the
canonical draft's parent; Q06 clarifies the case in which that parent lacks the
requested document. The recognition mechanism and organization of validation
patterns remain for the design.

No reviewer wording suggestions have been received or applied in this first
round. The Markdown check passed for the effort directory using the repository
policy and baseline. Source-code behavior was described from the canonical
draft, not independently re-probed during this documentation task.

### Change summary for issue docs_layout_hardening (round 1)

#### Initial issue and question changes for issue docs_layout_hardening (round 1)

Created `docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md` from the canonical
draft as one issue. Added the current observations, expected contract, confirmed
scope boundaries, acceptance criteria, and source-provided examples and code
responsibilities.

Authored seven questions in the companion file and placed them into the issue
through `oqm`. The canonical draft was preserved. This is round 1, so there is
no preceding review round to compare.

### Writer response for issue docs_layout_hardening (round 1)

Writer response:

#### Writer response for the initial issue review for issue docs_layout_hardening (round 1)

Please assess whether the issue and its seven questions cover the source
draft's intended behavior and boundaries. In particular, check whether the
recommendations form a consistent discovery contract, whether fallback handling
needs further clarification, and whether any question should instead remain
for the later design review.

No prior reviewer feedback or disagreement exists. The writer will assess and
apply accepted intermediate feedback before publishing a replacement round.
Consolidation remains subject to the human's selection at the convergence gate.

### Reviewer focus for issue docs_layout_hardening (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-12T13:59:04+02:00
- Exchange: specification/issue/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for issue docs_layout_hardening round 1

#### Reviewer assessment of the layout-contract issue for issue docs_layout_hardening (round 1)

The issue is faithful to its canonical draft and keeps the three concerns
together without importing the review-resume acceptance instability. The five
recognition shapes in the observed-examples table match what
`_is_supported_docs_dir` (`tools/prompt_workflow_docs.py:444`) does today: a
full version at depth one, `COLLECTION_SLUG_RE` at depth two, so `topic`,
`images` and `sub` are accepted while `My_Slug` and `a.scratch` are rejected.
The seven questions are materially distinct, each option is a real alternative,
and I agree with every recommended option on substance.

What blocks convergence is not the direction of the answers. It is that two of
the questions describe current behavior incorrectly, one of the two directory
recognition call sites is missing from the issue, and three boundaries are left
undefined that the design cannot settle without reopening the requirement.

##### Two descriptions of current selection behavior that the code contradicts for issue docs_layout_hardening (round 1)

`select_document` (`tools/prompt_workflow_docs.py:593`) is
`most_recent(find_matching_documents(...))`, and `most_recent` (line 586) is
`max(paths, key=mtime)`. Among several matches, whether inside the canonical
draft's parent or across the fallback set, the shipped rule is that the most
recently modified file wins.

Q05 option A calls this "a unique match in the canonical draft's parent". There
is no uniqueness requirement in that directory today: two matching documents
there resolve by modification time. Q06 option C calls it "the first fallback
match" with a con about "directory ordering". Ordering plays no part.

This matters beyond wording. Both questions present their recommended option as
making an existing distinction explicit, when Q05 option A and Q06 option A each
replace the modification-time rule with something stricter. A behavior change
presented as a clarification is the kind of thing that gets dropped in the
design, and the confirmed-boundaries section already warns against treating a
proposal as a settled decision.

##### The two front doors differ on three axes, not on context alone for issue docs_layout_hardening (round 1)

Q05 frames the divergence as canonical-draft context. Reading the two paths:

| Axis | `resolve_document` (line 556) | `select_document` (line 593) |
| --- | --- | --- |
| Directory set | `docs_dirs_for_version(root, version)` (line 416) | `_topic_docs_dirs(root, topic)` (line 460): the draft's parent alone, otherwise every directory |
| Name match | `_exact_doc_matches` (line 512): one document type, exact folded slug | `_doc_matches` (line 485): every type in the role, plus `<slug>_<sub>` prefix matches |
| Several matches | raises `Ambiguous <type> document for ...` | `most_recent` picks by modification time |

The draft's reported example varies only the first axis, because the two copies
carry the same file name. Acceptance criterion 3 asks for the expected behavior
of both entry points, so the issue has to say which of these three axes it
settles and which it deliberately leaves alone.

##### Effort-directory recognition has two call sites for issue docs_layout_hardening (round 1)

`docs_dirs_for_version` applies `COLLECTION_SLUG_RE.fullmatch(sub.name)` at
`tools/prompt_workflow_docs.py:439` to the subdirectories of the full version
directory, independently of `_is_supported_docs_dir`. It is absent from the
existing-code-responsibilities list, and acceptance criterion 4 would be
satisfied by decoupling only one of the two from umbrella-row slug validation.

The consequence is sharper than a missing bullet. If Q01 option A adds a content
requirement to `_is_supported_docs_dir` alone, `resolve_document` keeps scanning
`docs/v1.2.3/images/` while every `docs_dirs` consumer stops. The release meant
to settle one front-door divergence would create a second one.

##### Q01 option A retires assertions two current tests hold for issue docs_layout_hardening (round 1)

The background says the concerns break nothing in the repository today, which
is true of the symptom and not of the contract. Two tests pin the behavior that
Q01 option A removes:

- `test_docs_dirs_supports_all_layouts`
  (`tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py:314`)
  creates an empty `docs/v9.8.0/topic` and asserts it is returned by
  `docs_dirs`.
- `test_docs_dirs_includes_version_slug_layout` (line 598) creates an empty
  `docs/v1.2.3/my_effort` and asserts it is returned by both `docs_dirs` and
  `docs_dirs_for_version`.

Acceptance criterion 5 speaks of "the existing end-to-end layout test" in the
singular. At least these two change, and the issue should say that the empty
directory stops being discoverable rather than leaving the design to discover
it from a red test.

##### Three boundaries the design cannot settle by itself for issue docs_layout_hardening (round 1)

First, the issue never defines an effort document, although Q01, Q02 and Q03 all
turn on the term. Q02 enumerates requirement, design, implementation plan and
validation plan in passing; the draft itself, the `review.<type>...md`
transcript that sits beside the documents, and an `a.*` scratch file are all
left unstated. A directory holding only its review transcript is a real case in
this very effort directory.

Second, slug comparison. `_slug_key` (line 468) folds `-` onto `_` because draft
slugs use `_` while requirement documents use `-`. Q03 asks for content matching
"both the enclosing version and slug" without saying whether that comparison
folds, so `docs/v1.2.3/my-effort/` holding `issue.v1.2.3.my_effort.md` has no
stated answer.

Third, what happens when the preferred directory set empties. `_topic_docs_dirs`
returns `matching or directories`. Under Q01 option A a directory that stops
qualifying drops out of `docs_dirs`, `matching` becomes empty, and workflow
selection silently widens from one directory to every supported directory.
Stricter recognition producing broader selection inverts the intent, and no
question covers it. Q06 assumes throughout that the canonical draft's parent is
still recognized.

### Question verdicts for issue docs_layout_hardening round 1

#### Reviewer verdicts on the seven open questions for issue docs_layout_hardening (round 1)

Every existing question is in scope for an issue: each one settles observable
behavior rather than a recognition mechanism. I agree with all seven recommended
options. Four need wording repairs, and three questions are missing.

##### Verdict on Q01 about excluding ordinary directories for issue docs_layout_hardening (round 1)

Keep the question. Options A and B are materially distinct and the consequences
are stated. My answer is option A, for the reason the issue gives: a folder
should not join effort discovery through its spelling alone.

Two additions are needed. The question has to name what counts as an effort
document, because Q02, Q03 and Q04 all inherit the term from here. The con for
option A also has to say that recognition becomes content-dependent: a directory
can enter and leave discovery as files are added, renamed or removed, which a
name-only test could never do, and two current tests assert that an empty
directory is discoverable.

##### Verdict on Q02 about discovery without a draft for issue docs_layout_hardening (round 1)

Keep the question as written. Options, consequences and the recommendation all
hold. My answer is option A: a requirement or a plan should not become invisible
because its working notes were removed, and a command that genuinely needs a
canonical draft can still check for one separately.

One addition: the enumeration in the question body (requirement, design,
implementation plan, validation plan) is the closest thing the issue has to a
definition of an effort document, so it should move into the expected-contract
section and be completed there rather than sitting inside a conditional
question.

##### Verdict on Q03 about matching the enclosing version and slug for issue docs_layout_hardening (round 1)

Keep the question. My answer is option A: the directory should represent the
effort it names, and accompanying unrelated files do not disqualify it.

The boundary is under-specified on one point that is behavior, not mechanism.
`_slug_key` folds `-` onto `_` so that a `my_effort` draft slug resolves
`my-effort` documents. Q03 must say whether the directory-to-document slug
comparison uses that same folding. Without it, `docs/v1.2.3/my-effort/` holding
`issue.v1.2.3.my_effort.md` has no stated outcome, and the design would be
choosing the requirement.

##### Verdict on Q04 about common folder names for issue docs_layout_hardening (round 1)

Keep the question, with one label change. My answer is option A: the concern is
ordinary content, not the words `images` or `sub`, and a reserved-name list
would need a scope nobody wants to maintain.

Q04 is conditional on Q01 option A in exactly the way Q02 and Q03 are: if Q01
settles as option B, names are the only signal and a reserved list becomes the
only available answer. The issue marks the conditionality on Q02 and Q03 and
omits it here.

##### Verdict on Q05 about canonical-draft context for issue docs_layout_hardening (round 1)

Keep the question and the recommended direction, but rewrite option A. My answer
is option A as repaired: strict ambiguity in general resolution, and workflow
selection allowed to use the canonical draft's parent.

As written, option A says selection uses "a unique match in the canonical
draft's parent". The code applies no uniqueness test there: `select_document`
returns the most recently modified match. Option A therefore adds a requirement
while claiming to preserve one. Suggested replacement for the option line:

```text
- Option A: Keep strict ambiguity in general resolution, and let workflow
  selection resolve within the canonical draft's parent alone when that
  directory is recognized.
  - pro: Makes the existing contextual distinction explicit and keeps the
    documented effort-directory preference.
  - con: Callers must understand why the two entry points differ, and the
    behavior when that directory holds several matches still needs a rule.
```

The question body should also state that the two entry points differ on three
axes today (directory set, name-match breadth, and the rule applied when several
documents match) and say which of them Q05 settles.

##### Verdict on Q06 about the document missing beside the draft for issue docs_layout_hardening (round 1)

Keep the question and the recommended option. My answer is option A: a unique
fallback match is useful, several competing matches should be reported rather
than picked, and absence should be reported as absence.

Option C misdescribes the current rule. Selection does not take the first match
and does not depend on directory ordering: `most_recent` takes the most recently
modified match. Since option C is the closest option to shipped behavior, the
issue must label it as such, so a reader can see that option A is a deliberate
change and not a restatement. Suggested replacement:

```text
- Option C: Keep the current rule and return the most recently modified match
  among the alternatives.
  - pro: Current behavior, so no caller changes and no duplicate cleanup.
  - con: The chosen document depends on file timestamps rather than on effort
    identity, and the choice is silent.
```

The question body should also say which directories form the fallback set, since
`_topic_docs_dirs` falls back to every supported directory rather than to the
other directories of the same version.

##### Verdict on Q07 about the compatibility scope for issue docs_layout_hardening (round 1)

Keep the question as written. My answer is option A: harden the version-and-slug
layout, keep the other four layouts and the current accepted name shapes.

One boundary is worth recording in the answer text rather than leaving it
implicit: `docs/vX.Y/vX.Y.Z/<slug>/` is not recognized today, and
`docs_relative_dir` only ever produces `docs/<full-version>/<slug>`, so a nested
slug directory under the minor-version layout stays rejected. Acceptance
criterion 1 asks for the rejected cases, and this is one of them.

##### Missing question Q08 about the second recognition call site for issue docs_layout_hardening (round 1)

`docs_dirs_for_version` filters the subdirectories of the full version directory
with `COLLECTION_SLUG_RE` independently of `_is_supported_docs_dir`. The issue
lists only the second. Proposed question:

```text
### Q08: Must every directory-recognition call site apply the same effort rule?

Two code paths decide today whether `docs/vX.Y.Z/<slug>/` is an effort
directory: the general layout predicate used by `docs_dirs`, and the
version-scoped listing used by document resolution. Must the settled rule
govern both, so that the two never disagree about the same directory?

Option A: Apply one settled rule at every recognition site.
  pro: `resolve_document` and every `docs_dirs` consumer see the same set of
  effort directories, and criterion 4 holds for both.
  con: More call sites change in this effort.
Option B: Apply the new rule only where the recognition concern was reported.
  pro: Smaller change.
  con: Document resolution keeps scanning an ordinary folder that discovery
  already rejects, which creates a second front-door divergence.

Recommended and answer: option A.
```

##### Missing question Q09 about several matching documents in one directory for issue docs_layout_hardening (round 1)

Q05 and Q06 both need a rule for "several matches remain" and neither states the
current one. Proposed question:

```text
### Q09: Which document does workflow selection return when several match?

Workflow selection currently returns the most recently modified match, inside
the canonical draft's parent as well as across the fallback set. Must that
timestamp rule stay, or must several matches be reported instead?

Option A: Report several matches as unresolved, everywhere selection applies.
  pro: One rule for both entry points once a directory no longer disambiguates.
  con: Retires a rule callers rely on, and an effort with a stale duplicate
  stops resolving until it is cleaned up.
Option B: Keep the most-recent rule everywhere.
  pro: No caller changes, and the layout work stays within its reported gaps.
  con: Selection stays silent about duplicates that resolution rejects.
Option C: Keep the most-recent rule inside the canonical draft's parent and
report several matches only in the fallback set.
  pro: Matches the intent of Q05 and Q06 as recommended.
  con: Two rules to document and test.

Recommended and answer: option C, because it is what Q05 option A and Q06
option A already imply when read together.
```

##### Missing question Q10 about a canonical-draft parent that stops qualifying for issue docs_layout_hardening (round 1)

Under Q01 option A a directory can fail the effort test. Workflow selection
prefers the canonical draft's parent only while that directory is in the
recognized set, and falls back to every supported directory otherwise. Proposed
question:

```text
### Q10: What happens when the canonical draft's own directory is not recognized?

Directory preference is applied by intersecting the recognized directories with
the canonical draft's parent. If that parent fails the settled effort test, the
preference disappears and selection widens to every supported directory. Is
that the expected result?

Option A: Report the unrecognized effort directory rather than widening.
  pro: Stricter recognition never produces broader selection.
  con: A partially populated effort directory stops resolving until corrected.
Option B: Keep the existing fallback to every supported directory.
  pro: No behavior change beyond the recognition rule itself.
  con: A directory failing the effort test makes selection search more widely
  than before, which inverts the intent of Q01.

Recommended and answer: option A.
```

### Requested changes for issue docs_layout_hardening round 1

Requested changes:

#### Requested changes to the layout-contract issue for issue docs_layout_hardening (round 1)

Each entry names the section, the defect, and the change. Section titles are the
ones in the reviewed issue.

##### Change 1 in current directory recognition and document selection for issue docs_layout_hardening (round 1)

Item 3 describes the divergence as ambiguity against a selected copy. Replace it
with the three axes on which the two entry points differ, so acceptance
criterion 3 has something exact to pin:

```text
3. `resolve_document` and `select_document` differ on three points, not one.
   They search different directory sets: resolution takes every supported
   directory of the version, while selection takes the canonical draft's parent
   alone when that directory is recognized and every supported directory
   otherwise. They match names differently: resolution requires one document
   type and an exact slug, while selection accepts every type of a role and
   also `<slug>_<sub>` sub-topics. They disagree when several documents match:
   resolution reports the match as ambiguous, while selection returns the most
   recently modified one.
```

##### Change 2 in current directory recognition and document selection for issue docs_layout_hardening (round 1)

Item 4 names `COLLECTION_SLUG_RE` as the directory-name check. Add the second
call site in the same item, since both apply that pattern to
`docs/vX.Y.Z/<slug>/` and only one is currently mentioned anywhere in the issue:

```text
4. The directory-name check reuses `COLLECTION_SLUG_RE`, which was introduced
   for slug validation in umbrella collection tables. Two independent call
   sites apply it to the same directories: the general layout predicate behind
   `docs_dirs`, and the version-scoped listing behind document resolution.
```

##### Change 3 in the observed examples table for issue docs_layout_hardening (round 1)

The second table reports the current result for duplicate copies. Add the rule
that produced it, because "Returns the copy under `docs/v1.2.3/`" reads as a
directory preference when it is also a timestamp comparison:

```text
| `select_document(...)` | Returns the most recently modified match, here the copy under `docs/v1.2.3/` |
```

##### Change 4 in the expected documentation-discovery contract for issue docs_layout_hardening (round 1)

Add a paragraph defining the term the recognition questions depend on:

```text
An effort document is a document this workflow writes for one effort: the
draft, the feature-request or issue, the design, the implementation plan and
the validation plan. A review transcript, an ignored `a.*` scratch file and any
other file are not effort documents, so a directory holding only those does not
become an effort directory.
```

##### Change 5 in the expected documentation-discovery contract for issue docs_layout_hardening (round 1)

The duplicate paragraph states that results need not become identical. Add the
sentence that makes the scope of this issue explicit:

```text
The contract must say which of the three differences between the two entry
points it settles, and state that the remaining ones stay as they are.
```

##### Change 6 in the consequences of the unsettled layout contract for issue docs_layout_hardening (round 1)

The section presents the recognition concern as latent. Add:

```text
Hardening recognition is not a behavior-free change. Two current tests create
an empty directory under a version directory and assert that discovery returns
it, so any content requirement retires those assertions along with the
directory shapes they cover.
```

##### Change 7 in the acceptance criteria for the layout contract for issue docs_layout_hardening (round 1)

Criterion 2 accepts a probe where the contract needs a regression guard, and
criterion 4 covers one call site. Criterion 5 is singular. Replace all three and
add two criteria for the answers that currently have none:

```text
2. Tests pin those accepted and rejected outcomes against the settled rule. The
   examples below describe the source draft's current observations, not
   predetermined target outcomes.
4. Effort-directory recognition is independent of changes made only to
   umbrella-row slug validation, at every call site that decides whether a
   `docs/vX.Y.Z/<slug>/` directory is an effort directory, and those call sites
   agree with each other for the same directory.
5. The existing layout tests are extended to meet any new conditions imposed on
   an effort directory, including the tests that currently assert an empty
   directory is discoverable, and they continue to verify discovery of the
   effort's sibling documents.
7. The result of workflow selection is documented and tested for each fallback
   case: a unique match elsewhere, several competing matches, and no match at
   all.
8. The result is documented and tested for a canonical draft whose own
   directory does not satisfy the settled effort rule.
```

##### Change 8 in the existing code responsibilities identified by the draft for issue docs_layout_hardening (round 1)

Add the entries for the second call site and for the selection rule that the
questions depend on:

```text
- `docs_dirs_for_version`: lists the supported directories of one version and
  applies its own `COLLECTION_SLUG_RE` check to the version directory's
  subdirectories.
- `most_recent`: returns the most recently modified path, and is the rule
  `select_document` applies when several documents match.
- `_slug_key`: folds `-` onto `_` so a `my_effort` slug and a `my-effort`
  document name compare equal.
```

##### Change 9 in the open questions section for issue docs_layout_hardening (round 1)

Add Q08, Q09 and Q10 from the reviewer verdicts, mark Q04 conditional on Q01
option A as Q02 and Q03 already are, and apply the quoted option replacements
for Q05 option A and Q06 option C.

### Writer instructions for issue docs_layout_hardening round 1

#### Writer instructions for the next layout-contract round for issue docs_layout_hardening (round 1)

Work only inside the reviewed issue. The canonical draft stays as it is, and no
recognition mechanism, pattern organization or code change belongs in this
document.

1. Repair the two current-behavior statements before anything else, because the
   rest of the round depends on them. Workflow selection returns the most
   recently modified match, not a unique match and not the first match.
2. Add the three missing questions in the reviewer verdicts, keeping the
   established question shape: body, BBQ picture, options with one pro and one
   con each, recommended option with arguments, and an answer paragraph.
3. Record the missing second recognition call site in the existing-code
   responsibilities list and widen acceptance criterion 4 to both call sites.
4. State what counts as an effort document in the expected-contract section,
   listing the accepted document kinds and the files that do not qualify.
5. Say plainly in the background or the consequences section that the
   recognition answer changes behavior current tests assert, and correct the
   singular "existing end-to-end layout test" in acceptance criterion 5.
6. Add acceptance criteria for the fallback outcomes and for the
   canonical-parent cases, which currently have settled answers and no
   criterion.
7. Apply the option and question-body replacements in the verdicts file where
   the wording is quoted, and keep every heading unique in the document.

Do not change the recommended option or the answer of any existing question:
all seven directions are accepted as they stand. The requested work is precision
about current behavior, coverage of the missing cases, and criteria that match
the answers.

After applying the changes, publish a replacement request for another automated
round. Consolidation stays with the human at the convergence gate, and this
answer does not recommend it.

### Final reviewer decision for issue docs_layout_hardening round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-09-12T14:07:04+02:00
- Exchange: specification/issue/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for issue docs_layout_hardening (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
Review round: 2

### Requestor assessment for issue docs_layout_hardening (round 2)

#### Assessment of the documentation-layout issue for issue docs_layout_hardening (round 2)

The user selected one issue requirement followed by review of its questions.
The reviewed document is derived from
`docs/v0.12.0/draft.v0.12.0.docs_layout_hardening.md`, with settled type `issue`,
version `v0.12.0`, and slug `docs_layout_hardening`. There is no umbrella.

The requirement retains all three source concerns: effort-directory
recognition, duplicate-document selection, and independence from umbrella-row
slug validation. It preserves the optional-slug contract and excludes the
unrelated review-resume acceptance instability.

Ten open questions now cover the original seven cases plus agreement between
recognition paths, several matching documents inside a selected scope, and an
unrecognized canonical parent. Each has distinct options with pros and cons, a
recommendation and a proposed answer. Q02, Q03 and Q04 state their dependency on
content-based recognition. Q03 now defines exact version equality and folded
hyphen/underscore slug equality. The effort-document vocabulary includes the
canonical workflow documents and excludes transcripts, scratch and unrelated files.

The writer verified the review's main code findings in
`tools/prompt_workflow_docs.py` and the two cited layout tests. Selection uses
modification time, two listing paths recognize slug directories independently,
and empty-directory recognition is already asserted by tests. Accepted reviewer
wording and coverage changes are applied. The first seven recommended directions
are retained; Q08 recommends A, Q09 recommends C, and Q10 recommends A.

One additional precision is necessary: a recognized canonical parent with no
matching sibling currently returns no match. Broad fallback is triggered only
when the parent is unrecognized. Q06 explicitly proposes a new missing-sibling
fallback, identifies B as the current result for that trigger, and offers C as
applying the existing timestamp rule to that new trigger. Q10 separately proposes
replacing the existing unrecognized-parent fallback with an explicit failure.
These recommendations are deliberate changes, not claims about current behavior.

The original duplicate probe lacks recorded timestamps, so the issue states the
verified selection rule without inventing which timestamp made that probe's
reported version-directory copy win. Name-match breadth and local timestamp-tie
behavior remain unchanged in scope. The recognition mechanism and pattern
organization remain for the design.

The questions and options appear sufficient after these repairs; no further
issue-level question is apparent. Recommendations remain proposals pending the
human consolidation gate. Please verify the revised current/target distinctions
and whether the ten acceptance criteria fully cover the proposed contract.

### Change summary for issue docs_layout_hardening (round 2)

#### Changes following the first issue review for issue docs_layout_hardening (round 2)

Corrected the current directory scope, name matching and multiplicity rules.
Explicitly separated missing-sibling absence from unrecognized-parent fallback.
Added the independent version-scoped listing, timestamp selection, slug folding,
and reviewed code/test references.

Defined effort-document kinds and exclusions; documented existing assertions
that content-based recognition will replace. Expanded acceptance coverage to
both recognition paths, fallback outcomes, canonical-parent eligibility, local
multiple matches, document kinds, identity comparison and unsupported layout shape.

Repaired Q01 and Q03 through Q07, retained all seven existing recommended
directions, and added Q08 through Q10 with full options and proposed answers.
Placed the revised question section through `oqm`. Preserved the canonical draft
and made no implementation changes.

### Writer response for issue docs_layout_hardening (round 2)

Writer response:

#### Writer response to the first issue review for issue docs_layout_hardening (round 2)

Accepted the review's substantive changes and all three additional questions.
The document now covers both recognition paths, defines effort-document kinds,
states separator equivalence, records compatibility boundaries, and adds the
missing selection acceptance cases. The requested option repairs have been
applied with the original recommended directions preserved.

The code read required precision beyond the suggested Q06 option C wording:
`_topic_docs_dirs` returns the recognized canonical parent exclusively even when
it contains no requested sibling. Consequently B, not C, describes today's
result for Q06's missing-sibling trigger. A introduces unique fallback; C offers
the current timestamp selection rule applied to that newly introduced fallback.
The issue clearly labels these changes. Q10 covers the separate existing
unrecognized-parent trigger. This accepts the review's recommended direction
while avoiding an inaccurate current-behavior label.

The observed-example table identifies the timestamp rule within the selected
directory set, but does not assert that the original probe compared timestamps
across both directories: its timestamps and complete context were not recorded
in the source draft. The canonical-parent filter applies before timestamp choice.

No substantive recommendation is rejected and there is no outstanding policy
disagreement. Please reassess the ten questions and their acceptance criteria.
Consolidation still requires the human's selection at convergence.

### Reviewer focus for issue docs_layout_hardening (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-09-12T14:11:30+02:00
- Exchange: specification/issue/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for issue docs_layout_hardening round 2

#### Reviewer assessment of the revised layout contract for issue docs_layout_hardening (round 2)

Every requested change from the first round is applied, and the writer's
pushback on Q06 is correct. `_topic_docs_dirs` returns `matching or
directories`: when the canonical draft's parent is in the recognized set, that
directory is the whole search, so a recognized parent without the requested
sibling yields absence and never reaches the broad fallback. My first-round
suggestion that option C described current behavior for that trigger was wrong,
and the revised Q06 states the trigger correctly.

##### Verification of the new current-behavior statements for issue docs_layout_hardening (round 2)

I checked each new claim against `tools/prompt_workflow_docs.py`:

- The three axes in item 3 hold: `docs_dirs_for_version` against
  `_topic_docs_dirs`, `_exact_doc_matches` against `_doc_matches`, and the
  ambiguity raise against `most_recent`.
- Item 5 holds, including the version requirement during a broad search:
  `_doc_matches` builds the prefix `f"{doc_type}.{version}."`, so widening the
  directory set never widens the version.
- Item 4 and Q08 are complete, not merely correct. The two recognition paths are
  the only two: `COLLECTION_SLUG_RE` is applied to a directory name at exactly
  `_is_supported_docs_dir` and inside `docs_dirs_for_version`, and every other
  consumer in `tools/` reaches directories through `docs_dirs`.
- The observed-examples note is honest about what the probe recorded. The
  canonical-parent filter does run before the timestamp rule, so the reported
  result does not prove a timestamp comparison took place.

##### Acceptance coverage against the ten proposed answers for issue docs_layout_hardening (round 2)

The writer asked whether the ten criteria cover the contract. Mapping each
answer to its criterion: Q01 to 1, 2 and 10; Q02 and Q03 to 10; Q04 to 1 and 2;
Q05 to 3; Q06 to 7; Q07 to 10; Q08 to 4; Q09 to 9 and 7; Q10 to 8. Nothing is
uncovered.

One criterion is ambiguous in a way that can authorize the opposite of Q07.
Criterion 5 says the existing layout tests are extended "including the tests
that currently expect empty directories to be discoverable". Those tests expect
five empty directories across four layouts, and Q07 option A changes only the
version-and-slug one. As written, criterion 5 reads as though every
empty-directory expectation is in play, so an implementer could remove
`docs/v9.8`, `docs/v9.8.0` and `docs/v9.8/v9.8.0` from discovery and still
claim the criterion.

##### What still needs a change for issue docs_layout_hardening (round 2)

Three precision items remain, all small and all in question text rather than in
any answer:

Q05 option A now ends with "when that directory is recognized and contains
matching documents". That clause decides Q06. Today the parent is the whole
search whether or not it contains a match, and under Q06 option B it would stay
that way, so Q05 option A only reads correctly if Q06 settles as A. An option
should not depend on a later question's outcome.

Q06 option A carries its own multiplicity rule ("report ambiguity when several
matches remain") while Q09 exists to settle multiplicity. The recommended
answers agree, so nothing contradicts today, but Q06 A combined with Q09 B would
contradict, and the document does not say which question governs.

Q10 describes its trigger as content-based recognition introducing an
unrecognized parent. That trigger already exists without any change to
recognition: `relevant_drafts` accepts a draft anywhere under `docs/`, so a
draft in an unsupported directory such as `docs/archive/` or at depth three
already produces the broad fallback today. Q10 option A therefore also changes
an existing case, which is worth stating for the same reason the other
current-target distinctions were.

No answer needs to change. All ten recommended directions are accepted,
including Q08 option A, Q09 option C and Q10 option A.

### Question verdicts for issue docs_layout_hardening round 2

#### Reviewer verdicts on the ten revised questions for issue docs_layout_hardening (round 2)

Ten questions now cover the contract and I have no eleventh to propose. The
recognition side is settled, the selection side is separated into the four
cases that actually differ, and every answer is one I would choose. Three
questions need a clause repaired; the other seven are accepted as they stand.

##### Accepted without change in round two for issue docs_layout_hardening (round 2)

Q01, Q02, Q03, Q04, Q07 and Q08 are accepted as written, with answers A, A, A,
A, A and A.

Q01 now names the effort-document vocabulary and its option A con states the
content-dependence and the retired test expectations. Q03 now fixes exact
version equality, folded slug equality, and the worked `my-effort` against
`my_effort` example, and its new option C makes the separator decision a real
choice rather than an assumption. Q04's conditionality is marked. Q07's answer
records the unsupported `docs/vX.Y/vX.Y.Z/<slug>/` shape. Q08 asks exactly the
right thing, and its two paths are the only two that exist.

Q09 is accepted as written and my answer is option C, for the reason the
question gives: canonical-parent context earns the timestamp rule, and a
fallback set has no context to justify a silent choice. Keeping the local
timestamp-tie behavior outside this effort's scope is the right boundary.

##### Verdict on the Q05 clause that decides Q06 for issue docs_layout_hardening (round 2)

My answer stays option A. Remove the trailing condition, which settles a case
Q06 owns:

```text
- Option A: Keep strict ambiguity in general resolution and let workflow
  selection resolve within the canonical draft's parent alone when that
  directory is recognized.
  - pro: Makes the existing contextual distinction explicit and preserves the
    documented effort-directory preference.
  - con: Callers must understand the different results. What happens when that
    parent holds no match is settled by Q06, and several matches inside it by
    Q09.
```

The recognized parent is the whole search set today whether or not it contains
a match. Writing "and contains matching documents" into Q05 assumes Q06 option
A, so a reader who settles Q06 as B finds Q05 describing something the code
never did and never will.

##### Verdict on the Q06 multiplicity clause for issue docs_layout_hardening (round 2)

My answer stays option A. Q06 should settle whether a fallback exists and leave
how many matches it tolerates to Q09:

```text
- Option A: Allow a fallback to other recognized documentation directories,
  with the multiplicity rule settled by Q09 and absence reported when nothing
  matches.
  - pro: Supports a recoverable partial layout instead of a dead end.
  - con: Introduces fallback where a recognized parent currently yields
    absence, and lets an effort draw a missing document from another directory.
```

Option C then reads as the same fallback under the other multiplicity rule,
which is where Q09 option B would put it. As the three options stand, answering
Q06 A and Q09 B produces two different rules for one situation and the document
does not say which wins.

##### Verdict on the Q10 trigger description for issue docs_layout_hardening (round 2)

My answer stays option A. Add the existing trigger to the question body, after
the sentence about content-based recognition:

```text
This case also exists today, before any recognition change: a draft is
discovered anywhere under `docs/`, so a draft in an unsupported directory such
as `docs/archive/` or below the accepted depth already leaves its parent out of
the recognized set and already widens selection to every supported directory.
```

That matters for the same reason the other current-target labels do. Option A
does not only prevent a case that stricter recognition would create, it also
replaces one that exists now, and its con should say that a draft in an
unsupported location stops resolving siblings instead of searching everywhere.

### Requested changes for issue docs_layout_hardening round 2

Requested changes:

#### Requested changes to the revised layout contract for issue docs_layout_hardening (round 2)

Four edits. Nothing else in the document needs work.

##### Change A in the acceptance criteria for the layout contract for issue docs_layout_hardening (round 2)

Criterion 5 can be read as putting all five empty-directory expectations in
play, which would contradict Q07 option A. Replace it:

```text
5. The existing layout tests are extended to meet any new conditions imposed on
   an effort directory. Only the version-and-slug expectation changes: an empty
   `docs/vX.Y/`, `docs/vX.Y.Z/` or `docs/vX.Y/vX.Y.Z/` directory stays
   discoverable. Coverage continues to verify discovery of the effort's sibling
   documents.
```

##### Change B in Q05 options for issue docs_layout_hardening (round 2)

Remove the clause that settles a Q06 case, using the replacement option text in
the reviewer verdicts. The recognized canonical parent is the entire search set
today whether or not it holds a matching document.

##### Change C in Q06 options for issue docs_layout_hardening (round 2)

Move the multiplicity rule out of option A and into a reference to Q09, using
the replacement option text in the reviewer verdicts. Keep option B and option
C as they are: with option A rewritten, option C reads as the same fallback
under Q09's other multiplicity rule, which is exactly the relationship the two
questions should have.

##### Change D in the Q10 question body and options for issue docs_layout_hardening (round 2)

Add the existing trigger sentence from the reviewer verdicts, and extend the
option A con so it names both consequences:

```text
  - con: A mismatched or incomplete effort must be corrected before selection
    proceeds, and a draft already sitting in an unsupported directory stops
    resolving siblings instead of searching every supported directory.
```

### Writer instructions for issue docs_layout_hardening round 2

#### Writer instructions for the third layout-contract round for issue docs_layout_hardening (round 2)

1. Apply the four requested changes. Three are single clauses in Q05, Q06 and
   Q10; one replaces acceptance criterion 5.
2. Change no answer and no recommended option. All ten directions are accepted,
   including the three questions added in round two.
3. Add no new question. The ten cover the contract, and I have no eleventh.
4. Do not revisit the effort-document vocabulary, the three-axis description,
   the second recognition path, the observed-examples note, or the other nine
   acceptance criteria. They are settled and verified against the code.

The Q06 correction from round two is accepted in full: a recognized canonical
parent without the requested sibling yields absence today, and the broad
fallback belongs to the unrecognized-parent trigger. The requested edits keep
that distinction and only stop Q05 and Q06 from deciding each other's cases.

Publish a replacement request for another automated round. With these four
edits applied and nothing else changed, I expect that round to be
convergence-ready. Consolidation stays with the human at the convergence gate,
and this answer does not recommend it.

### Final reviewer decision for issue docs_layout_hardening round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-09-12T14:14:01+02:00
- Exchange: specification/issue/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for issue docs_layout_hardening (round 3)

Umbrella draft: none
Reviewed specification: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
Review round: 3

### Requestor assessment for issue docs_layout_hardening (round 3)

#### Assessment after the second issue review for issue docs_layout_hardening (round 3)

The ten questions and recommended answers cover the issue's behavior and
acceptance boundaries. No additional question is apparent. The reviewer accepted
all ten directions in round 2 and requested four precision edits; all four are
now applied. Existing options and proposed answers remain sufficient, with the
same recommendations: A for every question except Q09, which recommends C.

Acceptance criterion 5 explicitly preserves empty directories in the older
layouts. Q05 delegates the no-match case to Q06 and the several-match case to
Q09. Q06 option A delegates multiplicity to Q09. Q10 now states the existing
unsupported-location fallback and the consequence of replacing it. The relevant
draft discovery code confirms that supported directory shape is not a condition
of recognizing a branch-relevant draft under `docs/`.

Reviewer wording suggestions for this round have been applied. The original
ten-question scope, other acceptance criteria, vocabulary, examples and
recommended answers are preserved. Recommendations remain proposals for the
human consolidation gate. No implementation change or recognition mechanism
has been introduced.

### Change summary for issue docs_layout_hardening (round 3)

#### Changes following the second issue review for issue docs_layout_hardening (round 3)

Applied only the four requested precision changes: acceptance criterion 5,
Q05 option A and its con, Q06 option A and its pro, and Q10's trigger description
and option A con. The Q10 text says a relevant draft can be discovered under
`docs/`, preserving the existing branch-relevance condition.

Replaced the question section through `oqm`. Added no question, changed no
recommended answer, and preserved the canonical draft and implementation files.

### Writer response for issue docs_layout_hardening (round 3)

Writer response:

#### Writer response to the second issue review for issue docs_layout_hardening (round 3)

Accepted all four requested changes and applied them to the reviewed issue.
The recognized-parent preference no longer assumes Q06's outcome, and Q06
option A explicitly defers multiplicity to Q09. Criterion 5 now protects the
older layouts' empty-directory recognition. Q10 identifies both existing
unsupported-location behavior and newly possible content-based rejection.

All ten recommended directions and their answer paragraphs remain unchanged.
There is no disagreement and no new question. Please confirm whether these
repairs make the issue ready for the human consolidation gate.

### Reviewer focus for issue docs_layout_hardening (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-09-12T14:17:22+02:00
- Exchange: specification/issue/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for issue docs_layout_hardening round 3

#### Reviewer assessment of the settled layout contract for issue docs_layout_hardening (round 3)

The four requested edits are applied exactly and nothing else moved. Acceptance
criterion 5 now names the three older-layout directories that stay discoverable
when empty, so it can no longer be read as authorizing what Q07 option A
forbids. Q05 option A no longer decides the no-match case and its con routes
that case to Q06 and several matches to Q09. Q06 option A defers multiplicity
to Q09. Q10 carries the existing trigger and the added consequence in its con.

The Q10 sentence is accurate as written: draft discovery requires only that the
path sit under `docs/`, so an unsupported location already leaves a parent out
of the recognized set today, and the sentence keeps the branch-relevance
condition rather than claiming every draft under `docs/` is discovered.

##### Coverage of the four selection cases for issue docs_layout_hardening (round 3)

The selection side is now partitioned with no gap and no overlap. A recognized
parent holding matches is Q05. A recognized parent holding none is Q06. Several
matches inside a recognized parent, and several in a permitted fallback, are
Q09. A parent that fails the effort rule is Q10. Each case has one owning
question, one answer, and one acceptance criterion: 3, 7, 9 and 8.

##### Coverage of the recognition side for issue docs_layout_hardening (round 3)

Q01 sets content-based eligibility, Q02 keeps a draft-less directory
discoverable, Q03 fixes exact version equality with folded slug equality, Q04
refuses reserved names, Q07 confines the change to the version-and-slug layout,
and Q08 applies one rule at both recognition paths. Criteria 1, 2, 4, 5 and 10
carry them, and the effort-document vocabulary in the expected-contract section
gives all six the same term to stand on.

##### Verification against the implementation for issue docs_layout_hardening (round 3)

Every current-behavior statement in the document matches
`tools/prompt_workflow_docs.py` as I read it across the three rounds: the three
axes separating the two entry points, the exclusive recognized-parent search,
the version requirement that survives a broad directory search, the timestamp
rule, the hyphen and underscore folding, and the two directory-recognition
paths being the only two. The two empty-directory tests named in the
consequences section are the ones that change.

##### Why this is convergence-ready for issue docs_layout_hardening (round 3)

Ten questions, ten answers, ten criteria, and no decision left implicit. What
remains is one phrase of polish recorded in the covered wording, which does not
change any answer and does not need a round of its own. The recognition
mechanism, the organization of the validation patterns, and the shape of the
fallback search stay with the design, which is where this issue left them.

This recommendation is advisory. The consolidation choice belongs to the human
at the convergence gate.

### Question verdicts for issue docs_layout_hardening round 3

#### Reviewer verdicts on the settled ten questions for issue docs_layout_hardening (round 3)

All ten questions are accepted as written. No question is missing, none is
redundant, none is outside the issue's scope, and none belongs to the later
design review. Every option set offers materially distinct alternatives with
their consequences stated.

##### Answers this reviewer would choose in round three for issue docs_layout_hardening (round 3)

| Question | Answer | Reason in one line |
| --- | --- | --- |
| Q01 | A | A folder should not join effort discovery through its spelling alone. |
| Q02 | A | A requirement or plan should not vanish with its working notes. |
| Q03 | A | The directory should name the effort it holds, with the separator equivalence the code already applies. |
| Q04 | A | The concern is ordinary content, not the words `images` and `sub`. |
| Q05 | A | The canonical draft identifies the effort's directory; a general resolver has no such context. |
| Q06 | A | A missing sibling should be recoverable without a silent choice among competitors. |
| Q07 | A | Three named contract gaps, not a documentation-layout migration. |
| Q08 | A | One directory must have one eligibility result whichever listing a caller uses. |
| Q09 | C | Parent context earns the timestamp rule; a fallback set has no context to justify a silent pick. |
| Q10 | A | Hardening recognition must not make document selection less constrained. |

##### Questions this reviewer considered adding and rejected for issue docs_layout_hardening (round 3)

Name-match breadth, the difference between an exact type with a folded slug and
a role with `<slug>_<sub>` subtopics, is the one remaining divergence between
the two entry points. The expected-contract section declares it retained and
out of scope, which is itself an issue-level decision rather than an omission,
and widening it would pull umbrella subtopic resolution into a
documentation-layout effort.

Timestamp ties inside a recognized parent are declared out of scope by Q09's
answer. Two files with the same modification time are a property of
`most_recent`, not of the layout contract.

The bootstrap ordering of directory creation before the first draft write is a
transient inside one workflow command, not an observable discovery contract.

##### Question quality note carried into the covered wording for issue docs_layout_hardening (round 3)

The three questions repaired in round two read correctly now. Q06's
recommendation and answer paragraphs still describe the choice as a unique-match
fallback, which restates Q09 option C's outcome inside Q06 after option A
delegated multiplicity to Q09. The recommended answers agree, so nothing
contradicts. It is recorded as optional polish rather than a change request.

### Convergence evidence for issue docs_layout_hardening round 3

Covered wording:

#### Covered wording for the layout-contract issue for issue docs_layout_hardening (round 3)

One optional polish item. It changes no answer, no option and no acceptance
criterion, and the issue is convergence-ready with or without it. Apply it
during consolidation if the human keeps this recommendation, or leave it.

##### Optional polish in the Q06 recommendation and answer for issue docs_layout_hardening (round 3)

Q06 option A now defers multiplicity to Q09, while the recommendation and answer
paragraphs still call the choice a unique-match fallback. That phrase is Q09
option C's outcome stated a second time inside Q06. Suggested replacements:

```text
#### Recommended option for Q06 (with arguments for this choice)

Option A: Introduce an explicit fallback rather than a dead end, under the
multiplicity rule Q09 settles. This changes current behavior when the recognized
canonical parent lacks the requested sibling; it is not just clarification of
an existing fallback trigger.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: Accept a fallback for a missing sibling because it supports recovery
of a partial layout, and leave to Q09 how many candidates that fallback
tolerates.
```

##### Wording confirmed as correct in round three for issue docs_layout_hardening (round 3)

The following read correctly and need no further change: acceptance criterion 5
and its three preserved older-layout directories, Q05 option A and its con, Q06
option A and its pro and con, Q10's added trigger paragraph and its option A
con, the effort-document vocabulary, the three-axis description of the two
entry points, the observed-examples note about the probe's unrecorded
timestamps, and the code-responsibilities list.

Convergence rationale:

#### Convergence rationale for the layout-contract issue for issue docs_layout_hardening (round 3)

Across three rounds the issue moved from seven questions with two incorrect
descriptions of current behavior to ten questions whose every factual claim I
have checked against `tools/prompt_workflow_docs.py` and the two layout tests.

Round one found that workflow selection was described as returning a unique or
first match when it returns the most recently modified one, that the two entry
points differ on three axes rather than on canonical-draft context alone, that
a second directory-recognition path was absent from the issue, that two current
tests pin the empty-directory recognition the answers retire, and that the
effort-document term, the slug comparison rule and the unrecognized-parent case
were undefined. Round two verified the writer's correction that a recognized
parent lacking the requested sibling yields absence today, accepted it, and
asked for four precision edits. Round three finds all four applied and nothing
else disturbed.

Every in-scope decision is settled. The recognition side has one rule, one
vocabulary, one scope and one agreement requirement across both call sites. The
selection side is partitioned into four cases with one owning question each and
no overlap. Ten acceptance criteria carry the ten answers, and the boundaries
that stay out, name-match breadth and timestamp ties inside an effort's own
directory, are declared rather than forgotten.

What remains is a single phrase in Q06's recommendation that restates Q09's
outcome. It is recorded in the covered wording and contradicts nothing, so it
does not justify another automated round.

Nothing in the document prescribes a recognition mechanism, a pattern
organization or an implementation shape. Those stay with the design, which is
the boundary this issue set for itself in round one and has kept.

This recommendation is advisory and authorizes nothing. The consolidation
choice, and the labels offered for it, belong to the human at the convergence
gate.

### Writer instructions for issue docs_layout_hardening round 3

#### Writer instructions at the layout-contract convergence gate for issue docs_layout_hardening (round 3)

No change is requested. The four round-two edits are applied correctly and the
issue is ready for the human's choice.

1. Present the ten questions, their recommended options and their answers to the
   human with the two registered labels, and make no edit before that choice.
2. If the human selects consolidation, the optional Q06 polish in the covered
   wording may be applied with it. Skipping it changes nothing.
3. If the human selects another round instead, that round needs a concrete
   reason from the human: this reviewer has none to supply.

Do not treat this recommendation as authorization. Consolidation, the decision
table and the removal of the open-questions section stay with the owning
workflow after the human confirms.

### Final reviewer decision for issue docs_layout_hardening round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-09-12T16:22:29+02:00
- Exchange: specification/issue/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/issue.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
