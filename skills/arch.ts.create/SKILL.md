---
name: arch.ts.create
description: This skill should be used when the user asks to "create an architecture spec", "document the architecture", "write an architecture document", "create arch spec for this module", "document this system's architecture", "generate an ADR", "create architecture documentation for this service", "write arch spec for integration", or needs to formally document the architecture of a system, module, layer, or integration.
version: 0.1.0
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

Apply when a system, module, or integration needs to be formally documented:

- "Create an arch spec for the payments module"
- "Document the architecture of the notification service"
- "Write an architecture document for the auth layer"
- "I need an ADR for the messaging integration"

## How to Create an Architecture Spec

### Step 1 — Understand the Context

Determine from the user's input:
- **Name** — the system, module, or layer being documented
- **Scope** — how broad the document should be (system / module / layer / integration)

Before writing, scan the codebase for:
- Existing code, README files, or prior specs that reveal current decisions and constraints
- Related architecture specs in `docs/arch/`

### Step 2 — Generate the Architecture Tech Spec

Create the file at `docs/arch/<name>.arch.md` using the full template in `references/template.md`.

Fill every section with concrete content. Use `[TODO: ...]` only for information that genuinely cannot be inferred and requires a human decision.

### Step 3 — Output Summary

After creating the file:
1. State the file path created
2. Summarize the key architectural decisions documented
3. List any `[TODO: ...]` items that remain open

## Output Location

```
docs/arch/<name>.arch.md
```

## Additional Resources

### Reference Files

- **`references/template.md`** — Full architecture tech spec template with all sections, ADR format, and component table structure
