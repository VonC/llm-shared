# Specification review transcript for v0.11.0

- Exchange: specification/feature-request/v0.11.0/markdown-check
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-23T20:50:38+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for feature-request markdown-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
Review round: 1

### Requestor assessment for feature-request markdown-check (round 1)

The feature request now states the repository need, current gap, mandatory
heading outline, policy constraints, acceptance cases, and scope boundaries.

Questions missing: none identified for this initial request. The seven placed
questions cover rule support, checked-file population, failure severity,
historical findings, structured-document applicability, heading equality, and
deeper heading levels.

Existing options and answers: each question has three distinct choices, stated
trade-offs, one recommended option, and a reasoned proposed answer. The
independent reviewer should challenge any option set or recommendation that
does not fully express the feature boundary.

Reviewer wording suggestions applied: none yet because this is round 1.

### Change summary for feature-request markdown-check (round 1)

Created the v0.11.0 markdown-check feature request from the approved focused
child draft. Added confirmed behavior for the Python checker, repository-root
launcher, shared gate, per-finding diagnostics, mandatory MD024 and MD025
handling, one-title and unique-title rules, nested heading structure, acceptance
cases, code references, and exclusions.

Added seven open questions to settle the remaining feature-level policy choices
before design work.

### Writer response for feature-request markdown-check (round 1)

Writer response: This is the initial specification-review request. No earlier reviewer feedback
exists. The writer asks the reviewer to assess the complete feature request and
all seven recommended answers, identify missing requirement questions, and
request precise changes when the specification is not ready for consolidation.

### Reviewer focus for feature-request markdown-check (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-23T21:06:53+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for feature-request markdown-check round 1

The specification is well organised and its confirmed sections are largely
sound. The need, the current-state summary, the runtime-independence
constraint, the finding format, the scope boundary, and the reference list all
read as implementable. Question Q07 is settled and needs no further work.

The specification is not ready for consolidation. Three defects block it, and
they are not wording problems: each one changes what the implementation must
do, and two of them make the currently recommended answers unbuildable or
self-contradicting against the repository as it exists today.

### Evidence measured independently for markdown-check (round 1)

The reviewer measured the repository rather than relying on the survey figure
carried in the source draft. Method: a fence-aware ATX and setext heading scan
over the 371 tracked Markdown files, with YAML frontmatter stripped and inline
code spans removed before raw-HTML detection. This approximates the declared
rules in Python; it is not markdownlint itself, because the environment has no
Node runtime, so the figures below establish order of magnitude and
distribution rather than an exact markdownlint result.

| Rule as declared by the specification | Findings | Files |
| --- | --- | --- |
| Multiple `##` sections required | 168 | 168 |
| Exactly one `#` title (missing) | 156 | 156 |
| MD033 raw HTML outside code spans | 61 | 11 |
| MD024 duplicate heading text | 0 | 0 |
| MD001 skipped heading level | 0 | 0 |

Two conclusions follow directly, and both bear on the recommended answers.

First, the two rules the umbrella calls non-negotiable are already clean.
MD024 reports zero findings and no tracked file skips a heading level. Enabling
those as hard failures costs nothing today and requires no baseline entry at
all.

Second, the adoption problem is concentrated entirely in the one-title rule and
the invented multiple-section rule. The 156 title-less files are not scattered
debt. They are the machine-consumed adapter files the umbrella itself mandates:
31 in `.agents/llm-shared/instructions`, 29 in `.agent/workflows`, 16 in
`.github/prompts`, 4 in `templates`, and one `SKILL.md` per skill directory.
Each carries its identity in a YAML frontmatter `description` and opens
directly with a numbered instruction body. `.agent/workflows/spec-reviewer.md`
is representative and correct as written.

The source draft's estimate of roughly one hundred findings across about forty
files understates both the count and, more importantly, the file distribution
by a factor of several. The recommended answers were chosen against that
smaller estimate, which is why two of them do not survive contact with the
measured repository.

### Existing code the markdown-check specification does not cite (round 1)

`tools/review_markdown_headings.py` already contains a fence-aware ATX heading
parser used by the review renderers. The checker should reuse that parser
rather than introduce a third independent heading scanner into the repository.
This is a constructive note for the design phase, not a blocking defect.

The shared gate is the repository-root `check.bat`, which accumulates step
results through its `record_failure <name> <status>` helper. That is the exact
integration point the confirmed "Shared-gate place" section refers to.

### Question verdicts for feature-request markdown-check round 1

### Q01 verdict for markdown-check: keep A2 and define "enabled" (round 1)

The question is well placed and its option set is materially distinct. The
recommendation is right in principle: a declared catalog is the correct
contract for a Python reimplementation, and rejecting an unknown enabled rule
is the correct way to prevent a false green result.

The recommendation cannot be implemented as written. `.markdownlint.json`
contains exactly two keys, `"MD013": false` and
`"MD033": {"allowed_elements": ["img"]}`. Under markdownlint semantics every
rule not named in the configuration is enabled by default. So "an enabled rule"
has two readings that produce opposite behaviour, and the specification chooses
neither:

- Read as default-on, every rule from MD001 to MD059 is enabled, almost none of
  them are in any bounded Python catalog, and A2's unknown-rule stop fires
  immediately against the repository's own current configuration.
- Read as explicit-only, the configuration enables nothing except MD033 and
  disables MD013, so neither MD024 nor MD025 is enabled by configuration at
  all, and both run only because they are separately hardcoded as mandatory.

Reviewer answer: keep A2 and add the missing interpretation. State that the
declared catalog is the enabled set; that keys in `.markdownlint.json` may only
disable or configure a rule already in the catalog; and that a key naming a
rule outside the catalog is a configuration error. Under that reading the
current `.markdownlint.json` needs no change, which is worth saying explicitly
because it is the first question a reader will ask.

### Q02 verdict for markdown-check: agree with B1 (round 1)

The full tracked population gives the gate one stable meaning, and the reviewer
reaches the same conclusion for the same reason. The objection that existing
defects can block unrelated work is real, but it is Q04's problem to solve and
Q04 does solve it. The option set and consequences are accurate. No change
required.

### Q03 verdict for markdown-check: agree with C1, evidence strengthens it (round 1)

Failing severity is correct: a configured rule that only warns is not a rule.
The measured evidence makes this easier than the question assumes. MD024 and
the level-skip check report zero findings across all 371 tracked files, so the
protocol-critical heading rules can fail hard from day one at no adoption cost
whatever. Only the one-title rule, the multiple-section rule, and MD033 carry
existing findings. Recommend recording that split in the question, because it
converts C1 from a costly choice into an almost free one.

### Q04 verdict for markdown-check: keep D2 and define the baseline (round 1)

A no-growth baseline is the right instrument and correctly respects the effort
boundary. Two properties that decide whether it works are missing.

Storage is unstated. The one baseline precedent in this repository,
`tools/groundhog/baseline.py`, writes `a.ghog.failures` at the project root as
an ignored scratch file refreshed on every run. That shape cannot enforce
no-growth: it is absent in a clean clone and it rewrites itself green. The
Markdown baseline must be a tracked file for the no-growth rule to mean
anything.

Entry identity is unstated. A baseline keyed on path and line number churns
whenever any unrelated edit shifts lines above a finding, which produces
constant false movement and destroys the shrink-or-unchanged signal. Keyed on
path, rule, and count it is stable under editing.

Reviewer answer: keep D2 and state both properties. Recommend a tracked
baseline file with entries keyed on path plus rule plus count, and recommend
scoping the baseline to the non-heading rules only, since the heading rules
already stand at zero.

### Q05 verdict for markdown-check: E2 is right but too narrow (round 1)

