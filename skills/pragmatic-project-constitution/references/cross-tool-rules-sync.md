# Cross-Tool Rules Sync

Shared procedure used by `pragmatic-project-constitution`, `pragmatic-project-constitution-update`, and `pragmatic-arch-spec-validate` to make generated rules visible to agentic tools other than Claude Code.

## When this runs

Immediately after a skill derives the directive sections (heading + bullet list) for `<slug>`. Nothing here changes the extraction logic itself — only where the result gets written.

## Inputs

- `slug` — identifier used for `.agents/rules/<slug>.md` and every tool-specific filename derived from it (`project-constitution`, or `<spec-name>-arch`)
- `title` — human-readable heading for the rule set (e.g. `Project Constitution Rules`, or `Architecture Rules — <System/Module Name>`)
- `source_path` — where these rules came from (`docs/constitution.md`, or the `.arch.md` file path)
- `sections` — the list of `{heading, bullets}` groups already extracted (e.g. `Global Stack Constraints`, `Cross-Module Constraints`, `AI Guardrails`, or `Dependency Rules`, `Naming Conventions`, `Component Boundaries`). Omit any section with zero bullets.
- `always_apply` — `true` for project-wide rules (constitution), `false` for module-scoped rules (arch)
- `globs` — only when `always_apply` is `false`: the module's own paths, if the arch spec names them clearly (e.g. `src/<module>/**`, `docs/arch/<module>.arch.md`). If no clear path exists, leave `always_apply` as `true` instead of guessing a glob.
- `claude_rules_filename` — optional; the filename to use inside `.claude/rules/` (default `<slug>.md`). Override this when load order matters — e.g. the project constitution passes `00-project-constitution.md` so Claude Code loads it before any module-specific rules file in the same directory. The symlink's own filename is independent of its target's, so this never affects `.agents/rules/<slug>.md`.

## Shared body

Build one block of markdown, used as the canonical file's content and reused verbatim wherever full duplication is required below:

```markdown
<!-- Source: <source_path> · Generated: <today's date> -->

## <heading 1>
- <bullet>
- <bullet>

## <heading 2>
- <bullet>
```

## Canonical file — `.agents/rules/<slug>.md`

Write the shared body to `.agents/rules/<slug>.md` first (create `.agents/rules/` if missing). This is the single source of truth for the distilled directive list. It is a plain markdown file with no tool-specific frontmatter, so it means nothing to any agentic tool on its own — every destination below either symlinks to it, imports it, or copies its content, but this file is what gets regenerated when the skill re-runs, and everything else derives from it.

It lives outside `.claude/`, `.cursor/`, etc. on purpose: none of those directories are neutral ground, and tying the one canonical copy to a tool-specific folder means every *other* tool's config quietly depends on a directory that only makes sense to that one tool.

## Mechanism by destination

| Destination | Mechanism | Confidence |
|---|---|---|
| `.agents/rules/<slug>.md` | canonical, full body | — |
| `.claude/rules/<claude_rules_filename>` (default `<slug>.md`) | **symlink** → `.agents/rules/<slug>.md` | confirmed — Claude Code docs (2026-07-17): "`.claude/rules/` directory supports symlinks... resolved and loaded normally" |
| `.windsurf/rules/<slug>.md` | **symlink** → `.agents/rules/<slug>.md` | assumed, not doc-verified — this destination needs no frontmatter (per existing design), and symlinks are an OS-level mechanism most file readers follow transparently, but Windsurf's own docs weren't checked and no live Windsurf test was run |
| `GEMINI.md` | full body, delimited block | **`@path` import tried and disconfirmed, 2026-07-17.** Gemini CLI's own docs describe `@file.md` static-import support inside GEMINI.md, but this file is also read by Antigravity, and a live headless test (`agy -p ...` against a real `GEMINI.md` containing `@.agents/rules/<slug>.md`) showed Antigravity does **not** resolve the reference — it reported the line as "a reference," not the expanded content. Antigravity's own docs (`antigravity.google/docs/cli/best-practices`) explain why: Antigravity's `@` is an **interactive prompt-box autocomplete** ("Type `@` within your prompt box to trigger the Interactive Path Suggestion overlay... imports the absolute workspace file path directly into your prompt") — a keystroke-triggered UI helper for composing a chat message, not a parser that expands `@path` references sitting in a static file loaded at session start. The two tools that read `GEMINI.md` implement unrelated features that happen to share the `@` character, so a reference written once in the file is never resolved by either at load time. Full duplication is the only version that reliably reaches both. |
| `.cursor/rules/<slug>.mdc` | `@path` import inside frontmatter'd body | **unreliable, not live-tested** — community bug reports of `@file` breaking inside `.mdc` rule files (Cursor forum); consistent with the GEMINI.md finding that `@import` support is inconsistent even within the same tool family. Verify manually before trusting it; fall back to full-body duplication if it doesn't resolve |
| `AGENTS.md` | full body, delimited block | no import mechanism confirmed for this file; it's also a shared file across multiple slugs, so a whole-file symlink can't work at the per-section level anyway |
| `.github/copilot-instructions.md` | full body, delimited block | same reasoning as `AGENTS.md` |

