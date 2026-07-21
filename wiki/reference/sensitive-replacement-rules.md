# Sensitive replacement-rules format

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

The install and sanitization skills validate this format automatically.
Humans may edit an ignored rules file directly, but should inspect rule order
and replacements before authorizing a history rewrite.

`a.sensitive.replacements.local.txt` is a UTF-8, Git-ignored list compatible
with `git filter-repo --replace-text`. The sensitive-history scanner and
commit hooks use each rule's left-hand side as a case-insensitive watch
pattern. The right-hand side is the replacement used during a history rewrite.

## File grammar

The file contains zero or more rules, one per physical line:

```text
SOURCE==>REPLACEMENT
```

A project-local file may be zero bytes when a configured shared file supplies
the effective rules. A non-empty file has these constraints:

- no blank lines;
- no comment lines;
- no byte-order mark;
- no `glob:` rules;
- most-specific rules before broader rules.

The parser splits on the first `==>`. Always include the delimiter and a
deliberate replacement. Although `git filter-repo` accepts a source without
`==>` and replaces it with `***REMOVED***`, that shorthand is too easy to
trigger accidentally.

## Source forms

| Form | Watch behavior | Example |
| --- | --- | --- |
| `literal:TEXT` | Treat every source character literally | `literal:example.internal==>public.example` |
| `regex:EXPRESSION` | Compile the source as a regular expression | `regex:(?i)example[._-]internal==>public-name` |
| bare `TEXT` | Treat the source as a literal | `Example Organization==>Public Organization` |
| `glob:PATTERN` | Rejected | not supported |

Matching by llm-shared is Unicode-aware and case-insensitive for every form.
An initial `(?i)` is accepted and removed before compilation because the
scanner already applies case-insensitive matching. Keep `(?i)` in regex rules
when the later `git filter-repo` rewrite must also ignore case.

Use `literal:` when punctuation has no regex meaning. Use `regex:` only to
cover intentional variants. Invalid regular expressions fail the scan or hook
with status 2.

## Ordering

Ordering does not change whether the hook finds a term, but it matters during a
rewrite. Put syntax-specific replacements before broad prose replacements:

```text
regex:(?i)_exampleproject_==>_public_project_
regex:(?i)exampleproject==>public-project
```

The first rule keeps identifiers valid; the second handles prose and paths.

## Shared and project-local files

The configured shared file is read first:

```sh
git config --path --get sensitive.sharedRulesFile
```

The project file is then read from:

```text
<TARGET_REPO>/a.sensitive.replacements.local.txt
```

Equivalent compiled expressions are deduplicated case-insensitively, keeping
the first occurrence. Therefore a shared rule wins over an equivalent local
rule. Keep only genuinely project-specific terms locally.

A conventional Windows layout is:

```text
%PROG%\git\a.sensitive.replacements.local.txt  shared rules
%PROG%\git\llm-shared\                        shared implementation
%PROG%\git\my-project\a.sensitive.replacements.local.txt
```

The installer stores the shared path in the target repository's local
`.git/config` as `sensitive.sharedRulesFile`; the path is not committed.

## Confidentiality requirements

The rules contain the terms being protected:

- ignore every shared and local rules file;
- never stage or commit them;
- do not print their contents in installation reports;
- report counts and locations only;
- keep generated scan reports ignored too.

Confirm the project file with:

```sh
git check-ignore -v --no-index -- a.sensitive.replacements.local.txt
```

## Relationship to explicit scanner inputs

With no explicit terms, terms file, or `--rules`, the history scanner merges
the configured shared file first and the project-local file second. “Global”
describes the file's intended reuse; the scanner finds it through the current
repository's `sensitive.sharedRulesFile` Git configuration.

An explicit `--rules PATH` uses only that named file and disables the default
shared-plus-local selection. Positional terms and `--terms-file` are separate
input forms; terms files allow blank lines and `#` comments because they are
not `git filter-repo` rule files.

Related: [Scanner reference](sensitive-history-scan.md),
[hook reference](sensitive-commit-hooks.md), and
[sanitization guide](../how-to/sanitize-history-before-publishing.md).
