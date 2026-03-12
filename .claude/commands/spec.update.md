# spec.update

Updates an existing technical specification with new requirements, corrections, or decisions.

## Usage

```
/spec.update <spec-file-path> [changes-description]
```

## Instructions

You are a pragmatic technical writer. Your task is to update an existing specification document.

**Input:** $ARGUMENTS

### Step 1 — Locate the Spec

Identify the spec file from the input. Common locations:
- `docs/specs/`
- `specs/`
- Any `.md` file matching the provided name

Read the current spec file and understand its full content and structure.

### Step 2 — Understand What Needs Updating

Analyze the change request from the arguments:
- If a description of changes is provided, apply those changes
- If no description is provided, scan the current spec for `[TODO: ...]` placeholders and prompt the user to fill them in
- Identify sections that may be affected by the requested changes

### Step 3 — Apply Updates

When modifying the spec:

1. **Preserve** all existing content that is not being changed
2. **Update** the `Status` field if appropriate (e.g., Draft → Review)
3. **Increment** the `Version` field (patch bump for minor changes, minor bump for significant changes)
4. **Add** a changelog entry at the end of the document:

```markdown
---
## Changelog

### v<new-version> — <date>
- <summary of changes made>
```

5. **Mark** removed or deprecated content with `~~strikethrough~~` rather than deleting, unless it is clearly outdated noise

### Step 4 — Validate After Update

After applying changes, verify:
- [ ] All `[TODO: ...]` items that were addressed are resolved
- [ ] No section is left inconsistent with the changes
- [ ] Acceptance criteria still reflect the updated solution
- [ ] Version and status fields are updated

### Output Instructions

1. Apply all changes directly to the spec file
2. Report a concise summary of what was changed
3. List any remaining `[TODO: ...]` items still present in the document
4. Flag any sections that may need human review due to the changes
