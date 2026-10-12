# Example Context Map

> This is a complete example of `docs/glossary/context-map.md`, following
> `references/context-map-template.md`. It describes the same project the other
> examples in this plugin come from: the order, payment, notification, and
> authentication specs. Each context below has its own example glossary file in this
> folder (`example-glossary-<context>.md`) — in a real project they live next to the
> map as `docs/glossary/<context>.md`.
> **Showcases:** the **Code** and per-context **Synced** columns that scope the sync flow and `scripts/glossary-drift.sh` (Identity has never been synced), the **Owns** column as the source of truth for each concept, an event
> relationship defined by a system-scope arch spec, a shared-types relationship, a
> synchronous call, and translations — including a word (*Customer*) that means a
> different thing in two contexts and in an external system.

---

# Context Map

## Contexts

| Context | Glossary | Arch spec | Purpose | Owns | Code | Synced |
|---|---|---|---|---|---|---|
| Ordering | [ordering](./ordering.md) | — | Receives customer orders and tracks them to delivery | Order, Order Item, Order Status, Cancellation, Customer, Operator | src/ordering | `9c3d2e1` |
| Payments | [payments](./payments.md) | [payments.arch](../arch/payments.arch.md) | Charges and refunds money for orders | Transaction, Charge, Refund, Payer | src/payments | `4f2a91c` |
| Notifications | [notifications](./notifications.md) | — | Tells recipients about events they care about | Notification, Recipient, Channel, Opt-out | src/notifications | `9c3d2e1` |
| Identity | [identity](./identity.md) | — | Authenticates users and issues access tokens | User, Access Token | src/auth | — |

## Relationships

| From → To | Mechanism | What crosses |
|---|---|---|
| Ordering → Notifications | Event | `order-events` (SQS): an Order Status changed. Defined in `docs/arch/notification-service.arch.md` (system scope); Notifications decides whether to notify |
| Payments → Notifications | Event | `payment-events` (SQS): a Transaction was confirmed or refunded. Same arch spec |
| Payments → Ordering | Event | `payment-events` (SQS): payment authorized, refund completed — moves the Order Status (`pending` → `confirmed`, `cancelled` → `refunded`) |
| Ordering ↔ Payments | Shared types | `OrderId` — Payments references an Order by identifier only and never stores its data |
| Notifications → Identity | Sync call | contact lookup by id: returns the email and name of the person to notify. Defined by the feature spec `docs/specs/order-notifications.md` (consumer step 3), not by an arch spec |

## Translations

The same concept under different names, each correct in its own context:

| Concept | Ordering | Identity | Payments | Notifications |
|---|---|---|---|---|
| The person behind an Order | Customer | User | — | Recipient |
| Who pays for an Order | Customer | — | Payer | — |

A Customer and a User are the same person in two roles, keyed by the same id: Ordering sees who bought, Identity sees who signs in. A Payer may be a different party from the Customer (a company card paying for an employee's Order).

### External systems

Vocabulary of integrations, mapped to ours so the adapters stay explicit:

| Concept | Ours | External |
|---|---|---|
| Who pays for an Order | Payments: Payer | Stripe: *Customer* — **not** an Ordering Customer |
| A record of money moving | Payments: Transaction | Stripe: *PaymentIntent* |
| A Recipient stops receiving a Channel | Notifications: Opt-out | SendGrid: *Unsubscribe* |
