# Sensitive-history scanner command

<img src="../assets/logo-llm-shared-trail-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

`sensitive_history_scan.bat` is a read-only, case-insensitive scanner for all
Git objects reachable from local branches and tags. The interactive Doskey
alias is `shscan`.

Normal phase-1 sanitization does not require a manual command. Invoke
`$llm-shared:sanitize-git-history`; the skill locates and runs the launcher.

## Invocation model

The sanitize-history skill normally calls this scanner before and after the
rewrite and interprets its report for the user. Invoke it directly for a
read-only audit, to refine the watch list, or while developing scanner behavior;
direct use does not authorize or perform a history rewrite.

## Source layout

```text
bin/sensitive_history_scan.bat
tools/sensitive_history/
├── __init__.py
├── history_scan.py
└── sensitive_history_scan.py
tests/unit/tools/sensitive_history/
```

## Input forms

```bat
shscan secretproject internal.example
shscan --terms-file a.sensitive.terms.local.txt
shscan --rules a.sensitive.replacements.local.txt
```

Positional terms and terms-file entries are literals. A terms file allows blank
lines and lines beginning with `#`. A replacement file uses each left-hand
side as a watch pattern: bare and `literal:` rules are literals; `regex:` rules
retain regex semantics. `glob:` rules are rejected. Equivalent patterns from
several inputs are scanned once.

### Example terms file

`--terms-file` expects one case-insensitive literal per line. Blank lines and
comment lines are allowed, so a neutral `a.sensitive.terms.local.txt` can
contain:

```text
# Demonstration literals only
example-project-name
example.internal
Example Organization
```

Run it with:

```bat
shscan --terms-file a.sensitive.terms.local.txt
```

### Example replacement-rules file

`--rules` accepts the replacement syntax used later by `git filter-repo`. The
scanner searches only the left-hand side; the right-hand side documents the
intended public replacement. Unlike a terms file, a rules file must not contain
blank or comment lines. A neutral `a.sensitive.replacements.example.txt` can
contain:

```text
literal:example-project-name==>public-project
regex:(?i)example[._-]internal==>public-name
Example Organization==>Public Organization
```

Run it with:

```bat
shscan --rules a.sensitive.replacements.example.txt
```

Use a literal rule when punctuation must have no regex meaning. Use `regex:`
only when several spellings intentionally belong to one rule. A bare rule is
also literal.

Every input is matched case-insensitively. An initial `(?i)` on a regex rule is
accepted but not required by the scanner; it remains important to
`git filter-repo` during the later rewrite.

With no explicit input, the command uses
`a.sensitive.replacements.local.txt` at the repository root when present.

## Options

| Option | Meaning |
| --- | --- |
| `--root PATH` | Repository to scan; defaults to the current directory |
| `--terms-file PATH` | Read one literal term per line |
| `--rules PATH` | Read `git filter-repo` replacement rules |
| `--output PATH` | Write the report; an in-repository path must be Git-ignored |
| `--json` | Emit structured JSON instead of Markdown |
| `--max-line-chars N` | Limit long lines to a centered excerpt; default 500, minimum 40 |
| `--full-lines` | Keep complete text lines regardless of length |
| `--validation-term TERM` | Fail unless a known term occurs in a historical blob |
| `--fail-on-match` | Return status 1 when any requested pattern matches |

## Report fields

The summary gives matching commit lines, tag lines, historical object/path
pairs, blob lines, and unique matching blobs per pattern. Exact-casing counts
show the spelling actually present.

Each detailed match includes the term label, source kind, object ID, tag name
when applicable, representative historical paths, one-based line number,
matching line or centered excerpt, exact forms, and binary/truncation flags.
JSON exposes the same data without Markdown rendering.

Markdown output starts with `<!-- markdownlint-disable-file -->`, the
file-wide directive documented by
[markdownlint](https://github.com/DavidAnson/markdownlint#configuration).
Context lines intentionally contain arbitrary historical text and are not
reformatted to satisfy documentation style rules.

`git rev-list --all --objects` supplies representative paths for unique
objects. One filename can therefore appear more than once when different
historical blob versions used it; those are distinct object/path matches.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | Scan completed; matches are report data |
| `1` | Scan completed with matches and `--fail-on-match` was requested |
| `2` | Invalid input, unsafe output path, failed positive control, or Git failure |

The scanner never fetches, checks out a commit, modifies the index, moves a
ref, rewrites an object, or pushes.

Related: [Audit tutorial](../tutorials/06-audit-sensitive-history.md),
[sanitization guide](../how-to/sanitize-history-before-publishing.md), and
[why context matters](../explanation/why-sensitive-history-needs-context.md).
