---
name: pragmatic-spec-validate
description: This skill should be used when the user asks to "validate a spec", "check if this spec is complete", "review the spec for completeness", "is this spec good?", "check the spec quality", "review this specification", "audit the spec", or wants a structured quality review of an existing specification document.
---

# pragmatic-spec-validate

Validate a technical specification for completeness, clarity, and consistency.

## Purpose

Run a structured review of a spec document and produce a PASS/WARN/FAIL report. Do not modify the spec — only report findings with actionable suggestions.

## When This Skill Applies

Use this skill when a spec **already exists** and the user wants a quality assessment — regardless of whether implementation has started.

**Do not use when:**
- No spec exists yet → use `pragmatic-spec-create`
- The user wants to apply changes to an existing spec → use `pragmatic-spec-update`

**Edge case:** if the user says "review the spec" but also wants edits applied, clarify intent before proceeding: "Do you want a quality report only, or should I apply fixes as well?"

## How to Validate a Spec

### Step 0 — Language Detection

Infer the report language from the existing spec:
1. If the spec contains a `Language:` metadata field, use it
2. Otherwise, infer from the majority language of prose content in sections 2, 3, and 4 (Problem Statement, Goals, Proposed Solution) — if ≥80% of prose words are attributable to a single language, use that language
3. If the spec contains no prose (only tables and code blocks), or if no single language reaches the 80% threshold, treat as ambiguous and use `AskUserQuestion`:

