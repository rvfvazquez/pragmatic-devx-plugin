---
name: pragmatic-spec-create
description: This skill should be used when the user asks to "create a spec", "write a technical specification", "document this feature as a spec", "create a spec for this story", "create spec for module", "generate a spec", "write a spec document", or needs to formalize a feature, story, or module as a structured technical specification document.
---

# pragmatic-spec-create

Create a structured technical specification document for a feature, story, or module.

## Purpose

Produce a complete, pragmatic spec document that defines the problem, proposed solution, technology decisions, detailed design, and acceptance criteria. Specs live in `docs/specs/` and serve as the source of truth for implementation decisions — **including explicit technology choices made by the team**.

## When This Skill Applies

Use this skill when **no spec exists yet** and the user wants to formally document a feature, story, or module.

**Do not use when:**
- A spec already exists and the user wants to modify it → use `pragmatic-spec-update`
- A spec already exists and the user wants a quality review → use `pragmatic-spec-validate`

**Edge case:** if the user says "improve" or "rewrite" an existing spec, clarify whether they want targeted updates to specific sections (`pragmatic-spec-update`) or to replace the entire document (`pragmatic-spec-create` with a fresh pass).

## How to Create a Spec

### Pre-condition 0 — Check for Project Constitution

Before anything else, check whether `docs/constitution.md` exists.

**If it does NOT exist:**

Use `AskUserQuestion` to ask:

> "No project constitution found at `docs/constitution.md`. A constitution defines cross-module rules, global stack decisions, and AI guardrails that apply to every spec — writing this feature spec without one may produce decisions that conflict with undocumented global constraints.
>
> Would you like to create a constitution first, or continue without one?"

Options:
- **Create constitution first** — end this skill now and run `pragmatic-project-constitution`. Return here after the constitution is created.
- **Continue without it** — proceed. Note that global tech stack and cross-module constraints will not be enforced for this spec.

**If it EXISTS:**

Load `docs/constitution.md` in full and hold it as active context for the rest of this skill. It will be used in Step 4 to skip questions already answered globally and to flag any decisions that conflict with the constitution.

---

### Pre-condition 1 — Check for Existing Spec

Before anything else, determine the `<feature-slug>` from the user's message and check whether `docs/specs/<feature-slug>.md` already exists.

If the file **exists**:
> "A spec already exists at `docs/specs/<feature-slug>.md`. This skill will **replace** it. Did you mean to:
> - Update specific sections → use `pragmatic-spec-update`
> - Review its quality → use `pragmatic-spec-validate`
>
> I will only continue if you explicitly confirm you want to replace the existing spec."

**STOP. Do not proceed until the user explicitly confirms they want to replace the existing spec.** If the user wants to update or validate instead, end this skill now.

---

### Step 0 — Language Selection

Infer the document language before asking:
1. **Detect user message language** — if ≥80% of prose words in the user's message are in pt-BR, es-ES, or en-US, use that language without asking
2. **Check existing specs** — if step 1 is ambiguous (e.g., mostly technical terms or code snippets), scan `docs/specs/` for existing spec files and use their language if uniform
3. **Ask only if inconclusive** — if both steps above are ambiguous, use `AskUserQuestion`:

```
In which language would you like the spec document to be generated?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and use it consistently for **all content** in the generated document — section headings, descriptions, acceptance criteria, TODO comments, and the changelog.

### Step 1 — Understand the Input

Extract from the user's message or conversation context:
- **Feature name or slug** — used for the filename (`docs/specs/<feature-slug>.md`)
- **Problem or goal** — what this feature solves
- **Scope hints** — any details about APIs, data models, behaviors already mentioned

### Step 2 — Confirm Full Picture Before Proceeding

**This is a mandatory step.** Do not proceed until you have a complete understanding of the need.

After extracting the initial input, use `AskUserQuestion` to actively validate and deepen your understanding. The goal is to arrive at a full picture of the problem, the context, and the expected outcome — before touching the codebase or asking technology questions.

Ask only what is genuinely unclear or missing. Adapt the questions to the specific feature.

**`multiSelect` rules for this step — always follow these:**
- **Goals**: `multiSelect: true` — the user may have multiple objectives
- **Non-Goals / Out of scope**: `multiSelect: true` — multiple items can be out of scope simultaneously
- **Success factors / Acceptance criteria hints**: `multiSelect: true` — multiple success signals can apply at once
- **Consumers / Constraints**: `multiSelect: true` when multiple selections are possible

Example format:

```
Before I scan the codebase and ask about technology choices, let me confirm my understanding:

**Problem & Goal**
- [Restate what you understood the feature to solve — ask the user to confirm or correct]
- Who are the main users or consumers of this feature? → multiSelect: true

**Goals** → multiSelect: true
- What are the main objectives of this feature? (select all that apply)

**Non-Goals / Out of Scope** → multiSelect: true
- What is explicitly out of scope? (select all that apply)

**Constraints & Non-Negotiables** → multiSelect: true
- Are there any hard constraints? (deadlines, compliance, existing contracts, performance targets)

