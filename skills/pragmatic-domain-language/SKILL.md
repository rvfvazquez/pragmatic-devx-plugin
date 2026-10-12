---
name: pragmatic-domain-language
description: This skill should be used when the user asks to "add a term to the glossary", "rename a domain term", "redefine what X means", "update the glossary", "update the context map", "add a bounded context", "record who owns X", or wants to change the project's domain language in docs/glossary/ directly, outside of writing a spec. Also use it to "sync the glossary with the code", "the code drifted from the glossary", "check the glossary against the code", or "update the glossary from the code". Also loaded by the other pragmatic skills for the shared glossary and context-map procedures they apply.
argument-hint: "[--sync] [--context <name>]"
---

# pragmatic-domain-language

The project's domain language — what each concept is called, what it means, which context owns it, and how contexts relate — kept in `docs/glossary/`. This skill is the single source for how that language is read, challenged, written, validated, and used.

## Example Files

Use these as calibration targets for format and level of detail. They describe one project — the order, payment, notification, and authentication specs in the other skills' examples — so the terms line up across the plugin:

- **`examples/example-context-map.md`** — four contexts, an event relationship defined by a system-scope arch spec, shared types, a synchronous call, and translations (including *Customer* meaning different things in two contexts and in Stripe)
- **`examples/example-glossary-ordering.md`** — terms that border another context's vocabulary, and resolved ambiguities
- **`examples/example-glossary-payments.md`**, **`example-glossary-notifications.md`**, **`example-glossary-identity.md`** — a context with an avoided word common in prose, one that keeps a provider's word out of the domain language, and a deliberately small context

## Three Ways This Skill Is Used

**Loaded by another pragmatic skill.** The calling skill names a section below (e.g. "apply §2 Interview Checks"). Apply **only that section**, within the caller's own step, then continue with the caller's next step. Do not run the Direct Edit flow, do not ask the questions in it, and do not end the caller's skill. The caller's own gates (recaps, STOPs, confirmations) still govern when anything is written.

**Invoked directly to change the language** — the user wants to change the domain language itself, outside of writing or updating a spec: add, rename, or redefine a term, add a context, record ownership, add a relationship or translation. Run the **Direct Edit** flow at the end of this file.

**Invoked directly to sync with the code** — the invocation carries the flag `--sync`, optionally with `--context <name>` to limit it to one context (`--sync --context payments`). `--context` on its own also means sync. The bare word `sync` (`sync payments`) is accepted as an alias, and so is a plain-language request to reconcile or check the glossary against the code. Run the **Sync from Code** flow at the end of this file. When the request could be either, ask which with `AskUserQuestion`, ➡️ Sync when it mentions the code, Direct Edit otherwise.

## Files

```
docs/glossary/
├── context-map.md        ← always present when the folder exists; the single entry point
└── <context-slug>.md     ← one per bounded context
```

