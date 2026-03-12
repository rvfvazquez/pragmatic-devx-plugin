# arch.ts.validate

Validates a software architecture tech spec for completeness, consistency, and architectural soundness.

## Usage

```
/arch.ts.validate <arch-spec-file-path>
```

## Instructions

You are a pragmatic software architecture reviewer. Your task is to validate an architecture technical specification document.

**Input:** $ARGUMENTS

### Step 1 — Locate and Read the Spec

Find and read the architecture spec file. Common locations:
- `docs/arch/`
- Any `.arch.md` or `.md` file matching the provided path or name

### Step 2 — Run Validation Checks

Evaluate the spec against the following criteria. For each check, report **PASS**, **WARN**, or **FAIL** with a short explanation.

#### A. Completeness Checks
- [ ] **Title & Status** — Has a clear name and defined status (Draft/Review/Approved)
- [ ] **Context & Motivation** — Explains why this architecture exists and what problem it solves
- [ ] **Goals defined** — At least one architectural goal is stated (quality attributes)
- [ ] **Constraints listed** — Technology or organizational constraints are documented
- [ ] **Non-goals defined** — Explicitly states what is out of scope
- [ ] **High-level design present** — Describes main components and their relationships
- [ ] **Component boundaries defined** — Lists components with responsibilities and public interfaces
- [ ] **At least one ADR** — At least one key design decision is documented in ADR format
- [ ] **Architecture patterns described** — Component structure, dependency direction, and communication style are defined
- [ ] **Data flow described** — At least one primary data flow is described
- [ ] **No unresolved TODOs** — No `[TODO: ...]` placeholders remain (WARN if present)

#### B. Architectural Soundness Checks
- [ ] **Single Responsibility per component** — Each component has one clear responsibility
- [ ] **Dependency direction is explicit** — The allowed direction of dependencies between layers is stated and consistent
- [ ] **No bidirectional dependencies** — No two components are described as mutually depending on each other
- [ ] **Public interfaces are defined** — Component boundaries expose explicit contracts, not implementation details
- [ ] **Error strategy is defined** — How errors propagate across boundaries is described

#### C. Clarity Checks
- [ ] **Unambiguous language** — No vague terms (e.g., "fast", "scalable") without measurable definitions
- [ ] **Diagrams present** — At least one diagram (ASCII or Mermaid) illustrates the structure
- [ ] **Consistent terminology** — Key terms (component, service, layer, etc.) are used consistently throughout
- [ ] **ADRs include rationale** — Each decision explains why that option was chosen over alternatives
- [ ] **Consequences are honest** — Trade-offs and downsides are acknowledged, not only benefits

#### D. Design Quality Checks
- [ ] **Component structure defined** — A standard layout or organization for components is described
- [ ] **Communication style stated** — How components interact is explicit (sync/async, events, direct calls, etc.)
- [ ] **Testability strategy present** — Describes how the architecture supports testing
- [ ] **External dependencies documented** — Integrations and external systems are listed with their purpose

### Step 3 — Generate Validation Report

Produce a structured report in this format:

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

1. **[No ADR]** Section 5 (Key Design Decisions) is missing
   - Add at least one ADR describing a significant architectural decision

2. **[Circular dependency]** Components A and B are described as mutually dependent
   - Introduce a shared abstraction or invert one dependency

### Warnings (WARN)
Should be addressed but not blocking:

1. **[Unresolved TODO]** Section 9 — Performance strategy is `[TODO: define strategy]`
   - Define the performance approach before moving to Approved status

2. **[No diagram]** No visual representation of the component structure
   - Add a Mermaid or ASCII diagram to Section 4.1

### Suggestions (INFO)
Optional improvements:

1. Consider documenting the deployment topology if the system has infrastructure dependencies

### Checks Passed
- Title & Status ✓
- Context & Motivation ✓
- Goals defined ✓
- ...
```

### Step 4 — Output Instructions

1. Print the full validation report in the terminal
2. Do **not** modify the architecture spec file — only report findings
3. Group findings by severity: FAIL → WARN → INFO → PASS
4. For each FAIL or WARN, provide a concrete, actionable suggestion
5. If the spec passes all checks, summarize its architectural strengths and confirm it is ready for approval
