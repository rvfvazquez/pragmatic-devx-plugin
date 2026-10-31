# Project Constitution

## 1. Project Identity
Internal support platform. Single tenant.

## 2. Global Tech Stack

| Decision | Value | Rationale |
|---|---|---|
| Language | Python 3.12 | Team standard |
| Database | PostgreSQL | Relational model, existing operations tooling |

## 3. Security Baseline

| Decision | Value | Rationale |
|---|---|---|
| Authentication | OIDC, tokens validated at the API gateway only | Single identity provider |
| Authorization | Per-resource ownership check in the service layer | Least privilege |
| Secrets management | Injected environment only | No secrets in source |
| Data classification | Customer PII never written to logs | Compliance |

## 4. Cross-Module Rules
- A module never imports another module's repository or data layer.

## 5. AI Behavior Guardrails
- Never add a dependency without a recorded decision.

## Changelog
| Date | Change | Reason |
|---|---|---|
| 2026-01-10 | Initial constitution created | — |
