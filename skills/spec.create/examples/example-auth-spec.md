# Example Spec: JWT Authentication

> This is a complete example of a spec produced by spec.create.
> Use it as a reference for output structure, level of detail, and writing style.

---

## 1. Overview

- **Title**: JWT Authentication for REST API
- **Status**: Review
- **Author**: backend-team
- **Created**: 2026-02-10
- **Version**: 1.0.0

## 2. Problem Statement

The API currently has no authentication mechanism. All endpoints are publicly accessible, which is a security risk as the product moves toward production. Users need a way to authenticate and receive a token that authorizes subsequent requests.

## 3. Goals & Non-Goals

**Goals:**
- Allow users to authenticate with email and password and receive a JWT access token
- Protect existing API endpoints so only authenticated requests are accepted
- Support token expiry and rejection of expired tokens

**Non-Goals:**
- OAuth2 / social login (out of scope for this iteration)
- Refresh token rotation (deferred — will be addressed in a follow-up spec)
- Role-based access control (RBAC) — authorization is out of scope; only authentication is covered here

## 4. Proposed Solution

Introduce a `POST /auth/login` endpoint that accepts credentials, validates them against the users table, and returns a signed JWT. A middleware will validate the `Authorization: Bearer <token>` header on all protected routes and reject requests with missing or invalid tokens.

## 5. Technology Decisions

| Concern | Decision | Alternatives Considered | Rationale |
|---------|----------|------------------------|-----------|
| Token format | JWT (HS256) | Opaque tokens, PASETO | Team familiarity; stateless — no session storage required |
| Token signing | Symmetric key (HMAC-SHA256) | RSA asymmetric | Single-service deployment; asymmetric adds complexity with no benefit here |
| Token storage | Client-side (Authorization header) | Cookie-based session | REST convention; avoids CSRF complexity |
| Token expiry | 24h access token | 1h, 7d | Balance between security and UX for internal tooling |
| Data store | PostgreSQL (existing `users` table) | Separate auth DB | Already in use; avoids new infrastructure |
| Password hashing | bcrypt (cost factor 12) | argon2, scrypt | Already used in user registration flow |
| Infrastructure | Existing ECS Fargate service | Lambda | No cold-start sensitivity; already deployed |

## 6. Detailed Design

### 6.1 API / Interface

```go
// AuthService defines the authentication contract
type AuthService interface {
    Login(ctx context.Context, req LoginRequest) (LoginResponse, error)
    ValidateToken(ctx context.Context, token string) (Claims, error)
}

type LoginRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Password string `json:"password" validate:"required,min=8"`
}

type LoginResponse struct {
    AccessToken string    `json:"access_token"`
    ExpiresAt   time.Time `json:"expires_at"`
}

type Claims struct {
    UserID string `json:"user_id"`
    Email  string `json:"email"`
    jwt.RegisteredClaims
}
```

**Endpoint:**
```
POST /auth/login
Content-Type: application/json

Body: { "email": "user@example.com", "password": "secret123" }

200 OK:  { "access_token": "<jwt>", "expires_at": "2026-02-11T10:00:00Z" }
401:     { "error": "invalid_credentials" }
400:     { "error": "validation_error", "details": [...] }
```

### 6.2 Data Model

No new tables. Uses existing `users` table:

```go
type User struct {
    ID           string    `db:"id"`
    Email        string    `db:"email"`
    PasswordHash string    `db:"password_hash"`
    CreatedAt    time.Time `db:"created_at"`
}
```

### 6.3 Behavior & Logic

1. Client sends `POST /auth/login` with email and password
2. Handler validates request body (400 if invalid)
3. `AuthService.Login` queries the `users` table by email (404-safe: return `invalid_credentials` regardless of whether user exists, to avoid email enumeration)
4. Compare submitted password against `password_hash` using bcrypt
5. On match: generate JWT with `user_id`, `email`, `iat`, `exp` (24h), signed with `AUTH_JWT_SECRET`
6. Return `LoginResponse`
7. Auth middleware on protected routes: extract `Authorization: Bearer <token>`, call `AuthService.ValidateToken`, inject `Claims` into request context; return 401 on failure

## 7. Acceptance Criteria

- [ ] `POST /auth/login` with valid credentials returns 200 with a signed JWT
- [ ] `POST /auth/login` with invalid password returns 401 with `invalid_credentials`
- [ ] `POST /auth/login` with non-existent email returns 401 (not 404 — no email enumeration)
- [ ] JWT is signed with HS256 and expires in 24 hours
- [ ] Protected endpoints return 401 when no `Authorization` header is present
- [ ] Protected endpoints return 401 when token is expired or signature is invalid
- [ ] Valid token grants access to protected endpoints and injects user context
- [ ] `AUTH_JWT_SECRET` is read from environment variable, never hardcoded

## 8. Technical Considerations

- **Security**: Never log passwords or token secrets. Return generic error messages on auth failure to prevent enumeration.
- **Performance**: bcrypt at cost 12 takes ~200ms on current hardware — acceptable for a login endpoint (not called at high frequency).
- **Dependencies**: Requires `github.com/golang-jwt/jwt/v5` and `golang.org/x/crypto/bcrypt` — both already in `go.mod`.
- **Breaking changes**: None — new endpoint and middleware; existing unauthenticated behavior unchanged until middleware is applied to routes.
- **Environment**: `AUTH_JWT_SECRET` must be added to ECS task definition secrets.

## 9. Open Questions

- [ ] [TODO: decide — should the middleware apply to all routes by default (opt-out) or only explicitly marked routes (opt-in)?]
- [ ] [TODO: decide — should failed login attempts be rate-limited? If yes, define threshold and cooldown period]
