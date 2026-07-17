---
name: pragmatic-arch-spec-validate
description: This skill should be used when the user asks to "validate an architecture spec", "check the arch spec", "review this architecture document", "is this arch spec complete?", "audit the architecture spec", "check architecture quality", "validate the ADRs", "is this arch spec ready for approval?", "is the architecture document ready to use?", or wants a structured quality review of an existing architecture technical specification document.
---

# pragmatic-arch-spec-validate

Validate a software architecture tech spec for completeness, consistency, and architectural soundness.

## Purpose

Run a structured review of an architecture spec and produce a PASS/WARN/FAIL report grouped by severity. Do not modify the spec — only report findings with actionable suggestions.

## Lifecycle Position

```
pragmatic-arch-spec-create → [pragmatic-arch-spec-validate] → pragmatic-arch-spec-check → pragmatic-arch-spec-update
```

Use this skill immediately after `pragmatic-arch-spec-create` to verify the spec is ready, or at any point when the spec needs a quality review before being used as reference for `pragmatic-arch-spec-check`.

## When This Skill Applies

Use this skill when an arch spec **already exists** and the user wants to assess its quality, completeness, or soundness — without touching the codebase.

**Do not use when:**
- The user wants to verify that the **code** conforms to the spec → use `pragmatic-arch-spec-check`
- No arch spec exists yet → use `pragmatic-arch-spec-create`
- The user wants to apply changes to the spec → use `pragmatic-arch-spec-update`

**Key distinction from `pragmatic-arch-spec-check`:** this skill reviews the spec document in isolation; `pragmatic-arch-spec-check` compares the spec against the actual codebase. If the user says "check the arch spec" without further context, clarify: "Check the spec document for completeness, or check if the code follows the spec?"

## How to Validate an Architecture Spec

### Step 0 — Language Detection

Infer the report language from the existing arch spec:
1. If the spec contains a `Language:` metadata field, use it
2. Otherwise, infer from the majority language of prose content in the Context & Motivation section and ADR rationale — if ≥80% of prose words are attributable to a single language, use that language
3. If no prose exists or no language reaches 80%, use `AskUserQuestion`:

```
In which language would you like the validation report to be generated?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and use it for **all report content** — section headings, check descriptions, notes, suggestions, and recommended actions.

### Step 1 — Locate and Read the Spec

Find the architecture spec file. Common locations: `docs/arch/`, or any `.arch.md` file matching the provided path. Read the full document before running any checks.

### Step 1.5 — Pre-scan: Detect Open TODO Items

**This is a mandatory step before running any checks.**

After reading the spec in Step 1, count all `[TODO: ...]` occurrences across the document. If any are found, use `AskUserQuestion` to ask:

> "I found **N open TODO item(s)** in this arch spec. These will result in WARN or FAIL findings. Would you like to:
> 1. **Resolve them first** with `pragmatic-arch-spec-update` — for a cleaner validation report
> 2. **Continue with validation as-is** — TODOs will be reported as findings"

**STOP. Wait for the user's choice before proceeding.** If the user chooses to resolve TODOs first, end this skill and defer to `pragmatic-arch-spec-update`.

---

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
- **Testability strategy present** — Describes how the architecture supports testing. A passing strategy must address: (a) which layers or components are unit-testable in isolation, (b) where external dependencies are mocked or stubbed (e.g., via interfaces or adapters at component boundaries), and (c) which flows require integration or e2e tests. A vague mention of "we will write tests" does not pass this check.
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
- **After a FAIL report:** assert explicitly — "**Do not run `pragmatic-arch-spec-check` against this spec** and do not use it as an implementation reference until FAIL items are resolved. Use `pragmatic-arch-spec-update` to address them."
- **After a WARN report:** close with: "Arch spec can proceed to conformance check. Consider resolving WARN items with `pragmatic-arch-spec-update` first. When ready, run `pragmatic-arch-spec-check`."
- **After a PASS report:** close with: "Arch spec is sound and ready. Run `pragmatic-arch-spec-check` to verify the codebase conforms to this spec."

### Step 4 — Generate Project Rules (Optional, PASS only)

Only offer this step when the overall validation status is **PASS**.

After printing the report, use `AskUserQuestion` to ask:

```
Would you like to generate project rules from this architecture spec?

This creates `.claude/rules/<spec-name>-arch.md` plus matching rule files for
other agentic tools (AGENTS.md, Cursor, Windsurf, GitHub Copilot, and GEMINI.md
if present) with concrete architectural constraints — forbidden imports, naming
conventions, component boundary rules — that these tools will follow
automatically during development in this project.
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

Then render the same sections into the cross-tool destinations described in `../pragmatic-project-constitution/references/cross-tool-rules-sync.md`, using `slug=<spec-name>-arch`, `title=Architecture Rules — <System/Module Name>`, `source_path=<path to .arch.md file>`. Set `always_apply=false` with `globs` pointing at the module's own paths only when the arch spec clearly names them (e.g. `src/<module>/**`); otherwise leave `always_apply=true` rather than guessing a glob.

After writing the files, state every path created or updated and how many rules were extracted, and include this note:

> **Note:** These rule files guide agentic tools during development sessions but are not guaranteed enforcement — an agent may not follow them perfectly in long conversations or when the user overrides them. For guaranteed architectural conformance, run `pragmatic-arch-spec-check` in CI.
