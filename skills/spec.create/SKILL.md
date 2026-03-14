---
name: spec.create
description: This skill should be used when the user asks to "create a spec", "write a technical specification", "document this feature as a spec", "create a spec for this story", "create spec for module", "generate a spec", "write a spec document", or needs to formalize a feature, story, or module as a structured technical specification document.
---

# spec.create

Create a structured technical specification document for a feature, story, or module.

## Purpose

Produce a complete, pragmatic spec document that defines the problem, proposed solution, technology decisions, detailed design, and acceptance criteria. Specs live in `docs/specs/` and serve as the source of truth for implementation decisions — **including explicit technology choices made by the team**.

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

### Step 2 — Scan Existing Codebase

Before writing, search for:
- Related files or modules that reveal existing patterns and **technology already in use**
- Prior specs in `docs/specs/` that may overlap
- Type definitions, interfaces, or configuration files that reveal tech stack choices

Note any technology already committed to in the codebase — these don't need to be asked again.

### Step 3 — Technology Discovery Interview

**This is a mandatory step.** Ask the user targeted questions about technology decisions that are not already evident from the codebase. Do not make assumptions — let the user choose.

Use `AskUserQuestion` to ask. Group questions by concern to avoid overwhelming the user. Example format:

```
Before I write the spec, I need to clarify a few technology decisions:

**Data Layer**
- Where will this data be stored? Options: PostgreSQL, DynamoDB, Redis, in-memory, existing DB
- Do you need a cache layer? (yes / no / undecided)

**API / Interface**
- How should this be exposed? Options: REST endpoint, GraphQL mutation, internal service call, event/message
- Any authentication/authorization requirement? (JWT, OAuth, API key, existing auth middleware)

**Async / Background Processing**
- Does any part of this need to run asynchronously? Options: background job, queue (SQS/RabbitMQ/etc.), cron, synchronous only

**Infrastructure / Deployment**
- Are there constraints on where this runs? (Lambda, container, specific region, existing service)

Answer what you know; for anything undecided, just say so and it will remain as an open question in the spec.
```

Adapt the questions to what is actually relevant for the feature described. Skip categories that clearly don't apply. Do **not** proceed to writing the spec until this step is done.

### Step 4 — Generate the Spec Document

Create the file at `docs/specs/<feature-slug>.md` using the full template in `references/template.md`.

Fill every section with concrete content:
- Capture all technology decisions made in Step 3 in section **5. Technology Decisions**
- Use `[TODO: decide — <options>]` for choices the user marked as undecided, listing the options discussed
- Use `[TODO: describe ...]` for information that cannot be inferred and needs human input

### Step 5 — Output Summary

After writing the file:
1. State the file path created
2. Summarize the key decisions captured, especially technology choices
3. List any `[TODO: ...]` items that remain open, indicating who needs to decide

## Output Location

```
docs/specs/<feature-slug>.md
```

## Additional Resources

### Reference Files

- **`references/template.md`** — Full spec template with all sections and formatting guidance
