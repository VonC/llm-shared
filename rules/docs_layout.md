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

## Workflow discovery

`pw` scans all supported layouts. Once it resolves a canonical draft, it searches
that draft's parent directory first and does not mix duplicate documents from
another layout into the effort.

Commands handed from one skill to another carry the actual repository-relative
path printed by `pw`; instructions do not reconstruct a fixed `docs/...` path.

## Umbrella continuation

An umbrella continuation inherits the umbrella draft's layout kind. Apply that
kind to the child effort's settled version, which may produce a different
version directory. For example, an umbrella under `docs/v2.4/v2.4.0/` gives a
`v2.5.1` child the directory `docs/v2.5/v2.5.1/`.
