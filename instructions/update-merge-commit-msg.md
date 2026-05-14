# Update merge commit message

When you merge a branch, the default commit message is not very informative. You can use this skill to update the merge commit message with a conventional commit message based on docs found in the merged branch.

Your goal is to write an `a.commit` with a conventional commit message explaining what is merged (why and what).

For that, call the helper script [`git-extract-merge-docs.sh`](../scripts/update-merge-commit-msg/git-extract-merge-docs.sh) shipped under `scripts/update-merge-commit-msg/`:

```bash
bash -c "%LLM_SHARED_DIR_UNIX%/scripts/update-merge-commit-msg/git-extract-merge-docs.sh"
```

No parameter is needed, can be called from anywhere, but you need to resolve the full path of the script.

A companion script [`git-reword-merge.sh`](../scripts/update-merge-commit-msg/git-reword-merge.sh) in the same folder rewrites the current merge commit with the contents of `a.commit` once the message is final.

If the script is successful, it creates `a.docs` with the extracted docs from the merged branch: analyse its content to write the `a.commit` message with a conventional commit message following the "Commit message rules for groups" section of [`group-commits-msg.md`](group-commits-msg.md) and the template in [`group-commits-msg.template.md`](../templates/group-commits-msg.template.md).  
There is only one group, so do not put "Group 1" or `git add -A` commands, only the commit message template filled with the right content.

Once `a.commit` is written, display it for user review, and ask the user if they want to edit it.
