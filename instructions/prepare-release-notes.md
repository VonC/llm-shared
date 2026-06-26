# Prepare release notes

Prepare the release notes for the next version of the project, before a
release is created. This skill turns the git history since the last tag
into a release-notes summary stored in `version.txt`, then updates the
`CHANGELOG.md`.

Run it once the development cycle for a `-SNAPSHOT` version is complete
and you are ready to cut the release.

## Inputs

- `<PRJ_DIR>/version.txt` whose first word is the current
  `X.Y.Z-SNAPSHOT` version.
- The git history between the last tag and `HEAD`.

## Outputs

- `<PRJ_DIR>/a.md` — the generated release-preparation notes (changelog
  titles grouped by type, plus the full commit list).
- `<PRJ_DIR>/version.txt` — rewritten with the release-notes summary.
- `<PRJ_DIR>/CHANGELOG.md` — updated by `update-changelog.bat`.

## Mutualized resources

- This instruction lives in [`../instructions`](.).
- The release-notes script is
  [`prepare_release_notes.sh`](../scripts/prepare_release_notes.sh)
  under [`../scripts`](../scripts).
- The `version.txt` summary template is
  [`prepare-release-notes.version-txt.template.txt`](../templates/prepare-release-notes.version-txt.template.txt)
  under [`../templates`](../templates).
- Writing rules: [`markdown.md`](../rules/markdown.md) and
  [`blacklist.md`](../rules/blacklist.md) under `../rules`.

## Workflow

### Step 1 — Generate `a.md`

Call the mutualized `prepare_release_notes.sh` script from
`<LLM_SHARED_DIR>/scripts/` (the sibling `../llm-shared` repository).
Run it from `<PRJ_DIR>`:

```bash
bash ../llm-shared/scripts/prepare_release_notes.sh
```

The script resolves the project directory from its first argument, then
the `PRJ_DIR` environment variable, then the current directory — so
running it from `<PRJ_DIR>` is enough. To be explicit, pass the project
directory as the first argument:

```bash
bash ../llm-shared/scripts/prepare_release_notes.sh "<PRJ_DIR>"
```

The script:

- reads `X.Y.Z` from the first word of the first line of `version.txt`
  and stops with a fatal error if it does not end with `-SNAPSHOT`;
- reads the last git tag (`git describe --tags --abbrev=0`, `v` prefix
  removed) and stops with a fatal error if it already equals `X.Y.Z`
  (the release notes are already prepared);
- writes `<PRJ_DIR>/a.md` with the changelog titles grouped by type and
  the full commit list since the last tag.

If the script exits with a non-zero status, stop and report the fatal
error to the user. Do not continue.

### Step 2 — Write the release-notes summary in `version.txt`

Read the generated `a.md` and analyse the `## vX.Y.Z changelog` and
`## vX.Y.Z commit list` sections to deduce the release-notes summary.

Write `<PRJ_DIR>/version.txt` following the template
[`prepare-release-notes.version-txt.template.txt`](../templates/prepare-release-notes.version-txt.template.txt):

- The first line is `X.Y.Z-SNAPSHOT -- Release notes summary for
  version X.Y.Z` (keep the ` -- ` separator: the changelog tooling
  splits the version and the title on it).
- Then three witty title / sub-title pairs.
- Then the main theme paragraph, and an optional secondary theme
  paragraph, with concrete and specific terms — no generalities.
- Then a `### Key changes` list of three key changes (do not add the
  version: the changelog tooling labels each `###` section with the version,
  so `### Key changes for vX.Y.Z` would render the version twice).

Writing constraints:

- Keep lines at most 80 characters wide.
- Witty titles and sub-titles must be grounded in concrete elements of
  the release (a renamed concept, a removed dependency, a measured
  speed-up, a fixed bug class), not abstract phrases.
- Do not use words from [`blacklist.md`](../rules/blacklist.md).
- `version.txt` is a text file, not markdown, even though the content
  uses a markdown-like layout.

### Step 3 — Pause for the title choice

Once `version.txt` is written, stop and display the three witty title /
sub-title pairs. Read [`../rules/interactive_menu.md`](../rules/interactive_menu.md),
then present these concrete choices:

- the three generated title / sub-title pairs;

Use the chosen or custom pair for the release notes summary.

### Step 4 — Finalize `version.txt`

Once the user has chosen, rewrite the start of `version.txt` so the
chosen title becomes the release title and its sub-title the second
line. The two remaining pairs stay in the list below. For a chosen
title 2, the start of `version.txt` becomes:

```txt
X.Y.Z-SNAPSHOT -- witty title 2

witty sub-title 2

- witty title 1
  -- witty sub-title 1
- witty title 3
  -- witty sub-title 3

Main theme for this release, ...
```

The main theme, secondary theme, and `### Key changes` sections stay
unchanged below.

### Step 5 — Update the changelog

Call `update-changelog.bat` from `<PRJ_DIR>`:

```bat
tools\dev_workflow\update-changelog.bat
```

Run it from PowerShell or cmd.exe, not from Git Bash — it is a `.bat`
toolchain script (see [`../rules/run_commands.md`](../rules/run_commands.md)).

- If it succeeds, output a message confirming the `CHANGELOG.md` was
  updated with the new version and the release-notes summary.
- If it fails, stop with an error: report the failure, include the
  relevant error output, and give troubleshooting hints.

### Step 6 — Report and give next steps

Output a final message confirming that:

- the release-notes summary was generated and saved to `version.txt`;
- the `CHANGELOG.md` was updated.

Then tell the user the next step: this skill does not create the
release. To create it, the user runs `brel`.

## Handoff to prepare-release

This skill can run on its own or as one step of the `prepare-release`
skill. Check for the flag file `a.prepare-release.active` at the project
root:

- When it exists, you are running inside a `prepare-release` run. Once
  `version.txt` and `CHANGELOG.md` are written (Steps 1 to 5), do not print
  the standalone "next, run `brel`" closing of Step 6: return control to
  `prepare-release` so it continues with the next release step
  (`prepare-release` makes the single prepare commit and tells the user
  about `brel` at the end of its own run). Do not delete the flag file,
  since `prepare-release` owns its lifecycle.
- When it is absent (a direct call), finish with Step 6 as described
  above and return to your caller.
