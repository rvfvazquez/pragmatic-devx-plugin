---
name: pragmatic-howto
description: This skill should be used when the user asks "what pragmatic skills are available", "how do I use this plugin", "what can pragmatic do", "show me the skill map", "which skill should I use", "how do I document a feature", "how do I create a spec or architecture doc", "what is the pragmatic workflow", or when starting a session with the pragmatic-devx plugin installed and there is no clear skill to invoke yet — establishes the document hierarchy and maps each skill to its purpose and trigger.
---

# Pragmatic DevX — How-To Guide

Pragmatic DevX provides two parallel skill lifecycles for engineering documentation: **Feature Specs** and **Architecture Specs**, anchored by a single **Project Constitution** that governs both.

## Document Hierarchy

```
docs/constitution.md              ← Project Constitution (global rules, governs everything)
      │
      ├── docs/arch/              ← Architecture Specs (system / module / layer / integration)
      │     └── <name>.arch.md
      │
      └── docs/specs/             ← Feature Specs (feature / story / module)
            └── <feature-slug>.md
```

Every spec reads the constitution. Every arch spec reads the constitution. The constitution has no parent — it is the root of all decisions.

## Feature Spec Lifecycle

```
pragmatic-spec-create  →  pragmatic-spec-validate  →  pragmatic-spec-update
                                                              ↓
                                               pragmatic-spec-build  →  pragmatic-spec-check
```

| Skill | When to invoke |
|---|---|
| `pragmatic-spec-create` | No spec exists yet — formalize from scratch |
| `pragmatic-spec-validate` | Spec exists — quality review before building |
| `pragmatic-spec-update` | Spec needs changes, corrections, or new decisions |
| `pragmatic-spec-build` | Spec is validated/approved — implement it |
| `pragmatic-spec-check` | Implementation exists — verify it matches the spec |

## Architecture Spec Lifecycle

```
pragmatic-arch-spec-create  →  pragmatic-arch-spec-validate  →  pragmatic-arch-spec-update
                                                                         ↓
                                                          pragmatic-arch-spec-check (ongoing)
```

| Skill | When to invoke |
|---|---|
| `pragmatic-arch-spec-create` | No arch spec exists for this system/module yet |
| `pragmatic-arch-spec-validate` | Arch spec exists — quality/completeness review |
| `pragmatic-arch-spec-update` | Arch spec needs new ADRs, corrections, or boundary changes |
| `pragmatic-arch-spec-check` | Verify codebase matches documented architecture decisions |

## Reverse Engineering Entry Point

When code already exists with no spec or arch spec at all,
`pragmatic-reverse-engineer` is the entry point instead of starting a
lifecycle interview from scratch. It scans the code, tags findings by
confidence (confirmed vs. inferred), and hands off into
`pragmatic-spec-create` or `pragmatic-arch-spec-create` — those two skills
still produce and own the document; this is only a different way to arrive
at their first step.

| Skill | When to invoke |
|---|---|
| `pragmatic-reverse-engineer` | Code exists, no spec/arch spec exists yet, and the document should be produced by reading the code rather than describing what to build |

## Governance

```
pragmatic-project-constitution  →  pragmatic-project-constitution-update
```

| Skill | When to invoke |
|---|---|
| `pragmatic-project-constitution` | No `docs/constitution.md` exists — create global project rules |
| `pragmatic-project-constitution-update` | Constitution exists — add rules, update decisions, deprecate constraints |

The constitution is not a spec — it has no acceptance criteria and is not validated against the codebase.

## Rule: Check Constitution Before Any Spec Work

Before creating or updating any spec or arch spec, check whether `docs/constitution.md` exists.

- **If it exists:** load it in full before proceeding — it defines the tech stack decisions, cross-module constraints, and AI behavior guardrails that apply to every document in this project.
- **If it does not exist:** offer to create it with `pragmatic-project-constitution` before continuing, or proceed with a disclaimer that global constraints will not be enforced.

## Quick-Decision Table

| User says… | Invoke |
|---|---|
| "create a spec for X" | `pragmatic-spec-create` |
| "is this spec ready?" / "validate the spec" | `pragmatic-spec-validate` |
| "update the spec" / "add a requirement" | `pragmatic-spec-update` |
| "implement from spec" / "build from spec" | `pragmatic-spec-build` |
| "does the code match the spec?" | `pragmatic-spec-check` |
| "document the architecture" / "create arch spec" | `pragmatic-arch-spec-create` |
| "is the arch spec complete?" | `pragmatic-arch-spec-validate` |
| "update the arch spec" / "add an ADR" | `pragmatic-arch-spec-update` |
| "does the code follow the architecture?" | `pragmatic-arch-spec-check` |
| "create a project constitution" / "set global rules" | `pragmatic-project-constitution` |
| "update the constitution" / "add a global rule" | `pragmatic-project-constitution-update` |
| "reverse engineer a spec from this code" / "generate a spec from existing code" / "document what this legacy code does" | `pragmatic-reverse-engineer` |

## Skill Invocation Rule

Invoke the relevant skill BEFORE responding or writing any document. Even when the user's need seems small — "just update one field in the spec" — the skill enforces changelog tracking, status transitions, and spec integrity.

**Never read skill files directly with the Read tool.** Use the Skill tool to invoke them. Skill content evolves; the Skill tool always loads the current version.

## Additional Resources

- **`references/skill-map.md`** — Full per-skill reference: purpose, output files, pre-conditions, and guards for every skill in this plugin.
