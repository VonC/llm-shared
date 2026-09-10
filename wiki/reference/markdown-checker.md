# Markdown checker reference

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

The repository Markdown checker evaluates every Markdown path returned by one
`git ls-files` inventory. It reads `.markdownlint.json`, compares findings with
`.markdownlint-baseline.json`, and returns zero only when no finding exceeds
the recorded allowances.

## Invocation model

The shared `check.bat` gate invokes the tracked `markdown-check.bat` launcher
automatically and records its result as the `markdown` component. Run the
launcher directly to diagnose Markdown findings or verify a focused edit; the
same repository configuration, adapters, inventory, and baseline apply in both
paths.

## Supported Markdown rule catalog

| Rule | Checked contract |
| --- | --- |
| `MD001` | Heading levels never skip their immediate parent level |
| `MD009` | A line ends with no trailing whitespace, or exactly the hard-break pair |
| `MD012` | No two consecutive blank lines outside fenced code |
| `MD013` | Line length is catalogued and disabled by repository policy |
| `MD024` | Literal heading text does not repeat |
| `MD025` | A document contains at most one level-one title |
| `MD032` | A list block has blank lines before and after it |
| `MD033` | Raw HTML is rejected except configured element names |
| `MD034` | An absolute URL is wrapped as an autolink or a link target |
| `MD038` | Inline-code delimiters contain no unnecessary inner padding |
| `MD040` | Every opening fence declares a language |
| `MD050` | Strong emphasis in prose uses asterisk delimiters |
| `LS001` | A structured document contains a level-one title |
| `LS002` | A structured document contains at least two level-two sections |
| `LS003` | Every anchor-normalized heading title is globally unique |

`MD012`, `MD024` and `MD025` are mandatory. A configuration that attempts to
disable any of them fails before inventory evaluation, and the baseline cannot
allow them either: an allowance naming a mandatory rule fails to load. A
mandatory finding therefore has exactly one repair, which is fixing the file.
The current policy disables `MD013` and permits only `img` under `MD033`.
Unknown configuration keys and unsupported option shapes also fail before file
evaluation.

## MD009 trailing whitespace and the hard-break pair

`MD009` reports any line whose trailing whitespace is neither zero nor exactly
two characters, in the `[Expected: 0 or 2; Actual: N]` form. Two trailing spaces
are the Markdown hard line break and stay legal; one, three, or a trailing tab
do not. Lines inside a fenced code block are exempt, but both fence marker lines
are checked, which matches the upstream rule's default `code_blocks` handling.

Indented code blocks are exempt too, which is why `_indented_code_lines` exists
on the source model. `MD009` stays non-mandatory because that block detection is
an approximation: a four-space run that follows a blank line and sits outside
every list block.

## MD034 bare URL boundaries

`MD034` reports an `http` or `https` URL that carries no surrounding link
syntax. THE SCHEME SET IS NOT ARBITRARY: upstream builds autolink literals only
for `http` and `https`, so a bare `ftp://` URL is not a finding, and reporting
one would be a false positive.

A URL is not bare when it is wrapped as an autolink in angle brackets, nested
inside another autolink such as `<view-source:https://host>`, used as a link or
image target after `](`, defined after a `[label]:` reference marker, quoted
inside an HTML attribute, or preceded by an ASCII letter. That last condition is
the upstream predicate: the character before the scheme must not be a letter, so
`view-source:https://host` IS a bare URL while `xhttps://host` is not. Inline
code, fenced code, and indented code are masked before the rule runs.

This remains a bounded approximation rather than a GFM autolink parser. It does
not detect a scheme-less `www.` host or a bare email address, and it stops a URL
at the first whitespace, angle bracket, parenthesis, bracket, quote, or
backtick. It is not mandatory for that reason.

## MD040 fenced code languages

`MD040` reports an opening fence whose info string is empty. Only openers are
read: a closing marker carries no language and a fence-shaped line inside an
open block is content, so neither is a finding. When a block holds output,
a transcript, or a diagnostic rather than a language, `text` is the conventional
info string and satisfies the rule.

## MD012 blank-run boundaries

