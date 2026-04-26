---
name: update-merge-commit-msg
description: 'Update the merge commit message with a conventional commit message based on docs found in the merged branch.'
user-invocable: true
metadata: 
  - "This skill is used to update the merge commit message with a conventional commit message based on docs found in the merged branch."
---

## Update merge commit message

When you merge a branch, the default commit message is not very informative. You can use this skill to update the merge commit message with a conventional commit message based on docs found in the merged branch.

Your goal is to write a a.commit with a conventional commit message explaining what is merged (why and what)

For that, call #file:./git-extract-merge-docs.sh making sure to use bash -c "C:\path\to\git-extract-merge-docs.sh". No parameter is needed, can be called from anywhere, but you need to resolve the full path of the script.

If the script is successful, it creates `a.docs` with the extracted docs from the merged branch: analyse its content to write the `a.commit` message with a conventional commit message following the "Commit message" section of #file:../group-commits-msg/SKILL.md and the template in #file:../group-commits-msg/TEMPLATE.md file.  
There is only one group, so do not put "Group 1" or `git add -A` commands, only the commit message template filled with the right content.

Once a.commit is written, display it for user review, and ask the user if they want to edit it.
