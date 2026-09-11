# Check Markdown against the repository rules

## Review-mode need behind the Markdown checker

Review mode treats malformed transcript headings as protocol defects, but the
repository has no executable Markdown check. Heading defects and other declared
Markdown violations are currently found by visual inspection, if they are found
at all. A published transcript and staged documentation can therefore violate
rules that the requestor and implementation-check instructions already call
non-negotiable.

As a maintainer, I want one repository command to check Markdown against the
repository policy so malformed documentation and review evidence fail through
the same shared gate as other lint errors.

## Current Markdown validation in v0.11.0

- `.markdownlint.json` disables MD013 and allows only `img` for MD033.
  Markdownlint treats rules omitted from that file as enabled by default, while
  the bounded Python catalog needs an explicit interpretation of which rules
  are enabled for this checker.
- MD032 is omitted from `.markdownlint.json` and therefore remains enabled. The
  checker must enforce blank lines before and after lists so list markers cannot
  merge accidentally with adjacent prose.
- MD038 is also omitted and remains enabled. It reports unnecessary spaces next
  to inline-code delimiters, but it must preserve markdownlint-compatible
  exceptions when the parsed code value genuinely contains boundary whitespace,
  when the span contains only spaces, or when matching delimiter padding is
  needed around literal backticks.
- `instructions/review-requestor.md` requires one top-level transcript title
  and unique heading text, and it forbids disabling MD024 or MD025 to make a
  transcript pass.
- `instructions/implementation-check.md` applies the same heading rule while
  validating review-mode work.
- The repository-root `check.bat` shared gate records each check through
  `record_failure <name> <status>`, but no shared gate command reads Markdown
  files.
- Node is unavailable in the required environment, and package retrieval cannot
  be relied on, so the JavaScript markdownlint CLI cannot be a runtime
  dependency.

### Measured adoption context for markdown-check

An independent, fence-aware approximation over 371 tracked Markdown files found
156 files without a level-one title, 168 files without multiple level-two
sections, and 61 MD033 findings across 11 files. It found no MD024 duplicate
headings and no skipped heading levels. The missing-title population is
concentrated in machine-consumed adapter files whose identity is carried by a
YAML frontmatter `description`, so those files are correct without an `#`
title. These figures describe the adoption boundary; the shipped checker will
remain the authoritative result.

## Gap to close for repository Markdown checking

1. Provide a Python checker that applies the repository's declared Markdown
   policy without requiring Node or package downloads.
2. Provide a repository-root launcher that runs without environment setup.
3. Add the checker to the shared gate so its configured failure result affects
   the walk like another lint result.
4. Report every finding separately with its path, line, rule, and reason.
5. Document the enforced rules and the non-disableable heading contract in a
   focused Diátaxis reference page.

## Required heading outline for checked Markdown

### Document classification for checked Markdown

A checked file is an adapter when any condition holds:

- YAML frontmatter provides its `description`; or
- it is under `.agents/llm-shared/instructions/`,
  `.agents/llm-shared/rules/`, `.claude/`, `.github/`, or `templates/`, has at
  most five non-blank body lines after frontmatter, and serves only as a pointer
  to canonical instructions; or
- it is under `templates/` and its first heading is level two or deeper, with no
  line-count bound, because it is a reusable fragment intended for substitution
  into a parent document and is structurally unable to carry a level-one title.

Every other tracked Markdown file is a structured document. Adapters are exempt
from the title-presence and multiple-section rules but remain subject to the
duplicate-title, global uniqueness, raw HTML, and complete hierarchy checks.

### One document title for checked Markdown

Each structured document has exactly one level-one `#` title. A file whose
identity is carried by the adapter classification may omit that title, but no
checked file may contain more than one level-one title. MD025 governs the second
level-one-title case and cannot be disabled. The missing-title behavior diverges
from MD041 because it includes the local adapter classification, so it is
reported as repository-local rule `LS001`.

### Section hierarchy for checked Markdown

Each structured document has multiple level-two `##` section titles.
Level-three `###` subsection titles belong below a preceding level-two section.
Every checked file follows immediate parent order for the heading levels it
uses; a heading cannot skip a level or appear without its required parent.
Insufficient level-two sections are reported as repository-local rule `LS002`.
The complete hierarchy check matches markdownlint's heading-increment semantics
and is reported as `MD001`. Levels `####` through `######` are allowed when
every heading has its immediate parent and no level is skipped.

