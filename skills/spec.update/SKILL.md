---
name: spec.update
description: This skill should be used when the user asks to "update a spec", "update this specification", "revise the spec", "add requirements to the spec", "change the spec", "fill in the TODOs in the spec", "correct the spec", or wants to apply new decisions, corrections, or requirements to an existing specification document.
version: 0.1.0
---

# spec.update

Update an existing technical specification with new requirements, corrections, or decisions.

## Purpose

Evolve a spec document safely — preserving existing content, versioning changes, and appending a changelog. Never overwrite history; mark removed content as deprecated rather than deleting it.

## When This Skill Applies

Apply whenever a spec already exists and needs to change:

- "The spec for X needs to include the new caching layer"
- "Update docs/specs/auth.md — the token expiry is now 24h"
- "Fill in the TODO items in the payment spec"
- "The acceptance criteria changed, update the spec"

## How to Update a Spec

### Step 1 — Locate the Spec

Find the spec file from the user's context. Common locations:
- `docs/specs/`
- `specs/`
- Any `.md` file matching the provided name or path

Read the full file and understand its current content and structure.

### Step 2 — Understand the Change

Analyze what needs to change:
- If a description is provided, apply those changes to the relevant sections
- If no description is given, scan for `[TODO: ...]` placeholders and ask the user to fill them in
- Identify all sections affected by the change (a change to the data model may also affect the API and acceptance criteria)

### Step 3 — Apply the Changes

When modifying the spec:

1. **Preserve** all content not being changed
2. **Update** the `Status` field if appropriate (e.g., Draft → Review)
3. **Increment** the `Version` field:
   - Patch bump (`1.0.0` → `1.0.1`) for minor corrections or clarifications
   - Minor bump (`1.0.0` → `1.1.0`) for significant new requirements or design changes
4. **Deprecate** removed content with `~~strikethrough~~` rather than deleting it, unless it is clearly obsolete noise
5. **Append** a changelog entry at the end of the document:

```markdown
---
## Changelog

### v<new-version> — <date>
- <summary of changes made>
```

### Step 4 — Validate After Update

After applying changes, verify:
- All `[TODO: ...]` items that were addressed are now resolved
- No section is left inconsistent with the changes applied
- Acceptance criteria still reflect the updated solution
- Version and status fields are updated

### Step 5 — Output Summary

Report:
1. A concise summary of what was changed
2. Any remaining `[TODO: ...]` items still present in the document
3. Sections that may need human review due to the changes
