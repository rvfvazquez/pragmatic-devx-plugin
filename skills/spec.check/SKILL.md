---
name: spec.check
description: This skill should be used when the user asks to "verify if the implementation follows the spec", "check conformance with the spec", "is the code aligned with the spec?", "audit implementation against the spec", "check if the acceptance criteria were implemented", "does the code match the spec", or wants to compare an existing implementation against a specification document.
---

# spec.check

Verify that an existing implementation conforms to its technical specification.

## Purpose

Produce a structured conformance report organized by three independent dimensions — acceptance criteria coverage, structural adherence, and open items resolved. Does not modify code or spec; only reports findings and recommends actions with explicit direction (fix in code or use `spec.update`).

## When This Skill Applies

Use this skill when a spec **and** an implementation both exist and the user wants to verify alignment between them.

**Do not use when:**
- No spec exists yet → use `spec.create`
- The user only wants to assess spec document quality → use `spec.validate`
- The user wants to apply changes to an existing spec → use `spec.update`

## How to Run a Conformance Check

### Step 0 — Language Detection

Infer the report language from the existing spec:
1. If the spec contains a `Language:` metadata field, use it
2. Otherwise, infer from the majority language of prose content in sections 2, 3, and 4 — if ≥80% of prose words are attributable to a single language, use that language
3. If no prose exists or no language reaches 80%, use `AskUserQuestion` to ask

### Step 1a — Identify the Spec

Determine the spec path from:
1. User-provided path in their message
2. File open in IDE context
3. Conversation context (recently mentioned spec)

If none of the above is available, use `AskUserQuestion` to ask. If multiple specs exist in `docs/specs/` and none was specified, list them and ask the user to select.

### Step 1b — Locate the Implementation

1. Extract the feature slug from the spec filename (e.g., `auth.md` → `auth`)
2. Search common paths: `src/<slug>/`, `internal/<slug>/`, `pkg/<slug>/`, `lib/<slug>/`, `<slug>/` at repo root
3. If exactly one match is found with high confidence → proceed
4. If multiple candidates are found → `AskUserQuestion` listing the candidates, asking the user to select
5. If nothing is found → `AskUserQuestion` asking the user to specify the implementation path

### Step 2 — Extract Verifiable Elements

Before scanning code, map everything that will be verified:
- **Acceptance criteria** — all items from section 7
- **Interfaces, structs, type definitions, endpoints** — from sections 6.1 and 6.2
- **Open TODOs** — all `[TODO: ...]` items from any section

If sections 6.1 and 6.2 are absent or contain no verifiable elements → mark Dimension 2 as `N/A`.
If no open `[TODO: ...]` items exist in the spec → mark Dimension 3 as `N/A`.

### Step 3 — Scan Implementation

For each element extracted in Step 2:

- **Acceptance criteria** → search test files (`*_test.go`, `*.test.ts`, `*.spec.ts`, `*.test.py`, `*_test.py`, `*Test.java`, etc.) for test cases that exercise the criterion. A criterion is PASS if a test clearly covers it, WARN if only indirectly covered, FAIL if no test is found.

- **Interfaces, structs, endpoints** → search source files for type definitions, function signatures, and route registrations. PASS if matches spec exactly, WARN if present but deviates in a minor way (with details), FAIL if not found.

- **Open TODOs** → search source files and config files for evidence of resolution (a decision implemented, a comment resolving the question). PASS if clear evidence found, WARN if partial or ambiguous, FAIL if no evidence found.

> **Scope note:** Scanning is limited to current code files (source, test, config). Git commit history is not scanned — that is a future enhancement.

### Step 4 — Generate Conformance Report

See `references/report-format.md` for the annotated format. The report structure is:

```
## Spec Conformance Report
**Spec:** <file path>
**Implementation:** <directory>
**Date:** <today>
**Overall Status:** PASS | WARN | FAIL

### Summary
- Passed:   X checks
- Warnings: X checks
- Failed:   X checks
- N/A:      X checks (not counted in totals above)

### Dimension 1 — Acceptance Criteria Coverage
**Status:** PASS | WARN | FAIL

| Criterion | Status | Finding |
|-----------|--------|---------|

### Dimension 2 — Structural Adherence
**Status:** PASS | WARN | FAIL | N/A

| Element | Status | Finding |
|---------|--------|---------|

> N/A when sections 6.1 and 6.2 are absent or contain no verifiable elements.

### Dimension 3 — Open Items Resolved
**Status:** PASS | WARN | FAIL | N/A

| TODO | Status | Finding |
|------|--------|---------|

> N/A when the spec has no open [TODO: ...] items.

### Recommended Actions
1. [FAIL][code] ...
2. [FAIL][spec.update] ...
3. [WARN][code] ...
```

**Status aggregation rules:**

Per-dimension:
- `FAIL` if any row in that dimension is FAIL
- `WARN` if any row is WARN and none are FAIL
- `PASS` if all rows are PASS
- `N/A` if the dimension has no elements to check

Overall Status:
- `FAIL` if any evaluated dimension is FAIL
- `WARN` if any evaluated dimension is WARN and none are FAIL
- `PASS` if all evaluated dimensions are PASS or N/A

**Finding column:** Always populate, even for passing rows (e.g., cite the test file and line number). Empty findings are not acceptable.

**Recommended Actions rules:**
- FAILs listed before WARNs
- Each action is tagged `[code]` (fix belongs in the implementation) or `[spec.update]` (decision or clarification needed in the spec)
- N/A checks are not counted in Summary totals
- If all dimensions are PASS or N/A: omit Recommended Actions and output a **Strengths** section summarizing what was verified and confirmed correct

## Additional Resources

- **`references/report-format.md`** — Annotated report format with inline explanations of each field
- **`examples/example-auth-check.md`** — Worked conformance check example against the JWT authentication spec
