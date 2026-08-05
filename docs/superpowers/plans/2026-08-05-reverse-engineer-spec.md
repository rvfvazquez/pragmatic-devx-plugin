# pragmatic-reverse-engineer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `pragmatic-reverse-engineer` skill that generates a feature spec or architecture spec by scanning existing, undocumented code and handing off to the existing `pragmatic-spec-create` / `pragmatic-arch-spec-create` skills to write the document.

**Architecture:** A discovery-only skill. It never writes `docs/specs/*.md` or `docs/arch/*.md` itself — it scans code, tags findings CONFIRMED (observable in code) or INFERRED (a guess about intent), and invokes the existing create skills via the Skill tool with those findings already in the conversation. It appends a `## Provenance` section to whatever the create skill writes, and — once every target in the session is done — writes a point-in-time session report to `docs/reverse-engineering/`.

**Tech Stack:** Markdown skill files (Claude Code plugin convention), no code/runtime — this plugin ships behavior as instructions, not executables.

## Global Constraints

- Zero edits to `skills/pragmatic-spec-create/` or `skills/pragmatic-arch-spec-create/` — the whole design depends on those skills' existing "restate to confirm" wording already tolerating a pre-informed handoff. (Source: design doc "Delegation Mechanics".)
- No new persisted-document placeholder syntax. Confidence tags (CONFIRMED/INFERRED) are conversational only; the only marker that ends up in a written spec/arch spec is the existing `[TODO: ...]` convention. (Source: design doc "Confidence Tagging".)
- All five version fields (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`, `.claude-plugin/marketplace.json`) must be bumped together, per `CLAUDE.md`'s Versioning section. Current value: `0.6.1`. This is a new feature (new skill), so bump to `0.7.0`.
- Multiple discovery targets are handled one at a time — never batch N targets into a single handoff. (Source: design doc "Sequential Delegation".)
- Follow the exact frontmatter/section-structure conventions already used by `pragmatic-spec-create` and `pragmatic-arch-spec-create` (When This Skill Applies / Do not use when / numbered Steps / STOP gates / Output Summary banner / Additional Resources) so the new skill reads as native to this plugin, not bolted on.

---

### Task 1: Discovery heuristics reference

**Files:**
- Create: `skills/pragmatic-reverse-engineer/references/discovery-heuristics.md`

**Interfaces:**
- Produces: five named sections that Task 3 (`SKILL.md`) links to by exact heading text: `## Confidence Vocabulary`, `## Architecture Branch — Component & Dependency Discovery`, `## Feature Branch — Candidate Boundary Discovery (No Target Given)`, `## Feature Branch — Behavior Inference (Target Known)`, `## Presenting the Brief During Handoff`.

- [ ] **Step 1: Write the reference file**

```markdown
# Discovery Heuristics — Reverse Engineering

Shared guidance for scanning existing code and building a confidence-tagged
discovery brief, used by both the architecture and feature branches of
`pragmatic-reverse-engineer`.

## Confidence Vocabulary

Use exactly two tags when presenting findings during handoff:

- **CONFIRMED** — directly observable in the code: an import, a config
  value, a route registration, a passing test, a file that exists. State
  these outright to the downstream skill; do not re-ask about them.
- **INFERRED** — a judgment call about *intent*, *rationale*, or *purpose*
  that code alone cannot prove. Surface these for the user to confirm or
  correct via the downstream skill's own interview.

A finding about *what exists* is almost always CONFIRMED. A finding about
*why* it exists, or *what problem it was meant to solve*, is almost always
INFERRED — code rarely states its own rationale unless a comment, commit
message, ADR, or existing doc says so explicitly (in which case cite the
source and still mark it CONFIRMED, with the source noted).

## Architecture Branch — Component & Dependency Discovery

- **Entry points**: main/index/app/server files, CLI entry commands, Lambda
  handlers.
- **Component boundaries**: top-level folders under the target path with a
  consistent internal shape (e.g., every folder has its own handler +
  service + repository) are strong signals of a component boundary. A
  folder that only holds shared types/utilities is not a component.
- **Dependency direction**: trace imports between the folders identified
  above. Report the direction actually observed (`A imports B`), not an
  idealized direction — if the code violates a layering convention (e.g.,
  domain importing infrastructure), report the violation as CONFIRMED
  rather than silently correcting it; the ADR-reconstruction step below is
  the place to flag it as a decision worth revisiting.
- **ADR reconstruction**: for each technology or pattern found (a specific
  queue client, ORM, cache, messaging library), record the **choice** as
  CONFIRMED and the **rationale** as INFERRED, unless a comment, commit
  message, or existing doc states the rationale explicitly.
- **Data flow**: pick the 1–3 flows with the most components involved
  (mirrors `pragmatic-arch-spec-create` section 7's "1–3 key flows"
  guidance) and trace each end to end through the code — request handler →
  service → repository/external call — to build the sequence.

## Feature Branch — Candidate Boundary Discovery (No Target Given)

When the user hasn't named a specific module, scan for candidate feature
boundaries using these signals, in order of reliability:

1. **Route/command groupings** — HTTP routes sharing a path prefix, or CLI
   subcommands, each usually correspond to one feature.
2. **Domain-named folders** — a folder named for a business concept
   (`payments/`, `orders/`, `checkout/`) rather than a technical layer
   (`handlers/`, `utils/`) is a strong feature-boundary signal.
3. **Test file groupings** — a dedicated test file or test folder per
   business concept is a strong secondary signal, and its test cases become
   the seed for that feature's acceptance criteria.

Build one candidate per distinct grouping. Present the list via
`AskUserQuestion` (`multiSelect: true`) with a one-line description of what
each candidate appears to do, and mark any candidate whose slug already
matches an existing file in `docs/specs/` as **"(already has a spec —
pragmatic-spec-create will offer to replace it)"** so the user doesn't
unknowingly duplicate work already done.

## Feature Branch — Behavior Inference (Target Known)

- **Problem/goal**: INFERRED — state your best read of what problem the
  code solves, in one or two sentences, for the user to confirm or correct.
- **Scope boundaries**: CONFIRMED — derived directly from which
  files/routes/handlers were scanned.
- **Technology decisions**: CONFIRMED — read directly from imports, config,
  and framework usage. This mirrors what `pragmatic-spec-create` Step 3
  already does; the difference here is these findings feed the handoff
  instead of triggering a fresh scan.
- **Acceptance criteria**: draft one Given/When/Then per distinct behavior
  found.
  - Tag **CONFIRMED-BY-TEST** when a passing automated test exercises
    exactly that behavior — cite the test file and case name.
  - Tag **INFERRED-NO-TEST** when the criterion is drafted from reading the
    code path alone, with no test backing it. Flag these as needing more
    scrutiny during confirmation than CONFIRMED-BY-TEST criteria.

## Presenting the Brief During Handoff

When invoking the downstream create skill, state findings in this shape so
its own steps can use them without re-asking:

```
Findings from scanning <target>:

CONFIRMED:
- <fact> (source: <file/test/config>)
- ...

INFERRED — please confirm or correct:
- <best guess> — <what would change if wrong>
- ...
```

The downstream skill's own `AskUserQuestion` steps should only actually
prompt for the INFERRED items and any genuine gaps neither branch above
could resolve — CONFIRMED items are stated, not asked.
```

- [ ] **Step 2: Verify the file reads cleanly**

Run: `cat skills/pragmatic-reverse-engineer/references/discovery-heuristics.md | head -5`
Expected: prints the `# Discovery Heuristics — Reverse Engineering` header — confirms the file was created at the right path with no leading whitespace/encoding issues.

- [ ] **Step 3: Commit**

```bash
git add skills/pragmatic-reverse-engineer/references/discovery-heuristics.md
git commit -m "feat: add discovery heuristics reference for reverse-engineer skill"
```

---

### Task 2: Session report template reference

**Files:**
- Create: `skills/pragmatic-reverse-engineer/references/report-template.md`

**Interfaces:**
- Produces: the section structure Task 3 (`SKILL.md`) Step 4 fills in when writing `docs/reverse-engineering/<session-slug>-<date>.report.md`: `1. Session Overview`, `2. Targets Scanned`, `3. Candidates Considered But Not Selected`, `4. Documents Produced`, `5. Confidence Summary`, `6. Corrections Made During Confirmation`.

- [ ] **Step 1: Write the reference file**

```markdown
# Reverse Engineering Session Report — Template

Used by `pragmatic-reverse-engineer` to write
`docs/reverse-engineering/<session-slug>-<date>.report.md` after a session
completes (including sessions that produced multiple documents via the
Sequential Delegation loop).

Fill every section with concrete content. This document has no
`[TODO: ...]` markers — anything unknown simply isn't a fact yet and is
omitted, not marked open. Unlike a spec, this report gets no follow-up pass.

---

## 1. Session Overview

- **Session slug**: `<session-slug>`
- **Date**: `<date>`
- **Branch**: Architecture | Feature | Both
- **Requested by**: (infer from git config or leave blank)

> This is a point-in-time snapshot of a reverse-engineering session run on
> `<date>`. It reflects the state of the code at that time and is **not
> updated** when the documents it produced are later changed — see each
> document's own Provenance section and changelog for current state.

## 2. Targets Scanned

| Target | Path | Scope type (arch only) |
|--------|------|--------------------------|
| ... | ... | ... |

## 3. Candidates Considered But Not Selected

*(Feature branch, repo-wide discovery only — omit this section entirely for
a named target or an architecture-only session.)*

| Candidate | Why it looked like a feature boundary | Already had a spec? |
|-----------|-----------------------------------------|------------------------|
| ... | ... | Yes / No |

## 4. Documents Produced

| Document | Path | Version at generation |
|----------|------|--------------------------|
| ... | `docs/specs/...` or `docs/arch/...` | ... |

## 5. Confidence Summary

One row per document produced in this session.

| Document | Confirmed from code | Inferred & user-confirmed | Still open (`[TODO: ...]`) |
|----------|------------------------|-------------------------------|--------------------------------|
| ... | N | N | N |

## 6. Corrections Made During Confirmation

Items the discovery brief inferred that the user corrected during the
downstream skill's interview — useful signal for where inference tends to
be wrong on this codebase.

| Document | Inferred | Corrected to |
|----------|----------|----------------|
| ... | ... | ... |

*(If nothing was corrected: "No corrections — all inferred items were
confirmed as-is.")*
```

- [ ] **Step 2: Verify the file reads cleanly**

Run: `cat skills/pragmatic-reverse-engineer/references/report-template.md | head -5`
Expected: prints the `# Reverse Engineering Session Report — Template` header.

- [ ] **Step 3: Commit**

```bash
git add skills/pragmatic-reverse-engineer/references/report-template.md
git commit -m "feat: add session report template for reverse-engineer skill"
```

---

### Task 3: Main skill file

**Files:**
- Create: `skills/pragmatic-reverse-engineer/SKILL.md`

**Interfaces:**
- Consumes: section headings from Task 1 (`references/discovery-heuristics.md`) and Task 2 (`references/report-template.md`), linked by relative path.
- Produces: the skill name `pragmatic-reverse-engineer` that Task 4's test prompt targets, and the Quick-Decision Table trigger phrases that Task 5 cross-references in `pragmatic-howto`.

- [ ] **Step 1: Write the skill file**

```markdown
---
name: pragmatic-reverse-engineer
description: This skill should be used when the user asks to "reverse engineer a spec from this code", "generate a spec from the existing code", "document what this code already does", "backfill a spec for this legacy module", "create a spec by reading the implementation, not from a description", "this module has no documentation, can you write a spec from what's actually there", or wants a feature spec or architecture spec produced primarily by reading existing, undocumented code rather than from a stated feature idea or architecture decision.
---

# pragmatic-reverse-engineer

Generate a feature spec or architecture spec by reading existing,
undocumented code — not by interviewing a human about something not yet
built.

## Purpose

Produce a `docs/specs/<feature-slug>.md` or `docs/arch/<name>.arch.md`
document for code that already exists and has no spec, by scanning the
code, inferring its behavior and structure, and handing off to the existing
create skills to confirm and write the document. This skill never writes
those files itself — it discovers, tags findings by confidence, and
delegates.

## When This Skill Applies

Use this skill when code already exists, no spec or arch spec documents it
yet, and the user wants the document produced primarily from reading the
code rather than describing what they want built.

**Do not use when:**
- The user has an idea for something not yet built and wants to spec it
  before writing code → use `pragmatic-spec-create`
- The user wants to design a system's architecture before or during
  building it → use `pragmatic-arch-spec-create`
- A spec or arch spec already exists for this target → use
  `pragmatic-spec-update` / `pragmatic-arch-spec-update` to revise it, or
  `pragmatic-spec-check` / `pragmatic-arch-spec-check` to verify it still
  matches the code

**Ownership:** This skill never writes to `docs/specs/` or `docs/arch/`. It
only scans, infers, and hands off — `pragmatic-spec-create` and
`pragmatic-arch-spec-create` remain the sole owners of those files,
including their own constitution check, existing-file guard, and
scope-splitting logic. Nothing about those two skills changes when invoked
from here.

## How Reverse Engineering Works

### Step 1 — Ask: Architecture, Feature, or Both

Before scanning anything, use `AskUserQuestion`:

```
Is this reverse-engineering pass about structure or about behavior?

- Architecture — components, boundaries, dependency direction, the
  decisions implicit in what was built. Produces an architecture spec.
- Feature — what a specific piece of functionality actually does:
  behavior, scope, acceptance criteria. Produces a feature spec.
- Both — run architecture first, then use its component boundaries to
  seed feature discovery.
```

This is always asked — never inferred from message wording. Routing to the
wrong branch means the wrong template and the wrong downstream skill, so it
isn't a safe guess.

### Step 2a — Architecture Branch

1. **Determine target.** A path/module the user named, or the whole
   repository if none was given.
2. **Scan.** Follow `references/discovery-heuristics.md` ("Architecture
   Branch — Component & Dependency Discovery") to find components,
   dependency directions, and the 1–3 most significant data flows.
3. **Reconstruct ADRs.** For each technology/pattern found, record the
   choice as CONFIRMED and the rationale as INFERRED (unless a
   comment/commit/doc states it — then cite the source).
4. **Hand off** to `pragmatic-arch-spec-create` (Step 3 below covers the
   handoff mechanics).

### Step 2b — Feature Branch

1. **Determine target(s).**
   - If the user named a module/path, that is the target.
   - If not, run repo-wide candidate discovery per
     `references/discovery-heuristics.md` ("Feature Branch — Candidate
     Boundary Discovery (No Target Given)"), then present the candidates
     via `AskUserQuestion` with `multiSelect: true` so the user can pick
     one or several.
2. **For each selected target**, scan per
   `references/discovery-heuristics.md` ("Feature Branch — Behavior
   Inference (Target Known)"): problem/goal (INFERRED), scope (CONFIRMED),
   tech stack (CONFIRMED), acceptance criteria drafted from tests where
   they exist (tagged CONFIRMED-BY-TEST or INFERRED-NO-TEST).
3. **Hand off** to `pragmatic-spec-create`, once per target — see
   "Sequential Delegation" below before processing more than one.

### Step 2c — Both

Run Step 2a to completion first (including its handoff and provenance —
Steps 3–4 below). Then run Step 2b, using the components found in Step 2a
as the seed list for candidate discovery instead of re-scanning the repo
from scratch.

### Sequential Delegation — One Target at a Time

When Step 2b (or a whole-repo Step 2a) surfaces more than one target, **do
not batch them into a single handoff.** For each target, in order:

1. Scan that one target.
2. Hand off to the downstream create skill and let its interview, file
   write, and Provenance edit (Steps 3–4 below) finish completely.
3. Only then move to the next target.

Carrying findings for every target at once into a single handoff dilutes
the downstream interview — by target 5, the conversation is crowded with
targets 1–4's findings too, and answer quality degrades. One target fully
handled before the next starts keeps each `pragmatic-spec-create`
invocation scoped to exactly what that one document needs. The session
report (Step 4) is what ties the resulting documents back together
afterward — the loop itself stays uncoupled between iterations.

### Step 3 — Handoff

Invoke `pragmatic-spec-create` or `pragmatic-arch-spec-create` via the
Skill tool. Before invoking, state the findings for this one target in the
shape defined in `references/discovery-heuristics.md` ("Presenting the
Brief During Handoff"): CONFIRMED items stated outright, INFERRED items
flagged for confirmation.

The downstream skill then runs its normal steps unmodified. Its own
"restate to confirm" wording (Step 2 of `pragmatic-spec-create`, Step 1.5
of `pragmatic-arch-spec-create`) and its own codebase-scan-skips-known-tech
behavior mean it will use the stated findings instead of asking blind — but
it still runs its own constitution check and existing-file guard exactly as
it would for a from-scratch spec.

### Step 4 — Provenance

After the downstream skill finishes writing the document for one target:

1. **Append a `## Provenance` section** to the just-written file (a
   follow-up `Edit`, not a change to any skill — same pattern as how
   `pragmatic-spec-update` appends a Changelog later, not part of the
   initial template):

   ```markdown
   ## Provenance

   Reverse-engineered from code on <date> (session: `<session-slug>`).
   - Confirmed from code: <N> items
   - Inferred, confirmed by user: <N> items
   - Still open: <N> items (see `[TODO: ...]` markers above)

   Full session report: `docs/reverse-engineering/<session-slug>-<date>.report.md`
   ```

