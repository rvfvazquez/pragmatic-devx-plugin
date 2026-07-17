> **Mirror of CLAUDE.md** — This file is kept in sync with `CLAUDE.md`. Edit `CLAUDE.md` and run `scripts/sync-agents.sh` to propagate changes here.

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

Pragmatic DevX provides skills for two documentation lifecycles — feature specs and architecture specs — governed by a project constitution. Skills are invoked before spec work begins, not after. The document hierarchy (`constitution → arch spec → feature spec`) is the core design decision everything else flows from.

## What Belongs Here

- Skills that operate on `docs/specs/`, `docs/arch/`, or `docs/constitution.md`
- Guards, pre-conditions, and lifecycle transitions in those skill flows
- Multi-platform adapters (`.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `GEMINI.md`) for existing skills
- Improvements to skill-triggering that are verifiable with the test suite in `tests/skill-triggering/`

## What Does Not Belong Here

**Project-specific skills.** If a skill only works for your project's domain (e.g., "create a spec for our invoicing system"), it belongs in your project's own skill directory, not here.

**Stack-specific decisions.** Skills must be stack-agnostic. "Always use PostgreSQL" is a constitution decision for a specific project, not a plugin-level rule.

**Process skills.** Workflow skills (TDD, debugging, planning, code review) belong in a process plugin like superpowers. This plugin is for documentation artifacts, not development workflows.

**Exception — internal subagents for `pragmatic-spec-build`.** `pragmatic-spec-build` is the one skill in this plugin that produces code, not a document. It may dispatch a process-oriented subagent (e.g. a TDD-discipline implementer) internally, scoped strictly to that skill's own build step. This is not a loophole for adding process skills generally: the subagent must not be exposed as a standalone top-level skill, must not be invoked by any documentation skill (`*-create`, `*-validate`, `*-update`, `*-check`), and any new subagent added under this exception needs the same evidence (specific failure in `pragmatic-spec-build`, before/after behavior) as a skill change under "Skill Changes Require Evidence".

**Duplicate lifecycle coverage.** Each lifecycle step (create → validate → update → build → check) has one skill. Do not add a second create skill for a different output format without first discussing whether a new parameter in the existing skill is sufficient.

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
