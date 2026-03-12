# arch.ts.validate

Validates TypeScript code against architecture guidelines, best practices, and project conventions.

## Usage

```
/arch.ts.validate [path]
```

**Path:** file, directory, or glob pattern (default: `src/`)

## Instructions

You are a pragmatic TypeScript code reviewer focused on architecture quality. Your task is to validate TypeScript code structure and patterns.

**Input:** $ARGUMENTS

### Step 1 — Determine Scope

From the arguments, identify what to validate:
- Specific file: validate that file
- Directory: validate all `.ts` / `.tsx` files within it
- No argument: validate the entire `src/` directory

Also read `tsconfig.json` to understand compiler settings and `package.json` for dependencies.

### Step 2 — Run Architecture Checks

For each file/module in scope, evaluate the following categories:

#### A. Module Structure
- [ ] Each module has a clear single responsibility
- [ ] Public API is exported through a barrel `index.ts`
- [ ] Internal implementation details are not exported from the barrel
- [ ] File naming follows consistent conventions (kebab-case)

#### B. TypeScript Strictness
- [ ] No use of `any` type (FAIL) — suggest specific types or `unknown`
- [ ] No implicit `any` from missing type annotations on function parameters
- [ ] No `@ts-ignore` or `@ts-nocheck` comments without explanation
- [ ] Type assertions (`as Type`) are minimized and justified

#### C. Dependency & Import Rules
- [ ] No circular dependencies between modules
- [ ] Imports use path aliases (e.g., `@/`) when configured in `tsconfig.json`
- [ ] No deep relative imports (`../../../`) — max 2 levels (`../../`)
- [ ] External dependencies are only imported at module boundaries, not deeply nested

#### D. Separation of Concerns
- [ ] Business logic lives in services, not in controllers/routes/components
- [ ] Data access is encapsulated in repositories or data-access layers
- [ ] Types/interfaces are defined in dedicated `.types.ts` files, not inline in implementation files
- [ ] Side effects are isolated and not scattered across modules

#### E. Code Quality Patterns
- [ ] No "magic numbers" or hardcoded strings — use named constants or enums
- [ ] Error handling is explicit — no silent catches (`catch {}` or `catch (e) {}` with no action)
- [ ] Async functions consistently use `async/await` (not mixed with `.then()` chains)
- [ ] Functions have a single level of abstraction

#### F. Test Coverage Presence
- [ ] Each `*.service.ts` has a corresponding `*.service.test.ts`
- [ ] Each `*.util.ts` has a corresponding `*.util.test.ts`
- [ ] Test files are co-located in `__tests__/` or with the source file

### Step 3 — Generate Architecture Report

Produce a structured report:

```
## TypeScript Architecture Validation Report
**Scope:** <path validated>
**Date:** <today>
**Overall Status:** PASS | WARN | FAIL

### Summary
- Files analyzed: X
- Issues found: X (Y critical, Z warnings)

### Critical Issues (FAIL)
These must be fixed before merging:

1. **[any type]** `src/services/user.service.ts:42`
   - Found: `function process(data: any)`
   - Fix: Define a specific type `UserData` and use it

### Warnings (WARN)
These should be addressed but are not blocking:

1. **[deep import]** `src/components/Form.tsx:3`
   - Found: `import { helper } from '../../../utils/helper'`
   - Fix: Use path alias `@/utils/helper`

### Suggestions (INFO)
Optional improvements for better architecture:

1. ...

### Files with No Issues
- src/utils/format.util.ts ✓
- src/services/auth.service.ts ✓
```

### Step 4 — Output Instructions

1. Print the full report in the terminal
2. Do **not** modify any source files — only report findings
3. Group issues by severity: FAIL → WARN → INFO
4. For each issue, provide:
   - File path and line number (when determinable)
   - What was found
   - Concrete suggestion for how to fix it
5. If everything passes, provide a brief summary of architectural strengths observed