2. **Record the target's results** (target scanned, candidates not
   selected, confidence counts, any corrections the user made to an
   INFERRED item) to be written into the session report once every target
   in the session is done.

Once every target from Step 2 has been through Steps 3–4, write the session
report at `docs/reverse-engineering/<session-slug>-<date>.report.md` using
`references/report-template.md`. Create the `docs/reverse-engineering/`
directory first if it doesn't exist. `<session-slug>` is the target name
from Step 1 (e.g. `payments`), or `repo-wide` when no target was named and
candidate discovery ran across the whole repository.

### Step 5 — Output Summary

After the session report is written:
1. List every document produced, with its path.
2. State the session report path.
3. Summarize confidence counts across the whole session (sum of Step 4's
   per-target counts).
4. List any candidates that were found but not selected, so the user knows
   what's still undocumented.

---

> **Reverse engineering complete** — see the session report at
> `docs/reverse-engineering/<session-slug>-<date>.report.md` for full
> detail.
>
> **Next step:** Run `pragmatic-spec-validate` / `pragmatic-arch-spec-validate`
> on each document produced before treating it as a source of truth —
> reverse-engineered content still needs the same quality gate as any other
> spec.

## Output Location

This skill does not own an output location for specs/arch specs — see
`pragmatic-spec-create` / `pragmatic-arch-spec-create`. It owns only:

```
docs/reverse-engineering/<session-slug>-<date>.report.md
```

## Additional Resources

- **`references/discovery-heuristics.md`** — component/feature boundary
  detection, confidence-tagging vocabulary, and the exact shape for
  presenting findings during handoff
- **`references/report-template.md`** — session report template
```

- [ ] **Step 2: Verify frontmatter is valid and paths resolve**

Run:
```bash
head -3 skills/pragmatic-reverse-engineer/SKILL.md
test -f skills/pragmatic-reverse-engineer/references/discovery-heuristics.md && echo "heuristics OK"
test -f skills/pragmatic-reverse-engineer/references/report-template.md && echo "template OK"
```
Expected: prints the `---` / `name: pragmatic-reverse-engineer` frontmatter lines, then `heuristics OK` and `template OK` — confirms both files Task 3 links to actually exist at those relative paths.

- [ ] **Step 3: Commit**

```bash
git add skills/pragmatic-reverse-engineer/SKILL.md
git commit -m "feat: add pragmatic-reverse-engineer skill"
```

---

### Task 4: Trigger test + regression check

**Files:**
- Create: `tests/skill-triggering/prompts/pragmatic-reverse-engineer.txt`

**Interfaces:**
- Consumes: `skills/pragmatic-reverse-engineer/SKILL.md`'s `description:` frontmatter (Task 3) — the prompt below is written to match its trigger phrasing without naming the skill explicitly, per this test suite's convention (see other files in `tests/skill-triggering/prompts/`).

- [ ] **Step 1: Write the trigger prompt**

```
We inherited a checkout module with zero documentation — no spec, no comments explaining the business rules, nothing written down anywhere. Can you read through the existing code and generate a spec from what it actually does, so we finally have something in docs/specs for it?
```

Save this exact text to `tests/skill-triggering/prompts/pragmatic-reverse-engineer.txt`.

- [ ] **Step 2: Run the new trigger test**

Run: `bash tests/skill-triggering/run-test.sh pragmatic-reverse-engineer tests/skill-triggering/prompts/pragmatic-reverse-engineer.txt`
Expected: `✅ PASS: Skill 'pragmatic-reverse-engineer' was triggered`

If it instead triggers `pragmatic-spec-create`, sharpen the prompt's wording (lean harder on "zero documentation" / "generate a spec from what it actually does" / "read through the existing code") and re-run until it passes. Do not weaken `pragmatic-spec-create`'s own description to force this — that would be an edit to a skill this plan is not allowed to touch (see Global Constraints).

- [ ] **Step 3: Run regression checks against the two skills this one delegates to**

Run:
```bash
bash tests/skill-triggering/run-test.sh pragmatic-spec-create tests/skill-triggering/prompts/pragmatic-spec-create.txt
bash tests/skill-triggering/run-test.sh pragmatic-arch-spec-create tests/skill-triggering/prompts/pragmatic-arch-spec-create.txt
```
Expected: both still `✅ PASS` for their own skill name — confirms adding `pragmatic-reverse-engineer` did not start cross-triggering on the existing create-skill prompts.

- [ ] **Step 4: Commit**

```bash
git add tests/skill-triggering/prompts/pragmatic-reverse-engineer.txt
git commit -m "test: add skill-triggering prompt for pragmatic-reverse-engineer"
```

---

### Task 5: Wire into pragmatic-howto

**Files:**
- Modify: `skills/pragmatic-howto/SKILL.md`
- Modify: `skills/pragmatic-howto/references/skill-map.md`

**Interfaces:**
- Consumes: `pragmatic-reverse-engineer` (Task 3), `pragmatic-spec-create` / `pragmatic-arch-spec-create` (existing, unmodified).

- [ ] **Step 1: Add a "Reverse Engineering Entry Point" section to `pragmatic-howto/SKILL.md`**

Insert this new section immediately after the existing `## Architecture Spec Lifecycle` table (after the line `| `pragmatic-arch-spec-check` | Verify codebase matches documented architecture decisions |`) and before `## Governance`:

