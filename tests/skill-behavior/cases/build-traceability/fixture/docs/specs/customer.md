# Customer lookup
Status: Approved
Language: English

## 2. Problem
Support staff must retrieve customer records.
## 3. Scope
Customer lookup only. Sending promotional emails is explicitly out of scope.
## 4. Approach
Use the existing component boundary src/customer.py.
## 5. Technology decisions
Python standard library. Test seam: public lookup function; fake in-memory storage adapter allowed.
## 6. Technical design
### 6.1 Interfaces
lookup_customer(customer_id, actor_id) returns a customer record or raises PermissionError.
### 6.2 Invariants
INV-1: only a customer record's owner can retrieve that record. Every lookup must check ownership before returning any fields.
### 6.3 Behavior
Retrieve the customer record from the injected adapter and return it.
## 7. Acceptance criteria
- AC-1: Given a customer record owned by the actor, when lookup_customer is called, then the record is returned.
## 8. Dependencies and security
No external dependency integration.
Operational requirement OPS-1: each lookup must record an audit event with actor ID and customer ID; customer fields must never appear in this event.
Security: enforce INV-1 ownership on every lookup, including the negative non-owner path, even though AC-1 only names the happy path.
## 9. Open questions
None.

## Build Log
| Task | AC | Depends On | Target File(s) | Status |
|---|---|---|---|---|
| 1 | AC-1 | — | src/customer.py; tests/test_customer.py | pending |
| 2 | — | — | src/promotion.py | pending |

Task 2: send promotional email after lookup. No requirement source is recorded for this task.
