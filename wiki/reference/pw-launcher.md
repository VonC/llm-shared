# pw launcher

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🔁 The prompt-workflow launcher: `bin\prompt_workflow.bat`, wrapping
`tools\prompt_workflow.py`, aliased `pw` in an interactive `cmd`. It
answers one question — what is the next step of this effort? — in three
workflow modes, and also exposes one stateless document locator.

## Invocation model

Other skills normally let the AI call this launcher as an internal handoff.
Humans call it directly to use the interactive menu, debug dispatch, or resume a
specific known phase without restarting the parent workflow.

## 🧠 Shared core of every mode

All modes resolve the topic from the branch and the `docs\` tree (locked
per branch in `a.prompt_memory`), read the same workflow state (which of
draft, requirement, design, plan, validation exist; open questions or
settled decision table; which plan steps are done), and know the host:
`CLAUDECODE` emits `/skill`, while `CODEX_THREAD_ID` emits the installed
plugin form `$llm-shared:skill`.

The menu-less `pw skill` and `pw handoff` modes call one shared topic resolver.
Normal resolution uses relevant changed drafts and branch memory. If it finds
no topic, the shared resolver has a safe fallback for a requirement split from
an unchanged collection draft:

1. normalize only the branch leaf, treating `-` and `_` as equivalent,
2. require exactly one feature-request or issue filename with that version and
   normalized slug,
3. use exactly one direct same-version, same-slug draft when present,
4. otherwise require exactly one same-version draft marked
   `- Draft role: umbrella` whose canonical requirement table contains the
   complete normalized slug.

Missing and ambiguous relationships return no topic. A same-version draft that
does not mention the item is never borrowed as context, and the umbrella draft
is not renamed to the item slug.

A clean umbrella branch has no changed draft or item requirement to feed those
routes. In that case, bare `pw skill` matches the normalized branch leaf to
exactly one canonical umbrella carrying a nonempty collection table. It then
returns the first valid pending row through `process-draft ... based on
<slug>`. No match or more than one match remains not applicable rather than
selecting an unrelated umbrella.

When a caller already knows a version, slug, and document type, it does not
need branch state, a draft path, or `a.prompt_memory`. The stateless form
`pw document <version> <slug> <type>` searches the four supported directories
for that version and prints the unique repository-relative path.

The collection checkpoint uses the same canonical table more strictly.
`pw skill --after-merge <umbrella-draft>` reads rows in numeric order. A
`completed` row must name an existing requirement and a validation plan whose
first non-title line is exactly `Yes, it is implemented.`. A `pending` row with
complete validation evidence is stale and fails closed. The first valid pending
row starts or resumes its workflow; only an exhausted table emits
`prepare-release`.

## 🎛️ The three modes side by side

| Mode | Step chosen by | Emits | Channel |
| --- | --- | --- | --- |
| `pw` | a human, from a menu | a full next-step prompt | `a.prompt.txt` + clipboard + `a.prompt_memory` |
| `pw handoff <task> <x>` | the caller (the step is given) | a full, assembled cycle prompt | `a.prompt.txt` + clipboard + `a.prompt_memory` |
| `pw skill [name] [--after-write role] [--after-merge umbrella]` | disk state, forced name, writer event, or collection checkpoint | one bare command line | stdout |

## 🔎 Stateless document lookup

```text
pw document v10.0.0 route-cleanup design
```

The three selector values are sufficient. Supported types are `draft`,
`requirement`, `feature-request`, `issue`, `design`, `plan`, and
`validation-plan`. `requirement` resolves either a feature request or an issue.
Slug hyphens and underscores are equivalent.

The lookup checks `docs/`, `docs/vX.Y/`, `docs/vX.Y.Z/`, and
`docs/vX.Y/vX.Y.Z/` for the supplied full version. It prints nothing and exits
not-applicable when no document exists. Multiple exact matches are an error:
the caller must remove or relocate the duplicate instead of relying on folder
order.

## 🤝 pw handoff tasks

| Call | When | Prompt written |
| --- | --- | --- |
| `pw handoff check <x>` | after `/implement-step <x>` or `/implement-missing-step <x>` ends green | the `implementation-check.md` prompt for step `<x>` |
| `pw handoff after-check <x>` | after `/implementation-check <x>` records its verdict | routed: `implement-missing-step.md` on `No`, `group-commits-msg.md` (`git add -A` form) on `Yes` |

`after-check` is neutral on purpose: `pw` reads the `Analysis of Step x`
status line the check wrote, so the caller cannot pick the wrong branch.

## 🗂️ What pw skill derives from disk

| State on disk | Printed command |
| --- | --- |
| fresh draft, no requirement | `/process-draft on docs\draft...md` |
| doc still carrying `## Open questions` | `/consolidate-then-review-ask-questions on ...` |
| current doc fresh: no open questions, no consolidated decisions | `/review-ask-questions on ...` |
| settled requirement | `/write-design` |
| settled design | `/write-plans` |
| settled plan, uncommitted validation work | `/implement-step <x>` |
| settled plan, final step committed | `/prepare-release` |

"Settled" means consolidated, not merely titled: the document must carry a
decisions section (`Requirement clarifications`, `Design decisions`, or
`Implementation decisions`) holding at least one row opening with a question id
(`| Qxx`) or the "No open questions" row a no-question review writes. A
decisions heading alone does not count.

Bare `pw skill` treats a complete settled marker as state and advances. Writers
therefore do not use bare inference: `pw skill --after-write
requirement|design|plan` names the artifact just created and always prints its
`/review-ask-questions`, even if its text already resembles a settled document.
The `<x>` of `/implement-step` comes from the validation plan's own step list:
the last verified step, or the plan's first step when none is verified, which
is not always `1` (a plan may open on a step 0). Whether the settled-plan
command is run at once (the default) or shown and held (`stop here` in the
consolidation invocation, or an explicit human instruction) is decided by the
skill instructions, not by `pw`.

## 🚩 Flags and special forms

| Form | Effect |
| --- | --- |
| `pw skill --after-write requirement\|design\|plan` | reviews the named artifact just written, ignoring settled-looking markers; prints nothing and exits not-applicable when it is absent |
| `pw skill --after-commit <x>` | told the plan step the pending commit completes, prints the contextual next action (next `/implement-step`, `/prepare-release`, or nothing) — read-only, used to build the commit-gate labels |
| `pw skill --after-merge <umbrella-draft>` | verifies the ordered umbrella status table; emits `process-draft ... based on <slug>`, resumes an existing pending effort, or emits `prepare-release` only when all rows are complete |
| `pw skill --host claude\|codex` | forces the command prefix |
| `pw skill <skill-name>` | prints a specific earlier phase's command, to re-run it by hand |
| `pw document <version> <slug> <type>` | prints the unique document path without branch or memory resolution |
| `pw --pick` | reopens the topic menu when the branch lock is wrong |
| `--root`, `--debug` | shared flags of the underlying tool |

## 🚦 Exit and error behavior

Skill mode exits `3` with empty stdout when no topic or requested artifact is
applicable, so a caller cannot mistake an error note for a command. The tool
exits `2` on fatal errors (`EXIT_FATAL`). A launcher error naming `No python_3*
directory found in "\venvs"` means a stale copy of
`prompt_workflow.bat` outside the real checkout.

Related: [One launcher, three modes](../explanation/one-launcher-three-modes.md),
[Run pw from any shell](../how-to/run-pw-from-any-shell.md), and
[Artifact files and naming conventions](artifact-files.md).
