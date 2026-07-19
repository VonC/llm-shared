# Document templates

<img src="../assets/logo-llm-shared-documents-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📝 The skeletons under `templates/` that the skills fill. Their place in the
shared source tree is shown in the
[repository layout](repository-layout.md#shared-bodies-and-rules). One template
per document kind; the instruction bodies reference them by path.

## Invocation model

AI workflow skills normally load and fill these templates, then ask the human to
validate decisions at the appropriate gate. Copy or fill one directly when
authoring a custom artifact outside the workflow or testing a template change.

## 📝 write-requirement.template.md

Two skeletons in one file. Feature-request: short title, the revision
that introduces the topic, current behavior in `vX.Y.Z`, the gap to close,
code references. Issue: the same plus revision history, current side
effects, wording and gap analysis, the confirmed rule, and concrete
examples.

## 📐 write-design.template.md

`# Design vX.Y.Z -- {Topic}`, then context, scope (with in-scope and
deferred subsections), confirmed technical facts, current and target
behavior, one section per design area, and the acceptance cases as a
scenario, expected outcome and reason table. No open-questions section —
the review loop adds it later.

## 🗺️ write-plans.template.md

The implementation plan: plan goal per step, scope anchors, complexity
and file-based IO cost clarifications, confirmed technical facts (files
at the 550-line risk, safe to extend, new), a test-tree snapshot, the
shared execution command checklist with ready-to-run `ghog` commands,
then the numbered steps. Each step carries three subsections: analysis
and intent, implementation (files involved, tests first, completion
criteria), and addendums (line-budget checkpoint, split guidance,
timing).

## ✅ write-plans.validation.template.md

The tracking companion: per step, an analysis section whose first
sentence is exactly `Yes. Step N has been fully implemented.` or
`No. Step N has NOT been fully implemented.`, the goal, what was
implemented, a `Missing work` list only when the verdict is No, then the
architecture, performance, unit-test-coverage and feature-integrity
checks. Freshly created sections hold
`_(empty — no check has taken place yet.)_.`.

## ❓ open-question.template.md

One `### Qxx: {title}` block per question: the description, a BBQ
rewording, an options section with pros and cons per option, the
recommended option, and an explicit `Answer to Qxx` slot.

## ✉️ group-commits-msg.template.md

The `a.commit` format: a `## Group x: [topic]` header, the `git add`
line, then a `log` fenced block holding the conventional message with its
`Why:` and `What:` sections. See
[Commit message format](commit-message-format.md).

## 🏷️ prepare-release-notes.version-txt.template.txt

Plain text, not markdown. First line
`X.Y.Z-SNAPSHOT -- Release notes summary for version X.Y.Z` (the ` -- `
separator is load-bearing), three witty title and subtitle pairs, the
main theme paragraph, an optional secondary theme, and a
`### Key changes` list of three bullets. After the title choice, line one
carries the chosen title and line three its subtitle.

## 🇫🇷 activity-report.french.template.md

`# Rapport d'activité du {start} au {end}`, an `## En bref` section of
three to six standalone manager-ready lines, then one short `##` section
per selected topic, each naming its working tree, all in French with
unique titles.

## 🧾 activity-elements.template.md

The generated `a.md` the report is built from: the period line, then per
working tree a commit-messages list and a fenced diff of the `*.md`
files.

## 📄 md_to_pdf.py.template

The reusable markdown-to-PDF helper: converts through the `markdown`
package, wraps in print-styled HTML, renders with xhtml2pdf — no browser
involved.

Related: [Artifact files and naming conventions](artifact-files.md),
[skills catalog](skills-catalog.md).
