# Pragmatic DevX — Skill Map

Complete reference for all skills in the pragmatic-devx plugin: purpose, outputs, pre-conditions, and guards.

---

## Governance

### pragmatic-project-constitution-update

**Purpose:** Apply targeted changes to an existing `docs/constitution.md` — new rules, corrected decisions, deprecated constraints — while preserving history and regenerating the auto-loaded rules file.

**Output:** Updated `docs/constitution.md` + regenerated `.claude/rules/00-project-constitution.md`

**Pre-conditions:** `docs/constitution.md` must exist. If not → use `pragmatic-project-constitution`.

**Behavior:**
- Preserves all existing rules; deprecated rules get `~~strikethrough~~` with reference to replacement
- Regenerates `.claude/rules/00-project-constitution.md` with only active (non-deprecated) rules
- Appends changelog entry with date, summary, and motivation
- Bumps version (patch for corrections, minor for new rules)

**Guard:** Confirms scope and motivation before writing — constitution changes are project-wide and affect every spec and session.

---

### pragmatic-project-constitution

**Purpose:** Create `docs/constitution.md` — the single source of truth for decisions that apply across all modules, features, and architecture specs.

**Output:** `docs/constitution.md`

**Pre-conditions:**
- No `docs/constitution.md` exists yet.
- For updates to an existing constitution, a dedicated update skill is planned.

**Covers:**
- Project identity and global technology stack decisions
- Security Baseline (document section 3): authentication model, authorization model, secrets management, data classification, security baseline reference
- Cross-module constraints and naming conventions
- AI behavior guardrails: what Claude must always ask vs. can decide autonomously

**Guard:** If a constitution already exists, STOP and confirm before replacing it. Do not silently overwrite.

---

## Feature Specs

All feature specs live in `docs/specs/<feature-slug>.md`.

---

### pragmatic-spec-create

**Purpose:** Formalize a feature, story, or module as a structured spec document from scratch.

**Output:** `docs/specs/<feature-slug>.md` (Status: Draft)

**Pre-conditions:**
- No spec file exists for this feature slug yet.
- `docs/constitution.md` checked first (load if present).

**Spec sections produced:**
1. Overview (title, status, author, created, version)
2. Problem Statement
3. Goals & Non-Goals
4. Proposed Solution
5. Technology Decisions
6. Detailed Design (API/Interface, Data Model, Behavior & Logic)
7. Acceptance Criteria — includes a security acceptance criterion (negative assertion) when section 8's Security item applies
8. Technical Considerations — includes a required **Security** item (untrusted input, authN, authZ, sensitive data, abuse case), inherited from the constitution Security Baseline where one exists
9. Open Questions

Changelog is not part of the initial document — it is appended later by `pragmatic-spec-update` on the first edit.

**Guard:** If a spec already exists at the target path, STOP. Offer `pragmatic-spec-update` or `pragmatic-spec-validate` instead. Only replace if the user explicitly confirms.

---

### pragmatic-spec-validate

**Purpose:** Structured quality review of an existing spec before it moves to Review or Approved status.

**Output:** PASS / FAIL report with specific failure items and remediation hints.

**Pre-conditions:** Spec exists at `docs/specs/<feature-slug>.md`.

**Checks:**
- Status field is present and valid
- No open `[TODO: ...]` placeholders in critical sections
- Technology decisions are explicit (no "TBD")
- Acceptance criteria are testable and unambiguous
- Section 8 Security item addressed (FAIL/WARN/PASS, not "mentioned"); security criteria are testable
- Internal consistency (no contradictions between sections)
- Changelog is present

---

### pragmatic-spec-update

**Purpose:** Apply targeted changes to an existing spec — new decisions, corrections, additional requirements.

**Output:** Updated `docs/specs/<feature-slug>.md` with incremented version and new changelog entry.

**Pre-conditions:** Spec exists.

**Behavior:**
- Preserves existing content and changelog history.
- Marks removed content as deprecated (strikethrough), not deleted.
- Bumps version (patch for corrections, minor for new requirements).
- Appends changelog entry with date, change description, and author.

**Guard:** If spec is in `Approved` status and the change affects acceptance criteria, confirm with the user before proceeding.

---

### pragmatic-spec-build

**Purpose:** Translate an approved spec into a working implementation, guided by spec decisions, architecture constraints, and project rules.

**Pre-conditions:**
- Spec exists with `Status: Review` or `Status: Approved`.
- No open `[TODO: ...]` items in technology decisions or acceptance criteria.
- Architecture specs loaded from `docs/arch/` if they exist.
- Constitution loaded from `docs/constitution.md` if it exists.

**Guard (HARD):** DO NOT write any implementation code if:
- Spec status is `Draft`
- Spec has unresolved TODO items in critical sections

Assert the block and instruct the user to run `pragmatic-spec-validate` + `pragmatic-spec-update` first.

**Definition of done:** `pragmatic-spec-check` returns PASS for all acceptance criteria.

---

### pragmatic-spec-check

**Purpose:** Verify that the existing implementation matches the spec's acceptance criteria.

**Output:** Conformance report across three independent dimensions — Acceptance Criteria Coverage, Structural Adherence, and Open Items Resolved — each rated PASS / WARN / FAIL / N/A, with an aggregated Overall Status of PASS / WARN / FAIL.

**Pre-conditions:** Spec exists + some implementation exists to check.

