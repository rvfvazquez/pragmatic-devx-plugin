# Architecture Tech Spec Template

Use this template when creating a new architecture tech spec. Fill all sections with concrete content; use `[TODO: ...]` only when information requires a human decision.

---

## 1. Overview

- **Name**: System / module name
- **Scope**: system | module | layer | integration
- **Status**: Draft | Review | Approved
- **Author**: (infer from git config or leave blank)
- **Created**: (today's date)
- **Version**: 1.0.0

## 2. Context & Motivation

Why does this architecture exist? What problem does it solve? What drove the design decisions?
Include a brief description of the business or technical context.

## 3. Goals & Constraints

**Architectural Goals:**
- List quality attributes being optimized (e.g., maintainability, scalability, testability)

**Constraints:**
- Technology or platform constraints
- Team or organizational constraints
- Non-functional requirements (performance SLAs, security requirements)

**Non-Goals:**
- What this architecture intentionally does not address

## 4. High-Level Design

Describe the overall structure in prose. Explain the main building blocks and how they relate.

### 4.1 Component Diagram (ASCII or Mermaid)

```mermaid
graph TD
  A[Component A] --> B[Component B]
  B --> C[Component C]
```

### 4.2 Component Boundaries

| Component | Responsibility | Public Interface | Trust level |
|-----------|---------------|-----------------|-------------|
| `component-a` | ... | `ServiceA` | untrusted edge — validates all inbound input |
| `component-b` | ... | `RepositoryB` | trusted core — assumes input already validated |

> Include the **Trust level** column only if this architecture has more than one trust
> level (see 4.3). If the whole system sits in a single trust domain, drop the column.

### 4.3 Trust Boundaries & Attack Surface

> **Assess applicability before writing this subsection.** This architecture has more
> than one trust level if any of these hold:
> - it exposes a network endpoint or receives input from outside its own process
> - it serves more than one tenant, customer, or actor role
> - it carries data across a process or host boundary from a less trusted zone
> - the project constitution defines a Security Baseline this scope must enforce
>
> **If yes:** fill the table and the attack-surface line below.
> **If no** (internal library, single-trust-domain batch job, pure computation module):
> replace the table with one sentence stating that and why, and skip the rest. Do not
> invent boundaries that do not exist.

Each row is a point where control or data passes from a less trusted zone into a more trusted one.

| Boundary (from → to) | What crosses it | Control applied on crossing |
|---|---|---|
| Internet → API Gateway | HTTP requests | authN, rate limiting, schema validation |
| API → Worker (via queue) | job messages | payload validation, idempotency key |
| Tenant context → shared store | queries | tenant-scoped filter enforced in the data layer |

**Attack surface of this architecture:** <public endpoints, open ports, file/upload intake, inbound webhooks, admin interfaces — every way external input enters>.

## 5. Key Design Decisions

Document significant architectural decisions using ADR format:

### Decision 1: [Short title]

- **Status**: Accepted | Proposed | Deprecated
- **Context**: Why was this decision needed?
- **Decision**: What was decided?
- **Rationale**: Why this option over alternatives?
- **Consequences**: What are the trade-offs and implications?

> If a decision changes the attack surface or a trust boundary (new inbound channel,
> a moved or removed authorization check, a new place a classified data category is
> stored), say so in **Consequences** and name the STRIDE category it opens or closes
> — Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, or
> Elevation of privilege.

### Decision 2: [Short title]

*(repeat as needed)*

## 6. Architecture Patterns & Conventions

### 6.1 Component Structure

Describe the standard layout and organization for components in this system.

### 6.2 Dependency Direction

Define the allowed dependency flow between layers or components. Use a Mermaid `flowchart TD` to make allowed and forbidden directions explicit:

```mermaid
flowchart TD
  Handler --> Service
  Service --> Domain
  Repository --> Domain
  Gateway --> Domain

  style Domain fill:#d4edda,stroke:#28a745
```

> Add a note below the diagram listing any explicitly **forbidden** dependencies (e.g., "Domain must never import from Repository, Gateway, or Handler").

### 6.3 Communication Style

How do components communicate? (e.g., direct calls, events, message queues, REST, gRPC)

### 6.4 Error Handling Strategy

How errors propagate across boundaries and how they are surfaced to consumers.

## 7. Data Flow

Describe 1–3 key flows with enough detail to understand runtime behavior. Use Mermaid diagrams — do not use plain text arrows.

- Use `sequenceDiagram` for synchronous request/response flows
- Use `flowchart LR` when the flow involves async steps, queues, events, or conditional branching

### Flow 1: [Name of the primary flow]

```mermaid
sequenceDiagram
  participant Client
  participant Handler
  participant Service
  participant Repository
  Client->>Handler: POST /resource (payload)
  Handler->>Service: call business method
  Service->>Repository: persist entity
  Repository-->>Service: entity saved
  Service-->>Handler: result
  Handler-->>Client: 201 Created
```

### Flow 2: [Name of an async or event-driven flow, if applicable]

```mermaid
flowchart LR
  A[Trigger] --> B[Service]
  B --> C[(Database)]
  B --> D[Outbox]
  D --> E[Queue]
  E --> F[Consumer]
```

## 8. External Integrations & Dependencies

| Dependency | Type | Purpose | Owned by |
|-----------|------|---------|---------|
| PostgreSQL | Infrastructure | Primary data store | Platform team |
| Auth Service | External API | Token validation | Identity team |

## 9. Non-Functional Requirements & Strategies

| Attribute | Requirement | Strategy |
|-----------|------------|---------|
| Testability | Business logic must be unit-testable | Dependency inversion, pure functions |
| Maintainability | Low coupling between components | Defined interfaces, bounded contexts |
| Performance | < 200ms p95 response time | [TODO: define strategy] |
| Security | Every trust boundary in 4.3 enforces its stated control; no component trusts data from outside its zone; no secret in source | Validation at the edge, typed domain models, ownership/authorization checks in the service layer, secrets via injected environment |

> If 4.3 concluded this is a single trust domain, set the Security row to
> "Single trust domain — no external attack surface (see 4.3)" rather than deleting it.

## 10. Open Questions

- [ ] [TODO: question]
