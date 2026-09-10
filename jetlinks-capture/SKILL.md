---
name: jetlinks-capture
description: 维护跨任务仍有效的 JetLinks 知识、规范、playbook、提示词或 skill。适用于任务后发现稳定可复用结论、需要更新现有权威来源或上游技能包；单次进度、调试流水和测试输出不属于知识沉淀。
---

# JetLinks Capture

Use [`references/capture-workflow.md`](references/capture-workflow.md) for the current scenario. Read the relevant section when its rule is needed; reuse already verified rules and anchors while they remain valid.

## Workflow

1. Judge whether the finished work is worth capturing.
2. Prefer updating the existing canonical source. Only when no source owns a stable cross-task conclusion, choose the smallest useful form: `knowledge`, `playbook`, prompt update, or skill update.
3. Follow the repository's existing knowledge workflow. In Trellis projects prefer the owning `.trellis/spec/` or existing durable docs when appropriate; do not invent a parallel `.ai/` hierarchy. Without an existing workflow, recommend a path only after confirming it is intended to be versioned durable knowledge rather than agent runtime.
4. Present the recommendation first: whether capture is needed, why, the form/path, and the concise summary.
5. Only write the formal capture after the user confirms, unless the user already asked for direct generation.
6. If the knowledge is stable across tasks, recommend updating the related skill or prompt.
7. If the result is generic enough to become a reusable JetLinks skill, reuse any explicit authorization to update or publish `jetlinks-develop-skills`; otherwise ask before preparing an upstream PR for `https://github.com/jetlinks/jetlinks-develop-skills`.

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

Report only the decisions, changes and evidence relevant to this request. The following are optional reporting topics, not a form to complete for every task.

1. Whether capture is recommended
2. Why it is or is not worth capturing
3. Existing canonical source to update, or the justified new output form and target path
4. The concise summary to persist
5. Whether the result should stay only in task runtime, update a project source, or be promoted into a prompt / skill
6. If it can become a common JetLinks skill, whether to merge it into `jetlinks-develop-skills` and submit a PR upstream