```
In which language would you like the validation report to be generated?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Record the chosen language and use it for **all report content** — section headings, check descriptions, notes, and recommended actions.

### Step 1 — Locate and Read the Spec

Find the spec file. Common locations: `docs/specs/`, `specs/`, or the path provided. Read the full document before running any checks.

For the Alignment checks in Step 2, look for `docs/constitution.md` and for the arch spec(s) in `docs/arch/` that cover this feature's module, layer or integration (match on the feature slug, component names and boundaries in the arch spec's section 4.2). If several arch specs plausibly apply, read each; if none matches, there is none. Do not ask — absence is an `N/A`, not a question.

For the Domain Language checks in Step 2, call the Skill tool with `pragmatic-domain-language` (once per session — without a Skill tool, read `../pragmatic-domain-language/SKILL.md`) and apply **§1 Locate the Context** — without asking: if several contexts plausibly apply, read each.

### Step 1.5 — Pre-scan: Detect Open TODO Items

**This is a mandatory step before running any checks.**

After reading the spec in Step 1, count all `[TODO: ...]` occurrences across the document. If any are found, use `AskUserQuestion` to ask:

> "I found **N open TODO item(s)** in this spec. These will result in WARN or FAIL findings. Would you like to:
> 1. **Resolve them first** with `pragmatic-spec-update` — for a cleaner validation report
> 2. **Continue with validation as-is** — TODOs will be reported as findings"

**STOP. Wait for the user's choice before proceeding.** If the user chooses to resolve TODOs first, end this skill and defer to `pragmatic-spec-update`.

---

### Step 2 — Run Validation Checks

Evaluate each criterion below. Report **PASS**, **WARN**, **FAIL**, or **N/A** with a short explanation for each.

**N/A** may be used only for the checks listed below, under the stated conditions. All other checks must produce PASS, WARN, or FAIL.

| Check | N/A condition |
|-------|---------------|
| Non-goals defined | N/A if this is an exploratory spec where scope is intentionally open |
| Acceptance Criteria (≥2 testable) | N/A if this is a design-only spec with no implementation expected |
| No unresolved TODOs | N/A if the spec is explicitly in Draft status (TODOs expected) |
| Criteria are testable | N/A if the spec has no acceptance criteria (see row above) |
| Interface matches design | N/A if sections 6.1/6.2 are absent |
| Breaking changes flagged | N/A for brand-new features with no prior API surface |
| Security considerations addressed | N/A only if ALL hold: no network surface, no persistence of user or third-party data, no external input. Must be asserted explicitly in the report, not assumed. |
| Security criteria testable | N/A if section 8's Security item has no applicable entries (all `N/A — <reason>`) |
| Single feature focus | N/A if the spec explicitly documents a bounded context that intentionally includes multiple related subsystems |
| Invariants verified | N/A if section 6.2 states `None — <reason>`, or the spec introduces or changes no data model |
| Constitution alignment | N/A if `docs/constitution.md` does not exist |
| Architecture alignment | N/A if no arch spec in `docs/arch/` covers this feature |
| Domain Language checks (all four) | N/A if `docs/glossary/` does not exist — the project has no glossary yet |
| Operational characteristics addressed | N/A if the feature involves no background/async processing, no concurrent/shared-state workflows, and no user interface |

#### Completeness
- **Title & Status** — Has a clear title and a defined status (Draft/Review/Approved)
- **Problem Statement** — Clearly describes the problem being solved
- **Goals defined** — At least one goal is stated
- **Non-goals defined** — Explicitly states what is out of scope *(may be N/A — see table above)*
- **Proposed Solution** — Describes the approach at a high level
- **Acceptance Criteria** — Has at least 2 testable acceptance criteria *(may be N/A — see table above)*
- **No unresolved TODOs** — No `[TODO: ...]` placeholders remain *(WARN if present; N/A if spec is Draft — see table above)*

#### Clarity
- **Unambiguous language** — No vague terms like "fast", "good", "easy" without measurable definitions
- **Acronyms defined** — All non-obvious acronyms are explained on first use
- **Consistent terminology** — Key terms are used consistently throughout

#### Consistency
- **Criteria are testable** — Each acceptance criterion specifies an actor, an action, and an observable result. FAIL if any criterion uses vague language ("the system should work correctly", "it should be fast") without measurable definitions. WARN if criteria are not in Given/When/Then format but are otherwise unambiguous. *(may be N/A — see table above)*
- **Error/edge cases covered** — At least one acceptance criterion addresses an error path, boundary condition, or edge case (not only happy path). *(may be N/A — see table above)*
- **Security criteria testable** — If section 7 contains security criteria, each names an actor, an action, and an observable result (an HTTP status code, the absence of protected data in the response). FAIL if a security criterion is vague ("must be secure", "unauthorized access is blocked" with no status). *(N/A if section 8's Security item has no applicable entries)*
- **Interface matches design** — If APIs/interfaces are defined, they align with the described behavior *(may be N/A — see table above)*
- **No contradictions** — Goals do not contradict the proposed solution or acceptance criteria
- **Invariants verified** — Section 6.2 has an Invariants table, and each invariant names a section 7 criterion that exists and asserts that rule. WARN if the table is missing while section 6.2 introduces or changes data, or if an invariant has no verifying criterion (or names one that asserts something else). *(may be N/A — see table above)*

#### Technology Decisions
- **Technology Decisions section present** — Spec contains an explicit Technology Decisions table or equivalent section
- **No implicit technology assumptions** — Mentions of databases, queues, caches, or frameworks are backed by an explicit decision, not just assumed
- **Undecided items flagged** — Any `[TODO: decide — options: ...]` items are listed in Open Questions so they are visible and actionable
- **Rationale captured** — Each technology decision includes at least a brief reason (or references team convention / existing stack)

#### Technical
- **Dependencies identified** — External dependencies and integrations are listed
- **Breaking changes flagged** — Any breaking changes are explicitly noted *(may be N/A — see table above)*
- **Security considerations addressed** — Evaluate the Security item in section 8:
  - **FAIL** if the spec exposes an endpoint or handler, touches user data or PII, or processes external input, and the Security item is absent or every sub-item is `N/A` without a stated reason
  - **FAIL** if the Security item has an applicable entry (authorization, sensitive data, untrusted input, abuse case) but section 7 has no corresponding security acceptance criterion
  - **WARN** if the Security item is present but the *Abuse case* sub-item is empty or unaddressed
  - **PASS** if every sub-item is addressed (handled or `N/A — <reason>`) and, where applicable, section 7 contains at least one testable security criterion
  *(may be N/A — see table above)*
- **Operational characteristics addressed** — Evaluate resilience and runtime behavior according to the feature's operational context (never impose an arbitrary universal checklist or re-ask discovered facts):
  - **Background / Async / Job processing** (queues, events, webhooks, cron, batch workers): evaluate whether retry policy, idempotency / replay mechanisms, and failure / dead-letter handling are addressed. **WARN** if the spec defines async processing or workers but omits recovery or idempotency.
  - **Concurrency / Shared state**: evaluate whether race condition handling, atomic updates, or locking/isolation invariants are specified. **WARN** if concurrent mutations to shared state are specified without consistency controls.
  - **User interfaces (UI)**: evaluate whether empty states, loading/error feedback, and accessible interactions are defined. **WARN** if UI interactions are specified without error/empty states.
  - **PASS** if applicable operational characteristics are addressed with concrete behavior or explicit decisions.
  *(may be N/A — see table above)*

#### Alignment
Compare only what the spec states; a decision the spec does not mention is silence, never a conflict. A contradiction is a **documented deviation** only when the spec names the constitution or arch spec entry it departs from and gives a reason (in the Rationale cell of section 5, or in the section 8 Security item). A documented deviation is `PASS` with the deviation quoted in the note — do not re-litigate it.
- **Constitution alignment** — Compare section 5 (Technology Decisions) and the section 8 Security item with the constitution's Global Tech Stack (section 2), Security Baseline (section 3) and Cross-Module Rules (section 4). **FAIL** if a decision contradicts a constitution entry (a different database or language, a different authentication or authorization model, a data category the Security Baseline bars from logs, a rule against importing another module's data layer) and is not a documented deviation. Quote both sides in the note: the spec's decision and the constitution entry. *(may be N/A — see table above)*
- **Architecture alignment** — Compare sections 5, 6 and 8 with the arch spec's Component Boundaries (4.2), Dependency Direction (6.2), Communication Style (6.3), Error Handling (6.4) and External Integrations (8). **FAIL** if the spec places code outside its component's boundary, imports across a forbidden direction, uses a communication style the arch spec forbids, or adds an integration the arch spec does not list as permitted, and it is not a documented deviation. Quote both sides in the note. *(may be N/A — see table above)*

#### Domain Language
Run the **base checks 1–4 of §4 Validation Checks** in `pragmatic-domain-language` against this spec, one report row each: **No avoided terms**, **Domain terms defined**, **Context map consistent**, **Glossary hygiene**. WARN at most, never FAIL; quote the glossary entry in each note. *(may be N/A — see table above)*

#### Scope
- **Single feature focus** — Section 7 (acceptance criteria) describes one cohesive feature. WARN if criteria span multiple independent user workflows with no shared data model or flow — such a spec is better split into separate documents. *(may be N/A — see table above)*

### Step 3 — Generate Validation Report

Produce the report in this format:

```
## Spec Validation Report
**File:** <file path>
**Date:** <today>
**Overall Status:** PASS | WARN | FAIL