`MD012` reports one finding per run of two or more blank lines, located at the
run's last line and carrying the run length, in the
`[Expected: 1; Actual: N]` form. A line holding only spaces or tabs counts as
blank. Lines inside a fenced code block are exempt, because fence content is
data, and so are the lines of a leading YAML frontmatter block. A run that ends
the file is reported like any other.

## Structured documents and bounded adapters

Title and section-count checks apply to structured documents. Three bounded
adapter forms omit those two obligations while every other rule still runs:

- a document with YAML frontmatter containing a nonempty `description`;
- a file in an approved adapter root with at most five body lines and a
  repository-relative Markdown link whose target exists in the tracked
  inventory; and
- a file under `templates/` whose first heading is level two or deeper.

A missing or escaping pointer target makes the file structured. All checked
documents still receive hierarchy, duplicate-heading, list, raw-HTML, and
inline-code evaluation.

## Heading hierarchy and global uniqueness

`MD001` accepts all six heading levels but requires every transition to retain
the immediate parent level. A jump from `#` to `###` fails because level two is
absent. `MD025` rejects a second level-one title.

`MD024` compares literal heading text. `LS003` is independent and applies this
anchor-style normalization before detecting later occurrences:

1. Replace Markdown links with their visible labels.
2. Remove HTML tags and the formatting markers `` ` ``, `*`, `_`, and `~`.
3. Apply Unicode case folding.
4. Keep letters, numbers, hyphens, and whitespace.
5. Trim the result and collapse each whitespace run to one hyphen.

An exact repeat may therefore report both `MD024` and `LS003`; neither finding
suppresses the other.

## MD032 list authoring boundaries

Every list block needs a blank line before its first item and after its final
item. Review content rendered as a standalone block follows the same rule.

The requested-changes, covered-wording, and writer-response fields are inlined
behind labels by their renderers. Their authored content starts with a prose
sentence, then a blank line, then any list. A leading list would touch the
label even if the caller supplied leading whitespace, because the renderer
strips that whitespace before prefixing the label.

## MD038 inline-code space exceptions

`MD038` rejects padding that is not part of the parsed inline-code value. It
accepts these cases:

- the parsed value genuinely begins or ends with whitespace;
- the code span contains only spaces; and
- matching single-space padding is required around content that begins or
  ends with a literal backtick.

When prose needs to describe a separator with surrounding spaces, name the
spaces in prose and keep only the separator inside the code span. Fenced code,
including fences nested under list items, is excluded from inline-code checks.

## MD050 strong style and code boundaries

`MD050` rejects underscore-delimited strong emphasis and requires asterisk
delimiters for strong prose. Inline and fenced code are masked before the rule
runs. A filename containing paired underscores, such as `__init__.py`, must
therefore be enclosed in backticks when it appears in prose or a list item.

## Finding and stream contract

Each enforced finding is written to standard output in this form:

```text
path/to/file.md:17: MD032: list block needs a blank line before it
```

Repository paths always use forward slashes, whole-file findings use line 1,
and results are sorted by path, line, rule, and reason. Configuration,
inventory, decoding, and other operational failures are written to standard
error. A passing baseline shrink is also written to standard error with the
`debt-reduced` marker.

## Versioned no-growth baseline

The root `.markdownlint-baseline.json` file uses version 1 and stores one
positive aggregate count per normalized path and rule:

```json
{
  "version": 1,
  "allowances": [
    {"path": "docs/legacy.md", "rule": "MD033", "count": 2}
  ]
}
```

A new path/rule key or a count above its allowance fails. An equal count passes
silently. A lower count passes with a `debt-reduced` advisory. The checker never
rewrites the baseline; maintainers review the complete findings and edit the
file by hand. Zero-debt Markdown rules, including `MD032` and `MD038`, have no
baseline entries, and the mandatory rules cannot acquire one.

## Direct commands and shared gate

On Windows, run the repository-root launcher without prior environment setup:

```bat
markdown-check.bat
```

On any supported platform, enter the same CLI boundary through Python:

```text
python -m tools.markdown_check.cli
```

Both commands accept `--root`, `--config`, and `--baseline` path overrides and
require no Node runtime, network access, or interactive input. `check.bat`
invokes the Windows launcher once and records a failed result under the
aggregate gate name `markdown`.