Formats and content rules: `references/glossary-template.md` (a context's terms) and `references/context-map-template.md` (contexts, Owns, Code paths, Relationships, Translations, and the `Last synced` marker).

`scripts/glossary-drift.sh` is a read-only drift report (needs bash, grep, awk, sed; git optional): `bash scripts/glossary-drift.sh [--root DIR] [--context NAME]`. It checks, per context with a Code column, that every `_In code_` identifier still exists in the code (STALE) and that no `_Avoid_` word is used as an identifier (AVOIDED). Exit 0 means no findings, 1 findings, 2 no map. It is the first step of Sync from Code and is safe to run in CI or a pre-commit hook on its own.

---

## §1 Locate the Context

1. If `docs/glossary/context-map.md` does not exist, there is no glossary yet — say so and continue; §2 treats every central concept as new.
2. Read the map. Identify the context the work belongs to by the map's **Purpose** and **Owns** columns, by the linked arch spec, or — when the work is about specific files — by the **Code** paths that contain them. Work spanning several contexts (a `system`-scope arch spec, an initiative) identifies each one.
3. Read the glossary file of each identified context in full.
4. **Ambiguous context** — if two or more contexts plausibly fit, ask the user which one via `AskUserQuestion`, recommending (`➡️`) the context whose Owns covers the central concept. Never pick silently.

Done when the context (or contexts) is known and its glossary is in context, or it is established that no glossary exists.

## §2 Interview Checks

Apply to the words used so far — the user's description and answers — counting only domain concepts specific to this project, never general programming vocabulary.

**Against the glossary** (when one exists), flag immediately, quoting the glossary entry:
- **Avoided word** — a word listed under a term's `_Avoid_`.
- **Different meaning** — a defined term used with another meaning.
- **New term** — a domain concept the glossary doesn't define.

**Whether or not a glossary exists:**
- **Overloaded word** — one word used for more than one thing ("account" for the buyer and for the login). Propose splitting it into distinct terms; never fold two concepts into one term.
- **Vague word** — a word too fuzzy to define in one sentence ("item", "record", "data"). Propose a precise canonical term.
- **Contradiction with code** — the user describes a concept differently from how the code models it. Surface it; don't pick a side.

**Resolve** avoided words, different meanings, overloaded words, and code contradictions through `AskUserQuestion`, each with a recommended answer (`➡️`) taken from the glossary first, then the code's naming.

**Terms handed in from code.** When the input contains a `DOMAIN TERMS` block (the handoff brief of `pragmatic-reverse-engineer`), it is the starting set of drafts — don't re-derive them:
- **CONFIRMED** — stated, not asked.
- **NEW** — already a draft; add its boundary scenario and carry it to the recap. Every NEW term goes to the recap, whatever interview depth the caller runs: these were found in the code, not invented.
- **Several code names for one concept** — the canonical term is a decision (the business word may differ from every identifier); recommend (`➡️`) the name the user's domain uses. The `_In code_` defaults to the **dominant identifier in the code**, so the glossary describes the code that exists. The other identifiers go under `_Avoid_` only as words; actually renaming them in code is a separate decision — record each as a **pending rename** for the caller's summary, never as a silent change.
- **DIVERGENCE** — resolve through `AskUserQuestion`: change the glossary's `_In code_` to match the code (➡️ when the code name is used consistently), or keep the glossary and record a pending rename in the code.

**Draft new terms yourself** — don't ask one question per term. A draft has: canonical term, one-sentence definition of what it *is*, `_Avoid_` synonyms heard so far, `_In code_` if the code already names it, and the context it belongs to.

**Boundary scenario** — next to each new or disputed term, give one concrete edge case and say which side the draft puts it on ("cancelling 1 of 3 items in an Order: is that a **Cancellation**? The draft says no — Cancellation ends the whole Order"). Pick the case two readers would most likely decide differently. If the user moves the case, the definition changes, not the scenario.

Drafts are confirmed in the caller's recap, not here. From this point on, use the confirmed canonical terms in every question and in the document.

Done when every flagged word is resolved and every new or disputed term has a draft and a boundary scenario.

## §3 Write the Glossary

Write only what the caller's recap (or the Direct Edit confirmation) confirmed. Formats per `references/`.

- **No `docs/glossary/` yet** — create the folder, `context-map.md`, and the context file together. Name the first context per `references/context-map-template.md` (an arch spec module, else the constitution's product name, else ask — never `default` or `main`).
- **New context** — confirm it with the user first, then add its file and its map row (Arch spec column `—` until one exists).
- **Existing term redefined** — edit it in place; never keep two definitions.
- **Rename** — the old name moves into the new term's `_Avoid_`; if it was a real confusion, record it under `## Resolved Ambiguities`, linking the document where it was decided.
- **Owns, Relationships, Translations** — edit the map rows to match what was confirmed. A renamed context renames its row and file; its Arch spec link follows.
- **Other documents** — never edit another spec or arch spec from here. Search `docs/specs/` and `docs/arch/` for every old or avoided name and report each file that still uses it; it needs its own `pragmatic-spec-update` / `pragmatic-arch-spec-update`.

Done when the glossary files reflect exactly what was confirmed and the list of documents still using old names is ready for the caller's summary.

## §4 Validation Checks

Report **WARN at most, never FAIL** — a young glossary produces false positives, and a wording finding must not block a document. Quote the glossary or map entry in each note. If `docs/glossary/` does not exist, the checks don't apply (the caller reports them as N/A or INFO, per its own format).

Base checks — every validator:
1. **No avoided terms** — no word listed under a term's `_Avoid_` is used in the document to mean that term. A word used for an unrelated concept is not a finding.
2. **Domain terms defined** — the domain concepts the document relies on (a spec's goals and criteria; an arch spec's components, events, flows) are defined in the context's glossary.
3. **Context map consistent** — every `docs/glossary/*.md` other than the map is listed in its Contexts table; every Glossary and Arch spec link resolves; no term is defined in two context files without a Translations row; every path in a Code column exists.
4. **Glossary hygiene** — in the context files the document touches, each entry follows `references/glossary-template.md`. WARN for: a definition longer than two sentences or describing behavior instead of what the concept is; implementation detail (table or column names, endpoints, field lists, types); a general programming concept (timeout, retry, DTO, cache); a missing definition; two terms sharing an `_In code_` identifier; a word under one term's `_Avoid_` that is another term's canonical name. A word under `_Avoid_` that matches the same term's own `_In code_` is not a finding (see §5).

Architecture checks — arch spec validators add:
5. **Context registered** — for a `module` scope, the map has a row for this module whose Arch spec link points at this file.
6. **Ownership consistent** — the map's Owns for this context agrees with the component boundaries, and does not contradict a Cross-Module Rule in the constitution.
7. **Communication matches the map** — wherever the arch spec has two contexts communicating, the map's Relationships row for that pair records the same mechanism; a pair communicating with no row is a finding too.

The fix for any of these is the matching update skill, which applies §3: `pragmatic-spec-update` or `pragmatic-arch-spec-update`.

## §5 Names in Code

For anything that writes or checks code, tests, or text about it:

- A type, function, event, test, or endpoint for a glossary concept uses the term's code identifier — `_In code_`, or the term itself when there is none — never a word under its `_Avoid_`.
- **`_In code_` wins over `_Avoid_`.** When a term's `_In code_` is `Account` while "account" is listed under `_Avoid_` (the business says Customer, the code says Account), using `Account` in code is correct — `_Avoid_` governs prose and new names, not the identifier the glossary itself records.
- **A concept missing from the glossary is a signal.** First check whether an existing term already covers it; most of the time one does, and inventing a name is the mistake. Only if none fits, name it consistently with the existing identifiers and record it as a **glossary gap** — never add it to the glossary from a build or a check.
- Conformance checks scan only their own scope. A different name or an avoided word in an interface or a test name is a warning; a concept the code doesn't represent at all is not a naming finding.

## §6 Scan Code

Used by Sync from Code and by `pragmatic-reverse-engineer`'s Domain Vocabulary pass. It proposes terms; it never writes the glossary and never renames code.

1. **Collect candidate concepts** from what the code names: domain types and entities, table and collection names, enum values that name states, route nouns, event and message names. A candidate is a domain concept when it is persisted, crosses a boundary (an endpoint, an event), names a state, or is a type other types are built around. Ignore general programming constructs: handlers, DTOs, configs, clients, utilities, mocks, and test helpers.
2. **Group synonyms** — the same concept under several names across the code (`Account`, `Customer`, `Client` all pointing at the same table) is one candidate with several names. Pick the **dominant** one (most uses) as the proposed `_In code_`, and list the others with their use counts as **rename candidates**. Propose the canonical term separately — it may be a business word none of the identifiers uses; the caller asks.
3. **Compare with the glossary** (locate the context per §1, judge names per §5):
   - the code uses the term's `_In code_` identifier → **CONFIRMED**
   - the code names a defined concept differently, or uses a word under its `_Avoid_` → **DIVERGENCE** (cite file:line, the code name, the glossary identifier)
   - a concept the glossary doesn't define → **NEW**, with an **INFERRED** one-sentence definition drawn from how the code uses it
4. **Contexts** (architecture targets only) — propose which context each component belongs to (or a new context, named after the module) and what it appears to own: the concepts it persists.

Done when every candidate is CONFIRMED, DIVERGENCE, or NEW, or was filtered out as non-domain.

---

## Direct Edit

Run this only when the user invoked this skill to change the domain language itself.

1. **Locate** — apply §1.
2. **Understand the change** — add, rename, or redefine a term; add or rename a context; change Owns; add a Relationship or Translation.
3. **Check it** — apply §2 to the requested change: draft the new or changed entries, each with a boundary scenario. For an Owns change, read `docs/constitution.md` if it exists — an ownership that contradicts a Cross-Module Rule needs `pragmatic-project-constitution-update` first; flag it and stop there.
4. **Confirm** — present the drafts and every map row that changes, plus the documents in `docs/specs/` and `docs/arch/` that use an affected name. **STOP until the user confirms.**
5. **Write** — apply §3.
6. **Summarize** — the files changed, the terms and rows added or changed, and every spec or arch spec that still uses an old name, with the update skill each one needs. A glossary change does not rewrite the documents that use it.

---

## Sync from Code

Run this only when the user invoked this skill to reconcile the glossary with the code. It never edits code, specs, or arch specs, and it never writes without confirmation. The code can tell you **facts** — an identifier is gone, a type appeared, a word you avoid is in use — not the business word or the definition, which stay the user's decisions.

1. **Locate** — apply §1 to every context in the map, or only the one named with `--context`. For a context whose Code column is empty or `—`, ask once through `AskUserQuestion` for its paths, ➡️ the directories whose names match the context name or its Owns terms (list the project's directories to find them), or skip that context. Answers are written to the Code column in step 5.
2. **Detect** — run `scripts/glossary-drift.sh --root . [--context <name>]` from the project root when `bash` is available. Otherwise do the same search yourself with Grep: every `_In code_` identifier no longer in the Code paths (STALE), and every `_Avoid_` word used as an identifier (AVOIDED), skipping a term's own `_In code_` identifier (§5). The match is textual — a comment can hide a STALE or raise an AVOIDED — so treat each finding as a question.
   Then read `Last synced` in the map. If it names a commit that exists in this repository, run §6 only on files changed since it (`git diff --name-only <sha>..HEAD -- <paths>`) and, for each STALE identifier, look for its successor (`git log -S'<old>' --oneline -- <paths>`, and renames in that diff). If the marker is missing or unknown, run §6 on the whole Code paths and say so.
3. **Classify** the results into groups, skipping empty ones:
   - **Gone** (STALE) — propose per item: renamed (the new `_In code_`), moved to another context (move the entry), or removed from the code (keep the term and ask whether to retire it; nothing is deleted without the user).
   - **Avoided word in code** (AVOIDED) — default: a **pending rename**, code untouched. Alternative when the code name is used consistently: change the term's `_In code_` to it (§6 dominant identifier).
   - **New** (§6 NEW) — draft each as in §2: canonical term, one-sentence definition, `_Avoid_`, `_In code_`, and a boundary scenario.
   - **Not checked in this version:** Owns and Relationships. Say so in the report — do not guess them from the code.
4. **Confirm** — one `AskUserQuestion` round per group, items numbered, each with a recommended answer (`➡️`). List the specs and arch specs that use any affected name. Every item accepts both directions: *the code is right* → the glossary changes; *the glossary is right* → record a pending rename and leave the glossary alone. **STOP until the user confirms.** If nothing drifted, say so and ask only whether to move the `Last synced` marker.
5. **Write** — apply §3 for each accepted glossary change. Write the Code column paths from step 1. Set `**Last synced:** \`<HEAD short sha>\` (<today>)` under the map's title (add the line if absent) — also when nothing drifted, and only after confirmation. The marker limits the next scan of *new* code; pending renames and avoided words are found again every run, because the script checks them on the whole Code paths.
6. **Summarize** — files changed; items by outcome (updated, pending rename, ignored); every pending rename with its file:line and use count; the specs and arch specs still using an old name, each with the update skill it needs (§3); and what was not checked.
