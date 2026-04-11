---
name: jetlinks-delivery
description: Prepare JetLinks code changes for compliant delivery. Use when Codex needs to create branch-safe commits, follow JetLinks commit title conventions, avoid pushing to protected branches, collect test evidence, or draft PR descriptions with concrete test and coverage data.
---

# JetLinks Delivery

Read [`references/git-and-pr-rules.md`](references/git-and-pr-rules.md) first.

## Workflow

1. Inspect the current branch and target base branch before staging or pushing anything.
2. Align the commit title with the repository's existing `type(scope): summary` style.
3. Run the relevant unit tests or integration tests and collect numeric evidence.
4. Prepare the PR description with purpose, core changes, test data, coverage data, and residual risks.

## Required Constraints

- Do not push directly to protected mainline branches unless the user explicitly overrides that rule.
- Do not say work is ready for merge without test evidence or a clearly stated blocker.
- Do not use vague PR text such as “tested” or “optimized” without data.

## Response Shape

1. Target branch strategy
2. Proposed commit title
3. Tests and coverage evidence
4. PR summary or remaining blockers
