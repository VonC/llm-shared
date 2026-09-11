# Design v0.11.0: Repository Markdown checker

Reference feature request: [feature-request.v0.11.0.markdown-check.md](feature-request.v0.11.0.markdown-check.md)

---

## Context for the v0.11.0 repository Markdown checker

Review-mode transcripts and ordinary repository documentation already have
declared heading and Markdown rules, but those rules are not enforced by an
executable repository check. The v0.11.0 design introduces a bounded Python
checker that interprets the repository configuration, classifies tracked
Markdown files, evaluates the supported rule catalog, compares residual
findings with a no-growth baseline, and participates in the existing shared
gate.

The checker is deliberately independent of Node and package downloads. Its
output and exit status become the authoritative machine result for the policy;
the adoption measurements in the feature request remain planning evidence only.

## Scope for the v0.11.0 repository Markdown checker

The v0.11.0 outcomes are:

1. Every tracked Markdown file is evaluated under one deterministic policy.
2. Structured documents and adapter documents receive the correct heading
   obligations without path-specific exemption lists.
3. Every unbaselined enforced finding fails both the direct checker and the
   repository shared gate.
4. Maintainers receive stable, source-located diagnostics and focused reference
   documentation for the supported catalog.

Everything else is supporting design context for those outcomes or is
explicitly deferred.

### Capabilities included in the v0.11.0 checker

- A direct Python entry point that discovers the repository and reads tracked
  Markdown paths.
- A repository-root launcher that requires no prior environment activation.
- Fence-aware Markdown parsing shared with existing review heading behavior
  where the existing parser is suitable.
- Adapter classification, configured `MD*` rules, mandatory heading rules, and
  repository-local `LS*` rules.
- A tracked no-growth baseline and deterministic diagnostics.
- Shared-gate integration, unit and acceptance coverage, and one Diataxis
  reference page.

### Capabilities deferred beyond the v0.11.0 checker

- Repairing every historical Markdown violation as part of this effort.
- Reproducing the complete external markdownlint implementation or depending on
  its JavaScript runtime.
- Incremental changed-file checking, editor integration, or automatic fixes.
- Changes to review-exchange ownership, state transitions, or recovery policy.

---

## Confirmed technical facts for the v0.11.0 repository Markdown checker

**The repository policy is small but open-ended by default**:
`.markdownlint.json` currently disables `MD013` and configures `MD033` to allow
`img`. Omitted external markdownlint rules would normally be enabled, so the
bounded Python implementation needs an explicit supported catalog rather than
claiming full markdownlint compatibility.

**The shared gate already has a uniform failure contract**: the root
`check.bat` captures each tool status, calls `record_failure <name> <status>`,
and reports the collected failures at the end. The Markdown launcher can join
that flow as one additional named check without changing the gate's ownership
model.

**A fence-aware heading transformer already exists**:
`tools/review_markdown_headings.py` recognizes authored headings outside fenced
code while preserving literal examples. The checker can reuse or extract its
fence-aware scanning behavior instead of introducing a second incompatible
interpretation of headings.

**The initial adoption population contains accepted debt**: the feature
request records residual `LS001`, `LS002`, and `MD033` findings. Rules measured
at zero, including `MD001`, `MD024`, and `LS003`, must remain at zero and must
not receive baseline entries. Newly enforced `MD038` also starts without a
baseline entry after its genuine-code-space exceptions are applied; any
remaining finding is repaired. A fence-aware review measured two `MD032`
findings across the 375 tracked and pending Markdown files that this effort will
commit: `.claude/skills/humanizer/SKILL.md` line 260 and
`docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md` line 264.
This documentation update repairs the transcript boundary, and implementation
repairs the skill file. Together they make `MD032` start at zero in the committed
state with no baseline entry; no separate human checkpoint remains.

---

## Current validation flow before the v0.11.0 checker

Markdown policy is distributed across `.markdownlint.json`, writing rules,
review instructions, and human review. The shared gate invokes Python and shell
checks, but it never inventories Markdown files or interprets their structure.
Consequently, a malformed document can be committed even when the relevant
instruction calls its heading defect non-negotiable.

```txt
author edits Markdown
  -> optional visual review
  -> check.bat runs unrelated checks
  -> Markdown policy has no machine result
```

## Target validation flow for the v0.11.0 checker

The direct launcher and the shared gate use the same checker entry point and
therefore cannot disagree about policy. One run builds an immutable inventory,
parses each file once, evaluates enabled rules, compares findings with the
baseline, emits every actionable result in stable order, and returns one final
process status.

