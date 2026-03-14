---
name: spec.create
description: This skill should be used when the user asks to "create a spec", "write a technical specification", "document this feature as a spec", "create a spec for this story", "create spec for module", "generate a spec", "write a spec document", or needs to formalize a feature, story, or module as a structured technical specification document.
version: 0.1.0
---

# spec.create

Create a structured technical specification document for a feature, story, or module.

## Purpose

Produce a complete, pragmatic spec document that defines the problem, proposed solution, detailed design, and acceptance criteria. Specs live in `docs/specs/` and serve as the source of truth for implementation decisions.

## When This Skill Applies

Apply this skill whenever a user describes a feature, story, or module that needs to be formally documented before or during implementation. Common triggers:

- "Create a spec for the authentication module"
- "I need a spec for this payment feature"
- "Document this story as a spec"
- "Write up the technical spec for X"

## How to Create a Spec

### Step 1 — Understand the Input

Extract from the user's message or conversation context:
- **Feature name or slug** — used for the filename (`docs/specs/<feature-slug>.md`)
- **Problem or goal** — what this feature solves
- **Scope hints** — any details about APIs, data models, behaviors already mentioned

When context is insufficient, ask one focused question before proceeding.

### Step 2 — Scan Existing Codebase

Before writing, search for:
- Related files or modules that reveal existing patterns
- Prior specs in `docs/specs/` that may overlap
- Type definitions or interfaces already in place

### Step 3 — Generate the Spec Document

Create the file at `docs/specs/<feature-slug>.md` using the full template in `references/template.md`.

Fill every section with concrete content. Use `[TODO: describe ...]` only for information that cannot be inferred and needs a human decision.

### Step 4 — Output Summary

After writing the file:
1. State the file path created
2. Summarize the key decisions captured
3. List any `[TODO: ...]` items that remain open

## Output Location

```
docs/specs/<feature-slug>.md
```

## Additional Resources

### Reference Files

- **`references/template.md`** — Full spec template with all sections and formatting guidance
