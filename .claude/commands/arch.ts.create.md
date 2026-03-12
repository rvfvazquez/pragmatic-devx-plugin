# arch.ts.create

Creates a TypeScript architecture scaffold following pragmatic design patterns and clean code principles.

## Usage

```
/arch.ts.create <module-name> [module-type]
```

**Module types:** `service` | `repository` | `controller` | `hook` | `util` | `module` (default: `module`)

## Instructions

You are a pragmatic TypeScript architect. Your task is to scaffold a well-structured TypeScript module.

**Input:** $ARGUMENTS

### Step 1 — Parse the Input

From the arguments, determine:
- **Module name**: convert to `kebab-case` for files and `PascalCase` for types/classes
- **Module type**: one of `service`, `repository`, `controller`, `hook`, `util`, or `module`
- **Target directory**: look for existing `src/` structure and match conventions; default to `src/<module-type>s/`

### Step 2 — Identify Project Conventions

Before generating code:
1. Scan `src/` for existing files to understand naming conventions
2. Check for `tsconfig.json` to understand path aliases and target settings
3. Check `package.json` for relevant dependencies (e.g., testing framework, HTTP lib)
4. Match the style and patterns already present in the codebase

### Step 3 — Generate the Architecture

Create the following files based on the module type:

#### For `module` (default)
```
src/<module-name>/
├── index.ts                    # Public API / barrel export
├── <module-name>.types.ts      # Interfaces, types, enums
├── <module-name>.service.ts    # Business logic
├── <module-name>.repository.ts # Data access (if applicable)
└── __tests__/
    └── <module-name>.service.test.ts
```

#### For `service`
```
src/services/<module-name>/
├── index.ts
├── <module-name>.service.ts
├── <module-name>.types.ts
└── __tests__/
    └── <module-name>.service.test.ts
```

#### For `repository`
```
src/repositories/
├── <module-name>.repository.ts
├── <module-name>.repository.types.ts
└── __tests__/
    └── <module-name>.repository.test.ts
```

#### For `hook` (React)
```
src/hooks/
├── use-<module-name>.ts
├── use-<module-name>.types.ts
└── __tests__/
    └── use-<module-name>.test.ts
```

#### For `util`
```
src/utils/
├── <module-name>.util.ts
└── __tests__/
    └── <module-name>.util.test.ts
```

### Step 4 — Code Generation Standards

When writing TypeScript files, follow these principles:

**Types file (`*.types.ts`)**
```typescript
// Always export named interfaces, not inline types
export interface <ModuleName>Options {
  // fields with JSDoc when non-obvious
}

export interface <ModuleName>Result {
  // ...
}

// Use const enums for closed sets of values
export const enum <ModuleName>Status {
  Active = 'active',
  Inactive = 'inactive',
}
```

**Service file (`*.service.ts`)**
```typescript
import type { <ModuleName>Options, <ModuleName>Result } from './<module-name>.types';

export class <ModuleName>Service {
  // Inject dependencies via constructor
  constructor(private readonly dep: DepType) {}

  async doSomething(options: <ModuleName>Options): Promise<<ModuleName>Result> {
    // Implementation
  }
}

// Also export a factory function for functional style
export function create<ModuleName>Service(dep: DepType): <ModuleName>Service {
  return new <ModuleName>Service(dep);
}
```

**Test file (`*.test.ts`)**
```typescript
import { describe, it, expect, beforeEach } from 'vitest'; // or jest

describe('<ModuleName>Service', () => {
  let service: <ModuleName>Service;

  beforeEach(() => {
    service = new <ModuleName>Service(/* mock deps */);
  });

  describe('doSomething', () => {
    it('should ...', async () => {
      // Arrange
      // Act
      // Assert
    });
  });
});
```

**Barrel export (`index.ts`)**
```typescript
// Only export the public API — never export internals
export type { <ModuleName>Options, <ModuleName>Result } from './<module-name>.types';
export { <ModuleName>Service, create<ModuleName>Service } from './<module-name>.service';
```

### Step 5 — Output Instructions

1. Create all files with production-ready boilerplate (not just empty stubs)
2. Add `// TODO:` comments where business logic needs to be filled in
3. Report the list of files created with their purpose
4. Suggest the next steps for implementing the module
