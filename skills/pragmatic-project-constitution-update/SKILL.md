---
name: pragmatic-project-constitution-update
description: This skill should be used when the user asks to "update the constitution", "update the project constitution", "add a global rule", "change a tech stack decision in the constitution", "add a cross-module constraint", "update the AI guardrails", "add a compliance requirement to the constitution", "revise the constitution", "add a new rule that applies to all modules", or wants to apply targeted changes to an existing project constitution document without replacing it.
---

# pragmatic-project-constitution-update

Apply targeted changes to an existing project constitution — adding new rules, correcting decisions, or updating constraints — while preserving history and regenerating the auto-loaded rules file.

## Purpose

Evolve `docs/constitution.md` safely. Never overwrite prior decisions; deprecate what is removed. Every update produces a new changelog entry and regenerates `.claude/rules/00-project-constitution.md` so Claude Code immediately reflects the change in all future sessions.

## Lifecycle Position

```
pragmatic-project-constitution → [pragmatic-project-constitution-update]
         ↓ read by
pragmatic-spec-create · pragmatic-arch-spec-create · pragmatic-spec-build · pragmatic-spec-check
```

## When This Skill Applies

Use when `docs/constitution.md` **already exists** and needs targeted changes — new rules, updated decisions, added compliance requirements, or revised guardrails.

**Do not use when:**
- No constitution exists yet → use `pragmatic-project-constitution`
- The user wants to replace the entire constitution from scratch → use `pragmatic-project-constitution` (with explicit confirmation to replace)

---

## How to Update a Constitution

### Step 0 — Language Detection

Infer the output language from the existing constitution:
1. Check the `Language:` metadata field — use it if present
2. Otherwise infer from the majority language of prose in sections 1–4 (≥80% threshold)
3. If ambiguous, use `AskUserQuestion`:

```
In which language would you like the constitution updates to be written?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Apply the chosen language to all new or modified content. Existing unchanged content stays in its original language.

---

### Step 1 — Locate and Read the Constitution

Read `docs/constitution.md` in full. Note:
- Current `Last Updated` date and version (if present)
- The content of each section: Project Identity, Global Tech Stack, Cross-Module Rules, AI Behavior Guardrails
- Existing changelog entries

Also read `.claude/rules/00-project-constitution.md` if it exists — it will need to be regenerated after the update.

---

### Step 2 — Understand the Change

Analyze what needs to change. Classify the update by area:

| Area | Examples |
|---|---|
| **Project Identity** | New compliance requirement (LGPD, GDPR), change in tenancy model, updated product scope |
| **Global Tech Stack** | Add permitted technology, remove forbidden one, update a stack decision and rationale |
| **Cross-Module Rules** | New inter-module constraint, updated ownership boundary, deprecated rule |
| **AI Behavior Guardrails** | New action Claude must always ask before taking, removed guardrail, updated trigger condition |

---

### Step 3 — Confirm Scope Before Proceeding

**This is a mandatory step.** Do not apply any changes until scope and intent are confirmed.

Use `AskUserQuestion` with the following structure. **Any question with a concrete option list must carry a recommended answer (`➡️`)**, derived in this priority order: (1) content already recorded elsewhere in `docs/constitution.md`, (2) a pragmatic default stated as such.

```
Before I apply any changes, let me confirm my understanding:

**What I understood**
- [Restate the change as you interpreted it — ask the user to confirm or correct]

**Sections in Scope** → multiSelect: true
Which areas of the constitution are changing?
- Section 1 — Project Identity
- Section 2 — Global Tech Stack
- Section 3 — Cross-Module Rules
- Section 4 — AI Behavior Guardrails

**Nature of the Change** → multiSelect: true
What kind of update is this?
- Adding a new rule or decision
  ➡️ [state which, based on the requested change]
- Correcting an existing rule (wrong information)
- Deprecating a rule that no longer applies
- Strengthening or narrowing an existing rule

**Motivation**
- What triggered this change? (new compliance requirement, new technology adopted, team decision, incident, audit finding)
- Does this change supersede or contradict any existing rule in the constitution?
  ➡️ Flag any existing rule found in Step 1 that appears to conflict — do not silently assume it doesn't

