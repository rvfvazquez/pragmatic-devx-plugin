# spec.check — Report Format Reference

This file defines the canonical format for a `spec.check` conformance report with inline annotations explaining each field. Annotations use `>` blockquotes and must not appear in the actual report output.

---

## Spec Conformance Report

> Header block: always present. "Overall Status" is derived from the three dimension statuses
> using the aggregation rules defined in SKILL.md — do not set it manually before filling in dimensions.

**Spec:** `docs/specs/<feature-slug>.md`
**Implementation:** `<directory scanned, e.g. internal/auth/>`
**Date:** `<today's date>`
**Overall Status:** `PASS | WARN | FAIL`

> Overall Status aggregation:
> - FAIL if any evaluated dimension is FAIL
> - WARN if any evaluated dimension is WARN and none are FAIL
> - PASS if all evaluated dimensions are PASS or N/A

---

### Summary

> Count each row across all dimensions. N/A rows are reported separately and NOT included
> in the Passed / Warnings / Failed counts.

- Passed:   X checks
- Warnings: X checks
- Failed:   X checks
- N/A:      X checks (not counted in totals above)

---

### Dimension 1 — Acceptance Criteria Coverage

> This dimension maps each item from section 7 of the spec to test evidence in the codebase.
> It is NEVER N/A — every spec must have at least some verifiable criteria.

**Status:** `PASS | WARN | FAIL`

> Per-dimension status aggregation:
> - FAIL if any row is FAIL
> - WARN if any row is WARN and none are FAIL
> - PASS if all rows are PASS

| Criterion | Status | Finding |
|-----------|--------|---------|
| `<verbatim criterion from spec section 7>` | PASS | `handler_test.go:42` — covers happy path |
| `<criterion>` | WARN | Only indirectly covered via `integration_test.go:88` — no dedicated test case |
| `<criterion>` | FAIL | No test found in codebase |

> Row-level status values: PASS, WARN, FAIL
> Finding column: always populate. For PASS, cite the file and line. For WARN/FAIL, explain what
> is missing or why coverage is indirect. Never leave Finding empty.

---

### Dimension 2 — Structural Adherence

> This dimension verifies that interfaces, structs, type definitions, and endpoints defined in
> spec sections 6.1 and 6.2 exist in the code with the expected signatures.
>
> Mark dimension as N/A when sections 6.1 and 6.2 are absent or contain no verifiable elements.

**Status:** `PASS | WARN | FAIL | N/A`

> N/A when sections 6.1 and 6.2 are absent or contain no verifiable elements.

| Element | Status | Finding |
|---------|--------|---------|
| `AuthService.Login` interface | PASS | `service.go:12` — signature matches spec |
| `LoginRequest.Password` validation | WARN | Field present in `types.go:34` but missing `validate:"min=8"` tag — spec requires it |
| `POST /auth/login` endpoint | FAIL | Route not registered in `routes.go` |

> For WARN rows: always specify what deviates and what the spec expects.
> For FAIL rows: confirm the element truly doesn't exist (search exhaustively before marking FAIL).

---

### Dimension 3 — Open Items Resolved

> This dimension checks whether open [TODO: ...] items in the spec have been addressed
> in the current codebase.
>
> Mark dimension as N/A when the spec has no open [TODO: ...] items.

**Status:** `PASS | WARN | FAIL | N/A`

> N/A when the spec has no open [TODO: ...] items.

| TODO | Status | Finding |
|------|--------|---------|
| `[TODO: decide — should middleware be opt-in or opt-out?]` | PASS | `middleware.go:8` — opt-in pattern implemented via `RequireAuth()` decorator |
| `[TODO: decide — should failed logins be rate-limited?]` | WARN | No rate limiting found; may be intentional out-of-scope — confirm with team |
| `[TODO: decide — token storage location]` | FAIL | No decision found in source files or config |

> PASS: clear evidence of resolution exists in source files or config.
> WARN: absence may be intentional (explicitly out of scope, deferred) — flag for human confirmation.
> FAIL: no evidence of the decision being made or implemented.

---

### Recommended Actions

> List only when Overall Status is WARN or FAIL.
> Order: all FAILs first, then WARNs.
> Each action is tagged with:
>   [code]        → the fix belongs in the implementation
>   [spec.update] → a decision or clarification is needed in the spec document
>
> If Overall Status is PASS: replace this section with a "Strengths" section summarizing
> what was verified and confirmed correct.

1. `[FAIL][code]` Add a dedicated test for token expiry — criterion "JWT expirado retorna 401" has no test coverage
2. `[FAIL][spec.update]` Token storage TODO has no decision — use `spec.update` to record the chosen approach
3. `[WARN][code]` Add `validate:"min=8"` to `LoginRequest.Password` or explicitly remove the constraint from the spec
4. `[WARN][spec.update]` Confirm whether rate limiting is intentionally out of scope — if yes, close the TODO via `spec.update`
