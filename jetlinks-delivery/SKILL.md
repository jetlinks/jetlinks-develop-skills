---
name: jetlinks-delivery
description: 为 JetLinks 代码变更准备合规交付内容。适用于需要创建符合分支策略的提交、遵循 JetLinks 提交标题规范、避免直推受保护分支、收集测试证据，或使用 gh 创建 GitHub PR 并编写包含测试与覆盖率数据的 PR 描述的场景。
---

# JetLinks Delivery

Read [`references/git-and-pr-rules.md`](references/git-and-pr-rules.md) first.

## Workflow

1. Inspect the current branch and target base branch before staging or pushing anything.
2. Align the commit title with the repository's existing `type(scope): summary` style.
3. Run the relevant unit tests or integration tests and collect numeric evidence.
4. Prepare the PR description with purpose, core changes, test data, coverage data, and residual risks.
5. When publishing to GitHub, prefer `gh` to inspect auth, detect the base branch, and create the PR.

## Required Constraints

- Do not push directly to protected mainline branches unless the user explicitly overrides that rule.
- Do not say work is ready for merge without test evidence or a clearly stated blocker.
- Do not use vague PR text such as “tested” or “optimized” without data.
- When the remote is GitHub and the task includes opening a PR, prefer `gh pr create` over asking the user to open the web page manually.
- In sandboxed agent environments such as Codex, do not run `gh` inside the sandbox; request non-sandbox execution.
- If `gh auth status` is invalid, stop and ask the user to re-authenticate before continuing PR creation.

## Response Shape

1. Target branch strategy
2. Proposed commit title
3. Tests and coverage evidence
4. PR creation plan, summary, or remaining blockers
