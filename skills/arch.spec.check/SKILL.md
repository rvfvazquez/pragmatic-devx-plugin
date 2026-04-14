---
name: arch.spec.check
description: This skill should be used when the user asks to "check if the code conforms to the architecture spec", "verify architecture conformance", "does the code follow the arch spec?", "check if the project respects the architecture", "validate architecture rules in the codebase", "run an architecture check", "arch conformance check", or wants to verify that the actual project structure and code comply with documented architecture technical specifications.
---

# arch.spec.check

Verify whether the actual project code and structure conform to the rules and decisions declared in one or more architecture tech spec documents (`.arch.md`).

## Purpose

Bridge the gap between the documented architecture and the implemented code. Scan the codebase using static analysis (file structure, imports, naming, dependency direction) and compare it against the architectural rules extracted from the spec(s). Produce a CONFORMANT/PARTIAL/NON-CONFORMANT report grouped by severity. Do not modify any file — only report findings with actionable suggestions.

This skill is language-agnostic: it applies to any codebase regardless of programming language.

## Lifecycle Position

```
arch.spec.create → arch.spec.validate → [arch.spec.check] → arch.spec.update → arch.spec.check
```

Use this skill after `arch.spec.validate` confirms the spec is sound. Run it periodically to detect drift between code and spec. When Option B is chosen for a violation (the code reflects an intentional evolution), use `arch.spec.update` to capture the decision in the spec, then re-run this check.

## When This Skill Applies

Use this skill when an arch spec **and** a codebase both exist, and the user wants to verify whether the code follows the spec.

**Do not use when:**
- No arch spec exists yet → use `arch.spec.create` first
- The user wants to check the quality of the spec document itself (not the code) → use `arch.spec.validate`
- The user wants to update the spec to reflect new decisions → use `arch.spec.update`

**Prerequisite:** the arch spec should pass `arch.spec.validate` before running this check. If the spec has unresolved `[TODO]` items or missing sections, conformance results will be unreliable.

**Key distinction from `arch.spec.validate`:** `arch.spec.validate` reviews the spec document; `arch.spec.check` scans the actual codebase against the spec.

## How to Check Architecture Conformance

### Step 0 — Language Selection

**This is a mandatory first step.** Use `AskUserQuestion` to ask the user which language they want the conformance report generated in:

```
In which language would you like the conformance report to be generated?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and use it for **all report content** — section headings, check descriptions, findings, and suggested actions. Do not proceed to the next step until the language is confirmed.

### Step 1 — Define the Check Scope

**This is a mandatory step.** Use `AskUserQuestion` to ask the user two questions in the same prompt:

```
Before I run the conformance check, I need to define the scope:

**Which architecture spec(s) should I check against?**
- [ ] All specs found in `docs/arch/` (*.arch.md)
- [ ] A specific spec — provide the file path or name

**Which part of the project should I scan?**
- [ ] The entire project
- [ ] A specific directory or module — provide the path
```

Record both answers and use them to constrain all subsequent steps. If the user chooses "all specs" and "entire project", apply every rule found across all spec files to the full codebase.

### Step 2 — Load Spec(s) and Extract Architectural Rules

For each spec in scope:

1. Read the full `.arch.md` file
2. Extract the following as explicit, checkable rules:

   - **Components** — names, responsibilities, and documented public interfaces from the component boundaries table
   - **Dependency direction** — which components may depend on which; which directions are forbidden
   - **Architecture patterns** — component structure conventions, naming conventions, communication style (sync/async/events), error handling strategy
   - **External integrations** — all documented external systems, services, or libraries and their integration approach
   - **Constraints** — technology or structural constraints that must hold in the code
   - **NFRs with structural implications** — e.g., "no direct DB access outside the repository layer"

3. Build a rule list before scanning the codebase. Each rule should be traceable to a specific section of the spec.

### Step 3 — Scan the Codebase

Use Glob and Grep to gather evidence from the codebase within the defined scope. Apply each extracted rule against what you observe.

#### A. Structural Conformance
- Do all documented components exist as directories or modules in the codebase?
- Are there significant directories or modules in the codebase not documented in the spec?
- Do component/module names follow the naming conventions declared in the spec?

#### B. Boundary Conformance
- Do imports or usages cross boundaries that the spec declares as forbidden?
- Are internal implementation details of a component being referenced directly from outside that component?
- Are the public interfaces (APIs, exported types, entry points) consistent with what the spec documents?

#### C. Dependency Direction Conformance
- Do dependencies flow only in the direction(s) allowed by the spec?
- Are there reverse dependencies (e.g., a domain module importing from an infrastructure module when the spec forbids it)?
- Are there circular dependencies not acknowledged in the spec?

#### D. Integration Conformance
- Are all external integrations used in the code documented in the spec?
- Are there undocumented external services, packages, or APIs being called within the scanned scope?
- Do integration patterns in the code match the approach documented in the spec (e.g., anti-corruption layer, direct SDK, event-based)?

#### E. Pattern & Convention Conformance
- Do file/class/function naming conventions match what the spec defines (e.g., `*Service`, `*Repository`, `*Handler`)?
- Is the communication style between components (sync calls, async events, queues) consistent with the spec?
- Is the error handling strategy consistent with what the spec defines (e.g., exceptions vs result types, boundary error propagation)?
- Does the internal structure of components match the layout described in the spec?

#### F. Divergence Signals
- Are there `TODO`, `FIXME`, or `HACK` comments that indicate intentional or unresolved architectural debt?
- Are there commented-out blocks that suggest a recent deviation from the original design?

### Step 4 — Generate Conformance Report

Produce the report using the format and output rules defined in `references/report-format.md`.

## Additional Resources

### Reference Files

- **`references/report-format.md`** — Full conformance report format, field definitions, and output rules
