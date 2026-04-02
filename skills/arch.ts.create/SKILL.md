---
name: arch.ts.create
description: This skill should be used when the user asks to "create an architecture spec", "document the architecture", "write an architecture document", "create arch spec for this module", "document this system's architecture", "generate an ADR", "create architecture documentation for this service", "write arch spec for integration", or needs to formally document the architecture of a system, module, layer, or integration.
---

# arch.ts.create

Create a software architecture technical specification document for a system, module, layer, or integration.

## Purpose

Produce a thorough architecture tech spec that captures design decisions (ADRs), component boundaries, architecture patterns, data flows, and non-functional requirements. Specs live in `docs/arch/`.

## Scope Types

- **`system`** — full application or bounded context
- **`module`** — a single feature module or domain
- **`layer`** — a horizontal layer (e.g., data access, presentation)
- **`integration`** — an external integration or adapter

Default scope when not specified: `module`.

## When This Skill Applies

Use this skill when **no arch spec exists yet** for the system, module, or integration being documented.

**Do not use when:**
- An arch spec already exists and the user wants to modify it → use `arch.ts.update`
- An arch spec already exists and the user wants a quality review → use `arch.ts.validate`

**Edge case:** if the user asks to "document the actual architecture" of an existing codebase (reverse-engineering decisions from code), scan the codebase thoroughly in Step 1 before the discovery interview — the code is the source of truth for what was actually built.

## How to Create an Architecture Spec

### Step 0 — Language Selection

**This is a mandatory first step.** Use `AskUserQuestion` to ask the user which language they want the architecture spec document generated in:

```
In which language would you like the architecture spec to be generated?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and use it consistently for **all content** in the generated document — section headings, component descriptions, ADR rationale, data flow descriptions, and TODO comments. Do not proceed to the next step until the language is confirmed.

### Step 1 — Understand the Context

Determine from the user's input:
- **Name** — the system, module, or layer being documented
- **Scope** — how broad the document should be (system / module / layer / integration)

Before writing, scan the codebase for:
- Existing code, README files, or prior specs that reveal current decisions and constraints
- Related architecture specs in `docs/arch/`

### Step 1.5 — Architecture Discovery Interview

**This is a mandatory step.** Do not generate the architecture document until you have a complete picture of the system's context, constraints, quality requirements, and open decisions.

After identifying the name/scope and scanning the codebase, use `AskUserQuestion` to conduct a focused architecture discovery. The goal is to understand the "why" behind the architecture — decisions only make sense in context.

Adapt the questions to the scope and what is not already evident from the codebase.

**`multiSelect` rules for this step — always follow these:**
- **Quality Attributes**: `multiSelect: true` — multiple NFRs apply simultaneously
- **Constraints**: `multiSelect: true` — technology, integration, and organizational constraints can coexist
- **Pain Points / Risks**: `multiSelect: true` — there are usually several concerns at once
- **Architectural Goals**: `multiSelect: true` — multiple goals drive the same architecture

Example format:

```
Before I write the architecture spec, I need to understand the broader context:

**Purpose & Drivers**
- What problem does this [system/module/layer/integration] solve, and for whom?
- What are the main business or product drivers behind this architecture?

**Quality Attributes (Non-Functional Requirements)** → multiSelect: true
Which of these matter most? (select all that apply — provide targets where known)
- Performance: expected throughput, latency targets
- Scalability: peak load, growth projections
- Availability: uptime requirements, acceptable downtime
- Security: data sensitivity, compliance requirements (LGPD, SOC2, PCI-DSS, etc.)
- Maintainability: how often will this change, and by what size team?
- Cost: any budget constraints on infrastructure?

**Constraints** → multiSelect: true
Which of these apply? (select all that apply)
- Technology constraints (existing platform, team skills, vendor agreements)
- Integration constraints (systems that cannot change)
- Organizational constraints (team structure, deployment pipeline, environment restrictions)

**Current Pain Points / Risks** → multiSelect: true
What is not working well today? (select all that apply)
- Performance / scalability problems
- Reliability / availability issues
- Security gaps or compliance risk
- High operational cost
- Developer experience / maintainability concerns

**Expected Evolution**
- How is this expected to evolve over the next 6–12 months?
- Are there known future requirements that should influence today's design?

**Open Decisions**
- Are there architectural decisions still being debated? Which options are on the table?

Answer what you know — for anything undecided, I'll capture it as an open ADR item in the spec.
```

Do **not** proceed to Step 2 until:
- The purpose and main quality attributes are understood
- Key constraints are captured
- Major open decisions are identified

### Step 2 — Generate the Architecture Tech Spec

Create the file at `docs/arch/<name>.arch.md` using the full template in `references/template.md`.

Fill every section with concrete content. Use `[TODO: ...]` only for information that genuinely cannot be inferred and requires a human decision.

#### Diagram Guide

Use Mermaid diagrams to make structure and behavior immediately visible. Apply the right diagram type for each context:

| Situation | Diagram type | Section |
|-----------|-------------|---------|
| Component structure and dependencies | `graph TD` or `flowchart TD` | 4.1, 6.2 |
| Request/response flow between components | `sequenceDiagram` | 7 |
| Async flow with queues, events, or branching | `flowchart LR` | 7 |
| State transitions (e.g., status machine) | `stateDiagram-v2` | 7 |

**Rules:**
- Section 4.1 (Component Diagram): always use `graph TD` — show every component and their dependency direction
- Section 6.2 (Dependency Direction): use `flowchart TD` to show allowed vs. forbidden dependency arrows explicitly
- Section 7 (Data Flow): use `sequenceDiagram` for synchronous flows; use `flowchart LR` when the flow involves async steps, queues, or conditional branching. Replace ASCII art — do not use plain text arrows.
- Keep diagrams focused: one diagram per flow. Do not combine multiple flows into a single diagram.

### Step 3 — Output Summary

After creating the file:
1. State the file path created
2. Summarize the key architectural decisions documented
3. List any `[TODO: ...]` items that remain open

**Next step:** run `arch.ts.validate` to verify the spec is complete and sound before using it as a reference for conformance checks.

## Output Location

```
docs/arch/<name>.arch.md
```

## Additional Resources

### Reference Files

- **`references/template.md`** — Full architecture tech spec template with all sections, ADR format, and component table structure

### Example Files

Use these examples as calibration targets for output structure, ADR depth, component boundary detail, diagram usage, and writing style. Each example showcases a different architecture pattern:

- **`examples/example-payments-arch.md`** — Payments module with anti-corruption layer and transactional outbox. Showcases `graph TD` for component dependencies, `flowchart TD` for dependency direction, and `sequenceDiagram` for synchronous multi-step flows
- **`examples/example-notification-service-arch.md`** — Event-driven notification service with multiple channels (email + push). Showcases consumer/dispatcher pattern, `sequenceDiagram` for async flows, and `flowchart LR` for opt-out/skip branching logic
