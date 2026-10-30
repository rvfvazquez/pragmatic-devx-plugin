# P1 opportunities implementation plan

**Goal:** Make skill behavior observable and prevent static test coverage or orphan tasks from implying completion.
**Spec:** User-approved P1 backlog in reports/Oportunidades para o Pragmatic DevX.md and instruction “aplicar os P1”.
**Architecture:** Extend the dependency-free runner with a conservative Codex JSONL adapter and scenario matrix; minimally update spec-check reporting and build task provenance. No new lifecycle or top-level skills.

## Tasks

- [x] Capture baseline behavior with current skills and fixture incidents; attempt existing trigger prompts before and after, recording authentication limitations.
- [x] Add separate Draft/no-TODO and Review/Approved-with-TODO gate fixtures; test evaluator against each case.
- [x] Add Codex adapter with read-only sandbox, explicit local skills, raw JSONL retained and conservative command evidence. Test CLI failures, mutations, unknown commands, and tool/turn failures.
- [x] Separate inspected coverage from execution evidence in spec-check, keeping static assessment possible with WARN/not done; report command, outcome and relevant tests. Failed assertions FAIL; skips/unavailable evidence WARN. Update report reference and worked example consistently.
- [x] Add source references and bidirectional obligation/task checkpoint to build, preserving old rows, recognizing existing code evidence and legitimate scaffold sources; flag orphan legacy tasks without resetting them.
- [x] Verify before/after behavioral cases and offline suite, obtain independent review, update backlog with exact evidence and remaining limitations. No push or PR.

## Constraints

Python 3.9+ and standard library only. No silent CLI model substitution, no permission bypass. Installed model aliases can fail with account access errors; classify those as infrastructure ERROR. A subagent experiment is not a CLI runner PASS. No claims of full parity or repeated reliability from single trials.

## Review focus

False PASS from process/turn failure or absent execution, shell parsing mistaken for semantic auditing, stale test evidence, skipped tests, tasks justified only by invented requirements, old Build Logs silently reordered, unknown external tooling and fixture contamination.
