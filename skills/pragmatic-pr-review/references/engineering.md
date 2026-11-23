# Engineering review

Use the actual code paths, existing callers, and applicable repository standards. Prioritize findings that affect correctness or materially increase maintenance and operational risk.

- Check changed behavior against relevant acceptance criteria, and verify error paths, boundary cases, and existing callers or persisted data.
- Review cross-module contracts, compatibility of schemas and APIs, migration sequencing, and behavior under retries or concurrency when the diff affects them.
- Assess whether tests use meaningful assertions, cover the changed paths, and would detect a regression. Distinguish a test you ran from a test you read.
- Evaluate cohesion, coupling, interface clarity, and whether patterns fit the responsibilities and conventions of the project. Treat code smells as leads. Report one when there is a concrete cost, such as duplicated policy that can diverge or a boundary that permits inconsistent state.
- Use CI results for mechanical rules already enforced by tools. Review operational implications where relevant, such as observability for failure modes and recovery after a risky rollout.

Anchor actionable findings to changed lines when possible. If the relevant impact crosses files, cite the changed line and the affected caller or contract. Name the violated rule or the scenario demonstrating impact.
