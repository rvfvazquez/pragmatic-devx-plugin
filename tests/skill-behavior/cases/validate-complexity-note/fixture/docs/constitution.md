# Project Constitution

## 1. Project Identity
Internal reporting platform. Single tenant.

## 2. Global Tech Stack

| Decision | Value | Rationale |
|---|---|---|
| Language | Python 3.12 | Team standard |
| Database | PostgreSQL | Existing operations tooling |

## 3. Security Baseline

| Decision | Value | Rationale |
|---|---|---|
| Authentication | OIDC, tokens validated at the API gateway only | Single identity provider |
| Authorization | Per-resource ownership check in the service layer | Least privilege |

## 4. Cross-Module Rules
— none defined yet —

## 5. AI Behavior Guardrails
- Never add a dependency without a recorded decision.

## Changelog
| Date | Change | Reason |
|---|---|---|
| 2026-01-10 | Initial constitution created | — |
