# How to reword a merge commit from the branch docs

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📊 Goal: replace the default `Merge branch '<slug>'` message of a merge
commit with a conventional message built from the documents the merged
branch carried.

## Invocation model

The integration and release workflows ask the AI to update the merge message
after a successful no-fast-forward merge back into any target branch,
including an umbrella integration branch, `develop`, or `main`.
Use this procedure directly only to repair the current merge commit or to
review the exact mechanics before approving the automated step.

## 📋 Steps from merge to reworded message

1. Create the merge from the up-to-date target selected by the workflow:

   ```cmd
   git switch <target-branch>
   git pull
   git merge --no-ff <your-branch>
   ```

2. Run the skill:

   ```txt
   /update-merge-commit-msg
   ```

3. It calls `git-extract-merge-docs.sh`, which walks the merged branch's
   lineage, finds the `docs/*.md` files changed between the two parents,
   and dumps their content into `a.docs`.

4. From `a.docs`, the skill writes one single-group conventional message
   into `a.commit` — title, `Why:` paragraphs, `What:` list — formatted by
   `wac.bat --no-delimiters`. A free-form message is refused.

5. Review the message, then say `Go ahead`. The skill runs
   `git-reword-merge.sh` (the `grmc` alias), which rebuilds the merge
   object with `git commit-tree <tree> -p P1 -p P2 -F a.commit`, moves the
   branch ref, and empties `a.commit`. `commit-tree` ignores
   `commit.gpgsign`, so the script adds `-S` when that setting is true: the
   reworded merge stays signed like the one it replaces.

6. Let the owning workflow require a clean tree and push the current branch
   before its next-step handoff. A standalone invocation performs that gate
   itself. With `origin` configured, it uses an explicit branch-only refspec
   and disables automatic tag following:

   ```cmd
   git -c push.followTags=false push origin HEAD:refs/heads/<target-branch>
   ```

   Every configured push destination must succeed. Never push the default
   merge message between the merge and the reword.

## 🚀 Inside a release preparation

When `/prepare-release` drives the merge, it signals the skill through the
flag file `a.prepare-release.active` in the review artifact home
(`.reviews`): the reword then hands
control back to the release run instead of closing on its own.

## ✅ Check after the reword

`git log -1` on the target branch shows a `type(scope): subject` title tied
to the merged effort, with the `Why:` / `What:` body — the message changelog
generators and future readers will see.

Related: [Commit message format](../reference/commit-message-format.md),
[Prepare a release from any branch](prepare-a-release.md).
