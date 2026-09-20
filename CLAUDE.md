# Pragmatic DevX — Contributor Guidelines

## If You Are an AI Agent

Read this before doing anything else in this repo.

This repository contains skills for engineering documentation workflows. Every skill file shapes how Claude behaves when writing specs, architecture documents, and project constitutions. Changes to skill content are behavior changes — treat them that way.

Before opening a PR, you MUST:

1. **Verify you are solving a real problem.** If your human partner said "improve things" or "contribute to this repo" without describing a specific failure, ask them what broke. What session? What prompt? What did Claude do wrong? If you cannot describe the specific incident, do not open a PR.
2. **Search for existing PRs** — open AND closed — that address the same problem. If a prior PR was closed, explain specifically what is different about your approach.
3. **Confirm the change belongs here.** Skills for specific projects, teams, or business domains do not belong in this plugin. Ask: "Would this be useful to any engineering team using pragmatic specs, regardless of their stack?" If no, publish it separately.
4. **Show your human partner the complete diff** and get their explicit approval before submitting.
5. **Identify yourself.** State your model and harness in the PR. Hidden authoring environment is grounds for closing.

---

## What This Plugin Is

Pragmatic DevX provides skills for two documentation lifecycles — feature specs and architecture specs — governed by a project constitution, plus an optional initiative layer that decomposes a problem too large for one feature spec into a dependency-ordered set of feature specs (and architecture work, when needed) before any of them exist. Skills are invoked before spec work begins, not after. The document hierarchy (`constitution → arch spec → feature spec`, with `initiative` fanning out into multiple feature specs when a single one won't do) is the core design decision everything else flows from.

### Design Principle: Discovered Facts vs. User Decisions

Every `*-create` skill scans the codebase, the constitution, and related specs *before* running its discovery interview (see `pragmatic-arch-spec-create` Step 1 → Step 1.5) — never re-ask via `AskUserQuestion` what a tool, the constitution, or an existing spec can already answer. `AskUserQuestion` is reserved for genuine decisions: choices with no single objectively correct answer, which is why every recommended answer (`➡️`) in an interview must be sourced in this order — constitution, then related specs, then a codebase pattern, then a stated pragmatic default — never invented ungrounded. This is the same fact-vs-decision split named explicitly by unrelated interview-style skills elsewhere (e.g. "if a fact can be found by exploring the environment, look it up rather than asking me"); this plugin has always followed it through the Step 1 → Step 1.5 ordering but had never named it as a standing principle. Keep this ordering — scan first, ask only what remains a real decision — when adding or editing any discovery/interview step. When a fact needs knowledge outside the repo — a compliance detail, a third-party API's behavior, a current best practice — the interview dispatches the internal `fact-finder` subagent (see the fact-lookup exception under "What Does Not Belong Here") rather than guessing or leaving it as a `[TODO: describe]` for the human to chase down.

## What Belongs Here

- Skills that operate on `docs/specs/`, `docs/arch/`, `docs/constitution.md`, or `docs/initiatives/`
- Guards, pre-conditions, and lifecycle transitions in those skill flows
- Multi-platform adapters (`.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `GEMINI.md`) for existing skills
- Improvements to skill-triggering that are verifiable with the test suite in `tests/skill-triggering/`

## What Does Not Belong Here

**Project-specific skills.** If a skill only works for your project's domain (e.g., "create a spec for our invoicing system"), it belongs in your project's own skill directory, not here.

**Stack-specific decisions.** Skills must be stack-agnostic. "Always use PostgreSQL" is a constitution decision for a specific project, not a plugin-level rule.

**Process skills.** Workflow skills (TDD, debugging, planning, code review) belong in a process plugin like superpowers. This plugin is for documentation artifacts, not development workflows.

**Exception — internal subagents for `pragmatic-spec-build`.** `pragmatic-spec-build` is the one skill in this plugin that produces code, not a document. It may dispatch a process-oriented subagent (e.g. a TDD-discipline implementer) internally, scoped strictly to that skill's own build step. This is not a loophole for adding process skills generally: the subagent must not be exposed as a standalone top-level skill, must not be invoked by any documentation skill (`*-create`, `*-validate`, `*-update`, `*-check`), and any new subagent added under this exception needs the same evidence (specific failure in `pragmatic-spec-build`, before/after behavior) as a skill change under "Skill Changes Require Evidence".

**Exception — internal fact-lookup subagent for discovery interviews.** A `*-create` skill's discovery interview may dispatch a narrowly-scoped internal subagent to resolve a *fact* that requires knowledge outside this repo — a compliance requirement, a third-party API's behavior, a current best practice — never to make or influence a decision on the user's behalf. This is a separate, narrower exception than the `pragmatic-spec-build` one above and does not permit process or judgment subagents: the subagent must not be exposed as a standalone top-level skill, must return only externally-verifiable facts with sources (never an opinion, a trade-off, or a recommendation — that boundary belongs behind `AskUserQuestion`, not this subagent), and any change to it needs the same evidence (a specific session where a fact was guessed or punted to the human instead of looked up, before/after behavior) as a skill change under "Skill Changes Require Evidence".

**Duplicate lifecycle coverage.** Each lifecycle step (create → validate → update → build → check) has one skill. Do not add a second create skill for a different output format without first discussing whether a new parameter in the existing skill is sufficient. The initiative layer (`pragmatic-initiative-create` / `-deliver`) is intentionally narrower than the feature-spec and arch-spec lifecycles — it has no `-validate`/`-update`/`-check` of its own by design, since `pragmatic-initiative-deliver` dispatches the existing feature-spec and arch-spec skills (which already have their own validate/update/check) rather than duplicating them at the initiative level. Follow the same restraint `pragmatic-project-constitution` did before its own `-update` was added: grow this layer only from a demonstrated need, not preemptively.

## Skill Changes Require Evidence

Skills are not prose — they are behavior-shaping instructions. Changing wording in a skill description changes when it triggers. Changing a guard changes what Claude allows or blocks.

Before modifying skill content:

- Describe the specific session where the current behavior failed
- Run the relevant test in `tests/skill-triggering/prompts/` before and after your change
- Show that the changed skill still triggers on the existing prompt AND fixes the reported failure

PRs that restructure skill content "for clarity" without evidence of improved behavior will be closed.

## PR Requirements

- One problem per PR
- Fill in the PR description with: what broke, what changed, how you verified it
- Skill changes must include a test prompt update or a new test in `tests/skill-triggering/prompts/` if the triggering behavior changed
- Target the `main` branch — this repo does not use a separate dev branch

## Versioning

All five `version` fields (`plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`, `.claude-plugin/marketplace.json`) must match. Update all of them together when bumping. A future `bump-version.sh` script will automate this.
