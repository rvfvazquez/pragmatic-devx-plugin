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

Targets attempted but not produced (the downstream skill ended without
writing a file — e.g. the existing-file guard was declined, or the user
chose to create a constitution first) are listed here too, with a status
explaining why.

| Document | Path | Version at generation | Status |
|----------|------|--------------------------|--------|
| ... | `docs/specs/...` or `docs/arch/...` | ... | Produced |
| ... | — | — | Not produced — `<reason>` |

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

## 7. Security Observations

SECURITY-GAP findings from the scan (see
`references/discovery-heuristics.md`) and what the user decided about each.
Never include a secret value here — file and line only.

| Location | Pattern | User's decision |
|----------|---------|------------------|
| `file:line` | missing ownership check / hardcoded secret / ... | intentional — documented in §8 / defect — `[TODO]` recorded / to fix separately |

*(If the scan found nothing: "No security gaps observed in the scanned
scope.")*

## 8. Domain Vocabulary

What the Domain Vocabulary pass (see `references/discovery-heuristics.md`)
found, and what the downstream skills wrote to `docs/glossary/`.

**Glossary changes**

| Context | Term | `_In code_` | Origin | File |
|---------|------|-------------|--------|------|
| ... | ... | `...` | CONFIRMED / NEW (confirmed) / NEW (corrected) | `docs/glossary/<context>.md` |

**New contexts and ownership** *(architecture targets only — omit
otherwise)*

| Context | Owns | Arch spec |
|---------|------|-----------|
| ... | ... | `docs/arch/<name>.arch.md` |

**Pending renames and divergences** — code names left as they are, with
the user's decision for each:

| Location | Code name | Glossary term | Decision |
|----------|-----------|---------------|----------|
| `file:line` (N uses) | `Client` | Customer (`_In code_: Account`) | rename later / keep — glossary updated / keep for now |

*(If nothing was found: "No domain concepts found in the scanned scope." If
every name matched: "No divergences — the glossary matches the code.")*
