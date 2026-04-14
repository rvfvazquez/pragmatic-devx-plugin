# pragmatic-devx-plugin

Claude Code plugin focused on Developer Experience — structured specs, architecture documentation, and pragmatic engineering patterns.

## Installation

**1. Add the marketplace:**

```bash
claude plugin marketplace add https://github.com/rvfvazquez/pragmatic-devx-plugin.git
```

**2. Install the plugin:**

```bash
claude plugin install pragmatic-devx-plugin@pragmatic-devx-plugin
```

After installation, the skills activate automatically. No configuration needed — Claude detects your intent from the conversation and loads the right skill.

## Skills

These are **context-triggered skills**, not slash commands. Just describe what you want in natural language and Claude will apply the right skill automatically.

---

### `spec.create`

Creates a structured technical specification document for a feature, story, or module.

Generates a full spec at `docs/specs/<feature-slug>.md` covering problem statement, goals, proposed solution, detailed design, and acceptance criteria.

**Triggers when you say things like:**
- "Create a spec for the notifications module"
- "Write a technical specification for this feature"
- "Document this story as a spec"
- "I need a spec for the payment flow"

**Example:**

> You: "Create a spec for the user authentication feature — it should support email/password and OAuth via Google."

Claude will scan the codebase for existing patterns, then generate `docs/specs/user-authentication.md` with all sections filled in and `[TODO: ...]` markers for decisions that still need human input.

---

### `spec.update`

Updates an existing specification with new requirements, corrections, or decisions.

Preserves existing content, increments the version, marks removed content as deprecated, and appends a changelog entry.

**Triggers when you say things like:**
- "Update the auth spec — token expiry is now 24h instead of 1h"
- "Add the rate limiting requirement to docs/specs/api-gateway.md"
- "Fill in the TODO items in the payment spec"
- "The acceptance criteria changed, revise the spec"

**Example:**

> You: "Update docs/specs/user-authentication.md — we decided to drop OAuth for now and support only email/password in v1."

Claude will update the relevant sections, bump the version to `1.1.0`, mark the OAuth content with `~~strikethrough~~`, and append a changelog entry with today's date.

---

### `spec.validate`

Validates a specification for completeness, clarity, and consistency.

Runs structured checks across completeness, clarity, consistency, and technical requirements. Outputs a detailed PASS/WARN/FAIL report without modifying the spec.

**Triggers when you say things like:**
- "Validate docs/specs/user-authentication.md"
- "Is this spec ready for review?"
- "Check the payment spec for completeness"
- "Run a quality check on this specification"

**Example:**

> You: "Validate the auth spec before we hand it off to the team."

Claude will check for missing acceptance criteria, vague language, unresolved TODOs, and inconsistencies between the proposed solution and the API design, then print a full report:

```
## Spec Validation Report
Overall Status: WARN

✓ Title & Status
✓ Problem Statement
⚠ Acceptance Criteria — only 1 defined, minimum is 2
✗ Security Considerations — section is empty
```

---

### `arch.spec.create`

Creates a software architecture technical specification document for a system, module, layer, or integration.

Generates a full architecture tech spec at `docs/arch/<name>.arch.md` covering context, design decisions (ADRs), component boundaries, architecture patterns, communication style, data flow, and non-functional requirements.

**Scope options:** `system` | `module` | `layer` | `integration` (default: `module`)

**Triggers when you say things like:**
- "Create an architecture spec for the payments module"
- "Document the architecture of the notification service"
- "Write an arch spec for the auth layer — scope is module"
- "I need an architecture document for the Stripe integration"

**Example:**

> You: "Create an architecture spec for the notification service — it needs to support email, push, and in-app channels."

Claude will scan the codebase for existing patterns, then generate `docs/arch/notification-service.arch.md` with a component diagram, ADRs for key decisions (e.g., sync vs async delivery), dependency direction, data flow for each channel, and a table of NFRs.

---

### `arch.spec.check`

Verifies whether the actual project code and structure conform to the rules declared in one or more architecture tech spec documents.