This is the most consequential defect in the specification. E2 exempts short
artifacts from the multiple-section rule only. It does not exempt them from the
one-title rule, and the confirmed section "One document title for checked
Markdown" states that a missing title is a finding and that configuration
cannot disable the rule.

Combine the recommended answers as they stand. Q02 checks every tracked file,
Q03 fails on every finding, and the one-title rule cannot be waived. The result
on day one is 156 failing files, every one of them an adapter that is correct
as written, on a rule that by construction admits no exception. The only relief
left is Q04's baseline, which would then carry roughly 156 permanent entries
that can never shrink, because the correct fix for those files is to change
nothing. A baseline whose entries are permanent by design is not a baseline.

Reviewer answer: extend E2 so the structured-document classification governs
the one-title requirement as well as the section-count requirement. A file
whose identity is carried by a YAML frontmatter `description` is not required
to carry an `#` title, while still being forbidden from carrying two. The
document-class boundary E2 already needs for section counting is the same
boundary, so this adds no new classification machinery.

### Q06 verdict for markdown-check: F3 cites a missing artifact (round 1)

The question itself is well formed and the three equality models are genuinely
distinct. F3's recommendation refers to "the repository's documented
anchor-style normalization". No such normalization is documented anywhere in
the tracked repository; the reviewer searched for it. F3 therefore recommends
conforming to a specification that this effort would itself have to write, and
that deliverable appears in neither the scope boundary nor the acceptance
criteria, both of which list only the checker, launcher, gate connection,
tests, and reference page.

There is a second consequence the question does not surface. Anchor-normalized
equality is strictly stronger than MD024, which compares heading content. A
checker that applies the stronger comparison and reports it under the `MD024`
identifier misattributes its own stricter rule to markdownlint. That interacts
directly with the missing question on rule-identifier namespacing.

Reviewer answer: keep F3, but only on two conditions. Name the exact
normalization inline rather than by reference, for which GitHub heading-anchor
rules are the natural choice: lowercase, drop inline formatting, remove
punctuation other than hyphens, and replace runs of whitespace with single
hyphens. Then add defining and documenting that normalization to the scope and
to the documentation acceptance case. If the writer prefers not to expand
scope, F2 is the honest fallback and should be selected instead. What the
specification cannot do is keep F3 while pointing at a document that is not
there.

### Q07 verdict for markdown-check: agree with G2 (round 1)

The full six-level hierarchy with strict parent ordering is the right contract,
the options are distinct, and the consequences are stated accurately. No
tracked file currently skips a level, so this rule also starts clean. Nothing
to change.

### Questions missing from the markdown-check feature request (round 1)

- Rule-identifier namespacing. The finding format requires a rule identifier on
  every output line, but "multiple `##` sections" is not a markdownlint rule
  and, if Q06 keeps F3, neither is the uniqueness comparison the checker
  actually applies. The specification needs a decision on a repository-local
  namespace, for which `LS001` and successors are a reasonable form, and a
  statement reserving `MD*` for markdownlint-defined semantics.
- Line number for whole-file findings. The one-title and section-count rules
  have no meaningful source line, yet the finding format requires one on every
  output line. Line 1 is the natural answer and simply needs to be written down.
- Launcher portability. The shared gate is `check.bat`, which is Windows-only.
  The specification should say whether the checker must also be runnable
  directly on a POSIX continuous-integration host, since that constrains
  whether the launcher may be the only supported entry point.

### Requested changes for feature-request markdown-check round 1

Requested changes:

- Blocking. Q01: define what an enabled rule is under markdownlint default-on
  semantics, and reconcile that definition with A2's unknown-rule stop so the
  repository's own two-key `.markdownlint.json` remains valid.
- Blocking. Q05: extend the structured-document classification to the one-title
  rule so the 156 frontmatter-identified adapter files are not failed on a rule
  that admits no exception and needs no fix.
- Blocking. Q04: state that the baseline is a tracked file keyed on path, rule,
  and count, and scope it to the non-heading rules.
- Q06: replace the reference to a non-existent documented anchor normalization
  with an inline definition plus a scope and acceptance addition, or select F2.
- New question: assign repository-local rules an identifier namespace distinct
  from `MD*`, covering the section-count rule and any uniqueness comparison
  stronger than MD024.
- New question or finding-format addition: state the line number reported for a
  whole-file finding.
- New question: state whether the checker must run on a POSIX continuous-
  integration host, given that the shared gate `check.bat` is Windows-only.
- Correct the existing-findings estimate carried from the draft, and re-argue
  Q03 and Q04 against the measured figures.
- Confirmed sections to update for consistency: "One document title for checked
  Markdown", its matching heading acceptance case, and the "Shared-gate place"
  wording once the severity and baseline answers are settled.

### Writer instructions for feature-request markdown-check round 1

Apply the changes below to the feature request, then publish the replacement
request. Do not treat any of these as optional wording polish. Items 1 to 3
block consolidation; items 4 to 7 close gaps that would otherwise surface as
rework during design.

1. Fix Q01's undefined "enabled rule". Add the interpretation to the question
   description and carry it into the answer: the declared catalog is the enabled
   set, `.markdownlint.json` keys may only disable or configure a catalog rule,
   and a key naming a rule outside the catalog is a configuration error. State
   explicitly that the current two-key configuration is already valid under this
   reading.

2. Widen Q05 so the structured-document classification governs the one-title
   rule as well as the section-count rule. Add to the answer that a file whose
   identity is carried by a YAML frontmatter `description` is not required to
   carry an `#` title and is still forbidden from carrying two. Update the
   confirmed section "One document title for checked Markdown" so its
   non-disableable claim is scoped to the duplicate-title case rather than the
   missing-title case, and correct the matching heading acceptance case.

3. Define Q04's baseline. State that it is a tracked file, not an ignored root
   scratch file, and give the reason: an ignored baseline is absent in a clean
   clone and cannot enforce no-growth. State that entries are keyed on path,
   rule, and count rather than on line number, and give the reason: line keys
   churn on unrelated edits. Add that the baseline covers only the non-heading
   rules, since MD024 and the level-skip check stand at zero findings.

4. Resolve Q06. Either name the anchor normalization inline, adopting GitHub
   heading-anchor rules, and add defining and documenting that normalization to
   both the scope boundary and the documentation acceptance case; or change the
   answer to F2. Remove the reference to a documented repository normalization
   that does not exist.

5. Add a question on rule-identifier namespacing, deciding on a repository-local
   namespace such as `LS001` and successors, and stating that `MD*` identifiers
   are reserved for markdownlint-defined semantics.

6. Add a question, or extend the finding-format section, stating which line
   number a whole-file finding reports.

7. Correct the existing-findings figure wherever the specification or its
   answers rely on it. The draft's estimate of roughly one hundred findings
   across about forty files is materially low. The reviewer's measurement over
   371 tracked files gives 156 missing-title files, 168 files below the section
   count, and 61 raw-HTML findings across 11 files, against zero MD024 and zero
   level-skip findings. Q03 and Q04 in particular were reasoned against the low
   estimate and should be re-argued against these figures.

Two further notes for the design phase, which need no feature-request change.
Reuse the fence-aware ATX heading parser already in
`tools/review_markdown_headings.py` instead of writing a third heading scanner.
The shared gate is `check.bat`, whose steps report through its
`record_failure <name> <status>` helper.

### Final reviewer decision for feature-request markdown-check round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-23T21:15:01+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for feature-request markdown-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
Review round: 2

### Requestor assessment for feature-request markdown-check (round 2)

The round 1 answer identified seven required changes. All seven are now applied
to the current feature request without disagreement.

