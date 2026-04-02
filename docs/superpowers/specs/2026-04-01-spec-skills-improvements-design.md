# Design: spec.* Skills Improvements + spec.check

**Date:** 2026-04-01
**Status:** In Review

---

## 1. Context

The plugin contains three spec skills (`spec.create`, `spec.update`, `spec.validate`) that together support the lifecycle of technical specification documents. This design covers two tracks of work:

1. **Improvements** to the three existing skills based on identified friction points
2. **New skill** `spec.check` — verifies that an existing implementation conforms to its spec

---

## 2. Improvements to Existing Skills

### 2.1 Language Selection — Reduce Friction in spec.update and spec.validate

**Problem:** All three skills start with a mandatory `AskUserQuestion` for language selection before doing any work. For `spec.update` and `spec.validate`, the spec file already exists — its language can be inferred directly from the document.

**Decision:** `spec.update` and `spec.validate` will detect the language from the existing spec and apply it automatically. They will only ask if detection is ambiguous.

**Detection rule:** If the spec contains a `Language:` metadata field, use it. Otherwise, infer from the majority language of prose content in sections 2, 3, and 4 (Problem Statement, Goals, Proposed Solution). If fewer than 80% of prose words can be attributed to a single language, treat as ambiguous and ask. A spec with only tables and code blocks and no prose is also treated as ambiguous.

`spec.create` retains the mandatory question since no reference document exists yet.

### 2.2 Merge Steps 2.5 and 2.6 in spec.update

**Problem:** Two consecutive `AskUserQuestion` rounds (Step 2.5 for scope/intent, Step 2.6 for technology TODOs) create unnecessary round-trips before any writing begins.

**Decision:** Merge into a single confirmation step that covers scope, affected sections, motivation, and open technology TODOs simultaneously.

The technology TODO portion of the merged step remains conditional — it is only included in the question if the spec currently contains open `[TODO: decide — ...]` items or if the requested change introduces new technology decisions. If the update is purely textual (wording corrections, status changes) with no new technical decisions and no existing open TODOs, the merged step omits the technology block entirely.

**Post-merge step numbering for spec.update:**

| Before merge | After merge |
|---|---|
| Step 0 — Language | Step 0 — Language detection |
| Step 1 — Locate the Spec | Step 1 — Locate the Spec |
| Step 2 — Understand the Change | Step 2 — Understand the Change |
| Step 2.5 — Confirm Scope and Intent | Step 3 — Confirm Scope, Intent, and Technology Decisions (merged) |
| Step 2.6 — Resolve Technology TODOs | *(merged into Step 3)* |

> **Note for implementers:** Step 0 in `spec.update` after this change is no longer always an `AskUserQuestion` call. It is a detection step that asks only when the language is ambiguous. The step header text ("This is a mandatory first step. Use `AskUserQuestion`...") must be updated to reflect this conditional behavior.
| Step 3 — Apply the Changes | Step 4 — Apply the Changes |
| Step 4 — Validate After Update | Step 5 — Validate After Update |
| Step 5 — Output Summary | Step 6 — Output Summary |

### 2.3 Add N/A Status to spec.validate Report

**Problem:** The validation report only accepts `PASS | WARN | FAIL`. Several checks (e.g., "Breaking changes flagged") are not applicable to every spec.

**Decision:** Add `N/A` as a valid row-level status in the report table and add an `N/A` count line to the Summary block (not counted in Passed/Warnings/Failed totals). The Overall Status roll-up ignores `N/A` rows.

The following checks may carry `N/A` status, with their conditions:

| Check | N/A condition |
|-------|---------------|
| Non-goals defined | N/A if this is an exploratory spec where scope is intentionally open |
| Acceptance Criteria (≥2) | N/A if this is a design-only spec with no implementation expected |
| No unresolved TODOs | N/A if the spec is explicitly in Draft status (TODOs expected) |
| Criteria are testable | N/A if the spec has no acceptance criteria (see row above) |
| Interface matches design | N/A if sections 6.1/6.2 are absent |
| Breaking changes flagged | N/A for brand-new features with no prior API surface |
| Security considerations addressed | N/A for purely internal tooling or non-networked features where security is genuinely not applicable |

All other checks must produce `PASS`, `WARN`, or `FAIL` — they cannot be `N/A`.