### Summary
- Passed:   X checks
- Warnings: X checks
- Failed:   X checks
- N/A:      X checks (not counted in totals above)

### Details
| Check | Status | Notes |
|-------|--------|-------|
| Title & Status | PASS | |
| Problem Statement | WARN | Section exists but is vague |
| Breaking changes flagged | N/A | New feature, no prior API surface |
| ... | | |

### Recommended Actions
1. <action item>
2. <action item>
```

### Output Rules

- Print the full report; do **not** modify the spec file or any glossary file
- **If an Alignment FAIL is present:** state the resolution paths without choosing one — change the spec's decision to match, record it as a documented deviation in the Rationale (with the reason), or, if the constitution or arch spec is the outdated side, update it with `pragmatic-project-constitution-update` or `pragmatic-arch-spec-update`. Which side moves is the user's decision
- **If a Domain Language WARN is present:** recommend `pragmatic-spec-update`, which replaces avoided terms in the spec and adds each undefined term to `docs/glossary/<context-slug>.md`; list the undefined terms so the update has them
- List FAILs first with concrete suggestions for each
- N/A checks are not counted in Passed/Warnings/Failed summary totals
- Overall Status is FAIL if any check is FAIL; WARN if any check is WARN and none are FAIL; PASS if all checks are PASS or N/A
- If all checks pass: summarize the spec's strengths instead of listing recommended actions
- If FAILs or actionable WARNs are present: end the report with an explicit recommendation to use `pragmatic-spec-update` to address them
- **After a FAIL report:** assert explicitly — "**Do not use this spec as an implementation reference** and do not share it with the team until FAIL items are resolved. Use `pragmatic-spec-update` to address them before starting implementation."
- **After a WARN report:** close with: "Spec can proceed to implementation. Consider resolving WARN items with `pragmatic-spec-update` before building. When ready, run `pragmatic-spec-build` against this spec."
- **If a Single feature focus WARN is present:** add: "Consider splitting this spec at `[boundary]` into separate specs — one per subsystem. A scoped spec produces a more precise `pragmatic-spec-check` report."
- **After a PASS report:** close with: "Spec is ready for implementation. Run `pragmatic-spec-build` against `docs/specs/<feature-slug>.md` to start."