Questions missing: none identified after adding Q08 for local rule identifiers,
Q09 for whole-file line numbers, and Q10 for POSIX portability.

Existing options and answers: Q01 now defines the catalog as the enabled set;
Q03 and Q04 use the measured repository population; Q04 defines a tracked
non-heading baseline keyed on path, rule, and count; Q05 covers title presence
and section count for structured documents while exempting frontmatter adapter
identity; and Q06 defines GitHub-style normalization inline and assigns its
documentation to this effort.

Reviewer wording suggestions applied: all blocking and non-blocking round 1
instructions were incorporated. The reviewer should verify the resulting
cross-section consistency and either identify exact remaining gaps or recommend
consolidation readiness.

### Change summary for feature-request markdown-check (round 2)

Revised the confirmed title and hierarchy rules so structured documents require
one title and multiple sections, YAML-frontmatter adapters may omit the title,
and no checked file may contain two level-one titles.

Added the measured 371-file adoption context, clarified markdownlint default-on
semantics, named `check.bat` as the shared gate, and tied local normalization,
rule identifiers, and file-level diagnostic lines to their questions.

Reworked Q01, Q03, Q04, Q05, and Q06 from reviewer evidence. Added Q08, Q09,
and Q10 for local rule names, whole-file line values, and a platform-neutral
Python entry point. Updated scope, acceptance, and documentation commitments for
the inline normalization.

### Writer response for feature-request markdown-check (round 2)

Writer response: The writer accepts every round 1 recommendation and reports no disagreement.
The implementation-facing parser-reuse and `record_failure` notes are retained
as design context rather than turned into new feature constraints. Please assess
the complete revised requirement and ten questions for consolidation readiness.

### Reviewer focus for feature-request markdown-check (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-23T21:19:33+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for feature-request markdown-check round 2

All seven round 1 instructions were applied, accurately and without
disagreement. Q01 now defines the catalog as the enabled set and confirms the
current two-key configuration stays valid. Q04 names a tracked baseline keyed
on path, rule, and count. Q06 defines the normalization inline and refuses to
mislabel it as MD024. Q08, Q09, and Q10 are well-formed additions whose
recommended answers H2, I1, and J2 the reviewer accepts without change, as it
accepts B1, C1, and G2. The measured figures were carried into the document
faithfully.

One round 1 instruction was applied in a way that does not achieve what it was
for, and verifying it surfaced a second gap that was latent before. Both are
substantive rather than wording, so this round cannot recommend consolidation.

### Verification of the round 2 exemption for markdown-check (round 2)

Round 1 asked that the structured-document classification cover the one-title
rule so correct adapter files would not fail a rule with no exception and no
fix. Q05 now does that, keyed on a YAML frontmatter `description`. The reviewer
re-measured the repository against that exact criterion to confirm it closes
the population it was written for. It does not.

| Population | Files |
| --- | --- |
| Tracked Markdown files | 371 |
| Files carrying a frontmatter `description` | 118 |
| Missing-title files exempted by that criterion | 117 |
| Missing-title files still failing | 39 |
| Files below the section count still failing | 51 |

The 39 files that still fail the title rule are 31 in
`.agents/llm-shared/instructions`, 4 in `templates`, and one each in
`.agents/llm-shared/rules`, `.claude`, `.github`, and the repository root. The
51 files that still fail the section count are those same 31 plus 6 in `rules`,
6 in `templates`, 3 in `instructions`, and 2 at the root.

The 31 are the decisive group, and they are the same class of artifact Q05
intended to exempt. Their median body is one non-blank line. The complete
content of `.agents/llm-shared/instructions/spec-reviewer.md` is a single
sentence pointing at the canonical instruction. These are the wrapper adapters
the umbrella explicitly mandates under "Complete existing skills by referencing
and creating new ones for review requestor". They simply carry no frontmatter,
so a `description`-keyed exemption cannot see them, even though they are the
files least able to hold a title and two sections.

### Interaction between the exemption gap and the baseline for markdown-check (round 2)

The gap would be a bounded problem if the baseline could absorb it. It cannot,
because Q04 deliberately scopes the tracked baseline to non-heading rules and
justifies that by "keeping the already-clean MD024 and hierarchy checks at
zero". The title rule and the section-count rule are heading rules, and unlike
MD024 and the hierarchy check they are not clean: 39 and 51 findings remain.

So the three settled answers now combine to a result none of them intends. Q02
checks every tracked file, Q03 fails on every enforced finding, Q05 exempts
only 117 of the affected files, and Q04's baseline is closed to the rules that
carry the remainder. The gate is red on its first run with no defined remedy,
which is the same outcome round 1 identified, at reduced scale.

Either the exemption must describe the adapter class correctly, or the baseline
must open to these two rules. The reviewer recommends both, because even a
correct classification leaves legitimate residue in `templates`, `rules`, and
`instructions` that a no-growth baseline is exactly the right instrument for.

### Question verdicts for feature-request markdown-check round 2

### Q05 verdict for markdown-check: the exemption criterion is wrong (round 2)

E2 remains the right shape and the reviewer still endorses it. The criterion it
now uses does not match the population it was written to protect.

Keying the exemption on a YAML frontmatter `description` exempts 117 of the 156
title-less files and leaves 39. Those 39 are adapters too, with a median body
of one non-blank line, and 31 of them sit in `.agents/llm-shared/instructions`
where the umbrella requires them to exist. A one-line pointer file is the
clearest possible case for exemption, and the current criterion is the only
reason it is not exempt.

The deeper problem is that the specification uses "structured document" as the
operative term in two confirmed rules and in Q05's answer, but never defines
it. Q05 lists "The checker needs a clear, documented classification rule" as
E2's own con, and nothing in the document then supplies that rule. The
`description` key is the closest thing to a definition and it is stated only
inside an option, not as the contract.

Reviewer answer: keep E2 and replace the criterion with a stated classification
that names both adapter shapes. A file is an adapter, and therefore exempt from
the title and section-count rules, when its identity is carried by YAML
frontmatter, or when it is a short pointer or template artifact below a stated
size that the specification fixes. Every other tracked file is a structured
document. State that rule as a confirmed subsection rather than leaving it
inside an option, because the checker cannot be built from an option's prose.

### Q04 verdict for markdown-check: reopen the baseline scope (round 2)

The tracked, path-rule-count baseline is exactly right and the reviewer
reaffirms it. Its scope is now the problem.

Round 1 recommended limiting the baseline to non-heading rules on the evidence
that MD024 and the hierarchy check were both at zero. That evidence was correct
and remains correct. It did not extend to the title and section-count rules,
which are also heading rules and which carry 39 and 51 residual findings after
the Q05 exemption. Scoping by the phrase "non-heading" therefore excludes two
rules that need the baseline and includes nothing that does.

Reviewer answer: keep D2 and re-scope by evidence rather than by category. The
baseline covers every rule that has residual findings after classification, and
excludes only the rules measured at zero, namely MD024 duplicate headings and
the heading-hierarchy check. State the exclusion as a list of rules at zero,
not as the category "non-heading", so the boundary stays true if a later
measurement changes.

### Q05 and Q04 combined effect on the markdown-check gate (round 2)

Neither change alone makes the first gate run green. Taken together with Q02's
full population and Q03's failing severity they do. The reviewer asks for both
and considers either one alone insufficient.

### Missing rule identity for the title check in markdown-check (round 2)

The specification never assigns a rule identifier to the missing-title check,
and the word MD041 appears nowhere in it or anywhere in the repository. That
matters now that Q01 makes the catalog the enabled set and Q08 requires every
finding to carry an honest identifier: a check with no identifier can be
neither configured, baselined, nor reported under the contract the document has
just adopted.

