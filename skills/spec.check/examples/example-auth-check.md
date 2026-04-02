# Example: Conformance Check — JWT Authentication

> This is a worked example of a `spec.check` report.
> Spec source: `skills/spec.create/examples/example-auth-spec.md`
> Hypothetical implementation: `internal/auth/`
>
> The example is intentionally crafted to demonstrate PASS, WARN, and FAIL across all three
> dimensions. It is not based on a real codebase — use it to calibrate output structure,
> finding detail level, and action tag usage.

---

## Spec Conformance Report
**Spec:** `docs/specs/auth.md`
**Implementation:** `internal/auth/`
**Date:** 2026-04-01
**Overall Status:** WARN

### Summary
- Passed:   9 checks
- Warnings: 4 checks
- Failed:   1 check
- N/A:      0 checks

---

### Dimension 1 — Acceptance Criteria Coverage
**Status:** WARN

| Criterion | Status | Finding |
|-----------|--------|---------|
| `POST /auth/login` with valid credentials returns 200 with signed JWT | PASS | `handler_test.go:42` — happy path covered |
| `POST /auth/login` with invalid password returns 401 with `invalid_credentials` | PASS | `handler_test.go:67` — covers invalid password case |
| `POST /auth/login` with non-existent email returns 401 (not 404) | WARN | Only indirectly covered via `handler_test.go:88` — no assertion that status is specifically 401 and not 404 |
| JWT is signed with HS256 and expires in 24 hours | PASS | `token_test.go:15` — asserts algorithm and expiry |
| Protected endpoints return 401 when no `Authorization` header is present | PASS | `middleware_test.go:23` — missing header case covered |
| Protected endpoints return 401 when token is expired or signature is invalid | WARN | `middleware_test.go:31` covers invalid signature but no test for expired token |
| Valid token grants access and injects user context | PASS | `middleware_test.go:45` — context injection asserted |
| `AUTH_JWT_SECRET` is read from environment variable, never hardcoded | PASS | `config_test.go:8` — asserts env var is used; grep confirms no hardcoded secret in source |

---

### Dimension 2 — Structural Adherence
**Status:** WARN

| Element | Status | Finding |
|---------|--------|---------|
| `AuthService` interface with `Login` method | PASS | `service.go:12` — signature matches spec exactly |
| `AuthService` interface with `ValidateToken` method | PASS | `service.go:18` — signature matches spec exactly |
| `LoginRequest` struct with `email` and `password` fields | WARN | `types.go:34` — fields present but `password` is missing `validate:"min=8"` tag; spec section 6.1 requires it |
| `LoginResponse` struct with `access_token` and `expires_at` | PASS | `types.go:41` — matches spec |
| `Claims` struct embedding `jwt.RegisteredClaims` | PASS | `types.go:48` — matches spec |
| `POST /auth/login` endpoint registered | PASS | `routes.go:22` — route registered with correct method and path |

---

### Dimension 3 — Open Items Resolved
**Status:** FAIL

| TODO | Status | Finding |
|------|--------|---------|
| `[TODO: decide — should middleware apply opt-in or opt-out?]` | FAIL | No decision found in source files or config; middleware.go uses a blanket apply-to-all approach with no documented decision |
| `[TODO: decide — should failed login attempts be rate-limited?]` | WARN | No rate limiting implemented; absence may be intentional (out of scope for this iteration) — confirm with team before closing |

---

### Recommended Actions

1. `[FAIL][spec.update]` The middleware opt-in/opt-out decision was never formally made — use `spec.update` to record the decision (current code applies middleware to all routes) and close the TODO
2. `[WARN][code]` Add a dedicated test for expired token returning 401 — indirect coverage in `middleware_test.go` is insufficient for a security-critical criterion
3. `[WARN][code]` Add `validate:"min=8"` to `LoginRequest.Password.validate` tag in `types.go:34`, or explicitly remove the constraint from spec section 6.1 if it was intentionally dropped
4. `[WARN][spec.update]` Confirm whether rate limiting is explicitly out of scope — if yes, close the TODO via `spec.update`; if deferred, create a follow-up spec
