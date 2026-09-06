# Artifact files and naming conventions

<img src="../assets/logo-llm-shared-documents-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📝 Every file the workflow reads or writes, split between the versioned
documents under `docs\` and the transient `a.*` files at the project root.

## Invocation model

Workflow skills create and consume most of these files automatically. Humans
normally inspect them at validation gates and edit only the artifacts whose
workflow explicitly requests an answer or approval. Use this reference when a
manual tool invocation needs an exact path or naming contract.

## 📚 Versioned documents under docs

A single-topic effort normally keeps one version slug `vX.Y.Z` and one topic
slug through every phase. A collection can keep one umbrella draft while its
independently developed requirements use their own item slugs:

`/process-draft` chooses one effort directory and keeps every versioned
document for that effort there:

| Layout | Effort directory for `vX.Y.Z` |
| --- | --- |
| Flat | `docs/` |
| Minor version | `docs/vX.Y/` |
| Full version | `docs/vX.Y.Z/` |
| Minor and full version | `docs/vX.Y/vX.Y.Z/` |

The full-version layout is the recommended default. In the patterns below,
`<effort-dir>` means whichever one of these four directories contains the
canonical draft.

| Pattern | Written by | Holds |
| --- | --- | --- |
| `docs\draft.<topic>.md` | the author | the raw idea, no version yet |
| `<effort-dir>/draft.vX.Y.Z.<slug>.md` | `/process-draft`, then `/split-and-define` for collections | the classified, branched draft; an umbrella carries the ordered status index, while an umbrella continuation writes the focused child into its item branch |
| `<effort-dir>/feature-request.vX.Y.Z.<topic>.md` | `/write-requirement` | new behavior to build |
| `<effort-dir>/issue.vX.Y.Z.<topic>.md` | `/write-requirement` | a bug or missing behavior |
| `<effort-dir>/design.vX.Y.Z.<topic>.md` | `/write-design` | scope, constraints, acceptance cases |
| `<effort-dir>/plan.vX.Y.Z.<topic>.md` | `/write-plans` | numbered implementation steps |
| `<effort-dir>/plan.vX.Y.Z.<topic>.validation.md` | `/write-plans`, then `/implementation-check` | per-step verdicts and checks |
| `<effort-dir>/review.<type>.vX.Y.Z.<topic>.md` | the review exchange | append-only specification or code review evidence |

### Document selector contract

Utilities do not need the effort directory when they already know the full
version, slug, and document type. The selector checks only the four supported
directories for that version. For example:

```text
pw document v10.0.0 route-cleanup plan
```

prints the unique repository-relative plan path. Supported types are `draft`,
`requirement`, `feature-request`, `issue`, `design`, `plan`, and
`validation-plan`. `requirement` accepts either concrete requirement prefix.
Hyphens and underscores in the slug compare as equivalent.

The match is exact: asking for `route-cleanup` does not silently select
`route-cleanup-extra`. No match returns the not-applicable exit code. If the
same selector exists in more than one supported layout, resolution fails as
ambiguous instead of choosing the newest or first copy.

### Direct and umbrella draft relationships

For an umbrella continuation, the focused child at
`<effort-dir>/draft.vX.Y.Z.<item-slug>.md` is a required on-disk artifact in the
item branch. `/process-draft` reads it back after branch creation and does not
open the approval gate until the file exists. That file is authoritative for
human review and later revisions; a copy rendered in conversation is only a
preview.

For a single topic, the draft and requirement usually share a slug:

```txt
docs\v10.0.0\draft.v10.0.0.route-cleanup.md
docs\v10.0.0\issue.v10.0.0.route-cleanup.md
```

For a collection, the umbrella draft deliberately keeps the collection slug:

```txt
docs\v10.0.0\draft.v10.0.0.sentinel.md
docs\v10.0.0\issue.v10.0.0.route-cleanup.md
branch: route_cleanup
```

The umbrella is marked explicitly:

```md
- Type: collection (feature-requests and issues)
- Draft role: umbrella
```

Its exact `## List of feature-requests and issues to create` section starts
with this compact schema:

```md
| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
```

`Order` is consecutive from 1. `Status` is `pending` or `completed`. Pending
rows use `-` for both paths; completed rows name an existing requirement and a
validation plan whose document-level status is `Yes, it is implemented.`.
`implementation-check` owns the completed transition.

The requirement filename, not the umbrella draft filename, identifies the
current item. The shared menu-less resolver used by `pw skill` and `pw handoff`
accepts this layout only when the normalized branch leaf matches exactly one
requirement and that requirement has exactly one related direct or canonical
umbrella draft. Same-version proximity alone is not a relationship.

## 🤖 Configured independent-review runtime files

The versioned project-root `.review-artifacts.ini` optionally selects one
repository-relative artifact home. When the declaration is absent, the home is
`.reviews`. The home itself is ignored through its exact catch-all `.gitignore`;
protocol results return paths below that home, and callers must not reconstruct
them.

| File | Role |
| --- | --- |
| `a.review-*` | current request, answer, coordination, tombstone, lock, migration journal, or archived recovery evidence |
| `a.code-review-evidence.<version>.<slug>.step-<step>.json` | retained code-review evidence manifest, retired after answer publication |

The versioned `review.<type>.<version>.<slug>.md` transcript is the exception:
it stays beside the reviewed document rather than in the runtime home. See the
[independent review contract](independent-review-mode-contract.md#artifact-home-configuration-and-migration)
for declaration, migration, and exact naming rules.

## 🧾 Transient a-dot files at the project root

All matched by the `a.*` gitignore line — scratch by design, never
committed:

| File | Role |
| --- | --- |
| `a.commit` | grouped-commit plan, one block per group, replayed by `gcba` |
| `a.diff` | snapshot of the staged diff written by `gcmp`, justifies the grouping |
| `a.docs` | dump of the merged branch documents for the merge reword |
| `a.prompt.txt` | next-step prompt written by `pw` and `pw handoff` |
| `a.prompt_memory` | per-branch workflow state: branch, locked topic, current step |
| `a.md` | scratch analysis: release-prep notes, or activity-report elements |
| `a.<base>.open.questions.md` | companion file of a review round, managed by `oqm.bat` |
| `a.prepare-release.active` | flag telling a callee skill to hand control back to `/prepare-release` |
| `a.activity-report.<start>-<end>.md` | the activity report (plus `.html` and `.pdf`) |
| `a.profile.html` | pyinstrument profile of one slow test |

## 🧪 Groundhog files

| File | Role |
| --- | --- |
| `.testmondata` | the testmon database; deleted and rebuilt by `ghog full` |
| `a.ghog.log` | redirect target of every LLM-driven run; overwritten per run, never deleted |
| `a.ghog.status` | run lifecycle line: `state=running pid=...`, then `state=done exit=...` |
| `a.ghog.failures` | failing node ids of the last full run, the focus baseline |
| `a.ghog.day.ok` | source snapshot of the last green walk; unchanged means the next walk is a noop |
| `a.ghog.outliers` | duration-outlier floor and accepted exclusions |
| `a.ghog.senv.log` | parked senv preamble of one call, replayed and deleted by the tool |

## 🚀 Version and release files

| File | Role |
| --- | --- |
| `version.txt` | first line `X.Y.Z-SNAPSHOT -- <title>`, then the release-notes summary |
| `CHANGELOG.md` | one section per release, folded in by `update-changelog.bat` |

Related: [Independent review mode contract](independent-review-mode-contract.md),
[Document templates](templates.md),
[ghog commands and exit codes](ghog-commands-and-exit-codes.md).