```txt
direct launcher or check.bat
  -> resolve repository and load policy
  -> obtain tracked Markdown inventory
  -> classify and parse each document
  -> evaluate the supported rule catalog
  -> compare residual findings with the baseline
  -> emit ordered findings and configuration errors
  -> return success or failure
```

Configuration, inventory, decoding, and baseline integrity errors are checker
failures. They are not converted into Markdown findings because no trustworthy
per-document policy result exists in those cases.

---

## Policy model for the v0.11.0 repository Markdown checker

### Supported rule catalog for repository policy

The checker owns a published catalog rather than dynamically accepting every
markdownlint key. The first catalog contains the rules required by the feature:
`MD001`, `MD013`, `MD024`, `MD025`, `MD032`, `MD033`, `MD038`, `MD050`, `LS001`,
`LS002`, and `LS003`.
`MD013` is present so the current explicit disable is valid configuration even
though it does not run. Each catalog entry declares its namespace, accepted
configuration shape, default enabled state, and whether it is mandatory.

`MD*` identifiers are used only when the implemented semantics match the named
markdownlint rule. Local classification and stronger repository semantics stay
under `LS*`. Unknown configuration keys fail policy loading so a misspelling or
unsupported external rule cannot be silently ignored.

`MD032` checks that every list block has a blank line before and after it. It
applies to structured documents and adapters alike, including lists inside
review artifacts.

`MD038` checks inline-code spans for unnecessary spaces immediately inside their
delimiters. It does not report whitespace that belongs to the parsed code value,
spans containing only spaces, or the matching single leading and trailing source
spaces used as delimiter padding when code content begins or ends with a
backtick. This mirrors markdownlint's intentional code-span exceptions instead
of replacing genuine code whitespace with prose such as `[space]`.

`MD050` requires asterisks for strong emphasis in prose. The shared source model
masks inline and fenced code before this evaluator runs, so an underscore-bearing
filename such as `__init__.py` must be written as code and is then exempt from
strong-style evaluation.

Review transcripts are generated from caller-authored requestor and reviewer
content without normalizing blank lines around lists. Because those transcripts
are protocol-owned and append-only after publication, authors must satisfy the
renderer-specific boundary before publication. Caller content rendered as its
own block keeps a blank line before and after every list. Content inlined behind
a label, specifically requested-changes, covered-wording, and writer-response
fields, must not begin with a list: it begins with a prose sentence, then a blank
line, then any list. Renderer changes remain outside this effort.

### Configuration precedence for mandatory heading protection

Repository configuration is loaded before any Markdown file. A configured
`false` disables a supported optional rule, and a rule-specific object supplies
validated options. `MD024` and `MD025` remain mandatory at the effective-policy
layer, so configuration cannot remove them from evaluation. An attempted
`false` for either mandatory rule fails policy loading before any document is
scanned. The reference page lists mandatory rules separately from configurable
rules.

Local `LS001`, `LS002`, and `LS003` behavior is defined by this design and the
feature request. They do not impersonate markdownlint options that have
different semantics.

### Stable finding model for policy evaluation

Every rule returns zero or more finding records rendered as
`path:line: RULE: reason`: repository-relative path, positive source line,
stable rule identifier, and a concrete reason. Whole-file findings use line 1.
Rules do not print directly; the runner owns ordering and rendering so parallel
or refactored evaluation cannot change observable output accidentally.

Findings are ordered by normalized repository path, source line, rule
identifier, and reason and written to standard output. Operational errors and
passing baseline-debt advisories are written to standard error. The direct
process exits successfully only when policy loading succeeds and every emitted
finding is covered without growth by the baseline.

## Document model for the v0.11.0 repository Markdown checker

### Tracked Markdown inventory boundary

The repository's Git index is the authority for scope. The checker asks Git for
tracked paths, retains Markdown suffixes case-insensitively, normalizes their
display form to forward-slash repository-relative paths, and evaluates a fixed
snapshot for the run. Untracked scratch files and ignored `a.*` workflow inputs
are outside the inventory.

Failure to obtain the inventory, a tracked path escaping the repository, or a
tracked Markdown file becoming unreadable during the run fails the checker with
an operational diagnostic.

### Fence-aware Markdown source representation

Each file is decoded as UTF-8 and scanned once into a lightweight source model.
The model records frontmatter bounds, fenced-code bounds, ATX headings with
their line and level, list-block boundaries, inline-code spans with delimiter
and parsed-value boundaries, raw HTML elements, and non-blank body lines.
Heading-like text and list markers inside a fence are literal
content and never enter the structural model.

