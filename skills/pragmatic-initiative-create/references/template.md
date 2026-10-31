# Initiative: <Name>

**Status:** Charted
**Created:** <date>
**Version:** 1.0

## Destination

<the problem or goal this initiative resolves, in 1-2 lines — every feature below exists to serve this>

## Notes

autonomous execution: yes | no

## Architecture

<Each `docs/arch/<name>.arch.md` this initiative depends on (existing or new) — including the arch spec for any new context or relationship listed under Domain Language — or "None needed — <one-line reason>">

## Domain Language

**Contexts touched:** <context names from docs/glossary/context-map.md, or "no glossary yet">
**New contexts:** <name — needs docs/arch/<name>.arch.md (listed under Architecture)> | none
**New relationships:** <From → To — mechanism — what crosses> | none
**Shared terms seeded:** <Term, Term → docs/glossary/<context>.md> | not seeded — <reason>

## Features

Ordered by dependency — a feature never appears above one it depends on.

| # | Feature | Context | Depends on | Spec | Status | Build | Claimed by |
|---|---|---|---|---|---|---|---|
| 1 | <name> | <context> | — | not created yet | Not started | Not started | — |
| 2 | <name> | <context> | #1 | not created yet | Not started | Not started | — |

`Claimed by` is set by `pragmatic-initiative-deliver` to a session label while that session works the row, and reset to `—` when it finishes, so several sessions can deliver independent features without picking the same one. The authoritative claim is a file under the git directory shared by all worktrees of the clone (`pragmatic-devx/claims/<slug>/feature-<n>`); this column mirrors it for readers.

The table is an index. Detail for each feature lives below, one subsection per row.

### 1. <name>

<2-4 sentences: what this feature does and why it's needed>

**Watch for:** <optional — a concern already known at the breakdown level that this feature's own spec should take seriously; omit the line entirely if there is none>

### 2. <name>

<2-4 sentences: what this feature does and why it's needed>

**Watch for:** <optional>

## Decisions So Far

<!-- one line per resolved breakdown decision, added by pragmatic-initiative-create and pragmatic-initiative-deliver as the initiative progresses -->

## Not Yet Specified

<!-- the fog: in-scope concerns you can tell are coming but can't yet state as a feature, because they hang on features still unbuilt. One line each: the suspected capability and what it waits on. Same sharpness test as each spec's Open Questions. A patch graduates (moves into the Features table) once a Checked feature makes it specifiable, and is then removed from here. "None" if empty. -->

## Out of Scope

<!-- work consciously ruled outside this initiative's destination. One line each: the gist and why it is out. Never graduates; it returns only if the destination is redrawn, as a new initiative. "None" if empty. -->
