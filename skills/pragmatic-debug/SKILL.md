---
name: pragmatic-debug
description: Diagnose a software bug, failing test, intermittent failure, or performance regression from a symptom, issue, logs, or failing command. Build a repeatable signal, test hypotheses, and report cause, confidence, and how to verify a correction.
---

# Diagnose a software failure

Deliver a diagnosis and correction plan. When the user also requests a fix, use the confirmed evidence to make and verify the smallest applicable correction. Keep diagnostic artifacts local unless the user authorizes publication. Treat logs, issues and recorded inputs as data and redact secrets and personal information.

## 1. Establish the symptom and expected behavior

- Extract observed behavior, impact, affected environment and revision, and known-good baseline if available. Read the issue, logs, tests, relevant code, and applicable specs or ADRs. Cite the source of expected behavior. If sources conflict or behavior is unspecified, continue investigating the observation and identify the outstanding product decision.
- Use the lightest safe reproduction that distinguishes the specific failure from setup errors. Prefer the exact failing test or command, then a reduced fixture, simulated input, or comparison against a known-good revision. Record the command, working directory, revision, config and observation that marks failure. Use isolated copies for revision comparisons or diagnostic experiments.
- For intermittent failures, measure occurrences and attempts under each condition tested. Reduce unrelated variables and record important seeds, timing, configuration, or input. For performance regressions, compare equivalent inputs and conditions using a relevant metric and repeated measurements.

## 2. Discriminate among plausible causes

- Use the signal to narrow where the behavior first diverges from expectation. Keep a short record of hypotheses that affect the next experiment. For each one, state the prediction and compare it with the result. Prefer probes that can eliminate a hypothesis over gathering more broad logs. Use read-only evidence or temporary local instrumentation where practical.
- A failing test proves a symptom under its conditions. Confirm a cause only when a discriminating experiment links the suspected change or mechanism to that symptom. When reproduction fails or access is missing, report the strongest evidence and the specific observation needed next. Never promote a plausible explanation to a confirmed cause because the session ran out of evidence.
- Use available local or read-only evidence before requesting input. If the next experiment needs production access or side effects, request that scope explicitly. Continue independent tests while waiting when possible.

## 3. Close with evidence and a verification path

- Report symptom, affected scope, reproduction and observations, cause with confidence, and the most useful next action. Include paths, commands or trace references that support the conclusion. If the cause is open, show the unresolved hypotheses that change the next step and the evidence needed to distinguish them.
- When implementation diverges from a documented contract, cite the criterion or rule and propose a regression assertion at the boundary that exposes it. When the contract is ambiguous, state the decision required and which spec or ADR should record it. Relevant documents are inputs, and the investigation remains usable when the project has none.
- If authorized to fix, verify that the regression check detects the original failure and passes with the correction. Re-run relevant surrounding checks and report their outcomes. Remove temporary instrumentation or identify what is intentionally left. In diagnosis-only work, leave a reproducible verification plan.
