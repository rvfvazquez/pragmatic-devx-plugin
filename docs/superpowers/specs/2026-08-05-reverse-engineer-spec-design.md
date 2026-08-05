# Design: `pragmatic-reverse-engineer` — Generate Specs from Existing Code

**Status:** Approved
**Date:** 2026-08-05

## Problem

Both `pragmatic-spec-create` and `pragmatic-arch-spec-create` assume a human is
originating the document from a stated need — a feature idea, an architecture
decision to make. Neither has a real path for the opposite case: **code
already exists, with no spec at all**, and someone needs a spec produced by
reading the code rather than an interview.

This shows up in three related situations: legacy/undocumented code that
needs a spec backfilled (primary driver), onboarding into an unfamiliar
repository, and audit/migration work that needs a documented baseline before
changing anything.

`pragmatic-arch-spec-create` has a one-line edge case gesturing at this
("scan the codebase thoroughly... the code is the source of truth") but
nothing operational: no guidance on reconstructing ADRs from code, no handling
for "I don't know the module boundaries yet," and no equivalent at all on the
feature-spec side.

## Non-Goals

- No new document type or template — output is exactly today's
  `docs/specs/<feature-slug>.md` / `docs/arch/<name>.arch.md`, produced by the
  existing skills.
- No changes to `pragmatic-spec-create` or `pragmatic-arch-spec-create`
  themselves. Both already tolerate a pre-informed conversation (their own
  "restate to confirm" wording and codebase-scan-before-interview steps
  already support this) — see Delegation Mechanics below.
- No new lifecycle skill (no "reverse-engineer-validate" or
  "reverse-engineer-update"). The session report this design introduces is an
  intentionally immutable, point-in-time record — not a document with its own
  lifecycle.

## Why a New Skill, Not a Parameter

The straightforward YAGNI move would be a "reverse-engineering mode" bolted
onto the two existing create skills. That was the first approach considered
and rejected for one reason: the user wants reverse engineering to be an
explicit, intentional entry point — not a mode buried inside two skills whose
primary shape is "interview a human about something not yet built." A
dedicated skill also groups the actually-new logic (codebase scanning,
confidence tagging, feature-boundary discovery) in one place instead of
duplicating it across both create skills.

