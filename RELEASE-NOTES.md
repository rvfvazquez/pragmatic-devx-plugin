# Pragmatic DevX — Release Notes

## v0.6.1 (2026-07-17)

### Fixes

- **Plugin failed to install** — `.claude-plugin/plugin.json` declared `"agents"`
  as a directory string; the schema requires an array of explicit `.md` file
  paths. Fixed to `["./agents/tdd-implementer.md"]`.
- **Plugin failed to load** — `plugin.json` also declared `"hooks":
  "./hooks/hooks.json"`, duplicating the file the loader already auto-loads by
  convention, which made every install fail with "Duplicate hooks file
  detected". Removed the redundant declaration.
- **10 of 12 `SKILL.md` files reported as missing frontmatter** — each file
  actually had correct frontmatter, but started with a UTF-8 BOM before the
  opening `---`, so the parser's literal-prefix check never matched. Stripped
  the BOM; no frontmatter content changed.

### Cross-Tool Rule Sync — Canonical File Redesign

`cross-tool-rules-sync.md` now writes a canonical `.agents/rules/<slug>.md`
file first, with `.claude/rules/<slug>.md` and `.windsurf/rules/<slug>.md` as
symlinks to it, instead of duplicating full content into every destination.
`GEMINI.md`, `AGENTS.md`, and `.github/copilot-instructions.md` still get a
full-body copy (no reliable import mechanism confirmed for any of them —
`@path` resolution was tested and disconfirmed for Antigravity's `GEMINI.md`
handling). `.cursor/rules/<slug>.mdc` now uses an `@import` line instead of a
full copy.

`pragmatic-project-constitution` and `pragmatic-project-constitution-update`
are now wired to this shared procedure — previously only
`pragmatic-arch-spec-validate` used it, and the constitution skills wrote
`.claude/rules/00-project-constitution.md` directly. A new
`claude_rules_filename` input lets a caller override the symlink's filename
independently of `<slug>.md`, so the constitution's `00-` load-order prefix is
preserved. `pragmatic-arch-spec-validate` also had a stale direct-write
instruction for `.claude/rules/<spec-name>-arch.md` left over from before this
procedure existed, conflicting with the procedure's own symlink step; removed.

## v0.6.0 (2026-07-09)

### Cross-Tool Rule Generation

`pragmatic-project-constitution`, `pragmatic-project-constitution-update`, and
`pragmatic-arch-spec-validate` now sync generated rules beyond
`.claude/rules/` so they are respected in other agentic IDEs, not just Claude
Code:

- **`AGENTS.md`** — read natively by Codex CLI and Antigravity (v1.20.3+), and
  used as fallback context by most other agentic tools
- **`.cursor/rules/<slug>.mdc`** — Cursor, with `alwaysApply`/`globs` frontmatter
- **`.windsurf/rules/<slug>.md`** — Windsurf
- **`.github/copilot-instructions.md`** — GitHub Copilot
- **`GEMINI.md`** — synced only when the project already has one, since it
  overrides `AGENTS.md` for Gemini-family tools when present

`.claude/rules/<slug>.md` generation is unchanged. See
`skills/pragmatic-project-constitution/references/cross-tool-rules-sync.md`
for the shared procedure.

## v0.4.0 (2026-06-13)

### Multi-Platform Support

Plugin now works across four AI development environments:

- **Codex CLI** — `.codex-plugin/plugin.json` with full `interface` block (displayName, shortDescription, longDescription, capabilities, defaultPrompt)
- **Cursor** — `.cursor-plugin/plugin.json` with cursor-specific hooks registration
- **Gemini CLI** — `GEMINI.md` (auto-loaded at session start via `@` references) + `gemini-extension.json`
- **Claude Code** — `.claude-plugin/plugin.json` updated with full metadata fields (`version`, `homepage`, `repository`, `license`, `keywords`, `skills`, `hooks`)

All platform adapters point to the same `./skills/` directory — no content duplication.

### Bootstrap Skill: pragmatic-howto

New skill that establishes the document hierarchy and maps every skill to its purpose and trigger.

Serves as the entry point for new sessions: Claude loads the full lifecycle map (constitution → arch spec → feature spec) and quick-decision table before responding to any spec-related request.

Includes `references/skill-map.md` with full per-skill reference (purpose, output paths, pre-conditions, guards) loaded on demand.

### SessionStart Hook

Automatic project state injection at session start. The hook:

- Detects whether pragmatic documentation exists in the current project (`docs/constitution.md`, `docs/specs/`, `docs/arch/`)
- If found, injects a `<pragmatic-project-context>` summary listing the constitution status and all known spec files
- If not found, outputs nothing — fully silent in projects that don't use pragmatic docs

Designed to coexist with superpowers and other plugins without conflict:
- Uses its own `<pragmatic-project-context>` tag (not `<EXTREMELY_IMPORTANT>`)
- Injects project state only, never workflow instructions
- Supports Claude Code, Cursor, Copilot CLI, and Gemini platform formats via environment variable detection

### Skill-Triggering Test Suite

New `tests/skill-triggering/` directory with:

- `run-test.sh` — runs a single skill test: invokes `claude -p` with a natural language prompt and verifies the expected skill was triggered via the Skill tool
- `run-all.sh` — runs all prompts and reports pass/fail summary
- `prompts/` — 11 `.txt` files, one per skill, each containing a realistic user message that should trigger that skill without explicitly naming it

Tests require the Claude Code CLI and are run with `--plugin-dir` pointing to the repo root.

### .claude-plugin/plugin.json

Enriched with `version`, `homepage`, `repository`, `license`, `keywords`, `skills`, and `hooks` fields to match the completeness of the new platform adapters.

---

## v0.3.0 (2026-05-01)

### Skills

Initial release of the pragmatic-devx skill set:

**Feature Spec Lifecycle**
- `pragmatic-spec-create` — create a spec from scratch
- `pragmatic-spec-validate` — quality review of an existing spec
- `pragmatic-spec-update` — apply changes with version tracking
- `pragmatic-spec-build` — implement from an approved spec
- `pragmatic-spec-check` — verify implementation matches spec

**Architecture Spec Lifecycle**
- `pragmatic-arch-spec-create` — create an architecture spec (system / module / layer / integration)
- `pragmatic-arch-spec-validate` — quality review of an existing arch spec
- `pragmatic-arch-spec-update` — apply ADRs and boundary changes
- `pragmatic-arch-spec-check` — verify codebase conforms to architecture decisions

**Governance**
- `pragmatic-project-constitution` — create a project-wide governance document

All skills follow a consistent pre-condition check pattern: verify constitution exists before any spec work; guard against replacing existing documents without explicit confirmation; enforce status transitions (Draft → Review → Approved).
