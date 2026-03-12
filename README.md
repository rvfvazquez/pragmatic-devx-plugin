# pragmatic-devx-plugin

Claude Code plugin focused in Developer Experience — structured specs, TypeScript architecture, and pragmatic engineering patterns.

## Marketplace

This plugin is available on the Claude Code Marketplace. It provides a set of skills to help developers write better specs and design cleaner TypeScript architectures.

## Skills

### `spec.create`
Creates a structured technical specification document for a feature, story, or module.

```
/spec.create <feature-name-or-description>
```

Generates a full spec document at `docs/specs/<feature-slug>.md` with sections for problem statement, goals, proposed solution, detailed design, and acceptance criteria.

---

### `spec.update`
Updates an existing specification with new requirements, corrections, or decisions.

```
/spec.update <spec-file-path> [changes-description]
```

Preserves existing content, increments version, and appends a changelog entry.

---

### `spec.validate`
Validates a specification for completeness, clarity, and consistency.

```
/spec.validate <spec-file-path>
```

Runs structured checks across completeness, clarity, consistency, and technical requirements. Outputs a detailed validation report with PASS/WARN/FAIL statuses.

---

### `arch.ts.create`
Creates a software architecture technical specification document for a system, module, layer, or integration.

```
/arch.ts.create <system-or-module-name> [scope]
```

**Scope:** `system` | `module` | `layer` | `integration`

Generates a full architecture tech spec at `docs/arch/<name>.arch.md` covering context, design decisions (ADRs), component boundaries, architecture patterns, communication style, data flow, and non-functional requirements.

---

### `arch.ts.validate`
Validates an architecture tech spec for completeness, consistency, and architectural soundness.

```
/arch.ts.validate <arch-spec-file-path>
```

Checks completeness (goals, ADRs, component boundaries, data flow), architectural soundness (single responsibility, dependency direction, no circular coupling), clarity (diagrams, unambiguous language), and design quality. Outputs a structured PASS/WARN/FAIL report.

---

## Project Structure

```
pragmatic-devx-plugin/
├── .claude/
│   ├── settings.json              # Marketplace & skill configuration
│   └── commands/
│       ├── spec.create.md         # spec.create skill definition
│       ├── spec.update.md         # spec.update skill definition
│       ├── spec.validate.md       # spec.validate skill definition
│       ├── arch.ts.create.md      # arch.ts.create skill definition
│       └── arch.ts.validate.md    # arch.ts.validate skill definition
├── plugin.json                    # Plugin manifest
├── LICENSE
└── README.md
```

## License

MIT
