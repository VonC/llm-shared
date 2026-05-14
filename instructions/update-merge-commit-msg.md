# Update merge commit message

When you merge a branch, the default commit message is not very informative. You can use this skill to update the merge commit message with a conventional commit message based on docs found in the merged branch.

Your goal is to write an `a.commit` with a conventional commit message explaining what is merged (why and what).

For that, call the helper script `git-extract-merge-docs.sh` shipped with the skill. Use the path that matches the SKILL.md that referenced this instruction:

- Copilot setup: `bash -c "%COPILOT_SHARED_DIR_UNIX%/.github/skills/update-merge-commit-msg/git-extract-merge-docs.sh"`.
- Claude Code setup: `bash -c "%COPILOT_SHARED_DIR_UNIX%/.claude/skills/update-merge-commit-msg/git-extract-merge-docs.sh"`.

No parameter is needed, can be called from anywhere, but you need to resolve the full path of the script.

If the script is successful, it creates `a.docs` with the extracted docs from the merged branch: analyse its content to write the `a.commit` message with a conventional commit message following the "Commit message rules for groups" section of [`group-commits-msg.md`](group-commits-msg.md) and the template in [`group-commits-msg.template.md`](../templates/group-commits-msg.template.md).  
There is only one group, so do not put "Group 1" or `git add -A` commands, only the commit message template filled with the right content.

Once `a.commit` is written, display it for user review, and ask the user if they want to edit it.
