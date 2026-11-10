# Push to origin before a next-step handoff

After a successful commit, completed commit batch, merge-message rewrite, or
authorized action following review convergence, require a clean working tree
and push the current branch's committed tip to `origin` before displaying or
executing the next workflow step. This includes a final `pw progress` report
and a handoff that stops for the human to launch the next command. An explicit
user instruction to defer or omit the push takes precedence.

## Final cleanup before the push

Apply this gate to both post-commit and post-convergence handoffs, after the
owning workflow's authorized commits and residual cleanup have succeeded.
Run `git status --porcelain --untracked-files=all` and check its exit status.
A failed status command blocks the handoff; it is not an empty working tree.

When the successful status command lists any remaining non-ignored change,
run repository-wide `git add -A`, then follow
[`group-commits-msg.md`](../instructions/group-commits-msg.md) for every staged
path, including changes of outside origin. Generate and validate the root
`a.commit`, settle Markdown and spelling checks, and obtain that workflow's
normal human go-ahead unless an existing authorization explicitly covers this
cleanup batch. Convergence alone never authorizes a commit. Do not bypass the
canonical batch tool, omit a path, or discard work to make the tree clean.

The cleanup invocation returns here after its batch, without recursively
starting another cleanup or pushing. Run
`git status --porcelain --untracked-files=all` again immediately before the
push gate below; it must succeed and print nothing. If changes remain after
this final cleanup pass, stop and report them. Do not push, display the normal
next step, or start another cleanup loop. Repair requires returning to the
owning workflow. This clean-tree requirement also applies without `origin`.

## Push gate at the workflow boundary

1. Finish required validation and any merge message rewrite, then pass the
   final cleanup gate above. A nested skill that returns to its caller without
   displaying a next step leaves these gates to that caller.
2. Run `git remote` in the repository being handed off and check its exit
   status. When the successful listing contains no exact `origin` entry,
   report that no origin is configured and continue without a push. A failed
   remote lookup is an error, not evidence that origin is absent.
3. When `origin` exists, resolve the current branch with
   `git symbolic-ref --quiet --short HEAD`. A failure or detached HEAD blocks
   the handoff; do not guess a destination branch.
4. Substitute that branch name for `<branch>` and run:

   ```text
   git -c push.followTags=false push origin "HEAD:refs/heads/<branch>"
   ```

   The explicit refspec works without an existing upstream and limits the
   push to the current branch. Honor all configured origin push URLs; success
   requires the push to succeed for every configured destination.
5. Only after a successful push, display or run the next step as the owning
   instruction permits. Report the branch pushed, or that it was already up
   to date. If another commit or working-tree change appears before the
   handoff, return to the owning workflow's cleanup and push gates before
   continuing.

## Push failure and existing workflow authority

On a failed or rejected push, report the diagnostic and stop before the normal
next-step report or execution. Keep completed local commits and review state
available for recovery. When only some push destinations succeeded, report
that partial result. Do not automatically force-push, rebase, reset, or change
remote configuration to make the push pass.

The requestor owns the cleanup and push at a completed review handoff; a
reviewer still publishes its answer and waits under the role-isolation rule.

Read-only status requests, intermediate review waits, convergence approval
choices, and pre-commit `pw skill --after-commit` lookups used to build approval
labels do not trigger these gates. Present the required approval before
committing; clean and push at the actual post-commit or post-convergence
next-phase handoff instead.
