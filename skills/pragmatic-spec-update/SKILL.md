---
name: pragmatic-spec-update
description: This skill should be used when the user asks to "update a spec", "update this specification", "revise the spec", "add requirements to the spec", "change the spec", "fill in the TODOs in the spec", "correct the spec", or wants to apply new decisions, corrections, or requirements to an existing specification document.
---

# pragmatic-spec-update

Update an existing technical specification with new requirements, corrections, or decisions.

## Purpose

Evolve a spec document safely — preserving existing content, versioning changes, and appending a changelog. Never overwrite history; mark removed content as deprecated rather than deleting it.

## When This Skill Applies

Use this skill when a spec **already exists** and needs to evolve — new requirements, corrections, resolved TODOs, or decisions made after the spec was written.

**Do not use when:**
- No spec exists yet → use `pragmatic-spec-create`
- The user only wants a quality assessment without changes → use `pragmatic-spec-validate`

**Edge case:** if the user wants to "completely rewrite" an existing spec, clarify whether they want section-by-section updates (`pragmatic-spec-update`) or a full replacement starting from scratch (`pragmatic-spec-create` over the existing file).

## How to Update a Spec

### Step 0 — Language Detection

Infer the output language from the existing spec:
1. If the spec contains a `Language:` metadata field, use it
2. Otherwise, infer from the majority language of prose content in sections 2, 3, and 4 (Problem Statement, Goals, Proposed Solution) — if ≥80% of prose words are attributable to a single language, use that language
3. If the spec contains no prose (only tables and code blocks), or if no single language reaches the 80% threshold, treat as ambiguous and use `AskUserQuestion`:

```
In which language would you like the spec updates to be written?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and apply it consistently to **all new or modified content** — section text, changelog entries, TODO comments, and any new acceptance criteria. Existing content that is not being changed should remain in its original language.

### Pre-condition — Check Spec Status

After locating the spec, check its `Status` field before proceeding.

If `Status: Approved`:
> "This spec is in **Approved** status. Modifying it may invalidate existing conformance checks. Confirm this update is intentional — and consider whether the status should be downgraded to Review as part of this change."

**STOP. Do not apply changes to an Approved spec until the user explicitly confirms the update is intentional.**

---

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

### Step 3 — Confirm Scope, Intent, and Technology Decisions

**This is a mandatory step.** Do not apply any changes until the full scope, intent, and open technology decisions are confirmed.

After analyzing the spec and the requested change, use `AskUserQuestion` to confirm your understanding with the user. Cover scope, motivation, and technology decisions in a single round.

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

[Include the following block only if the spec has open [TODO: decide — ...] items OR if the
 requested change introduces new technology decisions. Omit for purely textual updates.]

**Technology Decisions**
- This spec has unresolved technology decisions. Let's lock them in — every item carries a
  recommended answer (➡️), derived in this priority order: (1) decisions already made elsewhere
  in this spec or in the constitution, (2) patterns evident in the codebase, (3) a pragmatic
  default stated as such:
  [TODO item 1 — e.g. Data storage] Options: A, B, C — which do you want, or keep open?
    ➡️ A — consistent with the storage choice already made in section 5
  [TODO item 2 — e.g. Async processing] Options: SQS, background job, synchronous — which?
    ➡️ Synchronous — no fan-out described in this update; flag if that's wrong
- [If the requested change implies new tech choices, ask about them here, with the same ➡️ rule]

Answer what you know, or just confirm the ➡️ recommendation — for anything undecided, I'll leave it as an open item.
```

Do not proceed to Step 4 until:
- The exact scope of the change is confirmed
- The motivation is understood
- Sections to preserve vs. modify are clear
- All technology decisions that can be resolved have been addressed

### Step 3.5 — Follow-up Round for Dependent Decisions

After the user answers Step 3, check whether any answer unlocks a **dependent decision** that could not have been asked before it (its options only make sense given the parent answer). Common triggers:

| Parent answer | Dependent question to ask now |
|---|---|
| Queue (SQS/RabbitMQ/etc.) | Which queue? FIFO or standard? Dead-letter queue needed? |
| REST endpoint | Sync or paginated response? Rate limiting? |
| JWT / OAuth | Token lifetime? Refresh flow? Which claims are required? |
| Background job | Retry policy? Max attempts? Idempotency key strategy? |

If any dependent question applies, ask it now via `AskUserQuestion` — **with a recommended answer, following the same rule as Step 3** — instead of deferring it straight to a new `[TODO: decide]`. Only questions whose parent decision itself remained undecided should still become TODOs.

Run this check once. A second round should not itself spawn a third round unless the update is unusually deep — if it does, proceed to Step 4 anyway and leave the remainder as TODOs rather than turning the confirmation into an unbounded loop.

### Step 3.6 — Final Consistency Check

Before applying any changes, check whether what was confirmed in Steps 3 and 3.5 contradicts anything in the **existing spec content that is not being changed** (read in Step 1) — not just the answers gathered this session. Scan for contradiction only, not completeness — that is `pragmatic-spec-validate`'s job.

Known contradiction shapes to check for:

| New/changed decision | Existing untouched content | Contradiction pattern |
|---|---|---|
| New Technology Decision | Non-Goals or Constraints (unchanged) | The new choice implements something explicitly marked out of scope |
| New or corrected Acceptance Criterion | Existing Acceptance Criteria | The new criterion contradicts or supersedes one that wasn't marked for change |
| New scope item | "Related Sections to Cascade" answer | A section the user said would NOT cascade actually depends on the change |

If no contradiction is found, skip straight to the recap below.

**If a contradiction is found, do not silently resolve it.** Present it explicitly and wait:

> ⚠️ Possible contradiction: this update says "...", but the existing spec (section X, untouched) says "...". Which should hold — or should section X also be updated as part of this change?

Once clear, present a short recap and require explicit confirmation before writing:

> Here's what I'm about to change: [sections in scope, one line each]. Everything else in the spec stays as-is. Confirm before I apply this?

**STOP. Do not proceed to Step 4 until the user explicitly confirms.**

### Step 4 — Apply the Changes

When modifying the spec:

1. **Preserve** all content not being changed
2. **Update diagrams when their source sections change** — a diagram must always reflect the current state of the spec. If the change affects section 6.1 (API/Interface), 6.2 (Data Model), or 6.3 (Behavior & Logic), review any diagrams in those sections and update them in the same edit. Never leave a diagram describing behavior the spec has moved away from.
3. **Update** the `Status` field if appropriate (e.g., Draft → Review)
4. **Increment** the `Version` field:
   - Patch bump (`1.0.0` → `1.0.1`) for minor corrections or clarifications
   - Minor bump (`1.0.0` → `1.1.0`) for significant new requirements or design changes
5. **Deprecate** removed content with `~~strikethrough~~` rather than deleting it, unless it is clearly obsolete noise
6. **Append** a changelog entry at the **end of the file**, after section 9 (Open Questions):

```markdown
---
## Changelog

### v<new-version> — <date>
- <summary of changes made>
```

### Step 5 — Validate After Update

After applying changes, verify:
- All `[TODO: ...]` items that were addressed are now resolved
- No section is left inconsistent with the changes applied
- Acceptance criteria still reflect the updated solution
- Version and status fields are updated

### Step 6 — Output Summary

Report:
1. A concise summary of what was changed
2. Any remaining `[TODO: ...]` items still present in the document
3. Sections that may need human review due to the changes

> **Spec updated** — `docs/specs/<feature-slug>.md`.
>
> **Next step:** Run `pragmatic-spec-validate` to verify the updated spec is still sound and consistent.
