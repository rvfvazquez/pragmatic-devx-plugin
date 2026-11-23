# Security review

Review the change defensively. Look for weakened controls and recommend remediation based on source and scanner evidence.

- Read available static-analysis, dependency, and secret-scanning results. Record tool, scope, revision and outcome. If a result is missing or stale, run a configured, trusted scanner when available in an isolated environment suitable for the untrusted checkout. Use a trusted configuration or existing trusted CI result. Avoid running untrusted PR scripts or build hooks with credentials or write access. Report unverified coverage when safe execution or results are unavailable.
- Review affected authentication, authorization, sensitive-data handling, trust boundaries and CI permissions. For dependencies, confirm the affected package and version against the manifest or lockfile and tie the finding to an advisory when available.
- Validate applicability by tracing the relevant code and controls. Distinguish corroborated findings from alerts needing triage. Mark pre-existing findings separately from changes introduced by the PR. Keep values of secrets and sensitive data out of notes, logs and review comments.
- Use the project's severity and merge rules. State the relevant exposure and recommend a fix, protective test or control that verifies remediation. Keep review findings focused on defensive evidence.
