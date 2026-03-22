---
name: spec.validate
description: This skill should be used when the user asks to "validate a spec", "check if this spec is complete", "review the spec for completeness", "is this spec good?", "check the spec quality", "review this specification", "audit the spec", or wants a structured quality review of an existing specification document.
---

# spec.validate

Validate a technical specification for completeness, clarity, and consistency.

## Purpose

Run a structured review of a spec document and produce a PASS/WARN/FAIL report. Do not modify the spec — only report findings with actionable suggestions.

## When This Skill Applies

Use this skill when a spec **already exists** and the user wants a quality assessment without modifying it.

**Do not use when:**
- No spec exists yet → use `spec.create`
- The user wants to apply changes to an existing spec → use `spec.update`

**Edge case:** if the user says "review the spec" but also wants edits applied, clarify intent before proceeding: "Do you want a quality report only, or should I apply fixes as well?"

## How to Validate a Spec

### Step 0 — Language Selection

**This is a mandatory first step.** Use `AskUserQuestion` to ask the user which language they want the validation report generated in:

```
In which language would you like the validation report to be generated?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and use it for **all report content** — section headings, check descriptions, notes, and recommended actions. Do not proceed to the next step until the language is confirmed.

### Step 1 — Locate and Read the Spec

Find the spec file. Common locations: `docs/specs/`, `specs/`, or the path provided. Read the full document before running any checks.

### Step 2 — Run Validation Checks

Evaluate each criterion below. Report **PASS**, **WARN**, or **FAIL** with a short explanation for each.

#### Completeness
- **Title & Status** — Has a clear title and a defined status (Draft/Review/Approved)
- **Problem Statement** — Clearly describes the problem being solved
- **Goals defined** — At least one goal is stated
- **Non-goals defined** — Explicitly states what is out of scope
- **Proposed Solution** — Describes the approach at a high level
- **Acceptance Criteria** — Has at least 2 testable acceptance criteria
- **No unresolved TODOs** — No `[TODO: ...]` placeholders remain (WARN if present)

#### Clarity
- **Unambiguous language** — No vague terms like "fast", "good", "easy" without measurable definitions
- **Acronyms defined** — All non-obvious acronyms are explained on first use
- **Consistent terminology** — Key terms are used consistently throughout

#### Consistency
- **Criteria are testable** — Each acceptance criterion can be objectively verified
- **Interface matches design** — If APIs/interfaces are defined, they align with the described behavior
- **No contradictions** — Goals do not contradict the proposed solution or acceptance criteria

#### Technology Decisions
- **Technology Decisions section present** — Spec contains an explicit Technology Decisions table or equivalent section
- **No implicit technology assumptions** — Mentions of databases, queues, caches, or frameworks are backed by an explicit decision, not just assumed
- **Undecided items flagged** — Any `[TODO: decide — options: ...]` items are listed in Open Questions so they are visible and actionable
- **Rationale captured** — Each technology decision includes at least a brief reason (or references team convention / existing stack)

#### Technical
- **Dependencies identified** — External dependencies and integrations are listed
- **Breaking changes flagged** — Any breaking changes are explicitly noted
- **Security considerations addressed** — Security implications are at least mentioned

### Step 3 — Generate Validation Report

Produce the report in this format:

```
## Spec Validation Report
**File:** <file path>
**Date:** <today>
**Overall Status:** PASS | WARN | FAIL

### Summary
- Passed:   X checks
- Warnings: X checks
- Failed:   X checks

### Details
| Check | Status | Notes |
|-------|--------|-------|
| Title & Status | PASS | |
| Problem Statement | WARN | Section exists but is vague |
| ... | | |

### Recommended Actions
1. <action item>
2. <action item>
```

### Output Rules

- Print the full report; do **not** modify the spec file
- List FAILs first with concrete suggestions for each
- If all checks pass, summarize the spec's strengths
