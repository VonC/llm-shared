# Documentation effort directories

Each effort keeps its draft, requirement, design, implementation plan, and
validation plan in one directory. The canonical versioned draft records the
selected directory layout through its own parent path; no project-global
configuration file is needed.

## Supported layouts

For an effort targeting `vX.Y.Z`, the supported layouts are:

| Choice | Tool value | Effort directory |
| --- | --- | --- |
| Flat | `flat` | `docs/` |
| Minor release | `minor` | `docs/vX.Y/` |
| Full version | `version` | `docs/vX.Y.Z/` |
| Minor and full version | `minor-version` | `docs/vX.Y/vX.Y.Z/` |
| Full version and slug | `version-slug` | `docs/vX.Y.Z/<slug>/` |

`process-draft` asks for this choice after the target version is settled and
passes the tool value to `new_draft --docs-layout`. The renamed
`draft.vX.Y.Z.<slug>.md` is written in the selected effort directory.

All later document-writing skills derive the effort directory from the parent
of the document named in their prompt or context. They write their output beside
that document. They never add a directory below that effort directory: the
version and topic already remain explicit in every filename.

## Qualifying content for effort discovery

`pw` recognizes a `version-slug` directory only when its slug matches
`[a-z0-9][a-z0-9_-]*` and it contains at least one immediate regular file named
as a draft, feature-request, issue, design, ordinary plan or validation plan for
that exact enclosing version and slug. Hyphens and underscores are equivalent
in the slug. For example, `docs/v1.2.3/my-effort/issue.v1.2.3.my_effort.md`
qualifies without a draft. A validation plan uses
`plan.v1.2.3.my_effort.validation.md`; `.validation` identifies its kind.

Empty directories, assets, scratch files and review transcripts do not qualify.
Neither do files for another version or slug, subtopic-prefix matches, or files
found only in a nested directory. An effort named `images` or `sub` qualifies
under the same content rule. Uppercase or dotted slug directories, and slug
directories below `docs/vX.Y/vX.Y.Z/`, remain unsupported.

The four older layouts remain recognized even when empty. Both general and
version-scoped directory discovery inspect current filenames on every call,
without reading document bodies or caching eligibility. Filesystem errors
propagate; they do not count as missing content.

## Canonical preference and workflow fallback

`pw` scans all supported layouts. Workflow selection first validates the parent
of the topic's canonical draft path as a recognized directory. An unsupported
or identity-mismatched parent is an error that identifies the parent, version
and slug. The draft file itself need not exist.

For each requested document role, matches in the canonical parent take
precedence. Several local matches retain newest-file selection and the existing
candidate-order tie behavior. Only when that sibling is missing locally does
selection search all other recognized directories across the supported layouts.
Filename matching still requires the requested version and preserves workflow
role and folded topic/subtopic matching. A unique fallback is selected, no
fallback means absence, and multiple fallbacks produce an error naming the
role, topic, canonical parent and every competing path.

General `pw document` resolution keeps exact type/version/slug matching and
reports duplicate matches as ambiguous, including duplicates across a version
directory and its qualifying slug child. It does not apply workflow preference.

Post-commit discovery uses the validation plan's parent for its synthesized
draft path. A local or unique fallback ordinary plan includes that topic; no
plan skips it, while competing fallback plans propagate failure through the
CLI. Invalid-parent and ambiguity failures exit with code 2 without a success
prompt.

Commands handed from one skill to another carry the actual repository-relative
path printed by `pw`; instructions do not reconstruct a fixed `docs/...` path.

## Umbrella continuation

An umbrella continuation inherits the umbrella draft's layout kind. Apply that
kind to the child effort's settled version, which may produce a different
version directory. For example, an umbrella under `docs/v2.4/v2.4.0/` gives a
`v2.5.1` child the directory `docs/v2.5/v2.5.1/`.