Two attributions are being conflated. MD025 is the single-title rule and
governs a second level-one heading, which is what the revised confirmed text
correctly calls non-disableable. The missing-title case is markdownlint's
MD041, the first-line-heading rule, which the specification never names.

MD041 also carries a `front_matter_title` option whose whole purpose is to let
frontmatter supply the title. That is the exemption Q05 is trying to express by
hand. Adopting MD041 with a configured `front_matter_title` would express the
frontmatter half of Q05 natively and reduce the bespoke classification to the
pointer-and-template case alone.

Reviewer answer: name the missing-title check. Adopt MD041 with a stated
`front_matter_title` setting if the semantics match, or assign an `LS*`
identifier under Q08 if they diverge, and say which. Also assign the
section-count rule its `LS*` identifier in the same place, because Q04's
baseline is keyed on rule identifier and cannot be specified while two of the
rules it must record are unnamed.

### Accepted without change in markdown-check round 2

Q01, Q02, Q03, Q06, Q07, Q08, Q09, and Q10 are all accepted as written. The
reviewer would choose A2, B1, C1, F3, G2, H2, I1, and J2, which are the
recommended and stated answers in every case. Q01's catalog-as-enabled-set
contract and Q06's inline normalization both resolve their round 1 defects
completely.

One optional wording note on Q06, which does not block: the inline
normalization does not say how non-ASCII characters are treated, and GitHub's
own anchor rules keep them after lowercasing. Adding a clause for that would
make the definition complete, and it is a wording addition rather than a
decision.

### Requested changes for feature-request markdown-check round 2

Requested changes:

- Blocking. Q05: the frontmatter-`description` criterion exempts 117 of 156
  title-less files and leaves 39 failing, 31 of them one-line pointer adapters
  in `.agents/llm-shared/instructions` that the umbrella mandates. Replace the
  criterion with a stated classification covering frontmatter-identified files
  and short pointer or template artifacts, and promote that classification from
  an option into a confirmed subsection, since "structured document" is used as
  an operative term throughout and never defined.
- Blocking. Q04: re-scope the baseline from the category "non-heading" to an
  explicit exclusion list naming only the rules measured at zero, MD024 and the
  heading-hierarchy check. The title and section-count rules retain 39 and 51
  residual findings and currently have no baseline home, so with Q02 and Q03 the
  first gate run fails with no defined remedy.
- Blocking. Rule identity: the missing-title check has no identifier and MD041
  is never mentioned in the specification or the repository. Distinguish MD025,
  which governs a second level-one title, from the missing-title case, and adopt
  either MD041 with a stated `front_matter_title` setting or an `LS*` identifier
  under Q08. Assign the section-count rule its `LS*` identifier at the same
  time, because Q04's baseline is keyed on rule identifier.
- Optional wording. Q06: state how the inline normalization treats non-ASCII
  characters.
- Accepted without change: Q01, Q02, Q03, Q06, Q07, Q08, Q09, and Q10, with
  answers A2, B1, C1, F3, G2, H2, I1, and J2.

### Writer instructions for feature-request markdown-check round 2

Three changes are required. Items 1 and 2 must both land, because either alone
still leaves the first shared-gate run failing. Item 3 closes the rule-identity
gap the round 2 answers created by adopting a catalog and an identifier policy.

1. Replace Q05's exemption criterion and define its operative term. Add a
   confirmed subsection under "Required heading outline for checked Markdown"
   that states the classification directly rather than leaving it inside an
   option: a file is an adapter when its identity is carried by YAML
   frontmatter, or when it is a short pointer or template artifact below a size
   the specification fixes; every other tracked file is a structured document.
   Adapters are exempt from the title and section-count rules and remain subject
   to duplicate-title, uniqueness, and hierarchy checks. Update Q05's option E2,
   its recommendation, and its answer to match, and cite the residual counts of
   39 and 51 so the reason for the change is on the record.

2. Re-scope Q04's baseline by measurement instead of category. Replace
   "non-heading" with an explicit exclusion list naming the rules measured at
   zero, MD024 duplicate headings and the heading-hierarchy check, and state
   that every other enforced rule with residual findings is baselined,
   including the title and section-count rules. Update the option text, the
   recommendation, and the answer together, and say why the round 1
   "non-heading" wording no longer holds.

3. Name the missing-title check and the section-count check. State that MD025
   governs a second level-one title and that the missing-title case is
   markdownlint's MD041, which the document currently never mentions. Decide
   whether to adopt MD041 with a stated `front_matter_title` setting, which
   expresses the frontmatter half of item 1 natively, or to assign an `LS*`
   identifier under Q08 because the semantics diverge, and record the choice.
   Assign the section-count rule its `LS*` identifier at the same time, since
   Q04's baseline is keyed on rule identifier and cannot be written while these
   rules are unnamed.

Optional, non-blocking. Q06's inline normalization does not state how non-ASCII
characters are handled; GitHub's rules keep them after lowercasing. Adding that
clause completes the definition without changing any decision.

No other change is requested. Q01, Q02, Q03, Q06, Q07, Q08, Q09, and Q10 are
accepted as written, and the reviewer endorses A2, B1, C1, F3, G2, H2, I1, and
J2. The parser-reuse and `record_failure` notes remain design context, correctly
kept out of the feature constraints.

### Final reviewer decision for feature-request markdown-check round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-08-23T21:28:57+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for feature-request markdown-check (round 3)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
Review round: 3

### Requestor assessment for feature-request markdown-check (round 3)

All round 2 blocking changes are applied without disagreement. The confirmed
heading contract now defines adapter and structured-document classes, bounds the
short-pointer exemption to named roots and five non-blank body lines, assigns
`LS001` and `LS002`, and retains MD025 for duplicate level-one titles.

Q04 now baselines every enforced rule with residual findings and excludes only
the measured-zero MD024 and hierarchy checks. Q05 records the earlier residual
39 title and 51 section-count findings and covers the pointer population that
the first frontmatter-only criterion missed. Q06 now states that non-ASCII
characters survive lowercasing.

Questions missing: none identified. Existing options and answers remain
complete after the revisions. The reviewer should verify that the classification,
baseline, identifiers, acceptance cases, and recommendations now form one
buildable contract.

### Change summary for feature-request markdown-check (round 3)

Added a confirmed document-classification subsection covering frontmatter
adapters and bounded short pointer or template artifacts. Updated title,
section, uniqueness, and acceptance text to use that classification.

Selected local rule `LS001` for missing structured-document titles because the
semantics diverge from MD041, selected `LS002` for insufficient structured
sections, and retained MD025 for a second level-one title.

Reworked Q04 and Q05 around the round 2 measured residuals, and completed Q06's
normalization definition for non-ASCII characters.

### Writer response for feature-request markdown-check (round 3)

Writer response: The writer accepts all round 2 instructions and reports no disagreement. Both
changes needed for a viable first gate run landed together, and the previously
unnamed title and section checks now have stable repository-local identifiers.
Please assess the complete current feature request for consolidation readiness.

### Reviewer focus for feature-request markdown-check (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-08-23T21:33:23+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for feature-request markdown-check round 3

All three round 2 blocking changes landed, and the two that had to arrive
together did. The classification is now a confirmed subsection rather than
prose inside an option, Q04 scopes the baseline by measured residual instead of
by category, and the previously unnamed title and section checks carry `LS001`
and `LS002`. Q06's non-ASCII clause is added. The document is close to
buildable.

The reviewer re-measured the repository against the classification exactly as
it is now written, to confirm it does what round 2 asked. It largely does.

### Post-classification measurement for markdown-check (round 3)

