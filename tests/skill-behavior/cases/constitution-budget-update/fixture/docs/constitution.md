# Project Constitution
**Project:** Reporting platform
**Status:** Active
**Language:** English
**Last Updated:** 2026-01-10

---

## 1. Project Identity

Internal reporting tool for analysts. Single tenant. No compliance requirements.

---

## 2. Global Tech Stack

Non-negotiable technology decisions that apply to every module.

| Decision | Value | Rationale |
|---|---|---|
| Language | Python 3.12 | Team standard |
| Database | PostgreSQL | Existing operations tooling |

---

## 3. Security Baseline

| Decision | Value | Rationale |
|---|---|---|
| Authentication | OIDC validated at the gateway | Single identity provider |
| Authorization | Per-resource ownership check | Least privilege |
| Secrets management | Injected environment only | No secrets in source |
| Data classification | PII never in logs | Compliance hygiene |
| Security baseline reference | OWASP Top 10 | Shared minimum |

---

## 4. Cross-Module Rules

— none defined yet —

---

## 5. AI Behavior Guardrails

- **New dependency:** stop and ask before adding a third-party dependency.

---

## Changelog

| Date | Change | Reason |
|---|---|---|
| 2026-01-10 | Initial constitution created | — |
