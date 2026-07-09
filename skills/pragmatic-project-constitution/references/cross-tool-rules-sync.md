# Cross-Tool Rules Sync

Shared procedure used by `pragmatic-project-constitution`, `pragmatic-project-constitution-update`, and `pragmatic-arch-spec-validate` to make generated rules visible to agentic tools other than Claude Code.

## When this runs

Immediately after a skill writes `.claude/rules/<slug>.md`, using the same directive sections (heading + bullet list) it just extracted for that file. Nothing here changes `.claude/rules/<slug>.md` itself.

## Inputs

- `slug` — same identifier used for the `.claude/rules/<slug>.md` filename (`project-constitution`, or `<spec-name>-arch`)
- `title` — human-readable heading for the rule set (e.g. `Project Constitution Rules`, or `Architecture Rules — <System/Module Name>`)
- `source_path` — where these rules came from (`docs/constitution.md`, or the `.arch.md` file path)
- `sections` — the same list of `{heading, bullets}` groups already extracted for `.claude/rules/<slug>.md` (e.g. `Global Stack Constraints`, `Cross-Module Constraints`, `AI Guardrails`, or `Dependency Rules`, `Naming Conventions`, `Component Boundaries`). Omit any section with zero bullets.
- `always_apply` — `true` for project-wide rules (constitution), `false` for module-scoped rules (arch)
- `globs` — only when `always_apply` is `false`: the module's own paths, if the arch spec names them clearly (e.g. `src/<module>/**`, `docs/arch/<module>.arch.md`). If no clear path exists, leave `always_apply` as `true` instead of guessing a glob.

## Shared body

Build one block of markdown, reused verbatim across every destination below:

```markdown
<!-- Source: <source_path> · Generated: <today's date> -->

## <heading 1>
- <bullet>
- <bullet>

## <heading 2>
- <bullet>
```

## Destinations

### 1. `AGENTS.md` (project root)

If the file doesn't exist, create it with just `# AGENTS.md` as the first line. Then:
- If markers `<!-- pragmatic:<slug>:start -->` / `<!-- pragmatic:<slug>:end -->` already exist anywhere in the file, replace everything between them with `## <title>` followed by a blank line and the shared body.
- Otherwise, append to the end of the file:

```markdown

<!-- pragmatic:<slug>:start -->
## <title>

<shared body>
<!-- pragmatic:<slug>:end -->
```

### 2. `.github/copilot-instructions.md`

Same delimited technique as `AGENTS.md`. Create `.github/` and the file if either is missing.

### 3. `GEMINI.md` (project root) — only if it already exists

If `GEMINI.md` does not exist, skip this destination entirely — do not create it. Antigravity and other Gemini-family tools already read `AGENTS.md` when there is no `GEMINI.md`; creating one just for this would make `GEMINI.md` start shadowing `AGENTS.md` for content the user never asked to move. If `GEMINI.md` already exists, use the same delimited technique as `AGENTS.md`.

### 4. `.cursor/rules/<slug>.mdc`

Create `.cursor/rules/` if missing. Write the whole file (overwrite if present):

```markdown
---
description: <title>
alwaysApply: <always_apply>
```

Add a `globs: [<glob>, ...]` line to the frontmatter only when `always_apply` is `false`. Then close the frontmatter and add the shared body:

```markdown
---

<shared body>
```

### 5. `.windsurf/rules/<slug>.md`

Create `.windsurf/rules/` if missing. Write the whole file (overwrite if present) as just the shared body — no frontmatter.

## Output

Report every path written or updated in this run — the caller's own output summary step lists these alongside `.claude/rules/<slug>.md`.

## Worked example

Inputs: `slug=project-constitution`, `title=Project Constitution Rules`, `source_path=docs/constitution.md`, `always_apply=true`, one section:

```
Global Stack Constraints:
- Only PostgreSQL is permitted as a database engine. Never suggest SQLite, MongoDB, or any other engine.
```

Shared body:

```markdown
<!-- Source: docs/constitution.md · Generated: 2026-07-09 -->

## Global Stack Constraints
- Only PostgreSQL is permitted as a database engine. Never suggest SQLite, MongoDB, or any other engine.
```

`AGENTS.md` (new file):

```markdown
# AGENTS.md

<!-- pragmatic:project-constitution:start -->
## Project Constitution Rules

<!-- Source: docs/constitution.md · Generated: 2026-07-09 -->

## Global Stack Constraints
- Only PostgreSQL is permitted as a database engine. Never suggest SQLite, MongoDB, or any other engine.
<!-- pragmatic:project-constitution:end -->
```

`.cursor/rules/project-constitution.mdc`:

```markdown
---
description: Project Constitution Rules
alwaysApply: true
---

<!-- Source: docs/constitution.md · Generated: 2026-07-09 -->

## Global Stack Constraints
- Only PostgreSQL is permitted as a database engine. Never suggest SQLite, MongoDB, or any other engine.
```

`.windsurf/rules/project-constitution.md`:

```markdown
<!-- Source: docs/constitution.md · Generated: 2026-07-09 -->

## Global Stack Constraints
- Only PostgreSQL is permitted as a database engine. Never suggest SQLite, MongoDB, or any other engine.
```

`.github/copilot-instructions.md` and `GEMINI.md` (if present) follow the same block as `AGENTS.md`.
