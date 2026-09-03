---
name: pragmatic-project-constitution
description: This skill should be used when the user asks to "create a project constitution", "define global project rules", "set up project governance", "create a constitution", "define what the AI can decide alone", "define cross-module rules", "document global architecture decisions", "establish project-wide constraints", or wants a single source of truth for decisions that apply across all modules, features, and architecture specs — above any individual arch spec or feature spec.
---

# pragmatic-project-constitution

Create a project-wide governance document that defines what every agent, developer, and spec in this project must respect — regardless of module or feature.

## Purpose

Establish the rules that live above any individual arch spec or feature spec: project identity, non-negotiable tech stack decisions, the project security baseline, cross-module constraints, and AI behavior guardrails. This document is loaded first — before any module arch spec or feature spec is read.

## Lifecycle Position

```
[pragmatic-project-constitution] → pragmatic-project-constitution-update
         ↓ read by
pragmatic-spec-create · pragmatic-arch-spec-create · pragmatic-spec-build · pragmatic-spec-check
```

A constitution is created once and updated as global decisions evolve. It is not a spec — it has no acceptance criteria and is not validated against the codebase.

## When This Skill Applies

Use when:
- No `docs/constitution.md` exists yet and the project needs global governance
- The user wants to capture cross-module rules that no single arch spec owns
- The user wants to define what the AI must always ask before deciding autonomously

**Do not use when:**
- A constitution already exists and the user wants to modify it → use `pragmatic-project-constitution-update` ✓ *this skill exists*
- The rule belongs to a specific module → use `pragmatic-arch-spec-create` or `pragmatic-arch-spec-update`

---

## How to Create a Constitution

### Pre-condition — Check for Existing Constitution

Check whether `docs/constitution.md` already exists.

If it **exists**:
> "A project constitution already exists at `docs/constitution.md`. This skill will **replace** it. Use `pragmatic-project-constitution-update` (available) to make targeted changes instead.
>
> I will only continue if you explicitly confirm you want to replace the existing constitution."

**STOP. Do not proceed until the user explicitly confirms.** If they want targeted changes, end this skill now.

---

### Step 0 — Language Detection

Infer the document language before asking:
1. If the user's message is ≥80% in a single language (pt-BR, es-ES, en-US), use it without asking
2. If ambiguous, check existing docs in `docs/` for language uniformity
3. If still ambiguous, use `AskUserQuestion`:

```
In which language would you like the constitution to be generated?

1. pt-BR — Portuguese (Brazil)
2. es-ES — Spanish (Spain)
3. en-US — English (United States)
4. Other — specify which language
```

Use the chosen language for all content in both output files.

---

### Step 1 — Scan Existing Context

Before the discovery interview, read:
- All files in `docs/arch/` — extract global patterns already decided (tech stack, communication style, naming conventions that repeat across multiple specs)
- `.claude/rules/` — extract rules already in force
- `CLAUDE.md` at project root — understand any existing project-level instructions
- `docs/specs/` — scan a sample to infer the project domain and tech stack

From this scan, build a preliminary picture of what the project already is. Bring decisions already documented into the discovery interview as defaults — do not ask the user to re-decide what is already evident. Only ask about what is genuinely unknown or not documented anywhere.

---

### Step 2 — Discovery Interview

Use `AskUserQuestion` to fill the five areas of the constitution. Only ask what is NOT already clear from the Step 1 scan. Adapt the questions to the project context.

**Every question with a concrete option list must carry a recommended answer (`➡️`).** Derive it in this priority order:
1. What the Step 1 scan already found in `docs/arch/`, `.claude/rules/`, `CLAUDE.md`, or `docs/specs/`
2. A pragmatic default for the stated product type, stated as such (e.g. "no signal found — recommending X because Y")

Never present a bare menu with no recommendation — the user should be able to just confirm the `➡️` line.

**Area 1 — Project Identity**

Ask about the project's nature and non-negotiable context:
- What kind of product is it? (SaaS, internal tool, API platform, mobile backend, CLI, library...)
- Who are the end users or customers?
- Are there compliance requirements that are non-negotiable? (LGPD, GDPR, SOC2, PCI-DSS, HIPAA...)
  ➡️ None found in Step 1 scan — recommend confirming explicitly rather than leaving it implicit
- Is this multi-tenant? If yes, what is the tenancy model and isolation boundary?
  ➡️ State the Step 1 scan finding if one exists; otherwise "no signal found — recommend confirming explicitly, this affects Areas 3 and 4"