The risk with a dedicated skill is the one `CLAUDE.md` explicitly warns
about: two skills producing the same output artifact ("duplicate lifecycle
coverage"). This design avoids that by construction — `pragmatic-reverse-engineer`
never writes `docs/specs/*.md` or `docs/arch/*.md` itself. It only discovers
and hands off; the existing create skills remain the sole owners of those
outputs, identical to how `pragmatic-spec-build` dispatches `tdd-implementer`
for its own build step without that subagent owning any spec document.

## Flow

### Step 1 — Ask arch vs. feature vs. both

Before any scanning, `AskUserQuestion`:

> "Is this about structure (components, boundaries, ADRs) or about what a
> specific feature does (behavior, acceptance criteria)?"
> Options: **Architecture** / **Feature** / **Both**

Always asked up front — no inference from message wording. Getting this
wrong routes to the wrong template and the wrong downstream skill, so it's
not a good candidate for a heuristic guess.

### Step 2a — Architecture branch

1. Determine target: path/module named by the user, or the whole repo.
2. Scan for components, dependency directions, and data flow — using the
   same diagram categories `pragmatic-arch-spec-create` already defines
   (component structure, request/response flow, async flow, state
   transitions).
3. Reconstruct ADRs from code patterns (a queue in use, a specific ORM, a
   caching layer). Tag the **choice** as confirmed (it demonstrably exists in
   code) and the **rationale** as inferred (why that choice was made is not
   recoverable from code alone).
4. Invoke `pragmatic-arch-spec-create`, stating findings inline before its
   own Step 1.5 interview runs: confirmed facts are stated and moved past,
   inferred items are surfaced for the user to confirm or correct via that
   skill's own `AskUserQuestion` step.

### Step 2b — Feature branch

1. If the user names a target, scan it directly.
2. If not, scan the repo for candidate feature boundaries (routes, handlers,
   domain folders, distinct entry points) and present the list via
   `AskUserQuestion` (multi-select) for the user to pick one or several.
3. For each selected feature: infer problem/goal (flagged inferred — intent
   isn't verifiable from code), scope (confirmed from code paths), tech stack
   (confirmed from imports/config, same as the normal flow already infers in
   its own Step 3), and acceptance criteria drafted from existing tests where
   possible. Distinguish "backed by a passing test" from "inferred from code
   path with no test coverage" — this materially affects how much the
   resulting criterion should be trusted.
4. Invoke `pragmatic-spec-create` once per selected feature, same
   inline-findings handoff as the architecture branch. Multiple features
   naturally produce multiple specs, reusing `pragmatic-spec-create`'s
   existing Step 2.5 over-broad-scope guard rather than reimplementing it.

### Step 2c — Both

Run the architecture branch first. Reuse its component boundaries as the seed
list for feature-boundary discovery (avoids a second full repo scan), then
run the feature branch.

## Delegation Mechanics

`pragmatic-reverse-engineer` invokes the existing create skills via the Skill
tool, in the same conversation turn — not as a subagent dispatch. This means
the discovery findings from Step 2a/2b are already present in context when
the downstream skill's own steps run. Both existing skills already have
wording built to make use of that:

- `pragmatic-spec-create` Step 2's own example format says *"Restate what you
  understood the feature to solve — ask the user to confirm or correct"* —
  already a confirm-not-originate pattern.
- `pragmatic-spec-create` Step 3/4 already skip technology questions "already
  evident from the codebase."
- `pragmatic-arch-spec-create`'s existing edge case already treats the code
  as the source of truth for reverse-engineered content.

No edits to either skill file are required. The instruction to
`pragmatic-reverse-engineer` is simply: state confirmed findings outright,
surface inferred findings for the downstream skill's own confirmation step,
and let that skill's existing guards (constitution check, existing-file
check, scope-splitting) run unmodified.

## Confidence Tagging

Confidence tags (confirmed-from-code vs. inferred) are **conversational
scaffolding for the handoff, not a new persisted-document convention.** Once
the user confirms an inferred item during the downstream skill's normal
interview, it becomes ordinary content in the spec — no new marker in the
file. Genuinely unresolved gaps still use the existing `[TODO: ...]`
convention already defined in both templates. This avoids introducing a
second placeholder syntax alongside the one that already exists.

## Provenance

Two complementary records, serving different audiences:

**1. `## Provenance` section, appended inside the generated doc.** After
`pragmatic-spec-create` / `pragmatic-arch-spec-create` writes the file
normally, `pragmatic-reverse-engineer` performs one follow-up edit **to that
generated markdown file** (not to any skill definition) to append a trailing
section (same pattern as how Changelog is appended later by
`pragmatic-spec-update` — not part of the initial template): generation date,
counts of confirmed-from-code / inferred-and-user-confirmed / still-open
items, and a link to the session report below. This travels with the doc for
anyone reading it later.

**2. Session report, `docs/reverse-engineering/<session-slug>-<date>.report.md`.**
`<session-slug>` is the target name given in Step 1 (e.g. `payments`), or
`repo-wide` when no target was named and feature discovery ran across the
whole repository. One report per reverse-engineering run, covering every doc
produced in that session
(e.g. several feature specs from one discovery pass). Contents: targets
scanned, candidates considered but not selected (so a later session knows
what's still undocumented), confidence tags per item, corrections the user
made during confirmation (useful signal for where inference tends to be
wrong), and links to the resulting doc(s) with their version at generation
time.

This is explicitly a **point-in-time snapshot, not a living document** — no
update or validate skill of its own. The report itself states this plainly
("this reflects the state of the code on `<date>`; it is not updated when the
target docs change afterward — see that document's own changelog"). This is
what keeps it from becoming a second, silently-stale source of truth: it
never claims to be current beyond its own timestamp.

## New Files

```
skills/pragmatic-reverse-engineer/SKILL.md
skills/pragmatic-reverse-engineer/references/discovery-heuristics.md   — component/feature boundary detection, confidence-tagging vocabulary for the handoff
skills/pragmatic-reverse-engineer/references/report-template.md        — session report template
tests/skill-triggering/prompts/pragmatic-reverse-engineer.txt          — trigger prompt
```

Updated files:

```
skills/pragmatic-howto/references/skill-map.md   — new entry
skills/pragmatic-howto/SKILL.md                  — new row in Quick-Decision Table
```

Version bump: all five `version` fields per the Versioning section of
`CLAUDE.md`, done together when this ships.

## Testing

- `tests/skill-triggering/prompts/pragmatic-reverse-engineer.txt` must
  trigger `pragmatic-reverse-engineer`, not `pragmatic-spec-create` or
  `pragmatic-arch-spec-create` — run the full `tests/skill-triggering` suite
  before and after adding the skill to confirm no cross-triggering in either
  direction (existing create-skill prompts must still trigger the create
  skills, not the new one).
- Manual walkthrough of all three branches (architecture, feature with named
  target, feature with repo-wide discovery) against a real undocumented
  module in a sample project, confirming: the downstream create skill's own
  guards still run (constitution check, existing-spec-file check), the
  Provenance section is appended correctly, and the session report is
  written with accurate confidence counts.
