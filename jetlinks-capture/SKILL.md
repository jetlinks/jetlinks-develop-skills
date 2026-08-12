---
name: jetlinks-capture
description: 沉淀 JetLinks 开发过程中稳定、跨任务可复用的知识。适用于任务完成后判断结论是否应原位更新现有权威文档、项目规范、knowledge、playbook、提示词或 skill，并在用户确认后落档；不用于把单次任务流水、阶段总结或测试证据固化为仓库文档。若已成熟到可抽成通用 skill，则继续询问是否并入官方技能仓库 PR。
---

# JetLinks Capture

Read [`references/capture-workflow.md`](references/capture-workflow.md) first.

## Workflow

1. Judge whether the finished work is worth capturing.
2. Prefer updating the existing canonical source. Only when no source owns a stable cross-task conclusion, choose the smallest useful form: `knowledge`, `playbook`, prompt update, or skill update.
3. Follow the repository's existing knowledge workflow. In Trellis projects prefer the owning `.trellis/spec/` or existing durable docs when appropriate; do not invent a parallel `.ai/` hierarchy. Without an existing workflow, recommend a path only after confirming it is intended to be versioned durable knowledge rather than agent runtime.
4. Present the recommendation first: whether capture is needed, why, the form/path, and the concise summary.
5. Only write the formal capture after the user confirms, unless the user already asked for direct generation.
6. If the knowledge is stable across tasks, recommend updating the related skill or prompt.
7. If the result is generic enough to become a reusable JetLinks skill, ask whether to merge it into `jetlinks-develop-skills` and prepare a PR for `https://github.com/jetlinks/jetlinks-develop-skills`.

## Required Constraints

- Do not create capture docs for every trivial change.
- Do not use `worklog` as the default for a finished task. Completion summaries, attempts, failures, commands, progress, and validation transcripts belong to Trellis / local runtime or PR / CI, not durable knowledge.
- Do not restate raw diffs when no reusable knowledge was learned.
- Do not use README as a place for single-task worklogs, test reports, troubleshooting notes, or PR summaries.
- Do not create a new capture document when an existing knowledge, playbook, or owning source document should be updated instead.
- Do not use capture to backfill execution logs into plan / PRD / design documents or convert them into a committable summary. Authoritative docs keep current accepted facts; process records stay in Trellis / local runtime and test evidence stays in PR / CI.
- Do not promote unstable one-off decisions into skills.
- Do not silently skip the recommendation when the finished task clearly produced reusable knowledge.
- Do not auto-create capture docs without user confirmation unless the user explicitly asked to generate them.
- Do not recommend an official skill PR unless the conclusion is stable across tasks and not tightly bound to one project.
- Always separate verified project facts from temporary assumptions.

## Response Shape

1. Whether capture is recommended
2. Why it is or is not worth capturing
3. Existing canonical source to update, or the justified new output form and target path
4. The concise summary to persist
5. Whether the result should stay only in task runtime, update a project source, or be promoted into a prompt / skill
6. If it can become a common JetLinks skill, whether to merge it into `jetlinks-develop-skills` and submit a PR upstream
