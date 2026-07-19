# Commit message format

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📊 The commit format used across the workflow: Conventional Commits
v1.0.0 for the title, plus a fixed `Why:` / `What:` body defined by
the [grouped-commit template](templates.md#group-commits-msgtemplatemd).

## Invocation model

The grouped-commit workflow normally asks the AI to propose these messages and
the human approves the grouping and wording. Writing one directly is fully
supported for an isolated commit or when tailoring a proposal before commit.

## ✉️ Shape of one message

```txt
type(scope): subject

Why:

A detailed reason for the change...

A detailed description of the "now" state...

What:

- list of changes...
```

## 🔤 Title line rules

- 52 characters maximum, including type, optional scope, colon and space.
- `type` is one of `feat`, `fix`, `docs`, `chore`, `refactor`, `test`,
  `build`, `ci`, `perf`, `style`, or any project-declared type.
- `(scope)` is optional; the subject is short and imperative.

## 📄 Body rules

- Wrapped at 80 characters, never indented.
- `Why:` holds two paragraphs separated by an empty line: first the
  reason (what was broken, missing or unclear), then the "now" state (how
  the code is better once the commit lands).
- `What:` is a dash-prefixed list, one line per actual modification.
- The words described in the [blacklist reference](writing-rules.md#blacklistmd)
  are forbidden.

## 🗂️ The a.commit file format

`a.commit` stacks several such messages, one per dependency group:

````txt
# Grouping commits by topic

## Group 1: [topic]

git add -A path\to\file1 path\to\file2

```log
type(topic): subject

Why:
...
```
````

Groups are ordered least dependent first; a trailing docs group
(`docs(<topic>): record step <n> completion`) goes last. `wac.bat`
formats the file; `gcba` validates it and replays it as real commits. For
a merge reword, `a.commit` holds a single message with no group header
and no `git add` line.

Related: [Group a dirty tree into conventional commits](../how-to/group-commits-into-conventional-messages.md),
[Why grouped commits, least dependent first](../explanation/why-grouped-commits.md).