### 2.4 Post-Review Flow Guidance in spec.validate

**Problem:** `spec.validate` generates a report but gives no guidance on next steps when issues are found.

**Decision:** Add an explicit output rule: if FAILs or actionable WARNs are present, the report ends with a recommendation to use `spec.update` to address them.

### 2.5 Changelog Positioning in spec.update

**Problem:** Step 3 instructs to "append a changelog entry" but does not specify where in the file.

**Decision:** Changelog entries are appended at the end of the file, after section 9 (Open Questions).

### 2.6 Directory Creation in spec.create

**Problem:** Step 4 instructs writing to `docs/specs/<slug>.md` but does not address what to do if the directory does not exist.

**Decision:** Add a note in Step 4 to create the `docs/specs/` directory if it does not already exist.

### 2.7 Standardize Step Numbering

**Problem:** `spec.create` uses `0, 1, 1.5, 2, 3, 4, 5` and `spec.update` uses `0, 1, 2, 2.5, 2.6, 3, 4, 5` — inconsistent conventions.

**Decision:** Use sequential integer numbering (0, 1, 2, 3...) for all steps across all skills. The only sub-steps allowed are for genuinely subordinate, optional branches (e.g., `1a`, `1b`) — not as a way to insert steps without renumbering.

---

## 3. New Skill: spec.check

### 3.1 Purpose

Verify that an existing implementation conforms to its spec. Produces a structured conformance report organized by three independent dimensions. Does not modify code or spec — only reports findings and recommends actions.

### 3.2 Trigger Conditions

Use when the user asks: "verify if the implementation follows the spec", "check conformance with the spec", "is the code aligned with the spec?", "audit implementation against the spec", "check if the acceptance criteria were implemented".

**Do not use when:**
- No spec exists yet → use `spec.create`
- The user only wants to review spec quality without comparing to code → use `spec.validate`
- The user wants to apply changes to an existing spec → use `spec.update`

### 3.3 Scope

| Check type | Covered |
|------------|---------|
| Acceptance criteria → test coverage | Yes |
| Interfaces, structs, endpoints → code structure | Yes |
| Open TODOs → resolved in code | Yes |
| Code quality / style | No |
| Performance validation | No |
| Commit history scanning | No (future enhancement) |

> **Note on commit scanning:** Scanning git history to detect whether a TODO was resolved in a commit was considered but scoped out. The boundary (how many commits, which branch, since when) is too variable across repos. The skill will scan only current code files (source, test, config) for evidence of TODO resolution.

### 3.4 Implementation Locator Strategy

The skill uses a hybrid approach to find the implementation:

1. Extract the feature slug from the spec filename (e.g., `auth.md` → `auth`)
2. Search common paths: `src/<slug>/`, `internal/<slug>/`, `pkg/<slug>/`, `lib/<slug>/`, root-level `<slug>/`
3. If exactly one match is found → proceed with confidence
4. If multiple matches are found → `AskUserQuestion` listing the candidates, asking the user to select
5. If no match is found → `AskUserQuestion` asking the user to specify the path

### 3.5 Flow

**Step 0 — Language detection**
Infer from the spec using the same detection rule as section 2.1. Ask only if ambiguous.

**Step 1a — Identify the spec**
Determine the spec path from: user-provided path, open file in IDE context, or conversation context. If none is available, use `AskUserQuestion` to ask. If multiple specs exist and none was specified, list them and ask.

**Step 1b — Locate the implementation**
Apply the strategy from section 3.4.

**Step 2 — Extract verifiable elements**
Before scanning code, map everything that will be verified:
- Acceptance criteria list (section 7)
- Interfaces, structs, type definitions, and endpoints (sections 6.1, 6.2)
- Open `[TODO: ...]` items from any section

If sections 6.1 and 6.2 are absent or empty, Dimension 2 (Structural Adherence) is marked `N/A`.
If no open TODOs exist in the spec, Dimension 3 (Open Items Resolved) is marked `N/A`.

**Step 3 — Scan implementation**
For each element extracted in Step 2:
- Acceptance criteria → search test files (`*_test.go`, `*.test.ts`, `*.spec.ts`, `*.test.py`, etc.) for test cases that exercise the criterion
- Interfaces/structs/endpoints → search source files for type definitions, function signatures, and route registrations
- TODOs → search source files, config files, and inline comments for evidence of resolution