```markdown
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
```

- [ ] **Step 2: Add a row to the Quick-Decision Table in `pragmatic-howto/SKILL.md`**

Find the existing table row:
```markdown
| "update the constitution" / "add a global rule" | `pragmatic-project-constitution-update` |
```
Add immediately after it:
```markdown
| "reverse engineer a spec from this code" / "generate a spec from existing code" / "document what this legacy code does" | `pragmatic-reverse-engineer` |
```

- [ ] **Step 3: Add a skill-map entry to `skills/pragmatic-howto/references/skill-map.md`**

Append this new top-level section at the end of the file, after the existing `## Architecture Specs` section (after the line `**Behavior on VIOLATION:** Reports the specific file/location, the rule violated, and the ADR that defines the rule.`):

```markdown

---

## Reverse Engineering

### pragmatic-reverse-engineer

**Purpose:** Generate a feature spec or architecture spec by scanning
existing, undocumented code, then handing off to `pragmatic-spec-create` /
`pragmatic-arch-spec-create` to write it.

**Output:** Does not write `docs/specs/` or `docs/arch/` itself — see those
two skills. Owns only `docs/reverse-engineering/<session-slug>-<date>.report.md`.

**Pre-conditions:** None of its own — the downstream create skill's
pre-conditions (constitution check, existing-file guard) run unmodified
when invoked.

**Behavior:**
- Always asks Architecture / Feature / Both before scanning anything.
- Tags every finding CONFIRMED (observable in code) or INFERRED (a guess
  about intent) — CONFIRMED items are stated to the downstream skill
  outright, INFERRED items are surfaced for the user to confirm or correct.
- Processes multiple discovery targets one at a time, never batched, so
  each downstream interview stays scoped to one target.
- Appends a `## Provenance` section to each document the downstream skill
  writes, and a session report tying all of them together.

