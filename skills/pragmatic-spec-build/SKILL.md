---
name: pragmatic-spec-build
description: This skill should be used when the user asks to "implement the spec", "build this feature from the spec", "start implementing docs/specs/X.md", "build based on the spec", "implement the acceptance criteria", "code this feature", "build it following the spec", or wants to translate an approved specification document into a working implementation — guided by spec decisions, architecture constraints, and project rules.
---

# pragmatic-spec-build

Translate an approved technical specification into a working implementation — guided by the spec, architecture documents, and project rules already established in the codebase.

## Purpose

Orchestrate the implementation of a feature so that all decisions, constraints, and acceptance criteria defined in the spec are honored from the first line of code — not discovered retroactively. Synthesize `docs/specs/`, `docs/arch/`, and `.claude/rules/` into a build context before writing any code, then implement each acceptance criterion as a tracked task.

The definition of done is explicit: the implementation is complete when `pragmatic-spec-check` returns PASS.

## Lifecycle Position

```
pragmatic-spec-create → pragmatic-spec-validate → [pragmatic-spec-build] → pragmatic-spec-check
```

Use this skill after a spec has been validated and approved. Do not use it as a shortcut to skip `pragmatic-spec-create` or `pragmatic-spec-validate`.

## When This Skill Applies

Use this skill when a spec **exists and is not in Draft status** and the user wants to implement the feature it describes.

**Do not use when:**
- No spec exists yet → use `pragmatic-spec-create`
- The spec is in Draft status or has open TODOs → resolve with `pragmatic-spec-validate` + `pragmatic-spec-update` first
- The user only wants to verify existing code → use `pragmatic-spec-check`
- The user wants to update the spec document → use `pragmatic-spec-update`

---

<HARD-GATE>
Do NOT write any implementation code, create any files, or scaffold any structure until the spec Status is confirmed as Review or Approved AND has no open [TODO: ...] items in technology decisions or acceptance criteria.

This applies even if:
- The user says they know the spec is ready
- The spec is "almost done" or "good enough to start"
- This is a prototype or proof of concept

If the spec is in Draft status or has unresolved TODOs: STOP. Run `pragmatic-spec-validate` and `pragmatic-spec-update` first. Then return to this skill.
</HARD-GATE>

---

## How to Build from a Spec

### Pre-condition — Verify Spec Readiness

Before reading anything else, locate the spec and check its `Status` field.

- If `Status: Draft` → **STOP**. Assert: "This spec is in **Draft** status. Running `pragmatic-spec-build` on an incomplete spec will produce an implementation that does not match the final decisions. Run `pragmatic-spec-validate` and resolve FAIL items first, then use `pragmatic-spec-update` to set the status to Review or Approved."
- If the spec has open `[TODO: ...]` items in technology decisions or acceptance criteria → **STOP**. Assert: "This spec has **N unresolved TODO item(s)** in critical sections. Implement from an incomplete spec and the result will not conform to `pragmatic-spec-check`. Resolve them with `pragmatic-spec-update` first."
- If `Status: Review` or `Status: Approved` → proceed.

---

### Step 0 — Language Detection

Infer the working language from the spec:
1. If the spec contains a `Language:` metadata field, use it
2. Otherwise, infer from the majority language of prose content in sections 2, 3, and 4 — if ≥80% of prose words are in one language, use that language
3. If ambiguous, use `AskUserQuestion` to ask

Use the inferred language for all output in this skill: task descriptions, comments in generated stubs, and summary messages.

---

### Step 0.5 — Confirm Implementation Preferences

Before reading any files, confirm two execution preferences with a single `AskUserQuestion` call.

**Test strategy:**
- Interleaved: write one failing test then implement it, per acceptance criterion
- After each AC: implement the criterion then write its test
- Stubs first: write all test stubs upfront, then implement all behavior

**Scaffold preference:**
- Interface/type stubs first, then implement behavior
- End-to-end per AC: type + logic + test together for each criterion

These preferences affect execution order in Step 7 only — all acceptance criteria and tests are required regardless of choice.

If **Interleaved** is chosen and the harness supports dispatching subagents (the `Agent` tool is available), Step 7 dispatches the `tdd-implementer` agent per acceptance criterion instead of writing tests and code inline — see 7c/7d below. If the harness has no subagent dispatch, fall back to the manual flow in 7c/7d and apply red-green-refactor discipline yourself: write the test, run it, confirm it fails for the right reason, then implement.

