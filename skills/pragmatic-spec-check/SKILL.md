---
name: pragmatic-spec-check
description: This skill should be used when the user asks to "verify if the implementation follows the spec", "check conformance with the spec", "is the code aligned with the spec?", "audit implementation against the spec", "check if the acceptance criteria were implemented", "does the code match the spec", or wants to compare an existing implementation against a specification document.
---

# pragmatic-spec-check

Verify that an existing implementation conforms to its technical specification.

## Purpose

Produce a structured conformance report organized by four independent dimensions — acceptance criteria coverage, structural adherence, open items resolved, and domain language alignment. Does not modify code or spec; only reports findings and recommends actions with explicit direction (fix in code or use `pragmatic-spec-update`).

## When This Skill Applies

Use this skill when a spec **and** an implementation both exist and the user wants to verify alignment between them.

**Do not use when:**
- No spec exists yet → use `pragmatic-spec-create`
- The user only wants to assess spec document quality → use `pragmatic-spec-validate`
- The user wants to apply changes to an existing spec → use `pragmatic-spec-update`

## How to Run a Conformance Check

### Pre-condition — Verify Spec Readiness

After identifying the spec in Step 1a, check its `Status` field:
- If `Status: Draft` → assert: "This spec is in **Draft** status. Conformance results will be unreliable because the spec may be incomplete. Consider running `pragmatic-spec-validate` first."
- If the spec has open `[TODO: ...]` items → note their count upfront. Dimension 3 will evaluate them explicitly.

**STOP if the spec is in Draft status and the user has not explicitly confirmed they want to proceed anyway.**

---

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
2. First, detect the project layout by checking which top-level directories exist (e.g., `src/`, `app/`, `internal/`, `pkg/`, `lib/`, `packages/`). Then search the most likely paths for the slug:
   - General: `src/<slug>/`, `lib/<slug>/`, `<slug>/` at repo root
   - Go: `internal/<slug>/`, `pkg/<slug>/`
   - Rails/Django/Laravel: `app/<slug>/`, `app/models/`, `app/services/`
   - Java/Kotlin: `src/main/java/**/<slug>/`, `src/main/kotlin/**/<slug>/`
   - JavaScript/TypeScript monorepo: `packages/<slug>/`, `apps/<slug>/`
3. If exactly one match is found with high confidence → proceed
4. If multiple candidates are found → `AskUserQuestion` listing the candidates, asking the user to select
5. If nothing is found → `AskUserQuestion` asking the user to specify the implementation path

### Step 2 — Extract Verifiable Elements

Before scanning code, map everything that will be verified:
- **Acceptance criteria** — all items from section 7. Tag which ones are *security criteria*: a negative assertion about authorization, ownership, or rejected input (non-owner → `404`, unauthorized role → `403`, malformed input rejected).
- **Interfaces, structs, type definitions, endpoints** — from sections 6.1 and 6.2
- **Security controls** — each non-`N/A` entry in the section 8 Security item (authentication, authorization, untrusted-input validation, sensitive-data handling). Skip any control already fully expressed by a section 7 criterion — it is covered under Dimension 1.
- **Open TODOs** — all `[TODO: ...]` items from any section
- **Domain names** — if `docs/glossary/context-map.md` exists, call the Skill tool with `pragmatic-domain-language` (once per session — without a Skill tool, read `../pragmatic-domain-language/SKILL.md`), apply **§1 Locate the Context** without asking, and take from this spec's context, per **§5 Names in Code**: each term the spec uses, with its code identifier (`_In code_`, or the term itself) and its `_Avoid_` words

Mark Dimension 2 as `N/A` only if sections 6.1 and 6.2 are absent or contain no verifiable elements **and** the section 8 Security item has no applicable (non-`N/A`) entry.
If no open `[TODO: ...]` items exist in the spec → mark Dimension 3 as `N/A`.
If `docs/glossary/` does not exist → mark Dimension 4 as `N/A`.

### Step 3 — Scan Implementation

For each element extracted in Step 2:

- **Acceptance criteria** → search test files for test cases that exercise the criterion. Common patterns by language: Go (`*_test.go`, `*_integration_test.go`), TypeScript/JavaScript (`*.test.ts`, `*.spec.ts`, `*.test.js`, `**/__tests__/*`), Python (`*.test.py`, `*_test.py`, `test_*.py`, `tests/`), Java/Kotlin (`*Test.java`, `*Tests.java`, `*Test.kt`), Rust (`*_test.rs`, `tests/`), C# (`*Tests.cs`, `*Test.cs`), Ruby (`*_spec.rb`, `*_test.rb`), Scala (`*Spec.scala`, `*Suite.scala`). If the project's test naming convention is not in this list, detect it from existing test files before scanning. Record **Coverage** separately from **Execution**. Coverage is PASS if a non-stub test clearly asserts the criterion, WARN if only indirect, FAIL if no meaningful assertion is found. Finding a test never establishes that it passed.

  **Execution evidence:** detect the project's documented test command and run the relevant existing tests when execution is permitted and the environment is available. Do not install dependencies, start external services, or change source/tests/spec to obtain a green result. Respect inspection-only requests. Evidence must identify the command, working directory, outcome/exit code, and the tests actually selected; a successful process with zero selected tests or skipped matching tests is not a passing criterion. Existing evidence may be reused only when it identifies the current code/test revision, command and relevant passing cases; a stale Build Log or an implementer's unsupported claim is not evidence.

  Execution is `PASS` for relevant assertions observed passing, `FAIL` for a relevant assertion failure, `SKIPPED` when the relevant test did not execute, `NOT_RUN` when execution was not attempted/permitted or no current evidence exists, and `ERROR` for a setup/tool/environment failure that prevents evaluating the assertion. Report the reason for SKIPPED/NOT_RUN/ERROR; never label them PASS. Do not run a suite just to turn an inspection-only check green.

  The criterion's **Status** is FAIL if Coverage is FAIL or Execution is FAIL; otherwise WARN if Coverage is WARN or Execution is SKIPPED/NOT_RUN/ERROR; PASS only when both Coverage and Execution are PASS. Static-only reviews remain useful but cannot mark the story done. Test execution does not substitute for inspecting whether assertions cover the criterion.

- **Interfaces, structs, endpoints** → search source files for type definitions, function signatures, and route registrations. PASS if matches spec exactly, WARN if present but deviates in a minor way (with details), FAIL if not found.

- **Security controls** → for each section 8 Security entry mapped in Step 2, search source for the control on the relevant path: an auth middleware or guard (authentication), an ownership or role comparison against the caller identity before the resource is returned (authorization), request validation or a schema check (untrusted input), redaction or an allow-list in logging and a secrets-manager / env read (sensitive data). PASS if the control is present on the path, WARN if partial or ambiguous, FAIL if absent. Report these under Dimension 2. **Never reproduce a secret value found during this scan — cite file and line only.**

- **Open TODOs** → search source files and config files for evidence of resolution (a decision implemented, a comment resolving the question). PASS if clear evidence found, WARN if partial or ambiguous, FAIL if no evidence found.

- **Domain names** → in the implementation scope only, find the types, exported functions, endpoints, events, and test names that represent each glossary concept the spec uses. PASS if they use the term's code identifier. WARN if a concept is represented under a different name, or an identifier uses a word listed under the term's `_Avoid_` (the term's own code identifier is never a finding, even when it contains a word listed under `_Avoid_`) (cite file:line, the name found, and the expected identifier). A concept the code has no representation of is not a Dimension 4 finding — Dimensions 1 and 2 already cover missing behavior and types. Dimension 4 is **WARN at most, never FAIL**. Tag each action `[code]` (rename in code) or `[pragmatic-spec-update]` (the glossary's identifier should change instead).