**Area 2 — Global Tech Stack** (`multiSelect: true`)

Ask which technology decisions apply to ALL modules — not just one:
- Programming language(s) — is there more than one allowed?
  ➡️ State the language(s) found across `docs/arch/` and `docs/specs/` in Step 1
- Database engine(s) — which are permitted? Are any explicitly forbidden?
  ➡️ State the engine found in Step 1 scan, or "no engine committed yet — recommend picking one now to avoid drift across modules"
- Infrastructure constraints (cloud provider, runtime, deployment model)?
- Project-wide library standards (ORM, HTTP client, job queue, auth library)?

**Area 3 — Security Baseline** (`multiSelect: true`)

Ask which security decisions apply to ALL modules — not per feature. These become the assumptions every feature spec and arch spec inherits:
- Authentication model — how does a caller prove identity? (OIDC / OAuth2, session cookie, JWT, mTLS, API key)
  ➡️ State the mechanism found in `docs/arch/` or `docs/specs/` during Step 1; otherwise "no mechanism committed yet — recommend deciding now, every module needs it"
- Authorization model — how is access to a specific resource decided? (RBAC, ABAC, per-resource ownership check, ACL)
  ➡️ State the Step 1 finding, or "no signal — recommend per-resource ownership as the pragmatic default for any multi-user product"
- Secrets management — where do credentials, API keys, and tokens live, and where are they forbidden?
  ➡️ Yes to "secrets never in code or the repository — read them from a secrets manager or injected environment" — pragmatic default for any shared repo
- Data classification — are there data categories (PII, financial, health) with rules on how every module stores, logs, and transmits them?
  ➡️ State "yes" if Area 1 flagged LGPD / GDPR / HIPAA; otherwise recommend confirming explicitly rather than leaving it implicit
- Security baseline reference — is there a standard the project holds itself to? (OWASP Top 10, OWASP ASVS L1/L2, CWE Top 25)
  ➡️ No signal found — recommend OWASP Top 10 as a minimum shared reference

**Area 4 — Cross-Module Rules** (`multiSelect: true`)

Ask about rules that govern how modules interact with each other:
- Is there a module that must be the single source of truth for a domain? (e.g., AuthModule owns all user identity — no module may maintain its own user store)
  ➡️ Name the module already documented in `docs/arch/` as owning that domain, if found
- Are there modules that must never communicate directly? (must use events, queue, or gateway)
- Is there a module that all outbound calls (HTTP, email, SMS) must route through?
- Are there shared resources (DB, cache, queue) with rules on how all modules access them?

**Area 5 — AI Behavior Guardrails** (`multiSelect: true`)

Ask what the AI must ALWAYS stop and ask before deciding on its own:
- Introducing a new third-party dependency?
  ➡️ Yes — pragmatic default for any project with more than one contributor
- Adding a new external service integration?
  ➡️ Yes — same rationale
- Creating a new database table or changing an existing schema?
- Changing a public API contract (rename field, remove endpoint, change response shape)?
- Choosing a technology not already in the project stack?
  ➡️ Yes — keeps Area 2 decisions from drifting silently
- Weakening an Area 3 security decision — adding a new inbound entry point, changing an authorization check, or storing a classified data category in a new place?
  ➡️ Yes — an agent must never relax the security baseline on its own

Answer what you know, or just confirm the ➡️ recommendation. Areas 4 and 5 may be left as "none defined yet" if the user has no cross-module rules or guardrails to declare — but this must be an explicit answer, not a skipped step. Area 3 should not be "none" for any product with a network surface or more than one user; if the user genuinely has no security decision to record, capture that as an explicit statement, not a skipped step.

**STOP. Do not generate any files until Areas 1, 2, and 3 have enough content to produce a meaningful constitution.**

### Step 2.5 — Follow-up Round for Dependent Decisions

After the user answers Step 2, check whether any answer unlocks a **dependent decision** that could not have been asked before it (its options only make sense given the parent answer). Common triggers:

| Parent answer | Dependent question to ask now |
|---|---|
| Multi-tenant: yes | Tenancy isolation model — schema-per-tenant, row-level security, separate DB per tenant? |
| Compliance: LGPD/GDPR/HIPAA selected | Data residency requirement? Consent/retention policy owner? |
| Database engine chosen | Migration tool standard? Connection pooling policy? |
| "Module X is single source of truth for domain Y" | What must other modules do instead — event, API call, shared read replica? |
| Authentication model chosen (JWT / OIDC / session) | Token or session lifetime? Refresh / rotation policy? Where is it validated — gateway, each service, or both? |
| Authorization model = RBAC / ABAC | Where are roles or attributes defined, and who is allowed to change them? |
| Data classification includes PII / financial / health | Retention policy owner? Is that category ever allowed in application logs, or never? |

If any dependent question applies, ask it now via `AskUserQuestion` — **with a recommended answer, following the same rule as Step 2** — instead of leaving it implicit. Only questions whose parent decision itself remained undecided should still become "none defined yet."

Run this check once. Proceed to Step 3 afterward regardless of whether a second round would still find more dependents — do not turn this into an unbounded loop.

### Step 2.6 — Final Consistency Check

Before generating the document, assemble every decision confirmed across Steps 2 and 2.5 into one list, grouped by area. Scan pairwise for **contradiction** — the constitution has no separate validate skill, so this is the only check that runs before the document (and the rules files derived from it) become active project-wide.

Known contradiction shapes to check for:

| Area A | Area B | Contradiction pattern |
|---|---|---|
| Project Identity (tenancy model) | Cross-Module Rules (shared resources) | A stated isolation model conflicts with a rule allowing shared access to a resource |
| Project Identity (compliance) | AI Behavior Guardrails | A compliance requirement (e.g. LGPD) with no corresponding guardrail, or a guardrail that contradicts it |
| Global Tech Stack | Cross-Module Rules | A rule assumes a technology not listed as permitted in Area 2 |
| Security Baseline (authorization model) | Cross-Module Rules | One module is declared the single source of truth for identity, but another module is allowed to run its own permission check on that identity |
| Security Baseline (data classification) | Global Tech Stack / Cross-Module Rules | A data category is barred from logs, but a stack decision or rule routes that data through a shared log, queue, or cache with no exception noted |
| Security Baseline (secrets management) | AI Behavior Guardrails | Secrets are barred from the repository, but no guardrail stops the agent from adding one |
| Security Baseline (authentication model) | Project Identity (compliance) | A compliance requirement implies an authentication strength (e.g. MFA) the stated model does not provide |

If no contradiction is found, skip straight to the recap below.

**If a contradiction is found, do not silently resolve it.** Present it explicitly and wait:

> ⚠️ Possible contradiction: [Decision A, Area X] says "...", but [Decision B, Area Y] says "...". These look inconsistent because [reason]. Which should hold — or is there context I'm missing?

Once no contradictions remain, present the full recap and require explicit confirmation:

> Here's the complete picture before I write the constitution:
> **Area 1 (Project Identity):** ... **Area 2 (Global Tech Stack):** ... **Area 3 (Security Baseline):** ... **Area 4 (Cross-Module Rules):** ... **Area 5 (AI Behavior Guardrails):** ...
> Confirm this is complete, or tell me what's missing or wrong.

**STOP. Do not proceed to Step 3 until the user explicitly confirms.**

---

### Step 3 — Generate `docs/constitution.md`

If the `docs/` directory does not exist, create it. Create `docs/constitution.md` with this structure:

```markdown
# Project Constitution
**Project:** <name>
**Status:** Active
**Language:** <language>
**Last Updated:** <date>

---

## 1. Project Identity

<description of what the project is, who it serves, compliance requirements, tenancy model>

---

## 2. Global Tech Stack

Non-negotiable technology decisions that apply to every module. No spec or implementation may deviate from these without updating this constitution first.

| Decision | Value | Rationale |
|---|---|---|
| Language | <value> | <why> |
| Database | <value> | <why> |
| <...> | <...> | <...> |

---

## 3. Security Baseline

Non-negotiable security decisions that apply to every module. No feature spec, arch spec, or implementation may weaken these without updating this constitution first. Every spec inherits these as its starting assumptions.

| Decision | Value | Rationale |
|---|---|---|
| Authentication | <value> | <why> |
| Authorization | <value> | <why> |
| Secrets management | <value> | <why> |
| Data classification | <value> | <why> |
| Security baseline reference | <value> | <why> |

---

## 4. Cross-Module Rules

Rules that govern interactions between modules. These rules do not belong to any single module's arch spec — they apply to all modules simultaneously.

- **<Rule name>:** <description and rationale>

---

## 5. AI Behavior Guardrails

Decisions the AI agent must NOT make autonomously. For each item, the agent must stop, present the situation clearly, and wait for explicit human approval before proceeding.

- **<Guardrail name>:** <what triggers it and what the agent must do instead>

---

## Changelog

| Date | Change | Reason |
|---|---|---|
| <date> | Initial constitution created | — |
```

