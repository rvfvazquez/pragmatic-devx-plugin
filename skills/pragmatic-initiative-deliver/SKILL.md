---
name: pragmatic-initiative-deliver
description: This skill should be used when the user asks to "deliver this initiative", "build out all the features in this initiative", "run the initiative", "execute the plan for X", "go build everything in the initiative", or wants an existing docs/initiatives/<slug>.md initiative walked end-to-end — creating, validating, and building each feature's spec in dependency order until every feature is checked.
---

# pragmatic-initiative-deliver

Walk an existing initiative's feature table end-to-end — creating, validating, and building each feature's spec in dependency order — until every feature is `Checked` or a real blocker is hit.

## Purpose

Drive `pragmatic-spec-create`, `pragmatic-spec-validate`, `pragmatic-spec-update`, `pragmatic-spec-build`, `pragmatic-spec-check`, and (when the initiative names one) `pragmatic-arch-spec-create` for every feature in an initiative — using `pragmatic-initiative-status` to decide readiness at each step, and updating the initiative document as the running record of progress. This skill never decides the breakdown itself; it only executes the one `pragmatic-initiative-create` already produced.

## When This Skill Applies

Use when an initiative document already exists and the user wants it executed.

**Do not use when:**
- No initiative exists yet → use `pragmatic-initiative-create` first.
- The user wants to change the breakdown itself (add, remove, or reorder features) → that's a `pragmatic-initiative-create` concern, not this skill.

## How to Deliver an Initiative

### Pre-condition — Load the Initiative

Read `docs/initiatives/<slug>.md` in full. If it doesn't exist, stop and point to `pragmatic-initiative-create`. Note the `autonomous execution` value from `## Notes` — it governs Step 2.4 below for every feature in this run; it is never re-asked per feature.

### Step 1 — Architecture First, If Named

If `## Architecture` names an arch spec that doesn't exist yet, dispatch `pragmatic-arch-spec-create` for it before touching any feature. Call `pragmatic-initiative-status` on it afterward; do not proceed to Step 2 until it reports `Ready: yes`.

### Step 2 — Walk the Feature Table, in Order

For each feature row not yet `Build: Checked`, in table order (already topologically sorted by `pragmatic-initiative-create` — never reorder it here):

1. **No spec yet** (`Spec: not created yet`) — dispatch `pragmatic-spec-create` **in Lean mode**, using the initiative's `## Destination` plus this feature's own subsection (description and any `Watch for` note) as the input — pass the `Watch for` note through explicitly so the spec's interview doesn't have to rediscover it. Update the row's `Spec` column to the created path and its `Status` column to the created spec's own `Status` field.
2. **Spec exists, not yet validated this pass** — dispatch `pragmatic-spec-validate`. If it returns FAIL, dispatch `pragmatic-spec-update` addressing the specific findings, then re-validate once. Do not proceed to build on a FAIL, and do not loop validate/update more than once per feature without surfacing it as a blocker (Step 3).
3. **Check readiness** — call `pragmatic-initiative-status` on this feature's spec path.
4. **Decide whether to build**, using the `autonomous execution` setting noted in the Pre-condition:
   - `autonomous execution: yes` — proceed to build once `pragmatic-initiative-status` reports `Ready: yes` (Status is `Review` or `Approved`, zero open TODOs). Do not wait for a human to flip `Status` to `Approved`.
   - `autonomous execution: no` — stop here for this feature, report that its spec is ready, and wait for explicit human approval before dispatching `pragmatic-spec-build`.
5. **Build** — dispatch `pragmatic-spec-build`, then `pragmatic-spec-check`. Update the row's `Build` column (`In progress` → `Done` → `Checked`, matching `pragmatic-spec-check`'s Overall Status of PASS).
6. **Update the initiative document** after every sub-step above — it is the running log of this delivery, not a summary written once at the end. Table columns record the *what* (current Status/Build state); when a feature reaches `Build: Checked`, also append one line to `## Decisions So Far` recording the *why* — e.g. "Feature X: validated PASS on first pass, built and checked" or "Feature X: validate FAIL (open TODO in section 8), one `pragmatic-spec-update` pass, then checked." Only append on a feature's terminal outcome for this run (`Checked`, or the blocker reported in Step 3) — not on every sub-step transition, or the section turns into noise.

### Step 3 — Handle Real Blockers

If a feature's `pragmatic-spec-validate` still fails after one `pragmatic-spec-update` pass, or `pragmatic-spec-check` returns FAIL after build, **stop walking the table** and report exactly which feature and which check blocked. Append one line to `## Decisions So Far` recording the blocker before stopping — e.g. "Feature X: blocked, pragmatic-spec-check FAIL on AC-2 after build, see docs/specs/x.md" — so resuming later starts from a record, not just memory of the conversation. Do not skip ahead to features further down the table without the user's say-so — the dependency order already encodes what's genuinely independent; anything downstream of a blocked row may depend on it even if its own `Depends on` column doesn't name it directly (a later feature can inherit an assumption from an earlier one without listing it as a formal dependency).

### Step 4 — Output Summary

1. State which features reached `Checked` this run
2. State which are still pending, and why — waiting on human approval vs. genuinely blocked
3. Point to the initiative document as the full record

## Guard

**Never bypass `pragmatic-spec-build`'s own HARD-GATE** (spec `Status` must be `Review` or `Approved`, no open TODOs) or any other existing gate in a dispatched skill. `autonomous execution: yes` only changes *who* is allowed to treat those conditions as met — this skill, instead of a human manually setting `Approved` — it never removes the conditions themselves. If a dispatched skill's own gate blocks progress for a reason this skill cannot resolve by re-running `pragmatic-spec-update` once, that is a real blocker (Step 3), not something to route around.