---

### Step 1 — Read the Spec in Full

Read the entire spec document. Extract and record:

- **Feature name and slug** — used to locate related arch docs and implementation paths
- **Technology decisions** (section 5) — the definitive tech stack for this feature; do not re-ask or override
- **Interfaces, types, and endpoint definitions** (sections 6.1 and 6.2) — the contracts to implement
- **Behavior and logic** (section 6.3) — including any Mermaid diagrams; these define the execution model
- **Acceptance criteria** (section 7) — each criterion is a discrete implementation task and its own test case
- **Dependencies** (section 8) — external integrations and services that must be wired up
- **Open questions** (section 9) — any items not yet decided; note them but do not block on them unless they affect the acceptance criteria directly

---

### Step 2 — Scan Architecture Documents

Search `docs/arch/` for architecture specs that cover the same domain, module, or layer as this feature.

For each relevant arch spec found:
1. Read it fully
2. Extract all binding rules:
   - **Dependency direction** — which layers may import which
   - **Component boundaries** — where this feature's code must live
   - **Naming conventions** — file, type, and function naming patterns
   - **Forbidden dependencies** — what must not be imported directly
   - **Communication style** — sync vs async, direct call vs event, which mechanism to use
   - **Error propagation** — how errors must cross component boundaries
3. Note any **explicit deviations** the spec itself documents — if the spec's technology decisions intentionally diverge from the arch spec, capture that deviation; do not silently ignore it

If no arch docs are found, note this and continue — implementation will rely solely on spec decisions and project rules.

---

### Step 3 — Read Project Rules

Check `.claude/rules/` for any rule files that apply to this feature's domain or module (e.g., `*-arch.md` files generated by `pragmatic-arch-spec-validate`).

Read each matching rule file and extract:
- Forbidden import rules
- Naming convention rules
- Component boundary rules

Merge these with the arch spec rules gathered in Step 2. If a rule file contradicts an arch spec, flag the conflict explicitly and ask the user to resolve it before proceeding.

---

### Step 4 — Build Constraint Brief

Before writing any code, consolidate everything gathered into a constraint brief. This is not written to disk — it is the agent's internal working context for all subsequent steps.

The brief must answer:
1. **Where does this code live?** — directory path derived from component boundaries and codebase layout
2. **What may this code import?** — allowed dependency directions; what is explicitly forbidden
3. **What naming patterns must be followed?** — types, functions, files
4. **What is the communication model?** — sync/async, events, direct calls
5. **What external dependencies must be wired?** — from spec section 8
6. **What are the acceptance criteria, in order?** — implementation priority

If any of these questions cannot be answered from spec + arch + rules, use `AskUserQuestion` to ask — but only for genuinely missing information, not for decisions already captured.

---

### Step 6 — Decompose into Tracked Tasks

Use `TodoWrite` to create one task per acceptance criterion from section 7 of the spec. Each task description must:
- State the criterion clearly (rephrase in imperative form: "Implement: Given X, When Y, Then Z")
- Reference the criterion index (e.g., "AC-1", "AC-2") so tasks can be traced back to the spec

Also create tasks for:
- Setting up any external dependency integrations listed in spec section 8 that are not already present in the codebase
- Scaffolding the component structure (directory, entry files) if it does not already exist

Mark all tasks as pending. Mark each task complete immediately after its implementation and tests pass, not at the end of the whole feature.

---

### Step 7 — Implement Each Task

For each task (in the order established by Step 0.5 preferences):

#### 7a — Scaffold the component structure (if needed)

If the target directory or entry file does not exist, create it following:
- Component boundary rules from the constraint brief
- Naming conventions from arch spec and rules
- The project's existing directory layout (inferred from scanning the codebase)

Do not create new abstraction layers or directories not called for by the spec or arch constraints.

#### 7b — Implement interfaces and types (sections 6.1 and 6.2)

Translate each type definition and interface from the spec into the project's actual programming language (inferred from the codebase, confirmed in spec technology decisions). Generate:
- Type definitions / structs / interfaces as named in the spec
- Function signatures with parameter and return types as specified
- Leave function bodies empty or with a single `TODO: implement` comment

Follow naming conventions from the constraint brief exactly.

#### 7c/7d — Test and implement the behavior