**Step 4 — Generate conformance report**
See section 3.6.

**Step 5 — Recommended actions**
See report format rules in section 3.6.

### 3.6 Report Format

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
| <criterion text> | PASS | <test file>:<line> covers this |
| <criterion text> | WARN | No dedicated test found — only indirectly covered |
| <criterion text> | FAIL | No test found |

### Dimension 2 — Structural Adherence
**Status:** PASS | WARN | FAIL | N/A

| Element | Status | Finding |
|---------|--------|---------|
| <interface/struct/endpoint> | PASS | <file>:<line> matches spec |
| <interface/struct/endpoint> | WARN | Present but deviates: <details> |
| <interface/struct/endpoint> | FAIL | Not found in codebase |

> N/A when sections 6.1 and 6.2 are absent or empty.

### Dimension 3 — Open Items Resolved
**Status:** PASS | WARN | FAIL | N/A

| TODO | Status | Finding |
|------|--------|---------|
| <TODO text> | PASS | Resolution found in <file>:<line> |
| <TODO text> | WARN | Partial — decision present but not fully implemented |
| <TODO text> | FAIL | No evidence of resolution found |

> N/A when spec has no open [TODO: ...] items.

### Recommended Actions
1. [FAIL][code] <action — fix in implementation>
2. [FAIL][spec.update] <action — decision or TODO to close in spec>
3. [WARN][code] <action>
```

**Row-level status values:** `PASS`, `WARN`, `FAIL`, `N/A`

**Per-dimension status aggregation:**
- `FAIL` if any row in that dimension is `FAIL`
- `WARN` if any row is `WARN` and none are `FAIL`
- `PASS` if all rows are `PASS`
- `N/A` if the dimension is not applicable (no elements to check)

**Overall Status aggregation:**
- `FAIL` if any evaluated dimension is `FAIL`
- `WARN` if any evaluated dimension is `WARN` and none are `FAIL`
- `PASS` if all evaluated dimensions are `PASS` or `N/A`

**Finding column:** Always populate, even for passing rows (e.g., cite the test file and line). Empty findings are not acceptable — they prevent traceability.

**Recommended Actions rules:**
- FAILs listed before WARNs
- Each action is tagged `[code]` (fix in implementation) or `[spec.update]` (decision or clarification needed in spec)
- If all dimensions are `PASS` or `N/A`: omit the Recommended Actions section and instead output a **Strengths** section summarizing what was verified and confirmed correct
- Summary counts exclude `N/A` rows

### 3.7 Reference Files

The skill will include:

- **`references/report-format.md`** — annotated example of a complete `spec.check` report, with inline comments explaining each section (status values, aggregation rules, finding format, action tags). Format annotations use `> Note:` blockquotes.
- **`examples/example-auth-check.md`** — worked example of a conformance report against the JWT authentication spec located at `skills/spec.create/examples/example-auth-spec.md`. The example should include at least one PASS, one WARN, and one FAIL across the three dimensions to demonstrate the full range of outputs.

### 3.8 Integration with the spec.* Ecosystem

| Situation | Skill |
|-----------|-------|
| No spec exists | `spec.create` |
| User wants to assess spec document quality (regardless of implementation state) | `spec.validate` |
| Spec exists, implementation exists, user wants conformance check | `spec.check` |
| Divergence found — code needs to change | `spec.check` → fix code |
| Divergence found — decision changed or TODO to close | `spec.check` → `spec.update` |

---

## 4. Files to Create / Modify

| File | Action |
|------|--------|
| `skills/spec.create/SKILL.md` | Update: step numbering, directory creation note |
| `skills/spec.update/SKILL.md` | Update: language detection, merge steps 2.5+2.6 (new numbering in 2.2), changelog positioning, step numbering |
| `skills/spec.validate/SKILL.md` | Update: language detection, N/A status, post-review guidance, step numbering |
| `skills/spec.check/SKILL.md` | Create |
| `skills/spec.check/references/report-format.md` | Create — annotated report format example |
| `skills/spec.check/examples/example-auth-check.md` | Create — worked example using JWT auth spec |