Language-agnostic — works with any codebase. Uses static analysis (file structure, imports, naming, dependency direction) to check conformance against the spec. Outputs a CONFORMANT/PARTIAL/NON-CONFORMANT report. Each violation includes a mandatory **How to Fix** block with the action, location, and expected outcome.

**Triggers when you say things like:**
- "Check if the code conforms to the architecture spec"
- "Does our project follow the arch spec?"
- "Run an architecture conformance check"
- "Are there any architecture violations in the codebase?"

**Example:**

> You: "Check if the payments module conforms to its architecture spec."

Claude will ask which spec(s) to check and which part of the project to scan, then compare the codebase against the declared components, boundaries, dependency direction, integrations, and patterns — and produce a full conformance report:

```
## Architecture Conformance Report
Overall Status: PARTIAL

### Violations (NON-CONFORMANT)
[Dependency Direction — Section 6] domain/OrderService imports infra/Database directly
  - How to fix:
    - Action: Introduce a repository interface in domain/ and move DB access to infra/
    - Where: src/domain/order_service.go, src/infra/order_repository.go
    - Outcome: domain/ depends only on the interface; infra/ implements it

### Conformant Checks
- All documented components present ✓
- Naming conventions followed ✓
```

---

### `arch.spec.validate`

Validates an architecture tech spec for completeness, consistency, and architectural soundness.

Checks completeness (goals, ADRs, component boundaries, data flow), architectural soundness (single responsibility, dependency direction, no circular coupling), clarity (diagrams, unambiguous language), and design quality. Outputs a structured PASS/WARN/FAIL report grouped by severity.

**Triggers when you say things like:**
- "Validate docs/arch/notification-service.arch.md"
- "Is the auth architecture spec ready for approval?"
- "Check the payments module arch spec for soundness"
- "Review this architecture document before we start building"

**Example:**

> You: "Validate the notification service arch spec — we're about to start implementation."

Claude will run 20 checks across completeness, soundness, clarity, and design quality, then print a grouped report:

```
## Architecture Tech Spec Validation Report
Overall Status: WARN

### Failed Checks (FAIL)
None.

### Warnings (WARN)
[Unresolved TODO] Section 9 — Performance strategy is [TODO: define strategy]

### Checks Passed (18/20)
✓ Context & Motivation
✓ At least one ADR
✓ Component boundaries defined
...
```

---

### `arch.spec.update`

Updates an existing architecture tech spec with new architectural decisions, corrections, or intentional deviations.

Preserves existing ADRs, increments the version semantically (patch/minor/major), deprecates superseded decisions without deleting history, and appends a changelog entry. This is the natural next step when `arch.spec.check` identifies a violation resolved via **Option B** — the code reflects an intentional evolution the spec has not yet captured.

**Triggers when you say things like:**
- "Update the payments arch spec — we adopted the anti-corruption layer"
- "Add an ADR for the caching decision we made"
- "The auth module no longer depends on the user service directly, update the spec"
- "Fill in the TODOs in the notification arch spec"

**Example:**

> You: "Update the notification service arch spec — we decided to use EventBridge instead of direct SQS calls."

Claude will confirm the scope of the change, capture the decision as a new ADR (with options considered, rationale, and consequences), deprecate any superseded ADR, bump the version, and append a changelog entry.

---

## Project Structure

```
pragmatic-devx-plugin/
├── .claude-plugin/
│   ├── plugin.json                # Plugin manifest (name, description, author)
│   └── marketplace.json           # Marketplace registry (lists this plugin)
├── skills/
│   ├── spec.create/
│   │   ├── SKILL.md               # Skill definition & trigger logic
│   │   └── references/
│   │       └── template.md        # Spec document template
│   ├── spec.update/
│   │   └── SKILL.md
│   ├── spec.validate/
│   │   └── SKILL.md
│   ├── arch.spec.create/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── template.md        # Architecture tech spec template
│   ├── arch.spec.validate/
│   │   └── SKILL.md
│   ├── arch.spec.check/
│   │   └── SKILL.md
│   └── arch.spec.update/
│       └── SKILL.md
├── LICENSE
└── README.md
```

## License

MIT