Applying the stated criterion — frontmatter `description`, or one of the five
named roots with at most five non-blank body lines — classifies 153 of the 371
tracked files as adapters and reduces both residual populations sharply.

| Rule | Round 2 residual | Round 3 residual |
| --- | --- | --- |
| `LS001` missing structured title | 39 | 4 |
| `LS002` insufficient sections | 51 | 17 |
| MD033 raw HTML | 61 | 61 |
| MD024 duplicate headings | 0 | 0 |
| Anchor-normalized duplicate headings | 0 | 0 |
| Heading hierarchy | 0 | 0 |

The remaining `LS002` population is 6 files in `rules`, 6 in `templates`, 3 in
`instructions`, and 2 at the repository root. Because Q04 now admits every rule
with residual findings, all of these have a baseline home and the first shared
gate run is viable. That was the round 2 blocker and it is resolved.

The reviewer also confirms the anchor-normalized uniqueness rule measures zero
across all 371 files, so adopting F3 introduces no baseline debt of its own.

### Remaining mismatch in the adapter bound for markdown-check (round 3)

The classification names two adapter shapes in one clause: a pointer to
canonical instructions, and a short reusable Markdown fragment. The five-line
bound is calibrated for the first and excludes the second.

All four residual `LS001` files illustrate it. Three are the review templates
`templates/spec-review-answer.template.md`,
`templates/spec-review-request.template.md`, and
`templates/code-review-request.template.md`, at 11, 28, and 29 non-blank lines.
Each begins at `##` because it is substituted into a parent document, so none
can ever carry a level-one title. They are precisely the reusable fragments the
clause names, and the line bound is the only reason they are not adapters. The
fourth is `LICENSE.md`, which is outside the five named roots.

The consequence is small in size and identical in kind to the round 1 finding:
these files receive permanent baseline entries that can never shrink, because
the correct content for them is what they already contain. A no-growth baseline
should hold debt that someone could eventually pay down, not artifacts that are
already right.

A size bound is the wrong test for a fragment. A structural one works: a file
whose first heading is level two or deeper is designed for inclusion and cannot
hold a title. That test costs nothing extra, since the checker already parses
every heading to evaluate the other rules.

### Question verdicts for feature-request markdown-check round 3

### Q05 verdict for markdown-check: classification works, bound needs one fix (round 3)

The change from a frontmatter-only criterion to a named confirmed subsection is
the right one, and the measured effect proves it: `LS001` residuals fall from 39
to 4 and `LS002` from 51 to 17. The reviewer endorses E2 as revised and asks for
one correction inside it.

The clause covers "a pointer to canonical instructions or a short reusable
Markdown fragment" but gates both on five non-blank body lines. Pointer files
have a median body of one line and pass easily. The repository's actual reusable
fragments are the three review templates at 11, 28, and 29 non-blank lines, and
all three fail the bound while matching the description exactly. Each starts at
`##` because it is substituted into a parent document.

Reviewer answer: keep E2 and split the test by shape rather than by size. A
pointer adapter keeps the five-non-blank-line bound. A fragment adapter is any
checked file whose first heading is level two or deeper, with no line bound,
because such a file is structurally incapable of holding a level-one title. This
removes three of the four permanent `LS001` baseline entries and needs no new
parsing.

### Q04 verdict for markdown-check: accepted as revised (round 3)

Scoping by measured residual rather than by the category "non-heading" is
exactly the requested change, and admitting `LS001`, `LS002`, MD033, and any
other rule that starts with findings makes the first full gate run viable. The
exclusion of MD024 and the hierarchy check remains correct against measurement:
both are still at zero, as is the anchor-normalized uniqueness comparison. No
change requested beyond the identifier point below.

### Unassigned rule identifiers in markdown-check (round 3)

The document now requires every finding to carry a rule identifier, keys the
baseline on that identifier, and assigns `LS001` and `LS002` explicitly. Two
enforced rules are still unnamed, which leaves the contract incomplete in the
one place round 2 established it must be complete.

The anchor-normalized uniqueness rule is described as implemented "under a
repository-local rule identifier" without that identifier ever being chosen,
and the documentation acceptance case requires the reference page to
distinguish "its repository-local identifier from MD024". A page cannot
distinguish an identifier that does not exist. Under Q08's namespace this is
`LS003`.

The heading-hierarchy rule is named only descriptively, including inside Q04's
exclusion list. A baseline keyed on rule identifier cannot express an exclusion
for a rule that has no identifier. This one appears to be markdownlint's MD001
heading-increment rule; if the semantics match it should be named MD001, and if
they diverge it needs an `LS*` identifier like the others.

Reviewer answer: assign both. State `LS003` for anchor-normalized duplicate
headings and name the hierarchy rule, then use those identifiers in Q04's
exclusion list and in the documentation acceptance case instead of prose
descriptions.

### Accepted without change in markdown-check round 3

Q01, Q02, Q03, Q06, Q07, Q08, Q09, and Q10 remain accepted, with answers A2,
B1, C1, F3, G2, H2, I1, and J2. The Q06 non-ASCII clause completes that
definition. The revised acceptance criteria correctly express the adapter
exemption, the `LS001` and `LS002` reporting, and the MD025 duplicate-title
case, and they need no change beyond the two identifiers above.

One optional, non-blocking note. `LICENSE.md` is a conventional root file that
will hold a permanent `LS001` baseline entry, since it sits outside the five
named roots and carries no title by convention. The specification may either
accept that single entry or add conventional root files to the classification.
Either is defensible at a population of one, so the reviewer does not request a
change.

### Requested changes for feature-request markdown-check round 3

Requested changes:

- Q05 classification: the single five-non-blank-line bound gates both adapter
  shapes, but the repository's reusable fragments are the three review templates
  at 11, 28, and 29 non-blank lines, each starting at `##` because it is
  substituted into a parent document. Keep the line bound for pointer adapters
  and add a fragment adapter defined structurally as any file whose first
  heading is level two or deeper, so those three stop taking permanent `LS001`
  baseline entries.
- Rule identifiers: assign `LS003` to the anchor-normalized duplicate-heading
  rule, replacing the phrase "a repository-local rule identifier", and name the
  heading-hierarchy rule as MD001 or an `LS*` identifier. Use both in Q04's
  exclusion list and the documentation acceptance case, which currently
  reference them only in prose while the baseline is keyed on identifier.
- Accepted as revised: Q04's residual-scoped baseline, the confirmed
  classification subsection, the `LS001` and `LS002` assignments, the MD025
  duplicate-title retention, and the Q06 non-ASCII clause.
- Accepted without change: Q01, Q02, Q03, Q06, Q07, Q08, Q09, and Q10, with
  answers A2, B1, C1, F3, G2, H2, I1, and J2.
- Evidence, not a required change: measured post-classification residuals are 4
  `LS001`, 17 `LS002`, and 61 MD033, with MD024, anchor-normalized uniqueness,
  and the hierarchy check all at zero across 371 tracked files.

### Writer instructions for feature-request markdown-check round 3

Two changes remain. Both are narrow, and the reviewer expects the next round to
reach consolidation readiness if they land as described.

1. Split the adapter test by shape instead of gating both shapes on one line
   count. In the "Document classification for checked Markdown" subsection, keep
   the five-non-blank-line bound for pointer adapters, and add a fragment
   adapter: any checked file whose first heading is level two or deeper, with no
   line bound, because such a file is substituted into a parent document and
   cannot hold a level-one title. Update Q05's option E2, its recommendation,
   and its answer to match. Record the reason: the three review templates at 11,
   28, and 29 non-blank lines match the fragment description the clause already
   names, yet fail its bound and would otherwise take permanent `LS001` baseline
   entries.

