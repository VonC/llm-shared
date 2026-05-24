# Group commits message

Your goal is to group files listed in the prompt, from least to most dependent and, for each group, to write a conventional commit message, all in a file named `a.commit` at the root of the project.

The context that can inform how you will group those files can be:

- any `.md` files in your context, as well as previous prompts in your current conversation, can provide additional context for grouping files.
- `git diff --name-only --cached` to get the list of staged files, and then group them based on their dependencies.
- `git diff --cached` to get the recent evolutions done for those files listed in the prompt.

## Workflow for grouping commits

1. Get the list of files to group.

   Execute the following sequence of bat commands:

   ```bat
   cd "%PRJ_DIR%"
   git diff --cached --name-only
   ```

2. Get the changes done on those files.

   Execute the following sequence of bat commands:

   ```bat
   cd "%PRJ_DIR%"
   git diff --cached
   ```

3. Group files based on their dependencies and the context you have (previous prompts, `.md` files in your context, and the changes done on those files).

4. For each group, write a conventional commit message. Each group must follow the template provided in [`group-commits-msg.template.md`](../templates/group-commits-msg.template.md). See the next section for more details on how to write the commit message. The title `# Grouping commits by topic` from the template must be added only once, for the first group, and not for the following groups.

5. Replace the content of `a.commit` with the generated groups and commit messages. Each group must be separated by an empty line in `a.commit`.

6. Format `a.commit` with the `wrap_commit` tool so each ```log block fits within 80 characters and follows the inline-backtick rules. This keeps the file canonically formatted before the user reviews it.

   Execute the following sequence of bat commands (default parameters: 80-character width, ```log fence delimiters, backtick pass on):

   ```bat
   cd "%PRJ_DIR%"
   python "%LLM_SHARED_DIR%\tools\wrap_commit.py"
   ```

   The tool rewrites `a.commit` in place. An exit status of 0 means the file is now canonically formatted (whether or not changes were applied); a non-zero status means the file is missing or unreadable and the underlying issue must be fixed before proceeding.

7. Once `a.commit` is generated and formatted, display it for user review, and ask the user if they want to edit it. If the user wants to edit it, allow them to edit it, and then save the final version of the groups and commit messages in `a.commit`.

8. When the user says "go ahead", validate the `a.commit` file, and if it is not valid, fix any issue reported by the validation.

   To validate the `a.commit` file, you can use the following sequence of bat commands:

   ```bat
   cd "%PRJ_DIR%"
   python "%LLM_SHARED_DIR%\tools\git_batch_commit.py" --root-a-commit
   ```

   An exit status of 0 means the `a.commit` file is valid, while a non-zero exit status means there is an issue with the `a.commit` file that needs to be fixed.

   If the file is valid, there is nothing more to do: `git_batch_commit.py` will have proceeded automatically to create one commit per group, with the corresponding commit message.

## Commit message rules for groups

Each commit message must follow the template provided in [`group-commits-msg.template.md`](../templates/group-commits-msg.template.md).

Be mindful of empty lines mentioned in the template:

- Add an empty line between the title and the Why section.
- Add an empty line between `Why:` and its section.
- Add an empty line between the reason and the "now" state within the `Why:` section.
- Add an empty line between the end of the `Why:` section and the `What:` section.
- Add an empty line between `What:` and its section.

Reminder, conventional commit means, the title must start with `<type>[optional scope]: description`, with 52 characters max.
Types other than `fix:` and `feat:` are `build:`, `chore:`, `ci:`, `docs:`, `style:`, `refactor:`, `perf:`, `test:`, and others.

- The title must not exceed 52 characters.
- The body and footer lines must not exceed 80 characters, and must not be indented, no prefix spaces.
  Make sure each line in the body and footer is wrapped at 80 characters or less, which means it must go up to 80 characters and then break to the next line without indentation.

Make sure the body includes two sections, 'Why' and 'What':

- in the 'Why' section, you must have two parts separated by an empty line: read the template for guidance.
- in the 'What' section, make a list of modifications, each line starting with a dash: read the template for guidance.

Do not use words listed in the "Blacklist of words to avoid in the response" of [`blacklist.md`](../rules/blacklist.md). The same applies for the What section.
