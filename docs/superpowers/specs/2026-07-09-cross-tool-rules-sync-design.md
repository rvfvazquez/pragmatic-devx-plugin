# Design: Cross-Tool Rule File Sync for Constitution & Arch Rules

**Status:** Approved
**Date:** 2026-07-09

## Problem

`pragmatic-project-constitution`, `pragmatic-project-constitution-update`, and
`pragmatic-arch-spec-validate` all derive a directive list (project-wide rules,
or per-module architecture rules) and write it to a single destination:
`.claude/rules/<slug>.md`. This file is auto-loaded by Claude Code only.

When a team uses the pragmatic-devx-plugin skills from Claude Code but then
works on the same project from another agentic IDE (Antigravity, Codex CLI,
Cursor, Windsurf, GitHub Copilot), that tool never sees the rules the
constitution/arch skills produced — it has no `.claude/rules/` convention. The
rules silently stop being respected the moment work moves to a different tool,
even though the underlying spec/constitution content hasn't changed.

This is the same root cause in three places: each skill treats "generate
Claude project rules" as the terminal step, when it should be "generate rules,
then make them visible to whichever tool is actually driving the session."

## Non-Goals

- Changing what content is extracted into directives (unchanged — same
  extraction logic in all three skills today).
- Changing skill triggering / `description:` frontmatter (unaffected — no new
  `tests/skill-triggering/prompts/` entries required).
- Inventing a new rules format. Every destination below uses that tool's own,
  already-existing convention.

## Destinations

Research (see PR description for sources) confirmed the current (2026)
landscape has converged enough that this is a short, stable list:

| Destination | Tool(s) covered | Format | Created if absent? |
|---|---|---|---|
| `.claude/rules/<slug>.md` | Claude Code | unchanged, existing format | yes (unchanged behavior) |
| `AGENTS.md` (project root) | Codex CLI, Antigravity (native since v1.20.3), Aider, Zed, fallback for most others | plain markdown, delimited section | yes |
| `.cursor/rules/<slug>.mdc` | Cursor | YAML frontmatter (`description`, `alwaysApply`, `globs`) + directive body | yes |
| `.windsurf/rules/<slug>.md` | Windsurf | one file per slug, directory-based | yes |
| `.github/copilot-instructions.md` | GitHub Copilot | delimited section (single file) | yes |
| `GEMINI.md` (project root) | Gemini CLI / Antigravity | delimited section | **no** — only touched if it already exists |

`GEMINI.md` is the one deliberate exception: Antigravity/Gemini-family tools
prefer `GEMINI.md` over `AGENTS.md` when both are present. If we auto-created
an empty-ish `GEMINI.md` just to hold our section, we'd risk shadowing
`AGENTS.md` for a file the user never asked for. If the project has no
`GEMINI.md`, those tools already fall back to `AGENTS.md`, so skipping it here
is correct, not a gap. If a project *already* has one, we must sync our
section into it — otherwise our `AGENTS.md` section would be silently
invisible to those tools.

`slug` is the same identifier already used for the `.claude/rules/<slug>.md`
filename today: `project-constitution` for the constitution skills, and
`<spec-name>-arch` for `pragmatic-arch-spec-validate`.

## Shared Procedure (single source of truth)

The multi-file-sync mechanics are written once, as a shared reference doc:

```
skills/pragmatic-project-constitution/references/cross-tool-rules-sync.md
```

All three skills add one step that says "render the directive list for
`<slug>` using the procedure in this reference doc," rather than repeating the
mechanics three times. Each caller supplies:
- `slug`
- the directive list (already derived by existing logic — unchanged)
- destination-specific metadata: `alwaysApply: true` for the constitution
  (global, always relevant) vs. `alwaysApply: false` + `globs` scoped to the
  module's paths for arch rules (only relevant when touching that module)

### Idempotency

- **Delimited destinations** (`AGENTS.md`, `.github/copilot-instructions.md`,
  `GEMINI.md` when present): content is replaced only between
  `<!-- pragmatic:<slug>:start -->` and `<!-- pragmatic:<slug>:end -->`
  markers. Everything else in the file — other slugs' sections, the user's own
  content — is left untouched. If no markers for that slug exist yet, a new
  delimited block is appended.
- **Whole-file destinations** (`.claude/rules/<slug>.md`,
  `.cursor/rules/<slug>.mdc`, `.windsurf/rules/<slug>.md`): overwritten in
  full on every regeneration, same as `.claude/rules/<slug>.md` behaves today.

### Integration points

- `pragmatic-project-constitution` Step 4 (today: write
  `.claude/rules/00-project-constitution.md`) → also runs the shared sync
  step for `slug = project-constitution`.
- `pragmatic-project-constitution-update` Step 5 (today: regenerate
  `.claude/rules/00-project-constitution.md`) → also re-runs the shared sync
  step, cascading every update to every destination.
- `pragmatic-arch-spec-validate` Step 4 (today: optional, PASS-only, writes
  `.claude/rules/<spec-name>-arch.md`) → on acceptance, runs the shared sync
  step for `slug = <spec-name>-arch` instead of writing only the Claude file.

### Output summary

Each skill's final summary lists every file actually written/updated in that
run. Destinations skipped (only possible case: `GEMINI.md` absent) simply
don't appear.

## Testing / Verification

- No skill `description:` frontmatter changes → no new
  `tests/skill-triggering/prompts/` entries required by this repo's own gate.
- Run `tests/skill-triggering/run-test.sh` for the three affected skills
  before and after, to confirm no regression in triggering.
- Manual dry run: exercise the updated constitution skill and
  `pragmatic-arch-spec-validate` against a scratch project and inspect every
  generated file (`.claude/rules/*`, `AGENTS.md`, `.cursor/rules/*.mdc`,
  `.windsurf/rules/*.md`, `.github/copilot-instructions.md`) for correct
  content and correct delimiter placement. This is the verification evidence
  for the PR description.

## Rollout

Behavior change to three skills → bump all five version fields together per
this repo's Versioning section: `plugin.json`, `.codex-plugin/plugin.json`,
`.cursor-plugin/plugin.json`, `gemini-extension.json`,
`.claude-plugin/marketplace.json`.