The scanning primitive used by `tools/review_markdown_headings.py` is reused or
factored into a shared helper so review rendering and checking agree about
fenced content. Rule evaluators receive the source model and never rescan raw
text independently.

### Adapter classification before structured checks

Classification is deterministic and precedes rule evaluation. A document is an
adapter when it has YAML frontmatter with a non-empty `description`, when it is
a bounded canonical pointer in one of the approved adapter roots, or when it is
a reusable `templates/` fragment whose first heading is level two or deeper.

The bounded pointer classifier counts at most five non-blank body lines after
frontmatter and requires the body to contain a resolvable repository-relative
Markdown link to a canonical instruction or rule plus optional explanatory
pointer text. The fragment classifier has no line bound. Of the 35 current
bounded pointer candidates, 34 already carry that link and the remaining
template qualifies independently as a fragment, so this contract reclassifies
no current file. Classification exempts only `LS001` and `LS002`; all other
enabled rules receive both adapter and structured documents.

### Complete heading hierarchy and uniqueness evaluation

`LS001` requires one level-one title for structured documents. `LS002` requires
at least two level-two sections for structured documents. `MD025` reports every
level-one heading after the first in any checked file.

`MD001` evaluates the ordered heading stream and reports a heading whose level
has no preceding immediate parent or skips a level. Levels one through six are
valid when their ancestry is complete. Adapter status does not weaken this
hierarchy check.

`LS003` normalizes every heading title by dropping inline formatting,
lowercasing while retaining non-ASCII characters, removing punctuation other
than hyphens, and replacing whitespace runs with one hyphen. It reports every
occurrence after the first normalized title across the complete file,
regardless of heading level or parent. `MD024` remains in the mandatory catalog
for its matching duplicate-heading semantics. Both rules evaluate and report
independently when one occurrence violates both contracts.

## Baseline model for the v0.11.0 repository Markdown checker

### No-growth comparison for residual findings

The repository-root `.markdownlint-baseline.json` is a tracked, versioned JSON
document containing aggregate allowances with explicit path, rule, and count
fields. After evaluation, the runner groups findings by the same key. A key
fails when its actual count exceeds its allowance; a new key has an implicit
allowance of zero. A count below the allowance passes and writes a deterministic
debt-reduced advisory to standard error so the allowance can be lowered in a
later deliberate update.

Rules with no measured findings have no entries. The baseline cannot waive
configuration, inventory, decoding, or baseline-format errors.

### Baseline integrity and maintenance boundary

`.markdownlint-baseline.json` is parsed under a versioned schema, rejects
duplicate keys, requires positive counts, and rejects unsupported rule
identifiers. Paths use the same normalization as findings so alternate
separators cannot create a second allowance. The reference page explains how
maintainers verify a shrink before updating an allowance; normal checker
execution never rewrites the baseline.

## Runtime integration for the v0.11.0 repository Markdown checker

### Platform-neutral direct launcher contract

The root launcher self-locates the repository and the llm-shared Python
environment, accepts no interactive input, and invokes the checker with the
repository root, configuration, and baseline resolved by the checker contract.
Calling it from the repository root requires no prior `senv.bat` activation.
The same Python entry point remains callable on non-Windows hosts.

The process writes findings and policy errors to standard output or standard
error according to the documented diagnostic contract and returns zero only
for a complete passing evaluation. No network or Node lookup is attempted.

### Windows shared-gate connection

`check.bat` invokes the repository-root Markdown launcher once, captures its
exit status, reports the local success or failure message, and calls
`record_failure markdown <status>` on failure. The gate continues to its final
aggregate report so Markdown failures appear beside the other check names.

The integration does not duplicate rule configuration or baseline logic in
batch code. The direct launcher result and the shared-gate result therefore use
one policy authority.

## File-based IO cost clarification for the v0.11.0 checker design

One run executes one Git tracked-path query, one configuration read, one
baseline read, and one UTF-8 read per tracked Markdown file. The source model is
created once per file and passed to classification and rule evaluators in
memory. Baseline grouping and deterministic sorting operate on collected
records without reopening source files, and no rule performs its own directory
walk.

## Acceptance cases for the v0.11.0 repository Markdown checker

