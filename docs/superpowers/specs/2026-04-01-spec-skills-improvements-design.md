# Design: spec.* Skills Improvements + spec.check

**Date:** 2026-04-01
**Status:** Approved

---

## 1. Context

The plugin contains three spec skills (`spec.create`, `spec.update`, `spec.validate`) that together support the lifecycle of technical specification documents. This design covers two tracks of work:

1. **Improvements** to the three existing skills based on identified friction points
2. **New skill** `spec.check` — verifies that an existing implementation conforms to its spec

---

## 2. Improvements to Existing Skills

### 2.1 Language Selection — Reduce Friction in spec.update and spec.validate

**Problem:** All three skills start with a mandatory `AskUserQuestion` for language selection before doing any work. For `spec.update` and `spec.validate`, the spec file already exists — its language can be inferred directly from the document.

**Decision:** `spec.update` and `spec.validate` will detect the language from the existing spec and apply it automatically. They will only ask if the language is ambiguous or if the user explicitly wants to change it. `spec.create` retains the mandatory question since no reference document exists yet.

### 2.2 Merge Steps 2.5 and 2.6 in spec.update

**Problem:** Two consecutive `AskUserQuestion` rounds (Step 2.5 for scope/intent, Step 2.6 for technology TODOs) create unnecessary round-trips before any writing begins.

**Decision:** Merge into a single confirmation step that covers scope, affected sections, motivation, and open technology TODOs simultaneously.

### 2.3 Add N/A Status to spec.validate Report

**Problem:** The validation report only accepts `PASS | WARN | FAIL`. Several checks (e.g., "Breaking changes flagged") are not applicable to every spec.

**Decision:** Add `N/A` as a valid status in the report format. The skill documentation will specify which checks may be `N/A` and under what conditions.

### 2.4 Post-Review Flow Guidance in spec.validate

**Problem:** `spec.validate` generates a report but gives no guidance on next steps when issues are found.

**Decision:** Add an explicit output rule: if FAILs or actionable WARNs are present, the report will end with a clear recommendation to use `spec.update` to address them.

### 2.5 Changelog Positioning in spec.update

**Problem:** Step 3 instructs to "append a changelog entry" but does not specify where in the file.

**Decision:** Specify explicitly: changelog entries are appended at the end of the file, after section 9 (Open Questions).

### 2.6 Directory Creation in spec.create

**Problem:** Step 4 instructs writing to `docs/specs/<slug>.md` but does not address what to do if the directory does not exist.

**Decision:** Add a note in Step 4 to create the `docs/specs/` directory if it does not already exist.

### 2.7 Standardize Step Numbering

**Problem:** `spec.create` uses `0, 1, 1.5, 2, 3, 4, 5` and `spec.update` uses `0, 1, 2, 2.5, 2.6, 3, 4, 5` — inconsistent conventions.

**Decision:** Use sequential integer numbering (0, 1, 2, 3...) for all steps. Sub-steps are only used when they are genuinely subordinate and optional (e.g., a branch in the flow).

---

## 3. New Skill: spec.check

### 3.1 Purpose

Verify that an existing implementation conforms to its spec. Produces a structured conformance report organized by three independent dimensions. Does not modify code or spec — only reports findings and recommends actions.

### 3.2 Trigger Conditions

Use when the user asks: "verify if the implementation follows the spec", "check conformance with the spec", "is the code aligned with the spec?", "audit implementation against the spec", "check if the acceptance criteria were implemented".

### 3.3 Scope

| Check type | Covered |
|------------|---------|
| Acceptance criteria → test coverage | Yes |
| Interfaces, structs, endpoints → code structure | Yes |
| Open TODOs → resolved in code or commits | Yes |
| Code quality / style | No |
| Performance validation | No |

### 3.4 Implementation Locator Strategy

The skill uses a hybrid approach to find the implementation:

1. Extract the feature slug from the spec filename (e.g., `auth.md` → `auth`)
2. Search common paths: `src/<slug>/`, `internal/<slug>/`, `pkg/<slug>/`, `lib/<slug>/`, root-level `<slug>/`
3. If a match is found with high confidence → proceed
4. If ambiguous or nothing found → `AskUserQuestion` asking the user to specify the path

### 3.5 Flow

```
Step 0 — Language detection
  → Infer from spec; ask only if ambiguous

Step 1 — Locate spec and implementation
  → Read spec; infer implementation path; ask if unclear

Step 2 — Extract verifiable elements
  → Acceptance criteria (section 7)
  → Interfaces, structs, endpoints (sections 6.1, 6.2)
  → Open TODOs (any section)

Step 3 — Scan implementation
  → Criteria → test files (*_test.go, *.test.ts, *.spec.ts, etc.)
  → Interfaces/structs → type definitions, function signatures
  → TODOs → code comments, recent commits, config files

Step 4 — Generate conformance report (3 dimensions)
  → Dimension 1: Acceptance Criteria Coverage
  → Dimension 2: Structural Adherence
  → Dimension 3: Open Items Resolved

Step 5 — Recommended Actions
  → FAILs listed first
  → Each action tagged [código] or [spec.update]
  → If all pass: summarize strengths
```

### 3.6 Report Format

```
## Spec Conformance Report
**Spec:** <file path>
**Implementation:** <directory>
**Date:** <today>
**Overall Status:** PASS | WARN | FAIL

### Dimension 1 — Acceptance Criteria Coverage
Status: <status>
| Criterion | Status | Finding |
|-----------|--------|---------|

### Dimension 2 — Structural Adherence
Status: <status>
| Element | Status | Finding |
|---------|--------|---------|

### Dimension 3 — Open Items Resolved
Status: <status>
| TODO | Status | Finding |
|------|--------|---------|

### Recommended Actions
1. [FAIL][código] ...
2. [FAIL][spec.update] ...
3. [WARN][código] ...
```

### 3.7 Integration with the spec.* Ecosystem

| Situation | Skill |
|-----------|-------|
| No spec exists | `spec.create` |
| Spec exists, no implementation | `spec.validate` |
| Spec exists, implementation exists | `spec.check` |
| Divergence found in code | `spec.check` → fix code |
| Decision changed / TODO to close | `spec.check` → `spec.update` |

---

## 4. Files to Create / Modify

| File | Action |
|------|--------|
| `skills/spec.create/SKILL.md` | Update: step numbering, directory creation note |
| `skills/spec.update/SKILL.md` | Update: language detection, merge steps 2.5+2.6, changelog positioning, step numbering |
| `skills/spec.validate/SKILL.md` | Update: language detection, N/A status, post-review guidance, step numbering |
| `skills/spec.check/SKILL.md` | Create |
