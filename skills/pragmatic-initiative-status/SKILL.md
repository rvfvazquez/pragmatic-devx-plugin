---
name: pragmatic-initiative-status
description: Reads one or more pragmatic documents (a spec, an arch spec, or every feature row in an initiative) and reports each one's Status field, unresolved [TODO: ...] items, and Open Questions entries in one consolidated view. Dispatched internally by pragmatic-initiative-deliver before deciding whether a feature is ready to progress. Never invoke directly.
disable-model-invocation: true
---

# pragmatic-initiative-status

Read-only. Reports, for one or more pragmatic documents, the `Status` field, unresolved `[TODO: ...]` items, and Open Questions section entries — in one consolidated view, so a dispatcher can decide readiness without re-reading each document in full.

## Input

Either:
- A list of specific document paths (`docs/specs/<slug>.md`, `docs/arch/<name>.arch.md`, or `docs/constitution.md`), or
- An initiative document path (`docs/initiatives/<slug>.md`) — check every non-empty `Spec` column value in its Features table

## What to report, per document

1. **Status** — the document's own `Status` field (`Draft` / `Review` / `Approved`), or `not created yet` if the path doesn't exist or the column is still empty
2. **Open TODOs** — count and the text of every `[TODO: decide — ...]` / `[TODO: describe ...]` found in the body
3. **Open Questions** — count and a one-line gist of every entry in the document's "Open Questions" section (section 9 for feature specs, section 10 for arch specs)
4. **Ready** — `yes` only if Status is `Review` or `Approved` **and** the Open TODOs count is 0. Open Questions entries never block readiness on their own — an entry there is, by the section's own definition, a concern too vague to be a decision yet, not a pending one.

## Output format

```
| Document | Status | Open TODOs | Open Questions | Ready |
|---|---|---|---|---|
| docs/specs/auth.md | Review | 0 | 1 | yes |
| docs/specs/billing.md | Draft | 2 | 0 | no |
```

When the dispatcher needs to act on a blocker (not just see the count), report the actual TODO/Open-Question text alongside the table.

Never modify any document, and never render a judgment on whether a TODO or Open Question *should* be resolved a particular way — that decision belongs to the skill that owns the document (`pragmatic-spec-update`, `pragmatic-arch-spec-update`, or a human), not to this one.