**Behavior:**
- Reads the spec's acceptance criteria (section 7), interfaces/types (6.1, 6.2), the section 8 Security item, and open `[TODO: ...]` items.
- Reads the relevant implementation files.
- Dimension 2 (Structural & Security-Control Adherence) verifies section 8 security controls exist in the code (ownership check, input validation, no hardcoded secret). A security-criterion FAIL is always `[code]` and blocks "done".
- Reports each item individually with evidence (file path, line reference, or explanation of gap).
- Recommended Actions are tagged `[code]` or `[pragmatic-spec-update]` depending on whether the fix belongs in the implementation or the spec.

---

## Architecture Specs

All architecture specs live in `docs/arch/<name>.arch.md`.

---

### pragmatic-arch-spec-create

**Purpose:** Formally document the architecture of a system, module, layer, or integration.

**Scope types:**
- `system` — full application or bounded context
- `module` — a single feature module or domain
- `layer` — a horizontal layer (data access, presentation, etc.)
- `integration` — an external integration or adapter

Default scope when not specified: `module`.

**Output:** `docs/arch/<name>.arch.md`

**Pre-conditions:** No arch spec exists for this name yet. `docs/constitution.md` checked first.

**Covers:**
- Component boundaries and responsibilities
- Architecture patterns (layered, hexagonal, CQRS, event-driven, etc.)
- Data flows and key sequence diagrams
- Trust boundaries & attack surface (section 4.3) — conditional on the architecture having more than one trust level
- Non-functional requirements (latency, throughput, availability targets), including a Security row
- Architecture Decision Records (ADRs): options considered, rationale, consequences (with the STRIDE category a decision opens or closes)

**Guard:** If an arch spec already exists at the target path, STOP. Offer `pragmatic-arch-spec-update` or `pragmatic-arch-spec-validate` instead.

---

### pragmatic-arch-spec-validate

**Purpose:** Structured quality review of an existing arch spec — completeness, decision coverage, and ADR quality.

**Output:** PASS / FAIL report with specific failure items.

**Pre-conditions:** Arch spec exists at `docs/arch/<name>.arch.md`.

**Checks:**
- All components defined have documented responsibilities
- At least one ADR present per major technology or pattern decision
- Non-functional requirements are measurable (not "fast" — "< 200ms p99")
- Data flows cover the primary paths
- No open `[TODO: ...]` in ADRs or component definitions

---

### pragmatic-arch-spec-update

**Purpose:** Apply changes to an existing arch spec — new ADRs, corrected decisions, updated component boundaries.

**Output:** Updated arch spec with new/amended ADR, incremented version, changelog entry. Superseded ADRs marked deprecated.

**Pre-conditions:** Arch spec exists.

**Behavior:**
- Adds new ADR entries without removing superseded ones (marks them as deprecated with reference to superseding ADR).
- Bumps version (patch for corrections, minor for new components or ADRs).
- Appends changelog entry.

---

### pragmatic-arch-spec-check

**Purpose:** Verify that the codebase conforms to the documented architecture decisions.

**Output:** Conformance report grouped by severity, with an Overall Status of CONFORMANT / PARTIAL / NON-CONFORMANT.

**Pre-conditions:** Arch spec exists + codebase to check.

**Checks:**
- Component boundaries respected (no cross-boundary direct calls that bypass defined interfaces)
- Dependency direction matches documented flow
- Naming conventions from the spec appear in the code
- Banned patterns (documented in ADRs as rejected) are not present
- Layer isolation rules enforced
- Trust Boundary Conformance (check H, conditional on section 4.3): boundary controls applied before the trusted core, no unguarded path to it, no hardcoded secrets, no undocumented network entry points

**Behavior on VIOLATION:** Reports the specific file/location, the rule violated, and the ADR that defines the rule.

---

## Reverse Engineering

### pragmatic-reverse-engineer

**Purpose:** Generate a feature spec or architecture spec by scanning
existing, undocumented code, then handing off to `pragmatic-spec-create` /
`pragmatic-arch-spec-create` to write it.

**Output:** Does not create documents in `docs/specs/` or `docs/arch/`
itself — see those two skills for authorship. Its only edit to an existing
document there is the Provenance append (Step 4). Owns only
`docs/reverse-engineering/<session-slug>-<date>.report.md`.

**Pre-conditions:** None of its own — the downstream create skill's
pre-conditions (constitution check, existing-file guard) run unmodified
when invoked.

**Behavior:**
- Always asks Architecture / Feature / Both before scanning anything.
- Tags every finding CONFIRMED (observable in code) or INFERRED (a guess
  about intent) — CONFIRMED items are stated to the downstream skill
  outright, INFERRED items are surfaced for the user to confirm or correct.
- Runs a security pass and tags **SECURITY-GAP** findings (missing ownership
  check, hardcoded secret, unauthenticated entry point, unparameterized
  input, sensitive data in logs) — never fixed here, surfaced for the user
  to confirm as intentional or record as a `[TODO]`.
- Processes multiple discovery targets one at a time, never batched, so
  each downstream interview stays scoped to one target.
- Appends a `## Provenance` section to each document the downstream skill
  writes, and a session report tying all of them together.

**Guard:** Never creates or owns documents in `docs/specs/` or `docs/arch/`
— those remain owned exclusively by `pragmatic-spec-create` /
`pragmatic-arch-spec-create`. Its only edit to those files is the
Provenance append (Step 4).
