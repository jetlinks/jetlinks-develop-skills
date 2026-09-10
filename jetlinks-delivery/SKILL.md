---
name: jetlinks-delivery
description: 准备 JetLinks 提交与 PR：分支策略、中文 Conventional Commit、shell 提交命令、按边界复用验证证据和说明真实交付风险。适用于提交、推送、PR 起草或交付审查。
---

# JetLinks Delivery

Use [`references/git-and-pr-rules.md`](references/git-and-pr-rules.md) for the current scenario. Read the relevant section when its rule is needed; reuse already verified rules and anchors while they remain valid.

When long-task state, recovery or evidence lifetime needs coordination, use `$task-continuity` as its owner; simple commit wording or review does not require loading the recovery protocol. This skill only adds JetLinks branch, commit, test, documentation, comment, observability, and PR-template policy.

## Workflow

1. Classify the request as commit drafting, commit review, shell commit command output, delivery preparation, or PR preparation.
2. Inspect the current branch and target base branch before staging or pushing anything.
3. Read [`references/commit-message-zh.md`](references/commit-message-zh.md) when the task involves commit wording, compliance review, or commit title selection.
4. Read [`references/shell-commit-examples.md`](references/shell-commit-examples.md) when the user wants a ready-to-run command for PowerShell, bash, zsh, or cmd.
5. Align the commit message with the repository's existing `type(scope): summary` style and clearly separate verified facts from recommended wording.
6. If the change adds backend functionality or changes existing backend behavior, require repeatable behavior evidence at the boundary that owns the change. Reuse valid existing evidence; add or update tests only for an uncovered behavior or risk, choosing unit, contract, integration, end-to-end, or performance checks by observability rather than stacking them mechanically. Manual observation is fallback evidence only when automation is unavailable and its residual regression risk is explicit.
7. Follow [task-continuity](../task-continuity/SKILL.md) when stage checkpoints or recovery state are in use. Validate a coherent stage together, reuse valid evidence, and create commits only when authorized. A request for commit wording alone does not authorize staging, committing or pushing.
8. Check whether accepted durable requirements, contracts, architecture, API/module behavior, acceptance semantics, or long-term risks require synchronizing an existing authoritative source. Rewrite stale conclusions in place. Treat README as durable repository/module overview only; keep live task state in Trellis / local runtime and test evidence in PR/CI.
9. Before creating a ready PR for backend code changes, inspect the touched code for comment targets from [`../jetlinks-conventions/references/code-comments.md`](../jetlinks-conventions/references/code-comments.md); required comments must exist in code, not only in the PR description.
10. If the implementation was complex or entered a stagnation gate, verify the `$systematic-solving` outcome plus the JetLinks extension: violated invariant, common root cause or explicit variation axis, and removal / retention of special handling. Require the original trigger for a bug, a sibling only when shared behavior changed, a boundary / counterexample only when that risk changed, and affected regressions. Report conclusions, not the debugging transcript.
11. After all stages satisfy the overall acceptance matrix, map existing validation evidence to that matrix before running anything. Reuse evidence whose tested code / Git fingerprint and relevant tests, configuration, dependencies, base, environment, and check semantics are still valid; run only missing, invalidated, failed, or explicitly time-sensitive checks. Record the evidence source and reuse decision; when remote delivery is authorized, push and create or update the PR as a single delivery action.
12. Follow [`references/git-and-pr-rules.md`](references/git-and-pr-rules.md) to explain the final problem, changed behavior, validation and real risks. Respect an applicable repository template, but do not fill irrelevant categories or invent extra work to complete it.

## Required Constraints

- Do not push directly to protected mainline branches unless the user explicitly overrides that rule.
- Do not say work is ready for merge without test evidence or a clearly stated blocker.
- Do not mark a backend feature or behavior-change PR as ready when its changed observable behavior lacks valid evidence at the owning boundary. Do not require a new unit test when an existing unit, contract, integration, end-to-end, or other repeatable check is the more direct valid evidence.
- Do not trigger integration tests from technology keywords alone. Require them only for a changed cross-boundary contract or real assembly behavior that lower-level evidence cannot observe.
- Do not say delivery is complete when code or behavior changed but required source docs are clearly stale; either update them or state the exact gap and risk.
- Do not use vague PR text such as “tested” or “optimized” without data.
- Do not rerun the full test suite merely because work entered the commit, delivery, or PR phase. Reuse still-valid stage evidence and rerun only the affected acceptance slices.
- Do not default to creating a new per-task document, worklog, summary, or archive log in authoritative docs. Follow Trellis or the repo-local runtime workflow and prefer updating an existing canonical source only when its durable facts changed.
- Do not put single-task test reports, PR descriptions, temporary plans, or troubleshooting logs into README files.
- Do not emit multi-line `git commit` commands that rely on literal `\n` becoming real newlines.
- Do not push, create a PR, update PR body/comments, or mark a PR ready after every step or stage. Stage boundaries produce local commits; task completion produces the remote push and PR delivery. Only an explicit user request to share an intermediate branch or open a draft overrides this.
- Do not create a ready PR for backend code changes when public contracts, SPI methods, complex business branches, compatibility, permissions, lifecycle, tracing, MBean, protocol, event, or boundary logic need comments but the touched code lacks them. Fix the code comments first, or create a draft with the exact blocker.
- Do not mark a complex or previously stagnated task ready when changed shared behavior or boundary risk lacks representative evidence, or when new special branches / fallbacks remain without an explicit business variation axis.

## Response Shape

Report only the decisions, changes and evidence relevant to this request. The following are optional reporting topics, not a form to complete for every task.

For commit-only requests:

1. Return only the final commit message by default.
2. If the user asks for review, return the review result plus the corrected message.
3. If the user asks for a command, add the shell-safe command after the message.

For full delivery requests:

1. Current delivery context or target branch strategy
2. Proposed commit message or review result
3. Shell-safe commit command
4. Backend behavior gate, selected validation, and applicable coverage evidence
5. Validated stage commits and overall acceptance status
6. Documentation sync status
7. PR summary or remaining blockers
