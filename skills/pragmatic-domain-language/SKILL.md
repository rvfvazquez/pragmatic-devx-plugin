---
name: pragmatic-domain-language
description: This skill should be used when the user asks to "add a term to the glossary", "rename a domain term", "redefine what X means", "update the glossary", "update the context map", "add a bounded context", "record who owns X", or wants to change the project's domain language in docs/glossary/ directly, outside of writing a spec. Also loaded by the other pragmatic skills for the shared glossary and context-map procedures they apply.
---

# pragmatic-domain-language

The project's domain language — what each concept is called, what it means, which context owns it, and how contexts relate — kept in `docs/glossary/`. This skill is the single source for how that language is read, challenged, written, validated, and used.

## Two Ways This Skill Is Used

**Loaded by another pragmatic skill.** The calling skill names a section below (e.g. "apply §2 Interview Checks"). Apply **only that section**, within the caller's own step, then continue with the caller's next step. Do not run the Direct Edit flow, do not ask the questions in it, and do not end the caller's skill. The caller's own gates (recaps, STOPs, confirmations) still govern when anything is written.

**Invoked directly** — the user wants to change the domain language itself, outside of writing or updating a spec: add, rename, or redefine a term, add a context, record ownership, add a relationship or translation. Run the **Direct Edit** flow at the end of this file.

## Files

```
docs/glossary/
├── context-map.md        ← always present when the folder exists; the single entry point
└── <context-slug>.md     ← one per bounded context
```

Formats and content rules: `references/glossary-template.md` (a context's terms) and `references/context-map-template.md` (contexts, Owns, Relationships, Translations).

---

## §1 Locate the Context

1. If `docs/glossary/context-map.md` does not exist, there is no glossary yet — say so and continue; §2 treats every central concept as new.
2. Read the map. Identify the context the work belongs to by the map's **Purpose** and **Owns** columns, or by the linked arch spec. Work spanning several contexts (a `system`-scope arch spec, an initiative) identifies each one.
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
3. **Context map consistent** — every `docs/glossary/*.md` other than the map is listed in its Contexts table; every Glossary and Arch spec link resolves; no term is defined in two context files without a Translations row.
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

---

## Direct Edit

Run this only when the user invoked this skill to change the domain language itself.

1. **Locate** — apply §1.
2. **Understand the change** — add, rename, or redefine a term; add or rename a context; change Owns; add a Relationship or Translation.
3. **Check it** — apply §2 to the requested change: draft the new or changed entries, each with a boundary scenario. For an Owns change, read `docs/constitution.md` if it exists — an ownership that contradicts a Cross-Module Rule needs `pragmatic-project-constitution-update` first; flag it and stop there.
4. **Confirm** — present the drafts and every map row that changes, plus the documents in `docs/specs/` and `docs/arch/` that use an affected name. **STOP until the user confirms.**
5. **Write** — apply §3.
6. **Summarize** — the files changed, the terms and rows added or changed, and every spec or arch spec that still uses an old name, with the update skill each one needs. A glossary change does not rewrite the documents that use it.
