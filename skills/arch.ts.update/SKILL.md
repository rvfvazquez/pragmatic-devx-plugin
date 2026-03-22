---
name: arch.ts.update
description: This skill should be used when the user asks to "update an architecture spec", "revise the arch spec", "update this architecture document", "add a new ADR", "change the component boundaries", "fill in the TODOs in the arch spec", "correct the architecture spec", or wants to apply new decisions, corrections, or intentional deviations to an existing architecture technical specification document.
version: 0.1.0
---

# arch.ts.update

Update an existing architecture technical specification with new architectural decisions, corrections, or intentional deviations.

## Purpose

Evolve an arch spec safely — preserving existing ADRs, versioning changes, and appending a changelog. Never overwrite prior decisions; mark superseded ADRs as deprecated rather than deleting them. This skill is the natural next step when `arch.ts.check` identifies a violation that is resolved via **Option B** (the code reflects an intentional evolution the spec has not yet captured).

## When This Skill Applies

Apply whenever an arch spec already exists and needs to change:

- "The payments arch spec needs to reflect the new event-driven boundary"
- "We decided to use the anti-corruption layer — update the arch spec"
- "The auth module no longer depends on the user service directly, update the spec"
- "Add an ADR for the caching decision we made"
- "Fill in the TODOs in the notification arch spec"
- Option B was chosen after running `arch.ts.check`

## Lifecycle Position

```
arch.ts.create → arch.ts.validate → arch.ts.check → [arch.ts.update] → arch.ts.check
```

Use this skill when the arch spec needs to catch up with the implemented code, or when a new architectural decision must be formally recorded.

## How to Update an Architecture Spec

### Step 0 — Language Selection

**This is a mandatory first step.** Use `AskUserQuestion` to ask the user which language they want the updated content written in:

```
In which language would you like the arch spec updates to be written?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and apply it consistently to **all new or modified content** — ADR text, component descriptions, changelog entries, and TODO comments. Existing content that is not being changed should remain in its original language. Do not proceed to the next step until the language is confirmed.

### Step 1 — Locate the Arch Spec

Find the architecture spec file from the user's context. Common location: `docs/arch/*.arch.md`.

Read the full document and understand:
- Current status and version
- Existing ADRs and their decisions
- Component boundaries and dependency rules
- Any `[TODO: ...]` items already present

### Step 2 — Understand the Change

Analyze what needs to change:
- Is this a **new ADR** (a decision not previously documented)?
- Is this an **update to component boundaries** (responsibilities, public interfaces, dependency direction)?
- Is this a **correction** to existing content (wrong information, outdated constraint)?
- Is this resolving a **[TODO: ...]** placeholder?
- Is this capturing an **intentional deviation** identified by `arch.ts.check`?

Map which sections are directly affected and which may be indirectly impacted — a change to a component boundary may also affect dependency direction rules, data flow descriptions, and NFRs.

### Step 2.5 — Confirm Scope and Intent Before Proceeding

**This is a mandatory step.** Do not apply any changes until the full scope and intent of the update is clear.

After analyzing the spec and the requested change, use `AskUserQuestion` to confirm your understanding:

**`multiSelect` rules for this step — always follow these:**
- **Sections in scope**: `multiSelect: true` — multiple spec sections may need updating
- **Related sections to cascade**: `multiSelect: true` — changes often ripple across multiple sections
- **Expected outcomes**: `multiSelect: true` — the update may achieve several things at once

```
Before I apply any changes, let me confirm my understanding of this update:

**What I understood**
- [Restate the change as you interpreted it — ask the user to confirm or correct]

**Sections in Scope** → multiSelect: true
Which sections of the arch spec are explicitly changing?
- ADRs (new decision, updated rationale, or superseded decision)
- Component Boundaries (responsibilities, public interfaces)
- Dependency Direction (allowed/forbidden dependencies)
- Architecture Patterns (naming conventions, communication style, error strategy)
- Data Flows (new or changed flow)
- External Integrations (new or changed integration)
- NFRs / Constraints (new non-functional requirement or constraint)
- Open Decisions / TODOs (resolving a placeholder)

**Related Sections to Cascade** → multiSelect: true
Are there sections that should also be updated as a consequence?
(e.g., if a component boundary changes → dependency direction rules may also change)

**Motivation**
- What triggered this change? (new decision, intentional deviation found in code, correction, requirement change)
- Does this supersede any existing ADR or architectural decision?

**Expected Outcome** → multiSelect: true
After this update, what should the spec reflect that it doesn't today?
- New ADR captured
- Intentional deviation now documented
- Component boundary corrected
- TODO resolved
- Outdated decision deprecated
- Version/status bumped
```

Do **not** proceed to Step 2.6 until:
- The exact sections in scope are confirmed
- The motivation is understood
- Whether any existing ADR is superseded is clear

### Step 2.6 — Capture ADR Details for New Decisions

**Apply this step when the update includes a new or updated ADR.**

Use `AskUserQuestion` to ensure the ADR is fully documented:

```
To document this architectural decision properly, I need a few more details:

**Decision**
- What was decided? (state the choice made, not the options)

**Options Considered**
- What alternatives were evaluated before this decision?

**Rationale**
- Why was this option chosen over the alternatives?
- What constraints, quality attributes, or trade-offs drove this decision?

**Consequences**
- What are the known trade-offs or downsides of this decision?
- What becomes easier or harder as a result?

If any of these are unknown or still being debated, I'll mark them as open items.
```

Only skip this step if the update contains no new architectural decisions (e.g., pure wording corrections or TODO resolution with already-known content).

### Step 3 — Apply the Changes

When modifying the arch spec:

1. **Preserve** all content not being changed
2. **Update** the `Status` field if appropriate (e.g., Draft → Review → Approved)
3. **Increment** the `Version` field:
   - Patch bump (`1.0.0` → `1.0.1`) for wording corrections, TODO resolution, or minor clarifications
   - Minor bump (`1.0.0` → `1.1.0`) for new ADRs, updated component boundaries, or new integrations
   - Major bump (`1.0.0` → `2.0.0`) for fundamental architecture changes (e.g., new dependency direction, major component restructuring)
4. **Deprecate** superseded ADRs — mark them with `~~strikethrough~~` and add a note referencing the new decision. Never delete prior ADRs.
5. **Append** a changelog entry at the end of the document:

```markdown
---
## Changelog

### v<new-version> — <date>
- <summary of changes — e.g., "Added ADR-05: caching strategy", "Updated boundary for PaymentProcessor component">
```

### Step 4 — Validate Consistency After Update

After applying changes, verify:
- All `[TODO: ...]` items that were addressed are now resolved
- ADR references within the document are consistent (no orphan references)
- Component names used in dependency rules match the updated component boundaries table
- Dependency direction rules are consistent with the updated component structure
- No section is left contradicting the changes applied

### Step 5 — Output Summary and Next Steps

Report:
1. A concise summary of what was changed
2. Any remaining `[TODO: ...]` items still present in the document
3. Sections that may need human review due to the changes

**Next step:** run `arch.ts.check` to verify the updated spec now correctly reflects the implemented code.
