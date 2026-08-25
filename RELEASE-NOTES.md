# Pragmatic DevX — Release Notes

## v0.8.0 (2026-08-25)

### Structured Interviews Across All Six Create/Update Skills

Every create/update skill in the constitution, spec, and arch-spec lifecycles
(`pragmatic-project-constitution[-update]`, `pragmatic-spec-create[-update]`,
`pragmatic-arch-spec-create[-update]`) asked technology and ADR questions as
flat, single-round menus with no recommended default, so any dependent
sub-decision unlocked by an answer (e.g. picking a queue, then needing FIFO
vs. standard) had nowhere to go but a `[TODO: decide]` item — one that
`pragmatic-spec-validate` / `pragmatic-arch-spec-validate` would then report
as a FAIL/WARN. Found via structural comparison against the `grilling`
skill's design-tree/frontier interview model (a recommended answer per
question, and rounds that reopen based on prior answers).

- **Recommended answers (`➡️`)** — every question with a concrete option
  list now carries a recommendation, derived in priority order from the
  project constitution or existing specs, the codebase scan, then a stated
  pragmatic default.
- **Follow-up rounds for dependent decisions** — a new round after each main
  interview step asks dependent sub-decisions on the spot (queue type, token
  lifetime, retry policy, compliance controls, dependency-table updates,
  etc.) instead of deferring them to a TODO.
- **Final Consistency Check** — a new step right before each document is
  written recaps every decision confirmed so far, scans a short table of
  known contradiction shapes specific to that document type, and requires
  explicit user confirmation before proceeding. `-update` skills also check
  the proposed change against the existing, untouched document content, not
  just the current session's answers. Scoped to contradiction, not
  completeness, so it does not duplicate `pragmatic-spec-validate` /
  `pragmatic-arch-spec-validate`.
- **`pragmatic-spec-build`** — the Step 0.5 execution-preference menu (test
  strategy, scaffold order) also gained a recommendation, keyed on whether
  the harness supports subagent dispatch.

No skill `description`/trigger changed in this release, so
`tests/skill-triggering/prompts/` behavior is unaffected. All platform
adapters (`.codex-plugin`, `.cursor-plugin`, `GEMINI.md`) point at the same
`./skills/` directory, so the change applies uniformly without any
per-platform sync step.

## v0.7.0 (2026-08-15)

### New Skill — `pragmatic-reverse-engineer`

Adds a 13th skill that generates a feature spec or architecture spec by
scanning existing, undocumented code, instead of interviewing a human about
something not yet built. It never creates or owns documents in
`docs/specs/` or `docs/arch/` itself — it discovers, tags findings
CONFIRMED (observable in code) or INFERRED (a guess about intent), and
hands off to the existing `pragmatic-spec-create` / `pragmatic-arch-spec-create`
skills, which run their normal constitution check and existing-file guard
unmodified. Its only edit to the resulting document is a `## Provenance`
append; it owns one file of its own, a session report at
`docs/reverse-engineering/<session-slug>-<date>.report.md`.

Always asks Architecture / Feature / Both before scanning — never inferred
from wording, since it decides both the template and the downstream skill.
When more than one target is found (e.g. repo-wide candidate discovery with
no target named), each is scanned and handed off sequentially, one at a
time, so the downstream interview never gets diluted by findings from other
targets.

Wired into `pragmatic-howto` (bootstrap skill map and quick-decision
table), `GEMINI.md`, and `tests/skill-triggering/prompts/`.

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