2. Assign the two remaining rule identifiers and use them consistently. State
   `LS003` for the anchor-normalized duplicate-heading rule in the "Unique
   titles for checked Markdown" subsection, and replace the phrase "a
   repository-local rule identifier" with it. Name the heading-hierarchy rule,
   adopting MD001 if its semantics match markdownlint's heading-increment rule
   or an `LS*` identifier if they diverge, and say which. Then replace the prose
   descriptions in Q04's exclusion list and in the documentation acceptance case
   with those identifiers, so every enforced rule the baseline references has a
   stable name.

Optional and not requested: `LICENSE.md` will carry one permanent `LS001`
baseline entry because it sits outside the five named roots. Accepting a single
entry or adding conventional root files to the classification are both
reasonable; the reviewer takes no position.

Nothing else is requested. Q01, Q02, Q03, Q06, Q07, Q08, Q09, and Q10 are
accepted with answers A2, B1, C1, F3, G2, H2, I1, and J2. Q04 is accepted as
revised. The measured post-classification residuals are 4 `LS001`, 17 `LS002`,
and 61 MD033, against zero for MD024, anchor-normalized uniqueness, and the
hierarchy check; the writer may record those figures as the expected initial
baseline size, but that is evidence rather than a required change.

### Final reviewer decision for feature-request markdown-check round 3

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor

- Recorded: 2026-08-23T21:40:09+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for feature-request markdown-check (round 4)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
Review round: 4

### Requestor assessment for feature-request markdown-check (round 4)

All round 3 blocking changes are applied without disagreement. Adapter
classification now distinguishes frontmatter adapters, bounded canonical
pointers, and structurally identified reusable fragments whose first heading is
level two or deeper. The fragment shape has no line-count bound, so the three
review templates no longer require permanent missing-title baseline entries.

The anchor-normalized global uniqueness rule is now `LS003`. The complete
no-skipped-level hierarchy behavior matches markdownlint's heading-increment
semantics and is now `MD001`. Both identifiers appear in the rule contract,
acceptance cases, documentation requirement, baseline exclusions, and Q08.

Questions missing: none identified. Existing options and answers remain
complete after the revisions. The optional `LICENSE.md` baseline entry is
accepted as existing debt and does not require an additional exemption.

### Change summary for feature-request markdown-check (round 4)

Split adapter classification by shape: canonical pointers retain the named-root
and five-non-blank-line bound, while reusable fragments are identified by a
first heading at level two or deeper and have no line-count bound. Updated Q05
and the acceptance cases with the measured review-template rationale.

Assigned `LS003` to anchor-normalized duplicate headings and `MD001` to the
markdownlint-compatible heading-increment check. Replaced descriptive baseline
and documentation references with those stable identifiers and expanded Q08's
identifier registry.

### Writer response for feature-request markdown-check (round 4)

Writer response: The writer accepts both round 3 instructions and reports no disagreement. The
classification no longer treats fragment size as pointer size, and every
enforced local or markdownlint-compatible rule discussed by the baseline now
has a stable identifier. The optional conventional `LICENSE.md` entry remains
baseline debt rather than expanding the adapter contract. Please assess the
complete current feature request for consolidation readiness.

### Reviewer focus for feature-request markdown-check (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-08-23T21:43:50+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for feature-request markdown-check round 4

Both round 3 instructions were applied exactly as written. The identifier work
is complete and correct: `LS003` is assigned to anchor-normalized duplicate
headings, the hierarchy check is named `MD001` on matching markdownlint
semantics, Q08's registry now lists `LS001`, `LS002`, `LS003`, MD025, and
MD001, and Q04's exclusion list and the documentation acceptance case use those
identifiers instead of prose. That item is closed and needs no further work.

The fragment classification is also applied exactly as written, and that is the
problem. The instruction the reviewer gave in round 3 was underspecified, and
implementing it faithfully introduced a logical defect. The fault is the
reviewer's wording, not the writer's execution.

### Why the unbounded fragment clause disables LS001 (round 4)

Round 3 asked for "a fragment adapter: any checked file whose first heading is
level two or deeper, with no line bound". The document now states exactly that,
with no root restriction. Follow the consequence.

`LS001` fires when a file is not an adapter and has no level-one heading. Not
being an adapter means not being a fragment, so the file either has no headings
at all or its first heading is level one. A first heading at level one
contradicts having no level-one heading. Therefore `LS001` can fire only on a
structured file that contains no headings whatsoever.

That is the degenerate case. A structured document that is missing its title is
precisely a document whose first heading is level two, so the clause exempts
every file the rule exists to catch. An author who forgets the `#` title on a
new design document is not warned; the file is silently reclassified as a
reusable fragment.

The measurement matches the proof. Across all 371 tracked files, the single
surviving `LS001` finding is `LICENSE.md`, which is the one structured file with
no headings at all. Every other title-less file is exempted, and after the
frontmatter and pointer clauses already do their work, the fragment clause is
what exempts the rest.

The acceptance criteria contradict this. "A structured document with no `#`
title reports a finding" is currently unsatisfiable by any document that
contains headings, so that case cannot be tested as written.

### Bounding the clause costs nothing measurable (round 4)

The three genuine fragments are `templates/spec-review-answer.template.md`,
`templates/spec-review-request.template.md`, and
`templates/code-review-request.template.md`. All three sit under `templates/`,
which the classification already names as a root.

The reviewer compared the clause as written against the same clause scoped to
`templates/`, over the full tracked set:

| Fragment clause | `LS001` residual | Of which zero-heading |
| --- | --- | --- |
| Unbounded, as currently written | 1 (`LICENSE.md`) | 1 |
| Scoped to `templates/` | 1 (`LICENSE.md`) | 1 |

The outcome on the current repository is identical. Scoping the clause changes
no file's classification today and restores the rule's reachability for every
file added later, which is what a specification has to govern.

Nothing else is outstanding. Every other decision in the document is settled and
the reviewer expects the next round to reach consolidation readiness.

### Question verdicts for feature-request markdown-check round 4

### Q05 verdict for markdown-check: bound the fragment clause (round 4)

E2 is correct in shape and the reviewer continues to endorse it. The fragment
condition needs one bound, for the reason set out in the assessment: as written
it makes `LS001` unreachable for every file that has headings, because lacking a
level-one title is exactly what puts a file's first heading at level two.

The reviewer takes responsibility for this. The round 3 instruction said "with
no line bound" and did not say "within a declared root", and the writer
implemented that instruction correctly.

Reviewer answer: keep E2 and keep the structural test, which was the right
insight, but restrict it to files under `templates/`. A fragment adapter is a
file under `templates/` whose first heading is level two or deeper, with no
line-count bound. All three real fragments already live there, and `templates/`
is already a named root in the pointer clause, so this adds no new concept.

If the writer prefers a name-based test, `*.template.md` under any root is an
acceptable alternative that the reviewer would also approve; both bound the
clause so that a title-less structured document outside the fragment area still
reports `LS001`. What the specification cannot keep is an unbounded first-heading
test, because it silently exempts the defect the rule was created to detect.

### Q04 verdict for markdown-check: accepted, no change (round 4)

The baseline is settled. Scoping by measured residual, keying on path, rule, and
count, admitting `LS001`, `LS002`, MD033 and any rule that starts with findings,
and excluding only the zero-result MD024 and MD001 checks is exactly right, and
the exclusion list now names both by identifier. The reviewer confirms MD024,
MD001, and the `LS003` comparison all still measure zero across the 371 tracked
files, so the exclusions remain true against evidence.

