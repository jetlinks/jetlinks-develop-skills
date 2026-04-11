---
name: jetlinks-delivery
description: 为 JetLinks 代码变更准备合规交付内容。适用于需要创建符合分支策略的提交、起草或审查中文 Conventional Commit、生成 shell 可执行的 git commit 命令、遵循 JetLinks 提交标题规范、避免直推受保护分支、收集测试证据，或编写包含测试与覆盖率数据的 PR 描述的场景。
---

# JetLinks Delivery

Read [`references/git-and-pr-rules.md`](references/git-and-pr-rules.md) first.

## Workflow

1. Classify the request as commit drafting, commit review, shell commit command output, delivery preparation, or PR preparation.
2. Inspect the current branch and target base branch before staging or pushing anything.
3. Read [`references/commit-message-zh.md`](references/commit-message-zh.md) when the task involves commit wording, compliance review, or commit title selection.
4. Read [`references/shell-commit-examples.md`](references/shell-commit-examples.md) when the user wants a ready-to-run command for PowerShell, bash, zsh, or cmd.
5. Align the commit message with the repository's existing `type(scope): summary` style and clearly separate verified facts from recommended wording.
6. Run the relevant unit tests or integration tests and collect numeric evidence.
7. Prepare the PR description with purpose, core changes, test data, coverage data, and residual risks.

## Required Constraints

- Do not push directly to protected mainline branches unless the user explicitly overrides that rule.
- Do not say work is ready for merge without test evidence or a clearly stated blocker.
- Do not use vague PR text such as “tested” or “optimized” without data.
- Do not emit multi-line `git commit` commands that rely on literal `\n` becoming real newlines.

## Response Shape

For commit-only requests:

1. Return only the final commit message by default.
2. If the user asks for review, return the review result plus the corrected message.
3. If the user asks for a command, add the shell-safe command after the message.

For full delivery requests:

1. Current delivery context or target branch strategy
2. Proposed commit message or review result
3. Shell-safe commit command
4. Tests and coverage evidence
5. PR summary or remaining blockers
