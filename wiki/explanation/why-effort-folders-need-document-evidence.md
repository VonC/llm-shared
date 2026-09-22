# Why effort folders need document evidence

<img src="../assets/logo-llm-shared-documents-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📝 An effort can keep its documents under `docs/vX.Y.Z/<slug>/`. That gives
each topic its own directory while its filenames continue to identify the
version, topic, and workflow phase. Discovery uses those identities to decide
which folders belong to the workflow.

## Invocation model

The human chooses an effort layout through the workflow prompts. The AI runs
the workflow launcher to discover the matching documents and continue the
selected effort; directory discovery has no separate manual invocation.

## What changed since Ruben's original PR

Ruben (`guenounrub`) proposed the fifth layout in
[PR #5, Fix doc layout](https://github.com/VonC/llm-shared/pull/5).
The comparison here uses his original two commits,
[05cded5](https://github.com/VonC/llm-shared/commit/05cded592e7371255cfe37a0c6ea7d267434c5e5)
and [2d687d4](https://github.com/VonC/llm-shared/commit/2d687d4f98657bacf6b6b48649ad0065c44f6f69),
against the completed `v0.12.0` documentation-layout hardening effort.

His contribution added `version-slug` to the layout choices, passed the slug
through draft creation and relocation, made both directory discovery routes
recognize `docs/vX.Y.Z/<slug>/`, and updated the layout menus and tests. It
closed a real gap: draft discovery could already find a nested draft, but
sibling-document discovery rejected its parent. These changes remain the
foundation of the fifth layout.

The `v0.11.0` integration completed CLI help, a draft-creation acceptance case,
rejected-directory test coverage, and writing instructions that still forbade
an effort subdirectory. The subsequent hardening defines how that layout
behaves when folders contain unrelated files or documents are spread across
layouts:

| Concern | At Ruben's original PR | After hardening |
| --- | --- | --- |
| Choosing the fifth layout | `version-slug` creates or relocates the draft into its slug folder. | Preserved; later documents still belong beside the canonical draft. |
| Recognizing a slug folder | A full-version parent and a lowercase slug-shaped directory name suffice, even when empty. | At least one immediate supported document must match the enclosing version and folder slug. |
| Missing workflow sibling | A recognized canonical parent limits the search to that directory, even when the requested role is absent. | Local matches still take precedence; a missing role can use exactly one match from other recognized directories. Multiple fallback matches are an error. |
| Unrecognized canonical parent | Selection broadens to recognized directories and can choose the newest match. | Selection reports the invalid parent before attempting a fallback. |
| Exact document lookup | `pw document` requires a unique exact type/version/slug match. | Preserved and explicitly tested against parent/child duplicates; workflow preference does not apply to this command. |
| Discovery implementation | Lookup lives in the docs module and borrows the collection-row slug pattern. | A dedicated lookup module owns directory syntax, with compatible exports through the existing docs module. |
| Verification | Layout paths, the missing-slug error, directory discovery, and exact lookup have unit cases. | Additional tests cover filename eligibility, file changes between calls, fallback cardinality, and real Git/CLI routing, including post-commit topics without a draft. |

The four earlier layouts remain supported, including empty directories. The
optional slug argument remains compatible with those layouts; `version-slug`
still rejects a missing slug. Existing newest-file selection among matches
inside the canonical parent is preserved. No migration is needed for an effort
already containing correctly named documents.

## Why the directory name alone is insufficient

Consider `docs/v1.2.3/my-effort/`. In the original PR, its name alone made it
discoverable. After hardening, an immediate
`issue.v1.2.3.my_effort.md` is enough to qualify it, even without a draft.
Hyphens and underscores represent the same slug. An assets-only folder, a
review transcript, or a document for a different version or topic provides no
such evidence. A qualifying file nested another directory below it does not
establish the identity of its parent.

This also avoids a list of forbidden names: an effort actually named `images`
qualifies when it contains `issue.v1.2.3.images.md`. The filename establishes
the relationship. Requiring a draft specifically would exclude legitimate
later workflow states, so a requirement, design, ordinary plan, or validation
plan can establish that same relationship.

Discovery checks current filenames and file types on every call. Adding,
renaming, or removing the last qualifying document takes effect on the next
call in the same process. Eligibility needs no document-body parsing or cache;
workflow-state parsing remains a separate responsibility.

## Why lookup and workflow selection have different answers

Suppose the canonical draft is
`docs/v1.2.3/my-effort/draft.v1.2.3.my_effort.md`, with matching plans both
beside it and in `docs/v1.2.3/`. Workflow selection uses the local plan even
if the other copy is newer, because the draft identifies the effort's chosen
directory. That preference existed before hardening.

If the local plan is removed, selection now uses the sole matching plan in
the version directory. If another matching plan also exists in `docs/`, it
reports both fallback paths as ambiguous. Before hardening, the recognized
canonical directory prevented either fallback from being considered.

By contrast, `pw document v1.2.3 my-effort plan` has no canonical draft context:
two exact copies are ambiguous wherever they live. A timestamp cannot tell
this caller which copy was intended. The two routes deliberately answer
different questions, and their shared discovery rules keep that distinction
consistent across all five layouts.

Post-commit routing applies the same selection rules from a validation plan's
directory, even when no draft file remains. A local or unique fallback ordinary
plan lets that topic participate; an absent plan skips it, while competing
fallback plans stop routing with an error. This prevents a commit continuation
from silently choosing between copies.

## Evidence and related documentation

The [hardening validation plan](../../docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md)
records all four completed steps, maps the sixteen acceptance requirements to
tests, and records the full-suite 100% coverage result. The
[lookup implementation](../../tools/prompt_workflow_document_lookup.py) and
[CLI acceptance cases](../../tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py)
provide the corresponding code evidence.

- [From draft note to settled requirement](../tutorials/02-from-draft-to-settled-requirement.md)
  demonstrates choosing an effort directory.
- [Find a document without knowing its folder](../how-to/run-pw-from-any-shell.md#-find-a-document-without-knowing-its-folder)
  gives the launcher invocation and recovery steps.
- [Artifact files and naming conventions](../reference/artifact-files.md#effort-directory-recognition)
  specifies which files qualify a slug directory.
- [Workflow document selection](../reference/pw-launcher.md#workflow-document-selection)
  specifies local preference, fallback, and errors.
