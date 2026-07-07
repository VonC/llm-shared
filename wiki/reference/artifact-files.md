# Artifact files and naming conventions

<img src="../assets/logo-llm-shared-documents-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

📝 Every file the workflow reads or writes, split between the versioned
documents under `docs\` and the transient `a.*` files at the project root.

## 📚 Versioned documents under docs

One effort, one version slug `vX.Y.Z`, one topic slug — every phase adds
its file:

| Pattern | Written by | Holds |
| --- | --- | --- |
| `docs\draft.<topic>.md` | the author | the raw idea, no version yet |
| `docs\draft.vX.Y.Z.<slug>.md` | `/process-draft` | the classified, branched draft |
| `docs\feature-request.vX.Y.Z.<topic>.md` | `/write-requirement` | new behavior to build |
| `docs\issue.vX.Y.Z.<topic>.md` | `/write-requirement` | a bug or missing behavior |
| `docs\design.vX.Y.Z.<topic>.md` | `/write-design` | scope, constraints, acceptance cases |
| `docs\plan.vX.Y.Z.<topic>.md` | `/write-plans` | numbered implementation steps |
| `docs\plan.vX.Y.Z.<topic>.validation.md` | `/write-plans`, then `/implementation-check` | per-step verdicts and checks |

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

Related: [Document templates](templates.md),
[ghog commands and exit codes](ghog-commands-and-exit-codes.md).
