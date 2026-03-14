---
name: spec.validate
description: This skill should be used when the user asks to "validate a spec", "check if this spec is complete", "review the spec for completeness", "is this spec good?", "check the spec quality", "review this specification", "audit the spec", or wants a structured quality review of an existing specification document.
version: 0.1.0
---

# spec.validate

Validate a technical specification for completeness, clarity, and consistency.

## Purpose

Run a structured review of a spec document and produce a PASS/WARN/FAIL report. Do not modify the spec — only report findings with actionable suggestions.

## When This Skill Applies

Apply when a spec exists and the user wants to know if it's ready:

- "Validate docs/specs/auth.md"
- "Is this spec ready for review?"
- "Check the payment spec for completeness"
- "Run a quality check on this specification"

## How to Validate a Spec

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
