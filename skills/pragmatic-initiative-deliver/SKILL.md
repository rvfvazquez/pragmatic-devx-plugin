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
- The user wants to change the breakdown itself (add, remove, or reorder features) → that's a `pragmatic-initiative-create` concern, not this skill. The one exception is the Step 2.7 fog check: graduating a `## Not Yet Specified` line into a new last row, or descoping a feature, with the user's explicit confirmation.

## How to Deliver an Initiative

### Pre-condition — Load the Initiative

Read `docs/initiatives/<slug>.md` in full. If it doesn't exist, stop and point to `pragmatic-initiative-create`. Note the `autonomous execution` value from `## Notes` — it governs Step 2.4 below for every feature in this run; it is never re-asked per feature.

### Step 1 — Architecture First, If Named

For each arch spec `## Architecture` names that doesn't exist yet, dispatch `pragmatic-arch-spec-create` for it before touching any feature — for a new context listed under `## Domain Language`, as a `module`-scope arch spec for that context; for a new relationship, with that relationship as part of its input, so the context map records it. Call `pragmatic-initiative-status` on each afterward; do not proceed to Step 2 until every one reports `Ready: yes`.

### Step 2 — Work the Feature Table, One Feature at a Time

Pick the next feature, claim it, work it to a terminal outcome, release it, then pick again. Several sessions may run this skill on the same initiative at once — each is a human-driven session with every gate intact; this skill does not parallelize inside one session.

**Takeable.** A row is takeable when all hold: it is not `Build: Checked` and not `Descoped`; no other session holds it (neither its claim file nor its `Claimed by` cell names a different label); and every feature in its `Depends on` is `Build: Checked`. Choose the first takeable row in table order (already topologically sorted by `pragmatic-initiative-create` — never reorder it here). With one session this is exactly the old top-to-bottom walk, because a row only becomes takeable once its dependencies are `Checked`.

**Read the claims once per pick.** Before choosing, list the initiative's claim directory in one command (`ls "<git-common-dir>/pragmatic-devx/claims/<initiative-slug>/"`) and read only the files it shows, rather than probing row by row. Claims are checked only when you pick, when you try to claim, and when you resume — nothing watches them in between, so a claim another session takes after your pick surfaces as a failed exclusive create in the step below.

**Claim before any work.** Use a short label for this session (the user's name for it if given, otherwise a timestamp). A claim has two layers; the claim file is the authority, the table cell is its readable mirror.

1. **Claim file.** Resolve the shared git directory with `git rev-parse --git-common-dir` (the same for every worktree of this clone, never part of a commit). The claim file for feature `#n` is `<git-common-dir>/pragmatic-devx/claims/<initiative-slug>/feature-<n>`. Create its directory, then create the file *exclusively* so only one session can succeed — in a shell, `( set -C; printf '%s\n' "<label> | <ISO date> | <branch>" > "<path>" )`. If it succeeds, the feature is yours. If it fails because the file exists, read it: your own label means you are resuming; any other label means another session holds it — pick the next takeable row.
2. **Table mirror.** Write the label into the row's `Claimed by` cell and re-read the row. If the table has no `Claimed by` column (the initiative predates it), add the column with `—` on every row first. If a claim file names a label but the cell shows `—` (another worktree's copy of the table is behind), the claim file wins: treat the row as held, and write the label into the cell.

If the git directory is unavailable or not writable (no git, restricted sandbox), fall back to the table cell alone and say once that claims then protect only sessions sharing this checkout, not separate worktrees or clones.

**Nothing takeable.** If unchecked rows remain but none is takeable, stop and report which are claimed (and by which label) and which wait on a dependency still being built. Never override another session's claim. A claim file whose branch no longer appears in `git worktree list` is likely stale: report it as such, but delete it only when the user says so.

For the claimed feature:

