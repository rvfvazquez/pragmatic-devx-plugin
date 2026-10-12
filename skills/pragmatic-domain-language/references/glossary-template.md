# Glossary Template (one file per context)

Location: `docs/glossary/<context-slug>.md` — one file per bounded context, always inside `docs/glossary/`, always listed in `docs/glossary/context-map.md` (see `context-map-template.md`). Write it in the same language as the specs. Section headings below are translated along with the content.

Create it lazily: the folder, the context map, and the first context file are created together, when the first term is confirmed — never as an empty placeholder.

---

```markdown
# <Context Name>

<One or two sentences: what this context is and why it exists.>

## Language

### <Optional subheading — only when terms form natural clusters>

**<Term>**
<One or two sentences defining what it IS — not what it does, not how it is implemented.>
_Avoid_: <synonym>, <synonym>
_In code_: `<Identifier>`

**<Term>**
<Definition.>
_Avoid_: <synonym>
_In code_: `<Identifier>`

## Resolved Ambiguities

- "<word>" was used for both **<Term A>** and **<Term B>**. They are distinct: <one line on the difference>. Decided in `<path to spec or arch spec>`.
```

---

## Field Rules

| Field | Required | Rule |
|---|---|---|
| **Term** (bold) | yes | The canonical name, in the document language |
| Definition | yes | 1–2 sentences on what the concept *is*. No tables, endpoints, types, or behavior rules |
| `_Avoid_` | when synonyms exist | Every other word people use for this concept. This is what `pragmatic-spec-validate` checks against |
| `_In code_` | optional | The identifier the code uses (e.g. `Order` for "Pedido"). Bridges a non-English glossary to English code; omit when the term and the identifier are the same word |

## Content Rules

- **Be opinionated.** When several words exist for one concept, pick one and move the rest to `_Avoid_`.
- **Domain terms only.** Concepts specific to this project's context. General programming concepts (timeout, retry, DTO, cache) do not belong, even if the project uses them heavily.
- **No implementation.** Schemas, endpoints, and types belong in spec section 6. Invariants and business rules ("a delivered order never returns to pending") belong in spec section 6.2 — the glossary says what a thing is, the spec says the rules it obeys.
- **One meaning per term per context.** If the same word genuinely means two things, it is two terms — or a sign the word spans two contexts (record that in the context map's Translations section).
- **Resolved Ambiguities is optional.** Use it only for confusions that were actually discussed and decided, linking where. It keeps the same debate from reopening in the next spec. Omit the section when it would be empty.

## Example

```markdown
# Ordering

Receives customer orders and tracks them through to delivery.

## Language

### Order lifecycle

**Order**
A purchase request made by a Customer, with one or more Order Items and a single delivery address.
_Avoid_: purchase, transaction

**Order Item**
A product and its quantity within an Order; it does not exist outside one.
_Avoid_: line, order product
_In code_: `OrderItem`

**Cancellation**
Ending an entire Order before it ships. Partial cancellation does not exist in this context.
_Avoid_: refund (a Billing concept), void

### People

**Customer**
A person or company that places Orders.
_Avoid_: account, user, buyer

## Resolved Ambiguities

- "Account" was used for both **Customer** (who buys) and **User** (who logs in, Identity context). They are distinct. Decided in `docs/specs/checkout.md`.
```
