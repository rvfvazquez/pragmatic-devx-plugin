# Example Spec: Order Status Notifications

> This is a complete example of a spec produced by spec.create.
> **Diagram type showcased:** `flowchart LR` — use this pattern when the behavior involves
> asynchronous processing, message queues, or event-driven steps that don't fit a linear
> request/response model.

---

## 1. Overview

- **Title**: Order Status Email Notifications
- **Status**: Review
- **Author**: platform-team
- **Created**: 2026-04-01
- **Version**: 1.0.0

## 2. Problem Statement

Customers receive no automatic communication when their order status changes. This generates unnecessary support contact volume and degrades the post-purchase experience. All status inquiries are currently customer-initiated — the system does not proactively notify.

## 3. Goals & Non-Goals

**Goals:**
- Send an automatic email to the customer when an order transitions to `shipped` or `delivered`
- Ensure the notification dispatch does not block or delay the status change operation
- Record each notification attempt for auditing and data retention compliance

**Non-Goals:**
- SMS or mobile push notifications
- Customer-facing preferences panel (deferred)
- Automatic retry for failed delivery attempts at the provider level
- Email template internationalization

## 4. Proposed Solution

When an order status changes, the order service publishes an event to an SQS queue. A dedicated consumer reads those events, filters for relevant statuses, and triggers delivery via SendGrid Dynamic Templates. The send history is persisted to the `order_notifications` table in the existing PostgreSQL database.

## 5. Technology Decisions

| Concern | Decision | Alternatives Considered | Rationale |
|---------|----------|------------------------|-----------|
| Email provider | SendGrid (existing) | SES, Mailgun | Already contracted and has templates configured |
| Delivery mechanism | Async via SQS | Synchronous in request, SNS | Decouples status change from send; tolerant to provider failures |
| Templates | SendGrid Dynamic Templates | Go html/template, hardcoded | Editable without deploy; supported by current SendGrid contract |
| Notification history | PostgreSQL — `order_notifications` table | No persistence, separate table | DB already in use; history required for audit and data retention |
| Opt-out | SendGrid native unsubscribe link | User profile setting | Simpler solution; satisfies legal requirement without new UI |

## 6. Detailed Design

### 6.1 API / Interface

```go
// NotificationService defines the contract for the notification service
type NotificationService interface {
    SendOrderStatusEmail(ctx context.Context, event OrderStatusChangedEvent) error
}

type OrderStatusChangedEvent struct {
    OrderID    string    `json:"order_id"`
    CustomerID string    `json:"customer_id"`
    NewStatus  string    `json:"new_status"`
    OccurredAt time.Time `json:"occurred_at"`
}
```

### 6.2 Data Model

New table `order_notifications`:

```go
type OrderNotification struct {
    ID         string    `db:"id"`
    OrderID    string    `db:"order_id"`
    CustomerID string    `db:"customer_id"`
    Status     string    `db:"status"`      // "sent" | "skipped" | "failed"
    Channel    string    `db:"channel"`     // "email"
    SentAt     time.Time `db:"sent_at"`
    CreatedAt  time.Time `db:"created_at"`
}
```

### 6.3 Behavior & Logic

```mermaid
flowchart LR
    A[Order Service] -->|status changed| B[SQS\norder-events]
    B --> C{Consumer\nNotification Worker}
    C -->|status = shipped\nor delivered| D[SendGrid API]
    C -->|other status| E[Skip\nlog + return]
    D -->|success| F[(PostgreSQL\norder_notifications\nstatus=sent)]
    D -->|error| G[(PostgreSQL\norder_notifications\nstatus=failed)]
    F --> H([Done])
    G --> H
```

**Consumer steps:**
1. Receive SQS message with `OrderStatusChangedEvent`
2. Check if `new_status` is `shipped` or `delivered` — if not, skip (record `skipped`) and ack message
3. Fetch customer email and name via `customer_id` from the user service
4. Select the Dynamic Template ID corresponding to the status
5. Trigger send via SendGrid with order data
6. Persist result to `order_notifications` (sent/failed)
7. Ack the SQS message regardless of send result — delivery failures do not trigger reprocessing

## 7. Acceptance Criteria

- [ ] When an order status changes to `shipped`, the customer receives an email within 30s
- [ ] When an order status changes to `delivered`, the customer receives an email within 30s
- [ ] Changes to `pending` or `cancelled` do not trigger an email (recorded as `skipped`)
- [ ] Email contains a functional opt-out link via SendGrid unsubscribe
- [ ] After opt-out, no further emails are sent to that address
- [ ] Each send attempt is recorded in `order_notifications` with status and timestamp
- [ ] A SendGrid failure does not cause SQS message reprocessing (message is acked even on error)

## 8. Technical Considerations

- **Idempotency:** if the same SQS message is delivered more than once (at-least-once), duplicate emails may be sent. Mitigation: check `order_id + status` in `order_notifications` before sending.
- **Data retention:** the `order_notifications` history must respect the customer data retention policy. Include `customer_id` to support deletion requests.
- **Dependencies:** SendGrid SDK (`github.com/sendgrid/sendgrid-go`), AWS SDK for SQS — both already in `go.mod`.
- **Breaking changes:** none — the order service only needs to publish events to the existing queue. No existing contracts are changed.
- **Observability:** log `order_id`, `customer_id`, and `status` on each send attempt for traceability.

## 9. Open Questions

- [ ] [TODO: decide — what should happen when fetching the customer email fails? Options: skip (record failed), retry with backoff, dead-letter queue]
- [ ] [TODO: decide — which statuses beyond `shipped` and `delivered` should trigger email in future iterations?]
