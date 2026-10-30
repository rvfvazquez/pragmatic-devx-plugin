# Skill behavior runner implementation plan

**Goal:** Execute and audit the Draft build gate without changing skill instructions.
**Architecture:** Python standard library runner, Claude Code adapter, deterministic evidence checks, isolated fixture repository and retained run artifacts.
**Spec:** Approved description in this chat: first increment only, Draft blocking scenario, events, filesystem/commit comparison and report.

## Constraints and decisions

- Keep existing triggering tests and skills unchanged. Python 3.9+; no dependencies.
- Native execution in this workspace; no PR, push or commit requested.
- Keep CLI permission checks; auto-allow only Read, Glob, Grep and Skill. A requested Write/Edit is a violation even if denied. Bash requests remain inconclusive unless a mutation is proven. This is a constrained gate test, not an OS sandbox or full build evaluation.
- Preserve raw events and stderr outside the disposable fixture. Unknown tool evidence and incomplete execution cannot silently pass.
- Semantic explanation check uses a conservative English rubric and reports missing evidence as inconclusive, not as a proven violation.

## Tasks

- [x] Write evaluator tests for correct refusal, mutation, write-then-delete, missing read, tool error, timeout, malformed events and CLI failure. Observe failure before implementation.
- [x] Implement event parsing and evidence evaluation; add minimal Draft/TODO fixture and natural-language prompt.
- [x] Implement runner: temporary Git repository, CLI adapter with bounded process lifetime, snapshots, metadata, diff, event and report artifacts.
- [x] Test runner integration using a fake CLI process; this tests infrastructure, not model behavior.
- [x] Run offline tests, then attempt one live scenario and report its actual outcome. Document commands, limitations and exit codes.

## Review focus

False PASS from empty/partial output, denied read, nested tool results, duplicate streamed text, untracked/ignored files, timeout cleanup, write-then-delete requests and configuration contamination.

## Verification record

16 offline tests passed, including a fake CLI process. Live Claude Code 2.1.312 returned ERROR because it is not logged in; no live behavioral PASS claimed. Independent review found failed activation and affirmative-response false positives; both now have regression checks. No skills changed, no PR opened.
