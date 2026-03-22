---
name: spec.update
description: This skill should be used when the user asks to "update a spec", "update this specification", "revise the spec", "add requirements to the spec", "change the spec", "fill in the TODOs in the spec", "correct the spec", or wants to apply new decisions, corrections, or requirements to an existing specification document.
---

# spec.update

Update an existing technical specification with new requirements, corrections, or decisions.

## Purpose

Evolve a spec document safely — preserving existing content, versioning changes, and appending a changelog. Never overwrite history; mark removed content as deprecated rather than deleting it.

## When This Skill Applies

Use this skill when a spec **already exists** and needs to evolve — new requirements, corrections, resolved TODOs, or decisions made after the spec was written.

**Do not use when:**
- No spec exists yet → use `spec.create`
- The user only wants a quality assessment without changes → use `spec.validate`

**Edge case:** if the user wants to "completely rewrite" an existing spec, clarify whether they want section-by-section updates (`spec.update`) or a full replacement starting from scratch (`spec.create` over the existing file).

## How to Update a Spec

### Step 0 — Language Selection

**This is a mandatory first step.** Use `AskUserQuestion` to ask the user which language they want the updated content to be written in:

```
In which language would you like the spec updates to be written?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and apply it consistently to **all new or modified content** — section text, changelog entries, TODO comments, and any new acceptance criteria. Existing content that is not being changed should remain in its original language. Do not proceed to the next step until the language is confirmed.

### Step 1 — Locate the Spec

Find the spec file from the user's context. Common locations:
- `docs/specs/`
- `specs/`
- Any `.md` file matching the provided name or path

Read the full file and understand its current content and structure.

### Step 2 — Understand the Change

Analyze what needs to change:
- If a description is provided, identify the relevant sections
- If no description is given, scan for `[TODO: ...]` placeholders
- Map which sections are directly affected and which may be indirectly impacted (a change to the data model may also affect the API and acceptance criteria)

### Step 2.5 — Confirm Scope and Intent Before Proceeding

**This is a mandatory step.** Do not apply any changes until the full scope and intent of the update is clear.

After analyzing the spec and the requested change, use `AskUserQuestion` to confirm your understanding with the user. The goal is to have a complete picture of what is changing, why, and what should remain untouched — before writing anything.

Ask only what is genuinely unclear. Adapt the questions to the specific update.

**`multiSelect` rules for this step — always follow these:**
- **Sections in scope**: `multiSelect: true` — multiple spec sections may need updating
- **Related sections to cascade**: `multiSelect: true` — changes often ripple across multiple sections
- **Expected outcomes**: `multiSelect: true` — the update may achieve several things at once

Example format:

```
Before I apply any changes, let me confirm my understanding of this update:

**What I understood**
- [Restate the change as you interpreted it — ask the user to confirm or correct]

**Scope of the Update** → multiSelect: true
- Which sections of the spec are explicitly in scope for this change?
  Options: Problem Statement, Goals/Non-Goals, Proposed Solution, Technology Decisions,
           API/Interface, Data Model, Behavior & Logic, Acceptance Criteria, Open Questions

**Related Sections to Cascade** → multiSelect: true
- Are there related sections that should also be updated as a result?
  (e.g., if the API changes → should Acceptance Criteria also change?)

**Motivation**
- What triggered this change? (new requirement, correction, new decision, implementation feedback)
- Does this change deprecate or supersede any existing decision in the spec?

**Expected Outcome** → multiSelect: true
- After this update, what should the spec reflect that it doesn't today? (select all that apply)
  Options: new requirement captured, TODO resolved, incorrect info corrected,
           acceptance criteria updated, status/version bumped

Answer what you know — for anything undecided, I'll leave it as an open item.
```

Do **not** proceed to Step 2.6 until:
- The exact scope of the change is confirmed
- The motivation is understood
- Sections to preserve vs. modify are clear

### Step 2.6 — Resolve Technology TODOs via Interview

**Before writing any changes**, check if any open `[TODO: decide — options: ...]` items exist in the Technology Decisions section or elsewhere in the spec.

If yes, use `AskUserQuestion` to ask the user to decide each one. Present the options explicitly so the user can choose:

```
This spec has some unresolved technology decisions. Let's lock them in:

**[TODO item 1 — e.g. Data storage]**
Options: A, B, C
Which do you want to go with, or should it stay open?

**[TODO item 2 — e.g. Async processing]**
Options: SQS, background job, synchronous
Which do you prefer?
```

Do not assume a default. If the user says "undecided" or "keep open", leave the `[TODO]` in place.

Also ask about technology choices implied by new requirements that the user described but didn't specify:
- If a new caching requirement is added, ask: "What cache backend? Options: Redis, Memcached, in-process, CloudFront"
- If a new queue is needed, ask: "Which queue? Options: SQS, RabbitMQ, existing queue, other"

Only skip this step if the update is purely textual (wording corrections, status changes) with no new technical decisions.

### Step 3 — Apply the Changes

When modifying the spec:

1. **Preserve** all content not being changed
2. **Update** the `Status` field if appropriate (e.g., Draft → Review)
3. **Increment** the `Version` field:
   - Patch bump (`1.0.0` → `1.0.1`) for minor corrections or clarifications
   - Minor bump (`1.0.0` → `1.1.0`) for significant new requirements or design changes
4. **Deprecate** removed content with `~~strikethrough~~` rather than deleting it, unless it is clearly obsolete noise
5. **Append** a changelog entry at the end of the document:

```markdown
---
## Changelog

### v<new-version> — <date>
- <summary of changes made>
```

### Step 4 — Validate After Update

After applying changes, verify:
- All `[TODO: ...]` items that were addressed are now resolved
- No section is left inconsistent with the changes applied
- Acceptance criteria still reflect the updated solution
- Version and status fields are updated

### Step 5 — Output Summary

Report:
1. A concise summary of what was changed
2. Any remaining `[TODO: ...]` items still present in the document
3. Sections that may need human review due to the changes
