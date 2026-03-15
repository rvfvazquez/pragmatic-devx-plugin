---
name: arch.ts.validate
description: This skill should be used when the user asks to "validate an architecture spec", "check the arch spec", "review this architecture document", "is this arch spec complete?", "audit the architecture spec", "check architecture quality", "validate the ADRs", or wants a structured quality review of an existing architecture technical specification document.
version: 0.1.0
---

# arch.ts.validate

Validate a software architecture tech spec for completeness, consistency, and architectural soundness.

## Purpose

Run a structured review of an architecture spec and produce a PASS/WARN/FAIL report grouped by severity. Do not modify the spec — only report findings with actionable suggestions.

## When This Skill Applies

Apply when an architecture spec exists and the user wants to know if it's ready:

- "Validate docs/arch/payments.arch.md"
- "Is the auth architecture spec ready for approval?"
- "Check the notification module arch spec"
- "Review this architecture document for soundness"

## How to Validate an Architecture Spec

### Step 0 — Language Selection

**This is a mandatory first step.** Use `AskUserQuestion` to ask the user which language they want the validation report generated in:

```
In which language would you like the validation report to be generated?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and use it for **all report content** — section headings, check descriptions, notes, suggestions, and recommended actions. Do not proceed to the next step until the language is confirmed.

### Step 1 — Locate and Read the Spec

Find the architecture spec file. Common locations: `docs/arch/`, or any `.arch.md` file matching the provided path. Read the full document before running any checks.

### Step 2 — Run Validation Checks

Evaluate each criterion below. Report **PASS**, **WARN**, or **FAIL** with a short explanation.

#### A. Completeness
- **Title & Status** — Has a clear name and defined status (Draft/Review/Approved)
- **Context & Motivation** — Explains why this architecture exists and what problem it solves
- **Goals defined** — At least one architectural goal is stated (quality attributes)
- **Constraints listed** — Technology or organizational constraints are documented
- **Non-goals defined** — Explicitly states what is out of scope
- **High-level design present** — Describes main components and their relationships
- **Component boundaries defined** — Lists components with responsibilities and public interfaces
- **At least one ADR** — At least one key design decision is documented in ADR format
- **Architecture patterns described** — Component structure, dependency direction, and communication style are defined
- **Data flow described** — At least one primary data flow is described
- **No unresolved TODOs** — No `[TODO: ...]` placeholders remain (WARN if present)

#### B. Architectural Soundness
- **Single Responsibility per component** — Each component has one clear responsibility
- **Dependency direction is explicit** — The allowed direction of dependencies is stated and consistent
- **No bidirectional dependencies** — No two components are described as mutually depending on each other
- **Public interfaces are defined** — Component boundaries expose explicit contracts, not implementation details
- **Error strategy is defined** — How errors propagate across boundaries is described

#### C. Clarity
- **Unambiguous language** — No vague terms (e.g., "fast", "scalable") without measurable definitions
- **Diagrams present** — At least one diagram (ASCII or Mermaid) illustrates the structure
- **Consistent terminology** — Key terms are used consistently throughout
- **ADRs include rationale** — Each decision explains why that option was chosen over alternatives
- **Consequences are honest** — Trade-offs and downsides are acknowledged, not only benefits

#### D. Design Quality
- **Component structure defined** — A standard layout for components is described
- **Communication style stated** — How components interact is explicit (sync/async, events, direct calls)
- **Testability strategy present** — Describes how the architecture supports testing
- **External dependencies documented** — Integrations and external systems are listed with their purpose

### Step 3 — Generate Validation Report

Produce the report in this format:

```
## Architecture Tech Spec Validation Report
**File:** <file path>
**System/Module:** <name from spec>
**Date:** <today>
**Overall Status:** PASS | WARN | FAIL

### Summary
- Passed:   X checks
- Warnings: X checks
- Failed:   X checks

### Failed Checks (FAIL)
Must be addressed before approval:

1. **[Check name]** — explanation
   - Concrete suggestion to fix

### Warnings (WARN)
Should be addressed but not blocking:

1. **[Check name]** — explanation
   - Concrete suggestion to address

### Suggestions (INFO)
Optional improvements.

### Checks Passed
- Check name ✓
- ...
```

### Output Rules

- Print the full report; do **not** modify the spec file
- Group findings: FAIL → WARN → INFO → PASS
- For each FAIL or WARN, provide a concrete, actionable suggestion
- If all checks pass, summarize architectural strengths and confirm readiness for approval
