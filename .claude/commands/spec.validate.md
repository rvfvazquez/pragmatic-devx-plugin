# spec.validate

Validates a technical specification for completeness, clarity, and consistency.

## Usage

```
/spec.validate <spec-file-path>
```

## Instructions

You are a rigorous technical reviewer. Your task is to validate a specification document against quality and completeness standards.

**Input:** $ARGUMENTS

### Step 1 — Locate and Read the Spec

Find and read the specification file provided. Common locations:
- `docs/specs/`
- `specs/`
- Any `.md` file matching the provided path or name

### Step 2 — Run Validation Checks

Evaluate the spec against the following criteria. For each check, report PASS, WARN, or FAIL with a short explanation.

#### Completeness Checks
- [ ] **Title & Status** — Has a clear title and a defined status (Draft/Review/Approved)
- [ ] **Problem Statement** — Clearly describes the problem being solved
- [ ] **Goals defined** — At least one goal is stated
- [ ] **Non-goals defined** — Explicitly states what is out of scope
- [ ] **Proposed Solution** — Describes the approach at a high level
- [ ] **Acceptance Criteria** — Has at least 2 testable acceptance criteria
- [ ] **No unresolved TODOs** — No `[TODO: ...]` placeholders remain (WARN if present)

#### Clarity Checks
- [ ] **Unambiguous language** — No vague terms like "fast", "good", "easy" without measurable definitions
- [ ] **Acronyms defined** — All non-obvious acronyms are explained on first use
- [ ] **Consistent terminology** — Key terms are used consistently throughout the document

#### Consistency Checks
- [ ] **Criteria are testable** — Each acceptance criterion can be objectively verified
- [ ] **Interface matches design** — If API/interfaces are defined, they align with the described behavior
- [ ] **No contradictions** — Goals do not contradict the proposed solution or acceptance criteria

#### Technical Checks
- [ ] **Dependencies identified** — External dependencies and integrations are listed
- [ ] **Breaking changes flagged** — Any breaking changes are explicitly noted
- [ ] **Security considerations addressed** — Security implications are at least mentioned

### Step 3 — Generate Validation Report

Produce a structured report in this format:

```
## Spec Validation Report
**File:** <file path>
**Date:** <today>
**Overall Status:** PASS | WARN | FAIL

### Summary
- Passed: X checks
- Warnings: X checks
- Failed: X checks

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

### Output Instructions

1. Print the full validation report in the terminal
2. Do **not** modify the spec file — only report findings
3. If the spec passes all checks, congratulate with a summary of its strengths
4. If there are FAILs, list them first and provide concrete suggestions for each