### Unique titles for checked Markdown

Every heading title is unique across the complete document, regardless of its
level or parent section. A title repeated under another section is still a
finding. Configuration cannot weaken this rule to sibling-only uniqueness. This
effort defines anchor-style equality inline, implements it as repository-local
rule `LS003`, and documents it in the reference page rather than attributing
the stronger behavior to MD024. The normalization lowercases while retaining
non-ASCII characters, drops inline formatting, removes punctuation other than
hyphens, and replaces whitespace runs with one hyphen.

## Required repository policy for markdown-check

### Declared configuration for markdown-check

The checker respects the repository policy declared in `.markdownlint.json`,
including disabled MD013 and the MD033 `img` allowance. MD024 and MD025 remain
mandatory even if a later configuration edit attempts to disable them. The
published supported rule catalog is the enabled set: every catalog rule runs
unless the configuration disables it, configuration may only disable or
configure catalog rules, and a key outside the catalog stops the checker with a
clear error. MD032, MD038, and MD050 belong to that supported catalog. MD032 applies its
blanks-around-lists semantics to every checked file. MD038 reports only
unnecessary inner padding; it ignores spaces that are part of the parsed
inline-code value, space-only code spans, and the matching single-space padding
used to delimit code content that begins or ends with a backtick.

MD050 requires asterisk-delimited strong style in prose. Underscore-bearing
filenames such as `__init__.py` must be enclosed in inline-code delimiters, and
content already inside inline or fenced code is not evaluated as strong style.

### Runtime independence for markdown-check

The implementation is Python and runs unattended in the current repository
environment. It has no Node runtime, package-network, or interactive prompt
dependency. The Python checker is a documented direct, platform-neutral entry
point, while `check.bat` remains the Windows shared-gate launcher.

### Finding format for markdown-check

Each violation is reported on its own output line. That line identifies the
repository-relative path, source line, rule identifier, and concrete reason so
the author can locate and correct the defect without interpreting a summary.
Repository-local checks use the `LS*` namespace, while `MD*` is reserved for
matching markdownlint semantics. A finding that applies to the complete file
reports line 1 as its stable, positive source location.

### Shared-gate place for markdown-check

The repository-root launcher participates in the shared gate and checks every
tracked Markdown file. Every enforced finding fails the checker and gate. A
tracked no-growth baseline, keyed on repository-relative path, rule, and count,
records every enforced rule with residual findings after adapter
classification. Any new finding fails, and the baseline must shrink or remain
unchanged. The measured initial baseline contains one `LS001` entry, 17 `LS002`
entries, and 61 MD033 findings across 11 files; MD024, MD001, and `LS003` remain
at zero. MD038 also has no baseline entry after its genuine-code-space
exceptions are applied; any remaining MD038 finding must be repaired.

## Requirement clarifications

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Use the published supported catalog as the enabled set so unsupported configuration cannot be ignored silently. | Declared configuration for markdown-check | Reproduce every markdownlint rule; check only mandatory heading rules |
| Q02 | Check every tracked Markdown file so the gate represents the complete repository state. | Shared-gate place for markdown-check | Changed files only; changed-file gate plus separate full inventory |
| Q03 | Fail the checker and shared gate for every enforced finding so a green gate means the policy passed. | Shared-gate place for markdown-check | Warn for non-heading findings; make the first release report-only |
| Q04 | Keep a no-growth baseline keyed on path, rule, and count for residual findings, excluding only measured-zero rules. | Shared-gate place for markdown-check | Repair all historical findings first; avoid a baseline by checking changed files only |
| Q05 | Apply title and section-count requirements to structured documents while exempting deterministic frontmatter, bounded pointer, and bounded fragment adapters. | Document classification for checked Markdown | Require the outline everywhere; configure exemptions by path pattern |
| Q06 | Compare globally unique headings using the stated GitHub-style normalization under `LS003`. | Unique titles for checked Markdown | Exact source equality; case-insensitive rendered text without punctuation normalization |
| Q07 | Allow all six heading levels while requiring every immediate parent and forbidding skipped levels. | Section hierarchy for checked Markdown | Forbid levels below `###`; permit deeper headings without validating them |
| Q08 | Reserve `MD*` for matching markdownlint semantics and assign stable `LS*` identifiers to divergent local rules. | Finding format for markdown-check | Reuse approximate `MD*` identifiers; use descriptive names without stable identifiers |
| Q09 | Report line 1 for whole-file findings because it is positive, editor-friendly, and stable. | Finding format for markdown-check | Report the end-of-file line; use line 0 |
| Q10 | Expose the Python checker as the portable entry point while retaining `check.bat` for the Windows shared gate. | Runtime independence for markdown-check | Support only `check.bat`; add separate Windows and POSIX wrappers |

