# Report export job
Status: Review
Language: English
Version: 1.0.0

## 2. Problem Statement
Analysts cannot download a finished report as a file.

## 3. Goals & Non-Goals
**Goals:**
- An analyst can request an export of a finished report and download it.

**Non-Goals:**
- Scheduled recurring exports.

## 4. Proposed Solution
A request creates an export record; the file is produced and stored for download.

## 5. Technology Decisions

| Concern | Decision | Alternatives Considered | Rationale |
|---|---|---|---|
| Data storage | DynamoDB table `exports` | PostgreSQL | Scales well |
| Async processing | SQS queue + worker | Synchronous | Decoupling |
| Test seam | HTTP POST /reports/{id}/export, storage via fake adapter | Service layer | Public boundary maps to criteria |

## 6. Technical Design
### 6.1 Interfaces
POST /reports/{id}/export returns 201 with the export id; GET /exports/{id} returns the file or 404.
### 6.2 Invariants
None — the feature introduces no data rule beyond a record per request.
### 6.3 Behavior
Create the export record, produce the file, store it, return the id.

## 7. Acceptance Criteria
- AC-1: Given a finished report, when the analyst requests an export, then the system SHALL return 201 with an export id.
- AC-2: Given an unknown export id, when the analyst downloads it, then the system SHALL return 404.

## 8. Dependencies and Security
Dependencies: report service.
Security:
- Authentication: platform OIDC (from constitution).
- Authorization: only the requesting analyst can download an export.
- Untrusted input: report id validated.
- Sensitive data: report contents never logged.
- Abuse case: export flooding; rate limit per analyst.

## 9. Open Questions
None.
