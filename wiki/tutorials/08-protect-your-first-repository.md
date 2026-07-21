# Protect your first repository from sensitive commits

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Keep the repository to protect as the current workspace and ask the agent to
invoke `install-sensitive-git-hooks`. You run the harmless demonstration
commits yourself so you can observe both rejection paths.

📊 In this tutorial you install the sensitive commit hooks in one repository,
observe an idempotent second installation, and see a staged blob and a commit
message blocked. Use only the neutral demonstration term shown below.

## 1. Prepare a local rule

Open the repository you want to protect and make sure its local artifacts are
ignored:

```sh
git check-ignore -v --no-index -- a.sensitive.replacements.local.txt
```

Create `a.sensitive.replacements.local.txt` with this one demonstration rule:

```text
literal:DEMO_PRIVATE_TOKEN==>public-token
```

Do not stage this file. A real rules file contains the confidential terms it is
designed to catch.

## 2. Invoke the installation skill

With the repository to protect as the current workspace, and `llm-shared`
available as that repository, a sibling checkout, or a submodule, ask:

```text
install sensitive Git hooks in this repository
```

The `install-sensitive-git-hooks` skill resolves the current Git root, finds
`llm-shared`, selects its virtualenv Python, and runs the shared installer.
The target repository does not need Python.

The report should say **Installed**. Run the same request again. This time it
should say **Already installed** and make no file changes.

## 3. Observe a staged-blob rejection

Create `hook-demo.txt`:

```text
This contains DEMO_PRIVATE_TOKEN for the tutorial.
```

Stage it and attempt a neutral commit:

```sh
git add hook-demo.txt
git commit -m "test: demonstrate sensitive blob protection"
```

The commit is rejected. The error names `hook-demo.txt` and its line number
but does not echo the protected term.

Replace the file contents with neutral text and stage it again.

## 4. Observe a message rejection

Attempt a commit whose message contains the demonstration term:

```sh
git commit -m "test: mention DEMO_PRIVATE_TOKEN"
```

This time `pre-commit` accepts the safe staged blob and `commit-msg` rejects
the pending message. The error reports the message line without reproducing
the matched text.

Commit with a neutral message to complete the experiment.

## 5. Remove the demonstration rule

Remove `hook-demo.txt` if the tutorial commit is not useful. Replace the
demonstration rule with the real shared and project-specific rules appropriate
to the repository. Keep every rules file ignored and untracked.

## What you learned

The installation is idempotent, the target uses `llm-shared`'s interpreter,
and the two hooks protect different parts of one pending commit without
scanning history.

Next: [Install or verify sensitive hooks](../how-to/install-sensitive-commit-hooks.md),
[replacement-rules format](../reference/sensitive-replacement-rules.md), and
[hook contract](../reference/sensitive-commit-hooks.md).
