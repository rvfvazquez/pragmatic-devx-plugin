---
name: pragmatic-initiative-create
description: This skill should be used when the user asks to "break this big problem into features", "plan this initiative", "figure out what specs we need for X", "chart the path for this large effort", "decompose this into features and architecture", "this is too big for one spec, help me break it down", or wants a large, multi-feature problem decomposed into a tracked breakdown before any individual feature spec or arch spec is created.
---

# pragmatic-initiative-create

Plan the path to deliver a large, multi-feature problem — breaking it into features and, when needed, architecture work — without creating any feature spec or arch spec yet.

## Purpose

Produce `docs/initiatives/<initiative-slug>.md`: a single document naming the destination, the features it decomposes into (ordered by dependency), whether architecture work is needed first, and the breakdown decisions made along the way. This is the **charting** step only — it hands off to `pragmatic-initiative-deliver` to actually create and build each feature. This skill never writes a feature spec, an arch spec, or any code.

## When This Skill Applies

Use when the user describes a problem too large for a single feature spec — multiple independent-but-related capabilities, or a problem whose shape isn't yet known feature-by-feature.

**Do not use when:**
- The problem is already a single, cohesive feature → use `pragmatic-spec-create` directly. Producing a one-row initiative for something that's really one feature is unnecessary ceremony.
- An initiative already exists for this problem and the user wants to build it → use `pragmatic-initiative-deliver` instead.
- An initiative already exists and the user wants to change the breakdown → this skill can produce a fresh pass, but only with the same explicit replace-confirmation as Pre-condition 1 below; there is no dedicated `pragmatic-initiative-update` yet.

## How to Create an Initiative

### Pre-condition 0 — Check for Project Constitution

Before anything else, check whether `docs/constitution.md` exists. If it does, load it in full — every feature this initiative eventually produces will inherit its tech stack and Security Baseline decisions. If it doesn't, follow the same disclosure `pragmatic-spec-create` Pre-condition 0 uses: offer to create one first, or continue with a note that global constraints won't be available yet.

For the domain language, call the Skill tool with `pragmatic-domain-language` (once per session — without a Skill tool, read `../pragmatic-domain-language/SKILL.md`) and apply **§1 Locate the Context** for every context the destination plausibly touches. The breakdown names features and concepts with these terms.

### Pre-condition 1 — Check for Existing Initiative

Determine the `<initiative-slug>` from the user's message and check whether `docs/initiatives/<initiative-slug>.md` already exists.

If it exists:
> "An initiative already exists at `docs/initiatives/<initiative-slug>.md`. This skill will **replace** its breakdown. Did you mean to run `pragmatic-initiative-deliver` on the existing one instead?
>
> I will only continue if you explicitly confirm you want to replace the existing breakdown."

**STOP. Do not proceed until the user explicitly confirms they want to replace it.**

### Step 1 — Understand the Destination

Extract from the user's message: the problem or goal in their own words, why it matters, and any capability already mentioned that hints at the eventual feature breakdown. Keep this light — the depth of understanding each individual feature needs belongs to that feature's own `pragmatic-spec-create` interview later, not here.

### Step 2 — Confirm the Destination

Use `AskUserQuestion` to confirm your understanding of the destination and surface any obvious hard constraint (deadline, must-integrate-with-X, explicitly out of scope). One round — not the full depth of `pragmatic-spec-create` Step 2.

In the same round, run a light version of **§2 Interview Checks** on the destination: a word listed under a glossary term's `_Avoid_`, a word the user uses for more than one thing, or a destination that could belong to more than one existing context — each flagged with a recommended answer (`➡️`). Definitions and boundary scenarios are not drafted here; they belong to Step 4.5 and to each feature's spec.

**STOP. Do not proceed to Step 3 until the destination is confirmed.**

### Step 3 — Domain Research and Architecture Scoping

**Proactive research (once per initiative).** Unlike `pragmatic-spec-create`/`pragmatic-arch-spec-create`, this skill has no codebase to scan — the breakdown works only from what the user has described, and a large, multi-feature effort benefits from relevant domain facts *before* the breakdown is drawn, not just when a specific question happens to surface one. Dispatch `fact-finder` **once**, not per feature, asking: "What compliance requirements, established best practices, or common pitfalls are relevant to `<the destination>`?" Use whatever it returns, with its sources, to inform the scoping test and the breakdown in Step 4 — a returned fact becomes context for a feature's `Watch for` note, or a reason the scope test below triggers, not a feature by itself. Record any fact that materially shaped the breakdown as one line in `## Decisions So Far`, citing the source.