1. **No spec yet** (`Spec: not created yet`) — dispatch `pragmatic-spec-create` **in Lean mode**, using the initiative's `## Destination` plus this feature's own subsection (description and any `Watch for` note) as the input — pass the `Watch for` note through explicitly so the spec's interview doesn't have to rediscover it. Also pass the feature's **Context** column, so the spec reads that context's glossary — including the terms seeded by `pragmatic-initiative-create` and those added by earlier features' specs — instead of asking which context applies. The spec reads the glossary fresh when it is created, since another session may have added terms since this run began. Update the row's `Spec` column to the created path and its `Status` column to the created spec's own `Status` field.
2. **Spec exists, not yet validated this pass** — dispatch `pragmatic-spec-validate`. If it returns FAIL, dispatch `pragmatic-spec-update` addressing the specific findings, then re-validate once. Do not proceed to build on a FAIL, and do not loop validate/update more than once per feature without surfacing it as a blocker (Step 3).
3. **Check readiness** — call `pragmatic-initiative-status` on this feature's spec path.
4. **Decide whether to build**, using the `autonomous execution` setting noted in the Pre-condition:
   - `autonomous execution: yes` — proceed to build once `pragmatic-initiative-status` reports `Ready: yes` (Status is `Review` or `Approved`, zero open TODOs). Do not wait for a human to flip `Status` to `Approved`.
   - `autonomous execution: no` — stop here for this feature, report that its spec is ready, and wait for explicit human approval before dispatching `pragmatic-spec-build`.
5. **Build** — dispatch `pragmatic-spec-build`, then `pragmatic-spec-check`. Update the row's `Build` column (`In progress` → `Done` → `Checked`, matching `pragmatic-spec-check`'s Overall Status of PASS).
6. **Update the initiative document** after every sub-step above — it is the running log of this delivery, not a summary written once at the end. Table columns record the *what* (current Status/Build state); when a feature reaches `Build: Checked`, also append one line to `## Decisions So Far` recording the *why* — e.g. "Feature X: validated PASS on first pass, built and checked" or "Feature X: validate FAIL (open TODO in section 8), one `pragmatic-spec-update` pass, then checked." If the feature's spec added or redefined glossary terms, name them in that same line — later features will read them. Only append on a feature's terminal outcome for this run (`Checked`, or the blocker reported in Step 3) — not on every sub-step transition, or the section turns into noise. At that terminal outcome, also delete the claim file and reset the row's `Claimed by` to `—`. While waiting for human approval (`autonomous execution: no`), keep the claim: the work is this session's and resumes here.

7. **Fog check** — when a feature reaches `Build: Checked`, read `## Not Yet Specified`. For each line that this feature's outcome has made statable as a feature (the thing it was waiting on now exists), and for any not-yet-built feature that the outcome shows to lie beyond the destination, **propose it — never apply it silently**: list the graduation candidates (with the proposed feature description, context and Depends on) and the proposed Out of Scope moves, and ask the user to confirm. On confirmation, append the new row at the end of the table (never reorder existing rows), add its subsection, remove the graduated line from `## Not Yet Specified`, and append one line to `## Decisions So Far`; a confirmed out-of-scope move goes to `## Out of Scope` with its reason, the row marked `Descoped` in the table. If the user declines or does not answer, leave the document unchanged and carry the candidates into the Step 4 summary.

### Step 3 — Handle Real Blockers

If a feature's `pragmatic-spec-validate` still fails after one `pragmatic-spec-update` pass, or `pragmatic-spec-check` returns FAIL after build, **stop picking further features in this session** and report exactly which feature and which check blocked. Append one line to `## Decisions So Far` recording the blocker before stopping — e.g. "Feature X: blocked, pragmatic-spec-check FAIL on AC-2 after build, see docs/specs/x.md" — so resuming later starts from a record, not just memory of the conversation. Do not skip ahead to features further down the table without the user's say-so (a feature that lists the blocked one under `Depends on` is never takeable; for any other, the user starting another session on it is that say-so, and that session reads the blocker line first) — the dependency order already encodes what's genuinely independent; anything downstream of a blocked row may depend on it even if its own `Depends on` column doesn't name it directly (a later feature can inherit an assumption from an earlier one without listing it as a formal dependency).

### Step 4 — Output Summary

1. State which features reached `Checked` this run
2. State which are still pending, and why — waiting on human approval, genuinely blocked, or claimed by another session (with its label, from the claim files and the table)
3. State any unconfirmed fog-check candidates (graduations and descopes proposed in Step 2.7)
4. Point to the initiative document as the full record

## Guard

**Never bypass `pragmatic-spec-build`'s own HARD-GATE** (spec `Status` must be `Review` or `Approved`, no open TODOs) or any other existing gate in a dispatched skill. `autonomous execution: yes` only changes *who* is allowed to treat those conditions as met — this skill, instead of a human manually setting `Approved` — it never removes the conditions themselves. If a dispatched skill's own gate blocks progress for a reason this skill cannot resolve by re-running `pragmatic-spec-update` once, that is a real blocker (Step 3), not something to route around.
