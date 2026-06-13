# Pragmatic DevX — Release Notes

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