- **Divergence (Contradictions & Unrequested Scope)** → search the implementation scope of this feature for code or tests that deviate from the approved intent:
  - **Contradictory behavior (`[contradicts]`)**: code or test assertions that directly violate a stated requirement, invariant, status code, or explicit non-goal (e.g. spec requires 401 on missing auth, but implementation allows anonymous pass-through or returns 200). Report under Dimension 2 as **FAIL** with Finding explaining the direct contradiction.
  - **Unrequested scope (`[unrequested]`)**: newly added public endpoints, exported methods, or significant capabilities inside the feature module that have no origin in the spec (neither in goals, interfaces, ACs, dependencies, nor legitimate scaffold).
    - **False-positive guard:** limit strictly to the feature's package/directory and files modified for this feature. Existing codebase files, legacy utilities, or pre-existing dependencies outside the feature boundary must **never** be flagged as unrequested.
    - Report under Dimension 2 as **WARN** (or **FAIL** if it directly implements a stated Non-goal). Action tagged `[code]` (remove unrequested code) or `[pragmatic-spec-update]` (update spec to formalize the scope addition).

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

| Criterion | Coverage | Execution | Status | Finding |
|-----------|----------|-----------|--------|---------|

### Test Execution Evidence
| Command / working directory | Outcome / exit code | Relevant tests | Revision / evidence |
|---|---|---|---|

> For inspection-only checks, record NOT_RUN and the reason instead of inventing a command result.

### Dimension 2 — Structural & Security-Control Adherence
**Status:** PASS | WARN | FAIL | N/A

| Element | Status | Finding |
|---------|--------|---------|

> N/A only when sections 6.1 and 6.2 have no verifiable elements, the section 8 Security item has no applicable entry, and no unrequested/contradictory code is found.
> Security controls from section 8 not already covered by a section 7 criterion are verified here.
> Scope divergence (contradictions marked `[contradicts]` and unrequested scope marked `[unrequested]`) is reported here.

### Dimension 3 — Open Items Resolved
**Status:** PASS | WARN | FAIL | N/A

| TODO | Status | Finding |
|------|--------|---------|

> N/A when the spec has no open [TODO: ...] items.

### Dimension 4 — Domain Names
**Status:** PASS | WARN | N/A

| Term | Status | Finding |
|------|--------|---------|

> N/A when the project has no `docs/glossary/`. WARN at most — never FAIL.

### Recommended Actions
1. [FAIL][code] ...
2. [FAIL][pragmatic-spec-update] ...
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

**Execution evidence:** include command, working directory, outcome/exit code, selected relevant tests and revision when reusing a prior run. Missing runtime evidence makes Dimension 1 WARN at best.

**Finding column:** Always populate, even for passing rows (e.g., cite the test file and line number). Empty findings are not acceptable.

**Security criteria:** A FAIL on a security criterion in Dimension 1 (a negative assertion — non-owner blocked, unauthorized role blocked, malformed input rejected) is always a `[code]` action and blocks "done". Never downgrade it to WARN because the happy path works, and never aggregate it away — call it out by name in Recommended Actions.

**Recommended Actions rules:**
- FAILs listed before WARNs
- Each action is tagged `[code]` (implementation fix), `[pragmatic-spec-update]` (spec decision), or `[verification]` (run/repair the test environment or obtain current execution evidence; no implementation defect established)
- N/A checks are not counted in Summary totals
- If all dimensions are PASS or N/A: omit Recommended Actions and output a **Strengths** section summarizing what was verified and confirmed correct
- **After a FAIL report:** assert explicitly — "**This implementation does not conform to spec.** Fix `[code]` items before marking the story as done. For `[pragmatic-spec-update]` items — these represent decisions not yet captured in the spec; use `pragmatic-spec-update` before the next conformance check."
- **After a WARN report:** close with: "Implementation partially conforms. Address WARN items before marking the story as done — partial conformance is not done."
- **After a PASS report:** close with: "Implementation conforms to spec. Story can be marked as done."

## Additional Resources

- **`references/report-format.md`** — Annotated report format with inline explanations of each field
- **`examples/example-auth-check.md`** — Worked conformance check example against the JWT authentication spec, including a Dimension 4 (Domain Names) PASS and WARN
