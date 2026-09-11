# Expose commit-plan validation without committing

- Type: feature-request
- Version: v0.11.0
- Slug: `commit-plan-check`
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

## Boundary inherited from the review-mode umbrella

This effort exposes read-only validation of the root `a.commit` plan against
the exact staged file set. It belongs outside the reviewer role because it is
a reusable commit-plan tool, and outside batch execution because validation
must not depend on taking the committing path.

The effort depends on the completed `review-exchange-core` and `code-reviewer`
requirements. It must reuse the existing public `validate_commit_plan` API
rather than reproduce its grouping or diagnostic rules.

## Missing commit-plan validation entry point

The repository already validates commit plans during batch execution, but a
reviewer cannot invoke the same readiness floor directly without entering a
path associated with committing. The missing behavior is a launcher that
checks the current root plan and staged set while leaving repository state
unchanged.

### Root plan input for the validation command

The command reads the project-root `a.commit` and parses it with
`interactive=False`. It obtains the exact staged paths and passes the parsed
blocks and paths to `validate_commit_plan(blocks, staged_paths)`.

### Read-only repository contract for plan checking

The command must never reset, add, remove, or otherwise modify index entries.
It must not create a commit. Running it repeatedly against unchanged inputs
must leave both the index and working tree unchanged.

## Required validation report

The result must report the typed commit groups and every validation diagnostic
in a stable form that a reviewer can quote as readiness-floor evidence. A
failure must remain attributable to the affected group, staged path, or plan
rule instead of being reduced to an undifferentiated exit status.

### Typed group evidence in the report

Each parsed group must retain the group identity and commit-message type that
the public validator recognizes, together with its relationship to the exact
staged set.

### Diagnostic evidence in the report

Every validator diagnostic must be emitted without weakening or reinterpreting
the shared rules. The launcher is an adapter over the public API, not a second
validator with independent behavior.

## Entry-point decision to settle

The shipped entry point currently refuses `--root-a-commit` together with
`--dry-run`. The requirement and design must decide whether to add a focused
launcher or lift that restriction while preserving an unmistakably read-only
interface.

### Dedicated launcher option

A new launcher can expose only the validation operation and keep committing
flags out of its interface. This makes the no-mutation promise explicit but
adds another command users and documentation must discover.

### Existing launcher extension option

Lifting the current option restriction can reuse an established entry point.
The resulting contract must still make it impossible for the validation call
to fall through to index mutation or commit execution.

## Shared requestor and reviewer evidence

The requirement must decide whether `group-commits-msg` should call the same
read-only command before publishing a code-review request. If it does, the
requestor and reviewer will judge `a.commit` against the same staged set and
the same validator diagnostics.

### Pre-publication validation question

Calling the command before publication gives both roles identical evidence and
finds an invalid plan earlier. Keeping it reviewer-only avoids adding another
automatic step to grouping but permits requestor and reviewer readiness checks
to differ.

## Scope boundaries for commit-plan checking

- Do not reimplement `validate_commit_plan` rules in the launcher.
- Do not stage, unstage, reset, commit, or rewrite repository files.
- Do not move commit-plan validation into an assessment skill.
- Do not couple the read-only command to batch commit execution.
- Do not include active-review status or interrupted-review resumption, which
  remain separate umbrella topics.
