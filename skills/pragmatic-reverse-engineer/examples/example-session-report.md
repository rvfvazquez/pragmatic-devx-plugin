# Example Session Report: Repo-Wide Feature Discovery

> This is a complete example of a session report produced by
> pragmatic-reverse-engineer, following `references/report-template.md`.
> Use it as a reference for output structure, level of detail, and writing
> style. The two documents it references (`docs/specs/payments.md`,
> `docs/specs/notifications.md`) are written by `pragmatic-spec-create`, not
> by this skill — see `pragmatic-spec-create/examples/` for that output's
> shape.

---

## 1. Session Overview

- **Session slug**: `repo-wide`
- **Date**: 2026-08-15
- **Branch**: Feature
- **Requested by**: (inferred from git config) rvf.vazquez

> This is a point-in-time snapshot of a reverse-engineering session run on
> 2026-08-15. It reflects the state of the code at that time and is **not
> updated** when the documents it produced are later changed — see each
> document's own Provenance section and changelog for current state.

## 2. Targets Scanned

| Target | Path | Scope type (arch only) |
|--------|------|--------------------------|
| Payments | `src/payments/` | — |
| Notifications | `src/notifications/` | — |

## 3. Candidates Considered But Not Selected

| Candidate | Why it looked like a feature boundary | Already had a spec? |
|-----------|-----------------------------------------|------------------------|
| Rate limiting | Dedicated `src/ratelimit/` package with its own tests and a distinct config block | No |
| Admin audit log | `src/audit/` writes structured events on every mutating admin action | No |

## 4. Documents Produced

| Document | Path | Version at generation | Status |
|----------|------|--------------------------|--------|
| Payments spec | `docs/specs/payments.md` | 1.0.0 | Produced |
| Notifications spec | `docs/specs/notifications.md` | — | Not produced — user declined the existing-file guard prompt after `pragmatic-spec-create` found `docs/specs/notifications-draft.md` already covering part of this scope |

## 5. Confidence Summary

| Document | Confirmed from code | Inferred & user-confirmed | Still open (`[TODO: ...]`) |
|----------|------------------------|-------------------------------|--------------------------------|
| Payments spec | 11 | 3 | 1 |

## 6. Corrections Made During Confirmation

| Document | Inferred | Corrected to |
|----------|----------|----------------|
| Payments spec | Retry logic exists to handle provider timeouts | Retry logic exists to handle provider *rate limiting* specifically (429 responses only — confirmed by the caller reading the `Retry-After` header) |

---

**Session summary presented to the user:**

> **Reverse engineering complete.**
>
> - `docs/specs/payments.md` — produced, Provenance appended (11 confirmed, 3 inferred-confirmed, 1 still open)
> - Notifications — not produced this session; `docs/specs/notifications-draft.md` already exists and covers part of this scope. Run `pragmatic-spec-update` on that file instead, or re-run this skill once the overlap is resolved.
>
> Also found but not selected: **Rate limiting** and **Admin audit log** — both look like undocumented feature boundaries if you want to reverse-engineer them next.
>
> **Next step:** Run `pragmatic-spec-validate` on `docs/specs/payments.md` before treating it as a source of truth — reverse-engineered content still needs the same quality gate as any other spec.