A symlink is preferred over `@import` wherever it works, because the destination tool doesn't need to support anything special — from its point of view it's just reading a normal file; the filesystem resolves the indirection before the tool ever sees it. `@import` depends on the specific tool choosing to parse and expand that syntax, which the GEMINI.md test showed is not something you can assume even when a tool's own docs describe the syntax — a *sibling* tool reading the same file may not honor it. `@import` is only left in place here for Cursor's `.mdc`, because a real per-tool file with frontmatter is unavoidable there and no symlink-based alternative exists; treat it as unverified until checked in your own Cursor version.

## Destinations

### 1. `.claude/rules/<claude_rules_filename>` (default `.claude/rules/<slug>.md`)

Create `.claude/rules/` if missing. Create as a **symlink** to `.agents/rules/<slug>.md` (relative path: `../../.agents/rules/<slug>.md`), not a copied file — the link's own filename is independent of the target's, so use `claude_rules_filename` when a caller needs a specific name (e.g. an ordering prefix). If a real file already exists at this path from a previous run of this skill before this mechanism existed, replace it with the symlink.

### 2. `.windsurf/rules/<slug>.md`

Create `.windsurf/rules/` if missing. Create as a **symlink** to `.agents/rules/<slug>.md` (relative path: `../../.agents/rules/<slug>.md`).

### 3. `AGENTS.md` (project root)

If the file doesn't exist, create it with just `# AGENTS.md` as the first line. Then:
- If markers `<!-- pragmatic:<slug>:start -->` / `<!-- pragmatic:<slug>:end -->` already exist anywhere in the file, replace everything between them with `## <title>` followed by a blank line and the shared body.
- Otherwise, append to the end of the file:

```markdown

<!-- pragmatic:<slug>:start -->
## <title>

<shared body>
<!-- pragmatic:<slug>:end -->
```

### 4. `.github/copilot-instructions.md`

Same delimited technique as `AGENTS.md`. Create `.github/` and the file if either is missing.

### 5. `GEMINI.md` (project root) — only if it already exists

If `GEMINI.md` does not exist, skip this destination entirely — do not create it. Antigravity and other Gemini-family tools already read `AGENTS.md` when there is no `GEMINI.md`; creating one just for this would make `GEMINI.md` start shadowing `AGENTS.md` for content the user never asked to move. If `GEMINI.md` already exists, use the same delimited technique as `AGENTS.md` — full shared body, not an import line (see the mechanism table above for why: Antigravity does not resolve `@path` references inside this file, even though it reads the file itself).

### 6. `.cursor/rules/<slug>.mdc`

Create `.cursor/rules/` if missing. Write the whole file (overwrite if present). The body is a single import line instead of the shared body:

```markdown
---
description: <title>
alwaysApply: <always_apply>
---

@.agents/rules/<slug>.md
```

Add a `globs: [<glob>, ...]` line to the frontmatter only when `always_apply` is `false`.

If a manual check has shown `@import` does not resolve in the Cursor version in use, write the shared body directly in place of the import line instead.

## Output

Report every path written or updated in this run, including `.agents/rules/<slug>.md` and noting which destinations are symlinks vs. imports vs. full copies — the caller's own output summary step lists these.

## Worked example

Inputs: `slug=project-constitution`, `title=Project Constitution Rules`, `source_path=docs/constitution.md`, `always_apply=true`, `claude_rules_filename=00-project-constitution.md`, one section:

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

`.agents/rules/project-constitution.md` (canonical, real file):

```markdown
<!-- Source: docs/constitution.md · Generated: 2026-07-09 -->

## Global Stack Constraints
- Only PostgreSQL is permitted as a database engine. Never suggest SQLite, MongoDB, or any other engine.
```

`.claude/rules/00-project-constitution.md` — symlink (filename overridden via `claude_rules_filename` so Claude Code loads it before module-specific rules):

```bash
ln -s ../../.agents/rules/project-constitution.md .claude/rules/00-project-constitution.md
```

`.windsurf/rules/project-constitution.md` — symlink:

```bash
ln -s ../../.agents/rules/project-constitution.md .windsurf/rules/project-constitution.md
```

`AGENTS.md` (new file, full body — no import mechanism confirmed):

```markdown
# AGENTS.md

<!-- pragmatic:project-constitution:start -->
## Project Constitution Rules

<!-- Source: docs/constitution.md · Generated: 2026-07-09 -->

## Global Stack Constraints
- Only PostgreSQL is permitted as a database engine. Never suggest SQLite, MongoDB, or any other engine.
<!-- pragmatic:project-constitution:end -->
```

`.github/copilot-instructions.md` follows the same full-body block as `AGENTS.md`.

`GEMINI.md` (if present, full body — `@import` disconfirmed for Antigravity, see mechanism table):

```markdown

<!-- pragmatic:project-constitution:start -->
## Project Constitution Rules

<!-- Source: docs/constitution.md · Generated: 2026-07-09 -->

## Global Stack Constraints
- Only PostgreSQL is permitted as a database engine. Never suggest SQLite, MongoDB, or any other engine.
<!-- pragmatic:project-constitution:end -->
```

`.cursor/rules/project-constitution.mdc` (import reference, verify before trusting):

```markdown
---
description: Project Constitution Rules
alwaysApply: true
---

@.agents/rules/project-constitution.md
```