Skip this research only if the user's own description already demonstrates deep domain expertise (they stated exact regulatory requirements or standards themselves, precisely) — don't re-research what was already told to you with confidence.

**Scope test.** Apply the same over-broad-scope test `pragmatic-spec-create` Step 2.5 already uses: the description joins independent capabilities with "and"; the eventual acceptance criteria would span multiple distinct workflows with no shared entry point; the effort spans more than one trust boundary — now informed by whatever the research above surfaced, in addition to the user's own description. Where Step 2.5 treats that signal as a reason to split into separate specs and stop, here it means something different: **architecture work is needed before any feature spec is written.**

If triggered, name which `docs/arch/<name>.arch.md` this initiative depends on (existing, or new) and record it in the initiative's `## Architecture` section. Do not create the arch spec here — `pragmatic-initiative-deliver` dispatches `pragmatic-arch-spec-create` for it, in its own Step 1, before any feature.

If no such signal applies, record `## Architecture` as "None needed — <one-line reason>".

**Contexts.** Using the context map (if any) and the destination, list the contexts this initiative touches. Two signals add architecture work even when the scope test above did not trigger:
- **A new context** — the destination introduces a domain the map doesn't have (e.g. Loyalty). Name it and add its `module`-scope arch spec (`docs/arch/<context>.arch.md`) to `## Architecture`.
- **A new relationship** — the destination makes two contexts interact in a way the map's Relationships don't record. Name the relationship (from → to, likely mechanism) and add the arch spec that will define it — a `system`-scope arch spec, or an update to an existing one — to `## Architecture`.

Record both in the initiative's `## Domain Language` section. Do not edit the context map here — the arch spec that defines the context or relationship writes it.

**Facts vs. decisions (reactive fallback).** The proactive pass above won't catch everything — if a feature's cohesion in Step 4 turns on a fact the initial research didn't cover, dispatch `fact-finder` again for that specific gap before asking the user or guessing. Reserve `AskUserQuestion` for genuine decisions: choices with no single objectively correct answer, never for something `fact-finder` could have answered.

### Step 4 — Break Down Into Features

Decompose the destination into a list of features. Each one must pass the same cohesion test a single feature spec should pass on its own: removing it would still leave every other feature a complete, independently shippable capability.

Each feature is also a **vertical slice**: it cuts a narrow but complete path through every layer it needs (data, API, UI, tests) and is demonstrable or verifiable on its own. A feature that delivers one horizontal layer ("the database schema", "the admin screens") and only has value once another feature lands fails this test — reshape it around behavior a user or caller can observe, even if small.

Two sequencing patterns, applied only when they genuinely fit:
- **Prefactoring first.** When the user names, or the codebase (if any) shows, a restructuring that would make the features easy to build ("make the change easy, then make the easy change"), make it the first feature — behavior-preserving, with every feature it eases listing it under Depends on. Do not invent one to look thorough.
- **Wide refactors are the exception to slicing.** One mechanical change whose blast radius spans the codebase (rename a column, retype a shared symbol) breaks too many call sites at once for any slice to land green. Sequence it as **expand–contract**: an *expand* feature adds the new form beside the old; *migrate* features move call sites over in batches sized by blast radius (per package or directory), each depending on the expand; a *contract* feature removes the old form, depending on every migrate. Only the contract feature may fail the independently-shippable test.

For each feature, capture:
- A short name
- A short description (2-4 sentences) — what it does and why it's needed; enough context that `pragmatic-spec-create` doesn't have to re-derive intent from scratch later, but still not a full spec
- Its dependencies on other features in this same breakdown, if any
- Its **context** — the one context the feature lives in. A feature that spans two contexts is split at the boundary when that leaves two independently shippable features; when it can't be split, keep it whole, assign it to the context that owns its central concept, and add a **Watch for** naming the relationship it relies on (e.g. "reads Points, owned by Loyalty, by identifier only — relies on Ordering → Loyalty `OrderDelivered` event")
- Optionally, a **Watch for** note — anything already known at the breakdown level that this feature's own spec interview should take seriously (e.g. "touches PII, handle retention carefully" or "highest-risk feature in this set — consider Full interview mode even if others run Lean")

Name features and write descriptions with the glossary's canonical terms.

