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
1. Metadata (status, version, dates, owner)
2. Problem definition
3. Proposed solution
4. Technology decisions
5. Detailed design
6. Acceptance criteria
7. Changelog

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

**Output:** Conformance report — one row per acceptance criterion with status: PASS / PARTIAL / FAIL / NOT IMPLEMENTED.

**Pre-conditions:** Spec exists + some implementation exists to check.

**Behavior:**
- Reads the spec's acceptance criteria section.
- Reads the relevant implementation files.
- Reports each AC individually with evidence (file path, line reference, or explanation of gap).
- Concludes with overall PASS (all ACs pass) or FAIL (one or more ACs fail/partial).

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
- Non-functional requirements (latency, throughput, availability targets)
- Architecture Decision Records (ADRs): options considered, rationale, consequences

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

**Output:** Conformance report — one row per architecture rule: PASS / VIOLATION / NOT VERIFIABLE.

**Pre-conditions:** Arch spec exists + codebase to check.

**Checks:**
- Component boundaries respected (no cross-boundary direct calls that bypass defined interfaces)
- Dependency direction matches documented flow
- Naming conventions from the spec appear in the code
- Banned patterns (documented in ADRs as rejected) are not present
- Layer isolation rules enforced

**Behavior on VIOLATION:** Reports the specific file/location, the rule violated, and the ADR that defines the rule.
