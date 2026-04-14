# Architecture Conformance Report Format

Use this format when generating the conformance report in Step 4 of arch.spec.check.

---

```
## Architecture Conformance Report

**Spec(s):** <file path(s)>
**Scope:** <full project | specific path>
**Date:** <today>
**Overall Status:** CONFORMANT | PARTIAL | NON-CONFORMANT

### Summary
- Conformant: X checks
- Warnings:   X checks
- Violations: X checks

---

### Violations (NON-CONFORMANT)
Code diverges from the spec — must be addressed:

1. **[Rule from spec — section reference]**
   - Found: <what exists in the code>
   - Expected: <what the spec declares>
   - Location: <file path or directory>
   - How to resolve:
     - **Option A — Fix the code** (if the spec reflects the intended architecture):
       - **Action:** <concrete step — e.g., move file, rename module, remove import, extract interface>
       - **Where:** <specific file(s) or directory to change>
       - **Outcome:** <what the code should look like after the fix — describe the target state>
     - **Option B — Update the spec** (if the code reflects an intentional architectural evolution):
       - **Action:** update the relevant section of the spec to reflect the decision
       - **Where:** <spec file path and section to update>
       - **Outcome:** the divergence becomes a documented, intentional decision

---

### Warnings (PARTIAL)
Potential divergence — requires human review:

1. **[Rule from spec — section reference]**
   - Observation: <what was found>
   - Why it may be a problem: <rationale>
   - How to address:
     - **Option A:** <preferred correction if the spec intent should be preserved>
     - **Option B:** <alternative if the spec should be updated to reflect an intentional decision>

---

### Observations (INFO)
Notable patterns — not violations, but worth noting.

---

### Conformant Checks
- [Rule] ✓ — brief note on evidence found
- ...
```

## Output Rules

- Print the full report; do **not** modify any source or spec file
- Every violation and warning must reference the exact section of the spec it was derived from
- Every violation must include the file path or directory where the divergence was observed
- **Every violation must include a "How to resolve" block** with two options: fix the code to match the spec, or update the spec to reflect an intentional architectural evolution. Never leave a violation without both paths described
- **Every warning must include a "How to address" block** with two options: fix the code to match the spec, or update the spec to reflect an intentional deviation
- Group findings: NON-CONFORMANT → PARTIAL → INFO → CONFORMANT
- If all checks pass, summarize the architectural strengths observed and confirm conformance
- Be explicit about what could **not** be verified through static analysis (e.g., runtime behavior, performance NFRs) and flag those as outside the scope of this check
