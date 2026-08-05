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
create skills to confirm and write the document. This skill never creates
or owns those files itself — it discovers, tags findings by confidence, and
delegates; the only edit it makes to a document a create skill has already
written is the Provenance append (Step 4).

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

**Ownership:** This skill never *creates or owns* documents in
`docs/specs/` or `docs/arch/` — `pragmatic-spec-create` and
`pragmatic-arch-spec-create` remain their sole authors, including their own
constitution check, existing-file guard, and scope-splitting logic. Nothing
about those two skills changes when invoked from here. The only
modification this skill makes to those files is appending a `## Provenance`
section (Step 4) to a document a create skill has already written.

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

Run Step 2a to completion first, including its handoff and the per-document
Provenance append (Steps 3–4 below, excluding the session report — that is
written once, after both branches finish). Then run Step 2b, using the
components found in Step 2a as the seed list for candidate discovery
instead of re-scanning the repo from scratch.

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

If the downstream skill ends without writing a file (e.g. the existing-file
guard was declined, or the user chose to create a constitution first
instead of continuing), skip the Provenance append for that target, record
it in the session report as attempted-but-not-produced with the reason, and
continue to the next target in the Sequential Delegation loop (or, if this
was the only target, proceed directly to writing the session report).

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

   A corrected item counts under "inferred, confirmed by user" — the
   correction itself is detailed in the session report, not in this
   per-document count.

2. **Record the target's results** (target scanned, candidates not
   selected, confidence counts, any corrections the user made to an
   INFERRED item) to be written into the session report once every target
   in the session is done.

Once every target from Step 2 has been through Steps 3–4, write the session
report at `docs/reverse-engineering/<session-slug>-<date>.report.md` using
`references/report-template.md`. Create the `docs/reverse-engineering/`
directory first if it doesn't exist. `<session-slug>` is the target name
from Step 2a/2b (e.g. `payments`), or `repo-wide` when no target was named and
candidate discovery ran across the whole repository. If a report already
exists at that exact path (same target, same day), append `-2`, `-3`, etc.
rather than overwriting it.

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
`pragmatic-spec-create` / `pragmatic-arch-spec-create`. Its only edit to
those files is the Provenance append (Step 4). It owns only:

```
docs/reverse-engineering/<session-slug>-<date>.report.md
```

## Additional Resources

- **`references/discovery-heuristics.md`** — component/feature boundary
  detection, confidence-tagging vocabulary, and the exact shape for
  presenting findings during handoff
- **`references/report-template.md`** — session report template
