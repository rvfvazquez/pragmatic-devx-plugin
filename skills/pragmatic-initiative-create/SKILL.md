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

**STOP. Do not proceed to Step 3 until the destination is confirmed.**

### Step 3 — Scope the Architecture

Apply the same over-broad-scope test `pragmatic-spec-create` Step 2.5 already uses: the description joins independent capabilities with "and"; the eventual acceptance criteria would span multiple distinct workflows with no shared entry point; the effort spans more than one trust boundary. Where Step 2.5 treats that signal as a reason to split into separate specs and stop, here it means something different: **architecture work is needed before any feature spec is written.**

If triggered, name which `docs/arch/<name>.arch.md` this initiative depends on (existing, or new) and record it in the initiative's `## Architecture` section. Do not create the arch spec here — `pragmatic-initiative-deliver` dispatches `pragmatic-arch-spec-create` for it, in its own Step 1, before any feature.

If no such signal applies, record `## Architecture` as "None needed — <one-line reason>".

**Facts vs. decisions:** unlike `pragmatic-spec-create`/`pragmatic-arch-spec-create`, this skill does not scan a codebase — the breakdown works from what the user has already described. If the architecture-scoping decision above, or a feature's cohesion in Step 4, turns on a fact that needs knowledge outside what's already been said — a compliance requirement, a third-party API's behavior, a current best practice — dispatch the `fact-finder` subagent to resolve it before asking the user or guessing. Reserve `AskUserQuestion` for genuine decisions: choices with no single objectively correct answer.

### Step 4 — Break Down Into Features

Decompose the destination into a list of features. Each one must pass the same cohesion test a single feature spec should pass on its own: removing it would still leave every other feature a complete, independently shippable capability.

For each feature, capture:
- A short name
- A short description (2-4 sentences) — what it does and why it's needed; enough context that `pragmatic-spec-create` doesn't have to re-derive intent from scratch later, but still not a full spec
- Its dependencies on other features in this same breakdown, if any
- Optionally, a **Watch for** note — anything already known at the breakdown level that this feature's own spec interview should take seriously (e.g. "touches PII, handle retention carefully" or "highest-risk feature in this set — consider Full interview mode even if others run Lean")

**Order the table topologically** — a feature never appears above a feature it depends on. If a dependency cycle is detected, stop and ask the user to resolve it before proceeding; do not silently pick an order.

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

Create `docs/initiatives/<initiative-slug>.md` using the template in `references/template.md`. Every feature row starts at `Spec: not created yet`, `Status: Not started`, `Build: Not started`. Below the table, write one subsection per feature with the description and any `Watch for` note captured in Step 4 — the table stays a scannable index; the subsections hold the context.

### Step 7 — Output Summary

After writing the file:
1. State the file path created
2. List the features in delivery order, with their dependencies
3. State whether architecture work is needed first, and which arch spec
4. State the autonomy setting recorded
5. Tell the user the next step is `pragmatic-initiative-deliver` on this file

**Charting is one session's work.** This skill hands nothing off automatically — `pragmatic-initiative-deliver` only runs when the user explicitly invokes it afterward.

## Output Location

`docs/initiatives/<initiative-slug>.md` — create the `docs/initiatives/` directory if it does not exist.

## Additional Resources

- **`references/template.md`** — Full initiative document template.
