---
name: group-commits-msg
description: 'Group files and write a conventional commit message for each group, when the user enters the prompt "group commits messages" or "group commit messages" or "group commits message".'
user-invocable: true
metadata:
  - "This skill is used to group files and write a conventional commit message for each group in `a.commit`."
  - "Use git diff --name-only --cached to get the list of staged files, and then group them based on their dependencies."
  - "Any .md files in your context, as well as previous prompts in your current conversation, can provide additional context for grouping files."
---

## Group commits messages

Your goal is to group the staged files, from least to most dependent, and for each group write a conventional commit message, saving all groups to a file named `a.commit` at the root of the project.

The context that can inform how you group those files includes:

- any `.md` files in your context, as well as previous prompts in your current conversation.
- `git diff --name-only --cached` to get the list of staged files and group them based on their dependencies.
- `git diff --cached` to see the recent changes made to those staged files.

## Workflow

1. Get the list of staged files:

  ```bat
  git diff --cached --name-only
  ```

2. Get the changes made on those files:

  ```bat
  git diff --cached
  ```

3. Group files based on their dependencies and the context you have (previous prompts, `.md` files in your context, and the changes done on those files).

4. For each group, write a conventional commit message. Each group must follow the template provided in [`TEMPLATE.md`](./TEMPLATE.md). The heading `# Grouping commits by topic` from the template must appear only once, for the first group.

5. Replace the content of `a.commit` with the generated groups and commit messages. Separate each group with an empty line.

6. Display `a.commit` for user review and ask if they want to edit it. If so, allow edits and save the final version.

7. When the user says "go ahead", validate `a.commit`. A git batch commit tool (if available in the project) can be used to validate and execute the commits. Check the project's `tools/` folder for such a script (e.g., `git_batch_commit.py` or similar). If no such tool exists, apply the commits manually using the `git add` and `git commit` commands listed in each group.

## Commit message rules

Each commit message must follow the template provided in [`TEMPLATE.md`](./TEMPLATE.md).

Be mindful of empty lines:

- Add an empty line between the title and the Why section.
- Add an empty line between `Why:` and its section.
- Add an empty line between the reason and the "now" state" within the `Why:` section.
- Add an empty line between the end of the `Why:` section and the `What:` section.
- Add an empty line between `What:` and its section.

Conventional commit titles must start with `<type>[optional scope]: description`, 52 characters max.
Types other than `fix:` and `feat:` are `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others.

- The title must not exceed 52 characters.
- Body and footer lines must not exceed 80 characters and must not be indented.

The body must include two sections, 'Why' and 'What':

- In the 'Why' section, include two parts separated by an empty line: the reason and the "now" state (see the template).
- In the 'What' section, list each modification as a dash-prefixed item.

Do not use words listed in #file:../../blacklist.md .