Fill every section with concrete content. Use `— none defined yet —` only for areas where the user explicitly stated there are no constraints. Do not leave sections blank or with placeholder text.

---

### Step 4 — Generate `.claude/rules/00-project-constitution.md`

Extract only **concrete, actionable rules** from sections 2, 3, 4, and 5 of the constitution. Do not copy prose — translate decisions into directive statements the agent can act on during any session.

Group the extracted rules into sections:

- **Project Context** — a 1–2 sentence directive summarizing what the project is and its compliance context, plus the fixed bullet: "These rules take precedence over all module-specific arch rules."
- **Global Stack Constraints** — e.g.: "Only PostgreSQL is permitted as a database engine. Never suggest SQLite, MongoDB, or any other engine."
- **Security Baseline Constraints** — e.g.: "Authentication is the platform OIDC provider; no module implements its own credential check. Every endpoint returning a user-owned resource must verify ownership against the caller identity before responding. Secrets are never committed to the repository — read them from the injected environment. Never place PII in application logs."
- **Cross-Module Constraints** — e.g.: "AuthModule is the single source of truth for user identity. No module may maintain its own user store or replicate identity data."
- **AI Guardrails — Stop and Ask Before Deciding** — e.g.: "Never add a third-party dependency without listing: package name, purpose, license, and why an existing dependency does not cover it. Present this and wait for confirmation — do not modify package.json before approval."

Only include sections that have at least one rule. Omit empty sections entirely.

Render these sections into the canonical rules file and every cross-tool destination as described in `references/cross-tool-rules-sync.md`, using `slug=project-constitution`, `title=Project Constitution Rules`, `source_path=docs/constitution.md`, `always_apply=true`, `claude_rules_filename=00-project-constitution.md` — the `00-` prefix ensures this file is loaded before any module-specific rules files in every Claude Code session. Do not write `.claude/rules/00-project-constitution.md` directly — the shared procedure creates it as a symlink to the canonical `.agents/rules/project-constitution.md` file.

---

### Step 5 — Output Summary

After writing both files:

1. State every file path created or updated — `docs/constitution.md`, `.claude/rules/00-project-constitution.md`, and every cross-tool destination actually written (`AGENTS.md`, `.cursor/rules/project-constitution.mdc`, `.windsurf/rules/project-constitution.md`, `.github/copilot-instructions.md`, and `GEMINI.md` if it exists)
2. List each rule extracted into `.claude/rules/00-project-constitution.md` by category
3. List any areas explicitly marked as "none defined yet" — and what would typically trigger filling them
4. State:

> **These rules are now active.** Claude Code loads `.claude/rules/00-project-constitution.md` automatically at the start of every session. All future `pragmatic-spec-create`, `pragmatic-arch-spec-create`, and `pragmatic-spec-build` runs will use these as context.
>
> **Next step:** run `pragmatic-spec-create` for your first feature spec or `pragmatic-arch-spec-create` for the first module — the constitution will be read automatically.

---

## Output Locations

```
docs/constitution.md                              ← human-readable governance document
.claude/rules/00-project-constitution.md          ← auto-loaded by Claude Code every session
AGENTS.md                                         ← Codex CLI, Antigravity, and most other agentic tools
.cursor/rules/project-constitution.mdc            ← Cursor
.windsurf/rules/project-constitution.md           ← Windsurf
.github/copilot-instructions.md                   ← GitHub Copilot
GEMINI.md                                         ← Gemini CLI / Antigravity, only if the file already exists
```

## Constraint Priority

The constitution sits at the top of the constraint hierarchy:

```
docs/constitution.md                      ← project constitution (this skill)
  ↓ takes precedence over
docs/arch/*.arch.md                       ← module arch specs
  ↓ takes precedence over
.claude/rules/<spec-name>-arch.md         ← generated module rules
  ↓ takes precedence over
Codebase conventions (inferred)
```

If a feature spec, arch spec, or implementation decision conflicts with the constitution, **stop and flag the conflict explicitly** — do not silently pick one side.