## Acceptance criteria for markdown-check

### Heading acceptance cases for markdown-check

- A structured document with one `#` title, multiple `##` sections, properly
  nested `###` subsections, and globally unique heading text passes the heading
  checks.
- A structured document with no `#` title reports a finding.
- An adapter identified by YAML frontmatter, the bounded pointer rule, or a file
  under `templates/` whose first heading is level two or deeper may omit `#` and
  multiple `##` sections.
- A missing required structured-document title reports `LS001`, and an
  insufficient structured-document section count reports `LS002`.
- Any checked file with more than one `#` title reports MD025.
- A document that skips from `#` to `###`, or places `###` before a parent
  `##`, reports `MD001`.
- A document that repeats heading text anywhere in the file reports a finding,
  even when the repetitions have different levels or parents, as `LS003`.
- An attempted configuration change that disables MD024 or MD025 does not make
  a violating document pass.

### Repository-policy acceptance cases for markdown-check

- MD013 remains disabled under the current repository configuration.
- MD032 reports a list without a blank line before or after its list block.
- MD038 reports one-sided or otherwise unnecessary space next to an inline-code
  delimiter, but does not report a genuine boundary space, a space-only code
  span, or matching delimiter padding around literal backticks.
- MD050 reports underscore-delimited strong style in prose, including an
  unquoted `__init__.py` token, while accepting asterisk strong style and code
  spans.
- MD033 permits `img` and reports other raw HTML elements under the current
  repository configuration.
- Every reported violation includes path, line, rule, and reason.
- Repository-local findings use the `LS*` namespace, including `LS001` for a
  missing structured-document title, `LS002` for insufficient structured
  sections, and `LS003` for anchor-normalized duplicate headings. `MD*` remains
  reserved for matching markdownlint semantics, including `MD001` for hierarchy.
- The launcher runs from the repository root without prior environment setup.
- The checker and launcher run without Node and without network access.
- The shared gate invokes the checker and reflects its settled severity policy.

### Documentation acceptance case for markdown-check

A Diátaxis reference page identifies the checked rules, the launcher contract,
the diagnostic format, and why the duplicate-title and title-uniqueness rules
cannot be disabled. The page also defines the exact anchor-style normalization
and distinguishes `LS003` from MD024. It identifies the heading-hierarchy check
as `MD001`.

## Scope boundaries for markdown-check

This effort owns the checker, launcher, shared-gate connection, tests, and
reference documentation. It also owns the definition, implementation, tests,
and documentation of the anchor-style normalization. It does not repair every
historical Markdown finding as an unrelated side effect. It also does not
change review-exchange ownership, reviewer behavior, commit-plan validation,
review-status reporting, or interrupted-review recovery.

## File-based IO cost clarification for the markdown-check requirement

The checker obtains one tracked Markdown inventory from Git, loads policy and
baseline inputs once, and reads each inventory file once per run. Classification
and all supported rules reuse the same parsed representation, so the shared gate
does not multiply file reads by rule count.

## Code and policy references for markdown-check

- `.markdownlint.json`: current repository Markdown policy.
- `instructions/review-requestor.md`: transcript title-count and unique-title
  requirements.
- `instructions/implementation-check.md`: implementation validation rule that
  treats MD024 and MD025 findings as defects.
- `docs/v0.11.0/draft.v0.11.0.markdown-check.md`: approved source draft and
  umbrella-derived constraints.
- `docs/v0.11.0/draft.v0.11.0.review-mode.md`: umbrella identity, boundary,
  dependencies, and ordered status row.
