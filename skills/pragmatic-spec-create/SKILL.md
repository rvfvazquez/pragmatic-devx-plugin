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

> "No project constitution found at `docs/constitution.md`. A constitution defines the global tech stack, the project **Security Baseline** (authentication model, authorization model, secrets management, data classification), cross-module rules, and AI guardrails that apply to every spec — writing this feature spec without one means its Technology Decisions and its section 8 Security item start from a blank slate instead of inheriting project-wide decisions.
>
> Would you like to create a constitution first, or continue without one?"

Options:
- **Create constitution first** — end this skill now and run `pragmatic-project-constitution`. Return here after the constitution is created.
- **Continue without it** — proceed. Note that the global tech stack, Security Baseline, and cross-module constraints will not be available to anchor this spec.

**If it EXISTS:**

Load `docs/constitution.md` in full and hold it as active context for the rest of this skill. It will be used in Step 4 to skip technology questions already answered globally, in Step 5 to fill the section 8 Security item from the constitution's **Security Baseline**, and throughout to flag any decision that conflicts with the constitution.

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

**Security & Abuse** → multiSelect: true
- Who must **not** be able to do this? (other users / other tenants / unauthenticated callers / lower-privilege roles)
- What is the worst thing a malicious *authenticated* user could try here? (read or modify someone else's data, replay a request, enumerate ids, smuggle input into a query or template)
- Does this touch data that has handling rules — PII, credentials, financial, health?
  Skip this group only if the feature has no external input, no persistence of user data, and no network surface — and say so explicitly.

**Success Definition** → multiSelect: true
- How will we know this feature is working correctly? (select all that apply)
  Options: e2e flows passing, performance SLA met, staging approval, acceptance tests passing, etc.

Answer what you know — for anything undecided, just say so and we'll handle it as an open item.
```

The **Security & Abuse** answers feed section 8's Security item and, when any is applicable, the mandatory security acceptance criterion in section 7. If a project constitution is loaded, cross-check these answers against its Security Baseline rather than asking from scratch.

**STOP. Do not proceed to Step 2.5 until all four conditions below are met.** A spec written without this confirmation will have gaps that `pragmatic-spec-validate` will FAIL:
- The problem and goal are clearly understood
- The scope boundaries are defined
- Any hard constraints are captured
- The Security & Abuse group is answered, or explicitly established as not applicable

### Step 2.5 — Scope Validation

Evaluate whether the described scope is cohesive or spans multiple independent subsystems.

**Signs of over-broad scope — flag if two or more apply:**
- The feature name or description joins independent capabilities with "and" (e.g., "authentication and billing")
- The acceptance criteria would describe multiple distinct user workflows with no shared data model or primary entry point
- Removing one part of the scope would leave a complete, independently shippable feature

**If the scope appears to cover multiple independent subsystems**, do NOT proceed to Step 3. Assert:

> "This feature covers **[A]** and **[B]** — these look like independent subsystems. A single spec spanning both will produce acceptance criteria that are harder to verify independently and will make `pragmatic-spec-check` less precise.
>
> **Recommended:** create separate specs:
> - `docs/specs/<subsystem-a>.md`
> - `docs/specs/<subsystem-b>.md`
>
> If these subsystems are genuinely interdependent (shared data model, single deployment unit, or one cannot ship without the other), confirm and I will proceed with a single spec."

**STOP. Wait for user confirmation before proceeding.**
- User confirms interdependence → proceed to Step 3
- User agrees to split → end this skill; run `pragmatic-spec-create` separately for each subsystem

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
> "Authentication: platform OIDC provider (from project constitution Security Baseline — no choice needed)"
> "Authorization: per-resource ownership check (from project constitution Security Baseline)"

The constitution's **Security Baseline** (authentication model, authorization model, secrets management, data classification) is inherited the same way the tech stack is — do not re-ask it, and carry it into the section 8 Security item in Step 5.

If a technology option the user proposes conflicts with the constitution, flag it immediately:

> "The constitution defines [X] as the only permitted [category]. Choosing [Y] would conflict with the project constitution. To proceed with [Y], update the constitution first via `pragmatic-project-constitution-update`."

Do not silently accept a decision that violates the constitution.

Use `AskUserQuestion` to ask. Group questions by concern to avoid overwhelming the user.

**Every question must carry a recommended answer (`➡️`).** Derive it in this priority order:
1. The project constitution, if it leans toward an option even without mandating it
2. Patterns found in the codebase scan (Step 3) — e.g. an existing message broker, existing auth middleware, existing test pyramid
3. A pragmatic default for the stack in use, stated as such (e.g. "no strong signal — defaulting to X because Y")

Never present a bare menu with no recommendation — the user should be able to just confirm the `➡️` line instead of picking from scratch every time.

Example format:

```
Before I write the spec, I need to clarify a few technology decisions:

**Data Layer**
- Where will this data be stored? Options: PostgreSQL, DynamoDB, Redis, in-memory, existing DB
  ➡️ PostgreSQL — codebase already uses the `pg` client in 3 other modules
- Do you need a cache layer? (yes / no / undecided)
  ➡️ No — nothing in scope suggests a read-heavy access pattern yet

**API / Interface**
- How should this be exposed? Options: REST endpoint, GraphQL mutation, internal service call, event/message
  ➡️ REST endpoint — matches the existing `/api/*` convention in this repo
- Any authentication/authorization requirement? (JWT, OAuth, API key, existing auth middleware)
  ➡️ Existing auth middleware — already enforced on all `/api/*` routes

**Async / Background Processing**
- Does any part of this need to run asynchronously? Options: background job, queue (SQS/RabbitMQ/etc.), cron, synchronous only
  ➡️ Synchronous only — no fan-out or long-running work described so far

**Infrastructure / Deployment**
- Are there constraints on where this runs? (Lambda, container, specific region, existing service)
  ➡️ Same container as the rest of the service — no isolation requirement stated

**Testing Strategy**
- What test levels are expected for this feature? Options: unit only, unit + integration, unit + integration + e2e, contract tests, no automated tests
  ➡️ Unit + integration — matches the project's existing test pyramid (found in Step 3)
- Infer the testing framework from the codebase (Step 3) before asking — only ask if not evident
- Are there coverage gates or quality requirements? (e.g., all acceptance criteria must have a corresponding integration test)
  ➡️ State the repo's existing convention if one was found in Step 3, otherwise recommend "all acceptance criteria have a corresponding integration test"

Answer what you know, or just confirm the ➡️ recommendation. For anything undecided, say so and it will remain as an open question in the spec.
```

Adapt the questions to what is actually relevant for the feature described. Skip categories that clearly don't apply. **STOP. Do not write the spec until this step is complete.** Technology decisions skipped here will appear as FAIL findings in `pragmatic-spec-validate`.

### Step 4.5 — Follow-up Round for Dependent Decisions

After the user answers Step 4, check whether any answer unlocks a **dependent decision** that could not have been asked before it (its options only make sense given the parent answer). Common triggers:

| Parent answer | Dependent question to ask now |
|---|---|
| Queue (SQS/RabbitMQ/etc.) | Which queue? FIFO or standard? Dead-letter queue needed? |
| REST endpoint | Sync or paginated response? Rate limiting? |
| JWT / OAuth | Token lifetime? Refresh flow? Which claims are required? |
| Background job | Retry policy? Max attempts? Idempotency key strategy? |

If any dependent question applies, ask it now via `AskUserQuestion` — **with a recommended answer, following the same rule as Step 4** — instead of deferring it straight to `[TODO: decide]`. Only questions whose parent decision itself remained undecided should still become TODOs.

Run this check once. A second round should not itself spawn a third round unless the feature is unusually deep — if it does, proceed to Step 5 anyway and leave the remainder as TODOs rather than turning the interview into an unbounded loop.

### Step 4.6 — Final Consistency Check

Before generating the document, assemble every decision confirmed across Steps 2, 2.5, 4, and 4.5 into one list, grouped by area. Scan pairwise across areas for **contradiction** — not completeness (that is `pragmatic-spec-validate`'s job) — only cases where one confirmed decision makes another confirmed decision incoherent, redundant, or impossible.

Known contradiction shapes to check for:

| Area A | Area B | Contradiction pattern |
|---|---|---|
| Non-Goals | Technology Decisions | A technology choice implements something explicitly marked out of scope |
| Constraints (deadline) | Testing Strategy | Heavy test strategy (e2e + contract tests) against a tight, explicit deadline — worth flagging, not blocking |
| Consumers | API/Interface | Consumers include external parties, but the interface choice is "internal service call" |
| Success Definition | Acceptance Criteria hints | A stated success signal has no corresponding criterion discussed |

If no contradiction is found, skip straight to the recap below — do not manufacture a check for its own sake, and do not re-ask anything already confirmed.

**If a contradiction is found, do not silently resolve it.** Present it explicitly and wait:

> ⚠️ Possible contradiction: [Decision A, with its section] says "...", but [Decision B, with its section] says "...". These look inconsistent because [reason]. Which should hold — or is there context I'm missing that makes both correct?

Once no contradictions remain (or none were found), present the full recap and require explicit confirmation before writing anything:

> Here's the complete picture before I write the spec:
> **Problem & Goals:** [one-line summary]
> **Non-Goals:** [one-line summary]
> **Constraints:** [one-line summary]
> **Security & Abuse:** [who must not do this; the abuse case; data sensitivity — or "not applicable because ..."]
> **Technology Decisions:** [one-line summary per area from Step 4]
>
> Confirm this is complete, or tell me what's missing or wrong.

**STOP. Do not proceed to Step 5 until the user explicitly confirms.**

### Step 5 — Generate the Spec Document

If the directory `docs/specs/` does not exist, create it before writing the file.

Create the file at `docs/specs/<feature-slug>.md` using the full template in `references/template.md`.

Fill every section with concrete content:
- Capture all technology decisions made in Step 4 in section **5. Technology Decisions**
- Use `[TODO: decide — <options>]` for choices the user marked as undecided, listing the options discussed
- Use `[TODO: describe ...]` for information that cannot be inferred and needs human input

**Section 7 — Acceptance Criteria:** Write every criterion in **Given/When/Then** format: `Given [context], When [action], Then [observable result]`. Each criterion must be specific enough for a developer to write a test case directly from it — no interpretation required. Include at minimum one happy-path criterion and one error or edge-case criterion. If the Security item in section 8 has any applicable (non-`N/A`) entry, also include the conditional security criterion the template requires — a negative assertion (non-owner → `404`, unauthorized role → `403`, malformed input rejected) with an explicit status code.

**Section 8 — Security item:** Fill every sub-item (untrusted input, authentication, authorization, sensitive data, abuse case) with concrete handling or `N/A — <reason>`. Never leave it as a bare "security considerations" line. For any feature exposing an endpoint or handler, touching user data or PII, or processing external input, at least one sub-item must be non-`N/A`. Populate it from, in order: (1) the constitution's Security Baseline if one was loaded — state the inherited decision, e.g. "Authentication: platform OIDC (from constitution)"; (2) the Step 2 Security & Abuse answers — the "worst thing a malicious authenticated user could try" becomes the *Abuse case*; (3) the feature's own design.

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

---

> **Spec created** — `docs/specs/<feature-slug>.md` (Status: Draft).
>
> **Next step:** Run `pragmatic-spec-validate` to check completeness before sharing with the team or starting implementation.
> FAIL or WARN items → resolve with `pragmatic-spec-update` → re-validate until PASS → then proceed to `pragmatic-spec-build`.

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
