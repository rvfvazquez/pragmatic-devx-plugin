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