Answer what you know, or just confirm the ➡️ recommendation.
```

Do not proceed until:
- The section(s) in scope are confirmed
- The motivation is understood
- Whether any existing rule is superseded is explicit

### Step 3.5 — Follow-up Round for Dependent Decisions

After the user answers Step 3, check whether any answer unlocks a **dependent decision** that could not have been asked before it (its options only make sense given the parent answer). Common triggers:

| Parent answer | Dependent question to ask now |
|---|---|
| New compliance requirement added (LGPD/GDPR/HIPAA) | Does this also require a new AI guardrail — e.g. "always ask before logging or storing personal data"? |
| New Cross-Module Rule added | Does an existing AI guardrail or tech-stack decision need to reference this rule? |
| Tenancy model changed | Does this affect any existing Cross-Module Rule about shared resources? |

If any dependent question applies, ask it now via `AskUserQuestion` — **with a recommended answer, following the same rule as Step 3** — instead of leaving it implicit. Only questions whose parent decision itself remained undecided should still become an open item.

Run this check once. Proceed to Step 4 afterward regardless of whether a second round would still find more dependents — do not turn this into an unbounded loop.

### Step 3.6 — Final Consistency Check

Before applying any changes, check whether what was confirmed in Steps 3 and 3.5 contradicts anything in the **existing constitution content that is not being changed** (read in Step 1). Scan for contradiction only — the constitution has no separate validate skill, so this is the only check that runs before the update (and the regenerated rules files) become active project-wide.

Known contradiction shapes to check for:

| New/changed decision | Existing untouched content | Contradiction pattern |
|---|---|---|
| New or corrected rule | Untouched section of the same or another area | The new rule contradicts or silently supersedes an existing rule that wasn't marked as deprecated |
| New AI guardrail | Existing Global Tech Stack decision | The guardrail implies a technology choice the stack section doesn't list as permitted |
| Deprecated rule | Other rules referencing it | Another active rule still depends on the rule being deprecated |

If no contradiction is found, skip straight to the recap below.

**If a contradiction is found, do not silently resolve it.** Present it explicitly and wait:

> ⚠️ Possible contradiction: this update says "...", but the existing constitution (section X, untouched) says "...". Which should hold — or should section X also be updated as part of this change?

Once clear, present a short recap and require explicit confirmation before writing:

> Here's what I'm about to change: [sections in scope, one line each]. Everything else in the constitution stays as-is. Confirm before I apply this?

**STOP. Do not proceed to Step 4 until the user explicitly confirms.**

---

### Step 4 — Apply the Changes

When modifying `docs/constitution.md`:

1. **Preserve** all content not in scope
2. **Add** new rules, decisions, or constraints to the appropriate section
3. **Correct** wrong information in place
4. **Deprecate** removed rules with `~~strikethrough~~` and a note — never delete prior rules. Add a reference to the replacement if one exists:

```markdown
~~**Rule name:** old rule text~~ *(deprecated — superseded by: new rule name)*
```

5. **Update** the `Last Updated` date in the metadata header
6. **Increment** the version (if the constitution has one):
   - Patch bump for wording corrections or minor clarifications
   - Minor bump for new rules, updated decisions, or deprecated constraints
7. **Append** a changelog entry at the end of the file:

```markdown
| <date> | <summary of what changed> | <motivation — compliance, new decision, correction...> |
```

---

### Step 5 — Regenerate `.claude/rules/00-project-constitution.md`

After updating `docs/constitution.md`, regenerate the rules from the updated sections 2, 3, and 4.

Extract only **concrete, actionable directives** — not prose. Follow the same section grouping as the original generation:

- **Project Context** — a 1–2 sentence directive summarizing what the project is and its compliance context, plus the fixed bullet: "These rules take precedence over all module-specific arch rules."
- **Global Stack Constraints**
- **Cross-Module Constraints**
- **AI Guardrails — Stop and Ask Before Deciding**

Omit any section that has no active rules (after deprecations). The file must reflect only the current active state of the constitution — no deprecated rules.

Re-render these sections into the canonical rules file and every cross-tool destination as described in `../pragmatic-project-constitution/references/cross-tool-rules-sync.md`, using `slug=project-constitution`, `title=Project Constitution Rules`, `source_path=docs/constitution.md`, `always_apply=true`, `claude_rules_filename=00-project-constitution.md`. This cascades the update to every destination previously synced by `pragmatic-project-constitution` — do not write `.claude/rules/00-project-constitution.md` directly, it is a symlink to the canonical `.agents/rules/project-constitution.md` file.

---

### Step 6 — Output Summary

Report:
1. Which sections were changed and what was added, corrected, or deprecated
2. The updated `Last Updated` date and new version (if applicable)
3. Confirmation that `.claude/rules/00-project-constitution.md` and every cross-tool destination (`AGENTS.md`, `.cursor/rules/project-constitution.mdc`, `.windsurf/rules/project-constitution.md`, `.github/copilot-instructions.md`, and `GEMINI.md` if present) were regenerated

State:

> **These changes are now active.** Claude Code will load the updated rules from `.claude/rules/00-project-constitution.md` at the start of every future session. All `pragmatic-spec-create`, `pragmatic-arch-spec-create`, and `pragmatic-spec-build` runs will use the updated constraints.

---

## Output Locations

```
docs/constitution.md                              ← updated governance document
.claude/rules/00-project-constitution.md          ← regenerated from updated sections 2, 3, 4
AGENTS.md                                         ← Codex CLI, Antigravity, and most other agentic tools
.cursor/rules/project-constitution.mdc            ← Cursor
.windsurf/rules/project-constitution.md           ← Windsurf
.github/copilot-instructions.md                   ← GitHub Copilot
GEMINI.md                                         ← Gemini CLI / Antigravity, only if the file already exists
```

## Key Invariants

- **Never delete** prior rules — deprecate with `~~strikethrough~~`
- **Always regenerate** `.claude/rules/00-project-constitution.md` after any change — a stale rules file is worse than no update
- **Always confirm scope** before writing — a constitution change is project-wide; its effects are broader than any single spec
