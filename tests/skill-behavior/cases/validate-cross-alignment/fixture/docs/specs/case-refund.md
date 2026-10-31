# Case refund request
Status: Review
Language: English
Version: 1.0.0

## 2. Problem
Support agents cannot request a refund for a customer case from the support module.

## 3. Goals & Non-Goals
**Goals:**
- An agent can request a refund for a case they own.

**Non-Goals:**
- Issuing the refund payment itself.

## 4. Proposed Solution
The support module records a refund request, reads the case's invoice total, and tells the customer.

## 5. Technology Decisions

| Concern | Decision | Alternatives Considered | Rationale |
|---|---|---|---|
| Data storage | MongoDB collection `refund_requests` | PostgreSQL | Team likes document stores |
| Invoice total | Call billing's `InvoiceRepository.get_total()` directly | Domain event | Simpler |
| Customer notice | Synchronous call to the notifications module | Domain event | Deviation from arch spec 6.3: the event bus is unavailable until Q3; approved by the architecture owner; revisit when the bus ships |
| Test seam | HTTP POST /cases/{id}/refund-request, storage via fake adapter | Service layer | Public boundary maps to criteria |

## 6. Technical Design
### 6.1 Interfaces
POST /cases/{id}/refund-request returns 201 with the request id, 403 for a non-owner.
### 6.2 Invariants
| Invariant | Verified by |
|---|---|
| Only the case owner can request a refund | AC-2 |
### 6.3 Behavior
Check ownership, read the invoice total, store the request, notify the customer.

## 7. Acceptance Criteria
- AC-1: Given a case owned by the agent, when the agent posts a refund request, then the response is 201 with a request id.
- AC-2: Given a case owned by another agent, when the agent posts a refund request, then the response is 403 and nothing is stored.

## 8. Dependencies and Security
Dependencies: billing and notifications modules.
Security:
- Authentication: the service issues its own session cookie at login.
- Authorization: ownership check against the case owner before any read.
- Untrusted input: request body validated against a schema.
- Sensitive data: customer fields never logged.
- Abuse case: an agent flooding refund requests; rate limit per agent.

## 9. Open Questions
None.