**Order the table topologically** — a feature never appears above a feature it depends on. Among features with no dependency between them, put the one that introduces a concept before the ones that consume it — the first spec to define a term is the one other features will read it from. If a dependency cycle is detected, stop and ask the user to resolve it before proceeding; do not silently pick an order.

**Fog and scope.** Anything the user mentioned (or the research surfaced) that did not become a feature goes in exactly one of two places:
- **Not Yet Specified** (in scope, not sharp) — the test is whether you can state the capability precisely *now*, not whether you can build it now. If you can state it, it is a feature, even if blocked. If it hangs on something a feature below will reveal, write one loose line (what it is and what it waits on); do not pre-slice fog into feature-sized pieces.
- **Out of Scope** (ruled outside the destination) — one line with the reason. Scope, not sharpness, puts it here; it never graduates.

### Step 4.5 — Shared Vocabulary

`pragmatic-initiative-deliver` creates each feature's spec in Lean mode, one at a time — and Lean mode does not ask about new terms beyond the acceptance criteria. Without a shared vocabulary set up front, two features of the same initiative coin different names for the same concept.

From the breakdown, pick the domain concepts **used by more than one feature** — at most 8. Skip any already defined in the glossary. For each, draft a glossary entry as **§2** describes (canonical term, one-sentence definition, `_Avoid_`, `_In code_`, context) — boundary scenarios stay with each feature's spec. Present the drafts, together with each feature's context assignment, in one `AskUserQuestion` round, ➡️ "as drafted". Concepts used by a single feature are left to that feature's own spec.

On confirmation, apply **§3 Write the Glossary** of `pragmatic-domain-language`: it creates `docs/glossary/`, the context map, and context files as needed. A **new context** from Step 3 gets its context-map row now (Arch spec column `—` until its arch spec exists) so its terms have a home. List the seeded terms in the initiative's `## Domain Language` section.

If the user declines, skip the write and record "not seeded" — the specs will create terms as they go.

### Step 5 — Autonomy Setting

Decide the autonomy setting using the same explicit-signal-first precedence `pragmatic-spec-create` Step 0.5 uses for interview depth:
1. **Detect an explicit signal** — either in the skill's own `args` (e.g. `autonomous-execution=yes`), or in the user's request itself ("build it all automatically, don't stop for approval" vs. "I want to approve every build"). If found, do not ask — but do not silently assume it either: state it back in one line ("Recording this initiative as autonomous execution, as requested") so it's visible before anything is written.
2. **Ask only if no explicit signal was given** — use `AskUserQuestion`:

```
Once a feature's spec reaches Review status and passes pragmatic-spec-validate, should
pragmatic-initiative-deliver build it automatically, or pause for your approval first?

1. Autonomous — build once a spec is Review + validated, without waiting for Approved
2. Supervised — pause before build on every feature, waiting for explicit approval
```

Record the result in the initiative's `## Notes` section as `autonomous execution: yes` or `autonomous execution: no`. This is decided once, here, looking at the whole breakdown — `pragmatic-initiative-deliver` never re-asks it per feature.

### Step 6 — Generate the Initiative Document

Create `docs/initiatives/<initiative-slug>.md` using the template in `references/template.md`. Every feature row starts at `Spec: not created yet`, `Status: Not started`, `Build: Not started`, with its **Context** column from Step 4. Fill `## Domain Language` from Steps 3 and 4.5, and `## Not Yet Specified` / `## Out of Scope` from Step 4. Below the table, write one subsection per feature with the description and any `Watch for` note captured in Step 4 — the table stays a scannable index; the subsections hold the context.

### Step 7 — Output Summary

After writing the file:
1. State the file path created
2. List the features in delivery order, with their dependencies
3. State whether architecture work is needed first, and which arch spec(s)
4. State the contexts touched, any new context or relationship, and the glossary terms seeded (with file paths)
5. State the autonomy setting recorded, and how many items sit in Not Yet Specified and Out of Scope
6. Tell the user the next step is `pragmatic-initiative-deliver` on this file

**Charting is one session's work.** This skill hands nothing off automatically — `pragmatic-initiative-deliver` only runs when the user explicitly invokes it afterward.

## Output Location

`docs/initiatives/<initiative-slug>.md` — create the `docs/initiatives/` directory if it does not exist.

`docs/glossary/context-map.md` and `docs/glossary/<context-slug>.md` — only when shared terms were seeded in Step 4.5.

## Additional Resources

- **`references/template.md`** — Full initiative document template.
