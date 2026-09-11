# Request implementation code reviews

- Type: feature-request
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md

## Need

Update the existing `implement-step` skill in `instructions/implement-step.md` to trigger the review-request workflow immediately after the `group-commits-msg` skill call, where the workflow currently stops for human review.

The implementation writer owns its staged changes, end-of-step report, `a.commit`, and decision after review. The exchange lifecycle remains shared with the review-exchange core, and the code reviewer remains a separate role.

## Review workflow integration

When the project-root `a.review-mode` file exists, the LLM must use `pw` (`prompt-workflow`) and must not stop for the user's review of the grouped commit message in `a.commit`.

Instead, it must:

- Create or reuse `review.code.vX.Y.Z.slug.md` beside the implementation plan. Initialize it from the review-type and version template when it does not exist. This transcript is versioned alongside `plan.vX.Y.Z.slug.md`, is append-only for agents, and is not reread as working context.
- Delete a stale project-root `a.review-answer.code.vX.Y.Z.slug.md` when one exists.
- Create or overwrite project-root `a.review-requested.code.vX.Y.Z.slug.md` with the mandatory identity-bearing summary and the end-of-step implementation report.
- Append the requestor's general feedback to the sibling `review.code.vX.Y.Z.slug.md` transcript.
- Wait for project-root `a.review-answer.code.vX.Y.Z.slug.md`, then read the answer, inspect the staged changes and `a.commit`, and distinguish an intermediate rework request from a commit-readiness recommendation.

Every review request summary must identify its context in human-readable form. It names the umbrella draft when one exists, or states `Umbrella draft: none`; it also names the exact implementation plan, implementation step, and round. These fields must agree with the machine-readable exchange identity.

The request must direct the reviewer to use `implementation-check`, inspect the staged changes, avoid committing, repair missing work, amend `a.commit` when needed, and either request rework or recommend commit-readiness. Its conclusion must carry the meaning of:

> Step x of `docs\plan.v10.0.0.root-routing.md` has been implemented: look at the staged changes and see, following `$llm-shared:implementation-check`, if that is the case. `a.commit` is ready for commit, but do not commit anything yet. Review and fix what might be missing, amending `a.commit` accordingly if fixes are needed. Then summarize your fixes, if any, and write a `review-answer.code.vX.Y.Z.slug.md` file with feedback for the writer to review your changes.

## Automated rounds and human confirmation

Ordinary review rounds remain automated. For an intermediate round, the requestor applies or assesses the reviewer changes, makes any additional changes, deletes the consumed answer, and creates a replacement request with the updated identity-bearing summary. The dialogue continues without waiting for a human.

When the reviewer recommends commit-readiness, the recommendation is advisory and never authorizes a commit. The requestor retains the answer as decision evidence, enters `awaiting-human-confirmation`, and presents the human with:

- the umbrella identity or `none`;
- the exact plan, implementation step, and round;
- the reviewer recommendation;
- the staged changes and `a.commit`;
- the requestor's assessment.

Only the human may choose `Commit` or `Rework and review again`. `Commit` explicitly authorizes the owning workflow to run its existing commit step. `Rework and review again` records the override and any human guidance, resets the no-progress counters, and starts another automated round. Delete the answer only after the confirmed action is applied.

`awaiting-human-confirmation` is distinct from the `escalated` state used for timeout, abandonment, no-progress, disagreement, and inconsistent artifacts. Review waits must terminate or escalate when they are not completed in time or when the two roles disagree. The consolidated no-progress and disagreement rules bound the automated dialogue and define when to stop for human intervention.

## Existing-skill boundary

The `implement-step` instruction must reference the complementary review-requestor role rather than duplicate its process. That reference must make the LLM aware that review mode changes the normal stopping point and that requestor feedback is appended to the versioned review transcript.

The review-requestor process, template, script, and supporting utilities remain defined in their own shared role or skill. LLM-specific Markdown wrappers remain thin adapters that point directly to the canonical root instruction.

## Dependency

This feature depends on `review-exchange-core`.

## File-based IO cost clarification

- Resolve the exact plan, step, and exchange paths once at the post-grouping boundary.
- Use only ignored root input files and the shared exchange's constant exact-path operations during review rounds.
- Never scan documentation directories or reread the versioned transcript as working context.
