# Support Platform Architecture
Status: Approved

## 4. High-Level Design
### 4.2 Component Boundaries
| Component | Responsibility | Public Interface | Trust level |
|---|---|---|---|
| support | Customer cases | HTTP API, domain events | trusted core |
| billing | Invoices and payments | domain events | trusted core |
| notifications | Outbound messages | domain events | trusted core |

## 6. Architecture Patterns & Conventions
### 6.2 Dependency Direction
support may depend on shared kernel only. support must not import billing.
### 6.3 Communication Style
Cross-module communication is asynchronous through domain events. Direct synchronous calls between modules are forbidden.

## 8. External Integrations & Dependencies
| Dependency | Type | Purpose | Owned by |
|---|---|---|---|
| PostgreSQL | Infrastructure | Primary data store | Platform team |
