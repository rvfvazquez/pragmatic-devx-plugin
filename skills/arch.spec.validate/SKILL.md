---
name: arch.spec.validate
description: This skill should be used when the user asks to "validate an architecture spec", "check the arch spec", "review this architecture document", "is this arch spec complete?", "audit the architecture spec", "check architecture quality", "validate the ADRs", "is this arch spec ready for approval?", "is the architecture document ready to use?", or wants a structured quality review of an existing architecture technical specification document.
---

# arch.spec.validate

Validate a software architecture tech spec for completeness, consistency, and architectural soundness.

## Purpose

Run a structured review of an architecture spec and produce a PASS/WARN/FAIL report grouped by severity. Do not modify the spec — only report findings with actionable suggestions.

## Lifecycle Position

```
arch.spec.create → [arch.spec.validate] → arch.spec.check → arch.spec.update
```

Use this skill immediately after `arch.spec.create` to verify the spec is ready, or at any point when the spec needs a quality review before being used as reference for `arch.spec.check`.

## When This Skill Applies

Use this skill when an arch spec **already exists** and the user wants to assess its quality, completeness, or soundness — without touching the codebase.

**Do not use when:**
- The user wants to verify that the **code** conforms to the spec → use `arch.spec.check`
- No arch spec exists yet → use `arch.spec.create`
- The user wants to apply changes to the spec → use `arch.spec.update`

**Key distinction from `arch.spec.check`:** this skill reviews the spec document in isolation; `arch.spec.check` compares the spec against the actual codebase. If the user says "check the arch spec" without further context, clarify: "Check the spec document for completeness, or check if the code follows the spec?"

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

#### E. Checkability
- **Rules are concrete and verifiable** — Each architectural rule can be statically verified in code (file structure, imports, naming, dependency direction). Vague rules like "components should be loosely coupled" without concrete criteria are not checkable
- **Component names are canonical** — The names used in component boundaries match the expected directory or module names in the codebase
- **Dependency rules are explicit** — Forbidden and allowed dependencies are named, not implied
- **Naming conventions are precise** — Naming patterns (e.g., `*Service`, `*Repository`) are specific enough to be matched against actual file names

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
   - How to resolve:
     - **Option A — Fix the spec** (if the check criterion is valid and the spec is incomplete):
       - Concrete suggestion to address the gap in the spec
     - **Option B — Reconsider the criterion** (if the spec reflects a deliberate, documented decision that makes this check inapplicable):
       - Explain why the criterion does not apply, and add a note in the spec's Constraints or ADR section to make the intent explicit

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
- **Every FAIL must include a "How to resolve" block** with two options: fix the spec to satisfy the criterion, or reconsider the criterion if a deliberate decision makes it inapplicable
- For each WARN, provide a concrete, actionable suggestion
- If all checks pass, summarize architectural strengths and confirm readiness for approval
- **Next step after PASS:** run `arch.spec.check` to verify the codebase conforms to this spec

### Step 4 — Generate Claude Rules (Optional, PASS only)

Only offer this step when the overall validation status is **PASS**.

After printing the report, use `AskUserQuestion` to ask:

```
Would you like to generate Claude project rules from this architecture spec?

This creates a `.claude/rules/<spec-name>-arch.md` file with concrete architectural
constraints that Claude will follow automatically during development in this project
(e.g. forbidden imports, naming conventions, component boundary rules).
```

#### If the user accepts:

Extract only rules that passed **Section E (Checkability)** criteria — rules that are concrete, named, and verifiable. Do not extract vague guidelines.

Map spec content to rule types:

| Spec content | Rule type |
|---|---|
| Forbidden dependency direction (e.g., domain must not import infrastructure) | `Never import <X> inside <Y>` |
| Allowed dependency direction | `<A> may only depend on <B>` |
| Naming conventions (e.g., `*Service`, `*Repository`) | `Files in <path> must follow <pattern> naming` |
| Component boundary (e.g., all external calls via ACL) | `<X> must not call <Y> directly — route through <Z>` |
| Communication style (sync/async enforcement) | `<X> must communicate with <Y> via <mechanism>` |

Write the file to `.claude/rules/<spec-name>-arch.md` using this format:

```markdown
# Architecture Rules — <System/Module Name>
# Source: <path to .arch.md file>
# Generated: <today's date>

## Dependency Rules
- <rule>

## Naming Conventions
- <rule>

## Component Boundaries
- <rule>
```

Only include sections that have at least one rule. Omit empty sections.

After writing the file, state the path created and how many rules were extracted, and include this note:

> **Note:** Claude rules guide Claude during development sessions but are not guaranteed enforcement — Claude may not follow them perfectly in long conversations or when the user overrides them. For guaranteed architectural conformance, run `arch.spec.check` in CI.