Accepting `LICENSE.md` as a single baseline entry rather than widening the
adapter contract is a reasonable call and the reviewer agrees with it.

### Q08 verdict for markdown-check: registry complete (round 4)

The identifier registry is now complete and internally consistent: `LS001` for a
missing structured-document title, `LS002` for insufficient sections, `LS003`
for anchor-normalized duplicate headings, MD025 for a second level-one title,
and MD001 for heading increment. Reserving `MD*` for matching markdownlint
semantics while naming the divergent checks locally is the honest arrangement,
and the MD041 divergence is explained where `LS001` is defined. No change
requested.

### Accepted without change in markdown-check round 4

Q01, Q02, Q03, Q06, Q07, Q09, and Q10 remain accepted with answers A2, B1, C1,
F3, G2, I1, and J2, alongside Q04's D2, Q05's E2 as amended above, and Q08's H2.
The acceptance criteria, scope boundary, documentation requirement, and finding
format are all consistent with those answers, with the single exception of the
missing-title acceptance case, which becomes testable again once the fragment
clause is bounded.

### Requested changes for feature-request markdown-check round 4

Requested changes:

- Blocking, and caused by the reviewer's own round 3 wording rather than by the
  writer. Bound the fragment adapter clause: change "its first heading is level
  two or deeper" to "it is under `templates/` and its first heading is level two
  or deeper", keeping the absence of a line-count bound, in the classification
  subsection and in Q05's option E2, recommendation, and answer. An unbounded
  first-heading test exempts every structured document missing its title,
  because a missing title is what makes the first heading level two; `LS001` can
  then fire only on files with no headings at all, and the sole finding across
  371 tracked files is `LICENSE.md`, the one such file. Scoping to `templates/`
  changes no current classification, since all three fragments already live
  there. A `*.template.md` name bound is an equally acceptable alternative.

- Consequence of the same fix: the acceptance case "A structured document with
  no `#` title reports a finding" is currently unsatisfiable by any document
  containing headings, and becomes testable again once the clause is bounded.
- Accepted as revised and complete: the `LS003` and MD001 assignments, Q08's
  identifier registry, Q04's identifier-based exclusion list, and the
  documentation acceptance case.
- Accepted without change: Q01, Q02, Q03, Q04, Q06, Q07, Q08, Q09, and Q10,
  with answers A2, B1, C1, D2, F3, G2, H2, I1, and J2, and Q05's E2 once the
  bound above is added. Accepting `LICENSE.md` as a single baseline entry is
  endorsed.

### Writer instructions for feature-request markdown-check round 4

One change remains. It corrects an underspecified instruction the reviewer gave
in round 3, not an error in the writer's work.

1. Bound the fragment adapter clause to a declared area. In the "Document
   classification for checked Markdown" subsection, change the third condition
   from any file whose first heading is level two or deeper to a file under
   `templates/` whose first heading is level two or deeper, keeping the absence
   of a line-count bound. Mirror the same change in Q05's option E2, its
   recommendation, and its answer.

   State the reason on the record so the constraint is not dropped later: an
   unbounded first-heading test exempts every structured document that is
   missing its title, because a missing title is exactly what makes the first
   heading level two. Under the clause as currently written, `LS001` can fire
   only on a file containing no headings at all, and the sole surviving finding
   across 371 tracked files is `LICENSE.md`, the one such file. Scoping the
   clause to `templates/` leaves every current classification unchanged, since
   all three reusable fragments already live there.

   A name-based bound such as `*.template.md` is an equally acceptable
   alternative if the writer prefers it. Either bound restores the
   missing-title acceptance case, which is currently unsatisfiable by any
   document that contains headings.

Nothing else is requested. The identifier work from round 3 is complete and
correct, and Q08's registry, Q04's exclusion list, and the documentation
acceptance case are all consistent. Q01, Q02, Q03, Q04, Q06, Q07, Q08, Q09, and
Q10 are accepted with answers A2, B1, C1, D2, F3, G2, H2, I1, and J2, and Q05's
E2 is accepted once the bound above is added. Accepting `LICENSE.md` as one
baseline entry rather than widening the adapter contract is endorsed.

Current measured state for the record, unchanged from round 3 apart from the
classification: MD024, MD001, and the `LS003` comparison are all at zero across
371 tracked files; residual findings are `LS002` at 17 and MD033 at 61 across 11
files, plus the single `LS001` entry for `LICENSE.md`.

### Final reviewer decision for feature-request markdown-check round 4

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-4 -->

## Round 5 by requestor

- Recorded: 2026-08-23T21:49:52+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for feature-request markdown-check (round 5)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
Review round: 5

### Requestor assessment for feature-request markdown-check (round 5)

The sole round 4 blocking change is applied without disagreement. The reusable
fragment adapter is now restricted to files under `templates/` whose first
heading is level two or deeper, while retaining no line-count bound. This keeps
all three measured review templates classified as fragments without allowing a
title-less structured document elsewhere to evade `LS001`.

Q05's option, recommendation, and answer record the reachability reason for the
root bound. The heading acceptance case uses the same `templates/` restriction.
The completed `LS003` and MD001 identifier work remains unchanged.

Questions missing: none identified. All ten existing questions have confirmed
answers, and no new design decision is exposed by this correction.

### Change summary for feature-request markdown-check (round 5)

Restricted the structural reusable-fragment condition to `templates/`, keeping
the no-line-count behavior within that declared root. Updated the heading
acceptance case and every Q05 occurrence to match.

Recorded that an unbounded first-heading test would reclassify every structured
document missing its level-one title and make `LS001` reachable only for files
with no headings, while the root bound preserves all current fragment matches.

### Writer response for feature-request markdown-check (round 5)

Writer response: The writer accepts the round 4 correction and reports no disagreement. The
fragment exemption is now bounded to `templates/`, the missing-title acceptance
case is reachable again, and the current three reusable fragments remain
covered. Please assess the complete current feature request for consolidation
readiness.

### Reviewer focus for feature-request markdown-check (round 5)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-5 -->

## Round 5 by reviewer

- Recorded: 2026-08-23T21:52:59+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for feature-request markdown-check round 5

The sole round 4 blocking item is fixed correctly. The reusable-fragment
condition is now bounded to `templates/` while keeping the absence of a
line-count bound, which was the requested shape, and Q05 records the
reachability reason so the constraint survives later editing.

The reviewer re-ran the classification against the document as it now stands and
verified the fix does what it is supposed to do, in both directions.

### Verification of the bounded fragment clause (round 5)

Applying the three adapter conditions exactly as written classifies the 371
tracked files as 118 frontmatter adapters, 35 bounded pointers, 3 `templates/`
fragments, and 215 structured documents. The three fragments are the same three
review templates, so no current classification changed.

Reachability was the point of the fix, and it is restored. A title-less
structured document outside `templates/` whose first heading is level two — the
exact case the unbounded clause swallowed — now classifies as a structured
document and reports `LS001`. The three real templates remain exempt.

Residual findings are unchanged and all have a baseline home under Q04: one
`LS001` entry for `LICENSE.md`, 17 `LS002` entries, and 61 MD033 findings across
11 files. MD024, MD001, and the `LS003` comparison all remain at zero across the
full tracked set, so Q04's exclusion list is still true against measurement.

### Whole-document consistency at round 5

The reviewer checked the document as a whole rather than only the changed
sections. All ten questions carry exactly one recommendation and one answer.
The identifier registry in Q08, the exclusion list in Q04, the rule contract,
the acceptance criteria, and the documentation requirement all use the same five
identifiers consistently: `LS001`, `LS002`, `LS003`, MD025, and MD001, with
MD013 and MD033 governed by the declared configuration. The heading acceptance
case now carries the same `templates/` restriction as the classification.

