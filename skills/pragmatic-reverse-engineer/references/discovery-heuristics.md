# Discovery Heuristics — Reverse Engineering

Shared guidance for scanning existing code and building a confidence-tagged
discovery brief, used by both the architecture and feature branches of
`pragmatic-reverse-engineer`.

## Confidence Vocabulary

Two primary tags apply to every finding (below); two additional tags refine
acceptance-criteria findings specifically (see "Feature Branch — Behavior
Inference").

- **CONFIRMED** — directly observable in the code: an import, a config
  value, a route registration, a passing test, a file that exists. State
  these outright to the downstream skill; do not re-ask about them.
- **INFERRED** — a judgment call about *intent*, *rationale*, or *purpose*
  that code alone cannot prove. Surface these for the user to confirm or
  correct via the downstream skill's own interview.

All confidence tags — including the acceptance-criteria-specific
CONFIRMED-BY-TEST / INFERRED-NO-TEST — are conversational only. They belong
in the handoff brief, never in the written spec or arch spec. Once the user
confirms an item during the downstream skill's interview, it becomes
ordinary document content with no tag attached. The only marker that may
ever appear in a persisted document is the existing `[TODO: ...]`
convention.

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
