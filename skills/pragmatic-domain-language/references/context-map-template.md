# Context Map Template

Location: `docs/glossary/context-map.md` — the single entry point to the project's domain language. It always exists when `docs/glossary/` exists, even for a project with one context. Every skill that reads or writes terms opens this file first and follows it to the right `docs/glossary/<context-slug>.md`. Write it in the same language as the specs.

**Naming the first context:** take it from an existing `module`-scope arch spec in `docs/arch/` if one covers this area; otherwise from the product name in the constitution's project identity section; otherwise ask the user. Never use a generic name such as `default` or `main` — the context name is vocabulary too.

---

```markdown
# Context Map

**Last synced:** `<commit sha>` (<date>)

## Contexts

| Context | Glossary | Arch spec | Purpose | Owns | Code |
|---|---|---|---|---|---|
| <Name> | [<slug>](./<slug>.md) | [<name>.arch](../arch/<name>.arch.md) or — | <one line> | <terms whose source of truth is this context> | <paths, comma-separated> or — |

## Relationships

| From → To | Mechanism | What crosses |
|---|---|---|
| <Context A> → <Context B> | Event / Sync call / Shared types / Translation layer | <event, call, or type names> |

## Translations

The same concept under different names, each correct in its own context:

| Concept | <Context A> | <Context B> |
|---|---|---|
| <plain description> | <Term in A> | <Term in B> |
```

---

## Rules

- **One row per context file.** Every `docs/glossary/*.md` other than this map appears in Contexts, and every row's Glossary link resolves to an existing file.
- **Arch spec column:** link the `module`-scope arch spec for that context when one exists; `—` otherwise. A context without an arch spec is normal early on.
- **Code column (optional):** the directories, relative to the repository root and comma-separated, where this context's code lives (`src/payments`, `internal/ordering`). It scopes `pragmatic-domain-language`'s sync and `glossary-drift.sh`; a context with `—` is skipped by both. Fill it when known, never guess it.
- **Last synced (optional):** the commit the glossary was last reconciled with the code, written by the sync flow — never by hand and never by a skill that only reads the map. A map without it means "never synced"; the sync then scans the whole Code paths instead of the changes since that commit.
- **Owns:** the terms this context is the source of truth for. Other contexts reference them by identifier only. Must not contradict a cross-module rule in the constitution.
- **Mechanism** must agree with the Communication Style (section 6.3) of the arch specs involved, when they exist.
- **Single-context project:** one row in Contexts; omit Relationships and Translations entirely rather than leaving them empty.
- **Translations** is the only place the same concept may legitimately carry different names. The same word defined in two context files without a row here is a finding.

## Example

```markdown
# Context Map

**Last synced:** `9c3d2e1` (2026-10-12)

## Contexts

| Context | Glossary | Arch spec | Purpose | Owns | Code |
|---|---|---|---|---|---|
| Ordering | [ordering](./ordering.md) | [ordering.arch](../arch/ordering.arch.md) | Receives and tracks orders | Order, Order Item | src/ordering |
| Billing | [billing](./billing.md) | [billing.arch](../arch/billing.arch.md) | Issues invoices and processes payments | Invoice, Payment | src/billing |
| Fulfillment | [fulfillment](./fulfillment.md) | — | Picking and shipping | Shipment | — |

## Relationships

| From → To | Mechanism | What crosses |
|---|---|---|
| Ordering → Fulfillment | Event | `OrderConfirmed`: Fulfillment starts picking |
| Fulfillment → Billing | Event | `ShipmentDispatched`: Billing issues the Invoice |
| Ordering ↔ Billing | Shared types | `CustomerId`, `Money` |

## Translations

| Concept | Ordering | Billing |
|---|---|---|
| Who pays for the order | Customer | Payer |
```
