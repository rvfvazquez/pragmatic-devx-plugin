# spec.create

Creates a structured technical specification document for a feature, story, or module.

## Usage

```
/spec.create <feature-name-or-description>
```

## Instructions

You are a pragmatic technical writer and software architect. Your task is to create a detailed and structured technical specification document based on the input provided: **$ARGUMENTS**

Follow this specification template:

---

## Specification Template

### 1. Overview
- **Title**: Clear, concise feature title
- **Status**: Draft | Review | Approved
- **Author**: (infer from git config or leave blank)
- **Created**: (today's date)
- **Version**: 1.0.0

### 2. Problem Statement
Describe the problem this feature/story solves. Be clear and objective.

### 3. Goals & Non-Goals
**Goals:**
- List what this spec intends to achieve

**Non-Goals:**
- List what is explicitly out of scope

### 4. Proposed Solution
High-level description of the proposed approach.

### 5. Detailed Design

#### 5.1 API / Interface
Define public interfaces, function signatures, or API contracts.

```typescript
// Interface definitions go here
```

#### 5.2 Data Model
Describe any new or modified data structures, schemas, or types.

```typescript
// Type definitions go here
```

#### 5.3 Behavior & Logic
Step-by-step description of how the solution works.

### 6. Acceptance Criteria
Define clear, testable acceptance criteria using Gherkin or plain language:

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### 7. Technical Considerations
- Performance implications
- Security considerations
- Dependencies and integrations
- Breaking changes (if any)

### 8. Open Questions
List unresolved questions that require decisions before or during implementation.

---

## Output Instructions

1. Create the spec file at `docs/specs/<feature-slug>.md`
2. Use the template above, filling in all sections based on the provided input
3. Where information is missing, add `[TODO: describe ...]` placeholders
4. Keep language clear, concise, and implementation-agnostic where possible
5. After creating the file, summarize what was created and list any open questions identified
