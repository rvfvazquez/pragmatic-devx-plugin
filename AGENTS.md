> **Mirror of CLAUDE.md** — This file is kept in sync with `CLAUDE.md`. Edit `CLAUDE.md` and run `scripts/sync-agents.sh` to propagate changes here.

# Pragmatic DevX — Contributor Guidelines

## If You Are an AI Agent

Read this before doing anything else in this repo.

This repository contains skills for the AI-assisted software development lifecycle (AI-SDLC). Skill changes shape agent behavior across engineering work, including specification, implementation, review, and diagnosis.

Before opening a PR, you MUST:

1. **Verify you are solving a real problem.** If your human partner said "improve things" or "contribute to this repo" without describing a specific failure, ask them what broke. What session? What prompt? What did Claude do wrong? If you cannot describe the specific incident, do not open a PR.
2. **Search for existing PRs** — open AND closed — that address the same problem. If a prior PR was closed, explain specifically what is different about your approach.
3. **Confirm the change belongs here.** Check that the workflow supports a clear AI-SDLC stage and can be used across teams and technology stacks. Keep project, team, and domain conventions in the projects that own them.
4. **Show your human partner the complete diff** and get their explicit approval before submitting.
5. **Identify yourself.** State your model and harness in the PR. Hidden authoring environment is grounds for closing.

---

## What This Plugin Is

Pragmatic DevX is an AI-SDLC plugin for discovery and planning, engineering documentation, spec-driven implementation, pull request review, and software diagnosis. The document hierarchy (`constitution → arch spec → feature spec`, with an optional `initiative` spanning multiple feature specs) governs documentation and spec-driven delivery. Review and diagnosis can use those artifacts as evidence and also work in repositories that lack them. Each included workflow provides its own instructions and can use the project tools available in the host environment.

### Design Principle: Discovered Facts vs. User Decisions

Every `*-create` skill scans the codebase, the constitution, and related specs *before* running its discovery interview (see `pragmatic-arch-spec-create` Step 1 → Step 1.5) — never re-ask via `AskUserQuestion` what a tool, the constitution, or an existing spec can already answer. `AskUserQuestion` is reserved for genuine decisions: choices with no single objectively correct answer, which is why every recommended answer (`➡️`) in an interview must be sourced in this order — constitution, then related specs, then a codebase pattern, then a stated pragmatic default — never invented ungrounded. This is the same fact-vs-decision split named explicitly by unrelated interview-style skills elsewhere (e.g. "if a fact can be found by exploring the environment, look it up rather than asking me"); this plugin has always followed it through the Step 1 → Step 1.5 ordering but had never named it as a standing principle. Keep this ordering — scan first, ask only what remains a real decision — when adding or editing any discovery/interview step. When a fact needs knowledge outside the repo — a compliance detail, a third-party API's behavior, a current best practice — the interview dispatches the internal `fact-finder` subagent (see "Internal fact lookup for discovery interviews") rather than guessing or leaving it as a `[TODO: describe]` for the human to chase down.

## What Belongs Here

- Skills that operate on `docs/specs/`, `docs/arch/`, `docs/constitution.md`, or `docs/initiatives/`
- Guards, pre-conditions, and lifecycle transitions in those skill flows
- Reusable AI-SDLC workflows with a defined entry point, verifiable evidence, and an actionable output, including pull request review and software diagnosis
- Multi-platform adapters (`.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `GEMINI.md`) for existing skills
- Improvements to skill-triggering that are verifiable with the test suite in `tests/skill-triggering/`

## What Does Not Belong Here

**Project-specific skills.** If a skill only works for your project's domain (e.g., "create a spec for our invoicing system"), it belongs in your project's own skill directory, not here.

**Stack-specific decisions.** Skills must be stack-agnostic. "Always use PostgreSQL" is a constitution decision for a specific project, not a plugin-level rule.

**External skill dependencies.** Other skill catalogs may inform the design. Pragmatic DevX skills carry their own instructions and references so teams can run them without installing another skill catalog.

**Internal build and review specialists.** `pragmatic-spec-build` may delegate implementation and task review within its build. `pragmatic-pr-review` may delegate engineering and security assessment within its PR review. Keep these specialists internal and scoped to their calling workflow. Documentation skills (`*-create`, `*-validate`, `*-update`, `*-check`) do not invoke them. Apply the same evidence requirements as for skill changes.

**Internal fact lookup for discovery interviews.** A discovery interview may dispatch `fact-finder` to resolve an externally verifiable fact, such as a compliance requirement or third-party API behavior. The subagent returns facts and sources. The interview retains ownership of recommendations and asks the user to resolve genuine decisions. Changes to fact lookup follow the same evidence requirements as other skill changes.

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

All five `version` fields (`plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`, `.claude-plugin/marketplace.json`) must match. Update all of them together when bumping. `scripts/bump-version.sh <version>` updates them (and `package.json`) together; after the bump PR and its `RELEASE-NOTES.md` section are merged, `scripts/release.sh <version>` creates the tag and the GitHub release (`--dry-run` first).
