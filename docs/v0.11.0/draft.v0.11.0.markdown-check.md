# Check Markdown against the repository rules

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

## Boundary inherited from the umbrella

This child covers only umbrella item 7. It owns the repository-wide Markdown
checker, its repository-root launcher, its place in the shared gate, and the
Diátaxis reference that explains the enforced rules. It does not own the review
exchange lifecycle, specification or code reviewer behavior, commit-plan
validation, review-status reporting, or interrupted-review recovery.

The effort depends on the completed `review-exchange-core`, `code-reviewer`, and
`review-mode-docs` items. Its reason for remaining separate is that duplicate
transcript headings are review-protocol defects, while the executable checker
is a repository quality gate that must not become the responsibility of either
reviewer role.

The non-negotiable inherited constraints are:

- use the repository's declared `.markdownlint.json` policy, including disabled
  MD013 and MD033 limited to `img`;
- enforce MD032 so every list is surrounded by blank lines and cannot merge
  accidentally with the prose before or after it;
- enforce MD038 for unnecessary spaces immediately inside inline-code markers,
  while ignoring boundary spaces that the Markdown code-span syntax preserves
  as genuine code content or uses as required delimiter padding around
  backticks;
- enforce MD050 so prose uses asterisks for strong style and underscore-bearing
  filenames such as `__init__.py` are written as inline code;
- implement the unattended check in Python because Node and a reachable package
  network are unavailable;
- report each finding with its path, line, rule, and reason;
- never permit configuration to disable MD024 or MD025; and
- require exactly one `#` document title, multiple `##` section titles, and
  properly nested `###` subsection titles without skipped or orphaned heading
  levels;
- require every heading title to be unique across the complete document, not
  merely unique among siblings at the same level; and
- settle gate severity, tracked-versus-changed scope, and treatment of existing
  findings during requirement and design work instead of folding unrelated
  cleanup into this effort.

Review mode declares Markdown heading rules non-negotiable, but nothing in the
project can verify them. `instructions/review-requestor.md` states that every
heading text must be unique within a transcript, that a transcript keeps exactly
one top-level heading, and that "a transcript a Markdown linter reports `MD024`
or `MD025` on is a defect in the round that appended to it". The reviewer mode
added to `instructions/implementation-check.md` repeats that rule. The
repository carries `.markdownlint.json`, which turns MD013 off and limits MD033
to `img`, so the intended rule set is already declared. Yet no command in the
repository applies it: `ghog check` runs ty, pyright, ruff, radon, vulture, a
file-size check, shellcheck, and an end-of-file check, and none of them reads a
Markdown file.

## Why this is worth an effort of its own

Every Markdown defect found during the v0.11.0 code-reviewer effort was caught
by hand or not at all, and one reached a published protocol artifact before a
human noticed it.

- A published transcript heading was hand-edited to `## Round 1 by human - Step
  2 bis` to dodge a duplicate. The counter suffix violated the same instruction
  that forbids counters, and no check rejected it.
- `review.plan.v0.11.0.code-reviewer.md` carried six duplicate headings from a
  restarted exchange, in a file staged for commit. It took a reviewer reading
  headings by eye to find them.
- A sentence wrapped so that `0.` began a line, which CommonMark renders as an
  ordered list item in the middle of a paragraph.
- `plan.v0.11.0.code-reviewer.md` carried a whitespace-only line between a
  horizontal rule and a heading.

The store now prevents duplicate generated headings, and Step 4's renderer
qualifies authored ones. Those are the right fixes, but they protect only the
headings those two components emit. Every other Markdown file in the repository,
and every hand-authored section inside a review artifact, remains unverified.

## Shape of the need

A checker that applies the repository `.markdownlint.json` rules, a launcher
that runs it from the repository root without environment setup, and a step in
the shared gate so a violation stops the walk the way a lint error does today.
A Diátaxis reference page should state which rules are enforced and why the two
heading rules cannot be disabled. The checker must also validate the complete
heading outline: one level-one document title, multiple level-two sections with
their level-three subsections, no skipped levels, and no repeated heading title
anywhere in the file. It must also reject lists that are not surrounded by blank
lines under MD032. It must reject accidental inline-code padding under MD038 but
must not report spaces that genuinely belong to the parsed code value, including
space-only spans and delimiter padding needed around literal backticks.

The checker has to work in this environment: no Node runtime is installed, so
the markdownlint CLI is unavailable, and package downloads fail because the
network presents an untrusted certificate. A Python implementation over the
declared rule set is therefore the only route that runs unattended here.

## File-based IO cost clarification for the markdown-check draft

One checker run reads the tracked-path index, configuration, and baseline once,
then reads each tracked Markdown file once. Rule evaluators share the parsed
source model and do not reopen files or repeat repository-wide directory scans.

## Questions for the requirement and design phases

These are open on purpose and belong to `write-requirement` and `write-design`
rather than to this draft.

- Which rules the checker implements, and whether the set is fixed in code or
  read from `.markdownlint.json`.
- Whether the gate fails or warns, and whether it covers every tracked Markdown
  file or only the changed ones.
- What to do with the pre-existing findings outside this effort. A survey during
  the code-reviewer rounds counted roughly one hundred, spread over about forty
  files, dominated by blank-line rules around lists, headings, and fences. They
  are unrelated to review mode and should not silently enter an unrelated
  commit.
- Whether the transcript-specific rules deserve a stricter mode than ordinary
  documentation, since a duplicate heading in a transcript is a protocol defect
  while a missing blank line is cosmetic.