**If the Step 0.5 test strategy is Interleaved and the `Agent` tool is available:** dispatch the `tdd-implementer` subagent for this task instead of doing 7c/7d manually. Pass it, self-contained (it has no access to this conversation):
- The acceptance criterion's full Given/When/Then text and its index (e.g. `AC-3`)
- The constraint brief items relevant to this criterion: target file/directory, allowed and forbidden imports, naming conventions, communication model, and the technology decisions from spec section 5
- The test framework and file-naming convention detected from the codebase scan

The subagent writes a real (non-stub) failing test, runs it, confirms it fails for the right reason, implements the minimal code to pass, and reruns to confirm green. Its report includes the file paths touched and verbatim red/green run output — treat that output as the evidence the criterion is implemented. Do not mark the task complete without it.

**Otherwise** (a different test strategy was chosen, or no subagent dispatch is available in this harness), do 7c and 7d directly:

**7c — Generate test stubs from acceptance criteria**

For each acceptance criterion in Given/When/Then format, generate a test function stub using:
- The project's existing test framework and file naming conventions (detected from codebase scan)
- A descriptive test name derived from the criterion (e.g., `test_ShouldReturnUnauthorized_WhenTokenIsExpired`)
- The full criterion text as structured comments inside the stub:

```
// Given: [context from criterion]
// When:  [action from criterion]
// Then:  [expected result from criterion]
```

Leave the test body empty after the comments — the developer completes the assertion. Do not implement test logic that cannot be derived directly from the criterion text.

**7d — Implement the behavior**

Implement the logic described in spec section 6.3, following:
- The communication model (sync/async, events) from the constraint brief
- The dependency direction rules — never import across forbidden boundaries
- The error propagation model from the arch spec
- The technology decisions from spec section 5 (do not substitute or improvise)

If a behavior requires an integration with an external dependency listed in spec section 8, wire the dependency according to the arch spec's communication style. Do not create ad-hoc integrations that bypass documented boundaries.

#### 7e — Mark the task complete

Mark the corresponding `TodoWrite` task complete immediately after implementing its criterion's behavior and test stub. Do not batch task completion.

---

<HARD-GATE>
Do NOT declare the implementation complete, say "done", or express satisfaction until you have run `pragmatic-spec-check` against this spec and its output shows PASS for all acceptance criteria.

Run the check. Show the output. Only then claim completion.

| Rationalization | Reality |
|---|---|
| "I believe all criteria are implemented" | Belief ≠ evidence. Run the check. |
| "All TodoWrite tasks are marked complete" | Task completion ≠ spec conformance. |
| "The code compiles and tests pass locally" | Local tests ≠ spec criteria coverage. |
| "The user said they're satisfied" | The spec is the contract, not the conversation. |
| "spec-check is overkill for this" | No exceptions — one FAIL missed is a bug shipped. |
| "This is a prototype / proof of concept" | The spec defines done. Run the check. |

If `pragmatic-spec-check` returns FAIL or PARTIAL: address the gaps, re-run, confirm PASS. Then close.
</HARD-GATE>

---

### Step 8 — Output Summary

After all tasks are marked complete:

1. List all files created or modified
2. State which acceptance criteria are implemented (by index: AC-1, AC-2, ...)
3. List any constraint deviations encountered and how they were resolved
4. List any open items that require human follow-up (unresolved architecture conflicts, missing external dependencies, gaps not covered by the spec)

Close with an explicit next step:

> **Next step:** Run `pragmatic-spec-check` against `docs/specs/<feature-slug>.md` to verify that the implementation conforms to spec. The feature is not complete until `pragmatic-spec-check` returns PASS.

---

## Output Location

Code files are placed in the locations derived from the constraint brief (component boundaries + codebase layout). No output goes to `docs/` — this skill writes to source and test directories only.

---

## Constraint Priority

When rules from different sources conflict, apply this priority order:

1. **Spec section 5 (Technology Decisions)** — explicit decisions override defaults
2. **Architecture spec rules** (`docs/arch/*.arch.md`) — structural constraints
3. **Claude project rules** (`.claude/rules/`) — naming and boundary enforcement
4. **Codebase conventions** — inferred from existing code

If a conflict cannot be resolved by priority (e.g., the spec makes a technology decision that violates an arch spec boundary), **stop and ask** — do not silently pick one.