**Guard:** Never writes to `docs/specs/` or `docs/arch/` itself — those
remain owned exclusively by `pragmatic-spec-create` /
`pragmatic-arch-spec-create`.
```

- [ ] **Step 4: Verify both edits landed**

Run:
```bash
grep -c "pragmatic-reverse-engineer" skills/pragmatic-howto/SKILL.md
grep -c "pragmatic-reverse-engineer" skills/pragmatic-howto/references/skill-map.md
```
Expected: both commands print a number ≥ 2 (SKILL.md: section heading + table row; skill-map.md: section heading + purpose line).

- [ ] **Step 5: Commit**

```bash
git add skills/pragmatic-howto/SKILL.md skills/pragmatic-howto/references/skill-map.md
git commit -m "docs: wire pragmatic-reverse-engineer into pragmatic-howto"
```

---

### Task 6: Version bump

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `.cursor-plugin/plugin.json`
- Modify: `gemini-extension.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- None — this task only changes a `"version"` string in each file; no other task depends on the specific value beyond it being `0.7.0` and consistent across all five.

- [ ] **Step 1: Bump each file's version field from `0.6.1` to `0.7.0`**

In `.claude-plugin/plugin.json`, change:
```json
  "version": "0.6.1",
```
to:
```json
  "version": "0.7.0",
```

