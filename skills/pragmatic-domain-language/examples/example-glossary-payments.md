# Example Glossary: Payments

> This is a complete example of `docs/glossary/payments.md`, following
> `references/glossary-template.md`.
> **Showcases:** a concept (*Payer*) deliberately kept apart from another context's
> *Customer*, and `_Avoid_` words that are common in the surrounding prose.

---

# Payments

Charges and refunds money for Orders through an external payment provider.

## Language

**Transaction**
The record of one attempt to move money for an Order, either a Charge or a Refund.
_Avoid_: operation, movement
_In code_: `Transaction`

**Charge**
Taking money from a Payer for an Order.
_Avoid_: debit
_In code_: `Charge`

**Refund**
Returning the money of a Charge to the Payer.
_Avoid_: reversal, credit

**Payer**
The party whose payment method is charged for an Order; not always the Customer who placed it.
_Avoid_: customer, account, buyer
_In code_: `Payer`

## Resolved Ambiguities

- "Customer" was used in Payments for whoever pays. Ordering owns **Customer** (who places the Order), and the two can differ — a company card paying for an employee's Order — so Payments says **Payer**. Stripe also calls its paying party "Customer"; the adapter translates (see the context map). Decided in `docs/specs/payments.md`.
