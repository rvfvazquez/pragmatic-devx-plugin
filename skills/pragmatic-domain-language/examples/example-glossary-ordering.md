# Example Glossary: Ordering

> This is a complete example of `docs/glossary/ordering.md`, following
> `references/glossary-template.md`.
> **Showcases:** terms that sit next to another context's vocabulary (*refund* belongs
> to Payments), a definition whose boundary was decided with a scenario, and a resolved
> ambiguity recorded so the debate does not reopen in the next spec.

---

# Ordering

Receives customer orders and tracks them from placement to delivery.

## Language

### Orders

**Order**
A purchase request placed by a Customer, with one or more Order Items and one delivery address.
_Avoid_: purchase, transaction (a Payments term)
_In code_: `Order`

**Order Item**
A product and its quantity within an Order; it does not exist outside one.
_Avoid_: line, order line
_In code_: `OrderItem`

**Order Status**
The stage of an Order's life, from pending through delivered, cancelled, or refunded.
_Avoid_: phase, step
_In code_: `OrderStatus`

**Cancellation**
Ending an entire Order before it is delivered. Partial cancellation does not exist.
_Avoid_: void, annulment, partial cancellation

### People

**Customer**
A person or company that places Orders.
_Avoid_: account, client, buyer
_In code_: `Customer`

**Operator**
A staff member who manages Orders on behalf of Customers.
_Avoid_: admin, agent

## Resolved Ambiguities

- A Customer returning a **delivered** Order is not a **Cancellation**: Cancellation ends an Order before delivery (including one returned in transit), while a delivered Order goes from `delivered` straight to `refunded`. Decided in `docs/specs/order-lifecycle.md`.
- "Refund" appeared in Ordering as an Order Status (`refunded`) and in Payments as the movement of money. They are distinct: the status records that Payments completed a **Refund**; the Refund itself belongs to Payments. Decided in `docs/specs/order-lifecycle.md`.
- "Account" was used for both **Customer** (who buys) and **User** (who signs in, in Identity). They are the same person in two roles — see Translations in the context map. Decided in `docs/specs/auth.md`.