In `.codex-plugin/plugin.json`, change the same `"version": "0.6.1",` line the same way.

In `.cursor-plugin/plugin.json`, change the same `"version": "0.6.1",` line the same way.

In `gemini-extension.json`, change:
```json
  "version": "0.6.1"
```
(no trailing comma — it's the last field before the closing brace) to:
```json
  "version": "0.7.0"
```

In `.claude-plugin/marketplace.json`, change the nested plugin entry's version:
```json
      "version": "0.6.1"
```
to:
```json
      "version": "0.7.0"
```

- [ ] **Step 2: Verify all five are consistent**

Run: `grep -rn '"version"' .claude-plugin/plugin.json .codex-plugin/plugin.json .cursor-plugin/plugin.json gemini-extension.json .claude-plugin/marketplace.json`
Expected: five lines, every one showing `0.7.0` and no leftover `0.6.1`.

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/plugin.json .codex-plugin/plugin.json .cursor-plugin/plugin.json gemini-extension.json .claude-plugin/marketplace.json
git commit -m "chore: bump version to 0.7.0 for pragmatic-reverse-engineer"
```

---

## Post-Plan Checklist (from CLAUDE.md PR Requirements)

Not a task to execute blindly — a reminder for whoever opens the PR:

- [ ] Manually walk through all three branches (Architecture, Feature with a named target, Feature with repo-wide discovery) against a real undocumented module in a sample project. Confirm: the downstream create skill's own guards still fire (constitution check, existing-file guard), the `## Provenance` section is appended correctly, and the session report's confidence counts match what was actually presented during the handoff. This is exploratory QA, not a scripted step — do it before opening the PR, not as part of Tasks 1–6.
- [ ] Fill in the PR description: what broke (no reverse-engineering path existed), what changed (new `pragmatic-reverse-engineer` skill, delegating to the two existing create skills), how it was verified (Task 4's triggering + regression tests, plus the manual walkthrough above).
- [ ] State the authoring model and harness in the PR per `CLAUDE.md`'s "Identify yourself" requirement.
- [ ] Get explicit human approval on the full diff before submitting, per `CLAUDE.md`'s "Show your human partner the complete diff" requirement.