| Scenario | Expected outcome | Reason |
| --- | --- | --- |
| Structured file with one `#`, two `##` sections, nested `###`, and unique titles | Heading checks pass | The complete structured outline is present |
| Structured file with no `#` | `LS001` at line 1 | The local title rule owns adapter-aware absence |
| Adapter with frontmatter `description` and no `#` | No `LS001` or `LS002` | Adapter classification removes only structured obligations |
| File with a second `#` | `MD025` at the second title | Multiple top-level titles are always forbidden |
| File jumping from `#` to `###` | `MD001` at the `###` line | The immediate parent heading is absent |
| Repeated normalized title under another parent | `LS003` at each later occurrence | Uniqueness is global across the file |
| Exact repeated heading at one later occurrence | Both `MD024` and `LS003` at that occurrence | Mandatory literal and normalized uniqueness rules report independently |
| List touching adjacent prose without a blank line | `MD032` at the list boundary | Every list block must be surrounded by blank lines |
| Inline-code span with one-sided or unnecessary inner padding | `MD038` at the span | Accidental delimiter-adjacent space is rejected |
| Inline-code span whose parsed value genuinely preserves boundary whitespace, contains only spaces, or needs matching padding around literal backticks | No `MD038` | Markdown code-span semantics require the space |
| Underscore-delimited strong emphasis in prose | `MD050` at the source line | Strong style uses asterisks |
| Underscore-bearing filename inside inline or fenced code | No `MD050` | Code content is not strong-style prose |
| Raw `img` element under current configuration | No `MD033` | The configured element is allowed |
| Raw non-`img` element with no matching allowance | `MD033` at its source line | The enabled raw-HTML rule applies |
| Finding count above a matching baseline allowance | Checker failure | Residual debt may not grow |
| Finding count below a matching baseline allowance | Checker success with shrink visible in results | Debt may shrink without automatic baseline mutation |
| Unknown configuration key | Checker failure before file evaluation | Unsupported policy cannot be ignored |
| Direct launcher invoked without environment setup | Complete deterministic run | The launcher owns environment resolution |

## Design decisions for the v0.11.0 repository Markdown checker

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Evaluate and report `MD024` and `LS003` independently. | Complete heading hierarchy and uniqueness evaluation | Suppress `MD024` behind `LS003`; partition exact and normalized collisions |
| Q02 | Reject configuration that attempts to disable `MD024` or `MD025`. | Configuration precedence for mandatory heading protection | Ignore the conflict with or without an advisory |
| Q03 | Require a resolvable repository-relative Markdown link for bounded pointer adapters. | Adapter classification before structured checks | Accept path-like prose; classify every short file by location |
| Q04 | Pass a reduced baseline count with a debt-reduced advisory on standard error. | No-growth comparison for residual findings | Fail on shrink; pass silently |
| Q05 | Store explicit records in repository-root `.markdownlint-baseline.json`. | Baseline model for the v0.11.0 repository Markdown checker | Use a tab-separated file; mix debt into `.markdownlint.json` |
| Q06 | Emit `path:line: RULE: reason` findings on standard output and health messages on standard error. | Stable finding model for policy evaluation | Mix messages on standard output; emit JSON Lines |

## Documentation contract for the v0.11.0 repository Markdown checker

One focused page under `wiki/reference/` lists the supported rule catalog,
mandatory rules, configuration behavior, adapter classification, direct
launcher, diagnostic fields, `.markdownlint-baseline.json` semantics, and
shared-gate name. It
defines the exact `LS003` normalization and distinguishes it from `MD024`, and
identifies hierarchy findings as `MD001`, list-boundary findings as `MD032`, and
the genuine-code-space exceptions to `MD038`.
It also tells requestors and reviewers to leave a blank line before and after
every list rendered as its own block. For requested-changes, covered-wording,
and writer-response fields inlined behind labels, it requires an opening prose
sentence followed by a blank line before any list. Published transcripts cannot
rely on the checker to insert missing boundaries after publication.

Existing Diataxis navigation links the page in the repository order:
explanation, tutorials, how-to guides, then reference. The page remains a
reference contract and does not become an implementation walkthrough.

## Design boundaries for the v0.11.0 repository Markdown checker

This design specifies policy interpretation, document classification, data
flow, baseline semantics, diagnostic behavior, and gate integration. It leaves
file-by-file implementation sequencing, module names, detailed test placement,
and rollout commands to the implementation plan.

The checker does not edit documents, update its own baseline, fetch packages,
alter review-exchange state, or normalize caller-authored review content.
Historical debt remains visible and bounded without turning this effort into a
repository-wide Markdown rewrite.

The existing `MD032` finding at line 264 of the design-review transcript is
repaired during this documentation update. Step 3 therefore verifies the clean
boundary instead of waiting at a human-only checkpoint, and `MD032` keeps no
baseline allowance.