As a final check, the feature request was judged against the rules it defines.
It passes all of them: one level-one title, nine level-two sections, no exact or
anchor-normalized duplicate headings across its 72 headings, and no skipped
levels.

### Reviewer position on consolidation for markdown-check (round 5)

Every in-scope decision is settled and supported by evidence, and no substantive
work remains. The reviewer recommends consolidation. This recommendation is
advisory and does not authorize it; the choice belongs to the human at the
convergence gate.

### Question verdicts for feature-request markdown-check round 5

### Q05 verdict for markdown-check: accepted as bounded (round 5)

E2 is now complete. The classification names three adapter shapes with a
distinct, testable condition for each: frontmatter identity, a bounded canonical
pointer under a named root, and a `templates/` fragment identified structurally
with no line bound. The reviewer verified that this keeps all three review
templates exempt while restoring `LS001` for a title-less structured document
elsewhere. Accepted with no further change.

### Q04 verdict for markdown-check: accepted, exclusions still true (round 5)

The tracked baseline keyed on path, rule, and count, scoped to every rule with
residual findings and excluding only MD024 and MD001, remains correct. The
reviewer re-measured both exclusions and the `LS003` comparison at zero across
371 files, so the exclusion list is still accurate against evidence rather than
against category. Accepting `LICENSE.md` as a single baseline entry rather than
widening the adapter contract remains the right call.

### Q08 verdict for markdown-check: registry consistent throughout (round 5)

`LS001`, `LS002`, `LS003`, MD025, and MD001 are used consistently in the rule
contract, the acceptance criteria, the baseline exclusion list, and the
documentation requirement. Reserving `MD*` for matching markdownlint semantics
while naming the divergent checks locally is honest and stable, and the MD041
divergence is explained where `LS001` is defined.

### Full question set accepted for markdown-check (round 5)

The reviewer would choose, and the document states, A2 for Q01, B1 for Q02, C1
for Q03, D2 for Q04, E2 for Q05, F3 for Q06, G2 for Q07, H2 for Q08, I1 for Q09,
and J2 for Q10. Every option set is materially distinct, every recommendation
follows from the confirmed requirements and the measured repository state, and
no question is missing, redundant, unclear, or outside scope.

### Wording that consolidation should resolve for markdown-check (round 5)

Two sentences remain conditional on a question that now has a settled answer,
and they should become unconditional when the questions are folded into the
confirmed text. The documentation acceptance case opens "If Q06 confirms
anchor-style equality, the page also defines the exact normalization", and the
scope boundary opens "If Q06 confirms anchor-style equality, it also owns the
definition, implementation, tests, and documentation of that normalization".
Since Q06's answer is F3, both clauses hold unconditionally and the leading
conditions can simply be dropped.

These are wording-only edits of exactly the kind consolidation performs, and
they are not a reason to run another review round.

### Convergence evidence for feature-request markdown-check round 5

Covered wording: Only wording-level edits remain, all of them the kind consolidation performs.

- Drop the leading condition from the documentation acceptance case. "If Q06
  confirms anchor-style equality, the page also defines the exact normalization
  and distinguishes its repository-local identifier from MD024" becomes an
  unconditional sentence, because F3 is the settled answer.
- Drop the same leading condition from the scope boundary, where "If Q06
  confirms anchor-style equality, it also owns the definition, implementation,
  tests, and documentation of that normalization" likewise holds
  unconditionally.
- Apply the same treatment to the conditional clause inside "Unique titles for
  checked Markdown", which opens "If Q06 confirms anchor-style equality, this
  effort defines the normalization inline, implements it as repository-local
  rule `LS003`". The `LS003` assignment is settled, so the clause can state it
  directly.
- Optionally record the measured initial baseline size where Q04 describes the
  baseline: one `LS001` entry, 17 `LS002` entries, and 61 MD033 findings across
  11 files, with MD024, MD001, and `LS003` at zero. This is evidence the design
  phase will want and it is already stated elsewhere in the document.

No substantive change is requested. Every option set, recommendation, answer,
acceptance case, identifier, and scope statement is settled and mutually
consistent.

Convergence rationale: The specification is ready for consolidation, and the reviewer reaches that
position on evidence rather than on round count.

Every decision the umbrella deferred to this requirement is now settled with a
stated answer: rule coverage, checked-file population, gate severity, treatment
of existing findings, document classification, heading-title equality, heading
depth, rule-identifier namespacing, whole-file line numbers, and portability.
All ten questions carry one recommendation and one answer, and the reviewer
independently agrees with each of A2, B1, C1, D2, E2, F3, G2, H2, I1, and J2.

The four defects raised across earlier rounds are closed and verified rather
than merely asserted. Q01's undefined "enabled rule" is resolved by the
catalog-as-enabled-set contract, under which the repository's current two-key
`.markdownlint.json` stays valid. The adoption problem that would have failed
156 correct adapter files is resolved by a classification the reviewer
re-measured at each revision, from 39 residual title findings, to 4, to the
single conventional `LICENSE.md` entry. The unnamed rules now carry `LS001`,
`LS002`, `LS003`, MD025, and MD001 consistently across the contract, acceptance
criteria, baseline exclusions, and documentation requirement. The unbounded
fragment clause that made `LS001` unreachable is bounded to `templates/`, and
the reviewer confirmed both that the fix restores the rule and that it changes
no current classification.

The document is also implementable as written. A reader can determine which
files are checked, which class each file belongs to, which rules apply to it,
what identifier each finding carries, what line a whole-file finding reports,
which findings enter the tracked baseline, which rules are excluded and why, and
how the checker is invoked from both the Windows shared gate and a POSIX host.
The measured residuals give the design phase a known starting baseline of one
`LS001`, 17 `LS002`, and 61 MD033 findings, with MD024, MD001, and `LS003` at
zero.

As a final consistency signal, the feature request satisfies the rules it
defines: one level-one title, nine level-two sections, no duplicate headings
under either exact or anchor-normalized comparison across 72 headings, and no
skipped levels.

Only the wording edits listed alongside this rationale remain, and each is a
conditional clause whose condition is now settled. The reviewer recommends
consolidation. That recommendation is advisory and does not authorize it; the
decision belongs to the human at the convergence gate, who may equally choose
another round.

### Writer instructions for feature-request markdown-check round 5

No substantive change is requested. The specification is complete, internally
consistent, and implementable as written.

At consolidation, fold the ten answered questions into the confirmed text and
drop the three leading conditions that depend on Q06, whose answer F3 is
settled. Those clauses appear in the documentation acceptance case, the scope
boundary, and the "Unique titles for checked Markdown" subsection, and each
holds unconditionally once the question is closed.

Optionally record the measured initial baseline size where Q04 describes the
baseline: one `LS001` entry, 17 `LS002` entries, and 61 MD033 findings across 11
files, with MD024, MD001, and `LS003` at zero across the 371 tracked files. The
design phase will want that figure, and it already appears elsewhere in the
document.

Two notes carried forward for the design phase, which remain design context
rather than feature constraints. Reuse the fence-aware ATX heading parser
already in `tools/review_markdown_headings.py` rather than adding a third
heading scanner. Integrate with the shared gate through `check.bat`'s existing
`record_failure <name> <status>` helper.

The reviewer recommends consolidation. The recommendation is advisory; the human
at the convergence gate may choose `Consolidate` or `Revise and review again`.

### Final reviewer decision for feature-request markdown-check round 5

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-5 -->

## Round 5 by human - human-confirmation

- Recorded: 2026-08-23T22:03:01+02:00
- Exchange: specification/feature-request/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.markdown-check.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-5 -->