**Success Definition** → multiSelect: true
- How will we know this feature is working correctly? (select all that apply)
  Options: e2e flows passing, performance SLA met, staging approval, acceptance tests passing, etc.

Answer what you know — for anything undecided, just say so and we'll handle it as an open item.
```

**STOP. Do not proceed to Step 3 until all three conditions below are met.** A spec written without this confirmation will have gaps that `pragmatic-spec-validate` will FAIL:
- The problem and goal are clearly understood
- The scope boundaries are defined
- Any hard constraints are captured

### Step 3 — Scan Existing Codebase

Before writing, search for:
- Related files or modules that reveal existing patterns and **technology already in use**
- Prior specs in `docs/specs/` that may overlap
- Type definitions, interfaces, or configuration files that reveal tech stack choices

Note any technology already committed to in the codebase — these don't need to be asked again.

### Step 4 — Technology Discovery Interview

**This is a mandatory step.** Ask the user targeted questions about technology decisions that are not already evident from the codebase. Do not make assumptions — let the user choose.

**If a project constitution was loaded in Pre-condition 0:** Before asking any question in this step, check whether the constitution already answers it. If it does, do not ask — state the decision as inherited:

> "Database: PostgreSQL (from project constitution — no choice needed)"

If a technology option the user proposes conflicts with the constitution, flag it immediately:

> "The constitution defines [X] as the only permitted [category]. Choosing [Y] would conflict with the project constitution. To proceed with [Y], update the constitution first via `pragmatic-project-constitution-update`."

Do not silently accept a decision that violates the constitution.

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

**Testing Strategy**
- What test levels are expected for this feature? Options: unit only, unit + integration, unit + integration + e2e, contract tests, no automated tests
- Infer the testing framework from the codebase (Step 3) before asking — only ask if not evident
- Are there coverage gates or quality requirements? (e.g., all acceptance criteria must have a corresponding integration test)

Answer what you know; for anything undecided, just say so and it will remain as an open question in the spec.
```

Adapt the questions to what is actually relevant for the feature described. Skip categories that clearly don't apply. **STOP. Do not write the spec until this step is complete.** Technology decisions skipped here will appear as FAIL findings in `pragmatic-spec-validate`.

### Step 5 — Generate the Spec Document

If the directory `docs/specs/` does not exist, create it before writing the file.

Create the file at `docs/specs/<feature-slug>.md` using the full template in `references/template.md`.

Fill every section with concrete content:
- Capture all technology decisions made in Step 4 in section **5. Technology Decisions**
- Use `[TODO: decide — <options>]` for choices the user marked as undecided, listing the options discussed
- Use `[TODO: describe ...]` for information that cannot be inferred and needs human input

**Section 7 — Acceptance Criteria:** Write every criterion in **Given/When/Then** format: `Given [context], When [action], Then [observable result]`. Each criterion must be specific enough for a developer to write a test case directly from it — no interpretation required. Include at minimum one happy-path criterion and one error or edge-case criterion.

**Code blocks in sections 6.1 and 6.2:** The template uses Go as placeholder syntax. Always adapt code blocks to the project's actual programming language — inferred from Step 3 codebase scan or from the technology stack discussed in Step 4. For example: use TypeScript interfaces for a Node.js project, Python dataclasses or Protocol classes for a Python project, Java interfaces for a JVM project.

#### When to add diagrams

Add a Mermaid diagram to section **6.3 (Behavior & Logic)** when the behavior being described falls into one of these categories:

| Situation | Diagram type |
|-----------|-------------|
| Multi-step request/response flow (3+ steps involving 2+ components) | `sequenceDiagram` |
| State transitions (e.g., order status, approval workflow) | `stateDiagram-v2` |
| Async flow with queues, events, or background processing | `flowchart LR` |

Do **not** add a diagram for simple single-step operations or when the prose is already unambiguous without it. One diagram per distinct flow — do not combine multiple flows into a single diagram.

### Step 6 — Output Summary

After writing the file:
1. State the file path created
2. Summarize the key decisions captured, especially technology choices
3. List any `[TODO: ...]` items that remain open, indicating who needs to decide

**Next step:** run `pragmatic-spec-validate` to verify completeness before sharing with the team or starting implementation.

## Output Location

```
docs/specs/<feature-slug>.md
```

## Additional Resources

### Reference Files

- **`references/template.md`** — Full spec template with all sections and formatting guidance

### Example Files

Use these examples as calibration targets for output structure, level of detail, diagram usage, and writing style. Each example showcases a different diagram type:

- **`examples/example-auth-spec.md`** — JWT authentication feature. Showcases `sequenceDiagram` for multi-step request/response flows (login + middleware validation)
- **`examples/example-order-notifications-spec.md`** — Async email notifications via SQS. Showcases `flowchart LR` for event-driven and asynchronous processing flows
- **`examples/example-order-lifecycle-spec.md`** — Order status state machine. Showcases `stateDiagram-v2` for features with explicit state transitions and validity rules
